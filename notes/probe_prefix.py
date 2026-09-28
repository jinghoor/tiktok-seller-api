#!/usr/bin/env python3
"""对上轮 miss 的路径做前缀搜索,找出网关下的真实形态。"""
from __future__ import annotations
import concurrent.futures as cf, json, ssl, urllib.request, urllib.error
from pathlib import Path
import certifi

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "adfly_api/spec/route_probe.json").read_text())
CTX = ssl.create_default_context(cafile=certifi.where())
HEAD = {"Content-Type": "application/json; charset=UTF-8;", "lang": "zh-CN",
        "country": "CN", "CompanyExID": "10017794444062955153"}
GW = "https://front-v1.aiadfly.com/front_api"

PREFIXES = ["", "finance/", "finance_bff/", "advertise/", "advertise_bff/", "automation/",
            "ai_agent/", "back_api/", "bff/", "pay/", "wallet/", "ad/", "mcp/"]

# 每后端只挑前 6 个 miss 路径,避免请求爆炸
targets: dict[str, list[str]] = {}
for r in rows:
    if r["base"] == "gw" and r["live"] is False:
        targets.setdefault(r["backend"], [])
        if r["path"] not in targets[r["backend"]] and len(targets[r["backend"]]) < 6:
            targets[r["backend"]].append(r["path"])


def probe(url: str, method: str) -> tuple[str, str]:
    req = urllib.request.Request(url, data=b"{}" if method == "POST" else None, headers=HEAD, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8, context=CTX) as r:
            return "200", r.read().decode("utf-8", "replace")[:120].replace("\n", " ")
    except urllib.error.HTTPError as e:
        return str(e.code), e.read().decode("utf-8", "replace")[:120].replace("\n", " ")
    except Exception as e:
        return "ERR", type(e).__name__


def main() -> None:
    jobs = []
    for backend, paths in targets.items():
        for p in paths:
            for pre in PREFIXES:
                jobs.append((backend, p, pre))
    print(f"搜索 {len(jobs)} 个组合…")
    hits: dict[str, list] = {}
    with cf.ThreadPoolExecutor(16) as ex:
        futs = {ex.submit(probe, GW + "/" + pre + p.lstrip("/"), "POST"): (b, p, pre) for b, p, pre in jobs}
        for f in cf.as_completed(futs):
            backend, path, pre = futs[f]
            status, body = f.result()
            if "page not found" in body or status == "ERR":
                continue
            hits.setdefault(backend, []).append({"path": path, "prefix": pre, "status": status, "raw": body[:100]})
    (HERE / "adfly_api/spec/prefix_probe.json").write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    for backend, found in hits.items():
        print(f"\n## {backend}")
        for h in found[:10]:
            print(f"   prefix='{h['prefix']}' -> {h['path']}  {h['raw'][:70]}")
    missing = [b for b in targets if b not in hits]
    print("\n完全找不到前缀的后端:", missing)


if __name__ == "__main__":
    main()
