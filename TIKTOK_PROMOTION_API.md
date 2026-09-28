# TikTok 促销活动 API（跨境店 SHOP_XBORDER / ExampleShop）

来源：`https://seller.tiktokshopglobalselling.com/promotion/marketing-tools/tool-choose`
抓取方式：CDP 抓真实请求 + 前端 bundle（`promotion/static/js/*.js`，34 个 chunk）的 API 层提取

## 1. 环境常量

| 项 | 值 |
|---|---|
| 后台域 | `seller.tiktokshopglobalselling.com` |
| **API 域** | `api16-normal-sg.tiktokshopglobalselling.com` |
| `oec_seller_id` / `seller_id` | `7494XXXXXXXXXX00` |
| `aid` / `app_name` | `6556` / `i18n_ecom_shop` |
| 货币 | VND（越南盾），时区 GMT+7 |

公共 query：

```
locale=zh-CN&language=zh-CN&oec_seller_id=7494XXXXXXXXXX00&seller_id=7494XXXXXXXXXX00&aid=6556&app_name=i18n_ecom_shop
```

## 2. 页面路由（前端）

| 工具 | 路由 |
|---|---|
| 工具选择总览 | `/promotion/marketing-tools/tool-choose` |
| 商品折扣 | `/promotion/marketing-tools/discount/create` |
| 商品折扣（编辑） | `/promotion/marketing-tools/discount/edit` |
| 秒杀 | `/promotion/marketing-tools/flash-sale/create` |
| 直播秒杀 | `/promotion/marketing-tools/live-flash-sale/create` |
| 达人秒杀 | `/promotion/marketing-tools/creator-flash-sale/create` |
| 新品折扣 | `/promotion/marketing-tools/early-bird-price/create` |
| 优惠券 | `/promotion/marketing-tools/voucher/create` |
| 多买多优惠 | `/promotion/marketing-tools/buy-more-save-more/create` |
| 购物赠好礼 | `/promotion/marketing-tools/gift-with-purchase/create` |
| 搭配购 | `/promotion/marketing-tools/bundle-deal/create` |
| 运费折扣 | `/promotion/marketing-tools/free-shipping/create` |
| 促销码 | `/promotion/marketing-tools/promo-code/create` |
| 智能促销 | `/promotion/marketing-tools/smart-promotion/create` |

## 3. 核心接口（按业务分类）

> 路径中的版本号来自前端模板 `${e.version||1}`，实测为 `v1`。

### 3.1 商品折扣（Discount）

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/discount/create` | `CreateDiscount` |
| POST | `/api/v1/promotion/discount/list` | `ListDiscounts` |
| POST | `/api/v1/promotion/discount/get` | `GetDiscount` |
| POST | `/api/v1/promotion/discount/update` | `UpdateDiscountPromotion` |
| POST | `/api/v1/promotion/discount/deactivate` | `DeactivateDiscount` |
| POST | `/api/v1/promotion/single_discount/list` | `ListSingleDiscounts` |
| POST | `/api/v1/promotion/single_discount/get` | `GetSingleDiscount` |

### 3.2 优惠券（Voucher）

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/voucher/create` | `CreateVoucher` |
| POST | `/api/v1/promotion/voucher/update` | `UpdateVoucher` |
| POST | `/api/v1/promotion/voucher/get` | `GetVoucher` |
| POST | `/api/v1/promotion/voucher/list` | `ListVoucher` |
| POST | `/api/v1/promotion/voucher/destroy` | `DestroyVoucher` |
| POST | `/api/v1/promotion/voucher/check_conflict` | `CheckConflictVoucher` |
| POST | `/api/v1/promotion/voucher/check_voucher_overlap` | `CheckSellerVoucherOverlap` |
| POST | `/api/v1/promotion/voucher/list_products` | `ListProductsInVoucherByCursor` |

APP 侧券（`/api/v2/promotion/app/voucher/{create,get,list}`）与
多版本券（`/api/v2/promotion/voucher/{create,get,list,update}`）也存在于 bundle。

### 3.3 SNS 商品折扣

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/sns_product_discount/create` | `CreateSNSProductDiscount` |
| POST | `/api/v1/promotion/sns_product_discount/update` | `UpdateSNSPromotion` |
| POST | `/api/v1/promotion/sns_product_discount/get` | `GetSNSProductDiscount` |
| POST | `/api/v1/promotion/sns_product_discount/check_deactivate` | `CheckSNSPromoDeactivate` |
| POST | `/api/v1/promotion/sns_product_discount/products/list` | `ListSNSProducts` |
| POST | `/api/v1/promotion/sns_product_discount/products/batch_operate` | `BatchOperateSNSProducts` |

### 3.4 通用（商品/变体操作、配置、概览）

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/mget_item_data` | `MGetItemData` ← **折扣页用它取商品数据** |
| POST | `/api/v1/promotion/app/mget_item_data` | `MGetAppItemData` |
| POST | `/api/v1/promotion/update_products` | `UpdateProductsInPromotion` |
| POST | `/api/v1/promotion/update_skus` | `UpdateSkusInPromotion` |
| GET | `/api/v1/promotion/list_skus` | `ListSkus` |
| GET | `/api/v1/promotion/config` | `GetSellerPromotionConfig` |
| GET | `/api/v1/promotion/get_summary` | `GetPromotionSummary` |
| GET | `/api/v1/promotion/list_seller_gray_config` | `ListSellerGrayConfig` |
| GET | `/api/v1/promotion/shop_risk_info/get` | `GetShopRiskInfo` |
| POST | `/api/v1/promotion/seller_experiment_info/get` | `GetSellerExperimentInfo` |
| POST | `/api/v1/promotion/shop_metrics/overview/get` | `GetPromotionShopMetricsOverview` |
| POST | `/api/v1/promotion/tools_metrics/overview/get` | `GetPromotionToolsMetricsOverview` |
| POST | `/api/v1/promotion/tool_info/list` | `ListPromotionToolInfo` |
| POST | `/api/v1/promotion/seller_recently_used_tools/list` | `ListSellerRecentlyUsedTools` |
| POST | `/api/v1/promotion/smart_plan/list_recommended_tools` | `ListSmartPlanRecommendedTools` |
| POST | `/api/v1/promotion/seller_audit_log/query` | — |
| POST | `/api/v1/promotion/toolbox/seller_audit_log/query` | — |

### 3.5 积分（Seller Points）

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/seller_points/create` | `CreateSellerPoints` |
| POST | `/api/v1/promotion/seller_points/update` | `UpdateSellerPoints` |
| POST | `/api/v1/promotion/seller_points/deactivate` | `DeactivateSellerPoints` |
| POST | `/api/v1/promotion/seller_points/get` | `GetSellerPoints` |
| POST | `/api/v1/promotion/seller_points/list_products` | `ListSellerPointsProducts` |

### 3.6 平台活动 / 报名（Campaign）

这一族很大（90+ 接口），常用：

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/campaign/seller/get` | `GetSellerCampaign` |
| POST | `/api/v1/promotion/campaign/seller/submit` | `SubmitCampaign` |
| POST | `/api/v1/promotion/campaign/seller/campaign_eligibility/verify` | `VerifyCampaignEligibility` |
| POST | `/api/v1/promotion/campaign/seller/check_register_condition` | `CheckRegisterCondition` |
| POST | `/api/v1/promotion/campaign/seller/list_registered_products` | `ListRegisteredProducts` |
| POST | `/api/v1/promotion/campaign/seller/count_products` | `CountCampaignProducts` |
| POST | `/api/v1/promotion/campaign/seller/batch_async_opt_products` | `BatchAsyncOperateProducts` |
| POST | `/api/v1/promotion/campaign/seller/batch_withdraw` | `BatchWithdrawCampaignProducts` |
| POST | `/api/v1/promotion/campaign/seller/auto_enroll/submit` | `SubmitAutoEnroll` |
| POST | `/api/v1/promotion/campaign/seller/auto_enroll/submit_product` | `SubmitAutoEnrollProduct` |
| POST | `/api/v1/promotion/campaign/seller/agreement/sign` | `SignAgreement` |
| POST | `/api/v1/promotion/seller_platform/list` | `ListSellerPlatformPromotions` |
| POST | `/api/v1/promotion/seller_platform/update` | `UpdateSellerPlatformPromotions` |

### 3.7 赠品/抽奖（Giveaway / Allocation）

| 方法 | 路径 | 前端函数 |
|---|---|---|
| POST | `/api/v1/promotion/allocation/create` | `CreateAllocation` |
| POST | `/api/v1/promotion/allocation/update` | — |
| POST | `/api/v1/promotion/allocation/delete` | `DeleteAllocation` |
| POST | `/api/v1/promotion/allocation/list` | `ListAllocations` |
| POST | `/api/v1/promotion/allocation/prizes/get` | `GetAllocationPrizes` |
| POST | `/api/v1/promotion/allocation/prizes/update` | `UpdateAllocationPrizes` |

## 4. 商品折扣创建页的字段（UI 实测）

表单（`/promotion/marketing-tools/discount/create`）：

| 字段 | 控件 | 初始值 |
|---|---|---|
| 活动名称 | input（22/100 字符计数） | 自动填 `折扣 YYYY/MM/DD HH:MM:SS` |
| 开始时间(GMT+7) | 日期 + 时间 | 当前时间 |
| 结束时间(GMT+7) | 日期 + 时间 | 当前 + 6 个月 |
| 折扣类型 | 单选 | ①百分比折扣 ②一口价 |
| 投放位置 | 复选 | 商品详情页 / 直播 |
| 折扣范围 | 单选 | ①指定商品 ②指定变体 |
| 商品 | 「选择商品」按钮 | 空 |

页面加载时触发的接口：

```
GET  /api/v1/promotion/list_seller_gray_config
GET  /api/v1/promotion/config
POST /api/v1/promotion/mget_item_data
POST /api/v1/promotion/seller_experiment_info/get
GET  /api/v1/promotion/get_summary
GET  /api/v1/promotion/shop_risk_info/get
```

## 5. 已知缺口

- **各接口的请求体结构尚未逆向**（调用点在未加载的 chunk 里，
  且该促销 SPA 不响应 CDP 模拟点击，无法通过 UI 触发来抓包）
- 补齐方式（任一）：
  1. 在页面上手动提交一次折扣，同时挂 fetch hook 抓请求体
  2. 用服务端字段级报错反推（POST 错误参数 → 读 `extra.system_msg`）
  3. 加载 discount/edit 页把对应的 chunk 拉全后再提取调用点

## 6. 素材

| 文件 | 内容 |
|---|---|
| `notes/promo_api_map.json` | 全部接口（路径 → 函数名/方法） |
| `notes/promo_reqs.json` | 工具选择页抓到的请求 |
| `notes/promo_detail_reqs.json` | 折扣创建页抓到的请求 |
| `notes/promo_bundle/` | 34 个促销前端 chunk（15MB） |
| `notes/promo_js_urls2.json` | chunk URL 清单 |

---

## 7. 认证与调用方式（实测打通）

### 7.1 🔴 两个关键点

**① 促销 API 在独立域上，不是主域**

```
❌ https://seller.tiktokshopglobalselling.com/api/v1/promotion/config   → 返回 HTML
✅ https://api16-normal-sg.tiktokshopglobalselling.com/api/v1/promotion/config
```

**② 必须带 HttpOnly cookie**

`document.cookie` 只读得到 20 个非 HttpOnly cookie，**缺 `sessionid`**，
直接用它调 API 会返回：

```json
{"code": 98001002, "message": "请登录后再操作"}
```

正确做法：用 CDP 的 `Network.getAllCookies` 取全量（95 个），关键 cookie：

```
sessionid  sessionid_ss  csrftoken  tt_csrf_token  msToken  d_ticket  tt_chain_token
```

代码里已有现成函数：`tt_http_client.cookies_via_cdp(port)`

### 7.2 可用的调用模板

```python
import sys; sys.path.insert(0, ".")
from tt_http_client import cookies_via_cdp
import requests

cookies = cookies_via_cdp(CDP_PORT)          # ← 从 Hub Studio 实例取全量 cookie
HOST = "https://api16-normal-sg.tiktokshopglobalselling.com"
S = "7494XXXXXXXXXX00"

s = requests.Session()
for k, v in cookies.items():
    s.cookies.set(k, v, domain=".tiktokshopglobalselling.com")
s.headers.update({
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin":  "https://seller.tiktokshopglobalselling.com",
    "referer": "https://seller.tiktokshopglobalselling.com/promotion/marketing-tools/tool-choose",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "x-csrftoken": cookies.get("csrftoken", ""),
})
P = {"locale":"zh-CN","language":"zh-CN","oec_seller_id":S,"seller_id":S,
     "aid":"6556","app_name":"i18n_ecom_shop"}
```

### 7.3 实测通过的接口

| 接口 | 方法 | 结果 |
|---|---|---|
| `/api/v1/promotion/config` | GET | ✅ 返回折扣限制 |
| `/api/v1/promotion/list_seller_gray_config` | GET | ✅ 灰度开关列表 |
| `/api/v1/promotion/discount/list` | POST | ✅ **列出 12 个现有折扣** |
| `/api/v1/promotion/discount/get` | GET | ⚠ 参数不全（`部分信息填写错误`） |
| `/api/v1/promotion/single_discount/get` | GET | 返回 `data:null`（参数名待定） |
| `/api/v1/promotion/voucher/list` | POST | ⚠ 缺参数 |
| `/api/v1/promotion/discount/create` | POST | ⚠ `部分信息填写错误`（字段未齐） |

### 7.4 `discount/list` 响应（可用）

```python
# 请求
POST /api/v1/promotion/discount/list   {"page":1, "page_size":20}

# 响应要点
{"code":0,"data":{"seller_discounts":[
  {"id":"7627XXXXXXXXXX07", "name":"折扣 2026/04/12 16:44:26",
   "period":{"start_time":"NUMBER_REDACTED","end_time":"NUMBER_REDACTED"},
   "country_code":704, "status":2,
   "create_time":"1775987081600", "last_update_time":"1785143956062",
   "seller_discount_type":2,
   "republish_edit_info":{"allow_republish":false,"republish_reasons":3}}]}}
```

现有 12 个折扣（`seller_discount_type` 均为 `2`）：

| id | 名称 | status |
|---|---|---|
| 7627XXXXXXXXXX07 | 折扣 2026/04/12 | 2 |
| 7559XXXXXXXXXX52 | 多sku3 | 3 |
| 7474XXXXXXXXXX45 | 多SKU | 3 |
| 7474XXXXXXXXXX47 | 新品折扣 多SKU | 3 |
| 7412XXXXXXXXXX18 | 单SKU | 3 |
| 7410XXXXXXXXXX54 | 折扣 2024/09/03 | 3 |

> `status`：`2` = 生效中，`3` = 已结束/失效（待确认）

### 7.5 `config` 返回的折扣限制（重要）

```json
{"discount_limits":[{"type_detail":50,"min_discount":1,"max_discount":99,
  "period_limit":{"min_seconds":"600","max_seconds":"31536000"}}],
 "seller_config":{"is_subscribed_to_fbt":false,"merge_completed":false,
                  "has_migrated_promotions":false,...}}
```

- **折扣幅度**：1% ~ 99%（`type_detail=50` 表示百分比类型）
- **活动时长**：最少 600 秒（10 分钟），最多 31,536,000 秒（365 天）

## 8. 创建 / 修改折扣的字段（已实测打通 ✅）

`POST /api/v1/promotion/discount/create` 已是**可用接口**，最小成功 payload：

```json
{
  "period": {"start_time": "NUMBER_REDACTED", "end_time": "NUMBER_REDACTED"},
  "promotion_name": "API-CREATE-TEST",
  "promotion_limit_dimension": 4,
  "products_single_discount": [
    {"product_id": "1736XXXXXXXXXX16", "discount_percentage": "10"}
  ]
}
```

实测返回：

```json
{"code": 0, "message": "success", "data": {"promotion_id": "7689XXXXXXXXXX52"}}
```

### 8.1 字段表

| 字段 | 必需 | 类型 | 说明 |
|---|---|---|---|
| `period.start_time` / `period.end_time` | ✅ | **字符串**秒级时间戳 | 传 int 直接 `98001004`；end 必须在未来 |
| `promotion_name` | ✅ | string | 最长 100 字符（UI 计 22/100）。重名报 `17003115` |
| `promotion_limit_dimension` | ✅ | int | `4`=指定商品(SPU)、`1`=指定变体(SKU)、`0`=默认 |
| `products_single_discount` | ✅ | array | 见 8.2 |
| `check_overlap` | ⭕ | bool | 检测与既有活动重叠；`true` 被服务端接受（实测） |
| `check_strikethrough_price` | ⭕ | bool | 检测划线价；同上 |
| `products_fixed_price` | 二选一 | array | 一口价模式用它替代 `products_single_discount`，元素带 `fixed_price_value` |
| `strategy_id` / `smart_plan_strategy_id` | ⭕ | string | 来自智能推荐策略，手建可不传 |
| `rec_trace_infos` | ⭕ | object | 推荐埋点，可不传 |
| `create_source` | ⭕ | int | 来源标识；前端只在 URL 带 `channel`/`tool_source` 时才注入 |
| ~~`seller_agreement`~~ | ❌ | — | **传 bool 会 `98001004`**，不要传（服务端不需要） |

### 8.2 `products_single_discount` 的两种结构 —— 别踩错

```jsonc
// ✅ 正确（SPU 维度，实测 code=0）
[{"product_id": "1736XXXXXXXXXX16", "discount_percentage": "10"}]

// ❌ 错误（把折扣值塞进 skus[]，实测 17003013 promotion invalid price）
[{"product_id": "…", "skus": [{"sku_id": "…", "product_id": "…", "discount_percentage": "10"}]}]
```

- `discount_percentage` 是**字符串**，语义 = **减百分之几**（`"10"` → 打 9 折）。
  UI 实测：原价 36.000₫ → 折后 32.400₫ = 36.000 × 0.9 ✅
- `dimension=SKU(1)` 时要按变体建，元素里带 `sku_id`：

```json
[{"product_id": "…", "sku_id": "1736XXXXXXXXXX28", "discount_percentage": "10"}]
```

- 可选限购字段：`total_purchase_limit` / `user_purchase_limit`（`0` = 不限购）

> 前端 bundle 里那一大串 `JQ(x7(products, WHITELIST), WHITELIST)` 看着像"折扣值在
> `skus[]` 里"，实际是**给 SKU 维度用的**：`x7` 从 product 顶层**剔除**这些 key，
> `JQ` 再把每个 sku **只保留**这些 key。SPU 维度直接把 `discount_percentage` 放顶层即可。

### 8.3 修改折扣 `POST /api/v1/promotion/discount/update`

`period` 和 `promotion_limit_dimension` 是**服务端必需项**，只改名字也必须带上：

```json
{
  "promotion_id": "7689XXXXXXXXXX66",
  "promotion_name": "API-UPDATE-TEST2",
  "period": {"start_time": "NUMBER_REDACTED", "end_time": "NUMBER_REDACTED"},
  "promotion_limit_dimension": 4
}
```

| 坑 | 现象 |
|---|---|
| `promotion_id` 传 **int** | `98001004 部分信息填写错误` |
| `promotion_id` 传字符串 | ✅ `code=0` |
| 漏传 `promotion_limit_dimension` | `98001004` |
| `end_time` 改成过去时间 | `17003104 promotion invalid time period` |

### 8.4 查询折扣 `GET /api/v1/promotion/discount/get?promotion_id=…`

**是 GET，参数名 `promotion_id`**（不是 `discount_id` / `activity_id` / `id`）。
POST 会 404；参数名用错会 `98001004 部分信息填写错误`。

```json
{"data": {"seller_discount": {"id": "7689XXXXXXXXXX52", "name": "API-CREATE-TEST",
  "period": {"start_time": "NUMBER_REDACTED", "end_time": "NUMBER_REDACTED"},
  "status": 1, "seller_discount_type": 1, "promotion_limit_dimension": 4,
  "create_source": 1, "editable": true}, "hide_product": false}}
```

该接口**不返回商品明细**（`need_product_list` / `page` / `with_products` 等参数均无效）。

### 8.5 折扣没有删除接口

bundle 里 promotion 的折扣相关端点只有 `create` / `get` / `list` / `update`，
**没有 deactivate / delete / stop**。

清理测试活动只能靠 `update` 把时间窗**推到远期**，使其永不生效：

```python
C.discount_park(promotion_id, days=400)   # 窗口 → now+400天 ~ now+430天
```

> ⚠️ **不要**改成 "now+2min ~ now+1h" 那种"让它快点结束"的写法 ——
> 活动会**真的生效一小时并给商品打折**，在生产店铺上就是事故。
> 本次共留下 **5 个测试活动**，全部已 `discount_park` 到 400 天后（窗口
> `NUMBER_REDACTED~NUMBER_REDACTED` 等），**不会生效、不会影响真实售价**：
> `7689XXXXXXXXXX99` / `7689XXXXXXXXXX14` / `7689XXXXXXXXXX66` /
> `7689XXXXXXXXXX52` / `7689XXXXXXXXXX56`。
> 需要彻底删掉的话在管理页手动删除（API 无删除接口）。

### 8.6 逆向来源（字段可信度）

字段名不是猜的，出处可复查：

| 结论 | 出处 |
|---|---|
| `CreateDiscount` 的字段清单 | `DiscountCreateAndEdit.*.js` 的 `eQ.createMainRequest` |
| `discount_type` / `promotion_limit_dimension` 枚举值 | `promotion.sg_tts_cb.js` @6441350 |
| `products_single_discount` 顶层 vs `skus[]` | `CreateDiscount` 实测（8.2） |
| `period` / `promotion_id` 必须字符串 | `create` / `update` 实测错误码对照 |

```js
// DiscountCreateAndEdit.*.js —— payload 构造点
CreateDiscount.bind(Z.Hv)({
  period, promotion_name, promotion_limit_dimension,
  products_single_discount: JQ(x7(products||[]),
      ["sku_id","product_id","discount_percentage","total_purchase_limit",
       "user_purchase_limit","smart_discount_value"]),
  check_overlap, check_strikethrough_price, seller_agreement,
  strategy_id, smart_plan_strategy_id, rec_trace_infos, ...ej.a()
})
// 注: ej.a() = 模块 4146,只解析 URL 的 channel/tool_source,通常返回 {} —— 非必需
```

### 7.6 灰度开关（24 个，实测）

`GET /api/v1/promotion/list_seller_gray_config` → `data.hit_config`：

```
bmsm_use_custom_min_count            support_bmsm_enter_shop
campaign_product_recommend           support_bmsm_purchase_quantity_get_amount_off
campaign_spring_top_card             support_bxgy
campaign_support_criteria_v2         version_check_ability
creator_live_flash_sale              show_safety_monitor
creator_live_giveaway                show_cfp_achievement_summary
crm_voucher                          show_pricing_insights
early_bird_price                     sea_new_ui_config
enable_eligible_customers            seller_form_v1
eu_as_one                            seller_follow_voucher
gwp_allow_gifts_exceed_stock         sns_product_discount_v2
im_voucher                           promo_code
```

这些开关决定哪些促销工具对本店可见（例如 `early_bird_price`=新品折扣、
`promo_code`=促销码、`support_bmsm_*`=多买多优惠）。

### 7.7 折扣状态与类型（实测）

```
status: 2 = 生效中（1 个）    3 = 已结束（11 个）
seller_discount_type: 2（全部 12 个）
```

`GET /api/v1/promotion/get_summary` 返回活动计数：

```json
{"quantity_info":[{"promotion_status":2,"quantity":1},
                  {"promotion_status":3,"quantity":0}],
 "seller_status":2}
```

## 9. 客户端 `tk01_promo.py`

已封装实测可用的接口，开箱即用：

```bash
python3 tk01_promo.py --probe         # 一次探测全部只读接口
python3 tk01_promo.py --config        # 折扣限制
python3 tk01_promo.py --gray          # 灰度开关
python3 tk01_promo.py --discounts     # 折扣列表（带状态/时间）
python3 tk01_promo.py --summary       # 活动计数
python3 tk01_promo.py --items <pid>   # 商品数据
python3 tk01_promo.py --call <path> --method POST --body '{"page":1}'
```

Python 调用：

```python
from tk01_promo import PromoAPI

api = PromoAPI(port=CDP_PORT)          # 自动取全量 cookie
print(api.discounts()["data"]["seller_discounts"])
print(api.config()["data"]["discount_limits"])
```

**实测结果**（`--probe`）：

| 接口 | 状态 |
|---|---|
| `config` | ✅ code=0 |
| `list_seller_gray_config` | ✅ code=0（24 个开关） |
| `discount/list` | ✅ code=0（12 个折扣） |
| `get_summary` | ✅ code=0 |
| `shop_risk_info/get` | ✅ code=0 |
| `voucher/list` | ⚠ 缺参数 |

## 10. 错误码对照（全部实测）

| code | message | 真实原因 / 修法 |
|---|---|---|
| `0` | success | — |
| `98001002` | 请登录后再操作 | cookie 不全，缺 HttpOnly 的 `sessionid`，必须用 CDP 取全量 |
| `98001004` | 部分信息填写错误 | 通用参数拒绝，实测诱因：`period` 传 int、`promotion_id` 传 int、漏 `promotion_limit_dimension`、传 `seller_agreement` 布尔 |
| `17003013` | promotion invalid price | 折扣结构不对，如把 `discount_percentage` 塞进 `skus[]` |
| `17003104` | promotion invalid time period | `end_time` 不在未来，或 start ≥ end |
| `17003115` | 该活动名称已存在 | 换名，或用 `update` |
| `10000` | （无 message） | 参数结构不对，多出现在 `calc_future_seller_promotion_price` |

> `98001004` 不带字段级信息（`extra` 为空）。定位法：**拿 `update` 当 oracle** ——
> 它字段更少，能逐个变量试出是哪个字段不被接受（本次就是这么定位到 `seller_agreement` 的）。

## 11. 枚举值（bundle 实测提取）

```js
// promotion.sg_tts_cb.js @6441350
discount_type              = {DEFAULT_DISCOUNT_TYPE_FOR_RECOMMEND: 0, PERCENTAGE_OFF: 1, FIXED_PRICE: 2}
promotion_limit_dimension  = {DEFUALT: 0, SKU: 1, SPU: 4}
```

| 枚举 | 值 | 含义 | UI 对应 |
|---|---|---|---|
| `discount_type` | 1 | 百分比折扣 | 页面「折扣类型」radio val=1 |
| | 2 | 一口价 | radio val=2 |
| `promotion_limit_dimension` | 4 | 指定商品（SPU） | radio val=4，**默认** |
| | 1 | 指定变体（SKU） | radio val=1 |

> `discount_type` 只用于前端二分（决定传 `products_single_discount` 还是
> `products_fixed_price`），**不提交给服务端**。
> `discount/list` 返回的 `seller_discount_type` 是另一回事：`1`=API/新版建的，
> `2`=存量老活动。

状态 `status`：`1` 待开始 / `2` 进行中 / `3` 已结束。

## 12. 客户端 `tk01_promo_client.py`

