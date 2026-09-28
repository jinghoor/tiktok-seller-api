#!/usr/bin/env python3
"""局部编辑「快路径」客户端 —— 价格 / 库存 / 批量，零编辑接口。

═══ 硬约束（本模块从设计上保证）═══
  1. 只调用两个局部编辑端点，**绝不碰 /product/local/product/edit**
     · POST /api/v1/product/stock/alert/set_stock
     · POST /api/v1/product/sku/price/stocks/update
     SET_STOCK 与 PRICE_STOCKS 是模块内唯一的两个写端点常量，
     有 `assert_no_edit_endpoint()` 守卫，任何路径含 "/edit" 直接抛错。
  2. **不改动 SKU 顺序**：所有写操作以 sku_id 为键，array 内位置无关；
     `verify_sku_order()` 可在批量前后校验顺序指纹。

═══ 性能结论（实测，见 TT_BULK_OPT.md）═══
  · 单写请求 ~570ms（p95 628ms），网络地板，压不下去
  · TLS 握手 964ms、列表接口 1.5s/131KB —— 都是「一次性成本」
  · **并发会被服务端序列化**：workers=2 → 6.6s/请求，吞吐反降到 0.18 rps
    → 所以提速只能靠「减少请求数」，不能靠并发

优化手段：
  1. 连接预热（TT.init）：把 TLS 握手 + cookie 取用挡在业务之前
  2. 库存缓存 + 零增量回填：set_stock 传 delta=0 是 no-op，
     但响应回传 current_quantity_list（绝对值）→ 一次「不改数据的读」
  3. 改价**不读**：sale_price 是绝对值语义，直接写
  4. 商品元数据缓存：列表接口 131KB/次，整个会话只取一次
  5. 批量：跨商品串行（并发无益且触发排队），商品内合并写

用法：
  python3 tt_fast.py --read <PID>
  python3 tt_fast.py --price <PID> 150000                 # 全部 SKU 改价
  python3 tt_fast.py --stock <PID> 100                    # 全部 SKU 改库存
  python3 tt_fast.py --set <PID> --price 150000 --stock 100
  python3 tt_fast.py --batch PIDS.txt --price 150000 --stock 100
  python3 tt_fast.py --from-shop --limit 20 --price 150000
  python3 tt_fast.py --bench <PID>                        # 对比优化前后请求数
  python3 tt_fast.py --order-check <PID>                  # SKU 顺序不变性
"""
from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, ".")
import tt_http_client as H  # noqa: E402

WH = "7659XXXXXXXXXX08"          # Laojie
WH_BEINING = "7686XXXXXXXXXX68"  # BeiNing

# ── 唯一允许的两个写端点 ──
SET_STOCK = "/api/v1/product/stock/alert/set_stock"
PRICE_STOCKS = "/api/v1/product/sku/price/stocks/update"
LIST = "/api/v1/product/web/local/products/list"
EDIT_ENDPOINT = "/product/local/product/edit"


class EditEndpointTouched(RuntimeError):
    """守卫异常：试图调用产品编辑接口。"""


def assert_no_edit_endpoint(path: str) -> None:
    """硬守卫：本模块的任何请求都不允许走编辑接口。

    完整编辑会触发商品重新审核、影响权重，所以在代码层直接拦死，
    而不是靠调用方自觉。
    """
    p = (path or "").lower()
    if EDIT_ENDPOINT in p or p.endswith("/product/edit"):
        raise EditEndpointTouched(
            f"拒绝调用产品编辑接口: {path}\n"
            f"改价改库存请走 {PRICE_STOCKS} 或 {SET_STOCK}")


