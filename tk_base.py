#!/usr/bin/env python3
"""卖家中心 API 通用传输层 —— 所有域客户端共享的基座。

## 传输：借已打开的页面做页内 fetch（零打扰）

| 做法 | 结果 |
|---|---|
| `ctx.new_page()` | ❌ Chromium 默认**激活**新标签，会打扰操作员 |
| CDP `Target.createTarget({background:true})` | ❌ 不激活但 Playwright 不登记，回收困难 |
| **借已打开页面做页内 `fetch()`** | ✅ 采用 —— 零新建标签、零点击、零鼠标、零焦点 |

页内 `fetch` 自带 cookie，同源/跨域都行，后台标签也能跑（只有 timer 被节流）。
`close()` 只释放自己的 CDP 连接，**绝不关操作员的页面**。

## 店型差异（实测）

| | 跨境 | 本土 |
|---|---|---|
| 页面域 | `seller.tiktokshopglobalselling.com` | `seller-vn.tiktok.com` |
| API 域 | `api16-normal-sg.tiktokshopglobalselling.com`（**独立域**） | **同源** = 页面域 |
| `aid` | 6556 | 4068 |
| 时区 | `Asia/Bangkok` | `Asia/Ho_Chi_Minh` |

`is_local` 属性自动判定；`api_base` 自动选对。

## 用法

```python
from tk_base import BaseClient, ApiError

with BaseClient("tk89") as c:
    print(c.api_base, c.is_local)
    data = c.call("/api/v1/pay/settlement/settings")
    rows = c.call("/api/v1/insights/seller/core/stats", method="POST", body={"request": {}})
    # 批量（并发 + 超时，不会因为一个接口不响应就整体挂住）
    for r in c.batch([{"path": "/api/v1/x"}, {"path": "/api/v1/y", "method": "POST"}]):
        print(r["path"], r["http"], r.get("code"))
```
"""
from __future__ import annotations

import base64
import json
import pathlib
import sys
from typing import Any, Iterator, Sequence

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tk01_config as CFG  # noqa: E402


class ApiError(RuntimeError):
    pass


# 单次 fetch 的页内实现。**必须带超时** —— 服务端不响应时 fetch 会永久挂起，
# 整个 Promise.all 就永远不 resolve（实测把测绘卡死在 60/4205）。
_JS_ONE = """async (job) => {
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), job.tmo || 20000);
  try {
    const opt = { method: job.method, credentials: 'include', signal: ac.signal,
                  headers: { 'content-type': 'application/json; charset=utf-8',
                             'accept': 'application/json, text/plain, */*' } };
    if (job.method !== 'GET' && job.body !== null && job.body !== undefined)
      opt.body = JSON.stringify(job.body);
    const r = await fetch(job.url, opt);
    const ab = await r.arrayBuffer();
    const u8 = new Uint8Array(ab);
    let s = ''; for (let i = 0; i < u8.length; i += 8192)
      s += String.fromCharCode.apply(null, u8.subarray(i, i + 8192));
    return JSON.stringify({ ok: true, http: r.status, b64: btoa(s) });
  } catch (e) {
    return JSON.stringify({ ok: false, http: 0, err: String(e).slice(0, 200) });
  } finally {
    clearTimeout(timer);
  }
}"""

_JS_BATCH = """async ({jobs, conc}) => {
  const one = async (job) => {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), job.tmo || 20000);
    try {
      const opt = { method: job.method, credentials: 'include', signal: ac.signal,
                    headers: { 'content-type': 'application/json; charset=utf-8' } };
      if (job.method !== 'GET' && job.body !== null && job.body !== undefined)
        opt.body = JSON.stringify(job.body);
      const r = await fetch(job.url, opt);
      const t = await r.text();
      let code = null, msg = '';
      try { const d = JSON.parse(t); code = d.code; msg = String(d.message || '').slice(0, 120); }
      catch (e) { msg = 'NON_JSON: ' + t.replace(/\\s+/g, ' ').slice(0, 80); }
      return { ok: true, http: r.status, code, msg };
    } catch (e) {
      return { ok: false, http: 0, code: null, msg: 'ERR: ' + String(e).slice(0, 90) };
    } finally {
      clearTimeout(timer);
    }
  };
  const out = [];
  for (let i = 0; i < jobs.length; i += conc)
    out.push(...await Promise.all(jobs.slice(i, i + conc).map(one)));
  return JSON.stringify(out);
}"""


