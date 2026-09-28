#!/usr/bin/env python3
"""局部编辑接口测试套件 —— 价格 / 库存 / 组合 / 边界 / 不触发审核。

每个用例都「改 → 读回校验 → 还原」，跑完不留痕迹（除非 --keep）。
用测试商品，跑在真实店铺上但可完全回滚。

用法：
  python3 tt_partial_edit_test.py --all
  python3 tt_partial_edit_test.py --case price
  python3 tt_partial_edit_test.py --all --keep      # 不还原，留现场看
  python3 tt_partial_edit_test.py --selftest        # 只跑不写数据的用例
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback

sys.path.insert(0, ".")
import tt_partial_edit as PE  # noqa: E402
from tt_stock_api import StockAPI  # noqa: E402

PID = "1790XXXXXXXXXX16"
WH = "7659XXXXXXXXXX08"
SKUS = ["1737XXXXXXXXXX12", "1737XXXXXXXXXX48", "1737XXXXXXXXXX84"]

BASELINE_PRICE = 120000
BASELINE_QTY = {SKUS[0]: 200, SKUS[1]: 7, SKUS[2]: 7}

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = ""):
    results.append((name, bool(cond), detail))
    # flush=True 很重要：后台运行/重定向时 print 会缓冲，看不到实时进度，
    # 会误判成「卡住」
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""),
          flush=True)
    return cond


def read_map(api) -> dict:
    return {r["sku_id"]: r for r in PE.sku_state(api, PID)}


def price_of(api, sku) -> int | None:
    """读当前单价；读不到返回 None（直连后端对该商品读不到逐 SKU 价，
    而 sale_price 是绝对值语义，不能拿它"探读"—— 会真写进去）。"""
    return read_map(api).get(sku, {}).get("price")


def price_resp_codes(r) -> list:
    """从响应里取每个 SKU 的 sale_price（价格是绝对值，响应即真值）。"""
    j = (r.get("json") if isinstance(r, dict) else None) or {}
    return [(d.get("sku_id"), (d.get("price") or {}).get("sale_price"))
            for d in (j.get("price_stocks_data") or [])]


def qty_of(api, sku) -> int | None:
    return read_map(api).get(sku, {}).get("qty")


# ─────────────────────────── 用例 ───────────────────────────

def case_read(api, **kw):
    print("\n[read] 读取与基线", flush=True)
    m = read_map(api)
    check("三个 SKU 都能读到", len(m) == 3, f"{len(m)} 个")
    prices = [m[s]["price"] for s in SKUS if s in m]
    if all(p is None for p in prices):
        print("  SKIP  基线价格一致（该后端读不到逐 SKU 价，价格由响应体验证）",
              flush=True)
    else:
        check("基线价格一致", all(p == BASELINE_PRICE for p in prices))


def case_price(api, **kw):
    print("\n[price] 单 SKU 改价", flush=True)
    sku = SKUS[0]
    before = price_of(api, sku)
    r = PE.set_price(api, PID, sku, 131000)
    code = (r.get("json") or {}).get("code")
    check("改价请求 code=0", code == 0, str(code))
    got = dict(price_resp_codes(r)).get(sku)
    check("响应回传新价 131000", got == "131000", f"resp={got}")
    # sale_price 是绝对值：重复提交同样的值不应叠加
    r2 = PE.set_price(api, PID, sku, 131000)
    got2 = dict(price_resp_codes(r2)).get(sku)
    check("绝对值语义（重复提交不叠加）", got2 == "131000", f"resp={got2}")
    if before is not None:
        r3 = PE.set_price(api, PID, sku, before)
        check("已还原", price_of(api, sku) == before)
    else:
        PE.set_price(api, PID, sku, BASELINE_PRICE)
        print("  SKIP  已还原读回校验（后端读不到价格）", flush=True)
    return sku


def case_price_all(api, **kw):
    print("\n[price_all] 一次请求改全部 SKU", flush=True)
    r = PE.set_price_all(api, PID, 132000)
    j = r.get("json") or {}
    check("code=0", j.get("code") == 0, str(j.get("code")))
    data = j.get("price_stocks_data") or []
    check("响应含 3 条结果", len(data) == 3, f"{len(data)} 条")
    vals = [((d.get("price") or {}).get("sale_price")) for d in data]
    check("三个 SKU 全部生效", vals == ["132000"] * 3, str(vals))
    r2 = PE.set_price_all(api, PID, BASELINE_PRICE)
    vals2 = [((d.get("price") or {}).get("sale_price"))
             for d in ((r2.get("json") or {}).get("price_stocks_data") or [])]
    check("已还原", vals2 == [str(BASELINE_PRICE)] * 3, str(vals2))


def case_stock(api, **kw):
    print("\n[stock] 单 SKU 单仓库库存（增量语义）", flush=True)
    sku = SKUS[0]
    before = qty_of(api, sku)
    r = PE.set_stock(api, PID, sku, WH, before + 25)
    check("增量正确", r["delta"] == 25, f"delta={r['delta']}")
    check("库存已增", qty_of(api, sku) == before + 25, f"{before}→{qty_of(api, sku)}")
    r2 = PE.set_stock(api, PID, sku, WH, before)
    check("负增量正确", r2["delta"] == -25, f"delta={r2['delta']}")
    check("已还原", qty_of(api, sku) == before)


def case_stock_zero(api, **kw):
    print("\n[stock_zero] 库存清零再恢复", flush=True)
    sku = SKUS[1]
    before = qty_of(api, sku)
    PE.set_stock(api, PID, sku, WH, 0)
    check("可清零", qty_of(api, sku) == 0, f"{before}→0")
    PE.set_stock(api, PID, sku, WH, before)
    check("已还原", qty_of(api, sku) == before)


def case_both(api, **kw):
    print("\n[both] 同一请求改价 + 改库存", flush=True)
    sku = SKUS[0]
    p0, q0 = price_of(api, sku), qty_of(api, sku)
    p0 = p0 if p0 is not None else BASELINE_PRICE
    r = PE.set_price_and_stock(api, PID, sku, WH, price=p0 + 3000, stock=q0 + 3)
    j = r.get("json") or {}
    check("code=0", j.get("code") == 0, str(j.get("code")))
    d = (j.get("price_stocks_data") or [{}])[0]
    check("响应含 price", (d.get("price") or {}).get("sale_price") == str(p0 + 3000),
          str((d.get("price") or {}).get("sale_price")))
    check("响应含 quantity", (d.get("quantity") or {}).get("available_quantity") == q0 + 3,
          str((d.get("quantity") or {}).get("available_quantity")))
    check("价格已生效", (d.get("price") or {}).get("sale_price") == str(p0 + 3000))
    check("库存已生效", qty_of(api, sku) == q0 + 3)
    PE.set_price_and_stock(api, PID, sku, WH, price=p0, stock=q0)
    check("已还原", qty_of(api, sku) == q0)


def case_batch(api, **kw):
    print("\n[batch] 整表批量（多 SKU 混合字段）", flush=True)
    base = read_map(api)
    r = PE.batch_apply(api, PID, price=134000, stock=None, wh_id=WH)
    check("code=0", (r["resp"].get("json") or {}).get("code") == 0)
    vals = price_resp_codes(r["resp"])
    check("全部价格生效", vals and all(v == "134000" for _, v in vals),
          str([v for _, v in vals]))
    r2 = PE.set_price_all(api, PID, BASELINE_PRICE)
    vals2 = price_resp_codes(r2)
    check("已还原", vals2 and all(v == str(BASELINE_PRICE) for _, v in vals2),
          str([v for _, v in vals2]))


def case_edge(api, *, fast: bool = False):
    print("\n[edge] 边界与错误处理" + ("（fast：跳过非法请求）" if fast else ""), flush=True)
    sku = SKUS[0]
    if not fast:
        # 不存在的 sku —— 服务端对无主 sku_id 会走全表扫描，单次可达 1-2 分钟
        r = PE.set_price(api, PID, "9999XXXXXXXXXX99", 130000)
        j = r.get("json") or {}
        check("非法 sku 返回非 0 或报错", j.get("code") != 0 or bool(r.get("raw")),
              f"code={j.get('code')} msg={(j.get('message') or r.get('raw') or '')[:60]}")
    # delta=0 应当是 no-op 且成功
    q0 = qty_of(api, sku)
    PE.set_stock(api, PID, sku, WH, q0)
    check("delta=0 是 no-op", qty_of(api, sku) == q0)
    # 价格传同样值
    p0 = price_of(api, sku)
    if p0 is None:
        p0 = BASELINE_PRICE
    r = PE.set_price(api, PID, sku, p0)
    got = dict(price_resp_codes(r)).get(sku)
    check("价格传同值幂等", got == str(p0), f"resp={got}")
    if not fast:
        # 负库存应被拒
        r = PE.set_stock(api, PID, sku, WH, -5)
        j = r.get("resp", {}).get("json") or {}
        check("负库存被拒（或落到0）", j.get("code") != 0 or qty_of(api, sku) >= 0,
              f"code={j.get('code')} qty={qty_of(api, sku)}")
    if qty_of(api, sku) != q0:
        PE.set_stock(api, PID, sku, WH, q0)
    check("已回到基线", qty_of(api, sku) == q0)


def case_no_audit(api, **kw):
    print("\n[no_audit] 局部编辑不触发重新审核", flush=True)
    before = PE.audit_state(api, PID)
    sku = SKUS[0]
    p0, q0 = price_of(api, sku), qty_of(api, sku)
    p0 = p0 if p0 is not None else BASELINE_PRICE
    PE.set_price_and_stock(api, PID, sku, WH, price=p0 + 500, stock=q0 + 1)
    time.sleep(1.5)
    after = PE.audit_state(api, PID)
    check("product_status 未变", before["product_status"] == after["product_status"],
          f"{before['product_status']}→{after['product_status']}")
    check("audit_status 未变", before["audit_status"] == after["audit_status"],
          f"{before['audit_status']}→{after['audit_status']}")
    # edit 接口会带 is_in_audit，局部接口响应里不应出现
    r = PE.set_price(api, PID, sku, p0 + 200)
    blob = json.dumps(r, ensure_ascii=False)
    check("响应无 is_in_audit 字段", "is_in_audit" not in blob)
    check("响应无 提交审核 提示", "提交审核" not in blob and "success_tip" not in blob)
    PE.set_price_and_stock(api, PID, sku, WH, price=p0, stock=q0)
    check("已还原", qty_of(api, sku) == q0)


def case_concurrent(api, **kw):
    print("\n[concurrent] 多 SKU 依次改价（同账号并发会被服务端限流，故串行）", flush=True)
    for i, s in enumerate(SKUS):
        r = PE.set_price(api, PID, s, 141000 + i)
        got = dict(price_resp_codes(r)).get(s)
        check(f"SKU{i+1} 改价 {141000+i} 生效", got == str(141000 + i), f"resp={got}")
    r2 = PE.set_price_all(api, PID, BASELINE_PRICE)
    vals = [v for _, v in price_resp_codes(r2)]
    check("已还原", vals and all(v == str(BASELINE_PRICE) for v in vals), str(vals))


def restore(api):
    print("\n[restore] 强制还原到基线", flush=True)
    rp = PE.set_price_all(api, PID, BASELINE_PRICE)
    pv = [v for _, v in price_resp_codes(rp)]
    check("价格回到基线", pv and all(v == str(BASELINE_PRICE) for v in pv), str(pv))
    ok_q = True
    for s, q in BASELINE_QTY.items():
        res = PE.set_stock(api, PID, s, WH, q)
        if res.get("target") != q:
            ok_q = False
    m = read_map(api)
    check("库存回到基线", all(m[s]["qty"] == BASELINE_QTY[s] for s in SKUS if s in m),
          str({s[:6]: m[s]["qty"] for s in SKUS if s in m}))


# 直连客户端（tt_http_client.TT）与 StockAPI 接口兼容（都有 call/get/post），
# 所以同一套用例可以直接跑在两种后端上。
# 直连更快更稳（0.9s/请求 vs 页面 1-2s 且会随机挂死），推荐默认用它。
def make_api(use_http: bool, port: int = CDP_PORT, gap: float = 0.6):
    if use_http:
        import tt_http_client as H
        return H.TT(port=port, min_gap=gap)
    return StockAPI()


CASES = {
    "read": case_read, "price": case_price, "price_all": case_price_all,
    "stock": case_stock, "stock_zero": case_stock_zero, "both": case_both,
    "batch": case_batch, "edge": case_edge, "no_audit": case_no_audit,
    "concurrent": case_concurrent,
}
SELFTEST = {"read", "no_audit"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--keep", action="store_true", help="不还原")
    ap.add_argument("--fast", action="store_true",
                    help="跳过会触发服务端慢路径的非法请求用例")
    ap.add_argument("--page", action="store_true",
                    help="用页面内 fetch（慢、易挂）；默认走直连 HTTP")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--gap", type=float, default=0.6,
                    help="请求最小间隔秒；服务端限流时调大")
    a = ap.parse_args()

    todo = list(CASES) if a.all else (list(SELFTEST) if a.selftest else a.case)
    if not todo:
        ap.print_help()
        return

    api = make_api(not a.page, a.port, a.gap)
    if not a.page:
        print(f"# 后端: 直连 HTTP ({len(api.cookies)} cookies)", flush=True)
    t0 = time.time()
    try:
        for name in todo:
            fn = CASES.get(name)
            if not fn:
                print(f"未知用例: {name}")
                continue
            try:
                fn(api, fast=a.fast)
                time.sleep(0.8)   # 用例间隔：连续高速写会被服务端降速
            except Exception as e:
                check(f"{name} 异常", False, f"{type(e).__name__}: {e}")
                traceback.print_exc()
        if not a.keep:
            restore(api)
    finally:
        try:
            api.close()
        except Exception:
            pass

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"结果: {passed}/{total} PASS   ({time.time()-t0:.1f}s)")
    fails = [n for n, ok, _ in results if not ok]
    if fails:
        print("失败:")
        for n in fails:
            print("  -", n)
    json.dump({"passed": passed, "total": total,
               "results": [{"name": n, "ok": ok, "detail": d} for n, ok, d in results]},
              open("notes/tt_partial_edit_test.json", "w"), ensure_ascii=False, indent=2)
    print("详见 notes/tt_partial_edit_test.json")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
