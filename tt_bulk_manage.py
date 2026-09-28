#!/usr/bin/env python3
"""批量价格 / 库存管理 —— 走局部编辑接口，不触发重新审核。

设计要点（都是踩过的坑）：
  · 同账号并发写会被 TikTok 服务端限流，请求会挂住 → 默认串行 + 可配间隔
  · 库存是增量语义，读-算-写之间有竞态 → 同一 SKU 严格串行，且写完即校验
  · 价格是绝对值语义，幂等 → 可以安全重试
  · 一次请求可以携带多个 SKU（商品内批量），跨商品必须分开请求

用法：
  # 改价：对一批商品统一设为 150000
  python3 tt_bulk_manage.py --price 150000 --products id1,id2,id3

  # 改价：按百分比调整（现值 × 1.1）
  python3 tt_bulk_manage.py --price-pct 10 --products id1,id2

  # 改库存：把指定仓库设为 100
  python3 tt_bulk_manage.py --stock 100 --wh 7659XXXXXXXXXX08 --products id1,id2

  # 从文件读商品 ID（每行一个，支持 # 注释）
  python3 tt_bulk_manage.py --price 150000 --file pids.txt

  # 干跑：只打印将要执行的操作，不写
  python3 tt_bulk_manage.py --price 150000 --products id1 --dry-run

  # 从店铺拉全部商品 ID 再批量操作
  python3 tt_bulk_manage.py --price 150000 --from-shop --limit 50

  # 只改草稿商品（tab_id=2）
  python3 tt_bulk_manage.py --price 150000 --from-shop --tab-id 2
"""
from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, ".")
import tt_partial_edit as PE  # noqa: E402
from tt_stock_api import StockAPI  # noqa: E402


