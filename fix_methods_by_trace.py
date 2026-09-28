#!/usr/bin/env python3
"""用 bundle 里的**真实调用点**修正 master.json 的方法。

## 为什么需要

主表里大量接口方法抽成了 `?`（别名 `a.UD`、方法在别的分支、窗口没覆盖到）。
探测时 `?` 会退化成 GET —— 而真实调用点是 POST，于是统统 404。
本轮 220 个 404 里绝大多数是这个原因：回查调用点全是
`${uriPrefix}/api/v${e.version||1}/...` + `method:"POST"`。

## 做法

**只扫一遍 bundle**，建立 `<路径尾段> → Counter(方法)` 索引：
  · 抓所有 `uriPrefix}/api/v...` / `"/api/..."` 形式的路径字面量
  · 抓该表达式**之后 200 字符内**的 `method:`（字面量优先，别名校其次）
然后拿索引去修 master 里方法为 `?` 的条目。

别名表：`a.UD` / `i.UD` / `n.UD` / `G` == **GET**（财务那轮实测确认）。

用法：
  python3 fix_methods_by_trace.py            # 只报告
  python3 fix_methods_by_trace.py --apply    # 写回 master.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUNDLE_DIRS = [HERE / "notes" / "mf_all", HERE / "notes" / "fin_js", HERE / "notes" / "fin_mf"]
MASTER = HERE / "notes" / "api_inventory" / "master.json"

# 路径字面量：三种写法都覆盖
PATH_RX = re.compile(
    r"`\$\{[^}]{0,60}\}/api/v\$\{[^}]{0,60}?\|\|\s*(\d)\}(/[A-Za-z0-9_/\-]{3,150})`"   # 模板+默认版本
    r"|`\$\{[^}]{0,60}\}(/api/v\d/[A-Za-z0-9_/\-]{3,150})`"                            # 模板+固定版本
    r"|\"(/api/v\d/[A-Za-z0-9_/\-]{3,150})\""                                          # 字面量
    r"|\"(/(?:insights|qualification|product|seller|promotion|fulfillment|logistics|trade)"
    r"/[A-Za-z0-9_/\-]{4,150})\""                                                      # 无 /api 前缀
)
METH = re.compile(r'method:\s*(?:"([A-Z]{3,6})"|([A-Za-z_$][\w$.]{0,14}))')
ALIAS = {"a.UD": "GET", "i.UD": "GET", "n.UD": "GET", "s.EJ": "GET", "EJ": "GET",
         "G": "GET", "O": "GET", "we": "GET", "method$1": "GET"}


def norm(p: str) -> str:
    p = re.sub(r"\$\{[^}]*\}", "{v}", p)
    p = re.sub(r"\?.*$", "", p)
    return re.sub(r"/+$", "", p)


def build_index():
    idx: dict[str, collections.Counter] = {}
    files = [f for d in BUNDLE_DIRS if d.exists() for f in d.rglob("*.js")
             if f.is_file() and f.stat().st_size > 300]
    print(f"扫描 {len(files)} 个 bundle …", flush=True)
    for i, f in enumerate(files):
        try:
            s = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in PATH_RX.finditer(s):
            ver, p = m.group(1), (m.group(2) or m.group(3) or m.group(4) or m.group(5))
            if not p:
                continue
            if ver:                       # 模板默认版本 → 生成 /api/vN/… 形式
                p = re.sub(r"^/api/v\d+/", f"/api/v{ver}/", p) \
                    if p.startswith("/api/v") else p
            key = norm(p)
            # 方法：表达式之后 200 字符内，字面量优先
            win = s[m.end():m.end() + 220]
            meth = None
            for mm in METH.finditer(win):
                if mm.group(1):
                    meth = mm.group(1); break
                if mm.group(2) and meth is None:
                    meth = ALIAS.get(mm.group(2))
            e = idx.setdefault(key, collections.Counter())
            if meth:
                e[meth] += 1
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{len(files)}  索引 {len(idx)} 条", flush=True)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    idx = build_index()
    print(f"\n索引 {len(idx)} 条路径\n")
    master = json.loads(MASTER.read_text(encoding="utf-8"))

    fixed, still_unknown, agree, conflict = [], [], 0, []
    for p, v in master.items():
        cur = v.get("method") or "?"
        cand = idx.get(norm(p))
        if not cand:
            if cur in ("?", None):
                still_unknown.append(p)
            continue
        best = cand.most_common(1)[0][0]
        if cur == best:
            agree += 1
        elif cur in ("?", None):
            v["method"] = best
            fixed.append((p, best))
        else:
            conflict.append((p, cur, best, dict(cand)))

    print(f"方法为 ? 且索引里有 → 修正 {len(fixed)} 个")
    print(f"索引里没有，仍是 ? → {len(still_unknown)} 个")
    print(f"与索引一致 → {agree} 个")
    print(f"★ 与索引**冲突** → {len(conflict)} 个（这些要人工看）")
    print("\n修正样例（前 20）:")
    for p, m in fixed[:20]:
        print(f"  → {m:5} {p}")
    print("\n冲突样例（前 20）—— 索引可能抓到相邻调用，需回查:")
    for p, c, b, d in conflict[:20]:
        print(f"  {c:5} vs 索引 {b:5} {p}   {d}")
    if len(conflict) > 20:
        print(f"  …还有 {len(conflict)-20} 个")

    if a.apply:
        MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n✅ 已写回 {MASTER.name}")
        (HERE / "notes" / "method_conflicts.json").write_text(
            json.dumps([{"path": p, "master": c, "traced": b, "evidence": d}
                        for p, c, b, d in conflict], ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(f"   冲突清单 → notes/method_conflicts.json")
    else:
        print("\n（未加 --apply，只是预览）")


if __name__ == "__main__":
    main()
