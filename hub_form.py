#!/usr/bin/env python3
"""读 GMV Max 创建页的表单控件。只读。"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    print(f"页面: {pg.url[:110]}\n")

    # 全部输入框 + 开关 + 单选
    data = pg.evaluate("""() => {
        const vis = e => { const r=e.getBoundingClientRect(); return r.width>2 && r.height>2; };
        const out = {inputs:[], switches:[], radios:[], buttons:[], texts:[]};
        for (const e of document.querySelectorAll('input, textarea')) {
            if (!vis(e)) continue;
            const r = e.getBoundingClientRect();
            out.inputs.push({type:e.type, ph:e.placeholder||'', val:e.value||'',
                x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width)});
        }
        for (const e of document.querySelectorAll('[role="switch"], .switch, [class*="switch"]')) {
            if (!vis(e)) continue;
            const r = e.getBoundingClientRect();
            const checked = e.getAttribute('aria-checked') ?? (e.className||'').includes('checked');
            out.switches.push({checked:String(checked), cls:(e.className||'').toString().slice(0,60),
                x:Math.round(r.x), y:Math.round(r.y), text:(e.innerText||'').trim().slice(0,30)});
        }
        for (const e of document.querySelectorAll('input[type=radio]')) {
            if (!vis(e)) continue;
            const r = e.getBoundingClientRect();
            const lbl = e.closest('label') || e.parentElement;
            out.radios.push({checked:e.checked, name:e.name||'',
                label:(lbl?lbl.innerText:'').trim().slice(0,40),
                x:Math.round(r.x), y:Math.round(r.y)});
        }
        for (const e of document.querySelectorAll('button, [role="button"]')) {
            if (!vis(e)) continue;
            const t=(e.innerText||'').trim().replace(/\\s+/g,' ');
            if (!t || t.length>40) continue;
            const r=e.getBoundingClientRect();
            out.buttons.push({text:t, cls:(e.className||'').toString().slice(0,50),
                x:Math.round(r.x), y:Math.round(r.y)});
        }
        return out;
    }""")

    for k in ("inputs", "switches", "radios"):
        print(f"=== {k} ({len(data[k])}) ===")
        for e in data[k]:
            print(f"  {json.dumps(e, ensure_ascii=False)}")
        print()
    print(f"=== buttons ({len(data['buttons'])}) ===")
    seen=set()
    for e in data["buttons"]:
        if e["text"] in seen: continue
        seen.add(e["text"])
        print(f"  ({e['x']:>5},{e['y']:>5}) {e['text'][:52]}")
    b.close()
