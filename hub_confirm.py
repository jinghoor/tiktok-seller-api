#!/usr/bin/env python3
"""确认商品选择 → 设 ROI → 校验 → (可选)发布。"""
import sys, json, time, re
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
ROI  = sys.argv[2] if len(sys.argv) > 2 else "14"
DO_PUBLISH = "--publish" in sys.argv

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 1) 点确认
    r = pg.evaluate("""() => {
        for (const e of document.querySelectorAll('button, [role=button]')) {
            if ((e.innerText||'').trim() === '确认') { 
                if (e.disabled) return 'disabled';
                e.click(); return 'clicked';
            }
        }
        return 'not-found';
    }""")
    print(f"点【确认】: {r}")
    time.sleep(5)

    # 2) 校验商品是否进主表单(且只有 1 个)
    st = pg.evaluate("""() => {
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        const ids = [...txt.matchAll(/ID:\\s*(\\d{15,25})/g)].map(x=>x[1]);
        return {selected: m?m[1]:null, ids: ids.slice(0,20), idCount: ids.length};
    }""")
    print(f"主表单商品: selected={st['selected']} idCount={st['idCount']} ids={st['ids']}")

    # 3) 设 ROI
    host = pg.locator('[data-testid="bid-select-index-9egWxE"]')
    print(f"ROI 组件数: {host.count()}")
    inp = pg.locator('[data-testid="bid-select-index-9egWxE"] input')
    before = inp.input_value()
    print(f"ROI 设置前: {before!r}")
    inp.click()
    pg.keyboard.press("Meta+A"); pg.keyboard.press("Control+A")
    pg.keyboard.press("Backspace")
    inp.type(ROI, delay=60)
    pg.keyboard.press("Tab")
    time.sleep(2)
    after = inp.input_value()
    comp = host.get_attribute("value")
    print(f"ROI 设置后: input={after!r}  组件 value={comp!r}")

    # 4) 汇总当前全部关键设置
    st2 = pg.evaluate("""() => {
        const out = {};
        const radios = [...document.querySelectorAll('input[type=radio]')].filter(r=>r.checked).map(r=>r.value);
        out.checkedRadios = radios;
        const roi = document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const bud = document.querySelector('[data-testid="budget-index-sC4ibw"]');
        out.roi = roi ? roi.getAttribute('value') : null;
        out.budget = bud ? bud.getAttribute('value') : null;
        const sw = document.querySelector('.promotion-days-switch-label');
        out.promotionDaysChecked = sw ? (sw.className||'').includes('checked') : null;
        // 促销日开关的 aria
        for (const e of document.querySelectorAll('[role=switch]')) {
            const lbl = e.getAttribute('aria-label')||'';
            if (/促销日/.test(lbl)) out.promotionSwitchAria = e.getAttribute('aria-checked');
        }
        const nm = document.querySelector('input[placeholder*="广告计划名称"]');
        out.name = nm ? nm.value : null;
        out.hasPublishBtn = !!([...document.querySelectorAll('button')].find(e=>(e.innerText||'').trim()==='发布'));
        return out;
    }""")
    print("\n=== 当前设置 ===")
    print(json.dumps(st2, ensure_ascii=False, indent=1))
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_ready.png")
    print("截图: notes/hub_ready.png")
    b.close()
