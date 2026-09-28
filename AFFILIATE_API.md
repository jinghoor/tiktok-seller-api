# 达人联盟（Affiliate）API 全量接口手册

> **来源**：从联盟中心**自己的前端 bundle** 抽取全部路径字面量，再与本地已验证集合交叉比对。
> 数据源 `notes/aff_js/`（46 个 bundle / 33 MB）、`notes/api_inventory/enriched.json`。

| 标记 | 含义 |
|---|---|
| ✅ | **实测通过** —— 本会话或主文档有 `code=0` 的直接证据，请求参数已知 |
| ◐ | 已接入 `tk01_affiliate.py` 等客户端，报文格式已知，但未单独跑过验证 |
| ○ | 前端 bundle 中存在，尚未接入 |

**共 552 个接口** — ✅ 33 / ◐ 3 / ○ 516（✅ 是**在这 564 个之内**的统计；
我们累计实测通过 42 个，多出的几个不在这个 bundle 列表里，见附 A）。
能定出 HTTP 方法的 337 个（**POST 307** / GET 30）。

> HTTP 方法的取法：窗口 = [本路径字面量结束, 下一个字面量开始)，只在这一段里找 `method:"…"`；
> 实测过的 42 个用实测方法覆盖推测值，其余取不到记 `?`。
> `/oec/` 族几乎全是 POST —— 这是它和旧 `/api/v1/affiliate/*` 族最大的手感差别。

---

## 0. 总览

### 0.1 域

| 用途 | 域 | 说明 |
|---|---|---|
| 联盟中心（主） | `affiliate.tiktokshopglobalselling.com` | **两套路径族都在这个域上** |
| 站内 IM（私有 protobuf） | `oec-im-tt-sg.tiktokglobalshopv.com/` **动态** | 由 `/api/v1/im/shop_creator/shop/user/token/get` 返回，见主文档 §40 |
| MCN / Partner | `api-partner-va.tiktokshop.com` | `partner_info` 等 |

### 0.2 ★ 两套路径族（行为完全不同，别混）

| 路径族 | 网关 | 实测特征 |
|---|---|---|
| `/api/v1/affiliate/*` | 旧网关 | 参数直给、多为 `GET`；响应里 `region` 字段正常 |
| `/api/v1/oec/affiliate/*` | 新网关 | 多为 `POST`；**缺 `oec_region` + 浏览器指纹块一律 `98001004`，且 `region:""`** |

`98001004` 是双关码：既是**参数错**也是**签名缺**。判据就是看响应里的 `region` 是不是空串。

### 0.3 `/oec/` 族请求必备 query

```
user_language, aid=6556, app_name=i18n_ecom_alliance, device_id,
oec_region=VN, oec_seller_id=<seller_id>,
fp, device_platform=web, screen_width, screen_height, browser_*, timezone_name
```

17 个业务参数 + 4 个签名参数（`msToken` / `X-Bogus` / `X-Gnarly` / `X-Tts-Oec-Bsid`）。
**签名只能由页面自己的 `byted_acrawler.frontierSign` 产生** —— 见主文档 §36 / §37。

### 0.4 编码

| 编码 | 用途 | 端点 |
|---|---|---|
| JSON | 绝大多数 | `Content-Type: application/json; charset=utf-8` |
| **protobuf** | 站内 IM | `Content-Type: application/x-protobuf`，见主文档 §40 |
| multipart | 图片 / 主题文件上传 | `affiliate/lux/image/*`、`affiliate/lux/screenshot` |

### 0.5 分页字段名按族不同（踩过的）

| 接口族 | 分页字段 |
|---|---|
| 定向计划 `invitation_group/search` | `cur_page` / `page_size` |
| 达人广场 `marketplace/find` | `next_pagination.search_key`（**服务端签名游标，不能自造**） |
| 排行榜 `cmp/creator/rank/list/get` | `rank_list_meta` 块 |
| 商品机会（非联盟） | `page_number` / `page_size` |

---

## 1. 账号 / 网关 / 配置 / 平台设置

*37 个 · ✅ 5*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `GET` | `/api/v1/affiliate/account/info` | `account_info` |
| ✅ | `GET` | `/api/v1/affiliate/account/info_v2` | `account_info_v2` |
| ✅ | `GET` | `/api/v1/affiliate/config` | `config` |
| ✅ | `GET` | `/api/v1/affiliate/menu` | `menu` |
| ✅ | `GET` | `/api/v1/affiliate/resource/list/get` | `resource_list` |
| ○ | `?` | `/api/v1/affiliate/account/all_sellers/get` |  |
| ○ | `?` | `/api/v1/affiliate/approve/check` |  |
| ○ | `POST` | `/api/v1/affiliate/creator/search` |  |
| ○ | `?` | `/api/v1/affiliate/has_agent` |  |
| ○ | `?` | `/api/v1/affiliate/log_out_agent` |  |
| ○ | `?` | `/api/v1/affiliate/name_list/get` |  |
| ○ | `POST` | `/api/v1/affiliate/new_request/count` |  |
| ○ | `?` | `/api/v1/affiliate/platform` |  |
| ○ | `?` | `/api/v1/affiliate/platform/account/root` |  |
| ○ | `?` | `/api/v1/affiliate/platform/account/shop` |  |
| ○ | `?` | `/api/v1/affiliate/platform/homepage` |  |
| ○ | `?` | `/api/v1/affiliate/platform/homepage/announcements` |  |
| ○ | `?` | `/api/v1/affiliate/platform/personalization-settings` |  |
| ○ | `POST` | `/api/v1/affiliate/request/search` |  |
| ○ | `POST` | `/api/v1/affiliate/request_status/update` |  |
| ○ | `POST` | `/api/v1/affiliate/resource/action/report` |  |
| ○ | `POST` | `/api/v1/affiliate/shop_setting/change` |  |
| ○ | `POST` | `/api/v1/affiliate/shop_setting/get` |  |
| ○ | `?` | `/api/v1/affiliate/violation/shop/list` |  |
| ○ | `?` | `/api/v1/affiliate/violation/unread/check` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/search/platform_quest` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/recommend_invitation/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/recommend_product/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/sample_info/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/diagnosis/recommendation/list` |  |
| ○ | `?` | `/api/v1/oec/affiliate/scopemetas` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/dismiss` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/search/feedback/submit` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/search/initial_questions/get` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/shop/info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/shop/settings/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/shop/settings/update` |  |

