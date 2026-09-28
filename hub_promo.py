#!/usr/bin/env python3
"""查清「促销日」开关的真实状态。只读。"""
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    r = pg.evaluate("""() => {
        const out = {};
        // 1) 找所有 role=switch
        out.switches = [...document.querySelectorAll('[role=switch]')].map(e => {
            const rc=e.getBoundingClientRect();
            const lbl = e.getAttribute('aria-label')||e.getAttribute('title')||'';
            return {label:lbl, checked:e.getAttribute('aria-checked'),
                    cls:(e.className||'').toString().slice(0,70),
                    x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width)};
        });
        // 2) 找 .promotion-days-switch-label 相关的整块
        const pd = document.querySelector('.promotion-days-switch-label');
        if (pd) {
            const box = pd.closest('div[class*="container"], div[class*="row"], div[class*="item"]') || pd.parentElement;
            out.promoBlock = {cls:(pd.className||'').toString(),
                              pdCls: (pd.className||'').toString(),
                              boxCls: box ? (box.className||'').toString().slice(0,90) : null,
                              html: box ? box.outerHTML.slice(0,1200) : null,
                              text: box ? (box.innerText||'').trim().slice(0,200) : null};
        }
        // 3) 全页搜「促销日」
        const txt = document.body.innerText;
        const idx = [];
        let i = -1;
        while ((i = txt.indexOf('促销日', i+1)) >= 0) idx.push(i);
        out.promoMentions = idx.map(i => txt.slice(Math.max(0,i-70), i+90).replace(/\\n/g,' | '));
        // 4) 输入框里含"促销"的
        out.promoInputs = [...document.querySelectorAll('input')].filter(e =>
            /促销|promo/i.test((e.placeholder||'')+(e.name||'')+(e.className||''))).map(e => ({
            ph:e.placeholder, val:e.value, cls:(e.className||'').toString().slice(0,60)}));
        return out;
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1)[:3000])
    b.close()
