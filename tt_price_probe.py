#!/usr/bin/env python3
"""价格/库存「局部编辑」接口参数爆破。

背景：完整 edit 会触发重新审核（影响商品权重），所以需要找到局部编辑接口。
库存侧已经确认：POST /product/stock/alert/set_stock，quantity 是增量。
价格侧候选接口从微前端 bundle 提取出来，但调用点在未加载的 chunk 里，
所以走「错误信息反推字段名」——服务端 binding 失败会报出缺失/非法字段。

用法：
  python3 tt_price_probe.py --read            # 只读：当前价格/库存
  python3 tt_price_probe.py --shapes          # 打印所有待测 payload 形状
  python3 tt_price_probe.py --probe <PID> <SKU> <目标价>
  python3 tt_price_probe.py --probe <PID> <SKU> <目标价> --only UpdateSKUPrice
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, ".")
from tt_stock_api import StockAPI  # noqa: E402

# 候选接口（来自 product_manage_stock / gateway bundle 的 API 层声明）
ENDPOINTS = {
    "UpdateSKUPrice":        "/api/v1/product/sku/price/update",
    "UpdateSKUPriceStocks":  "/api/v1/product/sku/price/stocks/update",
    "UpdateSkuPriceStocks":  "/api/v1/product/sku/price/stocks/update",
    "PartialEdit":           "/api/v1/product/local/product/partial/edit",
    "EditPrice":             "/api/v1/product/global/sku/price/edit",
}


def shapes(pid: str, sku: str, new_price: int, wh: str):
    """按「从简到繁」排列的候选 payload。服务端多数字段是可选/忽略的，
    所以先用最小形状探错误码，再逐步加字段。"""
    return [
        ("minimal",            {"product_id": pid, "sku_id": sku, "price": new_price}),
        ("sale_price_flat",    {"product_id": pid, "sku_id": sku, "sale_price": str(new_price)}),
        ("base_price",         {"product_id": pid, "sku_id": sku,
                                "base_price": {"region": "VN", "currency": "VND",
                                               "sale_price": str(new_price)}}),
        ("skus_array",         {"product_id": pid,
                                "skus": [{"id": sku, "sale_price": str(new_price)}]}),
        ("skus_price_obj",     {"product_id": pid,
                                "skus": [{"id": sku,
                                          "base_price": {"region": "VN", "currency": "VND",
                                                         "sale_price": str(new_price)}}]}),
        ("price_list",         {"product_id": pid, "sku_price_list": [
                                 {"sku_id": sku, "price": new_price}]}),
        ("sku_prices",         {"product_id": pid, "sku_prices": [
                                 {"sku_id": sku, "sale_price": str(new_price)}]}),
        ("region_price",       {"product_id": pid, "sku_id": sku,
                                "region_prices": [{"region": "VN", "currency": "VND",
                                                   "sale_price": str(new_price)}]}),
        ("with_wh",            {"product_id": pid, "sku_id": sku,
                                "base_price": {"region": "VN", "currency": "VND",
                                               "sale_price": str(new_price)},
                                "warehouse_quantity_list": [{"warehouse_id": wh, "quantity": 0}]}),
        ("alert_shape",        {"product_id": pid, "sku_id": sku,
                                "sale_price": str(new_price),
                                "warehouse_quantity_list": [{"warehouse_id": wh, "quantity": 0}]}),
    ]


def read_state(api: StockAPI, pid: str):
    r = api.call("GET", f"/api/v1/product/local/product/get?product_id={pid}")
    d = (r.get("json") or {}).get("data") or {}
    p = d.get("product") or {}
    out = {"product_status": p.get("product_status"), "audit_status": p.get("audit_status"), "skus": []}
    for s in p.get("skus") or []:
        bp = s.get("base_price") or {}
        out["skus"].append({
            "sku_id": s.get("id"),
            "seller_sku": s.get("seller_sku"),
            "sale_price": bp.get("sale_price"),
            "quantities": [(q.get("warehouse_id"), q.get("total_quantity"))
                           for q in (s.get("quantities") or [])],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--read")
    ap.add_argument("--shapes", nargs=4, metavar=("PID", "SKU", "PRICE", "WH"))
    ap.add_argument("--probe", nargs=3, metavar=("PID", "SKU", "PRICE"))
    ap.add_argument("--wh", default="7659XXXXXXXXXX08")
    ap.add_argument("--only", default=None, help="只测指定接口")
    a = ap.parse_args()

    if a.shapes:
        pid, sku, price, wh = a.shapes
        for n, b in shapes(pid, sku, int(price), wh):
            print(f"{n:18} {json.dumps(b, ensure_ascii=False)}")
        return

    api = StockAPI()
    try:
        if a.read:
            print(json.dumps(read_state(api, a.read), ensure_ascii=False, indent=2))
            return
        if not a.probe:
            ap.print_help()
            return

        pid, sku, price = a.probe
        price = int(price)
        before = read_state(api, pid)
        print("改前:", json.dumps(before, ensure_ascii=False))

        tasks = [(nm, ep, lb, body)
                 for nm, ep in ENDPOINTS.items()
                 if not a.only or a.only in nm
                 for lb, body in shapes(pid, sku, price, a.wh)]

        def run(t):
            nm, ep, lb, body = t
            try:
                r = api.call("POST", ep, body)
                j = r.get("json") or {}
                return {"ep": nm, "shape": lb, "status": r.get("status"),
                        "code": j.get("code"), "msg": (j.get("message") or "")[:110],
                        "raw": (r.get("raw") or "")[:90], "body": body}
            except Exception as e:
                return {"ep": nm, "shape": lb, "status": "EXC", "code": None,
                        "msg": str(e)[:110], "raw": "", "body": body}

        # 串行发，避免并发把接口层搞乱（也是礼仪式：写接口不该并发轰炸）
        results = []
        for t in tasks:
            results.append(run(t))
            time.sleep(0.25)

        print("\n--- 响应 ---")
        for r in results:
            tag = f"{r['ep']}/{r['shape']}"
            print(f"{tag:40} status={r['status']} code={r['code']} msg={r['msg'] or r['raw']}")

        time.sleep(2.0)
        after = read_state(api, pid)
        print("\n改后:", json.dumps(after, ensure_ascii=False))
        changed = json.dumps(before["skus"]) != json.dumps(after["skus"])
        print("\n>>> SKU 是否变化:", "是 ✅" if changed else "否 ❌")
        json.dump({"before": before, "after": after, "results": results},
                  open("notes/tt_price_probe.json", "w"), ensure_ascii=False, indent=2)
        print("详见 notes/tt_price_probe.json")
    finally:
        api.close()


if __name__ == "__main__":
    main()
