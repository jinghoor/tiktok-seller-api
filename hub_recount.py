#!/usr/bin/env python3
"""进入创建页 → 选定商品 → 打开选择器 → 数剩余可选商品。"""
import json, sys, time, re
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)

    # 1) 点「创建 GMV Max 广告」
    pg.get_by_role("button", name=re.compile("创建 GMV Max 广告")).click(timeout=15000)
    time.sleep(6)
    print(f"进入: {pg.url[:100]}")

    # 2) 选「选定商品」
    ok = pg.evaluate("""() => {
        const r = document.querySelector('input[type=radio][value="specific"]');
        if (!r) return false;
        (r.closest('label') || r.parentElement || r).click();
        return true;
    }""")
    print(f"选「选定商品」: {ok}")
    time.sleep(3)

    # 3) 点「添加商品」
    loc = pg.get_by_text("添加商品", exact=True)
    print(f"'添加商品' 匹配: {loc.count()}")
    if loc.count():
        loc.last.click(timeout=12000)
    time.sleep(6)

    # 4) 数商品
    r = pg.evaluate("""() => {
        const rows = [];
        for (const tr of document.querySelectorAll('tr')) {
            const t = (tr.innerText||'').trim().replace(/\\s+/g,' ');
            const idm = t.match(/ID:\\s*(\\d{15,25})/);
            if (idm) rows.push({id: idm[1], title: t.slice(0,70)});
        }
        const txt = document.body.innerText;
        const m = txt.match(/已选择\\s*(\\d+)\\s*件商品/);
        return {rowCount: rows.length, rows, selected: m?m[1]:null,
                drawerOpen: !!document.querySelector('[data-testid="product-select-index-6KM6mN"]')};
    }""")
    print(f"\n可选商品行数: {r['rowCount']}   已选: {r['selected']}   抽屉: {r['drawerOpen']}")
    for x in r["rows"]:
        print(f"  {x['id']}  {x['title'][:60]}")
    b.close()
