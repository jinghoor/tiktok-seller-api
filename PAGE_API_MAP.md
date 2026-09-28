# 页面 → 接口 映射表

从 11 个微前端的 bundle 里抽出的**前端路由**与**接口**，做归属映射。

- 前端路由 **783 个**（清洗后）
- 后端接口 **4873 个**

> 路由是从 bundle 里的字符串常量抽的（形如 `"/promotion/marketing-tools/discount/create"`）；
> 接口是靠「路径紧邻 `method:"…"`」判据区分的 —— 见 [`CRAWL_PLAN.md`](CRAWL_PLAN.md)。

## 1. 路由一级段 → 归属

| 一级路由 | 路由数 | 归属微前端 | 业务域 | 该域接口数 |
|---|---|---|---|---|
| `/seller` | 201 | `(shell + 多 mf)` | 混合 —— 卖家中心外壳路由 | 0 |
| `/promotion` | 172 | `mf_promotion` | 营销 / 促销 | 532 |
| `/compass` | 91 | `mf_data` | 数据 / 罗盘 / 报表 | 874 |
| `/product` | 78 | `mf_product` | 商品 / 库存 / 定价 | 433 |
| `/qualification` | 64 | `mf_governance` | 治理 / 违规 / 申诉 | 75 |
| `/insights` | 60 | `mf_data` | 数据 / 罗盘 / 报表 | 874 |
| `/logistics` | 18 | `mf_logistics` | 履约 / 物流 / 面单 | 384 |
| `/fbt` | 16 | `mf_logistics_us` | 履约 / 物流 / 面单 | 384 |
| `/passport` | 11 | `(shell)` | 账号安全 / 通行证 | 25 |
| `/brand_auth` | 10 | `mf_merchant` | 商家 / 入驻 / 资质 | 374 |
| `/finance` | 9 | `mf_finance` | 财务 / 结算 / 税务 | 251 |
| `/profile` | 8 | `(shell)` | 商家 / 入驻 / 资质 | 374 |
| `/address_oversea` | 6 | `(未映射)` | 其他 / 未分类 | 390 |
| `/administrative` | 6 | `(未映射)` | 其他 / 未分类 | 390 |
| `/multimedia` | 5 | `(shell)` | 内容创作 / 视频中心 | 153 |
| `/webapp` | 4 | `(未映射)` | 其他 / 未分类 | 390 |
| `/settle` | 3 | `mf_finance` | 财务 / 结算 / 税务 | 251 |
| `/postcode` | 2 | `(未映射)` | 其他 / 未分类 | 390 |
| `/maps` | 2 | `(未映射)` | 其他 / 未分类 | 390 |
| `/account` | 2 | `(shell)` | 账号安全 / 通行证 | 25 |
| `/pssresource` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/vc` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/easesafe` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/ticket` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/instant` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/health-center` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/supply_chain` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/app` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/common` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/bytemap` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/order` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/goods` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/shipment` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/university` | 1 | `(未映射)` | 其他 / 未分类 | 390 |
| `/logistics-us` | 1 | `(未映射)` | 其他 / 未分类 | 390 |

## 2. 各微前端的路由（前 25 条）

### `(shell + 多 mf)` —— 201 条路由

- `/seller/account/get`
- `/seller/account/switch/get`
- `/seller/account/update`
- `/seller/account_verification/get`
- `/seller/ads_optimizers/get`
- `/seller/affiliate_card/get`
- `/seller/allowed_geo_l0/get`
- `/seller/badge/is_read/get`
- `/seller/badge/set`
- `/seller/check_and_cache_register_info`
- `/seller/check_invite_code`
- `/seller/common/check_verification_code`
- `/seller/common/get`
- `/seller/common/send_verification_code`
- `/seller/common_extra/get`
- `/seller/creativityhub/get`
- `/seller/custom_role/resource/get`
- `/seller/custom_role/resource/set`
- `/seller/custom_role/resource_config_list/get`
- `/seller/customer_service/im/base_info/get`
- `/seller/delegation/am/abort`
- `/seller/delegation/history/get`
- `/seller/delegation/info`
- `/seller/delegation/mode/set`
- `/seller/delegation/seller/abort`
- …还有 176 条

### `mf_promotion` —— 172 条路由

- `/promotion/allocation/create`
- `/promotion/allocation/delete`
- `/promotion/allocation/list`
- `/promotion/allocation/prizes/get`
- `/promotion/allocation/prizes/update`
- `/promotion/app/buy_more_save_more/create`
- `/promotion/app/buy_more_save_more/get`
- `/promotion/app/buy_more_save_more/list`
- `/promotion/app/buy_more_save_more/update`
- `/promotion/app/config`
- `/promotion/app/config/get`
- `/promotion/app/flash_sale/create`
- `/promotion/app/flash_sale/get`
- `/promotion/app/flash_sale/list`
- `/promotion/app/home_page_info`
- `/promotion/app/list_products`
- `/promotion/app/mget_item_data`
- `/promotion/app/price_details/get`
- `/promotion/app/product_discount/create`
- `/promotion/app/product_discount/get`
- `/promotion/app/product_discount/list`
- `/promotion/app/recommended_promotion_tool/list`
- `/promotion/app/search_products`
- `/promotion/app/seller_allow_list/get`
- `/promotion/app/voucher/create`
- …还有 147 条

### `mf_data` —— 151 条路由

- `/compass/affiliate-analytics`
- `/compass/affiliate-video`
- `/compass/analytics-live`
- `/compass/analytics-rankings`
- `/compass/auth`
- `/compass/authorization`
- `/compass/campaign-analysis`
- `/compass/campaign-analysis/detail`
- `/compass/campaign-analysis/pop-campaign-detail`
- `/compass/campaign-analysis/report`
- `/compass/cancel-returns`
- `/compass/channel-diagnosis`
- `/compass/complaints`
- `/compass/creator-analysis`
- `/compass/creator-report`
- `/compass/customer-analysis`
- `/compass/data-affiliate/transaction`
- `/compass/data-overview`
- `/compass/fulfillment`
- `/compass/keywords-ranking`
- `/compass/keywords-ranking/keyword-detail`
- `/compass/live-analysis`
- `/compass/live-analysis/accounts-diagnosis`
- `/compass/live-analysis/live-details`
- `/compass/live-analysis/livestream-top-selling`
- …还有 126 条

### `mf_product` —— 78 条路由

- `/product/audit/product/get`
- `/product/brand/check`
- `/product/brand/create`
- `/product/brand/delete`
- `/product/brand/detail`
- `/product/brand/list`
- `/product/brand/suggest`
- `/product/brand/update`
- `/product/bundles/mactivate`
- `/product/bundles/mdeactivate`
- `/product/bundles/mdelete`
- `/product/categories/search`
- `/product/category/bind_info/get`
- `/product/category_rec/list`
- `/product/child_categories/list`
- `/product/commission/config/get`
- `/product/commission/delete`
- `/product/commission/set`
- `/product/diagnosis/overview/get`
- `/product/download_instruction/list`
- `/product/duplication/title/check`
- `/product/guide_context/get`
- `/product/image/quality/check`
- `/product/images/msubmit`
- `/product/list/seller/warehouses`
- …还有 53 条

### `mf_governance` —— 64 条路由

- `/qualification/brand`
- `/qualification/center/address/district/list`
- `/qualification/center/available/category/tree`
- `/qualification/center/black_word/check`
- `/qualification/center/brand/seller_brand/list`
- `/qualification/center/category/banner_close`
- `/qualification/center/category/list`
- `/qualification/center/category/submit`
- `/qualification/center/check_pending_epr`
- `/qualification/center/check_pending_takeback_tasks`
- `/qualification/center/epr_upload/category_epr/delete`
- `/qualification/center/epr_upload/category_epr/edit`
- `/qualification/center/epr_upload/category_epr/list`
- `/qualification/center/epr_upload/category_epr/qualification_type_list`
- `/qualification/center/epr_upload/category_epr/submit`
- `/qualification/center/epr_upload/epr/delete`
- `/qualification/center/epr_upload/epr/display_info`
- `/qualification/center/epr_upload/epr/edit`
- `/qualification/center/epr_upload/epr/list`
- `/qualification/center/epr_upload/epr/multisubmit`
- `/qualification/center/epr_upload/epr/submit`
- `/qualification/center/epr_upload/epr_info/list`
- `/qualification/center/epr_upload/epr_rule/list`
- `/qualification/center/file/upload`
- `/qualification/center/fs/product_qualification_task/list`
- …还有 39 条

### `(未映射)` —— 35 条路由

- `/address_oversea/concat_address`
- `/address_oversea/parse_address`
- `/address_oversea/place_autocomplete`
- `/address_oversea/place_autocomplete_line2`
- `/address_oversea/place_detail`
- `/address_oversea/validate_address`
- `/administrative/country_list`
- `/administrative/district`
- `/administrative/district_input_tips`
- `/administrative/district_version`
- `/administrative/list_districts`
- `/administrative/standardize`
- `/app/multimedia/image/upload_token/get`
- `/bytemap/v1/config/region_profile`
- `/common/region_domain`
- `/easesafe/oec_tax_qualification/upload`
- `/goods/create`
- `/health-center/experience-score`
- `/instant/api/v`
- `/logistics-us/pop-setup-result`
- `/maps/api/js`
- `/maps/api/key`
- `/order/fulfill-policy`
- `/postcode/postcode`
- `/postcode/validate`
- …还有 10 条

### `(shell)` —— 26 条路由

- `/account/login`
- `/account/register`
- `/multimedia/file/upload_token/get`
- `/multimedia/image/upload_token/get`
- `/multimedia/upload_completion/notify`
- `/multimedia/video/get`
- `/multimedia/video/upload_token/get`
- `/passport/open/check_qrcode`
- `/passport/pin/check`
- `/passport/pin/info`
- `/passport/pin/reset_by_ticket`
- `/passport/pin/set`
- `/passport/pin/verify`
- `/passport/sso`
- `/passport/web/email/verify`
- `/passport/web/send_code`
- `/passport/web/user/check_email_registered`
- `/passport/web/validate_code`
- `/profile/account-setting/holiday-mode`
- `/profile/account-setting/payment`
- `/profile/account-setting/warehouse`
- `/profile/auth`
- `/profile/list`
- `/profile/seller-profile`
- `/profile/seller-profile/shipping-init`
- …还有 1 条

### `mf_logistics` —— 18 条路由

- `/logistics/co-funded-program`
- `/logistics/delivery`
- `/logistics/delivery-template/create`
- `/logistics/district/get`
- `/logistics/district/list`
- `/logistics/fee-and-service`
- `/logistics/free-shipping`
- `/logistics/free-shipping/edit-free-shipping-threshold`
- `/logistics/free-shipping/product`
- `/logistics/fulfillment-setting`
- `/logistics/overview`
- `/logistics/pop-setup-result`
- `/logistics/pop-setup-warehouse`
- `/logistics/shipping-cost`
- `/logistics/shipping-template`
- `/logistics/shipping-template/edit/0`
- `/logistics/warehouse-setting`
- `/logistics/warehouse-setup-result`

### `mf_logistics_us` —— 16 条路由

- `/fbt/api/landing/add_seller_to_fbt_waitlist`
- `/fbt/api/landing/create_merchant_by_seller`
- `/fbt/api/landing/enroll_product_value_plus`
- `/fbt/api/landing/get_all_value_plus_products`
- `/fbt/api/landing/get_content_for_module`
- `/fbt/api/landing/get_merchant_by_fs_seller`
- `/fbt/api/landing/get_merchant_by_seller`
- `/fbt/api/landing/get_merchant_onboarding_cost`
- `/fbt/api/landing/get_seller_in_opt_out_from_free_shipping_status`
- `/fbt/api/landing/get_seller_latest_enrollment_stats`
- `/fbt/api/landing/get_vat_status_by_fs_seller`
- `/fbt/api/landing/go_to_fbt`
- `/fbt/api/landing/message/seller_web_action`
- `/fbt/api/landing/print_goods_barcode`
- `/fbt/api/landing/search_content_by_keywords`
- `/fbt/fbt_landing`

### `mf_finance` —— 12 条路由

- `/finance/bills`
- `/finance/change/tax-infomation`
- `/finance/eu/tax`
- `/finance/invoice`
- `/finance/payment-transaction`
- `/finance/settled`
- `/finance/statements`
- `/finance/tax`
- `/finance/tax-staged`
- `/settle/kyc-staged`
- `/settle/tax-staged`
- `/settle/verification`

### `mf_merchant` —— 10 条路由

- `/brand_auth/close_banner`
- `/brand_auth/get_ba_permission`
- `/brand_auth/get_brand_name`
- `/brand_auth/get_receipt_brand_list`
- `/brand_auth/get_submit_ba_profile`
- `/brand_auth/list_ba`
- `/brand_auth/list_trademark_registration`
- `/brand_auth/search_standard_brand`
- `/brand_auth/submit_ba`
- `/brand_auth/validate_ba`

## 3. 各微前端的接口（前 20 条）

### `mf_promotion` —— 847 个接口

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/app/multimedia/image/upload_token/get` |
| `?` | `/api/v1/arch/config_center_gw/mget_config_by_app_name` |
| `?` | `/api/v1/common/region_domain` |
| `POST` | `/api/v1/dynamic_configs/get` |
| `POST` | `/api/v1/i18n_conf/currency/format_currency` |
| `?` | `/api/v1/i18n_conf/currency/format_currency_v2` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_currency_code` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_geo_name_id` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_region_code` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_list` |
| `GET` | `/api/v1/i18n_conf/currency/get_region_list` |
| `POST` | `/api/v1/i18n_conf/datetime/format_locale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_locale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_region_code` |
| `GET` | `/api/v1/i18n_conf/language/get_locales_by_region_code` |
| `GET` | `/api/v1/i18n_conf/region/get_eu_region_info` |
| `GET` | `/api/v1/i18n_conf/timezone/get_default_timezone` |
| `POST` | `/api/v1/i18n_conf/timezone/get_dst_result` |
| `GET` | `/api/v1/i18n_conf/timezone/get_exact_timezone` |
| `GET` | `/api/v1/i18n_conf/timezone/get_icann_timezone` |

