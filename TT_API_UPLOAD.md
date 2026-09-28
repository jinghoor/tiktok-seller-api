# TikTok 商品上架 —— 纯 API 操作方式

不用 UI、不点按钮。全部通过 `seller-vn.tiktok.com` 的 OpenAPI 完成，请求从浏览器页面上下文 `fetch` 发出
（自动带 cookie / `X-CSRFToken` / `fp`）。

- 客户端 → [`tt_api.py`](tt_api.py)
- 表单模型模板 → `notes/tk178_edit_payload.json`（**核心资产**）
- 详情视图备份 → `notes/tk178_master_product.json`

---

## 1. 结论速览

| 项 | 值 |
|---|---|
| 上架接口 | `POST /api/v1/product/local/product/create` |
| 编辑接口 | `POST /api/v1/product/local/product/edit` |
| 列表接口 | `POST /api/v1/product/local/products/list` |
| 详情接口 | `GET /api/v1/product/local/product/get?product_id=` |
| 请求体结构 | **表单模型**（不是详情视图） |
| 新建流程 | 生成雪花 id → `get_schema_v2` 预热注册 → `create` |
| 实测成功率 | 预热 4 轮后 1~2 次尝试内成功 |
| 商品名约束 | 25~255 字符，**不允许中文**（`12052262`） |

---

## 2. 四个必须知道的坑

### 2.1 create/edit 要的是「表单模型」，不是详情视图

这是最大的坑。`GET /product/local/product/get` 返回的结构**不能**直接回传给 `create`/`edit`：

| 详情视图（`product/get`） | 表单模型（`create`/`edit`） |
|---|---|
| `categories: [{id, level, is_leaf}]` | `category_id: "601646"` |
| `brand: null` | `brand_id: 0` |
| 属性项是 `{id, name, is_enum, is_multi_choice, is_input, values[]}` | 属性项是 `{id, values:[{id, name, is_custom}]}` |
| `base_price` 带 `sale_price_display` / `localized_dutiable_price_display` | `base_price` 只要 `list_price` / `sale_price` / `region` / `currency` |
| 无 `components` | **有** `components[]`（7 项，属性以 JSON 字符串塞在 `value` 里） |
| 无 `schema_context` | **有** `schema_context` |
| 无 `comp_submit_data` | **有**（且必须是**字符串** `"{}"`） |

拿详情响应当模板 → 永远报 `12052910 Invalid input parameters`，且不告诉你哪个字段错。

**正确做法**：抓一次真实 UI 保存的 `edit` 请求体当模板，之后只打补丁。

### 2.2 `comp_submit_data` 必须是字符串

Go 的反序列化错误会直接告诉你字段类型：

```
json: cannot unmarshal object into Go struct field SaveLocalDraftRequest.comp_submit_data of type string
```

传 `"{}"`（字符串），不是 `{}`。

### 2.3 SKU id 不能跨商品复用

用别的商品的 SKU id → `12052557 The SKU ID does not belong to the product`。

**做法**：SKU 用本地自增 id（`900`/`901`/`902`…），服务端在响应里返回映射：

```json
{"code":0, "data":{
  "product_id":"1790XXXXXXXXXX71",
  "sku_id_map":[{"oldID":"910","newID":"1737XXXXXXXXXX80"},
                {"oldID":"911","newID":"1737XXXXXXXXXX16"},
                {"oldID":"912","newID":"1737XXXXXXXXXX52"}]}}
```

同理，`sale_properties[].values[].id` 也用本地 id，服务端在 `property_value_id_map` 里回映射。

### 2.4 product_id 的注册是**概率性**的 —— 用 id 池最划算

前端打开新建页时会自己生成一个雪花 id（19 位，形如 `1737XXXXXXXXXX84`），
服务端要打若干次 `get_schema_v2` 才把它纳入发布服务。

实测结论（这是全部关键）：

| 观察 | 数据 |
|---|---|
| 预热 1 轮后 create | 基本都报 `12052032` |
| 预热 4 轮后 create | 约 5/8 成功 |
| 预热 6 轮后 create | 约 8/8 成功（同一批内也有失败） |
| 注册成功的 id 能活多久 | **≥20 秒**（20s 后使用仍 4/5 成功） |
| 预热本身耗时 | 16 个 id × 6 轮并发 = **1~2.5 秒** |

**所以正确做法不是「每个商品现场预热重试」，而是预注册一个 id 池，之后取用即建。**

