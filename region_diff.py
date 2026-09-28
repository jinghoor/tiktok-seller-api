#!/usr/bin/env python3
"""两店差异矩阵 —— 跨境 vs 本土的接口可达性对比（阶段 5）。

## 输入

`notes/probe_*.json` / `notes/route_map_*.json` —— 各店实测结果。

## 判据

把每个店铺的判定归一成三态：

| 态 | 来源判定 |
|---|---|
| `有` | ✅ 通 / ◐ 路由存在 / ◐ 缺 body / ◐ 缺参数 |
| `无` | ✗ 路由不存在 / ✗ 404 / 🚫 无此路由 |
| `?` | 请求失败 / 未测 |

然后按 (path) 做交叉表，输出四类：
  · **共有**（两店都有）
  · **仅跨境**（本土无）
  · **仅本土**（跨境无）
  · **都无**（抽出来但两边都不通 —— 需要复核抽取）

用法：
  python3 region_diff.py --a tk89 --b tk01
  python3 region_diff.py --a tk89 --b tk56 --out notes/DIFF_tk89_tk56.json
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
NOTES = HERE / "notes"

EXISTS_PREFIX = ("✅", "◐")
MISSING_PREFIX = ("✗", "🚫")


def state(v: str) -> str:
    if v.startswith(EXISTS_PREFIX):
        return "有"
    if v.startswith(MISSING_PREFIX):
        return "无"
    return "?"


def load_shop(key: str) -> dict[str, str]:
    """把某店所有探测/测绘结果合成 path → 判定。冲突时'有'优先（更可信）。"""
    out: dict[str, str] = {}
    files = (glob.glob(str(NOTES / f"probe_{key}_*.json"))
             + glob.glob(str(NOTES / f"route_map_{key}_*.json")))
    for f in files:
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, list):
            rows = d
        elif isinstance(d, dict):
            rows = d.get("results") or d.get("merged") or []
        else:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            k = (r.get("cls") or r.get("v") or "")
            if not k:
                continue
            s = state(k)
            prev = out.get(r["path"])
            if prev is None or (prev != "有" and s == "有"):
                out[r["path"]] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="tk89", help="本土店 key")
    ap.add_argument("--b", default="tk01", help="跨境店 key")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    A, B = load_shop(a.a), load_shop(a.b)
    print(f"  {a.a}: {len(A)} 条判定    {a.b}: {len(B)} 条判定\n")
    if not A or not B:
        print("  ✗ 数据不足，先跑探测")
        return

    master = json.loads((NOTES / "api_inventory" / "master.json").read_text(encoding="utf-8"))
    paths = sorted(set(A) | set(B))
    rows = []
    for p in paths:
        sa, sb = A.get(p, "未测"), B.get(p, "未测")
        if sa == "有" and sb == "有":
            tag = "共有"
        elif sa == "有" and sb == "无":
            tag = f"仅{a.a}"
        elif sb == "有" and sa == "无":
            tag = f"仅{a.b}"
        elif sa == "无" and sb == "无":
            tag = "都无"
        else:
            tag = "未测"
        rows.append({"path": p, "a": sa, "b": sb, "tag": tag,
                     "method": master.get(p, {}).get("method", "?"),
                     "domain": master.get(p, {}).get("domain", "?")})

    c = collections.Counter(r["tag"] for r in rows)
    print("交叉表:")
    for k, v in c.most_common():
        print(f"    {v:>5}  {k}")
    print(f"    {sum(1 for _ in rows):>5}  合计")

    # 按业务域看差异
    print("\n按业务域（共有 / 仅A / 仅B / 都无）:")
    by = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        by[r["domain"]][r["tag"]] += 1
    print(f"    {'业务域':34} {'共有':>6} {('仅'+a.a):>7} {('仅'+a.b):>7} {'都无':>6}")
    for d in sorted(by, key=lambda x: -sum(by[x].values())):
        t = by[d]
        print(f"    {d:34} {t['共有']:>6} {t[f'仅{a.a}']:>7} {t[f'仅{a.b}']:>7} {t['都无']:>6}")

    out = pathlib.Path(a.out) if a.out else NOTES / f"diff_{a.a}_vs_{a.b}.json"
    out.write_text(json.dumps({"a": a.a, "b": a.b, "rows": rows,
                               "counts": dict(c)}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\n→ {out.name}")

    for tag, label in ((f"仅{a.a}", f"仅本土（{a.a} 有、{a.b} 无）"),
                       (f"仅{a.b}", f"仅跨境（{a.b} 有、{a.a} 无）")):
        sub = [r for r in rows if r["tag"] == tag]
        if not sub:
            continue
        print(f"\n### {label} —— {len(sub)} 个（前 25）")
        for r in sub[:25]:
            print(f"    {r['method']:5} {r['path']}")


if __name__ == "__main__":
    main()
