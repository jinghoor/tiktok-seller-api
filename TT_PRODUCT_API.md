# TikTok 卖家中心 · 商品上架接口

对 `https://seller-vn.tiktok.com`（店铺：Kira Skincare，VN 本土店，`oec_seller_id=7494XXXXXXXXXX00`）
商品模块的接口逆向与实测。

- 全量接口表（307 条）→ [`TT_PRODUCT_API_TABLE.md`](TT_PRODUCT_API_TABLE.md)
- 机器可读接口图 → `notes/tt_api_map_full.json`（全站 568 条）、`notes/tt_product_api.json`（商品 307 条）
- 实测结果 → `notes/tt_replay_result.json`、`notes/tt_probe_result.json`
- 完整表单 schema → `notes/tt_schema_full.json`

---

## 1. 结论速览

| 项 | 结果 |
|---|---|
| 卖家中心全量接口 | **568** 个唯一 (方法, 路径) |
| 商品相关接口 | **307** 个（POST 285 / GET 21 / PUT 1），分 63 个业务域 |
| 请求方式 | 页面内 `fetch`，cookie + `X-CSRFToken`，自动带指纹 |
| 实测方式 | 抓真实请求 → 原样重放（空 body 探测会被网关 403） |
| 实调数量 | 重放 56 个真实请求，业务成功 **44** 个 |
| 商品接口实测成功 | **10** 个（见 §4） |
| 写路径 | 创建/发布接口已定位，端到端写测试**未做**（见 §7） |
| 表单结构 | **后端驱动**：`comp/get_schema` + `product_creation/preload` 下发字段定义与校验规则 |

---

## 2. 认证与请求约定

**认证只有两样东西**，都从 Hub Studio 环境 profile 自动加载，不需要重新登录：

| 项 | 来源 |
|---|---|
| cookie（145 条 tiktok.com 域） | 环境 profile |
| `X-CSRFToken` | 从 cookie `csrf_token` 取，需要 `decodeURIComponent` |

**公共 query 参数**（除少数例外，每个请求都要带）：

```
locale=zh-CN&language=zh-CN&oec_seller_id=7494XXXXXXXXXX00&seller_id=7494XXXXXXXXXX00
&aid=4068&app_name=i18n_ecom_shop
```

**请求头**：

```
Content-Type: application/json; charset=utf-8     # POST 才有
X-CSRFToken: <从 cookie csrf_token 取, 需 URL 解码>
Accept: application/json, text/plain, */*
```

### 防伪参数（重要）

真实浏览器请求还带两组防伪参数，**缺失会被网关拒绝**：

| 参数 | 位置 | 说明 |
|---|---|---|
| `X-Tts-Oec-Bsid` | query | 每次请求都不同，base64 长串。公共 GET 接口不带也行 |
| `msToken` | query | 会话级，同一会话内稳定 |
| `X-Bogus` / `X-Gnarly` | query | 每次请求都不同，由 `webmssdk` 签名生成 |
| `fp` / `verifyFp` | query | 设备指纹 |

**结论：不要脱离页面自己拼请求。** 正确做法是在页面上下文里 `fetch`，让页面自己的 sdk 补这些参数，或者直接复用页面已建立的会话。

### fp 的现象（需注意）

`POST /api/v1/product/comp/get_schema_v2`、`size_chart/search`、`stock/sku/list`、
`commission/config/get` 这几个接口，**从页面内 fetch 会返回 403 + 空 body `{}`**：

```
[403] POST /api/v1/product/comp/get_schema_v2
      {}
```

但**页面自己发同一个请求时是 200**。说明这几个接口校验的不是 cookie 和 CSRF，
而是 `X-Tts-Oec-Bsid` / `fp` 这类会话绑定的字段。

- `comp/get_schema_v2` 用 `fp=verify_mnr5kgd4_...` 页面自己发的能通，我用简化 query 发的 403
- 同一批里 `comp/get_schema`（GET）用简化 query 就通

**绕过方式**：直接从页面抓它自己的请求（本文 §5 的方法），或者用 CDP 在网络层拦截并重放原请求。

---

## 3. 表单是后端驱动的（这是关键架构事实）

商品创建表单**不是前端写死的**，字段定义和校验规则由服务端下发。三条链路：

### 3.1 `GET /api/v1/product/comp/get_schema` — 组件级校验规则

返回 `component_schema`（JSON 字符串，需要二次 parse），每个组件带完整规则：

