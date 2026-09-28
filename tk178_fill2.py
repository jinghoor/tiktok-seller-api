#!/usr/bin/env python3
"""TK178 商品上架 —— 表单填充器（第二轮，通用策略）。

关键坑（都是实测踩出来的）：
  1. 商品名称控件无 placeholder，只能用 `#preview-product-title input`
  2. 类目是多列 cascader（`.core-cascader-list-column`），要逐列点
  3. Arco Select 的 input 被 `span.core-select-view-selector` 盖住，不能直接 click input，
     要点外层容器
  4. 页面有吸顶导航 `#navbar`，会拦截 click；必须先把视口调高 + 用滚轮把元素滚到视口中上部
  5. 描述是 ProseMirror，用 execCommand('insertText') 最稳

用法：
    python3 tk178_fill2.py --step probe
    python3 tk178_fill2.py --step brand
    python3 tk178_fill2.py --step all
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
SHOT = os.path.join(HERE, "notes")

NAME = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g - "
        "Giảm Thâm Quầng, Sáng Da, Chống Lão Hóa Vùng Mắt")

DESC = """Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g

Công thức làm sáng chuyên biệt giúp lấy lại làn da mịn màng, rạng rỡ cho vùng da quanh mắt.

THÀNH PHẦN CHÍNH:
- AXIT ASCORBIC: Giảm sạm màu, bề mặt và vết thâm.
- AXIT CITRIC: Làm sáng hiệp đồng ở lớp trung bình, thúc đẩy tái tạo da, tăng độ rạng rỡ và giảm xỉn màu.
- NIACINAMIDE: Ức chế melanin ở lớp sâu, giúp da đều màu và sáng mịn.

CÔNG DỤNG:
- Giảm thâm quầng và bọng mắt
- Dưỡng sáng vùng da quanh mắt
- Hỗ trợ làm mờ nếp nhăn nhỏ
- Cấp ẩm, giữ vùng mắt mềm mại

CÁCH DÙNG:
Lấy một lượng nhỏ kem, chấm nhẹ quanh vùng mắt rồi vỗ nhẹ cho thấm. Dùng 2 lần mỗi ngày, sáng và tối.

