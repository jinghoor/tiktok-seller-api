#!/usr/bin/env python3
"""促销页请求抓取 hook —— Page.addScriptToEvaluateOnNewDocument 持久注入。

为什么必须用 addScriptToEvaluateOnNewDocument:
  Runtime.evaluate 注入的 hook 挂在当前 execution context 上，
  页面一旦完整导航(非 SPA 路由)就整块销毁，window.__hits 变 undefined。
  上次 discount/create 的 payload 就是这么丢的。

用法:
  python3 tt_promo_hook.py install [port] [--reload]     # 装 hook(默认 reload 一次验证)
  python3 tt_promo_hook.py hits    [port] [--grep P]     # 读捕获
  python3 tt_promo_hook.py save    [port] <out.json> [--grep P]
  python3 tt_promo_hook.py clear   [port]
  python3 tt_promo_hook.py uninstall [port]

只读工具: 不改页面状态，不抢窗口焦点(不调 Page.bringToFront)。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from hub_headless import CDPPage  # noqa: E402

DEFAULT_PORT = CDP_PORT
IDENT_FILE = HERE / "notes" / ".hook_identifier"

# 只抓业务接口，静态资源一律忽略；上限防止长会话内存膨胀
HOOK_SRC = r"""
(function () {
  if (window.__hook_v2) return;
  window.__hook_v2 = true;
  window.__hits = window.__hits || [];
  var MAX = 400;
  var RX = /\/api\/v1\/|\/promotion\/|\/api\/promotion/;

  function rec(o) {
    try {
      if (window.__hits.length >= MAX) window.__hits.shift();
      var u = String(o.url || '');
      var m = u.match(/^https?:\/\/[^/]+(\/[^?#]*)/);
      o.path = m ? m[1] : u;
      if (!RX.test(o.path)) return;
      if (o.body && o.body.length > 60000) o.body = o.body.slice(0, 60000) + '...[truncated]';
      if (o.resp && o.resp.length > 4000) o.resp = o.resp.slice(0, 4000) + '...[truncated]';
      o.ts = Date.now();
      window.__hits.push(o);
    } catch (e) {}
  }

  var _open = XMLHttpRequest.prototype.open;
  var _send = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (method, url) {
    this.__m = method; this.__u = url;
    return _open.apply(this, arguments);
  };
  XMLHttpRequest.prototype.send = function (body) {
    var xhr = this;
    var entry = {
      kind: 'xhr', method: String(xhr.__m || '').toUpperCase(),
      url: String(xhr.__u || ''), body: (body === undefined || body === null) ? null : String(body)
    };
    try {
      xhr.addEventListener('load', function () {
        entry.status = xhr.status;
        try { entry.resp = String(xhr.responseText || ''); } catch (e) {}
        rec(entry);
      });
      xhr.addEventListener('error', function () { entry.status = -1; rec(entry); });
    } catch (e) { rec(entry); }
    return _send.apply(this, arguments);
  };

  var _fetch = window.fetch;
  if (_fetch) {
    window.fetch = function (input, init) {
      var url = (typeof input === 'string') ? input : (input && input.url) || '';
      var method = (init && init.method) || (input && input.method) || 'GET';
      var body = (init && init.body) || null;
      if (body && typeof body !== 'string') {
        try { body = (body instanceof FormData) ? JSON.stringify(Object.fromEntries(body)) : JSON.stringify(body); }
        catch (e) { body = String(body); }
      }
      var entry = { kind: 'fetch', method: String(method).toUpperCase(), url: String(url), body: body ? String(body) : null };
      return _fetch.apply(this, arguments).then(function (res) {
        entry.status = res.status;
        try {
          res.clone().text().then(function (t) { entry.resp = t; rec(entry); },
                                  function () { rec(entry); });
        } catch (e) { rec(entry); }
        return res;
      }, function (err) { entry.status = -1; rec(entry); throw err; });
    };
  }
})();
"""


def tabs(port: int) -> list[dict]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=8) as f:
        return [t for t in json.load(f) if t.get("type") == "page"]


def new_tab(port: int, url: str) -> dict:
    """开新 tab —— 避免 reload 掉 operator 正在看的页面的筛选状态。"""
    req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(url, safe='')}",
                                 method="PUT")
    with urllib.request.urlopen(req, timeout=15) as f:
        return json.load(f)


def pick(port: int, needle: str | None = None) -> dict:
    """挑促销页 tab。needle 为 None 时优先 discount/create 页，其次任意 promotion 页。"""
    ts = tabs(port)
    if needle:
        for t in ts:
            if needle in (t.get("url") or ""):
                return t
        raise SystemExit(f"没有 URL 含 {needle!r} 的 tab；当前: "
                         + ", ".join((t.get('url') or '')[:70] for t in ts))
    for t in ts:
        if "promotion" in (t.get("url") or ""):
            return t
    raise SystemExit("没有 promotion tab；当前: "
                     + ", ".join((t.get('url') or '')[:70] for t in ts))


def connect(port: int, needle: str | None = None) -> CDPPage:
    t = pick(port, needle)
    pg = CDPPage(t["webSocketDebuggerUrl"], timeout=120)
    pg.enable("Page", "Runtime")
    return pg


def cmd_install(args) -> None:
    if args.new_tab:
        t = new_tab(args.port, args.new_tab)
        time.sleep(4.0)
        pg = CDPPage(t["webSocketDebuggerUrl"], timeout=120)
        pg.enable("Page", "Runtime")
        print("新 tab:", pg.url()[:90])
    else:
        pg = connect(args.port, args.tab)
    ident = pg.add_init_script(HOOK_SRC)
    IDENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    IDENT_FILE.write_text(ident)
    print(f"hook 已注入 (identifier={ident})  tab={pg.url()[:80]}")
    # 当前 context 也要立即生效，否则 reload 前的请求抓不到
    pg.js(HOOK_SRC + "; 'ok'")
    if args.reload:
        pg.navigate(pg.url(), wait=0)
        for _ in range(20):
            time.sleep(0.5)
            try:
                if pg.js("!!window.__hook_v2"):
                    break
            except Exception:
                pass
        time.sleep(2.5)
        n = pg.js("(window.__hits||[]).length")
        print(f"reload 后验证: __hook_v2={pg.js('!!window.__hook_v2')}  已捕获 {n} 条")
        for h in (json.loads(pg.js("JSON.stringify((window.__hits||[]).slice(-6))") or "[]")):
            print(f"  {h.get('method'):6} {h.get('path','')[:78]}  body={len(h.get('body') or '')}")
    pg.close()


def cmd_hits(args) -> None:
    pg = connect(args.port, args.tab)
    raw = pg.js("JSON.stringify(window.__hits || [])") or "[]"
    arr = json.loads(raw)
    if args.grep:
        arr = [h for h in arr if args.grep in (h.get("path") or "")]
    print(f"=== {len(arr)} 条 ===")
    for h in arr:
        print(f"  [{h.get('status')}] {h.get('method'):6} {h.get('path','')[:88]}  body={len(h.get('body') or '')}")
    if args.dump:
        for h in arr:
            print(f"\n--- {h.get('method')} {h.get('path')} ---")
            print("REQ :", (h.get("body") or "")[:2500])
            print("RESP:", (h.get("resp") or "")[:1200])
    pg.close()


def cmd_save(args) -> None:
    pg = connect(args.port, args.tab)
    raw = pg.js("JSON.stringify(window.__hits || [])") or "[]"
    arr = json.loads(raw)
    if args.grep:
        arr = [h for h in arr if args.grep in (h.get("path") or "")]
    if not arr:
        raise SystemExit("没有匹配的请求 —— 先确认页面确实发出了该请求")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(arr, ensure_ascii=False, indent=2))
    print(f"{len(arr)} 条 → {out}")
    last = arr[-1]
    print(f"最后一条: {last.get('method')} {last.get('path')}")
    print((last.get("body") or "")[:2000])
    pg.close()


def cmd_clear(args) -> None:
    pg = connect(args.port, args.tab)
    pg.js("window.__hits = []; 'cleared'")
    print("已清空 __hits")
    pg.close()


def cmd_uninstall(args) -> None:
    pg = connect(args.port, args.tab)
    if IDENT_FILE.exists():
        pg.remove_init_script(IDENT_FILE.read_text().strip())
        print("已移除 init script")
    pg.js("window.__hook_v2 = false; window.__hits = []; 'off'")
    pg.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="促销页请求 hook")
    ap.add_argument("cmd", choices=["install", "hits", "save", "clear", "uninstall"])
    ap.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT)
    ap.add_argument("out", nargs="?", help="save 的输出路径")
    ap.add_argument("--tab", help="按 URL 子串选 tab")
    ap.add_argument("--grep", help="按路径子串过滤")
    ap.add_argument("--dump", action="store_true", help="hits 时打印请求/响应体")
    ap.add_argument("--no-reload", dest="reload", action="store_false", help="install 后不 reload")
    ap.add_argument("--new-tab", help="先开一个新 tab 再注入(不碰现有页面)")
    args = ap.parse_args()
    {"install": cmd_install, "hits": cmd_hits, "save": cmd_save,
     "clear": cmd_clear, "uninstall": cmd_uninstall}[args.cmd](args)


if __name__ == "__main__":
    main()
