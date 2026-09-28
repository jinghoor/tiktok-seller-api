#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_state.png")
    print("截图: notes/hub_state.png")
    # 找所有按钮文案
    btns = pg.evaluate("""() => {
        const out=[];
        for (const e of document.querySelectorAll('button, [role=button], span')) {
            const t=(e.innerText||'').trim();
            if (!t || t.length>16) continue;
            const rc=e.getBoundingClientRect();
            if (rc.width<10||rc.height<10) continue;
            out.push({t, tag:e.tagName, x:Math.round(rc.x), y:Math.round(rc.y)});
        }
        const seen=new Set(); const u=[];
        for (const o of out){ if(seen.has(o.t))continue; seen.add(o.t); u.push(o); }
        return u.slice(0,40);
    }""")
    print(json.dumps(btns, ensure_ascii=False, indent=1)[:1500])
    b.close()
