#!/usr/bin/env python3
"""验证多 host 自动路由 + 分组兜底。无需 token:看返回码是不是"路由存在"。"""
from __future__ import annotations
import sys, warnings
from collections import Counter
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from adfly_api import AdflyAuthError, AdflyClient, AdflyError, AdflyRouteError

c = AdflyClient(state_path=Path("adfly_api/.session.json"), auto_login=False)

CASES = [
    ("广告-账户列表",   c.ads.get_advertiser_list,    {"page": 1, "page_size": 5, "platform": 1}),
    ("广告-GMVmax列表", c.ads.get_gmv_max_list,       {"page": 1, "page_size": 5}),
    ("广告-授权列表",   c.ads.get_gmv_max_auth_list,      "POST"),
    ("广告-像素列表",   c.ads.get_pixel_list,             {}),
    ("广告-广告报表",   c.ads.get_ad_report_list,         {"page": 1, "page_size": 5}),
    ("广告-账户报表",   c.ads.get_ad_account_report_list, {"page": 1, "page_size": 5}),
    ("广告-任务列表",   c.ads.get_tiktok_task_list,       {"page": 1, "page_size": 5}),
    ("广告-账户配置",   lambda kw=None: c.ads.get_advertiser_config(params={"platform": 1}), "GET"),
    ("广告-授权链接",   c.ads.get_advertiser_config,          None),
    ("广告-店铺列表",   c.ads.get_gmv_max_store_list,     {"advertiser_id": "0", "tt_auth_id": 0}),
    ("前端-用户信息",   c.front.get_user_info,            "GET"),
    ("前端-公司端口",   c.front.get_port_list,            {}),
    ("前端-国家列表",   c.front.get_country_list,         {}),
    ("资金-钱包列表",   c.wallet.list_wallet,             {}),
    ("资金-优惠券",     c.wallet.get_coupon_list,         {"page": 1, "page_size": 5}),
    ("资金-支付流水",   c.wallet.get_trade_list,          {"page": 1, "page_size": 5}),
    ("财务-结算列表",   c.fin.get_settlement_list,        {"page": 1, "page_size": 5}),
    ("财务-账期设置",   c.fin.get_bill_set_need,          "GET"),
    ("财务-应收明细",   c.fin.get_payable_detail,         {"page": 1, "page_size": 5}),
    ("自动化-策略列表", c.auto.automation_get_list_tactic, {"page": 1, "page_size": 5}),
    ("自动化-标签列表", c.auto.get_label_list,            {"page": 1, "page_size": 5}),
    ("AI-用户画像",     c.agent.get_user_profile,          "GET"),
]

ok = auth = routed = biz = err = 0
for name, fn, body in CASES:
    try:
        data = fn() if body == "GET" else fn(body)
        print(f"  OK   {name:18} 200, 返回 {type(data).__name__}")
        ok += 1
    except AdflyAuthError as exc:
        host = exc.path.split("/")[2] if exc.path.count("/") > 2 else exc.path
        print(f"  OK   {name:18} 路由通(鉴权 {exc.code}: {exc.message[:22]}) host={host}")
        auth += 1
    except AdflyRouteError:
        print(f"  MISS {name:18} 所有候选 host 都 404")
        routed += 1
    except AdflyError as exc:
        host = exc.path.split("/")[2] if exc.path.count("/") > 2 else exc.path
        if exc.code in (400, 401, 403, 55):
            print(f"  OK   {name:18} code={exc.code} {exc.message[:30]} host={host}")
            auth += 1
        else:
            print(f"  BIZ  {name:18} code={exc.code} {exc.message[:40]} host={host}")
            biz += 1
    except Exception as exc:
        print(f"  ERR  {name:18} {type(exc).__name__}: {str(exc)[:60]}")
        err += 1

print(f"\n路由可达 {ok + auth}/{len(CASES)}   全 404: {routed}   业务错误: {biz}   异常: {err}")

rp = Path("adfly_api/spec/routes.json")
if rp.exists():
    import json
    routes = json.loads(rp.read_text())
    hosts = Counter((v.get("route", "?") if isinstance(v, dict) else v).split("|")[0] for v in routes.values())
    print(f"\n路由缓存 {len(routes)} 条,按 host 归类:")
    for host, n in hosts.most_common():
        print(f"  {host:16} {n}")
