#!/usr/bin/env python3
"""通过 CDP 接管 Hub Studio 实例。只读探测用 —— 不改动页面。

    python3 hubstudio_cdp.py --port CDP_PORT            # 看店铺信息
    python3 hubstudio_cdp.py --port CDP_PORT --dump     # 打印页面文本
"""
from __future__ import annotations
import argparse, json, re, sys
from playwright.sync_api import sync_playwright

PORTS = {CDP_PORT: "TK89_Local_Shop",
         58766: "TK56_CrossBorder_Shop",
         53686: "TK20跨境_个护_立志（曝光量降低）",
         51630: "TK01_CrossBorder_Shop"}


def read_shop(page) -> dict:
    """从当前 TikTok 后台页面读店铺标识。"""
    info = {"url": page.url, "title": page.title()}
    try:
        info.update(page.evaluate("""() => {
            const out = {};
            // TikTok seller 会把店铺信息挂在全局或 meta 里
            try { out.shopId = window.__SHOP_ID__ || null; } catch(e) {}
            const m = document.querySelector('meta[name="shop-id"], meta[name="shop_id"]');
            if (m) out.metaShopId = m.content;
            // 从页面文本里抓店铺名
            const el = document.querySelector('[data-tid="shop-name"], .shop-name, header');
            if (el) out.headerText = (el.innerText||'').slice(0,120);
            return out;
        }"""))
    except Exception as e:
        info["evalErr"] = str(e)[:90]
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--dump", action="store_true", help="打印页面文本前 1500 字")
    ap.add_argument("--tab", type=int, default=0, help="第几个 tiktok 页面(默认 0)")
    args = ap.parse_args()

    name = PORTS.get(args.port, "?")
    print(f"接管实例: 端口 {args.port}  ({name})")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{args.port}")
        except Exception as e:
            print(f"  连接失败: {e}")
            return 2
        ctxs = browser.contexts
        print(f"  contexts = {len(ctxs)}")
        pages = []
        for c in ctxs:
            pages.extend(c.pages)
        print(f"  页面总数 = {len(pages)}")
        tt = [pg for pg in pages if "tiktok" in pg.url]
        print(f"  TikTok 页面 = {len(tt)}")
        for i, pg in enumerate(tt):
            print(f"    [{i}] {pg.title()[:56]}")
            print(f"         {pg.url[:110]}")
        if tt:
            tgt = tt[min(args.tab, len(tt)-1)]
            print(f"\n--- 读第 {args.tab} 个页面 ---")
            info = read_shop(tgt)
            print(json.dumps(info, ensure_ascii=False, indent=1)[:900])
            if args.dump:
                txt = tgt.evaluate("() => document.body ? document.body.innerText : ''")
                print("\n--- 页面文本 ---")
                print(txt[:1500])
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
