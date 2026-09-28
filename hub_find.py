#!/usr/bin/env python3
import sys, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    w = pg.evaluate("() => window.innerWidth + 'x' + window.innerHeight")
    print(f"视口: {w}")
    print(f"页面总高: {pg.evaluate('() => document.body.scrollHeight')}")
    print()
    # 找含关键文案的元素及其位置/标签
    keys = ["所有商品","选定商品","排除商品","ROI 目标","商品 ROI 目标","日预算","总收入（原模式）","净销售额（新模式）"]
    for k in keys:
        r = pg.evaluate("""(k) => {
            const hits=[];
            for (const e of document.querySelectorAll('*')) {
                if (e.children.length) continue;
                const t=(e.innerText||'').trim();
                if (t !== k) continue;
                const rc=e.getBoundingClientRect();
                hits.push({tag:e.tagName, cls:(e.className||'').toString().slice(0,60),
                    x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width)});
            }
            return hits.slice(0,4);
        }""", k)
        print(f"  {k!r}: {json.dumps(r, ensure_ascii=False)}")
    print()
    # 找所有 contenteditable / arco-input / 可输入容器
    inp = pg.evaluate("""() => {
        const out=[];
        for (const e of document.querySelectorAll('[contenteditable="true"], .arco-input-inner, [class*="input-inner"], [class*="Input"]')) {
            const r=e.getBoundingClientRect();
            if (r.width<10||r.height<10) continue;
            out.push({tag:e.tagName, cls:(e.className||'').toString().slice(0,70),
                ce:e.getAttribute('contenteditable'), x:Math.round(r.x), y:Math.round(r.y),
                w:Math.round(r.width), txt:(e.innerText||e.value||'').trim().slice(0,30)});
        }
        return out.slice(0,25);
    }""")
    print(f"=== 输入类元素 ({len(inp)}) ===")
    for e in inp: print("  "+json.dumps(e, ensure_ascii=False))
    b.close()
