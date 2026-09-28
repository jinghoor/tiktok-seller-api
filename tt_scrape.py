#!/usr/bin/env python3
"""卖家中心接口发现工具。

两条路:
  static  —— 拉页面所有 JS bundle,正则抽 API 路径(能覆盖 UI 未触发的接口)
  record  —— 注入 XHR/fetch 钩子,跑真实操作抓完整请求/响应

    python3 tt_scrape.py static --port CDP_PORT --page /product/create
    python3 tt_scrape.py record --port CDP_PORT --url https://seller-vn.tiktok.com/product/manage
    python3 tt_scrape.py tabs   --port CDP_PORT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_headless import HubStudio, attach  # noqa: E402

BASE = "https://seller-vn.tiktok.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes")
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------- 静态抽取

# 覆盖:字符串字面量里的 /api/... 路径、模板拼接的 base、绝对 URL
API_RE = re.compile(
    r"""["'`](?P<path>/(?:api|oec|api_bg|api-gateway|homepage|passport|aweme)[A-Za-z0-9_\-/{}$.:]*
        |(?:https?://[A-Za-z0-9.\-]+)?/(?:api|oec)/v[0-9]/[A-Za-z0-9_\-/{}$.:]*)["'`]""",
    re.X)

# 形如 `${X}/api/v1/product/foo` 或 "/api/v1/product/" + name
CONCAT_RE = re.compile(r"[\"'`](/[A-Za-z0-9_\-/{}$.]*?/api/[A-Za-z0-9_\-/{}$.]{4,})[\"'`]")
GENERIC_RE = re.compile(r"[\"'`](/[a-z][A-Za-z0-9_\-/{}]{6,})[\"'`]")


def fetch_scripts(port: int, url: str, wait: float = 6.0) -> list[str]:
    with attach(port) as p:
        p.navigate(url, wait=wait)
        srcs = p.js("JSON.stringify([...document.querySelectorAll('script[src]')].map(s=>s.src))")
        return json.loads(srcs or "[]")


def download(url: str, dest: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except (urllib.error.URLError, OSError):
        return False


def extract_paths(text: str) -> set[str]:
    hits: set[str] = set()
    for m in API_RE.finditer(text):
        hits.add(m.group("path"))
    for m in CONCAT_RE.finditer(text):
        hits.add(m.group(1))
    return hits


def cmd_static(a) -> int:
    url = a.url or (BASE + a.page)
    print(f"→ 打开 {url}")
    srcs = fetch_scripts(a.port, url, a.wait)
    print(f"  发现 {len(srcs)} 个 script")

    # SPA 常常是动态 import:再从 performance 里拿已加载资源
    with attach(a.port) as p:
        res = p.js("JSON.stringify(performance.getEntriesByType('resource')"
                   ".map(e=>e.name).filter(n=>n.endsWith('.js')))")
        perf = json.loads(res or "[]")
    alljs = list(dict.fromkeys(srcs + perf))
    print(f"  合并后 {len(alljs)} 个 JS")

    os.makedirs(f"{OUT}/js", exist_ok=True)
    paths: set[str] = set()
    ok = 0
    for i, u in enumerate(alljs):
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/")[-1].split("?")[0])[:80]
        dest = f"{OUT}/js/{i:03d}_{name}"
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            ok += 1
        elif download(u, dest):
            ok += 1
        else:
            continue
        try:
            with open(dest, encoding="utf-8", errors="replace") as f:
                paths |= extract_paths(f.read())
        except OSError:
            pass
        if (i + 1) % 20 == 0:
            print(f"  ...{i+1}/{len(alljs)} 累计路径 {len(paths)}")

    print(f"\n下载成功 {ok}/{len(alljs)},抽出 {len(paths)} 条候选路径")
    picked = sorted(p for p in paths if any(k in p.lower() for k in a.filter))
    out = f"{OUT}/product_api_paths.json"
    with open(out, "w") as f:
        json.dump({"page": url, "all_paths": sorted(paths), "filtered": picked}, f,
                  ensure_ascii=False, indent=2)
    print(f"写入 {out}")
    print(f"\n按关键词 {a.filter} 过滤后 {len(picked)} 条:")
    for p in picked:
        print("   ", p)
    return 0


# ---------------------------------------------------------------- 动态记录

RECORDER = r"""
(() => {
  const KEY = '__ttRecBuf';
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; } };
  const save = (arr) => { try { localStorage.setItem(KEY, JSON.stringify(arr.slice(-400))); } catch (e) {} };
  const buf = load();
  const push = (rec) => { buf.push(rec); save(buf); };

  const clip = (s, n) => (typeof s === 'string' && s.length > n) ? s.slice(0, n) + `...[+${s.length-n}]` : s;

  const makeApi = () => ({
    get: () => load(),
    clear: () => { localStorage.removeItem(KEY); buf.length = 0; return 'cleared'; },
    count: () => load().length,
  });

  // 页面重载后 window.__ttRec 会丢,但钩子还在 —— 只重建 API 对象,不重复挂钩
  if (window.__ttHookInstalled) {
    window.__ttRec = makeApi();
    return 'api-rebuilt';
  }
  window.__ttHookInstalled = true;

  const origOpen = XMLHttpRequest.prototype.open;
  const origSend = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u, ...rest) {
    this.__tt = { method: m, url: String(u) };
    return origOpen.call(this, m, u, ...rest);
  };
  XMLHttpRequest.prototype.send = function (body) {
    const info = this.__tt || {};
    const t0 = Date.now();
    this.addEventListener('load', () => {
      let resp = '';
      try { resp = this.responseType === '' || this.responseType === 'text' ? this.responseText : `<${this.responseType}>`; } catch (e) {}
      push({ kind: 'xhr', method: info.method, url: info.url, status: this.status,
             reqBody: clip(typeof body === 'string' ? body : null, 200000),
             respBody: clip(resp, 60000), ms: Date.now() - t0, ts: Date.now() });
    });
    return origSend.call(this, body);
  };

  const origFetch = window.fetch;
  window.fetch = function (input, init) {
    const u = typeof input === 'string' ? input : (input && input.url);
    const m = (init && init.method) || (input && input.method) || 'GET';
    const body = init && init.body;
    const t0 = Date.now();
    return origFetch.apply(this, arguments).then((r) => {
      const clone = r.clone();
      clone.text().then((txt) => {
        push({ kind: 'fetch', method: m, url: String(u), status: r.status,
               reqBody: clip(typeof body === 'string' ? body : null, 200000),
               respBody: clip(txt, 60000), ms: Date.now() - t0, ts: Date.now() });
      }).catch(() => {});
      return r;
    });
  };

  window.__ttRec = makeApi();
  return 'installed';
})()
"""


def cmd_record(a) -> int:
    with attach(a.port) as p:
        # 先 reset 缓冲(用 localStorage,跨导航存活)
        p.js("localStorage.removeItem('__ttRecBuf')")
        # 关键:用 addScriptToEvaluateOnNewDocument,在任何页面 JS 之前注入,跨导航存活
        ident = p.add_init_script(RECORDER)
        print("预注入钩子:", ident)
        # 立即在当前页也装一份,这样不导航也能抓到 SPA 内部路由的请求
        print("当前页安装:", p.js(RECORDER))
        if not a.no_nav:
            p.navigate(a.url or (BASE + a.page), wait=a.wait)
        else:
            time.sleep(a.wait)
        if a.js:
            print("执行附加 JS:", p.js(a.js))
            time.sleep(a.extra_wait)
        data = json.loads(p.js("JSON.stringify(window.__ttRec.get())") or "[]")

    hits = [d for d in data if any(k in (d.get("url") or "").lower() for k in a.filter)]
    out = a.out or f"{OUT}/capture.json"
    with open(out, "w") as f:
        json.dump({"url": a.url or (BASE + a.page), "total": len(data),
                   "filtered": a.filter, "records": hits if a.filter else data}, f,
                  ensure_ascii=False, indent=2)
    print(f"\n抓到 {len(data)} 条请求,命中过滤 {len(hits)} 条 → {out}")
    for d in hits if a.filter else data:
        u = (d.get("url") or "")
        u = u.split("?")[0] if a.strip_query else u
        print(f"  [{d.get('status')}] {d.get('method'):<5} {u[:150]}")
    return 0


def cmd_tabs(a) -> int:
    hub = HubStudio()
    for c in hub.running():
        from hub_headless import _probe_cdp_for_pid, cdp_get
        port = _probe_cdp_for_pid(c.get("pid"))
        ok, tabs = cdp_get(port, "/json/list") if port else (False, [])
        print(f"\n== {c['containerCode']} pid={c['pid']} CDP={port}")
        for t in (tabs or []):
            if t.get("type") == "page":
                print("   ", (t.get("title") or "")[:36], "|", (t.get("url") or "")[:120])
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="卖家中心接口发现")
    # 父级与子级都接受 --port,这样 `--port N record ...` 和 `record --port N ...` 都行
    ap.add_argument("--port", type=int, default=CDP_PORT)
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--port", type=int, default=CDP_PORT)

    s = sub.add_parser("static", parents=[common], help="扒 bundle 抽 API 路径")
    s.add_argument("--page", default="/product/manage")
    s.add_argument("--url", default=None)
    s.add_argument("--wait", type=float, default=6.0)
    s.add_argument("--filter", nargs="*", default=["product", "sku", "category", "image",
                                                   "brand", "logistic", "package", "warehouse",
                                                   "spec", "attribute", "draft", "listing"])
    s.set_defaults(func=cmd_static)

    r = sub.add_parser("record", parents=[common], help="抓真实请求")
    r.add_argument("--page", default="/product/manage")
    r.add_argument("--url", default=None)
    r.add_argument("--wait", type=float, default=8.0)
    r.add_argument("--extra-wait", type=float, default=0.0)
    r.add_argument("--js", default=None)
    r.add_argument("--filter", nargs="*", default=[])
    r.add_argument("--out", default=None)
    r.add_argument("--no-nav", action="store_true",
                   help="不导航,只在当前页装钩子抓 SPA 内部路由")
    r.add_argument("--reset", action="store_true", default=True)
    r.add_argument("--strip-query", action="store_true")
    r.set_defaults(func=cmd_record)

    sub.add_parser("tabs", parents=[common], help="列所有运行中实例的标签页").set_defaults(func=cmd_tabs)

    a = ap.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
