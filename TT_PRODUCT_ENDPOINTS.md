# TikTok 商品接口详解 —— 列表 / 编辑 / 库存 / 价格

实测环境：`seller-vn.tiktok.com`，店 DOPI DOPI（TK178），`oec_seller_id = 7494XXXXXXXXXX00`。

公共 query（除个别例外，每个请求都要带）：

```
locale=zh-CN&language=zh-CN&oec_seller_id=7494XXXXXXXXXX00
&seller_id=7494XXXXXXXXXX00&aid=4068&app_name=i18n_ecom_shop
```

**参数位置的坑**：有的接口参数走 **query**，有的走 **body**，同一类接口不统一。
下面的表逐条标了实测结果。

---

## 1. 商品列表

### `GET /api/v1/product/local/products/list`

**POST 会返回 404** —— 这是 GET 接口。

全部参数走 **query**，且 `tab_id` 是必填（缺了报 `12052910`）：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `page_number` | int | 是 | 页码，从 1 开始 |
| `page_size` | int | 是 | 每页条数，**上限 ≤ 50**（传 200 报 `12052910`） |
| `tab_id` | int | **是** | 状态筛选，见下表 |
| `sku_number` | int | 否 | SKU 数（用于筛选多规格商品） |
| `is_need_target_stock` | bool | 否 | 是否返回目标库存 |
| `same_product_page_size` | int | 否 | 同款商品条数 |
| `product_sort_fields` | int | 否 | 排序字段（`3` = 更新时间） |
| `product_sort_types` | int | 否 | `0` 降序 / `1` 升序 |

**分页拉全量**（`page_size` 最大 50）：

```python
def all_products(tt, tab="1", page_size=50):
    out, page = [], 1
    while True:
        r = tt.get("/api/v1/product/local/products/list", {
            "page_number": page, "page_size": page_size, "tab_id": tab,
            "sku_number": 0, "is_need_target_stock": "true",
            "same_product_page_size": 3,
            "product_sort_fields": 3, "product_sort_types": 0})
        d = r.get("data") or {}
        ps = d.get("products") or []
        out.extend(ps)
        if len(ps) < page_size or len(out) >= (d.get("total_product_count") or 0):
            return out
        page += 1
```

单次查询示例：

```python
r = tt.get("/api/v1/product/local/products/list", {
    "page_number": 1, "page_size": 20, "tab_id": 1,
    "sku_number": 0, "is_need_target_stock": "true",
    "same_product_page_size": 3,
    "product_sort_fields": 3, "product_sort_types": 0})
# → {"code":0, "data":{"page_number":1,"page_size":20,
#      "total_product_count":131, "products":[...], "need_async_load_same_products":false}}
```

`products[]` 每项关键字段：

| 字段 | 说明 |
|---|---|
| `product_id` | 商品 id |
| `product_name` | 商品名 |
| `image` | 主图（`{uri, thumb_url_list, width, height}`） |
| `product_status` | 见 §5 状态表 |
| `audit_status` | 审核状态 |
| `is_online_version` | 是否线上版本 |
| `price_range` | `{min_sale_price, max_sale_price, min_sale_price_display, max_sale_price_display}` |

### `GET /api/v1/product/tab/count/get`

各状态 tab 的商品数。无参。

```json
{"code":0,"data":[{"tab_id":1,"count":"131"},{"tab_id":2,"count":"99"},...]}
```

实测本店：`tab_id=1` → 131（全部），`2` → 99（草稿），`5` → 29，`7` → 7，`8` → 3，`4` → 1，`12`/`19` → 1，其余 0。

### `GET /api/v1/product/local/product/get`

商品详情。**`product_id` 走 query**；缺参报 `12052910`。

```python
r = tt.get("/api/v1/product/local/product/get", {"product_id": "1790XXXXXXXXXX71"})
```

