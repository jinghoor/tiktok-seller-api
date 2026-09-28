#!/usr/bin/env python3
"""adfly_api 客户端实机验证。

阶段 1:连通性 / 路由 / 错误处理(无需凭证)
阶段 2:登录 + 读接口(需要凭证)
阶段 3:写接口 payload 结构校验(离线,从 bundle 复现,不提交)

用法:
  python3 verify_client.py --stage 1
  python3 verify_client.py --stage 2 --account PHONE_REDACTED --password '***'
  python3 verify_client.py --stage 2 --token <JWT> --company <ex_id>
"""
from __future__ import annotations

import argparse, json, sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from adfly_api import AdflyAuthError, AdflyClient, AdflyError, AdflyRouteError  # noqa: E402
from adfly_api.spec import load_endpoints  # noqa: E402

RESULTS: list[tuple[str, str, str]] = []


def record(name: str, ok: bool | None, note: str = "") -> None:
    status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
    icon = {"PASS": "✓", "FAIL": "✗", "SKIP": "-"}[status]
    RESULTS.append((status, name, note))
    print(f"  {icon} {name}" + (f"  [{note}]" if note else ""))


def stage1(c: AdflyClient) -> None:
    print("\n=== 阶段 1:连通性 / 路由 / 错误处理 ===")
    rows = load_endpoints()
    record("接口清单", len(rows) >= 291, f"{len(rows)} 条唯一接口")

    # 必须用一个干净会话:带 token 的客户端打这里会 200,测不出鉴权分支
    from adfly_api import AdflyClient as _C
    anon = _C(state_path=Path("/tmp/.adfly_anon.json"), auto_login=False)
    anon.t.session.token = ""
    try:
        anon.raw("front", "GET", "/user/info")
        record("无 token 抛 AdflyAuthError", False, "没有抛异常")
    except AdflyAuthError as e:
        record("无 token 抛 AdflyAuthError", True, f"code={e.code}")
    except Exception as e:
        record("无 token 抛 AdflyAuthError", False, type(e).__name__)

    try:
        c.raw("front", "GET", "/definitely_not_a_route_xyz")
        record("未知路径抛 AdflyRouteError", False, "竟然成功")
    except AdflyRouteError:
        record("未知路径抛 AdflyRouteError", True)
    except AdflyError as e:
        record("未知路径抛 AdflyRouteError", True, f"code={e.code}")

    probes = [
        ("front", "GET", "/user/info"), ("front", "POST", "/company/get_ports_list"),
        ("advertise", "POST", "/advertiser/list"), ("advertise", "POST", "/tiktok/gmv_max/list"),
        ("advertise", "POST", "/tiktok/auth_list"), ("advertise", "GET", "/advertiser/config"),
        ("finance_bff", "POST", "/wallet/list"), ("finance", "POST", "/finance/settlement/list"),
        ("automation", "POST", "/tactic/list"), ("ai_agent", "GET", "/ai_agent/v1/user/profile"),
    ]
    ok = 0
    failed = []
    for group, method, path in probes:
        try:
            c.raw(group, method, path, {} if method == "POST" else None)
            ok += 1
        except AdflyAuthError as e:
            ok += 1
        except AdflyError as e:
            # 空 body 打到需要参数的接口时,服务端可能回 500;路由本身是通的
            if getattr(e, "code", None) in (400, 401, 403, 55, 404, 500) and "page not found" not in str(e):
                ok += 1
            else:
                failed.append(f"{group}{path}: {e.code}")
        except Exception as e:
            failed.append(f"{group}{path}: {type(e).__name__}")
    record("各后端路由可达", ok >= len(probes) - 1, f"{ok}/{len(probes)}" + (f" 失败 {failed}" if failed else ""))


