#!/usr/bin/env python3
"""全量接口客户端 —— 覆盖主表里全部 4205 个接口，带实测状态标注。

这是「后训练」的产物：不是又写十个域客户端，而是把主表变成**可查询、可调用**的
索引，每个接口都带：
  · 方法（878 个经 bundle 调用点核验，0 冲突）
  · 业务域
  · **实测状态**（本土店 4205 条全量测绘 + 跨境 653 条）
  · 是否 `code=0`（参数已猜对，可直接用）

## 用法

```bash
python3 tk_api.py domains                          # 域清单 + 存在率
python3 tk_api.py search insights --shop tk89      # 按关键词搜
python3 tk_api.py verified --domain 财务 --shop tk89
python3 tk_api.py call /api/v1/pay/settlement/settings --shop tk89
python3 tk_api.py call /api/v1/insights/seller/core/stats --method POST --body '{"request":{}}'
python3 tk_api.py probe /api/v1/x /api/v1/y        # 现测几个
```

```python
from tk_api import ApiIndex, Api
idx = ApiIndex()
print(idx.stats())
for row in idx.search("insights", domain="数据 / 罗盘 / 报表", verified="exists"):
    print(row["method"], row["path"], row["verdict"])

with Api("tk89") as a:
    a.call("/api/v1/pay/settlement/settings")        # 直接调
```
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
NOTES = HERE / "notes"
MASTER = NOTES / "api_inventory" / "master.json"

from tk_base import BaseClient, ApiError  # noqa: E402

EXISTS_PREFIX = ("✅", "◐")
MISSING_PREFIX = ("✗", "🚫")


def _state(v: str) -> str:
    if v.startswith(EXISTS_PREFIX):
        return "exists"
    if v.startswith(MISSING_PREFIX):
        return "missing"
    return "unknown"


class ApiIndex:
    """主表 + 实测状态的可查询索引。"""

    def __init__(self, master: pathlib.Path = MASTER):
        self.master = json.loads(master.read_text(encoding="utf-8"))
        self.measured: dict[str, dict] = {}
        self._load_measurements()

    def _load_measurements(self):
        """合并所有探测/测绘结果。冲突时 `exists` 优先（更可信）。"""
        files = (glob.glob(str(NOTES / "route_map_*.json"))
                 + glob.glob(str(NOTES / "probe_*.json")))
        for f in files:
            shop = pathlib.Path(f).stem
            try:
                d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
            except Exception:
                continue
            # 探测结果有两种形状：{"results": [...]} / {"merged": [...]} / 裸 list
            if isinstance(d, list):
                rows = d
            elif isinstance(d, dict):
                rows = d.get("results") or d.get("merged") or []
            else:
                continue
            if not isinstance(rows, list):
                continue
            for r in rows:
                v = r.get("v") or r.get("cls") or ""
                if not v:
                    continue
                st = _state(v)
                # route_map 的结果没存 code 字段，要从判定串里解出来：
                #   "✅ 通"                      → code = 0
                #   "◐ 路由存在（code=98001004）" → code = 98001004
                code = r.get("code")
                if code is None:
                    if v.startswith("✅"):
                        code = 0
                    else:
                        mm = re.search(r"code=(-?\d+)", v)
                        code = int(mm.group(1)) if mm else None
                cur = self.measured.get(r["path"])
                # 只保留信息量最大的那条：exists > missing > unknown
                rank = {"exists": 2, "missing": 1, "unknown": 0}
                if cur is None or rank[st] > rank[cur["state"]]:
                    self.measured[r["path"]] = {
                        "state": st, "verdict": v, "shop": shop,
                        "code": code,
                        "http": r.get("http"),
                    }

    # ── 查询 ──
    def get(self, path: str) -> dict | None:
        e = self.master.get(path)
        if e is None:
            return None
        m = self.measured.get(path, {})
        return {"path": path, "method": e.get("method", "?"),
                "domain": e.get("domain", "?"), "sources": e.get("sources", []),
                "names": e.get("names", []),
                "state": m.get("state", "unmeasured"),
                "verdict": m.get("verdict", ""), "code": m.get("code")}

    def search(self, keyword: str = "", *, domain: str | None = None,
               verified: str | None = None, method: str | None = None,
               limit: int = 200) -> list[dict]:
        out = []
        kw = keyword.lower()
        for p, e in self.master.items():
            if kw and kw not in p.lower() and not any(
                    kw in str(n).lower() for n in e.get("names", [])):
                continue
            if domain and domain not in e.get("domain", ""):
                continue
            if method and e.get("method", "").upper() != method.upper():
                continue
            m = self.measured.get(p, {})
            st = m.get("state", "unmeasured")
            if verified == "exists" and st != "exists":
                continue
            if verified == "ok" and m.get("code") != 0:
                continue
            if verified == "missing" and st != "missing":
                continue
            out.append({"path": p, "method": e.get("method", "?"),
                        "domain": e.get("domain", "?"), "state": st,
                        "verdict": m.get("verdict", ""), "code": m.get("code"),
                        "names": e.get("names", [])})
        return out[:limit]

    def domains(self) -> list[tuple[str, int, int, int]]:
        """(域, 总数, 存在数, code=0 数)，按存在数降序。"""
        acc = collections.defaultdict(lambda: [0, 0, 0])
        for p, e in self.master.items():
            d = e.get("domain", "?")
            acc[d][0] += 1
            m = self.measured.get(p)
            if m and m["state"] == "exists":
                acc[d][1] += 1
                if m.get("code") == 0:
                    acc[d][2] += 1
        return sorted(((d, *v) for d, v in acc.items()), key=lambda x: -x[2])

    def stats(self) -> dict:
        st = collections.Counter(
            self.measured.get(p, {}).get("state", "unmeasured") for p in self.master)
        return {"total": len(self.master), **st,
                "ready": sum(1 for m in self.measured.values() if m.get("code") == 0)}


class Api:
    """可调用的全量客户端（索引 + 传输）。"""

    def __init__(self, shop: str | None = None, *, port: int | None = None,
                 page_hint: str | None = None, verbose: bool = False):
        self.index = ApiIndex()
        self.c = BaseClient(shop, port=port, page_hint=page_hint, verbose=verbose)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.c.close()
        return False

    @property
    def shop_info(self):
        return self.c.shop_info()

    @property
    def ready(self) -> list[str]:
        """实测 `code=0` 的接口 —— 参数已猜对，能直接用。"""
        return sorted(p for p, m in self.index.measured.items() if m.get("code") == 0)

    def call(self, path: str, *, method: str | None = None, body=None,
             params: dict | None = None, version: int | None = None,
             auto_method: bool = True, raw: bool = False):
        """调接口。`method` 不给时按主表里的记录自动选。"""
        if method is None and auto_method:
            e = self.index.master.get(path, {})
            m = (e.get("method") or "GET").upper()
            method = m if m in ("GET", "POST", "PUT", "PATCH", "DELETE") else "POST"
        return self.c.call(path, method=method or "GET", body=body, params=params,
                           version=version, raw=raw)

    def call_ready(self, path: str, **kw):
        """调一个已实测 code=0 的接口，`code != 0` 抛异常。"""
        if path not in self.index.measured:
            print(f"  ⚠ {path} 没实测记录，仍照常发", file=sys.stderr)
        return self.c.call_ok(path, **kw)

    def probe(self, paths: Sequence[str], **kw) -> list[dict]:
        jobs = []
        for p in paths:
            e = self.index.master.get(p, {})
            m = (e.get("method") or "POST").upper()
            jobs.append({"path": p, "method": m if m in ("GET", "POST") else "POST",
                         "body": {} if m != "GET" else None})
        return self.c.batch(jobs, **kw)


# ── CLI ──
def _fmt(row: dict, width: int = 96) -> str:
    mark = {"exists": "◐", "missing": "✗", "unknown": "?", "unmeasured": " "}.get(row["state"], " ")
    code = f" code={row['code']}" if row.get("code") not in (None, 0) else ""
    return f"  {mark} {row['method']:5} {row['path'][:width]}{code}"


def main():
    ap = argparse.ArgumentParser(description="卖家中心全量接口客户端")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("domains", help="域清单 + 存在率")
    p.add_argument("--shop", default=None)

    p = sub.add_parser("search", help="按关键词搜接口")
    p.add_argument("keyword", nargs="?", default="")
    p.add_argument("--domain")
    p.add_argument("--verified", choices=["exists", "ok", "missing"])
    p.add_argument("--method")
    p.add_argument("--limit", type=int, default=60)
    p.add_argument("--shop", default=None)

    p = sub.add_parser("verified", help="列出已实测存在（或 code=0）的接口")
    p.add_argument("--domain")
    p.add_argument("--ok-only", action="store_true", help="只要 code=0 的")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--shop", default=None)

    p = sub.add_parser("call", help="实测调一个接口")
    p.add_argument("path")
    p.add_argument("--method")
    p.add_argument("--body", help="JSON 字符串")
    p.add_argument("--version", type=int)
    p.add_argument("--shop", default=None)
    p.add_argument("--page-hint", default=None)
    p.add_argument("--raw", action="store_true", help="输出原始 bytes 长度")

    p = sub.add_parser("probe", help="现测几个接口")
    p.add_argument("paths", nargs="+")
    p.add_argument("--shop", default=None)

    a = ap.parse_args()

    if a.cmd == "domains":
        idx = ApiIndex()
        st = idx.stats()
        print(f"总接口 {st['total']}  实测存在 {st.get('exists',0)}  "
              f"不存在 {st.get('missing',0)}  未测 {st.get('unmeasured',0)}  "
              f"code=0 的 {st.get('ready',0)}\n")
        print(f"  {'业务域':30} {'总数':>6} {'存在':>6} {'code=0':>7}  存在率")
        for d, tot, ex, ok in idx.domains():
            print(f"  {d:30} {tot:>6} {ex:>6} {ok:>7}  {ex*100//max(1,tot):>4}%")
        return

    if a.cmd in ("search", "verified"):
        idx = ApiIndex()
        kw = getattr(a, "keyword", "")
        ver = "ok" if getattr(a, "ok_only", False) else \
              ("exists" if a.cmd == "verified" else getattr(a, "verified", None))
        rows = idx.search(kw, domain=getattr(a, "domain", None), verified=ver,
                          method=getattr(a, "method", None), limit=a.limit)
        print(f"命中 {len(rows)} 个\n")
        for r in rows:
            print(_fmt(r))
        return

    if a.cmd == "call":
        body = json.loads(a.body) if a.body else None
        with Api(a.shop, page_hint=a.page_hint, verbose=True) as api:
            print(f"  {api.shop_info}")
            e = api.index.master.get(a.path)
            print(f"  主表: {e.get('method') if e else '(不在表里)'} {a.path}")
            m = api.index.measured.get(a.path)
            if m:
                print(f"  实测: {m['verdict']}")
            r = api.call(a.path, method=a.method, body=body, version=a.version,
                         raw=a.raw)
            if a.raw:
                print(f"  原始 {len(r[1])} 字节 http={r[0]}")
            else:
                print(json.dumps(r, ensure_ascii=False, indent=1)[:3000])
        return

    if a.cmd == "probe":
        with Api(a.shop, verbose=True) as api:
            print(f"  {api.shop_info}")
            for r in api.probe(a.paths, show_progress=True):
                mark = "✅" if r.get("code") == 0 else ("◐" if r.get("ok") else "✗")
                print(f"  {mark} {r['method']:5} {r['path'][:80]}  http={r['http']}"
                      f" code={r.get('code')} {str(r.get('msg'))[:60]}")
        return


if __name__ == "__main__":
    main()
