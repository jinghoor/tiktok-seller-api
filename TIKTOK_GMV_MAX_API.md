# TikTok GMV Max 广告后台接口技术文档

来源：Hub Studio 环境内实抓浏览器请求（CDP 注入记录器）+ 纯 API 客户端 `tiktok_ads.py` 回放验证。
本文所有数字、ID、字段均取自本机素材文件，未验证项一律标注「未验证」。</br>
素材：`tiktok_ads.py`、`notes/tiktok_payload_template.json`、`notes/tiktok_create_api.json`、`notes/tiktok_product_list_api.json`、`notes/tiktok_session.json`、`notes/tiktok_done.json`、`notes/hub_done.json`、`notes/tiktok_batch.log`、`notes/hub_batch.log`、`hub_capture.py`、`hub_session.py`、`hub_batch.py`

---

# 第一部分：SHOP_LOCAL / 越本土店（原始逆向记录）

> 这一部分是 SHOP_LOCAL（越本土店）的完整逆向过程与回放验证，
> 常量与 SHOP_XBORDER 不通用（差异见 §19）。

## 1. 结论速览

| 指标 | 值 |
|---|---|
| 文档化接口数 | 2 个核心（商品查询 `search_spu`、广告创建 `all_ad_data/create`）+ 1 个辅助（互斥查询 `mutex_roi1/query`） |
| 抓包里出现的其他 TikTok 业务接口 | 19 条 path（§7 全表），其中 7 条来自创建页、其余来自同一环境的其他页面 |
| 认证方式 | cookie（`notes/tiktok_session.json` 导入）+ 请求头 `X-CSRFToken`（值取自 cookie `csrftoken`） |
| 是否需重新登录 | 否。cookie 从 Hub Studio 环境 profile 直接导出 |
| 已导出 cookie 规模 | 410 条总量，其中 `tiktok` 域名下 145 条 |
| 已验证程度 | 商品查询：实抓 + 客户端回放；创建：实抓 1 次 + 客户端批量回放 13 次；互斥查询：仅实抓 |
| 达成效果 | 63 秒内创建 13 条广告计划，加此前 1 条共 14 个 SPU 建满；后台看板 8 行全部「已生效」，ROI 14.00，预算 200.00 USD |
| 单条耗时 | UI 一轮完整流程 10:00:13 → 10:01:08 = 55 秒/条；纯 API 63 秒/13 条 ≈ 4.8 秒/条 |
| 店铺 | Kira Skincare（VN 本土店） |
| 广告账户 | DAMAI-SHOP_LOCAL，`is_ka=true`，`status=4` |

---

## 2. 环境常量

常量全部硬编码在 `tiktok_ads.py` 顶部（第 25-32 行）。

| 常量 | 值 | 用途 / 出现位置 |
|---|---|---|
| `BASE` | `https://seller-vn.tiktok.com` | 全部请求的 host，同时用作 `Origin` |
| `OEC_SELLER_ID` | `7494XXXXXXXXXX00` | query `oec_seller_id`；同时是 `ad_info.shop_id` |
| `AADVID` | `7689XXXXXXXXXX74` | query `aadvid`，广告账户 DAMAI-SHOP_LOCAL |
| `SHOP_BC` | `7626XXXXXXXXXX75` | query `org_id`（商品查询必填）；同时是 `ad_info.shop_authorized_bc` |
| `ROI` | `"14.0"` | `ad_info.roas_bid` 字符串 |
| `BUDGET` | `"200.00"` | `ad_info.budget` 与 `campaign_info.budget`，字符串 |
| `SHOP_ID` | `7494XXXXXXXXXX00` | 与 `OEC_SELLER_ID` 同值，`ad_info.shop_id` |
| Referer | `{BASE}/ads-creation/creation` | 请求头 |

账户侧已抓到的旁证（`notes/tiktok_product_list_api.json`，`roi2/exclusive_authorization/query` 响应）：

| 字段 | 值 |
|---|---|
| `adv_info.name` | `DAMAI-SHOP_LOCAL` |
| `adv_info.is_ka` | `true` |
| `adv_info.status` | `4` |
| `bc_id` | `7626XXXXXXXXXX75` |
| `authorization_status` / `cps_authorization_status` | `1` / `1` |

---

## 3. 认证

### 3.1 会话来源

| 项 | 说明 |
|---|---|
| 导出脚本 | `hub_session.py`（Playwright `connect_over_cdp` 连到 Hub Studio 实例端口，默认 `CDP_PORT`） |
| 导出内容 | `notes/tiktok_session.json`，4 个键：`cookies` / `localStorage` / `url` / `ua` |
| cookie 总数 | 410（全部域），其中含 `tiktok` 的 145 条 |
| 关键 cookie 名 | `csrftoken`（`seller-vn.tiktok.com` 域）、`passport_csrf_token`、`tt_csrf_token`、`msToken` |
| localStorage | 399 键（未用于请求，仅作状态观测；值被导出脚本截断到 120 字符） |
| 页面 URL | `https://seller-vn.tiktok.com/ads-creation/dashboard?...` |
| UA | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36` |

### 3.2 请求头

创建接口抓到的 headers 只有 3 个（`notes/tiktok_create_api.json` → `requests[33]`）：

| Header | 值 |
|---|---|
| `Accept` | `application/json, text/plain, */*` |
| `Content-Type` | `application/json; charset=utf-8` |
| `X-CSRFToken` | 值等于 `seller-vn.tiktok.com` 域的 `csrftoken` cookie 值（32 字符） |

客户端实际发送的头（`tiktok_ads.py` 第 55-62 行）在此基础上补了 `User-Agent` / `Origin` / `Referer`：

| Header | 值 |
|---|---|
| `Accept` | `application/json, text/plain, */*` |
| `Content-Type` | `application/json; charset=utf-8` |
| `User-Agent` | 从 `tiktok_session.json` 的 `ua` 取 |
| `Origin` | `https://seller-vn.tiktok.com` |
| `Referer` | `https://seller-vn.tiktok.com/ads-creation/creation` |
| `X-CSRFToken` | `cookies["csrftoken"]` |

没有出现 `Authorization`、签名参数、`msToken` 参与业务接口的迹象。

### 3.3 典型 cookie 生命周期

| cookie | 域 | 值长度 | `expires`（Unix） |
|---|---|---|---|
| `csrftoken` | `seller-vn.tiktok.com` | 32 | NUMBER_REDACTED |
| `csrftoken` | `ads.tiktok.com` | 32 | NUMBER_REDACTED |
| `passport_csrf_token` | `.tiktok.com` | 32 | NUMBER_REDACTED |
| `tt_csrf_token` | `.tiktok.com` | 36 | NUMBER_REDACTED |

---

## 4. 商品查询接口（已验证）

### 4.1 请求

| 项 | 值 |
|---|---|
| Method | `POST` |
| Path | `/oec_ads/shopping/v1/creation/search_spu` |
| Query | `aadvid=7689XXXXXXXXXX74&exclude_mutex=true&language=zh&locale=zh&new_product_only=false&oec_seller_id=7494XXXXXXXXXX00&org_id=7626XXXXXXXXXX75` |
| Body | 见下 |

```json
{
  "page_info": {"page_index": 1, "page_size": 20},
  "sort_param": {"sort_field": 9, "sort_order": 0},
  "spu_scope": 1,
  "title": "",
  "spu_ids": [],
  "sku_ids": [],
  "mutex_scene": 2
}
```

| Body 字段 | 抓包值 | 说明 |
|---|---|---|
| `page_info.page_index` / `page_size` | `1` / `20` | 抓包用的每页 20；`tiktok_ads.py` 用 `page_size=100`，同样返回 200 且能取到数据（数量未验证） |
| `sort_param.sort_field` / `sort_order` | `9` / `0` | 排序参数，含义未验证 |
| `spu_scope` | `1` | 商品范围，含义未验证 |
| `title` | `""` | 关键词搜索，空串 = 不筛 |
| `spu_ids` / `sku_ids` | `[]` | 定向查询时填，本次为空 |
| `mutex_scene` | `2` | 互斥场景，含义未验证 |

### 4.2 响应

| 项 | 值 |
|---|---|
| HTTP | 200 |
| 顶层 | `{"code":0,"msg":"","data":{"spu_infos":[...],"total_count":14}}` |
| 商品数组路径 | `data.spu_infos[]` |
| 取 SPU ID | `data.spu_infos[].spu.spu_id`（字符串） |
| 抓包样本大小 | 30972 字符，14 条 |

`data.spu_infos[0]` 结构（已抓样本）：

| 路径 | 类型 | 样本值 |
|---|---|---|
| `spu.spu_id` | string | `1737XXXXXXXXXX44` |
| `spu.title` | string | 越南语商品标题 |
| `spu.price.price_range` | string | `99000-159000` |
| `spu.price.sale_price_range` | string | `63000-109000` |
| `spu.price.price_unit` | string | `VND` |
| `spu.stock` | int | `6000` |
| `spu.total_sales` | int | `0` |
| `spu.mutex_status` | int | `2` |
| `spu.ad_service_status` | int | `1` |
| `spu.ad_service_status_for_toko` | int | `2` |
| `spu.shop_id` | string | `7494XXXXXXXXXX00` |
| `spu.category.id` / `.name` | string | `873480` / 中文类目路径 |
| `spu.catalog_id` | string | `""` |
| `spu.modify_time` | int（毫秒） | `1790241050932` |
| `spu.picture` | string | CDN URL |
| `sku_infos[]` | array | 每个 SPU 挂 SKU：`sku_id` / `price{price,sale_price,price_unit}` / `picture` / `title` / `catalog_id` / `product_id` |

