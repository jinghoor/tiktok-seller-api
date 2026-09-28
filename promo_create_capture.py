#!/usr/bin/env python3
"""端到端：在 SHOP_XBORDER 促销页创建一个商品折扣，并抓取 discount/create 的完整请求体。

流程本身已逆向清楚(见 TIKTOK_PROMOTION_API.md §8):
  1. 折扣类型 radio  val=1 百分比折扣 / val=2 一口价   —— 必须显式选中
  2. 商品粒度   radio  val=4 指定商品(默认) / val=1 指定变体
  3. 「选择商品」弹层里行 checkbox：只点 label 容器能更新 React state
     (派发合成事件 / input.click() / DOM checked=true 全部无效)
  4. 时间段内已打折的行会被 .theme-arco-checkbox-disabled 置灰
  5. 「批量操作」区填 % 折扣 → 「批量更新」应用
  6. 「同意并发布」

抓包说明:
  Playwright 的 request 回调里只能读本地缓存属性(url/method/post_data/status)。
  在里面调 res.text() 是同步 API,会和外层事件循环死锁 —— 上一版就是这么丢的 payload。

用法:
  python3 promo_create_capture.py                  # 走完整流程 + 抓包
  python3 promo_create_capture.py --prepare-only    # 只准备不提交(留页面等手工确认)
  python3 promo_create_capture.py --reuse           # 复用已有 create tab,不新开
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

captured: list[dict] = []


# ---- 页面查询 JS(只返回 JSON 可序列化值) ----

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
  const cbs=[...m.querySelectorAll('input[type=checkbox]')].slice(2);
  const e=cbs[i];
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
          done_disabled: btn? btn.disabled : null,
          count_text: (m.innerText.match(/已选择\\s*\\d+/)||[''])[0]};
}"""

JS_BATCH_INPUT = """() => {
  // 「批量操作」区里的 % 折扣 输入框：在含 '% 折扣' 文本的容器里找唯一可编辑 text input
  const all=[...document.querySelectorAll('*')];
  const n=all.find(e=>e.children.length===0 && (e.innerText||'').trim()==='% 折扣');
  if(!n) return null;
  let box=n; for(let i=0;i<5&&box;i++){ box=box.parentElement;
    const i2=box && box.querySelector('input[type=text]:not([disabled])');
    if(i2) return i2; }
  return null;
}"""

JS_BATCH_INPUT_INDEX = """() => {
  const el=(() => {
    const all=[...document.querySelectorAll('*')];
    const n=all.find(e=>e.children.length===0 && (e.innerText||'').trim()==='% 折扣');
    if(!n) return null;
    let box=n; for(let i=0;i<5&&box;i++){ box=box.parentElement;
      const i2=box && box.querySelector('input[type=text]:not([disabled])');
      if(i2) return i2; }
    return null;})();
  if(!el) return -1;
  return [...document.querySelectorAll('input')].indexOf(el);
}"""


def log(*a) -> None:
    print(*a, flush=True)


def wait_body(page, min_len: int = 900, secs: int = 40) -> int:
    n = 0
    for _ in range(secs):
        time.sleep(1)
        try:
            n = page.evaluate("document.body.innerText.length")
            if n and n >= min_len:
                return n
        except Exception:
            pass
    return n