## 2. 首页 / 平台运营位 / 公告 / 引导

*21 个 · ✅ 0*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ○ | `?` | `/api/v1/affiliate/announcement/detail` |  |
| ○ | `?` | `/api/v1/affiliate/announcement/list` |  |
| ○ | `POST` | `/api/v1/affiliate/announcement/read` |  |
| ○ | `?` | `/api/v1/affiliate/backend/app/account/info` |  |
| ○ | `?` | `/api/v1/affiliate/backend/category/get` |  |
| ○ | `?` | `/api/v1/affiliate/backend/homepage/external_link_program/get` |  |
| ○ | `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/mupdate` |  |
| ○ | `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/types/get` |  |
| ○ | `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/update` |  |
| ○ | `?` | `/api/v1/affiliate/backend/homepage/information_card/get` |  |
| ○ | `?` | `/api/v1/affiliate/backend/homepage/todo_dashboard/get` |  |
| ○ | `POST` | `/api/v1/affiliate/backend/homepage/todo_list/confirm` |  |
| ○ | `?` | `/api/v1/affiliate/backend/homepage/todo_list/get` |  |
| ○ | `?` | `/api/v1/affiliate/banner` |  |
| ○ | `?` | `/api/v1/affiliate/errorpage` |  |
| ○ | `?` | `/api/v1/affiliate/guide/articles` |  |
| ○ | `?` | `/api/v1/affiliate/homepage` |  |
| ○ | `?` | `/api/v1/affiliate/promotion_position` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/guidance_page/creator_fans_portrait` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/guidance_page/creator_recommendation` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/guidance_page/creator_stats` |  |

## 3. 达人广场 / 达人搜索 / 达人画像

*31 个 · ✅ 4*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/affiliate/lux/creator/auth_profiles` |  |
| ✅ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/find` | `marketplace_find` |
| ✅ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/option` | `marketplace_option` |
| ✅ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/profile` | `marketplace_profile` |
| ○ | `?` | `/api/v1/affiliate/creator/detail` |  |
| ○ | `?` | `/api/v1/affiliate/creator/rankings` |  |
| ○ | `?` | `/api/v1/affiliate/creator/vertical-list` |  |
| ○ | `?` | `/api/v1/affiliate/creator_application/list` |  |
| ○ | `?` | `/api/v1/affiliate/creator_data/filter_option/get` |  |
| ○ | `?` | `/api/v1/affiliate/creator_marketplace/filled/get` |  |
| ○ | `?` | `/api/v1/affiliate/creator_marketplace/get` |  |
| ○ | `POST` | `/api/v1/affiliate/creator_marketplace/mget` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/creator/profile` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/config` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/ai/find` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/content/stats` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/creator/profile/stats` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/follower/stats` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/invitation_recommend_creator` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/mcn/info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/recommendation` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/search` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/search_new` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/arrival` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/category/creator` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/category/list` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/settings/contact` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/settings/contact/update` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/settings/preference` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/settings/preference/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/vertical/category/list` |  |

## 4. 定向计划 / 达人邀约（核心业务）

*160 个 · ✅ 13*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `GET` | `/api/v1/affiliate/lux/invitation/available_list` | `avail_invitation` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/conflict_check` | `group_conflict` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/conflict_check/resolve` | `group_conflict_fix` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/create` | `group_create` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creators_add` | `group_creators_add` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/detail` | `group_detail` |
| ✅ | `GET` | `/api/v1/oec/affiliate/seller/invitation_group/general/config` | `group_general_cfg` |
| ✅ | `GET` | `/api/v1/oec/affiliate/seller/invitation_group/invitation/limit` | `invitation_limit` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/product_creator_relation` | `product_creator_rel` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search` | `group_search` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/sensitive_text_check` | `group_text_check` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/terminate` | `group_terminate` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/update` | `group_update` |
| ◐ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/creator` | `group_search_creator` |
| ○ | `?` | `/api/v1/affiliate/campaign/contact_info/get` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/create` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/detail/get` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/edit` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/modify_sample_quota` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/partner/search` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/partners/list` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/product/approve` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/product/cancel` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/product_performance/get` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/products/list` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/register` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/register_contact_info` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/registered_products/edit` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/registered_products/get` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/search` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/seller/permission/get` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/seller/product/list` |  |
| ○ | `?` | `/api/v1/affiliate/campaign/single_product_performance/get` |  |
| ○ | `POST` | `/api/v1/affiliate/campaign/update/status` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/auction-stock` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/open-collaboration` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/open-collaboration/bulk-edit` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/open-collaboration/creator-applications` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/open-collaboration/growth-products` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-create` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-description` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-detail` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-edit` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/create` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/detail` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/edit` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/create` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/detail` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/send-result` |  |
| ○ | `?` | `/api/v1/affiliate/collaboration/target-invitation/select` |  |
| ○ | `?` | `/api/v1/affiliate/creator` |  |
| ○ | `?` | `/api/v1/affiliate/lux/invitation/c_detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/invitation/creator/list` |  |
| ○ | `?` | `/api/v1/affiliate/lux/invitation/detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/creator/list` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/target_plan/c_detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/target_plan/detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/target_plan/list` |  |
| ○ | `POST` | `/api/v1/affiliate/meta_plan/search` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/bind` |  |
| ○ | `?` | `/api/v1/affiliate/plan/check_exist` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/check_if_has_plans_by_seller_id` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/creator_count` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/gen_share_url` |  |
| ○ | `?` | `/api/v1/affiliate/plan/list` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/mget_seller_landing_task_extra` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/mset_seller_landing_task_extra` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/recommend_commissions/list` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/search` |  |
| ○ | `POST` | `/api/v1/affiliate/plan/sync` |  |
| ○ | `?` | `/api/v1/affiliate/plan_detail/list` |  |
| ○ | `POST` | `/api/v1/affiliate/plan_status/update` |  |
| ○ | `?` | `/api/v1/affiliate/seller/effective_time/get` |  |
| ○ | `?` | `/api/v1/affiliate/seller/invitation/contact_info/get` |  |
| ○ | `POST` | `/api/v1/affiliate/seller/invitation/contact_info/update` |  |
| ○ | `POST` | `/api/v1/affiliate/shop_plan/create` |  |
| ○ | `?` | `/api/v1/affiliate/shop_plan/get` |  |
| ○ | `POST` | `/api/v1/affiliate/shop_plan/update` |  |
| ○ | `?` | `/api/v1/affiliate/sub_plan/list` |  |
| ○ | `?` | `/api/v1/oec/affiliate/campaign/config/options/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/card/message` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/entrance/check` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/im/get/token` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/last_new_message` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/options` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/permission` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/im/product/info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/product/pack` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/im/translate/message` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/accept` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/audit/result` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/auth/banner` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/auth/banner/cancel` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/brand/video/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/campaign/action` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/fe/resource` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/filter` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/campaign/product_search` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/collection/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/confirm_page/confirm` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/confirm_page/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/decline` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/decline/feedback` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/detail` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/entrance` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/filter/config` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/new/clear` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/new_feature_remind` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/product/search` |  |
| ○ | `?` | `/api/v1/oec/affiliate/creator/invitation/products` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/reactive` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/recommend` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/search` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/unread/clear` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/creator/invitation/unread/count` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/detail` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/approve` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/edit` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/post` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video_list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/pay` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/pay/status` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation/products_info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/create` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/detail` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/update` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/banner` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/create` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/creator_set` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/criteria` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/product_set` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/shop_validate` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/commission/history` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/count` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator/relevancy/prediction` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator_promotion_detail` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator_video_list` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/invitation_group/detail/creators` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/latest_basic_info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/product/intra_check` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/promotion/configs` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/rate_limit_info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/re_update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/recommend/cache` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/invitation` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/product` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/share/short_url` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/invitation_group/vertical/conflict` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/previous_invitation/use_status` |  |
| ○ | `POST` | `/api/v2/affiliate/shop_plan/create` |  |
| ○ | `?` | `/api/v2/affiliate/shop_plan/get` |  |
| ○ | `POST` | `/api/v2/affiliate/shop_plan/quit` |  |
| ○ | `POST` | `/api/v2/affiliate/shop_plan/update` |  |
| ○ | `POST` | `/api/v2/affiliate/target_plan/create` |  |
| ○ | `POST` | `/api/v2/affiliate/target_plan/product_selection/guide_new_seller/list` |  |
| ○ | `POST` | `/api/v2/affiliate/target_plan/update` |  |

