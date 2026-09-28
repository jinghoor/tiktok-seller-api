# TikTok 卖家中心「局部编辑」接口逆向
### 为什么不能走完整 edit、走什么代替、接口的精确语义

逆向目标：`https://seller-vn.tiktok.com/product/manage`（商品管理）
店铺：TK178越本土 / DOPI DOPI / `oec_seller_id=7494XXXXXXXXXX00`

---

## 1. 问题：完整编辑会触发重新审核

TikTok 的规则是：**编辑商品（走 `POST /api/v1/product/local/product/edit`）会让商品重新进入审核**，审核期间商品权重受影响。实测证据：

```
POST /api/v1/product/local/product/edit
→ "success_tip": "提交审核成功，变更内容将在审核通过后生效。"
→ "is_in_audit": true
→ ScenarioContext 里 PublishScene: 2
```

所以「只改库存」「只改价格」这种**不影响商品信息的简单变更**不应该走完整编辑接口。

**结论：改库存和改价格各有专门的局部接口，它们不触发重新审核。**

---

## 2. 逆向方法

完整方法链（可复用）：

| 步骤 | 工具 | 产出 |
|---|---|---|
| 1. 被动抓写请求 | `tt_live_capture.py` — 常驻 hook 页面 `fetch`，只记写操作 | 请求 URL + body |
| 2. UI 复现触发 | CDP `Input.dispatchMouseEvent` 真实鼠标点击 | 界面元素 → 操作路径 |
| 3. **调用栈反推** | `tt_fetch_hook.py` — hook fetch 并 `new Error().stack` | 构造请求的源 bundle 位置 |
| 4. bundle 源码验证 | `tt_api_extract_bundle.py` + 定点 grep | 字段名 + 过滤逻辑（**最终证据**） |
| 5. API 直接验证 | `tt_partial_edit.py` | 语义确认 + 可回滚测试 |

关键工具：

- **`tt_live_capture.py`** — 常驻服务，页面里注入 fetch hook，把写请求落到 `notes/tt_live_hits.jsonl`。被动记录，不干扰操作。
- **`tt_fetch_hook.py`** — 除了请求体，还会捕获 **JS 调用栈**。这是从「抓到 body」升级到「读懂代码」的关键：栈帧直接指向构造 payload 的那个 chunk。
- **`tt_api_extract_bundle.py`** — 从微前端 bundle 里按「方法名(参数){...`${this.uriPrefix}<PATH>`...method:`POST`}」的结构切分，一次提取 1000+ 接口（模板串里的路径普通 grep 抓不到）。

### 踩坑记录

| 现象 | 原因 | 修法 |
|---|---|---|
| 商品列表页 `body.innerText.length == 90`，DOM 却在（innerHTML 597KB） | 无头模式下 SPA 不渲染主体 | `Emulation.setFocusEmulationEnabled({enabled:true})` |
| `/product/list` 页面空白 | **路径错了**，真实路径是 `/product/manage` | 从 `performance.getEntriesByType('resource')` 反推正确路由 |
| 输入框值变成 `1790355...1790355...`（重复两遍） | CDP 同时发 `keyDown`+`char` 导致每字符插入两次 | 用 `Input.insertText` 一次性输入 |
| 点铅笔图标没反应 | 图标是 `row-hover-show-icon`，要先进单元格 hover | 先 `mouseMoved` 到单元格，停 300ms，再移到图标上点 |
| `Runtime.evaluate: Object reference chain is too long` | `js()` 返回了 DOM 对象 | 表达式必须返回 `JSON.stringify(...)` 字符串 |
| WebSocket `Connection timed out` | 浏览器周期性踢空闲 CDP 连接 | `CDPPage._reconnect()` + 调用层透明重试 |
| `curl` 下载 bundle 失败 SSL 证书 | 本机代理 MITM | `curl -sk` |

---

## 3. 接口一：库存（局部编辑）

### `POST /api/v1/product/stock/alert/set_stock`

前端函数名 `SetInShopStock`，位于 `product_manage_stock` 微前端。

