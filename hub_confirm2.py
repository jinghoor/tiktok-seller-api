#!/usr/bin/env python3
"""真实鼠标点【确认】关闭抽屉。"""
import sys, time, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 找【确认】的可见元素
    loc = pg.get_by_text("确认", exact=True)
    n = loc.count()
    print(f"'确认' 精确匹配 {n} 个")
    target = None
    for i in range(n):
        el = loc.nth(i)
        try:
            box = el.bounding_box()
            if box and box["width"] > 20 and box["height"] > 15:
                print(f"  [{i}] box={box} tag={el.evaluate('e=>e.tagName')}")
                if target is None: target = el
        except Exception as e:
            print(f"  [{i}] err {str(e)[:60]}")
    if not target:
        print("找不到可点的确认"); sys.exit(1)

    print("\n真实鼠标点击【确认】…")
    target.click(timeout=10000)
    time.sleep(4)

    # 校验抽屉是否关闭
    r = pg.evaluate("""() => {
        const d = document.querySelector('[data-testid="product-select-index-6KM6mN"]');
        const rc = d ? d.getBoundingClientRect() : null;
        const topAt = document.elementsFromPoint(700,700).slice(0,3).map(e=>e.tagName);
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        const m2 = txt.match(/已选择\\s*(\\d+)\\s*件商品/);
        return {drawer: !!d, drawerRect: rc ? [Math.round(rc.width), Math.round(rc.height)] : null,
                topAt, listSelected: m?m[1]:null, anySelected: m2?m2[1]:null};
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    time.sleep(2)
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_closed.png")
    print("截图: notes/hub_closed.png")
    b.close()