class BaseClient:
    """借已打开页面发请求的通用客户端。"""

    def __init__(self, shop: str | None = None, *, port: int | None = None,
                 page_hint: str | None = None, verbose: bool = False,
                 timeout_ms: int = 20000):
        self.shop = CFG.load_shop(shop)
        self.key = self.shop["_key"]
        self.port = port or self.shop["cdp_port"]
        self.page_hint = page_hint
        self.verbose = verbose
        self.timeout_ms = timeout_ms
        self._pw = None
        self._browser = None
        self._page = None

    # ── 店型判定 ──
    @property
    def is_local(self) -> bool:
        """本土店的卖家中心域名本身就是 API 域（同源）。"""
        return "tiktokshopglobalselling" not in self.shop["seller_origin"]

    @property
    def api_base(self) -> str:
        return self.shop["seller_origin"] if self.is_local else self.shop["api_host"]

    @property
    def page_origin(self) -> str:
        return self.shop["seller_origin"]

    @property
    def query_block(self) -> str:
        sid, aid = self.shop["seller_id"], self.shop["aid"]
        return (f"aid={aid}&app_id={aid}&app_name={self.shop['api_app_name']}"
                f"&device_platform=web&oec_seller_id={sid}&seller_id={sid}"
                f"&locale=zh-CN&language=zh-CN")

    # ── 借页面 ──
    def _connect(self):
        if self._page is not None:
            try:
                _ = self._page.url          # 页面被关掉会抛
                return self._page
            except Exception:
                self._page = None
        from playwright.sync_api import sync_playwright
        if self._pw is None:
            self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
        ctx = self._browser.contexts[0]
        pages = [p for p in ctx.pages if not p.url.startswith("chrome-extension")]
        if self.page_hint:
            self._page = next((p for p in pages if self.page_hint in p.url), None)
        if self._page is None:
            # 只要同源就行 —— 卖家中心任意页面都能当 fetch 源（API 与页面无关）
            self._page = next((p for p in pages if p.url.startswith(self.page_origin)), None)
        if self._page is None:
            self._page = next((p for p in pages if p.url.startswith(self.api_base)), None)
        if self._page is None:
            raise ApiError(
                f"没找到可借的页面（端口 {self.port}，需要 {self.page_origin} 下已打开的页面）。"
                f"现有：{[p.url[:70] for p in pages]}")
        if self.verbose:
            print(f"  [借页面] {self._page.url[:88]}", file=sys.stderr)
        return self._page

    def close(self):
        """只释放自己的 CDP 连接 —— 绝不关操作员的页面。"""
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
        self._page = self._browser = self._pw = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    # ── URL 组装 ──
    def build_url(self, path: str, *, params: dict | None = None,
                  version: int | None = None, auto_version: bool = False) -> str:
        if version and "/v1/" in path:
            path = path.replace("/v1/", f"/v{version}/")
        elif auto_version and "/v1/" in path:
            # 本土店实测：部分族只有 v2 注册（如 pay/settlement/file/list）
            path = path.replace("/v1/", "/v2/")
        q = self.query_block
        if params:
            q += "&" + "&".join(
                f"{k}={json.dumps(v) if isinstance(v, (dict, list)) else v}"
                for k, v in params.items() if v is not None)
        return f"{self.api_base}{path}?{q}"

    # ── 单发 ──
    def call(self, path: str, *, method: str = "GET", body: Any = None,
             params: dict | None = None, version: int | None = None,
             raw: bool = False, timeout_ms: int | None = None) -> Any:
        """发一个请求。`raw=True` 返回 (http, bytes)，否则返回解析后的 JSON。"""
        url = self.build_url(path, params=params, version=version)
        pg = self._connect()
        out = json.loads(pg.evaluate(_JS_ONE, {
            "url": url, "method": method.upper(), "body": body,
            "tmo": timeout_ms or self.timeout_ms}))
        if not out.get("ok"):
            raise ApiError(f"fetch 失败 {path}: {out.get('err')}")
        blob = base64.b64decode(out["b64"])
        if raw:
            return out["http"], blob
        txt = blob.decode("utf-8", "replace")
        try:
            return json.loads(txt)
        except Exception:
            return {"_non_json": txt[:600], "_http": out["http"]}

    def call_ok(self, *a, **kw) -> Any:
        """只关心 data 的场景。`code != 0` 抛 ApiError。"""
        d = self.call(*a, **kw)
        if not isinstance(d, dict) or d.get("code") != 0:
            code = d.get("code") if isinstance(d, dict) else None
            msg = d.get("message") if isinstance(d, dict) else str(d)[:120]
            raise ApiError(f"{a[0] if a else kw.get('path')}: code={code} {msg}")
        return d.get("data")

    def try_versions(self, path: str, *, versions: Sequence[int] = (1, 2),
                     **kw) -> Any:
        """依次试版本，返回第一个 `code == 0` 的。"""
        last = None
        for v in versions:
            try:
                d = self.call(path, version=v, **kw)
            except ApiError:
                continue
            last = d
            if isinstance(d, dict) and d.get("code") == 0:
                d["_used_version"] = v
                return d
        return last

    # ── 批量 ──
    def batch(self, jobs: Sequence[dict], *, conc: int = 8,
              show_progress: bool = False) -> list[dict]:
        """并发批量。每个 job: `{path, method?, body?, params?, version?}`。

        返回 `[{path, http, code, msg}]` —— 一个接口超时不会拖垮整批。
        """
        prepared = []
        for j in jobs:
            prepared.append({
                "path": j["path"],
                "url": self.build_url(j["path"], params=j.get("params"),
                                      version=j.get("version")),
                "method": (j.get("method") or "GET").upper(),
                "body": j.get("body") if j.get("method", "GET").upper() != "GET" else None,
                "tmo": j.get("timeout_ms") or self.timeout_ms,
            })
        pg = self._connect()
        out: list[dict] = []
        for i in range(0, len(prepared), 40):
            chunk = prepared[i:i + 40]
            try:
                got = json.loads(pg.evaluate(_JS_BATCH,
                                             {"jobs": chunk, "conc": conc}))
            except Exception as e:
                # 页面导航把执行上下文销毁了 —— 重新借一个再继续
                if self.verbose:
                    print(f"  [批 {i}] 上下文失效（{str(e)[:50]}），重借页面", file=sys.stderr)
                self._page = None
                pg = self._connect()
                try:
                    got = json.loads(pg.evaluate(_JS_BATCH,
                                                 {"jobs": chunk, "conc": conc}))
                except Exception as e2:
                    got = [{"ok": False, "http": 0, "code": None,
                            "msg": f"BATCH_FAIL: {str(e2)[:70]}"} for _ in chunk]
            for j, r in zip(chunk, got):
                out.append({"path": j["path"], "method": j["method"],
                            "http": r.get("http"), "code": r.get("code"),
                            "msg": r.get("msg", ""), "ok": r.get("ok", False)})
            if show_progress:
                print(f"    {min(i+40, len(prepared))}/{len(prepared)}", flush=True)
        return out

    # ── 二进制（导出/下载） ──
    def download(self, url: str, dest: str | pathlib.Path, *,
                 timeout_ms: int | None = None) -> pathlib.Path:
        """下载到文件。`url` 可以是相对路径（走本店 api_base）或绝对 URL。"""
        if not url.startswith("http"):
            url = self.build_url(url)
        http, blob = self.call(url, method="GET", raw=True, timeout_ms=timeout_ms)
        dest = pathlib.Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        if self.verbose:
            print(f"  [下载] {http} {len(blob)} B → {dest}", file=sys.stderr)
        return dest

    def shop_info(self) -> dict:
        return {"key": self.key, "label": self.shop.get("label"),
                "region": self.shop.get("region"), "seller_id": self.shop["seller_id"],
                "is_local": self.is_local, "api_base": self.api_base,
                "port": self.port}