```json
{
  "product_id": "1790XXXXXXXXXX16",
  "sku_id": "1737XXXXXXXXXX12",
  "warehouse_quantity_list": [
    {"warehouse_id": "7659XXXXXXXXXX08", "quantity": 50}
  ]
}
```

**`quantity` 是增量（delta），不是绝对值。**

两次对照实验（同一 SKU，Laojie 仓）：

| 界面输入框原值 | 我设成的值 | 实际发出 `quantity` | 计算 |
|---|---|---|---|
| 88 | 9999 | **9911** | 9999 − 88 |
| 9999 | 150 | **−9849** | 150 − 9999 |

服务端返回更新后的绝对值：

```json
{"code":0,"message":"success",
 "current_quantity_list":[{"warehouse_id":"7659XXXXXXXXXX08","quantity":200}]}
```

bundle 源码佐证（`product-stock.n87bqkie.js`）：

```js
async requestUpdateSkuQty(e){
  let {productId:t, skuId:n, data:r} = e,
      i = await qd.SetInShopStock({
        product_id: t,
        sku_id: n,
        warehouse_quantity_list: r.map(e => ({ warehouse_id: e.whId, quantity: e.increment }))
      });
  ...
}
```

`quantity: e.increment` —— 字段就是增量。

**所以纯 API 调用要传 delta：`delta = 目标值 − 当前值`。传 0 是 no-op。**

---

## 4. 接口二：价格 + 库存（可多 SKU）

### `POST /api/v1/product/sku/price/stocks/update`

前端函数名 `UpdateSkuPriceStocks` / `UpdateSKUPriceStocks`。

```json
{
  "product_id": "1790XXXXXXXXXX16",
  "price_stocks_edit_data": [
    {"sku_id": "1737XXXXXXXXXX12", "warehouse_id": "7659XXXXXXXXXX08",
     "quantity_variation": 134800},
    {"sku_id": "1737XXXXXXXXXX48", "warehouse_id": "7659XXXXXXXXXX08",
     "quantity_variation": 134993}
  ],
  "tab_id": 2
}
```

单项可用字段（来自 `product-manage.il8pamf6.js` 的 `diffSkuToEditData`）：

| 字段 | 语义 | 备注 |
|---|---|---|
| `sku_id` | 必填 | |
| `sale_price` | 零售价，**绝对值**（字符串） | 改价用这个 |
| `audit_list_price` | 审核清单价，绝对值 | 与 `sale_price` 二选一或并存 |
| `quantity_variation` | 库存，**增量**（数字） | 改库存用这个，需配 `warehouse_id` |
| `warehouse_id` | 仓库 ID | 改库存时必填 |
| `unit_inventory_items` | 单位级库存 | 组合装 / 多单位场景 |

源码里的过滤逻辑（决定什么算「有变更」）：

```js
let e = diffSkuToEditData(i, t).filter(e =>
  w === `stock` ? e.quantity_variation !== void 0 || e.unit_inventory_items?.length > 0
: w === `price` ? e.sale_price !== void 0 || e.audit_list_price !== void 0
: !0);
```

**价格是绝对值，库存是增量** —— 两者可以在**同一个请求的同一条目里并存**，所以「改价 + 改库存」一次请求完成。

响应回传更新后的绝对值：

```json
{"code":0,"message":"success",
 "price_stocks_data":[{
   "sku_id":"1737XXXXXXXXXX48",
   "quantity":{"warehouse_id":"7659XXXXXXXXXX08","available_quantity":11},
   "price":{"region":"VN","currency":"VND","list_price":"138500",
            "sale_price":"138500","sale_price_display":"138.500₫"}}]}
```

失败时可能返回 `stock_edit_failed_skus` 数组。

### 已验证的两次实验

| 操作 | 请求 | 结果 |
|---|---|---|
| 批量改价 3 SKU 到 138000 | `[{"sku_id":A,"sale_price":"138000"},{"sku_id":B,"sale_price":"138000"},{"sku_id":C,"sale_price":"138000"}]` | 三个全部生效 |
| 同一请求改价 + 改库存 | `[{"sku_id":A,"sale_price":"139000","warehouse_id":WH,"quantity_variation":133}]` | 价格 139000、库存 333 同时生效 |