*（其余 827 个见 `ALL_API_INVENTORY.md`）*

### `mf_workbench` —— 820 个接口

| 方法 | 路径 |
|---|---|
| `POST` | `/api/v1/app/seller/cancel_conds/verify` |
| `POST` | `/api/v1/app/seller/cancel_criteria/get` |
| `GET` | `/api/v1/arch/config_center_gw/get_config` |
| `GET` | `/api/v1/arch/config_center_gw/mget_config_by_app_name` |
| `GET` | `/api/v1/arch/config_center_gw/mget_config_by_config_name` |
| `POST` | `/api/v1/insights/pop/product/optimize/data/get` |
| `POST` | `/api/v1/insights/pop/product/optimize/optimized/list` |
| `POST` | `/api/v1/insights/seller/core/stats` |
| `POST` | `/api/v1/insights/seller/core/stats/export` |
| `POST` | `/api/v1/insights/seller/creator/list` |
| `POST` | `/api/v1/insights/seller/creator/list/export` |
| `POST` | `/api/v1/insights/seller/creator/live/diagnosis/stats` |
| `POST` | `/api/v1/insights/seller/creator/live/list` |
| `POST` | `/api/v1/insights/seller/creator/product/list` |
| `POST` | `/api/v1/insights/seller/creator/video/list` |
| `POST` | `/api/v1/insights/seller/data/overview/creator/list` |
| `POST` | `/api/v1/insights/seller/live/creator/list` |
| `POST` | `/api/v1/insights/seller/live/creator/list/search` |
| `POST` | `/api/v1/insights/seller/live/diagnosis/creator/details` |
| `POST` | `/api/v1/insights/seller/live/diagnosis/creator/list` |

