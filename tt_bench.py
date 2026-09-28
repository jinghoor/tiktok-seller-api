#!/usr/bin/env python3
"""局部编辑接口的基准测试 + 并发安全矩阵。

目标：在「不碰编辑接口、不打乱 SKU 顺序」两个硬约束下找到最优操作参数。

测量维度：
  · gap（请求间隔）对成功率与吞吐的影响
  · 并发度对成功率的影响（判断是接口级还是商品级限流）
  · 每次操作后校验 SKU 顺序是否与基线一致
  · 延迟分布（p50 / p95 / max）

用法：
  python3 tt_bench.py --latency <PID>                    # 单请求延迟分布
  python3 tt_bench.py --gap-matrix <PID>                 # gap × 吞吐/成功率
  python3 tt_bench.py --parallel-matrix <PID>            # 并发度 × 成功率（跨 SKU）
  python3 tt_bench.py --multi-product <PID1,PID2,...>    # 跨商品并发
  python3 tt_bench.py --order-check <PID>                # SKU 顺序不变性验证
  python3 tt_bench.py --all <PID> 
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, ".")
import tt_http_client as H  # noqa: E402
import tt_partial_edit as PE  # noqa: E402

WH = "7659XXXXXXXXXX08"


# ─────────────────────────── 基础探测 ───────────────────────────

def sku_ids_ordered(tt: H.TT, pid: str) -> list[str]:
    """按**接口返回顺序**取 SKU id。这个顺序就是产品的规格顺序。"""
    item = H.find_list_item(tt, pid)
    return [str(s.get("id")) for s in (item.get("skus") or [])]


def stock_map(tt: H.TT, pid: str) -> dict[str, int]:
    out = {}
    for sid in sku_ids_ordered(tt, pid):
        q = H.probe_stock(tt, pid, sid, WH)
        out[sid] = q if q is not None else -1
    return out


def _timed(fn, *a, **kw):
    t = time.time()
    try:
        r = fn(*a, **kw)
        return time.time() - t, True, r, None
    except Exception as e:
        return time.time() - t, False, None, f"{type(e).__name__}: {e}"


def stats(lat: list[float], ok: int, fail: int):
    if not lat:
        return {"n": 0}
    s = sorted(lat)
    return {
        "n": len(s), "ok": ok, "fail": fail,
        "ok_rate": round(ok / max(1, ok + fail), 3),
        "mean_ms": round(statistics.mean(s) * 1000),
        "p50_ms": round(s[len(s) // 2] * 1000),
        "p95_ms": round(s[min(len(s) - 1, int(len(s) * 0.95))] * 1000),
        "max_ms": round(s[-1] * 1000),
        "rps": round(ok / max(0.001, sum(lat)), 2),
    }


# ─────────────────────── 数据快照与自动还原 ───────────────────────
# 基准测试会真实写数据。任何异常/中断都可能留下脏库存，
# 所以在开始时拍快照，main 的 finally 里无条件还原。

def snapshot(tt: H.TT, pids: list[str]) -> dict:
    snap = {}
    for pid in pids:
        try:
            snap[pid] = {"skus": sku_ids_ordered(tt, pid), "stock": stock_map(tt, pid)}
        except Exception as e:
            print(f"  ! 快照失败 {pid}: {e}", flush=True)
    return snap


def restore_snapshot(tt: H.TT, snap: dict) -> int:
    """按快照还原库存。用 delta 写，避免依赖读值。"""
    fixed = 0
    for pid, s in snap.items():
        cur = stock_map(tt, pid)
        items = []
        for sid, q in (s.get("stock") or {}).items():
            if q is None or q < 0:
                continue
            now = cur.get(sid)
            if now == q:
                continue
            items.append({"sku_id": sid, "warehouse_id": WH, "quantity_variation": q - now})
        if items:
            try:
                tt.post(PRICE_STOCKS, {"product_id": pid, "price_stocks_edit_data": items,
                                       "tab_id": 2})
                fixed += 1
            except Exception as e:
                print(f"  ! 还原失败 {pid}: {e}", flush=True)
    return fixed


# ─────────────────────────── 用例 ───────────────────────────

def case_latency(tt: H.TT, pid: str, n: int = 20):
    """单请求延迟分布：用 delta=0 的 no-op 写（不改数据）。"""
    print(f"\n[latency] {n} 次 no-op 写请求（delta=0，不改数据）", flush=True)
    sids = sku_ids_ordered(tt, pid)
    lat, ok, fail = [], 0, 0
    for i in range(n):
        sid = sids[i % len(sids)]
        dt, good, _, err = _timed(H.probe_stock, tt, pid, sid, WH)
        lat.append(dt)
        if good:
            ok += 1
        else:
            fail += 1
            if i < 3:
                print(f"    失败样本: {err}", flush=True)
    st = stats(lat, ok, fail)
    print(f"    {json.dumps(st, ensure_ascii=False)}", flush=True)
    return st


def case_gap_matrix(tt_factory, pid: str, gaps=(0.0, 0.2, 0.4, 0.6, 1.0),
                    per_gap: int = 10):
    """不同 gap 下的成功率与吞吐。每次新建客户端避免状态污染。"""
    print(f"\n[gap_matrix] 每档 {per_gap} 次请求", flush=True)
    rows = []
    for gap in gaps:
        tt = tt_factory(gap)
        try:
            sids = sku_ids_ordered(tt, pid)
            lat, ok, fail = [], 0, 0
            for i in range(per_gap):
                sid = sids[i % len(sids)]
                dt, good, _, _ = _timed(H.probe_stock, tt, pid, sid, WH)
                lat.append(dt)
                ok += good
                fail += (not good)
            st = stats(lat, ok, fail)
            st["gap"] = gap
            rows.append(st)
            print(f"    gap={gap:<4} → ok={st['ok']}/{st['n']} "
                  f"mean={st['mean_ms']}ms p95={st['p95_ms']}ms rps={st['rps']}", flush=True)
        finally:
            tt.close()
        time.sleep(3)      # 每档之间冷却，避免上一档的限流影响下一档
    return rows


def case_parallel_matrix(tt: H.TT, pid: str, workers=(1, 2, 4, 8), per_worker: int = 3):
    """同一商品内跨 SKU 并发。不同 sku_id 无数据竞争，但服务端可能商品级加锁。"""
    print(f"\n[parallel_matrix] 同一商品跨 SKU 并发（每档 {per_worker} 请求/线程）", flush=True)
    sids = sku_ids_ordered(tt, pid)
    rows = []
    for w in workers:
        tasks = [sids[i % len(sids)] for i in range(w * per_worker)]

        def one(sid):
            return _timed(H.probe_stock, tt, pid, sid, WH)

        t0 = time.time()
        lat, ok, fail = [], 0, 0
        with ThreadPoolExecutor(w) as ex:
            for fut in as_completed([ex.submit(one, s) for s in tasks]):
                dt, good, _, _ = fut.result()
                lat.append(dt)
                ok += good
                fail += (not good)
        wall = time.time() - t0
        st = stats(lat, ok, fail)
        st.update({"workers": w, "wall_s": round(wall, 2),
                   "throughput_rps": round(ok / max(0.001, wall), 2)})
        rows.append(st)
        print(f"    workers={w:<3} → ok={st['ok']}/{st['n']} wall={st['wall_s']}s "
              f"吞吐={st['throughput_rps']} rps mean={st['mean_ms']}ms", flush=True)
        time.sleep(4)
    return rows


def case_multi_product(tt_factory, pids: list[str], workers: int = 4, gap: float = 0.3):
    """跨商品并发（每个商品一个线程，商品内串行）。这是批量场景的真实形态。"""
    print(f"\n[multi_product] {len(pids)} 个商品，并发 {workers}，gap={gap}", flush=True)
    t0 = time.time()
    results = {}

    def one(pid):
        tt = tt_factory(gap)
        try:
            t1 = time.time()
            sids = sku_ids_ordered(tt, pid)
            ok = 0
            for sid in sids:
                if H.probe_stock(tt, pid, sid, WH) is not None:
                    ok += 1
            return pid, ok, len(sids), time.time() - t1, None
        except Exception as e:
            return pid, 0, 0, time.time() - t1, f"{type(e).__name__}: {e}"
        finally:
            tt.close()

    with ThreadPoolExecutor(workers) as ex:
        for pid, ok, tot, dt, err in ex.map(one, pids):
            results[pid] = {"ok": ok, "total": tot, "sec": round(dt, 2), "err": err}
    wall = time.time() - t0
    good = sum(1 for r in results.values() if r["err"] is None)
    print(f"    完成 {good}/{len(pids)} 商品，wall={wall:.1f}s，"
          f"吞吐={len(pids)/max(0.001, wall):.2f} 商品/秒", flush=True)
    for pid, r in list(results.items())[:8]:
        flag = "OK " if r["err"] is None else "ERR"
        print(f"      {flag} {pid[:18]} sku={r['ok']}/{r['total']} {r['sec']}s "
              f"{r['err'] or ''}", flush=True)
    return {"wall_s": round(wall, 2), "done": good, "total": len(pids), "detail": results}


def case_order_check(tt: H.TT, pid: str, rounds: int = 5):
    """SKU 顺序不变性：连续做价/库存写操作，每轮比对 SKU id 序列。"""
    print(f"\n[order_check] {rounds} 轮写操作后校验 SKU 顺序", flush=True)
    base = sku_ids_ordered(tt, pid)
    print(f"    基线顺序: {base}", flush=True)
    all_ok = True
    for i in range(rounds):
        sid = base[i % len(base)]
        # no-op 写：set_stock 传 delta=0 不改数据。
        # 这里绝不能用「读当前值再写回」的写法 —— 读失败时的兜底值
        # 会真的写进库存（踩过：一次把 3 个 SKU 从 7 写成 200）。
        if i % 2 == 0:
            H.probe_stock(tt, pid, sid, WH)          # delta=0，纯 no-op
            kind = "库存"
        else:
            H.set_price(tt, pid, sid, 120000)        # sale_price 绝对值，同值幂等
            kind = "价格"
        cur = sku_ids_ordered(tt, pid)
        same = cur == base
        all_ok &= same
        print(f"    第{i+1}轮 ({kind}写) → {'顺序未变' if same else '顺序变了！'}", flush=True)
    print(f"    结论: {'✅ 顺序始终不变' if all_ok else '❌ 顺序被打乱'}", flush=True)
    return {"base_order": base, "stable": all_ok}


def case_no_edit_guard(tt: H.TT, pid: str):
    """守卫检查：确认我们用的路径不触碰编辑接口。
    通过对比操作前后的 audit_status / product_status 判断。"""
    print("\n[no_edit_guard] 确认不走编辑接口、不触发重审", flush=True)
    before = PE.audit_state(tt, pid)
    sids = sku_ids_ordered(tt, pid)
    H.set_price_all(tt, pid, 121000)
    # +/-1 都记下来，后面按 delta 反着还原（不用绝对值，避免读失败兜底值被写进去）
    H.probe_stock_delta(tt, pid, sids[0], WH, +1)
    time.sleep(1.5)
    after = PE.audit_state(tt, pid)
    checks = {
        "product_status 未变": before["product_status"] == after["product_status"],
        "audit_status 未变": before["audit_status"] == after["audit_status"],
    }
    for k, v in checks.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}", flush=True)
    # 还原：价格走绝对值（幂等），库存走反向 delta
    H.set_price_all(tt, pid, 120000)
    H.probe_stock_delta(tt, pid, sids[0], WH, -1)
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", default="1790XXXXXXXXXX16")
    ap.add_argument("--latency", action="store_true")
    ap.add_argument("--gap-matrix", action="store_true")
    ap.add_argument("--parallel-matrix", action="store_true")
    ap.add_argument("--multi-product", metavar="PIDS")
    ap.add_argument("--order-check", action="store_true")
    ap.add_argument("--no-edit-guard", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--out", default="notes/tt_bench.json")
    a = ap.parse_args()

    def factory(gap):
        return H.TT(min_gap=gap)

    report = {}
    tt = factory(0.6)
    snap = snapshot(tt, [a.pid] + ([x.strip() for x in a.multi_product.split(",")]
                                   if a.multi_product else []))
    print(f"# 已拍快照: { {k: v['stock'] for k, v in snap.items()} }", flush=True)
    try:
        if a.all or a.latency:
            report["latency"] = case_latency(tt, a.pid, a.n)
        if a.all or a.order_check:
            report["order_check"] = case_order_check(tt, a.pid)
        if a.all or a.no_edit_guard:
            report["no_edit_guard"] = case_no_edit_guard(tt, a.pid)
    except Exception as e:
        print(f"! 用例异常: {type(e).__name__}: {e}", flush=True)
    finally:
        n = restore_snapshot(tt, snap)
        after = snapshot(tt, [a.pid])
        same = all(after.get(p, {}).get("stock") == v.get("stock")
                   for p, v in snap.items())
        print(f"# 还原: 修正 {n} 个商品，数据{'一致 ✅' if same else '仍有差异 ❌'}", flush=True)
        if not same:
            print(f"#   快照 {snap.get(a.pid, {}).get('stock')}", flush=True)
            print(f"#   现状 {after.get(a.pid, {}).get('stock')}", flush=True)
        tt.close()

    if a.all or a.gap_matrix:
        report["gap_matrix"] = case_gap_matrix(factory, a.pid)
    if a.all or a.parallel_matrix:
        tt2 = factory(0.6)
        try:
            report["parallel_matrix"] = case_parallel_matrix(tt2, a.pid)
        finally:
            tt2.close()
    if a.multi_product:
        pids = [x.strip() for x in a.multi_product.split(",") if x.strip()]
        report["multi_product"] = case_multi_product(factory, pids)

    json.dump(report, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"\n# 报告已写入 {a.out}", flush=True)


if __name__ == "__main__":
    main()