---

## 5. 不触发重新审核的证据

| | 完整 edit | 局部接口 |
|---|---|---|
| 端点 | `POST /product/local/product/edit` | `POST /product/stock/alert/set_stock`<br>`POST /product/sku/price/stocks/update` |
| 响应字段 | `is_in_audit: true`、`success_tip: "提交审核成功…"` | 只有 `current_quantity_list` / `price_stocks_data` |
| `ScenarioContext` | `PublishScene: 2` | 无 |
| 商品 `product_status` | 会变更 | 测试前后都是 `4`，未变 |
| 商品 `audit_status` | 会变更 | 测试前后都是 `3`，未变 |

自动化断言（`tt_partial_edit_test.py --case no_audit`）就是检查这四项。

---

## 6. 客户端

### `tt_partial_edit.py`

```bash
# 读当前 SKU × 仓库状态
python3 tt_partial_edit.py --read 1790XXXXXXXXXX16

# 查审核状态（验证不触发重审）
python3 tt_partial_edit.py --audit-check 1790XXXXXXXXXX16

# 改单个 SKU 价格（绝对值）
python3 tt_partial_edit.py --price <PID> <SKU> 150000

# 一次请求改全部 SKU 价格
python3 tt_partial_edit.py --price-all <PID> 150000

# 改库存到目标值（内部算 delta）
python3 tt_partial_edit.py --stock <PID> <SKU> <WH> 50

# 同一请求改价 + 改库存
python3 tt_partial_edit.py --both <PID> <SKU> <WH> --set-price 150000 --set-stock 50

# 整表批量
python3 tt_partial_edit.py --batch <PID> --set-price 150000 --set-stock 50
```

Python 调用：

```python
import tt_partial_edit as PE
from tt_stock_api import StockAPI

api = StockAPI()                    # 连到已开的 Hub Studio 环境（CDP CDP_PORT）
PE.set_price(api, pid, sku, 150000)                  # 绝对值
PE.set_stock(api, pid, sku, wh, 50)                  # → delta 自动算
PE.set_price_and_stock(api, pid, sku, wh, price=150000, stock=50)   # 一次请求
PE.set_price_all(api, pid, 150000)                   # 多 SKU 一次请求
```

### `tt_stock_api.py`（底层）

- `StockAPI.call(method, path, body)` — 在页面上下文里 `fetch`，自动带 `x-csrftoken`
- 自动重连：CDP 掉线后重连并重注入桥接，请求透明重试
- `sku_list()` / `warehouse_stock()` — SKU × 仓库明细

### `tt_api_extract_bundle.py`（方法论工具）

```bash
python3 tt_api_extract_bundle.py --all --md API_TABLE.md     # 提取微前端全部接口
python3 tt_api_extract_bundle.py --all --filter price        # 按关键词过滤
```

### `tt_fetch_hook.py`（抓请求 + 调用栈）

```bash
python3 tt_fetch_hook.py --install          # 装 hook
python3 tt_fetch_hook.py --show             # 列出捕获（含 body / resp / stack）
python3 tt_fetch_hook.py --stack <关键词>    # 看某请求的完整调用栈
```

---

## 7. 测试

```bash
python3 tt_partial_edit_test.py --all          # 全部用例（含慢的非法请求诊断）
python3 tt_partial_edit_test.py --all --fast   # 跳过慢诊断
python3 tt_partial_edit_test.py --case price   # 单用例
```

用例覆盖：读取、单 SKU 改价、整表改价、库存增减、库存清零、改价+改库存同请求、批量、边界（幂等/delta=0/非法 SKU/负库存）、**不触发审核**、并发改价。

每个用例都是「改 → 读回校验 → 还原」，跑完不留痕迹。结果落到 `notes/tt_partial_edit_test.json`。

### 性能注意

非法 `sku_id`（不存在的 ID）会让服务端走全表扫描，**单次可达 1–2 分钟**。这是服务端行为，不是客户端问题。`--fast` 会跳过这两个诊断用例。

