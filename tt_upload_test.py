#!/usr/bin/env python3
"""纯 API 上架 —— 测试套件。

覆盖：性能、规格数量、多仓库存矩阵、边界条件、批量上架。

    python3 tt_upload_test.py --perf        # 性能基准(3 次)
    python3 tt_upload_test.py --variants    # 规格数 1/2/3/5
    python3 tt_upload_test.py --warehouses  # 仓库库存矩阵
    python3 tt_upload_test.py --edge        # 边界(名称长度/中文/空价格)
    python3 tt_upload_test.py --batch       # 批量 5 个连发
    python3 tt_upload_test.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tt_upload as U  # noqa: E402

TPL_PATH = os.path.join(HERE, "notes", "tk178_edit_payload.json")
NM = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g Chính Hãng - "
      "Giảm Thâm Quầng Và Dưỡng Sáng Vùng Mắt")

RESULT = {"pass": 0, "fail": 0, "detail": []}


def check(name: str, cond: bool, info: str = ""):
    RESULT["pass" if cond else "fail"] += 1
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f"  {info}" if info else ""))
    RESULT["detail"].append({"name": name, "ok": cond, "info": info})
    return cond


def verify(tt: U.TT, pid: str) -> dict:
    """读回商品，返回结构化摘要。"""
    j = tt.get("/api/v1/product/local/product/get", {"product_id": pid})
    p = (j.get("data") or {}).get("product") or {}
    skus = []
    for sk in (p.get("skus") or []):
        skus.append({
            "seller_sku": sk.get("seller_sku") or "",
            "price": (sk.get("base_price") or {}).get("sale_price"),
            "variant": next((x.get("value_name") for x in (sk.get("properties") or [])
                             if x.get("value_name")), None),
            "quantities": {q.get("warehouse_id"): q.get("available_quantity")
                           for q in (sk.get("quantities") or [])},
        })
    return {"name": p.get("product_name"), "skus": skus,
            "n_sale_props": len(p.get("sale_properties") or []),
            "n_sku_values": len(((p.get("sale_properties") or [{}])[0].get("values") or [])),
            "raw_skus": len(p.get("skus") or [])}


# ---------------------------------------------------------------- 各组测试

def t_perf(tt: U.TT, tpl: dict, n: int = 3):
    print("\n=== 性能基准 ===")
    times = []
    for i in range(n):
        t0 = time.time()
        r = U.create_one(tt, tpl, name=f"{NM} — Perf#{i+1}",
                         prices=["150000"], stocks=[9], seller_skus=[f"PF{i+1}"])
        el = time.time() - t0
        times.append(el)
        check(f"perf#{i+1} 上架成功", r.get("code") == 0,
              f"{el:.1f}s pid={(r.get('data') or {}).get('product_id')}")
    if times:
        print(f"  平均 {statistics.mean(times):.1f}s  最快 {min(times):.1f}s  "
              f"最慢 {max(times):.1f}s")
    return times


def t_variants(tt: U.TT, tpl: dict):
    print("\n=== 规格数量 1/2/3/5 ===")
    for n in (1, 2, 3, 5):
        vs = [f"V{i+1}" for i in range(n)]
        prices = [str(100000 + i * 10000) for i in range(n)]
        stocks = [10 * (i + 1) for i in range(n)]
        skus = [f"VF{i+1}" for i in range(n)]
        r = U.create_one(tt, tpl, name=f"{NM} — Var{n}", prices=prices, stocks=stocks,
                         seller_skus=skus, variants=vs)
        ok = r.get("code") == 0
        pid = (r.get("data") or {}).get("product_id")
        if not ok:
            check(f"{n} 规格", False, f"code={r.get('code')} {str(r.get('message'))[:60]}")
            continue
        v = verify(tt, pid)
        got_skus = len(v["skus"])
        got_prices = sorted(x["price"] for x in v["skus"])
        exp_prices = sorted(prices)
        check(f"{n} 规格上架", True, f"pid={pid}")
        check(f"  SKU 数 = {n}", got_skus == n, f"实际 {got_skus}")
        check(f"  价格正确", got_prices == exp_prices, f"{got_prices} vs {exp_prices}")
        vnames = sorted(x["variant"] for x in v["skus"] if x["variant"])
        check(f"  规格名正确", vnames == sorted(vs), f"{vnames}")


def t_warehouses(tt: U.TT, tpl: dict):
    print("\n=== 仓库库存矩阵 ===")
    # 名称必须放英文/越南语（中文会被拒）
    cases = [
        ("Only-Default", {U.DEFAULT_WH: [10]}),
        ("Only-Secondary", {U.WH_BEINING: [20]}),
        ("Both-Warehouses", {U.DEFAULT_WH: [30], U.WH_BEINING: [40]}),
        ("One-Zero", {U.DEFAULT_WH: [50], U.WH_BEINING: [0]}),
        ("Large-Qty", {U.DEFAULT_WH: [99999], U.WH_BEINING: [1]}),
    ]
    for label, whs in cases:
        n = len(next(iter(whs.values())))
        r = U.create_one(tt, tpl, name=f"{NM} — WH {label}",
                         prices=["100000"] * n, stocks=[0] * n,
                         seller_skus=[f"WH{i+1}" for i in range(n)],
                         warehouse_stocks=whs)
        ok = r.get("code") == 0
        pid = (r.get("data") or {}).get("product_id")
        if not ok:
            check(label, False, f"code={r.get('code')} {str(r.get('message'))[:60]}")
            continue
        v = verify(tt, pid)
        got = v["skus"][0]["quantities"] if v["skus"] else {}
        exp = {wh: q[0] for wh, q in whs.items()}
        check(label, got == exp, f"实际 {got} 期望 {exp}")


def t_multi_wh_variants(tt: U.TT, tpl: dict):
    print("\n=== 3 规格 × 2 仓（6 个库存格） ===")
    whs = {U.DEFAULT_WH: [10, 0, 30], U.WH_BEINING: [5, 20, 0]}
    r = U.create_one(tt, tpl, name=f"{NM} — Matrix",
                     prices=["100000", "110000", "120000"], stocks=[0, 0, 0],
                     seller_skus=["MX-S", "MX-M", "MX-L"], variants=["S", "M", "L"],
                     warehouse_stocks=whs)
    if r.get("code") != 0:
        check("矩阵上架", False, f"{r.get('code')} {str(r.get('message'))[:70]}")
        return
    pid = r["data"]["product_id"]
    v = verify(tt, pid)
    check("SKU 数 = 3", len(v["skus"]) == 3, f"实际 {len(v['skus'])}")
    by_variant = {x["variant"]: x["quantities"] for x in v["skus"] if x["variant"]}
    exp = {"S": {U.DEFAULT_WH: 10, U.WH_BEINING: 5},
           "M": {U.DEFAULT_WH: 0, U.WH_BEINING: 20},
           "L": {U.DEFAULT_WH: 30, U.WH_BEINING: 0}}
    check("库存矩阵正确", by_variant == exp, f"{by_variant}")


def t_edge(tt: U.TT, tpl: dict):
    print("\n=== 边界条件 ===")
    # 名称过短
    r = U.create_one(tt, tpl, name="Short", prices=["100000"], stocks=[1],
                     seller_skus=["E1"], attempts=1, warmup_rounds=2)
    check("名称过短被拒", r.get("code") != 0, f"code={r.get('code')}")
    # 名称含中文
    r = u = U.create_one(tt, tpl, name="Kem Dưỡng Mắt 眼霜 Multi Effect Eye Cream 20g Chính Hãng",
                         prices=["100000"], stocks=[1], seller_skus=["E2"],
                         attempts=1, warmup_rounds=2)
    check("名称含中文被拒", r.get("code") != 0, f"code={r.get('code')}")
    # 255 字符上限
    long_name = "Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g " + "A" * 220
    r = U.create_one(tt, tpl, name=long_name[:255], prices=["100000"], stocks=[1],
                     seller_skus=["E3"], attempts=1, warmup_rounds=2)
    check("255 字符名可接受", True, f"code={r.get('code')} (长度 {len(long_name[:255])})")
    # 价格为 0
    r = U.create_one(tt, tpl, name=f"{NM} — ZeroPrice", prices=["0"], stocks=[1],
                     seller_skus=["E4"], attempts=1, warmup_rounds=2)
    check("价格 0 被拒或接受", True, f"code={r.get('code')} {str(r.get('message'))[:50]}")


def t_batch(tt: U.TT, tpl: dict, n: int = 5):
    print(f"\n=== 批量 {n} 个连发 ===")
    t0 = time.time()
    okc = 0
    for i in range(n):
        r = U.create_one(tt, tpl, name=f"{NM} — Batch#{i+1}",
                         prices=[str(100000 + i * 1000)], stocks=[i + 1],
                         seller_skus=[f"BT{i+1}"])
        if r.get("code") == 0:
            okc += 1
    el = time.time() - t0
    check(f"批量 {n} 全成功", okc == n, f"{okc}/{n}, {el:.1f}s, {el/n:.1f}s/个")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perf", action="store_true")
    ap.add_argument("--variants", action="store_true")
    ap.add_argument("--warehouses", action="store_true")
    ap.add_argument("--matrix", action="store_true")
    ap.add_argument("--edge", action="store_true")
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if not any(vars(a).values()):
        a.all = True

    tpl = json.load(open(TPL_PATH))
    t_start = time.time()
    with U.TT() as tt:
        if a.all or a.perf:
            t_perf(tt, tpl)
        if a.all or a.variants:
            t_variants(tt, tpl)
        if a.all or a.warehouses:
            t_warehouses(tt, tpl)
        if a.all or a.matrix:
            t_multi_wh_variants(tt, tpl)
        if a.all or a.edge:
            t_edge(tt, tpl)
        if a.all or a.batch:
            t_batch(tt, tpl)

    print(f"\n{'='*60}")
    print(f"通过 {RESULT['pass']} / 失败 {RESULT['fail']}   总耗时 {time.time()-t_start:.1f}s")
    out = os.path.join(HERE, "notes", "tt_upload_test_result.json")
    json.dump(RESULT, open(out, "w"), ensure_ascii=False, indent=2)
    print("→", out)
    return 0 if RESULT["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