*（其余 800 个见 `ALL_API_INVENTORY.md`）*

### `mf_finance` —— 703 个接口

| 方法 | 路径 |
|---|---|
| `POST` | `/aff/member/switch/` |
| `GET` | `/api/v1/address_component/config` |
| `?` | `/api/v1/app/common/get` |
| `POST` | `/api/v1/app/seller/entity/get` |
| `POST` | `/api/v1/app/seller/profile/address_consent/set` |
| `POST` | `/api/v1/finance/acquiring/agreement/cancel` |
| `POST` | `/api/v1/finance/acquiring/agreement/init` |
| `POST` | `/api/v1/finance/acquiring/agreement/query` |
| `POST` | `/api/v1/finance/acquiring/balance_withdraw` |
| `POST` | `/api/v1/finance/acquiring/creator_flow/get_flow_details` |
| `POST` | `/api/v1/finance/acquiring/light_refund/order/list` |
| `POST` | `/api/v1/finance/acquiring/payment/biz_order/list` |
| `POST` | `/api/v1/finance/acquiring/payment/limit/query` |
| `POST` | `/api/v1/finance/acquiring/payment/order/continue_pay` |
| `POST` | `/api/v1/finance/acquiring/payment/order/list` |
| `POST` | `/api/v1/finance/acquiring/payment/order/pay` |
| `POST` | `/api/v1/finance/acquiring/query/account` |
| `POST` | `/api/v1/finance/acquiring/refund/get_payout_url` |
| `POST` | `/api/v1/finance/acquiring/refund/order/list` |
| `POST` | `/api/v1/finance/acquiring/security_deposit_refund/order/list` |