**注意**：返回的是**详情视图**，结构与 `create`/`edit` 需要的**表单模型**不同（见 `TT_API_UPLOAD.md` §2.1），不能直接回传。

### 其它列表接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/v1/product/spu/search` | POST | SPU 检索 |
| `/api/v1/product/spuv2/search` | POST | SPU 检索 v2 |
| `/api/v1/product/spu/match` | POST | SPU 匹配 |
| `/api/v1/product/local/same_products/list` | POST | 同款商品 |
| `/api/v1/product/optimize/page/get` | POST | 待优化商品分页 |
| `/api/v1/product/actions/list` | POST | 商品可用操作列表 |
| `/api/v1/product/creator_stock/list` | POST | 达人库存列表 |

---

## 2. 编辑商品

### `POST /api/v1/product/local/product/edit`

**改商品的主接口**。载荷 = 完整表单模型（见 `TT_API_UPLOAD.md`）。

**实测：改价格、改库存、改名、改规格全部走这个接口。**
编辑页 UI 上改一个价格，发的就是这个请求（8KB 完整载荷），没有"轻量改价"端点。

```python
payload = patch_payload(tpl, pid="1790XXXXXXXXXX71",
                        prices=["111000","222000","333000"], stocks=[11,22,33])
r = tt.post("/api/v1/product/local/product/edit", payload)
# → {"code":0,"data":{"product_id":"...","sku_id_map":[{"oldID":"905","newID":"1737XXXXXXXXXX44"}],
#      "success_tip":"提交审核成功，变更内容将在审核通过后生效。","is_in_audit":true}}
```

**SKU id 必须是服务端已属于该商品的 id**，用别的商品的会报
`12052557 The SKU ID does not belong to the product`。
新 SKU 用本地自增字符串 id，服务端在 `sku_id_map` 里返回映射。

### `POST /api/v1/product/local/product/create`

新建商品，载荷结构与 `edit` 相同（**同一套表单模型**）。

差异：

| | create | edit |
|---|---|---|
| `product_id` | 必须是一个服务端已"认识"的 id | 必须是已存在的商品 id |
| 传已存在的 id | 变成**更新**（不是新建） | 正常更新 |
| 传随机 id | `12052032 此商品不存在` | 同上 |

**product_id 的注册是最终一致性** —— 生成 id 后要先打若干次
`POST /api/v1/product/comp/get_schema_v2`（把该 id 带进 `schema_context`），
1 次往往不够，3~5 次稳定。所以必须**预热 + 重试**。

### `POST /api/v1/product/local/product/precheck`

纯校验，无副作用。用于提交前确认名称/类目/描述合法。

```python
tt.post(".../precheck", {"product_name": "x"*30, "category_id": "601646"})   # → code 0
tt.post(".../precheck", {"description": "<p>...</p>"})                        # → code 0
tt.post(".../precheck", {"category_id": "601646", "brand_id": "0"})           # → code 0
```

### 其它编辑相关

| 接口 | 方法 | 实测 |
|---|---|---|
| `/api/v1/product/local/draft/save` | POST | `product_id` 必须**已存在**，否则 `12052032`。`comp_submit_data` 必须是**字符串** |
| `/api/v1/product/local/product/partial/edit` | POST | 传 `{"product_id": PID}` 返回 `code=0` 但 `data=null`（空操作） |
| `/api/v1/product/local/edit/template` | POST | 返回 `{"code":0,"download_url":null}` |
| `/api/v1/product/local/product/bulk_create` | POST | 批量建（未实测） |
| `/api/v1/product/local/product/multi_confirm` | POST | 批量确认（未实测） |
| `/api/v1/product/comp/get_schema_v2` | POST | 组件 schema v2，兼作 id 注册 |
| `/api/v1/product/comp/refetch_schema` | POST | 重取 schema |
| `/api/v1/product/comp/refetch_data` | POST | 重取数据（`action: async_check_product_property`） |

---

## 3. 库存接口

