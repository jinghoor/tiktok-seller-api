#!/usr/bin/env python3
import json, sys, time
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    pg = next(x for c in b.contexts for x in c.pages if "/ads-creation/creation" in x.url)
    frames = pg.frames
    print(f"=== frame 总数 {len(frames)} ===")
    for f in frames:
        try:
            print(f"  name={f.name!r} url={f.url[:100]}")
            print(f"      body 长度={len(f.evaluate('() => document.body ? document.body.innerText.length : 0'))}")
        except Exception as e:
            print(f"  name={f.name!r} url={f.url[:80]}  (err {str(e)[:50]})")
    b.close()
