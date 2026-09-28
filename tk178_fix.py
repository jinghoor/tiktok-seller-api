#!/usr/bin/env python3
"""TK178 —— 精确校正那几个没填成功的字段。

问题都是「选项不在当前列表里」：品牌列表没加载全、原产国默认只有 7 项、版本/原料偏好被 blur 清空。
统一用「在下拉里搜 → 精确匹配 → 点击 → 真实键盘校验」这条链。

    python3 tk178_fix.py --check          # 只读当前状态 + 错误控件
    python3 tk178_fix.py --field 品牌      # 修单个
    python3 tk178_fix.py --all            # 全修
"""
from __future__ import annotations

import argparse
import json
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly")
from tk178_fill2 import get_page  # noqa: E402

LABELS = ["品牌", "原产国/原产地", "版本", "原料偏好", "包裹重量",
          "License type", "License number", "Date of issuance", "Place of issuance",
          "制造商/贸易商名称", "制造商/经销商地址", "物流方式"]

CHECK_JS = r"""
() => {
  const info = {};
  for (const l of __LABELS__) {
    const lb = [...document.querySelectorAll('span._title_80dgt_103')]
        .find(e => (e.textContent||'').trim() === l);
    if (!lb) { info[l] = {exists:false}; continue; }
    let n = lb;
    for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement;
      if (n.querySelector('input,.core-select')) break; }
    const sel = n.querySelector('.core-select,[role=combobox]');
    const vs = n.querySelector('.core-select-view-value');
    const inputs = [...n.querySelectorAll('input')].filter(i=>i.offsetParent!==null)
        .map(i => ({ph: i.placeholder||'', v: (i.value||'').slice(0,30)}));
    const tags = [...n.querySelectorAll('[class*=tag-content],[class*=tag-ng-content]')]
        .map(e=>(e.innerText||'').trim()).filter(Boolean);
    info[l] = {
      exists: true,
      err: sel ? /error/i.test((sel.className||'').toString()) : false,
      selTxt: sel ? (sel.innerText||'').trim().slice(0,40) : '',
      valSpan: vs ? (vs.innerText||'').trim().slice(0,40) : '',
      inputs, tags,
      ph: inputs.length ? inputs[0].ph : '',
    };
  }
  return info;
}
"""


def check(page):
    js = CHECK_JS.replace("__LABELS__", json.dumps(LABELS, ensure_ascii=False))
    info = page.evaluate(js)
    print(f"{'field':<22} {'err':<4} {'值':<34} 备注")
    bad = []
    for l in LABELS:
        d = info.get(l, {})
        if not d.get("exists"):
            print(f"{l:<22} {'-':<4} (无字段)")
            continue
        v = d.get("valSpan") or (d["inputs"][0]["v"] if d["inputs"] else "") or \
            ("|".join(d.get("tags") or [])) or ""
        note = ""
        if d.get("tags"):
            note = f"tags={len(d['tags'])}"
        print(f"{l:<22} {'ERR' if d['err'] else '   ':<4} {str(v)[:34]:<34} {note}")
        if d["err"] or not v:
            bad.append(l)
    print(f"\n需要修: {bad}")
    return info, bad


def open_dd(page, label):
    r = page.evaluate("""(l) => {
      const lb = [...document.querySelectorAll('span._title_80dgt_103')]
          .find(e => (e.textContent||'').trim() === l);
      if (!lb) return null;
      let n = lb;
      for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement;
        if (n.querySelector('input,.core-select')) break; }
      const sel = n.querySelector('.core-select,[role=combobox]') || n.querySelector('input');
      if (!sel) return null;
      sel.scrollIntoView({block:'center'});
      const b = sel.getBoundingClientRect();
      return {x: Math.round(b.x + Math.min(b.width/2, 250)), y: Math.round(b.y + b.height/2)};
    }""", label)
    if not r:
        return False
    page.mouse.click(r["x"], r["y"])
    time.sleep(2.0)
    return bool(page.evaluate("""() => [...document.querySelectorAll('.core-select-popup')]
        .some(e => e.offsetParent !== null)"""))


def popup_opts(page):
    return page.evaluate("""() => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      if (!pop) return [];
      return [...pop.querySelectorAll('*')]
        .filter(e => e.children.length === 0 && e.offsetParent !== null)
        .map(e => (e.innerText||'').trim()).filter(Boolean);
    }""")


