#!/usr/bin/env python3
"""TK178 商品上架 —— 表单填充驱动。

用真实 CDP 连无头实例,Playwright 走真实鼠标键盘(自定义 React 组件忽略 JS .click())。

    python3 tk178_fill.py --step probe      # 看表单当前状态
    python3 tk178_fill.py --step name       # 填商品名
    python3 tk178_fill.py --step category   # 选类目(美妆个护>护肤品>眼部护理)
    python3 tk178_fill.py --step desc       # 填描述
    python3 tk178_fill.py --step all        # 一路做到底
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
IMG = os.path.join(HERE, "notes", "product_img", "eye_cream_main.jpg")
SHOT = os.path.join(HERE, "notes")

# 卖家中心商品描述里对 HTML 标签有白名单;纯文本 + 换行最稳
DESC = """Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g

Công thức làm sáng chuyên biệt giúp lấy lại làn da mịn màng, rạng rỡ cho vùng da quanh mắt.

THÀNH PHẦN CHÍNH:
- AXIT ASCORBIC: Giảm sạm màu, bề mặt và vết thâm.
- AXIT CITRIC: Làm sáng hiệp đồng ở lớp trung bình, thúc đẩy tái tạo da, tăng độ rạng rỡ và giảm xỉn màu.
- NIACINAMIDE: Nguyên liệu "anh quốc", ức chế melanin ở lớp sâu.

CÔNG DỤNG:
- Giảm thâm quầng và bọng mắt
- Dưỡng sáng vùng da quanh mắt
- Hỗ trợ làm mờ nếp nhăn nhỏ
- Cấp ẩm, giữ vùng mắt mềm mại

CÁCH DÙNG:
Lấy một lượng nhỏ kem, chấm nhẹ quanh vùng mắt rồi vỗ nhẹ cho thấm. Dùng 2 lần/ngày, sáng và tối.

THÔNG TIN SẢN PHẨM:
- Dung tích: 20g (0.71oz)
- Hạn sử dụng: 3 năm kể từ ngày sản xuất
- Xuất xứ: Nội địa Trung Quốc
- Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp
"""

NAME = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g - "
        "Giảm Thâm Quầng, Sáng Da, Chống Lão Hóa Vùng Mắt")


def get_page(pw):
    b = pw.chromium.connect_over_cdp(CDP)
    pages = [p for p in b.contexts[0].pages if "seller-vn" in p.url]
    if not pages:
        raise RuntimeError("没找到 seller-vn 页面")
    return pages[0]


def dump_state(page, tag=""):
    st = page.evaluate(r"""() => {
      const inputs = [...document.querySelectorAll('input')].filter(i => i.type !== 'file');
      const ce = [...document.querySelectorAll('[contenteditable=true]')];
      const imgs = [...document.querySelectorAll('img')].filter(e => e.src.includes('aphluv4xwc'));
      const btns = [...document.querySelectorAll('button,[class*=btn]')]
          .map(e => (e.innerText || '').trim()).filter(t => t && t.length < 20);
      return {
        inputs: inputs.map(i => ({ v: (i.value || '').slice(0, 60), ph: i.placeholder || '',
                                   aria: i.getAttribute('aria-label') || '' })),
        contentEditables: ce.map(e => (e.innerText || '').trim().slice(0, 60)),
        imgCount: imgs.length,
        cascader: (document.querySelector('[class*=cascader-select-view]') || {}).innerText || '',
        buttons: [...new Set(btns)].slice(0, 20),
        title: (document.querySelector('input[placeholder*="名称"]') || {}).value || '',
      };
    }""")
    print(f"--- 状态 {tag} ---")
    print(json.dumps(st, ensure_ascii=False, indent=2)[:2200])
    return st


NAME_SEL = "#preview-product-title input.core-input, #preview-product-title input"


def do_name(page):
    """商品名称。实测控件是 #preview-product-title 下的 core-input(无 placeholder)。"""
    loc = page.locator(NAME_SEL).first
    loc.wait_for(state="visible", timeout=10000)
    loc.click(timeout=8000)
    time.sleep(0.4)
    page.keyboard.press("Control+A")
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(NAME, delay=10)
    time.sleep(1.5)
    v = page.evaluate("(sel) => { const i = document.querySelector(sel);"
                      " return i ? i.value : null; }", NAME_SEL)
    print(f"  写入 {len(NAME)} 字符 → DOM {len(v or '')} 字符")
    print("  内容:", (v or '')[:110])
    return bool(v and len(v) >= 25)


