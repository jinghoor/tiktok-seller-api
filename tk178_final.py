#!/usr/bin/env python3
"""TK178 上架 —— 一次性把剩余字段填完并提交，抓 create 的真实 payload。

拿到 payload 结构后，后续就用纯 API 调 `/api/v1/product/local/product/create`。

    python3 tk178_final.py --fill     # 只填，不提交
    python3 tk178_final.py --submit   # 填完并提交，抓 payload
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CDP = os.environ.get("TK178_CDP", "http://127.0.0.1:CDP_PORT")
sys.path.insert(0, HERE)
from tk178_fill2 import (get_page, scroll_element_to, wrap_label, click_at,  # noqa: E402
                         op_pick_search)

PRICE = "200000"
STOCK = "100"
WEIGHT = "80"
DIMS = ("12", "4", "3")
LIC_NO = "GNUMBER_REDACTED"
LIC_DATE = "2024-01-15"
LIC_PLACE_ASCII = "Guangdong"


def _wrap_js(label: str) -> str:
    """表单项容器。"""
    return ("(function(){ const lb=[...document.querySelectorAll('span._title_80dgt_103')]"
            f".find(e=>(e.textContent||'').trim()==={json.dumps(label, ensure_ascii=False)});"
            " if(!lb) return null; let n=lb;"
            " for(let i=0;i<9&&n.parentElement;i++){n=n.parentElement;"
            "   if(n.querySelector('input,textarea,[contenteditable=true]')) break;}"
            " return n; })()")


def _inputs_js(label: str) -> str:
    return ("(function(){ const lb=[...document.querySelectorAll('span._title_80dgt_103')]"
            f".find(e=>(e.textContent||'').trim()==={json.dumps(label, ensure_ascii=False)});"
            " if(!lb) return null; let n=lb;"
            " for(let i=0;i<9&&n.parentElement;i++){n=n.parentElement;"
            "   if(n.querySelector('input,textarea,[contenteditable=true]')) break;}"
            " return [...n.querySelectorAll('input')].filter(i=>i.offsetParent!==null); })()")


def type_into(page, label, value, *, index=None, clear=True):
    """把值敲进某 label 下第 index 个可见 input(table 里用 index 区分长宽高)。"""
    js = _inputs_js(label)
    n = page.evaluate("(j) => { const a = eval(j); return a ? a.length : -1; }", js)
    if n is None or n < 0:
        print(f"    !! {label} 找不到 input")
        return False
    idx = index if index is not None else (len(page.evaluate("(j)=>{const a=eval(j);return a?a.map(i=>({c:(i.className||'').toString(),v:i.value}));[];}") or []) and 0)
    idx = 0 if index is None else index
    box = page.evaluate("""(args) => {
      const a = eval(args.js);
      const e = a[args.idx];
      if (!e) return null;
      const r = e.getBoundingClientRect();
      return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2), w: Math.round(r.width)};
    }""", {"js": js, "idx": idx})
    if not box:
        print(f"    !! {label}[{idx}] 定位失败 (共 {n} 个)")
        return False
    # 滚到视口中上部再点,避免吸顶导航拦截
    page.evaluate("""(args) => {
      const a = eval(args.js); const e = a[args.idx];
      if (e) e.scrollIntoView({block: 'center'});
    }""", {"js": js, "idx": idx})
    time.sleep(0.6)
    box = page.evaluate("""(args) => {
      const a = eval(args.js); const e = a[args.idx];
      if (!e) return null;
      const r = e.getBoundingClientRect();
      return {x: Math.round(r.x + Math.min(r.width/2, 200)), y: Math.round(r.y + r.height/2)};
    }""", {"js": js, "idx": idx})
    page.mouse.click(box["x"], box["y"])
    time.sleep(0.35)
    if clear:
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
    page.keyboard.type(value, delay=20)
    time.sleep(0.7)
    got = page.evaluate("""(args) => {
      const a = eval(args.js); return a ? a.map(i => i.value) : null;
    }""", {"js": js})
    print(f"    {label}[{idx}] = {value!r}  → {got}")
    return bool(got and any(v for v in got))


def fill_license(page):
    print(">>> License 三件套")
    # License number:ASCII 值(控件吞中文)
    type_into(page, "License number", LIC_NO, index=2)
    # Date of issuance:试直接敲日期文本
    ok = type_into(page, "Date of issuance", LIC_DATE, index=0)
    if not ok:
        # 退而点开日历选今天
        b = scroll_element_to(page, wrap_label("Date of issuance", "[class*=select-view]"))
        if b:
            page.mouse.click(b["x"], b["y"])
            time.sleep(2)
            r = page.evaluate("""() => {
              const cells = [...document.querySelectorAll('[class*=cell],[class*=date-item],td')]
                .filter(e => e.offsetParent !== null && /^\\d{1,2}$/.test((e.innerText||'').trim()));
              const c = cells.find(e => (e.innerText||'').trim() === '15') || cells[0];
              if (!c) return null;
              const rr = c.getBoundingClientRect();
              return {x: Math.round(rr.x+rr.width/2), y: Math.round(rr.y+rr.height/2), t:(c.innerText||'').trim()};
            }""")
            if r:
                page.mouse.click(r["x"], r["y"])
                print("    日历选:", r["t"])
                time.sleep(1.5)
    # Place of issuance:自定义值输入框
    type_into(page, "Place of issuance", LIC_PLACE_ASCII, index=1)


def fill_sales(page):
    print(">>> 销售信息")
    # 零售价 / 库存 / SKU
    for label, val, idx in (("零售价", PRICE, 0), ("库存", STOCK, 0),
                            ("商家 SKU", "KOR-EYE-20G", 0)):
        try:
            type_into(page, label, val, index=idx)
        except Exception as e:
            print(f"    !! {label}: {type(e).__name__}: {str(e)[:120]}")
    # 页面里价格表头可能不带 _title_80dgt_103,退回按 placeholder 找
    if not page.evaluate("() => [...document.querySelectorAll('input')].some(i => i.value === %s)" % json.dumps(PRICE)):
        print("    零售价未写入,试 placeholder 路径")
        r = page.evaluate(r"""() => {
          const ins = [...document.querySelectorAll('input')].filter(i => i.offsetParent !== null);
          return ins.map((i, k) => ({k, ph: i.placeholder||'', v:(i.value||'').slice(0,20),
                                     cls:(i.className||'').toString().slice(0,40)})).slice(-18);
        }""")
        print("    可见 input 尾部:", json.dumps(r, ensure_ascii=False)[:900])


def fill_dims(page):
    print(">>> 包裹尺寸")
    for i, v in enumerate(DIMS):
        try:
            type_into(page, "包裹尺寸", v, index=i)
        except Exception as e:
            print(f"    !! dims[{i}]: {type(e).__name__}")
    print(">>> 包裹重量")
    type_into(page, "包裹重量", WEIGHT, index=0)


def show_errors(page, tag=""):
    errs = page.evaluate(r"""() => {
      const e = [...document.querySelectorAll('._error_[class*=_], [class*=form-error], [class*=invalid-text]')]
        .filter(x => x.offsetParent !== null)
        .map(x => (x.innerText||'').trim()).filter(t => t && t.length < 100);
      return [...new Set(e)].slice(0, 12);
    }""")
    if errs:
        print(f"    校验错误 {tag}:", json.dumps(errs, ensure_ascii=False)[:600])
    return errs


def submit_and_capture(page):
    print(">>> 提交并抓 payload")
    page.evaluate("() => localStorage.removeItem('__ttRecBuf')")
    rec = open(os.path.join(HERE, "tt_scrape.py")).read().split('RECORDER = r"""')[1].split('"""')[0]
    page.evaluate(rec)
    page.evaluate("() => window.scrollTo(0, 0)")
    time.sleep(1)
    btn = page.get_by_text("提交审核", exact=True).first
    box = btn.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    print("    已点击提交")
    time.sleep(8)
    recs = json.loads(page.evaluate("() => JSON.stringify(window.__ttRec.get())") or "[]")
    hits = [r for r in recs if any(k in (r.get("url") or "") for k in
                                   ("local/product/create", "product/msubmit", "local/draft/save",
                                    "product/local/product/edit", "precheck"))]
    print(f"    抓到 {len(recs)} 条,命中提交类 {len(hits)} 条")
    for h in hits:
        print("=" * 90)
        print(f"[{h.get('status')}] {h.get('method')} {(h.get('url') or '').split('?')[0]}")
        print("  REQ :", (h.get("reqBody") or "")[:3000])
        print("  RESP:", (h.get("respBody") or "")[:600])
    out = os.path.join(HERE, "notes", "tk178_create_payload.json")
    json.dump({"hits": hits, "all_count": len(recs)}, open(out, "w"), ensure_ascii=False, indent=2)
    print("→", out)
    # 页面上的错误
    errs = page.evaluate(r"""() => {
      const e = [...document.querySelectorAll('[class*=error],[class*=invalid],[role=alert]')]
        .filter(x => x.offsetParent !== null)
        .map(x => (x.innerText||'').trim()).filter(t => t && t.length < 120);
      return [...new Set(e)].slice(0, 20);
    }""")
    if errs:
        print("    页面错误:", json.dumps(errs, ensure_ascii=False)[:800])
    return hits



def fill_all_remaining(page):
    """把剩余字段一次填完。选择器都来自实测。"""
    print(">>> 重新上传主图(页面重载会丢)")
    try:
        import base64, os as _os
        img = _os.path.join(HERE, "notes", "product_img", "eye_cream_main.jpg")
        b64 = base64.b64encode(open(img, "rb").read()).decode()
        page.evaluate("""(b64) => {
          const bin = atob(b64); const arr = new Uint8Array(bin.length);
          for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
          const dt = new DataTransfer();
          dt.items.add(new File([arr], 'eye_cream_main.jpg', {type: 'image/jpeg'}));
          const inp = document.querySelector('input[type=file][accept*=".jpg"]');
          if (inp) { inp.files = dt.files;
                     inp.dispatchEvent(new Event('change', {bubbles: true})); }
        }""", b64)
        print("    已注入图片并触发 change")
        time.sleep(8)
    except Exception as e:
        print("    图片注入失败:", type(e).__name__, str(e)[:100])

    def fill_ph(ph, val):
        r = page.evaluate("""(a) => {
          const i = [...document.querySelectorAll('input')].find(x =>
              x.offsetParent !== null && (x.placeholder||'').includes(a.ph) && !x.value);
          const el = i || [...document.querySelectorAll('input')].find(x =>
              x.offsetParent !== null && (x.placeholder||'').includes(a.ph));
          if (!el) return null;
          el.scrollIntoView({block: 'center'});
          const b = el.getBoundingClientRect();
          return {x: Math.round(b.x + Math.min(b.width/2, 150)), y: Math.round(b.y + b.height/2)};
        }""", {"ph": ph})
        if not r:
            print(f"    !! 找不到 {ph}"); return False
        page.mouse.click(r["x"], r["y"]); time.sleep(0.3)
        page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
        page.keyboard.type(val, delay=25); time.sleep(0.6)
        got = page.evaluate("""(a) => { const i = [...document.querySelectorAll('input')]
            .find(x => (x.placeholder||'').includes(a.ph)); return i ? i.value : null; }""", {"ph": ph})
        print(f"    {ph} = {got}")
        return bool(got)

    print(">>> 价格 / 库存 / SKU")
    fill_ph("零售价", PRICE)
    fill_ph("数量", STOCK)
    fill_ph("商家 SKU", "KOR-EYE-20G")

    print(">>> 包裹尺寸 / 重量")
    for i, v in enumerate(DIMS):
        try:
            type_into(page, "包裹尺寸", v, index=i)
        except Exception as e:
            print(f"    !! dims[{i}]: {type(e).__name__}")
    type_into(page, "包裹重量", WEIGHT, index=0)

    print(">>> License 三件套")
    for lbl, val, idx in (("License number", LIC_NO, None),
                          ("Date of issuance", LIC_DATE, None),
                          ("Place of issuance", LIC_PLACE_ASCII, None)):
        try:
            js = _inputs_js(lbl)
            n = page.evaluate("(j) => { const a = eval(j); return a ? a.length : -1; }", js)
            # 取最后一个可见 input(第一个常是搜索框)
            type_into(page, lbl, val, index=max(0, (n or 1) - 1))
        except Exception as e:
            print(f"    !! {lbl}: {type(e).__name__}: {str(e)[:100]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    if not (a.fill or a.submit):
        ap.error("需要 --fill 或 --submit")

    with sync_playwright() as pw:
        page = get_page(pw)
        page.keyboard.press("Escape")
        time.sleep(0.6)
        fill_all_remaining(page)
        path = os.path.join(HERE, "notes", "tk178_filled.png")
        page.screenshot(path=path, full_page=True)
        print("截图:", path)
        if a.submit:
            submit_and_capture(page)
            page.screenshot(path=os.path.join(HERE, "notes", "tk178_submitted.png"), full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
