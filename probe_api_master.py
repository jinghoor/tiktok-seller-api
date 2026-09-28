#!/usr/bin/env python3
"""借已打开页面批量探测全量接口状态 —— 零打扰。

从 `notes/api_inventory/master.json` 读全量清单，按业务域/优先级筛选，
在页面里用 `fetch()` 批量打，按响应分类归档。

**零打扰**：不新建标签、不点击、不移动鼠标、不抢焦点。借操作员**已打开**的
同源页面做 fetch 源即可 —— API 与页面无关，任何同源页都能打。

分类判据：
  code=0                     ✅ 通
  invalid params / 填写错误   ◐ 缺参数（接口存在）
  98001002 请登录             🔑 需额外鉴权
  No matching route          🚫 该店/该网关无此路由
  404 / Not Found            ✗ 路径或版本不对（会自动重试 v2）
  其它                       记录原值

用法：
  python3 probe_api_master.py --shop tk89 --domain "数据 / 罗盘 / 报表" --limit 200
  python3 probe_api_master.py --shop tk89 --p0                 # 只探 P0 域
  python3 probe_api_master.py --shop tk01 --domain "商品 / 库存 / 定价"
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tk01_config as CFG  # noqa: E402

P0_DOMAINS = ["数据 / 罗盘 / 报表", "商品 / 库存 / 定价", "履约 / 物流 / 面单",
              "商家 / 入驻 / 资质", "营销 / 促销", "订单 / 售后"]
P1_DOMAINS = P0_DOMAINS + ["内容创作 / 视频中心", "学习中心 / 内容",
                           "治理 / 违规 / 申诉", "交易（/trade 前缀，另一套）"]

# 写操作默认跳过（避免在账号里造成副作用）
WRITE_RX = re.compile(
    r"/(create|submit|update|set|save|delete|remove|add|apply|accept|cancel|pay|recharge|"
    r"upload|declare|freeze|withdraw|retry|resolve|bind|unbind|confirm|modify|edit|publish|"
    r"batch_|bulk_|import|sync|send|push|mark_|activate|deactivate|enable|disable|reset)",
    re.I)

JS = """async (jobs) => {
  const out = [];
  for (const j of jobs) {
    try {
      const opt = { method: j.m, credentials: 'include',
                    headers: { 'content-type': 'application/json; charset=utf-8',
                               'accept': 'application/json, text/plain, */*' } };
      if (j.m !== 'GET' && j.body !== undefined && j.body !== null)
        opt.body = JSON.stringify(j.body);
      const r = await fetch(j.url, opt);
      const t = await r.text();
      let code = null, msg = '';
      try { const d = JSON.parse(t); code = d.code; msg = String(d.message || '').slice(0, 80); }
      catch (e) { msg = t.replace(/\\s+/g, ' ').slice(0, 50); }
      out.push({ path: j.path, m: j.m, http: r.status, code, msg });
    } catch (e) {
      out.push({ path: j.path, m: j.m, http: 0, code: null, msg: String(e).slice(0, 60) });
    }
  }
  return JSON.stringify(out);
}"""


def classify(r) -> str:
    if r.get("code") == 0:
        return "✅ 通"
    m = r.get("msg") or ""
    # ★ 绑定错误 oracle：`binding: expr_path=<字段>, cause=missing required`
    #   http=400 且不返回 JSON code —— 说明**接口存在且可达**，只是缺 body 字段。
    #   早期把它归成 `?`（无法识别），157 个里 151 个都是这个，严重低估了覆盖率。
    if "binding:" in m and "missing required" in m:
        fld = ""
        mm = __import__("re").search(r"expr_path=([A-Za-z0-9_.\[\]]+)", m)
        if mm:
            fld = f"({mm.group(1)})"
        return f"◐ 缺 body{fld}"
    if "No matching route" in m:
        return "🚫 无此路由"
    if "请登录" in m or r.get("code") in (98001002,):
        return "🔑 需鉴权"
    if any(k in m for k in ("invalid params", "填写错误", "Invalid parameters", "invalid param",
                            "is required", "param")):
        return "◐ 缺参数"
    if "404" in m or r.get("http") == 404:
        return "✗ 404"
    if r.get("code") is None:
        return "?"
    return f"其它({r['code']})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shop", default=None)
    ap.add_argument("--domain", action="append", default=None)
    ap.add_argument("--p0", action="store_true")
    ap.add_argument("--p1", action="store_true")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--include-writes", action="store_true")
    ap.add_argument("--tag", default=None, help="输出文件名后缀")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright

    shop = CFG.load_shop(a.shop)
    key = shop["_key"]
    port = shop["cdp_port"]
    is_local = "tiktokshopglobalselling" not in shop["seller_origin"]
    api_base = shop["seller_origin"] if is_local else shop["api_host"]
    sid, aid = shop["seller_id"], shop["aid"]
    q = (f"aid={aid}&app_id={aid}&app_name=i18n_ecom_shop&device_platform=web"
         f"&oec_seller_id={sid}&seller_id={sid}&locale=zh-CN&language=zh-CN")

    master = json.loads((HERE / "notes" / "api_inventory" / "master.json")
                        .read_text(encoding="utf-8"))
    want = a.domain
    if a.p0:
        want = P0_DOMAINS
    if a.p1:
        want = P1_DOMAINS
    rows = [p for p, v in master.items()
            if (not want or v["domain"] in want)
            and (a.include_writes or not WRITE_RX.search(p))]
    rows = sorted(rows)[a.offset:a.offset + a.limit]
    print(f"[{key}] 目标 {len(rows)} 个接口  api_base={api_base}")

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        ctx = b.contexts[0]
        n0 = len(ctx.pages)
        pg = next((p for p in ctx.pages
                   if p.url.startswith(shop["seller_origin"])), None)
        if pg is None:
            print(f"  ✗ 没有 {shop['seller_origin']} 下已打开的页面。现有：")
            for p in ctx.pages:
                print(f"      {p.url[:88]}")
            return
        print(f"  借用 {pg.url[:78]}   （页面数 {n0}，全程不新建）")

        jobs = [{"path": p,
                 "m": (master[p]["method"] if master[p]["method"] in ("GET", "POST") else "GET"),
                 "url": f"{api_base}{p}?{q}"} for p in rows]
        for j in jobs:
            j["body"] = {} if j["m"] == "POST" else None

        res = []
        for i in range(0, len(jobs), a.batch):
            try:
                res += json.loads(pg.evaluate(JS, jobs[i:i + a.batch]))
            except Exception as e:
                print(f"    批次 {i} 失败 {str(e)[:90]}")
            print(f"    {min(i+a.batch, len(jobs))}/{len(jobs)}", flush=True)

        # 404 的试 v2
        retry = [{"path": r["path"].replace("/v1/", "/v2/"), "m": r["m"],
                  "url": f"{api_base}{r['path'].replace('/v1/','/v2/')}?{q}",
                  "body": {} if r["m"] == "POST" else None}
                 for r in res if r.get("http") == 404 and "/v1/" in r["path"]]
        if retry:
            print(f"  404 的 {len(retry)} 个试 v2 …", flush=True)
            for i in range(0, len(retry), a.batch):
                try:
                    res += json.loads(pg.evaluate(JS, retry[i:i + a.batch]))
                except Exception:
                    pass

        for r in res:
            r["cls"] = classify(r)
        cnt = collections.Counter(r["cls"] for r in res)
        print(f"\n结果: " + "  ".join(f"{k}={v}" for k, v in cnt.most_common()))
        show = [r for r in res if r["cls"].startswith(("✅", "◐", "🔑"))]
        print(f"\n可用/存在 的 {len(show)} 个（按域内路径序）:")
        for r in sorted(show, key=lambda x: x["path"])[:a.limit]:
            extra = f"  {r['msg'][:44]}" if r["msg"] else ""
            print(f"  {r['cls']:8} {r['m']:4} {r['path']}{extra}")
        bad = [r for r in res if r["cls"].startswith(("✗", "🚫"))]
        print(f"\n不可用 {len(bad)} 个（前 20）:")
        for r in bad[:20]:
            print(f"  {r['cls']:8} {r['m']:4} {r['path']}")

        tag = a.tag or f"{key}_{'-'.join((want or ['all']))[:1][0]}"
        out = HERE / "notes" / f"probe_{tag}.json"
        out.write_text(json.dumps({"shop": key, "api_base": api_base,
                                   "domains": want, "results": res},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n→ {out.name}")
        print(f"页面数核对: {len(ctx.pages)}（开始 {n0}）")


if __name__ == "__main__":
    main()
