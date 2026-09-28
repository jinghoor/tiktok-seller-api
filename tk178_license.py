#!/usr/bin/env python3
"""TK178 商品合规 —— 手动添加下拉选项。

流程（用户确认的正确操作顺序）：
  1. 点开下拉
  2. 在底部的「输入自定义值」输入框里填值
  3. 点输入框右侧的「添加」按钮
  4. 新选项出现在「暂无数据」的位置 → 点它选中

License type 先复位成 CPNF，License number 清掉试错留下的脏值。
"""
from __future__ import annotations

import json
import sys
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly")
from tk178_fill2 import get_page, scroll_element_to, wrap_label  # noqa: E402

CPNF = "Cosmetic product notification form (CPNF)"
DATE_VAL = "2024-01-15"
PLACE_VAL = "Guangdong"


def open_dropdown(page, label):
    b = scroll_element_to(page, wrap_label(label, "[class*=select-view]"))
    if not b:
        raise RuntimeError(f"{label}: 找不到控件")
    page.mouse.click(b["x"], b["y"])
    time.sleep(2.2)
    return b


def popup_state(page):
    return page.evaluate(r"""() => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e => e.offsetParent !== null);
      const pop = pops[pops.length - 1];
      if (!pop) return {err: 'no popup'};
      const inp = pop.querySelector('input');
      const btn = [...pop.querySelectorAll('button,[role=button]')]
        .find(e => (e.innerText||'').trim() === '添加');
      const items = [...pop.querySelectorAll('*')]
        .filter(e => e.offsetParent !== null && e.children.length === 0)
        .map(e => (e.innerText||'').trim()).filter(t => t && t !== '添加' && t !== '暂无数据');
      return {txt: (pop.innerText||'').trim().slice(0,200),
              hasInput: !!inp, inputPh: inp ? (inp.placeholder||'') : '',
              hasAdd: !!btn,
              addBox: btn ? (() => { const b = btn.getBoundingClientRect();
                  return {x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)}; })() : null,
              inputBox: inp ? (() => { const b = inp.getBoundingClientRect();
                  return {x:Math.round(b.x+Math.min(b.width/2,150)), y:Math.round(b.y+b.height/2)}; })() : null,
              items: [...new Set(items)].slice(0,10)};
    }""")


def add_option(page, label, value):
    """在一个下拉里手动添加选项并选中。"""
    print(f"  ── {label} ← {value!r}")
    open_dropdown(page, label)
    st = popup_state(page)
    print(f"     弹层: {json.dumps({k: st.get(k) for k in ('txt','hasInput','inputPh','hasAdd','items')}, ensure_ascii=False)[:260]}")
    if not st.get("hasAdd"):
        print("     !! 没有「添加」按钮")
        page.keyboard.press("Escape")
        return False
    # 2) 填自定义值
    ib = st.get("inputBox")
    if ib:
        page.mouse.click(ib["x"], ib["y"])
        time.sleep(0.4)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(value, delay=40)
        time.sleep(0.8)
        typed = page.evaluate("""() => {
          const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
          const i = pops.length ? pops[pops.length-1].querySelector('input') : null;
          return i ? i.value : null;
        }""")
        print(f"     输入框 → {typed!r}")
    # 3) 点「添加」
    ab = st["addBox"]
    page.mouse.click(ab["x"], ab["y"])
    time.sleep(2.5)
    st2 = popup_state(page)
    print(f"     点添加后: {json.dumps({k: st2.get(k) for k in ('txt','items')}, ensure_ascii=False)[:260]}")
    # 4) 选中新选项
    ok = page.evaluate("""(want) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e => e.offsetParent !== null);
      const pop = pops[pops.length - 1];
      if (!pop) return null;
      const hit = [...pop.querySelectorAll('*')]
        .find(e => e.children.length === 0 && (e.innerText||'').trim() === want);
      if (!hit) return null;
      const b = hit.getBoundingClientRect();
      return {x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)};
    }""", value)
    if ok:
        page.mouse.click(ok["x"], ok["y"])
        print("     已点选新选项")
        time.sleep(1.5)
    else:
        print("     !! 新选项未出现，尝试点第一个可用项")
        page.keyboard.press("Escape")
        time.sleep(0.5)
        return False
    got = page.evaluate("""(a) => {
      const lb = [...document.querySelectorAll('span._title_80dgt_103')]
          .find(e => (e.textContent||'').trim() === a.l);
      let n = lb;
      for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement; if(n.querySelector('input')) break; }
      return [...n.querySelectorAll('input')].map(i => i.value).filter(Boolean);
    }""", {"l": label})
    print(f"     {label} 当前值 → {got}")
    return bool(got)


def reset_license_type(page):
    """把 License type 复位成 CPNF。"""
    print(f"  ── License type 复位为 CPNF")
    open_dropdown(page, "License type")
    r = page.evaluate("""(want) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e => e.offsetParent !== null);
      const pop = pops[pops.length - 1];
      if (!pop) return null;
      const hit = [...pop.querySelectorAll('*')]
        .find(e => e.children.length === 0 && (e.innerText||'').trim() === want);
      if (!hit) return null;
      const b = hit.getBoundingClientRect();
      return {x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)};
    }""", CPNF)
    if r:
        page.mouse.click(r["x"], r["y"])
        time.sleep(1.5)
        print("     已选 CPNF")
    else:
        print("     !! CPNF 选项未找到")
        page.keyboard.press("Escape")


def clear_license_number(page):
    """清掉 License number 里试错拼进去的脏值。"""
    print("  ── License number 清脏值")
    b = scroll_element_to(page, wrap_label("License number", "input"))
    if not b:
        print("     找不到"); return
    page.mouse.click(b["x"], b["y"])
    time.sleep(0.6)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    time.sleep(1)
    got = page.evaluate("""() => {
      const lb = [...document.querySelectorAll('span._title_80dgt_103')]
          .find(e => (e.textContent||'').trim() === 'License number');
      let n = lb;
      for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement; if(n.querySelector('input')) break; }
      return [...n.querySelectorAll('input')].map(i => i.value);
    }""")
    print(f"     清后 → {got}")


def main() -> int:
    with sync_playwright() as pw:
        page = get_page(pw)
        page.keyboard.press("Escape")
        time.sleep(0.8)
        reset_license_type(page)
        clear_license_number(page)
        print("\n>>> Date of issuance")
        add_option(page, "Date of issuance", DATE_VAL)
        print("\n>>> Place of issuance")
        add_option(page, "Place of issuance", PLACE_VAL)
        page.screenshot(path="/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly/notes/tk178_license_ok.png",
                        full_page=True)
        print("\n截图: notes/tk178_license_ok.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
