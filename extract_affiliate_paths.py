#!/usr/bin/env python3
"""从联盟中心前端 bundle 抽取全部 API 路径 + HTTP 方法 → notes/api_inventory/enriched.json

bundle 写法（拼接式，路径不能直接整串 grep）：
    "".concat(this.uriPrefix, "/api/v").concat(e.version || "1", "/oec/affiliate/xxx/yyy")
    → 尾部字面量 "/oec/affiliate/xxx/yyy" 是完整可抓的；版本默认从 `version || "N"` 取。

方法抽取的坑：单看字面量**后面** 400 字符会把下一个调用的 method 也吃进来。
所以窗口 = [本字面量结束, 下一个字面量开始)，只看这一段。
"""
import re, json, pathlib, collections

HERE = pathlib.Path(__file__).resolve().parent
JS = HERE / "notes/aff_js"
OUT = HERE / "notes/api_inventory/enriched.json"

TAIL = re.compile(r'"/(oec|api|im|insights|affiliate|common|reverse|media|v\d+)/[A-Za-z0-9_/\.\-]{3,110}"')
VER = re.compile(r'version\s*\|\|\s*"(\d)"')
METH = re.compile(r'method:\s*"(GET|POST|PUT|PATCH|DELETE|HEAD)"')
# 已知的真实方法（实测过的，优先于 bundle 推测）
KNOWN = json.loads((HERE / "notes/api_inventory/known_methods.json").read_text(encoding="utf-8")) \
    if (HERE / "notes/api_inventory/known_methods.json").exists() else {}

rec = {}
for f in sorted(JS.glob("*")):
    if not f.is_file() or f.stat().st_size < 2000:
        continue
    s = f.read_text(encoding="utf-8", errors="replace")
    ms = list(TAIL.finditer(s))
    for i, m in enumerate(ms):
        p = "/" + m.group(0).strip('"').lstrip("/")
        if len(p) < 6:
            continue
        win_end = ms[i + 1].start() if i + 1 < len(ms) else m.end() + 320
        window = s[m.end():min(win_end, m.end() + 320)]
        ver = VER.search(s[max(0, m.start() - 300):m.start()])
        e = rec.setdefault(p, {"versions": set(), "methods": collections.Counter(), "src": set()})
        e["versions"].add(ver.group(1) if ver else "1")
        mm = METH.search(window)
        if mm:
            e["methods"][mm.group(1)] += 1
        e["src"].add(f.name[:30])

rows_by_full = {}
for p, e in sorted(rec.items()):
    ver = sorted(e["versions"])[0]
    full = f"/api/v{ver}{p}" if p.startswith(("/oec/", "/affiliate/", "/insights/", "/creator/")) else p
    # 垃圾串：以 / 结尾、段数太少、或只是前缀
    if full.endswith("/") or len([x for x in full.split("/") if x]) < 3:
        continue
    # ★ 必须在 **归一化后的 full** 上去重：tail `/oec/affiliate/x` 与 `/affiliate/x`
    #   会归一成同一路径，按 tail 去重会留两条
    r = rows_by_full.setdefault(full, {"path": full, "ver": set(), "methods": collections.Counter()})
    r["ver"] |= e["versions"]
    r["methods"] += e["methods"]

rows = []
for full, r in sorted(rows_by_full.items()):
    meth = KNOWN.get(full) or (r["methods"].most_common(1)[0][0] if r["methods"] else "?")
    rows.append({"path": full, "ver": sorted(r["ver"]), "method": meth,
                 "method_src": "known" if full in KNOWN else
                 ("bundle" if r["methods"] else "unknown")})
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(rows)} 个路径 → {OUT}")
print("方法:", collections.Counter(r["method"] for r in rows).most_common())
print("来源:", collections.Counter(r["method_src"] for r in rows).most_common())