def step_prepare(page, discount: str) -> bool:
    """把表单填到「同意并发布」之前的状态。返回是否成功。"""
    log("\n[1] 等表单渲染…")
    n = wait_body(page)
    if "折扣类型" not in page.evaluate("document.body.innerText"):
        log(f"    表单未渲染 (body={n})")
        return False
    log(f"    OK body={n}")

    log("[2] 选「百分比折扣」")
    lab = page.locator("label", has_text="百分比折扣").first
    lab.click()
    time.sleep(1.2)
    rd = page.evaluate("[...document.querySelectorAll('input[type=radio]')].map(e=>e.checked)")
    log(f"    radios={rd}")
    if not rd or rd[0] is not True:
        log("    百分比折扣未选中 —— 中止")
        return False

    log("[3] 打开「选择商品」弹层")
    page.locator("button", has_text="选择商品").first.click()
    for i in range(25):
        time.sleep(1.2)
        st = page.evaluate(JS_MODAL_STATE)
        if st.get("rows", 0) > 0:
            break
    st = page.evaluate(JS_MODAL_STATE)
    log(f"    弹层: {json.dumps(st, ensure_ascii=False)}")
    if not st.get("enabled"):
        log("    没有可勾选的行(全部与现有活动时间重叠) —— 中止")
        return False

    log("[4] 勾选第一行可用商品(点 label 容器,不是 input)")
    idx = page.evaluate(JS_FIRST_ENABLED_ROW)
    info = page.evaluate(JS_ROW_INFO, idx)
    log(f"    row#{idx}: {info}")
    h = page.evaluate_handle("""(i) => {
      const m=[...document.querySelectorAll('[class*=modal]')]
        .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
      const e=[...m.querySelectorAll('input[type=checkbox]')].slice(2)[i];
      return e.closest('label') || e.closest('[class*=checkbox]');
    }""", idx).as_element()
    h.scroll_into_view_if_needed()
    h.click()
    time.sleep(1.5)
    st = page.evaluate(JS_MODAL_STATE)
    log(f"    勾选后: {json.dumps(st, ensure_ascii=False)}")
    if not st.get("selected"):
        log("    勾选未生效 —— 中止")
        return False

    log("[5] 点「完成」")
    page.locator("button", has_text="完成").first.click()
    time.sleep(3)
    txt = page.evaluate("document.body.innerText")
    if "件商品" not in txt:
        log("    商品未加入表单 —— 中止")
        return False

    log("[6] 全选行 + 填折扣 + 批量更新")
    page.evaluate("""() => {
      const cbs=[...document.querySelectorAll('input[type=checkbox]')];
      const head=cbs[0];
      const lab=head.closest('label')||head.closest('[class*=checkbox]');
      (lab||head).click();
    }""")
    time.sleep(1.5)
    bi = page.evaluate(JS_BATCH_INPUT_INDEX)
    log(f"    % 折扣 input index={bi}")
    if bi < 0:
        log("    找不到折扣输入框 —— 中止")
        return False
    inp = page.locator("input").nth(bi)
    inp.click()
    inp.fill(discount)
    time.sleep(0.8)
    log(f"    填入 {inp.input_value()}")
    page.locator("button", has_text="批量更新").first.click()
    time.sleep(2.5)

    ok = page.evaluate(f"""() => document.body.innerText.includes('% 折扣') &&
        [...document.querySelectorAll('input')].some(e=>e.value==='{discount}')""")
    # 折扣是否真的落到行上：原价 × (1-折扣) 会出现在行文本里
    row_ok = page.evaluate("""(d) => {
      const t=document.body.innerText;
      const m=t.match(/([\\d.]+)₫ - ([\\d.]+)₫[\\s\\S]{0,40}?% 折扣[\\s\\S]{0,40}?([\\d.]+)₫ - ([\\d.]+)₫/);
      if(!m) return 'pattern-miss';
      const f=1-Number(d)/100;
      return Math.abs(Number(m[1].replace(/\\./g,''))*f - Number(m[3].replace(/\\./g,'')))<2 ? 'applied' : 'mismatch:'+m.slice(1).join(',');
    }""", discount)
    log(f"    折扣应用检查: {row_ok}  (input 值正确={ok})")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--reuse", action="store_true", help="复用已有 create tab")
    ap.add_argument("--discount", default="10", help="百分比折扣值")
    ap.add_argument("--name", default=None, help="活动名称(默认用页面自动生成的)")
    args = ap.parse_args()

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(PORT)
        ctx = b.contexts[0]
        existing = next((x for x in ctx.pages if "discount/create" in x.url), None)
        if args.reuse and existing:
            page = existing
            log("复用 tab:", page.url[:90])
            page.reload(wait_until="domcontentloaded", timeout=60000)
        else:
            page = ctx.new_page()
            log("新 tab →", CREATE_URL)
            page.goto(CREATE_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        try:
            if not step_prepare(page, args.discount):
                log("\n准备阶段失败,未提交")
                return

            if args.name:
                page.locator("input").nth(0).fill(args.name)
                time.sleep(0.5)

            if args.prepare_only:
                log("\n--prepare-only: 停在提交前,未发出 create 请求")
                return

            # 监听必须在点击之前挂好；回调里只读本地缓存属性
            def on_request(req):
                try:
                    u = req.url
                    if "/api/v1/promotion/" not in u or req.method == "OPTIONS":
                        return
                    captured.append({"method": req.method,
                                     "path": u.split("?")[0].split(".com")[-1],
                                     "url": u, "body": req.post_data})
                except Exception as e:            # 回调里绝不冒泡异常
                    captured.append({"_hook_err": str(e)[:120]})

            def on_response(res):
                try:
                    for c in captured:
                        if c.get("url") == res.url and "status" not in c:
                            c["status"] = res.status
                except Exception:
                    pass

            page.on("request", on_request)
            page.on("response", on_response)

            log("\n[7] 点「同意并发布」")
            btn = page.locator("button", has_text="同意并发布").first
            log(f"    disabled={btn.is_disabled()}")
            btn.click()

            for _ in range(25):
                time.sleep(1)
                if any((c.get("path") or "").endswith("/discount/create") for c in captured):
                    time.sleep(3)
                    break
        finally:
            log(f"\n=== 捕获 {len(captured)} 条 promotion 请求 ===")
            for c in captured:
                log(f"  [{c.get('status')}] {c['method']:5} {(c.get('path') or '')[:78]}"
                    f"  body={len(c.get('body') or '')}")

            creates = [c for c in captured if (c.get("path") or "").endswith("/discount/create")]
            if creates:
                c = creates[-1]
                raw = c.get("body") or ""
                OUT.parent.mkdir(parents=True, exist_ok=True)
                OUT.write_text(json.dumps({
                    "path": c["path"], "method": c["method"],
                    "body": json.loads(raw) if raw.lstrip().startswith(("{", "[")) else None,
                    "body_raw": raw,
                    "all_requests": captured,
                }, ensure_ascii=False, indent=2))
                log(f"\n=== discount/create payload → {OUT} ===")
                log("REQ :", raw[:2600])
            else:
                log("\n未捕获 discount/create（提交可能被前端校验拦下）")
                try:
                    log("页面尾部:", page.evaluate("document.body.innerText.slice(-500)"))
                except Exception:
                    pass


if __name__ == "__main__":
    main()