*（其余 683 个见 `ALL_API_INVENTORY.md`）*

### `mf_logistics_us` —— 628 个接口

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/address_component/config` |
| `?` | `/api/v1/app/common/get` |
| `?` | `/api/v1/arch/config_center_gw/mget_config_by_app_name` |
| `GET` | `/api/v1/cb/seller/incentives/algo/tasks/get` |
| `GET` | `/api/v1/cb/seller/incentives/overview/get` |
| `GET` | `/api/v1/cb/seller/incentives/program/get` |
| `GET` | `/api/v1/cb/seller/incentives/program/popUp/get` |
| `GET` | `/api/v1/cb/seller/incentives/tasks/get` |
| `GET` | `/api/v1/cb/seller/incentives/unclaimed/get` |
| `GET` | `/api/v1/cb/seller/start/tasks/status/get` |
| `POST` | `/api/v1/cb/seller/tasks/exposed/save` |
| `GET` | `/api/v1/cb/seller/tasks/island/get` |
| `POST` | `/api/v1/cb/seller/tasks/overview/get` |
| `GET` | `/api/v1/cb/seller/tasks/peaks/get` |
| `GET` | `/api/v1/cb/seller/tasks/sections/get_all` |
| `GET` | `/api/v1/cb/seller/tasks/step/get_all` |
| `POST` | `/api/v1/config` |
| `POST` | `/api/v1/conversation` |
| `POST` | `/api/v1/fulfillment/actions/na/upload` |
| `POST` | `/api/v1/fulfillment/checklist/list` |

*（其余 608 个见 `ALL_API_INVENTORY.md`）*

### `mf_logistics` —— 582 个接口

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/address_component/config` |
| `GET` | `/api/v1/app/common/get` |
| `POST` | `/api/v1/fulfillment/actions/na/upload` |
| `POST` | `/api/v1/fulfillment/checklist/list` |
| `POST` | `/api/v1/fulfillment/config_center/get` |
| `GET` | `/api/v1/fulfillment/default/seller/get` |
| `POST` | `/api/v1/fulfillment/delivery_template/download` |
| `POST` | `/api/v1/fulfillment/delivery_template/export` |
| `POST` | `/api/v1/fulfillment/doc/print_status/verify` |
| `POST` | `/api/v1/fulfillment/export/err_file` |
| `POST` | `/api/v1/fulfillment/export/file_submit` |
| `POST` | `/api/v1/fulfillment/export/file_upload` |
| `POST` | `/api/v1/fulfillment/fulfill_info/list` |
| `POST` | `/api/v1/fulfillment/insurance/na/set_affidavit_auto_send_app` |
| `POST` | `/api/v1/fulfillment/invoice_no/save` |
| `GET` | `/api/v1/fulfillment/logistic_detail/list` |
| `POST` | `/api/v1/fulfillment/logistics/provider/list` |
| `POST` | `/api/v1/fulfillment/logistics_service/list` |
| `POST` | `/api/v1/fulfillment/package/create` |
| `POST` | `/api/v1/fulfillment/package/delivery_update` |