### 4.3 关键坑：漏 `org_id` 报权限错

| 现象 | 缺 `org_id` query 参数时返回 `code=3`，`msg` 为「当前账号没有使用当前店铺的商品进行广告投放的权限。」 |
|---|---|
| 原因 | `org_id` 必须等于 `SHOP_BC`（`7626XXXXXXXXXX75`），不是 `oec_seller_id` |
| 修法 | `tiktok_ads.py` 第 92-94 行显式把 `org_id` 并进 query，并留注释 |

### 4.4 抓包样本的实际内容

| 观测 | 值 |
|---|---|
| `data.total_count` | `14` |
| `data.spu_infos` 长度 | `14` |
| 返回的 14 个 `spu_id` | 与 `notes/tiktok_done.json` 的 14 个 ID **完全一致**（集合相等，无差集） |

---

## 5. 创建接口（已验证）

### 5.1 请求

| 项 | 值 |
|---|---|
| Method | `POST` |
| Path | `/oec_ads/shopping/v1/creation/all_ad_data/create` |
| Query | `locale=zh&language=zh&oec_seller_id=7494XXXXXXXXXX00&aadvid=7689XXXXXXXXXX74` |
| Headers | `Accept`、`Content-Type: application/json; charset=utf-8`、`X-CSRFToken`（其余头部不需要） |
| Body | 完整 payload，见 §6 与 `notes/tiktok_payload_template.json` |
| 超时设置 | `tiktok_ads.py` 用 `timeout=60`（商品查询用 30） |
| 抓包时间戳样本 | `campaign_name`/`start_time` 均为 `2026-09-25 09:02:02` |

### 5.2 响应

| 项 | 值 |
|---|---|
| HTTP | 200 |
| Body | `{"code":0,"msg":"","data":{"campaign_id":"1877XXXXXXXXXX78","ad_id":"1877XXXXXXXXXX94"}}` |
| 取值 | `data.campaign_id`、`data.ad_id`，均为字符串 |
| 失败判定 | `tiktok_ads.py::_post` 对 `code not in (0, None)` 抛 `RuntimeError("业务错误 code=… msg=…")`；非 200 抛 `HTTP <code>`；非 JSON 抛 `非 JSON 响应` |

### 5.3 批量创建产出（`notes/tiktok_batch.log`）

| 序 | spu_id | campaign_id | ad_id |
|---|---|---|---|
| 1 | 1737XXXXXXXXXX12 | 1877XXXXXXXXXX58 | 1877XXXXXXXXXX74 |
| 2 | 1737XXXXXXXXXX32 | 1877XXXXXXXXXX26 | 1877XXXXXXXXXX26 |
| 3 | 1737XXXXXXXXXX68 | 1877XXXXXXXXXX69 | 1877XXXXXXXXXX85 |
| 4 | 1737XXXXXXXXXX40 | 1877XXXXXXXXXX06 | 1877XXXXXXXXXX22 |
| 5 | 1737XXXXXXXXXX04 | 1877XXXXXXXXXX14 | 1877XXXXXXXXXX30 |
| 6 | 1737XXXXXXXXXX40 | 1877XXXXXXXXXX89 | 1877XXXXXXXXXX05 |
| 7 | 1737XXXXXXXXXX04 | 1877XXXXXXXXXX14 | 1877XXXXXXXXXX82 |
| 8 | 1737XXXXXXXXXX24 | 1877XXXXXXXXXX86 | 1877XXXXXXXXXX02 |
| 9 | 1737XXXXXXXXXX96 | 1877XXXXXXXXXX18 | 1877XXXXXXXXXX34 |
| 10 | 1737XXXXXXXXXX00 | 1877XXXXXXXXXX50 | 1877XXXXXXXXXX86 |
| 11 | 1737XXXXXXXXXX12 | 1877XXXXXXXXXX78 | 1877XXXXXXXXXX94 |
| 12 | 1737XXXXXXXXXX08 | 1877XXXXXXXXXX62 | 1877XXXXXXXXXX78 |
| 13 | 1737XXXXXXXXXX76 | 1877XXXXXXXXXX30 | 1877XXXXXXXXXX14 |

批量日志时间跨度：`10:05:24` → `10:06:29`，即 **63 秒 13 条**，单条间隔恒为 5 秒（`--sleep` 默认 2.0s + 请求耗时）。<br>
`ad_id` 与 `campaign_id` 规律：`ad_id = campaign_id + 16`（样本内全部成立，仅观测规律，未验证是否平台保证）。

### 5.4 辅助接口：互斥查询（仅实抓，未回放）

| 项 | 值 |
|---|---|
| Method / Path | `POST /oec_ads/shopping/v1/roi2/mutex_roi1/query` |
| Query | `locale=zh&language=zh&oec_seller_id=…&aadvid=…` |
| Body | `{"mutex_asset_ids":["1737XXXXXXXXXX36"],"mutex_asset_id_type":101}` |
| 响应 | `{"code":0,"msg":"","extra":null,"data":{"mutex_roi1_ads":[],"influence_ad_object_count":0}}` |
| 用途 | 建广告前查同一商品是否已被 ROI1 计划占用 |
| `mutex_asset_id_type` | `101` = SPU（同抓包里 `100` 用于 shop 级 `exclusive_authorization/query`） |
| 客户端行为 | `create` 子命令会先调它，失败只打印一行「mutex 查询失败(继续)」不中断 |

---

## 6. Payload 不变量

基准文件：`notes/tiktok_payload_template.json`（92 行）。
核对方式：把抓包真实请求体（`tiktok_create_api.json` → `requests[33].body`）与模板展平成叶子路径后逐项比对。

| 项 | 结果 |
|---|---|
| 叶子字段数 | 抓包 66 / 模板 66 |
| 字段路径集合 | 完全相同（无增无缺） |
| 值不同的字段 | **0 个** |

即：**模板与实抓请求体数值完全一致**——连 `campaign_name`、`ad_info.name`、`start_time`、`product_list[0].spu_id`（`1737XXXXXXXXXX36`）都是同一个值。模板本身就是从这次 UI 会话回捞出来的可提交状态，`build_payload` 只在此基础上替换 §6.3 的 4 个变化字段并重钉约束字段。

### 6.1 恒定字段

| 路径 | 值 | 类型 |
|---|---|---|
| `ad_info.roas_bid` | `"14.0"` | string |
| `ad_info.promotion_days_setting.is_enable` | `false` | bool |
| `ad_info.promotion_days_setting.benchmark_roas_bid` | `14` | int（注意：与 `roas_bid` 一个是字符串一个是数字） |
| `product_list` 长度 | 恒为 `1` | 1 个 SPU / 条广告计划 |
| `ad_info.budget` | `"200.00"` | string |
| `campaign_info.budget` | `"200.00"` | string |
| `ad_info.budget_mode` / `campaign_info.budget_mode` | `0` | int |
| `ad_info.schedule_type` | `1` | 持续投放，无结束时间 |
| `ad_info.country` | `"VN"` | string |
| `ad_info.custom_tz_id` | `"7473XXXXXXXXXX44"` | string |
| `ad_info.custom_tz_type` | `2` | int |
| `ad_info.external_type` | `304` | int |
| `ad_info.optimize_goal` | `111` | int |
| `ad_info.deep_bid_type` | `108` | int |
| `ad_info.product_specific_type` | `3` | int |

### 6.2 其余恒定字段（模板内，未逐一变更验证）

| 路径 | 值 |
|---|---|
| `campaign_info.campaign_id` / `ad_info.campaign_id` / `ad_info.ad_id` | `""`（创建时留空） |
| `campaign_info.shop_automation_type` | `2` |
| `campaign_info.shop_image_aigc_mode` | `1` |
| `campaign_info.gmv_roi_mode` | `0` |
| `ad_info.inventory_flow_type` / `inventory_flow` | `0` / `[3000, 9000]` |
| `ad_info.shopping_inventory_type` | `1` |
| `ad_info.is_comment_disable` | `0` |
| `ad_info.flow_control_mode` | `1` |
| `ad_info.product_video_selection_type` | `1` |
| `ad_info.pricing` | `9` |
| `ad_info.cpa_skip_first_phrase` | `1` |
| `ad_info.external_action` | `96` |
| `ad_info.product_platform_id` | `""` |
| `ad_info.shop_id` | `7494XXXXXXXXXX00` |
| `ad_info.shop_type` | `1` |
| `ad_info.shop_authorized_bc` | `7626XXXXXXXXXX75` |
| `ad_info.promotion_flow_type` | `5` |
| `ad_info.product_source` | `2` |
| `ad_info.product_bid_type` | `1` |
| `ad_info.promotion_days_setting.automode_enable` | `true` |
| `ad_info.promotion_days_setting.custom_schedules` | `[]` |
| `ad_info.promotion_days_setting.roas_bid_multiplier` | `90` |
| `ad_info.promotion_days_setting.budget_multiplier` | `150` |
| `ad_info.promotion_days_setting.adjusted_roas_bid` | `"12.6"`（= 14 × 0.9） |
| `ad_info.promotion_days_setting.adjusted_budget` | `"300.00"`（= 200 × 1.5） |
| `ad_info.compensation_activity_type` | `3` |
| `ad_info.gmax_budget_adjust_setting.strategy` | `2` |
| `ad_info.gmax_budget_adjust_setting.auto_budget_switch` | `false` |
| `ad_info.gmax_budget_adjust_setting.promotion_day_adjust_config.adjust_ratio` | `0.5` |
| `ad_info.gmax_budget_adjust_setting.promotion_day_adjust_config.max_daily_adjust_times` | `10` |
| `ad_info.identity_list` / `custom_anchor_videos` / `shop_video_filters` / `pre_item_list` | `[]` |
| `ad_info.shop_aca_mode` / `shop_aigc_mode` | `1` / `1` |
| `ad_info.enable_shop_video_exclusion_filter` | `true` |
| `ad_info.shop_new_creative_exploration` | `1` |
| `ad_info.shop_product_boost_type` | `1` |
| `risk_info.*` | 见 §6.4 |

