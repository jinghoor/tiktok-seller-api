#!/usr/bin/env python3
"""由实测数据生成预计算精确路由表 spec/routes_builtin.json。

host_compare.py 的全量对比证明:每个接口只在一个 host 上成立(0 个歧义)。
把这个事实固化成静态表,客户端运行时就不需要探测了。

表结构: "组::路径" -> "base_key|路径变体"
排序依据: host_compare 的实测命中;无命中的接口沿用组内候选顺序(不影响,因为它们本来就 404)。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api.spec import config  # noqa: E402
from backend_map import SECTION_DEFAULT  # noqa: E402

# host_compare.py 的实测统计(每个组在各 host 上的命中数)
MEASURED = {
    "advertise": [("front", 49), ("advertise_bff", 11)],
    "ai_agent": [("front", 13), ("ai_agent_root", 43)],
    "automation": [("automation", 19), ("front", 1)],
    "finance": [("front", 13), ("advertise_bff", 5), ("finance", 5)],
    "finance_bff": [("finance_bff", 10), ("front", 1)],
    "front": [("front", 22)],
    "mcp_open": [("mcp_open", 0)],
}

# 决定性归属:只在某一个 host 上 OK 的接口(来自 host_compare 的"独有"清单)
EXCLUSIVE = {
    "advertise_bff": [
        "/ad/pixel/list", "/ad/store_app_info/get", "/bc/create", "/bc/query_auth",
        "/tt/bc/list", "/tt/bc/is_adv_bound", "/tt/admin_store/list",
        "/ad/gmv_max_store_config/get", "/ad/gmv_max_store_config/list",
        "/ad/gmv_max_store_config/list_by_store_id", "/ad/gmv_max_store_config/delete",
        "/kanban/google_adv_consume", "/kanban/google_adv_consume/export",
        "/pay/adv_amount_clear", "/pay/adv_recharge", "/pay/adv_reduce", "/pay/coupon_recharge",
    ],
    "finance_bff": [
        "/wallet/list", "/wallet/currency/exchange", "/wallet/wallet/exchange",
        "/wallet/company/exchange", "/wallet/sub_company/list", "/wallet/calculate_reverse_exchange_amount",
        "/pay/trade_list", "/pay/trade_list/export", "/pay/transfer", "/pay/transfer_detail",
        "/pay/online_worldfrist", "/pay/online_cogolinks", "/pay/pay_detail",
        "/coupon/list", "/coupon/detail/list", "/coupon/has_point",
        "/activity_link/by_code",
    ],
    "finance": [
        "/finance/account/payable/detail", "/finance/company_detail/list",
        "/finance/rebate/company_detail/confirm", "/finance/rebate/recharge",
        "/finance/rebate/rule/list", "/finance/rebate/rule_detail/list",
        "/finance/rebate/adv_detail/list", "/finance/rebate/export",
        "/finance/settlement/detail/export", "/finance/settlement/overdue-t7",
        "/finance/billset/find", "/finance/billset/update",
    ],
    "automation": [
        "/tactic/add", "/tactic/edit", "/tactic/list", "/tactic/find", "/tactic/delete",
        "/tactic/bind", "/tactic/unbind", "/tactic/status/update", "/tactic/adv/list",
        "/label/list", "/label/add", "/label/del", "/label_category/list",
        "/label_category/add", "/label_category/del",
        "/advertiser_label_relation/find", "/advertiser_label_relation/bind",
        "/advertiser_label_relation/unbind",
        "/tactic_action_log/list", "/tactic_action_log/export",
        "/tactic_change_log/list", "/tactic_change_log/export",
        "/material/list", "/material_group/list", "/material_group/add",
        "/material_group/edit", "/material_group/del", "/material_group/detail",
        "/ad/list", "/adgroup/list", "/campaign/list", "/advertiser/list",
    ],
    "ai_agent_root": [
        "/ai_agent/v1/session_id/create", "/ai_agent/v1/message/reset", "/ai_agent/v1/adv/list",
        "/ai_agent/market/session_id/create",
    ],
}


def table_from_matrix() -> dict:
    """从 host_compare 的实测矩阵直接建精确表 —— 这是唯一可信来源。

    只接受明确命中的 verdict:
      OK        code=0 或二进制导出
      REACHED   路由到达业务层,仅缺参数/权限(排除 500)
    """
    src = HERE / "adfly_api/spec/host_matrix.json"
    if not src.exists():
        return {}
    matrix = json.loads(src.read_text())
    order = ["front", "advertise_bff", "finance_bff", "finance", "automation",
             "ai_agent_root", "ai_agent", "mcp_open"]
    out = {}
    for key, hosts in matrix.items():
        hits = [h for h in order if hosts.get(h, {}).get("v") in ("OK", "REACHED")]
        if not hits:
            continue
        group, _, rest = key.partition("::")
        path = rest.split(" ", 1)[1] if " " in rest else rest
        out[f"{group}::{path}"] = f"{hits[0]}|{path.lstrip('/')}"
    return out


def main() -> None:
    rows = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
    cfg = config()
    groups = cfg["groups"]
    bases = cfg["backends"]["prod"]
    measured = table_from_matrix()
    print(f"实测矩阵提供 {len(measured)} 条精确归属")
    out: dict = {}
    stats = {"measured": 0, "exact": 0, "group_default": 0, "unknown_host": 0}

    for r in rows:
        key = f'{r["backend"]}::{r["path"]}'
        if key in measured:
            out[key] = measured[key]
            stats["measured"] += 1
            continue
        group, path = r["backend"], r["path"]
        base_key = None
        # 1) 精确表(实测独有)
        for host, paths in EXCLUSIVE.items():
            if path in paths and host in bases:
                base_key = host
                stats["exact"] += 1
                break
        # 2) /ai_agent/ 前缀 → ai-agent 服务
        if base_key is None and path.startswith("/ai_agent/") and "ai_agent_root" in bases:
            base_key = "ai_agent_root"
            stats["exact"] += 1
        # 3) 组内按实测命中数排序取第一个可用 host
        if base_key is None:
            cands = [c for c in groups.get(group, []) if c in bases]
            if cands:
                ranked = [h for h, _ in MEASURED.get(group, []) if h in cands]
                rest = [c for c in cands if c not in ranked]
                base_key = (ranked + rest)[0]
                stats["group_default"] += 1
        if base_key is None:
            stats["unknown_host"] += 1
            continue
        out[f"{group}::{path}"] = f"{base_key}|{path.lstrip('/')}"

    dest = HERE / "adfly_api/spec/routes_builtin.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    from collections import Counter
    print(f"预计算路由表: {len(out)} 条 → {dest.name}")
    print(f"  实测命中 {stats['measured']} / 手写精确 {stats['exact']} / "
          f"组默认 {stats['group_default']} / 无 host {stats['unknown_host']}")
    print("\n按 host 分布:")
    for host, n in Counter(v.split("|")[0] for v in out.values()).most_common():
        print(f"  {host:16} {n}")


if __name__ == "__main__":
    main()
