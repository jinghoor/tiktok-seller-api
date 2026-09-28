# 接口覆盖测试报告

- 测试时间:2026-09-25 03:56:41
- 接口总数:**291**,实测 199,跳过写入类 92
- 耗时 30.2s,并发 6

## 汇总

| 状态 | 数量 |
|---|---|
| SKIP(write) | 92 |
| OK | 66 |
| PARAM | 45 |
| GONE | 33 |
| NOAUTH | 32 |
| ERROR | 12 |
| OK(bytes) | 10 |
| AUTH | 1 |

## 按后端

| 后端 | OK | PARAM | NOAUTH | GONE | ERROR | 跳过 |
|---|---|---|---|---|---|---|
| advertise | 22 | 9 | 24 | 1 | 2 | 8 |
| ai_agent | 14 | 28 | 2 | 0 | 1 | 22 |
| automation | 8 | 3 | 0 | 3 | 3 | 15 |
| finance | 10 | 3 | 4 | 27 | 3 | 19 |
| finance_bff | 3 | 0 | 1 | 0 | 3 | 9 |
| front | 9 | 1 | 0 | 2 | 0 | 19 |
| mcp_open | 0 | 1 | 1 | 0 | 0 | 0 |

## 延迟

n=199, p50=67ms, p90=236ms, p99=30013ms, max=30023ms

## 全部接口状态