```json
{"code":0,"message":"success",
 "schema_context":{"gray_comps":["title_comp","desc_comp","main_images_comp"]},
 "component_schema":"{\"desc_comp\":{\"id\":\"desc_comp\",\"type\":1,\"control_element\":{},
   \"rules\":[
     {\"rule_type\":\"IS_REQUIRED\",\"rule_value\":\"true\",\"trigger\":2},
     {\"rule_type\":\"MAX_LENGTH\",\"rule_value\":\"10000\",\"trigger\":2},
     {\"rule_type\":\"MIN_IMAGE_WIDTH\",\"rule_value\":\"100\",\"trigger\":0},
     {\"rule_type\":\"MIN_IMAGE_HEIGHT\",\"rule_value\":\"100\",\"trigger\":0},
     {\"rule_type\":\"MAX_IMAGE_NUM\",\"rule_value\":\"30\",\"trigger\":2},
     {\"rule_type\":\"MAX_TARGET_SIZE\",\"rule_value\":\"10485760\",\"trigger\":0},
     {\"rule_type\":\"ASYNC_CHECK\",\"rule_value\":\"true\",\"trigger\":2}
   ]},
   \"title_comp\":{...}, \"main_images_comp\":{...}}"}
```

`title_comp` 的规则示例：`IS_REQUIRED=true`、`MIN_LENGTH=1`、`MAX_LENGTH=255`、
再加一条 `REGULAR` 正则限制（表情/特殊字符）。

### 3.2 `POST /api/v1/product/comp/get_schema_v2` — 组件运行时状态

每个组件带 `control`（是否隐藏/禁用）和本地化文案：

```json
{"code":0,"message":"success","components":[
 {"id":"title_comp","ui_type":"TEXT_INPUT",
  "description":{"label_name":{"key":"productlisting_product_name","name":"商品名称",
                               "space":"fe","project":"i18n_ecom_shop"},
                 "label_tips":[{...}]},
  "control":{"is_hidden":false,"is_disabled":false,"is_support":true},
  "rules":[{"rule_type":"IS_REQUIRED","rule_value":"true",
            "tips":{"key":"productlisting_enter_name","name":"输入商品名称"}},
           {"rule_type":"MIN_LENGTH","rule_value":"1"},
           {"rule_type":"MAX_LENGTH","rule_value":"255"}]}]}
```

**只传 `{}` 或 `{category_id}` 时只返回 `title_comp` 一个组件。** 完整表单必须带创建页那套 query（见 §4.1）。

### 3.3 `GET /api/v1/product/product_creation/preload` — 全部约束与选项

**实测 `data` 下 100 个字段**，是构造 payload 的依据。关键约束（VN 店实测）：

| 字段 | 值 |
|---|---|
| `max_sku_count` | 300 |
| `max_sale_property_value_count` | 300 |
| `product_name_limit` | `{min_length, max_length}` |
| `main_image_num` | `{max_num: 9}` |
| `main_image_pixel_limit` | `{min_height: 300, min_width: 300}` |
| `sale_property_length_limit` | `{max_length: 30}` |
| `sale_property_value_length_limit` | `{max_length: 50}` |
| `desc_image_pixel_limit` | `{min_height, min_width, max_height, max_width}` |
| `qualification_image_pixel_limit` | `{min_height, min_width}` |
| `warehouses` | **3** 个仓（LaoJie=`7626XXXXXXXXXX69` 默认、BeiNing、…） |
| `warehouse_logistics_services` | 每仓可用物流（`service_id`/`service_name`/`is_default`） |
| `available_categories` | **26** 个一级品类 |
| `default_sale_platforms` | `[0]` |
| `support_lang_list` | `en` / `zh` / `vi` |
| `local_lang` | `{code:"vi"}` |
| `seller_type` | 2 |
| `total_submit_count` | 151（该店历史提交数） |
| `session_id` | 每次不同，如 `202609251800527C8755A5DF5FE31C7398` |
| `is_multi_warehouse_open` | true |
| `is_support_global_listing` | true |
| `is_support_category_v2` | true |
| `is_support_pre_tax_price` | true |
| `is_support_clearance` | true |
| `is_clone_support` | true |
| `is_nfs_support` | true |
| `max_package_weight` | 100000 |
| `category_migrate_ddl_date` | 2025-11-24 |
| `publish_fields` | `[{warranty_policy,is_open:false},{warranty_period,false},{white_image,false}]` |
| `comp_gray_list` | 9 个已灰度组件（`title_comp`、`product_property_comp`…） |
| `schema_context.gray_comps` | `[brand_comp, property_comp, desc_comp, main_images_comp, tax_info_comp, title_comp]` |
| `in_quick_listing` | true |
| `gpr_shop_type` | 1 |
| `dimension_config` | 1 |

100 个字段的完整原始数据：`notes/tt_preload.json`。

> **响应体积随 query 变化**：用创建页那套完整 query（含 `listing_page_for_schema_v2` 等）实测返回
> **37,638B**；用简化 query 返回 **19,283B**。字段数相同（100），差异在中英文案与图片 URL 上。

