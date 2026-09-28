#!/usr/bin/env python3
"""用 helpers 跑真实工作流,逐项验收。只读 + 结构组装,不提交写操作。"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from adfly_api import AdflyClient
from adfly_api import helpers as H

R: list = []


def step(name: str, ok: bool, note: str = "") -> None:
    R.append((name, ok, note))
    print(f"  {'OK ' if ok else 'FAIL'} {name}" + (f"  [{note}]" if note else ""))


c = AdflyClient(state_path=Path("adfly_api/.session.json"))

print("[1] 资金辅助")
try:
    w = H.wallet_balances(c, "USD")
    step("wallet_balances", bool(w["wallets"]), f"{len(w['wallets'])} 个币种, available_usd={w['available_usd']}")
except Exception as e:
    step("wallet_balances", False, str(e)[:70])
try:
    H.check_currency("CNY")
    step("currency 校验", False, "CNY 应该被拒")
except H.AdflyUsageError:
    step("currency 校验", True, "CNY 被本地拦截,不用等服务端 400")

print("\n[2] 分页辅助")
try:
    d = c.auto.automation_get_list_tactic(H.paging_nested(1, 5))
    step("paging_nested(tactic/list)", isinstance(d, dict), f"total={d.get('page_info',{}).get('total_number')}")
except Exception as e:
    step("paging_nested(tactic/list)", False, str(e)[:70])
try:
    d = c.wallet.get_coupon_list(H.paging_nested(1, 5))
    step("paging_nested(coupon/list)", isinstance(d, dict), f"total={d.get('page_info',{}).get('total_number')}")
except Exception as e:
    step("paging_nested(coupon/list)", False, str(e)[:70])

print("\n[3] 报表辅助")
for label, path, kwargs in [
    ("账户报表", "/tiktok/advertiser_report", {"days": 7}),
    ("系列报表", "/tiktok/campaign_report", {"days": 7}),
    ("广告组报表", "/tiktok/adgroup_report", {"days": 7}),
    ("广告报表", "/tiktok/ad_report", {"days": 7}),
]:
    try:
        rows = list(H.iter_report(c, path, page_size=50, **kwargs))
        step(f"iter_report {label}", True, f"{len(rows)} 行")
    except Exception as e:
        step(f"iter_report {label}", False, str(e)[:60])

print("\n[4] GMVmax 建广告链")
try:
    ready = H.find_gmv_max_ready_account(c)
    step("find_gmv_max_ready_account", bool(ready), f"{len(ready)} 个账户可用")
    if ready:
        acct = ready[0]
        print(f"       {acct['advertiser_id']} / {acct['advertiser_name']} / store={acct['store_id']}")
        ids = H.gmv_max_identities(c, advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
                                  store_authorized_bc_id=acct["store_authorized_bc_id"],
                                  tt_auth_id=acct["tt_auth_id"])
        step("gmv_max_identities", bool(ids), f"{len(ids)} 个 identity")
        occ = H.gmv_max_occupancy_batch(advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
                                       identity_ids=[i["identity_id"] for i in ids[:1]])
        step("gmv_max_occupancy_batch", len(occ["batch"]) == 1, f"{len(occ['batch'])} 条校验项")
        d = c.ads.check_occupied_custom_shop_ads({**occ, "tt_auth_id": acct["tt_auth_id"]})
        step("占用校验实调", True, f"返回 {type(d).__name__}")

        payload = H.gmv_max_create_payload(
            advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
            store_authorized_bc_id=acct["store_authorized_bc_id"],
            campaign_name="API 验收_勿提交", roas_bid=3, budget=300,
            tt_auth_id=acct["tt_auth_id"], item_group_ids=["1735XXXXXXXXXX50"],
            identity_list=ids[:1], schedule_start_time="2026-10-01 00:00:00")
        step("gmv_max_create_payload", "batch" in payload and "tt_auth_id" in payload,
             f"batch[0] {len(payload['batch'][0])} 字段")
        # 本地校验必须拦住缺参
        BAD = [("store_id", dict(store_id="")), ("roas_bid", dict(roas_bid=0)),
               ("item_group_ids", dict(item_group_ids=[], promote_all_products=False)),
               ("budget", dict(budget=0)), ("schedule_start_time", dict(schedule_type="fixed"))]
        for why, override in BAD:
            kw = dict(advertiser_id="a", store_id="b", store_authorized_bc_id="c",
                      campaign_name="n", roas_bid=3, budget=300, tt_auth_id=1,
                      item_group_ids=["x"])
            kw.update(override)
            try:
                H.gmv_max_create_payload(**kw)
                step(f"校验拦 {why}", False, "没拦住")
            except H.AdflyUsageError:
                step(f"校验拦 {why}", True)

        # 全店推广分支
        allp = H.gmv_max_create_payload(advertiser_id="a", store_id="b", store_authorized_bc_id="c",
                                        campaign_name="n", roas_bid=3, budget=300, tt_auth_id=1,
                                        promote_all_products=True)
        step("全店推广分支", "item_group_ids" not in allp["batch"][0]
             and allp["batch"][0]["product_specific_type"] == "ALL", "已去掉 item_group_ids")
        # 编辑 merge
        existing = (c.ads.get_gmv_max_list({"page": 1, "page_size": 1}) or {}).get("list", [{}])[0]
        edit = H.gmv_max_edit(existing, budget=500, tt_auth_id=acct["tt_auth_id"])
        step("gmv_max_edit merge", edit["batch"][0]["budget"] == 500
             and "cost" not in edit["batch"][0], f"{len(edit['batch'][0])} 字段(只读字段已剥离)")
except Exception as e:
    step("GMVmax 链", False, str(e)[:80])

print("\n[5] BC 授权辅助")
try:
    advs = c.advertisers()
    body = H.bc_bind_body(bc_id=advs[0]["owner_bc_id"], advertiser_ids=[advs[0]["advertiser_id"]])
    step("bc_bind_body", "bc_id" in body and "advertiser_ids" in body, f"{body['advertiser_ids']}")
    ub = H.bc_unbind_body(bc_id=advs[0]["owner_bc_id"], advertiser_id=advs[0]["advertiser_id"])
    step("bc_unbind_body(单个)", "advertiser_id" in ub)
    ub2 = H.bc_unbind_body(bc_id=advs[0]["owner_bc_id"],
                           advertiser_ids=[a["advertiser_id"] for a in advs[:3]])
    step("bc_unbind_body(批量)", len(ub2["advertiser_ids"]) == 3)
    try:
        H.bc_bind_body(bc_id="", advertiser_ids=[])
        step("bc_bind_body 校验", False, "没拦住空参数")
    except H.AdflyUsageError:
        step("bc_bind_body 校验", True)
except Exception as e:
    step("BC 辅助", False, str(e)[:70])

print("\n[6] 导出辅助")
try:
    fields = H.export_fields([("账户名称", "advertiser_name"), ("消耗", "spend")])
    body = {**H.report_body(days=7), "fields": fields}
    p = c.download("advertise", "/tiktok/advertiser_report/export", "out/验收导出.xlsx", body)
    size = Path(p).stat().st_size
    step("下载 xlsx 落盘", size > 1000, f"{size} 字节 -> {p}")
except Exception as e:
    step("下载 xlsx 落盘", False, str(e)[:70])

ok = sum(1 for _, o, _ in R if o)
print(f"\n=== helpers 验收 {ok}/{len(R)} ===")
for n, o, note in R:
    if not o:
        print(f"  FAIL {n}: {note}")
sys.exit(0 if ok == len(R) else 1)
