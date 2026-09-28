#!/usr/bin/env python3
"""深度爬取财务接口 —— 不只是首屏，而是把子 tab / 筛选 / 导出按钮都点一遍。

为什么需要这个：首屏只会发 ~20 个接口。而"导出 / 批量下载"这类**必须点按钮才触发**，
静态清单里能看到路径，但拿不到真实 body（导出参数全在 body 里）。

做法：
  · 每个页面先等首屏，再按文本模式找可点元素（tab / 导出 / 下载 / 筛选 / 分页）
  · 逐个点击，每次等 2.5s 并记录期间发出的请求
  · 对 export / download / file / task 类 URL **连响应体一起抓**（要拿 task_id / 下载地址）

纪律：只用 `ctx.new_page()`（登记在 ctx.pages 里），一次一个，finally 必关，结束核对页面数。

用法：
  python3 crawl_finance_deep.py CDP_PORT            # 本土 SHOP_LOCAL
  python3 crawl_finance_deep.py CDP_PORT --set cb   # 跨境 SHOP_XBORDER
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

LOCAL_PAGES = [
    ("transactions", "https://seller-vn.tiktok.com/finance/transactions?shop_region=VN&tab=settled_tab"),
    ("transactions-onhold", "https://seller-vn.tiktok.com/finance/transactions?shop_region=VN&tab=on_hold_tab"),
    ("withdraw-new", "https://seller-vn.tiktok.com/finance/withdraw-new?shop_region=VN"),
    ("invoice", "https://seller-vn.tiktok.com/finance/invoice?shop_region=VN"),
]
CB_PAGES = [
    ("bills-onhold", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview&shop_region=VN"),
    ("bills-settled", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=settled&tab=overview&shop_region=VN"),
    ("bills-paid", "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=paid&tab=overview&shop_region=VN"),
    ("bill-payment", "https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN"),
    ("deposit", "https://seller.tiktokshopglobalselling.com/deposit?shop_region=VN"),
    ("transactions", "https://seller.tiktokshopglobalselling.com/finance/transactions?shop_region=VN&tab=settled_tab"),
    ("withdraw-new", "https://seller.tiktokshopglobalselling.com/finance/withdraw-new?shop_region=VN"),
    ("invoice", "https://seller.tiktokshopglobalselling.com/finance/invoice?shop_region=VN"),
]
PAGES = LOCAL_PAGES if SET == "local" else CB_PAGES

# 值得点开的元素（按可见文本匹配）
CLICK_PATTERNS = [
    r"^导出$", r"^下载$", r"^批量导出$", r"^Export$", r"^Download$",
    r"导出记录", r"下载记录", r"Export History", r"Download History",
    r"^全部$", r"^All$", r"待结算", r"已结算", r"已支付", r"退款", r"On hold", r"Settled", r"Paid",
    r"^详情$", r"^Detail$", r"^查看$", r"^View$",
    r"筛选", r"Filter", r"^账单$", r"^Statements?$", r"^Transactions?$", r"^Invoices?$",
    r"^税务信息$", r"Tax info", r"发票", r"Invoice",
]
# 响应体值得抓的（导出任务/文件）
BODY_PAT = re.compile(r"export|download|file|task|report", re.I)
DWELL_FIRST = 12
DWELL_CLICK = 2.6
MAX_CLICKS_PER_PAGE = 14


def main():
    from playwright.sync_api import sync_playwright
    out: dict = {}
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        ctx = b.contexts[0]
        before = len(ctx.pages)
        print(f"[{PORT}/{SET}] 连接前页面数 {before}")
        for name, url in PAGES:
            pg = None
            reqs: list[dict] = []
            bodies: dict = {}
            try:
                pg = ctx.new_page()

                def on_req(r, _c=reqs):
                    if "/api/" in r.url:
                        _c.append({"t": round(time.time(), 2), "method": r.method,
                                   "url": r.url, "post": (r.post_data or "")[:800]})

                def on_resp(r, _c=reqs, _b=bodies):
                    if "/api/" not in r.url:
                        return
                    _c.append({"t": round(time.time(), 2), "response": r.status, "url": r.url})
                    if BODY_PAT.search(r.url):
                        try:
                            txt = r.text()
                            if len(txt) < 4000:
                                _b[r.url.split("?")[0]] = txt[:3000]
                        except Exception:
                            pass

                pg.on("request", on_req)
                pg.on("response", on_resp)
                pg.goto(url, wait_until="domcontentloaded", timeout=60000)
                if "/account/login" in pg.url or "/account/register" in pg.url:
                    raise RuntimeError(f"会话失效 → {pg.url.split('?')[0]}")
                time.sleep(DWELL_FIRST)
                print(f"\n=== {name}: 首屏 {len(reqs)} 条事件")

                # 找可点元素
                cands = []
                for pat in CLICK_PATTERNS:
                    try:
                        loc = pg.get_by_text(re.compile(pat), exact=False)
                        n = min(loc.count(), 3)
                        for i in range(n):
                            el = loc.nth(i)
                            try:
                                if el.is_visible():
                                    cands.append((pat, el))
                            except Exception:
                                pass
                    except Exception:
                        pass
                # 去重（同文本只点一次）
                seen_txt, picked = set(), []
                for pat, el in cands:
                    try:
                        t = (el.inner_text() or "").strip()[:24]
                    except Exception:
                        continue
                    if not t or t in seen_txt:
                        continue
                    seen_txt.add(t)
                    picked.append((t, el))
                picked = picked[:MAX_CLICKS_PER_PAGE]
                print(f"    候选项 {len(picked)} 个: {[t for t, _ in picked]}")

                for txt, el in picked:
                    try:
                        el.click(timeout=4000)
                        time.sleep(DWELL_CLICK)
                    except Exception as e:
                        print(f"      ✗ 点 {txt!r}: {str(e)[:70]}")
                time.sleep(3)
                # 滚一下触发懒加载
                try:
                    for _ in range(2):
                        pg.mouse.wheel(0, 1600); time.sleep(1.5)
                except Exception:
                    pass
            except Exception as e:
                print(f"  ✗ {name}: {str(e)[:200]}")
            finally:
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
            fin = [r for r in uniq if re.search(r"/pay/|/finance/|/tax/|settlement|invoice|statement", r["url"])]
            print(f"    唯一请求 {len(uniq)} / 财务 {len(fin)} / 抓到响应体 {len(bodies)}")
            for r in fin:
                p = "/api/" + r["url"].split("/api/", 1)[1].split("?")[0]
                body = f"  body={r['post'][:90]}" if len(r.get("post") or "") > 2 else ""
                print(f"      {r['method']:5} {p}{body}")
            out[name] = {"page": url, "requests": uniq, "finance": fin, "bodies": bodies}

        after = len(ctx.pages)
        print(f"\n关闭后页面数 {after}（连接前 {before}）—— "
              f"{'✅ 已复原' if after <= before else '⚠ 有残留'}")
        out["_pages_before"] = before
        out["_pages_after"] = after
        f = HERE / "notes" / f"finance_deep_{SET}.json"
        f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        tot = sum(len(v.get("finance", [])) for k, v in out.items() if not k.startswith("_"))
        print(f"财务接口合计 {tot} → {f.name}")


if __name__ == "__main__":
    main()
