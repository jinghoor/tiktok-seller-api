"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class FinanceAPI:
    """财务 finance-v1.aiadfly.com —— 结算、账单、返点"""

    BACKENDS = ('finance',)
    _GROUP_DEFAULT = 'finance'

    def __init__(self, t: Transport):
        self._t = t

    def update_google_app_ad_group_status(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad_group/status/update  (前端 updateGoogleAppAdGroupStatusAPI)"""
        return self._t.post('finance', "/ad_group/status/update", body, **kw)

    def update_google_app_ad_group_quick_edit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ad_group/update  (前端 updateGoogleAppAdGroupQuickEditAPI)"""
        return self._t.post('finance', "/ad_group/update", body, **kw)

    def add_custom_anchor_video(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /add_custom_anchor_video  (前端 addCustomAnchorVideoAPI)"""
        return self._t.post('finance', "/add_custom_anchor_video", body, **kw)

    def get_adv_consume_list_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/adv_consume_report  (前端 getAdvConsumeListNew)"""
        return self._t.post('finance', "/advertiser/adv_consume_report", body, **kw)

    def get_fb_adv_consume_list_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/adv_fb_consume_report  (前端 getFBAdvConsumeListNew)"""
        return self._t.post('finance', "/advertiser/adv_fb_consume_report", body, **kw)

    def bind_adv(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bind_adv  (前端 bindAdvAPI)"""
        return self._t.post('finance', "/advertiser/bind_adv", body, **kw)

    def bind_adv_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bind_adv_list  (前端 bindAdvListAPI)"""
        return self._t.post('finance', "/advertiser/bind_adv_list", body, **kw)

    def bind_adv_options_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bind_adv_option_list  (前端 bindAdvOptionsListAPI)"""
        return self._t.post('finance', "/advertiser/bind_adv_option_list", body, **kw)

    def un_bind_adv(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/unbind_adv  (前端 unBindAdvAPI)"""
        return self._t.post('finance', "/advertiser/unbind_adv", body, **kw)

    def list_bound_google_advertisers(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertisers/list  (前端 listBoundGoogleAdvertisersAPI)"""
        return self._t.post('finance', "/advertisers/list", body, **kw)

    def create_bc(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /bc/create  (前端 createBCAPI)"""
        return self._t.post('finance', "/bc/create", body, **kw)

    def get_google_app_campaign_quick_edit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaign/get  (前端 getGoogleAppCampaignQuickEditAPI)"""
        return self._t.post('finance', "/campaign/get", body, **kw)

    def update_google_app_campaign_status(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaign/status/update  (前端 updateGoogleAppCampaignStatusAPI)"""
        return self._t.post('finance', "/campaign/status/update", body, **kw)

    def update_google_app_campaign_quick_edit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaign/update  (前端 updateGoogleAppCampaignQuickEditAPI)"""
        return self._t.post('finance', "/campaign/update", body, **kw)

    def export_gmvmax_ad_campaigns(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaigns/export  (前端 exportGmvmaxAdCampaignsAPI)"""
        return self._t.post('finance', "/campaigns/export", body, **kw)

    def list_gmvmax_campaigns(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /campaigns/list  (前端 listGmvmaxCampaignsAPI)"""
        return self._t.post('finance', "/campaigns/list", body, **kw)

    def list_google_app_conversion_actions(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /conversion_actions/list  (前端 listGoogleAppConversionActionsAPI)"""
        return self._t.post('finance', "/conversion_actions/list", body, **kw)

    def suggest_google_app_ads_copy(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /copy/suggest  (前端 suggestGoogleAppAdsCopyAPI)"""
        return self._t.post('finance', "/copy/suggest", body, **kw)

    def remove_custom_anchor_video(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /creative/remove  (前端 removeCustomAnchorVideoAPI)"""
        return self._t.post('finance', "/creative/remove", body, **kw)

    def export_gmvmax_ad_accounts(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /export  (前端 exportGmvmaxAdAccountsAPI)"""
        return self._t.post('finance', "/export", body, **kw)

    def get_payable_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/account/payable/detail  (前端 getPayableDetailAPI)
        实测必需字段(1 个,已实调跑通): company_ex_id:string
        可用 body 样例: {"company_ex_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('finance', "/finance/account/payable/detail", body, **kw)

    def get_customer_bill_set_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/billset/find  (前端 getCustomerBillSetInfoAPI)"""
        return self._t.post('finance', "/finance/billset/find", body, **kw)

    def get_bill_set_need(self, **kw: Any) -> Any:
        """GET /finance/billset/need  (前端 getBillSetNeedAPI)  params 走 query string"""
        return self._t.get('finance', "/finance/billset/need", **kw)

    def update_bill_set_need(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/billset/update  (前端 updateBillSetNeedAPI)"""
        return self._t.post('finance', "/finance/billset/update", body, **kw)

    def list_company_rebate_detail_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/company_detail/list  (前端 listCompanyRebateDetailFrontAPI)"""
        return self._t.post('finance', "/finance/company_detail/list", body, **kw)

    def list_adv_rebate_detail_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/adv_detail/list  (前端 listAdvRebateDetailFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/adv_detail/list", body, **kw)

    def rebate_confirm_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/company_detail/confirm  (前端 rebateConfirmFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/company_detail/confirm", body, **kw)

    def rebate_export_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/export  (前端 rebateExportFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/export", body, **kw)

    def rebate_recharge_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/recharge  (前端 rebateRechargeFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/recharge", body, **kw)

    def list_rebate_rule_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/rule/list  (前端 listRebateRuleFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/rule/list", body, **kw)

    def list_rule_rebate_detail_front(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/rebate/rule_detail/list  (前端 listRuleRebateDetailFrontAPI)"""
        return self._t.post('finance', "/finance/rebate/rule_detail/list", body, **kw)

    def get_settlement_detail_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/settlement/detail/export  (前端 getSettlementDetailExportAPI)"""
        return self._t.post('finance', "/finance/settlement/detail/export", body, **kw)

    def get_settlement_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/settlement/detail/list  (前端 getSettlementDetailAPI)"""
        return self._t.post('finance', "/finance/settlement/detail/list", body, **kw)

    def get_settlement_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/settlement/list  (前端 getSettlementListAPI)"""
        return self._t.post('finance', "/finance/settlement/list", body, **kw)

    def get_settlement_overdue_t7(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /finance/settlement/overdue-t7  (前端 getSettlementOverdueT7API)"""
        return self._t.post('finance', "/finance/settlement/overdue-t7", body, **kw)

    def suggest_google_campaign_geo_targets(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /geo_targets/suggest  (前端 suggestGoogleCampaignGeoTargetsAPI)"""
        return self._t.post('finance', "/geo_targets/suggest", body, **kw)

    def get_gmvmax_product_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /group_items  (前端 getGmvmaxProductListAPI)"""
        return self._t.post('finance', "/group_items", body, **kw)

    def list_google_campaign_image_assets(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /image_assets/list  (前端 listGoogleCampaignImageAssetsAPI)"""
        return self._t.post('finance', "/image_assets/list", body, **kw)

    def list_google_campaign_languages(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /languages/list  (前端 listGoogleCampaignLanguagesAPI)"""
        return self._t.post('finance', "/languages/list", body, **kw)

    def list_gmvmax_ad_accounts(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /list  (前端 listGmvmaxAdAccountsAPI)"""
        return self._t.post('finance', "/list", body, **kw)

    def pay_adv_amount_clear(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_amount_clear  (前端 payAdvAmountClearAPI)"""
        return self._t.post('finance', "/pay/adv_amount_clear", body, **kw)

    def pay_adv_recharge(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_recharge  (前端 payAdvRechargeAPI$1)"""
        return self._t.post('finance', "/pay/adv_recharge", body, **kw)

    def pay_adv_deduct(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_reduce  (前端 payAdvDeductAPI)"""
        return self._t.post('finance', "/pay/adv_reduce", body, **kw)

    def pay_coupon_recharge(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/coupon_recharge  (前端 payCouponRechargeAPI)"""
        return self._t.post('finance', "/pay/coupon_recharge", body, **kw)

    def list_google_play_install_conversion_actions(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /play_install_conversion_actions/list  (前端 listGooglePlayInstallConversionActionsAPI)"""
        return self._t.post('finance', "/play_install_conversion_actions/list", body, **kw)

    def get_gmvmax_campaign_series_chat(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /series/chart  (前端 getGmvmaxCampaignSeriesChatAPI)"""
        return self._t.post('finance', "/series/chart", body, **kw)

    def get_gmvmax_series_summary(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /series/summary  (前端 getGmvmaxSeriesSummaryAPI)"""
        return self._t.post('finance', "/series/summary", body, **kw)

    def create_gmvmax_session(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /session/create  (前端 createGmvmaxSessionAPI)"""
        return self._t.post('finance', "/session/create", body, **kw)

    def delete_gmvmax_session(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /session/delete  (前端 deleteGmvmaxSessionAPI)"""
        return self._t.post('finance', "/session/delete", body, **kw)

    def get_gmvmax_session_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /session/list  (前端 getGmvmaxSessionListAPI)"""
        return self._t.post('finance', "/session/list", body, **kw)

    def update_gmvmax_session(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /session/update  (前端 updateGmvmaxSessionAPI)"""
        return self._t.post('finance', "/session/update", body, **kw)

    def export_google_app_ads_account_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/account/export  (前端 exportGoogleAppAdsAccountSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/account/export", body, **kw)

    def list_google_app_ads_account_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/account/list  (前端 listGoogleAppAdsAccountSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/account/list", body, **kw)

    def export_google_app_ads_ad_asset_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/ad_asset_snapshots/export  (前端 exportGoogleAppAdsAdAssetSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/ad_asset_snapshots/export", body, **kw)

    def list_google_app_ads_ad_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/ad_asset_snapshots/list  (前端 listGoogleAppAdsAdSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/ad_asset_snapshots/list", body, **kw)

    def export_google_app_ads_ad_group_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/ad_group/export  (前端 exportGoogleAppAdsAdGroupSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/ad_group/export", body, **kw)

    def list_google_app_ads_ad_group_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/ad_group/list  (前端 listGoogleAppAdsAdGroupSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/ad_group/list", body, **kw)

    def export_google_app_ads_campaign_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/campaign/export  (前端 exportGoogleAppAdsCampaignSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/campaign/export", body, **kw)

    def list_google_app_ads_campaign_snapshots(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /snapshots/campaign/list  (前端 listGoogleAppAdsCampaignSnapshotsAPI)"""
        return self._t.post('finance', "/snapshots/campaign/list", body, **kw)

    def submit_google_app_ads(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /submit  (前端 submitGoogleAppAdsAPI)"""
        return self._t.post('finance', "/submit", body, **kw)

    def get_gmvmax_ad_account_summary(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /summary  (前端 getGmvmaxAdAccountSummaryAPI)"""
        return self._t.post('finance', "/summary", body, **kw)

    def update_gmvmax_campaign_status(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/campaign_modify  (前端 updateGmvmaxCampaignStatusAPI)"""
        return self._t.post('finance', "/tiktok/campaign_modify", body, **kw)

    def get_ad_data_panel_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /tiktok/panel_report  (前端 getAdDataPanelListAPI)"""
        return self._t.post('finance', "/tiktok/panel_report", body, **kw)

    def update_gmvmax_campaign(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /update  (前端 updateGmvmaxCampaignAPI)"""
        return self._t.post('finance', "/update", body, **kw)

    def list_google_campaign_video_assets(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /video_assets/list  (前端 listGoogleCampaignVideoAssetsAPI)"""
        return self._t.post('finance', "/video_assets/list", body, **kw)

    def get_google_you_tube_video(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /youtube_video/get  (前端 getGoogleYouTubeVideoAPI)"""
        return self._t.post('finance', "/youtube_video/get", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
