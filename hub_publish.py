#!/usr/bin/env python3
"""提交当前广告计划。"""
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 提交前最终状态
    st = pg.evaluate("""() => {
        const s  = document.querySelector('[data-testid="promotion-days-toggle-3EnDzt"]');
        const roi= document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const bud= document.querySelector('[data-testid="budget-index-sC4ibw"]');
        const txt= document.body.innerText;
        const m  = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        const nm = document.querySelector('input[placeholder*="广告计划名称"]');
        return {promo: s?s.getAttribute('aria-checked'):null, roi: roi?roi.getAttribute('value'):null,
                budget: bud?bud.getAttribute('value'):null, selected: m?m[1]:null,
                name: nm?nm.value:null};
    }""")
    print("=== 提交前 ===")
    print(json.dumps(st, ensure_ascii=False, indent=1))

    # 点【发布】—— 用真实鼠标
    loc = pg.get_by_text("发布", exact=True)
    n = loc.count()
    print(f"\n'发布' 匹配 {n} 个")
    tgt = None
    for i in range(n):
        el = loc.nth(i)
        try:
            box = el.bounding_box()
            if box and box["width"] > 20:
                print(f"  [{i}] box={box}")
                if tgt is None: tgt = el
        except Exception: pass
    if not tgt:
        print("找不到发布按钮"); sys.exit(1)

    tgt.click(timeout=12000)
    print("已点【发布】,等待提交结果…")
    for i in range(10):
        time.sleep(3)
        cur = pg.url
        txt = pg.evaluate("() => document.body.innerText")
        done = ("已提交" in txt or "创建成功" in txt or "发布成功" in txt
                or "dashboard" in cur or "campaign" in cur)
        print(f"  [{(i+1)*3}s] url={cur[:90]}")
        if done:
            print("  → 疑似完成")
            break
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_published.png")
    print("截图: notes/hub_published.png")
    txt = pg.evaluate("() => document.body.innerText")
    print("\n=== 提交后页面文本(前 800) ===")
    print(txt[:800])
    b.close()
