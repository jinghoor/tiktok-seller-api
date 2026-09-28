#!/usr/bin/env python3
"""抓 discount/create 的完整请求体 —— 最终可用方案。

抓包机制演进(为什么最后是 Fetch domain):
  1. 页面内注 JS hook(XHR/fetch 包装)  → 同域请求能抓,但 promotion API 在
     api16-normal-sg 跨域域,微前端里那条链路绕过了主 frame 的 window.XMLHttpRequest → 抓不到
  2. Playwright page.on("request")     → 能看见请求,但 connectOverCDP 下 post_data 恒为 None
  3. Playwright page.route             → 完全拦不到(请求不走 Playwright 的路由层)
  4. CDP Network.requestWillBeSent     → 能看见请求,postData 仍为 None
  5. CDP Fetch.requestPaused           → ✅ request.postData 有完整 body,continueRequest 放行

定位要点:
  - 折扣类型 radio val=1 百分比 / val=2 一口价,必须显式选中
  - 商品行 checkbox 只能点 label 容器才更新 React state
  - 这个 SPA 里 input 的 offsetParent 为 null,不能用它做可见性过滤

用法:
  python3 promo_capture_v2.py [--discount 10] [--name NAME] [--keep-tab]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "notes" / "promo_create_payload.json"
PORT = "http://127.0.0.1:CDP_PORT"
CREATE_URL = ("https://seller.tiktokshopglobalselling.com/promotion/"
              "marketing-tools/discount/create?shop_region=VN")
PATTERN = "*api16-normal-sg.tiktokshopglobalselling.com/api/v1/promotion*"

JS_FIRST_ENABLED_ROW = """() => {
  const m=[...document.querySelectorAll('[class*=modal]')]
    .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
  if(!m) return -1;
  const cbs=[...m.querySelectorAll('input[type=checkbox]')].slice(2);
  return cbs.findIndex(e=>!e.closest('[class*=checkbox-disabled]'));
}"""

JS_ROW_INFO = """(i) => {
  const m=[...document.querySelectorAll('[class*=modal]')]
    .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
  const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
  if(!e) return null;
  let r=e; for(let k=0;k<12&&r;k++){ r=r.parentElement;
    if(r&&r.className&&/row|tr/.test(r.className)) return (r.innerText||'').replace(/\\s+/g,' ').slice(0,110); }
  return null;
}"""

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

JS_BATCH_INPUT_INDEX = """() => {
  const all=[...document.querySelectorAll('input')];
  const hits=[...document.querySelectorAll('*')]
    .filter(e=>(e.innerText||'').trim()==='% 折扣' && e.children.length===0);
  for(const h of hits){
    let box=h;
    for(let i=0;i<8&&box;i++){
      box=box.parentElement; if(!box) break;
      const inp=box.querySelector('input[type=text]:not([disabled])');
      if(inp && !inp.placeholder) return all.indexOf(inp);
    }
  }
  const c=all.filter(e=>e.type==='text' && (e.className||'').includes('size-large')
                        && !e.disabled && !e.placeholder);
  return c.length ? all.indexOf(c[c.length-1]) : -1;
}"""


def log(*a):
    print(*a, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discount", default="10")
    ap.add_argument("--name", default=None)
    ap.add_argument("--keep-tab", action="store_true")
    ap.add_argument("--submit", action="store_true",
                    help="真的点「同意并发布」；默认只跑到批量更新(会触发 calc 预览,零副作用)")
    args = ap.parse_args()

    captured: list[dict] = []
    rows_meta: list[dict] = []

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(PORT)
        ctx = b.contexts[0]
        page = ctx.new_page()
        cdp = ctx.new_cdp_session(page)
        cdp.send("Fetch.enable", {"patterns": [{"urlPattern": PATTERN,
                                                "requestStage": "Request"}]})

        def on_paused(ev):
            rid = ev.get("requestId")
            try:
                r = ev.get("request", {})
                u = r.get("url", "")
                if r.get("method") != "OPTIONS":
                    captured.append({"method": r.get("method"),
                                     "path": u.split("?")[0].split(".com")[-1],
                                     "url": u,
                                     "postData": r.get("postData")})
            except Exception as e:
                captured.append({"_err": str(e)[:120]})
            finally:
                # 必须放行,否则页面请求全部挂起
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
            log("    表单就绪")

            log("[2] 选「百分比折扣」")
            page.locator("label", has_text="百分比折扣").first.click()
            time.sleep(1.2)
            if page.evaluate("[...document.querySelectorAll('input[type=radio]')][0].checked") is not True:
                raise RuntimeError("百分比折扣未选中")

            log("[3] 打开「选择商品」")
            page.locator("button", has_text="选择商品").first.click()
            for _ in range(25):
                time.sleep(1.2)
                if page.evaluate(JS_MODAL_STATE).get("rows", 0) > 0:
                    break
            st = page.evaluate(JS_MODAL_STATE)
            log(f"    {json.dumps(st, ensure_ascii=False)}")
            if not st.get("enabled"):
                raise RuntimeError("没有可勾选商品(与现有活动时间重叠)")

            idx = page.evaluate(JS_FIRST_ENABLED_ROW)
            rows_meta.append({"row_index": idx, "row_text": page.evaluate(JS_ROW_INFO, idx)})
            log(f"[4] 勾选 row#{idx}: {rows_meta[-1]['row_text']}")
            h = page.evaluate_handle("""(i) => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
              return e.closest('label') || e.closest('[class*=checkbox]');
            }""", idx).as_element()
            h.scroll_into_view_if_needed()
            h.click()
            time.sleep(1.5)
            if not page.evaluate(JS_MODAL_STATE).get("selected"):
                raise RuntimeError("勾选未生效")

            log("[5] 完成 → 回到表单")
            page.locator("button", has_text="完成").first.click()
            time.sleep(3)
            if "件商品" not in page.evaluate("document.body.innerText"):
                raise RuntimeError("商品未加入表单")

            log("[6] 全选行 → 填折扣 → 批量更新")
            page.evaluate("""() => {
              const cbs=[...document.querySelectorAll('input[type=checkbox]')];
              const head=cbs[0];
              const lab=head.closest('label')||head.closest('[class*=checkbox]');
              (lab||head).click();
            }""")
            time.sleep(1.5)
            bi = page.evaluate(JS_BATCH_INPUT_INDEX)
            if bi < 0:
                raise RuntimeError("定位折扣输入框失败")
            inp = page.locator("input").nth(bi)
            inp.click()
            inp.fill(args.discount)
            time.sleep(0.8)
            page.locator("button", has_text="批量更新").first.click()
            time.sleep(3)
            log("    行价:", page.evaluate("""() => {
              const m=document.body.innerText.match(/([\\d.]+)₫ - ([\\d.]+)₫[\\s\\S]{0,60}?% 折扣[\\s\\S]{0,60}?([\\d.]+)₫ - ([\\d.]+)₫/);
              return m? m.slice(1).join(' | ') : 'pattern-miss';}"""))

            if args.name:
                nm = page.locator("input").nth(0)
                nm.click()
                nm.fill(args.name)
                time.sleep(0.6)

            if args.submit:
                log("[7] 提交")
                btn = page.locator("button", has_text="同意并发布").first
                log(f"    disabled={btn.is_disabled()}")
                btn.click()
                for _ in range(30):
                    time.sleep(1)
                    if any((c.get("path") or "").endswith("/discount/create") for c in captured):
                        time.sleep(3)
                        break
            else:
                log("[7] --no-submit: 停在提交前,只保留 calc 预览请求")
                time.sleep(2)
        finally:
            try:
                cdp.send("Fetch.disable")
            except Exception:
                pass

            log(f"\n=== 捕获 {len(captured)} 条 promotion 请求 ===")
            for c in captured:
                log(f"  {c.get('method'):5} {(c.get('path') or '')[:76]}"
                    f"  postData={len(c.get('postData') or '')}")

            ALL = HERE / "notes" / "promo_captured_requests.json"
            if captured:
                ALL.parent.mkdir(parents=True, exist_ok=True)
                ALL.write_text(json.dumps(captured, ensure_ascii=False, indent=2))
                log(f"（全部捕获 → {ALL}）")

            creates = [c for c in captured if (c.get("path") or "").endswith("/discount/create")]
            if creates:
                c = creates[-1]
                raw = c.get("postData") or ""
                OUT.parent.mkdir(parents=True, exist_ok=True)
                OUT.write_text(json.dumps({
                    "path": c["path"],
                    "method": c["method"],
                    "body": json.loads(raw) if raw.lstrip().startswith(("{", "[")) else None,
                    "body_raw": raw,
                    "rows": rows_meta,
                    "all_requests": captured,
                }, ensure_ascii=False, indent=2))
                log(f"\n=== discount/create payload → {OUT} ===")
                log(raw[:3500])
            else:
                log("\n未捕获 discount/create")
                try:
                    log("页面尾部:", page.evaluate("document.body.innerText.slice(-400)"))
                except Exception:
                    pass

            if not args.keep_tab:
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
        raise
