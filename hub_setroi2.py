#!/usr/bin/env python3
"""设 ROI —— 逐字符删除后输入。"""
import sys, time, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
ROI  = sys.argv[2] if len(sys.argv) > 2 else "14"
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    sel = '[data-testid="bid-select-index-9egWxE"] input'
    host = pg.locator('[data-testid="bid-select-index-9egWxE"]')
    inp  = pg.locator(sel)
    print(f"设置前: {inp.input_value()!r}  (组件 {host.get_attribute('value')!r})")

    inp.click(timeout=15000)
    time.sleep(0.4)
    # 全选:三击选中全部文本
    inp.click(click_count=3, timeout=8000)
    time.sleep(0.3)
    pg.keyboard.press("Backspace")
    time.sleep(0.5)
    print(f"清空后: {inp.input_value()!r}")
    if inp.input_value().strip():
        # 兜底:逐字符删
        for _ in range(12):
            pg.keyboard.press("Backspace")
        time.sleep(0.4)
        print(f"再次清空后: {inp.input_value()!r}")

    inp.type(ROI, delay=100)
    time.sleep(0.6)
    pg.keyboard.press("Tab")
    time.sleep(2.5)
    print(f"设置后: input={inp.input_value()!r}  组件 value={host.get_attribute('value')!r}")

    st = pg.evaluate("""() => {
        const r = document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const b = document.querySelector('[data-testid="budget-index-sC4ibw"]');
        const sw = document.querySelector('.promotion-days-switch-label');
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        return {roi: r?r.getAttribute('value'):null, budget: b?b.getAttribute('value'):null,
                promoDays: sw?(sw.className||'').includes('checked'):null, selected: m?m[1]:null};
    }""")
    print(json.dumps(st, ensure_ascii=False))
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_roi2.png")
    b.close()
