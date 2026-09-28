#!/usr/bin/env python3
"""段 + 路径 → 候选组 的唯一权威映射。

为什么需要:线上 bundle 的 7 个模块段是按**页面**分块的,和真实服务不对应 ——
finance 段里塞了 Google Ads 的 /snapshots/*,ai_agent 段里塞了主网关的 /notice/*。
只按段决定 host 会让这些接口被打到错的域名上(静默 404)。

实测结论(2026-09):
  * /tt/*、/kanban/*、/ad/gmv_max_store_config/*、/ad/pixel/list、/bc/query_auth
    → advertise_bff.aiadfly.com/front_api 独立路由集,front-v1 上没有
  * /material/*、/tactic*、/label* → automation
  * /ai_agent/* → ai-agent 独立服务,其余(notice/auth/company) → 主网关
  * /snapshots/*、/campaigns/*、/series/* 等 Google Ads 路径 → 任何线上 host 都不存在(旧版本残留)

extract_endpoints.py 与 gen_modules.py 都从这里取,保证清单与代码一致。
"""

from __future__ import annotations

# 段级默认
SECTION_DEFAULT = {
    "front": "front",
    "advertise": "advertise",
    "automation": "automation",
    "finance": "finance",
    "finance_bff": "finance_bff",
    "ai_agent": "ai_agent",
    "mcp_open": "mcp_open",
}

# 路径级覆盖(优先于段级)
PATH_RULES = (
    ("/tt/", "advertise"),
    ("/kanban/", "advertise"),
    ("/ad/", "advertise"),
    ("/advertiser/get_pixel_token", "advertise"),
    ("/bc/query_auth", "advertise"),
    ("/material/", "automation"),
    ("/material_group/", "automation"),
    ("/tactic", "automation"),
    ("/label", "automation"),
    ("/advertiser_label_relation", "automation"),
    ("/notice/", "front"),
    ("/auth/", "front"),
    ("/company/", "front"),
    ("/user/", "front"),
    ("/sign/", "front"),
)


def group_for(section: str, path: str) -> str:
    """返回 config.groups 里的组名。"""
    for prefix, group in PATH_RULES:
        if path.startswith(prefix):
            return group
    return SECTION_DEFAULT.get(section, section)


def normalize_endpoints(rows: list) -> tuple:
    """就地纠正每行的 backend(原始段名留在 section 字段)。"""
    changed = []
    for r in rows:
        section = r.get("section") or r["backend"]
        r["section"] = section
        want = group_for(section, r["path"])
        if want != r["backend"]:
            changed.append((r["fn"], section, r["backend"], want))
            r["backend"] = want
    return tuple(changed)