---

## 8. 环境

| 项 | 值 |
|---|---|
| 浏览器环境 | Hub Studio `containerCode=NUMBER_REDACTED`，serial 660，`TK178越本土-XX-限单（痘痘精华）` |
| 组 | TKSP_越南 |
| 店铺 | DOPI DOPI，`oec_seller_id=7494XXXXXXXXXX00` |
| CDP 端口 | `CDP_PORT`（headless） |
| 代理 | SOCKS5 `PROXY_HOST:31331` |
| 仓库 | `7659XXXXXXXXXX08` Laojie（默认）、`7686XXXXXXXXXX68` BeiNing |
| 测试商品 | `1790XXXXXXXXXX16`，3 SKU，基线价 120000，基线库存 200/7/7 |

页面上下文里的公共 query：

```
locale=zh-CN&language=zh-CN&oec_seller_id=<id>&seller_id=<id>&aid=4068&app_name=i18n_ecom_shop
```

### 常用页面路由（踩过坑，记下来）

| 页面 | 正确路径 | 错误路径 |
|---|---|---|
| 商品管理（列表） | `/product/manage?tab_id=1` | ~~`/product/list`~~ 空白 |
| 库存管理 | `/product/stock` | |

`tab_id`：`1` 全部、`2` 草稿、`3` 审核中、`4` 违规、`5` 下架、`7` 待优化、`8` 驳回。

---

## 9. 产物清单

| 文件 | 作用 |
|---|---|
| `tt_partial_edit.py` | **主客户端** — 价格/库存局部编辑 |
| `tt_partial_edit_test.py` | 测试套件（可回滚） |
| `tt_stock_api.py` | 底层 CDP + 页面 fetch 桥、自动重连 |
| `tt_api_extract_bundle.py` | 微前端接口提取器 |
| `tt_fetch_hook.py` | 请求 + 调用栈捕获 |
| `tt_live_capture.py` | 常驻写请求记录 |
| `tt_price_probe.py` | 参数形状爆破（探索期工具） |
| `notes/tt_partial_edit_test.json` | 测试结果 |
| `notes/bundles/mgmt/` | 商品管理页 bundle（108 个 chunk） |
| `notes/bundles/stock/` | 库存页 bundle（41 个 chunk） |

---

## 10. 附录：商品管理页其他「局部操作」接口

从 `product_manage_page` / `product_manage_stock` 微前端提取（96 个商品管理相关接口里的关键项）。
这些都是**单接口单动作**，不走完整编辑，因此不触发商品信息重新审核。

### 上下架 / 删除（商品级，批量）

| 接口 | 前端函数 | 语义 |
|---|---|---|
| `POST /api/v1/product/products/activate` | `MActivateProducts` | 批量上架 |
| `POST /api/v1/product/products/deactivate` | `MDeactivateProducts` | 批量下架 |
| `POST /api/v1/product/products/delete` | `MDeleteProducts` | 批量删除 |
| `POST /api/v1/product/products/recover` | `MRecoverProducts` | 批量恢复（回收站） |
| `POST /api/v1/product/global/products/delete` | `MDeleteGlobalProducts` | 批量删除（全球商品） |
| `POST /api/v1/product/local/product/multi_confirm` | `MConfirmProducts` | 批量确认 |

典型 body（批量接口都是 ID 数组）：

```json
{"product_ids": ["1790XXXXXXXXXX16"]}
```

### 库存（另一批接口，参数结构与主流程不同）

| 接口 | 前端函数 | 备注 |
|---|---|---|
| `POST /api/v1/product/sku/stocks/increase` | `IncreaseSKUStocks` | 单独增加，实测 5 种形状都报 `98001004 部分信息填写错误` |
| `POST /api/v1/product/sku/stocks/decrease` | `DecreaseSKUStocks` | 单独减少，同上 |
| `POST /api/v1/product/sku/price/update` | `UpdateSKUPrice` | 只改价，实测同上 |
| `POST /api/v1/product/global/sku/price/edit` | `EditPrice` | 全球商品改价 |
| `POST /api/v1/product/global/sku/stock/edit` | `EditStock` | 全球商品改库存 |
| `POST /api/v1/product/global/product/stock/edit` | `EditProductStock` | 全球商品改库存（商品级） |
| `POST /api/v1/product/multi_region_listing/sku/price/stocks/update` | `UpdateRegionSkuPriceStocks` | 多地区版本，body 多 `product_source` 和 `region` 字段 |

