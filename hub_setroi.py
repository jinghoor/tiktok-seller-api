#!/usr/bin/env python3
"""设 ROI。"""
import sys, time, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
ROI  = sys.argv[2] if len(sys.argv) > 2 else "14"
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    host = pg.locator('[data-testid="bid-select-index-9egWxE"]')
    inp  = pg.locator('[data-testid="bid-select-index-9egWxE"] input')
    print(f"设置前: input={inp.input_value()!r}  组件 value={host.get_attribute('value')!r}")

    inp.click(timeout=15000)
    time.sleep(0.5)
    pg.keyboard.press("Meta+A")
    pg.keyboard.press("Control+A")
    time.sleep(0.2)
    pg.keyboard.press("Backspace")
    time.sleep(0.3)
    inp.type(ROI, delay=80)
    time.sleep(0.8)
    pg.keyboard.press("Tab")
    time.sleep(2)

    print(f"设置后: input={inp.input_value()!r}  组件 value={host.get_attribute('value')!r}")
    st = pg.evaluate("""() => {
        const roi = document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const bud = document.querySelector('[data-testid="budget-index-sC4ibw"]');
        const sw  = document.querySelector('.promotion-days-switch-label');
        const radios = [...document.querySelectorAll('input[type=radio]')].filter(r=>r.checked).map(r=>r.value);
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        return {roi: roi?roi.getAttribute('value'):null, budget: bud?bud.getAttribute('value'):null,
                promoDays: sw ? (sw.className||'').includes('checked') : null,
                radios, selectedProducts: m?m[1]:null,
                name: (document.querySelector('input[placeholder*="广告计划名称"]')||{}).value || null};
    }""")
    print(json.dumps(st, ensure_ascii=False, indent=1))
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_roi.png")
    print("截图: notes/hub_roi.png")
    b.close()
