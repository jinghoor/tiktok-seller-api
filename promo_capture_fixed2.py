#!/usr/bin/env python3
"""自己开专用 tab → 立刻挂 Fetch → 自动提交一口价 → 抓 fixed_price/create 的 payload。

为什么要"自己开 tab":
  promo_watch_create.py 靠 ctx.pages 轮询挂载新 tab，实测会卡住（日志里只挂上最初
  4 个页面，operator 新开的 tab 从没挂上），所以改成在同进程内先开 tab 再挂 Fetch。

为什么要用 Emulation.setDeviceMetricsOverride 而不是 page.set_viewport_size:
  后台 tab 的 viewport 为 0 时商品表格虚拟滚动不渲染任何行（checkbox 和输入框都不进
  DOM）；而 set_viewport_size 对非活动 tab 可能挂起 —— CDP 层面的 override 更稳。

页面定位要点（都是踩出来的）:
  - 折扣类型 radio: val=1 百分比 / val=2 一口价，必须显式选中
  - 弹层「完成」按钮要限定在弹层内 + 用 Playwright 真实 click
  - 行 checkbox 只能用键盘 Space（鼠标点击会让整个表格从 DOM 卸载）
  - 金额输入框用 data-prefill-id 前缀定位；填完要 press("Tab") 让 React 收值
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
NOTES = HERE / "notes"
CREATE_URL = ("https://seller.tiktokshopglobalselling.com/promotion/"
              "marketing-tools/discount/create?shop_region=VN")

JS_MODAL = """() => {
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


def log(*a):
    print(*a, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--price", default="30000")
    ap.add_argument("--name", default=None)
    ap.add_argument("--type", choices=["fixed", "percent"], default="fixed")
    ap.add_argument("--no-submit", action="store_true")
    ap.add_argument("--dimension", choices=["spu", "sku"], default="sku",
                    help="一口价实测活动都是 SKU 维度(dim=1)")
    args = ap.parse_args()

    # 1) 用 CDP HTTP 开一个专用 tab（会成为活动 tab，不需要再抢焦点）
    req = urllib.request.Request(
        f"http://127.0.0.1:{args.port}/json/new?"
        + urllib.parse.quote(CREATE_URL, safe=""), method="PUT")
    new = json.load(urllib.request.urlopen(req, timeout=15))
    target_id = new.get("id")
    log(f"[0] 已开专用 tab id={target_id}")

    captured: list[dict] = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{args.port}")
        page = None
        for _ in range(20):
            time.sleep(1)
            page = next((x for x in b.contexts[0].pages
                         if "discount/create" in x.url), None)
            if page:
                break
        assert page is not None, "找不到刚开的 tab"
        log(f"    锁定: {page.url[:76]}")
        # 关键：非活动 tab 时 Chromium 可能不把合成输入事件派发给 React，
        # 表现出来就是 DOM checked=true 而表单 state 为空（"请先选择折扣类型"= 这么来的）。
        # operator 已授权操作他的电脑，这里把 tab 激活。
        try:
            page.bring_to_front()
            time.sleep(1.5)
        except Exception as e:
            log(f"    bring_to_front 失败: {str(e)[:60]}")
        log(f"    已激活 tab (hasFocus={page.evaluate('document.hasFocus()')})")

        cdp = b.contexts[0].new_cdp_session(page)
        # CDP 层面的 viewport —— 不加这行表格不渲染任何行
        cdp.send("Emulation.setDeviceMetricsOverride", {
            "width": 1600, "height": 1200, "deviceScaleFactor": 1, "mobile": False})
        # 抓包交给 promo_catcher.py（原始 websocket + 独立线程）——
        # 在这里 enable Fetch 会让回调里的 continueRequest 挂死整个页面

        def on_paused(ev):
            rid = ev.get("requestId")
            try:
                r = ev.get("request", {})
                if r.get("method") != "OPTIONS":
                    rec = {"at": time.strftime("%H:%M:%S"), "method": r.get("method"),
                           "path": r["url"].split("?")[0].split(".com")[-1],
                           "full_url": r.get("url"), "body": r.get("postData")}
                    captured.append(rec)
                    log(f"\n★ 捕获 {rec['method']} {rec['path']}\n{rec.get('body')}\n")
            except Exception as e:
                log("  记录异常:", str(e)[:90])
            finally:
                try:
                    cdp.send("Fetch.continueRequest", {"requestId": rid})
                except Exception:
                    pass

        # cdp.on("Fetch.requestPaused", on_paused)   # 见上：会让页面挂死，不要开

        try:
            log("[1] 等表单")
            for _ in range(40):
                time.sleep(1)
                if "折扣类型" in page.evaluate("document.body.innerText"):
                    break
            log(f"    就绪（viewport {page.evaluate('innerWidth')}x{page.evaluate('innerHeight')}）")

            kind = "一口价" if args.type == "fixed" else "百分比折扣"
            want = 1 if args.type == "fixed" else 0
            log(f"[2] 选「{kind}」(radio index={want})")
            # check() 是 Playwright 专门给 radio/checkbox 的接口：会校验并重试到真正选中。
            # 之前用 label.click() 只让 DOM checked=true，React 表单 state 仍是空的，
            # 页面报"请先选择折扣类型"，submit 就被前端静默拦掉（这是前面反复失败的根因）。
            try:
                page.locator("input[type=radio]").nth(want).check(force=True, timeout=10000)
                log("    用 check() 选中")
            except Exception as e:
                log(f"    check() 失败，退回 label.click(): {str(e)[:60]}")
                page.locator("label", has_text=kind).first.click()
            time.sleep(1.5)
            rd = page.evaluate("[...document.querySelectorAll('input[type=radio]')].map(e=>e.checked)")
            still = "请先选择折扣类型" in page.evaluate("document.body.innerText")
            log(f"    radios={rd}  表单仍报未选类型={still}")

            if args.dimension == "sku":
                log("[2b] 选「指定变体」(radio index=3)")
                try:
                    page.locator("input[type=radio]").nth(3).check(force=True, timeout=10000)
                except Exception as e:
                    log(f"    check() 失败，退回 label.click(): {str(e)[:60]}")
                    page.locator("label", has_text="指定变体").first.click()
                time.sleep(1.5)
                rd2 = page.evaluate("[...document.querySelectorAll('input[type=radio]')].map(e=>e.checked)")
                log(f"     radios={rd2}")

            log("[3] 打开商品弹层")
            page.locator("button", has_text="选择商品").first.click()
            for _ in range(30):
                time.sleep(1.2)
                if page.evaluate(JS_MODAL).get("rows", 0) > 0:
                    break
            st = page.evaluate(JS_MODAL)
            log(f"    {json.dumps(st, ensure_ascii=False)}")
            assert st.get("enabled"), "没有可勾选商品（与现有活动时间重叠）"

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
            assert page.evaluate(JS_MODAL).get("selected"), "勾选未生效"

            log("[5] 弹层内「完成」")
            done = page.evaluate_handle("""() => {
              const m=[...document.querySelectorAll('[class*=modal]')]
                .filter(e=>e.offsetParent!==null && (e.innerText||'').length>40).pop();
              return m ? [...m.querySelectorAll('button')].find(b=>b.innerText.trim()==='完成') : null;
            }""").as_element()
            assert done is not None, "找不到完成按钮"
            done.scroll_into_view_if_needed()
            done.click()
            for _ in range(15):
                time.sleep(1)
                cnt = page.evaluate("""() => {
                  const m=document.body.innerText.match(/(\\d+)\\s*件商品/);
                  return m? Number(m[1]) : -1;}""")
                if cnt and cnt > 0:
                    break
            log(f"    件商品 = {cnt}")
            assert cnt > 0, "商品未加入表单"

            log("[6] 逐个勾选所有行（键盘 Space）")
            for round_ in range(4):
                st = page.evaluate("""() => [...document.querySelectorAll('input[type=checkbox]')]
                  .map((e,i)=>({i, chk:e.checked, dis:!!e.closest('[class*=disabled]')}))""")
                todo = [x["i"] for x in st if not x["chk"] and not x["dis"]]
                log(f"    第{round_+1}轮: 共 {len(st)} 个 checkbox，未勾选 {len(todo)}")
                if not todo:
                    break
                for i in todo:
                    el = page.evaluate_handle("""(i) => {
                      const cbs=[...document.querySelectorAll('input[type=checkbox]')];
                      const e=cbs[i]; return e ? (e.closest('label')||e) : null;}""", i).as_element()
                    if el is None:
                        continue
                    try:
                        page.locator("input[type=checkbox]").nth(i).check(force=True, timeout=8000)
                        time.sleep(0.6)
                    except Exception as e:
                        log(f"      #{i} check 失败: {str(e)[:50]}")
                time.sleep(1.5)
            n_chk = page.evaluate('[...document.querySelectorAll("input[type=checkbox]")].filter(e=>e.checked).length')
            log(f"    最终勾选数 = {n_chk}")
            log("    已选择:", page.evaluate("(document.body.innerText.match(/已选择\\s*\\d+/g)||[]).join(' | ')"))

            log("[7] dump 输入框（找金额位）")
            dump = page.evaluate("""() => [...document.querySelectorAll('input')]
              .filter(e=>e.offsetParent!==null)
              .map((e,i)=>({i, type:e.type, prefill:e.getAttribute('data-prefill-id'),
                            ph:e.placeholder, val:String(e.value).slice(0,12)}))""")
            for d in dump:
                log(f"    {d}")
            pref = ("fixed" if args.type == "fixed" else "percentage")
            cands = [d for d in dump if d.get("prefill") and pref in str(d["prefill"]).lower()]
            if not cands:
                cands = [d for d in dump if d.get("prefill") and "price" in str(d["prefill"]).lower()]
            log(f"    → 命中 {len(cands)} 个: {[c['prefill'] for c in cands]}")
            filled = 0
            for c in cands:
                try:
                    el = page.locator(f'input[data-prefill-id="{c["prefill"]}"]').first
                    el.fill(args.price, timeout=10000)
                    el.press("Tab")
                    filled += 1
                    time.sleep(0.7)
                except Exception as e:
                    log(f"    {c['prefill'][:40]} 填失败: {str(e)[:60]}")
            log(f"    已填 {filled} 个输入框")

            # fill() 只改 DOM 值，未必进 React 表单 state ——
            # 「批量更新」才是把优惠价刷进表单的动作（与 checkbox 需键盘 Space 同理）
            log("[7b] 点「批量更新」把优惠价刷进表单")
            try:
                bu = page.evaluate_handle("""() => [...document.querySelectorAll('button')]
                  .find(b=>b.innerText.trim()==='批量更新') || null""").as_element()
                if bu is not None:
                    log(f"    批量更新 disabled={bu.is_disabled()}")
                    bu.click(timeout=8000)
                    time.sleep(3)
                    log("    已点击批量更新")
                    body2 = page.evaluate("document.body.innerText")
                    log(f"    折扣列是否出现折后价: {'优惠价' in body2}")
                else:
                    log("    未找到批量更新按钮")
            except Exception as e:
                log(f"    批量更新失败: {str(e)[:70]}")

            if args.name:
                nm = page.locator("input").nth(0)
                nm.click(); nm.fill(args.name); nm.press("Tab")
                time.sleep(0.6)
            time.sleep(4)

            if args.no_submit:
                log("[8] --no-submit，停在提交前")
            else:
                log("[8] 提交")
                for attempt in range(8):
                    btn = page.evaluate_handle("""() => [...document.querySelectorAll('button')]
                      .find(b=>b.innerText.trim()==='同意并发布') || null""").as_element()
                    if btn is None:
                        time.sleep(3); continue
                    try:
                        btn.click(timeout=8000)
                        log(f"    已点击（第 {attempt+1} 次）")
                        break
                    except Exception as e:
                        log(f"    第 {attempt+1} 次失败: {str(e)[:70]}")
                        time.sleep(3)
                for _ in range(25):
                    time.sleep(1)
                    if captured:
                        time.sleep(3)
                        break

            if not args.no_submit:
                try:
                    log("\n提交后页面提示:")
                    tail = page.evaluate("document.body.innerText.slice(-500)").replace("\n", " | ")
                    log("  " + tail[:420])
                    tips = page.evaluate("""() => JSON.stringify(
                      [...document.querySelectorAll('[class*=message],[class*=alert],[class*=tooltip],[class*=form-item-error]')]
                        .filter(e=>e.offsetParent!==null && (e.innerText||'').trim())
                        .slice(0,6).map(e=>(e.innerText||'').replace(/\\s+/g,' ').slice(0,90)))""")
                    log("  可见提示:", tips)
                except Exception as e:
                    log("  读页面失败:", str(e)[:70])

            # 提交后从服务端查最新活动，反查 promotion_id
            if captured:
                try:
                    import sys
                    sys.path.insert(0, str(HERE))
                    from tk01_promo_client import PromoClient
                    C = PromoClient(port=args.port)
                    latest = C.discounts(1, 3)
                    log("\n最新活动:")
                    for it in latest:
                        log(f"  {it['id']} type={it['seller_discount_type']} {it['name'][:30]}")
                    newest = latest[0]
                    if newest["seller_discount_type"] == 2:
                        rows = C.promo_list_products(newest["id"])
                        log(f"  一口价活动商品数 = {len(rows)}")
                        C.discount_park(newest["id"])
                        log("  已 park 到远期")
                except Exception as e:
                    log("  反查失败:", str(e)[:100])
        finally:
            try:
                cdp.send("Fetch.disable")
            except Exception:
                pass
            log(f"\n=== 捕获 {len(captured)} 条 ===")
            for c in captured:
                log(f"  {c['method']} {c['path']}  body={len(c.get('body') or '')}B")
            if captured:
                NOTES.mkdir(parents=True, exist_ok=True)
                (NOTES / "promo_fixed_payload.json").write_text(
                    json.dumps(captured, ensure_ascii=False, indent=2))
                log(f"\n→ notes/promo_fixed_payload.json")
                log("PAYLOAD:\n" + (captured[-1].get("body") or "")[:3000])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
