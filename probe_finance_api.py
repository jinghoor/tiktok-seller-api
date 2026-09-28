#!/usr/bin/env python3
"""财务接口批量探测 —— 零打扰。

不新建标签、不点击、不移动鼠标、不抢焦点：
借操作员**已经打开**的、与目标同源的页面，在页内用 `fetch()` 打接口。
`fetch` 天然带 cookie、同源、且后台标签也能跑（只有 timer 会被节流，fetch 不会）。

探测判据：
  code=0                      → ✅ 存在且当前参数能过
  参数类错误(98001004/命名参数) → ◐ 存在，缺参数
  404 / Not Found             → ✗ 路径或版本不对（会自动再试 v2）
  其它 code                   → 记录原值

用法：
  python3 probe_finance_api.py local     # 本土 SHOP_LOCAL（CDP_PORT）
  python3 probe_finance_api.py cb        # 跨境 SHOP_XBORDER（CDP_PORT）
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
WHICH = sys.argv[1] if len(sys.argv) > 1 else "local"

TARGETS = {
    "local": {
        "port": CDP_PORT,
        # 借这个已打开的页做 fetch 源（同源 = seller-vn.tiktok.com）
        "origin_page": "seller-vn.tiktok.com/homepage",
        "origin": "https://seller-vn.tiktok.com",
        "q": ("aid=4068&app_id=4068&app_name=i18n_ecom_shop&device_platform=web"
              "&oec_seller_id=7494XXXXXXXXXX00&seller_id=7494XXXXXXXXXX00"
              "&locale=zh-CN&language=zh-CN"),
    },
    "cb": {
        "port": CDP_PORT,
        "origin_page": "/finance/bills",
        # ★ 跨境的 API 在**独立域**，不是页面域 —— 拿页面域 fetch 会落到 SPA 回退（返回 HTML）
        "origin": "https://api16-normal-sg.tiktokshopglobalselling.com",
        "q": ("aid=6556&app_id=6556&app_name=i18n_ecom_shop&device_platform=web"
              "&oec_seller_id=7494XXXXXXXXXX00&seller_id=7494XXXXXXXXXX00"
              "&locale=zh-CN&language=zh-CN"),
    },
}
IS_FIN = re.compile(r"^/api/v1/finance/|^/api/v1/pay/|^/api/v1/tax/|^/widget/api/v1/(pay|tax)/|"
                    r"^/api/oec/pay/|^/api/oec/finance/|cross_border/deposit/")
# 明显是写操作 / 会建任务的，只探不触发（避免在操作员账号里留垃圾任务）
SKIP_WRITE = re.compile(r"/(create|submit|pay|recharge|apply|accept|bind_card|init_agreement|"
                        r"cancel|update|set_|upload|declare|freeze|withdraw|retry|resolve|save_)",
                        re.I)

JS = """async (jobs) => {
  const out = [];
  for (const j of jobs) {
    try {
      const opt = { method: j.m, credentials: 'include',
                    headers: { 'content-type': 'application/json; charset=utf-8',
                               'accept': 'application/json' } };
      if (j.m !== 'GET' && j.body !== undefined) opt.body = JSON.stringify(j.body);
      const r = await fetch(j.url, opt);
      const t = await r.text();
      let code = null, msg = '';
      try { const d = JSON.parse(t); code = d.code; msg = String(d.message || '').slice(0, 90); }
      catch (e) { msg = t.replace(/\\s+/g, ' ').slice(0, 70); }
      out.push({ path: j.path, m: j.m, http: r.status, code, msg });
    } catch (e) {
      out.push({ path: j.path, m: j.m, http: 0, code: null, msg: String(e).slice(0, 70) });
    }
  }
  return JSON.stringify(out);
}"""


def main():
    from playwright.sync_api import sync_playwright
    cfg = TARGETS[WHICH]
    rows = json.loads((HERE / "notes" / "api_inventory" / "finance_paths.json")
                      .read_text(encoding="utf-8"))
    fin = [r for r in rows if IS_FIN.search(r["path"])]
    print(f"[{WHICH}] 财务接口 {len(fin)} 个，端口 {cfg['port']}")

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{cfg['port']}")
        ctx = b.contexts[0]
        n0 = len(ctx.pages)
        pg = next((p for p in ctx.pages if cfg["origin_page"] in p.url), None)
        if pg is None:
            print(f"  ✗ 找不到已打开的 {cfg['origin_page']} 页；现有：")
            for p in ctx.pages:
                print(f"      {p.url[:90]}")
            return
        print(f"  借用页面 {pg.url[:80]}")
        print(f"  当前页面数 {n0}（本脚本不会新建任何标签）")

        jobs, skipped = [], []
        for r in fin:
            if SKIP_WRITE.search(r["path"]):
                skipped.append(r["path"]); continue
            m = r["method"] if r["method"] in ("GET", "POST") else "GET"
            jobs.append({"path": r["path"], "m": m,
                         "url": f"{cfg['origin']}{r['path']}?{cfg['q']}",
                         "body": {} if m == "POST" else None})
        print(f"  探测 {len(jobs)} 个（跳过写操作 {len(skipped)} 个）\n")

        res, B = [], 25
        for i in range(0, len(jobs), B):
            chunk = jobs[i:i + B]
            try:
                res += json.loads(pg.evaluate(JS, chunk))
            except Exception as e:
                print(f"  批次 {i} 失败 {str(e)[:110]}")
            print(f"    {min(i+B, len(jobs))}/{len(jobs)}", flush=True)

        # 404 的再试 v2
        retry = []
        for r in res:
            if r["http"] == 404 or "Not Found" in (r["msg"] or ""):
                if "/v1/" in r["path"]:
                    retry.append({"path": r["path"].replace("/v1/", "/v2/"), "m": r["m"],
                                  "url": f"{cfg['origin']}{r['path'].replace('/v1/','/v2/')}?{cfg['q']}",
                                  "body": {} if r["m"] == "POST" else None})
        if retry:
            print(f"\n  404 的 {len(retry)} 个再试 v2 …")
            for i in range(0, len(retry), B):
                try:
                    res += json.loads(pg.evaluate(JS, retry[i:i + B]))
                except Exception:
                    pass

        def badge(r):
            if r["code"] == 0:
                return "✅"
            if r["http"] == 404 or "Not Found" in (r["msg"] or ""):
                return "✗"
            if r["code"] is not None:
                return "◐"
            return "?"
        for r in res:
            r["badge"] = badge(r)
        res.sort(key=lambda r: (r["badge"] != "✅", r["badge"] != "◐", r["path"]))
        cnt = {}
        for r in res:
            cnt[r["badge"]] = cnt.get(r["badge"], 0) + 1
        print(f"\n结果: " + "  ".join(f"{k}={v}" for k, v in sorted(cnt.items())))
        for r in res:
            print(f"  {r['badge']} http={r['http']} code={r['code']} {r['m']:4} {r['path']}"
                  + (f"   {r['msg'][:60]}" if r["msg"] else ""))
        print(f"\n(跳过写操作 {len(skipped)} 个: {skipped[:8]}…)")
        out = HERE / "notes" / f"finance_probe_{WHICH}.json"
        out.write_text(json.dumps({"target": WHICH, "results": res, "skipped": skipped},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {out.name}")
        print(f"页面数核对: {len(ctx.pages)}（开始 {n0}）")


if __name__ == "__main__":
    main()