**建议走已验证的两个**（`set_stock` + `sku/price/stocks/update`），上面这批是不同入口用的，字段契约未验证。

多地区版本的 body 结构（源码 `useTracker.cf3uqrvl.js` 可见）：

```js
let l = { product_id: s.product_id, price_stocks_edit_data: c,
          product_source: jt.WEB, region: e().editRegion };
await V.UpdateRegionSkuPriceStocks(l);
```

### 库存预警阈值

| 接口 | 前端函数 |
|---|---|
| `POST /api/v1/product/stock/alert/set_seller_alert` | `SetSellerAlertStock` |
| `POST /api/v1/product/stock/alert/sales/forecast_option/update` | `UpdateSalesForecastOption` |

### 批量改价（另一条产品线）

| 接口 | 前端函数 | 备注 |
|---|---|---|
| `POST /api/v1/latamb/product_task/product_price/batch_change` | `BatchProductPriceChange` | 走「商品任务」体系，参数未逆向 |

### 仓库 / 库存配置

| 接口 | 前端函数 |
|---|---|
| `GET /api/v1/product/stock/fbt_setting/get` | `GetFBTSetting` |
| `GET /api/v1/product/stock/fbt_setting/update` | `UpdateFBTSetting` |
| `POST /api/v1/product/stock/restriction/update` | `UpdateRestriction` |
| `POST /api/v1/product/stock/restriction/delete` | `DeleteRestriction` |
| `POST /api/v1/product/stock/warehouse/deactivatable/check` | `CheckWarehouseDeactivatable` |
| `POST /api/v1/product/stock/negative/check` | `CheckNegative` |
| `POST /api/v1/product/stock/negative/close` | `CloseNegative` |

### 读取（列表 / 明细 / 计数）

| 接口 | 前端函数 | 备注 |
|---|---|---|
| `GET /api/v1/product/local/product/get?product_id=` | `GetLocalProduct` | 商品详情，`data.product`，`page_size` ≤ 50 |
| `GET /api/v1/product/tab/count/get` | — | 各 tab 数量，返回 `[{tab_id,count}]` |
| `GET /api/v1/product/local/products/list` | `ListLocalProducts` | 本地商品列表 |
| `GET /api/v1/product/web/local/products/list` | — | 商品管理页实际用的列表接口（**269 个商品实测可用**） |
| `GET /api/v1/product/local/product/skus/list` | `ListLocalProductSKUs` | SKU 列表 |
| `POST /api/v1/product/stock/sku/list` | `ListSKU` | SKU × 仓库库存明细（`skus` 在**顶层**） |
| `POST /api/v1/product/stock/query/sku` | — | 单个 SKU 库存查询 |
| `POST /api/v1/product/stock/flow/list` | `ListStockFlow` | 库存流水 |
| `POST /api/v1/product/stock/status_count/list` | `CountProductStockStatus` | 库存状态计数 |

**列表接口实测**：

```
GET /api/v1/product/web/local/products/list?tab_id=1&page_size=20&page=1
→ {"code":0,"data":{"page_size":20,"total_product_count":269,
                    "next_cursor":"[...]","has_more":true,"products":[...]}}
```

- `products/list` 必须是 **GET**（POST 返回 404）
- `page_size` **≤ 50**，超了报 `12052910`

### 其他商品操作