THÔNG TIN SẢN PHẨM:
- Dung tích: 20g (0.71oz)
- Hạn sử dụng: 3 năm kể từ ngày sản xuất
- Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp
"""

# 具体取值:测试商品,填真实可核验的中性信息
ORIGIN = "中国"                  # 原产国/原产地
MAKER = "Guangzhou Kormesic Cosmetics Co., Ltd."
MAKER_ADDR = "No. 88 Baiyun Avenue, Baiyun District, Guangzhou, Guangdong, China"
LICENSE_TYPE = "国产普通化妆品备案"   # License type
LICENSE_NO = "粤G妆网备字NUMBER_REDACTED"
ISSUE_DATE = "2024-01-15"
ISSUE_PLACE = "广东省药品监督管理局"
WEIGHT_G = "80"
LENGTH_CM, WIDTH_CM, HEIGHT_CM = "12", "4", "3"


# ---------------------------------------------------------------- 基础设施

def get_page(pw, *, resize=True):
    b = pw.chromium.connect_over_cdp(CDP)
    pages = [p for p in b.contexts[0].pages if "seller-vn" in p.url]
    if not pages:
        raise RuntimeError("没找到 seller-vn 页面")
    page = pages[0]
    if resize:
        try:
            page.set_viewport_size({"width": 1680, "height": 2400})
        except Exception:
            pass
    return page


def js_center(page, js_find: str):
    """拿到元素在视口中的中心坐标。

    js_find 支持两种写法:
      1. `(function(){...})()` 形式的 IIFE —— 直接调用
      2. 普通表达式(如 `document.querySelector('.x')`)—— 求值取结果
    两种都走同一条求值路径:表达式求值即可,不必区分。
    """
    return page.evaluate(
        "(src) => { let e = null;"
        " try { e = eval(src); } catch (err) { return null; }"
        " if (e && typeof e === 'function') e = e();"
        " if (!e) return null;"
        " const r = e.getBoundingClientRect();"
        " return {x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2),"
        "         w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.y)}; }",
        js_find)


def scroll_element_to(page, js_find: str, target_y: int = 300, tries: int = 8):
    """用滚轮把目标元素滚到视口的 target_y 处 —— 纯 JS scrollIntoView 会被吸顶导航挡。"""
    for _ in range(tries):
        box = js_center(page, js_find)
        if not box:
            return None
        if abs(box["top"] - target_y) <= 40:
            return box
        delta = box["top"] - target_y
        page.mouse.wheel(0, max(-800, min(800, delta)))
        time.sleep(0.45)
    return js_center(page, js_find)


def click_at(page, box, label=""):
    if not box:
        raise RuntimeError(f"定位失败: {label}")
    page.mouse.click(box["x"], box["y"])
    return box


def _climb_js(label: str) -> str:
    """定位含该 label 的表单项容器。

    坑:label 的 `closest('div').parentElement.parentElement` 只到 label 组(第 3 层),
    真正的控件在第 5 层。必须一直往上爬到「容器里出现表单控件」为止。
    """
    return ("(function(){"
            f" const LBL = {json.dumps(label, ensure_ascii=False)};"
            " const lb = [...document.querySelectorAll('span._title_80dgt_103')]"
            "   .find(e => (e.textContent||'').trim() === LBL);"
            " if (!lb) return null;"
            " let node = lb;"
            " for (let i = 0; i < 9 && node.parentElement; i++) {"
            "   node = node.parentElement;"
            "   if (node.querySelector('input,textarea,[contenteditable=true],[class*=select-view]')) break;"
            " }"
            " return node; }})")


def wrap_wrap(label: str) -> str:
    """表单项容器本身。"""
    return _climb_js(label)


def wrap_label(label: str, selector: str) -> str:
    """表单项容器内的某个控件。"""
    return ("(function(){"
            f" const LBL = {json.dumps(label, ensure_ascii=False)};"
            " const lb = [...document.querySelectorAll('span._title_80dgt_103')]"
            "   .find(e => (e.textContent||'').trim() === LBL);"
            " if (!lb) return null;"
            " let node = lb;"
            " for (let i = 0; i < 9 && node.parentElement; i++) {"
            "   node = node.parentElement;"
            "   if (node.querySelector('input,textarea,[contenteditable=true],[class*=select-view]')) break;"
            " }"
            f" return node.querySelector({json.dumps(selector)}); }})")


# ---------------------------------------------------------------- 各字段操作

def op_name(page):
    sel = "#preview-product-title input"
    box = scroll_element_to(page, f"document.querySelector({json.dumps(sel)})")
    click_at(page, box, "商品名称")
    time.sleep(0.3)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(NAME, delay=8)
    time.sleep(1.2)
    v = page.evaluate(f"() => (document.querySelector({json.dumps(sel)})||{{}}).value || ''")
    print(f"    商品名 {len(v)} 字符: {v[:70]}")
    return len(v) >= 25


def op_category(page):
    path = ["美妆个护", "护肤品", "眼部护理"]
    cur = page.evaluate("() => (document.querySelector('[class*=cascader-select-view]')||{}).innerText || ''")
    if all(p in cur for p in path):
        print("    类目已是:", cur.strip().replace("\n", " "))
        return True
    box = scroll_element_to(page,
                            "(function(){ return document.querySelector('.p-cascader-select-view, [class*=cascader-select-view]'); })")
    click_at(page, box, "类目")
    time.sleep(2.5)
    for i, want in enumerate(path):
        r = page.evaluate(r"""(want) => {
          const cols = [...document.querySelectorAll('.core-cascader-list-column')];
          for (let ci = cols.length - 1; ci >= 0; ci--) {
            const it = [...cols[ci].querySelectorAll('.core-cascader-list-item')]
                .find(e => (e.innerText||'').trim() === want);
            if (it) {
              it.scrollIntoView({block: 'center'});
              const b = it.getBoundingClientRect();
              return {x: Math.round(b.x + b.width / 2), y: Math.round(b.y + b.height / 2), col: ci};
            }
          }
          return null;
        }""", want)
        if not r:
            print(f"    !! 第{i+1}级找不到 {want}")
            return False
        page.mouse.click(r["x"], r["y"])
        print(f"    L{i+1} {want} (列{r['col']})")
        time.sleep(2.0)
    cur = page.evaluate("() => (document.querySelector('[class*=cascader-select-view]')||{}).innerText || ''")
    print("    类目 →", cur.strip().replace("\n", " "))
    return "眼部护理" in cur


def op_brand_none(page):
    """品牌选「无品牌」。"""
    # 先看有没有直接的「无品牌」入口
    box = scroll_element_to(page, wrap_label("品牌", "[class*=select-view]"))
    if not box:
        box = scroll_element_to(page, "(function(){ return document.querySelector(\"input[placeholder*='选择品牌']\")?.closest('[class*=select]'); })")
    click_at(page, box, "品牌")
    time.sleep(2.5)
    r = page.evaluate(r"""() => {
      const opt = [...document.querySelectorAll('[class*=option],[role=option],li')]
        .filter(e => e.offsetParent !== null)
        .find(e => /无品牌|No brand|no brand/.test((e.innerText||'')));
      if (!opt) return null;
      opt.scrollIntoView({block:'center'});
      const b = opt.getBoundingClientRect();
      return {x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2), t:(opt.innerText||'').trim()};
    }""")
    if r:
        page.mouse.click(r["x"], r["y"])
        print("    品牌 →", r["t"][:30])
        time.sleep(1.5)
        return True
    # 没有无品牌选项:看是否有输入框可搜
    opts = page.evaluate("""() => [...document.querySelectorAll('[class*=option],[role=option]')]
        .filter(e=>e.offsetParent!==null).map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,20)""")
    print("    品牌下拉选项:", json.dumps(opts, ensure_ascii=False)[:400])
    page.keyboard.press("Escape")
    return False


def op_select_by_label(page, label, prefer=(), contains=()):
    """通用:点开某个 Select，在弹层里挑一个选项。"""
    box = scroll_element_to(page, wrap_label(label, "[class*=select-view]"))
    if not box:
        box = scroll_element_to(page, wrap_label(label, ".core-input, input.core-select-view-input:not(.core-select-hidden)"))
    if not box:
        print(f"    !! {label} 找不到控件")
        return False
    click_at(page, box, label)
    time.sleep(2.0)
    pat = list(prefer) + list(contains)
    r = page.evaluate(r"""(pats) => {
      const opts = [...document.querySelectorAll('[class*=option],[role=option],li')]
        .filter(e => e.offsetParent !== null);
      for (const p of pats) {
        const hit = opts.find(e => (e.innerText||'').includes(p));
        if (hit) { hit.scrollIntoView({block:'center'});
          const b = hit.getBoundingClientRect();
          return {x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2), t:(hit.innerText||'').trim()}; }
      }
      // 退而取第一个非空选项
      const first = opts.find(e => (e.innerText||'').trim());
      if (first) { const b = first.getBoundingClientRect();
        return {x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2), t:(first.innerText||'').trim(), fallback:true}; }
      return null;
    }""", pat)
    if not r:
        print(f"    !! {label} 下拉无选项")
        page.keyboard.press("Escape")
        return False
    page.mouse.click(r["x"], r["y"])
    print(f"    {label} → {r['t'][:40]}{'  (兜底首项)' if r.get('fallback') else ''}")
    time.sleep(1.5)
    return True


def op_text_by_label(page, label, text):
    """通用:往某 label 下的 input 输入文本。"""
    box = scroll_element_to(page, wrap_label(label, ".core-input, input.core-select-view-input:not(.core-select-hidden)"))
    if not box:
        print(f"    !! {label} 找不到 input")
        return False
    click_at(page, box, label)
    time.sleep(0.3)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(text, delay=8)
    time.sleep(0.8)
    v = page.evaluate(
        "(args) => { const lb = [...document.querySelectorAll('span._title_80dgt_103')]"
        ".find(e => (e.textContent||'').trim() === args.l);"
        " if (!lb) return null;"
        " const w = lb.closest('div')?.parentElement?.parentElement;"
        " const i = w ? w.querySelector('.core-input, input.core-select-view-input:not(.core-select-hidden)') : null; return i ? i.value : null; }",
        {"l": label})
    print(f"    {label} → {str(v)[:60]}")
    return bool(v)


def op_desc(page):
    box = scroll_element_to(page, "document.querySelector('.ProseMirror')")
    click_at(page, box, "描述")
    time.sleep(0.5)
    r = page.evaluate(r"""(text) => {
      const pm = document.querySelector('.ProseMirror');
      if (!pm) return 'no pm';
      pm.focus();
      const sel = window.getSelection(); sel.removeAllRanges();
      const rng = document.createRange(); rng.selectNodeContents(pm); sel.addRange(rng);
      document.execCommand('delete', false, null);
      text.split('\n').forEach((ln, i) => {
        if (i > 0) document.execCommand('insertLineBreak', false, null);
        if (ln) document.execCommand('insertText', false, ln);
      });
      return (pm.innerText || '').length;
    }""", DESC)
    time.sleep(1.2)
    ln = page.evaluate("() => ((document.querySelector('.ProseMirror')||{}).innerText||'').length")
    print(f"    描述 DOM 长度 {ln} (返回 {r})")
    return ln > 200


def op_weight(page):
    return op_text_by_label(page, "包裹重量", WEIGHT_G)


def op_dimensions(page):
    """包裹尺寸:长宽高三个 input。"""
    box = scroll_element_to(page, wrap_label("包裹尺寸", ".core-input, input.core-select-view-input:not(.core-select-hidden)"))
    if not box:
        print("    !! 包裹尺寸找不到")
        return False
    click_at(page, box, "包裹尺寸")
    time.sleep(0.3)
    vals = [LENGTH_CM, WIDTH_CM, HEIGHT_CM]
    ok = page.evaluate(r"""(vals) => {
      const lb = [...document.querySelectorAll('span._title_80dgt_103')]
        .find(e => (e.textContent||'').trim() === '包裹尺寸');
      const w = lb.closest('div')?.parentElement?.parentElement;
      const ins = [...w.querySelectorAll('input:not(.core-select-hidden)')].filter(i => i.offsetParent !== null);
      ins.forEach((i, k) => {
        if (vals[k]) {
          const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
          setter.call(i, vals[k]);
          i.dispatchEvent(new Event('input', {bubbles:true}));
          i.dispatchEvent(new Event('change', {bubbles:true}));
        }
      });
      return ins.map(i => i.value);
    }""", vals)
    print("    包裹尺寸 →", ok)
    return True


def op_pick_search(page, label, query, exact=None, allow_fallback=False):
    """点开一个带搜索的 Select,输入 query,挑精确匹配项。"""
    box = scroll_element_to(page, wrap_label(label, "[class*=select-view]"))
    if not box:
        print(f"    !! {label} 找不到控件")
        return False
    click_at(page, box, label)
    time.sleep(1.2)
    if query:
        # Arco Select 的可搜索 input 就是可见的那个
        try:
            si = page.locator("input.core-select-view-input:not(.core-select-hidden)").first
            si.click(timeout=5000)
        except Exception:
            pass
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(query, delay=90)
        time.sleep(2.0)
    want = exact or query
    r = page.evaluate(r"""(args) => {
      const opts = [...document.querySelectorAll('[class*=option],[role=option],li')]
        .filter(e => e.offsetParent !== null)
        .filter(e => (e.innerText || '').trim());
      let hit = opts.find(e => (e.innerText || '').trim() === args.want);
      let fb = false;
      if (!hit && args.allow) { hit = opts[0]; fb = true; }
      if (!hit && args.q) hit = opts.find(e => (e.innerText || '').includes(args.q));
      if (!hit) return null;
      hit.scrollIntoView({block: 'center'});
      const b = hit.getBoundingClientRect();
      return {x: Math.round(b.x + b.width / 2), y: Math.round(b.y + b.height / 2),
              t: (hit.innerText || '').trim(), fallback: fb};
    }""", {"want": want, "q": query, "allow": allow_fallback})
    if not r:
        opts = page.evaluate("""() => [...document.querySelectorAll('[class*=option],[role=option]')]
            .filter(e=>e.offsetParent!==null).map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,15)""")
        print(f"    !! {label}: 搜 '{query}' 无匹配。可见选项: {opts}")
        page.keyboard.press("Escape")
        return False
    page.mouse.click(r["x"], r["y"])
    print(f"    {label} → {r['t'][:50]}{'  (兜底)' if r['fallback'] else ''}")
    time.sleep(1.2)
    return True


def op_text_direct(page, label, text):
    """往某 label 下真实 input 输入(用键盘,不用 JS 赋值)。"""
    sel_js = wrap_label(label, ".core-input, input.core-select-view-input:not(.core-select-hidden)")
    box = scroll_element_to(page, sel_js)
    if not box:
        print(f"    !! {label} 找不到 input")
        return False
    click_at(page, box, label)
    time.sleep(0.4)
    page.keyboard.press("Meta+A")
    if not text:
        page.keyboard.press("Backspace")
    else:
        page.keyboard.type(text, delay=12)
    time.sleep(0.8)
    v = page.evaluate("(js) => { const e = eval('(' + js + ')')(); return e ? e.value : null; }", sel_js)
    print(f"    {label} → {str(v)[:60]}")
    return bool(v)


def op_date_direct(page, label, value):
    """日期字段:可能是原生 input[type=date],也可能是文本。"""
    info = page.evaluate("(js) => { const e = eval('(' + js + ')')(); "
                         "return e ? {tag:e.tagName, type:e.type||'', ph:e.placeholder||''} : null; }",
                         wrap_label(label, "input"))
    print(f"    {label} 控件: {info}")
    return op_text_direct(page, label, value)


STEPS = {
    "name": op_name,
    "category": op_category,
    "brand": op_brand_none,
    "desc": op_desc,
    "weight": lambda p: op_text_direct(p, "包裹重量", WEIGHT_G),
    "dimensions": op_dimensions,
    "license_type": lambda p: op_pick_search(p, "License type", "Cosmetic", allow_fallback=True),
    "license_no": lambda p: op_text_direct(p, "License number", LICENSE_NO),
    "issue_date": lambda p: op_date_direct(p, "Date of issuance", ISSUE_DATE),
    "issue_place": lambda p: op_text_direct(p, "Place of issuance", ISSUE_PLACE),
    "origin": lambda p: op_pick_search(p, "原产国/原产地", "中国", exact=ORIGIN),
    "maker": lambda p: op_text_direct(p, "制造商/贸易商名称", MAKER),
    "maker_addr": lambda p: op_text_direct(p, "制造商/经销商地址", MAKER_ADDR),
    "shipping": lambda p: op_select_by_label(p, "物流方式"),
}


JS_READ = r"""
() => {
  const read = (l) => {
    const lb = [...document.querySelectorAll('span._title_80dgt_103')]
        .find(e => (e.textContent||'').trim() === l);
    if (!lb) return null;
    let node = lb;
    for (let i = 0; i < 9 && node.parentElement; i++) {
      node = node.parentElement;
      if (node.querySelector('input,textarea,[contenteditable=true],[class*=select-view]')) break;
    }
    // Arco Select 已选值在 .core-select-view-value,搜索 input 是空的
    const val = node.querySelector('.core-select-view-value');
    if (val && (val.innerText || '').trim()) return (val.innerText || '').trim();
    const inp = node.querySelector('.core-input, input.core-select-view-input:not(.core-select-hidden)');
    if (inp && (inp.value || '').trim()) return (inp.value || '').trim();
    const cas = node.querySelector('[class*=cascader-select-view]');
    if (cas && (cas.innerText || '').trim()) return (cas.innerText || '').trim().replace(/\s+/g, ' ');
    const any = node.querySelector('input');
    return any ? (any.value || '') : '(空)';
  };
  const q = (s) => document.querySelector(s);
  return {
    name: (q('#preview-product-title input') || {}).value || '',
    category: (q('[class*=cascader-select-view]') || {}).innerText || '',
    brand: read('品牌'),
    origin: read('原产国/原产地'),
    maker: read('制造商/贸易商名称'),
    makerAddr: read('制造商/经销商地址'),
    licenseType: read('License type'),
    licenseNo: read('License number'),
    issueDate: read('Date of issuance'),
    issuePlace: read('Place of issuance'),
    weight: read('包裹重量'),
    descLen: ((q('.ProseMirror') || {}).innerText || '').length,
    imgCount: [...document.querySelectorAll('img')].filter(e => e.src.includes('aphluv4xwc')).length,
  };
}
"""


def dump_state(page, tag=""):
    st = page.evaluate(JS_READ)
    print(f"--- 表单状态 {tag} ---")
    empty = []
    for k, v in st.items():
        sv = str(v).replace("\n", " ")[:80]
        ok = bool(v) and "0/255" not in sv and sv not in ("(空)", "None")
        if not ok:
            empty.append(k)
        print(f"  [{'✓' if ok else ' '}] {k:<12} {sv}")
    if empty:
        print(f"  待填: {', '.join(empty)}")
    return st


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True)
    ap.add_argument("--shot", default=None)
    a = ap.parse_args()

    with sync_playwright() as pw:
        page = get_page(pw)
        if a.step == "probe":
            dump_state(page, "probe")
        elif a.step == "all":
            dump_state(page, "before")
            for nm, fn in STEPS.items():
                print(f"\n>>> {nm}")
                try:
                    print("    结果:", fn(page))
                except Exception as e:
                    print(f"    !! {nm} 异常: {type(e).__name__}: {str(e)[:160]}")
                time.sleep(0.8)
            dump_state(page, "after")
        else:
            if a.step not in STEPS:
                print(f"未知 step: {a.step}；可用: probe, all, {', '.join(STEPS)}", file=sys.stderr)
                return 2
            print(f">>> {a.step}")
            print("    结果:", STEPS[a.step](page))
            time.sleep(1)
            dump_state(page, a.step)
        path = a.shot or os.path.join(SHOT, f"tk178_{a.step}.png")
        page.screenshot(path=path, full_page=True)
        print("截图:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