```python
pool = IDPool(tt, warmup_rounds=6, batch=16)
pool.fill()                      # 1~2.5s 建池
for name, prices, ... in jobs:
    r = create_with_pool(tt, pool, tpl, name=name, prices=prices, ...)
```

池里的 id 失败就换下一个（不需要重新预热），池快空了再补。

### 2.5 预热必须**并发**发

`get_schema_v2` 串行发 14 个 id × 5 轮 = 23.3 秒；用 `Promise.all` 并发 = **4.2 秒**。
`tt_upload.py` 的 `TT.post_many(items, parallel=True)` 走的就是并发路径。

---

## 3. 完整流程

```
① 拿模板（只需一次，之后复用）
   └─ 抓真实 UI 保存的 edit 请求体 → notes/tk178_edit_payload.json

② 生成 product_id
   └─ str(1790XXXXXXXXXX00 + random)

③ 预热注册
   └─ POST /api/v1/product/comp/get_schema_v2   × 4
      body: {"schema_context":{"page":3,"get_audit_version":false,
                               "product_id":PID,"category_id":"601646",
                               "product_type_list":["ProductType_Normal"]},
             "components":[],
             "scene_param":{"product_type_add_list":["ProductType_Normal"]}}

④ 打补丁
   └─ 替换 product_name / images / description / sale_properties / skus
      components[title_comp] 同步新商品名
      publish_event_param.session_id 换新

⑤ 提交
   └─ POST /api/v1/product/local/product/create   （新建）
      POST /api/v1/product/local/product/edit     （改已有）
```

### 代码调用

```python
import json, tt_api as A

tpl = json.load(open("notes/tk178_edit_payload.json"))

r = A.create_product(
    tpl,
    name="Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g Chính Hãng - "
         "Giảm Thâm Quầng Và Dưỡng Sáng Vùng Mắt",     # 25~255 字符, 不能有中文
    prices=["150000", "180000", "220000"],              # 每个 SKU 一个价
    stocks=[30, 40, 50],                                # 每个 SKU 一个库存
    seller_skus=["API-S", "API-M", "API-L"],
    variants=["S", "M", "L"],                           # 规格名
)
print(r["code"], r["data"]["product_id"])
```

改已有商品：

```python
r = A.api_post("/api/v1/product/local/product/edit",
               A.patch_payload(tpl, pid="1790XXXXXXXXXX71",
                               prices=["160000", "190000", "230000"]))
```

---

## 4. 关键字段说明

### `images`（主图）

```json
[{"uri": "tos-alisg-i-aphluv4xwc-sg/<32-hex>",
  "url_list": ["https://p16-oec-sg.ibyteimg.com/tos-alisg-i-aphluv4xwc-sg/<32-hex>~tplv-...jpeg?...&from=476444299"],
  "width": 794, "height": 804}]
```

`uri` 是 TOS 路径；`url_list` 是可直接访问的 CDN 地址。两者要**指向同一张图**，
所以换图时要把 `url_list` 里的 `<32-hex>` 一起替换。

### `sale_properties`（规格/变体）

```json
[{"id": "100089",            // 属性 id（如「Thông số」），模板里带
  "text": "Thông số",
  "has_image": true,
  "is_custom": false,
  "values": [
    {"id": "901", "name": "S", "is_custom": true,
     "image": {"uri": "tos-alisg-i-aphluv4xwc-sg/<hex>", "url_list": ["..."],
               "width": 794, "height": 794}},
    {"id": "902", "name": "M", "is_custom": true, "image": {...}}
  ]}]
```

`values[].image` 就是 **SKU 图**。`has_image: true` 时前端/详情页会显示。

### `skus`（每个规格一个 SKU）

```json
[{"id": "910",                                  // 本地自增 id
  "seller_sku": "API-S",
  "properties": [{"id": "100089", "name": "Thông số",
                  "value_id": "901", "value_name": "S"}],
  "base_price": {"list_price": "150000", "sale_price": "150000",
                 "list_price_display": "", "sale_price_display": "",
                 "region": "VN", "currency": "VND",
                 "localized_dutiable_price": "0", "audit_list_price": ""},
  "quantities": [{"available_quantity": 30, "quantity_variation": 0,
                  "warehouse_id": "7659XXXXXXXXXX08"}],
  "pre_order_ship_day": 0, "fulfillment_info": {},
  "purchase_order_quantity_limit": {}, "fees": []}]
```

**价格字段**：`list_price` 和 `sale_price` 都要填（没有折扣时两者相同）。
**库存字段**：`quantities[].available_quantity` + 每个仓库一条记录，见 §5。

### `components`

7 项。只有这三项需要跟着顶层改：