### 6.3 变化字段（仅 4 项 + 自动生成）

| 路径 | 生成方式（`tiktok_ads.py::build_payload`） |
|---|---|
| `campaign_info.campaign_name` | `商品 GMV Max_总收入_Kira Skincare_{YYYYMMDDHHMMSS}`（可被 `campaign_name=` 覆盖） |
| `ad_info.name` | `广告组_Kira Skincare_{YYYY-MM-DD HH:MM:SS}` |
| `ad_info.start_time` | 提交时刻本地时间，格式 `YYYY-MM-DD HH:MM:SS`（可被 `start_time=` 覆盖） |
| `ad_info.product_list[0].spu_id` | 目标 SPU，字符串化 |

被 `build_payload` 强制重钉的字段（即使模板漂移也会被覆盖回基准值）：`roas_bid`、`budget`（ad 与 campaign 两处）、`budget_mode`（两处）、`promotion_days_setting.is_enable`、`promotion_days_setting.benchmark_roas_bid`。

### 6.4 `risk_info` 段

| 字段 | 值 |
|---|---|
| `cookie_enabled` | `true` |
| `screen_width` / `screen_height` | `1512` / `982` |
| `browser_language` | `vi-VN` |
| `browser_platform` | `MacIntel` |
| `browser_name` / `browser_version` | `Mozilla` / Chrome 141 UA 串 |
| `browser_online` | `true` |
| `timezone_name` | `Asia/Bangkok` |

`risk_info` 与 query 里的 `locale=zh&language=zh` 不一致（前者 vi-VN / Asia/Bangkok，后者 zh）——服务端未因此拒绝，抓包与客户端回放都成功。是否影响风控：未验证。

### 6.5 页面上抓到的高级设置默认值（旁证）

`POST /oec_ads/shopping/v1/creation/get_gmax_advanced_setting` 抓包请求体：

```json
{"check":true,
 "gmax_budget_adjust_setting":{"strategy":2,"auto_budget_switch":false,
   "promotion_day_adjust_config":{"adjust_ratio":0.5,"max_daily_adjust_times":10}},
 "promotion_days_setting":{"is_enable":true,"automode_enable":true,"custom_schedules":[],
   "roas_bid_multiplier":90,"adjusted_roas_bid":"1.8"},
 "budget":"200.00","roas_bid":2,"key_live_days":[]}
```

响应：`{"code":0,"data":{"mode":3,"effective_budget":200,"effective_roas_bid":1.8,"next_increase_budget":100,"max_budget":1200,"remain_adjust_times":10}}`。
页面的 `promotion_days_setting.is_enable=true` 是默认态，必须靠 UI 关掉或在 payload 里直接置 `false`——纯 API 方案直接置 `false`，绕过了这次额外调用。

---

## 7. 抓包覆盖到的其他接口（未构造请求，仅记录）

来自 `notes/tiktok_product_list_api.json`（251 条记录，含埋点）：

| Method | Path | 抓包次数 |
|---|---|---|
| POST | `/oec_ads/shopping/v1/creation/search_spu` | 1 |
| POST | `/oec_ads/shopping/v1/timezone/get` | 1 |
| POST | `/oec_ads/shopping/v1/creation/get_gmax_advanced_setting` | 1 |
| POST | `/oec_ads/shopping/v1/creation/get_category_list` | 1 |
| POST | `/oec_ads/shopping/v1/creation/shop_claimed_products` | 1 |
| POST | `/oec_ads/shopping/v1/creation_recommendation` | 2 |
| POST | `/oec_ads/shopping/v1/creation_recommendation/advanced_setting` | 2 |
| POST | `/oec_ads/shopping/v1/benefit/campaign/query/creation` | 2 |
| POST | `/oec_ads/shopping/v1/roi2/exclusive_authorization/query` | 1 |
| POST | `/oec_ads/shopping/v2/creative/video_list` | 5 |
| POST | `/oec_ads/shopping/v1/recommendation/good_campaign_standard` | 3 |
| POST | `/oec_ads/pa/api/account/payment/query_bind_pa_info/` | 1（`tiktok_create_api.json`） |
| POST | `/oec_ads/pa/api/account/payment/query_payment_ready/` | 1（同上） |
| GET | `/oec_ads/bm/account/query/billing_and_own/info/` | 1（同上） |
| GET | `/oec_ads/shopping/v1/oec/get_onboard_info` | 1（同上） |
| POST | `/oec_ads/shopping/v1/oec/check_primary_adv_access` | 1（同上） |
| GET | `/oec_ads/bm/technical/white_list/config/` | 1（同上） |
| POST | `/api/v1/arch/config_center_gw/get_config` | 6 |
| POST | `/api/v4/i18n/optimizer/message/` | 1 |

其中 `shop_claimed_products`（body 传 `{}`）响应含 `data.claimed_product_list`，抓包里是 7 个 id：

```
1737XXXXXXXXXX48  1737XXXXXXXXXX36  1737XXXXXXXXXX20  1737XXXXXXXXXX16
1737XXXXXXXXXX44  1737XXXXXXXXXX64  1737XXXXXXXXXX16
```

这 7 个 id **不在** `search_spu` 返回的 14 个里（两集合无交集）。同一份 localStorage 里存在键
`gmv-max-shop_key_7494XXXXXXXXXX96_7626XXXXXXXXXX75_7689XXXXXXXXXX74_claimedProductsPolling`，值以 `{"claimedSpuIds":[…` 开头——即「已认领商品」是前端单独轮询维护的集合，与 `search_spu` 的 `exclude_mutex=true` 不是同一套过滤。

接口语义边界（`exclude_mutex=true` 到底按什么维度排除）未验证；§9.1 有对应矛盾记录。

---

## 8. `tiktok_ads.py` 命令行

| 子命令 | 参数 | 行为 | 退出码 |
|---|---|---|---|
| `products` | 无（内部写死 `page_size=100`） | 调 `search_spu`，打印「可投商品(未占用): N」+ 每行 `spu_id` 与标题前 60 字符 | 成功 `0`；异常由 `RuntimeError` 抛栈（`exit 1`） |
| `create` | `--spu <id>`（必填）、`--dry`（可选） | 先 `check_mutex`（失败仅打印不中断）→ 打印 `提交 spu=… start_time=… ROI=14.0 促销日=关 预算=200.00` → `--dry` 时只打印「[dry] 不提交」直接返回；否则提交并打印 `campaign_id` / `ad_id`，把 spu 写进 `notes/tiktok_done.json` | 成功 `0`；`--dry` 也 `0`；异常 `1` |
| `batch` | `--limit N`（默认 0 = 不限）、`--sleep S`（默认 2.0 秒）、`--keep-going`（遇错不中断） | 读 `tiktok_done.json` → 拉 `products(page_size=100)` → 过滤已做的 → 逐个 `create`，每条成功即写 `done.json`（断点续跑）并 `sleep` | 恒为 `0`（失败不改变退出码，只写日志） |

其他行为约定：

| 项 | 说明 |
|---|---|
| 缺会话文件 | `TikTokAds()` 抛 `SystemExit("缺少会话文件 …;先跑 hub_session.py")` |
| 日志 | 双写 stdout + `notes/tiktok_batch.log`，行格式 `[HH:MM:SS] msg` |
| 断点续跑 | `notes/tiktok_done.json`，JSON 数组，每次成功即落盘（不是批末统一写） |
| 失败日志格式 | `[{i}/{n}] ✗ spu=… 失败: {异常类名}: {前 160 字符}` |
| 未实现 | 无 `created` 子命令（模块 docstring 第 7 行提到 `created`，argparse 里没有——**docstring 与实现不一致**） |

### 8.1 最小可复制用法

```python
# 直接复用客户端:列商品 → 建 1 条
from tiktok_ads import TikTokAds, ROI, BUDGET

c = TikTokAds()                      # 默认读 notes/tiktok_session.json
items = c.products(page_size=100)    # search_spu
spu = c.spu_id(items[0])             # data.spu_infos[].spu.spu_id
print(spu, c.title_of(items[0]))

payload = c.build_payload(spu)       # 只组装、不发请求(可先落盘人工核对)
data = c.create(spu)                 # POST all_ad_data/create
print(data["campaign_id"], data["ad_id"])
```