其它已抓取样本：`notes/tt_categories.json`、`notes/tt_warehouses.json`、`notes/tt_regions.json`。

---

## 4. 商品接口实测结果

### 4.1 已验证可用（10 个）

| METHOD | PATH | 实测结果 |
|---|---|---|
| GET | `/api/v1/product/comp/get_schema` | 200，5952B，返回 3 个组件规则 |
| GET | `/api/v1/product/product_creation/preload` | 200，**37,638B**，100+ 约束字段 |
| GET | `/api/v1/product/product_creation/preload_all_categories` | 200，**1,120,220B**，全品类树 |
| GET | `/api/v1/product/categories/search` | 200，688B，品类搜索 |
| GET | `/api/v1/product/tab/count/get` | 200，477B，各 tab 商品数 |
| GET | `/api/v1/product/regions/mget` | 200，466B，区域+币种+价格上下限 |
| GET | `/api/v1/product/list/seller/warehouses` | 200，1124B，仓库列表 |
| GET | `/api/v1/product/optimize/meta/get` | 200，2360B，优化元数据 |
| GET | `/api/v1/product/stock/banner/check` | 200，46B，需 `banner_type` |
| GET | `/api/v1/product/notifications/get` | 200，30B，需 `source=1` |

### 4.2 创建页真实调用链（抓包所得完整 query）

```bash
# 1. 品类搜索
GET /api/v1/product/categories/search
    ?key_word=&top_n_recent_categories=6&sale_platforms=0
    &<公共参数>

# 2. 全部品类（1.1MB，慎用）
GET /api/v1/product/product_creation/preload_all_categories
    ?need_unauthorized=true&require_image=true&sale_platforms=0&need_deactive_categories=true
    &<公共参数>

# 3. 创建页预加载（表单字段与约束）
GET /api/v1/product/product_creation/preload
    ?need_unauthorized_category=true&need_deactive_categories=true&require_image=true
    &page_type=1&listing_page_for_schema_v2=PUBLISH_PAGE
    &platform_for_schema_v2=SELLER_PC&product_type_for_schema_v2=ProductType_Norm
    &need_stock_lock_info=true&covered_categories=true
    &<公共参数>

# 4. 组件 schema（全量）
GET /api/v1/product/comp/get_schema?get_audit_version=false&<公共参数>

# 5. 组件 schema v2（需页面会话，见 §2）
POST /api/v1/product/comp/get_schema_v2?<公共参数>
```

### 4.3 写路径定位（未实测）

| 用途 | 接口 |
|---|---|
| 存草稿 | `POST /api/v1/product/local/draft/save` |
| **建商品** | `POST /api/v1/product/local/product/create` |
| 改商品 | `POST /api/v1/product/local/product/edit` |
| 局部改 | `POST /api/v1/product/local/product/partial/edit` |
| 批量建 | `POST /api/v1/product/local/product/bulk_create` |
| 上传图片 | `POST /api/v1/product/local/upload` |
| **预检（提交前校验）** | `POST /api/v1/product/local/product/precheck` |
| 提交上架 | `POST /api/v1/product/msubmit` |
| 图片提交 | `POST /api/v1/product/images/msubmit` |
| 上架/下架 | `POST /api/v1/product/products/activate` / `deactivate` |
| 删除/恢复 | `POST /api/v1/product/products/delete` / `recover` |
| 价格/库存 | `POST /api/v1/product/sku/price/update`、`POST /api/v1/product/sku/price/stocks/update` |
| 库存增减 | `POST /api/v1/product/sku/stocks/increase` / `decrease` |

**`precheck` 是关键**：它是纯校验接口，可以用来在真正提交前验证 payload 结构是否正确，不产生数据。

---

## 5. 测试方法（可复现）

空 body 探测在卖家中心**没有意义** —— 网关对缺参 POST 一律返回 `403 + {}`：

```
[403] POST /api/v1/product/brand/detail        {}     ← 不是"没权限",是"没参数"
```

正确流程：

```bash
cd "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly"

# 1. 静态提取全量接口（从 API client bundle）
python3 tt_api_extract.py                          # → notes/tt_api_map_full.json  568 条
python3 tt_api_extract.py --files oec_product      # 只跑商品模块

# 2. 动态抓真实请求（CDP 预注入 XHR/fetch 钩子，跨导航存活）
python3 tt_scrape.py record --port CDP_PORT --page "/product/create?shop_region=VN" \
        --wait 20 --out notes/cap_product_create.json
python3 tt_scrape.py record --port CDP_PORT --page "/product/manage?shop_region=VN&tab=all" \
        --wait 14 --out notes/cap_product_manage.json

# 3. 重放真实请求（去掉一次性防伪参数后重发）
python3 tt_replay.py --cap notes/cap_product_create.json notes/cap_product_manage.json

# 4. 空探测（仅用于路由存在性，结论有限）
python3 tt_probe.py --dry-run                      # 先审清单
python3 tt_probe.py                                # 127 个只读接口
python3 tt_probe.py --include-writes               # 危险:不推荐
```

