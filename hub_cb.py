#!/usr/bin/env python3
"""搞清 checkbox 与产品的对应关系。"""
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    r = pg.evaluate("""() => {
        const out = [];
        const boxes = [...document.querySelectorAll('input[type=checkbox]')];
        boxes.forEach((cb, i) => {
            const rc = cb.getBoundingClientRect();
            const row = cb.closest('tr') || cb.closest('[role=row]') || cb.closest('[class*="row"]') || cb.parentElement;
            const rowText = row ? (row.innerText||'').trim().replace(/\\s+/g,' ').slice(0,90) : '';
            out.push({i, checked: cb.checked, vis: rc.width>2,
                x: Math.round(rc.x), y: Math.round(rc.y),
                isHeader: !rowText || /商品名称/.test(rowText),
                row: rowText});
        });
        return out;
    }""")
    print(f"checkbox 共 {len(r)}")
    for e in r[:25]:
        mark = "✓" if e["checked"] else " "
        hdr = " [表头/全选]" if e["isHeader"] else ""
        print(f"  [{mark}] #{e['i']:>2} vis={e['vis']}{hdr}  {e['row'][:76]}")
    b.close()
