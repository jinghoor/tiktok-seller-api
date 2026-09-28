#!/usr/bin/env python3
import json, sys
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    print("=== 所有页面 ===")
    for c in b.contexts:
        for pg in c.pages:
            print(f"  {pg.url[:130]}")
            print(f"    title={pg.title()!r}")
    print()
    pg = next((x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url), None)
    if pg:
        print("=== 创建页顶部覆盖层检测 ===")
        r = pg.evaluate("""() => {
            const out = {overlays: [], fixed: []};
            for (const e of document.querySelectorAll('body > div, body > *')) {
                const rc = e.getBoundingClientRect();
                const cs = getComputedStyle(e);
                if (rc.width > 300 && rc.height > 200 && (cs.position === 'fixed' || cs.position === 'absolute')) {
                    out.overlays.push({tag:e.tagName, cls:(e.className||'').toString().slice(0,80),
                        pos:cs.position, z:cs.zIndex, x:Math.round(rc.x), y:Math.round(rc.y),
                        w:Math.round(rc.width), h:Math.round(rc.height),
                        txt:(e.innerText||'').trim().slice(0,150)});
                }
            }
            return out;
        }""")
        print(json.dumps(r, ensure_ascii=False, indent=1)[:2000])
        print()
        print("=== 页面文本里搜「商品」相关区段 ===")
        txt = pg.evaluate("() => document.body.innerText")
        for kw in ["添加商品", "已选", "选择商品", "商品名称", "搜索"]:
            i = txt.find(kw)
            if i >= 0:
                print(f"  {kw!r} @ {i}: ...{txt[max(0,i-60):i+200]}...".replace("\n"," | "))
                print()
    b.close()
