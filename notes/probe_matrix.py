#!/usr/bin/env python3
"""全量矩阵探测:对每个接口尝试 (base, prefix) 组合,确定真实 URL 形态。

网关 front-v1.aiadfly.com/front_api 会按 <module>/ 前缀转发到内部服务,
但各模块在 bundle 里有的自己带了域名前缀、有的没带,所以逐个实测。

结果写 spec/route_map.json: fn -> {method, path, base, prefix, live}
"""
from __future__ import annotations
import concurrent.futures as cf, json, ssl, urllib.request, urllib.error
from pathlib import Path
import certifi

HERE = Path(__file__).resolve().parent
ROWS = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
CTX = ssl.create_default_context(cafile=certifi.where())
HEAD = {"Content-Type": "application/json; charset=UTF-8;", "lang": "zh-CN",
        "country": "CN", "CompanyExID": "10017794444062955153"}

BASES = {
    "gw": "https://front-v1.aiadfly.com/front_api",
    "automation": "https://automation-v1.aiadfly.com/front_api",
    "ai_agent": "https://ai-agent-v1.aiadfly.com/ai_agent",
    "mcp": "https://mcp-open.aiadfly.com",
}
# 每个 module 尝试的前缀(空 = 直接拼在 base 后面)
PREFIX_BY_BACKEND = {
    "front": [""],
    "advertise": ["", "advertise/"],
    "finance": ["", "finance/"],
    "finance_bff": ["", "finance_bff/", "finance/"],
    "automation": ["", "automation/"],
    "ai_agent": ["", "v1/", "market/"],
    "mcp_open": ["", "mcp_open/"],
}
BASES_BY_BACKEND = {
    "automation": ["automation", "gw"],
    "ai_agent": ["ai_agent", "gw"],
    "mcp_open": ["mcp", "gw"],
}


def probe(base: str, prefix: str, path: str, method: str) -> tuple[bool | None, str]:
    url = f"{BASES[base]}/{prefix}{path.lstrip('/')}"
    req = urllib.request.Request(url, data=b"{}" if method == "POST" else None, headers=HEAD, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")[:160]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:160]
    except Exception as e:
        return None, type(e).__name__
    sq = body.replace("\n", " ")
    if "page not found" in sq:
        return False, sq
    return True, sq


def main() -> None:
    jobs = []
    for r in ROWS:
        for base in BASES_BY_BACKEND.get(r["backend"], ["gw"]):
            for pre in PREFIX_BY_BACKEND.get(r["backend"], [""]):
                jobs.append((base, pre, r))
    print(f"矩阵探测 {len(jobs)} 次…")
    best: dict[str, dict] = {}
    raw = []
    with cf.ThreadPoolExecutor(24) as ex:
        futs = {ex.submit(probe, b, p, r["path"], r["method"]): (b, p, r) for b, p, r in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            b, p, r = futs[f]
            live, body = f.result()
            rec = {"fn": r["fn"], "backend": r["backend"], "method": r["method"], "path": r["path"],
                   "base": b, "prefix": p, "live": live, "raw": body[:120]}
            raw.append(rec)
            key = f'{r["backend"]}:{r["path"]}:{r["method"]}'
            if live is True and key not in best:
                best[key] = rec
            if i % 100 == 0:
                print(f"  {i}/{len(jobs)}")

    out = {
        "route_map": {k: {"fn": v["fn"], "method": v["method"], "path": v["path"], "base": v["base"], "prefix": v["prefix"]}
                      for k, v in best.items()},
        "raw": raw,
    }
    (HERE / "adfly_api/spec/route_map.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    total = len(ROWS)
    print(f"\n确定形态: {len(best)}/{total}")
    from collections import Counter
    c = Counter((v["backend"], v["base"], v["prefix"]) for v in best.values())
    for (backend, base, pre), n in sorted(c.items()):
        print(f"  {backend:12} base={base:10} prefix='{pre}'  {n}")
    nolive = [r for r in ROWS if f'{r["backend"]}:{r["path"]}:{r["method"]}' not in best]
    print(f"\n未确定({len(nolive)}):")
    for r in nolive[:25]:
        print(f'  {r["backend"]:12} {r["method"]:5} {r["path"]}')


if __name__ == "__main__":
    main()
