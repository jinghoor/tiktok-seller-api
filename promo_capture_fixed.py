#!/usr/bin/env python3
"""自己走 UI 提交一次「一口价」促销，用 Fetch domain 抓出真实 payload。

为什么需要它：
  - POST /promotion/fixed_price/create 在所有试过的结构下都返回 code=10000
  - POST /promotion/discount/create 收下 products_fixed_price 会返回 code=200 的
    promotion_id，但 list_products 读回 0 个商品 —— 是个"假成功"
  所以一口价的字段组合只能从真实 UI 提交里抓。

复用 promo_capture_v3.py 里已验证的页面定位修法：
  - viewport 必须设（后台 tab viewport=0 时表格虚拟滚动不渲染行）
  - 弹层「完成」按钮要限定在弹层内，并用 Playwright 真实 click
  - 行 checkbox 只能用键盘 Space（鼠标点击会让整个表格从 DOM 卸载）
  - 折扣输入框用 data-prefill-id 前缀定位
  - Fetch domain 只在提交前 enable，且必须 continueRequest 放行
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
NOTES = HERE / "notes"
PORT = "http://127.0.0.1:CDP_PORT"
CREATE_URL = ("https://seller.tiktokshopglobalselling.com/promotion/"
              "marketing-tools/discount/create?shop_region=VN")
PATTERN_ALL = "*api16-normal-sg.tiktokshopglobalselling.com/api/v1/promotion*"

JS_MODAL_STATE = """() => {
  const m=[...document.querySelectorAll('[class*=modal]')]
    .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
  if(!m) return {modal:false};
  const cbs=[...m.querySelectorAll('input[type=checkbox]')].slice(2);
  const btn=[...m.querySelectorAll('button')].find(b=>b.innerText.trim()==='完成');
  return {modal:true, rows:cbs.length,
          enabled:cbs.filter(e=>!e.closest('[class*=checkbox-disabled]')).length,
          selected:cbs.filter(e=>e.checked).length,
          done_disabled: btn? btn.disabled : null};
}"""

JS_DUMP_INPUTS = """() => [...document.querySelectorAll('input')]
  .filter(e=>e.offsetParent!==null)
  .map((e,i)=>({i, type:e.type, prefill:e.getAttribute('data-prefill-id'),
                ph:e.placeholder, val:String(e.value).slice(0, 14)}))"""


def log(*a):
    print(*a, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", default="30000", help="一口价(越南盾，必须低于该 SKU 原价)")
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-submit", action="store_true", help="只填到提交前，不点发布")
    args = ap.parse_args()

    captured: list[dict] = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(PORT)
        ctx = b.contexts[0]
        page = ctx.new_page()
        page.set_viewport_size({"width": 1600, "height": 1200})   # 不加这行表格不渲染
        cdp = ctx.new_cdp_session(page)

        def on_paused(ev):
            rid = ev.get("requestId")
            try:
                r = ev.get("request", {})
                if r.get("method") != "OPTIONS":
                    captured.append({"method": r.get("method"),
                                     "path": r["url"].split("?")[0].split(".com")[-1],
                                     "postData": r.get("postData")})
            except Exception as e:
                captured.append({"_err": str(e)[:120]})
            finally:
                try:
                    cdp.send("Fetch.continueRequest", {"requestId": rid})
                except Exception:
                    pass

        cdp.on("Fetch.requestPaused", on_paused)
        try:
            log("[1] 打开 create 页")
            page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=60000)
            for _ in range(30):
                time.sleep(1)
                if "折扣类型" in page.evaluate("document.body.innerText"):
                    break

            log("[2] 选「一口价」(radio val=2)")
            page.locator("label", has_text="一口价").first.click()
            time.sleep(1.5)
            rd = page.evaluate("[...document.querySelectorAll('input[type=radio]')].map(e=>e.checked)")
            log(f"    radios={rd}")
            assert rd and rd[1] is True, "一口价未选中"

            log("[3] 打开商品选择弹层")
            page.locator("button", has_text="选择商品").first.click()
            for _ in range(25):
                time.sleep(1.2)
                if page.evaluate(JS_MODAL_STATE).get("rows", 0) > 0:
                    break
            st = page.evaluate(JS_MODAL_STATE)
            log(f"    {json.dumps(st, ensure_ascii=False)}")
            assert st.get("enabled"), "没有可勾选商品"

            idx = page.evaluate("""() => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              const cbs=[...m.querySelectorAll('input[type=checkbox]')].slice(2);
              return cbs.findIndex(e=>!e.closest('[class*=checkbox-disabled]'));
            }""")
            log(f"[4] 勾选 row#{idx}")
            h = page.evaluate_handle("""(i) => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
              return e.closest('label') || e.closest('[class*=checkbox]');
            }""", idx).as_element()
            h.scroll_into_view_if_needed()
            h.click()
            time.sleep(1.5)
            assert page.evaluate(JS_MODAL_STATE).get("selected"), "勾选未生效"

            log("[5] 弹层内「完成」")
            done = page.evaluate_handle("""() => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              return m ? [...m.querySelectorAll('button')].find(b=>b.innerText.trim()==='完成') : null;
            }""").as_element()
            assert done is not None, "找不到完成按钮"
            done.scroll_into_view_if_needed()
            done.click()
            time.sleep(9)

            cnt = page.evaluate("""() => {
              const m=document.body.innerText.match(/(\\d+)\\s*件商品/); return m? Number(m[1]) : -1;}""")
            log(f"    件商品 = {cnt}")
            if cnt <= 0:
                raise RuntimeError("商品未加入表单")

            log("[6a] 键盘 Space 勾选行")
            box = page.evaluate_handle("""() => {
              const cbs=[...document.querySelectorAll('input[type=checkbox]')];
              const row=cbs[cbs.length-1];
              return row ? (row.closest('label')||row) : null;}""").as_element()
            if box is not None:
                box.scroll_into_view_if_needed()
                box.press("Space")
                time.sleep(2.5)

            log("[6b] dump 所有输入框（找一口价的输入位）")
            dump = page.evaluate(JS_DUMP_INPUTS)
            for d in dump:
                log(f"    {d}")
            cand = [d for d in dump if d.get("prefill") and "fixed" in str(d["prefill"]).lower()]
            if not cand:
                cand = [d for d in dump if d.get("prefill") and "price" in str(d["prefill"]).lower()]
            if not cand:
                cand = [d for d in dump if d.get("prefill")]
            log(f"    → 候选输入框 {len(cand)} 个: {[c['prefill'] for c in cand]}")

            log(f"[6c] 填一口价 = {args.price}")
            filled = 0
            for c in cand:
                try:
                    inp = page.locator(f'input[data-prefill-id="{c["prefill"]}"]').first
                    inp.fill(args.price, timeout=8000)
                    inp.press("Tab")
                    filled += 1
                    time.sleep(0.6)
                except Exception as e:
                    log(f"    {c['prefill']} 填失败: {str(e)[:60]}")
            log(f"    成功填 {filled} 个")
            if args.name:
                nm = page.locator("input").nth(0)
                nm.click(); nm.fill(args.name); time.sleep(0.6)
            time.sleep(4)

            if args.no_submit:
                log("[7] --no-submit: 停在提交前")
                time.sleep(2)
            else:
                log("[7] 提交并抓包（此刻才开 Fetch 全量拦截）")
                cdp.send("Fetch.enable", {"patterns": [
                    {"urlPattern": PATTERN_ALL, "requestStage": "Request"}]})
                for attempt in range(8):
                    btn = page.evaluate_handle("""() => [...document.querySelectorAll('button')]
                      .find(b=>b.innerText.trim()==='同意并发布') || null""").as_element()
                    if btn is None:
                        log(f"    第 {attempt+1} 次: 按钮不存在")
                        time.sleep(3)
                        continue
                    try:
                        btn.click(timeout=8000)
                        log(f"    已点击 (第 {attempt+1} 次)")
                        break
                    except Exception as e:
                        log(f"    第 {attempt+1} 次失败: {str(e)[:70]}")
                        time.sleep(3)
                for _ in range(25):
                    time.sleep(1)
                    if any(("create" in (c.get("path") or "")) for c in captured):
                        time.sleep(3)
                        break
        finally:
            try:
                cdp.send("Fetch.disable")
            except Exception:
                pass
            log(f"\n=== 捕获 {len(captured)} 条 ===")
            for c in captured:
                log(f"  {c.get('method'):5} {(c.get('path') or '')[:70]}  body={len(c.get('postData') or '')}")
            creates = [c for c in captured if "create" in (c.get("path") or "")]
            if creates:
                NOTES.mkdir(parents=True, exist_ok=True)
                (NOTES / "promo_fixed_payload.json").write_text(
                    json.dumps({"all": captured, "create": creates[-1]},
                               ensure_ascii=False, indent=2))
                log(f"\n=== 建活动的请求 → notes/promo_fixed_payload.json ===")
                log(f"PATH: {creates[-1]['path']}")
                log(f"BODY: {(creates[-1].get('postData') or '')[:3000]}")
            else:
                log("\n未抓到 create 请求")
                try:
                    log("页面尾部:", page.evaluate("document.body.innerText.slice(-300)").replace("\n", " | "))
                except Exception:
                    pass
            try:
                page.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