```bash
python3 tiktok_ads.py products
python3 tiktok_ads.py create --spu 1737XXXXXXXXXX76 --dry
python3 tiktok_ads.py create --spu 1737XXXXXXXXXX76
python3 tiktok_ads.py batch --limit 3 --sleep 1 --keep-going
```

依赖：`requests`（会话文件由 `hub_session.py` 生成，需要 `playwright` + 一个已登录的 Hub Studio 实例端口）。

---

## 9. 实测成果

| 项 | 值 | 证据 |
|---|---|---|
| 纯 API 批量 | 13 条 / 63 秒（10:05:24 → 10:06:29） | `notes/tiktok_batch.log` |
| 此前单条 | 1 条（UI 路线跑通的那一条，spu `1737XXXXXXXXXX48`） | `notes/hub_done.json`、`notes/hub_batch.log` |
| 累计 SPU | 14 | `notes/tiktok_done.json`（14 个 id） |
| 后台看板 | 8 行全部「已生效」 | 任务下达时给定的观测值（原始看板截图不在素材里，见 §12 说明） |
| ROI / 预算 | 14.00 / 200.00 USD | `notes/hub_promo_off.png` 右侧「广告计划摘要」：`ROI 目标: 14.0`、`当前预算: 200.00 USD` |
| 广告账户 / 店铺 | DAMAI-SHOP_LOCAL（主要账号）/ Kira Skincare | `notes/hub_dash.png` |
| 是否建满 | 任务记录：最后一次 `search_spu` 返回 0 个可用商品 = 已加到上限 | 与已抓样本冲突，见 §9.1 |

### 9.1 与素材的冲突（重要）

已抓的 `search_spu` 响应（`notes/tiktok_product_list_api.json`）返回的是 **14 个**商品、`total_count=14`，且这 14 个 id 与 `notes/tiktok_done.json` **完全相等**。也就是说：

* 该样本不能证明「返回 0 个可用商品」；它证明的是相反状态——`exclude_mutex=true` 下返回了 14 个、其中 14 个后来都被建成了广告。
* 时间线上，这份样本落盘于 `10:04`（批量开跑 `10:05:24` 之前）。此前的 14 条里只有 1 条来自 UI（`hub_done.json` 的 `1737XXXXXXXXXX48`，该 id 不在样本里），因此样本里的 14 条在抓取时确实都还没有广告。
* 那么批量为什么还能建 13 条？样本里另有一个集合：`shop_claimed_products` 返回 7 个 id（见 §7），与 `search_spu` 的 14 个**零交集**。两个集合关系及 `exclude_mutex` 的真实语义**未验证**。
* 「加满上限」这一结论暂时只有任务描述作为来源，素材内没有对应抓包或日志。要看它成立，需要重跑一次 `python3 tiktok_ads.py products` 并留存输出。

---

## 10. 踩过的坑

### 10.1 促销日开关误判（DOM 选择器错）

| 项 | 内容 |
|---|---|
| 错误做法 | 读 `.promotion-days-switch-label` 的 class/text，得到 `false`（误以为已关） |
| 真相 | 真实开关元素是 `[data-testid="promotion-days-toggle-3EnDzt"]`，判据是它的 `aria-checked` |
| 证据 | `hub_promo.py` 枚举全部 `[role=switch]` 后才发现；`hub_promoff.py` 用 testid 读 `aria-checked=true` → 点击 → 变 `false`；截图 `notes/hub_promo_off.png` 显示开关为关闭态 |
| 结论 | 必须用 testid 判定，不能读文本节点或 class 名 |

### 10.2 ROI 输入框全选失效

| 项 | 内容 |
|---|---|
| 错误做法 | `Meta+A` / `Control+A` 全选后输入 |
| 现象 | 结果变成 `"142.0"`（原值 `14.0` 前面插入了 `2`，全选没生效） |
| 修法 | `inp.click()` → `inp.click(click_count=3)` 三击全选 → `Backspace` 清空 → 校验 `input_value()` 为空，不空则连按 12 次 `Backspace` 兜底 → `type(val, delay=90)` → `Tab` → 读组件 `value` 复核 |
| 实现 | `hub_setroi2.py`、`hub_batch.py::set_roi`、`hub_capture.py` 第 117-122 行 |
| 纯 API 方案 | 无需输入框，直接把 `roas_bid` 写成 `"14.0"` |

### 10.3 抽屉元素拦截点击 + 假按钮

| 项 | 内容 |
|---|---|
| 拦截元素 | `[data-testid="product-select-index-6KM6mN"]`（商品选择抽屉）覆盖在弹窗之上 |
| 现象 | 自定义按钮忽略 JS `.click()`，点了没反应 |
| 修法 | 用真实鼠标事件：`pg.get_by_text("确认", exact=True)` + 遍历 `bounding_box()` 取 `width > 20` 的那个再 `.click()`；抽屉关闭判断用 `pg.locator(SEL_DRAWER).count() == 0` 轮询 10 次 |
| 相关排查 | `hub_drawer.py`（dump 抽屉的 `getBoundingClientRect` / `display` / `open` / `visible`）、`hub_confirm.py`、`hub_iframe.py` |

### 10.4 点商品复选框点中了表头「全选」

| 项 | 内容 |
|---|---|
| 错误做法 | 取第 1 个可见 `input[type=checkbox]`（idx=1）当作第一个商品（idx=0 是表头「全选」） |
| 现象 | 该次点击落到表头全选框上，整页商品被选中 |
| 实测结果 | 截图 `notes/hub_picked.png` 底部显示「已选择 **18** 件商品」，4 个可见行全部打勾、表头也打勾 |
| 修法 | 跳过行文本含「商品名称」的行；只接受行文本匹配 `/ID:\s*\d+/` 的行（`hub_fix.py`）；`hub_batch.py::pick_products` 用「按 id 匹配行再勾」的方式，并回读 checked 行做断言 |
| 纯 API 方案 | 不存在这一步，`product_list[0].spu_id` 直接指定 |

### 10.5 `SCHEDULE_FROM_NOW` 仍必须显式传 `schedule_start_time`

| 项 | 内容 |
|---|---|
| 现象 | 排期类型为「从现在开始」（`schedule_type=1`）时若不带开始时间，服务端 MySQL 报 `Incorrect datetime value: '0000-00-00'` |
| 修法 | 无论哪种排期都显式传 `ad_info.start_time`，格式 `YYYY-MM-DD HH:MM:SS`；`tiktok_ads.py` 每条都用当前本地时间生成 |
| 记录位置 | 该结论同时写在 adfly 侧文档 `ADFLY_API_FULL.md` 第 1784 行（同一坑的另一侧实现） |

### 10.6 坑的代价对比

| 坑 | UI 方案成本 | API 方案 |
|---|---|---|
| 促销日开关 | 需要重跑 + 截图核对 | 不存在（payload 直接 `is_enable=false`） |
| ROI 输入 | 全选失效 + 逐字符删除 + 复核 | 不存在 |
| 抽屉/假按钮 | 需要真实鼠标事件 + 遮罩轮询 | 不存在 |
| 表头全选 | 多选 18 个商品，得回滚重来 | 不存在 |
| 排期时间 | 需读页面状态 | 直接写 payload |

---

## 11. UI 自动化 vs 纯 API

| 维度 | `hub_batch.py`（UI / CDP） | `tiktok_ads.py`（纯 API） |
|---|---|---|
| 单条耗时 | 一轮完整流程 55 秒（`notes/hub_batch.log`：10:00:13 起 → 10:01:08「已提交」，含开创建页、勾选、设 ROI、发布、等跳回 dashboard） | 4.8 秒/条（63 秒 / 13 条） |
| 吞吐 | 受页面渲染、抽屉动画、遮罩消失、发布后跳转约束 | 只受 HTTP 往返约束 |
| 依赖 | 端口 `CDP_PORT` 的 Chrome + `ads-creation` 页面 + 选择器全部正确 | `notes/tiktok_session.json` 一份 cookie |
| 脆弱点 | testid 变了就废（促销日/ROI/抽屉/Budget 全是 testid）；文案改了也废（「添加商品」「确认」「发布」「商品名称」「ID:」） | 只依赖 path + query + payload 字段 |
| 可重放 | 每次都要重走 UI，无法脚本化 diff | 可 `--dry` 先落 payload 人工核对，可重放、可 diff、可批量 |
| 校验能力 | 能在提交前读页面状态做断言（`selected`/`promo`/`roi`） | 无页面状态可读，只能靠响应 `code` + 后台复核 |
| 失败恢复 | 失败要重开创建页，慢 | 直接重发；`done.json` 记录进度，断点续跑 |
| 并发 | 单页串行，天然无法并发 | 理论可并发（未验证，`--sleep` 目前是串行间隔） |
| 环境要求 | 必须有浏览器 + Hub Studio 实例 | 只要有 cookie（在有效期内） |

结论：UI 路线只保留价值是「首次抓包」和「兜底核对」；日常批量走 API。

---

## 12. 限制与已知缺口

