#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    print("=== iframe ===", pg.evaluate("() => document.querySelectorAll('iframe').length"))
    print("=== body 直接子元素 ===")
    print(json.dumps(pg.evaluate("""() => [...document.body.children].map(e => ({
        tag: e.tagName, id: e.id, cls: (e.className||'').toString().slice(0,60),
        kids: e.children.length, h: Math.round(e.getBoundingClientRect().height)}))"""), ensure_ascii=False, indent=1)[:1200])

    # 点击后截图
    loc = pg.locator("span:text-is('添加商品')")
    print(f"\nspan 精确匹配数: {loc.count()}")
    if loc.count():
        el = loc.first
        el.click(timeout=8000)
        print("已点击")
        time.sleep(5)
    pg.screenshot(path="notes/hub_after_add.png", full_page=False)
    print("截图: notes/hub_after_add.png")
    print("\n=== 点击后 body 子元素 ===")
    print(json.dumps(pg.evaluate("""() => [...document.body.children].map(e => ({
        tag: e.tagName, id: e.id, cls: (e.className||'').toString().slice(0,60),
        kids: e.children.length, h: Math.round(e.getBoundingClientRect().height)}))"""), ensure_ascii=False, indent=1)[:1200])
    # 文本变化
    txt = pg.evaluate("() => document.body.innerText")
    i = txt.find("添加商品")
    print("\n=== '添加商品' 附近 ===")
    print(txt[max(0,i-100):i+500])
    b.close()
