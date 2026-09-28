#!/usr/bin/env python3
"""用 CDP Fetch 域在网络层拦请求 —— 抓完整 payload,不依赖页面内钩子。

比 inject JS 可靠：不受导航/重渲染影响，且能拿到完整体（不截断）。

    python3 tk178_cdp_capture.py --fill      # 填表并停在提交前
    python3 tk178_cdp_capture.py --submit    # 填表 + 提交 + 打印抓到的 payload
    python3 tk178_cdp_capture.py --replay FILE   # 用抓到的 payload 重放(纯 API)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import threading
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tk178_fill2 import get_page  # noqa: E402

CAPTURE = os.path.join(HERE, "notes", "tk178_intercepted.json")
WATCH = ("/api/v1/product/local/product/create", "/api/v1/product/local/product/edit",
         "/api/v1/product/local/draft/save", "/api/v1/product/msubmit",
         "/api/v1/product/local/product/precheck", "/api/v1/product/images/msubmit")


class NetTap:
    """CDP Fetch 拦截器：记录匹配的请求体，同时让请求继续发出。"""

    def __init__(self, page, watch=WATCH):
        self.page = page
        self.watch = watch
        self.hits: list[dict] = []
        self.cdp = page.context.new_cdp_session(page)
        self.cdp.on("Fetch.requestPaused", self._on_paused)
        self.cdp.send("Fetch.enable", {"patterns": [
            {"urlPattern": "*product/local/product/*", "requestStage": "Request"},
            {"urlPattern": "*product/local/draft/*", "requestStage": "Request"},
            {"urlPattern": "*product/msubmit*", "requestStage": "Request"},
            {"urlPattern": "*product/images/msubmit*", "requestStage": "Request"},
        ]})
        print("[tap] Fetch 拦截已启用")

    def _on_paused(self, params):
        try:
            req = params.get("request", {})
            url = req.get("url", "")
            path = url.split("?")[0].replace("https://seller-vn.tiktok.com", "")
            if any(w in path for w in self.watch):
                body = req.get("postData", "")
                self.hits.append({"path": path, "method": req.get("method"),
                                  "url": url, "body": body, "len": len(body)})
                print(f"[tap] ★ {req.get('method')} {path}  body={len(body)}B")
            # 放行
            self.cdp.send("Fetch.continueRequest", {"requestId": params["requestId"]})
        except Exception as e:  # noqa: BLE001
            print(f"[tap] !! {type(e).__name__}: {str(e)[:120]}")
            try:
                self.cdp.send("Fetch.continueRequest", {"requestId": params["requestId"]})
            except Exception:
                pass

    def stop(self):
        try:
            self.cdp.send("Fetch.disable")
        except Exception:
            pass


def fill_form(page):
    import tk178_build as B
    steps = [
        ("image", B.step_image), ("name", B.step_name), ("category", B.step_category),
        ("desc", B.step_desc),
        ("品牌", lambda p: B.pick_existing(p, "品牌", ["无品牌"], query="无品牌")),
        ("原产国", lambda p: B.pick_existing(p, "原产国/原产地", ["China"], query="China")),
        ("版本", lambda p: B.pick_existing(p, "版本", ["标准版"])),
        ("原料偏好", lambda p: B.pick_existing(p, "原料偏好",
                                            ["维他命C", "透明质酸", "神经酰胺"], multi=True)),
        ("sales", B.step_sales), ("dims", B.step_dims),
        ("物流方式", lambda p: B.pick_radio(p)),
        ("License type", lambda p: B.pick_existing(
            p, "License type", ["Cosmetic product notification form (CPNF)"])),
        ("License number", lambda p: B.add_and_pick(p, "License number", B.LIC_NO)),
        ("Date of issuance", lambda p: B.add_and_pick(p, "Date of issuance", B.LIC_DATE)),
        ("Place of issuance", lambda p: B.add_and_pick(p, "Place of issuance", B.LIC_PLACE)),
        ("制造商名称", lambda p: B.add_and_pick(p, "制造商/贸易商名称", B.MAKER)),
        ("制造商地址", lambda p: B.add_and_pick(p, "制造商/经销商地址", B.ADDR)),
    ]
    for nm, fn in steps:
        try:
            r = fn(page)
            print(f"  {nm}: {r}")
        except Exception as e:
            print(f"  !! {nm}: {type(e).__name__}: {str(e)[:110]}")
        time.sleep(0.5)


def do_submit(page):
    page.evaluate("() => window.scrollTo(0,0)")
    time.sleep(1.5)
    page.get_by_text("提交审核", exact=True).first.click(timeout=15000)
    time.sleep(8)
    dlg = page.evaluate("""() => {
      const d=[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null&&(x.innerText||'').trim()==='提交');
      return d.map(x=>{const r=x.getBoundingClientRect(); return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};});
    }""")
    if dlg:
        page.mouse.click(dlg[-1]["x"], dlg[-1]["y"])
        print("  已点弹窗确认")
    time.sleep(16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--replay", default=None)
    ap.add_argument("--pid", default=None, help="--replay 时替换 product_id")
    a = ap.parse_args()

    if a.replay:
        return replay(a.replay, a.pid)

    with sync_playwright() as pw:
        page = get_page(pw)
        tap = NetTap(page)
        try:
            print("\n打开创建页…")
            page.goto("https://seller-vn.tiktok.com/product/create?shop_region=VN",
                      wait_until="domcontentloaded")
            time.sleep(20)
            page.set_viewport_size({"width": 1680, "height": 2400})
            time.sleep(2)
            page.keyboard.press("Escape")
            time.sleep(1)
            print("URL:", page.url)
            print("\n--- 填表 ---")
            fill_form(page)
            if a.submit:
                print("\n--- 提交 ---")
                do_submit(page)
            time.sleep(4)
        finally:
            tap.stop()
            json.dump({"hits": tap.hits}, open(CAPTURE, "w"), ensure_ascii=False, indent=2)
            print(f"\n抓到 {len(tap.hits)} 个匹配请求 → {CAPTURE}")
            for h in tap.hits:
                print(f"  {h['method']} {h['path']}  {h['len']}B")
            page.screenshot(path=os.path.join(HERE, "notes", "tk178_cdp_capture.png"),
                            full_page=True)
    return 0


def replay(path: str, pid: str | None) -> int:
    """把抓到的 payload 通过页面上下文重放。"""
    data = json.load(open(path))
    hits = data.get("hits") or data
    if not hits:
        print("没有可重放的请求", file=sys.stderr)
        return 2
    PAGE_JS = open(os.path.join(HERE, "tk178_api.py")).read() \
        .split('PAGE_JS = r"""')[1].split('"""')[0] \
        .replace("__SELLER__", "7494XXXXXXXXXX00") \
        .replace("__AID__", "4068").replace("__APP__", "i18n_ecom_shop")
    with sync_playwright() as pw:
        page = get_page(pw)
        for h in hits:
            body = h["body"]
            if pid:
                body = body.replace('"product_id":"%s"' % h.get("pid", ""), "")
            print(f"重放 {h['method']} {h['path']} ({len(body)}B)")
            r = page.evaluate("""async (a) => {
              const csrf = decodeURIComponent((document.cookie.match(/csrf_token=([^;]+)/)||[])[1]||'');
              const resp = await fetch(a.url, {
                method: a.method, credentials: 'include',
                headers: {'Content-Type':'application/json; charset=utf-8',
                          'X-CSRFToken': csrf, 'Accept':'application/json'},
                body: a.body });
              const t = await resp.text();
              return {status: resp.status, body: t.slice(0, 1500)};
            }""", {"url": h["url"], "method": h["method"], "body": body})
            print(f"  → {r['status']}: {r['body'][:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
