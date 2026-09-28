#!/usr/bin/env python3
"""下载 mf_finance 微前端本体 + 递归展开它的 chunk（deposit / bills / transactions 全在这）。

mf_finance 是 garfish/atlas 微前端，入口：
  //lf16-oversea.goofy-cdn.com/obj/goofy-sg/gftar/i18n/ecom/shop/mf_finance/<ver>/TTS/unihan/mf_finance.js
它内部再按 chunk 懒加载，chunk 引用有三种写法（Vite/webpack 混用）：
  import("./x.js")              webpack 具名 chunk
  "./x.abcdef12.js"             hash 后缀
  "/obj/.../js/x.js"            绝对路径
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
JS = HERE / "notes" / "fin_mf"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.7559.230 Safari/537.36")
ENTRY = ("https://lf16-oversea.goofy-cdn.com/obj/goofy-sg/gftar/i18n/ecom/shop/"
         "mf_finance/1.0.0.4610/TTS/unihan/mf_finance.js")
# 同目录相对引用
REF_REL = re.compile(r'["\']\./([A-Za-z0-9_~.\-]+\.js)["\']')
REF_ABS = re.compile(r'["\'](https?://[^"\']+?\.js)["\']')
REF_PATH = re.compile(r'["\']((?:/obj/)?[A-Za-z0-9_/.~\-]*?(?:js|chunks?)/[A-Za-z0-9_.~\-]+\.js)["\']')


def cookies(port=CDP_PORT) -> str:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        return "; ".join(f"{c['name']}={c['value']}" for c in b.contexts[0].cookies()
                         if "tiktokshopglobalselling.com" in c.get("domain", ""))


def get(url: str, ck: str) -> bytes:
    return subprocess.run(["curl", "-sk", "--max-time", "60", "--compressed",
                           "-H", f"cookie: {ck}", "-H", f"user-agent: {UA}", url],
                          capture_output=True).stdout


def fname(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[-1])[-170:]


def main():
    ck = cookies()
    JS.mkdir(parents=True, exist_ok=True)
    entry_base = ENTRY.rsplit("/", 1)[0]

    queue = [ENTRY]
    seen: set[str] = set()
    manifest = []
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        dst = JS / fname(u)
        if dst.exists() and dst.stat().st_size > 0:
            data = dst.read_bytes()
        else:
            data = get(u, ck)
            if data and not data.startswith(b'{"Success":-1'):
                dst.write_bytes(data)
        manifest.append({"url": u, "file": f"notes/fin_mf/{dst.name}", "bytes": len(data)})
        print(f"  [{len(manifest):>3}] {len(data):>9,}  {u.rsplit('/',1)[-1][:70]}", flush=True)
        if not data or len(data) < 100 or data.startswith(b'{"Success":-1'):
            continue
        s = data.decode("utf-8", "replace")
        for m in REF_REL.finditer(s):
            queue.append(f"{entry_base}/{m.group(1)}")
        for m in REF_PATH.finditer(s):
            p = m.group(1)
            if p.startswith("/obj/"):
                queue.append("https://lf16-oversea.goofy-cdn.com" + p)
        for m in REF_ABS.finditer(s):
            if "goofy-cdn" in m.group(1) or "oecstatic" in m.group(1):
                queue.append(m.group(1))
        # 去掉已处理的，避免队列膨胀
        queue = [x for x in dict.fromkeys(queue) if x not in seen]

    (HERE / "notes" / "fin_mf_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    tot = sum(m["bytes"] for m in manifest)
    print(f"\n共 {len(manifest)} 个 / {tot/1e6:.1f} MB → notes/fin_mf")


if __name__ == "__main__":
    main()
