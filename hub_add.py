#!/usr/bin/env python3
"""用真实鼠标点击【添加商品】。"""
import sys, json, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 精确定位:文本完全等于「添加商品」的最内层元素
    loc = pg.locator("text='添加商品'")
    n = loc.count()
    print(f"匹配 '添加商品' 的元素数: {n}")
    target = None
    for i in range(n):
        el = loc.nth(i)
        try:
            box = el.bounding_box()
            tag = el.evaluate("e => e.tagName + '.' + (e.className||'').toString().slice(0,50)")
            print(f"  [{i}] {tag} box={box}")
            if box and box['width'] > 20 and target is None:
                target = el
        except Exception as e:
            print(f"  [{i}] err {e}")
    if not target:
        print("没找到可点的目标"); sys.exit(1)

    print("\n真实鼠标点击…")
    target.scroll_into_view_if_needed()
    time.sleep(0.5)
    target.click(timeout=8000)
    time.sleep(6)

    # 检查弹窗
    r = pg.evaluate("""() => {
        const found = [];
        for (const e of document.querySelectorAll('div, section')) {
            const rc = e.getBoundingClientRect();
            const cs = getComputedStyle(e);
            if (rc.width > 400 && rc.height > 300 && (cs.position === 'fixed')) {
                const t = (e.innerText||'').trim();
                if (t.length > 30) found.push({cls:(e.className||'').toString().slice(0,70),
                    x:Math.round(rc.x), y:Math.round(rc.y), w:Math.round(rc.width), h:Math.round(rc.height),
                    head: t.slice(0,200)});
            }
        }
        return found.slice(0,5);
    }""")
    print("=== fixed 覆盖层 ===")
    print(json.dumps(r, ensure_ascii=False, indent=1)[:2000])
    b.close()
