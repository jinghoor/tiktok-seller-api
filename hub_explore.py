#!/usr/bin/env python3
"""侦察 Hub Studio 里 TikTok 广告创建页的结构。只读，不点击。"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pages = [pg for c in b.contexts for pg in c.pages if "tiktok" in pg.url]
    pg = pages[0]
    print(f"页面: {pg.url[:120]}")
    print(f"标题: {pg.title()!r}")
    print()

    # 1) 页面主要文本
    txt = pg.evaluate("() => document.body ? document.body.innerText : ''")
    print("=== 页面文本(前 2000 字) ===")
    print(txt[:2000])
    print()

    # 2) 可点元素:按钮/链接/菜单
    els = pg.evaluate("""() => {
        const out = [];
        const sel = 'button, a[href], [role="button"], [role="menuitem"], [role="tab"], .arco-btn, .btn';
        for (const e of document.querySelectorAll(sel)) {
            const t = (e.innerText||'').trim().replace(/\\s+/g,' ');
            if (!t || t.length > 60) continue;
            const r = e.getBoundingClientRect();
            if (r.width < 2 || r.height < 2) continue;
            out.push({text: t, tag: e.tagName, cls: (e.className||'').toString().slice(0,70),
                      x: Math.round(r.x), y: Math.round(r.y)});
        }
        // 去重
        const seen = new Set(); const uniq = [];
        for (const o of out) { const k = o.text + o.tag; if (seen.has(k)) continue; seen.add(k); uniq.push(o); }
        return uniq.slice(0, 80);
    }""")
    print(f"=== 可点元素 ({len(els)}) ===")
    for e in els:
        print(f"  [{e['tag']:6}] ({e['x']:>5},{e['y']:>4}) {e['text'][:56]}")
    print()

    # 3) 输入框
    inputs = pg.evaluate("""() => {
        const out = [];
        for (const e of document.querySelectorAll('input, textarea, [contenteditable="true"]')) {
            const r = e.getBoundingClientRect();
            if (r.width < 2) continue;
            out.push({tag: e.tagName, type: e.type||'', placeholder: e.placeholder||'',
                      name: e.name||'', cls:(e.className||'').toString().slice(0,60),
                      x: Math.round(r.x), y: Math.round(r.y)});
        }
        return out.slice(0, 30);
    }""")
    print(f"=== 输入框 ({len(inputs)}) ===")
    for e in inputs:
        print(f"  [{e['tag']:8} {e['type']:10}] ({e['x']:>5},{e['y']:>4}) ph={e['placeholder'][:40]!r} name={e['name'][:20]}")
    b.close()
