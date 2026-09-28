#!/usr/bin/env python3
"""路由存在性全量测绘 —— **不需要有效登录**。

## 原理

网关的匹配顺序是 **先路由、后鉴权**。所以会话过期时：

| 响应 | 含义 |
|---|---|
| `98001002 请登录`（或任何业务 code / binding 错误） | **路由存在** —— 请求打到了业务层 |
| `No matching route` | **路由不存在** —— 网关注册表里没有 |
| `404`（HTML/TLB） | 也不存在，但来自更外层网关 |

于是即使会话失效，也能拿到一张**权威的路由存在性地图**。

## 用法

  python3 map_route_existence.py --shop tk89 --limit 500
  python3 map_route_existence.py --shop tk89 --all        # 全量（约 15 分钟）
  python3 map_route_existence.py --shop tk56 --domain "履约 / 物流 / 面单"
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tk01_config as CFG  # noqa: E402

JS = """async (jobs) => {
  const out = [];
  for (const j of jobs) {
    try {
      const opt = { method: j.m, credentials: 'include',
                    headers: { 'content-type': 'application/json; charset=utf-8' } };
      if (j.m !== 'GET') opt.body = '{}';
      const r = await fetch(j.url, opt);
      const t = await r.text();
      out.push({ path: j.path, m: j.m, http: r.status, body: t.slice(0, 160) });
    } catch (e) {
      out.push({ path: j.path, m: j.m, http: 0, body: String(e).slice(0, 60) });
    }
  }
  return JSON.stringify(out);
}"""


def verdict(r) -> str:
    b = r.get("body") or ""
    if "No matching route" in b:
        return "✗ 路由不存在"
    if r.get("http") == 404 or "<html" in b.lower() or "404 Not Found" in b:
        return "✗ 404（外层网关）"
    if r.get("http") == 0:
        return "? 请求失败"
    # 只要不是"无此路由/404"，就说明路由匹配成功了
    code = None
    m = re.search(r'"code"\s*:\s*(-?\d+)', b)
    if m:
        code = m.group(1)
    if code == "0":
        return "✅ 通"
    if code == "98001002":
        return "◐ 路由存在（需登录）"
    if "binding:" in b:
        return "◐ 路由存在（缺 body）"
    if code:
        return f"◐ 路由存在（code={code}）"
    if "请登录" in b:
        return "◐ 路由存在（需登录）"
    return "? 其它"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shop", default="tk89")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright
    shop = CFG.load_shop(a.shop)
    key, port = shop["_key"], shop["cdp_port"]
    is_local = "tiktokshopglobalselling" not in shop["seller_origin"]
    api_base = shop["seller_origin"] if is_local else shop["api_host"]
    sid, aid = shop["seller_id"], shop["aid"]
    q = (f"aid={aid}&app_id={aid}&app_name=i18n_ecom_shop&device_platform=web"
         f"&oec_seller_id={sid}&seller_id={sid}&locale=zh-CN&language=zh-CN")

    master = json.loads((HERE / "notes" / "api_inventory" / "master.json")
                        .read_text(encoding="utf-8"))
    rows = [(p, v) for p, v in master.items() if not a.domain or v["domain"] == a.domain]
    rows.sort()
    if not a.all:
        rows = rows[a.offset:a.offset + a.limit]
    print(f"[{key}] 测绘 {len(rows)} 个路由  base={api_base}")

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        ctx = b.contexts[0]
        n0 = len(ctx.pages)
        pg = next((p for p in ctx.pages if p.url.startswith(shop["seller_origin"])), None)
        if pg is None:
            print(f"  ✗ 没有 {shop['seller_origin']} 下已打开的页面")
            for p in ctx.pages:
                print(f"      {p.url[:80]}")
            return
        print(f"  借用 {pg.url[:76]}（页面数 {n0}，不新建）")

        jobs = [{"path": p,
                 "m": (v["method"] if v["method"] in ("GET", "POST") else "POST"),
                 "url": f"{api_base}{p}?{q}"} for p, v in rows]
        res = []
        for i in range(0, len(jobs), a.batch):
            try:
                res += json.loads(pg.evaluate(JS, jobs[i:i + a.batch]))
            except Exception as e:
                print(f"    批次 {i} 失败 {str(e)[:80]}")
            if (i // a.batch) % 8 == 0:
                print(f"    {min(i+a.batch, len(jobs))}/{len(jobs)}", flush=True)
        for r in res:
            r["v"] = verdict(r)
        c = collections.Counter(r["v"] for r in res)
        print(f"\n结果:")
        for k, v in c.most_common():
            print(f"  {v:>5}  {k}")
        exists = sum(v for k, v in c.items() if k.startswith("◐") or k.startswith("✅"))
        print(f"\n★ 路由存在 {exists}/{len(res)} = {exists*100//max(1,len(res))}%")

        tag = a.tag or f"{key}_routes"
        f = HERE / "notes" / f"route_map_{tag}.json"
        f.write_text(json.dumps({"shop": key, "base": api_base, "results": res},
                                ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {f.name}")
        print(f"页面数核对: {len(ctx.pages)}（开始 {n0}）")


if __name__ == "__main__":
    main()
