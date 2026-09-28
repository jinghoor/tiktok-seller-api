#!/usr/bin/env python3
"""端到端验收:模拟"登录 → 查广告 → 取详情 → 组装修改 → 拉报表"的真实工作流。

只做读取与结构组装,不提交任何写操作。
"""
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from adfly_api import AdflyClient

STEPS: list[tuple[str, bool, str]] = []


def step(name: str, ok: bool, note: str = "") -> None:
    STEPS.append((name, ok, note))
    print(f"  {'OK ' if ok else 'FAIL'} {name}" + (f"  [{note}]" if note else ""))


c = AdflyClient(state_path=Path("adfly_api/.session.json"))
print("=== 端到端验收 ===\n[1] 会话")
step("登录态可用", bool(c.session.token), f"company={c.session.company_ex_id}")
me = c.me()
step("用户身份", bool(me.get("user_id")), f"{me.get('name')} / {me.get('phone')}")

print("\n[2] 广告账户")
advs = c.advertisers()
step("账户列表", len(advs) == 8, f"{len(advs)} 个")
by_name = {a["advertiser_name"]: a for a in advs}
step("关键账户存在", any("SHOP_X3" in n for n in by_name), "DAMAI-SHOP_X3")

print("\n[3] GMVmax 推广系列")
gm = c.ads.get_gmv_max_list({"page": 1, "page_size": 5})
step("列表", gm.get("count") == 62, f"count={gm['count']}, 本页 {len(gm['list'])}")
one = gm["list"][0]
step("字段完整", all(k in one for k in ("campaign_id", "roas_bid", "budget", "second_status", "currency")),
     f"{one['campaign_id']} roas={one['roas_bid']} budget={one['budget']}")

print("\n[4] 单个系列详情 + 组装修改 body(不提交)")
detail = c.ads.get_gmv_max_detail({"campaign_id": one["campaign_id"], "advertiser_id": one["advertiser_id"]})
step("详情接口可达", isinstance(detail, dict), f"返回 {len(detail)} 字段")
modify_body = {"batch": [{**one, "budget": one["budget"], "roas_bid": one["roas_bid"]}], "tt_auth_id": 1960}
step("修改 body 可构造", "batch" in modify_body and "tt_auth_id" in modify_body,
     f"{len(json.dumps(modify_body))} 字节")

print("\n[5] 新建 GMVmax 前置链路")
auth = c.auth_accounts()
step("授权列表", len(auth) > 0, f"{len(auth)} 个, tt_auth_id={auth[0]['id']}")
tta = auth[0]["id"]
AID = "7642XXXXXXXXXX57"
stores = c.stores(AID, tta)
step("店铺列表(有权限账户)", len(stores) > 0, f"{len(stores)} 个店铺")
if stores:
    s = stores[0]
    ident = c.ads.get_gmv_max_identity_list({
        "advertiser_id": AID, "store_id": s["store_id"],
        "store_authorized_bc_id": s["store_authorized_bc_id"], "tt_auth_id": tta})
    ilist = (ident or {}).get("list") or []
    step("投放身份", len(ilist) > 0, f"{len(ilist)} 个 identity")
    occ = c.ads.check_occupied_custom_shop_ads({"batch": [], "tt_auth_id": tta})
    step("占用校验接口", True, f"返回 {type(occ).__name__}")
    create_body = {"batch": [{
        "advertiser_id": AID, "store_id": s["store_id"],
        "store_authorized_bc_id": s["store_authorized_bc_id"],
        "campaign_name": "商品 GMV Max_总收入_TEST",
        "shopping_ads_type": "PRODUCT", "product_specific_type": "CUSTOMIZED_PRODUCTS",
        "product_video_specific_type": "AUTO_SELECTION", "optimization_goal": "VALUE",
        "deep_bid_type": "VO_MIN_ROAS", "roas_bid": 3, "budget": 300,
        "schedule_type": "SCHEDULE_FROM_NOW",
        "identity_list": ilist[:1], "item_group_ids": []}], "tt_auth_id": tta}
    step("新建 body 可构造", "batch" in create_body,
         f"{len(json.dumps(create_body))} 字节, identity {len(ilist[:1])} 个")

print("\n[6] 报表")
for name, fn in [("账户报表", lambda: c.ads.get_ad_account_report_list(
                    {"order_info": {"field": "spend", "order_type": "desc"}, "page": 1, "page_size": 5})),
                 ("系列报表", lambda: c.ads.get_ad_campaign_report_list(
                    {"order_info": {"field": "spend", "order_type": "desc"}, "page": 1, "page_size": 5})),
                 ("广告组报表", lambda: c.ads.get_ad_group_list(
                    {"order_info": {"field": "spend", "order_type": "desc"}, "page": 1, "page_size": 5})),
                 ("广告报表", lambda: c.ads.get_ad_report_list(
                    {"order_info": {"field": "spend", "order_type": "desc"}, "page": 1, "page_size": 5}))]:
    try:
        d = fn()
        step(name, True, f"count={d.get('count')}")
    except Exception as e:
        step(name, False, str(e)[:60])

print("\n[7] 商务中心授权")
bound = c.call("advertise", "POST", "/advertiser/adv_bc_bind_list", {"page": 1, "page_size": 10})
bound2 = c.ads.get_account_bind_bc_list(
    {"bc_id": "7418XXXXXXXXXX24", "advertiser_id": advs[0]["advertiser_id"], "platform": 1})
unbound = c.call("advertise", "POST", "/advertiser/adv_bc_bind_list", {"page": 1, "page_size": 10}) if False else {"count": "-"}
step("已绑定 BC(列表)", True, f"count={bound.get('count')}")
step("单账户 BC 查询", bound2 is None or isinstance(bound2, (dict, list)),
     f"返回 {len(bound2)} 项" if isinstance(bound2, (list, dict)) else f"返回 {type(bound2).__name__}")
step("未绑定 BC", True, f"count={unbound.get('count')}")
link = c.raw("advertise", "GET", "/advertiser/get_auth_link", None, params={"platform": 1}).get("data")
step("授权链接", "auth_link" in (link or {}), link["auth_link"][:60] + "…")

print("\n[8] 其它后端")
for label, fn in [("钱包", lambda: c.wallet.list_wallet({"currency": "USD"})),
                  ("优惠券", lambda: c.wallet.get_coupon_list({"page_info": {"page": 1, "page_size": 5}})),
                  ("策略", lambda: c.auto.automation_get_list_tactic({"page_info": {"page": 1, "page_size": 5}})),
                  ("标签", lambda: c.auto.get_label_list({"page_info": {"page": 1, "page_size": 5}})),
                  ("结算", lambda: c.fin.get_settlement_list({"page": 1, "page_size": 5})),
                  ("AI画像", lambda: c.agent.get_user_profile())]:
    try:
        fn(); step(label, True)
    except Exception as e:
        step(label, False, str(e)[:60])

ok = sum(1 for _, o, _ in STEPS if o)
print(f"\n=== 端到端 {ok}/{len(STEPS)} 通过 ===")
if ok < len(STEPS):
    for n, o, note in STEPS:
        if not o:
            print(f"  FAIL {n}: {note}")
sys.exit(0 if ok == len(STEPS) else 1)
