#!/usr/bin/env python3
"""抓财务页的真实网络请求 → notes/api_inventory/finance_live.json

为什么必须抓真流量：财务接口的主机是**运行时拼出来的**
（`api16-normal-{region}.tiktokshopglobalselling.com`），静态读 bundle 推不出来；
而且一批 `method:a.UD` 的接口到底是 GET 还是 POST，也只有真请求能确定。

纪律（之前踩过"开了 10 个重复标签页"的坑）：
  - 只用 Playwright 的 `ctx.new_page()`，它登记在 `ctx.pages` 里，收得回来
  - **不用** `Target.createTarget({newWindow:true})`
  - 不开前台、不碰操作员已开的标签页
  - finally 里一定 close，并核对页面数回到原值
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PAGES = [
    ("bills", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview&shop_region=VN"),
    ("deposit", "https://seller.tiktokshopglobalselling.com/deposit?shop_region=VN"),
    ("bill-payment", "https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN"),
]
DWELL = 14  # 秒，等页面把首屏接口打完


def main():
    from playwright.sync_api import sync_playwright
    out: dict = {}
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://127.0.0.1:CDP_PORT")
        ctx = b.contexts[0]
        before = len(ctx.pages)
        print(f"连接前页面数 {before}")
        for name, url in PAGES:
            pg = None
            caps: list[dict] = []

            def on_req(req, _caps=caps):
                u = req.url
                if "/api/" in u or "/widget/api/" in u:
                    _caps.append({"method": req.method, "url": u,
                                  "post": (req.post_data or "")[:400]})

            def on_resp(resp, _caps=caps):
                u = resp.url
                if "/api/" in u or "/widget/api/" in u:
                    _caps.append({"response": resp.status, "url": u})

            try:
                pg = ctx.new_page()
                pg.on("request", on_req)
                pg.on("response", on_resp)
                pg.goto(url, wait_until="domcontentloaded", timeout=45000)
                print(f"\n=== {name}: 已加载，等待 {DWELL}s 收首屏请求…")
                time.sleep(DWELL)
                # 滚一下触发懒加载区块
                try:
                    for _ in range(3):
                        pg.mouse.wheel(0, 1200)
                        time.sleep(1.5)
                    time.sleep(4)
                except Exception:
                    pass
            except Exception as e:
                print(f"  ✗ {str(e)[:160]}")
            finally:
                if pg is not None:
                    try:
                        pg.close()
                    except Exception:
                        pass
                time.sleep(1)

            reqs = [c for c in caps if "method" in c]
            hosts = sorted({c["url"].split("/api/")[0] for c in reqs})
            print(f"  捕获 {len(reqs)} 个请求 / 主机 {hosts}")
            out[name] = {"page": url, "count": len(reqs), "hosts": hosts,
                         "requests": reqs, "all": caps}
            # 去重打印
            seen = set()
            for c in reqs:
                key = (c["method"], c["url"].split("?")[0])
                if key in seen:
                    continue
                seen.add(key)
                p = c["url"].split("?")[0]
                if "/api/" in p:
                    p = "/api/" + p.split("/api/", 1)[1]
                print(f"    {c['method']:5} {p}")

        after = len(ctx.pages)
        print(f"\n关闭后页面数 {after}（连接前 {before}）—— "
              f"{'✅ 已复原' if after <= before else '⚠ 有残留，需人工确认'}")
        (HERE / "notes" / "api_inventory" / "finance_live.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        tot = sum(v["count"] for v in out.values())
        print(f"共 {tot} 个请求 → notes/api_inventory/finance_live.json")


if __name__ == "__main__":
    main()