| 限制 | 说明 | 处理 |
|---|---|---|
| cookie 会过期 | `notes/tiktok_session.json` 是快照；过期后所有请求返回未授权 | 重跑 `hub_session.py --port <CDP_PORT>` 从 Hub Studio 重新导出 |
| `X-CSRFToken` 来源 | 值必须等于 `seller-vn.tiktok.com` 域的 `csrftoken` cookie | 换 cookie 后自动跟随；不要手工写死 |
| 单店铺硬编码 | 换店铺要改 4 个常量：`OEC_SELLER_ID`、`AADVID`、`SHOP_ID`、`SHOP_BC`（`SHOP_ID` 与 `OEC_SELLER_ID` 同值，`SHOP_BC` 同时当 `org_id` 用） | 目前是模块级常量，未做参数化 |
| 「加满上限」结论 | 只有任务描述，素材内无对应抓包 | 需重跑 `python3 tiktok_ads.py products` 留存输出 |
| 看板 8 行数据 | 素材里没有对应的看板截图或 `hub_count.py` 输出文件 | 如需复核，跑 `hub_count.py` 并留存输出 |
| 18 / 14 / 7 三个集合的关系 | `hub_picked.png` 显示选中 18；`search_spu` 返回 14；`shop_claimed_products` 返回 7 | 语义未验证，不要当成同一口径引用 |
| `search_spu` 的 `page_size` 上限 | 客户端用 100，抓包用 20，都能返回数据；是否分页截断未验证 | 大批量前先核对 `total_count` 与 `len(spu_infos)` |
| `created` 子命令 | 模块 docstring 提到，argparse 未实现 | 文档按实现写 |
| 素材未落盘的内容 | `hub_flow.py` 的 `schedule_start_time` / MySQL 报错、18 个商品的实际 id 列表、看板 8 行的原件——只存在于会话过程，没有文件证据 | 已在 §10、§12 标注来源强弱 |

---

## 附：本文引用的素材文件

| 文件 | 用途 |
|---|---|
| `tiktok_ads.py` | 纯 API 客户端主逻辑（226 行） |
| `notes/tiktok_payload_template.json` | 建广告请求体基准（92 行） |
| `notes/tiktok_create_api.json` | 实抓创建请求（41 条记录，创建请求在 `requests[33]`） |
| `notes/tiktok_product_list_api.json` | 实抓商品查询及创建页其他请求（251 条） |
| `notes/tiktok_session.json` | cookie / localStorage 快照（只读结构，值不入文档） |
| `notes/tiktok_done.json` | 已建 14 个 spu_id |
| `notes/hub_done.json` | UI 方案已建 1 个 spu_id |
| `notes/tiktok_batch.log` | 纯 API 批量日志（63 秒 13 条） |
| `notes/hub_batch.log` | UI 批量日志（一轮完整流程 55 秒，1 条） |
| `hub_capture.py` | CDP 注入式抓包器（fetch + XHR 双挂钩） |
| `hub_session.py` | cookie / localStorage 导出 |
| `hub_batch.py` | UI 自动化兜底方案 |
| `notes/hub_now.png` / `hub_picked.png` / `hub_promo_off.png` / `hub_roi2.png` / `hub_dash.png` | 关键状态截图证据 |

---
---

# 第二部分：SHOP_XBORDER / ExampleShop 跨境店（已验证跑通）

> 第一节那套常量是 **SHOP_LOCAL（越本土店）**的，跨境店完全不通用。
> 本节记录 **TK01_CrossBorder_Shop / ExampleShop** 的完整可跑方案。
> 抓包日期 2026-09-26，实测已成功创建广告并回读校验。

## 13. 环境常量（跨境店）

| 常量 | 值 | 说明 |
|---|---|---|
| 后台主域 | `seller.tiktokshopglobalselling.com` | **广告接口全部走这里** |
| 商品中心域 | `api16-normal-sg.tiktokshopglobalselling.com` | 商品类接口（aid=6556） |
| `oec_seller_id` / `shop_id` | `7494XXXXXXXXXX00` | 两家同值 |
| `aadvid` | `7689XXXXXXXXXX09` | 广告账户 **DAMAI-SHOP_XBORDER** |
| `org_id` / `shop_authorized_bc` | `7385XXXXXXXXXX92` | BC「Hello House3」 |
| 店铺 | ExampleShop，`region_code=CN`（跨境） | `shop_code=CNVNCBLNLLHT` |
| 时区 | UTC+07:00 | 仪表板显示「科布多时间(蒙古)」 |

### 13.1 ⚠ 域路由（踩过，必看）

**广告类接口不能用商品中心域。** `api16...` 打 `creation/*` 全部 404：

```
POST https://api16-normal-sg.tiktokshopglobalselling.com/oec_ads/shopping/v1/creation/search_spu
→ HTTP 404 (TLB)

POST https://seller.tiktokshopglobalselling.com/oec_ads/shopping/v1/creation/search_spu
→ 200 {"code":0,...}
```

**规则**：`/oec_ads/**` → 一律 `seller.tiktokshopglobalselling.com`；
`/api/v1/product/**`（商品管理）→ `api16-normal-sg...`。

### 13.2 `org_id` 的确定

`user_admin_bc` 返回两个候选，只有一个能用：

| 候选 | 结果 |
|---|---|
| `7385XXXXXXXXXX92` (Hello House3) | ✅ `code:0` |
| `7379XXXXXXXXXX81` (Hello House2) | ❌ code=3「没有使用当前店铺的商品进行广告投放的权限」 |
| `7382XXXXXXXXXX33` (partner_bc NNQQS_TK) | ❌ 同上 |

## 14. 创建接口的完整 payload

### 14.1 顶层结构：**4 个字段**（不是 3 个）

从 `creation-atlas/ads/js/entry-esm.*.js` 解出的 SDK 定义：

```js
function CreateAllAdData(Br, Ur) {
  const Xr = {
    campaign_info:    Wr.campaign_info,
    ad_info:          Wr.ad_info,
    risk_info:        Wr.risk_info,
    sdk_create_source: Wr.sdk_create_source,   // ← 容易漏
  };
  const Jr = {aadvid, oec_seller_id, locale, language,
              _signature, msToken, "X-Bogus"};     // query
  const Zr = {"Tt-Ticket-Guard-Client-Data", "Tt-Ticket-Guard-Public-Key",
              "Tt-Ticket-Guard-Version", "Tt-Ticket-Guard-Web-Version",
              "Tt-Ticket-Guard-Iteration-Version"}; // headers
}
```

**实测结论**：`sdk_create_source` 缺失也能成功（服务端容错），
`_signature`/`X-Bogus`/`msToken`/`Tt-Ticket-Guard-*` **都不是必需**。

### 14.2 🔴 最关键的一处：`adjusted_roas_bid`

这是整个逆向里唯一真正卡死流程的字段。

```json
"promotion_days_setting": {
  "is_enable": false,
  "automode_enable": true,
  "roas_bid_multiplier": 90,
  "benchmark_roas_bid": 20,        // = roas_bid（数字）
  "adjusted_roas_bid": "18.0"      // = roas_bid × 0.9（字符串）★
}
```

**错填 `adjusted_roas_bid = "20.0"`（等于 roas_bid）会失败**：

```json
{"code":3,"msg":"出现错误，请重试。",
 "extra":{"i18n_key":"promotion_days_v2_adjusted_roas_bid_not_equal"}}
```

计算式（两个样本都吻合）：

| 目标 ROI | multiplier | 正确 adjusted_roas_bid |
|---|---|---|
| 20 | 90 | **18.0** |
| 14 | 90 | **12.6** |

即 `adjusted_roas_bid = roas_bid × roas_bid_multiplier / 100`。

### 14.3 其余必填字段（用「删掉看是否报参数错误」逐项确证）

| 字段 | 值 | 删掉后的报错 |
|---|---|---|
| `ad_info.promotion_flow_type` | `5` | 参数无效 |
| `ad_info.optimize_goal` | `111` | 参数无效 |
| `ad_info.deep_bid_type` | `108` | 参数无效 |
| `ad_info.pricing` | `9` | 改 1 →「计费点仅支持oCPM」 |
| `ad_info.product_specific_type` | `3` | 改 1 →「"所有商品"系列不支持选择特定商品」 |
| `ad_info.country` | `"VN"` | 参数无效 |
| `ad_info.shop_id` | `7494XXXXXXXXXX00` | 参数无效 |
| `ad_info.shop_authorized_bc` | `7385XXXXXXXXXX92` | 参数无效 |
| `ad_info.end_time`（示意） | — | 不传=持续投放 |

`promotion_flow_type` 的合法值只有 **2** 和 **5**：
- 2 → 「推广目标有误，请重新选择」
- 5 → 通过 ✅
- 其余全报「购物广告类型无效」

### 14.4 `start_time` 必须 ≥ 当前时间

模板里的固定值 `2026-09-25 09:02:02` 会报：

```
code=3 msg='开始时间不能早于当前时间。'
```

必须每次动态生成 `YYYY-MM-DD HH:MM:SS`。

## 15. 报错与诊断（这一节最省时间）

### 15.1 🔴 Python 直连看不到真实错误

同一个 payload、同一账号：

| 调用方式 | 响应 |
|---|---|
| `requests` 直连 | `{"code":3,"msg":"出现错误，请重试。"}` ← **无 extra** |
| 浏览器页面内 `fetch` | `{"code":3,"msg":"出现错误，请重试。",
                     "extra":{"i18n_key":"promotion_days_v2_adjusted_roas_bid_not_equal"}}` |