| 接口 | 前端函数 |
|---|---|
| `POST /api/v1/product/local/product/copy` | `CopyLocalProduct` |
| `POST /api/v1/product/local/same_products/list` | `ListLocalSameProducts` |
| `GET /api/v1/product/local/product/extra/get` | `GetLocalProductExtra` |
| `POST /api/v1/product/sku/price/cal` | `CalCrossBoardSKUPrice` |
| `POST /api/v1/product/sku/prices/mcal` | `MCalCrossBoardSKUPrices` |
| `POST /api/v1/product/promotion/price/get` | `GetPromotionPrice` |
| `POST /api/v1/product/optimize/meta/get` | — |
| `GET /api/v1/product/optimize/products/get` | `GetOptimizationProducts` |

---

## 11. 批量改价 / 批量改库存的推荐做法

### 单商品多 SKU（一次请求）

```python
PE.set_price_all(api, pid, 150000)          # 改价（绝对值，一次全改）
PE.batch_apply(api, pid, price=150000, stock=100, wh_id=WH)   # 价 + 库存
```

### 多商品

`price_stocks_edit_data` 是**商品内**的 SKU 数组，跨商品要循环（每商品一次请求）。
多商品循环时用 `ThreadPoolExecutor` 并发（**不同商品**，同一商品不要并发，会撞写）：

```python
from concurrent.futures import ThreadPoolExecutor

def upd(pid):
    return PE.set_price_all(api, pid, 150000)

with ThreadPoolExecutor(8) as ex:
    list(ex.map(upd, product_ids))
```

### 注意

- 同一 SKU 不要在并发请求里同时提交（服务端会拒绝重复 `sku_id`）
- 库存是增量语义：并发改同一 SKU 的库存会因为「读到旧值」而算错 delta
- 价格是绝对值语义：并发改同一 SKU 价格是幂等的（最后一次赢）

---

## 12. 后端选型：页面 fetch vs 直连 HTTP

两套后端都实现了同一组接口，代码路径不同：

| | 页面 fetch（`tt_stock_api.StockAPI`） | **直连 HTTP（`tt_http_client.TT`）** |
|---|---|---|
| 原理 | CDP `Runtime.evaluate` 在页面里 `fetch` | 从 CDP 取 cookie，之后用 `http.client` 直发 |
| 鉴权 | 浏览器自动带 | 手动带 cookie + `x-csrftoken` |
| 单次耗时 | 1–2s，**会随机挂死** | **稳定 0.45s** |
| 页面路由要求 | 必须在 `/product/manage` 等轻量页 | **无要求** |
| 实测结果 | 长任务里反复 `Runtime.evaluate` 超时 | `--all --fast` **37/37 PASS** |

**推荐直连。** 页面后端保留作兜底（例如 cookie 取不到时）。

### 为什么页面 fetch 会挂死

卖家中心页面自己跑大量轮询脚本，会长时间占住 JS 主线程。此时：

- `Runtime.evaluate` 永远等不到结果 —— 因为页面根本没机会执行那段 JS
- Python 侧 `websocket` 的 `settimeout` **在 TLS 层读阻塞时不生效**，`recv()` 无限阻塞
- 表现：脚本静默挂死，`ps` 显示 0% CPU 睡在 I/O，只能靠 `faulthandler` 抓栈才看得出来

`faulthandler.dump_traceback_later(45, exit=True)` 是定位这类问题的关键工具：

```
File "websocket/_socket.py", line 129 in recv
  raise WebSocketTimeoutException("Connection timed out")
File "hub_headless.py", line 292 in send
  msg = json.loads(self.ws.recv())
File "hub_headless.py", line 324 in js
  r = self.send("Runtime.evaluate", ...)
File "tt_partial_edit.py", line 67 in get_product
```

修了两层：
1. 页面侧 `AbortController` —— 让 `fetch` 自己超时，保证 `evaluate` 一定返回
2. Python 侧 `SIGALRM` 看门狗 —— socket 层卡住时硬超时抛异常

但即便修了这两层，长任务里仍然会挂。所以最终走直连。

## 13. 直连 HTTP 的完整踩坑记录

这一段是本次最费时间的部分，按遇到顺序：

