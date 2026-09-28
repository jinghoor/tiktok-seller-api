#!/usr/bin/env python3
"""运行时 hook fetch，抓「写请求」的 URL / body / JS 调用栈。

比被动抓包强的地方：调用栈直接指出哪段 bundle 代码构造了这个请求，
即使请求体字段名未知，也能从栈帧源码里读出来。

用法：
  python3 tt_fetch_hook.py --install            # 装 hook 并列出已捕获
  python3 tt_fetch_hook.py --show               # 读已捕获
  python3 tt_fetch_hook.py --show --clear       # 读完清空
  python3 tt_fetch_hook.py --stack <关键词>      # 看某请求的完整栈帧源码
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

sys.path.insert(0, ".")
from hub_headless import CDPPage  # noqa: E402

CDP_PORT = CDP_PORT

# 只关心写操作 + 产品相关读，避免日志被埋
HOOK_JS = r"""
(() => {
  if (window.__hookInstalled) return 'already';
  window.__hookInstalled = true;
  window.__hits = [];

  const WRITE = /\/(edit|update|set_|save|create|submit|delete|activate|deactivate|batch|partial|change|increase|decrease|adjust)/i;
  const KEEP  = /\/api\/v1\/product|\/api\/v1\/latamb/;

  const origFetch = window.fetch;
  window.fetch = async function (input, init) {
    const url = (typeof input === 'string') ? input : (input && input.url) || '';
    const method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
    const body = (init && init.body) || null;

    let stack = [];
    if (method !== 'GET' || WRITE.test(url)) {
      try { throw new Error('probe'); } catch (e) { stack = (e.stack || '').split('\n').slice(1, 14); }
    }
    let hit = null;
    if (KEEP.test(url) && (method !== 'GET' || WRITE.test(url))) {
      hit = {t: Date.now(), method, url: url.split('?')[0], query: url.split('?')[1] || '',
             body: (typeof body === 'string') ? body.slice(0, 4000) : null, stack};
      window.__hits.push(hit);
      if (window.__hits.length > 400) window.__hits.shift();
    }

    const res = await origFetch.apply(this, arguments);
    if (hit) {
      try {
        const c = res.clone();
        c.text().then(txt => { hit.resp = txt.slice(0, 1200); }).catch(() => {});
      } catch (e) {}
    }
    return res;
  };

  // XHR 同样 hook（部分老代码走 XHR）
  const XO = XMLHttpRequest.prototype.open, XS = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function (m, u) { this.__m = m; this.__u = u; return XO.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (b) {
    const self = this;
    if (KEEP.test(self.__u || '') && (self.__m || 'GET').toUpperCase() !== 'GET') {
      let stack = [];
      try { throw new Error('probe'); } catch (e) { stack = (e.stack || '').split('\n').slice(1, 14); }
      const hit = {t: Date.now(), method: self.__m, url: (self.__u || '').split('?')[0],
                   query: (self.__u || '').split('?')[1] || '',
                   body: typeof b === 'string' ? b.slice(0, 4000) : null, stack, via: 'xhr'};
      window.__hits.push(hit);
      self.addEventListener('load', () => { try { hit.resp = (self.responseText || '').slice(0, 1200); } catch (e) {} });
    }
    return XS.apply(this, arguments);
  };
  return 'installed';
})()
"""


def connect(port=CDP_PORT):
    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=8))
    page = next((x for x in tabs if x.get("type") == "page"
                 and "seller" in (x.get("url") or "")), None)
    if page is None:
        page = next(x for x in tabs if x.get("type") == "page")
    return CDPPage(page["webSocketDebuggerUrl"], timeout=180), page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--stack", metavar="KEYWORD")
    ap.add_argument("--json", metavar="OUT")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    a = ap.parse_args()

    pg, page = connect(a.port)
    try:
        if a.install:
            print("装入 hook →", pg.js(HOOK_JS))
            print("目标页面:", page.get("url"))
            # 状态检查：如果调用时页面已跳转，hook 丢了
            print("hits 数组存在:", pg.js("Array.isArray(window.__hits)"))

        if a.show or a.json:
            hits = json.loads(pg.js("JSON.stringify(window.__hits || [])") or "[]")
            if a.json:
                json.dump(hits, open(a.json, "w"), ensure_ascii=False, indent=2)
                print(f"已写 {a.json}（{len(hits)} 条）")
            for h in hits:
                print(f"\n[{h.get('method')}] {h.get('url')}")
                if h.get("body"):
                    print("  body:", h["body"][:500])
                if h.get("resp"):
                    print("  resp:", h["resp"][:300])
                top = [s.strip() for s in (h.get("stack") or [])[:3]]
                if top:
                    print("  stack:", " | ".join(x[:90] for x in top))
            print(f"\n共 {len(hits)} 条")
            if a.clear:
                pg.js("window.__hits = []")
                print("已清空")

        if a.stack:
            hits = json.loads(pg.js("JSON.stringify(window.__hits || [])") or "[]")
            matched = [h for h in hits if a.stack.lower() in (h.get("url") or "").lower()
                       or a.stack.lower() in (h.get("body") or "").lower()]
            for h in matched[-3:]:
                print(f"\n{'='*70}\n[{h.get('method')}] {h.get('url')}\n{'='*70}")
                print("body:", (h.get("body") or "")[:800])
                for i, s in enumerate(h.get("stack") or []):
                    print(f"  #{i}: {s[:200]}")
            print(f"\n匹配 {len(matched)} 条")
    finally:
        pg.close()


if __name__ == "__main__":
    main()