| id | 何时改 |
|---|---|
| `title_comp` | 改商品名时（值是 `json.dumps(新名字)`，注意带引号） |
| `product_property_normal` | 改非合规属性（原产地、版本、原料偏好…）时 |
| `product_property_compliance` | 改合规属性（License 四项）时 |

其余（`virtual_unboxing_comp` / `blindbox_comp` / `qualification_*`）照抄模板。

### `product_properties`（属性值 id）

属性值 id 由服务端下发，**不能凭空构造**。两个来源：

1. 模板里已有的（`102872` CPNF、`100149` China、`102999`/`103000`/`103001` License 四项…）
2. 现场创建：用下拉的「输入自定义值 + 添加」流程，服务端返回临时 id（`499`/`500`…），
   保存后再由 `property_value_id_map` 换成真实 id

---

## 5. 规格与仓库库存设置

### 5.1 一个规格 × 多个仓库

`quantities` 是**数组**，每个仓库一条：

```json
"quantities": [
  {"available_quantity": 100, "quantity_variation": 0, "warehouse_id": "7659XXXXXXXXXX08"},
  {"available_quantity": 50,  "quantity_variation": 0, "warehouse_id": "7686XXXXXXXXXX68"}
]
```

本店（TK178 / DOPI DOPI）的仓：

| warehouse_id | 名称 | 是否默认 |
|---|---|---|
| `7659XXXXXXXXXX08` | Laojie | 是 |
| `7686XXXXXXXXXX68` | BeiNing | 否 |

### 5.2 仓库列表怎么拿

```
GET /api/v1/product/list/seller/warehouses
→ {"seller_warehouses":[{"warehouse_id","name","is_default","warehouse_type",
                         "warehouse_sub_type","geo_name_l0..l4"}]}
```

### 5.3 每个仓库的物流服务

建商品时 `logistics_services` 可以让服务端按仓库自动选（传 `[]`）。
要指定的话从 preload 取：

```
GET /api/v1/product/product_creation/preload
→ data.warehouse_logistics_services[]
     [{warehouse_id, logistics_services:[{service_id, service_name,
                                          is_reachable, is_default, service_level}]}]
```

---

## 6. 错误码对照（实测）

| 码 | 含义 | 处理 |
|---|---|---|
| `0` | 成功 | — |
| `12052910` | 参数无效（**载荷结构错**，最典型是用了详情视图） | 换表单模型模板 |
| `12052032` | 此商品不存在 | 多预热几轮 / 换新 id 重试 |
| `12052031` | 发现无效商品 ID | 同上传 id 格式不对 |
| `12052051` | 商品名称长度不符 / 状态不对 | 检查 25~255 字符 |
| `12052262` | 商品名称不支持中文字符 | 换成越南语/英语 |
| `12052557` | SKU ID 不属于该商品 | SKU id 改本地自增 |
| `12052241` | 属性名称/ID 为空 | `product_properties` 缺必填项 |
| `12052900` | 系统错误 | 重试 |
| `12047007` | 无该功能权限（店铺类型/区域限制） | — |

**排错技巧**：Go 服务的 `debug_info.status_error` 有时会带完整的反序列化错误，
比顶层的 `message` 信息量大得多。看这个字段。

---

## 7. 已知限制

1. **需要 product_id 已注册** —— 纯 API 无法让服务端凭空分配 id，必须走「生成 id + 预热」。
   预热是最终一致性，不是 100% 确定性，所以必须重试。
2. **商品名不允许中文**，只能越南语/英语/数字。
3. **表单模型模板是抓来的**，不是文档定义的。如果 TikTok 前端改版，需要重新抓一次
   （用 `tk178_cdp_capture.py`）。
4. **`create` 与 `edit` 共用同一套载荷结构**，只差 `product_id` 处理方式。
   实测 `create` 传已存在的 id 会变成「更新」。
5. 商品创建后是**草稿**（`product_status=7`），要上架还需提交审核。

---

## 8. 上架速度优化（实测数据）

### 优化前后

| 指标 | 优化前 | 优化后 | 倍数 |
|---|---|---|---|
| 单个商品上架 | 8.4s | **1.1 ~ 2.3s** | ~4.5x |
| 建池（16 个 id × 6 轮） | 23.3s（串行） | **1.1 ~ 2.5s**（并发） | ~15x |
| 批量 6 个总耗时 | ~50s | **13.7s** | ~3.6x |
| 摊销成本 | 8.4s/个 | **2.28s/个** | ~3.7x |

### 三个提速点

**① 复用一条 CDP WebSocket**