def search(page, text):
    """点下拉里的搜索框并真实打字。"""
    r = page.evaluate("""() => {
      const lb = window.__curLabel;
      const label = [...document.querySelectorAll('span._title_80dgt_103')]
          .find(e => (e.textContent||'').trim() === label0());
      return null;
    }""") if False else None
    box = page.evaluate("""() => {
      // 可搜索 Select 的输入框就在 combobox 内
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      const scope = pop ? pop.parentElement : document;
      const cands = [...document.querySelectorAll('.core-select-view-input')]
          .filter(i => i.offsetParent !== null && !/hidden/.test(i.className));
      const e = cands[cands.length-1];
      if (!e) return null;
      e.scrollIntoView({block:'center'});
      const b = e.getBoundingClientRect();
      return {x: Math.round(b.x + Math.min(b.width/2, 120)), y: Math.round(b.y + b.height/2)};
    }""")
    if not box:
        return False
    page.mouse.click(box["x"], box["y"])
    time.sleep(0.5)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(text, delay=70)
    time.sleep(2.2)
    return True


def click_opt(page, want):
    r = page.evaluate("""(w) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      if (!pop) return 'no-popup';
      const hit = [...pop.querySelectorAll('*')]
          .find(e => e.children.length === 0 && (e.innerText||'').trim() === w);
      if (!hit) return 'not-found';
      hit.scrollIntoView({block:'center'});
      const b = hit.getBoundingClientRect();
      return {x: Math.round(b.x + Math.min(b.width/2, 250)), y: Math.round(b.y + b.height/2)};
    }""", want)
    if isinstance(r, dict):
        page.mouse.click(r["x"], r["y"])
        return "picked"
    return r


def add_opt(page, value):
    """在下拉里用「输入自定义值 + 添加」新增选项。"""
    typed = page.evaluate("""(v) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      if (!pop) return 'no-popup';
      const inp = pop.querySelector("input[data-tid='m4b_input']")
                  || [...pop.querySelectorAll('input')].find(i => (i.placeholder||'').includes('自定义'));
      if (!inp) return 'no-input';
      const b = inp.getBoundingClientRect();
      window.__addBox = {x: Math.round(b.x + Math.min(b.width/2, 80)), y: Math.round(b.y + b.height/2)};
      return 'ok';
    }""", value)
    if typed != "ok":
        return typed
    box = page.evaluate("() => window.__addBox")
    page.mouse.click(box["x"], box["y"])
    time.sleep(0.4)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(value, delay=35)
    time.sleep(0.8)
    clicked = page.evaluate("""() => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      if (!pop) return 'no-popup';
      const btn = pop.querySelector("button[data-tid='m4b_button']")
                  || [...pop.querySelectorAll('button')].find(b => (b.innerText||'').trim()==='添加');
      if (!btn) return 'no-button';
      btn.click();
      return 'clicked';
    }""")
    if clicked != "clicked":
        return clicked
    time.sleep(2.5)
    return "added"


def blur(page):
    page.mouse.click(300, 150)
    time.sleep(1.2)


def do_field(page, label, value, *, mode="search", log=print):
    """修一个字段。mode: search(搜索后选) / add(新增选项后选)。"""
    log(f"── {label} ← {value!r} [{mode}]")
    if not open_dd(page, label):
        log("   !! 弹层未打开")
        return False
    opts = popup_opts(page)
    log(f"   选项({len(opts)}): {opts[:8]}")
    if mode == "add" or (value not in opts and "添加" in opts):
        if value not in opts:
            r = add_opt(page, value)
            log(f"   添加: {r}")
    if value not in popup_opts(page):
        search(page, value)
        opts2 = popup_opts(page)
        log(f"   搜索后选项: {opts2[:8]}")
    r = click_opt(page, value)
    log(f"   选中: {r}")
    if r == "picked":
        blur(page)
    return r == "picked"


FIELDS = {
    "品牌": ("无品牌", "search"),
    "原产国/原产地": ("China", "add"),
    "版本": ("标准版", "search"),
    "原料偏好": ("维他命C", "search"),
    "包裹重量": ("克 (g)", "search"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--field", default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    with sync_playwright() as pw:
        page = get_page(pw)
        page.keyboard.press("Escape")
        time.sleep(1)
        check(page)
        if a.field:
            v, m = FIELDS.get(a.field, (None, "search"))
            if not v:
                print(f"未知字段 {a.field}")
                return 2
            do_field(page, a.field, v, mode=m)
            time.sleep(1)
            check(page)
        if a.all:
            for l, (v, m) in FIELDS.items():
                do_field(page, l, v, mode=m)
                time.sleep(0.8)
            print()
            check(page)
            page.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/tk178_fixed.png",
                            full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