**排障必须走页面环境**，否则永远是「出现错误，请重试。」，无法定位。
这是本轮浪费最多时间的地方。

### 15.2 错误码表

| `i18n_key` | 含义 | 处理 |
|---|---|---|
| `promotion_days_v2_adjusted_roas_bid_not_equal` | ROI 关联字段不等 | 见 §14.2，**必修** |
| `product_roi2_mutex_error` | 商品已被 GMV Max/购物广告占用 | 该商品跳过 |
| `spu_id_not_legal_error` | 商品不具备投放资格 | 该商品跳过 |
| `validate_campaign_name_existed` | 广告名重复 | 换名或跳过 |
| （无 extra，仅「出现错误」） | 直连环境，信息丢失 | 改页面环境重发 |

### 15.3 资格判定：`check` 不可靠，只能用 `create`

`POST /oec_ads/shopping/v1/creation/all_ad_data/check`

```json
→ {"code":0,"data":{"fake_campaign_id":"1","fake_ad_id":"1"}}
```

响应里的 `fake_*` 说明它**只做形状校验**。实测：
- 对 150 个商品（含大量实际不可投的）全部返回 `code:0`
- 删掉 `sdk_create_source`、删掉 `risk_info`、乱填值 —— 依然 `code:0`

**所以 `check` 只能用来验证 payload 结构，不能用来判商品资格。**
判资格只能真发 `create` 看错误码。

### 15.4 ⚠ `create` 有副作用：失败也占位

`create` 在写库前**先占用商品**（`mutex_status` 置 1），失败不回滚。

实测代价：反复试建把 `exclude_mutex=true` 的可用商品从 196 个打到 **0 个**。
占用会分批自动释放，但期间无法建任何广告。

**结论：不要用「逐个试错」的方式判资格。**
先修好 payload（`check` + 首次成功建），再批量。

## 16. 页面 UI 操作路径（自动化时用）

创建页 `https://seller.tiktokshopglobalselling.com/ads-creation/creation?mpa=1`

| 步骤 | 控件 | 要点 |
|---|---|---|
| 1 | 「商品推广」卡片 | 点击后表单才渲染 |
| 2 | 「选定商品」 | ⚠ 必须选它。「所有商品」不支持指定商品（服务端会报） |
| 3 | 「添加商品」→ 勾选 → 「确认」 | 确认后提示「已选择 N 件商品」 |
| 4 | 「总收入（原模式）」 | ⚠ 只有这个模式有「日预算」；新模式「不设日预算」 |
| 5 | 商品 ROI 目标 | 见下方 shadow DOM 说明 |
| 6 | 日预算 | 同上 |
| 7 | 「促销日」开关 | `aria-checked` true→false |
| 8 | 广告计划名称 | 填 `中文简称-主SKU-product_id` |
| 9 | 「发布」 | |

### 16.1 ⚠ 表单控件在嵌套 shadow DOM 里

ROI / 预算不是普通 `<input>`，`querySelectorAll('input')` **找不到**：

```
<X-INPUT-NUMBER-XXXX>            ← 自定义元素（host），有 value
  └─ #shadowRoot
      └─ <X-INPUT-VTWLXT73>
          └─ #shadowRoot
              └─ <INPUT class="input">   ← 真正要改的
```

下钻取真实 input 的方法：

```js
function deep(el, d, out){
  if(!el || d>6) return out;
  if(el.tagName==='INPUT') out.push(el);
  const kids = el.shadowRoot ? [...el.shadowRoot.querySelectorAll('*')] : [...el.children];
  for(const k of kids) deep(k, d+1, out);
  return out;
}
const hosts = [...document.querySelectorAll('*')].filter(e=>/^X-INPUT-NUMBER/.test(e.tagName));
// hosts[0] = 商品 ROI 目标（初值 2.0）；hosts[1] = 日预算（初值 200.00，placeholder「至少 10」）
```

### 16.2 设值的两个坑

| 坑 | 现象 | 解法 |
|---|---|---|
| 直接改 `.value` 无效 | React 受控组件回滚 | 用 `Object.getOwnPropertyDescriptor(proto,'value').set.call(el,v)` + 派发 `input`/`change`（composed:true） |
| 键盘输入会追加 | 2 → "2200.0" | 先真实点击聚焦，再全选删除；或只用上面的 setter 方式 |

页面校验：`目标 ROI 必须介于 0.1 与 20 之间` —— 上限就是 20。

### 16.3 表单会重渲染

加商品、切模式会重建表单，**之前设好的 ROI/预算会被重置回默认值**。
顺序上应最后再设参数，设完立即提交。

## 17. 可跑通的完整方案（`tk01_ads.py`）

```bash
python3 tk01_ads.py products            # 可投商品
python3 tk01_ads.py names               # 打印将用的广告名（干跑）
python3 tk01_ads.py create --spu <id> --dry
python3 tk01_ads.py create --spu <id>   # 单条
python3 tk01_ads.py batch --limit 10    # 批量
```

Python 调用：

```python
from tk01_ads import TK01Ads, PageSession

c = TK01Ads()
todo = {"product_id": "...", "ad_name": "祛疤膏-2818SX-1733XXXXXXXXXX40"}

# ✅ 推荐：走页面环境（能拿到精确错误码）
ps = PageSession(port=CDP_PORT)          # Hub Studio 实例的 CDP 端口
res = ps.create_batch([todo], c)
print(res[0]["kind"], res[0]["campaign_id"])   # OK / MUTEX / NOT_LEGAL / OTHER
ps.close()

# ⚠ 直连（拿不到错误码，仅用于结构验证）
# c.create(todo["product_id"], todo["ad_name"])
```

固定参数：`ROI=20.0`、`ADJUSTED_ROI=18.0`、`BUDGET=200.00`、
`promotion_days_setting.is_enable=false`、`schedule_type=1`（无结束时间）、
`promotion_flow_type=5`。

## 18. 首次成功记录（可回读校验）

```
campaign_id = 1877XXXXXXXXXX89
ad_id       = 1877XXXXXXXXXX25
ad_name     = 祛疤膏-2818SX-1733XXXXXXXXXX40
spu_id      = 1733XXXXXXXXXX40
```

用 `all_ad_data/detail` 回读（`GET`，query 带 `campaign_id`）：

| 字段 | 值 | 对应需求 |
|---|---|---|
| `campaign_info.campaign_name` | `祛疤膏-2818SX-1733XXXXXXXXXX40` | 命名格式 |
| `ad_info.roas_bid` | `20` | ROI=20 |
| `ad_info.budget` | `200` / `budget_mode=0` | 日预算 200 USD |
| `ad_info.schedule_type` | `1` | 无结束时间 |
| `ad_info.promotion_days_setting.is_enable` | `false` | 广告日关闭 |
| `ad_info.product_list` | 长度 1 | 每广告 1 商品 |

## 19. 跨境店 vs 越本土店 差异速查

| | SHOP_LOCAL（越本土） | SHOP_XBORDER（跨境 ExampleShop） |
|---|---|---|
| 主域 | `seller-vn.tiktok.com` | `seller.tiktokshopglobalselling.com` |
| 商品 API | 同域 | 独立域 `api16-normal-sg...`（aid=6556） |
| `org_id` | `7626XXXXXXXXXX75` | `7385XXXXXXXXXX92` |
| ROI 默认 | 14（adjusted 12.6） | 20（adjusted 18.0） |
| 关键字段 | 同 | `adjusted_roas_bid` 必须错开（§14.2） |
| 报错可见性 | — | **必须走页面环境**（§15.1） |

## 20. 后训练优化（第二轮实测）

### 20.1 🔴 官方只读预检：`validate_product_list`

这是本轮最有价值的发现 —— **唯一无副作用的资格判定接口**。

```
POST /oec_ads/shopping/v1/creation/validate_product_list
Query: is_new_product_mode=false&aadvid=&org_id=&oec_seller_id=&locale=zh&language=zh
Body : {"spu_scope":1, "mutex_scene":2, "spu_ids":[...], "sku_ids":[]}
```

响应（一次可传 25 个 SPU）：

```json
{"code":0,"data":{"validation_result":[
  {"spu_id":"1733XXXXXXXXXX40","is_valid":false,"invalid_reason_code":3}
]}}
```

`invalid_reason_code` 实测对应关系：

| code | 含义 | 对应 create 的报错 |
|---|---|---|
| （无 / `is_valid:true`） | 可投 | 可直接发 create |
| `1` | **商品不具备投放资格** | `spu_id_not_legal_error` |
| `3` | **被互斥占用** | `product_roi2_mutex_error` |

`mutex_scene` 只有 **2** 有意义（0/1/3 返回空数组）。

### 20.2 三个判定手段的正确分工

| 手段 | 副作用 | 能测什么 | 不能测什么 |
|---|---|---|---|
| `validate_product_list` | **无** ✅ | 商品资格（可投/不可投/占用） | payload 结构 |
| `all_ad_data/check` | 无 | **payload 结构**（形状） | 商品资格（实测 150 个全 code:0） |
| `all_ad_data/create` | ⚠ **失败也占位** | 一切（真判） | — |

**正确顺序**：先 `validate` 筛商品 → 再 `check` 验 payload → 最后 `create` 提报。
**千万不要**用 create 试错判资格（会把商品打到 mutex）。

### 20.3 实测规模结论