### 3.1 仓库列表

### `GET /api/v1/product/list/seller/warehouses`

```json
{"code":0,"seller_warehouses":[
  {"warehouse_id":"7659XXXXXXXXXX08","name":"Laojie","is_default":true,
   "warehouse_type":1,"warehouse_sub_type":1,
   "geo_name_l0":"越南","geo_name_l1":"老街", ...},
  {"warehouse_id":"7686XXXXXXXXXX68","name":"BeiNing","is_default":false, ...}]}
```

本店两个仓：

| warehouse_id | 名称 | 默认 |
|---|---|---|
| `7659XXXXXXXXXX08` | Laojie | 是 |
| `7686XXXXXXXXXX68` | BeiNing | 否 |

### 3.2 仓库物流服务

### `GET /api/v1/product/product_creation/preload`

`data.warehouse_logistics_services[]` 给出每个仓可用的物流：

```json
[{"warehouse_id":"7686XXXXXXXXXX68",
  "logistics_services":[{"service_id":"7057XXXXXXXXXX58","service_name":"标准运输",
                          "is_reachable":true,"is_default":true,"service_level":2},
                        {"service_id":"7308XXXXXXXXXX46","service_name":"批量发货",...},
                        {"service_id":"7432XXXXXXXXXX44","service_name":"次日达",...}]}]
```

两个仓的物流选项相同（标准运输 / 批量发货 / 次日达）。

### 3.3 改库存的正确方式

**实测结论：改库存走 `POST /api/v1/product/local/product/edit`，在 `skus[].quantities[]` 里给每个仓库一条记录。**

```json
"skus": [{
  "id": "1737XXXXXXXXXX80",          // 服务端的真实 sku id
  "seller_sku": "API-S",
  "base_price": {"list_price":"150000","sale_price":"150000",
                 "region":"VN","currency":"VND",
                 "localized_dutiable_price":"0","audit_list_price":""},
  "quantities": [
    {"available_quantity": 10, "quantity_variation": 0,
     "warehouse_id": "7659XXXXXXXXXX08"},     // Laojie
    {"available_quantity": 5,  "quantity_variation": 0,
     "warehouse_id": "7686XXXXXXXXXX68"}      // BeiNing
  ]
}]
```

**已验证的库存矩阵**（3 规格 × 2 仓，6 个格子各自独立）：

| 规格 | Laojie | BeiNing |
|---|---|---|
| S | 10 | 5 |
| M | 0 | 20 |
| L | 30 | 0 |

读回完全一致。`available_quantity: 0` 是合法值（表示该仓不备货）。

### 3.4 专用库存/价格接口的实测状态

| 接口 | 方法 | 实测结果 |
|---|---|---|
| `/api/v1/product/sku/price/stocks/update` | POST | 返回 `code=0 success` 但**值不变** —— 字段名不对，服务端静默忽略。**不要用** |
| `/api/v1/product/sku/price/update` | POST | `98001004 部分信息填写错误`（缺必填字段） |
| `/api/v1/product/sku/stocks/increase` | POST | `98001004` 同上 |
| `/api/v1/product/sku/stocks/decrease` | POST | 同类，未实测 |
| `/api/v1/product/stock/sku/list` | POST | `400 validating: expr_path=Page, cause=invalid` —— body 里要 `page` 对象，格式未摸清 |
| `/api/v1/product/stock/product/list` | POST | 同上 |
| `/api/v1/product/stock/list` | POST | `200` 但空 body（需特定参数组合） |
| `/api/v1/product/stock/sku/count/list` | POST | `code=0` |
| `/api/v1/product/stock/status_count/list` | POST | `code=0` |
| `/api/v1/product/stock/query/sku` | POST | `12039003 参数无效`（缺必填） |
| `/api/v1/product/stock/query/inventory_health` | POST | **可能用**，返回健康分：`{"seller_health_score_info":{"health_score":0,"instock_rate_pct":0,...}}` |
| `/api/v1/product/stock/query/warehouse/stock_sale_type` | POST | `12039003 params invalid` |
| `/api/v1/product/stock/flow/list` | POST | `12039003 参数无效` |

