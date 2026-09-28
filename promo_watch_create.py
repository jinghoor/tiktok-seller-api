#!/usr/bin/env python3
"""后台监听 promotion 的 create/update/submit 请求体，实时落盘。

v2: 挂载【所有】promotion 页面，并每 3 秒扫描新开的 tab 自动挂载。

上一版只复用一个已有 tab —— 结果 operator 在另一个页面操作，一条都没抓到。
Playwright 的 Page 对象可哈希，直接拿它当 dict key 判断是否已挂载。

只拦 URL 含 create/update/submit 的请求，其余请求一律不暂停，
所以不会影响页面上任何其它操作。

用法:
  python3 promo_watch_create.py [--port CDP_PORT] [--seconds 1800] [--out notes/watched_create.jsonl]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent

PATTERNS = [{"urlPattern": pat, "requestStage": "Request"} for pat in (
    "*tiktokshopglobalselling.com/api/*create*",
    "*tiktokshopglobalselling.com/api/*update*",
    "*tiktokshopglobalselling.com/api/*submit*",
)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--seconds", type=int, default=1800)
    ap.add_argument("--out", default=str(HERE / "notes" / "watched_create.jsonl"))
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("")
    stream = out.open("a", buffering=1)
    hits = [0]

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{args.port}")
        ctx = b.contexts[0]
        attached: dict = {}          # Page -> cdp session

        def attach(page) -> None:
            try:
                page.set_viewport_size({"width": 1600, "height": 1200})
            except Exception:
                pass                     # 非活动 tab 设不了，忽略
            cdp = ctx.new_cdp_session(page)
            cdp.send("Fetch.enable", {"patterns": PATTERNS})

            def on_paused(ev):
                rid = ev.get("requestId")
                try:
                    r = ev.get("request", {})
                    if r.get("method") != "OPTIONS":
                        rec = {"at": time.strftime("%H:%M:%S"),
                               "method": r.get("method"),
                               "path": r["url"].split("?")[0].split(".com")[-1],
                               "full_url": r.get("url"),
                               "body": r.get("postData")}
                        stream.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        hits[0] += 1
                        print(f"[{rec['at']}] ★ 捕获 #{hits[0]}  {rec['method']} {rec['path']}  "
                              f"body={len(rec['body'] or '')}B", flush=True)
                except Exception as e:
                    print("  记录异常:", str(e)[:100], flush=True)
                finally:
                    try:
                        cdp.send("Fetch.continueRequest", {"requestId": rid})
                    except Exception:
                        pass

            cdp.on("Fetch.requestPaused", on_paused)
            attached[page] = cdp
            print(f"  ✓ 已挂载: {page.url[:74]}", flush=True)

        for pg in ctx.pages:
            if "tiktokshopglobalselling.com" in pg.url:
                try:
                    attach(pg)
                except Exception as e:
                    print(f"  ✗ 挂载失败 {pg.url[:44]}: {str(e)[:60]}", flush=True)

        print(f"\n监听中（{args.seconds}s）—— 每 3 秒扫描新 tab；"
              f"只拦 create/update/submit，不影响其它操作")
        print(f"结果实时写入 {out}\n", flush=True)

        deadline = time.time() + args.seconds
        try:
            while time.time() < deadline: CONTACT_REDACTED(3)
                for pg in ctx.pages:
                    if pg in attached or "tiktokshopglobalselling.com" not in pg.url:
                        continue
                    try:
                        attach(pg)
                    except Exception as e:
                        print(f"  ✗ 挂载失败 {pg.url[:44]}: {str(e)[:60]}", flush=True)
        except KeyboardInterrupt:
            print("\n手动停止", flush=True)
        finally:
            for page, cdp in attached.items():
                try:
                    cdp.send("Fetch.disable")
                except Exception:
                    pass
            stream.close()
            print(f"结束：共捕获 {hits[0]} 条 → {out}", flush=True)


if __name__ == "__main__":
    main()
