#!/usr/bin/env python3
"""回查接口的**真实调用点** —— 拿 bundle 里的原始代码定性，而不是空 body 硬试。

用途：探测出现 404 时，判断到底是
  ① 抽路径时把**前端路由**误当接口
  ② 前缀不对（`/api/v1` vs `/widget/api` vs 无前缀）
  ③ 版本不对（`/api/v` + `${version||1}` 的默认值不是 1）
  ④ 方法不对
  ⑤ 该网关注册表里确实没有

做法：拿路径的**特征尾段**在全部 bundle 里搜，打印上下文里的
`uriPrefix + "/api/v..."` 表达式、`method:`、`body:`。

用法：
  python3 trace_endpoint.py "customs/hscode"
  python3 trace_endpoint.py --from-404 notes/probe_tk56_merged.json --top 20
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

METH = re.compile(r'method:\s*(?:"([A-Z]{3,6})"|([A-Za-z_$][\w$.]{0,12}))')
URL_EXPR = re.compile(r'`\$\{[^}]{0,40}\}(/api[^`]{0,160})`|"(/api[^"]{0,160})"')
ALIAS = {"a.UD": "GET", "i.UD": "GET", "n.UD": "GET", "G": "GET", "O": "GET"}


def bundles():
    for d in BUNDLE_DIRS:
        if not d.exists():
            continue
        for f in d.rglob("*.js"):
            if f.is_file() and f.stat().st_size > 300:
                yield f


def trace(tail: str, *, ctx: int = 420, max_hits: int = 3, show: bool = True):
    """tail 是路径的特征片段，如 `customs/hscode`。"""
    pat = re.compile(re.escape(tail))
    out = []
    for f in bundles():
        try:
            s = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in pat.finditer(s):
            lo, hi = max(0, m.start() - ctx), m.start() + ctx // 2
            win = s[lo:hi]
            # 找最近的 api 表达式
            urls = URL_EXPR.findall(win)
            url = next((a or b for a, b in urls), "")
            # 找最近的方法
            meth = ""
            for mm in METH.finditer(s[m.start():m.start() + 300]):
                if mm.group(1):
                    meth = mm.group(1); break
                if mm.group(2):
                    meth = ALIAS.get(mm.group(2), f"alias:{mm.group(2)}"); break
            # 是否有 body
            has_body = bool(re.search(r"body\s*:", s[m.start():m.start() + 260]))
            # 是否紧邻 method（说明是接口调用而不是路由常量）
            near_meth = bool(METH.search(s[max(0, m.start() - 260):m.start() + 260]))
            out.append({"file": f.name[:56], "url_expr": url, "method": meth,
                        "has_body": has_body, "near_method": near_meth,
                        "snippet": win.replace("\n", " ")[-330:]})
            if show:
                print(f"\n  ── {f.name[:60]}")
                print(f"     url_expr = {url or '(未找到 api 表达式)'}")
                print(f"     method   = {meth or '(未找到)'}   has_body={has_body}  near_method={near_meth}")
                print(f"     …{win.replace(chr(10), ' ')[-300:]}")
            if len(out) >= max_hits:
                return out
    if not out and show:
        print(f"  ⚠ 在 {sum(1 for _ in bundles())} 个 bundle 里没找到 {tail!r} —— "
              f"说明它不是从这些 bundle 里抽出来的（可能是前端路由或别的来源）")
    return out


def classify_trace(hits) -> str:
    if not hits:
        return "🗑 不是接口（疑似前端路由）"
    h = hits[0]
    if not h["near_method"] and not h["url_expr"]:
        return "🗑 不是接口（路径附近没有 method）"
    u = h["url_expr"]
    if u:
        if "/widget/" in u:
            return "🔀 前缀不同：/widget/api"
        if "api/v" in u and "version" in u:
            return "🔀 版本由调用方给（`${version||1}`）"
        if not u.startswith("/api"):
            return "🔀 无 /api 前缀"
    if h["method"].startswith("alias:"):
        return f"🔀 方法别名 {h['method']}"
    return "✔ 是接口，路径/方法需按调用点修正"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tail", nargs="?")
    ap.add_argument("--from-404", default=None)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()

    if a.tail:
        trace(a.tail)
        return

    if not a.from_404:
        print("用法: trace_endpoint.py <tail>  或  --from-404 <probe.json>")
        return

    d = json.loads(pathlib.Path(a.from_404).read_text(encoding="utf-8"))
    rows = d.get("merged") or d.get("results") or []
    bad = [r["path"] for r in rows if r["cls"].startswith("✗")]
    # 按前缀聚类，每簇取一个代表来查
    cluster = collections.Counter()
    for p in bad:
        seg = [s for s in p.split("/") if s and s not in ("api", "widget")]
        seg = [s for s in seg if not re.fullmatch(r"v\d+", s)]
        cluster["/".join(seg[:3])] += 1
    print(f"404 共 {len(bad)} 个，{len(cluster)} 个前缀簇\n")
    print(f"{'数量':>5}  {'前缀簇':52} 判定")
    print("─" * 130)
    for pre, n in cluster.most_common(a.top):
        hits = trace(pre, show=False, max_hits=2)
        verdict = classify_trace(hits)
        print(f"{n:>5}  /{pre:51} {verdict}")
        if hits and hits[0]["url_expr"]:
            print(f"{'':7}└ url_expr: {hits[0]['url_expr'][:100]}")
    print()


if __name__ == "__main__":
    main()