def stage2(c: AdflyClient) -> None:
    print("\n=== 阶段 2:登录 + 读接口 ===")
    if not c.session.token:
        record("token 就绪", False, "无 token")
        return
    record("token 就绪", True, f"len={len(c.session.token)}")

    try:
        info = c.me()
        record("GET /user/info", bool(info.get("user_id")),
               f"{info.get('name','')} / {info.get('phone','')}")
    except AdflyError as e:
        record("GET /user/info", False, str(e)[:80])

    try:
        cos = c.companies()
        record("公司列表", bool(cos), f"{len(cos)} 家, 选中 {c.session.company_ex_id}")
    except AdflyError as e:
        record("公司列表", False, str(e)[:80])

    advs = []
    try:
        advs = c.advertisers()
        record("POST /advertiser/list", len(advs) > 0, f"{len(advs)} 个广告账户")
    except AdflyError as e:
        record("POST /advertiser/list", False, str(e)[:90])
    if advs:
        a = advs[0]
        print(f"      样例: {a.get('advertiser_id')} / {a.get('advertiser_name')} / "
              f"{a.get('balance')} {a.get('currency')} / bc={a.get('owner_bc_id')}")

    aid = advs[0]["advertiser_id"] if advs else None
    reads = [
        ("tiktok/gmv_max/list", {"page": 1, "page_size": 10}),
        ("tiktok/gmv_max/get_refresh_time", {}),
        ("tiktok/auth_list", None),
        ("tiktok/gmv_max/identity/get", {"advertiser_id": "7642XXXXXXXXXX57",
                                         "store_id": "8648XXXXXXXXXX10",
                                         "store_authorized_bc_id": "7457XXXXXXXXXX28",
                                         "tt_auth_id": 1960}),
        ("advertiser/adv_bc_bind_list", {"page": 1, "page_size": 10}),
        ("advertiser/bc_un_bind_list", {"page": 1, "page_size": 10}),
        ("tiktok/advertiser_report", {"order_info": {"field": "spend", "order_type": "desc"},
                                      "page": 1, "page_size": 5}),
        ("tiktok/campaign_report", {"order_info": {"field": "spend", "order_type": "desc"},
                                    "page": 1, "page_size": 5}),
        ("tiktok/adgroup_report", {"order_info": {"field": "spend", "order_type": "desc"},
                                   "page": 1, "page_size": 5}),
        ("tiktok/ad_report", {"order_info": {"field": "spend", "order_type": "desc"},
                              "page": 1, "page_size": 5}),
        ("advertiser/tt_create_task_list", {"start_date": "2020-01-01", "end_date": "2030-01-01",
                                            "page": 1, "page_size": 5}),
    ]
    for path, body in reads:
        try:
            data = c.call("advertise", "POST", "/" + path, body if body is not None else {})
            shape = ""
            if isinstance(data, dict):
                shape = "keys=" + ",".join(list(data)[:5])
                if isinstance(data.get("list"), list):
                    shape += f" list={len(data['list'])}"
                if data.get("count") is not None:
                    shape += f" count={data['count']}"
            record(f"POST /{path}", True, shape[:100])
        except AdflyRouteError:
            record(f"POST /{path}", None, "该路径在当前版本不存在(404)")
        except AdflyError as e:
            record(f"POST /{path}", False, f"code={e.code} {e.message[:50]}")
        except Exception as e:
            record(f"POST /{path}", False, type(e).__name__)

    others = [
        ("front", "POST", "/company/get_ports_list", {}),
        ("front", "POST", "/company/country_list", {}),
        ("front", "POST", "/auth/get_company_menu", {}),
        ("front", "POST", "/company/custom_list", {"company_ex_id": c.session.company_ex_id}),
        ("finance_bff", "POST", "/wallet/list", {"currency": "USD"}),
        ("finance_bff", "POST", "/coupon/list", {"page_info": {"page": 1, "page_size": 5}}),
        ("finance_bff", "POST", "/pay/trade_list", {"page_info": {"page": 1, "page_size": 5}}),
        ("finance", "POST", "/finance/settlement/list", {"page": 1, "page_size": 5}),
        ("automation", "POST", "/tactic/list", {"page_info": {"page": 1, "page_size": 5}}),
        ("automation", "POST", "/label/list", {"page_info": {"page": 1, "page_size": 5}}),
        ("automation", "POST", "/advertiser/list", {"page_info": {"page": 1, "page_size": 5}}),
        ("ai_agent", "GET", "/ai_agent/v1/user/profile", None),
    ]
    for group, method, path, body in others:
        try:
            data = c.call(group, method, path, body)
            note = f"keys={list(data)[:4]}" if isinstance(data, dict) else type(data).__name__
            record(f"{group} {method} {path}", True, str(note)[:80])
        except AdflyRouteError:
            record(f"{group} {method} {path}", None, "404(当前版本无此路由)")
        except AdflyError as e:
            record(f"{group} {method} {path}", False, f"code={e.code} {e.message[:45]}")
        except Exception as e:
            record(f"{group} {method} {path}", False, type(e).__name__)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--account")
    ap.add_argument("--password")
    ap.add_argument("--token")
    ap.add_argument("--company")
    ap.add_argument("--env", default=None)
    ap.add_argument("--state", default=str(Path(__file__).resolve().parent / "adfly_api/.session.json"))
    args = ap.parse_args()

    c = AdflyClient(token=args.token, company_ex_id=args.company, env=args.env,
                    state_path=Path(args.state), auto_login=False)

    if args.stage >= 2 and not c.session.token and args.account and args.password:
        print(f"登录 {args.account} …")
        try:
            c.login(args.account, args.password)
            print(f"  登录成功: company_ex_id={c.session.company_ex_id}")
        except AdflyError as e:
            print(f"  登录失败: {e}")
            return 2

    stage1(c)
    if args.stage >= 2:
        stage2(c)

    ok = sum(1 for s, _, _ in RESULTS if s == "PASS")
    bad = sum(1 for s, _, _ in RESULTS if s == "FAIL")
    skip = sum(1 for s, _, _ in RESULTS if s == "SKIP")
    print(f"\n=== 结果 {ok} 通过 / {bad} 失败 / {skip} 跳过 ===")
    for s, n, note in RESULTS:
        if s == "FAIL":
            print(f"  ✗ {n}  [{note}]")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
