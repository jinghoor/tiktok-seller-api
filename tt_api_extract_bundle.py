#!/usr/bin/env python3
"""从 TikTok 卖家中心微前端 bundle 中提取 API 层定义。

bundle 里的 API 长这样：
  <MethodName>(e,t){return z(`${this.uriPrefix}/api/v${e.version||1}/product/stock/alert/set_stock`,
                            {method:`POST`,headers:R,body:e},t)}
所以不能简单 grep 反引号字符串的完整路径（含 ${} 模板变量），
必须按「方法名(参数){ ... `${this.uriPrefix}<PATH>` ... method:`<M>` }」的结构切分。

用法：
  python3 tt_api_extract_bundle.py product-stock.n87bqkie.js
  python3 tt_api_extract_bundle.py --all --md ../TT_STOCK_API_FROM_BUNDLE.md
  python3 tt_api_extract_bundle.py --all --filter price
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import OrderedDict

# 方法名(参数列表){  ...  `.../api/v${...}/<path>`  ...  method:`POST`
RE_API = re.compile(
    r"(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(([^()]{0,200}?)\)\s*\{"          # 方法名 (参数) {
    r"(?:(?!\}\s*,\s*[A-Za-z_$]).){0,900}?"                              # 中间体（不跨越到下一个方法）
    r"\$\{this\.uriPrefix\}"                                             # URI 前缀模板
    r"(/api/v\$?\{?[^`'\"]{0,200}?)"                                     # 真正的路径
    r"[`'\"]"                                                            # 路径结束
    r"(?:(?!\n\s*[A-Za-z_$][\w$]*\s*\().){0,400}?"                       # 到 method 之间
    r"method\s*:\s*[`'\"]([A-Z]+)[`'\"]",                                # HTTP 方法
    re.S,
)

# 从路径里剥掉 ${...} 模板变量，得到可读路径
RE_TPL = re.compile(r"\$\{[^}]*\}")


def clean_path(p: str) -> str:
    p = RE_TPL.sub("{}", p)
    return p.replace("/api/v{}", "/api/v1")


def walk_file(path: str) -> list[dict]:
    src = open(path, encoding="utf-8", errors="replace").read()
    out: OrderedDict[str, dict] = OrderedDict()
    for m in RE_API.finditer(src):
        name, params, raw_path, method = m.groups()
        if name in {"if", "for", "while", "switch", "catch", "return", "function"}:
            continue
        p = clean_path(raw_path)
        if "/api/" not in p:
            continue
        key = f"{method} {p}"
        if key in out:
            continue
        out[key] = {
            "method": method,
            "path": p,
            "fn": name,
            "params": params.strip(),
            "file": os.path.basename(path),
        }
    return list(out.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true", help="扫描 ./stock/*.js 与当前目录 *.js")
    ap.add_argument("--filter", default=None, help="按关键词过滤路径")
    ap.add_argument("--md", default=None, help="输出 Markdown 表格到文件")
    ap.add_argument("--json", default=None, help="输出 JSON 到文件")
    a = ap.parse_args()

    files = list(a.files)
    if a.all or not files:
        files = sorted(glob.glob("stock/*.js")) + sorted(glob.glob("*.js"))
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        sys.exit("没找到输入文件")

    rows: list[dict] = []
    seen = set()
    for f in files:
        try:
            for r in walk_file(f):
                k = (r["method"], r["path"])
                if k in seen:
                    continue
                seen.add(k)
                rows.append(r)
        except Exception as e:  # bundle 是机器生成的，单文件失败不该影响整体
            print(f"  ! {f}: {e}", file=sys.stderr)

    if a.filter:
        kw = a.filter.lower()
        rows = [r for r in rows if kw in r["path"].lower() or kw in r["fn"].lower()]

    rows.sort(key=lambda r: (r["path"], r["method"]))

    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(f"# TikTok 微前端 API 层提取（{len(rows)} 个接口）\n\n")
            fh.write("来源：`oec-magellan-sg/i18n/ecom/next/product_manage_stock/` bundle\n\n")
            fh.write("| 方法 | 路径 | 前端函数名 | 源文件 |\n|---|---|---|---|\n")
            for r in rows:
                fh.write(f"| {r['method']} | `{r['path']}` | `{r['fn']}` | {r['file']} |\n")
        print(f"已写 {a.md}（{len(rows)} 条）")

    if a.json:
        json.dump(rows, open(a.json, "w"), ensure_ascii=False, indent=2)
        print(f"已写 {a.json}")

    for r in rows:
        print(f"{r['method']:6} {r['path']:<72} {r['fn']}")
    print(f"\n总计 {len(rows)} 个接口，扫描 {len(files)} 个文件")


if __name__ == "__main__":
    main()
