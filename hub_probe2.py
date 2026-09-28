#!/usr/bin/env python3
import sys, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    # 所有 x-input-number 组件
    r = pg.evaluate("""() => {
        const out=[];
        for (const e of document.querySelectorAll('*')) {
            const tag = e.tagName.toLowerCase();
            if (!tag.startsWith('x-input-number')) continue;
            const rc=e.getBoundingClientRect();
            out.push({tag, uid:e.getAttribute('data-uid'), testid:e.getAttribute('data-testid'),
                value:e.getAttribute('value'), precision:e.getAttribute('precision'),
                x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width),
                html:e.outerHTML.slice(0,300)});
        }
        return out;
    }""")
    print(f"=== x-input-number 组件 ({len(r)}) ===")
    for e in r:
        print(f"  testid={e['testid']} uid={e['uid']} value={e['value']!r} prec={e['precision']} "
              f"pos=({e['x']},{e['y']}) w={e['w']}")
    print()
    # 看第一个组件的 shadow DOM 结构
    if r:
        sd = pg.evaluate("""() => {
            const e = document.querySelector('x-input-number-ra7bqy1k');
            if (!e) return null;
            const sr = e.shadowRoot;
            return {hasShadow: !!sr, html: sr ? sr.innerHTML.slice(0,900) : e.innerHTML.slice(0,900)};
        }""")
        print("=== ROI 组件内部 ===")
        print(json.dumps(sd, ensure_ascii=False, indent=1)[:1200])
    b.close()