## 5. 公开合作 / 竞价库存

*39 个 · ✅ 1*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/affiliate/open_collaboration/opt_in/card/get` | `opt_in_card` |
| ○ | `POST` | `/api/v1/affiliate/auction_stock/products/list` |  |
| ○ | `?` | `/api/v1/affiliate/auction_stock/summary` |  |
| ○ | `?` | `/api/v1/affiliate/open_collaboration/ad/account_info/get` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/ad_commission/suggest_commission/get` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/affected_promotion_info/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/auction_commission/detail` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/authorized_ad_video/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/commission_history/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/commission_version/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/creator_application/batch_review` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/creator_application/search` |  |
| ○ | `?` | `/api/v1/affiliate/open_collaboration/product_creator_relation/detail` |  |
| ○ | `?` | `/api/v1/affiliate/open_collaboration/product_creator_relation/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/product_creator_relation/terminate` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/ad_commission/upsert` |  |
| ○ | `?` | `/api/v1/affiliate/open_collaboration/promote_products/async_task/get` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/async_task/submit` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/auction_commission/upsert` |  |
| ○ | `?` | `/api/v1/affiliate/open_collaboration/promote_products/count` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/gmv_max/suggest` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/gmv_max/upsert` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/list` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/terminate` |  |
| ○ | `POST` | `/api/v1/affiliate/open_collaboration/promote_products/upsert` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/batch_create` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/create` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/delete` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/excel_check` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/list_search` |  |
| ○ | `?` | `/api/v1/affiliate/open_plan/allowlist/performance` |  |
| ○ | `?` | `/api/v1/affiliate/open_plan/allowlist/pre_create` |  |
| ○ | `POST` | `/api/v1/affiliate/open_plan/allowlist/pre_create_v2` |  |
| ○ | `?` | `/api/v1/affiliate/open_plan/allowlist/pre_delete` |  |
| ○ | `POST` | `/api/v2/affiliate/open_plan/create` |  |
| ○ | `POST` | `/api/v2/affiliate/open_plan/delete` |  |
| ○ | `POST` | `/api/v2/affiliate/open_plan/list` |  |
| ○ | `POST` | `/api/v2/affiliate/open_plan/product_selection/list` |  |
| ○ | `POST` | `/api/v2/affiliate/open_plan/update` |  |

## 6. 样品寄样

*57 个 · ✅ 1*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/affiliate/sample/group/list` | `sample_group_list` |
| ○ | `POST` | `/api/v1/affiliate/lux/sample/apply` |  |
| ○ | `?` | `/api/v1/affiliate/lux/sample/c_info` |  |
| ○ | `?` | `/api/v1/affiliate/lux/sample/info` |  |
| ○ | `POST` | `/api/v1/affiliate/opt_in/sample/check` |  |
| ○ | `?` | `/api/v1/affiliate/sample` |  |
| ○ | `?` | `/api/v1/affiliate/sample/apply/list` |  |
| ○ | `?` | `/api/v1/affiliate/sample/approved_fail/count` |  |
| ○ | `?` | `/api/v1/affiliate/sample/approved_fail/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/auto_placement_rule/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/auto_placement_rule/save` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/groi/join` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/groi/perf/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/groi/perf/summary` |  |
| ○ | `?` | `/api/v1/affiliate/sample/groi/seller_info/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/group/action` |  |
| ○ | `?` | `/api/v1/affiliate/sample/group/label_menu` |  |
| ○ | `?` | `/api/v1/affiliate/sample/group_order/config` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/group_order/submit` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/hint/search` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/im_fulfillment_reminder/list` |  |
| ○ | `?` | `/api/v1/affiliate/sample/notice` |  |
| ○ | `?` | `/api/v1/affiliate/sample/performance` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/placement_rule/get` |  |
| ○ | `?` | `/api/v1/affiliate/sample/placement_rule/open_plan_hosting/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/placement_rule/save` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/recommendation/approval/banner` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/recommendation/approval/inference/trigger` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/recommendation/approval/preference/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/recommendation/approval/result` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/refundable/apply/list` |  |
| ○ | `?` | `/api/v1/affiliate/sample/refundable/tab/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/review/delete` |  |
| ○ | `?` | `/api/v1/affiliate/sample/review/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/review/save` |  |
| ○ | `?` | `/api/v1/affiliate/sample/rule/async_task/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/rule/async_task/submit` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/rule/del` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/rule/mget` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/rule/save` |  |
| ○ | `?` | `/api/v1/affiliate/sample/sample-request` |  |
| ○ | `?` | `/api/v1/affiliate/sample/sample-settings` |  |
| ○ | `?` | `/api/v1/affiliate/sample/seller_setting/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/seller_setting/save` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/settings/product/batch_save` |  |
| ○ | `?` | `/api/v1/affiliate/sample/settings/product/config` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/settings/product/detail` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/settings/product/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/settings/product/mget` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/settings/product/save` |  |
| ○ | `?` | `/api/v1/affiliate/sample/shipment/info` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/sku_config/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/support4pl/status` |  |
| ○ | `?` | `/api/v1/affiliate/sample/tab/list` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/tag/delete` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/ui/version/get` |  |
| ○ | `POST` | `/api/v1/affiliate/sample/ui/version/set` |  |