对 153 个「有销量」商品跑一遍 `validate_product_list`：

| 分类 | 数量 | 说明 |
|---|---|---|
| 可投 | 0（当时） | 原本应有 70 个，但被前一轮试建全部占住 |
| `reason=1` 不可投 | **82** | 这些商品**本来就不能投广告** |
| `reason=3` 占用 | 70 | 会自动释放 |

**关键结论**：「有销量」≠「可投广告」。
本店 153 个有销量商品里，**只有 70 个真正具备 GMV Max 投放资格**，
另外 82 个无论怎么改 payload 都建不了（`spu_id_not_legal_error`）。
这正是排名靠前的几个商品（灭蚊灯、胶囊精华等）反复失败的真实原因。

### 20.4 提效流水线

```
① validate_product_list（25 个/次，只读）
      ↓ 只保留 is_valid=true
② all_ad_data/check（验 payload 形状，只读）
      ↓ code:0
③ all_ad_data/create（真提报，逐条记录 campaign_id/ad_id）
      ↓ 失败分类
   MUTEX      → 跳过（占用中）
   NOT_LEGAL  → 跳过（永久不可投）
   NAME_EXIST → 换名重试
   其他       → 记录待查
```

`tk01_ads.PageSession` 已封装：

```python
ps = PageSession(port=CDP_PORT)
keep, dropped = ps.valid_only(todos)      # ① 只读筛选
res = ps.create_batch(keep, c, gap=2.5)   # ③ 批量提报（逐条分类）
```

### 20.5 其它可用的广告管理接口

从 SDK 提取到的 175 个 `/oec_ads/` 接口里，与 GMV Max 运营相关的：

| 接口 | 方法 | 用途 |
|---|---|---|
| `creation/all_ad_data/detail` | GET | **查单条广告**（query 带 `campaign_id`）——已用于回读校验 |
| `creation/all_ad_data/update` | POST | 编辑广告 |
| `creation/specific_field/update` | POST | 改单个字段 |
| `creation/campaign/update_status` | POST | 启停（body: `{campaign_list, operation}`） |
| `creation/campaign/bulk_disable` | POST | 批量关闭（body: `{external_type_list}`） |
| `creation/campaign/name/update` | POST | 批量改名（body: `{name_map}`） |
| `creation/batch_create_gmv_max_ads` | POST | **批量建**（body 同 create 三段 + query `target_oec_seller_id_list`） |
| `creation/get_batch_create_gmv_max_ads_status` | GET | 批量任务进度（query `biz_key`） |
| `creation/batch_apply_gmax_setting` | POST | 批量套用设置 |
| `roi2/query_asset_mutex_info` | POST | 查资产互斥（需 `mutex_adv_id`，非空） |
| `oec/stat/post_campaign_list_v2` | POST | 广告数据列表（body 需 `query_list/action/start_time/end_time/filters/dims`） |
| `oec/stat/post_creative_list_v2` | POST | 素材数据 |
| `oec/stat/post_product_list_v2` | POST | 商品维度数据 |
| `oec/stat/post_video_list` | POST | 视频素材数据 |
| `shop_video/*` | POST/GET | 素材上传（token/list/upload/play_info） |

> `post_campaign_list(_v2)` 直接构造会报 `QueryStatData error`，
> 需要前端那套完整 `query_list`/`dims` 参数，尚未逆向。

## 21. 业务规则：哪些商品能投 GMV Max（经运营确认）

### 21.1 不可投放的商品

**产品下架 / 已删除状态的商品不能投 GMV Max**，会返回 `spu_id_not_legal_error`。
这不是 payload 问题，改任何参数都没用。

### 21.2 ⚠ `product_status` 不能当判据

实测 153 个有销量商品的交叉验证：

| `product_status` | 不可投（reason=1） | 可投/占用（reason=3） |
|---|---|---|
| `2` | 12 | 0 |
| `3` | 14 | 0 |
| **`4`** | **49** | **70** |
| `6` | 7 | 0 |
| 合计 | 82 | 70 |

**`status=4` 同时出现在两类里**（49 个不可投 + 70 个可投）——
说明 `4` 内部还有上架/下架子状态，用 `product_status` 判资格必然误判。

**正确做法：只用 `validate_product_list` 判资格**（见 §20.1）。

### 21.3 双重保障的取数口径

```
① POST /oec_ads/shopping/v1/creation/search_spu   (exclude_mutex=true)
      → 服务端按广告投放条件过滤，只返回可投商品
② POST /oec_ads/shopping/v1/creation/validate_product_list
      → 逐 SPU 权威复核 is_valid / invalid_reason_code
```

两层都过才发 `create`。第 ① 层已经帮我们砍掉了大部分下架/删除商品，
第 ② 层用来复核并发现在途占用。

### 21.4 口径修正（重要）

原先按「商品列表 API 的 `product_sales.total_sales > 0`」筛出 153 个「有销量商品」，
但其中 **只有 70 个具备 GMV Max 投放资格**。

**不能**只看销量就提报 —— 必须叠加 `search_spu` + `validate_product_list`。
否则会有一半以上的请求注定失败（且 `create` 失败还占位）。

## 22. ⚠ 「所有商品」模式会锁死全店（本轮踩的大坑）

### 22.1 事故经过

我在 UI 测试时建了一条广告，它把**全店商品**纳入投放：

```json
{"campaign_info":{"campaign_name":"商品 GMV Max_总收入_ExampleShop_20260926081832"},
 "ad_info":{"product_specific_type": 1,        ← 1 = 所有商品
            "product_list": [],                ← 空，因为不需要逐个列
            "inventory_flow_type": 1}}
```

后果：**全店 196 个商品全部变成 `mutex_status=1`**，
`search_spu(exclude_mutex=true)` 返回 **0 个**，任何新广告都建不了，
`validate_product_list` 全部返回 `invalid_reason_code=3`。

我当时误以为是「试建占位没释放」，等了 45 分钟毫无变化 —— 实际是这条广告锁着。

**关闭它后立刻恢复**：可用商品数 `0 → 196`。

### 22.2 关闭广告的接口

```
POST /oec_ads/shopping/v1/creation/campaign/update_status
Query: aadvid=&oec_seller_id=&locale=zh&language=zh
Body : {"campaign_list": [1877XXXXXXXXXX93], "operation": 2}
→ {"code":0,"msg":"success","data":{"status":"success"}}
```

⚠ **两个坑**：

1. `campaign_list` 必须是**数字 ID 的数组**。
   传对象数组（`[{"campaign_id":...,"ad_id":...}]`）会报：
   ```
   strconv.ParseInt: parsing "{\"campaign_id\":...}": invalid syntax
   ```
2. `operation: 2` = 关闭。
   传字符串 `"disable"` / `"off"` 或 `0/3` 都报「参数无效」。

关闭后 `campaign_info.opt_status` 从 `0` → `1`。

### 22.3 上线前必做的异常检测（`tk01_scan.py`）

建广告前/后都应该扫一遍，确认没有「全店模式」广告：

```bash
python3 tk01_scan.py --avail                    # 看可用商品数（突然变 0 就是被全店锁了）
python3 tk01_scan.py --check <campaign_id>      # 查单条
python3 tk01_scan.py --scan                     # 扫全部已知广告，列出高危
python3 tk01_scan.py --disable <campaign_id>    # 关闭（交互确认）
```

高危判据（读 `all_ad_data/detail`，纯只读）：

| 字段 | 高危值 | 含义 |
|---|---|---|
| `ad_info.product_specific_type` | **1** | 「所有商品」模式 ★ |
| `ad_info.product_list` | 空数组 | 印证全店模式 |
| `ad_info.inventory_flow_type` | `1` | 全店库存流 |

正常广告应该是 `product_specific_type = 3`（选定商品）+ `product_list` 长度 = 1。

> 实现细节坑：`detail` 查询依赖页面上下文 —— 页面若停在
> `/ads-creation/dashboard`，同一 campaign_id 查询会返回 `code:3`；
> 必须导航到 `/ads-creation/creation` 并等渲染完成。

## 23. 批量提报的三道防线（最终方案）

```
防线①  商品池过滤
   search_spu(exclude_mutex=true)     ← 服务端按投放条件过滤
防线②  只读预检（无副作用）
   validate_product_list              ← 判定 is_valid / invalid_reason_code
        reason=1 (NOT_LEGAL) → 跳过：下架/已删除，永久不可投
        reason=3 (MUTEX)     → 跳过：被占用（可能是全店模式广告）
防线③  提报 + 分类重试
   create → product_roi2_mutex_error  → 跳过
            spu_id_not_legal_error    → 跳过
            spu_id_access_error       → 记录，可重试
            validate_campaign_name_existed → 改名重试
```

### 23.1 页面健康检查（必须）

```python
def ensure_page(self):
    """提报过程中页面可能被导航走（实测跳到 /ads-creation/dashboard），
    之后 Runtime.evaluate 报 'Execution context was destroyed.'，整批中断。"""
```

实测中断点就在第 15/69 条 → 加上 `ensure_page()` 后连续跑完 49 条无中断。

### 23.2 本轮实测成绩

