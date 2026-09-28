#!/usr/bin/env python3
"""TikTok 卖家中心 API 直连客户端 —— 不经过页面 JS 主线程。

为什么不用页面里 fetch：
  卖家中心页面自己跑大量轮询脚本，会长时间占住 JS 主线程。
  此时 CDP 的 Runtime.evaluate 永远等不到结果（底层 TLS recv 无限阻塞，
  websocket 的 settimeout 也不生效），整个脚本静默挂死。
  实测：同一操作在页面里走 fetch 平均 1–2s，但会随机挂 140s+ 不返回。

这个客户端的做法：
  1. 一次性从浏览器 CDP 里取 cookie（含 sessionid / csrf_token）
  2. 之后全部用 requests 直连，带 Cookie + x-csrftoken 头
  3. 完全脱离页面主线程，性能稳定，且不需要页面处于任何特定路由

前提：浏览器（Hub Studio 环境）已登录卖家中心，且 CDP 端口可访问。

用法：
  python3 tt_http_client.py --check                      # 验证 cookie 与连通性
  python3 tt_http_client.py --read <PID>                 # 读 SKU × 仓库状态
  python3 tt_http_client.py --price <PID> <SKU> 150000
  python3 tt_http_client.py --price-all <PID> 150000
  python3 tt_http_client.py --stock <PID> <SKU> <WH> 100
  python3 tt_http_client.py --both <PID> <SKU> <WH> --set-price 150000 --set-stock 100
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import gzip
import http.client
import socket
import zlib
import ssl
import urllib.request

# 本机代理（SOCKS5/HTTP）会做 TLS 中间人，证书链是自签的。
# 这是自己的 lab 出口链路，跳过校验；生产环境应换成固定 CA。
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

sys.path.insert(0, ".")

HOST = "seller-vn.tiktok.com"
BASE = f"https://{HOST}"
SELLER_ID = "7494XXXXXXXXXX00"
COMMON = (f"locale=zh-CN&language=zh-CN&oec_seller_id={SELLER_ID}&seller_id={SELLER_ID}"
          "&aid=4068&app_name=i18n_ecom_shop")

# 代理：优先环境变量，其次 urllib 的系统设置（macOS 网络偏好里的 HTTP 代理）
def _detect_proxy() -> str | None:
    for k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY"):
        v = __import__("os").environ.get(k)
        if v:
            return v if "://" in v else f"http://{v}"
    try:
        p = urllib.request.getproxies()
        return p.get("https") or p.get("http")
    except Exception:
        return None


PROXY = _detect_proxy()

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")


# ─────────────────── cookie 获取（唯一需要 CDP 的部分） ───────────────────

def cookies_via_cdp(port: int = CDP_PORT) -> dict:
    """从浏览器取 seller-vn.tiktok.com 的 cookie。只用一次 CDP，之后不再碰页面。"""
    import websocket  # websocket-client

    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=10))
    page = next((x for x in tabs if x.get("type") == "page" and "seller" in (x.get("url") or "")),
                None)
    if page is None:
        page = next((x for x in tabs if x.get("type") == "page"), None)
    if page is None:
        raise RuntimeError(f"端口 {port} 上没有可用的页面")

    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30,
                                     suppress_origin=True, max_size=None)
    jar: list = []
    try:
        # getAllCookies 覆盖 httpOnly（csrf_token 通常是 httpOnly）
        ws.send(json.dumps({"id": 1, "method": "Network.getAllCookies"}))
        ws.send(json.dumps({"id": 2, "method": "Network.getCookies",
                            "params": {"urls": [BASE]}}))
        got = set()
        while len(got) < 2:
            msg = json.loads(ws.recv())
            mid = msg.get("id")
            if mid in (1, 2):
                got.add(mid)
                jar.extend((msg.get("result") or {}).get("cookies") or [])
    finally:
        try:
            ws.close()
        except Exception:
            pass

    out: dict = {}
    for c in jar:
        # 只保留 tiktok/oec 系域的 cookie。
        # 带上别的域（microsoft/google 等）会让服务端判定会话异常 -> POST 403；
        # 但 csrftoken 必须留下来（卖家中心用它做 CSRF 校验）。
        d = c.get("domain", "")
        if not any(k in d for k in ("tiktok", "oec", "byteintl", "ibyteimg")):
            continue
        out.setdefault(c["name"], c["value"])
    # TikTok 卖家中心用 SELLER_TOKEN / UNIFIED_SELLER_TOKEN，不是 sessionid
    if not any(k in out for k in ("SELLER_TOKEN", "UNIFIED_SELLER_TOKEN", "sessionid",
                                  "sessionid_ss")):
        raise RuntimeError(f"cookie 里没有卖家凭证，可能浏览器未登录。拿到: {list(out)[:15]}")
    return out


# ─────────────────── HTTP 客户端 ───────────────────


# ─────────────────── 每接口自适应限流 ───────────────────
# TikTok 对写接口有**按接口独立**的短时熔断：
#   实测 gap=0.5s 下 /sku/price/stocks/update 连续 17 次后开始返回 code=10000，
#   set_stock 约 34 次，冷却约 60s 后自愈。
# 触发限流时服务端返回 HTTP 200 + {"code":10000,"message":""}，
# 所以必须在**业务码**层面识别，不能只看 HTTP 状态。
#
# 组合策略：
#   1. 主动节流 —— 滑动窗口内计数，接近容量就先等
#   2. 被动熔断 —— 一旦收到 10000，暂停该接口一段时间再恢复
RATE_LIMIT_CODES = {10000}


def is_rate_limited_json(j) -> bool:
    """判断响应体是否是限流（而非业务错误）。

    code=10000 也出现在「商品不可编辑」等场景，但那种情况下
    重试几次仍然失败，退避成本可接受；这里偏向保守：一律先退避。
    """
    return isinstance(j, dict) and j.get("code") in RATE_LIMIT_CODES


class RateGuard:
    """按端点独立计数的滑动窗口 + 熔断。

    实测（gap=0.5s 连续打）：
      · /sku/price/stocks/update 第 18 次开始 code=10000
      · /stock/alert/set_stock   第 35 次开始失败
      · 冷却约 60–70s 后自愈
    容量默认 8（30s 窗口）—— 低于实测阈值，让主动等待先于被动熔断发生。
    """

    def __init__(self, capacity: int = 8, window: float = 30.0,
                 cooldown: float = 70.0):
        self.capacity = capacity
        self.window = window
        self.cooldown = cooldown
        self.hits: dict[str, list[float]] = {}
        self.until: dict[str, float] = {}
        self.trips = 0

    def wait(self, key: str) -> float:
        """调用前等待。返回实际等待秒数。"""
        slept = 0.0
        now = time.time()
        # 熔断中先等到期
        if now < self.until.get(key, 0):
            d = self.until[key] - now
            time.sleep(d)
            slept += d
            now = time.time()
        ts = [t for t in self.hits.get(key, []) if now - t < self.window]
        if len(ts) >= self.capacity:
            d = self.window - (now - ts[0]) + 0.2
            if d > 0:
                time.sleep(d)
                slept += d
        return slept

    def record(self, key: str) -> None:
        ts = self.hits.setdefault(key, [])
        ts.append(time.time())
        if len(ts) > 200:
            del ts[:-100]

    def trip(self, key: str, cooldown: float | None = None) -> float:
        cd = cooldown if cooldown is not None else self.cooldown
        self.until[key] = time.time() + cd
        self.trips += 1
        self.hits[key] = []
        return cd

    def status(self) -> dict:
        return {"trips": self.trips,
                "cooldowns": {k: round(max(0.0, v - time.time()), 1)
                              for k, v in self.until.items() if v > time.time()}}


class TT:
    def __init__(self, port: int = CDP_PORT, timeout: float = 30.0,
             cookies: dict | None = None, min_gap: float = 0.6,
             guard: RateGuard | None = None, rate_retries: int = 3):
        self.cookies = cookies if cookies is not None else cookies_via_cdp(port)
        from urllib.parse import unquote
        # 卖家中心用 csrftoken（不是 csrf_token）；passport_csrf_token 是另一套
        csrf = ""
        for k in ("csrftoken", "csrf_token", "passport_csrf_token"):
            if self.cookies.get(k):
                csrf = self.cookies[k]
                break
        self.csrf = unquote(csrf)
        if not self.csrf:
            raise RuntimeError("没拿到 csrftoken，POST 会被 403。"
                               f"cookie 名: {[k for k in self.cookies if 'csrf' in k.lower()]}")
        self.timeout = timeout
        self.calls = 0
        self._c = None
        self._min_gap = min_gap
        self._last_call = 0.0
        self._penalty = 0.0
        self.guard = guard if guard is not None else RateGuard()
        self.rate_retries = rate_retries

    def _headers(self, extra: dict | None = None) -> dict:
        h = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json",
            "user-agent": UA,
            "x-csrftoken": self.csrf,
            "referer": f"{BASE}/product/manage",
            "cookie": "; ".join(f"{k}={v}" for k, v in self.cookies.items()),
        }
        if extra:
            h.update(extra)
        return h

    def _conn(self):
        """复用一个 keep-alive 连接：省掉每次 TLS 握手（~0.5-1s/次）。

        注意：urllib 会自动读系统代理（本机 http://127.0.0.1:7890），
        而 http.client 不会 —— 直连 seller-vn.tiktok.com 会超时。
        所以这里手工走 HTTP CONNECT 隧道，既保留长连接又走代理。
        """
        if self._c is not None:
            return self._c
        proxy = PROXY
        if proxy:
            host, _, port = proxy.replace("http://", "").partition(":")
            raw = socket.create_connection((host, int(port or 80)), timeout=self.timeout)
            raw.sendall(("CONNECT %s:443 HTTP/1.1\r\n"
                         "Host: %s:443\r\n"
                         "Proxy-Connection: keep-alive\r\n\r\n" % (HOST, HOST)).encode())
            buf = b""
            while b"\r\n\r\n" not in buf:
                chunk = raw.recv(4096)
                if not chunk:
                    raise RuntimeError("代理 CONNECT 隧道被关闭")
                buf += chunk
            if b" 200 " not in buf.split(b"\r\n")[0]:
                raise RuntimeError(f"代理 CONNECT 失败: {buf.split(chr(13).encode())[0]!r}")
            self._c = http.client.HTTPSConnection(
                HOST, timeout=self.timeout, context=_SSL_CTX)
            self._c.sock = _SSL_CTX.wrap_socket(raw, server_hostname=HOST)
        else:
            self._c = http.client.HTTPSConnection(HOST, timeout=self.timeout,
                                                  context=_SSL_CTX)
        return self._c

    def _drop_conn(self):
        try:
            if self._c:
                self._c.close()
        except Exception:
            pass
        self._c = None

    def call(self, method: str, path: str, body=None, *, retries: int = 5,
             timeout: float | None = None) -> dict:
        url = f"{BASE}{path}"
        url = f"{url}?{COMMON}" if "?" not in url else f"{url}&{COMMON}"
        data = json.dumps(body) if body is not None else None
        last = None
        rl_key = f"{method} {url.split('?')[0]}"
        self._throttle()
        rl_hits = 0
        for attempt in range(retries):
            try:
                c = self._conn()
                c.request(method, url, body=data, headers=self._headers())
                resp = c.getresponse()
                raw_bytes = resp.read()
                # urllib 会自动解压，http.client 不会 —— 忘了这一步
                # 会把 gzip 二进制当文本解析，JSON 全变成 None
                enc = (resp.getheader("Content-Encoding") or "").lower()
                if "gzip" in enc:
                    try:
                        raw_bytes = gzip.decompress(raw_bytes)
                    except Exception:
                        pass
                elif "deflate" in enc:
                    try:
                        raw_bytes = zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
                    except Exception:
                        pass
                txt = raw_bytes.decode("utf-8", "replace")
                self.calls += 1
                # 服务端可能回 Connection: close —— 那条连接已经废了，
                # 复用它会让下一次请求一直挂到超时
                if (resp.getheader("Connection", "") or "").lower() == "close" \
                        or resp.version == 10:
                    self._drop_conn()
                if resp.status == 403:
                    # 403 有两种：csrf/会话失效，或请求速率风控。
                    # 后者会自愈，所以退避重试；重试还失败才当会话问题。
                    last = f"HTTP 403: {txt[:120]}"
                    self._backoff()          # 风控时把节奏放慢
                    continue
                if resp.status == 401:
                    last = f"HTTP 401: {txt[:120]}"
                    break
                self._penalty = max(0.0, self._penalty * 0.5 - 0.1)
                self.guard.record(rl_key)
                try:
                    _j = json.loads(txt)
                except json.JSONDecodeError:
                    _j = None
                if is_rate_limited_json(_j) and rl_hits < self.rate_retries:
                    # 业务码层面的限流：退避后重试同一个请求
                    rl_hits += 1
                    cd = self.guard.trip(rl_key)
                    last = f"RATE_LIMIT code={_j.get('code')} 冷却 {cd:.0f}s 后重试"
                    self._drop_conn()
                    time.sleep(cd)
                    continue
                self.guard.wait(rl_key)
                try:
                    return {"status": resp.status, "json": json.loads(txt), "raw": ""}
                except json.JSONDecodeError:
                    line = next((l for l in txt.split("\n") if l.strip().startswith("{")), None)
                    if line:
                        try:
                            return {"status": resp.status, "json": json.loads(line), "raw": ""}
                        except json.JSONDecodeError:
                            pass
                    return {"status": resp.status, "json": None, "raw": txt[:600]}
            except Exception as e:
                last = f"{type(e).__name__}: {e}"
                self._drop_conn()          # 连接坏了就重建
            time.sleep(0.6 * (attempt + 1))
        raise RuntimeError(f"{method} {path.split('?')[0]} 失败: {last}")

    # ── 自适应限流 ──
    # TikTok 对写接口有速率限制，打太快会回 403（不是 csrf 问题）。
    # 命中就指数退避并把后续请求的间隔拉长，避免整批任务全废。
    def _backoff(self):
        self._penalty = min(self._penalty * 2 or 1.0, 30.0)
        time.sleep(self._penalty)

    def _throttle(self):
        gap = self._min_gap
        if self._penalty > 0:
            gap = max(gap, self._penalty)
        now = time.time()
        delta = now - self._last_call
        if delta < gap:
            time.sleep(gap - delta)
        self._last_call = time.time()

    def close(self):
        self._drop_conn()

    def get(self, path: str, **kw) -> dict:
        return self.call("GET", path, **kw)

    def post(self, path: str, body=None, **kw) -> dict:
        return self.call("POST", path, body, **kw)


# ─────────────────── 业务层 ───────────────────

SET_STOCK = "/api/v1/product/stock/alert/set_stock"
PRICE_STOCKS = "/api/v1/product/sku/price/stocks/update"


def find_list_item(tt: TT, pid: str, *, tab_ids=(1, 2), page_size: int = 50) -> dict:
    """从商品列表接口拿商品对象。

    为什么不用 /product/local/product/get：直连调它返回 code=10000，
    页内 fetch 同样拿不到（该接口对部分商品状态不可用）。
    列表接口稳定可用，且带 skus / sale_price_ranges / total_available_stock。
    """
    for tab in tab_ids:
        page = 1
        while page <= 10:
            r = tt.get(f"/api/v1/product/web/local/products/list"
                       f"?tab_id={tab}&page_size={page_size}&page={page}")
            d = (r.get("json") or {}).get("data") or {}
            prods = d.get("products") or []
            hit = next((x for x in prods if str(x.get("product_id")) == str(pid)), None)
            if hit:
                return hit
            if not d.get("has_more") or not prods:
                break
            page += 1
    return {}


def probe_stock(tt: TT, pid: str, sku_id: str, wh_id: str) -> int | None:
    """零增量探测某 SKU 在某仓的当前库存。

    set_stock 的 quantity 是增量，传 0 是 no-op，但响应会回传
    current_quantity_list（更新后的绝对值）。所以这是一次「免费读」，
    不需要 product/get。这是绕过 product/get 不可用的关键技巧。
    """
    body = {"product_id": str(pid), "sku_id": str(sku_id),
            "warehouse_quantity_list": [{"warehouse_id": str(wh_id), "quantity": 0}]}
    r = tt.post(SET_STOCK, body)
    j = r.get("json") or {}
    cq = j.get("current_quantity_list") or []
    for x in cq:
        if str(x.get("warehouse_id")) == str(wh_id):
            return x.get("quantity")
    return None


def probe_stock_delta(tt: TT, pid: str, sku_id: str, wh_id: str, delta: int) -> int | None:
    """直接发指定增量，返回更新后的绝对值。delta=0 即纯 no-op 读。"""
    body = {"product_id": str(pid), "sku_id": str(sku_id),
            "warehouse_quantity_list": [{"warehouse_id": str(wh_id), "quantity": int(delta)}]}
    r = tt.post(SET_STOCK, body)
    j = r.get("json") or {}
    if j.get("code") != 0:
        raise RuntimeError(f"set_stock 失败: code={j.get('code')} {j.get('message')}")
    for x in (j.get("current_quantity_list") or []):
        if str(x.get("warehouse_id")) == str(wh_id):
            return x.get("quantity")
    return None


def probe_stock_all(tt: TT, pid: str, wh_id: str) -> dict[str, int]:
    """一次探测该商品全部 SKU 在指定仓的库存。"""
    item = find_list_item(tt, pid)
    out: dict[str, int] = {}
    for s in item.get("skus") or []:
        q = probe_stock(tt, pid, s["id"], wh_id)
        if q is not None:
            out[str(s["id"])] = q
    return out


def sku_list(tt: TT, pid: str) -> list[dict]:
    """SKU 基本信息（id / seller_sku），来自列表接口。"""
    item = find_list_item(tt, pid)
    return [{"sku_id": s.get("id"), "seller_sku": s.get("seller_sku")}
            for s in (item.get("skus") or [])]


def sku_state(tt: TT, pid: str, wh_id: str = "7659XXXXXXXXXX08") -> list[dict]:
    """SKU × 指定仓库状态。库存用零增量探测，价格从列表的价格带取。"""
    item = find_list_item(tt, pid)
    out = []
    for s in item.get("skus") or []:
        q = probe_stock(tt, pid, s["id"], wh_id)
        out.append({"sku_id": s.get("id"), "seller_sku": s.get("seller_sku"),
                    "price": None,          # 单 SKU 价格列表接口不给，用 --set-price 直接写
                    "warehouse_id": wh_id, "qty": q})
    return out


def audit_state(tt: TT, pid: str) -> dict:
    p = find_list_item(tt, pid)
    sp = (p.get("sale_platform_products") or [{}])[0]
    return {"product_id": p.get("product_id"),
            "product_status": p.get("product_status"),
            "audit_status": p.get("audit_status"),
            "product_status_view": sp.get("product_status_view") or p.get("product_status_view"),
            "suspend_reason": sp.get("suspend_reason") or p.get("suspend_reason")}


def set_price(tt: TT, pid: str, sku_id: str, target, *, tab_id: int = 2):
    body = {"product_id": str(pid),
            "price_stocks_edit_data": [{"sku_id": str(sku_id), "sale_price": str(target)}],
            "tab_id": tab_id}
    return tt.post(PRICE_STOCKS, body)


def set_price_all(tt: TT, pid: str, target, *, tab_id: int = 2):
    seen, items = set(), []
    for r in sku_list(tt, pid):
        if r["sku_id"] in seen:
            continue
        seen.add(r["sku_id"])
        items.append({"sku_id": str(r["sku_id"]), "sale_price": str(target)})
    if not items:
        raise RuntimeError("没有可改的 SKU")
    return tt.post(PRICE_STOCKS, {"product_id": str(pid),
                                  "price_stocks_edit_data": items, "tab_id": tab_id})


def set_stock(tt: TT, pid: str, sku_id: str, wh_id: str, target: int):
    now = probe_stock(tt, pid, sku_id, wh_id)
    now = int(now or 0)
    delta = int(target) - now
    body = {"product_id": str(pid), "sku_id": str(sku_id),
            "warehouse_quantity_list": [{"warehouse_id": str(wh_id), "quantity": delta}]}
    return {"from": now, "delta": delta, "target": int(target),
            "resp": tt.post(SET_STOCK, body)}


def set_price_and_stock(tt: TT, pid: str, sku_id: str, wh_id: str, *,
                        price=None, stock: int | None = None, tab_id: int = 2):
    item: dict = {"sku_id": str(sku_id)}
    if price is not None:
        item["sale_price"] = str(price)
    if stock is not None:
        now = int(probe_stock(tt, pid, sku_id, wh_id) or 0)
        item["warehouse_id"] = str(wh_id)
        item["quantity_variation"] = int(stock) - now
    return tt.post(PRICE_STOCKS, {"product_id": str(pid),
                                  "price_stocks_edit_data": [item], "tab_id": tab_id})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--read", metavar="PID")
    ap.add_argument("--audit-check", metavar="PID")
    ap.add_argument("--price", nargs=3, metavar=("PID", "SKU", "单价"))
    ap.add_argument("--price-all", nargs=2, metavar=("PID", "单价"))
    ap.add_argument("--stock", nargs=4, metavar=("PID", "SKU", "WH", "库存"))
    ap.add_argument("--both", nargs=3, metavar=("PID", "SKU", "WH"))
    ap.add_argument("--set-price")
    ap.add_argument("--set-stock", type=int)
    a = ap.parse_args()

    t0 = time.time()
    tt = TT(port=a.port)
    print(f"# cookie 就绪（{len(tt.cookies)} 项，csrf={'有' if tt.csrf else '无'}）"
          f" {time.time()-t0:.2f}s", flush=True)
    try:
        if a.check:
            r = tt.get("/api/v1/product/tab/count/get")
            j = r.get("json") or {}
            counts = {x["tab_id"]: x["count"] for x in (j.get("data") or [])}
            print(f"连通性 OK  code={j.get('code')}")
            print(f"tab 计数: {counts}")
        elif a.read:
            for r in sku_state(tt, a.read):
                print(f"  {r['seller_sku'] or '(空)':8} sku={r['sku_id']} "
                      f"wh={r['warehouse_id']} price={r['price']} qty={r['qty']}")
        elif a.audit_check:
            print(json.dumps(audit_state(tt, a.audit_check), ensure_ascii=False, indent=2))
        elif a.price:
            pid, sku, t = a.price
            r = set_price(tt, pid, sku, t)
            print(f"code={(r.get('json') or {}).get('code')}  "
                  f"{json.dumps((r.get('json') or {}).get('price_stocks_data'), ensure_ascii=False)[:300]}")
        elif a.price_all:
            pid, t = a.price_all
            r = set_price_all(tt, pid, t)
            print(f"code={(r.get('json') or {}).get('code')}  "
                  f"{json.dumps((r.get('json') or {}).get('price_stocks_data'), ensure_ascii=False)[:400]}")
        elif a.stock:
            pid, sku, wh, t = a.stock
            print(json.dumps(set_stock(tt, pid, sku, wh, int(t)), ensure_ascii=False))
        elif a.both:
            pid, sku, wh = a.both
            r = set_price_and_stock(tt, pid, sku, wh, price=a.set_price, stock=a.set_stock)
            print(json.dumps(r.get("json"), ensure_ascii=False)[:600])
        else:
            ap.print_help()
    finally:
        tt.close()
    print(f"# 耗时 {time.time()-t0:.2f}s，{tt.calls} 次请求", flush=True)


if __name__ == "__main__":
    main()
