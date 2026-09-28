#!/usr/bin/env python3
"""抓取完整的 create 请求体 —— 之后就能纯 API 复现。

流程：预注入抓包器(跨导航存活) → 用 tk178_build 的步骤填表 → 提交 → 导出 payload

    python3 tk178_capture.py                 # 建一个新商品并抓包
    python3 tk178_capture.py --dump          # 只看已抓到的
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tk178_fill2 import get_page  # noqa: E402
import tk178_build as B            # noqa: E402

OUT = os.path.join(HERE, "notes", "tk178_create_full.json")


def install_recorder(page):
    rec = open(os.path.join(HERE, "tt_scrape.py")).read() \
        .split('RECORDER = r"""')[1].split('"""')[0]
    # 用 Playwright 的 add_init_script —— session 由 Playwright 持有,不会失效
    page.add_init_script(rec)
    page.evaluate(rec)          # 当前页也装一份
    print("抓包器已预注入 (add_init_script)")
    return rec


def fill_form(page):
    """跑完整填表流程。"""
    steps = [
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
    for nm, fn in steps:
        print(f"\n>>> {nm}")
        try:
            print(f"    结果: {fn(page)}")
        except Exception as e:
            print(f"    !! {nm}: {type(e).__name__}: {str(e)[:140]}")
        time.sleep(0.6)


def dump_captured(page, tag=""):
    page.evaluate("""() => {
      if (!window.__ttRec) { window.__ttRec = { get: () => JSON.parse(localStorage.getItem('__ttRecBuf') || '[]') }; }
    }""")
    recs = json.loads(page.evaluate("() => JSON.stringify(window.__ttRec.get()||[])") or "[]")
    posts = [r for r in recs if r.get("method") == "POST" and "seller-vn" in (r.get("url") or "")]
    print(f"\n--- 抓包 {tag}: 共 {len(recs)} 条, 自家 POST {len(posts)} ---")
    for r in posts:
        u = r["url"].split("?")[0].replace("https://seller-vn.tiktok.com", "")
        print(f"  [{r.get('status')}] {u}  body={len(r.get('reqBody') or '')}B")
    return posts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--submit", action="store_true", default=True)
    a = ap.parse_args()

    with sync_playwright() as pw:
        page = get_page(pw)
        if a.dump:
            posts = dump_captured(page, "existing")
            return 0

        install_recorder(page)
        page.evaluate("() => localStorage.removeItem('__ttRecBuf')")
        print("\n重新打开创建页…")
        page.goto("https://seller-vn.tiktok.com/product/create?shop_region=VN",
                  wait_until="domcontentloaded")
        time.sleep(20)
        page.set_viewport_size({"width": 1680, "height": 2400})
        time.sleep(2)
        print("URL:", page.url)
        page.keyboard.press("Escape")
        time.sleep(1)

        fill_form(page)

        print("\n\n========== 提交 ==========")
        page.evaluate("() => window.scrollTo(0,0)")
        time.sleep(1.5)
        page.get_by_text("提交审核", exact=True).first.click(timeout=15000)
        time.sleep(8)
        # 确认弹窗
        dlg = page.evaluate("""() => {
          const d=[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null&&(x.innerText||'').trim()==='提交');
          return d.map(x=>{const r=x.getBoundingClientRect(); return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};});
        }""")
        if dlg:
            page.mouse.click(dlg[-1]["x"], dlg[-1]["y"])
            print("已点弹窗确认")
        time.sleep(18)

        posts = dump_captured(page, "after submit")
        json.dump({"posts": posts}, open(OUT, "w"), ensure_ascii=False, indent=2)
        print(f"\n→ {OUT}")
        # 找 create / edit
        for r in posts:
            u = r["url"]
            if any(k in u for k in ("product/create", "product/edit", "draft/save", "/msubmit")):
                body = r.get("reqBody") or ""
                print("=" * 96)
                print(f"[{r.get('status')}] {u.split('?')[0]}")
                print(f"body {len(body)} 字符")
                print(body[:1200])
        page.screenshot(path=os.path.join(HERE, "notes", "tk178_capture.png"), full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