### 工具说明

| 脚本 | 作用 |
|---|---|
| `tt_api_extract.py` | 从 bundle 静态抽 `方法名 → {HTTP 方法, 路径}` |
| `tt_bundles.py` | 下载 CDN 上的 JS bundle（`curl` 直取，无鉴权） |
| `tt_scrape.py` | CDP 预注入 XHR/fetch 记录器，抓真实请求/响应 |
| `tt_replay.py` | 重放抓到的真实请求 |
| `tt_probe.py` | 空 body 批量探测（带写接口黑名单） |

---

## 6. 空探测结果（供对照，结论有限）

对 127 个判定为只读的商品接口做空探测：

| 状态 | 数量 | 含义 |
|---|---|---|
| `OK` | 14 | 无需参数即返回业务数据 |
| `NOAUTH_HTTP` | 59 | HTTP 403 + 空 body —— **主要是缺参数，不是权限问题** |
| `404_NO_ROUTE` | 43 | 返回 `No matching route`，该店铺/区域未开放此路由 |
| `PARAM` | 1 | 路由通，报参数缺失 |
| `NOT_JSON` | 6 | 正常 200（分类器误判，实为首页统计类接口） |
| 其它业务码 | 4 | `12047007` / `98001004` / `12001120` |

`404_NO_ROUTE` 的 43 条集中在 `global/*`（跨境）、`multi_region_listing/*`（多区域）、
`optimize/title_strategy/*`（标题策略）——这些是**其他店铺类型/区域才开放**的功能，
该 VN 本土店没有。它们不是"接口不存在"，换店铺/区域可能就通。

---

## 7. 未完成项与阻碍

### 7.1 端到端建商品未实测

**已具备**：接口定位、表单 schema、字段约束、仓库/品类/物流选项。
**缺三样**：

1. **真实图片 URL**：`main_images_comp` 要求至少 1 张图，`min 300x300`。需要先走
   `POST /api/v1/product/local/upload` 上传拿到 `uri`。
2. **`/product/local/product/create` 的字段名**：客户端是直通式
   （`CreateLocalProduct(e,n){ return t(url,{method:'POST',body:e},n) }`），
   **body 不做任何转换，字段名完全由调用方给**。静态读 bundle 拿不到字段名，
   必须从一次真实提交的请求体里取。
3. **完整表单的 schema**：`get_schema_v2` 只回 `title_comp`；全量表单位于
   `preload`（约束）+ `get_schema`（规则）两处，需要拼装。

取字段名的最快路径：在创建页把表单填完（可以用任意真实商品数据，**最后一步点提交前**
抓包），或者对已有商品点「编辑商品」再保存，抓 `edit` 的请求体 —— 它和 `create` 同构。

### 7.2 已知的响应语义

| 码 | 含义 |
|---|---|
| `0` | 成功 |
| `98001004` | 参数不完整/格式错（`部分信息填写错误`） |
| `12052910` | 缺必填参数（例：`search param cannot be nil`） |
| `12047007` | 该店铺无此功能权限 |
| `12001120` | 跨境/instant 模式不可用 |
| `403 + {}` | 网关拒绝：缺 `fp`/`X-Tts-Oec-Bsid` 或参数不全 |
| `No matching route` | 该路由未在该店铺/区域注册 |

---

## 8. 已知限制

1. **不要脱离页面拼请求**：`fp` / `X-Tts-Oec-Bsid` / `X-Bogus` 缺失会导致 403。正确做法是在页面内 `fetch`。
2. **`preload_all_categories` 返回 1.1MB**，循环调用会拖慢页面。有品类缓存就别重复拉。
3. **307 条接口里 285 条是 POST**，其中约 180 条有写副作用。`tt_probe.py` 内置写接口黑名单，默认不实调。
4. **`multi_region_listing/*` 与 `global/*` 共 43 条在本店不可用**，换店铺需重测。
5. **`search_spu` 的 `exclude_mutex` 语义已实测确认**：

   | `exclude_mutex` | total | 返回 |
   |---|---|---|
   | `true` | **0** | 0 |
   | `false` | **21** | 21 |

   该店 21 个商品全部已被 GMV Max 认领，因此 `exclude_mutex=true` 时为 0。这不是接口故障。
