#!/usr/bin/env python3
"""抓商品列表接口:从进入创建页就记录。"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE = Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT

REC = open(HERE / "hub_capture.py", encoding="utf-8").read()
m = re.search(r'RECORDER = r"""(.*?)"""', REC, re.S)
RECORDER = m.group(1)

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)
    pg.goto("https://seller-vn.tiktok.com/ads-creation/creation", wait_until="domcontentloaded")
    pg.wait_for_timeout(4000)
    print("记录器:", pg.evaluate(RECORDER))
    pg.wait_for_timeout(3000)

    # 触发商品列表加载
    pg.evaluate("""() => { const r=document.querySelector('input[type=radio][value="specific"]');
        if(r)(r.closest('label')||r.parentElement||r).click(); }""")
    pg.wait_for_timeout(3000)
    pg.get_by_text("添加商品", exact=True).last.click(timeout=15000)
    pg.wait_for_timeout(8000)

    rec = json.loads(pg.evaluate("() => JSON.stringify(window.__rec || [])"))
    print(f"捕获 {len(rec)} 个请求")
    # 找响应里含 spu_id / product 的
    hits = []
    for r in rec:
        resp = r.get("response") or ""
        if ("spu_id" in resp or "product_id" in resp) and len(resp) > 200:
            hits.append(r)
    print(f"\n=== 含商品数据的请求: {len(hits)} ===")
    for r in hits:
        print(f"\n  {r.get('method')} {r.get('status')} {(r.get('url') or '')[:140]}")
        print(f"     body: {(r.get('body') or 'null')[:300]}")
        print(f"     resp: {(r.get('response') or '')[:400]}")
    out = HERE / "notes" / "tiktok_product_list_api.json"
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n全部请求已存 {out}")
    b.close()
