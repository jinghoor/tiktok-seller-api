#!/usr/bin/env python3
"""探测：创建商品折扣页上「勾选商品行」到底哪种方式有效。

背景：页面前置流程已能稳定走到「1 件商品 + 批量操作区 + 折扣输入框 index=13」，
但「批量更新」按钮 disabled，需要行被选中(已选择 > 0)。
已证实：用 JS 找到 input[type=checkbox] 的 label 再用 Playwright click，
       会导致整个商品表格从 DOM 卸载(cb: 0) —— 疑似滚动或误命中控件。

每个策略在独立的新 page 里跑一遍前置流程，互不污染。
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = ("https://seller.tiktokshopglobalselling.com/promotion/"
       "marketing-tools/discount/create?shop_region=VN")
SHOT = Path(__file__).resolve().parent / "notes"

JS_STATE = """() => ({
  url: location.href.slice(-46),
  cbTotal: document.querySelectorAll('input[type=checkbox]').length,
  cbChecked: [...document.querySelectorAll('input[type=checkbox]')].filter(e=>e.checked).length,
  selected: (document.body.innerText.match(/已选择\\s*\\d+/)||[''])[0],
  goodsCount: (document.body.innerText.match(/(\\d+)\\s*件商品/)||[,'-1'])[1],
  hasBulk: document.body.innerText.includes('批量操作'),
  discountInput: (()=>{
    const all=[...document.querySelectorAll('input')];
    const c=all.filter(e=>e.type==='text' && (e.className||'').includes('theme-arco-input-size-large')
                          && !e.disabled && !e.placeholder);
    return c.length ? all.indexOf(c[c.length-1]) : -1;})(),
  bulkBtn: [...document.querySelectorAll('button')].filter(b=>b.innerText.trim()==='批量更新')
             .map(b=>b.disabled)
})"""


def reach_step5(page, tag: str) -> bool:
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    for _ in range(30):
        time.sleep(1)
        if "折扣类型" in page.evaluate("document.body.innerText"):
            break
    page.locator("label", has_text="百分比折扣").first.click()
    time.sleep(1.2)
    page.locator("button", has_text="选择商品").first.click()
    for _ in range(25):
        time.sleep(1.2)
        if page.evaluate("""()=>{const m=[...document.querySelectorAll('[class*=modal]')]
              .filter(e=>e.offsetParent!==null&&(e.innerText||'').length>40).pop();
              return m? m.querySelectorAll('input[type=checkbox]').length : 0;}""") > 2:
            break
    idx = page.evaluate("""()=>{const m=[...document.querySelectorAll('[class*=modal]')]
      .filter(e=>e.offsetParent!==null&&(e.innerText||'').length>40).pop();
      return [...m.querySelectorAll('input[type=checkbox]')].slice(2)
        .findIndex(e=>!e.closest('[class*=checkbox-disabled]'));}""")
    if idx < 0:
        print(f"  [{tag}] 弹层无可用商品行")
        return False
    h = page.evaluate_handle("""(i)=>{const m=[...document.querySelectorAll('[class*=modal]')]
      .filter(e=>e.offsetParent!==null&&(e.innerText||'').length>40).pop();
      const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
      return e.closest('label')||e.closest('[class*=checkbox]');}""", idx).as_element()
    h.scroll_into_view_if_needed()
    h.click()
    time.sleep(1.5)
    done = page.evaluate_handle("""()=>{const m=[...document.querySelectorAll('[class*=modal]')]
      .filter(e=>e.offsetParent!==null&&(e.innerText||'').length>40).pop();
      return m ? [...m.querySelectorAll('button')].find(b=>b.innerText.trim()==='完成') : null;}""").as_element()
    if done is None:
        print(f"  [{tag}] 找不到完成按钮")
        return False
    done.scroll_into_view_if_needed()
    done.click()
    time.sleep(5)
    return True


STRATEGIES = {
    "A_head_selectall_locator": lambda pg: pg.locator("label.theme-arco-checkbox").first.click(),
    "B_row_locator_nth1":       lambda pg: pg.locator("label.theme-arco-checkbox").nth(1).click(),
    "C_head_force_noscroll":    lambda pg: pg.locator("label.theme-arco-checkbox").first.click(force=True),
    "D_js_click_label_noscroll": lambda pg: pg.evaluate("""() => {
        const cbs=[...document.querySelectorAll('input[type=checkbox]')];
        const row=cbs[cbs.length-1];
        const lab=row.closest('label')||row.closest('[class*=checkbox]')||row;
        lab.click();
        return lab.className;
    }"""),
    "E_keyboard_space":         None,   # 特殊处理
}


def main() -> None:
    results = {}
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:CDP_PORT")
        ctx = b.contexts[0]
        for name, fn in STRATEGIES.items():
            print(f"\n{'='*10} 策略 {name} {'='*10}")
            page = ctx.new_page()
            page.set_viewport_size({"width": 1600, "height": 1200})
            try:
                if not reach_step5(page, name):
                    results[name] = {"ok": False, "reason": "reach_step5 failed"}
                    continue
                before = page.evaluate(JS_STATE)
                print(f"  前置状态: goods={before['goodsCount']} discountInput={before['discountInput']} "
                      f"bulkBtn={before['bulkBtn']} cb={before['cbTotal']}")
                if before["discountInput"] < 0:
                    results[name] = {"ok": False, "reason": "前置未就绪"}
                    continue
                # 填折扣
                inp = page.locator("input").nth(before["discountInput"])
                inp.click()
                inp.fill("10")
                time.sleep(0.8)
                # 执行勾选策略
                try:
                    if name == "E_keyboard_space":
                        box = page.evaluate_handle("""() => {
                          const cbs=[...document.querySelectorAll('input[type=checkbox]')];
                          const row=cbs[cbs.length-1];
                          return row ? (row.closest('label')||row) : null;}""").as_element()
                        box.scroll_into_view_if_needed()
                        box.press("Space")
                    else:
                        fn(page)
                except Exception as e:
                    print(f"  策略执行异常: {str(e)[:90]}")
                time.sleep(3)
                after = page.evaluate(JS_STATE)
                print(f"  执行后: cb={after['cbTotal']} checked={after['cbChecked']} "
                      f"selected='{after['selected']}' goods={after['goodsCount']} "
                      f"discountInput={after['discountInput']} bulkBtn={after['bulkBtn']}")
                page.screenshot(path=str(SHOT / f"promo_strategy_{name}.png"), full_page=False)
                ok = bool(after["cbChecked"]) and after["selected"] not in ("", "已选择 0")
                results[name] = {"ok": ok, "before": before, "after": after}
            except Exception as e:
                print(f"  异常: {str(e)[:140]}")
                results[name] = {"ok": False, "reason": str(e)[:140]}
            finally:
                try:
                    page.close()
                except Exception:
                    pass

    print(f"\n\n{'='*20} 汇总 {'='*20}")
    for k, v in results.items():
        mark = "✅ 可用" if v.get("ok") else "❌"
        print(f"  {mark} {k}  {json.dumps({kk: vv for kk, vv in v.items() if kk != 'ok'}, ensure_ascii=False)[:170]}")


if __name__ == "__main__":
    main()
