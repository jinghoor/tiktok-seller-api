"""侦察：拉两个店的完整导航树 → 得到全部页面路由。零打扰（借已打开页面页内 fetch）。"""
import json, sys, pathlib
sys.path.insert(0, ".")
from tk01_finance import FinanceClient

CANDIDATES = [
    ("/api/v2/seller/menu/get", "GET", None),
    ("/api/v1/seller/menu/get", "GET", None),
    ("/api/v1/seller/navigation_bar/get", "GET", None),
    ("/api/v3/seller/common/get", "GET", None),
    ("/api/v1/seller/common/get", "GET", None),
]
out = {}
for shop in ("tk89", "tk01"):
    C = FinanceClient(shop)
    out[shop] = {}
    try:
        print(f"\n{'='*100}\n### {shop}  ({C.api_base})\n{'='*100}")
        for path, m, body in CANDIDATES:
            try:
                r = C.call("probe", path=path, method=m, body=body)
                code = r.get("code") if isinstance(r, dict) else None
                n = len(json.dumps(r)) if r else 0
                print(f"  {m:5} {path:44} code={code}  {n} 字节")
                out[shop][path] = {"code": code, "resp": r}
            except Exception as e:
                print(f"  {m:5} {path:44} ✗ {str(e)[:80]}")
    finally:
        C.close()
pathlib.Path("notes/page_recon.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1)[:3000000], encoding="utf-8")
print("\n→ notes/page_recon.json")

# 从 menu 响应里抽路由
import re
for shop, d in out.items():
    for path, v in d.items():
        if v.get("code") != 0: continue
        txt = json.dumps(v["resp"], ensure_ascii=False)
        routes = sorted(set(re.findall(r'"(/[a-z][a-z0-9_/\-]{2,80})"', txt)))
        if len(routes) < 5: continue
        print(f"\n### {shop} {path} → {len(routes)} 条路由")
        for r in routes[:120]:
            print(f"    {r}")
        pathlib.Path(f"notes/routes_{shop}.txt").write_text("\n".join(routes), encoding="utf-8")
        break
