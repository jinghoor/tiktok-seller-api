#!/usr/bin/env python3
"""本土店（seller-vn.tiktok.com）财务板块爬取 —— 全程在该容器浏览器内完成。

为什么必须"在浏览器内"：`seller-vn.tiktok.com` 直连和 SOCKS5 都是 000（连不上），
走本地代理是 302。而容器浏览器自己带正确的出口 + cookie —— 所以：
  · 页面 HTML / JS 用 `page.evaluate(fetch)` 在页内取（同源、带 cookie）
  · 接口用 CDP 网络监听抓真实请求（主机名是运行时拼的，静态读不出来）

纪律：只用 `ctx.new_page()`（登记在 ctx.pages 里），一次一个，finally 必关，
      结束核对页面数回到原值。默认端口 CDP_PORT = TK89_Local_Shop argv[1] 覆盖）。
★ 别用 CDP_PORT —— 那是另一个容器，只有过期的 seller-vn cookie，会误判成"未登录"。
"""
from __future__ import annotations

import base64
import json
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
PAGES = [
    ("transactions", "https://seller-vn.tiktok.com/finance/transactions?shop_region=VN&tab=settled_tab"),
    ("withdraw-new", "https://seller-vn.tiktok.com/finance/withdraw-new?shop_region=VN"),
    ("invoice", "https://seller-vn.tiktok.com/finance/invoice?shop_region=VN"),
]
DWELL = 16
OUT_HTML = HERE / "notes" / "vn_local"
OUT_JS = OUT_HTML / "js"


def main():
    from playwright.sync_api import sync_playwright
    OUT_HTML.mkdir(parents=True, exist_ok=True)
    OUT_JS.mkdir(parents=True, exist_ok=True)
    report: dict = {}

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]
        before = len(ctx.pages)
        print(f"[{PORT}] 连接前页面数 {before}")
        # 先拿店铺身份
        shop_id = None
        try:
            pg0 = ctx.pages[0]
            ls = pg0.evaluate("() => JSON.stringify(Object.keys(localStorage).filter(k=>/finance_statement_config/.test(k)))")
            m = re.search(r"seller-vn\.tiktok\.com:(\d+):", ls or "")
            shop_id = m.group(1) if m else None
        except Exception:
            pass
        print(f"  本土店 shop_id = {shop_id}")
        report["shop_id"] = shop_id

        for name, url in PAGES:
            pg = None
            reqs: list[dict] = []
            try:
                pg = ctx.new_page()
                pg.on("request", lambda r, _c=reqs: _c.append(
                    {"method": r.method, "url": r.url, "post": (r.post_data or "")[:400]})
                    if "/api/" in r.url else None)
                pg.on("response", lambda r, _c=reqs: _c.append(
                    {"method": r.request.method, "url": r.url, "status": r.status})
                    if "/api/" in r.url else None)
                pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                if "/account/login" in pg.url or "/account/register" in pg.url:
                    raise RuntimeError(
                        f"会话失效：{url} 被重定向到 {pg.url.split('?')[0]} —— "
                        f"需要先在该容器里登录 seller-vn.tiktok.com")
                print(f"\n=== {name}: 已加载，等 {DWELL}s")
                time.sleep(DWELL)
                try:
                    for _ in range(3):
                        pg.mouse.wheel(0, 1400); time.sleep(1.6)
                    time.sleep(4)
                except Exception:
                    pass
                # 页面 HTML（页内取，同源）
                try:
                    html = pg.evaluate("() => document.documentElement.outerHTML")
                    (OUT_HTML / f"{name}.html").write_text(html, encoding="utf-8")
                except Exception as e:
                    print(f"    HTML ✗ {str(e)[:100]}")
                # 资源清单
                js = pg.evaluate("""() => JSON.stringify(
                    performance.getEntriesByType('resource')
                      .map(r=>r.name).filter(u=>/\\.js(\\?|$)/.test(u)))""")
                js_urls = json.loads(js)
                print(f"    JS 资源 {len(js_urls)} 个")
                # 在页内下载 JS（同源 + cookie），base64 回传
                got = 0
                for u in js_urls:
                    fn = OUT_JS / re.sub(r"[^A-Za-z0-9._-]", "_", u.split("//", 1)[-1])[-150:]
                    if fn.exists() and fn.stat().st_size > 0:
                        got += 1
                        continue
                    try:
                        b64 = pg.evaluate(
                            """async (u) => { const r = await fetch(u, {credentials:'include'});
                                 const b = await r.arrayBuffer(); const y = new Uint8Array(b);
                                 let s=''; for (let i=0;i<y.length;i+=8192)
                                   s += String.fromCharCode.apply(null, y.subarray(i,i+8192));
                                 return btoa(s); }""", u)
                        data = base64.b64decode(b64)
                        if data:
                            fn.write_bytes(data); got += 1
                    except Exception:
                        pass
                print(f"    已存 JS {got}/{len(js_urls)}")
            except Exception as e:
                print(f"  ✗ {name}: {str(e)[:180]}")
            finally:
                if pg is not None:
                    try:
                        pg.close()
                    except Exception:
                        pass
                time.sleep(1.2)

            seen, uniq = set(), []
            for r in reqs:
                if "method" not in r or "status" in r:
                    continue
                k = (r["method"], r["url"].split("?")[0])
                if k in seen:
                    continue
                seen.add(k); uniq.append(r)
            hosts = sorted({r["url"].split("/api/")[0] for r in uniq})
            print(f"    捕获 {len(uniq)} 个唯一请求 / 主机 {hosts}")
            for r in uniq:
                p = r["url"].split("?")[0]
                p = "/api/" + p.split("/api/", 1)[1] if "/api/" in p else p
                print(f"      {r['method']:5} {p}")
            report[name] = {"page": url, "hosts": hosts, "requests": uniq}

        after = len(ctx.pages)
        print(f"\n关闭后页面数 {after}（连接前 {before}）—— "
              f"{'✅ 已复原' if after <= before else '⚠ 有残留，需人工确认'}")
        report["_pages_before"] = before
        report["_pages_after"] = after
        (HERE / "notes" / "vn_local_live.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        tot = sum(len(v.get("requests", []))
                  for k, v in report.items()
                  if not k.startswith("_") and isinstance(v, dict))
        print(f"共 {tot} 个唯一请求 → notes/vn_local_live.json")


if __name__ == "__main__":
    main()
