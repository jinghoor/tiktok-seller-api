#!/usr/bin/env python3
"""把财务微前端的懒加载 chunk 全部展开下载。

财务这套是 Vite 构建：
  - entry:  i18n/ecom/finance_overview/entry/finance_overview.<hash>.js
  - 代码:   i18n/ecom/finance_overview/js/elyrmlej.js（3.8MB，含全部业务代码）
  - 懒加载: 同目录 import("./<8位id>.js")，还有具名 chunk（useFbt.bva535ks.js 等）
  - 没有 sourcemap（.map 一律 404）

所以必须把 `import("./X.js")` 全抓出来递归下完，否则接口抽不全。
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
JS = ROOT / "notes" / "fin_js"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.7559.230 Safari/537.36")

# import("./x.js") / from"./x.js" / import("../js/x.js") / "js/x.js"
# ★ 两种命名都要覆盖：
#   具名 + hash:  payoutCycleSetting.k7hkdehg.js
#   匿名 id 即名: b5xeyaup.js   ← 只差一个点，早期正则漏了这种，导致 chunk 展开不全
REF = re.compile(r'["\'](\.\.?/)?([A-Za-z0-9_~.\-]+\.js)["\']')
# 还有不带 hash 的具名 chunk：import("./common.internal.js")
REF2 = re.compile(r'["\'](\.\.?/)?([A-Za-z0-9_~.\-]+?\.(?:internal|external)\.js)["\']')


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


def main():
    ck = cookies()
    bases = [
        "https://lf-gs-frontend-cn.fanchenstatic.com/obj/she-op-static/i18n/ecom/finance_overview/js",
        "https://lf-gs-frontend-cn.fanchenstatic.com/obj/she-op-static/i18n/ecom/bill-payment/js",
    ]
    have = {p.name for p in JS.glob("*")}
    print(f"已有 {len(have)} 个文件")

    # 从已有文件收集引用
    refs: set[str] = set()
    for f in JS.glob("*"):
        if f.stat().st_size < 300:
            continue
        s = f.read_text(encoding="utf-8", errors="replace")
        for m in REF.finditer(s):
            refs.add(m.group(2))
        for m in REF2.finditer(s):
            refs.add(m.group(2))
    print(f"发现 chunk 引用 {len(refs)} 个（去重）")

    todo = []
    for base in bases:
        tag = "finance_overview" if "finance_overview" in base else "bill-payment"
        for r in sorted(refs):
            name = f"lf-gs-frontend-cn.fanchenstatic.com_obj_she-op-static_i18n_ecom_{tag}_js_{r}"
            if name not in have:
                todo.append((f"{base}/{r}", name))
    print(f"待下载 {len(todo)} 个\n")

    ok = fail = 0
    for i, (url, name) in enumerate(todo):
        data = get(url, ck)
        if data and len(data) > 60 and not data.startswith(b'{"Success":-1'):
            (JS / name).write_bytes(data)
            ok += 1
            print(f"  [{i+1}/{len(todo)}] {len(data):>9,}  {name[-60:]}")
        else:
            fail += 1
    print(f"\n新增 {ok} 个，失败 {fail} 个")
    files = [p for p in JS.glob("*") if p.is_file()]
    print(f"notes/fin_js 共 {len(files)} 个 / {sum(p.stat().st_size for p in files)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
