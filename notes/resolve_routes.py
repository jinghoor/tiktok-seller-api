#!/usr/bin/env python3
"""为每个接口确定真实 base,结果缓存到 spec/routes.json。

对每个接口按其 backend 的候选 host 列表逐个实测(无 token,看返回码),
能返回业务 JSON(非 "page not found")的即为正确 base。多命中时按候选顺序取第一个。

输出:
  spec/routes.json      fn -> {method, path, base_key}
  spec/routes_raw.json  全部探测记录
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import ssl
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import certifi

HERE = Path(__file__).resolve().parent
ROWS = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
CTX = ssl.create_default_context(cafile=certifi.where())
HEAD = {"Content-Type": "application/json; charset=UTF-8;", "lang": "zh-CN",
        "country": "CN", "CompanyExID": "10017794444062955153"}

# 服务根 + 网关前缀。路径本身已带 /ai_agent/ 段时必须打在根上,不能重复叠加。
BASES = {
    "front": "https://front-v1.aiadfly.com/front_api",
    "finance_bff": "https://finance-bff-v1.aiadfly.com/front_api",
    "finance": "https://finance-v1.aiadfly.com/front_api",
    "automation": "https://automation-v1.aiadfly.com/front_api",
    "ai_agent": "https://ai-agent-v1.aiadfly.com/ai_agent",
    "ai_agent_root": "https://ai-agent-v1.aiadfly.com",
    "mcp_open": "https://mcp-open.aiadfly.com",
}


def join(base_key: str, path: str) -> str:
    base = BASES[base_key]
    p = "/" + path.lstrip("/")
    # /ai_agent/xxx 这类自带前缀的路径,打在服务根上
    if base.endswith("/ai_agent") and p.startswith("/ai_agent/"):
        return base[: -len("/ai_agent")] + p
    return base + p

# 候选顺序:浏览器实测到的优先
CANDIDATES = {
    "front": ["front", "finance_bff", "finance", "automation"],
    "advertise": ["front", "finance_bff"],
    "finance_bff": ["finance_bff", "front"],
    "finance": ["finance", "front"],
    "automation": ["automation", "front"],
    "ai_agent": ["ai_agent", "ai_agent_root"],
    "mcp_open": ["mcp_open"],
}


def probe(base_key: str, path: str, method: str) -> tuple[bool | None, str]:
    url = join(base_key, path)
    req = urllib.request.Request(url, data=b"{}" if method == "POST" else None, headers=HEAD, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")[:160]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:160]
    except Exception as exc:
        return None, type(exc).__name__
    sq = body.replace("\n", " ")
    return ("page not found" not in sq), sq


def main() -> None:
    jobs = []
    for r in ROWS:
        for base_key in CANDIDATES.get(r["backend"], ["front"]):
            jobs.append((base_key, r))
    print(f"探测 {len(jobs)} 次(接口 {len(ROWS)})…")

    best: dict[str, dict] = {}
    raw = []
    with cf.ThreadPoolExecutor(20) as ex:
        futs = {ex.submit(probe, b, r["path"], r["method"]): (b, r) for b, r in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            b, r = futs[f]
            live, body = f.result()
            raw.append({"fn": r["fn"], "backend": r["backend"], "method": r["method"],
                        "path": r["path"], "base": b, "live": live, "raw": body[:120]})
            if live is True:
                best.setdefault(r["fn"], {"fn": r["fn"], "backend": r["backend"], "method": r["method"],
                                          "path": r["path"], "base": b})
            if i % 150 == 0:
                print(f"  {i}/{len(jobs)}")

    (HERE / "adfly_api/spec/routes.json").write_text(json.dumps(best, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "adfly_api/spec/routes_raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n确定: {len(best)}/{len(ROWS)}")
    for (backend, base), n in sorted(Counter((v["backend"], v["base"]) for v in best.values()).items()):
        print(f"  {backend:12} -> {base:12} {n}")
    missing = [r for r in ROWS if r["fn"] not in best]
    print(f"\n未确定 {len(missing)}:")
    for r in missing[:30]:
        print(f'  {r["backend"]:12} {r["method"]:5} {r["path"]}')


if __name__ == "__main__":
    main()