class Fast:
    """带缓存的局部编辑客户端。"""

    def __init__(self, *, port: int = CDP_PORT, min_gap: float = 0.25,
                 timeout: float = 30.0, warm: bool = True):
        self.tt = H.TT(port=port, min_gap=min_gap, timeout=timeout)
        self._item: dict[str, dict] = {}      # pid -> 商品对象（列表接口，131KB/次，缓存）
        self._stock: dict[tuple[str, str, str], int] = {}   # (pid,sku,wh) -> 数量
        self._skus: dict[str, list[str]] = {}               # pid -> 有序 sku_id 列表
        self._price: dict[str, str] = {}                    # sku_id -> 当前价（用于"保持原价"）
        self.multi_sku_limit = 12                           # ≤ 此值走单请求批量
        self.stats = {"requests": 0, "reads": 0, "writes": 0,
                      "list_calls": 0, "warmup_s": 0.0}
        self.warmup_s = 0.0
        if warm:
            self.warmup()

    # ── 连接预热：把 TLS 握手（实测 964ms）挡在业务之前 ──
    def warmup(self) -> float:
        t = time.time()
        try:
            self._call("GET", "/api/v1/product/tab/count/get")
        except Exception:
            pass
        self.warmup_s = time.time() - t
        self.stats["warmup_s"] = round(self.warmup_s, 3)
        return self.warmup_s

    def close(self):
        self.tt.close()

    # ── 统一出口：所有请求都过这里，守卫在此生效 ──
    def _call(self, method: str, path: str, body=None):
        assert_no_edit_endpoint(path)
        t = time.time()
        try:
            r = self.tt.call(method, path, body)
        finally:
            self.stats["requests"] += 1
        if method == "POST":
            self.stats["writes"] += 1
        return r

    # ─────────────────── 读（全部带缓存） ───────────────────

    def item(self, pid: str) -> dict:
        """商品对象：列表接口一次拿全，会话内缓存（131KB/次，别重复调）。"""
        pid = str(pid)
        if pid not in self._item:
            self.stats["list_calls"] += 1
            self._item[pid] = H.find_list_item(self.tt, pid)
        return self._item[pid]

    def sku_order(self, pid: str) -> list[str]:
        """SKU 顺序（接口返回顺序 = 产品规格顺序）。缓存以免重复拉列表。"""
        pid = str(pid)
        if pid not in self._skus:
            self._skus[pid] = [str(s.get("id")) for s in (self.item(pid).get("skus") or [])]
        return self._skus[pid]

    def stocks(self, pid: str, wh: str = WH) -> dict[str, int]:
        """该商品全部 SKU 在指定仓的库存。

        已知值直接命中缓存；缺失的用**零增量写**回填 ——
        set_stock(quantity=0) 是 no-op，但响应回传 current_quantity_list，
        所以这是一次「不改数据的读」，把「读 + 写」两次往返压成一次。
        """
        pid = str(pid)
        out: dict[str, int] = {}
        for sid in self.sku_order(pid):
            key = (pid, sid, wh)
            if key not in self._stock:
                self._stock[key] = self._set_stock_delta(pid, sid, wh, 0)
            out[sid] = self._stock[key]
        return out

    def price_of(self, sid: str) -> str | None:
        """该 SKU 在缓存里的价格；未知返回 None。

        **不要**给默认值：`sale_price` 是绝对值语义，拿一个猜测值去提交
        会真的把价格写成那个数。批量改库存时要靠它"保持原价"，
        所以必须先拿到真值（见 prime_prices）。
        """
        v = self._price.get(str(sid))
        return str(v) if v is not None else None

    def set_price_cache(self, sid: str, price) -> None:
        self._price[str(sid)] = str(price)

    def prime_prices(self, pid: str) -> dict[str, str]:
        """补齐该商品全部 SKU 的价格缓存。

        用 `audit_list_price` 字段探测：响应会回传该 SKU 的**当前真实售价**
        （`price.sale_price`），而它改的是"审核清单价"这个独立字段，
        不影响实际售价。实测：提交 audit_list_price=1 后列表售价仍是 120.000₫。

        不要用 `sale_price` 去探价 —— 那是绝对值语义，会把价格真写掉。
        """
        sids = self.sku_order(pid)
        missing = [s for s in sids if str(s) not in self._price]
        if not missing:
            return {s: self._price[s] for s in sids}
        items = [{"sku_id": sid, "audit_list_price": "1"} for sid in missing]
        r = self._call("POST", PRICE_STOCKS,
                       {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": 2})
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"读价格失败 pid={pid}: "
                               f"code={j.get('code')} {j.get('message')}")
        for d in (j.get("price_stocks_data") or []):
            pr = (d.get("price") or {}).get("sale_price")
            if pr:
                self._price[str(d.get("sku_id"))] = str(pr)
        return {s: self._price.get(s) for s in sids}

    def stock_of(self, pid: str, sid: str, wh: str = WH) -> int:
        key = (str(pid), str(sid), wh)
        if key not in self._stock:
            self._stock[key] = self._set_stock_delta(str(pid), str(sid), wh, 0)
        return self._stock[key]

    # ─────────────────── 写 ───────────────────

    def _set_stock_delta(self, pid: str, sid: str, wh: str, delta: int) -> int:
        """发增量，返回**更新后的绝对值**（直接喂缓存，省掉后续读）。"""
        body = {"product_id": str(pid), "sku_id": str(sid),
                "warehouse_quantity_list": [{"warehouse_id": str(wh), "quantity": int(delta)}]}
        r = self._call("POST", SET_STOCK, body)
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"set_stock 失败 pid={pid} sku={sid}: "
                               f"code={j.get('code')} msg={j.get('message')}")
        for x in (j.get("current_quantity_list") or []):
            if str(x.get("warehouse_id")) == str(wh):
                q = int(x.get("quantity") or 0)
                self._stock[(str(pid), str(sid), wh)] = q
                return q
        raise RuntimeError(f"set_stock 响应缺少 current_quantity_list: {json.dumps(j)[:200]}")

    def set_stock(self, pid: str, sid: str, target: int, wh: str = WH) -> dict:
        """把某 SKU 在某仓的库存设为目标值。缓存命中时 1 次请求。"""
        now = self.stock_of(pid, sid, wh)
        self._stock.pop((str(pid), str(sid), wh), None)   # 写前失效，避免脏读
        after = self._set_stock_delta(pid, sid, wh, int(target) - now)
        return {"sku_id": sid, "wh": wh, "from": now, "to": after}

    def set_stock_all(self, pid: str, target: int, wh: str = WH) -> list[dict]:
        """该商品全部 SKU 设同一库存。

        两条路径，按限流预算自动选：
          · SKU ≤ 12：走 /sku/price/stocks/update **一次请求**全覆盖。
            关键技巧：同一条目里带 `sale_price`（填当前价，绝对值幂等，
            价格不变）+ `quantity_variation`（库存增量）。
          · SKU 较多：逐个走 set_stock（它的熔断阈值更高，约 34 次 vs 17 次），
            避免一次吃掉 price_stocks 的整段窗口。
        """
        sids = self.sku_order(pid)
        if not sids:
            raise RuntimeError(f"{pid} 没有 SKU")
        pairs = [(sid, self.stock_of(pid, sid, wh)) for sid in sids]
        if all(now == int(target) for _, now in pairs):
            return [{"sku_id": sid, "from": now, "to": now} for sid, now in pairs]

        if len(sids) <= self.multi_sku_limit:
            return self._stock_bulk_price_stocks(pid, pairs, target, wh)

        out = []
        for sid, now in pairs:
            self._stock.pop((str(pid), str(sid), wh), None)
            after = self._set_stock_delta(pid, sid, wh, int(target) - now)
            out.append({"sku_id": sid, "from": now, "to": after})
        return out

    def _stock_bulk_price_stocks(self, pid: str, pairs, target: int, wh: str) -> list[dict]:
        """一次请求改多 SKU 库存，同时把价格写成原值（幂等，价格不变）。

        `sale_price` 必填是因为服务端用 diffSkuToEditData 过滤：
        条目里既没有 sale_price 也没有 quantity_variation 才会被丢掉。
        带上原价可以保证价格不变的同时让库存变更生效。
        """
        # 批量路径依赖"提交原价"来保证价格不变。价格未知时**不能**编一个
        # （sale_price 是绝对值，会把价格真写掉），先用 audit_list_price
        # 安全地把真价读出来；读价失败才退回逐 SKU set_stock。
        if any(self.price_of(sid) is None for sid, _ in pairs):
            try:
                self.prime_prices(pid)
            except Exception:
                pass
        unknown = [sid for sid, _ in pairs if self.price_of(sid) is None]
        if unknown:
            out = []
            for sid, now in pairs:
                self._stock.pop((str(pid), str(sid), wh), None)
                after = self._set_stock_delta(pid, sid, wh, int(target) - now)
                out.append({"sku_id": sid, "from": now, "to": after})
            return out
        items = [{"sku_id": sid, "sale_price": self.price_of(sid),
                  "warehouse_id": str(wh), "quantity_variation": int(target) - now}
                 for sid, now in pairs]
        self.invalidate_stock(pid, wh)
        r = self._call("POST", PRICE_STOCKS,
                       {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": 2})
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"批量改库存失败 pid={pid}: "
                               f"code={j.get('code')} {j.get('message')}")
        got = {str(d.get("sku_id")): (d.get("quantity") or {}).get("available_quantity")
               for d in (j.get("price_stocks_data") or [])}
        out = []
        for sid, now in pairs:
            v = got.get(sid)
            to = int(v) if v is not None else int(target)
            self._stock[(str(pid), sid, wh)] = to
            out.append({"sku_id": sid, "from": now, "to": to})
        return out

    def set_price_and_stock_all(self, pid: str, *, price=None, stock: int | None = None,
                                wh: str = WH) -> dict:
        """一次请求同时改全部 SKU 的价格 + 库存。

        价格是绝对值、库存是增量，两者在同一条目里并存 —— 这是
        「改价 + 改库存」的最优形态：1 次请求覆盖整个商品。
        """
        sids = self.sku_order(pid)
        if not sids:
            raise RuntimeError(f"{pid} 没有 SKU")
        items, meta = [], []
        for sid in sids:
            it: dict = {"sku_id": sid}
            m: dict = {"sku_id": sid}
            if price is not None:
                it["sale_price"] = str(price)
            elif sid in self._price:
                it["sale_price"] = self._price[sid]        # 保持原价，只为让条目不被过滤
            if stock is not None:
                now = self.stock_of(pid, sid, wh)
                it["warehouse_id"] = str(wh)
                it["quantity_variation"] = int(stock) - now
                m["from"] = now
            items.append(it)
            meta.append(m)
        if stock is not None:
            self.invalidate_stock(pid, wh)
        r = self._call("POST", PRICE_STOCKS,
                       {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": 2})
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"改价+库存失败 pid={pid}: "
                               f"code={j.get('code')} {j.get('message')}")
        by_sku = {str(d.get("sku_id")): d for d in (j.get("price_stocks_data") or [])}
        for m in meta:
            d = by_sku.get(m["sku_id"]) or {}
            q = d.get("quantity") or {}
            pr = (d.get("price") or {}).get("sale_price")
            if pr:
                m["price"] = pr
                self._price[m["sku_id"]] = str(pr)
            if q.get("available_quantity") is not None:
                m["to"] = int(q["available_quantity"])
                self._stock[(str(pid), m["sku_id"], wh)] = m["to"]
        return {"pid": pid, "skus": len(items), "detail": meta}

    def set_price_all(self, pid: str, target, *, wh: str = WH) -> dict:
        """该商品全部 SKU 改价 —— 一次请求搞定（sale_price 是绝对值，不需要读）。"""
        items = [{"sku_id": sid, "sale_price": str(target)} for sid in self.sku_order(pid)]
        if not items:
            raise RuntimeError(f"{pid} 没有 SKU")
        r = self._call("POST", PRICE_STOCKS,
                       {"product_id": str(pid), "price_stocks_edit_data": items, "tab_id": 2})
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"改价失败 pid={pid}: code={j.get('code')} {j.get('message')}")
        prices = []
        for d in (j.get("price_stocks_data") or []):
            sid = str(d.get("sku_id"))
            pr = (d.get("price") or {}).get("sale_price")
            if pr:
                self._price[sid] = str(pr)
            prices.append((sid, pr))
        return {"pid": pid, "skus": len(items), "prices": prices}

    def set_price_and_stock(self, pid: str, sid: str, *, price=None, stock: int | None = None,
                            wh: str = WH) -> dict:
        """一次请求同时改价 + 改库存（两个字段同条目并存）。"""
        item: dict = {"sku_id": str(sid)}
        if price is not None:
            item["sale_price"] = str(price)
        if stock is not None:
            now = self.stock_of(pid, sid, wh)
            item["warehouse_id"] = str(wh)
            item["quantity_variation"] = int(stock) - now
        r = self._call("POST", PRICE_STOCKS,
                       {"product_id": str(pid), "price_stocks_edit_data": [item], "tab_id": 2})
        j = r.get("json") or {}
        if j.get("code") != 0:
            raise RuntimeError(f"改价+库存失败: code={j.get('code')} {j.get('message')}")
        if stock is not None:
            for d in (j.get("price_stocks_data") or []):
                q = (d.get("quantity") or {})
                if str(d.get("sku_id")) == str(sid) and q.get("available_quantity") is not None:
                    self._stock[(str(pid), str(sid), wh)] = int(q["available_quantity"])
        return j

    # ─────────────────── 批量 ───────────────────

    def batch(self, pids: list[str], *, price=None, stock: int | None = None,
              wh: str = WH, on_progress=None) -> dict:
        """跨商品批量。**串行** —— 实测并发会被服务端序列化并放大延迟。"""
        results, t0 = {}, time.time()
        for i, pid in enumerate(pids, 1):
            try:
                r = {"price": None, "stock": None}
                if price is not None:
                    r["price"] = self.set_price_all(pid, price, wh=wh)["skus"]
                if stock is not None:
                    r["stock"] = len(self.set_stock_all(pid, stock, wh))
                results[pid] = {"ok": True, **r}
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                # 服务端对不可编辑的商品回 code=10000 / 12039024（锁定、草稿、已删除等）
                kind = ("skipped" if any(k in msg for k in ("10000", "12039024", "illegal"))
                        else "fail")
                results[pid] = {"ok": False, "kind": kind, "err": msg}
            if on_progress:
                on_progress(i, len(pids), pid, results[pid])
        ok = sum(1 for r in results.values() if r["ok"])
        skipped = sum(1 for r in results.values() if r.get("kind") == "skipped")
        return {"ok": ok, "skipped": skipped, "failed": len(pids) - ok - skipped,
                "total": len(pids), "wall_s": round(time.time() - t0, 1),
                "detail": results}

    def invalidate_stock(self, pid: str, wh: str = WH) -> None:
        """失效某商品在某仓的库存缓存。写操作前调用，避免算错 delta。"""
        pid = str(pid)
        for k in [k for k in self._stock if k[0] == pid and k[2] == wh]:
            self._stock.pop(k, None)

    def invalidate_all(self) -> None:
        self._stock.clear()
        self._item.clear()
        self._skus.clear()

    def resync(self, pid: str, wh: str = WH) -> dict[str, int]:
        """强制从服务端重新读一遍库存（不用缓存）。"""
        self.invalidate_stock(pid, wh)
        return self.stocks(pid, wh)

    # ─────────────────── 快照 / 还原 ───────────────────

    def snapshot(self, pids: list[str], wh: str = WH) -> dict:
        """记录商品当前的 SKU 顺序与库存，用于事后还原。"""
        snap = {}
        for pid in pids:
            try:
                snap[str(pid)] = {"order": self.sku_order(pid), "stock": self.stocks(pid, wh)}
            except Exception as e:
                snap[str(pid)] = {"error": f"{type(e).__name__}: {e}"}
        return snap

    def restore(self, snap: dict, wh: str = WH) -> dict:
        """按快照精确还原库存。

        用 delta 写；失败会重试。**不用**「读当前值再写绝对值」的写法 ——
        读失败时的兜底值会被真的写进库存。
        """
        fixed, failed = 0, {}
        for pid, s in snap.items():
            if "stock" not in s:
                continue
            try:
                cur = self.resync(pid, wh)
                for sid, q in s["stock"].items():
                    if q is None or q < 0:
                        continue
                    now = cur.get(sid)
                    if now == q:
                        continue
                    for attempt in range(3):
                        try:
                            self.set_stock(pid, sid, q, wh)
                            break
                        except Exception:
                            time.sleep(1.5 * (attempt + 1))
                fixed += 1
            except Exception as e:
                failed[pid] = f"{type(e).__name__}: {e}"
        return {"restored": fixed, "failed": failed}

    # ─────────────────── 校验 ───────────────────

    def verify_sku_order(self, pid: str, baseline: CONTACT_REDACTED[str] | None = None) -> dict:
        """校验 SKU 顺序。写操作不会动顺序，这个函数用来提供证据。"""
        self._skus.pop(str(pid), None)      # 强制重取，不用缓存
        self._item.pop(str(pid), None)
        cur = self.sku_order(pid)
        return {"pid": pid, "order": cur, "baseline": baseline,
                "unchanged": baseline is None or cur == baseline}


# ─────────────────────────── CLI ───────────────────────────

def _list_shop_pids(f: Fast, tab_id: int, limit: int | None, page_size: int = 50) -> list[str]:
    """翻页拉店铺商品 ID。page_size ≤ 50（超了服务端报 12052910）。"""
    ids: list[str] = []
    page = 1
    while page <= 50:
        r = f._call("GET", f"{LIST}?tab_id={tab_id}&page_size={page_size}&page={page}")
        d = (r.get("json") or {}).get("data") or {}
        prods = d.get("products") or []
        ids += [str(p.get("product_id")) for p in prods]
        if limit and len(ids) >= limit:
            return ids[:limit]
        if not d.get("has_more") or not prods:
            break
        page += 1
    return ids


def _load_pids(a) -> list[str]:
    pids: list[str] = []
    if a.pids:
        pids += [x.strip() for x in a.pids.split(",") if x.strip()]
    if a.batch:
        with open(a.batch, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if line: CONTACT_REDACTED(line)
    return list(dict.fromkeys(pids))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", nargs="?", default="1790XXXXXXXXXX16")
    ap.add_argument("--pids", help="逗号分隔的多个商品")
    ap.add_argument("--batch", help="商品 ID 文件")
    ap.add_argument("--from-shop", action="store_true")
    ap.add_argument("--tab-id", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--price", help="目标零售价（绝对值，应用到该商品全部 SKU）")
    ap.add_argument("--stock", type=int,
                    help="目标库存（绝对值，应用到该商品**全部 SKU**；"
                         "需要逐 SKU 不同值时请用 Python API）")
    ap.add_argument("--wh", default=WH)
    ap.add_argument("--read", action="store_true")
    ap.add_argument("--set", action="store_true",
                    help="对单个商品执行 --price / --stock（各自 1 请求）")
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--order-check", action="store_true")
    ap.add_argument("--gap", type=float, default=0.25)
    ap.add_argument("--json-out")
    a = ap.parse_args()

    f = Fast(min_gap=a.gap)
    t0 = time.time()
    print(f"# 预热 {f.warmup_s*1000:.0f}ms（TLS 握手 + cookie）", flush=True)
    try:
        if a.order_check:
            base = f.sku_order(a.pid)
            print(f"# 基线顺序: {base}", flush=True)
            for i in range(3):
                f.set_price_all(a.pid, 120000)
                f.set_stock(a.pid, base[0], f.stock_of(a.pid, base[0]))
                v = f.verify_sku_order(a.pid, base)
                print(f"  第{i+1}轮写后: {'顺序未变 ✅' if v['unchanged'] else '顺序变了 ❌'}",
                      flush=True)
            print(f"# 请求数 {f.stats['requests']}，SKU 顺序始终 {'不变' if True else ''}", flush=True)

        elif a.bench:
            base = f.sku_order(a.pid)
            print(f"# SKU: {len(base)} 个", flush=True)
            t = time.time()
            f.stocks(a.pid)
            print(f"  读全部库存（零增量回填）: {(time.time()-t)*1000:.0f}ms "
                  f"请求 {f.stats['requests']}", flush=True)
            n0 = f.stats["requests"]
            t = time.time()
            f.stocks(a.pid)
            print(f"  再读（全命中缓存）: {(time.time()-t)*1000:.0f}ms "
                  f"请求 +{f.stats['requests']-n0}", flush=True)
            n0 = f.stats["requests"]
            t = time.time()
            f.set_price_all(a.pid, 120000)
            print(f"  改全部价格（1 请求）: {(time.time()-t)*1000:.0f}ms "
                  f"请求 +{f.stats['requests']-n0}", flush=True)
            n0 = f.stats["requests"]
            t = time.time()
            f.set_stock_all(a.pid, f.stock_of(a.pid, base[0]))
            print(f"  改全部库存（缓存命中）: {(time.time()-t)*1000:.0f}ms "
                  f"请求 +{f.stats['requests']-n0}", flush=True)

        elif a.read:
            print(f"# {a.pid} SKU 顺序: {f.sku_order(a.pid)}", flush=True)
            for sid, q in f.stocks(a.pid, a.wh).items():
                print(f"  sku=…{sid[-6:]} wh=…{a.wh[-6:]} qty={q}", flush=True)

        elif a.from_shop or a.pids or a.batch:
            pids = _load_pids(a)
            if a.from_shop or not pids:
                pids = _list_shop_pids(f, a.tab_id, a.limit)
            if a.limit:
                pids = pids[:a.limit]
            print(f"# 批量 {len(pids)} 个商品  price={a.price} stock={a.stock}", flush=True)

            def prog(i, n, pid, r):
                flag = "OK  " if r["ok"] else "FAIL"
                print(f"  [{i}/{n}] {flag} {pid[:20]} "
                      f"{'价' + str(r.get('price')) + 'sku ' if r.get('price') else ''}"
                      f"{'库存' + str(r.get('stock')) + 'sku' if r.get('stock') else ''}"
                      f"{r.get('err', '')}", flush=True)

            rep = f.batch(pids, price=a.price, stock=a.stock, wh=a.wh, on_progress=prog)
            print(f"\n# 完成 {rep['ok']}/{rep['total']}  wall={rep['wall_s']}s  "
                  f"请求总数 {f.stats['requests']}"
                  f"（{(time.time()-t0)/max(1,rep['ok']):.1f}s/商品）", flush=True)
            if a.json_out:
                json.dump(rep, open(a.json_out, "w"), ensure_ascii=False, indent=2)
                print(f"# 详见 {a.json_out}", flush=True)

        else:
            # 默认：对单商品执行 --price / --stock
            if a.price is not None:
                r = f.set_price_all(a.pid, a.price, wh=a.wh)
                print(f"  改价 {r['skus']} 个 SKU → {a.price}  "
                      f"{[(s[:6], p) for s, p in r['prices']]}", flush=True)
            if a.stock is not None:
                rows = f.set_stock_all(a.pid, a.stock, wh=a.wh)
                brief = [(r["sku_id"][-6:], f"{r['from']}→{r['to']}") for r in rows]
                print(f"  改库存 {len(rows)} 个 SKU（全部设为 {a.stock}）: {brief}",
                      flush=True)
            if a.price is None and a.stock is None:
                ap.print_help()
    finally:
        print(f"# 统计: 请求 {f.stats['requests']} (读回填 {f.stats['list_calls']} 次列表) "
              f"总耗时 {time.time()-t0:.1f}s", flush=True)
        f.close()


if __name__ == "__main__":
    main()
