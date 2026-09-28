"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class FinanceBffAPI:
    """资金 BFF finance-bff-v1.aiadfly.com —— 钱包、充值、优惠券、支付"""

    BACKENDS = ('finance_bff',)
    _GROUP_DEFAULT = 'finance_bff'

    def __init__(self, t: Transport):
        self._t = t

    def get_activity_link_by_code(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /activity_link/by_code  (前端 getActivityLinkByCodeAPI)"""
        return self._t.post('finance_bff', "/activity_link/by_code", body, **kw)

    def get_coupon_detail_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /coupon/detail/list  (前端 getCouponDetailListAPI)"""
        return self._t.post('finance_bff', "/coupon/detail/list", body, **kw)

    def has_coupon_point(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /coupon/has_point  (前端 hasCouponPointAPI)"""
        return self._t.post('finance_bff', "/coupon/has_point", body, **kw)

    def get_coupon_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /coupon/list  (前端 getCouponListAPI)"""
        return self._t.post('finance_bff', "/coupon/list", body, **kw)

    def online_cogolinks_pay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/online_cogolinks  (前端 onlineCogolinksPayAPI)"""
        return self._t.post('finance_bff', "/pay/online_cogolinks", body, **kw)

    def online_worldfrist_pay(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/online_worldfrist  (前端 onlineWorldfristPayAPI)"""
        return self._t.post('finance_bff', "/pay/online_worldfrist", body, **kw)

    def get_trade_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/trade_list  (前端 getTradeListAPI)"""
        return self._t.post('finance_bff', "/pay/trade_list", body, **kw)

    def export_pay_trade_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/trade_list/export  (前端 exportPayTradeListAPI)"""
        return self._t.post('finance_bff', "/pay/trade_list/export", body, **kw)

    def pay_transfer(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/transfer  (前端 payTransferAPI$1)"""
        return self._t.post('finance_bff', "/pay/transfer", body, **kw)

    def get_transfer_detail(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /pay/transfer_detail  (前端 getTransferDetailAPI)"""
        return self._t.post('finance_bff', "/pay/transfer_detail", body, **kw)

    def get_currency_reverse_exchange(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/calculate_reverse_exchange_amount  (前端 getCurrencyReverseExchangeAPI)"""
        return self._t.post('finance_bff', "/wallet/calculate_reverse_exchange_amount", body, **kw)

    def get_company_wallet_exchange(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/company/exchange  (前端 getCompanyWalletExchangeAPI)"""
        return self._t.post('finance_bff', "/wallet/company/exchange", body, **kw)

    def get_currency_exchange(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/currency/exchange  (前端 getCurrencyExchangeAPI)"""
        return self._t.post('finance_bff', "/wallet/currency/exchange", body, **kw)

    def list_wallet(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/list  (前端 listWalletAPI)
        实测必需字段(1 个,已实调跑通): currency:enum
        可用 body 样例: {"currency": "USD", "page": 1, "page_size": 5}
        """
        return self._t.post('finance_bff', "/wallet/list", body, **kw)

    def get_sub_company_wallet_list(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/sub_company/list  (前端 getSubCompanyWalletListAPI)
        实测必需字段(1 个,已实调跑通): company_ex_id:string
        可用 body 样例: {"company_ex_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
        """
        return self._t.post('finance_bff', "/wallet/sub_company/list", body, **kw)

    def exchange_wallet(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /wallet/wallet/exchange  (前端 exchangeWalletAPI)"""
        return self._t.post('finance_bff', "/wallet/wallet/exchange", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
