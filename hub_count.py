#!/usr/bin/env python3
import json, re, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)
    pg.goto("https://seller-vn.tiktok.com/ads-creation/dashboard", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)
    r = pg.evaluate("""() => {
        const txt = document.body.innerText;
        const m = txt.match(/共\\s*(\\d+)\\s*条/);
        const rows = [...document.querySelectorAll('tr')].filter(tr => /商品 GMV Max/.test(tr.innerText||''));
        const rois = rows.map(tr => { const m=(tr.innerText||'').match(/\\b(\\d+\\.\\d{2})\\b/g); return m?m.slice(-2):[]; });
        return {total: m?m[1]:null, pageRows: rows.length, rois: rois.slice(0,3),
                anyNon14: rows.filter(tr => !/\\b14\\.00\\b/.test(tr.innerText||'')).length,
                statuses: [...new Set(rows.map(tr => ((tr.innerText||'').match(/已生效|审核中|待定|已暂停/)||['?'])[0]))]};
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    b.close()
