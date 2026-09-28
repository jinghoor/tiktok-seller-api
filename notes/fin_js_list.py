#!/usr/bin/env python3
"""抓 seller 中心【财务】板块全部前端资源 → notes/fin_js/

1. 读浏览器实时 cookie（只读 CDP，不动标签页）
2. 直连拉 3 个财务页 HTML（**不走本地代理**，走代理会超时）
3. 从 HTML 抽 JS URL + 微前端 registry
4. 下载所有 JS，并顺着 Vite 的 chunk 映射继续展开懒加载 chunk

输出 notes/fin_urls.json / notes/fin_js_manifest.json
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
JS_DIR = HERE / "fin_js"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.7559.230 Safari/537.36")

PAGES = {
    "bills": "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview&shop_region=VN",
    "deposit": "https://seller.tiktokshopglobalselling.com/deposit?shop_region=VN",
    "bill-payment": "https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN",
}


def browser_cookies(port: int = CDP_PORT) -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        cks = [c for c in b.contexts[0].cookies()
               if "tiktokshopglobalselling.com" in c.get("domain", "")]
        return "; ".join(f"{c['name']}={c['value']}" for c in cks)


def fetch(url: str, cookie: str, *, binary: bool = False):
    args = ["curl", "-sk", "--max-time", "60", "--compressed",
            "-H", f"cookie: {cookie}", "-H", f"user-agent: {UA}",
            "-H", "accept: */*", url]
    r = subprocess.run(args, capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def main():
    cookie = browser_cookies()
    print(f"cookie 长度 {len(cookie)}")
    all_js: dict[str, set] = {}
    htmls = {}
    for name, url in PAGES.items():
        html = fetch(url, cookie)
        htmls[name] = html
        (HERE / f"fin_{name}.html").write_text(html, encoding="utf-8")
        urls = set(re.findall(r'https://[^"\'\s\\<>]+?\.js(?:\?[^"\'\s<>]*)?', html))
        print(f"\n=== {name}  HTML {len(html):,}B  JS {len(urls)}")
        for u in sorted(urls):
            if any(k in u for k in ("finance", "deposit", "bill", "payment", "tax", "atlas")):
                all_js.setdefault(u, set()).add(name)
                print(f"    + {u[:135]}")

    # ── 下载第一层，再从 Vite chunk 映射里展开 ──
    JS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    queue = list(all_js)
    seen = set()
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        name = re.sub(r"[^A-Za-z0-9._-]", "_", u.split("//", 1)[1])[-160:]
        dst = JS_DIR / name
        if dst.exists() and dst.stat().st_size > 0:
            data = dst.read_bytes()
        else:
            data = fetch(u, cookie, binary=True)
            if data:
                dst.write_bytes(data)
        manifest.append({"url": u, "file": str(dst.relative_to(ROOT)), "bytes": len(data)})
        print(f"  [{len(manifest):>3}] {len(data):>9,}  {u.split('/')[-1][:70]}")
        if not data or len(data) < 400:
            continue
        s = data.decode("utf-8", "replace")
        # Vite 生产构建的 chunk 引用：形如 "js/xxx.hash.js" / "./xxx.hash.js"
        for m in re.finditer(r'["\'](?:\./)?((?:js/)?[A-Za-z0-9_~\-]+?\.[a-z0-9]{8}\.js)["\']', s):
            rel = m.group(1)
            base = u.rsplit("/", 1)[0]
            if rel.startswith("js/"):
                base = u.split("/js/")[0]
            cand = f"{base}/{rel}"
            if cand not in seen:
                queue.append(cand)
                all_js.setdefault(cand, set()).add("lazy")
    (HERE / "fin_urls.json").write_text(
        json.dumps({k: {"page": PAGES[k], "html": str(HERE / f'fin_{k}.html')} for k in PAGES},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "fin_js_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    tot = sum(m["bytes"] for m in manifest)
    print(f"\n共 {len(manifest)} 个 JS / {tot/1e6:.1f} MB → {JS_DIR}")


if __name__ == "__main__":
    main()
