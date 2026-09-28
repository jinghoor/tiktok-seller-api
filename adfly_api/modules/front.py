"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class FrontAPI:
    """前端主服务 front-v1.aiadfly.com —— 登录/用户/公司/菜单/通知/快捷入口"""

    BACKENDS = ('front',)
    _GROUP_DEFAULT = 'front'

    def __init__(self, t: Transport):
        self._t = t

    def edit_company_menu(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /auth/edit_company_menu  (前端 editCompanyMenuAPI)"""
        return self._t.post('front', "/auth/edit_company_menu", body, **kw)

    def get_company_menu(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /auth/get_company_menu  (前端 getCompanyMenuAPI)"""
        return self._t.post('front', "/auth/get_company_menu", body, **kw)

    def list_google_auth(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /auth/list  (前端 listGoogleAuthAPI)"""
        return self._t.post('front', "/auth/list", body, **kw)

    def batch_edit_company_menu(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /auth/multi_edit_company_menu  (前端 batchEditCompanyMenuAPI)"""
        return self._t.post('front', "/auth/multi_edit_company_menu", body, **kw)

    def change_custom_passwd(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /company/change_custom_passwd  (前端 changeCustomPasswdAPI)"""
        return self._t.post('front', "/company/change_custom_passwd", body, **kw)

    def get_country_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /company/country_list  (前端 getCountryList)"""
        return self._t.post('front', "/company/country_list", body, **kw)

    def get_custom_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /company/custom_list  (前端 getCustomListAPI)"""
        return self._t.post('front', "/company/custom_list", body, **kw)

    def update_custom_list_item(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /company/edit  (前端 updateCustomListItemAPI)"""
        return self._t.post('front', "/company/edit", body, **kw)

    def get_port_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /company/get_ports_list  (前端 getPortList)"""
        return self._t.post('front', "/company/get_ports_list", body, **kw)

    def get_notice_archive_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /notice/archive_list  (前端 getNoticeArchiveListAPI)"""
        return self._t.post('front', "/notice/archive_list", body, **kw)

    def get_notice_bell_list(self, **kw: Any) -> Any:
        """GET /notice/bell_list  (前端 getNoticeBellListAPI)  params 走 query string"""
        return self._t.get('front', "/notice/bell_list", **kw)

    def read_notice_bell(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /notice/mark_read  (前端 readNoticeBellAPI)"""
        return self._t.post('front', "/notice/mark_read", body, **kw)

    def download_contract(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /sign/contract/download  (前端 downloadContractAPI)"""
        return self._t.post('front', "/sign/contract/download", body, **kw)

    def get_contract_sign_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /sign/flow/list  (前端 getContractSignList)"""
        return self._t.post('front', "/sign/flow/list", body, **kw)

    def get_if_need_sign(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /sign/need  (前端 getIfNeedSign)"""
        return self._t.post('front', "/sign/need", body, **kw)

    def get_contract_aborted_addr(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /sign/recission/addr/acquire  (前端 getContractAbortedAddr)"""
        return self._t.post('front', "/sign/recission/addr/acquire", body, **kw)

    def get_contract_sign_addr(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /sign/tosign/addr/acquire  (前端 getContractSignAddr)"""
        return self._t.post('front', "/sign/tosign/addr/acquire", body, **kw)

    def login_check_fa(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/check_fa  (前端 loginCheckFaAPI)"""
        return self._t.post('front', "/user/check_fa", body, **kw)

    def update_member_info(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/edit  (前端 updateMemberInfoAPI)"""
        return self._t.post('front', "/user/edit", body, **kw)

    def update_email(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/email/update  (前端 updateEmail)"""
        return self._t.post('front', "/user/email/update", body, **kw)

    def forgot_pwd(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/forget_pass  (前端 forgotPwd)"""
        return self._t.post('front', "/user/forget_pass", body, **kw)

    def get_business(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/get_business  (前端 getBusiness)"""
        return self._t.post('front', "/user/get_business", body, **kw)

    def get_user_info(self, **kw: Any) -> Any:
        """GET /user/info  (前端 getUserInfoAPI)  params 走 query string"""
        return self._t.get('front', "/user/info", **kw)

    def get_member_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/list  (前端 getMemberListAPI)"""
        return self._t.post('front', "/user/list", body, **kw)

    def login(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/login  (前端 login$2)"""
        return self._t.post('front', "/user/login", body, **kw)

    def create_qr_login(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/login/qrcode/create  (前端 createQRLoginAPI)"""
        return self._t.post('front', "/user/login/qrcode/create", body, **kw)

    def query_qr_login_status(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/login/qrcode/status  (前端 queryQRLoginStatusAPI)"""
        return self._t.post('front', "/user/login/qrcode/status", body, **kw)

    def update_phone(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/phone/update  (前端 updatePhone)"""
        return self._t.post('front', "/user/phone/update", body, **kw)

    def register(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/register  (前端 registerAPI)"""
        return self._t.post('front', "/user/register", body, **kw)

    def send_code(self, **kw: Any) -> Any:
        """GET /user/send_code  (前端 sendCodeAPI)  params 走 query string"""
        return self._t.get('front', "/user/send_code", **kw)

    def update_pwd(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /user/upt_pass  (前端 updatePwd)"""
        return self._t.post('front', "/user/upt_pass", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