## 7. 达人管理 / CRM / 关系 / 名单

*45 个 · ✅ 2*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `GET` | `/api/v1/oec/affiliate/crm/creator/upper_limit/get` | `crm_upper_limit` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/wish_list/search/creator` | `wishlist_search` |
| ◐ | `POST` | `/api/v1/oec/affiliate/crm/im_messages/batch_send` | `crm_batch_send` |
| ○ | `?` | `/api/v1/affiliate/assets` |  |
| ○ | `?` | `/api/v1/affiliate/assets/creator-management` |  |
| ○ | `?` | `/api/v1/affiliate/assets/creator-management/bulk-im` |  |
| ○ | `?` | `/api/v1/affiliate/assets/creator/bulk-im` |  |
| ○ | `?` | `/api/v1/affiliate/assets/quota/overview` |  |
| ○ | `?` | `/api/v1/affiliate/assets/video-analysis` |  |
| ○ | `POST` | `/api/v1/affiliate/relation/operate` |  |
| ○ | `POST` | `/api/v1/affiliate/relation/search` |  |
| ○ | `POST` | `/api/v1/affiliate/review/creator/metrics` |  |
| ○ | `POST` | `/api/v1/affiliate/review/creator/reviews` |  |
| ○ | `?` | `/api/v1/affiliate/seller/contact_info/get` |  |
| ○ | `POST` | `/api/v1/affiliate/seller/contact_info/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/block_creator/create` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/block_creator/delete` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/block_creator/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/block_creator/query` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/cmp/search` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/batch_create` |  |
| ○ | `?` | `/api/v1/oec/affiliate/crm/creator/batch_task/result/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/batch_task/submit` |  |
| ○ | `?` | `/api/v1/oec/affiliate/crm/creator/block/setting/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/block/setting/update` |  |
| ○ | `?` | `/api/v1/oec/affiliate/crm/creator/content/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/create` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/delete` |  |
| ○ | `?` | `/api/v1/oec/affiliate/crm/creator/detail_info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/import` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/import_check` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/product/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/tag/bind` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/creator/target_collaboration/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/material/check` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/tag/create` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/tag/delete` |  |
| ○ | `?` | `/api/v1/oec/affiliate/crm/tag/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm/tag/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/crm_toc/block_creator/query` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/quota/connected_creators` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/quota/connection/check` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/quota/info` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/wish_list/update/creator` |  |

## 8. 消息 / 站内 IM / 通知

*32 个 · ✅ 1*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `GET` | `/api/v1/oec/affiliate/seller/im/get/token` | `im_token` |
| ◐ | `POST` | `/api/v1/affiliate/notification/im/relation/update` | `tk01_im` |
| ○ | `GET` | `/api/v1/affiliate/lux/notification/im/latest` |  |
| ○ | `GET` | `/api/v1/affiliate/lux/notification/im/message` |  |
| ○ | `GET` | `/api/v1/affiliate/lux/notification/im/unread` |  |
| ○ | `GET` | `/api/v1/affiliate/lux/notification/im/unread_count` |  |
| ○ | `?` | `/api/v1/affiliate/notification/classify/list` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/config` |  |
| ○ | `?` | `/api/v1/affiliate/notification/ec_permission` |  |
| ○ | `?` | `/api/v1/affiliate/notification/get_latest_creator_notification` |  |
| ○ | `?` | `/api/v1/affiliate/notification/group/schemas` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/im/conversation/update` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/im/conversation/update_tag` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/im/entrance_check` |  |
| ○ | `?` | `/api/v1/affiliate/notification/im/list` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/im/permission` |  |
| ○ | `?` | `/api/v1/affiliate/notification/im/seller_category` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/im/shop_quota` |  |
| ○ | `?` | `/api/v1/affiliate/notification/list` |  |
| ○ | `?` | `/api/v1/affiliate/notification/list_schemas` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/mark_as_clicked` |  |
| ○ | `POST` | `/api/v1/affiliate/notification/mark_as_read` |  |
| ○ | `?` | `/api/v1/affiliate/notification/unread_count` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/card/message` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/im/product/info` |  |
| ○ | `?` | `/api/v1/oec/affiliate/seller/im/product/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/remind/can` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/remind/send` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/settings/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/settings/update` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/template/message` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/im/translate/message` |  |

## 9. 商品 / 选品 / 佣金

