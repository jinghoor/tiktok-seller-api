"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class AiAgentAPI:
    """AI Agent ai-agent-v1.aiadfly.com —— 对话、开户引导、GMVmax/VSA 创建链路"""

    BACKENDS = ('ai_agent',)
    _GROUP_DEFAULT = 'ai_agent'

    def __init__(self, t: Transport):
        self._t = t

    def adv_bc_bind(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/adv_bc_bind  (前端 AdvBcBindAPI)"""
        return self._t.post('ai_agent', "/advertiser/adv_bc_bind", body, **kw)

    def get_bind_bc_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/adv_bc_bind_list  (前端 getBindBCListAPI)"""
        return self._t.post('ai_agent', "/advertiser/adv_bc_bind_list", body, **kw)

    def get_bind_bc_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/adv_bc_bind_list/export  (前端 getBindBCListExportAPI)"""
        return self._t.post('ai_agent', "/advertiser/adv_bc_bind_list/export", body, **kw)

    def get_un_bind_bc_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /advertiser/bc_un_bind_list  (前端 getUnBindBCListAPI)"""
        return self._t.post('ai_agent', "/advertiser/bc_un_bind_list", body, **kw)

    def get_ad_data_panel_list_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/chat/history  (前端 getAdDataPanelListNewAPI)
        实测必需字段(1 个,已实调跑通): session_id:string
        可用 body 样例: {"page": 1, "page_size": 5, "session_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('ai_agent', "/ai_agent/market/chat/history", body, **kw)

    def get_chat_list(self, **kw: Any) -> Any:
        """GET /ai_agent/market/chat/list  (前端 getChatList)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/market/chat/list", **kw)

    def re_gene_desc_creative(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/creative/re_gene_desc  (前端 reGeneDescCreativeAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/creative/re_gene_desc", body, **kw)

    def regene_image(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/image/regene  (前端 regeneImageAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/image/regene", body, **kw)

    def reupload_image(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/image/reupload  (前端 reuploadImageAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/image/reupload", body, **kw)

    def message_save(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/message/save  (前端 messageSaveAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/message/save", body, **kw)

    def create_session_id_new(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/session_id/create  (前端 createSessionIdNewAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/session_id/create", body, **kw)

    def get_session_id_new(self, **kw: Any) -> Any:
        """GET /ai_agent/market/session_id/get  (前端 getSessionIdNewAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/market/session_id/get", **kw)

    def stop_stream(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/stream/stop  (前端 stopStreamAPI)"""
        return self._t.post('ai_agent', "/ai_agent/market/stream/stop", body, **kw)

    def get_video_batch(self, **kw: Any) -> Any:
        """GET /ai_agent/market/video/batch  (前端 getVideoBatchAPI)  params 走 query string
        实测必需字段(1 个,字段已摸清): batch_id:string
        可用 body 样例: {"batch_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.get('ai_agent', "/ai_agent/market/video/batch", **kw)

    def get_video_list(self, **kw: Any) -> Any:
        """GET /ai_agent/market/video/list  (前端 getVideoListAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/market/video/list", **kw)

    def terminate_video(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/market/video/terminate  (前端 terminateVideoAPI)
        实测必需字段(1 个,字段已摸清): video_id:string
        可用 body 样例: {"page": 1, "page_size": 5, "video_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('ai_agent', "/ai_agent/market/video/terminate", body, **kw)

    def get_campaign_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/campaign/list  (前端 getCampaignListAPI)
        实测必需字段(2 个,字段已摸清): message_id:string, ad_type:string
        可用 body 样例: {"ad_type": "x", "message_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/campaign/list", body, **kw)

    def get_gmv_max_identity_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/identity/list  (前端 getGMVMaxIdentityList)
        实测必需字段(3 个,字段已摸清): advertiser_id:string, store_id:string, store_authorized_bc_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "store_authorized_bc_id": "7689XXXXXXXXXX05", "store_id": "8657XXXXXXXXXX38"}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/identity/list", body, **kw)

    def check_occupied_custom_shop_ads(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list  (前端 checkOccupiedCustomShopAdsAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list", body, **kw)

    def ad_gmv_max_store_config(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/store/config  (前端 adGmvMaxStoreConfigAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/store/config", body, **kw)

    def get_gmv_max_store_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/store/list  (前端 getGMVMaxStoreList)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/store/list", body, **kw)

    def get_gvm_product_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/store/product/list  (前端 getGVMProductListAPI)
        实测必需字段(3 个,字段已摸清): advertiser_id:string, bc_id:string, store_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "store_id": "8657XXXXXXXXXX38"}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/store/product/list", body, **kw)

    def validate_gmv_max_store_id(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/gmv_max/store_id/validate  (前端 validateGmvMaxStoreIdAPI)
        实测必需字段(3 个,字段已摸清): advertiser_id:string, store_id:string, tt_auth_id:number
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "store_id": "8657XXXXXXXXXX38", "tt_auth_id": 1}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/gmv_max/store_id/validate", body, **kw)

    def reset_guide_ad_create(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/guide/ad_create/reset  (前端 resetGuideAdCreateAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/ad/guide/ad_create/reset", body, **kw)

    def reset_guide_adv_apply(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/guide/adv_apply/reset  (前端 resetGuideAdvApplyAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/ad/guide/adv_apply/reset", body, **kw)

    def get_tik_tok_account_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/tt/account/list  (前端 getTikTokAccountListAPI)
        实测必需字段(2 个,字段已摸清): bc_id:string, tt_auth_id:number
        可用 body 样例: {"bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "tt_auth_id": 1}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/tt/account/list", body, **kw)

    def get_tik_tok_asset_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/tt/asset/list  (前端 getTikTokAssetListAPI)
        实测必需字段(3 个,字段已摸清): bc_id:string, asset_type:enum, tt_auth_id:number
        可用 body 样例: {"asset_type": "ADVERTISER", "bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "tt_auth_id": 1}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/tt/asset/list", body, **kw)

    def get_identity_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/identity/get  (前端 getIdentityListAPI)
        实测必需字段(2 个,字段已摸清): advertiser_id:string, identity_authorized_bc_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "identity_authorized_bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/identity/get", body, **kw)

    def get_interest_category_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/interest_category/list  (前端 getInterestCategoryListAPI)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/interest_category/list", body, **kw)

    def get_ad_create_public_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/public_info/get  (前端 getAdCreatePublicInfo)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/public_info/get", body, **kw)

    def get_region_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/region/search  (前端 getRegionListAPI)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/region/search", body, **kw)

    def get_store_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/store/list  (前端 getStoreListAPI)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/store/list", body, **kw)

    def get_vsa_product_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/store/product/list  (前端 getVSAProductListAPI)
        实测必需字段(3 个,字段已摸清): advertiser_id:string, bc_id:string, store_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "bc_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5, "store_id": "8657XXXXXXXXXX38"}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/store/product/list", body, **kw)

    def get_vedio(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ad/vsa/video/search  (前端 getVedioAPI)
        实测必需字段(1 个,字段已摸清): advertiser_id:string
        可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ad/vsa/video/search", body, **kw)

    def get_advertiser_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/adv/list  (前端 getAdvertiserListAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/adv/list", body, **kw)

    def get_ad_data_panel_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/chat/history  (前端 getAdDataPanelListAPI$1)
        实测必需字段(1 个,已实调跑通): session_id:string
        可用 body 样例: {"page": 1, "page_size": 5, "session_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/chat/history", body, **kw)

    def get_chat_list_1(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/chat/list  (前端 getChatList$1)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/chat/list", **kw)

    def get_cloud_file_url(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/file/cloud_url/get  (前端 getCloudFileUrlAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/file/cloud_url/get", body, **kw)

    def adv_recharge_submit(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/guide/adv_recharge  (前端 advRechargeSubmitAPI)
        实测必需字段(1 个,字段已摸清): amount:number
        可用 body 样例: {"amount": 1, "page": 1, "page_size": 5}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/guide/adv_recharge", body, **kw)

    def message_feedback(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/message/feedback  (前端 messageFeedbackAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/message/feedback", body, **kw)

    def message_get(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/message/get  (前端 messageGetAPI)  params 走 query string
        实测必需字段(1 个,字段已摸清): message_id:string
        可用 body 样例: {"message_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.get('ai_agent', "/ai_agent/v1/message/get", **kw)

    def get_message_prompt(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/message/get_prompt  (前端 getMessagePromptAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/message/get_prompt", **kw)

    def reset_message_prompt(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/message/reset  (前端 resetMessagePromptAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/message/reset", body, **kw)

    def message_save_1(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/message/save  (前端 messageSaveAPI$1)"""
        return self._t.post('ai_agent', "/ai_agent/v1/message/save", body, **kw)

    def ocr_recognition(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/ocr  (前端 ocrRecognitionAPI)
        实测必需字段(2 个,字段已摸清): url:string, type:enum
        可用 body 样例: {"page": 1, "page_size": 5, "type": "1", "url": "x"}
        """
        return self._t.post('ai_agent', "/ai_agent/v1/ocr", body, **kw)

    def generate_wechat_qrcode(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/qrcode/generate  (前端 generateWechatQrcodeAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/qrcode/generate", body, **kw)

    def query_wechat_qrcode(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/qrcode/query  (前端 queryWechatQrcodeAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/qrcode/query", body, **kw)

    def get_rebate_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/rebate/list  (前端 getRebateListAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/rebate/list", body, **kw)

    def create_session_id(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/session_id/create  (前端 createSessionIdAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/session_id/create", body, **kw)

    def get_session_id(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/session_id/get  (前端 getSessionIdAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/session_id/get", **kw)

    def get_contract_sign_addr(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/sign/draft/addr/acquire  (前端 getContractSignAddr$1)"""
        return self._t.post('ai_agent', "/ai_agent/v1/sign/draft/addr/acquire", body, **kw)

    def get_support_info(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/support/info  (前端 getSupportInfo)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/support/info", **kw)

    def submit_user_recharge_agreement(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /ai_agent/v1/user/confirm_first_recharge  (前端 submitUserRechargeAgreementAPI)"""
        return self._t.post('ai_agent', "/ai_agent/v1/user/confirm_first_recharge", body, **kw)

    def guide_task(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/user/guide_task  (前端 guideTaskAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/user/guide_task", **kw)

    def get_user_profile(self, **kw: Any) -> Any:
        """GET /ai_agent/v1/user/profile  (前端 getUserProfileAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/ai_agent/v1/user/profile", **kw)

    def get_pay_adv_amount_clear_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_amount_clear_list  (前端 getPayAdvAmountClearListAPI)"""
        return self._t.post('ai_agent', "/pay/adv_amount_clear_list", body, **kw)

    def get_pay_adv_amount_clear_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_amount_clear_list/export  (前端 getPayAdvAmountClearListExportAPI)"""
        return self._t.post('ai_agent', "/pay/adv_amount_clear_list/export", body, **kw)

    def get_pay_adv_recharge_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_recharge_list  (前端 getPayAdvRechargeListAPI)"""
        return self._t.post('ai_agent', "/pay/adv_recharge_list", body, **kw)

    def get_pay_adv_recharge_list_export(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/adv_recharge_list/export  (前端 getPayAdvRechargeListExportAPI)"""
        return self._t.post('ai_agent', "/pay/adv_recharge_list/export", body, **kw)

    def airwallex_pay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/airpay  (前端 airwallexPayAPI)"""
        return self._t.post('ai_agent', "/pay/airpay", body, **kw)

    def get_bill_tips(self, **kw: Any) -> Any:
        """GET /pay/bill_tips  (前端 getBillTipsAPI)  params 走 query string"""
        return self._t.get('ai_agent', "/pay/bill_tips", **kw)

    def lianlian_pay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/llpay  (前端 lianlianPayAPI)"""
        return self._t.post('ai_agent', "/pay/llpay", body, **kw)

    def get_pay_detal(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/pay_detail  (前端 getPayDetalAPI)"""
        return self._t.post('ai_agent', "/pay/pay_detail", body, **kw)

    def pingpong_pay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/pppay  (前端 pingpongPayAPI)"""
        return self._t.post('ai_agent', "/pay/pppay", body, **kw)

    def get_wallet_adjust_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/wallet_adjust_detail  (前端 getWalletAdjustDetailAPI)"""
        return self._t.post('ai_agent', "/pay/wallet_adjust_detail", body, **kw)

    def message_report(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /public/data/report  (前端 messageReportAPI)
        实测必需字段(4 个,字段已摸清): page_id:string, event_type:string, event_code:string, session_id:string
        可用 body 样例: {"event_code": "x", "event_type": "x", "page": 1, "page_id": "7689XXXXXXXXXX05", "page_size": 5, "session_id": "7689XXXXXXXXXX05"}
        """
        return self._t.post('ai_agent', "/public/data/report", body, **kw)

    def update_role_item_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /role_edit  (前端 updateRoleItemInfoAPI)"""
        return self._t.post('ai_agent', "/role_edit", body, **kw)

    def get_role_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /role_list  (前端 getRoleListAPI)"""
        return self._t.post('ai_agent', "/role_list", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
