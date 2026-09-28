#!/usr/bin/env python3
"""商务中心授权流程验收。只做读取与 body 组装,不提交绑定。"""
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
advs = c.advertisers()
a0 = advs[0]

print("[1] 授权链接")
try:
    L = H.auth_link(c)
    step("auth_link(platform=1)", L["auth_link"].startswith("https://business-api.tiktok.com"), L["app_id"])
    step("state 拆解", len(L["state"].split("_")) == 4,
         f'company={L["company_ex_id"][:6]}… user={L["user_ex_id"][:6]}…')
    step("redirect_uri", "advertiser/adv_auth" in L["redirect_uri"], L["redirect_uri"][:52])
except Exception as e:
    step("auth_link", False, str(e)[:70])
try:
    H.auth_link(c, platform=0)
    step("缺 platform 应报错", False, "没报错")
except Exception as e:
    step("缺 platform 应报错", "server_invalid_platform" in str(e) or "999" in str(e), "已确认需 platform=1")

print("\n[2] 可用商务中心")
try:
    bcs = H.tt_bc_list(c, 1960)
    step("tt_bc_list", bool(bcs), f"{len(bcs)} 个 BC")
    if bcs:
        det = bcs[0]["bc_detail"]
        print(f"       {det['bc_id']} / {det['name']} / {det['company'][:30]} / {det['currency']} / {det['registered_area']}")
        step("BC 字段完整", all(k in det for k in ("bc_id", "name", "company", "currency", "status")),
             f"verification={det.get('verification_status')}")
except Exception as e:
    step("tt_bc_list", False, str(e)[:70])

print("\n[3] 账户挂靠的 BC")
try:
    mine = H.advertiser_bcs(c, a0["advertiser_id"], a0["owner_bc_id"])
    step("advertiser_bcs", bool(mine), f"{[b.get('bc_name') for b in mine]}")
except Exception as e:
    step("advertiser_bcs", False, str(e)[:70])

print("\n[4] 绑定任务记录")
try:
    recs = H.bind_records(c, page_size=50)
    step("bind_records", bool(recs), f"{len(recs)} 条")
    from collections import Counter
    dist = Counter(r.get("status") for r in recs)
    step("status 可读", True, f"{ {H.BIND_STATUS.get(k, k): v for k, v in dist.items()} }")
    pend = H.pending_bind_records(c)
    step("pending_bind_records", True, f"{len(pend)} 条处理中")
    if recs:
        r0 = recs[0]
        step("记录字段", all(k in r0 for k in ("task_id", "advertiser_id", "bc_id", "status")),
             f"task={r0['task_id'][:14]}…")
except Exception as e:
    step("bind_records", False, str(e)[:70])

print("\n[5] body 组装 + 本地校验")
try:
    b = H.bind_body(advertiser_id=a0["advertiser_id"], bc_id="7626XXXXXXXXXX75", task_id="T1")
    step("bind_body", isinstance(b["advertiser_id"], list), f"advertiser_id 是数组: {b['advertiser_id']}")
    u = H.unbind_single_body(owner_bc_id=a0["owner_bc_id"], un_bind_bc_id="7626XXXXXXXXXX75",
                             advertiser_id=a0["advertiser_id"])
    step("unbind_single_body", "un_bind_bc_id" in u and u["bc_id"] != u["un_bind_bc_id"],
         "owner_bc_id 与 un_bind_bc_id 分开")
    bad = [("bc_id 缺失", dict(bc_id="")), ("advertiser_id 缺失", dict(advertiser_id=""))]
    for why, ov in bad:
        kw = dict(advertiser_id="a", bc_id="b")
        kw.update(ov)
        try:
            H.bind_body(**kw)
            step(f"校验拦 {why}", False, "没拦住")
        except H.AdflyUsageError:
            step(f"校验拦 {why}", True)
    for why, ov in [("un_bind_bc_id 缺失", dict(un_bind_bc_id="")),
                    ("owner_bc_id 缺失", dict(owner_bc_id="")),
                    ("advertiser_id 缺失", dict(advertiser_id=""))]:
        kw = dict(owner_bc_id="o", un_bind_bc_id="u", advertiser_id="a")
        kw.update(ov)
        try:
            H.unbind_single_body(**kw)
            step(f"校验拦 {why}", False, "没拦住")
        except H.AdflyUsageError:
            step(f"校验拦 {why}", True)
except Exception as e:
    step("body 组装", False, str(e)[:70])

print("\n[6] 输入规范化")
step("全角逗号", H.normalize_bc_ids("1，2，3") == "1,2,3")
step("多余空格/空项", H.normalize_bc_ids(" 1 , 2 ,, 3 ") == "1,2,3")
step("空输入", H.normalize_bc_ids("") == "")

print("\n[7] 导出")
try:
    p = c.download("advertise", "/advertiser/adv_bc_bind_list/export", "out/绑定列表.xlsx",
                   {"page": 1, "page_size": 50})
    sz = Path(p).stat().st_size
    step("绑定列表导出", sz > 1000, f"{sz} 字节")
except Exception as e:
    step("绑定列表导出", False, str(e)[:70])

ok = sum(1 for _, o, _ in R if o)
print(f"\n=== BC 验收 {ok}/{len(R)} ===")
for n, o, note in R:
    if not o:
        print(f"  FAIL {n}: {note}")
sys.exit(0 if ok == len(R) else 1)
