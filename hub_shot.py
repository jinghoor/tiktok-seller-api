#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_now.png")
    print("截图已存 notes/hub_now.png")
    # 找所有 position:fixed/absolute 且 z-index 高的容器
    r = pg.evaluate("""() => {
        const out=[];
        for (const e of document.querySelectorAll('*')) {
            const cs = getComputedStyle(e);
            const z = parseInt(cs.zIndex||'0',10);
            const rc = e.getBoundingClientRect();
            if (z > 100 && rc.width > 300 && rc.height > 200) {
                const t=(e.innerText||'').trim();
                out.push({tag:e.tagName, cls:(e.className||'').toString().slice(0,64),
                    z, pos:cs.position, x:Math.round(rc.x), y:Math.round(rc.y),
                    w:Math.round(rc.width), h:Math.round(rc.height), head:t.slice(0,110)});
            }
        }
        return out.sort((a,b)=>b.z-a.z).slice(0,8);
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1)[:2200])
    b.close()
