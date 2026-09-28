#!/usr/bin/env python3
import sys, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    # 在 ROI/预算区域附近找所有 input（含隐藏的）
    r = pg.evaluate("""() => {
        const out=[];
        for (const e of document.querySelectorAll('input')) {
            const rc=e.getBoundingClientRect();
            out.push({type:e.type, val:e.value||'', ph:e.placeholder||'',
                cls:(e.className||'').toString().slice(0,64),
                x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width), h:Math.round(rc.height),
                visible: rc.width>2&&rc.height>2});
        }
        return out;
    }""")
    print(f"=== 全部 input ({len(r)}) ===")
    for e in r: print("  "+json.dumps(e, ensure_ascii=False))
    print()
    # ROI / 预算 标签附近的结构
    for label in ["creation-bid-title-v2-R0Rv", "budget-title-v2-LD-T"]:
        s = pg.evaluate("""(cls) => {
            const el = document.querySelector('.'+cls);
            if (!el) return null;
            const box = el.closest('div[class*="container"], div[class*="wrapper"], div[class*="row"]') || el.parentElement;
            return {html: box.outerHTML.slice(0, 1400)};
        }""", label)
        print(f"=== .{label} 附近 HTML ===")
        print((s or {}).get("html","(未找到)")[:1300])
        print()
    b.close()
