#!/usr/bin/env python3
"""打开商品选择弹窗并列出商品。"""
from __future__ import annotations
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)

    # 点【添加商品】
    clicked = pg.evaluate("""() => {
        for (const e of document.querySelectorAll('button, [role=button], a, div')) {
            const t=(e.innerText||'').trim();
            if (t === '添加商品') { e.click(); return t; }
        }
        return null;
    }""")
    print(f"点击: {clicked!r}")
    if not clicked: sys.exit(1)
    time.sleep(6)

    # 弹窗信息
    d = pg.evaluate("""() => {
        let dlg = null;
        for (const sel of ['[role=dialog]', '.theme-arco-modal', '[class*="modal-content"]', '[class*="drawer"]']) {
            const el = document.querySelector(sel);
            if (el && el.getBoundingClientRect().width > 200) { dlg = el; break; }
        }
        if (!dlg) return {err:'no dialog'};
        const rows = [];
        // 表格行
        for (const tr of dlg.querySelectorAll('tr, [role=row], [class*="table-row"], [class*="TableRow"]')) {
            const t = (tr.innerText||'').trim().replace(/\\s+/g,' ');
            if (t && t.length < 220) rows.push(t);
        }
        const cbs = dlg.querySelectorAll('input[type=checkbox]').length;
        const btns = [];
        for (const e of dlg.querySelectorAll('button, [role=button]')) {
            const t=(e.innerText||'').trim();
            if (t && t.length<20) btns.push(t);
        }
        return {text: dlg.innerText.slice(0,1500), rowCount: rows.length,
                firstRows: rows.slice(0,8), checkboxes: cbs, buttons: [...new Set(btns)].slice(0,12)};
    }""")
    print(json.dumps(d, ensure_ascii=False, indent=1)[:2500])
    b.close()
