#!/usr/bin/env python3
"""探测 293 个接口在各候选 基础URL 下的真实可达性(无 token,看返回码)。

判定:
  code=2/400 WITHOUT_TOKEN / 401  -> 路由存在,仅缺鉴权  => LIVE
  404 page not found             -> 该前缀下无此路由    => MISS
  其它                            -> 记录原文
输出 spec/route_probe.json
"""
from __future__ import annotations
import concurrent.futures as cf, json, ssl, sys, urllib.request, urllib.error
from pathlib import Path
import certifi

HERE = Path(__file__).resolve().parent
ROWS = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
CTX = ssl.create_default_context(cafile=certifi.where())
COMPANY = "10017794444062955153"
HEAD = {"Content-Type": "application/json; charset=UTF-8;", "lang": "zh-CN",
        "country": "CN", "CompanyExID": COMPANY,
        "Origin": "https://ad.aiadfly.com", "Referer": "https://ad.aiadfly.com/"}

# 候选 base:
#  1) front 网关(广告/财务/资金都在这)
#  2) 自动化直连
#  3) ai_agent 直连
CANDIDATES = {
    "gw": "https://front-v1.aiadfly.com/front_api",
    "automation": "https://automation-v1.aiadfly.com/front_api",
    "ai_agent": "https://ai-agent-v1.aiadfly.com/ai_agent",
}


def one(base_key: str, path: str, method: str) -> dict:
    url = CANDIDATES[base_key] + path
    data = b"{}" if method == "POST" else None
    req = urllib.request.Request(url, data=data, headers=HEAD, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
            body = r.read().decode("utf-8", "replace")[:200]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
    except Exception as e:
        return {"base": base_key, "live": None, "raw": type(e).__name__}
    sq = body.replace("\n", " ")
    if "page not found" in sq:
        live = False
    elif '"code":2' in sq or "WITHOUT_TOKEN" in sq or '"code":401' in sq or '"code":400' in sq:
        live = True
    else:
        live = True  # 能返回业务 JSON 就算活着
    return {"base": base_key, "live": live, "raw": sq[:150]}


def main() -> None:
    jobs = []
    for r in ROWS:
        # 每个接口只试最可能的一个 base,减少请求量;ai_agent 段固定跑 ai_agent + gw
        bases = ["ai_agent", "gw"] if r["backend"] == "ai_agent" else (
            ["automation", "gw"] if r["backend"] == "automation" else ["gw"])
        for b in bases:
            jobs.append((b, r["path"], r["method"], r))
    print(f"探测 {len(jobs)} 次请求 (接口 {len(ROWS)} 个)…")
    out = []
    with cf.ThreadPoolExecutor(16) as ex:
        futs = {ex.submit(one, b, p, m): (b, p, m, r) for b, p, m, r in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            b, p, m, r = futs[f]
            res = f.result()
            out.append({**r, **res})
            if i % 60 == 0:
                print(f"  {i}/{len(jobs)}")
    (HERE / "adfly_api/spec/route_probe.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    live_by_base: dict[str, dict[str, int]] = {}
    for o in out:
        d = live_by_base.setdefault(o["base"], {"live": 0, "miss": 0, "err": 0})
        if o["live"] is True:
            d["live"] += 1
        elif o["live"] is False:
            d["miss"] += 1
        else:
            d["err"] += 1
    print("\n按 base 汇总:")
    for k, v in live_by_base.items():
        print(f"  {k:12} live={v['live']:4} miss={v['miss']:4} err={v['err']:3}")

    print("\n每个后端的可选 base(取 live 占比最高的):")
    for backend in sorted({r["backend"] for r in ROWS}):
        stats = {}
        for o in out:
            if o["backend"] != backend:
                continue
            s = stats.setdefault(o["base"], [0, 0, 0])
            s[0 if o["live"] is True else (1 if o["live"] is False else 2)] += 1
        print(f"  {backend:12} " + "  ".join(f"{b}:live={v[0]},miss={v[1]},err={v[2]}" for b, v in stats.items()))


if __name__ == "__main__":
    main()
