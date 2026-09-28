#!/usr/bin/env python3
"""列出可选商品(含过滤条件),用于规划循环。"""
import json, sys, time, re
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next((x for c in b.contexts for x in c.pages if "ads-creation" in x.url), None)

    # 关键:看每个商品的「优惠资格」列 —— 已投放的商品会被排除
    rows = pg.evaluate("""() => {
        const out = [];
        for (const tr of document.querySelectorAll('tr')) {
            const t = (tr.innerText||'').trim().replace(/\\s+/g,' ');
            const idm = t.match(/ID:\\s*(\\d{15,25})/);
            if (!idm) continue;
            out.push({id: idm[1], text: t.slice(0,220), cells: [...tr.querySelectorAll('td')].map(td=>(td.innerText||'').trim().replace(/\\s+/g,' ').slice(0,40))});
        }
        return out;
    }""")
    print(f"列表中的商品行: {len(rows)}")
    for r_ in rows[:25]:
        print(f"  {r_['id']}  cells={r_['cells'][-3:]}")
    b.close()
