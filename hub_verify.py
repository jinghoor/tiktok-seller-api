#!/usr/bin/env python3
"""验证广告计划是否创建成功。"""
import json, sys, time, re
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next((x for c in b.contexts for x in c.pages if "ads-creation" in x.url), None)
    print(f"当前页: {pg.url[:110]}\n")
    pg.wait_for_timeout(3000)
    txt = pg.evaluate("() => document.body.innerText")
    # 找广告计划列表区
    for kw in ["广告计划", "推广系列", "GMV Max", "商品 GMV Max", "审核", "投放中", "预算"]:
        i = txt.find(kw)
        if i >= 0:
            print(f"--- {kw} @ {i} ---")
            print("  " + txt[max(0,i-80):i+400].replace("\n", " | "))
            print()
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_dash.png", full_page=False)
    print("截图: notes/hub_dash.png")
    b.close()