| # | 现象 | 根因 | 修法 |
|---|---|---|---|
| 1 | `SSL: CERTIFICATE_VERIFY_FAILED` | 本机代理做 TLS MITM | `ssl.CERT_NONE`（自建出口链路；生产换固定 CA） |
| 2 | `http.client` 直连超时 | `http.client` **不读系统代理**，`urllib` 会读 | 手工发 `CONNECT host:443` 建隧道，再 `wrap_socket` |
| 3 | 所有响应 `json` 为 `None` | `http.client` **不自动解压 gzip** | 检查 `Content-Encoding` 后 `gzip.decompress` |
| 4 | 所有 POST 返回 **403** | cookie 里没有 `csrf_token`；卖家中心用的是 **`csrftoken`** | 三个候选名都试：`csrftoken` / `csrf_token` / `passport_csrf_token` |
| 5 | 有了 csrf 仍 403 | cookie 带了 243 项含 microsoft/google 等无关域 | 只保留 `tiktok` / `oec` / `byteintl` 系域 → 剩 88 项 |
| 6 | 连续请求几十次后开始 403 | 写接口**速率风控** | 自适应限流：命中退避，成功后衰减；默认间隔 0.6s |
| 7 | `/product/local/product/get` 返回 `code: 10000` | 该接口对部分商品状态不可用（页内 fetch 同样拿不到） | 用列表接口 + **零增量探测**替代 |
| 8 | 拿不到逐 SKU 价格 | 列表只给 `sale_price_ranges`；`sale_price` 是**绝对值语义**，不能拿写接口"探读"（会真写进去） | 测试断言改为**响应体驱动**：写接口的响应里就带回更新后的真值 |

### 关键技术：零增量探测（免费读库存）

`set_stock` 的 `quantity` 是增量，传 `0` 是 no-op，但**响应会回传 `current_quantity_list`（更新后的绝对值）**：

```python
def probe_stock(tt, pid, sku_id, wh_id) -> int:
    body = {"product_id": pid, "sku_id": sku_id,
            "warehouse_quantity_list": [{"warehouse_id": wh_id, "quantity": 0}]}
    r = tt.post("/api/v1/product/stock/alert/set_stock", body)
    return r["json"]["current_quantity_list"][0]["quantity"]
```

这是一次「不改变数据的读」，在 `product/get` 不可用时是唯一稳定的库存读法。

### 读路径（直连）

```python
# 商品级：SKU id 列表、价格区间、总库存
GET /api/v1/product/web/local/products/list?tab_id=1&page_size=50&page=1
    → data.products[].skus[].id / sale_price_ranges / total_available_stock

# SKU × 仓库库存：零增量探测
POST /api/v1/product/stock/alert/set_stock  (quantity=0)

# 价格：不读，直接用写接口的响应体（响应里是绝对值真值）
POST /api/v1/product/sku/price/stocks/update
```

## 14. 最终测试结果

```
python3 tt_partial_edit_test.py --all --fast --gap 0.8
→ 37/37 PASS   (247.5s)   后端：直连 HTTP
```

用例覆盖：

| 用例 | 断言 | 验证内容 |
|---|---|---|
| read | 3 | SKU 可读 |
| price | 4 | 单 SKU 改价、绝对值语义、还原 |
| price_all | 4 | 一次请求改 3 个 SKU |
| stock | 4 | 库存增量语义（正/负 delta） |
| stock_zero | 2 | 清零再恢复 |
| both | 6 | **同一请求改价 + 改库存** |
| batch | 3 | 整表批量 |
| edge | 3 | delta=0 是 no-op、同值幂等 |
| no_audit | 5 | **不触发重新审核**（状态不变 + 响应无审核字段） |
| concurrent | 4 | 多 SKU 依次改价（并发会被限流，故串行） |
| restore | 2 | 完全回到基线 |

结果落到 `notes/tt_partial_edit_test.json`。

### 限流现实

写接口有速率限制。`--gap` 控制最小请求间隔：
- `0.15s` → 连续 30+ 次后开始 403
- `0.6s`（默认）→ 基本稳定
- `0.8–1.0s` → 长批量任务建议值

用 `--from-shop` 批量操作几百个商品时，脚本会串行 + 自适应退避；预计 200 个商品改价约 5–8 分钟。