**结论：库存/价格改了不生效时，优先怀疑「用了专用端点但字段名不对」。
统一走 `product/local/product/edit` 是可靠路径。**

---

## 4. 批量改价 / 改库存

没有找到可用的轻量批量端点。要批量改，只能：

1. 逐个商品 `GET /product/local/product/get` 拿详情
2. 转成表单模型（或直接用抓到的模板改 `skus`）
3. 逐个 `POST /product/local/product/edit`

**关键**：转表单模型时 `skus[].id` 必须用**服务端返回的真实 id**（从 `product/get` 的 `skus[].id` 取），
否则报 `12052557`。

```python
# 批量改价示例
for pid, new_prices in jobs.items():
    detail = tt.get("/api/v1/product/local/product/get", {"product_id": pid})
    # ⚠️ 详情是「详情视图」，要映射成表单模型字段（见 TT_API_UPLOAD.md §2.1）
    payload = detail_to_form_model(detail, prices=new_prices)
    r = tt.post("/api/v1/product/local/product/edit", payload)
```

---

## 5. 状态码对照

### 商品状态 `product_status`

| 值 | 含义（实测） |
|---|---|
| `1` | 已生效 / 上架中 |
| `4` | 待提交 / 编辑中 |
| `7` | 草稿（新建后默认） |

### 商品 tab `tab_id`

| tab_id | 含义 | 本店数量 |
|---|---|---|
| `1` | 全部 | 131 |
| `2` | 草稿箱 | 99 |
| `3` | 审核中 | 0 |
| `4` | 违规下架 | 1 |
| `5` | 已下架 | 29 |
| `7` | 待优化 | 7 |
| `8` | 审核驳回 | 3 |

### 业务错误码

| 码 | 含义 | 处理 |
|---|---|---|
| `0` | 成功 | — |
| `98001004` | 部分信息填写错误 | 缺必填字段，检查 body |
| `12039003` | 参数无效 | 缺必填 |
| `12047007` | 无该功能权限 | 店铺类型/区域限制 |
| `12052031` | 发现无效商品 ID | product_id 格式不对 |
| `12052032` | 此商品不存在 | 多预热几轮 / 换新 id |
| `12052051` | 名称长度不符（25~255） | 改名 |
| `12052241` | 属性名称/ID 为空 | 补 `product_properties` |
| `12052262` | 名称不支持中文 | 换越南语/英语 |
| `12052557` | SKU ID 不属于该商品 | 用服务端真实 id |
| `12052896` | 价格错误 | VND 允许 `1₫ ~ 999.999.999₫` |
| `12052900` | 系统错误 | 重试 |
| `12052910` | 参数无效（**载荷结构错**） | 最常见：用了详情视图当载荷 |
| `12052910`（HTTP 400 `validating: expr_path=Page`） | body 缺 `page` 对象 | 加 `{"page":{"page_number":1,"page_size":N}}` |

---

## 6. 排错工具

```bash
# 看原始响应（status / content-type / body），绕过 JSON 解析
python3 tt_raw_probe.py --suite
python3 tt_raw_probe.py /api/v1/product/stock/sku/list POST --body '{"page":{"page_number":1,"page_size":5}}'

# 抓 UI 的真实请求（CDP Fetch 层，完整体不截断）
python3 tk178_cdp_capture.py --submit
```

**排错顺序**：
1. `tt_raw_probe.py` 看 HTTP 状态 —— 404 说明方法/路径错，400 看 `validating:` 提示
2. 看 `debug_info.status_error` —— Go 的反序列化错误比顶层 message 信息量大
3. 还不行就用 CDP 拦截抓一次 UI 操作的真实请求