*（其余 562 个见 `ALL_API_INVENTORY.md`）*

### `mf_product` —— 582 个接口

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/app/multimedia/image/upload_token/get` |
| `?` | `/api/v1/bidding/bid/details` |
| `?` | `/api/v1/bidding/seller/bidding-config` |
| `?` | `/api/v1/bidding/seller/overview` |
| `?` | `/api/v1/bidding/seller/spotlight` |
| `?` | `/api/v1/bidding/top/spotlight` |
| `POST` | `/api/v1/dbmp/pop/product_growth/category/authorized` |
| `POST` | `/api/v1/dbmp/pop/product_growth/ready_time` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/audit` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/check` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/create` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/delete` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/edit` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/mget` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/search` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/shop/list` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/sim_product_rel/export` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/sim_product_rel/list` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/favorite` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/content` |

*（其余 562 个见 `ALL_API_INVENTORY.md`）*

### `mf_data` —— 555 个接口

| 方法 | 路径 |
|---|---|
| `POST` | `/api/v1/i18n_conf/currency/format_currency` |
| `?` | `/api/v1/i18n_conf/currency/format_currency_v2` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_currency_code` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_geo_name_id` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_region_code` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_list` |
| `GET` | `/api/v1/i18n_conf/currency/get_region_list` |
| `POST` | `/api/v1/i18n_conf/datetime/format_locale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_locale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_region_code` |
| `GET` | `/api/v1/i18n_conf/language/get_locales_by_region_code` |
| `GET` | `/api/v1/i18n_conf/region/get_eu_region_info` |
| `GET` | `/api/v1/i18n_conf/timezone/get_default_timezone` |
| `POST` | `/api/v1/i18n_conf/timezone/get_dst_result` |
| `GET` | `/api/v1/i18n_conf/timezone/get_exact_timezone` |
| `GET` | `/api/v1/i18n_conf/timezone/get_icann_timezone` |
| `GET` | `/api/v1/i18n_conf/timezone/get_region_timezone_info` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_hour` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_sec` |

*（其余 535 个见 `ALL_API_INVENTORY.md`）*

### `mf_merchant` —— 405 个接口

| 方法 | 路径 |
|---|---|
| `?` | `/api/v1/operation/form_open/user_page/query_by_code` |
| `POST` | `/api/v1/seller/auth/tt_user_info/get` |
| `POST` | `/api/v1/seller/c2b/qrcode/check` |
| `POST` | `/api/v1/seller/c2b/trial_period/skip` |
| `?` | `/api/v1/seller/creator/agg/get` |
| `POST` | `/api/v1/seller/creator/agg/verify/invite` |
| `POST` | `/api/v1/seller/creator/availability/verify` |
| `?` | `/api/v1/seller/creator/get` |
| `POST` | `/api/v1/seller/creator/info/get` |
| `POST` | `/api/v1/seller/creator/info/verify` |
| `POST` | `/api/v1/seller/creator/invitation/send` |
| `POST` | `/api/v1/seller/creator/official_creator/bind` |
| `POST` | `/api/v1/seller/creator/official_creator/get` |
| `POST` | `/api/v1/seller/creator/official_creator/upgrade` |
| `POST` | `/api/v1/seller/creator/qrcode/check` |
| `POST` | `/api/v1/seller/creator/remain/get` |
| `POST` | `/api/v1/seller/creator/tip/report` |
| `POST` | `/api/v1/seller/creator/unbind` |
| `POST` | `/api/v1/seller/creator/unbind_apply/get` |
| `POST` | `/api/v1/seller/creator/unbind_apply/update` |

*（其余 385 个见 `ALL_API_INVENTORY.md`）*

### `mf_reverse` —— 344 个接口

| 方法 | 路径 |
|---|---|
| `POST` | `/api/v1/debugs/reverse/orders/list_main_orders` |
| `POST` | `/api/v1/fulfillment/actions/na/upload` |
| `POST` | `/api/v1/fulfillment/checklist/list` |
| `POST` | `/api/v1/fulfillment/config_center/get` |
| `GET` | `/api/v1/fulfillment/default/seller/get` |
| `POST` | `/api/v1/fulfillment/delivery_template/download` |
| `POST` | `/api/v1/fulfillment/delivery_template/export` |
| `POST` | `/api/v1/fulfillment/doc/print_status/verify` |
| `POST` | `/api/v1/fulfillment/doc_record/generate` |
| `POST` | `/api/v1/fulfillment/export/err_file` |
| `POST` | `/api/v1/fulfillment/export/file_submit` |
| `POST` | `/api/v1/fulfillment/export/file_upload` |
| `POST` | `/api/v1/fulfillment/fulfill_info/list` |
| `PUT` | `/api/v1/fulfillment/insurance/na/set_affidavit_auto_send` |
| `POST` | `/api/v1/fulfillment/insurance/na/upload_affidavit` |
| `POST` | `/api/v1/fulfillment/invoice/list` |
| `POST` | `/api/v1/fulfillment/invoice_no/save` |
| `GET` | `/api/v1/fulfillment/logistic_detail/list` |
| `POST` | `/api/v1/fulfillment/logistics/provider/list` |
| `POST` | `/api/v1/fulfillment/order/history` |

*（其余 324 个见 `ALL_API_INVENTORY.md`）*

### `mf_governance` —— 214 个接口

| 方法 | 路径 |
|---|---|
| `POST` | `/api/v1/seller/growth_center/shop/violation/quick_filter/query` |
| `POST` | `/api/v1/seller/growth_center/shop/warning/quick_filter/query` |
| `POST` | `/logistics/district/get` |
| `POST` | `/logistics/district/list` |
| `POST` | `/product/brand/check` |
| `POST` | `/product/brand/create` |
| `POST` | `/product/brand/delete` |
| `POST` | `/product/brand/detail` |
| `POST` | `/product/brand/update` |
| `POST` | `/product/bundles/mactivate` |
| `POST` | `/product/bundles/mdeactivate` |
| `POST` | `/product/bundles/mdelete` |
| `POST` | `/product/commission/config/get` |
| `POST` | `/product/commission/delete` |
| `POST` | `/product/commission/set` |
| `POST` | `/product/duplication/title/check` |
| `POST` | `/product/guide_context/get` |
| `POST` | `/product/image/quality/check` |
| `POST` | `/product/images/msubmit` |
| `POST` | `/product/local/bundle/create` |

*（其余 194 个见 `ALL_API_INVENTORY.md`）*

### `mf_privatedomain` —— 132 个接口

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/app/multimedia/image/upload_token/get` |
| `?` | `/api/v1/common/region_domain` |
| `GET` | `/api/v1/multimedia/file/upload_token/get` |
| `GET` | `/api/v1/multimedia/image/get` |
| `GET` | `/api/v1/multimedia/image/upload_token/get` |
| `GET` | `/api/v1/multimedia/video/upload_token/get` |
| `POST` | `/api/v1/multimedia/white_background/check` |
| `POST` | `/api/v1/multimedia/white_background/get` |
| `POST` | `/api/v1/seller/audit/dismiss` |
| `?` | `/api/v1/seller/get` |
| `POST` | `/api/v1/seller/logo/aigc/add` |
| `?` | `/api/v1/seller/logo/aigc/detail` |
| `POST` | `/api/v1/seller/logo/aigc/list` |
| `POST` | `/api/v1/seller/logo/aigc/submit` |
| `?` | `/api/v1/seller/onboard/v1/config_aggr/get` |
| `POST` | `/api/v1/seller/onboard/v1/contact/verify` |
| `?` | `/api/v1/seller/onboard/v1/cross_border/config/get` |
| `?` | `/api/v1/seller/onboard/v1/cross_border/deposit/get` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/draft/get` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/draft/save` |

*（其余 112 个见 `ALL_API_INVENTORY.md`）*

## 4. 局限

静态映射只能到**微前端粒度**，不能精确到「某条路由加载时打哪几个接口」——
那需要真流量捕获（`capture_finance_live.py` 的通用化版本），
**当前受阻于两个容器的会话均已过期**（见下）。

```
port CDP_PORT (本土): 2/4 个页面是登录/注册页
port CDP_PORT (跨境): 5/7 个页面是登录/注册页
实测：/api/v1/pay/settlement/settings（此前实测通过）现在返回
      98001002 You must log in to continue
```

> ⚠ **记录更正**：先前把 `insights` 域的 `98001002 请登录` 判为「需要特殊鉴权头」，
> 复核后确认**就是会话过期** —— 同时段所有域都返回同一错误。崩溃分析时已自证。
