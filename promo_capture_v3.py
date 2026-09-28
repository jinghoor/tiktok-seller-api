#!/usr/bin/env python3
"""SHOP_XBORDER 促销「商品折扣」创建 —— 抓 discount/create payload(最终版)。

payload 结构来自前端 bundle 逆向(notes/promo_bundle/DiscountCreateAndEdit.*.js):
  Z.Hv.CreateDiscount({
    period, promotion_name, promotion_limit_dimension,
    products_single_discount: pick(products, [sku_id, product_id, discount_percentage,
                                              total_purchase_limit, user_purchase_limit,
                                              smart_discount_value]),
    check_overlap, check_strikethrough_price, seller_agreement,
    strategy_id, smart_plan_strategy_id, rec_trace_infos, ...commonFlags })
枚举(promotion.sg_tts_cb.js):
  discount_type             {PERCENTAGE_OFF:1, FIXED_PRICE:2}
  promotion_limit_dimension {DEFUALT:0, SKU:1, SPU:4}

UI 定位要点:
  - 折扣类型 radio val=1 百分比 / val=2 一口价 —— 必须显式选中
  - 商品行 checkbox 只点 label 容器才更新 React state
  - 「折扣」输入框 = 唯一的 .theme-arco-input-size-large 且 placeholder 为空者
    (活动名称框也是 size-large,但有 placeholder,用这个区分)
  - 「批量更新」才会把批量区输入框的值写回行;不点则值不落表

抓包: CDP Fetch.requestPaused(request.postData 完整) + continueRequest 放行。
      Playwright page.on("request") 在 connectOverCDP 下 post_data 恒为 None;
      page.route 拦不到; 页面内 JS hook 抓不到跨域 api16 那条链路。

用法:
  python3 promo_capture_v3.py                 # 走到填折扣,不提交(抓 calc 预览)
  python3 promo_capture_v3.py --submit        # 真提交,抓 discount/create
  python3 promo_capture_v3.py --submit --name "API测试"
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
# 只拦 create 一个请求 —— 全量拦 promotion/* 会把前置流程的 mget_item_data 等
# 一起拖慢/打断,导致商品表格不渲染(踩过的坑)
PATTERN = "*api16-normal-sg.tiktokshopglobalselling.com/api/v1/promotion/discount/create*"
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

# 折扣输入框: size-large 但 placeholder 为空(活动名称那个有 placeholder)
JS_DISCOUNT_INPUT_INDEX = """() => {
  const all=[...document.querySelectorAll('input')];
  const c=all.filter(e=>e.type==='text'
                        && (e.className||'').includes('theme-arco-input-size-large')
                        && !e.disabled && !e.placeholder);
  return c.length ? all.indexOf(c[c.length-1]) : -1;
}"""

JS_ROW_TEXT = """(i) => {
  const m=[...document.querySelectorAll('[class*=modal]')]
    .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
  const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
  if(!e) return null;
  let r=e; for(let k=0;k<12&&r;k++){ r=r.parentElement;
    if(r&&r.className&&/row|tr/.test(r.className)) return (r.innerText||'').replace(/\\s+/g,' ').slice(0,110); }
  return null;
}"""


def log(*a):
    print(*a, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true", help="真的点「同意并发布」")
    ap.add_argument("--discount", default="10")
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    captured: list[dict] = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(PORT)
        ctx = b.contexts[0]
        page = ctx.new_page()
        # 关键: 后台 tab 的 viewport 为 0,商品表格虚拟滚动不渲染任何行 ——
        # checkbox 和「折扣」输入框都不进 DOM,前面所有"定位失败"都源于此
        page.set_viewport_size({"width": 1600, "height": 1200})
        cdp = ctx.new_cdp_session(page)
        # Fetch 只在提交阶段开(见 [7]) —— 前置阶段开着会干扰表格渲染
        def on_paused(ev):
            rid = ev.get("requestId")
            try:
                r = ev.get("request", {})
                if r.get("method") != "OPTIONS":
                    u = r.get("url", "")
                    captured.append({"method": r.get("method"),
                                     "path": u.split("?")[0].split(".com")[-1],
                                     "post_data": r.get("postData")})
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

            log("[2] 选「百分比折扣」(radio val=1)")
            page.locator("label", has_text="百分比折扣").first.click()
            time.sleep(1.2)
            assert page.evaluate(
                "[...document.querySelectorAll('input[type=radio]')][0].checked") is True, "折扣类型未选中"

            log("[3] 打开商品选择弹层")
            page.locator("button", has_text="选择商品").first.click()
            for _ in range(25):
                time.sleep(1.2)
                if page.evaluate(JS_MODAL_STATE).get("rows", 0) > 0:
                    break
            st = page.evaluate(JS_MODAL_STATE)
            log(f"    {json.dumps(st, ensure_ascii=False)}")
            assert st.get("enabled"), "没有可勾选商品(与现有活动时间重叠)"

            idx = page.evaluate("""() => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              const cbs=[...m.querySelectorAll('input[type=checkbox]')].slice(2);
              return cbs.findIndex(e=>!e.closest('[class*=checkbox-disabled]'));
            }""")
            log(f"[4] 勾选 row#{idx}: {page.evaluate(JS_ROW_TEXT, idx)}")
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

            log("[5] 点弹层内的「完成」")
            done = page.evaluate_handle("""() => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              if(!m) return null;
              return [...m.querySelectorAll('button')].find(b=>b.innerText.trim()==='完成') || null;
            }""").as_element()
            assert done is not None, "弹层里找不到「完成」"
            done.scroll_into_view_if_needed()
            done.click()
            time.sleep(9)
            cnt = page.evaluate("""() => {
              const m=document.body.innerText.match(/(\\d+)\\s*件商品/); return m? Number(m[1]) : -1;}""")
            log(f"    件商品 = {cnt}")

            log("[6a] 勾选商品行 —— 键盘 Space")
            # 鼠标 click 这个 checkbox(不论 locator 还是 JS label.click())都会让整个商品表格
            # 从 DOM 卸载;只有键盘 Space 能正确切换 React state 且保留表格
            box = page.evaluate_handle("""() => {
              const cbs=[...document.querySelectorAll('input[type=checkbox]')];
              const row=cbs[cbs.length-1];
              return row ? (row.closest('label')||row) : null;}""").as_element()
            if box is not None:
                box.scroll_into_view_if_needed()
                box.press("Space")
                time.sleep(2.5)
            log("    批量更新 disabled:", page.evaluate(
                "[...document.querySelectorAll('button')].filter(b=>b.innerText.trim()==='批量更新').map(b=>b.disabled)"))

            log("[6] 填折扣值")
            # 折扣输入框的稳定标识: data-prefill-id="product_discount_percentage__<product_id>"
            # 比按 nth(index) 定位可靠得多;fill 会自己 focus,不需要先 click
            inp = page.locator('input[data-prefill-id^="product_discount_percentage__"]').first
            inp.wait_for(state="attached", timeout=35000)
            filled = False
            for attempt in range(6):
                try:
                    inp.fill(args.discount, timeout=8000)
                    filled = True
                    break
                except Exception as e:
                    log(f"    fill 重试 {attempt}: {str(e)[:70]}")
                    time.sleep(2.5)
            assert filled, "填折扣值失败"
            log(f"    填入 = {inp.input_value()}")
            # Arco InputNumber 需要 blur 才把值提交给表单 —— 不按 Tab 的话
            # React state 不更新,价格预览不刷新,提交会被前端校验静默拦下
            try:
                inp.press("Tab")
            except Exception as e:
                log(f"    Tab 失败: {str(e)[:60]}")
            time.sleep(4)
            log("    行价(原价|折后):", page.evaluate("""() => {
              const m=document.body.innerText.match(
                /([\\d.]+)₫ - ([\\d.]+)₫[\\s\\S]{0,60}?% 折扣[\\s\\S]{0,60}?([\\d.]+)₫ - ([\\d.]+)₫/);
              return m? m.slice(1).join(' | ') : 'pattern-miss';}"""))
            # 值已直接写进行内输入框,批量更新只是把「批量操作」区的值刷到行上 ——
            # 可选,失败也不影响提交(点了它反而会因为重渲染造成 detached)
            time.sleep(4)
            log("    行价(原价|折后):", page.evaluate("""() => {
              const m=document.body.innerText.match(
                /([\\d.]+)₫ - ([\\d.]+)₫[\\s\\S]{0,60}?% 折扣[\\s\\S]{0,60}?([\\d.]+)₫ - ([\\d.]+)₫/);
              return m? m.slice(1).join(' | ') : 'pattern-miss';}"""))

            if args.name:
                nm = page.locator("input").nth(0)
                nm.click()
                nm.fill(args.name)
                time.sleep(0.8)

            if args.submit:
                log("[7] 提交")
                cdp.send("Fetch.enable", {"patterns": [
                    {"urlPattern": PATTERN_ALL, "requestStage": "Request"}]})
                btn = page.evaluate_handle("""() => {
                  return [...document.querySelectorAll('button')]
                    .find(b=>b.innerText.trim()==='同意并发布') || null;}""").as_element()
                assert btn is not None, "找不到提交按钮"
                log(f"    disabled={btn.is_disabled()}")
                clicked = False
                for attempt in range(6):
                    try:
                        btn.click(timeout=8000)
                        clicked = True
                        break
                    except Exception as e:
                        log(f"    提交重试 {attempt}: {str(e)[:70]}")
                        time.sleep(3)
                        btn = page.evaluate_handle("""() => {
                          return [...document.querySelectorAll('button')]
                            .find(b=>b.innerText.trim()==='同意并发布') || null;}""").as_element()
                        if btn is None:
                            break
                log(f"    已点击={clicked}")
                for _ in range(30):
                    time.sleep(1)
                    if any((c.get("path") or "").endswith("/discount/create") for c in captured):
                        time.sleep(3)
                        break
            else:
                log("[7] 未提交,等 calc 预览请求…")
                time.sleep(10)
        finally:
            try:
                cdp.send("Fetch.disable")
            except Exception:
                pass

            try:
                log("提交后页面尾部:", page.evaluate("document.body.innerText.slice(-320)").replace(chr(10), " | "))
            except Exception:
                pass
            log(f"\n=== 捕获 {len(captured)} 条 ===")
            for c in captured:
                log(f"  {c.get('method'):5} {(c.get('path') or '')[:74]}"
                    f"  body={len(c.get('post_data') or '')}")
            if captured:
                NOTES.mkdir(parents=True, exist_ok=True)
                (NOTES / "promo_captured_requests.json").write_text(
                    json.dumps(captured, ensure_ascii=False, indent=2))

            creates = [c for c in captured if (c.get("path") or "").endswith("/discount/create")]
            if creates:
                raw = creates[-1].get("post_data") or ""
                (NOTES / "promo_create_payload.json").write_text(json.dumps(
                    {"path": creates[-1]["path"], "method": "POST",
                     "body": json.loads(raw) if raw.lstrip().startswith("{") else None,
                     "body_raw": raw, "all_requests": captured},
                    ensure_ascii=False, indent=2))
                log(f"\n=== discount/create payload → notes/promo_create_payload.json ===\n{raw[:3500]}")
            else:
                log("\n(未捕获 discount/create)")
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
