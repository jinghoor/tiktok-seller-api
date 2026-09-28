#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    for i in range(6):
        time.sleep(3)
        r = pg.evaluate("""() => {
            const d = document.querySelector('[data-testid="product-select-index-6KM6mN"]');
            const st = document.elementsFromPoint(700, 700).slice(0,4).map(e=>e.tagName+'.'+(e.className||'').toString().slice(0,40));
            const txt = document.body.innerText;
            const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
            return {drawerInDom: !!d, drawerLen: d?d.outerHTML.length:0,
                    topEls: st, selected: m?m[1]:null};
        }""")
        print(f"  [{(i+1)*3}s] drawer={r['drawerInDom']}({r['drawerLen']}B) selected={r['selected']}")
        print(f"        (700,700) 顶层元素: {r['topEls']}")
        if not r["drawerInDom"]:
            print("  → 抽屉已卸载"); break
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_after_confirm.png")
    print("截图: notes/hub_after_confirm.png")
    b.close()
