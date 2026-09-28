#!/usr/bin/env python3
"""从卖家中心 API client bundle 里提取「方法名 → {HTTP 方法, 路径}」。

TikTok 卖家中心的 API 客户端是自动生成的,模式极规整:

  方法名(e,n){ let r=i(e); return t(`<prefix>/api/v${e.version||1}/product/xxx${r}`,
                                     {method:`GET`,headers:a},n) }

  方法名(e,n){ return t(`<prefix>/api/v${e.version||1}/product/yyy`,
                        {method:`POST`,headers:a,body:e},n) }

body 存在 ⇒ POST/PUT;query 拼 `${r}` ⇒ GET(除非显式 method)。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JSROOT = os.path.join(HERE, "notes", "js")

# 匹配一次完整的调用:前置的方法名,模板路径,后面的 options
CALL_RE = re.compile(
    r"""
    (?P<name>[A-Z][A-Za-z0-9_]*)\s*\((?P<args>[^)]{0,120})\)\s*\{
    (?P<body>.{0,600}?)
    \},
    """,
    re.X | re.S)

PATH_RE = re.compile(r"`(?P<path>[^`]*?/api/v\$\{[^}]+\}/(?P<ep>[A-Za-z0-9_/]+))"
                     r"(?P<tail>[^`]*)`")
METHOD_RE = re.compile(r"method\s*:\s*[`'\"](?P<m>[A-Za-z]+)[`'\"]")
BODY_RE = re.compile(r"body\s*:")


def parse_file(path: str) -> dict[str, dict]:
    with open(path, encoding="utf-8", errors="replace") as f:
        src = f.read()

    out: dict[str, dict] = {}
    # 逐段定位 `return t(\`...\`,` 之前的标识符作为方法名
    for m in re.finditer(r"(?P<pre>[A-Za-z0-9_,{}\s()]{0,200}?)\breturn\s+t\(`(?P<path>[^`]+)`"
                         r"\s*,\s*\{(?P<opts>[^}]{0,400})\}", src):
        pre = m.group("pre")
        names = re.findall(r"([A-Z][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{$", pre)
        if not names:
            names = re.findall(r"([A-Z][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{\s*$", pre)
        name = names[-1] if names else "?"
        raw_path = m.group("path")
        opts = m.group("opts")

        mm = METHOD_RE.search(opts)
        method = mm.group("m").upper() if mm else ("POST" if BODY_RE.search(opts) else None)

        # 归一化路径:去掉 ${...} 版本段和 ${r} query 段
        # `/api/v${e.version||1}/...` → `/api/v1/...`
        norm = re.sub(r"/v\$\{[^}]*version[^}]*\}/", "/v1/", raw_path)
        norm = norm.replace("/api/v1/", "/api/v1/")
        norm = re.sub(r"\$\{r\}", "", norm)
        norm = re.sub(r"\$\{[^}]*uriPrefix[^}]*\}", "", norm)
        norm = norm.replace("${this.uriPrefix}", "")
        # 去掉残留的 ${...}
        norm = re.sub(r"\$\{[^}]{1,60}\}", "{param}", norm)
        norm = norm.split("?")[0]

        if name == "?":
            continue
        key = f"{method or '?'} {norm}"
        if key in out and out[key]["name"] != name:
            out[key]["aliases"].append(name)
            continue
        out[key] = {
            "name": name,
            "method": method,
            "path": norm,
            "raw": raw_path,
            "has_body": bool(BODY_RE.search(opts)),
            "aliases": [],
            "file": os.path.basename(path),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=JSROOT)
    ap.add_argument("--out", default=os.path.join(HERE, "notes", "tt_api_map.json"))
    ap.add_argument("--grep", default=None, help="只显示路径含该子串的")
    ap.add_argument("--files", nargs="*", default=None, help="只解析文件名含这些子串的")
    a = ap.parse_args()

    total: dict[str, dict] = {}
    files = []
    for root, _, names in os.walk(a.dir):
        for n in names:
            if not n.endswith(".js"):
                continue
            if a.files and not any(s in n for s in a.files):
                continue
            files.append(os.path.join(root, n))
    print(f"扫描 {len(files)} 个 JS")

    for p in files:
        try:
            got = parse_file(p)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {os.path.basename(p)}: {e}", file=sys.stderr)
            continue
        for k, v in got.items():
            if k in total:
                total[k]["aliases"].append(v["name"])
                if v["file"] not in total[k].get("files", []):
                    total[k].setdefault("files", [total[k]["file"]]).append(v["file"])
            else:
                total[k] = v

    print(f"解析出 {len(total)} 个唯一 (方法, 路径)")
    json.dump(total, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"→ {a.out}\n")

    rows = sorted(total.values(), key=lambda d: (d["path"], d["method"] or ""))
    if a.grep:
        rows = [r for r in rows if a.grep in r["path"]]
    print(f"{'METHOD':<6} {'PATH':<68} name")
    for r in rows:
        print(f"{(r['method'] or '?'):<6} {r['path'][:68]:<68} {r['name']}"
              + (f"  (+{len(r['aliases'])})" if r["aliases"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
