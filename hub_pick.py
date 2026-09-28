#!/usr/bin/env python3
"""在「选择商品」弹窗里勾选商品并确认。"""
import sys, json, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
IDX  = int(sys.argv[2]) if len(sys.argv) > 2 else 0     # 选第几个
COUNT= int(sys.argv[3]) if len(sys.argv) > 3 else 1     # 选几个

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 确认弹窗在
    if not pg.locator("text='选择商品'").count():
        print("弹窗不在 —— 需要先点【添加商品】"); sys.exit(1)
    print("弹窗已在")

    # 商品行 checkbox:排除表头(全选)
    boxes = pg.locator("input[type=checkbox]")
    n = boxes.count()
    print(f"checkbox 总数: {n}")
    info = []
    for i in range(n):
        el = boxes.nth(i)
        try:
            box = el.bounding_box()
            info.append((i, box))
        except Exception:
            info.append((i, None))
    visible = [(i, bx) for i, bx in info if bx]
    print(f"可见 checkbox: {len(visible)}")

    # 勾选:第 0 个通常是表头全选,商品行从第 1 个开始
    start = 1 if len(visible) > 1 else 0
    picked = 0
    for k in range(COUNT):
        idx, bx = visible[start + IDX + k]
        # 点它的外层 label / 用真实鼠标
        el = boxes.nth(idx)
        el.scroll_into_view_if_needed()
        time.sleep(0.3)
        try:
            el.click(timeout=5000)
        except Exception:
            pg.mouse.click(bx["x"] + bx["width"]/2, bx["y"] + bx["height"]/2)
        time.sleep(0.6)
        picked += 1
        print(f"  勾选第 {picked} 个 (checkbox idx={idx})")

    time.sleep(2)
    # 读底部已选数量
    txt = pg.evaluate("() => document.body.innerText")
    import re
    m = re.search(r"已选择\s*(\d+)\s*件商品", txt)
    print(f"底部显示: 已选择 {m.group(1) if m else '?'} 件商品")

    # 点【确认】
    ok = pg.evaluate("""() => {
        for (const e of document.querySelectorAll('button, [role=button]')) {
            const t=(e.innerText||'').trim();
            if (t === '确认') {
                if (e.disabled || (e.getAttribute('aria-disabled')==='true')) return 'disabled';
                e.click(); return 'clicked';
            }
        }
        return 'not-found';
    }""")
    print(f"确认按钮: {ok}")
    time.sleep(6)

    # 弹窗是否关闭 + 商品是否进来了
    still = pg.locator("text='选择商品'").count()
    txt = pg.evaluate("() => document.body.innerText")
    m2 = re.search(r"清单中的商品：\s*(\d+)|取消选择|个商品", txt)
    print(f"\n弹窗还在? {still>0}")
    i = txt.find("选定商品")
    print("--- 商品区 ---")
    print(txt[max(0,i-100):i+400])
    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_picked.png")
    print("\n截图: notes/hub_picked.png")
    b.close()
