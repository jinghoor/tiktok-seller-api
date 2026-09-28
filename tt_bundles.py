#!/usr/bin/env python3
"""纯 curl 扒卖家中心 JS bundle,抽 API 路径。

CDN(lf16-scmcdn.oecstatic.com / ttwstatic.com)静态资源无鉴权,curl 直取即可。
资源清单来自页面 performance entries,先从页面导出一次。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "notes", "js")
PATHFILE = os.path.join(HERE, "notes", "product_api_paths.json")
os.makedirs(OUT, exist_ok=True)

PATTERNS = [
    # /api/v1/product/...  /api/v2/seller/...  /api/v3/...
    re.compile(r"""["'`](?P<p>/api/v[0-9]/[A-Za-z0-9_\-/]{3,90})["'`]"""),
    # 模板拼接:/api/v1/product/${id}/list
    re.compile(r"""["'`](?P<p>/api/v[0-9]/[A-Za-z0-9_\-/]*\$\{[^}]{1,40}\}[A-Za-z0-9_\-/]*)["'`]"""),
    # oec_ads / oec_ 系列
    re.compile(r"""["'`](?P<p>/oec_[a-z0-9_]+/v[0-9]/[A-Za-z0-9_\-/]{3,90})["'`]"""),
    # 不带版本号的: /api/product/... /api/seller/...
    re.compile(r"""["'`](?P<p>/api/[A-Za-z0-9_\-]+/[A-Za-z0-9_\-/]{4,80})["'`]"""),
    # /product/api/... 或者相对拼接起点 "/product/"
    re.compile(r"""["'`](?P<p>/[a-z][a-z0-9_]+/v[0-9]/[A-Za-z0-9_\-/]{4,80})["'`]"""),
]


def extract(text: str) -> set[str]:
    hits: set[str] = set()
    for rex in PATTERNS:
        for m in rex.finditer(text):
            p = m.group("p")
            if len(p) < 150 and ".." not in p:
                hits.add(p)
    return hits


def curl(url: str, dest: str) -> tuple[str, bool, int]:
    r = subprocess.run(
        ["curl", "-sSL", "--compressed", "-m", "60",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
         "-H", "Referer: https://seller-vn.tiktok.com/",
         "-o", dest, "-w", "%{http_code}", url],
        capture_output=True, text=True)
    code = r.stdout.strip()
    ok = code == "200" and os.path.exists(dest) and os.path.getsize(dest) > 200
    size = os.path.getsize(dest) if os.path.exists(dest) else 0
    return url, ok, size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", default=None, help="资源清单 JSON 文件(URL 数组)")
    ap.add_argument("--glob", default=None, help="按子串过滤 URL")
    ap.add_argument("--max", type=int, default=400)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--filter", nargs="*", default=["product", "sku", "category", "image",
                                                   "brand", "logistic", "package", "warehouse",
                                                   "spec", "attribute", "draft", "listing",
                                                   "publish", "create", "edit", "stock",
                                                   "price", "variant"])
    a = ap.parse_args()

    if not a.list:
        print("需要 --list notes/resources.json (先跑 tt_scrape.py listres 导出)", file=sys.stderr)
        return 2
    urls = json.load(open(a.list))
    if isinstance(urls, dict):
        urls = urls.get("urls") or []
    if a.glob:
        urls = [u for u in urls if a.glob in u]
    urls = list(dict.fromkeys(urls))[:a.max]
    print(f"待下载 {len(urls)} 个 JS")

    store: dict[str, str] = {}
    fails = 0
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {}
        for u in urls:
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("?")[0].split("/")[-1])[:80]
            prefix = re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/obj/")[-1].rsplit("/", 1)[0])[:60] if "/obj/" in u else "root"
            d = os.path.join(OUT, prefix)
            os.makedirs(d, exist_ok=True)
            futs[ex.submit(curl, u, os.path.join(d, name))] = (u, os.path.join(d, name))
        done = 0
        for f in cf.as_completed(futs):
            u, dest = futs[f]
            done += 1
            try:
                _, ok, size = f.result()
            except Exception:
                ok, size = False, 0
            if ok:
                store[u] = dest
            else:
                fails += 1
            if done % 25 == 0:
                print(f"  {done}/{len(urls)}  ok={len(store)} fail={fails}")

    print(f"\n下载成功 {len(store)}/{len(urls)} (fail={fails})")
    allpaths: set[str] = set()
    for u, dest in store.items():
        try:
            with open(dest, encoding="utf-8", errors="replace") as f:
                allpaths |= extract(f.read())
        except OSError:
            pass

    filtered = sorted(q for q in allpaths if any(k in q.lower() for k in a.filter))
    json.dump({"count": len(allpaths), "all": sorted(allpaths), "filtered": filtered},
              open(PATHFILE, "w"), ensure_ascii=False, indent=2)
    print(f"\n抽出候选路径 {len(allpaths)},命中关键词 {len(filtered)} → {PATHFILE}")
    print("\n=== 命中关键词的路径 ===")
    for q in filtered:
        print("   ", q)
    print("\n=== 全部路径(去重排序) ===")
    for q in sorted(allpaths):
        print("   ", q)
    return 0


if __name__ == "__main__":
    sys.exit(main())
