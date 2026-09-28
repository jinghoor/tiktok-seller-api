#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    r = pg.evaluate("""() => {
        const out = {};
        const d = document.querySelector('[data-testid="product-select-index-6KM6mN"]');
        out.drawerFound = !!d;
        if (d) {
            const rc = d.getBoundingClientRect();
            const cs = getComputedStyle(d);
            out.drawer = {x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width),
                          h:Math.round(rc.height), display:cs.display, visibility:cs.visibility,
                          transform:cs.transform.slice(0,40), open:d.getAttribute('open'),
                          visible:d.getAttribute('visible'),
                          text:(d.innerText||'').trim().slice(0,120)};
        }
        // 全部 ks-drawer
        out.drawers = [...document.querySelectorAll('ks-drawer-1-1-28, [class*="KsDrawer"]')].map(e => {
            const rc=e.getBoundingClientRect(); const cs=getComputedStyle(e);
            return {outer:e.outerHTML.slice(0,150), x:Math.round(rc.x), w:Math.round(rc.width),
                    display:cs.display, open:e.getAttribute('open'), visible:e.getAttribute('visible')};
        });
        return out;
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1)[:2200])
    b.close()
