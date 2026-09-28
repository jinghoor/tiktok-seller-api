#!/usr/bin/env python3
"""TikTok 卖家中心「局部库存/价格编辑」接口客户端。

逆向自 UI 抓包（2026-xx）：
  POST /api/v1/product/stock/alert/set_stock
  {"product_id":"...","sku_id":"...","warehouse_quantity_list":[{"warehouse_id":"...","quantity":N}]}

关键语义（两次对照实验确定）：
  quantity 是 **增量**，不是目标绝对值。界面输入目标值 T，当前值 C，发出 quantity = T - C。
  所以纯 API 直接调用时传 delta，传 0 即「设为当前值」（no-op）。
  quantity 可以为负数（减库存）。

这条路径不触发重新审核（对照：完整 edit 会返回 is_in_audit=true + 提交审核成功）。

用法：
  python3 tt_stock_api.py --list 1790XXXXXXXXXX16
  python3 tt_stock_api.py --set 1790XXXXXXXXXX16 1737XXXXXXXXXX12 7659XXXXXXXXXX08 100
  python3 tt_stock_api.py --delta 1790XXXXXXXXXX16 1737XXXXXXXXXX12 7659XXXXXXXXXX08 -20
  python3 tt_stock_api.py --multi 1790XXXXXXXXXX16 <sku_id> <wh1>:50 <wh2>:30
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request

sys.path.insert(0, ".")

from hub_headless import CDPPage  # noqa: E402

CDP_PORT = CDP_PORT
SELLER_ID = "7494XXXXXXXXXX00"
COMMON = (
    f"locale=zh-CN&language=zh-CN&oec_seller_id={SELLER_ID}&seller_id={SELLER_ID}"
    "&aid=4068&app_name=i18n_ecom_shop"
)

# 页面里的统一 fetch 桥：CSRF 从 cookie 取，credentials include（沿用会话 cookie）
#
# AbortController 是必须的：没有它，一个卡住的请求会让 Runtime.evaluate
# 永远等不到 promise resolve；Python 侧的 socket settimeout 此时不生效
# （底层的 TLS 读阻塞），整个脚本就静默挂死、只能靠 faulthandler 抓栈
# 才看得出来。页面侧超时能保证 evaluate 一定会返回。
BRIDGE = """
window.__tt = window.__tt || (async (method, path, body, timeoutMs) => {
  const m = document.cookie.match(/(?:^|;\\s*)csrf_token=([^;]*)/);
  const h = {'content-type': 'application/json'};
  if (m) h['x-csrftoken'] = decodeURIComponent(m[1]);
  const ac = new AbortController();
  const tid = setTimeout(() => ac.abort(), timeoutMs || 120000);
  try {
    const r = await fetch(path, {
      method, headers: h, credentials: 'include', signal: ac.signal,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const txt = await r.text();
    let j = null;
    try { j = JSON.parse(txt); } catch (e) {
      const line = txt.trim().split('\\n').find(x => x.trim().startsWith('{'));
      if (line) { try { j = JSON.parse(line); } catch (e2) {} }
    }
    return JSON.stringify({status: r.status, json: j, raw: j ? '' : txt.slice(0, 600)});
  } catch (e) {
    return JSON.stringify({status: 0, json: null,
      raw: 'FETCH ' + (e && e.name === 'AbortError' ? 'TIMEOUT' : (e && e.message) || 'ERROR')});
  } finally {
    clearTimeout(tid);
  }
});
"""


class StockAPI:
    """在卖家中心页面上下文里发请求。

    页面选择很重要：如果连到 /product/edit（编辑页）这类重页面，
    Runtime.evaluate 会长时间不返回（页面自己还在跑初始化/轮询），
    表现就是「第一个 API 调用卡住几分钟」。所以必须挑轻量列表页。
    """

    # 优先级从高到低：都是不会阻塞 Runtime.evaluate 的列表型页面
    PREFERRED = ("/product/manage", "/product/stock", "/product/list",
                 "/product/showcase", "/product/optimize")

    def __init__(self, port: int = CDP_PORT, timeout: float = 120.0,
                 url_hint: str | None = None):
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=10))
        seller = [x for x in tabs if x.get("type") == "page"
                  and "seller" in (x.get("url") or "")]

        page = None
        if url_hint:
            page = next((x for x in seller if url_hint in (x.get("url") or "")), None)
            if page is None:
                raise RuntimeError(f"没有匹配 {url_hint!r} 的卖家中心页面；"
                                   f"可用: {[x.get('url', '')[:60] for x in seller]}")
        else:
            for pat in self.PREFERRED:
                page = next((x for x in seller if pat in (x.get("url") or "")), None)
                if page:
                    break
            if page is None and seller:
                # 退一步：任意卖家页面，但把 /product/edit 排到最后
                seller.sort(key=lambda x: "/product/edit" in (x.get("url") or ""))
                page = seller[0]
        if page is None:
            raise RuntimeError(f"端口 {port} 上没有卖家中心页面，"
                               f"标签页: {[(x.get('type'), (x.get('url') or '')[:50]) for x in tabs]}")

        self.page_url = page.get("url", "")
        self.pg = CDPPage(page["webSocketDebuggerUrl"], timeout=timeout)
        self.timeout = timeout
        self.pg.js(BRIDGE)
        self.warmup_seconds: float | None = None
        self.warmup()

    def warmup(self, *, force: bool = False) -> float:
        """预热一次请求。

        页面上如果很久没发请求，连接池是冷的：第一次 fetch 要重建
        SOCKS5 代理连接 + TLS 握手，实测可达 120 秒。之后所有调用 <1s。
        所以第一次调用需要给足超时，并且预热一次把它挡在业务逻辑之外。
        """
        import time as _t
        if self.warmup_seconds is not None and not force:
            return self.warmup_seconds
        t = _t.time()
        try:
            self.pg.js(
                f"window.__tt('GET', {json.dumps('/api/v1/product/tab/count/get?' + COMMON)}, undefined)",
                await_promise=True,
                timeout=max(self.timeout, 300.0),
            )
        except Exception:
            pass
        self.warmup_seconds = _t.time() - t
        return self.warmup_seconds

    def call(self, method: str, path: str, body=None, *, _retry: bool = True,
             timeout_ms: int | None = None):
        full = f"{path}?{COMMON}" if "?" not in path else f"{path}&{COMMON}"
        # 页面侧超时比 CDP 侧短一点：让 fetch 自己 abort 并返回结果，
        # 而不是把 Runtime.evaluate 挂住
        tmo = timeout_ms if timeout_ms is not None else max(5000, int(self.timeout * 1000) - 5000)
        try:
            out = self.pg.js(
                f"window.__tt({json.dumps(method)}, {json.dumps(full)}, "
                f"{json.dumps(body) if body is not None else 'undefined'}, {tmo})",
                await_promise=True,
                timeout=self.timeout,
            )
        except Exception:
            # 重连后页面上下文里的 __tt 桥会丢，重新注入一次再试
            if not _retry:
                raise
            self.pg._reconnect()
            self.pg.js(BRIDGE)
            return self.call(method, path, body, _retry=False, timeout_ms=timeout_ms)
        return json.loads(out)

    def close(self):
        self.pg.close()

    # ---------- 读 ----------

    def sku_list(self, product_id: str | None = None):
        """GET 不到的 SKU×仓库明细走 stock/sku/list（POST，body 是固定骨架）。"""
        body = {
            "search_back_order_list": [],
            "sort_type": [{"field": 4, "type": 1}],
            "page": 1,
            "size": 50,
            "is_need_toggle_status": True,
            "alert_value_filter": [],
            "is_need_target_stock": True,
        }
        res = self.call("POST", "/api/v1/product/stock/sku/list", body)
        j = res.get("json") or {}
        skus = j.get("skus") or (j.get("data") or {}).get("skus") or []
        if product_id:
            skus = [s for s in skus if str(s.get("product_id")) == str(product_id)]
        return skus

    def warehouse_stock(self, product_id: str):
        """返回 {sku_id: {warehouse_id: {name, qty}}}"""
        out: dict[str, dict] = {}
        for s in self.sku_list(product_id):
            wh = {}
            for w in s.get("warehouse_stock_list") or []:
                wh[str(w.get("warehouse_id"))] = {
                    "name": w.get("warehouse_name"),
                    "qty": w.get("in_shop_stock"),
                    "prohibited": w.get("is_stock_edit_prohibited"),
                }
            out[str(s.get("sku_id"))] = wh
        return out

    # ---------- 写 ----------

    def set_stock_delta(self, product_id: str, sku_id: str, warehouse_id: str, delta: int):
        """直接发增量。界面等价于：输入目标值 T → delta = T - 当前。"""
        body = {
            "product_id": str(product_id),
            "sku_id": str(sku_id),
            "warehouse_quantity_list": [
                {"warehouse_id": str(warehouse_id), "quantity": int(delta)}
            ],
        }
        return self.call("POST", "/api/v1/product/stock/alert/set_stock", body)

    def set_stock_multi(self, product_id: str, sku_id: str, deltas: dict[str, int]):
        """一次请求携带多个仓库 —— 验证服务端是否接受多仓批量。"""
        body = {
            "product_id": str(product_id),
            "sku_id": str(sku_id),
            "warehouse_quantity_list": [
                {"warehouse_id": str(w), "quantity": int(q)} for w, q in deltas.items()
            ],
        }
        return self.call("POST", "/api/v1/product/stock/alert/set_stock", body)

    def set_stock_target(self, product_id: str, sku_id: str, warehouse_id: str, target: int,
                         *, verify: bool = True):
        """设为目标绝对值：先读当前 → 算 delta → 发 → 复核。"""
        cur = self.warehouse_stock(product_id).get(str(sku_id), {}).get(str(warehouse_id), {})
        now = cur.get("qty")
        if now is None:
            raise RuntimeError(f"读不到当前库存 sku={sku_id} wh={warehouse_id}")
        delta = int(target) - int(now)
        res = self.set_stock_delta(product_id, sku_id, warehouse_id, delta)
        time.sleep(0.8)
        after = None
        if verify:
            after = self.warehouse_stock(product_id).get(str(sku_id), {}).get(str(warehouse_id), {}).get("qty")
        return {"from": now, "delta": delta, "to": after, "resp": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", metavar="PRODUCT_ID")
    ap.add_argument("--set", nargs=4, metavar=("PID", "SKU", "WH", "TARGET"))
    ap.add_argument("--delta", nargs=4, metavar=("PID", "SKU", "WH", "DELTA"))
    ap.add_argument("--multi", nargs="+", metavar="PID SKU WH:DELTA [WH:DELTA ...]")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    a = ap.parse_args()

    api = StockAPI(a.port)
    try:
        if a.list:
            print(json.dumps(api.warehouse_stock(a.list), ensure_ascii=False, indent=2))
        elif a.set:
            pid, sku, wh, target = a.set
            print(json.dumps(api.set_stock_target(pid, sku, wh, int(target)),
                             ensure_ascii=False, indent=2))
        elif a.delta:
            pid, sku, wh, d = a.delta
            print(json.dumps(api.set_stock_delta(pid, sku, wh, int(d)),
                             ensure_ascii=False, indent=2))
        elif a.multi:
            pid, sku = a.multi[0], a.multi[1]
            deltas = {k: int(v) for k, v in (x.split(":") for x in a.multi[2:])}
            print(json.dumps(api.set_stock_multi(pid, sku, deltas), ensure_ascii=False, indent=2))
        else:
            ap.print_help()
    finally:
        api.close()


if __name__ == "__main__":
    main()