*16 个 · ✅ 1*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/affiliate/product_selection/list` | `product_selection` |
| ○ | `POST` | `/api/v1/affiliate/commission_unique/check` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/product/c_detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/product/detail` |  |
| ○ | `?` | `/api/v1/affiliate/lux/plan/product/list` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/product/c_detail_list` |  |
| ○ | `?` | `/api/v1/affiliate/lux/product/category/children` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/product/category/childrenv2` |  |
| ○ | `?` | `/api/v1/affiliate/product/list` |  |
| ○ | `POST` | `/api/v1/affiliate/product/search` |  |
| ○ | `?` | `/api/v1/affiliate/product/selection_status/get` |  |
| ○ | `?` | `/api/v1/affiliate/product_category/list` |  |
| ○ | `?` | `/api/v1/affiliate/recommend_commission/get` |  |
| ○ | `POST` | `/api/v1/affiliate/suggest_commission/default` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/shoppable_photo_discount/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/seller/shoppable_photo_discount/update` |  |

## 10. 排行榜 / 数据 / 报表 / 导出

*41 个 · ✅ 3*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/insights/affiliate/creator/search/suggestions` | `search_suggestions` |
| ✅ | `POST` | `/api/v1/oec/affiliate/cmp/creator/rank/list/get` | `creator_rank` |
| ✅ | `POST` | `/api/v1/oec/affiliate/cmp/filter` | `cmp_filter` |
| ○ | `?` | `/api/v1/affiliate/cmp/contact` |  |
| ○ | `?` | `/api/v1/affiliate/cmp/contact_types` |  |
| ○ | `?` | `/api/v1/affiliate/export_history` |  |
| ○ | `?` | `/api/v1/affiliate/export_link` |  |
| ○ | `POST` | `/api/v1/insights/affiliate/creator/video/list` |  |
| ○ | `?` | `/api/v1/insights/creator-outreach` |  |
| ○ | `?` | `/api/v1/insights/sample-analysis` |  |
| ○ | `?` | `/api/v1/insights/transaction-analysis` |  |
| ○ | `?` | `/api/v1/insights/transaction-analysis/creator-detail` |  |
| ○ | `?` | `/api/v1/insights/transaction-analysis/product-detail` |  |
| ○ | `?` | `/api/v1/insights/video-analysis` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/cmp/creator/ec/stats` |  |
| ○ | `?` | `/api/v1/oec/affiliate/cmp/creator/invite/list/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/cmp/main/industries` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/list/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/send` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/available_date/get` |  |
| ○ | `?` | `/api/v1/oec/affiliate/compass/creator_detail/creator_profile/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/creator_detail/detail_list/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/export_task/create` |  |
| ○ | `?` | `/api/v1/oec/affiliate/compass/export_task/export` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/export_task/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/outreach/creator/list` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/outreach/funnel_conversion/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/outreach/key_metrics/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/posted_video_list/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/product_detail/core_performance/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/product_detail/detail_list/get` |  |
| ○ | `?` | `/api/v1/oec/affiliate/compass/product_detail/product_info/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/product_info/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/sample/core_performance/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/sample/decomposition/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/sample/detail_list/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/sample/funnel_conversion/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/transaction/core_performance/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/transaction/decomposition/get` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/compass/transaction/detail_list/get` |  |

## 11. 订单 / 结算 / 税务

*6 个 · ✅ 0*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ○ | `POST` | `/api/v1/affiliate/export_order` |  |
| ○ | `?` | `/api/v1/affiliate/export_order_task` |  |
| ○ | `POST` | `/api/v1/affiliate/export_order_v2` |  |
| ○ | `POST` | `/api/v1/affiliate/orders` |  |
| ○ | `?` | `/api/v1/affiliate/withhold_tax/info` |  |
| ○ | `?` | `/api/v1/affiliate/withhold_tax/set` |  |

## 12. Partner / MCN

*27 个 · ✅ 0*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ○ | `?` | `/api/v1/affiliate/lux/partner/product/filter` |  |
| ○ | `?` | `/api/v1/affiliate/lux/partner/product/ranking/entry` |  |
| ○ | `?` | `/api/v1/affiliate/lux/partner/product/ranking/tab` |  |
| ○ | `?` | `/api/v1/affiliate/partner` |  |
| ○ | `?` | `/api/v1/affiliate/partner/agency` |  |
| ○ | `?` | `/api/v1/affiliate/partner/agency/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/collaboration-overview` |  |
| ○ | `?` | `/api/v1/affiliate/partner/discover-partners` |  |
| ○ | `?` | `/api/v1/affiliate/partner/discover-partners/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/exclusive` |  |
| ○ | `?` | `/api/v1/affiliate/partner/exclusive/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/find-mcn` |  |
| ○ | `?` | `/api/v1/affiliate/partner/find-mcn/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/find-mcn/share` |  |
| ○ | `?` | `/api/v1/affiliate/partner/initiated` |  |
| ○ | `?` | `/api/v1/affiliate/partner/initiated/create` |  |
| ○ | `?` | `/api/v1/affiliate/partner/initiated/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/marketplace` |  |
| ○ | `?` | `/api/v1/affiliate/partner/marketplace/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/partner-collabs` |  |
| ○ | `?` | `/api/v1/affiliate/partner/partner-collabs/agency/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/partner-collabs/exclusive/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/partner-collabs/seller/create` |  |
| ○ | `?` | `/api/v1/affiliate/partner/partner-collabs/seller/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/registered` |  |
| ○ | `?` | `/api/v1/affiliate/partner/registered/detail` |  |
| ○ | `?` | `/api/v1/affiliate/partner/root` |  |

## 13. 基础设施 / 媒体上传 / i18n / 风控 / 其他

*40 个 · ✅ 2*