def fetch_shop_products(api: StockAPI, tab_id: int = 1, limit: int | None = None,
                        page_size: int = 20) -> list[str]:
    """翻页拉取商品 ID。page_size 上限 50，超了服务端报 12052910。"""
    ids: list[str] = []
    page = 1
    while True:
        r = api.call("GET", f"/api/v1/product/web/local/products/list"
                            f"?tab_id={tab_id}&page_size={page_size}&page={page}")
        j = r.get("json") or {}
        d = j.get("data") or {}
        batch = [str(p.get("product_id")) for p in (d.get("products") or [])]
        ids.extend(batch)
        if limit and len(ids) >= limit:
            return ids[:limit]
        if not d.get("has_more") or not batch:
            return ids
        page += 1
        if page > 200:
            return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", help="逗号分隔的商品 ID")
    ap.add_argument("--file", help="商品 ID 文件（每行一个）")
    ap.add_argument("--from-shop", action="store_true", help="从店铺拉商品列表")
    ap.add_argument("--tab-id", type=int, default=1, help="商品 tab（默认 1=全部）")
    ap.add_argument("--limit", type=int, help="最多处理多少个商品")

    ap.add_argument("--price", help="设为该零售价（绝对值）")
    ap.add_argument("--price-pct", type=float, help="价格调整百分比，如 10 = 涨价 10%%")
    ap.add_argument("--stock", type=int, help="设为该库存数（目标值）")
    ap.add_argument("--wh", default="7659XXXXXXXXXX08", help="仓库 ID")
    ap.add_argument("--sku-filter", help="只处理 seller_sku 含该子串的 SKU")

    ap.add_argument("--delay", type=float, default=1.2, help="商品之间的间隔秒数")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json-out", help="结果写到该 JSON 文件")
    a = ap.parse_args()

    if not (a.price or a.price_pct is not None or a.stock is not None):
        ap.error("至少要指定 --price / --price-pct / --stock 之一")

    ids: list[str] = []
    if a.products:
        ids += [x.strip() for x in a.products.split(",") if x.strip()]
    if a.file:
        with open(a.file, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if line: CONTACT_REDACTED(line)

    api = StockAPI()
    report = {"ok": [], "fail": [], "skipped": []}
    t0 = time.time()
    try:
        if a.from_shop or not ids:
            got = fetch_shop_products(api, a.tab_id, a.limit)
            ids = ids or got
            print(f"店铺拉取: {len(got)} 个商品")
        ids = list(dict.fromkeys(ids))
        if a.limit:
            ids = ids[:a.limit]
        print(f"待处理: {len(ids)} 个商品  "
              f"(操作: {'改价 ' if a.price or a.price_pct is not None else ''}"
              f"{'改库存' if a.stock is not None else ''})\n")

        for n, pid in enumerate(ids, 1):
            try:
                rows = PE.sku_state(api, pid)
                if not rows:
                    report["skipped"].append({"pid": pid, "why": "无 SKU"})
                    print(f"[{n}/{len(ids)}] {pid}  跳过（无 SKU）")
                    continue
                if a.sku_filter:
                    rows = [r for r in rows if a.sku_filter in (r["seller_sku"] or "")]
                    if not rows:
                        report["skipped"].append({"pid": pid, "why": "SKU 未匹配"})
                        continue

                plan = []
                if a.price or a.price_pct is not None:
                    for r in rows:
                        if r["price"] is None:
                            continue
                        tgt = (int(a.price) if a.price
                               else int(round(r["price"] * (1 + a.price_pct / 100))))
                        plan.append(f"价 {r['price']}→{tgt}")
                if a.stock is not None:
                    for r in rows:
                        if r["warehouse_id"] != a.wh:
                            continue
                        plan.append(f"库存({r['warehouse_id'][:6]}) {r['qty']}→{a.stock}")

                if a.dry_run:
                    print(f"[{n}/{len(ids)}] {pid}  将执行: {len(plan)} 项  {'; '.join(plan[:4])}")
                    continue

                res = {}
                if a.price or a.price_pct is not None:
                    # 价格绝对值：多 SKU 一次请求
                    items = []
                    for r in rows:
                        if r["price"] is None:
                            continue
                        tgt = (int(a.price) if a.price
                               else int(round(r["price"] * (1 + a.price_pct / 100))))
                        items.append({"sku_id": str(r["sku_id"]), "sale_price": str(tgt)})
                    if items:
                        rr = api.call("POST", PE.PRICE_STOCKS,
                                      {"product_id": pid,
                                       "price_stocks_edit_data": items, "tab_id": a.tab_id})
                        res["price"] = (rr.get("json") or {}).get("code")
                if a.stock is not None:
                    # 库存增量：每个 SKU 单独算 delta，串行
                    codes = []
                    for r in rows:
                        if r["warehouse_id"] != a.wh:
                            continue
                        rr = PE.set_stock(api, pid, r["sku_id"], a.wh, a.stock)
                        codes.append((rr.get("resp", {}).get("json") or {}).get("code"))
                        time.sleep(0.35)
                    res["stock"] = codes

                ok = all(v == 0 for v in res.values() if isinstance(v, int)) and \
                     all(all(c == 0 for c in v) for v in res.values() if isinstance(v, list))
                (report["ok"] if ok else report["fail"]).append(
                    {"pid": pid, "plan": plan, "res": res})
                print(f"[{n}/{len(ids)}] {pid}  {'OK ' if ok else 'FAIL'}  {'; '.join(plan[:4])}"
                      + (f"  res={res}" if not ok else ""))
            except Exception as e:
                report["fail"].append({"pid": pid, "error": f"{type(e).__name__}: {e}"})
                print(f"[{n}/{len(ids)}] {pid}  ERROR  {type(e).__name__}: {e}")
            time.sleep(a.delay)

        print(f"\n{'='*60}")
        print(f"完成: {len(report['ok'])} OK / {len(report['fail'])} FAIL / "
              f"{len(report['skipped'])} 跳过   ({time.time()-t0:.1f}s)")
        if report["fail"]:
            print("失败清单:")
            for r in report["fail"][:20]:
                print("  ", r.get("pid"), r.get("error") or r.get("res"))
        if a.json_out:
            json.dump(report, open(a.json_out, "w"), ensure_ascii=False, indent=2)
            print(f"详见 {a.json_out}")
    finally:
        api.close()


if __name__ == "__main__":
    main()
