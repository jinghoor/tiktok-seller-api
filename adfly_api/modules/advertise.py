"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class AdvertiseAPI:
    """广告 BFF advertise-bff-v1.aiadfly.com —— 广告账户、授权、VSA/GMVmax、报表"""

    BACKENDS = ('advertise',)
    _GROUP_DEFAULT = 'advertise'

    def __init__(self, t: Transport):
        self._t = t

    def get_google_app_ad_quick_edit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/get  (前端 getGoogleAppAdQuickEditAPI)"""
        return self._t.post('advertise', "/ad/get", body, **kw)

    def delete_gmv_max_store_config(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/gmv_max_store_config/delete  (前端 deleteGmvMaxStoreConfigAPI)"""
        return self._t.post('advertise', "/ad/gmv_max_store_config/delete", body, **kw)

    def get_gmv_max_store_config(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/gmv_max_store_config/get  (前端 getGmvMaxStoreConfigAPI)
        实测必需字段(1 个,字段已摸清): gmv_max_store_config_id:number
        可用 body 样例: {"gmv_max_store_config_id": 1, "page": 1, "page_size": 5}
        """
        return self._t.post('advertise', "/ad/gmv_max_store_config/get", body, **kw)

    def list_gmv_max_store_config(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/gmv_max_store_config/list  (前端 listGmvMaxStoreConfigAPI)"""
        return self._t.post('advertise', "/ad/gmv_max_store_config/list", body, **kw)

    def list_gmv_max_store_config_by_store_id(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/gmv_max_store_config/list_by_store_id  (前端 listGmvMaxStoreConfigByStoreIdAPI)"""
        return self._t.post('advertise', "/ad/gmv_max_store_config/list_by_store_id", body, **kw)

    def get_ad_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/list  (前端 getAdListAPI)"""
        return self._t.post('advertise', "/ad/list", body, **kw)

    def get_pixel_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/pixel/list  (前端 getPixelListAPI)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('advertise', "/ad/pixel/list", body, **kw)

    def search_app_applications(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/store_app_info/get  (前端 searchAppApplicationsAPI)
        实测必需字段(2 个,字段已摸清): query:string, country:string
        可用 body 样例: {"country": "x", "page": 1, "page_size": 5, "query": "x"}
        """
        return self._t.post('advertise', "/ad/store_app_info/get", body, **kw)

    def update_google_app_ad_quick_edit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad/update  (前端 updateGoogleAppAdQuickEditAPI)"""
        return self._t.post('advertise', "/ad/update", body, **kw)

    def advertiser_apply(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/apply  (前端 AdvertiserApplyAPI)"""
        return self._t.post('advertise', "/advertiser/apply", body, **kw)

    def get_advertiser_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/apply_detail  (前端 getAdvertiserDetailAPI)"""
        return self._t.post('advertise', "/advertiser/apply_detail", body, **kw)

    def get_advertiser_apply_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/apply_list  (前端 getAdvertiserApplyListAPI)"""
        return self._t.post('advertise', "/advertiser/apply_list", body, **kw)

    def get_advertiser_apply_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/apply_list/export  (前端 getAdvertiserApplyListExportAPI)"""
        return self._t.post('advertise', "/advertiser/apply_list/export", body, **kw)

    def account_un_bind_bc_multi(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bc_un_bind_multi  (前端 accountUnBindBcMultiAPI)"""
        return self._t.post('advertise', "/advertiser/bc_un_bind_multi", body, **kw)

    def account_un_bind_bc_single(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bc_un_bind_single  (前端 accountUnBindBcSingleAPI)"""
        return self._t.post('advertise', "/advertiser/bc_un_bind_single", body, **kw)

    def get_advertiser_config(self, **kw: Any) -> Any:
        """GET /advertiser/config  (前端 getAdvertiserConfig)  params 走 query string"""
        return self._t.get('advertise', "/advertiser/config", **kw)

    def get_apply_limit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/get_apply_limit_num  (前端 getApplyLimitAPI)"""
        return self._t.post('advertise', "/advertiser/get_apply_limit_num", body, **kw)

    def get_account_bind_bc_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/get_bind_bc  (前端 getAccountBindBcListAPI)"""
        return self._t.post('advertise', "/advertiser/get_bind_bc", body, **kw)

    def get_panda_token(self, **kw: Any) -> Any:
        """GET /advertiser/get_panda_token  (前端 getPandaTokenAPI)  params 走 query string"""
        return self._t.get('advertise', "/advertiser/get_panda_token", **kw)

    def get_advertiser_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/list  (前端 getAdvertiserListAPI$2)"""
        return self._t.post('advertise', "/advertiser/list", body, **kw)

    def get_advertiser_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/list/export  (前端 getAdvertiserListExportAPI)"""
        return self._t.post('advertise', "/advertiser/list/export", body, **kw)

    def get_tiktok_task_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/tt_create_task_list  (前端 getTiktokTaskList)"""
        return self._t.post('advertise', "/advertiser/tt_create_task_list", body, **kw)

    def query_bc_auth(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /bc/query_auth  (前端 queryBCAuthAPI)
        实测必需字段(1 个,已实调跑通): auth_link_ex_id:string
        可用 body 样例: {"auth_link_ex_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('advertise', "/bc/query_auth", body, **kw)

    def file_upload_complete(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /file/complete  (前端 fileUploadCompleteAPI)"""
        return self._t.post('advertise', "/file/complete", body, **kw)

    def get_cos_sign(self, **kw: Any) -> Any:
        """GET /file/sign  (前端 getCosSignAPI)  params 走 query string"""
        return self._t.get('advertise', "/file/sign", **kw)

    def get_gg_adv_consume_list_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /kanban/google_adv_consume  (前端 getGGAdvConsumeListNew)"""
        return self._t.post('advertise', "/kanban/google_adv_consume", body, **kw)

    def export_gg_adv_consume_list_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /kanban/google_adv_consume/export  (前端 exportGGAdvConsumeListNew)"""
        return self._t.post('advertise', "/kanban/google_adv_consume/export", body, **kw)

    def get_tiktok_ad_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/ad_detail  (前端 getTiktokAdDetailAPI)"""
        return self._t.post('advertise', "/tiktok/ad_detail", body, **kw)

    def modify_tiktok_ad(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/ad_modify  (前端 modifyTiktokAdAPI)"""
        return self._t.post('advertise', "/tiktok/ad_modify", body, **kw)

    def get_ad_report_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/ad_report  (前端 getAdReportListAPI)"""
        return self._t.post('advertise', "/tiktok/ad_report", body, **kw)

    def get_ad_report_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/ad_report/export  (前端 getAdReportListExportAPI)"""
        return self._t.post('advertise', "/tiktok/ad_report/export", body, **kw)

    def get_tiktok_ad_group_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adgroup_detail  (前端 getTiktokAdGroupDetailAPI)"""
        return self._t.post('advertise', "/tiktok/adgroup_detail", body, **kw)

    def adgroup_extend(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adgroup_extend  (前端 adgroupExtendAPI)"""
        return self._t.post('advertise', "/tiktok/adgroup_extend", body, **kw)

    def modify_tiktok_ad_group(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adgroup_modify  (前端 modifyTiktokAdGroupAPI)"""
        return self._t.post('advertise', "/tiktok/adgroup_modify", body, **kw)

    def get_ad_group_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adgroup_report  (前端 getAdGroupListAPI)"""
        return self._t.post('advertise', "/tiktok/adgroup_report", body, **kw)

    def get_ad_group_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adgroup_report/export  (前端 getAdGroupListExportAPI)"""
        return self._t.post('advertise', "/tiktok/adgroup_report/export", body, **kw)

    def check_unionpay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/adv_unionpay_check  (前端 checkUnionpay)"""
        return self._t.post('advertise', "/tiktok/adv_unionpay_check", body, **kw)

    def get_advertiser_balance_get(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/advertiser_balance_get  (前端 getAdvertiserBalanceGetAPI)"""
        return self._t.post('advertise', "/tiktok/advertiser_balance_get", body, **kw)

    def get_ad_account_report_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/advertiser_report  (前端 getAdAccountReportListAPI)"""
        return self._t.post('advertise', "/tiktok/advertiser_report", body, **kw)

    def get_ad_account_report_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/advertiser_report/export  (前端 getAdAccountReportListExportAPI)"""
        return self._t.post('advertise', "/tiktok/advertiser_report/export", body, **kw)

    def update_advertiser_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/advertiser_update  (前端 updateAdvertiserInfoAPI)"""
        return self._t.post('advertise', "/tiktok/advertiser_update", body, **kw)

    def get_gmv_max_auth_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/auth_list  (前端 getGMVMaxAuthList)"""
        return self._t.post('advertise', "/tiktok/auth_list", body, **kw)

    def get_tiktok_ad_aampaign_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/campaign_detail  (前端 getTiktokAdAampaignInfoAPI)"""
        return self._t.post('advertise', "/tiktok/campaign_detail", body, **kw)

    def modify_tiktok_ad_aampaign_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/campaign_modify  (前端 modifyTiktokAdAampaignInfoAPI)"""
        return self._t.post('advertise', "/tiktok/campaign_modify", body, **kw)

    def get_ad_campaign_report_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/campaign_report  (前端 getAdCampaignReportListAPI)"""
        return self._t.post('advertise', "/tiktok/campaign_report", body, **kw)

    def get_ad_campaign_report_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/campaign_report/export  (前端 getAdCampaignReportListExportAPI)"""
        return self._t.post('advertise', "/tiktok/campaign_report/export", body, **kw)

    def copy_adv_group(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/copy_advertisement  (前端 copyAdvGroupAPI)"""
        return self._t.post('advertise', "/tiktok/copy_advertisement", body, **kw)

    def create_tiktok_ad(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/create_advertisement  (前端 createTiktokAdAPI)"""
        return self._t.post('advertise', "/tiktok/create_advertisement", body, **kw)

    def batch_create_adv(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/create_advertisement_new  (前端 batchCreateAdvAPI)"""
        return self._t.post('advertise', "/tiktok/create_advertisement_new", body, **kw)

    def get_tt_ad_detail_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/get_ad_detail_list  (前端 getTTAdDetailListAPI)"""
        return self._t.post('advertise', "/tiktok/get_ad_detail_list", body, **kw)

    def get_tiktok_config(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/get_config  (前端 getTiktokConfig)"""
        return self._t.post('advertise', "/tiktok/get_config", body, **kw)

    def get_campaign_options(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/get_opt_campaign  (前端 getCampaignOptionsAPI)"""
        return self._t.post('advertise', "/tiktok/get_opt_campaign", body, **kw)

    def get_tt_video_url_by_item_id(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/get_video_url  (前端 getTTVideoUrlByItemId)"""
        return self._t.post('advertise', "/tiktok/get_video_url", body, **kw)

    def get_vedio(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/get_videos  (前端 getVedioAPI$1)"""
        return self._t.post('advertise', "/tiktok/get_videos", body, **kw)

    def copy_campaign(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/copy  (前端 copyCampaignAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/copy", body, **kw)

    def create_gmv_max_ad(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/create  (前端 createGmvMaxAdAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/create", body, **kw)

    def get_gmv_max_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/detail  (前端 getGMVMaxDetailAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/detail", body, **kw)

    def get_gmv_max_campaign_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/export  (前端 getGMVMaxCampaignExportAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/export", body, **kw)

    def get_campaign_detail_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/get_detail_info  (前端 getCampaignDetailInfoAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/get_detail_info", body, **kw)

    def get_campaign_refresh_time(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/get_refresh_time  (前端 getCampaignRefreshTimeAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/get_refresh_time", body, **kw)

    def get_gmv_max_group_item_report(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/group_item_report  (前端 getGMVMaxGroupItemReportAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/group_item_report", body, **kw)

    def get_gmv_max_identity_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/identity/get  (前端 getGMVMaxIdentityList$1)"""
        return self._t.post('advertise', "/tiktok/gmv_max/identity/get", body, **kw)

    def get_gmv_max_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/list  (前端 getGMVMaxListAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/list", body, **kw)

    def check_occupied_custom_shop_ads(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/occupied_custom_shop_ads/list  (前端 checkOccupiedCustomShopAdsAPI$1)"""
        return self._t.post('advertise', "/tiktok/gmv_max/occupied_custom_shop_ads/list", body, **kw)

    def get_gmv_max_post_item_report(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/post_item_report  (前端 getGMVMaxPostItemReportAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/post_item_report", body, **kw)

    def refresh_campaign(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/refresh  (前端 refreshCampaignAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/refresh", body, **kw)

    def get_gmv_max_store_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/store/list  (前端 getGMVMaxStoreList$1)"""
        return self._t.post('advertise', "/tiktok/gmv_max/store/list", body, **kw)

    def get_shop_ad_usage_check(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/store/shop_ad_usage_check  (前端 getShopAdUsageCheck)"""
        return self._t.post('advertise', "/tiktok/gmv_max/store/shop_ad_usage_check", body, **kw)

    def edit_gmv_max_ad(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/gmv_max/update  (前端 EditGmvMaxAdAPI)"""
        return self._t.post('advertise', "/tiktok/gmv_max/update", body, **kw)

    def get_tiktok_identity(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/identity_get  (前端 getTiktokIdentity)"""
        return self._t.post('advertise', "/tiktok/identity_get", body, **kw)

    def list_tik_tok_admin_store(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tt/admin_store/list  (前端 listTikTokAdminStoreAPI)
        实测必需字段(2 个,已实调跑通): tiktok_auth_id:number, bc_id:string
        可用 body 样例: {"bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "tiktok_auth_id": 1960}
        """
        return self._t.post('advertise', "/tt/admin_store/list", body, **kw)

    def list_tik_tok_auth(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tt/auth/list  (前端 listTikTokAuthAPI)"""
        return self._t.post('advertise', "/tt/auth/list", body, **kw)

    def is_bc_adv_id_bound(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tt/bc/is_adv_bound  (前端 isBcAdvIdBoundAPI)
        实测必需字段(3 个,字段已摸清): bc_id:string, advertiser_id:string, tt_auth_id:number
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "tt_auth_id": 1}
        """
        return self._t.post('advertise', "/tt/bc/is_adv_bound", body, **kw)

    def list_tik_tok_bc(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tt/bc/list  (前端 listTikTokBcAPI)
        实测必需字段(1 个,已实调跑通): tiktok_auth_id:number
        可用 body 样例: {"page": 1, "page_size": 5, "tiktok_auth_id": 1960}
        """
        return self._t.post('advertise', "/tt/bc/list", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
