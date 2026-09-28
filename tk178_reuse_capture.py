#!/usr/bin/env python3
"""复用 tk178_build.py 里已跑通的填充步骤 + CDP 拦截 → 抓真实 create 调用。

不重写填充逻辑，只把 build 的 step 函数按顺序跑一遍，同时在网络层记录。
"""
from __future__ import annotations

import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tk178_fill2 import get_page   # noqa: E402
import tk178_build as B            # noqa: E402

WATCH = ("/product/local/", "/product/msubmit", "/product/images/msubmit", "/product/comp/")


class Tap:
    def __init__(self, page):
        self.hits = []
        self.cdp = page.context.new_cdp_session(page)
        self.cdp.on("Fetch.requestPaused", self._on)
        self.cdp.send("Fetch.enable", {"patterns": [
            {"urlPattern": "*seller-vn.tiktok.com/api/v1/product/*", "requestStage": "Request"}]})
        print("[tap] on")

    def _on(self, p):
        rid = p.get("requestId")
        try:
            req = p.get("request", {})
            path = req.get("url", "").split("?")[0].replace("https://seller-vn.tiktok.com", "")
            body = req.get("postData", "")
            if any(w in path for w in WATCH):
                self.hits.append({"path": path, "method": req.get("method"),
                                  "url": req.get("url"), "body": body, "len": len(body)})
                print(f"[tap] ★ {req.get('method'):<5} {path}  {len(body)}B")
        except Exception as e:  # noqa: BLE001
            print("[tap] !!", type(e).__name__, str(e)[:90])
        try:
            self.cdp.send("Fetch.continueRequest", {"requestId": rid})
        except Exception:
            pass

    def stop(self):
        try:
            self.cdp.send("Fetch.disable")
        except Exception:
            pass


STEPS = [
    ("image", B.step_image),
    ("name", B.step_name),
    ("category", B.step_category),
    ("desc", B.step_desc),
    ("品牌", lambda p: B.pick_existing(p, "品牌", ["无品牌"], query="无品牌")),
    ("原产国", lambda p: B.pick_existing(p, "原产国/原产地", ["China"], query="China")),
    ("版本", lambda p: B.pick_existing(p, "版本", ["标准版"])),
    ("原料偏好", lambda p: B.pick_existing(p, "原料偏好",
                                        ["维他命C", "透明质酸", "神经酰胺"], multi=True)),
    ("sales", B.step_sales),
    ("dims", B.step_dims),
    ("物流方式", lambda p: B.pick_radio(p)),
    ("License type", lambda p: B.pick_existing(
        p, "License type", ["Cosmetic product notification form (CPNF)"])),
    ("License number", lambda p: B.add_and_pick(p, "License number", B.LIC_NO)),
    ("Date of issuance", lambda p: B.add_and_pick(p, "Date of issuance", B.LIC_DATE)),
    ("Place of issuance", lambda p: B.add_and_pick(p, "Place of issuance", B.LIC_PLACE)),
    ("制造商名称", lambda p: B.add_and_pick(p, "制造商/贸易商名称", B.MAKER)),
    ("制造商地址", lambda p: B.add_and_pick(p, "制造商/经销商地址", B.ADDR)),
]


def main() -> int:
    with sync_playwright() as pw:
        page = get_page(pw)
        tap = Tap(page)
        try:
            print("打开创建页…")
            page.goto("https://seller-vn.tiktok.com/product/create?shop_region=VN",
                      wait_until="domcontentloaded")
            time.sleep(20)
            page.set_viewport_size({"width": 1680, "height": 2400})
            time.sleep(2)
            page.keyboard.press("Escape")
            time.sleep(1)
            print("URL:", page.url)
            for nm, fn in STEPS:
                try:
                    r = fn(page)
                    print(f"  {nm:<18} {r}")
                except Exception as e:
                    print(f"  !! {nm:<15} {type(e).__name__}: {str(e)[:110]}")
                time.sleep(0.6)

            print("\n--- 提交 ---")
            page.evaluate("() => window.scrollTo(0,0)")
            time.sleep(1.5)
            page.get_by_text("提交审核", exact=True).first.click(timeout=15000)
            time.sleep(8)
            dlg = page.evaluate("""() => {
              const d=[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null
                && (x.innerText||'').trim()==='提交');
              return d.map(x=>{const r=x.getBoundingClientRect();
                return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};});
            }""")
            if dlg:
                page.mouse.click(dlg[-1]["x"], dlg[-1]["y"])
                print("已点弹窗提交")
            time.sleep(22)
        finally:
            tap.stop()
            out = os.path.join(HERE, "notes", "tk178_create_real.json")
            json.dump({"hits": tap.hits}, open(out, "w"), ensure_ascii=False, indent=2)
            print(f"\n抓到 {len(tap.hits)} 个 → {out}")
            for h in tap.hits:
                print(f"  {h['method']:<5} {h['path']}  {h['len']}B")
            page.screenshot(path=os.path.join(HERE, "notes", "tk178_create_real.png"),
                            full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
