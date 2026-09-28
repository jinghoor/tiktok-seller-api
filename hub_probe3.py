#!/usr/bin/env python3
import sys, json
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    r = pg.evaluate("""() => {
        const res = {};
        for (const tid of ['bid-select-index-9egWxE','budget-index-sC4ibw']) {
            const host = document.querySelector(`[data-testid="${tid}"]`);
            if (!host) { res[tid] = 'not found'; continue; }
            const info = {tag: host.tagName.toLowerCase(), attrs: {}};
            for (const a of host.attributes) info.attrs[a.name] = a.value.slice(0,80);
            // 逐层进 shadow DOM 找 input
            let node = host, depth = 0, path = [];
            while (node && depth < 6) {
                const sr = node.shadowRoot;
                if (!sr) break;
                path.push(node.tagName.toLowerCase());
                const inp = sr.querySelector('input');
                if (inp) {
                    info.foundInput = {
                        type: inp.type, value: inp.value, step: inp.step,
                        cls: (inp.className||'').toString().slice(0,60),
                        path: path.join(' > ')
                    };
                    break;
                }
                node = sr.querySelector('x-input, [x-name]') || sr.firstElementChild;
                depth++;
            }
            if (!info.foundInput) info.path = path.join(' > ');
            res[tid] = info;
        }
        return res;
    }""")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    b.close()
