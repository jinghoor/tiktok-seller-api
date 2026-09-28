#!/usr/bin/env python3
"""性能基线:量化路由探测开销、连接复用收益、并发表现。

    python3 bench.py            # 跑全部
    python3 bench.py probe      # 只量化探测开销
    python3 bench.py lat        # 只测延迟
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api import AdflyClient  # noqa: E402
from adfly_api.transport import Transport  # noqa: E402

EP = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())


def measure_probe_overhead() -> None:
    """统计:清空路由缓存后,跑 N 个不同路径需要多少额外探测请求。"""
    print("=== 探测开销 ===")
    for n in (10, 20):
        routes_path = HERE / "adfly_api/spec/routes.json"
        backup = routes_path.read_text() if routes_path.exists() else None
        if routes_path.exists():
            routes_path.unlink()

        counter = {"probe": 0, "real": 0}
        t = Transport(state_path=HERE / "adfly_api/.session.json")
        orig_probe = t._probe_one

        def counting_probe(url):
            counter["probe"] += 1
            return orig_probe(url)

        t._probe_one = counting_probe  # type: ignore[assignment]

        sample = [r for r in EP if r["method"] == "POST" and not r["path"].startswith("/ai_agent")][:n]
        t0 = time.time()
        for r in sample:
            try:
                t.request("POST", r["path"], json_body={}, group=r["backend"])
            except Exception:
                pass
        dt = time.time() - t0
        print(f"  {n:3} 个不同路径: 探测 {counter['probe']:3} 次 / 业务请求 {n} 次 "
              f"→ 放大 {counter['probe']/max(n,1):.2f}x, 耗时 {dt:.1f}s")

        # 二次调用(已缓存)应该零探测
        counter["probe"] = 0
        t0 = time.time()
        for r in sample:
            try:
                t.request("POST", r["path"], json_body={}, group=r["backend"])
            except Exception:
                pass
        print(f"       缓存后重跑: 探测 {counter['probe']} 次, 耗时 {time.time()-t0:.1f}s")

        if backup:
            routes_path.write_text(backup)


def measure_latency() -> None:
    print("\n=== 延迟 ===")
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    body = {"page": 1, "page_size": 5}
    # 冷启动(含首次路由探测)
    t0 = time.time()
    c.ads.get_gmv_max_list(body)
    cold = (time.time() - t0) * 1000
    # 热路径
    warm = []
    for _ in range(20):
        t0 = time.time()
        c.ads.get_gmv_max_list(body)
        warm.append((time.time() - t0) * 1000)
    print(f"  GMVmax 列表  冷启动 {cold:.0f}ms  热路径 "
          f"p50={statistics.median(warm):.0f}ms  min={min(warm):.0f}ms  max={max(warm):.0f}ms")

    # 连接复用:同一会话 vs 每次都新建
    import requests
    url = "https://front-v1.aiadfly.com/front_api/tiktok/gmv_max/list"
    hdrs = c.t._headers({"Content-Type": "application/json; charset=UTF-8;"})
    t0 = time.time()
    for _ in range(10):
        requests.post(url, json=body, headers=hdrs, timeout=15)
    fresh = (time.time() - t0) / 10 * 1000
    t0 = time.time()
    for _ in range(10):
        c.t.http.post(url, json=body, headers=hdrs, timeout=15)
    pooled = (time.time() - t0) / 10 * 1000
    print(f"  连接复用  每次新建 {fresh:.0f}ms  复用会话 {pooled:.0f}ms  "
          f"省 {(1 - pooled/fresh)*100:.0f}%" if fresh else "")


def measure_concurrency() -> None:
    print("\n=== 并发 ===")
    import concurrent.futures as cf
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    c.ads.get_gmv_max_list({"page": 1, "page_size": 5})  # 预热路由

    def call(_i):
        t0 = time.time()
        try:
            c.ads.get_gmv_max_list({"page": 1, "page_size": 5})
            return time.time() - t0, None
        except Exception as e:
            return time.time() - t0, type(e).__name__

    for workers in (1, 8, 16, 32):
        t0 = time.time()
        with cf.ThreadPoolExecutor(workers) as ex:
            res = list(ex.map(call, range(64)))
        dt = time.time() - t0
        errs = sum(1 for _, e in res if e)
        lat = sorted(r for r, _ in res)
        print(f"  并发 {workers:3}: 64 请求 {dt:.1f}s  {64/dt:.0f} rps  "
              f"p50={lat[len(lat)//2]*1000:.0f}ms  p95={lat[int(len(lat)*0.95)]*1000:.0f}ms  错误={errs}")


def measure_prewarm() -> None:
    """对比:逐条冷启动 vs prewarm 批量预热。"""
    print("\n=== 路由预热 ===")
    from adfly_api.spec import load_endpoints

    routes_path = HERE / "adfly_api/spec/routes.json"
    backup = routes_path.read_text() if routes_path.exists() else None

    # A: 不预热,逐条跑 30 个不同路径
    if routes_path.exists():
        routes_path.unlink()
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    sample = [r for r in load_endpoints() if r["backend"] in ("advertise", "front")
              and r["method"] == "POST" and "export" not in r["path"]][:30]
    t0 = time.time()
    for r in sample:
        try:
            c.call(r["backend"], r["method"], r["path"], {"page": 1, "page_size": 5})
        except Exception:
            pass
    lazy = time.time() - t0
    lazy_stats = dict(c.t.stats)

    # B: 先 prewarm(并行),再跑
    if routes_path.exists():
        routes_path.unlink()
    c2 = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    t0 = time.time()
    c2.prewarm(workers=10)
    warm_ms = (time.time() - t0) * 1000
    t0 = time.time()
    for r in sample:
        try:
            c2.call(r["backend"], r["method"], r["path"], {"page": 1, "page_size": 5})
        except Exception:
            pass
    warm = time.time() - t0

    print(f"  逐条懒解析 30 路径: {lazy:.1f}s  (探测 {lazy_stats['probes']} 次)")
    print(f"  prewarm 全量 293 条: {warm_ms:.0f}ms 后跑同 30 路径: {warm:.1f}s  "
          f"(探测 {c2.t.stats['probes']} 次)")
    if backup:
        routes_path.write_text(backup)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "probe"):
        measure_probe_overhead()
    if what in ("all", "prewarm"):
        measure_prewarm()
    if what in ("all", "prewarm"):
        measure_prewarm()
    if what in ("all", "lat"):
        measure_latency()
    if what in ("all", "conc"):
        measure_concurrency()
