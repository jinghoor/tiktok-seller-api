#!/usr/bin/env python3
"""点【创建 GMV Max 广告】并侦察进入后的页面。"""
from __future__ import annotations
import json, sys, time
from playwright.sync_api import sync_playwright

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    ctx = b.contexts[0]
    pages_before = list(ctx.pages)
    print(f"点击前页面数: {len(pages_before)}")
    for pg in pages_before: print(f"  {pg.url[:100]}")

    pg = next((x for x in pages_before if "tiktok" in x.url), None)
    if not pg:
        print("找不到 TikTok 页面"); sys.exit(1)

    # 找按钮并点击
    btn = pg.query_selector("button:has-text('创建 GMV Max 广告')")
    if not btn:
        # 退一步:用文本匹配
        els = pg.query_selector_all("button")
        for e in els:
            t = (e.inner_text() or "").strip()
            if "创建 GMV Max" in t: btn = e; break
    if not btn:
        print("找不到按钮"); sys.exit(1)
    print(f"找到按钮: {btn.inner_text().strip()!r}")
    btn.click()
    print("已点击,等待新页面/弹层…")
    time.sleep(6)

    pages_after = list(ctx.pages)
    print(f"\n点击后页面数: {len(pages_after)}")
    newpages = [x for x in pages_after if x not in pages_before]
    print(f"新开页面: {len(newpages)}")
    for x in newpages:
        print(f"  NEW: {x.url[:140]}")
    print("\n全部页面:")
    for x in pages_after:
        print(f"  {x.url[:120]}")

    # 取最活跃的页面(新开的或原页面)
    target = newpages[0] if newpages else pg
    try:
        target.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception: pass
    time.sleep(3)
    print(f"\n=== 目标页 {target.url[:110]} ===")
    txt = target.evaluate("() => document.body ? document.body.innerText : ''")
    print("页面文本(前 2500 字):")
    print(txt[:2500])
    b.close()
