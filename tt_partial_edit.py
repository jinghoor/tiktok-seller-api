#!/usr/bin/env python3
"""TikTok 卖家中心「局部编辑」接口客户端 —— 价格 + 库存 + 审核清单价。

全部结论来自 UI 抓包 + bundle 源码双向验证。

═══════════════════════════════════════════════════════════════════
接口一：库存（单 SKU，单/多仓库）
  POST /api/v1/product/stock/alert/set_stock          (SetInShopStock)
  {"product_id","sku_id","warehouse_quantity_list":[{"warehouse_id","quantity"}]}
  · quantity 是**增量 delta**：界面输入目标值 T，当前 C → 发出 T-C，可为负
  · 源码证据：requestUpdateSkuQty → warehouse_quantity_list: r.map(e=>({
      warehouse_id: e.whId, quantity: e.increment }))
  · 响应回传 current_quantity_list（更新后的绝对值）

═══════════════════════════════════════════════════════════════════
接口二：价格 + 库存（可一次改多个 SKU）
  POST /api/v1/product/sku/price/stocks/update        (UpdateSkuPriceStocks)
  {"product_id","price_stocks_edit_data":[{...}],"tab_id"}
  单项字段（源码 product-manage.js 的 diffSkuToEditData）：
    sku_id            必填
    sale_price        **绝对值**（字符串）—— 改价用这个
    audit_list_price  审核清单价（绝对值）
    quantity_variation **增量**（数字）—— 改库存用这个
    warehouse_id      改库存时必填
    unit_inventory_items  单位级库存（组合装/多单位场景）
  过滤逻辑（源码原样）：
    w==='stock' ? e.quantity_variation!==undefined || unit_inventory_items?.length
  : w==='price' ? e.sale_price!==undefined || e.audit_list_price!==undefined
  : true
  · 响应回传 price_stocks_data，price / quantity 都是更新后的绝对值
  · 失败时可能返回 stock_edit_failed_skus

═══════════════════════════════════════════════════════════════════
为什么用它们：**不触发重新审核**
  完整编辑 POST /product/local/product/edit
    → 响应含 is_in_audit=true、success_tip="提交审核成功，变更内容将在审核通过后生效。"
    → ScenarioContext PublishScene:2
  上面两个局部接口
    → 响应只有 current_quantity_list / price_stocks_data，无任何审核字段
    → 商品 product_status / audit_status 不变

用法：
  python3 tt_partial_edit.py --read <PID>
  python3 tt_partial_edit.py --audit-check <PID>
  python3 tt_partial_edit.py --price   <PID> <SKU> <单价>
  python3 tt_partial_edit.py --price-all <PID> <单价>
  python3 tt_partial_edit.py --stock   <PID> <SKU> <WH> <目标库存>
  python3 tt_partial_edit.py --both    <PID> <SKU> <WH> --set-price N --set-stock M
  python3 tt_partial_edit.py --batch   <PID> --set-price N --set-stock M
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, ".")
from tt_stock_api import StockAPI  # noqa: E402

DEFAULT_WH = "7659XXXXXXXXXX08"   # Laojie（默认仓）
SET_STOCK = "/api/v1/product/stock/alert/set_stock"
PRICE_STOCKS = "/api/v1/product/sku/price/stocks/update"


# ───────────────────────── 读 ─────────────────────────

def get_product(api: StockAPI, pid: str) -> dict:
    """读商品对象。

    /product/local/product/get 对部分商品/后端不可用（直连返回 code=10000，
    页内 fetch 也可能拿不到）。失败时降级到列表接口 —— 列表同样带
    skus / sale_price_ranges / total_available_stock，足够算增量。
    """
    try:
        r = api.call("GET", f"/api/v1/product/local/product/get?product_id={pid}")
        j = r.get("json") or {}
        if j.get("code") == 0:
            p = (j.get("data") or {}).get("product") or {}
            if p.get("skus"):
                return p
    except Exception:
        pass
    return _product_from_list(api, pid)


def _product_from_list(api: StockAPI, pid: str, *, tab_ids=(1, 2)) -> dict:
    for tab in tab_ids:
        page = 1
        while page <= 10:
            r = api.call("GET", f"/api/v1/product/web/local/products/list"
                                f"?tab_id={tab}&page_size=50&page={page}")
            d = (r.get("json") or {}).get("data") or {}
            prods = d.get("products") or []
            hit = next((x for x in prods if str(x.get("product_id")) == str(pid)), None)
            if hit:
                # 列表里 skus 只有 id/seller_sku，归一化成 get 的形状
                hit["skus"] = [{"id": s.get("id"), "seller_sku": s.get("seller_sku"),
                                "base_price": {}, "quantities": []}
                               for s in (hit.get("skus") or [])]
                return hit
            if not d.get("has_more") or not prods:
                break
            page += 1
    return {}


def probe_stock(api: StockAPI, pid: str, sku_id: str, wh_id: str) -> int | None:
    """零增量探测：set_stock 传 quantity=0 是 no-op，但响应回传
    current_quantity_list（更新后的绝对值）。等于一次免费读法。"""
    body = {"product_id": str(pid), "sku_id": str(sku_id),
            "warehouse_quantity_list": [{"warehouse_id": str(wh_id), "quantity": 0}]}
    r = api.call("POST", SET_STOCK, body)
    for x in ((r.get("json") or {}).get("current_quantity_list") or []):
        if str(x.get("warehouse_id")) == str(wh_id):
            return x.get("quantity")
    return None


def price_from_list(api: StockAPI, pid: str) -> int | None:
    """兜底：从列表的 sale_price_ranges 取区间下限当参考价。"""
    try:
        p = _product_from_list(api, pid)
        for rng in (p.get("sale_price_ranges") or []):
            pr = rng.get("price_range") or ""
            nums = "".join(ch if ch.isdigit() else " " for ch in pr).split()
            if nums:
                return int(nums[0])
    except Exception:
        pass
    return None


def sku_state(api: StockAPI, pid: str, wh_id: str | None = None) -> list[dict]:
    """每个 SKU × 仓库一行：{sku_id, seller_sku, price, warehouse_id, qty}

    库存优先取 quantities；拿不到（走 list 降级时）就用零增量探测补齐。
    价格拿不到时为 None —— 用 probe_price / price_from_list 补。
    """
    p = get_product(api, pid)
    out = []
    for s in p.get("skus") or []:
        price = (s.get("base_price") or {}).get("sale_price")
        qs = s.get("quantities") or []
        if qs:
            for q in qs:
                out.append({"sku_id": s.get("id"), "seller_sku": s.get("seller_sku"),
                            "price": int(price) if price else None,
                            "warehouse_id": q.get("warehouse_id"),
                            "qty": q.get("total_quantity")})
        else:
            # 降级路径：列表不给逐仓库存，用探测
            probe_wh = wh_id or DEFAULT_WH
            out.append({"sku_id": s.get("id"), "seller_sku": s.get("seller_sku"),
                        "price": int(price) if price else None,
                        "warehouse_id": probe_wh,
                        "qty": probe_stock(api, pid, s.get("id"), probe_wh)})
    return out


def audit_state(api: StockAPI, pid: str) -> dict:
    p = get_product(api, pid)
    sp = (p.get("sale_platform_products") or [{}])[0]
    return {"product_id": p.get("product_id"),
            "product_status": p.get("product_status"),
            "audit_status": p.get("audit_status"),
            "product_status_view": sp.get("product_status_view") or p.get("product_status_view"),
            "suspend_reason": sp.get("suspend_reason") or p.get("suspend_reason"),
            "product_warehouse_status": p.get("product_warehouse_status")}


# ───────────────────────── 写 ─────────────────────────

def set_price(api: StockAPI, pid: str, sku_id: str, target: int | str, *,
              tab_id: int = 2, audit_list_price: int | str | None = None):
    """改单个 SKU 价格。sale_price 是绝对值，不需要读当前值。"""
    item: dict = {"sku_id": str(sku_id), "sale_price": str(target)}
    if audit_list_price is not None:
        item["audit_list_price"] = str(audit_list_price)
    body = {"product_id": str(pid), "price_stocks_edit_data": [item], "tab_id": tab_id}
    return api.call("POST", PRICE_STOCKS, body)


def set_price_all(api: StockAPI, pid: str, target: int | str, *, tab_id: int = 2):
    """一次请求改该商品所有 SKU 的价格。"""
    rows, seen = sku_state(api, pid), set()
    items = []
    for r in rows:
        if r["sku_id"] in seen:
            continue
        seen.add(r["sku_id"])
        items.append({"sku_id": str(r["sku_id"]), "sale_price": str(target)})
    if not items:
        raise RuntimeError("没有可改的 SKU")
    body = {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": tab_id}
    return api.call("POST", PRICE_STOCKS, body)


def set_stock(api: StockAPI, pid: str, sku_id: str, wh_id: str, target: int):
    """改单个 SKU 在指定仓库的库存（走 set_stock，quantity 是增量）。"""
    rows = sku_state(api, pid)
    cur = next((r for r in rows if r["sku_id"] == sku_id and r["warehouse_id"] == wh_id), None)
    now = int(cur["qty"] or 0) if cur else 0
    delta = int(target) - now
    body = {
        "product_id": str(pid),
        "sku_id": str(sku_id),
        "warehouse_quantity_list": [{"warehouse_id": str(wh_id), "quantity": delta}],
    }
    return {"from": now, "delta": delta, "target": int(target),
            "resp": api.call("POST", SET_STOCK, body)}


def set_price_and_stock(api: StockAPI, pid: str, sku_id: str, wh_id: str, *,
                        price: int | str | None = None, stock: int | None = None,
                        tab_id: int = 2):
    """一次请求同时改价 + 改库存（源码里 price_stocks_edit_data 两种字段并存）。"""
    item: dict = {"sku_id": str(sku_id)}
    if price is not None:
        item["sale_price"] = str(price)
    if stock is not None:
        rows = sku_state(api, pid)
        cur = next((r for r in rows if r["sku_id"] == sku_id and r["warehouse_id"] == wh_id), None)
        now = int(cur["qty"] or 0) if cur else 0
        item["warehouse_id"] = str(wh_id)
        item["quantity_variation"] = int(stock) - now
    body = {"product_id": str(pid), "price_stocks_edit_data": [item], "tab_id": tab_id}
    return api.call("POST", PRICE_STOCKS, body)


def batch_apply(api: StockAPI, pid: str, *, price: int | str | None = None,
                stock: int | None = None, wh_id: str | None = None, tab_id: int = 2):
    """整表批量：每个 SKU 一条，价格绝对值 + 库存增量一起发（等价界面「批量编辑」）。"""
    rows = sku_state(api, pid)
    items, detail = [], []
    for r in rows:
        if wh_id and r["warehouse_id"] != wh_id:
            continue
        item: dict = {"sku_id": str(r["sku_id"])}
        if price is not None:
            item["sale_price"] = str(price)
        if stock is not None:
            now = int(r["qty"] or 0)
            item["warehouse_id"] = str(r["warehouse_id"])
            item["quantity_variation"] = int(stock) - now
            detail.append({"sku_id": r["sku_id"], "wh": r["warehouse_id"],
                           "qty": f"{now}→{stock}"})
        if len(item) > 1:
            items.append(item)
    if not items:
        raise RuntimeError("没有可提交的变更")
    body = {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": tab_id}
    return {"changed": detail, "items": len(items),
            "resp": api.call("POST", PRICE_STOCKS, body)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", metavar="PID")
    ap.add_argument("--audit-check", metavar="PID")
    ap.add_argument("--price", nargs=3, metavar=("PID", "SKU", "单价"))
    ap.add_argument("--price-all", nargs=2, metavar=("PID", "单价"))
    ap.add_argument("--stock", nargs=4, metavar=("PID", "SKU", "WH", "目标库存"))
    ap.add_argument("--both", nargs=3, metavar=("PID", "SKU", "WH"))
    ap.add_argument("--batch", metavar="PID")
    ap.add_argument("--set-price")
    ap.add_argument("--set-stock", type=int)
    ap.add_argument("--wh")
    ap.add_argument("--tab-id", type=int, default=2)
    a = ap.parse_args()

    api = StockAPI()
    try:
        if a.read:
            print(json.dumps(sku_state(api, a.read), ensure_ascii=False, indent=2))
        elif a.audit_check:
            print(json.dumps(audit_state(api, a.audit_check), ensure_ascii=False, indent=2))
        elif a.price:
            pid, sku, t = a.price
            print(json.dumps(set_price(api, pid, sku, t, tab_id=a.tab_id),
                             ensure_ascii=False, indent=2))
        elif a.price_all:
            pid, t = a.price_all
            print(json.dumps(set_price_all(api, pid, t, tab_id=a.tab_id),
                             ensure_ascii=False, indent=2))
        elif a.stock:
            pid, sku, wh, t = a.stock
            print(json.dumps(set_stock(api, pid, sku, wh, int(t)), ensure_ascii=False, indent=2))
        elif a.both:
            pid, sku, wh = a.both
            r = set_price_and_stock(api, pid, sku, wh, price=a.set_price,
                                    stock=a.set_stock, tab_id=a.tab_id)
            print(json.dumps(r, ensure_ascii=False, indent=2))
        elif a.batch:
            r = batch_apply(api, a.batch, price=a.set_price, stock=a.set_stock,
                            wh_id=a.wh, tab_id=a.tab_id)
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            ap.print_help()
    finally:
        api.close()


if __name__ == "__main__":
    main()