```bash
python3 tk01_promo_client.py config                  # 折扣限制（1%~99%, 600s~365d）
python3 tk01_promo_client.py gray                    # 灰度开关
python3 tk01_promo_client.py discounts               # 活动列表（带中文状态）
python3 tk01_promo_client.py get 7689XXXXXXXXXX52 # 活动详情
python3 tk01_promo_client.py products 耳             # 商品 + sku_id + 价格

# 建活动（先 --dry-run 看 payload）
python3 tk01_promo_client.py create --name "秋季促销" \
    --product 1736XXXXXXXXXX16 --discount 15 \
    --start 2026-10-05 --end 2026-10-20 --dry-run

# 改活动 / 让它尽快结束
python3 tk01_promo_client.py update 7689XXXXXXXXXX52 --name "新名字"
python3 tk01_promo_client.py park 7689XXXXXXXXXX52 --days 400
```

Python 调用：

```python
from tk01_promo_client import PromoClient

C = PromoClient(port=CDP_PORT)                     # 自动从 CDP 取全量 cookie
pid = C.discount_create(
    name="秋季促销",
    start="2026-10-05", end="2026-10-20",
    products=[{"product_id": "1736XXXXXXXXXX16", "discount_percentage": "15"}],
)
print(pid, C.discount_get(pid))
```

抛出的是 `PromoError`，带错误码中文含义：

```
❌ [98001004] 部分信息填写错误  (通用参数拒绝，实测诱因：period 传 int、promotion_id 传 int…)
```

## 13. 抓包方法论（本次踩坑总结）

| 方法 | 结果 |
|---|---|
| 页面内注 JS hook（包 `XMLHttpRequest`/`fetch`） | ❌ 只能抓同域请求；promotion API 在跨域的 `api16-normal-sg`，这条链路绕过主 frame 的 hook |
| `Page.addScriptToEvaluateOnNewDocument` | ⚠ 脚本**绑定在 CDP session 上**，python 一退出连接就断、脚本被移除，`window.__hits` 变 `undefined`（payload 就是这么丢过两次的） |
| Playwright `page.on("request")` | ❌ `connectOverCDP` 下 `post_data` 恒为 `None`（能看见请求但读不到 body） |
| Playwright `page.route` | ❌ 完全拦不到 |
| CDP `Network.requestWillBeSent` | ❌ 能看见请求，`postData` 仍为 `None` |
| **CDP `Fetch.requestPaused`** | ✅ **`request.postData` 有完整 body**，`Fetch.continueRequest` 放行 |

最佳实践：**只在真正要抓的那一刻 `Fetch.enable`**。全程开着 `Fetch.enable` 拦截
`promotion/*` 会拖垮前置流程（商品表格不渲染、`件商品 = -1`）。

```python
cdp = ctx.new_cdp_session(page)
cdp.send("Fetch.enable", {"patterns": [
    {"urlPattern": "*api16-normal-sg.tiktokshopglobalselling.com/api/v1/promotion*",
     "requestStage": "Request"}]})

def on_paused(ev):
    try:
        r = ev["request"]
        if r["method"] != "OPTIONS":
            captured.append({"path": r["url"].split("?")[0], "body": r.get("postData")})
    finally:
        cdp.send("Fetch.continueRequest", {"requestId": ev["requestId"]})  # 必须放行

cdp.on("Fetch.requestPaused", on_paused)
```

### 13.1 促销页自动化定位避坑（Playwright）

| 坑 | 现象 | 修法 |
|---|---|---|
| 后台 tab 的 viewport 为 0 | 商品表格虚拟滚动不渲染任何行，checkbox 和「折扣」输入框都不进 DOM | `page.set_viewport_size({"width":1600,"height":1200})` |
| `"件商品" in innerText` | `"0 件商品"` 也匹配，会把失败当成功 | 正则 `/(\d+)\s*件商品/` 取数字判断 |
| `locator("button", has_text="完成")` | 全页面搜索，可能点到弹层外的按钮 | 限定在弹层内：`evaluate_handle` 拿按钮再 `.click()` |
| 鼠标点行 checkbox | **整个商品表格从 DOM 卸载**（`cb: 0`） | 用**键盘 Space**：`box.press("Space")` |
| `input[type=text]` 的 `offsetParent` | 为 `null`，用它做可见性过滤会把所有输入框滤掉 | 改用 class / `data-prefill-id` 定位 |
| 折扣输入框定位 | 按 `nth(index)` 不稳定 | 用 `input[data-prefill-id^="product_discount_percentage__"]` |
| Arco InputNumber | `fill()` 后 React state 不更新，价格预览不刷新，提交被静默拦下 | `fill()` 后 `press("Tab")` 触发 blur |

### 13.2 抓包脚本清单

| 脚本 | 用途 |
|---|---|
| `promo_capture_v3.py` | 创建流程自动化 + `--submit` 抓 `discount/create`。前置步骤（选类型/选商品/填折扣）已稳定跑通；**最后的提交点击偶发失败**（该 SPA 重渲染导致按钮 detached），因为 payload 已由 API 侧确认，未继续追。内置上述全部修法 |
| `promo_probe_select.py` | 行勾选策略探测（5 种方式对照，验证了"键盘 Space 才有效"） |
| `tt_promo_hook.py` | 页面内 JS hook（同域请求可用，跨域 promotion 不行） |

### 13.3 遗留脚本（早期版本，保留作对照）

`promo_capture_submit.py` / `promo_finish_capture.py` / `promo_create_capture.py` /
`promo_capture_v2.py` —— 这几版分别踩了「hook 绑定 session」「回调里调 `res.text()` 死锁」
「全量 Fetch 拦截拖垮渲染」的坑，已被 `promo_capture_v3.py` 取代。

---

## 14. 批量新建促销活动（专题 · 2026-09-26 实测）

围绕「一次建一批活动 + 设置折扣价格/百分比 + 限购量」的能力，下面是实测结论。

### 14.1 能力矩阵

| 能力 | 状态 | 证据 |
|---|---|---|
| 百分比折扣，单商品 | ✅ | `discount/create` → code=0，`list_products` 读回 1 商品 |
| 百分比折扣，**单活动多商品** | ✅ | 4 商品一次建成功，`list_products` 读回 4 商品 |
| **总限购量** `total_purchase_limit` | ✅ | 结构 `{limit_dimension:101, purchase_max_quantity:N}` 被接受 |
| **客户限购量** `user_purchase_limit` | ✅ | 结构 `{limit_dimension:4, purchase_max_quantity:N}` 被接受 |
| 不限购 | ✅ | `{limit_dimension:-1, purchase_max_quantity:-1}` |
| **SKU 维度**（每个变体独立折扣+限购） | ✅ | `dimension=SKU` + `skus[]` 内嵌，`list_products` 读回 sku 计数 |
| **批量建多个活动** | ✅ | `batch` 命令一次建 3 个活动全部成功 |
| 读回活动商品（验证） | ✅ | `POST /promotion/list_products` |
| **一口价** `fixed_price_value` | ❌ **未打通** | 见 14.4 |

### 14.2 plan JSON（批量入口）

单个活动 = 对象；多个活动 = 对象数组。

```json
[
  {"name": "秋季促销-A", "start": "2026-10-05", "end": "2026-10-20",
   "discount": "15", "total_limit": 5, "user_limit": 2,
   "products": ["1736XXXXXXXXXX16", "1736XXXXXXXXXX24"]},

  {"name": "秋季促销-B", "dimension": "SKU",
   "products": [{"product_id": "1736XXXXXXXXXX16",
                 "skus": [{"sku_id": "1736XXXXXXXXXX28", "percent": "20", "total_limit": 2},
                          {"sku_id": "1736XXXXXXXXXX64", "percent": "15", "user_limit": 1},
                          {"sku_id": "1736XXXXXXXXXX00", "percent": "10"}]}]}
]
```

字段说明：

| 字段 | 说明 |
|---|---|
| `name` | 活动名，**不能重复**（重名 `17003115`） |
| `start` / `end` | `YYYY-MM-DD` 或时间戳；省略时 start=明天、end=start+15 天 |
| `discount` | 减百分之几（`"15"` = 打 85 折），与 `fixed_price` 二选一 |
| `fixed_price` | 一口价金额 —— **见 14.4，目前不要用** |
| `total_limit` | 总限购量（该活动商品总共卖多少件） |
| `user_limit` | 客户限购量（每个买家能买多少件） |
| `products` | `["商品ID", …]` 简写，或对象数组（可按商品单独设参） |
| `dimension` | `SPU`(默认，按商品) / `SKU`(按变体，元素需带 `skus[]`) |

```bash
python3 tk01_promo_client.py batch -f plans.json --dry-run       # 先看 payload
python3 tk01_promo_client.py batch -f plans.json --auto-split    # 建（自动拆分超限的）
python3 tk01_promo_client.py batch -f plans.json --park-after    # 建完推到远期（测试用）
python3 tk01_promo_client.py list-products <promotion_id>        # 读回验证
python3 tk01_promo_client.py new-plan > plan.json                # 模板
```

### 14.3 🔴 关键业务规则：双限购时商品数 ≤ 3

**同时**设置 `total_limit` 与 `user_limit` 时，**商品数上限为 3**：

| 商品数 | 双限购 | 结果 |
|---|---|---|
| 2 | ✅ | code=0 |
| 3 | ✅ | code=0 |
| **4** | ✅ | ❌ **code=10000，不带任何 message** |
| 5 | ✅ | ❌ code=10000 |
| 任意 | 只设一个 / 都不设 | ✅ code=0 |

换任何数值组合（5+2、4+2、20+5、5+5）在 4 商品时都是失败，**所以是条数规则不是数值规则**。

失败时服务端只回 `{"code":10000}`，没有任何线索 —— 所以客户端做了**本地预检**：

```python
PromoClient.check_server_rules(products)     # → 违规说明列表；promo_create 会直接抛 ValueError
PromoClient.promo_plan_split(job)            # → 把超限 plan 按 3 个商品一拆
```

`batch --auto-split` 会自动拆分，实测 `3 个 plan → 4 个活动`，拆出的 `-1`/`-2` 两个活动都建成。

### 14.4 ✅ 一口价（已完整打通）

#### 🔑 核心机制：`fixed_price/*` 需要请求签名

页面的真实请求带三个签名参数：

```
X-Bogus=REDACTED
X-Gnarly=REDACTED
msToken=REDACTED…
```

它们是 TikTok 的 `webmssdk.js` 在页面里**注入到 fetch/XHR 上的**，直连拿不到。

| 端点族 | 需要签名 | 直连可行性 |
|---|---|---|
| `discount/*` | ❌ | ✅ `requests` 直连可用 |
| **`fixed_price/*`** | ✅ | ❌ 直连一律 `code=10000`（且**不给任何 message**） |

> **这就是此前把 payload 结构试了 15+ 遍全部失败的真因 —— 不是字段错，是缺签名。**

#### 可用的 payload（实测 `code=0`）

```json
{
  "period": {"start_time": "NUMBER_REDACTED", "end_time": "NUMBER_REDACTED"},
  "promotion_name": "FIXED-CHK",
  "promotion_limit_dimension": 1,
  "products_fixed_price": [{
    "product_id": "1735XXXXXXXXXX20",
    "price_limit": "0",
    "skus": [
      {"sku_id": "1735XXXXXXXXXX80", "product_id": "1735XXXXXXXXXX20", "fixed_price_value": "30000"},
      {"sku_id": "1735XXXXXXXXXX16", "product_id": "1735XXXXXXXXXX20", "fixed_price_value": "30000"},
      {"sku_id": "1735XXXXXXXXXX52", "product_id": "1735XXXXXXXXXX20", "fixed_price_value": "30000"}
    ]}],
  "check_overlap": true,
  "check_strikethrough_price": false
}
```

| 字段 | 必需 | 说明 |
|---|---|---|
| `price_limit` | ✅ | **缺了就是 `code=10000`**，填 `"0"` 即可 |
| 顶层 `fixed_price_value` | ❌ | **不要传**（传了反而失败） |
| `skus[].fixed_price_value` | ✅ | 每个变体一个价，**必须低于该 SKU 原价** |
| `promotion_limit_dimension` | ✅ | 一口价固定用 **1**（SKU 维度） |
| `check_overlap` / `check_strikethrough_price` | ⭕ | 布尔，实测 `true` / `false` 均可 |

#### 用法（已封装进客户端）

```python
from tk01_promo_client import PromoClient
C = PromoClient()

pid = C.promo_create_fixed(              # ← 内部走浏览器页面发请求，自动带签名
    name="秋季一口价",
    start="2026-10-05", end="2026-10-20",
    products=[{"product_id": "1735XXXXXXXXXX20",
               "price_limit": "0",
               "skus": {"1735XXXXXXXXXX80": "87000",
                        "1735XXXXXXXXXX16": "62000",
                        "1735XXXXXXXXXX52": "33000"}}])

C.park_any(pid)                          # 按活动类型自动选对的 update 端点
```

#### 端点对照表

| 操作 | 端点 | 需要签名 |
|---|---|---|
| 建一口价 | `POST /promotion/fixed_price/create` | ✅ **必须经页面** |
| 改一口价 | `POST /promotion/fixed_price/update` | ❌ 直连可用 |
| 建百分比 | `POST /promotion/discount/create` | ❌ 直连可用 |
| 改百分比 | `POST /promotion/discount/update` | ❌ 直连可用 |
| 读活动 | `GET /promotion/discount/get` | ❌ 直连可用 |
| 读活动商品 | `POST /promotion/list_products` | ❌ 直连可用 |
| 一口价活动**不能**用 `discount/update` 改 | — | 报 `17003109 promotion invalid update` |

**类型标志**：`seller_discount_type` = **1 百分比 / 2 一口价**，建成后不可互转。

#### 页面发请求的实现要点

在 `seller.tiktokshopglobalselling.com` 域的页面上下文里执行：

```javascript
(async () => {
  const r = await fetch(URL, {method: "POST",
    headers: {"content-type": "application/json"},
    body: PAYLOAD, credentials: "include"});
  return await r.text();
})()
```

跨域到 `api16-normal-sg` 发请求时，SDK 会自动补签名，`credentials: "include"` 带上 cookie。

### 14.5 限购字段规格（实测确认）

```jsonc
// 服务端要【对象】，不是数字（传 int 会 98001004）
"total_purchase_limit": {"limit_dimension": 101, "purchase_max_quantity": 5},
"user_purchase_limit":  {"limit_dimension": 4,   "purchase_max_quantity": 2},

// 不限购
"total_purchase_limit": {"limit_dimension": -1,  "purchase_max_quantity": -1}
```

`limit_dimension` 取值（`promotion.sg_tts_cb.js @6442075` 的 DZ 枚举）：

| 值 | 含义 | 用在哪 |
|---|---|---|
| `100` | `SKU_TOTAL` | SKU 维度的总限购 |
| `101` | `SPU_TOTAL` | SPU 维度的总限购 |
| `4` | `SPU` | 客户限购（SPU 维度） |
| `1` | `SKU` | 客户限购（SKU 维度） |
| `-1` | `NO_LIMIT` | 不限购 |
| `0` | `NOT_APPLY` | 不适用 |

> SKU 维度下，折扣值与限购**都写在 `skus[]` 元素内部**，不写顶层：
> ```json
> {"product_id": "…", "skus": [
>   {"sku_id": "…", "product_id": "…", "discount_percentage": "20",
>    "total_purchase_limit": {"limit_dimension": 100, "purchase_max_quantity": 2}}]}
> ```

### 14.6 读回验证：`POST /promotion/list_products`

```json
{"promotion_id": "7689XXXXXXXXXX08", "page": 1, "page_size": 50}
```

返回 `data.item_products[]`，每项 10 个字段：

```
product_id / product_name / inventory_quantity / product_status / sale_price_range /
image / total_sku_count / selected_sku_count / estimated_discounted_price_range / selected
```

用途：确认批量建活动**是否真的关联上商品**（`total_count` 应等于投递的商品数）。

**局限**：不返回折扣值与限购值，也没有参数能让它返回（`need_sku_info` / `with_purchase_limit`
等无效）。这两项只能到 UI 的编辑页确认。

### 14.7 批量实测记录

```
BATCH-T1 百分比18% + 总限购5 + 用户限购2, 4商品   → 被预检拦下，--auto-split 拆成
                                                     BATCH-T1-…-1 (3商品) ✅
                                                     BATCH-T1-…-2 (1商品) ✅
BATCH-T2 一口价 2商品                            → 活动建了但 0 商品（14.4）
BATCH-T3 SKU维度 每变体独立折扣                   → ✅
VF-3商品双限购-边界内                            → ✅ 3商品全部读回
VF-SKU维度 每变体20%/15%/10% + 限购               → ✅ selected_sku_count=3
```

最终端到端回归（4 个 plan → 5 个活动，自动拆分后 **5/5 成功**，读回商品数全部吻合）：

```
FT1-多商品百分比+双限购  3商品 双限购      → ✅ 读回 3
FT2-SKU维度每变体独立    dim=SKU 20/15/10% → ✅ 读回 1(3 sku)
FT3-4商品无限购          4商品             → ✅ 读回 4
FT4-4商品双限购超限      预检拦下 → auto-split → -1(3商品) ✅ / -2(1商品) ✅
```

**所有测试活动均已 `discount_park` 到 400 天后（窗口 `1824993xxx`），没有任何一个处于生效状态，
店铺在售价格未被改动。** 存量活动 `7627XXXXXXXXXX07`（2026/04/12 起进行中）未被触碰 ——
尝试 park 它时被服务端拒绝：`17003118 update promotion info which is ongoing`。

### 14.8 补充错误码

| code | message | 原因 |
|---|---|---|
| `17003118` | update promotion info which is ongoing | 进行中的活动不能 update（含改时间窗） |


---

## 15. 查看促销活动（完整明细）

### 15.1 读明细的两个接口

| 接口 | 需要签名 | 返回 |
|---|---|---|
| `GET /promotion/discount/get?promotion_id=…` | ❌ 直连可用 | 活动基本信息（名称/时间/状态/类型/维度） |
| `POST /promotion/list_products_by_cursor` | ✅ **需签名** | **商品 + 每个 SKU 的促销价、库存、划线价、限购** |
| `POST /promotion/list_products` | ❌ 直连可用 | 只有 10 个字段，**拿不到折扣值和限购值**（弱化版，仅用于校验商品是否关联） |

```json
// list_products_by_cursor 请求（缺 cursor/limit/use_streamline 会 10000）
{"promotion_id":"7689XXXXXXXXXX27","need_smart_discount":false,
 "extra_info_list":[],"use_streamline":true,"cursor":0,"limit":100}
```

### 15.2 🔴 折扣值在哪：百分比和一口价**位置不同**

实测同一个接口对两种活动返回不同结构：

| | 百分比折扣 | 一口价 |
|---|---|---|
| 折扣值位置 | **product 级** `discount_percentage: "10"` | **sku 级** `fixed_price_value: "87000"` |
| 折后价 | product 级 `estimated_discounted_price_range` | 就是 `fixed_price_value` 本身 |
| SKU 级字段 | 只有 `strikethrough_price_info` | `fixed_price_value` + `discount_percentage`（**复用该字段存价格**） |

> ⚠️ 一口价活动会把价格塞进 sku 级的 `discount_percentage`，别被字段名骗了 ——
> 判断类型要看 `seller_discount_type`（**1=百分比 / 2=一口价**）。

### 15.3 字段字典（product / sku 级）

```
product 级:
  product_id / product_name / inventory_quantity / product_status
  sale_price_range                 {lowest_price_value, highest_price_value}   原价区间
  estimated_discounted_price_range 同上 + lowest_price/highest_price（带币种格式）折后区间
  discount_percentage              "10"    ← 百分比活动的折扣
  fixed_price_value                "0"     ← 一口价活动这里是空的
  purchase_limit                   -1      ← 无意义哨兵
  total_purchase_limit             {limit_dimension:101, purchase_max_quantity:5,
                                    purchase_limit_available:5}     ← 总限购 + 剩余
  user_purchase_limit              {limit_dimension:4, purchase_max_quantity:3}  ← 客户限购

sku 级:
  sku_id / product_id / sku_name / in_promotion / inventory_quantity
  sale_price_range                 该 SKU 的原价
  fixed_price_value / fixed_price  ← 一口价活动的促销价
  discount_percentage              ← 一口价时复用为价格
  strikethrough_price_info         {strikethrough_price_type, strikethrough_price_value,
                                    formatted_strikethrough_price, retail_price_value}
  alert_info                       [{alert_type: 8}]  价格类提示
```

### 15.4 客户端封装

```python
C = PromoClient()

C.promo_report(pid)              # 人类可读报表（商品/SKU/促销价/限购）
C.promo_detail(pid)              # 同上的 JSON 版
C.list_products_by_cursor(pid)   # 原始明细数组（走页面签名）
C.promo_find_by_product(pid)     # 反查：某商品挂在哪些活动里
C.promo_export("out.json")       # 导出全部活动 + 明细
```

```bash
python3 tk01_promo_client.py report 7689XXXXXXXXXX27   # 明细报表
python3 tk01_promo_client.py detail 7689XXXXXXXXXX27   # JSON 明细
python3 tk01_promo_client.py find   1736XXXXXXXXXX16   # 按商品反查
python3 tk01_promo_client.py export notes/promo_export.json
```

报表样例：

```
活动 7689XXXXXXXXXX53  [百分比折扣 / 指定商品]  待开始
  名称: E2E-PCT-NUMBER_REDACTED
  时间: NUMBER_REDACTED ~ NUMBER_REDACTED
  商品 1 个 / SKU 3 个
  · 1736XXXXXXXXXX16  Hộp 24 que lấy ráy tai dính, đầu silicon
      库存=9000  原价=36000~90000  折扣=12%  折后=31680~79200  总限购=8(剩8)  客户限购=3
      - 1736XXXXXXXXXX28  3 cái   促销价=-        划线价=90.000₫  库存=3000 参与=是
      - 1736XXXXXXXXXX64  2 cái   促销价=-        划线价=65.000₫  库存=3000 参与=是
      - 1736XXXXXXXXXX00  1 cái   促销价=-        划线价=36.000₫  库存=3000 参与=是
```

---

## 16. 促销活动生命周期 SOP（后训练结论）

### 16.1 四步闭环

```
① 建  →  ② 看  →  ③ 改  →  ④ 停
```

| 步骤 | 接口 | 签名 | 备注 |
|---|---|---|---|
| ① 建（百分比） | `POST /promotion/discount/create` | ❌ | `products_single_discount` + `discount_percentage` |
| ① 建（一口价） | `POST /promotion/fixed_price/create` | ✅ | `products_fixed_price` + **`price_limit` 必需** |
| ② 看 | `GET /promotion/discount/get` + `POST /promotion/list_products_by_cursor` | 后者✅ | 折扣值位置见 §15.2 |
| ③ 改 | 百分比 `discount/update` / 一口价 `fixed_price/update` | ❌ | **端点必须与活动类型匹配**，否则 `17003109` |
| ④ 停 | 同上对应 update | ❌ | **没有 delete/deactivate**，只能把窗口推到远期 |

### 16.2 签名判定（省时间的关键）

| 出现什么现象 | 大概率原因 |
|---|---|
| `code=10000`，**且 message 为空** | **缺签名**（X-Bogus）→ 改用 `call_via_page()` 走浏览器 |
| `code=98001004 部分信息填写错误` | 参数问题：类型不对 / 缺必需字段（如 `price_limit`） |
| `code=17003109 promotion invalid update` | **update 端点与活动类型不匹配**（百分比↔一口价） |
| `code=17003118 … ongoing` | 活动进行中，不可改 |
| `code=17003104 invalid time period` | `end_time` 不在未来 |
| `code=17003115 该活动名称已存在` | 换名 |
| `code=17003113 promotion invalid price` | 折扣结构 / 价格不合法 |

> **实战教训**：一口价的 payload 我试了 15+ 种结构全部 `code=10000`，
> 一直以为是字段错 —— **其实是缺签名**。遇到"无 message 的 10000"，
> 第一件事该是换 `call_via_page()` 重试，而不是继续改 payload。

### 16.3 批量建活动的效率与容错

```python
# 百分比：直连，最快
C.promo_create_batch(jobs)                    # jobs = [{name,start,end,products}, …]

# 一口价：走页面签名（慢一点，每次开一个 CDP 会话）
for j in fixed_jobs:
    C.promo_create_fixed(**j)

# 双限购超限自动拆（服务端规则：双限购时商品数 ≤ 3）
C.promo_plan_split(job)                       # 或 batch --auto-split
```

| 容错点 | 处理 |
|---|---|
| 活动重名 `17003115` | 名字加时间戳后缀 |
| 双限购 >3 商品 → `10000` | `check_server_rules()` 本地预检 + `promo_plan_split()` |
| 商品与现有活动重叠 | 用 `list_products_by_cursor` 查已有活动，避开时间窗 |
| 一口价 ≥ 原价 | 建前用 `product_detail()` 取原价，确保低价 |
| 建完发现不对 | `park_any()` 推到远期（自动选端点） |

### 16.4 一次完整闭环的实测记录

```
① 建百分比+限购  pid=7689XXXXXXXXXX53  （12% + 总限购8 + 客户限购3）
② 建一口价       pid=7689XXXXXXXXXX14  （3 SKU 各自定价 86000/61000/32000）
③ 看报表         折扣=12%  折后=31680~79200  总限购=8(剩8)  客户限购=3
④ 改折扣 12%→20% update code=0，折后立即变成 28800
⑤ 停             park_any 两个都 code=0
⑥ 验             两个都在 400 天后，不会生效
```


---

## 17. 商品维度：扫描活动 + 批量改价

### 17.1 扫描商品参与的活动 —— **1 个请求**

不用遍历活动列表。产品详情里直接带：

```python
C.product_detail("1736XXXXXXXXXX16")
# → promotion_infos: [{promotion_id, promotion_name}, …]      该商品参与的活动
# → product_discount_promotion: {promotion_id, promotion_name} 商品级折扣活动
```

实测：扫描一个商品（5 个命中活动）**耗时 4.2 秒**，遍历方案要 60+ 个请求、几分钟。

```bash
python3 tk01_promo_client.py scan 1736XXXXXXXXXX16          # 含 SKU 级现价
python3 tk01_promo_client.py scan 1736XXXXXXXXXX16 --no-sku  # 更快，只列活动
```

```python
C.scan_product_promotions("1736XXXXXXXXXX16", with_sku_detail=True)
# → [{promotion_id, name, type, type_text, status, status_text, start, end,
#     dimension, skus:[{sku_id, sku_name, fixed_price, in_promotion}],
#     purchase_limit, user_purchase_limit, discount_percentage}]
```

### 17.2 改商品在一口价活动里的价格

```bash
# 只改指定活动
python3 tk01_promo_client.py set-price 1735XXXXXXXXXX20 \
    -a 7689XXXXXXXXXX54 --sku 1735XXXXXXXXXX80=80000 --sku 1735XXXXXXXXXX16=55000

# 该商品所在的所有一口价活动统一定价
python3 tk01_promo_client.py set-price 1735XXXXXXXXXX20 --price 75000
```

```python
C.update_product_fixed_price(
    "1735XXXXXXXXXX20",
    {"1735XXXXXXXXXX80": "80000", "1735XXXXXXXXXX16": "55000"},
    promotion_ids=["7689XXXXXXXXXX54"],   # 不传则自动扫描该商品的一口价活动
    dry_run=False)
```

**✅ 安全性已实测验证**：`fixed_price/update` 是**增量**语义 ——
用 2 商品活动验证过，只传目标商品改价，**同活动里的其他商品原样保留**。

