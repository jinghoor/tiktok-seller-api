#!/usr/bin/env python3
"""查 dashboard 上的广告计划列表。"""
import json, re, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)
    if "/dashboard" not in pg.url:
        pg.goto("https://seller-vn.tiktok.com/ads-creation/dashboard", wait_until="domcontentloaded")
        pg.wait_for_timeout(6000)
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    rows = pg.evaluate("""() => {
        const out=[];
        for (const tr of document.querySelectorAll('tr')) {
            const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
            if (/商品 GMV Max/.test(t)) out.push(t.slice(0,240));
        }
        return out;
    }""")
    print(f"广告计划行数: {len(rows)}")
    for r in rows:
        # 抽关键字段
        m = re.search(r'(商品 GMV Max[^ ]*[^|]*?)(?= 数据分析| 修改|$)', r)
        roi = re.search(r'(\d+\.\d{2})\s*\|', r)
        print(f"  {r[:150]}")
        print()
    b.close()
