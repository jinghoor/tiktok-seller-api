#!/usr/bin/env python3
"""关闭「促销日」开关。"""
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
SEL = '[data-testid="promotion-days-toggle-3EnDzt"]'
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    sw = pg.locator(SEL)
    print(f"开关数: {sw.count()}  当前 aria-checked={sw.get_attribute('aria-checked')}")
    if sw.get_attribute("aria-checked") == "true":
        sw.scroll_into_view_if_needed()
        time.sleep(0.5)
        sw.click(timeout=10000)
        time.sleep(2.5)
        print(f"点击后 aria-checked={sw.get_attribute('aria-checked')}")
        print(f"class 含 checked? {'checked' in (sw.get_attribute('class') or '')}")
    else:
        print("已经是关闭状态")

    st = pg.evaluate("""() => {
        const s = document.querySelector('[data-testid="promotion-days-toggle-3EnDzt"]');
        const roi = document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const bud = document.querySelector('[data-testid="budget-index-sC4ibw"]');
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        const sum = txt.match(/促销日[^\\n]{0,20}/g);
        return {promoSwitch: s?s.getAttribute('aria-checked'):null,
                roi: roi?roi.getAttribute('value'):null,
                budget: bud?bud.getAttribute('value'):null,
                selected: m?m[1]:null,
                promoSummary: sum ? sum.slice(-3) : null};
    }""")
    print(json.dumps(st, ensure_ascii=False, indent=1))
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_promo_off.png")
    print("截图: notes/hub_promo_off.png")
    b.close()