def do_category(page):
    """类目:美妆个护 > 护肤品 > 眼部护理(601646)。优先用下拉里的搜索框。"""
    page.locator(".p-cascader-select-view, [class*=cascader-select-view]").first.click(timeout=10000)
    time.sleep(2.5)
    # 尝试搜索框
    got = page.evaluate("""() => {
        const inp = [...document.querySelectorAll('input')]
            .filter(i => i.offsetParent !== null)
            .map(i => ({ph: i.placeholder || '', aria: i.getAttribute('aria-label') || '',
                        cls: (i.className||'').toString().slice(0,50)}));
        return inp;
    }""")
    print("  可见输入框:", json.dumps(got, ensure_ascii=False)[:400])
    s = None
    for ph in ("搜索", "Search", "请输入"):
        try:
            s = page.locator(f"input[placeholder*='{ph}']").first
            if s.count() and s.is_visible():
                s.click(timeout=5000)
                break
        except Exception:
            s = None
    if s is not None:
        page.keyboard.type("眼部护理", delay=60)
        time.sleep(3)
    # 点叶子节点
    clicked = False
    for label in ("眼部护理",):
        try:
            page.get_by_text(label, exact=True).last.click(timeout=8000)
            clicked = True
            break
        except Exception as e:
            print(f"  点 {label} 失败: {type(e).__name__}")
    time.sleep(2.5)
    cur = page.evaluate("""() => {
        const e = document.querySelector('[class*=cascader-select-view]');
        return e ? (e.innerText||'').trim().replace(/\\s+/g,' ') : '';
    }""")
    print("  类目当前值:", cur[:120])
    return clicked and ("眼部" in cur or "护肤" in cur)


def do_desc(page):
    """描述:ProseMirror contenteditable。用 execCommand 插纯文本比逐字输入稳。"""
    pm = page.locator(".ProseMirror").first
    pm.click(timeout=10000)
    time.sleep(0.8)
    ok = page.evaluate("""(text) => {
        const pm = document.querySelector('.ProseMirror');
        if (!pm) return 'no ProseMirror';
        pm.focus();
        const lines = text.split('\\n');
        lines.forEach((ln, i) => {
            if (i > 0) document.execCommand('insertLineBreak', false, null);
            if (ln) document.execCommand('insertText', false, ln);
        });
        return 'len=' + (pm.innerText || '').length;
    }""", DESC)
    time.sleep(1.5)
    ln = page.evaluate("() => (document.querySelector('.ProseMirror')||{}).innerText?.length || 0")
    print(f"  描述: {ok} → DOM 长度 {ln}")
    return ln > 200


STEPS = {"name": do_name, "category": do_category, "desc": do_desc}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=list(STEPS) + ["probe", "all"])
    ap.add_argument("--reload", action="store_true")
    ap.add_argument("--shot", default=None)
    a = ap.parse_args()

    with sync_playwright() as pw:
        page = get_page(pw)
        if a.reload:
            page.reload(wait_until="domcontentloaded")
            time.sleep(14)
        if a.step == "probe":
            dump_state(page, "probe")
        elif a.step == "all":
            dump_state(page, "before")
            for nm, fn in STEPS.items():
                print(f"\n>>> {nm}")
                try:
                    print("  结果:", fn(page))
                except Exception as e:
                    print(f"  !! {nm} 异常: {type(e).__name__}: {str(e)[:200]}")
                time.sleep(1)
            dump_state(page, "after")
        else:
            print(f">>> {a.step}")
            print("  结果:", STEPS[a.step](page))
            time.sleep(1)
            dump_state(page, a.step)
        path = a.shot or os.path.join(SHOT, f"tk178_{a.step}.png")
        page.screenshot(path=path, full_page=True)
        print("截图:", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