原来每个 API 调用都 `sync_playwright().start()` + `attach()` + 关连接，每次约 0.3s。
现在 `TT` 类在一次会话里全程复用同一条 WS（`tt_upload.py` 的 `TT` 类）。

**② 并发预热**

```python
# 串行：14 个 id × 5 轮 = 70 个请求 ≈ 23s
for pid in pids:
    for _ in range(5): post(schema_v2, ...)

# 并发：1~2.5s
items = [{"path": ".../get_schema_v2", "body": {...}} for pid in pids for _ in range(6)]
tt.post_many(items, parallel=True)     # → Promise.all
```

**③ id 池**

预注册一批 id，上架时直接取，避免「失败→重新预热」的串行等待。

### 批量上架

```bash
python3 tt_upload.py --template notes/tk178_edit_payload.json --batch jobs.json
```

`jobs.json`：

```json
[
 {"name": "Kem Dưỡng Mắt ... Chính Hãng", "prices": ["100000"],
  "stocks": [5], "skus": ["B1"]},
 {"name": "Kem Dưỡng Mắt ... Bản Cao Cấp", "prices": ["110000","120000"],
  "stocks": [6,7], "skus": ["B2-S","B2-M"], "variants": ["S","M"],
  "wh_stocks": {"7659XXXXXXXXXX08": [10,20], "7686XXXXXXXXXX68": [5,0]}}
]
```

输出：

```
[pool] 预注册 16 个 id（6 轮并发），耗时 2.5s
[1/6] OK  code=0  1.2s  pid=1790XXXXXXXXXX99  Kem Dưỡng Mắt KORMESIC ...
...
合计 6 个, 13.7s
```

可选参数：`--no-pool`（关池，逐个预热）、`--pool-size N`（默认 16）、`--warmup-rounds N`（默认 6）。

### 规格 × 仓库库存的完整用法

```bash
python3 tt_upload.py --template notes/tk178_edit_payload.json   --name "Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g Chính Hãng"   --prices 100000,110000,120000   --stocks 0,0,0   --skus MX-S,MX-M,MX-L   --variants S,M,L   --wh-stocks "7659XXXXXXXXXX08:10,0,30;7686XXXXXXXXXX68:5,20,0"
```

→ `S` 在老街 10 / 北宁 5，`M` 在老街 0 / 北宁 20，`L` 在老街 30 / 北宁 0。

---

## 9. 测试套件

```bash
python3 tt_upload_test.py --all
```

覆盖 6 组共 31 项断言：

| 组 | 内容 |
|---|---|
| `--perf` | 3 次上架计时 |
| `--variants` | 规格数 1/2/3/5，校验 SKU 数/价格/规格名 |
| `--warehouses` | 5 种仓库组合（单仓/双仓/某仓 0/大数量） |
| `--matrix` | 3 规格 × 2 仓 = 6 个库存格 |
| `--edge` | 名称过短/含中文/255 上限/价格 0 |
| `--batch` | 5 个连续上架 |

最近一次全绿结果见 `notes/tt_upload_test_result.json`（31/31 通过，总耗时 47.7s）。

---

## 10. 会话稳定性

长会话（连续跑几十个请求后）CDP WebSocket 会被回收，报：

```
websocket._exceptions.WebSocketTimeoutException: Connection timed out
```

`tt_upload.TT` 已内置自愈：捕获这类异常 → 重新 `cdp_get /json/list` 找 target →
重连并重注入桥接 → 重试一次。看到这行就是它在工作：

```
  [tt] WebSocket 异常(WebSocketTimeoutException) → 重连重试
```

`hub_headless.CDPPage` 的默认 WS 超时也从 30s 提到 180s。

---

## 11. 相关文件

| 文件 | 作用 |
|---|---|
| `tt_upload.py` | **优化版上架客户端**（id 池、并发预热、多仓库存、批量） |
| `tt_upload_test.py` | 测试套件（6 组 31 项断言） |
| `tt_api.py` | 基础版客户端 + `patch_payload` / `create_product` |
| `tt_raw_probe.py` | 原始响应诊断（status / content-type / body） |
| `TT_PRODUCT_ENDPOINTS.md` | 列表 / 编辑 / 库存接口详解 |
| `tk178_cdp_capture.py` | CDP Fetch 层拦截器（抓完整体 payload） |
| `notes/tk178_edit_payload.json` | **表单模型模板**（核心资产） |
| `notes/tt_upload_test_result.json` | 最近一次测试结果 |
| `notes/tt_test_products.json` | 测试期间创建的商品清单（待清理） |

