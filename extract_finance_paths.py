#!/usr/bin/env python3
"""从 seller 财务板块前端抽全部接口 → notes/api_inventory/finance_paths.json

财务这套 bundle 有**三种**路径写法，必须都覆盖（前两版各漏了一种）：

1. 字面量：        "/api/v1/finance/purchase/recharge"
2. 模板 + 默认版本： `${this.uriPrefix}/api/v${e.version||1}/pay/settlement/balance/get`
   ← 关键：`/api/v` 后面不是数字而是 `${...}`，只匹配 `v\\d` 会把这 35+ 个全漏掉
3. oec 网关：      "/api/oec/pay/merchant/statement/view/statements"

版本号从 `${...||N}` 里取默认值（通常是 1）。方法名从包裹它的具名方法取：
    GetBalance(e,t){ … `${...}/api/v${e.version||1}/pay/settlement/balance/get` … }
"""
from __future__ import annotations

import collections
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
DIRS = [HERE / "notes" / "fin_js", HERE / "notes" / "fin_mf"]
OUT = HERE / "notes" / "api_inventory" / "finance_paths.json"

TPL = re.compile(r"/(widget/)?api/v\$\{[^}]{0,60}?\|\|\s*(\d)\}/([A-Za-z0-9_/\-]{3,140})")
TPL_NODEF = re.compile(r"/(widget/)?api/v\$\{[^}]{0,80}\}/([A-Za-z0-9_/\-]{3,140})")
LIT = re.compile(r"/(widget/)?api/v(\d)/([A-Za-z0-9_/\-]{3,140})")
OEC = re.compile(r"/api/oec/([A-Za-z0-9_/\-]{3,140})")
# ★ method 有三种写法：字符串字面量 "POST"、别名 a.UD、以及带 body 的默认 POST。
#   实测确认（真流量捕获）`a.UD` == GET —— 只认字符串字面量会把 89 个 GET 误标成 `?`，
#   再按 `?` 去试 POST 就全是 404。
METH2 = re.compile(r'method:\s*(?:"([A-Z]{3,6})"|([A-Za-z_$][\w$.]{0,12}))')
ALIAS = {"a.UD": "GET", "i.UD": "GET", "a.Xl": "GET", "UD": "GET"}
NAME = re.compile(r"([A-Z][A-Za-z0-9_]{2,48})\s*\((?:[a-z]+,\s*)*[a-z]+\)\s*\{")
JUNK = re.compile(r"(\.js|\.css|\.map|\?.*|\$\{.*|[\"'`].*)$")


def clean(p: str) -> str:
    p = JUNK.sub("", p) or p
    return re.sub(r"/+$", "", p)


rec: dict[str, dict] = {}


def add(full: str, *, win: str = "", back: str = "", src: str = ""):
    if len([x for x in full.split("/") if x]) < 3:
        return
    e = rec.setdefault(full, {"meth": collections.Counter(),
                              "names": collections.Counter(), "src": set()})
    if src:
        e["src"].add(src)
    # 窗口里可能同时有别名和字面量（相邻调用），字面量优先
    lits, aliases = [], []
    for mm in METH2.finditer(win):
        (lits if mm.group(1) else aliases).append(mm.group(1) or mm.group(2))
    if lits:
        e["meth"][lits[0]] += 1
    elif aliases:
        al = aliases[0]
        e["meth"][ALIAS.get(al, "POST" if "body:" in win[:200] else "?")] += 1
    nm = None
    for x in NAME.finditer(back):
        nm = x.group(1)
    if nm:
        e["names"][nm] += 1


files = [f for d in DIRS for f in sorted(d.glob("*"))]
for f in files:
    if not f.is_file() or f.stat().st_size < 300:
        continue
    s = f.read_text(encoding="utf-8", errors="replace")
    tag = f.name[:34]
    for m in TPL.finditer(s):
        w, ver, path = m.group(1), m.group(2), m.group(3)
        add(clean(f"/{w or ''}api/v{ver}/{path}"),
            win=s[m.end():m.end() + 200], back=s[max(0, m.start() - 300):m.start()], src=tag)
    for m in TPL_NODEF.finditer(s):
        w, path = m.group(1), m.group(2)
        add(clean(f"/{w or ''}api/v1/{path}"),
            win=s[m.end():m.end() + 200], back=s[max(0, m.start() - 300):m.start()], src=tag)
    for m in LIT.finditer(s):
        w, ver, path = m.group(1), m.group(2), m.group(3)
        add(clean(f"/{w or ''}api/v{ver}/{path}"),
            win=s[m.end():m.end() + 200], back=s[max(0, m.start() - 300):m.start()], src=tag)
    for m in OEC.finditer(s):
        add(clean(f"/api/oec/{m.group(1)}"),
            win=s[m.end():m.end() + 200], back=s[max(0, m.start() - 300):m.start()], src=tag)

rows = []
for p, e in sorted(rec.items()):
    rows.append({"path": p,
                 "method": e["meth"].most_common(1)[0][0] if e["meth"] else "?",
                 "names": [n for n, _ in e["names"].most_common(3)],
                 "src": sorted(e["src"])[:2]})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(rows)} 个路径 → {OUT}")
print("方法:", collections.Counter(r["method"] for r in rows).most_common())
print("\n命名空间（前 4 段）:")
c = collections.Counter()
for r in rows:
    c["/".join([x for x in r["path"].split("/") if x][:4])] += 1
for k, v in c.most_common(32):
    print(f"  {v:>4}  /{k}")