| 状态 | 后端 | 方法 | 路径 | 耗时 | 返回/错误 |
|---|---|---|---|---|---|
| AUTH | advertise | POST | `/advertiser/apply_detail` | 66ms | [code=11] 开户记录不存在 (https://front-v1.aiadfly.com/front_api/advertiser/a |
| ERROR | advertise | POST | `/ad/list` | 70ms | [code=500] failed to find adgroup info (https://automation-v1.aiadfly. |
| ERROR | advertise | POST | `/kanban/google_adv_consume/export` | 156ms | [code=500] unknown request error (https://advertise-bff-v1.aiadfly.com |
| ERROR | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/store/config` | 56ms | [code=500] unknown request error (https://ai-agent-v1.aiadfly.com/ai_a |
| ERROR | automation | POST | `/adgroup/list` | 81ms | [code=500] failed to find adgroup info (https://automation-v1.aiadfly. |
| ERROR | automation | POST | `/campaign/list` | 64ms | [code=500] failed to find campaign info (https://automation-v1.aiadfly |
| ERROR | automation | POST | `/material_group/detail` | 63ms | [code=500] unknown request error (https://automation-v1.aiadfly.com/fr |
| ERROR | finance | POST | `/finance/rebate/adv_detail/list` | 97ms | [code=500] unknown request error (https://finance-v1.aiadfly.com/front |
| ERROR | finance | POST | `/finance/rebate/rule/list` | 55ms | [code=500] unknown request error (https://finance-v1.aiadfly.com/front |
| ERROR | finance | POST | `/finance/rebate/rule_detail/list` | 58ms | [code=500] unknown request error (https://finance-v1.aiadfly.com/front |
| ERROR | finance_bff | POST | `/wallet/calculate_reverse_exchange_amount` | 158ms | [code=500] 内部错误 (https://finance-bff-v1.aiadfly.com/front_api/wallet/c |
| ERROR | finance_bff | POST | `/wallet/list` | 30023ms | HTTPSConnectionPool(host='finance-bff-v1.aiadfly.com', port=443): Read |
| ERROR | finance_bff | POST | `/wallet/sub_company/list` | 30013ms | HTTPSConnectionPool(host='finance-bff-v1.aiadfly.com', port=443): Read |
| GONE | advertise | POST | `/ad/get` | 72ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | automation | POST | `/material/daily` | 69ms | [code=404] 404 page not found (https://automation-v1.aiadfly.com/front |
| GONE | automation | POST | `/material/export` | 77ms | [code=404] 404 page not found (https://automation-v1.aiadfly.com/front |
| GONE | automation | POST | `/material/summary` | 73ms | [code=404] 404 page not found (https://automation-v1.aiadfly.com/front |
| GONE | finance | POST | `/add_custom_anchor_video` | 66ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/advertisers/list` | 57ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/campaign/get` | 72ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/campaigns/export` | 70ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/campaigns/list` | 67ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/conversion_actions/list` | 65ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/export` | 62ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/geo_targets/suggest` | 65ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/group_items` | 64ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/image_assets/list` | 63ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/languages/list` | 56ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/list` | 70ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/play_install_conversion_actions/list` | 67ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/series/chart` | 72ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/series/summary` | 69ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/session/list` | 67ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/account/export` | 68ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/account/list` | 65ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/ad_asset_snapshots/export` | 78ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/ad_asset_snapshots/list` | 70ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/ad_group/export` | 79ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/ad_group/list` | 67ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/campaign/export` | 88ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/snapshots/campaign/list` | 68ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/summary` | 67ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/video_assets/list` | 77ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | finance | POST | `/youtube_video/get` | 66ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | front | POST | `/auth/list` | 68ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| GONE | front | POST | `/auth/multi_edit_company_menu` | 56ms | [code=404] 404 page not found (https://front-v1.aiadfly.com/front_api/ |
| NOAUTH | advertise | POST | `/advertiser/bc_un_bind_multi` | 58ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/advertiser/b |
| NOAUTH | advertise | POST | `/advertiser/bc_un_bind_single` | 54ms | [code=999] 广告账号id为空 (https://front-v1.aiadfly.com/front_api/advertiser |
| NOAUTH | advertise | POST | `/advertiser/get_bind_bc` | 55ms | [code=999] 广告账号id为空 (https://front-v1.aiadfly.com/front_api/advertiser |
| NOAUTH | advertise | POST | `/tiktok/ad_detail` | 60ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/ad_de |
| NOAUTH | advertise | POST | `/tiktok/ad_modify` | 55ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/ad_mo |
| NOAUTH | advertise | POST | `/tiktok/adgroup_detail` | 53ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/adgro |
| NOAUTH | advertise | POST | `/tiktok/adgroup_extend` | 55ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/adgro |
| NOAUTH | advertise | POST | `/tiktok/adgroup_modify` | 53ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/adgro |
| NOAUTH | advertise | POST | `/tiktok/adv_unionpay_check` | 1349ms | [code=999] license_no: value is required but missing (https://front-v1 |
| NOAUTH | advertise | POST | `/tiktok/advertiser_update` | 60ms | [code=999] batch is empty (https://front-v1.aiadfly.com/front_api/tikt |
| NOAUTH | advertise | POST | `/tiktok/campaign_detail` | 60ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/campa |
| NOAUTH | advertise | POST | `/tiktok/campaign_modify` | 52ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/campa |
| NOAUTH | advertise | POST | `/tiktok/copy_advertisement` | 54ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/copy_ |
| NOAUTH | advertise | POST | `/tiktok/create_advertisement` | 67ms | [code=999] 商品或素材参数有误 (https://front-v1.aiadfly.com/front_api/tiktok/cr |
| NOAUTH | advertise | POST | `/tiktok/create_advertisement_new` | 53ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/creat |
| NOAUTH | advertise | POST | `/tiktok/get_ad_detail_list` | 57ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/get_a |
| NOAUTH | advertise | POST | `/tiktok/get_config` | 68ms | [code=999] advertiser_id nil (https://front-v1.aiadfly.com/front_api/t |
| NOAUTH | advertise | POST | `/tiktok/get_video_url` | 56ms | [code=999] 帖子id为空 (https://front-v1.aiadfly.com/front_api/tiktok/get_v |
| NOAUTH | advertise | POST | `/tiktok/get_videos` | 55ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/get_v |
| NOAUTH | advertise | POST | `/tiktok/gmv_max/get_detail_info` | 69ms | [code=999] record not found (https://front-v1.aiadfly.com/front_api/ti |
| NOAUTH | advertise | POST | `/tiktok/gmv_max/group_item_report` | 63ms | [code=999] record not found (https://front-v1.aiadfly.com/front_api/ti |
| NOAUTH | advertise | POST | `/tiktok/gmv_max/identity/get` | 56ms | [code=999] advertiser_id or store_id or store_authorized_bc_id nil (ht |
| NOAUTH | advertise | POST | `/tiktok/gmv_max/store/list` | 56ms | [code=999] advertiser_id nil (https://front-v1.aiadfly.com/front_api/t |
| NOAUTH | advertise | POST | `/tiktok/gmv_max/store/shop_ad_usage_check` | 57ms | [code=999] advertiser_id or store_id  nil (https://front-v1.aiadfly.co |
| NOAUTH | ai_agent | POST | `/advertiser/adv_bc_bind` | 90ms | [code=999] 广告账号id列表为空 (https://front-v1.aiadfly.com/front_api/advertis |
| NOAUTH | ai_agent | POST | `/ai_agent/v1/rebate/list` | 61ms | [code=500] get company_ex_id error (https://ai-agent-v1.aiadfly.com/ai |
| NOAUTH | finance | POST | `/advertiser/bind_adv` | 73ms | [code=999] platform invalid (https://front-v1.aiadfly.com/front_api/ad |
| NOAUTH | finance | POST | `/advertiser/bind_adv_option_list` | 58ms | [code=999] platform invalid (https://front-v1.aiadfly.com/front_api/ad |
| NOAUTH | finance | POST | `/advertiser/unbind_adv` | 55ms | [code=999] platform invalid (https://front-v1.aiadfly.com/front_api/ad |
| NOAUTH | finance | POST | `/tiktok/campaign_modify` | 66ms | [code=999] 广告账号为空 (https://front-v1.aiadfly.com/front_api/tiktok/campa |
| NOAUTH | finance_bff | POST | `/activity_link/by_code` | 56ms | [code=999] code is empty (https://front-v1.aiadfly.com/front_api/activ |
| NOAUTH | mcp_open | POST | `/oauth/authorize_confirm` | 166ms | [code=400] {"error":"company_ex_id is required"} (https://mcp-open.aia |
| OK | advertise | POST | `/ad/gmv_max_store_config/list` | 61ms | 0 条 |
| OK | advertise | POST | `/ad/gmv_max_store_config/list_by_store_id` | 57ms | 0 条 |
| OK | advertise | POST | `/advertiser/apply_list` | 68ms | 4 条 |
| OK | advertise | GET | `/advertiser/config` | 157ms | 5 条 |
| OK | advertise | POST | `/advertiser/get_apply_limit_num` | 61ms | 1 条 |
| OK | advertise | POST | `/advertiser/list` | 1556ms | 0 条 |
| OK | advertise | POST | `/advertiser/tt_create_task_list` | 59ms | 3 条 |
| OK | advertise | POST | `/kanban/google_adv_consume` | 111ms | 0 条 |
| OK | advertise | POST | `/tiktok/ad_report` | 2335ms | 3 条 |
| OK | advertise | POST | `/tiktok/adgroup_report` | 553ms | 3 条 |
| OK | advertise | POST | `/tiktok/advertiser_balance_get` | 55ms | 0 条 |
| OK | advertise | POST | `/tiktok/advertiser_report` | 1015ms | 5 条 |
| OK | advertise | POST | `/tiktok/auth_list` | 62ms | 3 条 |
| OK | advertise | POST | `/tiktok/campaign_report` | 285ms | 3 条 |
| OK | advertise | POST | `/tiktok/get_opt_campaign` | 58ms | 0 条 |
| OK | advertise | POST | `/tiktok/gmv_max/detail` | 59ms | 32 条 |
| OK | advertise | POST | `/tiktok/gmv_max/get_refresh_time` | 60ms | 2 条 |
| OK | advertise | POST | `/tiktok/gmv_max/list` | 66ms | 5 条 |
| OK | advertise | POST | `/tiktok/gmv_max/occupied_custom_shop_ads/list` | 57ms |  |
| OK | advertise | POST | `/tiktok/gmv_max/post_item_report` | 53ms | 0 条 |
| OK | advertise | POST | `/tiktok/gmv_max/refresh` | 183ms |  |
| OK | advertise | POST | `/tt/auth/list` | 74ms | 3 条 |
| OK | ai_agent | POST | `/advertiser/adv_bc_bind_list` | 76ms | 5 条 |
| OK | ai_agent | POST | `/advertiser/bc_un_bind_list` | 85ms | 3 条 |
| OK | ai_agent | GET | `/ai_agent/market/chat/list` | 59ms | 0 条 |
| OK | ai_agent | GET | `/ai_agent/market/session_id/get` | 59ms | 2 条 |
| OK | ai_agent | GET | `/ai_agent/market/video/list` | 59ms | 0 条 |
| OK | ai_agent | POST | `/ai_agent/v1/adv/list` | 182ms | 0 条 |
| OK | ai_agent | GET | `/ai_agent/v1/chat/list` | 75ms | 0 条 |
| OK | ai_agent | GET | `/ai_agent/v1/message/get_prompt` | 72ms | 2 条 |
| OK | ai_agent | GET | `/ai_agent/v1/session_id/get` | 156ms | 2 条 |
| OK | ai_agent | GET | `/ai_agent/v1/support/info` | 63ms | 1 条 |
| OK | ai_agent | GET | `/ai_agent/v1/user/guide_task` | 63ms | 5 条 |
| OK | ai_agent | GET | `/ai_agent/v1/user/profile` | 57ms | 6 条 |
| OK | ai_agent | POST | `/role_edit` | 80ms |  |
| OK | ai_agent | POST | `/role_list` | 88ms | 5 条 |
| OK | automation | POST | `/advertiser/list` | 1263ms | 0 条 |
| OK | automation | POST | `/advertiser_label_relation/find` | 83ms | 5 条 |
| OK | automation | POST | `/label/list` | 76ms | 1 条 |
| OK | automation | POST | `/label_category/list` | 67ms | 1 条 |
| OK | automation | POST | `/material/list` | 67ms | 0 条 |
| OK | automation | POST | `/material_group/list` | 73ms | 1 条 |
| OK | automation | POST | `/tactic/list` | 178ms | 0 条 |
| OK | automation | POST | `/tactic_action_log/list` | 236ms | 0 条 |
| OK | finance | POST | `/advertiser/adv_consume_report` | 310ms | 5 条 |
| OK | finance | POST | `/advertiser/adv_fb_consume_report` | 128ms | 3 条 |
| OK | finance | POST | `/advertiser/bind_adv_list` | 73ms |  |
| OK | finance | POST | `/finance/billset/find` | 68ms | 16 条 |
| OK | finance | GET | `/finance/billset/need` | 59ms | 1 条 |
| OK | finance | POST | `/finance/company_detail/list` | 182ms | 0 条 |
| OK | finance | POST | `/finance/settlement/detail/list` | 63ms | 0 条 |
| OK | finance | POST | `/finance/settlement/list` | 65ms | 3 条 |
| OK | finance | POST | `/finance/settlement/overdue-t7` | 67ms | 1 条 |
| OK | finance | POST | `/tiktok/panel_report` | 220ms | 2 条 |
| OK | finance_bff | POST | `/coupon/detail/list` | 271ms | 5 条 |
| OK | finance_bff | POST | `/coupon/has_point` | 176ms | 1 条 |
| OK | finance_bff | POST | `/coupon/list` | 356ms | 5 条 |
| OK | front | POST | `/auth/get_company_menu` | 60ms |  |
| OK | front | POST | `/company/country_list` | 175ms | 5 条 |
| OK | front | POST | `/company/custom_list` | 116ms | 0 条 |
| OK | front | POST | `/company/get_ports_list` | 170ms | 9 条 |
| OK | front | POST | `/notice/archive_list` | 70ms | 3 条 |
| OK | front | GET | `/notice/bell_list` | 71ms | 2 条 |
| OK | front | POST | `/user/get_business` | 199ms | 34 条 |
| OK | front | GET | `/user/info` | 150ms | 13 条 |
| OK | front | POST | `/user/list` | 74ms | 3 条 |
| OK(bytes) | advertise | POST | `/advertiser/apply_list/export` | 85ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/advertiser/list/export` | 1524ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/tiktok/ad_report/export` | 2255ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/tiktok/adgroup_report/export` | 532ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/tiktok/advertiser_report/export` | 1020ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/tiktok/campaign_report/export` | 273ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | advertise | POST | `/tiktok/gmv_max/export` | 59ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | ai_agent | POST | `/advertiser/adv_bc_bind_list/export` | 78ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://f |
| OK(bytes) | automation | POST | `/tactic_action_log/export` | 299ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://a |
| OK(bytes) | automation | POST | `/tactic_change_log/export` | 75ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' (https://a |
| PARAM | advertise | POST | `/ad/gmv_max_store_config/get` | 59ms | [code=400] invalid GetGmvMaxStoreConfigRequest.GmvMaxStoreConfigId: va |
| PARAM | advertise | POST | `/ad/pixel/list` | 170ms | [code=400] invalid GetPixelListRequest.AdvertiserId: value length must |
| PARAM | advertise | POST | `/ad/store_app_info/get` | 71ms | [code=400] invalid GetStoreAppInfoRequest.Query: value length must be  |
| PARAM | advertise | GET | `/advertiser/get_panda_token` | 59ms | [code=200] 非 JSON 响应(content-type=?):  (https://front-v1.aiadfly.com/f |
| PARAM | advertise | POST | `/bc/query_auth` | 156ms | [code=400] invalid QueryAuthRequest.AuthLinkExId: value length must be |
| PARAM | advertise | POST | `/tiktok/identity_get` | 57ms | [code=400] {"code":999,"message":"Key: 'IdentityListReq.AccessToken' E |
| PARAM | advertise | POST | `/tt/admin_store/list` | 60ms | [code=400] invalid ListTikTokAdminStoreRequest.TiktokAuthId: value mus |
| PARAM | advertise | POST | `/tt/bc/is_adv_bound` | 54ms | [code=400] invalid IsBcAdvIdBoundRequest.BcId: value length must be at |
| PARAM | advertise | POST | `/tt/bc/list` | 60ms | [code=400] invalid ListTikTokBcRequest.TiktokAuthId: value must be gre |
| PARAM | ai_agent | POST | `/ai_agent/market/chat/history` | 151ms | [code=400] invalid ChatHistoryRequest.SessionId: value length must be  |
| PARAM | ai_agent | POST | `/ai_agent/market/stream/stop` | 3056ms | [code=200] SSE 流式响应(content-type=text/event-stream) (https://ai-agent- |
| PARAM | ai_agent | GET | `/ai_agent/market/video/batch` | 49ms | [code=400] invalid GetVideoBatchRequest.BatchId: value length must be  |
| PARAM | ai_agent | POST | `/ai_agent/market/video/terminate` | 58ms | [code=400] invalid TerminateVideoRequest.VideoId: value length must be |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/campaign/list` | 62ms | [code=400] invalid ListCampaignRequest.MessageId: value length must be |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/identity/list` | 74ms | [code=400] invalid ListGmvMaxIdentityRequest.AdvertiserId: value lengt |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list` | 175ms | [code=500] record not found (https://ai-agent-v1.aiadfly.com/ai_agent/ |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/store/list` | 61ms | [code=400] invalid ListGmvMaxStoreRequest.AdvertiserId: value length m |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/store/product/list` | 64ms | [code=400] invalid ListGmvMaxStoreProductRequest.AdvertiserId: value l |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/gmv_max/store_id/validate` | 77ms | [code=400] invalid ValidateGmvMaxStoreIdRequest.AdvertiserId: value le |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/tt/account/list` | 60ms | [code=400] invalid ListTikTokAccountRequest.BcId: value length must be |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/tt/asset/list` | 74ms | [code=400] invalid ListTikTokAssetRequest.BcId: value length must be a |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/identity/get` | 55ms | [code=400] invalid GetIdentityRequest.AdvertiserId: value length must  |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/interest_category/list` | 51ms | [code=400] invalid ListInterestCategoryRequest.AdvertiserId: value len |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/public_info/get` | 56ms | [code=400] invalid GetAdCreatePublicInfoRequest.AdvertiserId: value le |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/region/search` | 56ms | [code=400] invalid SearchRegionRequest.AdvertiserId: value length must |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/store/list` | 56ms | [code=400] invalid ListStoreRequest.AdvertiserId: value length must be |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/store/product/list` | 56ms | [code=400] invalid ListStoreProductRequest.AdvertiserId: value length  |
| PARAM | ai_agent | POST | `/ai_agent/v1/ad/vsa/video/search` | 56ms | [code=400] invalid SearchVideoRequest.AdvertiserId: value length must  |
| PARAM | ai_agent | POST | `/ai_agent/v1/chat/history` | 168ms | [code=400] invalid ChatHistoryRequest.SessionId: value length must be  |
| PARAM | ai_agent | POST | `/ai_agent/v1/file/cloud_url/get` | 62ms | [code=500] region[] is invalid (https://ai-agent-v1.aiadfly.com/ai_age |
| PARAM | ai_agent | POST | `/ai_agent/v1/guide/adv_recharge` | 64ms | [code=400] invalid GuideAdvRechargeRequest.Amount: value must be great |
| PARAM | ai_agent | GET | `/ai_agent/v1/message/get` | 51ms | [code=400] invalid MessageGetRequest.MessageId: value length must be a |
| PARAM | ai_agent | POST | `/ai_agent/v1/ocr` | 66ms | [code=400] invalid OCRRequest.Url: value length must be at least 1 run |
| PARAM | ai_agent | POST | `/ai_agent/v1/qrcode/generate` | 74ms | [code=500] qrcode_type is required (https://ai-agent-v1.aiadfly.com/ai |
| PARAM | ai_agent | POST | `/ai_agent/v1/qrcode/query` | 64ms | [code=500] ticket cannot be empty (https://ai-agent-v1.aiadfly.com/ai_ |
| PARAM | ai_agent | POST | `/ai_agent/v1/user/confirm_first_recharge` | 59ms | [code=500] is_sure must be 1 (https://ai-agent-v1.aiadfly.com/ai_agent |
| PARAM | ai_agent | POST | `/public/data/report` | 58ms | [code=400] invalid DataReportRequest.PageId: value length must be at l |
| PARAM | automation | POST | `/tactic/adv/list` | 148ms | [code=400] invalid ListTacticAdvRequest.TacticExId: value length must  |
| PARAM | automation | POST | `/tactic/find` | 171ms | [code=400] invalid FindTacticRequest.TacticExId: value length must be  |
| PARAM | automation | POST | `/tactic_change_log/list` | 70ms | [code=500] find tactic_action_log data empty (https://automation-v1.ai |
| PARAM | finance | POST | `/finance/account/payable/detail` | 169ms | [code=400] invalid GetAccountPayableDetailRequest.CompanyExId: value l |
| PARAM | finance | POST | `/finance/rebate/export` | 98ms | [code=500] record not found (https://finance-v1.aiadfly.com/front_api/ |
| PARAM | finance | POST | `/finance/settlement/detail/export` | 227ms | [code=500] record not found (https://finance-v1.aiadfly.com/front_api/ |
| PARAM | front | POST | `/user/check_fa` | 166ms | [code=404] 用户不存在 (https://front-v1.aiadfly.com/front_api/user/check_fa |
| PARAM | mcp_open | GET | `/decrypt/wlh_login_info` | 162ms | [code=400] decrypt payload failed (https://mcp-open.aiadfly.com/decryp |
| SKIP(write) | advertise | POST | `/ad/gmv_max_store_config/delete` | 0ms |  |
| SKIP(write) | advertise | POST | `/ad/update` | 0ms |  |
| SKIP(write) | advertise | POST | `/advertiser/apply` | 0ms |  |
| SKIP(write) | advertise | POST | `/file/complete` | 0ms |  |
| SKIP(write) | advertise | GET | `/file/sign` | 0ms |  |
| SKIP(write) | advertise | POST | `/tiktok/gmv_max/copy` | 0ms |  |
| SKIP(write) | advertise | POST | `/tiktok/gmv_max/create` | 0ms |  |
| SKIP(write) | advertise | POST | `/tiktok/gmv_max/update` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/market/creative/re_gene_desc` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/market/image/regene` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/market/image/reupload` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/market/message/save` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/market/session_id/create` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/ad/guide/ad_create/reset` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/ad/guide/adv_apply/reset` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/message/feedback` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/message/reset` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/message/save` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/session_id/create` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/ai_agent/v1/sign/draft/addr/acquire` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/adv_amount_clear_list` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/adv_amount_clear_list/export` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/adv_recharge_list` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/adv_recharge_list/export` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/airpay` | 0ms |  |
| SKIP(write) | ai_agent | GET | `/pay/bill_tips` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/llpay` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/pay_detail` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/pppay` | 0ms |  |
| SKIP(write) | ai_agent | POST | `/pay/wallet_adjust_detail` | 0ms |  |
| SKIP(write) | automation | POST | `/advertiser_label_relation/bind` | 0ms |  |
| SKIP(write) | automation | POST | `/advertiser_label_relation/unbind` | 0ms |  |
| SKIP(write) | automation | POST | `/label/add` | 0ms |  |
| SKIP(write) | automation | POST | `/label/del` | 0ms |  |
| SKIP(write) | automation | POST | `/label_category/add` | 0ms |  |
| SKIP(write) | automation | POST | `/label_category/del` | 0ms |  |
| SKIP(write) | automation | POST | `/material_group/add` | 0ms |  |
| SKIP(write) | automation | POST | `/material_group/del` | 0ms |  |
| SKIP(write) | automation | POST | `/material_group/edit` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/add` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/bind` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/delete` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/edit` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/status/update` | 0ms |  |
| SKIP(write) | automation | POST | `/tactic/unbind` | 0ms |  |
| SKIP(write) | finance | POST | `/ad_group/status/update` | 0ms |  |
| SKIP(write) | finance | POST | `/ad_group/update` | 0ms |  |
| SKIP(write) | finance | POST | `/bc/create` | 0ms |  |
| SKIP(write) | finance | POST | `/campaign/status/update` | 0ms |  |
| SKIP(write) | finance | POST | `/campaign/update` | 0ms |  |
| SKIP(write) | finance | POST | `/copy/suggest` | 0ms |  |
| SKIP(write) | finance | POST | `/creative/remove` | 0ms |  |
| SKIP(write) | finance | POST | `/finance/billset/update` | 0ms |  |
| SKIP(write) | finance | POST | `/finance/rebate/company_detail/confirm` | 0ms |  |
| SKIP(write) | finance | POST | `/finance/rebate/recharge` | 0ms |  |
| SKIP(write) | finance | POST | `/pay/adv_amount_clear` | 0ms |  |
| SKIP(write) | finance | POST | `/pay/adv_recharge` | 0ms |  |
| SKIP(write) | finance | POST | `/pay/adv_reduce` | 0ms |  |
| SKIP(write) | finance | POST | `/pay/coupon_recharge` | 0ms |  |
| SKIP(write) | finance | POST | `/session/create` | 0ms |  |
| SKIP(write) | finance | POST | `/session/delete` | 0ms |  |
| SKIP(write) | finance | POST | `/session/update` | 0ms |  |
| SKIP(write) | finance | POST | `/submit` | 0ms |  |
| SKIP(write) | finance | POST | `/update` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/online_cogolinks` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/online_worldfrist` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/trade_list` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/trade_list/export` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/transfer` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/pay/transfer_detail` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/wallet/company/exchange` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/wallet/currency/exchange` | 0ms |  |
| SKIP(write) | finance_bff | POST | `/wallet/wallet/exchange` | 0ms |  |
| SKIP(write) | front | POST | `/auth/edit_company_menu` | 0ms |  |
| SKIP(write) | front | POST | `/company/change_custom_passwd` | 0ms |  |
| SKIP(write) | front | POST | `/company/edit` | 0ms |  |
| SKIP(write) | front | POST | `/notice/mark_read` | 0ms |  |
| SKIP(write) | front | POST | `/sign/contract/download` | 0ms |  |
| SKIP(write) | front | POST | `/sign/flow/list` | 0ms |  |
| SKIP(write) | front | POST | `/sign/need` | 0ms |  |
| SKIP(write) | front | POST | `/sign/recission/addr/acquire` | 0ms |  |
| SKIP(write) | front | POST | `/sign/tosign/addr/acquire` | 0ms |  |
| SKIP(write) | front | POST | `/user/edit` | 0ms |  |
| SKIP(write) | front | POST | `/user/email/update` | 0ms |  |
| SKIP(write) | front | POST | `/user/forget_pass` | 0ms |  |
| SKIP(write) | front | POST | `/user/login` | 0ms |  |
| SKIP(write) | front | POST | `/user/login/qrcode/create` | 0ms |  |
| SKIP(write) | front | POST | `/user/login/qrcode/status` | 0ms |  |
| SKIP(write) | front | POST | `/user/phone/update` | 0ms |  |
| SKIP(write) | front | POST | `/user/register` | 0ms |  |
| SKIP(write) | front | GET | `/user/send_code` | 0ms |  |
| SKIP(write) | front | POST | `/user/upt_pass` | 0ms |  |