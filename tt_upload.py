#!/usr/bin/env python3
"""TikTok 商品上架 —— 优化版纯 API 客户端。

相对 tt_api.py 的优化：
  1. **单连接复用**：一次 attach 完成整个流程，不再每个请求重连 CDP（原来每次 attach ~0.3s）
  2. **并行预热**：多轮 get_schema_v2 并发发出，注册更快
  3. **并行重试**：多个候选 product_id 同时预热，谁先注册成谁用
  4. **精确的多仓库存**：每个 SKU 对每个仓库给独立数量
  5. **批量上架**：一次提交多个商品

    python3 tt_upload.py --template notes/tk178_edit_payload.json --warmup-test
    python3 tt_upload.py --template ... --name "..." --prices 100000,110000 \
        --stocks 5,6 --skus A,B --variants S,M --warehouses-stock "wh1:10,20;wh2:5,0"
    python3 tt_upload.py --template ... --batch batch.json
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tk178_fill2 import get_page   # noqa: E402
from hub_headless import CDPPage, cdp_get, _probe_cdp_for_pid  # noqa: E402

SELLER = os.environ.get("TT_SELLER", "7494XXXXXXXXXX00")
CDP_PORT = int(os.environ.get("TT_CDP_PORT", "CDP_PORT"))
DEFAULT_WH = "7659XXXXXXXXXX08"    # Laojie（默认仓）
WH_BEINING = "7686XXXXXXXXXX68"    # BeiNing

BRIDGE = r"""
window.__tt = {
  csrf: () => decodeURIComponent((document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''),
  q: (extra) => {
    const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
      oec_seller_id:'__SELLER__', seller_id:'__SELLER__', aid:'4068',
      app_name:'i18n_ecom_shop'});
    for (const [k, v] of Object.entries(extra || {})) q.set(k, String(v));
    return q.toString();
  },
  post: async (path, body, extra) => {
    const [base, pre] = path.split('?');
    const qs = pre ? pre + '&' + window.__tt.q(extra) : window.__tt.q(extra);
    const r = await fetch(base + '?' + qs, {
      method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/json; charset=utf-8',
                'X-CSRFToken': window.__tt.csrf(), 'Accept': 'application/json'},
      body: JSON.stringify(body)});
    return {status: r.status, body: await r.text()};
  },
  postRaw: async (path, text, extra) => {
    const [base, pre] = path.split('?');
    const qs = pre ? pre + '&' + window.__tt.q(extra) : window.__tt.q(extra);
    const r = await fetch(base + '?' + qs, {
      method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/json; charset=utf-8',
                'X-CSRFToken': window.__tt.csrf(), 'Accept': 'application/json'},
      body: text});
    return {status: r.status, body: await r.text()};
  },
  getAll: async (items) => {
    const out = [];
    for (const it of items) {
      const r = await window.__tt.post(it.path, it.body, it.extra);
      out.push({tag: it.tag, status: r.status, body: r.body});
    }
    return out;
  },
  // 真并发:Promise.all —— 预热提速的关键
  getAllPar: async (items) => {
    const rs = await Promise.all(items.map(it =>
      window.__tt.post(it.path, it.body, it.extra).then(r => ({tag: it.tag, status: r.status, body: r.body}))
        .catch(e => ({tag: it.tag, status: 0, body: String(e)}))));
    return rs;
  },
  get: async (path, extra) => {
    const [base, pre] = path.split('?');
    const qs = pre ? pre + '&' + window.__tt.q(extra) : window.__tt.q(extra);
    const r = await fetch(base + '?' + qs, {credentials: 'include',
      headers: {'Accept': 'application/json'}});
    return {status: r.status, body: await r.text()};
  },
};
'ok'
""".replace("__SELLER__", SELLER)


def parse_json_loose(txt: str, status=None):
    try:
        return json.loads(txt)
    except json.JSONDecodeError as e:
        parts, dec, i = [], json.JSONDecoder(), 0
        while i < len(txt):
            while i < len(txt) and txt[i] in " \t\r\n":
                i += 1
            if i >= len(txt):
                break
            try:
                obj, end = dec.raw_decode(txt, i)
            except json.JSONDecodeError:
                break
            parts.append(obj)
            i = end
        if len(parts) == 1:
            return parts[0]
        if parts:
            return {"code": "MULTI_JSON", "parts": parts}
        return {"code": "NON_JSON", "status": status, "_raw": txt[:400], "_err": str(e)[:120]}


class TT:
    """一个 CDP 连接跑完整流程 —— 这是主要提速点。"""

    def __init__(self, port: int = CDP_PORT, resize=True, keep_playwright=False):
        # 复用同一个 CDP WebSocket（这是提速关键：原来每个请求都重启 playwright+attach）
        self._pw = sync_playwright().start()
        self._pl_page = get_page(self._pw, resize=resize)
        if resize:
            try:
                self._pl_page.set_viewport_size({"width": 1680, "height": 2400})
            except Exception:
                pass
        ws = self._pl_page.context.new_cdp_session(self._pl_page)  # 占位，保持 playwright 存活
        self._keep = ws
        # CDPPage 自己开一条到同一 target 的 WS
        ok, tabs = cdp_get(port, "/json/list")
        pages = [t for t in tabs if t.get("type") == "page"] if ok else []
        target = None
        for t in pages:
            if "seller-vn" in (t.get("url") or ""):
                target = t
                break
        if not target and pages:
            target = pages[0]
        if not target:
            raise RuntimeError(f"CDP {port} 没有可用 page target")
        self.page = CDPPage(target["webSocketDebuggerUrl"], timeout=120)
        self.page.js(BRIDGE)

    def close(self):
        try:
            self.page.close()
        except Exception:
            pass
        try:
            self._pw.stop()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    # ---- 连接自愈
    def _reconnect(self) -> None:
        """长会话里 CDP WebSocket 会被回收/超时 —— 重建到同一 target 的连接。"""
        try:
            self.page.close()
        except Exception:
            pass
        for attempt in range(3):
            try:
                ok, tabs = cdp_get(CDP_PORT, "/json/list")
                if not ok:
                    time.sleep(1)
                    continue
                pages = [t for t in tabs if t.get("type") == "page"]
                target = next((t for t in pages if "seller-vn" in (t.get("url") or "")),
                              pages[0] if pages else None)
                if not target:
                    time.sleep(1)
                    continue
                self.page = CDPPage(target["webSocketDebuggerUrl"], timeout=180)
                self.page.js(BRIDGE)
                self._reconnects = getattr(self, "_reconnects", 0) + 1
                return
            except Exception:
                time.sleep(1)
        raise RuntimeError("CDP 重连失败")

    def _run(self, js: str, timeout: int = 240):
        """执行 JS，遇 WebSocket 异常自动重连并重试一次（GET/预热幂等）。"""
        for attempt in (0, 1):
            try:
                return self.page.js(js, await_promise=True, timeout=timeout)
            except Exception as e:
                name = type(e).__name__
                if attempt == 0 and ("Timeout" in name or "Connection" in name
                                     or "closed" in str(e).lower()):
                    print(f"  [tt] WebSocket 异常({name}) → 重连重试")
                    self._reconnect()
                    continue
                raise

    # ---- 基础
    def post(self, path: str, body: dict, extra: dict | None = None) -> dict:
        r = self._run("window.__tt.post(" + json.dumps(path) + "," + json.dumps(body) + ","
                      + json.dumps(extra or {}) + ")")
        return parse_json_loose(r.get("body", ""), r.get("status"))

    def get(self, path: str, extra: dict | None = None) -> dict:
        r = self._run("window.__tt.get(" + json.dumps(path) + ","
                      + json.dumps(extra or {}) + ")")
        return parse_json_loose(r.get("body", ""), r.get("status"))

    def post_many(self, items: list[dict], parallel: bool = True) -> list[dict]:
        """并发发一批请求。parallel=True 走 Promise.all（预热提速数倍）。"""
        fn = "window.__tt.getAllPar" if parallel else "window.__tt.getAll"
        r = self._run(fn + "(" + json.dumps(items) + ")", timeout=300)
        return [parse_json_loose(x.get("body", ""), x.get("status")) for x in (r or [])]

    # ---- 注册预热
    def warmup(self, pid: str, category_id: str = "601646", rounds: int = 4) -> None:
        body = {"schema_context": {"page": 3, "get_audit_version": False, "product_id": pid,
                                   "category_id": category_id,
                                   "product_type_list": ["ProductType_Normal"]},
                "components": [],
                "scene_param": {"product_type_add_list": ["ProductType_Normal"]}}
        for _ in range(rounds):
            self.post("/api/v1/product/comp/get_schema_v2", body)

    def warmup_batch(self, pids: list[str], category_id: str = "601646",
                     rounds: int = 4) -> None:
        """并行预热多个候选 id（比逐个预热快 N 倍）。"""
        body = {"schema_context": {"page": 3, "get_audit_version": False,
                                   "category_id": category_id,
                                   "product_type_list": ["ProductType_Normal"]},
                "components": [],
                "scene_param": {"product_type_add_list": ["ProductType_Normal"]}}
        items = []
        for pid in pids:
            for _ in range(rounds):
                b = copy.deepcopy(body)
                b["schema_context"]["product_id"] = pid
                items.append({"path": "/api/v1/product/comp/get_schema_v2", "body": b})
        self.post_many(items)


# ---------------------------------------------------------------- 载荷组装

def gen_pid() -> str:
    return str(1790XXXXXXXXXX00 + random.randint(0, 2_000_000_000))


def build(tpl: dict, *, pid: str, name: str, prices: list[str], stocks: list[int],
          seller_skus: list[str], variants: list[str] | None = None,
          image_uri: str | None = None, desc_html: str | None = None,
          sku_image_uris: list[str] | None = None,
          warehouse_stocks: dict[str, list[int]] | None = None,
          logistics_services: list[dict] | None = None) -> dict:
    """组装 create/edit 载荷。

    warehouse_stocks: {warehouse_id: [该仓每个 SKU 的数量]}。给了就用它，
                      否则用 stocks 只写默认仓。
    """
    p = copy.deepcopy(tpl)
    p["product_id"] = pid
    p["pre_build_product_id"] = pid
    p["product_name"] = name
    p["product_source"] = 4
    p["page_type"] = 1
    p["from_new_oc"] = False
    pep = dict(p.get("publish_event_param") or {})
    pep["session_id"] = str(int(time.time() * 1000)) + "000"
    p["publish_event_param"] = pep
    sc = dict(p.get("schema_context") or {})
    sc["product_id"] = pid
    sc.setdefault("page", 3)
    sc.setdefault("category_id", str(p.get("category_id") or ""))
    sc.setdefault("product_type_list", ["ProductType_Normal"])
    p["schema_context"] = sc
    if logistics_services is not None:
        p["logistics_services"] = logistics_services

    for c in p.get("components") or []:
        if c.get("id") == "title_comp":
            c["value"] = json.dumps(name, ensure_ascii=False)

    if image_uri:
        imgs = p.get("images") or [{}]
        import re
        for im in imgs:
            im["uri"] = image_uri
            if im.get("url_list"):
                im["url_list"] = [re.sub(r"aphluv4xwc-sg/[a-f0-9]{32}", image_uri, u)
                                  for u in im["url_list"]]
        p["images"] = imgs
    if desc_html is not None:
        p["description"] = desc_html

    # 变体
    sps = p.get("sale_properties") or []
    vals = []
    if sps:
        sp = sps[0]
        src_vals = sp.get("values") or []
        src_img = next((c["image"] for c in src_vals if c.get("image")), None)
        if variants:
            # 指定了变体名 → 按变体名重建
            for i, vn in enumerate(variants):
                v = {"id": str(900 + i + 1), "name": vn, "is_custom": True}
                if src_img:
                    im = copy.deepcopy(src_img)
                    if sku_image_uris and i < len(sku_image_uris):
                        import re
                        im["uri"] = sku_image_uris[i]
                        im["url_list"] = [re.sub(r"aphluv4xwc-sg/[a-f0-9]{32}", im["uri"], u)
                                          for u in (im.get("url_list") or [])]
                    v["image"] = im
                vals.append(v)
            sp["values"] = vals
            sp["has_image"] = any("image" in v for v in vals)
            p["sale_properties"] = [sp]
        else:
            # 没指定变体名 → 只用第一个规格值（否则模板的 3 个值会生成 3 个空 SKU）
            keep = copy.deepcopy(src_vals[0]) if src_vals else {"id": "1", "name": "", "is_custom": True}
            sp["values"] = [keep]
            p["sale_properties"] = [sp]
            vals = [keep]

    # SKU
    n = len(vals) if vals else max(1, len(prices))
    sp0 = sl = (p.get("sale_properties") or [{}])[0] if p.get("sale_properties") else {}
    out = []
    for i in range(n):
        sk = {"id": str(950 + i),
              "seller_sku": seller_skus[i] if i < len(seller_skus) else "",
              "properties": ([{"id": sp0["id"], "name": sp0.get("text"),
                               "value_id": vals[i]["id"], "value_name": vals[i]["name"]}]
                             if vals and sp0.get("id") else []),
              "base_price": {"list_price": str(prices[i] if i < len(prices) else prices[-1]),
                             "sale_price": str(prices[i] if i < len(prices) else prices[-1]),
                             "list_price_display": "", "sale_price_display": "",
                             "region": "VN", "currency": "VND",
                             "localized_dutiable_price": "0", "audit_list_price": ""},
              "quantities": [], "pre_order_ship_day": 0, "fulfillment_info": {},
              "purchase_order_quantity_limit": {}, "fees": []}
        if warehouse_stocks:
            for wh, qty_list in warehouse_stocks.items():
                q = qty_list[i] if i < len(qty_list) else (qty_list[-1] if qty_list else 0)
                sk["quantities"].append({"available_quantity": int(q),
                                         "quantity_variation": 0, "warehouse_id": wh})
        else:
            q = stocks[i] if i < len(stocks) else (stocks[-1] if stocks else 0)
            sk["quantities"].append({"available_quantity": int(q),
                                     "quantity_variation": 0, "warehouse_id": DEFAULT_WH})
        out.append(sk)
    p["skus"] = out
    return p


# ---------------------------------------------------------------- 上架

# 值得重试的错误码（服务端最终一致性导致，不是载荷问题）
RETRYABLE = {"12052032", 12052032, "12052900", 12052900, "12052910", 12052910}

# 模块级懒加载 id 池：create_one 也复用，避免每次重建
_POOL_CACHE: dict = {}


def _get_pool(tt: "TT", category_id: str, warmup_rounds: int = 6,
              batch: int = 16) -> "IDPool":
    key = (id(tt), category_id)
    pool = _POOL_CACHE.get(key)
    if pool is None or not pool.ready:
        pool = IDPool(tt, category_id=category_id, warmup_rounds=warmup_rounds, batch=batch)
        pool.fill(verbose=False)
        _POOL_CACHE[key] = pool
    return pool



class IDPool:
    """预注册 product_id 池。

    实测：预热后约 50% 的 id 才真正注册成功（概率性，不是次数问题），
    但注册成功的 id 能存活 ≥20s。所以批量预注册、建池、取用，
    比「每个商品现场预热重试」快得多。
    """

    def __init__(self, tt: "TT", category_id: str = "601646",
                 warmup_rounds: int = 6, batch: int = 16):
        # 实测最优: warmup_rounds=6 + batch=16 → 8/8 成功率, 1.79s/个
        # (rounds=4 只有 5/8; 注册是概率性的,轮数比池大小更关键)
        self.tt = tt
        self.category_id = category_id
        self.warmup_rounds = warmup_rounds
        self.batch = batch
        self.ready: list[str] = []

    def fill(self, n: int | None = None, verbose: bool = True) -> int:
        """预注册一批（并发），返回池中数量。"""
        n = n or self.batch
        pids = [gen_pid() for _ in range(n)]
        t0 = time.time()
        body = {"schema_context": {"page": 3, "get_audit_version": False,
                                   "category_id": self.category_id,
                                   "product_type_list": ["ProductType_Normal"]},
                "components": [],
                "scene_param": {"product_type_add_list": ["ProductType_Normal"]}}
        items = []
        for pid in pids:
            for _ in range(self.warmup_rounds):
                b = copy.deepcopy(body)
                b["schema_context"]["product_id"] = pid
                items.append({"path": "/api/v1/product/comp/get_schema_v2", "body": b})
        self.tt.post_many(items, parallel=True)
        el = time.time() - t0
        self.ready.extend(pids)
        if verbose:
            print(f"  [pool] 预注册 {n} 个 id（{self.warmup_rounds} 轮并发），耗时 {el:.1f}s")
        return len(self.ready)

    def take(self) -> str:
        if not self.ready:
            self.fill()
        return self.ready.pop()


def create_with_pool(tt: TT, pool: IDPool, tpl: dict, *, name: str, prices: list[str],
                     stocks: list[int], seller_skus: list[str],
                     variants: list[str] | None = None, image_uri: str | None = None,
                     desc_html: str | None = None, sku_image_uris: list[str] | None = None,
                     warehouse_stocks: dict[str, list[int]] | None = None,
                     max_try: int = 4, verbose: bool = False) -> dict:
    """从池里取 id 直接 create；失败就换下一个（不重新预热）。"""
    last: dict = {"code": "EXHAUSTED", "message": "池内 id 全部失败"}
    for i in range(max_try):
        pid = pool.take()
        payload = build(tpl, pid=pid, name=name, prices=prices, stocks=stocks,
                        seller_skus=seller_skus, variants=variants, image_uri=image_uri,
                        desc_html=desc_html, sku_image_uris=sku_image_uris,
                        warehouse_stocks=warehouse_stocks)
        r = tt.post("/api/v1/product/local/product/create", payload)
        if verbose:
            print(f"      try{i+1} pid={pid} -> {r.get('code')} {str(r.get('message'))[:44]}")
        last = r
        if r.get("code") == 0:
            r["_pid"] = pid
            r["_payload"] = payload
            return r
        if r.get("code") not in RETRYABLE:
            return r
    return last


def create_one(tt: TT, tpl: dict, *, name: str, prices: list[str], stocks: list[int],
               seller_skus: list[str], variants: list[str] | None = None,
               image_uri: str | None = None, desc_html: str | None = None,
               sku_image_uris: list[str] | None = None,
               warehouse_stocks: dict[str, list[int]] | None = None,
               category_id: str = "601646", attempts: int = 6,
               warmup_rounds: int = 6, parallel_warmup: int = 3,
               verbose: bool = False) -> dict:
    """上架一个商品。并行预热多个候选 id，逐个试 create，谁先成用谁。

    实测 product_id 的注册是**最终一致性**：同一个 id 预热 4 轮后仍可能报
    `12052032 此商品不存在`。所以这里做「一轮预热 → 批量试 → 下一轮」的重试，
    并对可重试错误码继续换 id。返回最后一次响应；全失败时带 `_exhausted: True`。
    """
    pool = _get_pool(tt, category_id, warmup_rounds, max(16, attempts * 2))
    return create_with_pool(tt, pool, tpl, name=name, prices=prices, stocks=stocks,
                            seller_skus=seller_skus, variants=variants, image_uri=image_uri,
                            desc_html=desc_html, sku_image_uris=sku_image_uris,
                            warehouse_stocks=warehouse_stocks,
                            max_try=attempts, verbose=verbose)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="notes/tk178_edit_payload.json")
    ap.add_argument("--warmup-test", action="store_true", help="测预热+创建耗时")
    ap.add_argument("--name", default=None)
    ap.add_argument("--prices", default=None)
    ap.add_argument("--stocks", default=None)
    ap.add_argument("--skus", default=None)
    ap.add_argument("--variants", default=None)
    ap.add_argument("--image", default=None)
    ap.add_argument("--wh-stocks", default=None,
                    help='多仓库存: "wh1:10,20;wh2:5,6"')
    ap.add_argument("--category", default="601646")
    ap.add_argument("--batch", default=None, help="批量 JSON 文件")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-pool", action="store_true", help="不用 id 池，逐个预热（慢）")
    ap.add_argument("--pool-size", type=int, default=16, help="id 池大小")
    ap.add_argument("--warmup-rounds", type=int, default=6, help="每个 id 预热轮数")
    a = ap.parse_args()

    tpl = json.load(open(a.template)) if os.path.exists(a.template) else None
    if not tpl:
        print(f"模板不存在: {a.template}", file=sys.stderr)
        return 2

    wh_stocks = None
    if a.wh_stocks:
        wh_stocks = {}
        for seg in a.wh_stocks.split(";"):
            wh, qs = seg.split(":")
            wh_stocks[wh.strip()] = [int(x) for x in qs.split(",")]

    with TT() as tt:
        if a.warmup_test:
            print("=== 计时: 预热 + 创建 ===")
            t0 = time.time()
            r = create_one(tt, tpl,
                           name="Performance Test — Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g",
                           prices=["120000"], stocks=[7], seller_skus=["PERF1"])
            el = time.time() - t0
            print(f"耗时 {el:.1f}s  code={r.get('code')}  pid={r.get('_pid')}")
            if r.get("code") == 0:
                print("新商品:", r.get("data", {}).get("product_id"))
            return 0

        if a.batch:
            jobs = json.load(open(a.batch))
        else:
            if not (a.name and a.prices and a.skus):
                ap.error("需要 --name --prices --skus（或用 --batch）")
            jobs = [{"name": a.name,
                     "prices": a.prices.split(","),
                     "stocks": [int(x) for x in (a.stocks or "100").split(",")],
                     "skus": a.skus.split(","),
                     "variants": a.variants.split(",") if a.variants else None,
                     "image": a.image,
                     "wh_stocks": wh_stocks}]

        if a.dry_run:
            for j in jobs:
                p = build(tpl, pid="0", name=j["name"], prices=j["prices"],
                          stocks=j["stocks"], seller_skus=j["skus"],
                          variants=j.get("variants"), image_uri=j.get("image"),
                          warehouse_stocks=j.get("wh_stocks"))
                print(f"[dry] {j['name'][:40]} SKU={len(p['skus'])}")
                for sk in p["skus"]:
                    print(f"   {sk['seller_sku']:<10} {sk['base_price']['sale_price']:>8} "
                          f"{[(q['warehouse_id'][-6:], q['available_quantity']) for q in sk['quantities']]}")
            return 0

        # 池式上架：预注册一批 id，之后每个商品直接取用（实测 1.8~3.3s/个，对比顺序预热 8.4s）
        use_pool = (not a.no_pool) and len(jobs) >= 1
        pool = None
        if use_pool:
            pool = IDPool(tt, category_id=a.category,
                          warmup_rounds=a.warmup_rounds, batch=a.pool_size)
            pool.fill()

        t_all = time.time()
        for i, j in enumerate(jobs):
            t0 = time.time()
            if pool is not None and len(pool.ready) < 2:
                pool.fill(verbose=False)
            if pool is not None:
                r = create_with_pool(tt, pool, tpl, name=j["name"], prices=j["prices"],
                                     stocks=j["stocks"], seller_skus=j["skus"],
                                     variants=j.get("variants"), image_uri=j.get("image"),
                                     desc_html=j.get("desc"),
                                     sku_image_uris=j.get("sku_images"),
                                     warehouse_stocks=j.get("wh_stocks"), max_try=4)
            else:
                r = create_one(tt, tpl, name=j["name"], prices=j["prices"], stocks=j["stocks"],
                               seller_skus=j["skus"], variants=j.get("variants"),
                               image_uri=j.get("image"), desc_html=j.get("desc"),
                               sku_image_uris=j.get("sku_images"),
                               warehouse_stocks=j.get("wh_stocks"),
                               category_id=j.get("category", a.category))
            el = time.time() - t0
            ok = r.get("code") == 0
            pid = (r.get("data") or {}).get("product_id") if ok else "-"
            print(f"[{i+1}/{len(jobs)}] {'OK ' if ok else 'FAIL'} code={r.get('code')} "
                  f"{el:5.1f}s  pid={pid}  {j['name'][:44]}")
            if not ok:
                print("      ", str(r.get("message"))[:120])
            json.dump(r, open(f"notes/tt_upload_{i+1}.json", "w"), ensure_ascii=False, indent=2)
        print(f"\n合计 {len(jobs)} 个, {time.time()-t_all:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