| | 方法 | 路径 | 本地实现 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/affiliate/grayscale_strategy/check` | `grayscale_check` |
| ✅ | `POST` | `/api/v1/oec/affiliate/seller/feature_control` | `feature_control` |
| ○ | `?` | `/api/feelgood/v1/answer` |  |
| ○ | `?` | `/api/v1/affiliate/lux/article` |  |
| ○ | `?` | `/api/v1/affiliate/lux/feelgood/c_token` |  |
| ○ | `?` | `/api/v1/affiliate/lux/feelgood/token` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/image/c_url` |  |
| ○ | `?` | `/api/v1/affiliate/lux/image/upload_token` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/image/url` |  |
| ○ | `POST` | `/api/v1/affiliate/lux/screenshot` |  |
| ○ | `?` | `/api/v1/affiliate/lux/screenshot/status` |  |
| ○ | `?` | `/api/v1/bs/rt` |  |
| ○ | `?` | `/api/v1/bs/setting` |  |
| ○ | `POST` | `/api/v1/i18n_conf/currency/format_currency` |  |
| ○ | `?` | `/api/v1/i18n_conf/currency/format_currency_v2` |  |
| ○ | `GET` | `/api/v1/i18n_conf/currency/get_currency_by_currency_code` |  |
| ○ | `GET` | `/api/v1/i18n_conf/currency/get_currency_by_geo_name_id` |  |
| ○ | `GET` | `/api/v1/i18n_conf/currency/get_currency_by_region_code` |  |
| ○ | `GET` | `/api/v1/i18n_conf/currency/get_currency_list` |  |
| ○ | `GET` | `/api/v1/i18n_conf/currency/get_region_list` |  |
| ○ | `POST` | `/api/v1/i18n_conf/datetime/format_locale` |  |
| ○ | `GET` | `/api/v1/i18n_conf/language/get_language_by_locale` |  |
| ○ | `GET` | `/api/v1/i18n_conf/language/get_language_by_region_code` |  |
| ○ | `GET` | `/api/v1/i18n_conf/language/get_locales_by_region_code` |  |
| ○ | `GET` | `/api/v1/i18n_conf/region/get_eu_region_info` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_default_timezone` |  |
| ○ | `POST` | `/api/v1/i18n_conf/timezone/get_dst_result` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_exact_timezone` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_icann_timezone` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_region_timezone_info` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_hour` |  |
| ○ | `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_sec` |  |
| ○ | `POST` | `/api/v1/oec/affiliate/opportunity_product/search` |  |
| ○ | `?` | `/api/v1/sentry_verify/get_idv` |  |
| ○ | `?` | `/api/v1/sentry_verify/report_user_event` |  |
| ○ | `?` | `/api/v1/sentry_verify/verify_idv` |  |
| ○ | `?` | `/api/v2/sitebuilder` |  |
| ○ | `POST` | `/common/current_timestamp/get` |  |
| ○ | `?` | `/v1/user/webid` |  |

---

## 附 A.0 ★ 值得优先开荒的未接入接口（按主题）

这些是 ✅/◐ 之外、且直接补业务闭环的。挑的都是路径语义明确的。

### 批量私信 / IM 群发（14 个未接入）

- `?` `/api/v1/affiliate/assets/creator-management/bulk-im`
- `?` `/api/v1/affiliate/assets/creator/bulk-im`
- `GET` `/api/v1/affiliate/lux/notification/im/latest`
- `GET` `/api/v1/affiliate/lux/notification/im/message`
- `GET` `/api/v1/affiliate/lux/notification/im/unread`
- `GET` `/api/v1/affiliate/lux/notification/im/unread_count`
- `POST` `/api/v1/affiliate/notification/im/conversation/update`
- `POST` `/api/v1/affiliate/notification/im/conversation/update_tag`
- `POST` `/api/v1/affiliate/notification/im/entrance_check`
- `?` `/api/v1/affiliate/notification/im/list`
- `POST` `/api/v1/affiliate/notification/im/permission`
- `?` `/api/v1/affiliate/notification/im/seller_category`
- `POST` `/api/v1/affiliate/notification/im/shop_quota`
- `?` `/api/v1/oec/affiliate/seller/im/product/list`

### 样品全流程（54 个接口没人碰）（56 个未接入）

- `POST` `/api/v1/affiliate/lux/sample/apply`
- `?` `/api/v1/affiliate/lux/sample/c_info`
- `?` `/api/v1/affiliate/lux/sample/info`
- `POST` `/api/v1/affiliate/opt_in/sample/check`
- `?` `/api/v1/affiliate/sample`
- `?` `/api/v1/affiliate/sample/apply/list`
- `?` `/api/v1/affiliate/sample/approved_fail/count`
- `?` `/api/v1/affiliate/sample/approved_fail/list`
- `POST` `/api/v1/affiliate/sample/auto_placement_rule/get`
- `POST` `/api/v1/affiliate/sample/auto_placement_rule/save`
- `POST` `/api/v1/affiliate/sample/groi/join`
- `POST` `/api/v1/affiliate/sample/groi/perf/list`
- `POST` `/api/v1/affiliate/sample/groi/perf/summary`
- `?` `/api/v1/affiliate/sample/groi/seller_info/get`
- …还有 42 个，见对应分组表

### 达人 CRM / 名单 / 标签 / 拉黑（33 个未接入）

- `?` `/api/v1/affiliate/open_collaboration/product_creator_relation/detail`
- `?` `/api/v1/affiliate/open_collaboration/product_creator_relation/list`
- `POST` `/api/v1/affiliate/open_collaboration/product_creator_relation/terminate`
- `POST` `/api/v1/affiliate/relation/operate`
- `POST` `/api/v1/affiliate/relation/search`
- `POST` `/api/v1/affiliate/sample/tag/delete`
- `POST` `/api/v1/oec/affiliate/crm/block_creator/create`
- `POST` `/api/v1/oec/affiliate/crm/block_creator/delete`
- `POST` `/api/v1/oec/affiliate/crm/block_creator/list`
- `POST` `/api/v1/oec/affiliate/crm/block_creator/query`
- `POST` `/api/v1/oec/affiliate/crm/cmp/search`
- `POST` `/api/v1/oec/affiliate/crm/creator/batch_create`
- `?` `/api/v1/oec/affiliate/crm/creator/batch_task/result/get`
- `POST` `/api/v1/oec/affiliate/crm/creator/batch_task/submit`
- …还有 19 个，见对应分组表

### 订单 / 业绩 / 导出（11 个未接入）

