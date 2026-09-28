#!/usr/bin/env python3
"""取消全选 → 只勾 1 个商品 → 确认。"""
import sys, json, time, re
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
WANT = int(sys.argv[2]) if len(sys.argv) > 2 else 1   # 想选几个

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 1) 表头全选 checkbox:点它取消全部
    st = pg.evaluate("""() => {
        const boxes=[...document.querySelectorAll('input[type=checkbox]')];
        // 找 checked 的、且其行文本含「商品名称」的 = 表头
        for (const cb of boxes) {
            const row = cb.closest('tr') || cb.closest('[role=row]') || cb.parentElement;
            const t = row ? (row.innerText||'') : '';
            if (cb.checked && /商品名称/.test(t)) { cb.click(); return 'header-unclicked'; }
        }
        return 'header-not-found';
    }""")
    print(f"取消全选: {st}")
    time.sleep(2)
    txt = pg.evaluate("() => document.body.innerText")
    m = re.search(r"已选择\s*(\d+)\s*件商品", txt)
    print(f"  现在: {m.group(0) if m else '?'}")

    # 2) 勾选前 WANT 个商品行(排除表头)
    picked = pg.evaluate("""(want) => {
        const boxes=[...document.querySelectorAll('input[type=checkbox]')];
        let n=0;
        for (const cb of boxes) {
            const row = cb.closest('tr') || cb.closest('[role=row]') || cb.parentElement;
            const t = row ? (row.innerText||'') : '';
            if (/商品名称/.test(t)) continue;          // 跳过表头
            if (!/ID:\\s*\\d+/.test(t)) continue;        // 只要真正的商品行
            if (cb.checked) continue;
            cb.click();
            n++;
            if (n >= want) break;
        }
        return n;
    }""", WANT)
    print(f"勾选商品数: {picked}")
    time.sleep(2)
    txt = pg.evaluate("() => document.body.innerText")
    m = re.search(r"已选择\s*(\d+)\s*件商品", txt)
    print(f"  现在: {m.group(0) if m else '?'}")

    # 3) 列出当前 checked 的商品行,确认只有一个
    rows = pg.evaluate("""() => {
        const out=[];
        for (const cb of document.querySelectorAll('input[type=checkbox]')) {
            if (!cb.checked) continue;
            const row = cb.closest('tr') || cb.closest('[role=row]') || cb.parentElement;
            const t = row ? (row.innerText||'').trim().replace(/\\s+/g,' ') : '';
            const idm = t.match(/ID:\\s*(\\d+)/);
            out.push({id: idm?idm[1]:null, head: t.slice(0,60)});
        }
        return out;
    }""")
    print("勾选中的行:")
    for r_ in rows: print(f"   id={r_['id']}  {r_['head'][:58]}")

    pg.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/hub_one.png")
    print("截图: notes/hub_one.png  (未点确认)")
    b.close()