| 指标 | 数值 |
|---|---|
| 清单 | 153 条（有销量商品） |
| 剔除 NOT_LEGAL（下架/删除） | 82 |
| 剔除 MUTEX（占用） | 6 |
| 实际提报 | 49 |
| 成功 | **48** |
| 失败 | 1（`spu_id_access_error`，可重试） |
| 全量回读校验 | **63/63 参数完全合规** |
| 单条耗时 | 约 3.4 秒 |

### 23.3 参数合规判据（回读校验用）

| 字段 | 期望值 |
|---|---|
| `campaign_name` | `中文简称-主SKU-product_id` |
| `roas_bid` | `20` |
| `budget` | `200`（`budget_mode=0`） |
| `schedule_type` | `1`（持续投放，无结束时间） |
| `promotion_days_setting.is_enable` | `false` |
| `product_specific_type` | **`3`**（选定商品，绝不能是 1） |
| `product_list` 长度 | `1` |
| `opt_status` | `0`（在投） |

## 24. 待办与注意事项

- 本轮创建的 63 条广告是**测试产物**，清单见 `notes/TK01_AD_LIST.md`（含 campaign_id / ad_id）
- 删除时优先处理 `product_specific_type=1` 的那条（已关闭，但确认一下）
- 82 个 `NOT_LEGAL` 商品若之后重新上架，可重新纳入提报（重跑 `tk01_run.py` 即可）
- `post_campaign_list(_v2)` 的完整参数（`query_list`/`dims`/`filters`）尚未逆向，
  广告数据看板类接口留待后续

---

# 第三部分：成功经验总汇（可复制照做）

> 本节把 `2026-09-26` 完整跑通 **63 条** GMV Max 广告的全部经验收在一处。
> 完整可提交 payload 存档：`notes/tk01_success_payload.json`（70 个叶子字段）。

## 25. 从零到批量提报：完整 SOP

### 25.1 前置条件

| 项 | 要求 |
|---|---|
| 浏览器 | Hub Studio 环境已启动，CDP 端口可访问（SHOP_XBORDER = `CDP_PORT`） |
| 登录态 | 卖家中心已登录（`seller.tiktokshopglobalselling.com`） |
| 页面 | **必须停在** `/ads-creation/creation?mpa=1` 并加载完成 |
| 会话 | 无需导出 cookie（页面环境直接发请求） |

### 25.2 六个步骤

```bash
# ① 拉可投商品（服务端已按投放条件过滤）
POST /oec_ads/shopping/v1/creation/search_spu
     ?exclude_mutex=true&org_id=7385XXXXXXXXXX92&aadvid=7689XXXXXXXXXX09
     &oec_seller_id=7494XXXXXXXXXX00&locale=zh&language=zh
Body {"page_info":{"page_index":1,"page_size":50},
      "sort_param":{"sort_field":9,"sort_order":0},
      "spu_scope":1,"title":"","spu_ids":[],"sku_ids":[],"mutex_scene":2}

# ② 只读预检（无副作用，25 个/批）
POST /oec_ads/shopping/v1/creation/validate_product_list
     ?is_new_product_mode=false&org_id=...&aadvid=...&oec_seller_id=...
Body {"spu_scope":1,"mutex_scene":2,"spu_ids":[...],"sku_ids":[]}
→ 只保留 is_valid=true

# ③ 环境自检（建之前必做，防全店模式锁死）
python3 tk01_scan.py --avail          # 可用商品数；突然为 0 说明被锁

# ④ 构造 payload（参数见 §26）
# ⑤ 提报
python3 tk01_run.py --go --batch 5 --gap 3.0

# ⑥ 回读校验
按 §23.3 的 8 项判据逐条 all_ad_data/detail 核对
```

### 25.3 建议参数

| 参数 | 值 | 理由 |
|---|---|---|
| 每批条数 | 5 | 单次 `Runtime.evaluate` 的耗时可控，失败影响面小 |
| 条间隔 | 3.0s | 实测 2.5–3.5s 无触发风控 |
| 批间隔 | 5.0s | 给页面喘息，降低被导航走的概率 |
| 单条耗时 | ≈3.4s | 49 条约 3 分钟 |

## 26. 成功 payload 的 70 个字段（可复制）

### 26.1 顶层三段

```json
{"campaign_info": {...}, "ad_info": {...}, "risk_info": {...}}
```

> SDK 源码里 `CreateAllAdData` 还取第 4 个字段 `sdk_create_source`，
> 但**实测缺失也能成功**，可不传。

### 26.2 `campaign_info`（7 字段，全部恒定）

| 字段 | 值 |
|---|---|
| `campaign_id` | `""`（创建时留空） |
| `campaign_name` | **变化项**：`中文简称-主SKU-product_id` |
| `budget_mode` | `0` |
| `budget` | `"200.00"` |
| `shop_automation_type` | `2` |
| `shop_image_aigc_mode` | `1` |
| `gmv_roi_mode` | `0` |

### 26.3 `ad_info` 关键字段（★ = 最容易错）

| 字段 | 值 | 备注 |
|---|---|---|
| `name` | 同 `campaign_name` | — |
| `campaign_id` / `ad_id` | `""` | 留空 |
| `roas_bid` | `"20.0"` | ★ 字符串 |
| `budget` | `"200.00"` / `budget_mode=0` | ★ 两处都要 |
| **`promotion_days_setting.adjusted_roas_bid`** | **`"18.0"`** | ★★ **绝不能等于 roas_bid** |
| `promotion_days_setting.benchmark_roas_bid` | `20` | ★ 数字（非字符串） |
| `promotion_days_setting.is_enable` | `false` | ★ 广告日关闭 |
| **`product_specific_type`** | **`3`** | ★★ **绝不能是 1（那是全店模式）** |
| `product_list` | `[{"spu_id":"..."}]` | ★ 长度恒为 1 |
| `schedule_type` | `1` | 持续投放、无结束时间 |
| `start_time` | `"YYYY-MM-DD HH:MM:SS"` | ★ **必须 ≥ 当前时间** |
| `shop_id` | `7494XXXXXXXXXX00` | — |
| `shop_authorized_bc` | `7385XXXXXXXXXX92` | — |
| `custom_tz_id` | `"7473XXXXXXXXXX44"` | ★ 别改成 `420`（会报时区无效） |
| `custom_tz_type` | `2` | — |
| `country` | `"VN"` | — |
| `promotion_flow_type` | `5` | ★ 只有 2/5 合法，5 才对 |
| `optimize_goal` | `111` | ★ 只有 100/111 合法 |
| `deep_bid_type` | `108` | ★ 唯一合法值 |
| `pricing` | `9` | ★ 改 1 报「计费点仅支持oCPM」 |
| `external_type` | `304` | — |
| `external_action` | `96` | — |
| `shop_type` | `1` | — |
| `inventory_flow_type` | `0` / `inventory_flow=[3000,9000]` | 选定商品模式用 0 |
| `shopping_inventory_type` | `1` | — |
| `flow_control_mode` | `1` | — |
| `compensation_activity_type` | `3` | — |
| `gmax_budget_adjust_setting` | `{strategy:2, auto_budget_switch:false, promotion_day_adjust_config:{adjust_ratio:0.5,max_daily_adjust_times:10}}` | — |
| `identity_list` / `custom_anchor_videos` / `pre_item_list` | `[]` | — |

### 26.4 `risk_info`

```json
{"cookie_enabled": true, "screen_width": 1512, "screen_height": 982,
 "browser_language": "vi-VN", "browser_platform": "MacIntel", "browser_name": "Mozilla",
 "browser_version": "…Chrome/…", "browser_online": true, "timezone_name": "Asia/Bangkok"}
```

服务端不校验其真实性（实测 screen 800×600 也能过）。

## 27. 排查问题的最快路径（按顺序）

遇到 create 失败，按这个顺序查，不要跳步：

```
1. 错误码是什么？
   └ 只有「出现错误，请重试。」无 extra → 你在用 Python 直连
     → 改用页面环境（PageSession）才能拿到 i18n_key
2. 有 i18n_key 了，对照 §15.2 错误码表
   ├ promotion_days_v2_adjusted_roas_bid_not_equal → 改 adjusted_roas_bid（§14.2）
   ├ product_roi2_mutex_error  → 商品占用
   │    └ 立刻查 tk01_scan.py --avail：可用数=0 就是被「全店模式」广告锁了（§22）
   ├ spu_id_not_legal_error    → 商品下架/已删除，永久不可投，跳过（§21）
   ├ spu_id_access_error       → 商品访问权限，可稍后重试
   └ validate_campaign_name_existed → 广告名重复
3. 都不是？先跑 validate_product_list 确认商品资格，再跑 check 确认 payload 结构
4. 还不行 → 逐字段做「删掉看是否报字段级错误」的差分（§14.3 用的方法）
```

## 28. 一句话记住的要点

1. **`adjusted_roas_bid` 必须 = `roas_bid × 0.9`**（ROI 20 → 18.0），不能相等
2. **`product_specific_type` 必须是 3**，用 1 会把全店商品锁死
3. **排障必须走页面环境**，Python 直连拿不到 `i18n_key`
4. **判资格只用 `validate_product_list`**，别用 `product_status`，更别用 create 试错
5. **提报前先 `--avail` 看可用数**，为 0 说明有「全店模式」广告在锁
6. **`start_time` 每次动态生成**，模板里的固定值会过期
7. **广告接口走 `seller.tiktokshopglobalselling.com`**，不要走 `api16` 域