- `?` `/api/v1/affiliate/campaign/product_performance/get`
- `?` `/api/v1/affiliate/campaign/single_product_performance/get`
- `POST` `/api/v1/affiliate/export_order`
- `?` `/api/v1/affiliate/export_order_task`
- `POST` `/api/v1/affiliate/export_order_v2`
- `?` `/api/v1/affiliate/open_plan/allowlist/performance`
- `POST` `/api/v1/affiliate/orders`
- `?` `/api/v1/affiliate/sample/performance`
- `POST` `/api/v1/oec/affiliate/compass/product_detail/core_performance/get`
- `POST` `/api/v1/oec/affiliate/compass/sample/core_performance/get`
- `POST` `/api/v1/oec/affiliate/compass/transaction/core_performance/get`

### 达人资产 / 素材库 / 配额（6 个未接入）

- `?` `/api/v1/affiliate/assets`
- `?` `/api/v1/affiliate/assets/creator-management`
- `?` `/api/v1/affiliate/assets/creator-management/bulk-im`
- `?` `/api/v1/affiliate/assets/creator/bulk-im`
- `?` `/api/v1/affiliate/assets/quota/overview`
- `?` `/api/v1/affiliate/assets/video-analysis`

### 活动 Campaign（另一套邀约体系）（21 个未接入）

- `?` `/api/v1/affiliate/campaign/contact_info/get`
- `POST` `/api/v1/affiliate/campaign/create`
- `?` `/api/v1/affiliate/campaign/detail/get`
- `POST` `/api/v1/affiliate/campaign/edit`
- `POST` `/api/v1/affiliate/campaign/modify_sample_quota`
- `?` `/api/v1/affiliate/campaign/partner/search`
- `?` `/api/v1/affiliate/campaign/partners/list`
- `POST` `/api/v1/affiliate/campaign/product/approve`
- `POST` `/api/v1/affiliate/campaign/product/cancel`
- `?` `/api/v1/affiliate/campaign/product_performance/get`
- `?` `/api/v1/affiliate/campaign/products/list`
- `POST` `/api/v1/affiliate/campaign/register`
- `POST` `/api/v1/affiliate/campaign/register_contact_info`
- `POST` `/api/v1/affiliate/campaign/registered_products/edit`
- …还有 7 个，见对应分组表

### MCN / Partner 域（23 个未接入）

- `?` `/api/v1/affiliate/partner/agency`
- `?` `/api/v1/affiliate/partner/agency/detail`
- `?` `/api/v1/affiliate/partner/collaboration-overview`
- `?` `/api/v1/affiliate/partner/discover-partners`
- `?` `/api/v1/affiliate/partner/discover-partners/detail`
- `?` `/api/v1/affiliate/partner/exclusive`
- `?` `/api/v1/affiliate/partner/exclusive/detail`
- `?` `/api/v1/affiliate/partner/find-mcn`
- `?` `/api/v1/affiliate/partner/find-mcn/detail`
- `?` `/api/v1/affiliate/partner/find-mcn/share`
- `?` `/api/v1/affiliate/partner/initiated`
- `?` `/api/v1/affiliate/partner/initiated/create`
- `?` `/api/v1/affiliate/partner/initiated/detail`
- `?` `/api/v1/affiliate/partner/marketplace`
- …还有 9 个，见对应分组表

### 公开合作 / 竞价库存（43 个未接入）

- `POST` `/api/v1/affiliate/auction_stock/products/list`
- `?` `/api/v1/affiliate/auction_stock/summary`
- `?` `/api/v1/affiliate/collaboration/open-collaboration`
- `?` `/api/v1/affiliate/collaboration/open-collaboration/bulk-edit`
- `?` `/api/v1/affiliate/collaboration/open-collaboration/creator-applications`
- `?` `/api/v1/affiliate/collaboration/open-collaboration/growth-products`
- `?` `/api/v1/affiliate/open_collaboration/ad/account_info/get`
- `POST` `/api/v1/affiliate/open_collaboration/ad_commission/suggest_commission/get`
- `POST` `/api/v1/affiliate/open_collaboration/affected_promotion_info/list`
- `POST` `/api/v1/affiliate/open_collaboration/auction_commission/detail`
- `POST` `/api/v1/affiliate/open_collaboration/authorized_ad_video/list`
- `POST` `/api/v1/affiliate/open_collaboration/commission_history/list`
- `POST` `/api/v1/affiliate/open_collaboration/commission_version/list`
- `POST` `/api/v1/affiliate/open_collaboration/creator_application/batch_review`
- …还有 29 个，见对应分组表

### 商品 / 佣金 / 选品（21 个未接入）

- `POST` `/api/v1/affiliate/commission_unique/check`
- `?` `/api/v1/affiliate/lux/plan/product/c_detail`
- `?` `/api/v1/affiliate/lux/plan/product/detail`
- `?` `/api/v1/affiliate/lux/plan/product/list`
- `POST` `/api/v1/affiliate/lux/product/c_detail_list`
- `?` `/api/v1/affiliate/lux/product/category/children`
- `POST` `/api/v1/affiliate/lux/product/category/childrenv2`
- `POST` `/api/v1/affiliate/open_collaboration/ad_commission/suggest_commission/get`
- `POST` `/api/v1/affiliate/open_collaboration/auction_commission/detail`
- `POST` `/api/v1/affiliate/open_collaboration/commission_history/list`
- `POST` `/api/v1/affiliate/open_collaboration/commission_version/list`
- `POST` `/api/v1/affiliate/open_collaboration/promote_products/ad_commission/upsert`
- `POST` `/api/v1/affiliate/open_collaboration/promote_products/auction_commission/upsert`
- `POST` `/api/v1/affiliate/plan/recommend_commissions/list`
- …还有 7 个，见对应分组表

### 达人画像 / 授权（4 个未接入）

- `POST` `/api/v1/affiliate/lux/creator/profile`
- `POST` `/api/v1/affiliate/review/creator/metrics`
- `POST` `/api/v1/affiliate/review/creator/reviews`
- `POST` `/api/v1/oec/affiliate/creator/marketplace/creator/profile/stats`

---

## 附 A. 已打通接口的关键参数（速查）

详见 [TIKTOK_PROMOTION_API.md](.work/adfly/TIKTOK_PROMOTION_API.md) 各节。