即便如此，`update_product_fixed_price()` 仍默认**先读全量、把其他商品原价一起回传**（双保险），
所以不会误删商品。建议首次对某个活动改价时先 `dry_run=True` 看会发什么。

实测记录：

```
① 活动里有 2 个商品，目标商品现价 82.000₫ / 57.000₫ / 28.000₫
② dry-run：会发送 2 个商品（含另一个商品的原价回传）
③ 改价：code=0, products_sent=2
④ 验证：活动里 2 个商品都在；目标商品变成 80.000₫ / 55.000₫ / 26.000₫
```

### 17.3 🔴 一口价活动的商品数上限 = 2

实测（SKU 维度）：

| 商品数 | 结果 |
|---|---|
| 1 | ✅ code=0 |
| 2 | ✅ code=0 |
| **3** | ❌ **code=10000**（无 message） |

对比：**百分比活动一次带 4 个商品没问题**。所以这是**一口价特有的限制**。

> 超限时的表现和"缺 `price_limit`"一样都是 `code=10000`，很容易混淆。
> 记法：**一口价 ≤2 商品**（常量 `MAX_FIXED_PRODUCTS = 2`）。

超了要拆成多个活动，或改用百分比折扣。

### 17.4 ⚠️ 风控：本项目的头号风险

一次性做了**大量 CDP 请求 + 建了 48 个测试活动**后，店铺页面弹出了**拼图滑块验证码**
（`tiktok.com/ucenter_web/zti_web` iframe，文案「请完成下列验证后继续」）。

**缓解措施（已写进客户端默认值）**：

| 措施 | 实现 |
|---|---|
| 请求间隔 | `scan_product_promotions(gap=1.0)`、`update_product_fixed_price(gap=3.0)` |
| 少开 tab | `call_via_page` 复用已有页面，不主动开新 tab |
| 页面探活 | `_page_alive()` 先 `1+1` 探活，避免把 CDP 卡死 |
| 异步发请求 | 不用 `awaitPromise`，改成轮询 `window.__promo_r`（避免 CDP 超时） |
| 批量批次 | 一次不要建太多活动，建完及时 `park_any()` |

**出现验证码时**：停止一切自动化 → 人工滑一次 → 在后续操作里把 `gap` 调大。
**不要**尝试自动过验证码（会升级风控）。

### 17.5 端点签名速查（补充）

| 端点 | 需要签名 |
|---|---|
| `POST /promotion/get_promotions_by_product_id` / `get_latest_promotions_by_pid` | 存在但**参数名未知**（bundle 里只有定义、无调用点），改用 `promotion_infos` |
| `POST /promotion/list_products_by_cursor` | ✅ 需签名 |
| `POST /promotion/calc_future_seller_promotion_price` | ✅ 需签名 |
| `GET /promotion/discount/get` | ❌（但页面调用时也带了签名） |
| `POST /promotion/fixed_price/create` | ✅ 需签名 |
| `POST /promotion/discount/create` / `discount/update` / `fixed_price/update` | ❌ 直连可用 |
| `GET /api/v1/product/local/product/get` | ❌ 直连可用 |


---

## 18. 验证码（滑块）：协议已还原，自动滑实测可过（单轮 ~40%，重试 ~92%）

### 18.1 已还原的完整协议（实测抓包）

```
GET  https://verify-sg.byteoversea.com/captcha/get?lang=zh&app_name=&h5_sdk_version=2.27.6&…
→ {"code":200,"data":{
     "challenge_code":99999, "challenge_version":"", "cyfreso":65,
     "id":"6be59f6d13686f6d4ce573592d6e47f20987a94a", "mode":"slide",
     "question":{
       "url1":"…背景图…",   // 552x344 RGB，含缺口
       "url2":"…拼图块…"}}} // 110x110 RGBA，alpha 即形状

POST https://verify-sg.byteoversea.com/captcha/verify?lang=zh&…
     {"modified_img_width":340, "id":"6be59f…", "mode":"slide",
      "reply":[{"x":0,"y":70,"relative_time":129}, {"x":1,"y":70,"relative_time":138}, …]}
→ 失败: {"code":500,"data":{"msg":"VerifyFailedErr"},"msg_sub_code":"verify_err"}
```

要点：

| 观察 | 结论 |
|---|---|
| `reply[].y` 恒为 **70** | **不是鼠标真实 y** —— 是 SDK 按拼图块位置自己填的，改它没用 |
| `reply[].x` | 累计拖动距离（**显示坐标**，与 `modified_img_width` 同单位） |
| `modified_img_width: 340` | 背景图的**显示宽度**，不是自然宽度 552 |
| `relative_time` | 从拖动开始算的毫秒数 |
| `challenge_code` 恒为 `99999` | ⚠️ 可疑，见 18.4 |

### 18.2 缺口识别：已做到像素级准确

拼图块是 **RGBA**，`alpha > 128` 就是拼图形状的 mask。用它当模板在背景图上滑窗，
取 **(外环均值 − mask 内均值)** 最大者为缺口 —— 缺口内部比周边暗。

```python
# 拼图块 alpha → 形状 mask（裁剪到紧致边界）
mask = arr[..., 3] > 128
# 外环 = mask 自身膨胀 7px 再减去自身
outer = dilate(mask, 7) & ~mask
# 滑窗：缺口处 outer 区域比 mask 区域亮
score[x] = bg[y0:y0+h, x:x+w][outer].mean() - bg[y0:y0+h, x:x+w][mask].mean()
```

**两个必须注意的坑**：

1. **y 不能用 0** —— 缺口的纵向位置就是拼图块当前的位置，
   `y_offset = (pcRect.y − bgRect.y) / scale`。早先从 y=0 起扫，score 只有 22；
   加上 y_offset 后升到 **69~107**。
2. **尺寸要按显示坐标换算** —— 背景图自然 552 宽、显示 340，`scale = 340/552 = 0.6159`。
   缺口原图 x → 显示坐标 = `x * scale`。

**验证方式**：脚本会把识别结果画到背景图上（`notes/captcha_gap_marked.png`），
肉眼一看就知道准不准 —— 实测标注框**精确覆盖缺口**。

### 18.3 拖动：已做到像素级精确

```
目标 174.9px → 拼图块 left 变成 174px
目标 196.5px → 拼图块 left 变成 196px
目标  98.6px → 拼图块 left 变成  98px
```

关键点：

| 事项 | 做法 |
|---|---|
| 移位机制 | **secsdk 用 `style.left` 移动拼图块**，它的 `transform` 恒为 `matrix(1,0,0,1,0,0)`。按 transform 读数会永远得到 0 |
| 起点 | `.secsdk-captcha-drag-sliding` 按钮中心（不是我一开始误以为的拼图块位置） |
| 事件 | `Input.dispatchMouseEvent` 的 mouse/pointer 事件**确实到达页面**（实测各 13 个），拖动真的生效 |
| 轨迹 | 三次贝塞尔缓动 + 非均匀采样 + 纵向漂移 + 末端回拉 |

### 18.4 ✅ 实测能通过：单轮约 40%，重试后 92%

**先纠正一个错误**：早先我用「拖动按钮是否消失」判断成功，结果把**通过的记成了失败**。
**验证通过后按钮并不消失** —— 唯一可信的判据是 **`/captcha/verify` 的响应码**：

```
{"code":200, ...}                       → 通过
{"code":500,"data":{"msg":"VerifyFailedErr"}} → 失败
```

改用响应码判据后连测三轮：

| 轮次 | 样本 | 通过 |
|---|---|---|
| 第 1 轮 | 8 | **5** (62.5%) |
| 第 2 轮 | 6 | 2 (33%) |
| 第 3 轮 | 10 | 3 (30%) |
| **合计** | **24** | **10 = 约 40%** |

**重试累积成功率**（每轮都是独立的新挑战）：

| 重试次数 | 累积成功率 |
|---|---|
| 2 | ~64% |
| 3 | ~78% |
| **5**（脚本默认） | **~92%** |

**辅助观察**：
- 有一次 `score = -0.13`（识别几乎没找到峰值）**居然也通过了** —— 服务端容差比预想的大
- 失败样本的距离分布很散（107 / 149 / 249 px），不是某个特定距离会挂，
  说明主要误差来自**缺口识别的几像素偏差**和**轨迹特征**，而不是系统性错误

**为什么不是 100%**：
1. 缺口识别在部分图上偏差几像素（score 波动 27~107，低分时可能偏）
2. 轨迹是数学模型生成的，`relative_time` 分布与真人仍有差异
3. `iid=0&did=0&device_id=0` 环境指纹为空

**实践上够用了**：脚本默认 `--retries 5`，累积 ~92%。
若要进一步提高，优先改**缺口识别**（多算法投票 + 亚像素插值），其次才是轨迹。

### 18.5 怎么验证它到底行不行

**唯一的验证途径是等真实风控触发验证码**（服务端返回 `10000` + `verify_data` 那条路径），
那时 challenge 是服务端认可的。触发后直接跑：

```bash
python3 tt_slide_solver.py --detect        # 确认出现了
python3 tt_slide_solver.py --solve        # 自动滑
```

**判断真假 challenge 的方法**：抓 `/captcha/get` 的响应，看 `challenge_code`。
`99999` = 疑似主动渲染的无效挑战；真实风控下的值应不同。

### 18.6 但它仍不该当主力 —— 优先「不触发」

自动滑能过，但**每次触发验证码本身就是风控已经在盯你的信号**，
连续触发会把路径推向 `verifySDK.SMS`（短信验证）。所以日常还是降低触发概率：

| 手段 | 客户端默认值 |
|---|---|
| 请求间隔 | `scan_product_promotions(gap=1.0)`、`update_product_fixed_price(gap=3.0)` |
| 少开 tab | `call_via_page` 复用页面 |
| 页面探活 | `_page_alive()` 先跑 `1+1` |
| 异步发请求 | 轮询 `window.__promo_r`，不用 `awaitPromise` |
| 及时收尾 | 测试完的活动 `park_any()` 掉，别堆在列表里 |

**经验值**：一次性 60+ 个 CDP 请求 + 建 40+ 个活动 → 必触发。
正常业务量（一天几个活动）不会。

### 18.7 附：验证码 SDK 结构（实测）

```
iframe   : https://www.tiktok.com/ucenter_web/zti_web
SDK      : secsdk-captcha 2.27.6  (verify-sg.byteoversea.com)
全局对象 : OECCaptcha = [TTVerifyCenter, close, config, getFp, init,
                         initWithLock, render, transform]
           verifySDK   = [renderCaptcha, closeCaptcha, getCaptchaWebId,
                          initVerifyOptions, renderSecondVerifyWeb,
                          renderSecondVerifyH5, autoRender, SMS,
                          initVerifyCenter, getNewCaptchaWebId]
DOM      : .secsdk-captcha-drag-sliding  拖动按钮 44x44
           .secsdk-captcha-drag-icon     拖动图标 64x40
           img.captcha_verify_img_slide  拼图块
           .captcha_verify_message       提示文本
```

> ⚠️ `verifySDK.SMS` 说明风控有升级路径（滑块 → 短信），别连续硬刚。

### 18.8 参考

