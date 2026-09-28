"""adfly ERP 接口客户端。

用法::

    from adfly_api import AdflyClient

    c = AdflyClient()                        # 读 .session.json 里的登录态
    c.login("PHONE_REDACTED", "password")       # 首次登录
    advs = c.advertisers()                   # 广告账户列表
    c.ads.gmv_max_list({"page": 1, "page_size": 20})

    # 未包装的路径也能直接打(自动选 host)
    c.call("advertise", "POST", "/tiktok/gmv_max/list", {"page": 1, "page_size": 20})

CLI::

    python -m adfly_api login --account PHONE_REDACTED
    python -m adfly_api list --grep gmv
    python -m adfly_api call advertise POST /advertiser/list '{"page":1,"page_size":50}'
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .modules import (
    AdvertiseAPI,
    AiAgentAPI,
    AutomationAPI,
    FinanceAPI,
    FinanceBffAPI,
    FrontAPI,
    McpOpenAPI,
)
from .transport import (
    DEFAULT_STATE,
    AdflyAuthError,
    AdflyError,
    AdflyRouteError,
    Session,
    Transport,
)

__all__ = [
    "AdflyClient",
    "Session",
    "Transport",
    "AdflyError",
    "AdflyAuthError",
    "AdflyRouteError",
]


class AdflyClient:
    """一个账号 + 一个公司上下文 的会话。

    `ads` 广告 BFF / `auto` 自动化 / `wallet` 资金 BFF / `fin` 财务 /
    `agent` AI Agent / `front` 前端主服务 / `mcp` MCP Open
    """

    def __init__(
        self,
        account: Optional[str] = None,
        password: Optional[str] = None,
        *,
        company_ex_id: Optional[str] = None,
        token: Optional[str] = None,
        env: Optional[str] = None,
        state_path: Path = DEFAULT_STATE,
        auto_login: bool = True,
        verbose: bool = False,
        cache_routes: bool = True,
    ):
        self.t = Transport(Session.load(state_path), env=env, state_path=state_path,
                           verbose=verbose, cache_routes=cache_routes)
        self.ads = AdvertiseAPI(self.t)
        self.auto = AutomationAPI(self.t)
        self.wallet = FinanceBffAPI(self.t)
        self.fin = FinanceAPI(self.t)
        self.agent = AiAgentAPI(self.t)
        self.front = FrontAPI(self.t)
        self.mcp = McpOpenAPI(self.t)

        if token:
            self.t.set_token(token, company_ex_id or "")
        elif not self.t.session.valid and account and password and auto_login:
            self.login(account, password)
        if company_ex_id:
            self.t.use_company(company_ex_id)

    # ---------- 会话 ----------

    def login(self, account: str, password: str) -> "AdflyClient":
        self.t.login(account, password)
        return self

    def check_fa(self, account: str, password: str) -> Dict[str, Any]:
        """探测账号是否需要双因素/图形验证码。"""
        return self.t.check_fa(account, password)

    def use_company(self, company_ex_id: str) -> "AdflyClient":
        self.t.use_company(company_ex_id)
        return self

    def companies(self) -> list:
        if not self.t.session.companies:
            self.t._load_companies()
        return self.t.session.companies

    def me(self) -> Dict[str, Any]:
        self.t.session.user = self.t.request("GET", "/user/info", group="front") or {}
        self.t.session.save(self.t.state_path)
        return self.t.session.user

    # ---------- 常用捷径 ----------

    def advertisers(self, page_size: int = 5000) -> list:
        """当前公司的广告账户列表。"""
        data = self.ads.get_advertiser_list({"page": 1, "page_size": page_size, "platform": 1})
        return (data or {}).get("list") or []

    def stores(self, advertiser_id: str, tt_auth_id: Any) -> list:
        """某广告账户下的 TikTok 店铺(GMVmax 建广告前置)。"""
        data = self.ads.get_gmv_max_store_list({"advertiser_id": advertiser_id, "tt_auth_id": tt_auth_id})
        return (data or {}).get("list") or data or []

    def auth_accounts(self) -> list:
        """已授权的 TikTok 账户(tt_auth_id 来源)。"""
        data = self.ads.get_gmv_max_auth_list()
        return (data or {}).get("list") or data or []

    def gmv_max_campaigns(self, **body: Any) -> list:
        payload = {"page": 1, "page_size": 50, **body}
        data = self.ads.get_gmv_max_list(payload)
        return (data or {}).get("list") or []

    # ---------- 通用 ----------

    def call(self, group: str, method: str, path: str,
             body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """按组名打任意路径(自动解析 host)。返回 data。"""
        return self.t.request(method.upper(), path, json_body=body, group=group, **kw)

    def raw(self, group: str, method: str, path: str,
            body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """同 call(),但返回完整信封 {code,message,request_id,data}。"""
        return self.call(group, method, path, body, raw=True, **kw)

    def download(self, group: str, path: str, out_path: str,
                 body: Optional[Dict[str, Any]] = None) -> str:
        """导出接口:落盘 xlsx/csv,返回文件路径。"""
        return self.t.download(group, path, out_path, body)

    def prewarm(self, workers: int = 8) -> dict:
        """按接口清单把路由缓存全部预热(批量任务前调一次,省掉逐条探测)。"""
        from .spec import load_endpoints

        triples = [(r["backend"], r["path"], r["method"]) for r in load_endpoints()]
        return self.t.prewarm(triples, workers=workers)

    def stats(self) -> str:
        return self.t.stats_report()

    @property
    def session(self) -> Session:
        return self.t.session
