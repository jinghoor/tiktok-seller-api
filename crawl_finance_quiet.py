#!/usr/bin/env python3
"""财务接口深度爬取 —— **静默版**，不打扰操作员。

和上一版的区别（上一版会让你看到标签页跳动）：

| 项 | 旧做法（会打扰） | 本脚本 |
|---|---|---|
| 建标签 | `ctx.new_page()` → Chromium 默认 **激活**该标签 | CDP `Target.createTarget({background:true})` → **不激活** |
| 点击 | `locator.click()` → 走 CDP Input 事件，需要前台 | `pg.evaluate(el => el.click())` → **DOM 层点击**，后台也能用 |
| 滚动 | `mouse.wheel()` → Input 事件 | `window.scrollTo()` → 纯 JS |
| 关闭 | `pg.close()`（可能残留） | `Target.closeTarget(targetId)` + `pg.close()` 双保险 |

所以整个过程中你的窗口、标签、焦点、鼠标都不会被碰。

用法：
  python3 crawl_finance_quiet.py CDP_PORT            # 本土 SHOP_LOCAL
  python3 crawl_finance_quiet.py CDP_PORT --set cb   # 跨境 SHOP_XBORDER
  python3 crawl_finance_quiet.py CDP_PORT --only transactions   # 只跑一页（小样验证）
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
SET = "cb" if "--set" in sys.argv and "cb" in sys.argv else "local"
ONLY = None
if "--only" in sys.argv:
    ONLY = sys.argv[sys.argv.index("--only") + 1]

LOCAL_PAGES = [
    ("transactions-settled", "https://seller-vn.tiktok.com/finance/transactions?shop_region=VN&tab=settled_tab"),
    ("transactions-onhold", "https://seller-vn.tiktok.com/finance/transactions?shop_region=VN&tab=on_hold_tab"),
    ("withdraw-new", "https://seller-vn.tiktok.com/finance/withdraw-new?shop_region=VN"),
    ("invoice", "https://seller-vn.tiktok.com/finance/invoice?shop_region=VN"),
]
CB_PAGES = [
    ("bills-onhold", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview&shop_region=VN"),
    ("bills-settled", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=settled&tab=overview&shop_region=VN"),
    ("bill-payment", "https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN"),
    ("withdraw-new", "https://seller.tiktokshopglobalselling.com/finance/withdraw-new?shop_region=VN"),
    ("invoice", "https://seller.tiktokshopglobalselling.com/finance/invoice?shop_region=VN"),
]
PAGES = LOCAL_PAGES if SET == "local" else CB_PAGES
if ONLY:
    PAGES = [p for p in PAGES if p[0] == ONLY]

CLICK_TEXTS = [
    "导出", "下载", "批量导出", "Export", "Download",
    "导出记录", "下载记录", "Export History", "Download History",
    "全部", "All", "待结算", "已结算", "已支付", "退款", "账单", "交易明细",
    "On hold", "Settled", "Paid", "Statements", "Transactions",
    "筛选", "Filter", "详情", "Detail", "税务信息", "Tax info", "发票", "Invoice",
    "确认", "确定", "OK", "Confirm", "Submit", "提交",
]
BODY_PAT = re.compile(r"export|download|file|task|report", re.I)
DWELL_FIRST = 13
DWELL_CLICK = 2.4


def js_collect_clicks(texts, limit=16):
    """在页内找可点元素（按文本），返回 [{text, path}] —— 只收集，不点。"""
    return """(texts) => {
      const out = [];
      const seen = new Set();
      const nodes = document.querySelectorAll(
        'button,[role=button],[role=tab],a,div[class*=tab],span[class*=tab],li[class*=tab],div[class*=Tab],span[class*=Tab]');
      for (const el of nodes) {
        const t = (el.innerText || el.textContent || '').trim();
        if (!t || t.length > 24 || seen.has(t)) continue;
        if (!texts.some(x => t === x || t.includes(x))) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 4 || r.height < 4) continue;
        const st = getComputedStyle(el);
        if (st.display === 'none' || st.visibility === 'hidden') continue;
        seen.add(t);
        // 用 textContent 精确回找
        el.setAttribute('data-dsh-click', String(seen.size - 1));
        out.push({ i: seen.size - 1, text: t });
        if (out.length >= %d) break;
      }
      return JSON.stringify(out);
    }""" % limit


def main():
    from playwright.sync_api import sync_playwright
    out: dict = {}
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]
        bsess = b.new_browser_cdp_session()
        before = len(ctx.pages)
        print(f"[{PORT}/{SET}] 连接前页面数 {before}（全程不新增可见标签）")

        for name, url in PAGES:
            pg = None
            tid = None
            reqs: list[dict] = []
            bodies: dict = {}
            try:
                # ★ background:true —— 不激活、不抢焦点
                tid = bsess.send("Target.createTarget",
                                 {"url": "about:blank", "background": True})["targetId"]
                pg = None
                for _ in range(30):
                    time.sleep(0.2)
                    cand = [p for p in ctx.pages if p.url == "about:blank"]
                    if cand:
                        pg = cand[-1]
                        break
                if pg is None:
                    raise RuntimeError("后台标签没在 ctx.pages 里出现")

                def on_req(r, _c=reqs):
                    if "/api/" in r.url:
                        _c.append({"method": r.method, "url": r.url,
                                   "post": (r.post_data or "")[:900]})

                def on_resp(r, _c=reqs, _b=bodies):
                    if "/api/" not in r.url:
                        return
                    _c.append({"response": r.status, "url": r.url})
                    if BODY_PAT.search(r.url):
                        try:
                            t = r.text()
                            if len(t) < 4000:
                                _b[r.url.split("?")[0]] = t[:3000]
                        except Exception:
                            pass

                pg.on("request", on_req)
                pg.on("response", on_resp)
                pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                if "/account/login" in pg.url or "/account/register" in pg.url:
                    raise RuntimeError(f"会话失效 → {pg.url.split('?')[0]}")
                time.sleep(DWELL_FIRST)
                print(f"\n=== {name}: 首屏事件 {len(reqs)}")

                # 收集可点元素（纯 JS，不点）
                try:
                    cands = json.loads(pg.evaluate(js_collect_clicks(CLICK_TEXTS)))
                except Exception as e:
                    cands = []
                    print(f"    收集失败 {str(e)[:80]}")
                print(f"    可点 {len(cands)} 个: {[c['text'] for c in cands]}")

                # ★ DOM 层逐个点击 —— 不产生 Input 事件，后台标签也能用
                for c in cands:
                    try:
                        pg.evaluate(
                            """(i) => { const el = document.querySelector(`[data-dsh-click="${i}"]`);
                                 if (el) el.click(); }""", c["i"])
                        time.sleep(DWELL_CLICK)
                    except Exception:
                        pass
                time.sleep(2.5)
                try:
                    pg.evaluate("() => { for (let y=0; y<4000; y+=800) setTimeout(()=>window.scrollTo(0,y), y/4); }")
                    time.sleep(3)
                except Exception:
                    pass
            except Exception as e:
                print(f"  ✗ {name}: {str(e)[:190]}")
            finally:
                if tid:
                    try:
                        bsess.send("Target.closeTarget", {"targetId": tid})
                    except Exception:
                        pass
                if pg is not None:
                    try:
                        pg.close()
                    except Exception:
                        pass
                time.sleep(1.0)

            seen, uniq = set(), []
            for r in reqs:
                if "method" not in r:
                    continue
                k = (r["method"], r["url"].split("?")[0])
                if k in seen:
                    continue
                seen.add(k); uniq.append(r)
            fin = [r for r in uniq
                   if re.search(r"/pay/|/finance/|/tax/|settlement|invoice|statement", r["url"])]
            print(f"    唯一 {len(uniq)} / 财务 {len(fin)} / 响应体 {len(bodies)}")
            for r in fin:
                p = "/api/" + r["url"].split("/api/", 1)[1].split("?")[0]
                bd = f"  body={r['post'][:80]}" if len(r.get("post") or "") > 2 else ""
                print(f"      {r['method']:5} {p}{bd}")
            out[name] = {"page": url, "requests": uniq, "finance": fin, "bodies": bodies}

        after = len(ctx.pages)
        print(f"\n结束页面数 {after}（开始 {before}）—— "
              f"{'✅ 一个都没多' if after <= before else '⚠ 有残留'}")
        out["_pages_before"] = before
        out["_pages_after"] = after
        f = HERE / "notes" / f"finance_quiet_{SET}.json"
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        tot = sum(len(v.get("finance", [])) for k, v in out.items() if not k.startswith("_"))
        print(f"财务接口 {tot} → {f.name}")


if __name__ == "__main__":
    main()