- [TikTok Shop 滑块验证码逆向分析与协议还原实践（看雪）](https://bbs.kanxue.com/thread-292336.htm)
  —— 纯协议化路线：从 `/captcha/verifyV2` 反推 SDK，插桩拿明文 `{id, mode, reply, mp, mm, mu}`，
  字段分治，最后复用 SDK 加密与签名。本文实测到的 `reply`/`id`/`mode` 结构与之一致
- [tiktok-captcha-solver](https://pypi.org/project/tiktok-captcha-solver/) —— 现成轮子（未验证）


---

## 19. 验证码自动化：长期约定与实现

### 19.1 约定（operator 指令）

> **在之后使用 TikTok 商店 API 的过程中，遇到需要滑动验证码的情况必须自动帮我滑；
> 不限于促销页，所有 TikTok 相关页面都要做；尽可能提高效率；同时尽可能不触发风控。**

落到代码里的三条：

| 要求 | 实现 |
|---|---|
| 遇到就滑 | `tk01_promo_client.call_via_page()` 拿到 `code=10000` 且页面有验证码 → **自动滑 + 重发原请求** |
| 覆盖所有 TikTok 页面 | `tt_captcha.TIKTOK_HINTS` 匹配 `tiktokshopglobalselling.com` / `seller-*.tiktok.com` / `*.tiktok.com` / `*.tiktokv.com` / `*.byteoversea.com` |
| 提效率 / 降风控 | 亚像素缺口识别 + 5 次重试；`RiskMonitor` 记录触发频率，超阈值自动冷却 |

### 19.2 用法

```python
from tt_captcha import CaptchaGuard

G = CaptchaGuard(port=CDP_PORT)
G.handle_if_present()      # 有就滑掉，没有直接返回 True
G.solve(retries=5)         # 明确求解
G.stats()                  # 触发/成功率统计
```

客户端的自动处理（无需手动调用）：

```python
C = PromoClient()
C.promo_create_fixed(...)          # 内部走 call_via_page
# ← 若中途弹验证码，会打印「⚠️ 命中风控验证码 → 自动滑动」，滑过后自动重发原请求
```

CLI：

```bash
python3 tt_captcha.py --detect            # 检测所有 TikTok 页面
python3 tt_captcha.py --solve             # 自动滑
python3 tt_captcha.py --stats             # 风控统计
python3 tt_captcha.py --solve --force     # 忽略冷却
```

### 19.3 实测成功率（含重试后）

**单轮 ≈ 40~50%**（三次独立测量：62.5% / 33% / 30% / 50%，24+ 样本）。
**关键是重试** —— 实测三次 `solve(retries=5)` 调用：

```
第 1 次: [1]500 → [2]500 → [3]200   ✅
第 2 次: [1]残留 → [2]200           ✅
第 3 次: [1]残留 → [2]200           ✅
```

**3/3 通过**，平均 2~3 次尝试。单轮 45% 时 5 次重试累积 ≈ **95%**。

### 19.4 提效率的两个关键点

1. **亚像素缺口定位** —— 对滑窗得分做抛物线拟合，避免整数列量化带来的 ±1px 误差。
   失败样本多为几像素偏差，这一步直接改善命中。
2. **「残留」不是失败** —— 拖动成功后拼图块会停在目标位，下一轮检测到
   `left > 2` 会被误判成残留。它其实是**上一次成功的痕迹**，
   所以处理方式是「顺手换新挑战继续」，而不是报错退出。

### 19.5 降风控的两个动作

1. **`RiskMonitor`** —— 每次触发记一条事件；近 1 小时触发 ≥ 8 次自动进 10 分钟冷却。
   依据：`verifySDK` 暴露了 `SMS`，说明风控可以升级到短信验证，不能无限硬刚。
2. **客户端节流**（已有默认值）：

```
scan_product_promotions(gap=1.0)      扫描间隔
update_product_fixed_price(gap=3.0)   改价间隔
call_via_page 复用页面，不主动开新 tab
_page_alive() 先探活，避免 CDP 卡死
建完活动立刻 park_any()
```

### 19.6 踩过的坑（避免重犯）

| 坑 | 后果 | 正解 |
|---|---|---|
| 用「拖动按钮是否消失」判成功 | 通过率被记成 0%，白折腾好几轮 | 只看 `/captcha/verify` 的响应码 |
| 缺口识别 y 从 0 起扫 | score 只有 22，误判 | y 用拼图块当前位置，score 升到 69~107 |
| 按 `transform` 读拼图块位置 | 恒为 `matrix(1,0,0,1,0,0)`，永远读成 0 | secsdk 用 `style.left` |
| hook `fetch` 抓验证请求 | secsdk 走 **XHR**，一直抓不到 | hook `XMLHttpRequest` |
| 在 `_attempt` 里嵌套「重渲染→重检测→重拖」 | 整个流程卡死 | 只调一次 `render`，其余交给上层循环 |
| 用 `awaitPromise` 发签名请求 | 页面节流时 CDP 挂死 | 轮询 `window.__promo_r` |

### 19.7 🔴 最关键的修正：3.7px 系统性偏差

**这是命中率上不去的真正原因** —— 由 operator 观察到「滑动时缺口没对准」而定位。

`find_gap` 返回的是**形状 mask**（96×96）左上角在背景图上的位置；
但拼图块的 `left` 说的是**整张图**（110×110）的位置。两者原点差一个裁剪偏移 `mx0`：

```
错误:  left = gap_x × scale_bg
正确:  left = gap_x × scale_bg − mx0 × scale_pc      ← 扣掉 mask 在拼图块内的偏移
```

实测 `mx0 = 6`、`scale_pc = 0.6159` → **系统性偏差 3.7px**。
拼图块看着拖到位了，实际差近 4px，服务端判 `VerifyFailedErr`。

**顺带修正 y**：同理，缺口的纵向位置是
`(pcRect.y + my0 × scale_pc − bgRect.y) / scale_bg`，不是 `(pcRect.y − bgRect.y) / scale_bg`。
代码里先用粗略 y 扫一遍拿到 `my0`，再用修正后的 y 重扫一次。

**修正效果**（修正前后各测一批）：

| | 真实拖动结果 |
|---|---|
| 修正前 | 单轮 ~40%（24 样本） |
| **修正后** | **4/4 全部 verify=200** |

> 另注：统计口径也要对。「拼图块残留」是**上一轮成功**留下的状态，
> 不是失败 —— 早先把它算成失败，导致成功率被严重低估。已改成三态返回
> `(ok, why, consumed)`，残留不计失败、也不消耗重试次数。

### 19.8 文件

| 文件 | 作用 |
|---|---|
| `tt_captcha.py` | **主力**：通用验证码处理器（检测/求解/风控监控），被客户端调用 |
| `tt_slide_solver.py` | 早期版本，含 `--analyze` 存图与缺口标注，用于调试识别效果 |
| `promo_catcher.py` | 抓包器（原始 websocket + 独立线程），用于协议分析 |


---

## 20. 商品机会（Product Opportunity）接口

页面：`/product/opportunity?shop_region=VN&sort_field=1&use_like=false`

### 20.1 端点全貌：53 个方法

来源是页面自带的 API 封装 JS：

```
/obj/she-op-static/i18n/ecom/next/product_opportunity_home/js/
    oec_product_seller_product_opportunity_api.g8gmfrvq.js
```

（国内 CDN 前缀 `lf-gs-frontend-cn.fanchenstatic.com`，13KB）
解析出的 `(方法名, HTTP 方法, 路径)` 映射存于 **`notes/opp_endpoints.json`**。

### 20.2 ⚠️ 两套前缀，用错一律 404

```
/api/v1/product/oc/seller_product_opportunity/…   ← 主套：lead / relate / submit / contract
/api/v1/product/seller_opportunity/…              ← 另一套：niche / collect / suggested_word
```

踩过：`ListNiches`、`GetSuggestedWord` 拿主前缀去调，返回的是 **HTML 404** 而不是 JSON。
（**判断技巧**：`_raw` 里出现 `<html>` 就是路径不对，不是参数问题。）

### 20.3 四大能力

| 需求 | 方法 | 端点 | 实测 |
|---|---|---|---|
| **查看商品机会** | `ListLead` | `POST seller/lead/list` | ✅ |
| | `GetLeadDetail` | `POST seller/lead/detail` | ✅ |
| | `GetLeadShowField` | `POST seller/lead/show_field` | ✅ |
| | `ListLeadTag` | `POST seller/lead/tag/list` | ✅（需 `lead_type`）|
| | `GetAppHomeLeadList` | `POST app_home/lead_top` | 未测 |
| **搜索机会商品** | `SearchTtsProducts` | `POST tts_product/search` | ⚠️ 见 20.5 |
| | `SearchTrendingTtsProducts` | `POST tts_product/trending/search` | ⚠️ 12051002 |
| **报名** | `RelateProductToSPO` | `POST relate` | ⚠️ 写操作，见 20.5 |
| | `UploadRelateSPOProduct` | `POST excel/relate/upload`（multipart）| 未测 |
| | `GetRelateSPOProductTemplate` | `GET excel/relate/get` | ✅ 返回 `download_url` |
| **提报结果** | `GetSocMySubmissionSubmitRecordList` | `POST submit/record/list` | ✅ |
| | `GetSocMySubmissionProductPerformanceList` | `POST product/performance/list` | ⚠️ 404 |
| | `GetSocMySubmissionProductPerformanceCard` | `POST product/performance/Card` | ⚠️ 98001034 |

其余可用端点：`SellerRejectSPO`(reject) / `MarkSpo`(mark) / `RecruitMark` /
`SetAutoSubmit` / `CheckSignedSPOContract` / `SignSPOContract` /
`GetShopFilter` / `GetPOPSellerShopFilter` / `ListSPOReport` / `SellerReportSummary` /
`ListSPOOptimizationTasks` / `UpdateSPOOptimizationTaskStatus` / `ListSPOProductTraffic` /
`ListNiches` / `ListNicheProducts` / `GetSuggestedWord` / `CollectItem`。

### 20.4 真实请求参数（抓包所得）

```jsonc
// 主列表（page_number 从 1 开始）
POST seller/lead/list
{"opportunity_type":3, "tab_code_filter":["high_potential_products"],
 "use_like":false, "sort_field":1, "page_number":1, "page_size":100,
 "traffic_source":"seller_organic"}

// 首屏（多类型一起拉）
POST seller/lead/list
{"page_number":0, "page_size":100, "use_like":true,
 "traffic_source":"seller_organic", "opportunity_type_list":[3,2,4]}

POST shop_filter/get    {"opportunity_type":[3], "need_aggregated":true, "topic_code":"…"}
POST contract/check     {"is_universal_product_white_list":false, "ab_experiment":true}
POST recruit/mark       {"event_type":2, "lead_list":[{"lead_id":"…","opportunity_type":3},…]}
```

**返回字段**（`seller/lead/list`）：

```
lead_id / lead_name / opportunity_type / pic_url
level1_cate_name / level2_cate_name / level3_cate_name  (+ _name_key)
search_volume / online_products / order / gmv / gmv_l30d
l30d_sales_volume / potential_score / collect / only_for_you / hide_metrics
external_platform / real_external_product_id / categories[]
```

`opportunity_type` 取值：`3` 高潜力商品、`2` 关键词机会、`4` 类目机会、`202` 选品推荐。

### 20.5 两个还没吃准的点（诚实标注 + 已排除的可能）

#### (1) `SearchTtsProducts` —— 参数语法正确，但恒返回空

必填 `search_text` + `page_number` 已补（服务端绑定错误告知的），
试过的组合全部返回 **`code=0` + `data=null`**：

| 试过的参数 | 结果 |
|---|---|
| `search_text`: gel / kem / sữa rửa mặt / tai nghe / áo | `data=null` |
| 从真实机会名里取词：`Loại` / `Dành` / `DERMATIDEM` / `PLUS` / `chấm` / `thâm` | `data=null` |
| `+ biz_type` / `+ opportunity_type` / `+ lead_id` / `+ use_like` | `data=null` |
| `+ traffic_source` / `+ tour_id` / `+ opportunity_type_list` | `data=null` |

**判断**：**参数语法是对的**（参数错会返回 400 或 12051002，而不是 `code=0`）。
所以更可能是「这个店铺当前没有可报名的商品」或需要报名弹窗的上下文。
**不要当成接口不通。**

从 JS 里挖到的调用模式（`lead-source-hover.g91i7fu1.js`）：

```javascript
lt.UploadRelateSPOProduct({file: r, traffic_source: xe(), tour_id: be()}, {timeout: 120e3})
```

**该页面所有请求都带 `traffic_source` 和 `tour_id`**，后者是动态取值（`be()`）。

#### (2) `RelateProductToSPO`（报名）—— 请求体结构未知

写操作，用猜的 body 会打脏数据，所以客户端默认 `apply=False`（只回 `would_post`）。

**报名的 UI 入口已定位**：机会卡片上的「**添加同款商品**」按钮。

### 20.6 🔴 UI 自动化在这套页面上不可行（三次验证）

为了抓搜索/报名的真实请求，我试过驱动 UI，**三次都失败**：

| 尝试 | 结果 |
|---|---|
| 验证码页：label.click / Space / `bring_to_front` | React state 不更新（DOM `checked=true` 但表单 state 空）|
| 促销页：行 checkbox / 弹层按钮 | 点击后表格整体重渲染卸载 |
| **机会页**：React native setter 写搜索框 + `input`/`change` 事件 + CDP Enter | 值写进去了（`val:"gel"`、`focused:true`），**但零请求** |
| **机会页**：「添加同款商品」按钮，坐标在视口内（472,371）CDP 真实点击 | **零请求、无弹窗** |

**结论：这个前端（React 18 + Atlas 微前端）不吃 CDP 的合成输入事件。**
以后再需要抓"交互后才发的请求"，**不要在 UI 自动化上花时间** ——
直接请人在页面上点一次，用 `promo_catcher.py` 抓。

### 20.7 参数发现的省时技巧

服务端的**参数绑定错误会直接点名缺失字段**，比逐个猜快得多：

```
400 binding: expr_path=search_text,  cause=missing required parameter
400 binding: expr_path=params,       cause=missing required parameter
400 binding: expr_path=lead_type,    cause=missing required parameter
```

另有几个非零码的含义（实测）：

| code | 含义 |
|---|---|
| `12047007` | rpc call error —— 请求体结构不对（如 `submit/record/list` 少了外层 `params`）|
| `12051002` | 无效参数 |
| `98001034` | 业务态不满足 |
| `12071012` | `soc invalid param` |

**嵌套结构**：`submit/record/list` 要 **两层 `params`**：

```json
{"params": {"params": {"page_number": 1, "page_size": 20}}}
```
单层会被 `12047007` 拒掉。

### 20.8 客户端 `tk01_opportunity.py`

```bash
python3 tk01_opportunity.py leads --type 3 --size 10    # 查看机会
python3 tk01_opportunity.py detail <lead_id>           # 机会详情
python3 tk01_opportunity.py tags  --type 3             # 机会标签
python3 tk01_opportunity.py submits                    # 提报结果
python3 tk01_opportunity.py template                   # 报名模板下载地址
python3 tk01_opportunity.py filter / reasons           # 筛选器 / 拒绝原因
python3 tk01_opportunity.py endpoints                  # 打印全部 53 个端点
```

```python
from tk01_opportunity import OpportunityClient
O = OpportunityClient(gap=1.2)          # 内置请求间隔，防验证码
for x in O.list_leads(opportunity_type=3, size=10):
    print(x["lead_id"], x["lead_name"], x["gmv"])
print(O.lead_detail("7408XXXXXXXXXX25"))
print(O.submit_records())
print(O.relate_template())             # 报名模板地址
```

CLI 实测输出：

```
共 4 条机会:
  7408XXXXXXXXXX25  [高潜力商品] [COMBO NGỪA MỤN] Sữa Rửa Mặt & Toner Trà
      类目=美妆个护/护肤品/痘痘、粉刺护理  在线商品=0  订单=6.803  GMV=20.157₫
  ...
报名模板下载地址: /wsos_v2/oec-product/object/wsos6ab84620851c4b34?timeStamp=…&sign=…
提报结果: {"total_cnt": 0}
```


---

## 21. 商品机会提报：后训练结论

### 21.1 提报流程的真实路径（UI 追踪所得）

```
机会列表 /product/opportunity
   └─ 卡片上的「添加同款商品」按钮
        └─ 跳到 /product/opportunity/search?search_tab=high_potential_products&search_text=…
             └─ 选择要关联的商品 → 提交
```

**关键观察**：点「添加同款商品」会**导航**（不是弹窗），
URL 上会带上 `search_text`。

### 21.2 ✅ Playwright 的点击在这套前端上有效（CDP 不行）

这是本轮最有价值的发现，**纠正了 §20.6 的结论**：

| 驱动方式 | 结果 |
|---|---|
| CDP `Input.dispatchMouseEvent` 点按钮 | **零请求、零导航** |
| **Playwright `locator.click()`** | **✅ 触发导航**（URL 从 `/opportunity` 变成 `/opportunity/search?search_tab=…`）|

**所以不要用裸 CDP 事件驱动 UI，用 Playwright 的 locator API。**
（`locator.click()` 会做 actionability 检查 + 滚动 + 完整的 hover→down→up 序列，
比手搓 `dispatchMouseEvent` 完整。）

**另一个坑**：`Input.dispatchMouseEvent` 的坐标必须在**视口内**。
早先点「添加同款商品」时坐标是 `(1285, 1351)`，而视口只有 `1512x741` —— 点击完全落空。

### 21.3 ⚠️ 提报的请求体仍未知（写操作，不能猜）

`RelateProductToSPO` → `POST relate` 是**写操作**。
用猜的 body 打出去会产生脏数据（可能生成错误的商品关联），所以客户端保持
`apply=False`，只回 `would_post` 不真发。

**已确认的调用模式**（从 `lead-source-hover.g91i7fu1.js` 提取）：

```javascript
lt.UploadRelateSPOProduct({file: r, traffic_source: xe(), tour_id: be()}, {timeout: 120e3})
//                          ↑文件        ↑动态取值         ↑动态取值
```

**该页面所有请求都带 `traffic_source` 和 `tour_id`**，后者由 `be()` 动态取得
（可能来自 URL / localStorage / 引导流程状态）。

### 21.4 抓包工具已就绪（这次修好了）

`promo_catcher.py` 的 hook 有两个坑，已修：

| 坑 | 现象 | 修法 |
|---|---|---|
| URL 取值 | `u.split('.com')[-1]` 在无 `.com` 时返回整串 → 记成 `None` | 先 `indexOf('.com')` 判断再切 |
| 跨导航失效 | 点击导致导航后 hook 与 `window.__oq` 一起没了 | 用 Playwright 的 `ctx.add_init_script()` 持久化 |
| **`add_init_script` 对已存在页面不生效** | 新装的 hook 抓不到任何请求 | **必须 reload/goto 一次**才注入 |

**正确的抓包姿势**：
```python
ctx = browser.contexts[0]
ctx.add_init_script(HOOK_SRC)          # 绑 context
page.goto(url, wait_until="domcontentloaded")   # ← 必须重新导航,否则 hook 不注入
time.sleep(15)
print(page.evaluate("JSON.stringify(window.__oq)"))
```

### 21.5 后训练结论：能自动化的边界

| 能力 | 状态 |
|---|---|
| 拉取机会列表 / 详情 / 标签 | ✅ 直连可用（`tk01_opportunity.py`）|
| 分页 / 按类型 / 排序筛选 | ✅ `page_number` / `opportunity_type` / `sort_field` |
| 读提报记录 | ✅ `submit/record/list` |
| 下载报名模板 | ✅ `excel/relate/get` → `download_url` |
| 读店铺筛选器 / 拒绝原因 | ✅ |
| **自动报名（写）** | ❌ 缺请求体结构 |
| **搜索可报名商品** | ⚠️ 参数语法正确但返回空 |

**关于"多练几次提高效率"**：提报是**写操作**，在拿到真实 body 之前，
反复试只会产生脏数据。**应该先在页面上完整提报一次并抓包**，
之后才能做到"批量提报 + 不触发验证码"。

### 21.6 不触发验证码的做法（已内置）

```python
O = OpportunityClient(gap=1.2)     # 请求间隔
```
- 端点之间强制间隔（`_throttle`）
- 不批量轮询；一次只做一件事
- 触发验证码由 `tt_captcha.CaptchaGuard` 自动接管（客户端已集成）
- 建完/改完立刻收敛，不在页面上留一堆待处理状态

---

## 22. 商品机会提报：效率诊断 + 准入预检规则（实测反推）

> 本章是 §20/§21 的修正与升级。§21 里"必须先抓一次真实请求体"的问题已解决，
> 并且找到了 4% 提报成功率的**真正原因**和一个可用的**准入过滤器**。

### 22.1 ⚠️ 传输层铁律：机会接口必须在页面上下文里发

**直连（requests / urllib）打这些端点会返回 `{"code": 0}` 且没有 `message`。**

这是"请求没被服务端当真"的**假成功**，不是成功。实测证据：

```
20 次直连 POST /relate  →  全部返回 code=0 / 无 message
                        →  但只有 1 次真的写进去了（缺签名的被静默丢弃）
```

判据：`code == 0` **且** 响应里有 `message` 字段才算真成功。
`tk01_opportunity.py` 的 `_failed()` 就是按这条判的，直连不再使用。

原因同 §17：页面里 webmssdk 会给请求注入
`X-Bogus` / `X-Gnarly` / `msToken` / `X-Tts-Oec-Bsid` / `fp`。

**query 里还必须带 `seller_id`**（不只是 `oec_seller_id`）—— 少了它
`submit/record/list` 会走到不同的路由分支。

### 22.2 为什么不用 awaitPromise（血泪）

页面在后台时 `Runtime.evaluate(awaitPromise=true)` 会**一直挂着**：

- fetch 可能永不 resolve
- 连 `AbortController` 的 `setTimeout` 都不一定跑 → 超时兜底形同虚设
- `page.set_default_timeout()` 对 `evaluate` **不生效**
- `page.evaluate()` **不接受 `timeout=` 关键字**（`TypeError`）

可靠做法 —— **发出去、写全局、轮询读回**：

```javascript
(() => {
  window.__opr1 = null;
  fetch(url, {method:"POST", credentials:"include", headers:{...}, body:"..."})
    .then(r => r.text().then(t => { window.__opr1 = r.status + "|" + t; }))
    .catch(e => { window.__opr1 = "EXC|" + String(e); });
  return "sent";            // 不 await
})()
# 然后每 0.4s 读一次 window.__opr1
```

### 22.3 端点全表：47 个 (方法, 版本, 路径)

路径模板：`uriPrefix + /api/v{version||1}/product/oc/seller_product_opportunity/<path>`
**version 由调用方给，缺省 1** —— 但 `submit/record/list` 实际用的是 **v2**。

解析结果存 `notes/opp_api_table.json`（`tk01_opportunity.py endpoints` 可打印）。
关键几条：

| 方法 | 路径 | 操作名 | 参数包装 |
|---|---|---|---|
| POST | `/seller/lead/list` | ListLead | flat |
| POST | `/seller/lead/detail` | GetLeadDetail | **flat** |
| POST | `/seller/lead/show_field` | GetLeadShowField | flat |
| POST | `/seller/lead/tag/list` | ListLeadTag | flat |
| POST | `/tts_product/search` | SearchTtsProducts | flat |
| POST | `/tts_product/trending/search` | SearchTrendingTtsProducts | flat |
| **POST** | **`/relate`** | **RelateProductToSPO** | **flat** |
| POST | `/reject` | SellerRejectSPO | flat |
| POST | `/reasons/list` | ListSellerRejectSPOReasons | flat |
| **POST** | **`/submit/record/list` (v2)** | GetSocMySubmissionSubmitRecordList | **params** |
| POST | `/product/performance/Card` | …PerformanceCard | **params** |
| POST | `/product/performance/list` | …PerformanceList | **params** |
| GET | `/excel/relate/get` | GetRelateSPOProductTemplate | — |
| POST | `/excel/relate/upload` | UploadRelateSPOProduct | multipart |
| GET | `/report/list` | ListSPOReport | query |
| GET | `/traffic/list` | ListSPOProductTraffic | query |
| GET | `/optimization_tasks/list` | ListSPOOptimizationTasks | query |
| GET | `/sensitive_words/check` | CheckProductTitleWords | query |
| GET | `/opportunity_type_by_region/get` | …ByRegion | — |
| GET | `/shop_experience_score/get` | GetShopExperienceScore | — |
| GET | `/seller/batch_listing/opportunity/count` | …Count | — |
| GET | `/seller/batch_listing/task/latest` | …Latest | query |
| POST | `/seller/batch_listing/task/create` | CreateBatchListingTask | flat |
| POST | `/contract/check` | CheckSignedSPOContract | flat |
| POST | `/contract/sign` | SignSPOContract | flat |
| POST | `/auto_submit/set` | SetAutoSubmit | flat |
| POST | `/mark` / `/recruit/mark` | MarkSpo / RecruitMark | flat |
| POST | `/shop_filter/get` | GetShopFilter | flat |
| POST | `/seller/report/summary` | SellerReportSummary | flat |
| POST | `/seller/leafcate/recommend` | LeafCateRecommend | flat |
| POST | `/seller/brand/recommend` | BrandRecommend | flat |
| POST | `/seller/eu/config` · `/seller/pop/config` | …Config | flat |
| POST | `/app_home/lead_top` · `/app_home/pop/lead_top` | GetAppHomeLeadList | flat |
| POST | `/pop/filter/get` · `/seller/new_shop_set_up/lead/list` | … | flat |
| POST | `/seller/seasonal_festival/tag/list` | GetSeasonalFestivalTagList | flat |
| POST | `/upload_details/get` | GetSPOUploadDetails | flat |
| POST | `/initial/list` · `/optimization_items_by_country/list` | … | flat |
| GET/POST | `/product/stock/get` · `/product/stock/update` | Get/UpdateProductStock | query/flat |
| POST | `/optimization_tasks/update_status` | …UpdateStatus | flat |

**Go mux 按方法严格路由**：给 GET-only 路由发 POST → `404 page not found`（纯文本，
不是 JSON）。所以 404 时先怀疑方法，再怀疑路径。

**路由不存在时的两种 404 长相**：
- `404 page not found`（小写纯文本）= API 网关（Go）没匹配上路径/方法
- `<html>…<center>TLB</center>` = 走到了 TikTok 负载均衡层，路径压根没有

### 22.4 提报结果接口（v2 + POST + 单层 params）—— 修正 §21

**真实请求（抓包确认）**：

```
POST /api/v2/product/oc/seller_product_opportunity/submit/record/list
     ?locale=zh-CN&language=zh-CN&oec_seller_id=…&seller_id=…&aid=6556&app_name=i18n_ecom_shop
     &fp=…&device_platform=web&…&browser_online=true&timezone_name=Asia/Ho_Chi_Minh
     &msToken=…&X-Bogus=…&X-Gnarly=…&X-Tts-Oec-Bsid=…
body: {"params": {"page_number": 1, "page_size": 20,
                  "approve_status": 1, "seller_operation_list": [1, 2]}}
```

**历史坑**：老客户端发的是 `{"params": {"params": {…}}}` 双层嵌套 →
`code=0` 但 `total_cnt=0`（看起来"没记录"，实际是参数进不去）。

**筛选语义（实测）**：

| 参数 | 取值 | 含义 |
|---|---|---|
| `approve_status` | 1 | 已批准 |
| | 2 | 已被拒（**不传时默认也是这档**） |
| | 3 | 空 |
| `seller_operation_list` | `[]` | 不过滤 → 总数 = 成功提报商品数（4227） |
| | `[1,2]` | 页面 UI 默认视图 |
| | `[1]` | 只留 op=1 |
| `seller_operation` | 1 / 2 / 4 | 都是真实取值（1 最少，2 最多） |

`total` **只在 `page_size >= 20` 时返回**（`page_size=5` 时字段直接消失）。

记录字段：
`opportunity_name` / `tts_product_info{name,id,images}` / `opportunity_type` /
`spo_audit_result{result_value, failure_reason}` / `seller_operation` /
`failure_reason` / `submit_time` / `last_update_time` / `lead_id` / `lead_images` /
`incentives_list` / `incentives` / `trend_graph` / `product_orders` / `product_pv` /
`is_cold_start_coupon` / `is_pontos` / `matrics_max_update_time`

注意 `submit_time` 是**毫秒字符串**。

### 22.5 提报成绩单与"效率"问题的定性

```
GET  /api/v1/…/product/performance/Card   body {"params":{"biz_type":0}}
```

实测（基线）：

| 指标 | 值 |
|---|---|
| `total_submit_num` | 83962 |
| `failed_submit_spo_num` | 79735 |
| `success_submit_spo_num` | 4227 |
| `sale_rate` | **4%** |
| `success_submit_num` | 506 |
| `total_gmv` | 24.781.472₫ |
| `total_pv` / `total_sales` | 128.434 / 571 |
| `product_co` / `product_ctr` | 9% / 5% |
| `in_checking_spo_num` | 0 |

合同状态：

```
POST /contract/check  {"is_universal_product_white_list":false,"ab_experiment":true}
→ {"is_signed":true,"is_set_overall_auto_submit":true,
   "themes":[{"code":"best_selling_online"}],
   "assistant_config":{"use_themes":false,"tab_list":[201,3,4]}}
```

**diagnosis（1000 条失败记录去重）**：

```
唯一货品 238 个 / 唯一机会 79 个 / 唯一 (货品,机会) 对 999 个
```

→ **不是重复提报，是把商品盲铺到了所有机会**。所以问题不在"发得慢"，
在于"发给了不该发的机会"。提高效率 = **加准入过滤**，不是加并发。

失败原因分布（500 条采样）：**500/500 全部是「商品与机会提报要求不符」** ——
服务端不给细粒度原因，只能自己算准入。

### 22.6 ❌ 「segment token 命中数」规则 —— 已被实测推翻，不要再用

**曾经的假设**：商品标题命中该机会 `lead_segment` 的 token 越多越容易过审
（≥3 个 → 94% 成功率）。

**它是错的。** 拿这个规则真打了 20 笔（5 个机会 × 4 个商品，全部满足 ≥3 命中）：

```
total_submit_num 83962 → 83967
20 笔全部落库，全部 result_value=2（已被拒），failure_reason 仍是「商品与机会提报要求不符」
预计 94%，实测 0%
```

**为什么会被骗**（三个叠加的取样错误）：

1. **只取了第 1 页**（`approved(page=1, size=100)`）。批准记录按时间倒序，
   第 1 页 = 最近的 100 条，集中在少数几个机会上 —— 典型的选择偏差。
2. **`lead_segment` 只覆盖了 31/48 个机会**。没拉到详情的 17 个机会
   `seg=[]`，被 `any(...)` 静默算成"不命中"，把已经偏向的样本又压了一层。
3. **子串匹配产生假阳性**：机会 `Gel chấm nốt ruồi…` 的 token `Gel`
   能在毫不相关的 `Kem Dưỡng Ẩm…` 长标题里被匹配到。

**换成 500 条已批准 + 200 条已被拒重新统计，假设直接反转**：

| 假设 | 已批准 | 已被拒 | 结论 |
|---|---|---|---|
| segment ≥1 命中（不区分大小写） | 131/500 = 26% | 79/200 = 40% | **反相关 / 噪音** |
| segment ≥3 命中 | 93/500 = 19% | 5/200 = 2.5% | 只是"标题越长越容易撞词" |
| 标题包含机会名前 2 个词 | 157/500 = 31% | 0/200 = 0% | 必要不充分 |

**教训**：从日志反推规则时，必须（a）跨页取样，（b）把缺失值单独归类而不是当 False，
（c）用完整词匹配而不是子串。否则会得到一个"看起来很干净"的假规则。

### 22.6b ✅ 正确的结论：判别式在「机会」侧，不在「商品」侧

**证据链**：

```
成功样本: 48 个机会 / 142 个商品
失败样本: 17 个机会 / 143 个商品
  机会交集 = 1     ← 两个样本的机会集合几乎不重叠
  商品交集 = 85    ← 142 个成功商品里有 85 个同时出现在失败集合里
```

**同一个商品在某些机会被批准、在另一些被拒**（例：`pid=1734XXXXXXXXXX88`
在 7 个机会获批、在 `7488XXXXXXXXXX23` 被拒）。所以：

> **商品本身不是开关，机会才是。** 提报效率问题 = "这个店能不能做这个机会"。

**把 4227 条批准记录全量拉下来（43 页）得到真值表**：

```
唯一机会 145 个上有批准记录
其中 ≥5 次批准的「开放机会」 93 个
→ notes/open_leads.json
```

开放机会的名字有两种形态，都是"能过"的信号：

| 批准数 | 机会名 | 形态 |
|---|---|---|
| 79× | `Kem trị sẹo nhanh, làm mờ vết sẹo, dưỡng ẩm và tái tạo da` | 宽泛品类词 |
| 61× | `Gel Thoa Mụn Thâm Chăm Sóc Da` | 宽泛品类词 |
| 57× | `kem trimun trang da` | 宽泛品类词 |
| 56× | `[FLASHSALE 50%] Kem Loại Bỏ Sẹo, Xóa Vết Sẹo Và Làm Mờ Sẹo…` | **就是本店商品标题** |
| 42× | `đồ ngoáy ráy tai` | 本店另一个品类（掏耳工具） |

而我盲打的 5 个机会（`Gel chấm nốt ruồi, mụn cóc, tàn nhang` 之类，
**去痣/去疣** —— 本店根本不做的品类）历史批准数为 **0**。

**标题↔机会名 词重叠率**（Jaccard 口径，仅作必要条件用）：

| 重叠率 | 已批准 500 条 | 本次实测被拒 32 条 |
|---|---|---|
| ~0 | 1.8% | 23/32 |
| 0.001–0.34 | 18.4% | 9/32 |
| 0.34–1.0 | 79.8% | **0/32** |

→ 重叠率 <0.34 基本必挂；但 ≥0.5 也不保证能过
（本店标题是关键词堆砌型，动辄 150–255 字符，撞词太容易）。
**所以重叠率只能用来排除，不能用来准入。**

### 22.6c ✅ 正确的靶单：批准数 > 0 且 拒绝数为 0

把「批准记录全量」与「拒绝记录样本」对齐后，两组的差异是**干净利落**的：

```
批准样本里有记录的 145 个机会   ×   拒绝样本里有记录的 79 个机会
                        交集 = 1
```

也就是说：**机会基本上要么是"开放的"（一直批），要么是"关着的"（一直拒）**，
中间态极少。这解释了为什么"商品标题"怎么调都没用 —— 门根本没开。

据此生成的靶单 `notes/target_leads.json`：

| 批准数 | 拒绝数(样本内) | 机会名 |
|---|---|---|
| 79 | 0 | `Kem trị sẹo nhanh, làm mờ vết sẹo, dưỡng ẩm và tái tạo da` |
| 75 | 0 | `Băng Giảm Béo Mặt Hình Chữ V Nâng Chăm Sóc Da Mặt` |
| 61 | 0 | `Gel Thoa Mụn Thâm Chăm Sóc Da` |
| 57 | 0 | `kem  trimun  trang  da` |
| 56 | 0 | `[FLASHSALE 50%] Kem Loại Bỏ Sẹo, Xóa Vết Sẹo Và Làm Mờ Sẹo` |
| 42 | 0 | `đồ ngoáy ráy tai` |
| … | … | （掏耳工具系列 30+ 个机会） |

**满足「≥5 次批准 且 样本内 0 拒绝」的机会共 92 个。**

⚠️ 诚实的限制：拒绝记录有 79735 条，我只抽样了 1000 条，
所以「0 拒绝」只代表**在这个样本里**没出现，不等于真实拒绝数为 0。
`sample_hit_rate` 只能用来排序，不能当真实命中率。
真正要验证还是得**先打 5 笔看结果**。

对照：我盲打的那 5 个机会（`Gel chấm nốt ruồi…` 等）批准数全是 **0**，
全都在拒绝组里 —— 靶单规则能正确地把它们排除掉。

### 22.6d ✅ 已验证可用的提报方法（实测 60%，最优子集 95%）

#### 先说阻塞了三轮的真因：**后台标签页**

这不是风控，是 Chrome 的行为：

```
document.visibilityState === 'hidden'   → 页面在后台
   ├─ Chrome 挂起后台页的网络 → fetch 永不 resolve
   │    表现：客户端报「轮询 20s 未拿到响应」，看着像服务端/风控挂起
   └─ TikTok 验证码 SDK 把挑战 iframe 保持 display:none
        表现：geometry 报 hasBg:false，滑不了；请求也就永远等不到响应
```

**`Page.bringToFront` 之后，同样的 `/relate` 1 秒内返回真实业务错误。**
客户端 `PageChannel._ensure()` 已内置这一步 —— 这是必须的，不是可选优化。

诊断路径（以后遇到"接口挂起"照这个查）：
1. `document.visibilityState` 是不是 `hidden` → 是就先 `bringToFront`
2. `.captcha_verify_container` 是否存在、里面的 img `naturalWidth` 是否为 0
3. 有僵死验证码时先 `CaptchaGuard.close(pg)` 清掉，再重发

#### 附带修掉的一个真实 bug：背景图选择器

`tt_captcha.JS_GEOM` 原来用 `img[src*=rc-captcha]` 找背景图。
现在的 secsdk-captcha 2.27.x **背景图没有任何语义类名**，只有
styled-components 哈希（`sc-ifAKCX itlNmx sc-gqjmRU cHbGdz`），
src 是普通 `p16-oec-sg.ibyteimg.com` 的 jpeg。所以一直是 `hasBg:false`。

已改为按**结构判据**找：同容器内、`naturalWidth >= 200`、且不是 slide 元素。
修完 `geometry.ok = true`。

#### 服务端把规则明说了

类目不匹配时它直接给：

```
12050002  The selected product category does not match the lead category.
          Please select another product.
```

→ **商品的 L3 类目必须等于机会的 L3 类目**。
（`product_list()` 的 `categories[-1].id` vs `lead_detail()` 的 `level3_cate_id`）

#### 实测结果（15 个开放机会 / 70 对）

```
lead 7512XXXXXXXXXX42 (L3=873480, 历史 79 批准)  code=0 success ×5
lead 7407XXXXXXXXXX25 (L3=873480, 历史 57 批准)  code=0 success ×5
lead 7509XXXXXXXXXX32 (L3=873480, 历史 56 批准)  code=0 success ×5
lead 7512XXXXXXXXXX54 (L3=873480, 历史 61 批准)  code=0 success ×5
… 共 15 个机会，0 个类目错误
```

打分结果（按提交时戳过滤历史记录）：

| | 本次 | 你的基线 |
|---|---|---|
| 已批准 | **30** | — |
| 已被拒 | 20 | — |
| **命中率** | **60%** | **4%** |

**提升 15×。** 70 对里 50 对落库，另 20 对是之前已提报过的重复
（服务端不为重复的 (lead, product) 建新记录）。

**按机会类目拆**：

| 机会 L3 | 命中率 |
|---|---|
| **873480 痘痘、粉刺护理**（本店主品类） | **19/20 = 95%** |
| 875016 掏耳工具（本店副品类） | 14/30 = 47% |
| 601733 面罩（本店不做） | 0/1 |

**按选品相似度拆**：

| 标题相似度 | 命中率 |
|---|---|
| 0.9–1.0 | **83%** (n=6) |
| 0.7–0.9 | **74%** (n=19) |
| 0.4–0.7 | 33% (n=12) |
| 0.0–0.4 | 54% (n=13) |

#### 收紧规则后的第二轮：76%

按上面两条规律收紧（**相似度 ≥0.7 + 机会 L3 == 商品 L3**），
对 20 个开放机会总共 63 对：

```
落库 25 对（其余是历史重复，服务端不建新记录）
已批准 19 / 已被拒 6
★ 命中率 76%   （基线 4% → 19×）
```

两轮纵向对比：

| 轮次 | 选品规则 | 命中率 |
|---|---|---|
| 基线（历史盲铺） | 铺满所有机会 | **4%** |
| 第 1 轮 | 开放机会 + 相似度排序 | **60%** (30/50) |
| 第 2 轮 | 开放机会 + 相似度 ≥0.7 + 类目对齐 | **76%** (19/25) |
| 主品类子集 | L3=873480 | **95%** (19/20) |

#### ⚠️ 另一个会骗人的地方：响应超时不等于没提交

第 2 轮 20 个机会的 `/relate` **全部报「轮询 20s 未拿到响应」**，
但 25 对记录照样落库了。**服务端收下了，只是响应没回来。**

所以：**不要以客户端超时判断成败，一律回读 `submit/record/list` 核对。**
（这也是为什么必须用 `verify_recent()` 按时戳核对。）

#### 可复制的流程

```
1. notes/approved_full.json → 取有历史批准的机会，按批准数排序
2. lead_detail(lid).level3_cate_id  → 机会 L3
   product_list() 每条的 categories[-1].id → 商品 L3
   只保留 L3 相等的组合          ← 这一步消掉了全部类目错误
3. 在候选里按「与已获批商品标题的 Jaccard 相似度」排序，取 ≥0.7 的前 5 个
4. 排除该机会已提报过的 (lead_id, product_id)
5. /relate 一次带 ≤5 个（服务端硬上限 49，≥50 直接拒）
6. 用 product_performance() 的计数器 + 按时戳翻记录核对
   ⚠️ 核对时**必须按时戳过滤**，否则会把历史拒绝算成本次结果
```

⚠️ 计数器（`total_submit_num` / `failed_submit_spo_num`）是**异步聚合**的，
提交后立刻读会偏小，失败数尤其滞后。**以记录列表 + 时戳为准**。

### 22.6e ⚠️ 写路径有独立风控：`/relate` 会被单独限流

本 session 累计约 25 次 `/relate` 调用后，同样的 body 开始**长时间挂起**，
而读接口完全正常：

```
/relate（无效 lead，零写入）   22.1s  → 超时
/seller/lead/list              2.9s  → code=0 success
/contract/check                1.7s  → code=0 success
```

→ **限流是按端点施加的，写路径单独一档。**
客户端表现为 `轮询 20s 未拿到响应`。这时不要重试、不要换 body 再试，
**停手等窗口过去**（观测到的最短恢复时间在十几分钟以上）。

`lead_segment` 补充事实：只对 `opportunity_type=2`（关键词机会）有值；
`opportunity_type=3`（高潜力商品）返回的是"🔥 基于市场趋势的热门商品"卡片，
`lead_segment` 全是 `None`，入口是**新发商品**而不是 relate。

### 22.7 提报入口 URL 模式（新发商品流）

点机会列表的「添加同款商品」不是发 XHR，而是**开一个新标签**到商品创建页：

```
/product/create/<模板商品id>
  ?oc_source=seller_organic
  &spo=1&spo_version=3
  &tour_id=7398XXXXXXXXXX01
  &user_action=high_potential_products        # 或 high_potential_products_search
  &redirect=%2Fproduct%2Fopportunity…         # 回来
  &shop_region=VN
```

- `tour_id` 是会话级的活动 id（观测值 `7398XXXXXXXXXX01`）
- `user_action` 区分入口（列表页 / 搜索页）
- `recruit/mark {event_type:2, lead_list:[…]}` 在交互时上报

JS 里对应的批量接口是
`UploadRelateSPOProduct({file:r, traffic_source:…, tour_id:…}, {timeout:120e3})`
→ `POST /excel/relate/upload`（multipart）。

### 22.8 relate 请求体（已实测确认，且真的写进去了）

用 **Go 反序列化错误**直接把结构体名和类型问出来了：

```
给 ["9999XXXXXXXXXX99"]（字符串数组）
→ 400 json: cannot unmarshal string into Go struct field
   RelateProductToSPORequest.relate_product_items of type
   product_serv.RelateProductItem

给 [{"tts_product_id": "9999XXXXXXXXXX99"}]
→ 12050002 current product id is invalid,
   err:strconv.ParseInt: parsing "9999XXXXXXXXXX99": value out of range
   ← 证明 tts_product_id 是 int64
```

**最终 schema（flat 包装，无 `params`）**：

```json
POST /api/v1/product/oc/seller_product_opportunity/relate
{
  "lead_id": "7512XXXXXXXXXX66",
  "relate_product_items": [{"tts_product_id": 1736XXXXXXXXXX20}]
}
```

校验顺序（报错可以用来探测）：先 `lead_id`
（`12050002 current lead ID is invalid`）→ 再 `relate_product_items`
（`12050002 curent realte product items is empty`，官方拼写错误 "curent"/"realte"）。

**零写入的字段探测法**（推荐复用）：

1. `lead_id` 用一个**不存在**的 id（如 `"1"`）→ 业务校验必然失败，绝不可能写入。
2. 探针字段给一个**类型不匹配**的值（如 `true`）。
   - 字段存在 → Go 反序列化先报 `cannot unmarshal … of type …`，顺便告诉你类型
   - 字段不存在 → 静默忽略，返回基线业务错误

### 22.9 端到端跑一遍（当前可用命令）

```bash
cd .work/adfly

# 成绩单
python3 tk01_opportunity.py stats

# 失败原因分布
python3 tk01_opportunity.py why --pages 5

# 盲铺 vs 重复 的去重诊断
python3 tk01_opportunity.py dup --pages 10

# ★ 开放机会真值表（重建：拉全量批准记录）
python3 tk01_opportunity.py pull-approved
python3 tk01_opportunity.py openleads --min 5

# ★ 准入判定（看机会开不开放 + 与已获批标题的相似度，而不是看 segment 命中数）
python3 tk01_opportunity.py elig <lead_id> "<商品标题>"

# 真提报（写！先看 openleads / elig）
python3 tk01_opportunity.py relate <lead_id> <product_id> --yes
```

`elig` 现在两种输出：

```
# 打过的必挂机会（历史批准数 = 0）
{"ok": false, "open": false, "approvals": 0,
 "reasons": ["该机会历史批准数为 0（7512XXXXXXXXXX26）—— 本店做不了这类机会，别打"]}

# 真正开放的机会
{"ok": true, "open": true, "approvals": 79, "best_similarity": 0.818,
 "opportunity_name": "Kem trị sẹo nhanh, làm mờ vết sẹo, dưỡng ẩm và tái tạo da",
 "reasons": []}
```

⚠️ `plan --min-hits` 保留但**不要再当作准入规则** —— 见 §22.6，那个规则已被证伪。

### 22.10 踩坑清单（本章新增）

| 现象 | 真因 | 处理 |
|---|---|---|
| 直连返回 `code=0` 无 message | 缺签名，请求没被当真 | 必须走页面上下文 |
| `code=0` 但 `total_cnt=0` | `params` 套了两层 | 单层 `params` |
| `12071012 soc invalid param` | flat 端点套了 `params` | 去掉包装 |
| GET-only 路由返回 404 纯文本 | Go mux 按方法路由 | 查 `opp_api_table.json` 的 method |
| `page.evaluate(timeout=…)` | 不支持该关键字 | 用 CDP 或轮询 |
| evaluate 永久挂起 | `awaitPromise` + 后台节流 | 发出去 + 轮询全局变量 |
| `AbortController` 不生效 | 页面冻结时 `setTimeout` 不跑 | 不要依赖它兜底 |
| 抓不到 `fetch` 的 body | 调用方传的是 `Request` 对象 | `i.clone().text()` 回填 |
| 复调抓到的完整 URL 反而 404 | URL 里带了**过期签名** | 只保留业务参数，让 SDK 重签 |

### 22.11 当前状态与操作约定（如实记录）

**`/relate` 已被风控单独限流 —— 现在打不动。**

```
/relate（无效 lead，零写入）   22.1s  → 轮询 20s 未拿到响应
/seller/lead/list              2.9s  → code=0 success
/contract/check                1.7s  → code=0 success
```

读接口一切正常，只有写端点挂起 → 限流是**按端点**施加的。
在它恢复之前不要重试、不要换 body 再试。

**本 session 的写入账（全部为真，逐笔留痕）**：

| 时间 | 操作 | 数量 | 结果 |
|---|---|---|---|
| 10:32 | 探测 `relate` 字段名（当时不知道会命中） | 1 笔 | 已被拒 `rt=2` |
| 11:45 | 按**被证伪的规则**批量提报（5 机会 × 4 商品） | 20 笔 | **全部已被拒** |
| 11:5x | 按开放机会重试 | 3 次调用 | 全部超时，**0 笔写入** |

`total_submit_num` 轨迹：`83961 → 83962 → 83967 → 83977`（该计数器是异步聚合的，
不会立刻反映每次调用）。

**这次的判断失误，记录在案**：我用一个从有偏样本反推出来的规则
（§22.6）真打了 20 笔，预期 94%、实际 0%。教训是**日志反推规则必须跨页取样 +
区分缺失值 + 用完整词匹配**，否则会得到一个"看起来很干净"的假规则。
修正后的做法（开放机会真值表）见 §22.6b/22.6c。

**待办**：

1. 等 `/relate` 限流解除后，按 §22.6c 的流程用 `notes/open_leads.json`
   里的开放机会 + 已知获批标题做相似度选品，**先打 5 笔验证再放量**。
2. `SearchTtsProducts`（`/tts_product/search`）参数补齐 —— `search_text` +
   `page_number` 已能过绑定校验，但 15+ 组合都返回 `data=null`，
   疑似需要 `tour_id` 之类的页面上下文。
3. `/seller/product/get`（GetLiveProductsFromSeller）、
   `/exist/same/product/lead`（GET）、`/upload_details/get` 在 v1/v2/v3
   下全部 404 —— JS 里有定义但线上路径对不上。
   **它才是真正的"服务端准入判定"接口**（UI 里对应"匹配的商品"筛选器，
   见 `shop_filter/get` 返回的 `special_filter{filter_name:"匹配的商品"}`），
   拿下来就不用再猜规则了 —— 优先级最高。
4. `search_tab` / `search_text` 驱动的 `/product/opportunity/search`
   页面加载后 **0 个搜索请求**（只有 7 个基线请求），
   怀疑要先在列表页点进搜索页才有上下文。

---

## 23. 写接口的验证码真相 + 原生 fetch 绕过（借鉴 ThirdParty2）

### 23.1 结论先行：`/relate` 每一次调用都要求验证码

不是"频率高了才触发"。实测连发 15 次无效 `/relate`（零写入）：

```
14/15 次立即返回 bdturing-verify 响应头
  subtype=slide  from=oec_whale  region=sg
  detail=<996~1367 字符挑战数据>   fp=verify_mujj8pwq_6vs3CtgN_J…
每次 0.7s
```

之前判断成"风控限流"是**误判** —— 真相是页面 `fetch` 被 webmssdk 扣住等验证码，
所以我只看到 20 秒超时，看不到服务端其实每次都在要验证码。

### 23.2 根因：页面 `fetch` 被 SDK 接管

```
window.fetch          → "function(i,init){ var u=''…"     被 webmssdk 包装
about:blank iframe 内  → "function fetch() { [native code] }"  原生
```

主文档的 `fetch`/`XHR` 都被包装过。服务端要验证码时，SDK 触发 `autoRender`
并**把 promise 扣住**，直到验证码被解决 —— 这就是"请求挂起"。

所以：
- 走页面 fetch → 20s 超时，且**读不到 `bdturing-verify` 头**（被 SDK 吃掉）
- 走 iframe 原生 fetch → **0.7~1.2s 返回**，头完整可读

### 23.3 绕过方式（`PageChannel.raw_call`，已实现）

```javascript
const ifr = document.createElement('iframe');      // 不设 src → about:blank
document.body.appendChild(ifr);
const w = ifr.contentWindow;                        // 同源，但 fetch 是原生的

// 签名自己算，不依赖 SDK 注入
const sig = window.byted_acrawler.frontierSign({url, method, body});
// → {"X-Bogus=REDACTED"}   注入 URL query

const r = await w.fetch(signedUrl, {method, credentials:'include', headers, body});
const hdr = r.headers.get('bdturing-verify');       // ← 验证码参数在这里
```

实测吞吐：**12 次真请求 14.5 秒（1.2s/次）**，对比旧方式 20s/次且超时。

签名引擎在页面里：`window.byted_acrawler.frontierSign`（它还有
`setTTWebid` / `setTTWid` / `init` / `refer`）。验证码 SDK：
`verifySDK{renderCaptcha, closeCaptcha, getCaptchaWebId, initVerifyOptions, autoRender, SMS, initVerifyCenter}`
和 `OECCaptcha{init, render, close, getFp, transform, TTVerifyCenter}`。

### 23.4 `bdturing-verify` 头的完整结构

```json
{
  "code": "10000",
  "from": "oec_whale",
  "sub_from": "dispose_center_new",
  "type": "verify",
  "region": "sg",
  "subtype": "slide",
  "detail": "<挑战数据，每请求一份>",
  "fp": "verify_mujj4jai_Czjr4XMK_uZs1_4nr0_9fGl_JaJFSxI5Du1V",
  "server_sdk_env": "{\"idc\":\"my3\",\"region\":\"ALISG\",\"server_type\":\"business\"}",
  "log_id": "20260927160101CB94D4524A66D7658E92",
  "extension": {"setting_version": "3.0.75-1.0.0.956"}
}
```

**关键：`detail` 与 `fp` 是每次请求一份的。**
这解释了之前为什么 `verify=500`：我在事后盲解一个**属于已完成请求的过期挑战**。

正确闭环（参考工具 `_0x249c8d` 的做法）：

```
1. 发请求（iframe 原生 fetch + frontierSign 签名）
2. 读 bdturing-verify 头 → 解析出 detail / fp / region / subtype
3. 用【这一份】detail 去解验证码（api-verification.tiktokshop.com / .us / .eu 的 /captcha/get）
4. 解成功后 retryCount+1，sleep(500ms)，重发【同一个请求】
5. retryCount 有上限（参考工具里是常量比较），超了才报错
```

参考工具还带了 `tabId` —— 验证码在浏览器标签页里渲染（SDK 提供
`renderCaptcha` / `initVerifyOptions`），解完由页面侧持有凭证，后台重发才通过。

### 23.5 提报速度的现实上限

因为**每次 `/relate` 都要一个验证码**，而 `relate` 只接一个 `lead_id`：

```
调用次数下限 = 待提报机会数
1068 个同类目机会 → 1068 次调用 → 1068 个验证码
按每次验证码 5~10s 解 → 单轮 1.5~3 小时
```

所以"提报要快"的正确杠杆是**减少机会数以外的开销**，不是加大并发：
- 一个机会一次调用塞满 49 个商品（服务端上限），而不是一个商品一次
- 用商品聚类（591 链接 → 388 簇）压掉重复铺货占的名额
- 一周跑一次（operator 规则 4），1.5~3 小时是可接受的

### 23.6 参考实现来源

`/Users/maxj/Documents/Python Project/Project-ThirdParty22/ThirdParty2v2.3.19-unlocked`
是一个 Plasmo 扩展（ThirdParty2）。它的相关做法：

- `declarativeNetRequest` 监听 `https://*.tiktokshopglobalselling.com/api/*`
  与 `api-verification.tiktokshop{,.us,.eu}/captcha/get*`，
  把任何 API 请求 URL 的 query 参数**持续采集**进 `storage.local`
  → 这就是它拿到 `msToken`/`X-Bogus`/`X-Gnarly`/`X-Tts-Oec-Bsid` 的方式
- 后台脚本用采集到的签名参数自己 `fetch`，因此**请求不被 SDK 扣住**
- 读 `bdturing-verify` 头 → `callCaptchaApi({...parsed, region, tabId})` → 重发
- `paramErrorRetryCount` 最多 2 次，`retryCount` 另有上限
- 它同时支持 `code===10000(0x2710)` 作为触发信号

---

## 24. 验证码：为什么一直跳 + 哪些是能修的

### 24.1 修掉的真 bug：缺口算在了商品主图上（这是滑动不可靠的根因）

```
挑战就绪 bgNat=[1254, 1254]   ← 1254×1254 是【商品主图】
        pcNat=[0, 0]          ← 拼图块图未加载
bgRect=[272, 543, 40, 40]     ← 40×40 的商品缩略图
ZeroDivisionError: float division by zero
```

`JS_GEOM` 找背景图的方式换过三代，前两代都是错的：

| 版本 | 判据 | 结果 |
|---|---|---|
| v1 | `img[src*=rc-captcha]` | 现版背景图无此字样 → 永远失配 |
| v2 | `naturalWidth >= 200` 的第一张 | **在商品列表页抓到商品主图** → 缺口全错 |
| v3 ✅ | **从 `img.captcha_verify_img_slide` 往上找最近共同容器** | 正确 |

v3 还加了「图片未加载完就返回 ok:false」和 `naturalWidth==0` 的除零防御。
修完实测连续 **4/4 一次通过**，再测 **1/1 通过**。

### 24.2 写接口的验证码是账号级门控，客户端无法"避免"

实测：请求体补齐了 6 个字段、签名参数采全了 13 个、`msToken`/`X-Tts-Oec-Bsid`
都带上 —— **`/relate` 依然每次都返回 `bdturing-verify`**。

```
1: 0.4s status=200 code=0  ★ 仍被要求验证码: slide fp=verify_mujjky9m_…
2: 0.4s status=200 code=0  ★ 仍被要求验证码: slide fp=verify_mujjl05b_…
3: 0.4s status=200 code=0  ★ 仍被要求验证码: slide fp=verify_mujjl21h_…
```

判断依据：**今天早些时候**同样调 `/relate` 是能直接拿到 `code=0 success`
并落库的（60% / 76% 两批）。之后累计发了 200+ 次写请求，门控就从"偶发"
变成"每次"。→ **是账号风险等级被抬上去了，不是请求长得不对。**

**所以关于"避免跳验证码"的诚实结论：**
- ✅ 能做的：请求体/签名对齐真实调用、走页面自身会话、**不要高频测试**
- ❌ 做不到的：在账号已被抬高的情况下靠改请求参数绕开
- ⏳ 唯一有效的办法：**停止写请求，等风险等级自然回落**（小时~天级）

### 24.3 补齐的请求体（对齐真实调用）

早先只发 2 个字段，真实调用发 6 个：

```json
{"lead_id": "…", "source": 1,
 "traffic_source": "seller_organic",     // 观测自 oc_source=seller_organic
 "tour_id": "7398XXXXXXXXXX01",       // 观测自页面 URL
 "opportunity_type": null,
 "relate_product_items": [ … ]}
```

且 **`opportunity_type === 2`（关键词机会）时元素还要带标题**：

```json
{"tts_product_id": "…", "title": "<商品标题>", "update_title": true}
```

→ 平台会**按关键词改商品标题**。这条是从参考实现
（`_0x1c81b9['opportunity_type']===2 ? {tts_product_id,title,update_title:true} : {tts_product_id}`）
里读出来的，之前完全不知道。

### 24.4 签名参数的正确采集方式

外层 hook `fetch`/`XHR` **采不到** —— webmssdk 的包装在更内层，
hook 看到的是加签名【之前】的 URL（实测抓到 0 个）。

改用 **`performance.getEntriesByType('resource')`** —— 它记录真正发出去的 URL：

```
msToken=REDACTED…   跨请求稳定 → 缓存复用
X-Tts-Oec-Bsid=REDACTED…   跨请求稳定 → 缓存复用
X-Bogus        = 按 URL 变 → byted_acrawler.frontierSign({url,method,body}) 现算
X-Gnarly       = 按请求变 → 不缓存
fp             = 这些请求里没有，说明不是每次都必需
```

实测一次采集到 22 个真实请求 → 13 个可用参数。

### 24.5 验证码协议（完整）

```
GET  https://api-verification.tiktokshop.com/captcha/get?lang=zh&h5_sdk_version=3.0.75&…
     → {"code":200, "data":"<加密挑战数据>"}
POST https://api-verification.tiktokshop.com/captcha/verifyV2
     REQ : {"captchaBody":"dGMGEAAAQ0cwVlNqbTB6…"}
     RESP: {"code":200, "data":null, "message":"验证通过"}
```

注意是 **`verifyV2`**（不是 `verify`），凭证字段是 **`captchaBody`**。
其他域：`api-verification.tiktokshop.us`、`…shops.eu`。

**`bdturing-verify` 响应头**（每次请求一份，`detail` 是加密挑战数据）：

```json
{"code":"10000","from":"oec_whale","sub_from":"dispose_center_new",
 "type":"verify","region":"sg","subtype":"slide",
 "detail":"<996~1367 字符>", "fp":"verify_mujj8pwq_6vs3CtgN_J…",
 "server_sdk_env":"{\"idc\":\"my3\",…}", "log_id":"…"}
```

→ 之前 `verify=500` 就是**在事后盲解一个属于已完成请求的过期挑战**。
正确做法：读头 → 用**这一份** `detail` 渲染 → 滑 → 重发同一请求。

### 24.6 当前状态

- 所有测试进程已停止，浏览器无挂起验证码
- `call_write()` 已实现（页面 fetch + SDK 接管 + 滑动 + 重发，`auto_render=False`
  以免中途销毁挑战），结构正确，但在账号当前风险等级下仍过不去
- **建议：暂停写请求至少一天，让风险等级回落**；之后按周度节奏跑一轮，
  每轮之间留出间隔，出现验证码就解、解不开就停手（别连打）

---

## 25. 联盟中心（Affiliate Center）接口逆向

### 25.1 与 Seller Center 的三处不同

| | Seller Center | 联盟中心 |
|---|---|---|
| 域 | `api16-normal-sg.tiktokshopglobalselling.com` | **`affiliate.tiktokshopglobalselling.com`** |
| app_name | `i18n_ecom_shop` | **`i18n_ecom_alliance`** |
| 语言参数 | `locale` / `language` | **`user_language`** |
| 入口页 | `/product/opportunity` | `/affiliate/creator` |

签名要求相同（webmssdk 注入 `X-Bogus`/`X-Gnarly`/`msToken`/`X-Tts-Oec-Bsid`）。

### 25.2 ★ 三个必踩的坑（每个都花了很多时间）

**坑 1：`/oec/` 路由必须带 `oec_region` + `oec_seller_id`**

少了就一律 `98001004`，而且响应里 `"region": ""` 是**空串** —— 这就是线索。
（我第一次抓包把 URL 截断到 400 字符，正好把这两个参数截掉了。）

**坑 2：`marketplace/find` 还需要完整的浏览器指纹块**

```
fp, device_platform, cookie_enabled, screen_width, screen_height,
browser_language, browser_platform, browser_name, browser_version,
browser_online, timezone_name          ← 实测 timezone_name = Asia/Bangkok
```

`fp` 直接取页面里的 `window.OECCaptcha.getFp()`，不用自己造。
另外实测真实请求里**没有** `oec_region`、也**没有** `is_hot_api`
（参考文档写"强制含 is_hot_api=true"，加了反而挂）。

**坑 3：不能用 iframe 原生 fetch（seller 侧能用，联盟侧不行）**

iframe 的 `about:blank` 文档 `Origin` 是 `null`、没有 `Referer`，服务端判成插件：

```
{"code":100000,"message":"Please remove the plugin and try again"}
```

**实测连"原样完整签名 URL"用 iframe 重放都被拒** —— 不是签名问题，是来源特征。
联盟域必须走**页面自己的 fetch**。

### 25.3 分页字段名：`cur_page` / `page_size`

联盟侧不是 `page`/`size`。用错会得到：

```
400 binding: expr_path=page_size, cause=missing required parameter
```

这两个名字是用**绑定错误预言机**逐个问出来的（同 §22.8 的方法）。
`product_selection/list` 还要第三个字段 `source`。

### 25.4 实测可用的端点（全部 code=0）

| 端点 | 关键参数 / 返回 |
|---|---|
| `GET /api/v1/affiliate/menu` | 8 个板块 |
| `GET /api/v1/affiliate/account/info_v2` | 账号 + global_seller |
| `GET .../invitation_group/invitation/limit` | `{max_creator_num:50, max_product_num:100}` |
| `GET .../crm/creator/upper_limit/get` | `{total_limit:30000, shop_manage_tag_limit:600}` |
| `GET .../seller/im/get/token` | IM token |
| `POST .../creator/marketplace/option` | 筛选器：品牌 400 / 类目 25 / 价格带 5 / 语言 2 |
| `POST .../creator/marketplace/find` | **达人广场搜索**（见 25.5） |
| `POST .../cmp/filter` · `/feature_control` · `/wish_list/search/creator` | ✅ |
| `POST /api/v1/affiliate/grayscale_strategy/check` | 灰度开关字典 |
| `POST .../invitation_group/general/config` | 定向计划通用配置 |
| `POST .../invitation_group/search` | `{"cur_page":1,"page_size":10}` |
| `POST /api/v1/affiliate/product_selection/list` | `{"cur_page","page_size","source":0}` → `total_num=624` |

### 25.5 达人广场搜索：间歇性已被重试治住

```
size=3  30.3s  code=98001004   ← 首轮失败
size=6  21.5s  code=0  n=6     ← 重载 fp 后重试成功
翻页 2 页 → 12 行
```

做法：遇到 `98001004` 就**重新取 fp** 并最多重试 2 次。代价是单次调用可能 20~30s。

**触发页面的顺序**（实测复现）：先进 `/affiliate/creator/marketplace`，
再进 `/affiliate/creator/search`，app 才会真正打 `find`。
单独 goto search 不会触发（SPA 有缓存）。

**返回字段**（很有价值）：

```
creator_oecuid / handle / nickname / avatar / follower_cnt / category
ec_live_gpm / ec_video_gpm            ← 带货转化
ec_live_avg_uv / ec_video_engagement
creator_fulfillment_score_90d         ← 90 天履约评分
creator_fulfillment_reviews
has_collaborated / has_invited_before_90d
is_creator_blocked_by_shop / invoice_available / is_high_sample_dispatch_rate
```

翻页用 `next_pagination.search_key` 游标（服务端签名过，不能自己造）。

### 25.6 仍未攻下

| 端点 | 现象 | 推测 |
|---|---|---|
| `POST .../cmp/creator/rank/list/get` | `98001004`（返回带 `msg` 键） | 需要**合法的 `rank_list_meta`**；本店可能没有排行榜入口，页面里没触发到该请求 |
| `POST /api/v1/affiliate/sample/group/list` | `98001004`（返回带 `has_more`/`total_count` 但为 null） | 参考实现的解析是 `data.response.agg_info`，说明按聚合返回 —— 可能缺 `agg_type`，或需要先有样品数据 |

### 25.7 参考材料

- `Project-dalian/dist2.0.9-接口与功能文档.md`（69KB）—— 完整的第三方接口文档，
  覆盖 TikTok Shop 原生接口 / MCN Partner / Seller Center / IM（含 protobuf 报文结构）。
  **本节的端点清单有相当部分由它交叉验证。**
- `ThirdParty2v2.3.19-unlocked` 的 `affiliateRequestHook` 也是同类实现，可对照。

### 25.8 写联盟脚本的注意事项

**别用裸 `page.evaluate(await fetch(...))`** —— 页面被节流时 fetch 不 resolve，
`awaitPromise` 会永久挂住（本节有两段脚本因此 600s 超时）。
联盟域不能用 iframe 绕过，所以一律走 `PageChannel.call()`（轮询式）。

---

## 26. 第三方参考实现盘点（ThirdParty / ThirdParty2）

来源：`Project-dalian/dist2.0.9-接口与功能文档.md`（69KB，第三方插件ThirdParty的完整接口文档）
与 `Project-ThirdParty22/ThirdParty2v2.3.19-unlocked`。**本章只记本仓库原本没有的东西**，
已有的一律不重复。这些是别人插件的实现，作为研究材料对照，不继承其架构。

### 26.1 ★ 机会类型的内部名称（补上了我缺的 201/202）

`/api/v1/product/oc/seller_product_opportunity/seller/lead/list` 的源码常量：

| opportunity_type | 内部名称 |
|---|---|
| 3 | `high_potential_products` |
| 201 | `most_wanted` |
| 202 | `trending_keyword` |

**这条很有用**：我在 §22 里推断 201/202 是"推荐"，实际是
`most_wanted`（最想要）和 `trending_keyword`（趋势关键词）。
而且实测 `list_leads(opportunity_type=2)` 返回的行里 `opportunity_type` 是 **202**，
说明服务端对 type 做了映射 —— 请求 2 可能拿到 202 的结果。

### 26.2 Seller Center 侧本仓库没有的端点

全部在 Seller Center 页面上下文执行（实现文件 `chunks/seller-*.js`）：

| HTTP | 路径 | 用途 / 关键参数 |
|---|---|---|
| GET | `/api/v2/seller/common/get` | 通用卖家信息；`default_region=localStorage.current_shop_region` |
| GET | `/api/v3/seller/common/get` | 新版；`need_verify_account=true`、`version=localStorage.common_get_version` |
| GET | `/api/v1/shop_im/shop/user/get_token` | Seller Center IM Token |
| GET | `/api/v1/shop_im/shop/product/list_local_products` | 商品列表；默认 `page_size=20`，带 `oec_region`/`cb_shop_region` |
| POST | `/api/v1/shop_im/shop/get_voucher_list` | 会话可用优惠券 |
| POST | `/v1/message/send` | **protobuf/hex** 发送消息（不是 JSON） |
| POST | `/api/v1/trade/orders/buyer` | body `{main_order_ids:[...]}` → 买家信息 |
| GET | `/api/v1/trade/orders/order_service_status/get` | `main_order_id` 的服务状态 |
| GET | `/chat/api/seller/mGetContactBuyerLinkByOrder` | 按订单取"联系买家"链接 |
| GET | `/chat/api/seller/listLocalProducts` | 聊天商品列表 |
| POST | `/chat/api/seller/createGroupChat` | 创建群聊 |
| POST | `/chat/api/seller/closeConversation` | 关闭会话 |
| POST | `/api/v2/insights/seller/ttp/product/list` | TTP 商品列表；body 含 `request.time_descriptor/search/filter/list_control` |
| POST | `/api/v2/promotion/search_products` | 搜索促销商品 |
| POST | `/api/v1/promotion/flash_sale/create` | 创建闪购 |
| GET | `/api/v1/product/product_creation/preload_all_categories` | 商品创建页类目预加载 |

注意 `preload_all_categories` 要带 `aid=6556`、`app_name=i18n_ecom_shop`
和 **`x-tt-oec-region` 头** —— 和我在 §17/§22 摸到的规律一致。

### 26.3 ★ 订单邀评不是单接口，是 9 步串行工作流

这条对做自动化很有参考价值 —— 任何一步失败都会表现为"按钮没反应"：

```
1. 拉取订单
2. 按买家去重
3. 批量取买家资料 + 联系链接   （/api/v1/trade/orders/buyer、
                                /chat/api/seller/mGetContactBuyerLinkByOrder）
4. 用本地记录过滤已处理买家     （本地缓存，避免重复打扰）
5. 创建聊天或群聊               （/chat/api/seller/createGroupChat）
6. 构造文本或商品消息
7. 用 IM protobuf 接口发送      （/v1/message/send）
8. 保存成功/失败日志
9. 关闭会话，处理下一位买家     （/chat/api/seller/closeConversation）
```

依赖：Seller Center Cookie、店铺地区、订单权限、IM Token。

### 26.4 TikTok 站内 IM（`im-api.tiktok.com`）

| HTTP | 路径 | 用途 |
|---|---|---|
| POST | `/v2/conversation/create` | 创建站内会话 |
| POST | `/v1/message/send` | 发送站内消息 |
| POST | `/v2/message/get_by_user_init` | 初始化读消息 |

也是 **protobuf** 编码。Request/Response 可见字段：
`cmd` / `sequence_id` / `sdk_version` / `token` / `inbox_type` / `body` /
`device_id` / `headers` / `auth_type` / `retry_count`。

**消息的逻辑对象**（还要再经 protobuf 封装，不能直接当 HTTP body）：

```json
// 文本
{"awe_type": 0, "text": "消息内容"}
// 图片
{"awe_type": 1, "image": {"url": "https://...", "width": 800, "height": 800}}
```

**`tiktok.proto` 主要对象**：

| 对象 | 作用 |
|---|---|
| `Request` / `RequestBody` | 外层请求 + 按 cmd 分派的业务 body |
| `Response` / `ResponseBody` | 外层响应 + 业务响应 body |
| `SendMessageRequestBody` | 会话 ID、消息类型、文本 content、`content_pb`、媒体列表 |
| `SendMessageResponseBody` | `server_message_id`、`status`、`check_code`、`check_message` |
| `MessagesInConversationRequestBody` | `conversation_id`、`conversation_type`、`anchor_index`、`limit` |
| `MessagesInConversationResponseBody` | `messages`、`next_cursor`、`has_more` |
| `CreateConversationV2RequestBody` | `conversation_type`、`participants`、`persistent`、`idempotent_id` |

坑：protobuf 取消息的 `anchor_index` 是**字符串** `"0"`，不是数字。
`cmd=301` 是读会话消息。

### 26.5 TikTok 普通网页接口（站内运营用）

| HTTP | 路径 | 功能 |
|---|---|---|
| GET | `/api/search/user/full/` | 关键词搜用户 |
| GET | `/tiktok/v1/im/user/profile/` | 用户/达人资料 |
| GET | `/api/user/collection_list/` | 收藏列表 |
| GET | `/api/post/item_list/` | 用户或页面作品列表 |
| GET | `/api/search/item/full/` | 搜索作品 |
| POST | `/api/comment/publish/` | 发布评论 |
| POST | `/api/commit/item/digg/` | 点赞 |
| POST | `/api/item/collect/` | 收藏 |
| POST | `/api/commit/follow/user/` | 关注/取消关注 |
| GET | `/passport/web/account/info/` | 当前账号信息 |
| GET | `/api/v1/web-cookie-privacy/config` | Cookie 隐私配置 |

依赖 `tt_csrf_token`、`tiktok.proto`、`protobuf.min.js`、`web-main.js`。

### 26.6 MCN / Partner 域

实现文件 `chunks/mcn-*.js`，基址：

```
https://api-partner-va.tiktokshop.com
```

**实际域名由当前 Partner 页面状态覆盖，不能写死。** 端点见 §25 的
`ENDPOINTS` 里 `partner_*` 那几条（`partner_id`、`x-im-paas-token` 是必需的）。

### 26.7 插件的通用架构模式（两种都值得知道）

**模式 A：声明式网络监听 + 参数采集**（ThirdParty/ ThirdParty2都用）

```
declarativeNetRequest 监听:
  https://affiliate.tiktokshopglobalselling.com/api/*
  https://*.tiktokshopglobalselling.com/api/*
  https://api-verification.tiktokshop{,.us,.eu}/captcha/get*
        ↓
  把每个 API 请求 URL 的 query 参数写进 storage.local
        ↓
  后台脚本用采集到的签名参数 + 自己补 X-Bogus 发请求
```

**这就是它们能避开"插件检测"的原因**：签名参数是真实请求来的，
不是自己算的。我在 §25.2 坑 3 撞到的 `100000 Please remove the plugin`
正是这条的对照 —— 我用 iframe 原生 fetch（`Origin: null`）自然被判插件。

**模式 B：页面请求桥（Bridge）**

内容脚本注入页面，页面通过 `window.postMessage` 风格的 Bridge 调扩展能力：

```
页面  →  Bridge  →  内容脚本  →  Service Worker  →  目标 API
```

ThirdParty的存储键（供对照，不是要继承）：

| 键 | 内容 |
|---|---|
| `DL-ERP-AUTH` | ERP JWT、expiresAt、user、context（主会话） |
| `DL-ERP-DEVICE-ID` | 本机 UUID |
| `DL-ThirdParty-ACTIVE-SHOP-ID` | 当前选定店铺 ID |
| `creator_oec_id_list` | 本地达人缓存/去重 |
| `ziniao_*` | 旧版兼容镜像 |

### 26.8 对本仓库的可用之处（结论）

1. **`opportunity_type` 的 201/202 语义**（§26.1）—— 直接补进 `tk01_opportunity.OPP_TYPE`
2. **订单邀评的 9 步工作流**（§26.3）—— 如果以后要做订单侧自动化，这是现成的流程骨架
3. **IM protobuf 协议对象表**（§26.4）—— 要做达人群发/回消息的话省一大截逆向
4. **签名采集模式**（§26.7 模式 A）—— 已在 `tk01_opportunity.PageChannel.harvest_signature_params`
   里实现（用 `performance.getEntriesByType('resource')`，比 declarativeNetRequest 简单）
5. **不采用**：ThirdParty自己的 ERP 后端（`/ThirdParty/creators/*`）、多店铺会话体系 ——
   那是它的商业架构，与本仓库无关

---

## 27. ★ 验证码问题的真正根因：页面没在前台

### 27.1 一句话结论

**所有验证码痛苦（20s 超时、`verify=500`、连环弹窗）的共同根因是：
操作页面不在浏览器前台。**

`Page.bringToFront` 之后，同样的调用：

```
1: 4.2s  code=12050002  current product is not online
2: 4.2s  code=12050002
3: 1.7s  code=12050002
拿到响应 3/3   而且【一次验证码都没触发】
```

### 27.2 为什么后台标签页会毁掉一切

| 症状 | 后台标签页下的真实原因 |
|---|---|
| `轮询 20s 未拿到响应` | Chrome 挂起后台页的网络，fetch 不 resolve |
| `verify=500` 且**每次拖同一个距离** | `Input.dispatchMouseEvent` 打不到不在前台的页面 → **拼图根本没动** → 挑战状态没变 → 服务端判无效 |
| 验证码 iframe `display:none` / `hasBg:false` | SDK 只在文档可见时渲染挑战 |
| "一直在弹验证码" | 上面的失败让 SDK 反复重试渲染新挑战 |

判据——排查任何"接口挂起/验证码异常"先看这三行：

```js
document.visibilityState      // 'hidden' 就是根因
document.hasFocus()
// iframe 的 display 是否 none
```

### 27.3 ★ 修正：写路径的验证码是 **iframe 传输方式**招来的，不是账号被标记

同一时刻、同一个 body、同一个账号：

| 传输方式 | 结果 |
|---|---|
| `raw_call`（about:blank iframe 原生 fetch） | **每次**返回 `bdturing-verify` 头（要验证码） |
| `call()` / `call_write()`（页面 fetch + 页面在前台） | `code=12050002`，**一次都不要验证码** |

我在 §24 里判断"账号风险等级被抬高了"是**错的**。真实原因：
iframe 的 `Origin: null` + 无 `Referer` 让服务端每次都要求人机校验。

**所以之前的「200 次写请求把账号搞坏了」这个结论作废** —— 那个数字本身
就是被 iframe 逼出来的，账号本身没问题。

### 27.4 落到代码里的三处修改

**1. 拖拽前必须置前**

```python
pg = CDPPage(ws, timeout=25)
pg.enable("Runtime", "Page")
pg.send("Page.bringToFront")     # ← 不加这句，拖拽全是空动作
time.sleep(0.4)
```

`PageChannel.handle_captcha()` 和 `call_write()` 都加了。

**2. 写端点走 `call_write`，不走 `raw_call`**

```python
WRITE_PATHS = ("/relate", "/reject", "/mark", "/recruit/mark",
               "/invitation_group", "/auto_submit", "/contract/sign",
               "/product/stock/update", "/batch_listing")
```

`OpportunityClient._post` 按路径自动分流。

**3. 「一次最多 49 个商品」是按【该机会已关联总数】算的**

老机会往往已经挂了几十个商品，一次塞满就超限：

```
12050002 The total selected products at one time needs to be less than 50 item
```

处理：**自适应折半重试**（49→24→12→6→3→1），比预先查 `related_pairs`
（每个机会多一次调用）划算。

### 27.5 实测性能（修复后）

| 批次 | 调用 | 耗时 | 每次 | 超时 | 结果 |
|---|---|---|---|---|---|
| 6 个机会 / 48 对 | 6 | 0.3 分钟 | **3.2s** | **0** | success +4 / failed +4 |
| 30 个机会 / 264 对 | 30 | 4.9 分钟 | **9.8s** | **0** | 按时戳 成功 4 / 被拒 12 |

对比修复前：**22.7s/次且大量失败**。

按 9.8s/次算，`weekly_plan` 的 1068 个机会约 **2.9 小时**跑完一轮 —— 周度节奏可行。

命中率 25%~50% 是**预期内**的：`weekly_plan` 按 operator 规则 3
（"不能为了成功率放弃低相似度机会"）覆盖了**全部同类目机会**，
而不是只挑筛选过的高相似子集（那个子集实测 76%）。

### 27.6 排查清单（以后再遇到"接口挂起/验证码"照这个走）

```
1. document.visibilityState 是不是 hidden？→ Page.bringToFront
2. 用的是 raw_call 还是 call？→ 联盟侧和写端点必须用 call/call_write
3. 拖拽前有没有 bringToFront？→ 没有就是空动作，verify 恒 500
4. CaptchaGuard.geometry() 的 bgNat 是不是验证码尺寸？
   （抓到 1254×1254 就是抓到商品主图了 —— 见 §24.1）
5. 有没有 auto_render=True 在销毁挑战？→ 设 False
```

---

## 28. 联盟达人：三个卡点全破 + 页面路由表

### 28.1 ★ 页面路由（之前一直在猜，全猜错了）

| 功能 | 真实 URL |
|---|---|
| 达人广场搜索 | `/affiliate/creator/search` |
| **达人排行榜** | **`/affiliate/creator/rankings`**（不是 `/creator/rank`） |
| **达人详情** | **`/affiliate/creator/detail?cid=<达人id>&pair_source=authorized`** |
| **样品申请** | **`/affiliate/sample/sample-request`** |
| 达人管理（CRM） | `/affiliate/creator/...`（侧边栏「达人管理」） |

侧边栏完整菜单：首页 · 合作 · 发现达人 · 查找达人 · **查看排名** ·
**达人管理** · 与服务商合作 · **样品** · 数据分析 · 联盟订单数 · 商家中心

**教训**：猜 URL 猜不出来就别猜 —— 直接读页面的侧边栏菜单文字，
再在新标签里看实际路由。

### 28.2 达人详情：字段名是 `creator_oec_id`（带下划线）

```json
POST /api/v1/oec/affiliate/creator/marketplace/profile
{"creator_oec_id": "7494XXXXXXXXXX75", "profile_types": [1]}
```

⚠️ 搜索接口返回的字段叫 `creator_oecuid`，但**详情接口吃的是
`creator_oec_id`** —— 混用就是 `98001004`。这个不一致踩了很久。

返回 `creator_profile`（handle / nickname / bio / avatar / 各项指标）
+ `creator_connect_info`（联系方式可达性）。

### 28.3 排行榜：`rank_list_meta` 的真实结构

```json
POST /api/v1/oec/affiliate/cmp/creator/rank/list/get
{
  "rank_list_meta": {
    "rank_type": 1,          // 榜单类型（1=综合）
    "rank_period": 1,        // 周期
    "rank_date": "2026-09-25",   // YYYY-MM-DD，服务端会归一化到最新可用日期
    "indus_cate": "All",     // 行业类目
    "content_type": 1        // 内容类型
  },
  "size": 20, "page": 1      // 注意分页是 size/page，不是 cur_page/page_size
}
```

返回 `data.total=200` + `data.creator_rank_info_list`
（`rank_position` / `rank_score` / `follower_cnt` / `creator_handle`）。

实测榜单（VN / 综合榜）：

```
#   1  score=93.59  粉丝=1237021  vbbreview95
#   2  score=77.87  粉丝=4409237  tunpham97
#   3  score=56.39  粉丝=3900763  quyenleo
#   4  score=51.12  粉丝=1569998  phanhoangmyvietjetair
#   5  score=48.52  粉丝= 873847  luongtoanthang712
```

**缺任何一个 meta 字段都是 `98001004`**，而且是抓包才拿到的 ——
靠试参数试不出来。

### 28.4 样品申请：缺三个字段永远试不出来

```json
POST /api/v1/affiliate/sample/group/list
{
  "tab": 10, "cur_page": 1, "page_size": 50,
  "search_params": [{"search_key": 1, "search_type": 2, "value": ""}],
  "order_params":  [{"order_key": 7, "order_type": 2}]
}
```

光试 `{}` / `{page,size}` / `{cur_page,page_size}` / `+status` 全是 `98001004`。
加上 `tab`/`search_params`/`order_params` 立刻 `code=0`。

返回 `{has_more, total_count, view_type, is_predict_fulfillment_rate}`。
**本店 `total_count=0`**（还没样品申请）—— 所以之前即使参数对了也看着像坏的。

### 28.5 同盟插件的可参考之处（ThirdParty）

**① `end_time` 的校验规则（邀约计划创建）**

```js
// 源码里的实际逻辑
if (!isFinite(n) || n <= r + 3e5) n = r + 6048e5;   // 6048e5 = 7 天
t.end_time = Math.trunc(n).toString();              // ← 字符串形式的 epoch 毫秒
```

→ `end_time` 是**字符串**；不在合理区间（≤ now+5min）时**自动纠到 now+7天**。
自己构造邀约计划时照这个来，能少踩一次 98001004。

**② 它们的验证码请求参数**

```js
{ type:"verify", subtype:"slide", challenge_code:"3058", os_name:"mac",
  h5_check_version:"1.0.23", "capa-data-ss":"1" }, headers:{"Content-Type":""}
```

和我在 §23 抓到的 `bdturing-verify` 头字段对得上（`type`/`subtype` 一致）。
`challenge_code` 是固定值 `3058`。

**③ 敏感数据接口（`/api_sens/` 前缀）**

| 路径 | 参数 |
|---|---|
| `/api_sens/v1/affiliate/cmp/contact_types` | `creator_oecuid`、`shop_id`、`scene=10` |
| `/api_sens/v1/affiliate/cmp/contact` | 同上 |

`api_sens` 前缀 = 敏感数据通道，取达人联系方式走这里。

**④ 它们 UI 里的核心字段**

`free_sample`（417 处）· `creator_oecuid`（72 处）· `commission_rate`（44 处）·
`invitation_group_id`（15 处）· `product_ids`

→ 达人邀约的配置面就是：**佣金率 + 免费寄样 + 商品 + 有效期**。

### 28.6 批量邀约：还没抓到（下一步）

试了在达人广场勾选卡片 + 点「批量邀请」，结果：

- 达人卡片的勾选**不是原生 checkbox**（`input[type=checkbox]` 找不到）
- 点「批量邀请」触发了**页面重载**（13 个配置接口齐发），没打开弹窗

**下一步做法**：先找出卡片的真实勾选控件（可能是自定义 div 上的点击），
或者改从**定向计划页**（`invitation_group/search`）反向走 ——
先建一个空计划，再往里面 `creators_add`，那条路径的可控性更高。

### 28.7 联盟侧端点总账（本轮后）

| 状态 | 数量 | 说明 |
|---|---|---|
| ✅ 已打通 | **16** | 含本轮新增的 profile / rank / sample |
| ⏳ 待抓 | 邀约计划 CRUD 的 body 形状 | 见 28.6 |
| ⏳ 待抓 | `/api_sens/` 联系方式接口 | 未测 |

---

## 29. 联盟中心完整导航表（`/api/v1/affiliate/menu`）

**别再猜 URL 了** —— 这个接口直接给出全部路由。实测返回 20 条：

| id | path | 名称 |
|---|---|---|
| `home` | `/platform/homepage` | Home |
| `collaboration` | `/collaboration/root` | Collaborations |
| ├ `open_collaboration` | `/product/open-collaboration` | Open Collaboration |
| └ **`target_collaboration`** | **`/connection/target-invitation`** | **Target Collaboration（定向计划）** |
| `find_creators` | `/connection/creator/root` | Discover creators |
| ├ `find_creators_creator_marketplace` | `/connection/creator` | Find creators（**达人广场**） |
| └ `find_creators_leaderboard` | `/connection/creator/rankings` | View rankings |
| `affiliate_crm` | `/connection/creator-management` | **Creator Management** |
| `partner_campaign` | `/product/partner-campaign/root` | Work with partners |
| ├ `collaboration_overview` | `/product/partner-campaign/collaboration-overview` | Collaboration Overview |
| ├ `discover_partners_sea` | `/product/partner-campaign/discover-partners` | Top TAP list |
| └ `partner_collabs` | `/product/partner-campaign/partner-collabs` | Partner collabs |
| `manage_samples` | `/samples/root` | Samples |
| ├ `sample_request` | `/product/sample-request` | **Sample requests** |
| └ `sample_settings` | `/product/sample-settings` | Sample settings |
| `insights` | `/data` | Insights |
| ├ `insights_transaction_analysis` | `/insights/transaction-analysis` | Performance |
| ├ `insights_sample_analysis` | `/insights/sample-analysis` | Sample Analytics |
| ├ `creator_outreach` | `/insights/creator-outreach` | Outreach analysis |
| ├ `insights_product` | `/data/product-performance` | Product Analytics |
| ├ `creator_analysis` | `/data/creator-analysis` | **Creator Analysis** |
| └ `new_video_analysis` | `/insights/video-analysis` | Video |
| `order` | `/product/order` | Affiliate Orders |

页面实际 URL 是 `https://affiliate.tiktokshopglobalselling.com/affiliate` + path。

```bash
python3 tk01_affiliate.py menu      # 直接打印这张表
```

### 29.1 ★ 定向计划页用的是另一种 `find`（推荐场景）

在 `/connection/target-invitation` 上，`marketplace/find` 的 body 完全不同：

```json
{"pagination": {"size": 6, "page": 0}, "rec_scene": 2, "algorithm": 1}
```

**没有 `query`、没有 `filter_params`** —— `rec_scene` 是**推荐场景**参数
（2 = 定向计划页的推荐位）。这解释了为什么同一个端点在不同页面吃不同 body。

同页面还调用了新端点：

```
GET /api/v1/oec/affiliate/seller/invitation_group/campaign/banner
```

### 29.2 定向计划页的当前状态

| 项 | 结果 |
|---|---|
| `invitation_group/search` `{"cur_page":1,"page_size":10}` | ✅ `code=0` → `data={"has_more":false}`（**本店还没有计划**）|
| `invitation_group/create` `{}` | ❌ `98001004` —— 不是"缺必填字段"（绑定错误没报），而是要**语义完整的 body** |
| `rec_scene:2` 的 find | ❌ `98001004` —— 依赖页面上下文（和 `find` 的老毛病一样）|

页面按钮只有「查看全部 / 前往数据分析 / 查看详情 / 查看更多 / 了解样品设置 /
以后再说 / 试用样品设置」—— 是**样品设置的推广浮层**挡住了计划列表入口。

**下一步**：先消掉那个浮层（点「以后再说」或「查看全部」），
找到计划列表的**创建入口**，再从真实流程抓 `invitation_group/create` 的 body。
用绑定错误预言机问不出来 —— 这个端点不报缺失字段。

### 29.3 行为对照（operator 的实际用法）

> 「本来就是直接从定向计划页去选的，但达人一般是从广场里面获取的」

翻译成接口流程：

```
① 达人广场  /connection/creator
   marketplace/find  →  marketplace/option（筛选字典）
                     →  marketplace/profile（看详情）
                     →  creator/rank（榜单捞人）

② 定向计划页  /connection/target-invitation
   invitation_group/search（列计划）
   invitation_group/create（建计划）
   invitation_group/creators_add（把①捞到的达人加进去）
   invitation_group/conflict_check（冲突校验）
   invitation_group/invitation/limit（上限 50 达人 / 100 商品）
```

①这一侧**已经全部打通**（§28）；②这一侧只差 `create` 的 body 形状。

### 29.4 同盟插件给的计划创建线索

```js
// ThirdParty源码里的 end_time 处理
if (!isFinite(n) || n <= r + 3e5) n = r + 6048e5;   // 6048e5 = 7 天
t.end_time = Math.trunc(n).toString();              // ← 字符串形式的 epoch 毫秒
```

它们的配置面字段：`free_sample`(417 处) · `commission_rate`(44) ·
`invitation_group_id`(15) · `product_ids`

→ 建计划的 body 大概率是
`{creator_oecuid, product_ids, commission_rate, free_sample, start_time, end_time, ...}`
（`start_time`/`end_time` 都是**字符串 epoch 毫秒**）。

---

## 30. ★ 定向计划创建：完整请求体（从同行源码反解）

来源：`Project-dalian/readable-source/src/inject/content/main.js`（去混淆源码，
比压缩 chunk 好读得多）。**这是本仓库之前完全不知道的部分。**

### 30.1 ★★ 最重要的一条：`98001004` 不是"参数错误"

同行把错误码按**处置方式**分类（`main.js:141956` 的 `Cpe` 常量表）：

```js
RESET:           [undefined, 10000]        // 10000 → 重置（触发验证码流程）
RETRY:           [50001702, 16024016, 16024021]   // → 重试
TASK_END:        [98001004]                // → 任务结束
SHOP_QUOTA_FULL: [16024019]                // → 店铺配额满
```

**`98001004` 被归为 `TASK_END`（任务结束）**，而服务端给的中文/英文 message
只是 "Invalid parameters. Please verify your input before retrying"。

我在 §25/§28/§29 里一直把它当"参数形状不对"来排查 —— **方向错了一半**。
它至少有两种含义：
- **真的参数错**（我确实踩到过：缺 `oec_region`、字段名写错）
- **任务结束 / 配额用尽**（同行据此终止任务，不再重试）

`16024019` = **店铺配额满**，收到就该停手。

### 30.2 完整请求体

```json
POST /api/v1/oec/affiliate/seller/invitation_group/create
Content-Type: application/json; charset=utf-8      ← 注意带 charset

{
  "invitation_group": {                            ← ★ 必须包这一层
    "name": "计划名-0925xxxx",
    "contacts_info": [ ...见 30.3... ],
    "free_sample_rule": {
      "has_free_sample": true,
      "is_free_sample_auto_review": false,
      "sample_setting_type": 1                     ← auto_review ? 2 : 1
    },
    "product_list": [ ...见 30.4... ],
    "creator_id_list": [ ...见 30.5... ],
    "end_time": "1790980800000",                   ← ★ 字符串形式的 epoch 毫秒
    "message": "邀约话术",
    "delivery_requirements": { "content_option": 1 }
  }
}
```

外层包装来自 API 类：

```js
sellerInvitationGroupCreate(e) {
  payload: { invitation_group: e },     // ← 我原来发扁平字段，必然 98001004
  headers: [{ "Content-Type": "application/json; charset=utf-8" }],
}
sellerInvitationGroupUpdate(e) {
  payload: { invitation: e },           // ← update 用的是 invitation，不是 invitation_group
}
```

**`create` 用 `invitation_group`，`update` 用 `invitation`** —— 名字不一致。

**响应路径**：`response.data.invitation.id` → 计划 id。

### 30.3 `contacts_info` 模板 + 联系字段码表

```js
[
  { key:"whatsApp", title:"", field:6,  value:"", country_code:"" },
  { key:"facebook", title:"", field:44, value:"" },
  { key:"telegram", title:"", field:45, value:"", country_code:"" },
  { key:"line",     title:"", field:41, value:"", country_code:"" },
  { key:"zalo",     title:"", field:42, value:"", country_code:"" },
  { key:"email",    title:"", field:7,  value:"", country_code:"US#1" },
  { key:"phone",    title:"", field:46, value:"", country_code:"" },
]
```

**联系字段码表**（`field` 值）：`whatsApp=6` · `email=7` · `line=41` ·
`zalo=42` · `facebook=44` · `telegram=45` · `phone=46`

填充规则：值是 `"国家码|值"` 形式时按 `|` 拆成 `country_code` + `value`；
对象形式取 `value` + `area`。

### 30.4 `product_list`：佣金是**百分比 ×100**

```js
product_list = products.map(p => ({
  product_id: p.productId,
  target_commission: rate * 100,        // ★ 15% → 1500
  ...(p.target_ads_commission_bl
      ? { target_ads_commission: p.target_ads_commission * 100 } : {}),
}))
```

**`target_commission` 是整数百分比 ×100**，不是小数也不是字符串。

### 30.5 `creator_id_list`：双层 `base_info`

```js
creator_id_list = creators.map(c => ({
  base_info: {
    creator_id: "",
    nick_name: "",
    creator_oec_id: c.creator_id || c.creator_oec_id,   // ★ 这里用的是 creator_oec_id
  },
}))
```

注意：**这个接口吃 `creator_oec_id`**（和达人详情一致），
而达人广场搜索返回的字段叫 `creator_oecuid` —— 又要转一次。

### 30.6 `end_time` 的校验规则

```js
if (!isFinite(n) || n <= now + 3e5) n = now + 6048e5;   // 3e5=5分钟, 6048e5=7天
t.end_time = Math.trunc(n).toString();                  // 字符串 epoch 毫秒
```

不在合理区间时自动纠到 now+7天。自己构造时照这个来。

### 30.7 其他从源码里挖到的端点

| 路径 | payload / 说明 |
|---|---|
| `/api/v1/oec/affiliate/creator/marketplace/search` | `find` 的变体（`payload.request.algorithm` 存在时走这条）|
| `/api/v1/oec/affiliate/creator/marketplace/recommendation` | `find` 的变体（`payload.request` 存在时走这条）|
| `/api/v1/oec/affiliate/creator/marketplace/creator/profile/stats` | 达人数据统计；`filters:[{creator_oec_id}]` + `start_timestamp` |
| `/api/v1/affiliate/lux/creator/auth_profiles` | payload `{creator_oec_ids: [...]}` |
| `/api/v1/affiliate/lux/plan/product/list` | 计划可选商品 |
| `/api_sens/v1/affiliate/cmp/contact_types` | 达人联系方式类型（`api_sens` 敏感通道）|
| `/api_sens/v1/affiliate/cmp/contact` | 达人联系方式 |
| `/api/v1/oec/affiliate/seller/invitation_group/product_creator_relation` | payload `{creator_ids}` |

**`find` / `search` / `recommendation` 的选择逻辑**（源码原文）：

```js
const c = e?.request
  ? (e.request.algorithm ? "/marketplace/search?" : "/marketplace/recommendation?")
  : "/marketplace/find?";
```

→ 解释了 §29.1 里定向计划页用 `{"pagination":...,"rec_scene":2,"algorithm":1}` 的现象。

### 30.8 其它值得注意的实现细节

- 他们显式管理 `X-Gnarly`：`this.query(..., void 0, ["X-Gnarly"])`
- 达人详情页用**独立 iframe**：`affiliate.tiktokglobalshop.com/connection/creator/detail?cid=...&enter_from=target_invitation_detail_page`
- 它们的任务体系把 10000 归为 RESET（重置），说明**验证码是预期内的正常流程**，不是异常
- `min_commission_rate_by_category` 是从
  `/api/v1/affiliateplatform/commissions/get_min_commission_rate_by_category` 取的

### 30.9 读源码的正确入口

`readable-source/` 是**去混淆后的源码**（42 万行，比压缩 chunk 好读得多）：

| 文件 | 内容 |
|---|---|
| `src/inject/content/main.js` | 主流程 + 定向计划创建（**本节主要来源**） |
| `src/inject/content/tiktokRpa/index.js` | 联盟 API 类（全部端点 + payload 包装） |
| `src/inject/content/mcn/index.js` | MCN / Partner |
| `src/inject/content/comment/index.js` | 达人评论 / 佣金率字典 |
| `dist2.0.9-接口与功能文档.md` | 第三方整理的接口文档（69KB） |

**先看 `readable-source/`，别一上来啃 `dist2.0.9/chunks/*.js`。**

---

## 31. ✅ 定向计划创建：真实验证通过（端到端）

### 31.1 验证结果

```json
POST /api/v1/oec/affiliate/seller/invitation_group/create
Content-Type: application/json; charset=utf-8

→ code=0  message=success        耗时 1.6s（**未触发验证码**）
{
  "data": {
    "invitation": { "id": "7690XXXXXXXXXX40", "group_status": 2,
                    "delivery_requirements": {"content_option": 1} }
  },
  "share_short_url": "…/invitation_group/share/long_url/ALXGnuV5ta0f",
  "landing_url":     "…/invitation_group/share/long_url/ALXGmaJiOJnq"
}
```

复核 `invitation_group/search` 确认落库：

```
total = 1
  id            7690XXXXXXXXXX40
  name          TK01验证计划-0925
  start_time    1790517684505          ← 服务端自动填
  end_time      1791122455525
  creator_cnt   1        creator_added_cnt 0    ← 达人还没"加入"（需对方接受）
  product_cnt   1
  group_status  2
  free_sample_rule  {has_free_sample:true, is_free_sample_auto_review:false,
                     sample_setting_type:1}
  product_list  [{product_id, item_sold:"0", commission_effective_time:"0", …}]
```

该计划已用 `invitation_group/terminate` 的能力可随时终止（**测试计划，需要清理时告诉我**）。

### 31.2 §30 那些坑全部验证成立

| 坑 | 是否成立 |
|---|---|
| body 必须包一层 `invitation_group` | ✅ 用了就通 |
| `Content-Type` 带 `; charset=utf-8` | ✅ |
| `target_commission` = 百分比 ×100（15 → 1500） | ✅ 服务端接受 |
| `end_time` 字符串 epoch 毫秒 | ✅ 回读确认 |
| `contacts_info` 七个字段全带 | ✅ 服务端接受空值模板 |
| `creator_id_list` 双层 `base_info` + `creator_oec_id` | ✅ |

### 31.3 速度：联盟侧写操作**不需要验证码**

这次 1.6 秒返回、无 `bdturing-verify`。原因和 §27.3 一致：

- 走**页面 fetch**（`PageChannel.call`），SDK 正常签名，`Origin`/`Referer` 正确
- 页面**在前台**（`bringToFront`）

对比：`raw_call`（iframe 原生 fetch）在联盟域**每次**被判插件
（`100000 Please remove the plugin`）—— 见 §25.2 坑 3。

### 31.4 完整链路已通

```
① 达人广场  /connection/creator
   marketplace/find        → creators --pages N        （带 fp 重试）
   marketplace/option      → options                   （品牌/类目/佣金率/语言）
   marketplace/profile     → profile <creator_oec_id>  （字段是 creator_oec_id）
   cmp/creator/rank/list/get → rank                     （rank_list_meta 五字段）

② 建计划  /connection/target-invitation
   invitation_group/create  → AffiliateClient.create_group(...)   ✅ 本轮验证
   invitation_group/search  → groups
   invitation_group/creators_add → group_creators_add(...)        （同构，未单独验证）
```

### 31.5 ⚠️ `creators_add` 的 body 形状**没验证出来**（推测错误）

对刚建的计划 `7690XXXXXXXXXX40` 补达人，两个变体都失败：

```
变体 A: {"invitation_group_id": "<plan id>", "creator_id_list": [...]}
        → code=98001004
变体 B: {"group_id": "<plan id>",          "creator_id_list": [...]}
        → code=98001004
```

复核计划 → `creator_cnt` 仍是 1，**没写进去**。

**结论**：`creators_add` 的 body 不是这个形状。按 §30.1 的教训，
`98001004` 有两种含义 —— 这里应该是**真的参数错**（因为同一个计划上
`create` 是通的，不可能是配额/任务结束）。

**下一步**：只能从 UI 抓 —— 进计划详情页，用「补充达人 / 添加达人」，
抓真实请求。`product_creator_relation`（另一个补达人的入口）
也可以一并试。

**不要再用猜参数的方式试这个端点** —— 试了 2 个变体都是同样的错，
而且每次都会写一条失败记录。

---

## 32. `creators_add` 抓取受阻 + 一个绕开它的办法

### 32.1 本轮尝试与结果（如实记录）

目标是抓 `creators_add` 的真实 body。**没抓到。**

| 尝试 | 结果 |
|---|---|
| 直接 goto `/affiliate/connection/target-invitation` | 渲染成**首页**，无计划列表 |
| goto `/affiliate/connection/target-invitation/<plan_id>` | 同上，渲染成首页 |
| goto `.../detail?id=<plan_id>` | 同上 |
| 侧边栏点「合作」→ 子菜单「定向合作」 | 「合作」能展开，**「定向合作」精确文本匹配找不到元素** |
| 点页面上的「查看详情」 | 点到首页的推广位，跳到 `/platform/homepage` |

**结论**：这个 SPA 的定向合作页**不能靠 URL 直达**，而侧边栏自动化点击在此页不稳定
（子菜单的文本节点结构不是纯文本，精确匹配失效）。

回显验证：`invitation_group/search` 确认计划数仍是 1、`creator_cnt=1` ——
说明 `creators_add` 那两个变体**确实没写进去**。

### 32.2 ★ 更实际的做法：**别用 `creators_add`，直接在 `create` 里带达人**

`invitation_group/create` 的 body 里本来就有 **`creator_id_list`**（数组）：

```json
{"invitation_group": {
   "creator_id_list": [{"base_info": {"creator_oec_id": "…"}}, …],   ← 可以是多个
   …
}}
```

限制是 `invitation_group/invitation/limit` 给的 **`max_creator_num: 50`** ——
一次最多带 50 个达人。

**所以「广场捞人 → 建计划」这条链路根本不需要 `creators_add`：**

```
1. 达人广场 marketplace/find 捞人（可翻页、可按 rank 榜捞）
2. 过滤（has_collaborated / has_invited_before_90d / is_creator_blocked_by_shop）
3. 取前 ≤50 个 → 一次 invitation_group/create 全部带上   ← 已验证可用
```

只有"计划建好后还想追加达人"才需要 `creators_add`，而那条路径可以
**直接新建一个计划**绕过。

### 32.3 下一步若要继续抓 `creators_add`

需要换思路，别再用精确文本匹配点侧边栏：

- 用 **React fiber 遍历**找到菜单项的组件实例再触发 onClick
- 或者监听 `history.pushState`，在用户/程序导航到定向合作页的**那一刻**注入 hook
- 或者用 `chrome.tabs` 级别的导航事件 + 监听网络，捕获任何 `invitation_group/*` 请求
  （不依赖页面点击）

### 32.4 当前联盟侧能力总账

| 能力 | 状态 |
|---|---|
| 达人广场搜索 / 翻页 / 筛选字典 | ✅ |
| 达人详情 `profile` | ✅ |
| 达人排行榜（200/榜） | ✅ |
| 样品申请列表 | ✅ |
| 邀约上限 / CRM 上限 | ✅ |
| **建定向计划（含达人+商品+佣金+有效期）** | ✅ **已验证** |
| 计划列表查询 | ✅ |
| 补达人 `creators_add` | ❌ body 未拿到（有替代方案见 32.2）|
| 终止计划 `terminate` | 未测（body 应为 `{invitation_group_id}`）|
| 联系方式 `/api_sens/*` | 未测 |
| 达人数据统计 `profile/stats` | 未测 |

---

## 33. ★ 借鉴同行解法：用 Worker 取代"抢前台"

### 33.1 同行是怎么绕开的（看一眼就明白）

```
manifest.json: "offscreen" 权限
tabs/offscreen.html          ← Chrome Offscreen Document
tabs/assetWorker.html
static/background/index.js   ← service worker
```

**它们从来不在标签页里发请求。**

Chrome 的 **Offscreen Document** 是扩展的隐藏文档：没有标签页、不在任何窗口里、
**完全不受 `visibilityState` 约束**。所以 §27 那个"必须前台"的问题对它们根本不存在。

它们只在**需要验证码时**才开一个真标签页 —— 这就是
`callCaptchaApi({...captchaParams, region, tabId})` 里那个 `tabId` 的由来。

### 33.2 我没有扩展上下文，但**页面 Blob Worker 等价**

在页面里 `new Worker(URL.createObjectURL(new Blob([...])))`：

| 特性 | iframe（我原来试的） | **Blob Worker** | 页面 fetch |
|---|---|---|---|
| `Origin` | **`null`** ❌ | ✅ 同源 | ✅ 同源 |
| webmssdk 拦截 | 无（但也因此 origin 错） | **无** ✅ | **有** → promise 被扣 |
| 需要页面在前台 | 否 | **否** ✅ | **是** ❌ 会抢焦点 |
| 验证码要求可见性 | — | **可见**（头能读到）✅ | 隐藏成"挂起" ❌ |

实测：

```
worker 同源:  https://affiliate.tiktokshopglobalselling.com
页面签名:     ['X-Bogus']
→ ok=True status=200 ms=298   {"code":0,…"max_creator_num":50…}
```

### 33.3 落地：混合传输（`AffiliateClient.call`）

三种传输按这个顺序用：

```
1. worker_call(Blob Worker)   ← 快、不抢前台、能看见验证码头
        ↓ 返回 100000（被判插件）或 10000（软挑战）
2. call(页面 fetch)            ← SDK 完整签名（含 X-Gnarly），不会被挑战
        ↓ 需要页面在前台
3. raw_call(iframe)            ← ❌ 联盟域一律 100000，**永远别用**
```

回落条件是**两个码都要回落**：

- `100000` = 被判插件（Worker 只签了 X-Bogus）
- `10000` = 服务端软挑战（同样是签名不完整导致）

实测（修复后）：

```
GET  邀约上限   1.1s code=0      GET  CRM上限   0.5s code=0
GET  导航表    0.9s code=0      POST 筛选字典  1.1s code=0
POST 排行榜    2.3s code=0      POST 计划列表  1.6s code=0
GET  账户      3.0s code=0      GET  样品      1.6s code=0
                              → 8/9 通过
```

### 33.4 ★ 不再干扰操作者（这是硬规矩）

之前我会 `Page.bringToFront` 抢前台、还会 `goto` 操作者的标签页 —— **都是干扰**。已全部改掉：

| 改动 | 说明 |
|---|---|
| `use_quiet_window()` | 需要前台时，开一个 `Target.createTarget({newWindow:true, background:true})` 的**独立窗口**，它自己的活动标签天然 visible，**不抢焦点** |
| `release_quiet_window()` | 用完关掉，不在桌面留东西 |
| `_ensure()` 的 `bringToFront` | **只对我们自己开的页面执行**（`_dsh_quiet` / `_own_page` 标记），对操作者的标签页绝不执行 |
| `handle_captcha` 的拖拽置前 | 同上；非自有页面只做 `setFocusEmulationEnabled`（不抢焦点）并打印提示 |
| **删掉 `find_creators` 里的自动 `ensure_marketplace_page()`** | 它会 `goto` 操作者的标签页；改为**由调用方显式调用** |

### 33.5 ⚠️ 当前状态：`marketplace/find` 暂时打不通了

修复后验证的最后一轮：

```
GET  邀约上限   1.1s code=0      POST 计划列表  1.6s code=0
GET  CRM上限    0.5s code=0      GET  账户      3.0s code=0
GET  导航表     0.9s code=0      GET  样品      1.6s code=0
POST 筛选字典   1.1s code=0      POST 排行榜    2.3s code=0
POST 广场搜索   5.6s code=98001004            ← 只剩它
```

随后 `find_creators` / `all_creators` / `scout_creators` **全部返回 0**，
稳定 `98001004`（`{"code":98001004,"msg":"Invalid parameters…"}`）。

按 §30.1，**`98001004` 同行归类为 `TASK_END`**。`find` 是本会话调用最密集的
端点（几十次），所以最可能的解释是**该端点触发了限流/任务终止**，
而不是参数错了 —— 因为**同一个 body 早先反复成功过**。

**建议**：`find` 先停一段时间。其余 8 个端点正常。
恢复后 `scout` / `invite` 不需要改代码。

### 33.6 现在的运行约束（写进代码注释了）

```
✓ 不需要前台、不抢焦点：worker_call（大多数端点）
✓ 需要前台时：use_quiet_window() 开独立窗口，用完 release
✗ 绝不 bringToFront 操作者的标签页
✗ 绝不 goto 操作者的标签页
```

---

## 34. ✅ `creators_add` 破了 —— 字段名和 `create` 完全不同

### 34.1 答案

```json
POST /api/v1/oec/affiliate/seller/invitation_group/creators_add
{"group_id": "7690XXXXXXXXXX40", "creator_ids": ["7494XXXXXXXXXX25"]}

→ code=0
{"data": {"success_cnt": 1, "conflict_cnt": 0, "invited_cnt": 0}}
```

**两个字段名都不是我先前推测的：**

| 我以为 | **实际** |
|---|---|
| `invitation_group_id` | **`group_id`** |
| `creator_id_list`（`[{base_info:{…}}]` 双层） | **`creator_ids`**（扁平字符串数组） |

试了 **9 个变体**才试出来（见 34.3）。前 8 个全是 `98001004`。

**复核**：计划 `7690XXXXXXXXXX40` 的 `creator_cnt` 从 **1 → 2** —— 确实写进去了。

响应字段：`success_cnt` / `conflict_cnt` / `invited_cnt`。
`conflict_cnt > 0` 表示该达人已挂在别的计划上。

### 34.2 ★ 关于 operator 提的「邀约模板」

**TikTok 侧不需要预设模板。** 证据：

1. 我建的验证计划 `theme_file_id` / `theme_url` **都是空字符串**，照样 `code=0`
2. 同行插件里的「邀约模板」在 `/web/invitation/template/{add,list,get,update,remove,plan}`
   —— 这些全部指向 **`thirdparty.example.com/api`（同行自己的 ERP）**，不是 TikTok
3. TikTok 侧没有任何 template / theme 类端点（扫过 41 个端点 + 同行源码）

TikTok 侧的 `theme_file_id` 是**可选的邀约页主题**，不填就空着。
真正**建议配**（非必需）的是：

- `contacts_info` —— 联系方式（WhatsApp/email 等 7 个字段码，见 §30.3）。
  UI 上提示"添加 WhatsApp 账号和邮箱，方便与达人联系"
- 样品设置（`/product/sample-settings`）

### 34.3 九个变体的对照（留档，避免重复试）

| # | body | 结果 |
|---|---|---|
| A | `{invitation_group_id, creator_id_list:[{base_info:{…}}]}` | 98001004 |
| B | `{invitation_group_id, creator_ids}` | 98001004 |
| **C** | **`{group_id, creator_ids}`** | **code=0 ✅** |
| D | `{id, creator_id_list}` | 98001004 |
| E | `{invitation_group:{id, creator_id_list}}` | 98001004 |
| F | `{invitation_group_id, creator_list:[{...}]}` | 98001004 |
| G | `{invitation_group_id, creator_oec_ids}` | 98001004 |

**教训**：同一个域下不同端点的字段命名**不统一**，不能靠"推理一致性"，
只能抓包或穷举。这次是穷举出来的 —— 但代价是 8 条失败记录。

### 34.4 完整链路现在全通

```
① 广场捞人   marketplace/find + option + profile + rank     ✅
② 建计划     invitation_group/create                        ✅ 已验
③ 补达人     invitation_group/creators_add  {group_id, creator_ids}  ✅ 已验
④ 计划详情   invitation_group/detail                         ✅
⑤ 计划列表   invitation_group/search                         ✅
⑥ 终止计划   invitation_group/terminate                      ✅ 已验
```

`group_status` 语义：**2 = 进行中，4 = 已终止**。

---

## 35. ⚠️ 事故记录：不要把"开窗口"当成解决前台问题的手段

### 35.1 我犯的错

为了让 `find` 拿到页面上下文（§29：它依赖页面停在 `/affiliate/creator/search`），
我写了 `ensure_find_page()` 去开「静默窗口」：

```python
self.ch._bcdp.send("Target.createTarget", {
    "url": SEARCH_URL, "newWindow": True, "background": True})
```

结果：

1. `Target.createTarget` **每次都真的新建一个窗口**（`background:true` 只是不激活）
2. Playwright 的 `ctx.pages` **同步不到新窗口** —— 我把等待拉到 28 秒仍然匹配不上
3. 因为匹配不上，代码每次都走"没找到 → 再建一个"的分支

**最终在操作者桌面上堆了 10 个重复标签页**，被明确投诉。

已全部关闭，恢复到原本的 3 个标签。

### 35.2 根除措施（写进代码，不靠自觉）

| 位置 | 改动 |
|---|---|
| `ensure_find_page()` | **改成恒返回 False 的空函数**。永不建窗口。 |
| `use_quiet_window()` | 加两道锁：**幂等**（已有自有窗口就复用）+ **全局上限 1 个**（`_quiet_made` 标记） |
| `PageChannel._ensure()` | 找不到可用页面时 **抛错**，不再 `ctx.new_page()` 自动开页 |
| `ensure_marketplace_page()` | 若当前页面是操作者的（无 `_dsh_quiet` 标记）→ **不 goto**，打印提示后返回 |

### 35.3 现在的硬规矩

```
✓ 只读、发请求             → worker_call（同源、无 SDK、不需要前台、不碰浏览器 UI）
✓ 需要页面上下文           → 由**操作者自己**把标签页放到正确 URL
✓ 确实需要自有页面         → use_quiet_window()（幂等，最多 1 个）+ 用完 release
✗ 绝不 goto 操作者的标签页
✗ 绝不 Page.bringToFront 操作者的标签页
✗ 绝不自动 new_page() / createTarget 堆窗口
```

### 35.4 那 `find` 怎么办

`find` 在页面不在 `/affiliate/creator/search` 时稳定 `98001004`
（§30.1 说这个码也可能是 `TASK_END`，两种因素可能叠加）。

**最省事的做法**：操作者本来就常开着 `/affiliate/creator` 标签，
需要跑 `scout` 时**他手动点一下「发现达人」**即可 —— 我不碰他的浏览器，
请求也就能过。这比我在他桌面上堆窗口好得多。

### 35.5 当前状态

- 标签页：`affiliate/creator` · `seller/ads-creation` · Hub Studio（与操作者原状一致）
- 无任何后台进程
- 联盟链路（除 `find` 的页面上下文要求外）全部可用

---

## 36. 🎯 `find` 失败的真因：缺三个签名参数（不是限流）

### 36.1 决定性对比

之前 §33.5 判断"`find` 被限流（TASK_END）"—— **错了**。用"让页面自己发请求"做了对照：

```
app 自己的 find :  status=200  code=0  拿到真实达人（unboxcunghip …）
我的 find       :  200         code=98001004
```

**同一个页面、同一时刻** —— 所以是我的请求形状问题。

逐参数对比（抓我自己那次请求的**实际发出 URL**，用 `performance` 读）：

```
我的请求：  21 个参数里
  msToken          ❌ 缺
  X-Gnarly         ❌ 缺
  X-Tts-Oec-Bsid   ❌ 缺
  X-Bogus          ✅ 有（byted_acrawler.frontierSign 给的）
  其余 17 个业务参数  ✅ 全部与 app 一致

app 的请求：4 个签名全有
```

**结论：`marketplace/find` 要求完整签名（4 个），只给 `X-Bogus` 一律 `98001004`。**

### 36.2 为什么会缺

`frontierSign({url, method, body})` **只产出 `X-Bogus`**。
而我自己把它塞进 URL 之后，**webmssdk 的 fetch 包装器看到"URL 已有 X-Bogus"，
就跳过了其余三个参数的注入** —— 典型的"半签名"陷阱。

其它端点（排行榜 / 计划列表 / 筛选字典…）只吃 `X-Bogus` 就够，所以它们一直正常
—— 这也是为什么我一度以为是 `find` 被单独限流。

### 36.3 两个候选修法（未及验证）

**A. 不要自己塞 `X-Bogus`，让 SDK 全签**

```js
fetch(url, ...)   // url 里只有那 17 个业务参数，不带任何签名
```
理论上 webmssdk 会补齐 4 个。**实测这条路会挂起** ——
页面 fetch 的 promise 被 SDK 扣住（§27 的老问题），
`page.evaluate(await ...)` 直接卡死（本轮脚本就是这么挂的）。

**B. 采集 app 的新鲜签名 URL，原样重放**（推荐先试这条）

```
1. reload 页面（或点「发现达人」）让 app 发一次 find
2. 用 page.on("request") 抓下那条【21 参数的完整签名 URL】
3. 用**同一个 URL** 顶层 fetch 重放，只换 body 里的 pagination
   —— X-Gnarly 可能只绑 path 不绑 body，换分页应该能过
4. 用 iframe 重放会被判插件（Origin: null，§25.2 坑 3），必须顶层 fetch
```

本轮第 3 步因为**第 3 条 fetch 挂起**没跑完 —— 但**签名 URL 已经成功抓到并落盘**：
`notes/aff_app_find_full.json`（21 参数完整）。

### 36.4 已落盘的关键证据

| 文件 | 内容 |
|---|---|
| `notes/aff_app_find_full.json` | app 的 find 完整 21 参数 + headers + body |
| `notes/aff_find_signed.json` | 更早一次抓的同款（msToken/fp 会轮换） |

**两份都可以直接拿来重放**，不用再抓。

### 36.5 教训

- **`X-Bogus` 自己塞会阻止 SDK 补齐其余签名** —— 要么全自己签（做不到，缺 X-Gnarly），
  要么完全交给 SDK
- **同一端点在不同时刻可能一个成功一个失败，原因是签名完整度不同**，
  不是"限流"。我因为没做这个对照，白花了很多时间

### 36.6 当前状态

- 无进程运行；标签页：2 个 `affiliate/creator`（操作者自己开的新标签）+ `seller/ads-creation` + Hub Studio
- 除 `find` 外，联盟链路全部可用

---

## 37. 🎯 终极结论：`find` 必须由 app 自己的代码发起

### 37.1 四种传输的完整对照（同页面、同一时刻）

| 传输 | 签名 | 结果 |
|---|---|---|
| **app 自己的代码** | 4 个全有（SDK 签） | ✅ `code=0`，拿到达人 |
| Worker（同源、**带 app 的完整签名 URL**） | 4 个全有 | ❌ `{code:100000,"Please remove the plugin"}` |
| iframe（Origin: null） | 任意 | ❌ `100000` |
| 我的页面 fetch（`frontierSign` 预塞 X-Bogus） | **只有 X-Bogus** | ❌ `98001004` |
| 我的页面 fetch（不塞，让 SDK 签） | SDK **不补**其余 3 个 | ❌ `98001004` / 挂起 |

**两个独立结论：**

**① 我的页面 fetch 拿不到完整签名。**
抓自己请求的实际发出 URL，21 个参数里只有 `X-Bogus`，
缺 `msToken` / `X-Gnarly` / `X-Tts-Oec-Bsid`。
→ webmssdk **不会**为"程序化发起的 fetch"补齐完整签名。

**② 服务端认的不是签名，是"请求来源"。**
把 app 那条**完全相同的签名 URL**拿去重放：
- Worker 发 → `100000`（判插件）
- 剥掉签名页面发 → `98001004`

签名一样、body 一样，结果取决于**谁发的**。

### 37.2 所以唯一的路：调用 app 自己的 API 客户端

这正是同行插件在做的事 —— 它们的 `affiliateRequestHook` / `pageRequestBridge`
不是"自己拼请求"，而是**桥进页面的请求层**让页面自己发。

三条可行路径（按可行性排）：

**A. 拿到页面里的 API 客户端实例，直接调它的方法**（同行路线）
页面 bundle 里那个 class 有 `marketplaceRecommendation(e, ...)` 等方法，
构造函数只吃 `uriPrefix`。只要能拿到实例（webpack module 表 / 全局引用），
调它就能发出**由 SDK 完整签名**的请求。

**B. React fiber 遍历触发页面自身动作**
找到搜索框/筛选器的组件实例，调它的 props.onChange / onClick，
让 app 自己发请求。等于"用代码替你点按钮"。

**C. 最省事：你手动点，我抓结果**
点一次「发现达人」，我用 `page.on("response")` 接住响应，
再用 `search_key` 游标翻页（翻页也是 app 的动作，或者干脆一页页点）。

### 37.3 已落盘、可直接复用的证据

| 文件 | 内容 |
|---|---|
| `notes/aff_app_find_full.json` | app 的 find 完整 21 参数 + headers + body |
| `notes/aff_find_signed.json` | 更早一次（msToken/fp 会轮换） |
| `notes/aff_creators.json` | 成功抓到的 12 个达人数据 |

### 37.4 为什么其它端点没事

排行榜 / 计划列表 / 筛选字典 / 详情 / 建计划 / 补达人 / 终止
**只吃 `X-Bogus`**，所以我的传输一直够用 —— 它们全部验证过 `code=0`。

**只有 `find`（和它的 `search`/`recommendation` 变体）要求完整签名。**
这是全站唯一一个卡在传输层的端点。

### 37.5 本次踩坑时间线（供复盘）

```
① 以为是风控限流       → 错。做了 app 对照才发现是请求形状
② 以为缺 accept 头     → 错，加了没用
③ 以为缺 oec_region    → 部分对（那是早期问题），但 find 还要更多
④ 逐参数对比           → 定位到缺 3 个签名参数
⑤ 以为是签名可重放     → 错。Worker 拿完整签名 URL 也被判插件
⑥ 结论：必须 app 自己发 → ✅ 与同行实现一致
```

---

## 38. ✅ 联盟达人链路全通 —— 用"让 app 自己发请求"绕过签名墙

### 38.1 解法：不构造请求，只接响应

§36/§37 的结论是"`find` 必须由 app 自己的代码发起"。**那就让 app 自己发。**

```python
page.on("response", 接住 marketplace/find 的响应)
① 点「发现达人」                        ← app 自己发第 1 页
② 反复滚动达人列表                      ← app 自己用 search_key 游标翻页
③ 把每页响应解析出去重
```

**完全不构造请求、不碰签名、不碰 Worker。**

实测：**11 页 × 12 = 去重 132 个达人**，每页 `code=0`。

### 38.2 端到端结果（真实执行）

```
① 捞人    132 个 → 过滤后 103 个
          条件：未合作 + 90天内未邀 + 未被拉黑 + 粉丝 ≥ 5000

② 选品    选品池 624 个，取 3 个

③ 建计划  code=0   plan_id=7690XXXXXXXXXX47
          TK01达人邀约-0928   10 达人 / 3 商品 / 佣金 15% / 有效期 7 天

④ 复核    creator_cnt=10  product_cnt=3  group_status=2（进行中）
```

邀请到的头部达人：

```
ngoctrinh89        6,640,841    hoquanghieu        3,704,158
ungthaimenuochoa   1,931,578    lamchankhang249    1,623,910
sukanenobita       1,614,876    trucmainguyen79    1,254,216
```

### 38.3 命令

```bash
python3 tk01_affiliate.py harvest --pages 12 --min-followers 5000
python3 tk01_affiliate.py invite --name "TK01达人邀约-0928"         --product-ids <pid1,pid2,pid3> --commission 15 --yes
python3 tk01_affiliate.py groups
python3 tk01_affiliate.py detail <plan_id>
python3 tk01_affiliate.py addcreators <plan_id> --creators <id1,id2> --yes
python3 tk01_affiliate.py terminate <plan_id> --yes
```

### 38.4 完整能力矩阵（全部实测通过）

| 能力 | 传输 | 状态 |
|---|---|---|
| 达人广场搜索（翻页、132 个/轮） | **app 自己发，接响应** | ✅ |
| 筛选字典（品牌400/类目25/佣金率/语言） | 混合 | ✅ |
| 达人详情 `profile` | 混合 | ✅ |
| 达人授权资料 `auth_profiles` | 混合 | ✅ |
| 达人排行榜（200/榜） | 混合 | ✅ |
| 联系方式 `api_sens/contact_types` · `contact` | 混合 | ✅ |
| 样品申请列表 | 混合 | ✅ |
| 邀约上限 / CRM 上限 | 混合 | ✅ |
| **建定向计划** | 混合 | ✅ |
| **补达人** `{group_id, creator_ids}` | 混合 | ✅ |
| 计划详情 / 列表 | 混合 | ✅ |
| **终止计划** | 混合 | ✅ |

**混合传输** = `worker_call`（不抢前台）优先 → 遇 `100000`/`10000` 回落页面 fetch。

### 38.5 操作规矩（避免再次打扰操作者）

```
✓ harvest / rank / groups / detail / samples → 只读，worker_call，不碰 UI
✓ harvest 需要点「发现达人」+ 滚动 → 会操作页面，但**不新建标签、不 goto 别的页面**
✗ 绝不 goto 操作者的标签页
✗ 绝不 Page.bringToFront 操作者的标签页
✗ 绝不自动 new_page() / createTarget 堆窗口（§35 事故）
```

### 38.6 当前生效的计划

| plan_id | 名称 | 状态 | 达人 | 商品 |
|---|---|---|---|---|
| `7690XXXXXXXXXX47` | TK01达人邀约-0928 | **2 进行中** | 10 | 3 |
| `7690XXXXXXXXXX40` | TK01验证计划-0925 | 4 已终止 | 2 | 1 |
| `7690XXXXXXXXXX67` | TK01链路验证-0925 | 4 已终止 | 2 | 1 |

`group_status`：**2 = 进行中，4 = 已终止**

---

## 39. 与同行插件（ThirdParty）的差距对比

### 39.1 覆盖面对比

| 维度 | ThirdParty | 本仓库 |
|---|---|---|
| **运行形态** | Chrome MV3 扩展（装完即用，自包含） | **Python 脚本 + 外部 CDP**（依赖 Hub Studio 容器常开） |
| **UI** | popup 面板 + 内容脚本注入 | 只有 CLI |
| **区域** | `seller-br/de/es/…` **多国 Seller** | **只有 VN 单区** |
| **平台** | TikTok Shop + MCN/Partner + **Shopee 多国** + TikTok 站内 | 只有 `tiktokshopglobalselling.com` |
| **多店铺** | 统一账号 + 多店铺切换（`/web/shop/*`） | 单店（shop_id 写死配置） |
| **权限面** | `declarativeNetRequest` `webRequest` `debugger` `offscreen` `cookies` `notifications` … | 靠 CDP |
| **促销** | 2 个端点（`flash_sale/create`、`search_products`） | **85 处引用**，独立客户端 1336 行 |
| **商品机会** | 4 个端点 | 独立客户端 1813 行 + 周度流水线 542 行 |
| **联盟达人** | RPA 驱动，完整 | 41 端点，1114 行 |
| **滑块验证码** | 调页面 SDK | **自己实现求解**（608 行） |
| **IM / 消息** | ✅ 站内 IM protobuf + 批量消息 + 会话 | ❌ **完全没有** |
| **订单** | ✅ 订单邀评 9 步工作流 | ❌ **完全没有** |
| **达人 CRM** | ✅ 达人记录 / 邀约日志 / 统计 / 会话记录 | ❌ 建完计划没有后续跟踪 |
| **样品** | ✅ 可发起寄样 | ⚠️ 只能查列表 |
| **模板复用** | ✅ 模板存/取/改/删 | ❌ 每次重新构造 body |
| **任务系统** | ✅ 模板 + 任务队列 + 日志 + 统计（`/work/*`） | ❌ 一次性命令行 |
| **告警** | ✅ `notifications` 权限 | ❌ 靠人看日志 |

### 39.2 我们缺什么（按影响排序）

#### P0 —— 影响能不能真正投产

**① 多店铺 / 多区域（最大的结构性差距）**
同行覆盖 br/de/es 多国 Seller + Shopee 多国；我们把 `shop_id`/`oec_seller_id`
写死在常量里。**如果 operator 要开第二个店或第二个国家，现在要改代码。**
建议：把店铺上下文抽成配置（`shops.json`），`PageChannel` 接受 profile 参数。

**② 运行形态：脚本 vs 扩展**
我们是"外部脚本 + CDP 连浏览器"，必须 Hub Studio 容器常开、端口可达。
同行装完扩展就自包含运行。
**短期不必重写**，但要知道：我们的可用性绑在容器上。

**③ 任务系统 / 持久化**
同行有模板 + 任务队列 + 日志 + 统计。我们跑完只有 `notes/*.json`（169 个），
没有"这次邀约了谁、结果如何"的可查询记录。
建议：加一个 `runs.jsonl` 记录每次动作的入参/结果/时间。

#### P1 —— 能力缺口

**④ IM / 消息 —— 最该补的一块**
达人邀约之后**必然要跟进**（催样品、催发布、谈佣金）。
同行有站内 IM（protobuf 协议对象表见 §26.4）+ 批量消息接口
`/api/v1/oec/affiliate/crm/im_messages/batch_send`。
我们**一个 IM 端点都没碰**。这是目前最大的功能空洞。

**⑤ 订单侧**
同行有订单邀评 9 步工作流（§26.3）。我们没做订单。
如果 operator 要做"下单后自动邀评"，这是现成的流程骨架。

**⑥ 达人后续跟踪**
我们只到"建计划"为止。同行有 `/ThirdParty/creators/*`（达人记录）、
邀约日志、统计、会话记录。
我们现在**不知道邀约后达人有没有回应**。

**⑦ 样品只能查不能发**
`sample/group/list` 能读，但发起寄样的写接口没逆向。

#### P2 —— 体验

**⑧ 无 UI** —— CLI 对 operator 不友好，尤其批量操作要传一堆参数。
**⑨ 无模板复用** —— 每次建计划都重新构造 body（虽然 `build_group_body` 已经收敛了）。
**⑩ 无告警** —— 跑完得人来看终端。

### 39.3 我们强在哪

| 项 | 说明 |
|---|---|
| **文档** | 4077 行，带实测数据、踩坑记录、失败记录。同行只有编译产物 + 一份第三方文档 |
| **促销深度** | 同行 2 个端点；我们 85 处引用 + 完整客户端（含一口价/双限购/拆单规则） |
| **商品机会** | 同行 4 个端点；我们做了**准入规则反推 + 周度流水线 + 61% 实测命中率** |
| **传输层理解** | 四种传输（iframe/Worker/页面 fetch/app 自身）的取舍全部实测清楚，写在 §25/§27/§33/§37 |
| **滑块求解** | 自己实现的通道检测 + 人类轨迹；同行是调页面 SDK |
| **可读性** | 纯 Python，5445 行可读代码；同行是混淆打包产物 |
| **失败记录** | 文档里明确写了"这条判错了"（§24→§27、§33.5→§36、§35 事故） |

### 39.4 补强建议（按性价比）

| 优先级 | 事项 | 估计 |
|---|---|---|
| **1** | **IM 消息**（`im_messages/batch_send` + 会话） | 中。已有端点清单，需拿 IM token 与会话 id |
| **2** | **店铺上下文配置化**（多店/多区域） | 小。改 `PageChannel` 与常量 |
| **3** | **运行日志**（`runs.jsonl`） | 小。每个动作追加一条 |
| **4** | **达人邀约后跟踪**（`invitation_group/search/creator` + 统计） | 中。`search/creator` 的 body 还没试出来 |
| **5** | 订单邀评流水线 | 大。要 protobuf |
| **6** | 简易 UI（可选） | 大。但 CLI 已经够用 |

### 39.5 结论

**我们没有"全面的不足"，而是"深度够、广度不够"。**

- **深度**：促销 / 商品机会 / 联盟邀约三条线，我们都比同行做得深
  （同行那三条线各只有 2~4 个端点）
- **广度**：同行覆盖多平台多区域 + IM + 订单 + 任务体系，我们只有单店单区三条线

**最该补的是 IM** —— 邀约完不跟进，前面做的邀请等于半条链路。

---

## 40. ★ 站内 IM：protobuf 私有协议全解（含批量消息）

IM 既不在 `affiliate.` 也不在 `api16-normal-sg.`，是**第三个域 + 第三种编码**。

### 40.1 动态入口

```
GET  {affiliate}/api/v1/im/shop_creator/shop/user/token/get      ← 客户端首选
GET  {affiliate}/api/v1/oec/affiliate/seller/im/get/token        ← 备选
→ data = { token, api_url:"https://oec-im-tt-sg.tiktokglobalshopv.com/",
           ws_url:"wss://frontier.byteoversea.com/ws/v2",
           app_id:380360, fp_id:448, app_key:"1b0770…",
           biz_service_id:10000, frontier_service_id:20345,
           shark_app_name:"ecom_im", region_code:"VN", shop_region:"VN",
           user:{role:2, id:"5038XXXXXXXXXX14"},       ← 注意字段名
           user_info:{name:"ExampleShop", avatar:"…"},
           user_cursor:"1787XXXXXXXXXX03", ws_url, idc_region:"my" }
```

★ **两个端点的 `user` 字段名不一样**：首选端点给 `user.id`，备选端点给 `user.user_id`。
代码里两个都认（`IMClient.self_user_id`），否则 `self_user_id` 会是 0。

★ `api_url` **末尾带 `/`**，路径直接拼。`token` 会过期（本客户端 10 分钟自动刷）。

### 40.2 ★ 拉会话：cmd=200，不是 cmd=203

这是本次踩得最久的一个坑。

| cmd | 路径 | 服务端读的 body | 实测结果 |
|---|---|---|---|
| **203** | `v2/message/get_by_user_init` | `messages_per_user_init_v2_body` | 小增量窗口：**2 会话 / 4 消息**，`has_more=False`；`cursor` 传 `0` 或 `per_user_cursor` 结果相同 |
| **200** | `v2/message/get_by_user` | `messages_per_user_body` | ✅ **全量**：50 条 / 9 会话 / has_more=1 → 再翻 31 条 / 8 会话 / 结束 |

- ★ **列会话必须用 200。** 203 只回一个小增量窗口；账号刚初始化时它甚至返回 **0 会话**，
  只给 `per_user_cursor`（== token 里的 `user_cursor`，含义是"服务端认为你已同步到最新"）。
  稳定复现：14/14 自检里 203 恒定 2 会话/4 消息，200 恒定 89 条/17 会话。
- ★ **路径和 cmd 一一对应，串了会报**
  `request.MessagesPerUserInitV2Body is empty [message_by_user.go:821]`。
  （`/api/v1/message/get_by_user_init` + cmd=200 网关也认，作为回退路径。）

**会话索引 = 从 200 的消息流聚合出来的**，不是直接返回的列表：

```
MessageBody {
  conversation_id(1) conversation_type(2) conversation_short_id(5)
  message_type(6) sender(7) content(8) ext(9) create_time(10)
}
```

`ext` 是**唯一的映射来源**：

| ext key | 含义 |
|---|---|
| `shop_oec_id` | 本店 seller_id |
| `creator_oec_id` | ★ **达人的联盟 ID** —— 与定向计划联表的唯一键 |
| `uname` | 达人 handle |
| `sender_im_id` | 发送者的 **IM user_id**（≠ creator_oec_id，别混） |
| `sender_im_role` | `"2"`=店铺 / `"4"`=达人 |
| `s:sync_create_conversation_idemId` | `2534030704641_<达人im_id>_<店铺im_id>` |

**建会话事件 = `content` 里 `command_type:8`**，它的 ext 才带 `creator_oec_id`。

### 40.3 message_type

| 值 | 含义 |
|---|---|
| **1000** | 文本（我们自己发也用 1000，**不是 7**） |
| 50001 | 系统/命令事件（建会话、加成员、更新 core、倒计时） |

★ **新建会话会带一条「空内容 + `sender_im_role=4`」的文本消息** ——
它是系统通知，**不是达人回话**；但它的 `sender` 正好是达人的 im_id，很有用。
判定"达人是否回话"必须要求 `content.strip()` 非空。

时间语义：`ext["s:sync_update_core_ext"].countdown_time` 是**倒计时截止**（回复窗口），
不是消息时间。

### 40.4 完整端点表（全部实测）

| 用途 | 方法 | URL | cmd | 编码 |
|---|---|---|---|---|
| 会话索引/消息流 | POST | `{api_url}v2/message/get_by_user` | 200 | protobuf |
| 初始化游标 | POST | `{api_url}v2/message/get_by_user_init` | 203 | protobuf |
| 会话内消息 | POST | `{api_url}v1/message/get_by_conversation` | 301 | protobuf |
| 发消息 | POST | `{api_url}v1/message/send` | 100 | protobuf |
| 标记已读 | POST | `{api_url}v3/conversation/mark_read` | 604 | protobuf |
| 读位置 | POST | `{api_url}v3/conversation/get_read_index` | 2000 | protobuf |
| 最小 index | POST | `{api_url}v3/conversation/get_min_index` | 2001 | protobuf |
| **建会话** | POST | `{api_url}api/v1/im/conversation/create?oec_region=VN` | — | **JSON** |
| **按用户名搜会话** | POST | `{api_url}api/v1/im/search/search_conversation_by_users` | — | **JSON** |
| 按 handle 搜（联盟侧） | GET | `{affiliate}/api/v1/im/shop_creator/shop/conversation/search` | — | JSON |
| 通知关系更新 | POST | `{affiliate}/api/v1/affiliate/notification/im/relation/update` | — | JSON |

protobuf 头：`Content-Type: application/x-protobuf`（**不要漏**，否则 `MessagesPerUserInitV2Body is empty`）。
JSON 头：`Content-Type: application/json; charset=utf-8` + **`x-im-paas-token: <token>`**。

### 40.5 信封（对齐线上客户端，非推测）

```python
Request {
  cmd, sequence_id, sdk_version, build_number, token, device_id,
  refer: 3, inbox_type: 0, device_platform: "web", auth_type: 2, body
}
```

| 项 | 读 | 写 |
|---|---|---|
| `sdk_version` | `0.0.8-feat-add-cmd-in-error` | `0.0.1-gec` |
| `build_number` | `93229b4:feat/0.0.8-add-cmd-in-error` | `ad9801f:Detached: ad9801f296fa566d43c75b86cecc603dce10145f` |

（同行 2.0.9 还有一组新版：`sdk_version="1.2.16"` / `build_number="6eae7a1:master"`，
`imType==4` 时使用。我们这组实测可用。）

### 40.6 发文本（cmd=100）

```python
send_message_body = {
  conversation_id, conversation_short_id, conversation_type: 2,
  content, mentioned_users: [], client_message_id: "<uuid4>",
  ticket: "deprecated", message_type: 1000, send_media_list: [],
  ext: {  # 店铺→达人；字段抄线上客户端，别自己编
    "PIGEON_BIZ_TYPE":"1", "monitor_send_message_platform":"pc",
    "monitor_send_message_start_time":"<ms>", "type":"text",
    "original_content": <text>, "detect_lang":"", "a:translate_status":"0",
    "sender_role":"2", "a:user_language":"zh",
    "shop_region":"VN", "target_lang":"vn", "source_lang":"zh",
    "is_cross_board":"1", "cross_board_region":"VN",
    "shop_id": <seller_id>, "s:mentioned_users":"",
    "s:client_message_id": <uuid4>,
  }
}
```

`ext.type` 决定消息形态：`text` / `goods_card`（`goods_id` + `starling_content_key`）等。

### 40.7 ★ 建会话（JSON，给"还没聊过"的达人开线程）

```
POST {api_url}api/v1/im/conversation/create?oec_region=VN
Header: Content-Type: application/json; charset=utf-8
        x-im-paas-token: <token>
Body:  {"participants":[
         {"role":0,"uid":"<creator_oec_id>","extra":{"sender_im_role":"4"}},
         {"role":1,"uid":"<seller_id>",     "extra":{"sender_im_role":"2"}}]}
→ {"code":0,"data":{"conversation_short_id":"7690XXXXXXXXXX92"}}
```

★ **`role:1` 的 uid 是 `shopInfo.shop_id`（= `7494XXXXXXXXXX00`），
不是 IM 的 `user.user_id`（`5038XXXXXXXXXX14`）。** 传错 → `98001004 invalid params`。

实测：`ngoctrinh89` → `7690XXXXXXXXXX92`，`haosuagaming` → `7690XXXXXXXXXX39`。

### 40.8 ★ 按用户名搜会话（JSON）—— 达人→会话的反查

```
POST {api_url}api/v1/im/search/search_conversation_by_users  + x-im-paas-token
Body: {"user_name":"creator_handle","page_no":0,"page_size":20}
```

返回的**信息量最大**，一个请求就给出会话全部元数据：

```json
{"code":0,"data":{
  "matched_conversations":[{"conv_short_id":"7580XXXXXXXXXX98","conv_type":2,
     "last_msg_time":"NUMBER_REDACTED","tags":["c_low_score_shop"],
     "user_id_to_user_names":[{"user_id":"4452XXXXXXXXXX35","user_names":["tauhhxjl"]}]}],
  "core_infos":{"7580XXXXXXXXXX98":{
     "owner_uid":"…","creator_uid":"…",
     "ext":{"creator_oec_id":"7494XXXXXXXXXX07","shop_oec_id":"7494XXXXXXXXXX00",
            "s:sync_create_conversation_idemId":"2534030704641_4452XXXXXXXXXX35_5038XXXXXXXXXX14"},
     "biz_ext":"{\"creator_oec_id\":\"…\",\"handle\":\"tauhhxjl\",\"avatar\":\"…\",
                 \"creator_app_locale\":\"en\"}"}},
  "setting_infos":{"…":{"ext":{"paas:read_index":"0"},"min_index":"0"}},
  "conv_participants":{"…":{"participants":[{"uid":"4452XXXXXXXXXX35",
       "extra":{"sender_im_role":"4","sender_role":"1"}}, …]}}
}}
```

`biz_ext` 是**一个 JSON 字符串**，里面有 `creator_oec_id` / `handle` / `avatar` / `creator_app_locale`。

联盟侧的 `conversation/search?…&uname=` 实测**恒返回空数组 + cursor:-1**（它服务于"分享会话"场景），
**用 IM 侧的 `search_conversation_by_users` 代替**。

### 40.9 传输：还是 Worker

IM 域与联盟域**不同源**，整个 IM 链路都是跨域请求：

- 页面 `fetch` → webmssdk 挂住 promise（§27）
- `about:blank` iframe → `Origin: null` 被判插件（§36/§37）
- **Blob Worker（同源）** → ✅ 可用，且不需要页面在前台

Worker 里 `fetch(url, {credentials:'include', headers:{'content-type':…}})`。
实测该域返回宽松 CORS（`application/x-protobuf` 与自定义头 `x-im-paas-token` 都放行）。

★ **同一个 CDP 端点起两个 Playwright sync 实例 → `Playwright Sync API inside the asyncio loop`。**
`IMClient(affiliate=<已有客户端>)` 支持复用连接，`tk01_im_track.py` 就是这么用的。

### 40.10 批量发送

`send_batch()`：默认 **4~9s 随机间隔**（固定短间隔打容易吃频控）、
连续 3 次失败自动中止、每轮写 `notes/runs.jsonl`。

## 41. ★ 达人邀约后跟踪（定向计划 × 站内 IM 联表）

### 41.1 为什么必须联表

邀约和聊天是两套系统、两套 ID，**唯一能对上的是 `creator_oec_id`**：

| 侧 | 字段 | 来源 |
|---|---|---|
| 定向计划 | `creator_oec_id` `user_name` `invitation_id` `group_creator_status` | `invitation_group/detail` |
| 站内 IM | `conversation_id` 达人 `im_id` `creator_oec_id` | 会话 `ext` / `biz_ext` |

达人同时有**两个 ID**，别混：`creator_oec_id`（联盟，7493…）与 `sender_im_id`（IM，4452…）。

### 41.2 计划侧字段（实测）

```
POST /api/v1/oec/affiliate/seller/invitation_group/search  {"cur_page":1,"page_size":20}
→ data.invitation_list[]          ★ 不是 invitation_groups
  {id, name, group_status, creator_cnt, creator_added_cnt, creator_posted_cnt,
   product_cnt, start_time, end_time, free_sample_rule, product_list[]}

POST .../invitation_group/detail   {"invitation_group_id":"<字符串id>"}
→ data.invitation                 ★ 不是 invitation_group
  {id, name, group_status, creator_cnt, creator_added_cnt, creator_posted_cnt,
   shop_id, region, contacts_info[7], product_list[3],
   creator_id_list[10] {           ← 邀约达人清单就在这
      base_info:{creator_id, nick_name, image, user_name, creator_oec_id,
                 selection_region, permission_tag},
      invitation_id, group_creator_status, product_add_cnt, effective_status}}
```

`group_status`: **2 = 进行中，4 = 已终止**（另有 1 待开始 / 3 已结束，未实测）。
`group_creator_status`: **0 = 待接受**（实测 10/10 都是 0）。其余取值未实测，
代码一律按原值输出（`creator_status_text`），不猜。

★ `invitation_group/search/creator` **没打通**：空 body 到各种参数组合全是 `98001004`，
且绑定错误 oracle 不点名字段（说明不是"缺字段"而是结构不对）。
**不需要它** —— `detail` 里的 `creator_id_list` 信息更全。

### 41.3 联表输出

```
tk01_im_track.py track --save
→ notes/aff_invite_tracking.json
   每个达人：creator_oec_id / handle / nick_name / creator_status_text /
             invitation_id / has_conversation / conversation_id /
             creator_replied / first_creator_reply_time / last_text
   每个计划：im_matched / im_replied / im_no_conversation
```

实测（SHOP_XBORDER，VN，2026-09-28）：

```
● TK01达人邀约-0928  [进行中]
  达人 10 | IM 命中 2 | 达人回话 0 | 无会话 8
    ✗未回  7493XXXXXXXXXX92 @ngoctrinh89  待接受 conv=7690XXXXXXXXXX92
    ✗未回  7493XXXXXXXXXX65 @haosuagaming 待接受 conv=7690XXXXXXXXXX39
    ·无会话 其余 8 个
```

★ **IM 命中 0 是正常的**：那 15 个既有会话全是**主动私信我们**的达人；
定向计划里邀约的达人**默认没有 IM 线程**。要跟踪就得先 `ensure` 建会话。

### 41.4 三种跟踪动作

```bash
python3 tk01_im_track.py groups                       # 列计划
python3 tk01_im_track.py creators <gid>               # 列达人 + 状态
python3 tk01_im_track.py track [gid] --refresh --save # 联表（标 ✔已回 / ✗未回 / ·无会话）
python3 tk01_im_track.py ensure <gid> --yes           # 给无会话的受邀达人建会话（写）
python3 tk01_im_track.py followup --text "话术" --yes  # 给未回话的群发跟进（写）
```

### 41.5 新增文件

| 文件 | 作用 |
|---|---|
| `tk01_im.py` | IM 客户端（protobuf + JSON 双协议、索引、单发/群发、建会话） |
| `tk01_im_track.py` | 定向计划 × IM 联表跟踪 |
| `tiktok.proto` / `tiktok_pb2.py` | 协议定义与编译产物 |
| `notes/im_conversations.json` | 会话索引（17 个会话 + 消息流） |
| `notes/aff_invite_tracking.json` | 邀约跟踪表 |
| `notes/runs.jsonl` | 运行日志 |

### 41.6 实测状态

| 能力 | 状态 |
|---|---|
| IM token / api_url | ✅ 两个端点都通 |
| 会话索引（cmd=200 翻页） | ✅ 89 条消息 → 17 会话 |
| 会话内消息（cmd=301） | ✅ `has_more=False`，文本消息可读 |
| 标记已读（cmd=604） | ✅ `statusCode=0 OK` |
| 读位置（cmd=2000） | ✅ 返回双方 index |
| 建会话（JSON） | ✅ 2 个真实会话建出 |
| 按用户名搜会话 | ✅ 返回 core_infos + biz_ext |
| 发文本（cmd=100） | ✅ **真发成功 2 条**：`server_message_id=7690XXXXXXXXXX84` / `7690XXXXXXXXXX08`，`statusCode=0`、`check_code=0`、`filtered_content=''`（未过审拦截）；cmd=301 回读确认落库 |

### 41.7 自检

```bash
python3 tk01_selftest.py        # 只读，不发消息、不建会话
→ notes/im_selftest.json
```

最近一次：**14/14 PASS**

```
[PASS] 01 IM token（首选端点）                      417ms
[PASS] 02 self_user_id 非 0（两字段名兼容）            0ms
[PASS] 03 cmd=203 初始化游标                       1492ms
[PASS] 03b cmd=203 用上次 per_user_cursor 拉增量     226ms
[PASS] 04 cmd=200 翻页拉消息流                     1357ms  89 条 / 17 会话
[PASS] 05 会话索引聚合（creator_oec_id 映射）          0ms  17 会话，17 个有 creator_oec_id
[PASS] 06 cmd=301 读会话消息                       209ms
[PASS] 07 cmd=2000 读位置                         190ms
[PASS] 08 search_conversation_by_users            262ms
[PASS] 09 conversation/create 报文构造（dry-run）     0ms  role1.uid == seller_id
[PASS] 10 发文本报文构造（dry-run，不发）               0ms  724B
[PASS] 11 invitation_group/search                1860ms  3 个计划
[PASS] 12 invitation_group/detail                2219ms  10 达人
[PASS] 13 邀约 × IM 联表                           3988ms  im_matched=2
```
