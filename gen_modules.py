#!/usr/bin/env python3
"""由 endpoints.json 生成各后端的 Python 方法包装。

每个后端生成一个 mixin 类,方法名取前端函数名去噪(去掉 $N 后缀与 API 结尾),
docstring 带上原始前端函数名与 endpoint,便于对着 bundle 复查。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from backend_map import group_for as _group_for

HERE = Path(__file__).resolve().parent
SPEC = HERE / "adfly_api" / "spec" / "endpoints.json"
OUTDIR = HERE / "adfly_api" / "modules"

# bundle 段名 → config.groups 里的候选组名
# 段归属纠正表:bundle 里这些接口的定义位置与实际服务不一致(页面分块导致),
# 值 = config.groups 里的候选组名。经实测确认。
BACKEND_OVERRIDES = {
    "front": "front", "advertise": "advertise", "automation": "automation",
    "finance": "finance", "finance_bff": "finance_bff", "mcp_open": "mcp_open",
    # 实测:ai_agent 段混装主网关路径,候选组按路径形态在 resolver 里再排序
    "ai_agent": "ai_agent",
}


def group_for(backend: str, path: str) -> str:
    """按 (段, 路径) 决定候选组 —— 比只按段更准。

    /tt/*、/ad/gmv_max_store_config/*、/kanban/*、/bc/* → advertise_bff 独立路由集,
    即使它们出现在 finance 段里。
    """
    if path.startswith(("/tt/", "/kanban/")):
        return "advertise"
    if path.startswith("/ad/") or path == "/bc/query_auth":
        return "advertise"
    if path.startswith(("/material/", "/tactic", "/label")):
        return "automation"
    return BACKEND_OVERRIDES.get(backend, backend)


def backend_group(backend: str) -> list:
    """清单里的 backend 已经是纠正后的组名,直接用。"""
    return [backend]


BACKEND_TITLE = {
    "front": "前端主服务 front-v1.aiadfly.com —— 登录/用户/公司/菜单/通知/快捷入口",
    "advertise": "广告 BFF advertise-bff-v1.aiadfly.com —— 广告账户、授权、VSA/GMVmax、报表",
    "automation": "自动化 automation-v1.aiadfly.com —— 策略/标签/素材池/广告列表",
    "ai_agent": "AI Agent ai-agent-v1.aiadfly.com —— 对话、开户引导、GMVmax/VSA 创建链路",
    "finance_bff": "资金 BFF finance-bff-v1.aiadfly.com —— 钱包、充值、优惠券、支付",
    "finance": "财务 finance-v1.aiadfly.com —— 结算、账单、返点",
    "mcp_open": "MCP Open mcp-open.aiadfly.com —— OAuth 授权确认、登录信息解密",
}

# camelCase → snake_case,并清掉 $N 噪音
def to_snake(fn: str) -> str:
    fn = re.sub(r"\$\d+$", "", fn)
    fn = fn.replace("API", "")
    fn = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", fn)
    fn = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", fn)
    s = re.sub(r"[^0-9a-zA-Z_]", "_", fn).strip("_").lower()
    return re.sub(r"_+", "_", s) or "call"


def main() -> None:
    rows = json.loads(SPEC.read_text(encoding="utf-8"))
    # 参数参考(由 extract_params.py 从服务端 proto 校验报错里提取)
    params_path = SPEC.parent / "params.json"
    params = {}
    if params_path.exists():
        try:
            raw = json.loads(params_path.read_text(encoding="utf-8"))
            for k, v in raw.items():
                if v.get("fields"):
                    params[(k.split("::")[0], v["path"])] = v
        except (json.JSONDecodeError, OSError, KeyError):
            params = {}
    grouped: dict[str, list] = {}
    for r in rows:
        grouped.setdefault(r["backend"], []).append(r)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for backend, items in sorted(grouped.items()):
        cls = "".join(p.capitalize() for p in backend.split("_")) + "API"
        used: dict[str, int] = {}
        lines = [
            '"""自动生成,勿手改。源: spec/endpoints.json (extract_endpoints.py)。"""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import Any, Dict, Optional",
            "",
            "from ..transport import Transport",
            "",
            "",
            f"class {cls}:",
            f'    """{BACKEND_TITLE.get(backend, backend)}"""',
            "",
            f"    BACKENDS = {tuple(backend_group(backend))!r}",
            f"    _GROUP_DEFAULT = {BACKEND_OVERRIDES.get(backend, backend)!r}",
            "",
            "    def __init__(self, t: Transport):",
            "        self._t = t",
            "",
        ]
        per_method_group: dict = {}
        for it in sorted(items, key=lambda x: (x["path"], x["method"])):
            name = to_snake(it["fn"])
            grp = _group_for(it.get("section", backend), it["path"])
            per_method_group[(it["method"], it["path"])] = grp
            if name in used:
                used[name] += 1
                name = f"{name}_{used[name]}"
            else:
                used[name] = 0
            method = it["method"].lower()
            path = it["path"]
            if method == "get":
                # axios 的 get(url, params) —— params 走查询串,不是 body
                doc = f'        """GET {path}  (前端 {it["fn"]})  params 走 query string"""'
                call = f'        return self._t.get({grp!r}, "{path}", **kw)'
                sig = "    def {name}(self, **kw: Any) -> Any:".format(name=name)
            else:
                doc = f'        """{it["method"]} {path}  (前端 {it["fn"]})"""'
                call = f'        return self._t.{method}({grp!r}, "{path}", body, **kw)'
                sig = ("    def {name}(self, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:"
                       .format(name=name))
            hint = params.get((backend, path)) or params.get((it.get("section", backend), path))
            if hint:
                flds = hint["fields"]
                shown = ", ".join(f'{f["json_field"]}:{f["kind"]}' for f in flds[:6])
                if len(flds) > 6:
                    shown += f" …(+{len(flds)-6})"
                tag = {"RESOLVED": "已实调跑通",
                       "PARAMS_COMPLETE": "字段已摸清"}.get(hint.get("status", ""), hint.get("status", ""))
                # 把原 docstring 的第一行取出来,再补参数说明
                first = doc.strip().strip('"').strip()
                doc_lines = [f'        """{first}',
                             f'        实测必需字段({len(flds)} 个,{tag}): {shown}']
                if hint.get("body"):
                    doc_lines.append(f'        可用 body 样例: {json.dumps(hint["body"], ensure_ascii=False)}')
                doc_lines.append('        """')
                doc = "\n".join(doc_lines)
            lines += [sig, doc, call, ""]
        # 通用逃生口:任何未包装的路径都能直接打
        lines += [
            "    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:",
            '        """任意路径逃生口:call(\"POST\", \"/tiktok/gmv_max/list\", {...})。"""',
            "        return self._t.request(method.upper(), path, json_body=body, group=self._GROUP_DEFAULT, **kw)",
            "",
        ]
        (OUTDIR / f"{backend}.py").write_text("\n".join(lines), encoding="utf-8")
        index_rows.append((backend, cls, len(items)))
        print(f"{backend:12} {cls:16} {len(items):4} 方法 -> modules/{backend}.py")

    init = ['"""adfly ERP 接口模块(自动生成)。"""', ""]
    for backend, cls, _n in sorted(index_rows):
        init.append(f"from .{backend} import {cls}")
    init += ["", "__all__ = ["]
    for _b, cls, _n in sorted(index_rows):
        init.append(f'    "{cls}",')
    init += ["]", ""]
    (OUTDIR / "__init__.py").write_text("\n".join(init), encoding="utf-8")
    print("\n写入 modules/__init__.py")


if __name__ == "__main__":
    main()
