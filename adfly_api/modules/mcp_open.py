"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import Transport


class McpOpenAPI:
    """MCP Open mcp-open.aiadfly.com —— OAuth 授权确认、登录信息解密"""

    BACKENDS = ('mcp_open',)
    _GROUP_DEFAULT = 'mcp_open'

    def __init__(self, t: Transport):
        self._t = t

    def decrypt_wlh_login_info(self, **kw: Any) -> Any:
        """GET /decrypt/wlh_login_info  (前端 decryptWlhLoginInfoAPI)  params 走 query string"""
        return self._t.get('mcp_open', "/decrypt/wlh_login_info", **kw)

    def authorize_confirm(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """POST /oauth/authorize_confirm  (前端 authorizeConfirmAPI)"""
        return self._t.post('mcp_open', "/oauth/authorize_confirm", body, **kw)

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        """任意路径逃生口:call("POST", "/tiktok/gmv_max/list", {...})。"""
        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)