| 接口 | 请求要点 | 响应要点 | 主文档 |
|---|---|---|---|
| `/api/v1/affiliate/menu` | `GET` 无参 | 20 条路由，导航表来源 | §29 |
| `/api/v1/affiliate/account/info_v2` | `GET` | 店铺/账号 | §25 |
| `.../seller/invitation_group/invitation/limit` | `GET` | `{max_creator_num:50,max_product_num:100}` | §30 |
| `.../seller/invitation_group/search` | `POST {"cur_page":1,"page_size":10}` | `data.invitation_list[]`（**不是** `invitation_groups`） | §41.2 |
| `.../seller/invitation_group/detail` | `POST {"invitation_group_id":"<字符串>"}` | `data.invitation.creator_id_list[]`（**不是** `invitation_group`） | §41.2 |
| `.../seller/invitation_group/create` | `POST {"invitation_group":{...}}` **必须包一层** | `data.invitation.id` | §30 / §31 |
| `.../seller/invitation_group/update` | `POST {"invitation":{...}}` 外层键名不同 | — | §30 |
| `.../seller/invitation_group/creators_add` | `POST {"group_id":...,"creator_ids":[...]}` | `{success_cnt,conflict_cnt,invited_cnt}` | §34 |
| `.../seller/invitation_group/terminate` | `POST {"invitation_group_id":...}` | — | §31 |
| `.../seller/invitation_group/invitation/limit` | `GET` | 邀约上限 | §30 |
| `/api/v1/oec/affiliate/crm/creator/upper_limit/get` | `GET` | `{total_limit:30000,…}` | §25 |
| `.../creator/marketplace/find` | **必须由 app 自己发起**（4 个签名） | 11 页 × 12 = 132 达人 | §36 / §37 / §38 |
| `.../creator/marketplace/option` | `POST` 筛选器 | brands 400 / cats 25 / price 5 / lang 2 | §28 |
| `.../creator/marketplace/profile` | `POST {"creator_oec_id":…,"profile_types":[1]}` | 达人画像 | §28 |
| `.../cmp/creator/rank/list/get` | `rank_list_meta` = `{rank_type:1,rank_period:1,rank_date:"YYYY-MM-DD",indus_cate:"All",content_type:1}` | 榜单 | §28 |
| `.../cmp/filter` | `POST` | 榜单筛选器 | §28 |
| `.../cmp/contact_types` + `/cmp/contact` | `POST` | 联系方式 | §28 |
| `.../seller/feature_control` | `POST` | 功能开关 | §25 |
| `.../seller/wish_list/search/creator` | `POST` | 收藏夹里的达人 | §28 |
| `/api/v1/affiliate/product_selection/list` | `POST` `cur_page`/`page_size`/`source` | `total_num=624` | §28 |
| `/api/v1/affiliate/sample/group/list` | `POST tab`/`search_params`/`order_params` | 样品组 | §28 |
| `/api/v1/affiliate/lux/creator/auth_profiles` | `POST` | 达人授权画像 | §28 |
| `/api/v1/affiliate/open_collaboration/opt_in/card/get` | `POST` | 平台运营位 | §25 |
| `/api/v1/im/shop_creator/shop/user/token/get` | `GET` | IM token + **动态 api_url** | §40.1 |
| `/api/v1/oec/affiliate/seller/im/get/token` | `GET` | 同上，备选，**`user` 字段名不同** | §40.1 |
| `/api/v1/insights/affiliate/creator/search/suggestions` | `POST` | 搜索联想 | §28 |

### 站内 IM（第二套协议，见 §40）

| cmd | 路径 | 作用 |
|---|---|---|
| 200 | `{api_url}v2/message/get_by_user` | **拉会话/消息流（全量）** |
| 203 | `{api_url}v2/message/get_by_user_init` | 初始化游标（只回小增量窗口） |
| 301 | `{api_url}v1/message/get_by_conversation` | 会话内消息 |
| 100 | `{api_url}v1/message/send` | 发消息 |
| 604 | `{api_url}v3/conversation/mark_read` | 标记已读 |
| 2000 | `{api_url}v3/conversation/get_read_index` | 读位置 |
| 2001 | `{api_url}v3/conversation/get_min_index` | 最小 index |
| — | `{api_url}api/v1/im/conversation/create` | **建会话（JSON）** |
| — | `{api_url}api/v1/im/search/search_conversation_by_users` | **按用户名搜会话（JSON）** |

## 附 B. 怎么自己续抓（bundle 更新后重跑）

```bash
# 1. 从【已打开的】联盟页读资源清单（只读：不导航、不新建页、不抢焦点）
nohup python3 notes/aff_js_list.py > notes/aff_js_list.out 2>&1 &

# 2. 下载 bundle（静态 CDN，走本地代理 127.0.0.1:7890，TLS MITM 要 -k）
#    46 个 / 33 MB，清单见 notes/aff_js_manifest.json

# 3. 抽路径 + 方法 → notes/api_inventory/enriched.json
nohup python3 extract_affiliate_paths.py

# 4. 重新生成本手册
python3 gen_affiliate_api.py
```

**抓取的三个坑**：

1. 路径是**拼接**的，不能整串 grep：
   `"".concat(this.uriPrefix, "/api/v").concat(e.version || "1", "/oec/affiliate/xxx")`
   → 只能抓**尾部字面量** `/oec/...`，版本从 `version || "N"` 取。
2. 方法窗口要看 `[本字面量, 下一个字面量)`，放宽到固定 400 字符会串到下一个调用的 method。
3. `ok`/`region` 之类的短串不要当路径 —— 长度阈值 >= 6 且必须含 `/`。

**主 bundle 位置**：

| bundle | 大小 | 内容 |
|---|---|---|
| `.../goofy-sg/gftar/i18n/ecom_alliance/creator_submodule_global/1.0.0.734/index.js` | **16.7 MB** | 达人子模块，达人广场 / 邀约 / 样品 绝大部分接口在这 |
| `.../oec-magellan-sg/i18n/ecom/alliance/seller/static/js/main.91b51ba4.js` | 1.0 MB | 主应用路由 |
| `.../apps/message-feedback/*/im-modal.*.js` | 108 KB | IM 弹窗 |
