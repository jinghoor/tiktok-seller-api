#!/usr/bin/env python3
"""TK178 上架 —— 从零一次建完（全部选择器均来自实测）。

执行顺序有依赖：
  商品名 → 类目(展开属性区) → 品牌 → 原产地 → 版本 → 原料偏好 →
  描述 → 价格/库存/SKU → 包裹重量/尺寸 → 物流方式 → 商品合规(License 四件套)

License/制造商这类字段是「下拉 + 底部输入自定义值 + 添加按钮」结构：
  点开下拉 → 在 popup 内的 input 里打字 → 点 popup 内的 button →
  新选项出现在列表里 → 点选它

关键坑：
  - 不能按 Escape 关多选（会清空已选）
  - 点「添加」按钮要用 popup 内的元素引用，用坐标会被吸顶导航/其它浮层拦截
  - 页面重载会丢图片，最后要重新注入

    python3 tk178_build.py --fill      # 只填
    python3 tk178_build.py --submit    # 填完提交
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from tk178_fill2 import get_page  # noqa: E402

IMG = os.path.join(HERE, "notes", "product_img", "eye_cream_main.jpg")
NAME = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g - "
        "Giảm Thâm Quầng, Sáng Da, Chống Lão Hóa Vùng Mắt")
DESC = """Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g

Công thức làm sáng chuyên biệt giúp lấy lại làn da mịn màng, rạng rỡ cho vùng da quanh mắt.

THÀNH PHẦN CHÍNH:
- AXIT ASCORBIC: Giảm sạm màu, bề mặt và vết thâm.
- AXIT CITRIC: Làm sáng hiệp đồng ở lớp trung bình, thúc đẩy tái tạo da.
- NIACINAMIDE: Ức chế melanin ở lớp sâu, giúp da đều màu và sáng mịn.

CÔNG DỤNG:
- Giảm thâm quầng và bọng mắt
- Dưỡng sáng vùng da quanh mắt
- Hỗ trợ làm mờ nếp nhăn nhỏ
- Cấp ẩm, giữ vùng mắt mềm mại

CÁCH DÙNG: Lấy một lượng nhỏ kem, chấm nhẹ quanh vùng mắt rồi vỗ nhẹ cho thấm. Dùng 2 lần mỗi ngày.

THÔNG TIN SẢN PHẨM:
- Dung tích: 20g (0.71oz)
- Hạn sử dụng: 3 năm kể từ ngày sản xuất"""
MAKER = "Kormesic Cosmetics Co Ltd"
ADDR = "Baiyun District Guangzhou"
LIC_NO = "GNUMBER_REDACTED"
LIC_DATE = "2024-01-15"
LIC_PLACE = "Guangdong"
PRICE, STOCK, SKU = "200000", "100", "KOR-EYE-20G"
WEIGHT, DIMS = "80", ("12", "4", "3")


def log(msg):
    print(f"    {msg}")


# ---------------------------------------------------------------- 基础操作

def find_select_js(label):
    return ("(function(){ const lb=[...document.querySelectorAll('span._title_80dgt_103')]"
            f".find(e=>(e.textContent||'').trim()==={json.dumps(label, ensure_ascii=False)});"
            " if(!lb) return null; let n=lb;"
            " for(let i=0;i<9&&n.parentElement;i++){n=n.parentElement;"
            "   if(n.querySelector('input,[role=combobox],.core-select')) break;}"
            " return n.querySelector('.core-select,[role=combobox]') || n.querySelector('input'); })()")


def center(page, js):
    return page.evaluate(
        "(src) => { let e=null; try { e = eval(src); } catch (e2) { return null; }"
        " if (e && typeof e === 'function') e = e(); if (!e) return null;"
        " e.scrollIntoView({block:'center'});"
        " const r = e.getBoundingClientRect();"
        " return {x: Math.round(r.x + Math.min(r.width/2, 300)),"
        "         y: Math.round(r.y + r.height/2)}; }", js)


def open_popup(page, label):
    """点开下拉,返回 popup 是否出现。"""
    c = center(page, find_select_js(label))
    if not c:
        log(f"!! {label}: 找不到控件")
        return False
    page.mouse.click(c["x"], c["y"])
    time.sleep(2.2)
    has = page.evaluate("""() => [...document.querySelectorAll('.core-select-popup')]
        .some(e => e.offsetParent !== null)""")
    return bool(has)


def add_and_pick(page, label, value):
    """下拉 → 在「输入自定义值」里填 → 点「添加」→ 选中新选项。

    注意:新增后选项不一定渲染在 .core-select-popup 内,所以选中时要在全页找。
    """
    if not open_popup(page, label):
        log(f"!! {label}: 弹层未出现")
        return False
    # 关键:选项是异步加载的。先等弹层稳定(有输入框 + 按钮),再操作,
    # 否则会在「暂无数据」状态下点「添加」，产生 refetch_data 抖动。
    for _ in range(30):
        ready = page.evaluate("""() => {
          const pops = [...document.querySelectorAll('.core-select-popup')]
            .filter(e => e.offsetParent !== null && (e.innerText||'').trim());
          const pop = pops[pops.length-1];
          if (!pop) return false;
          const inp = pop.querySelector("input[data-tid='m4b_input']");
          const btn = pop.querySelector("button[data-tid='m4b_button']");
          return !!(inp && btn);
        }""")
        if ready:
            break
        time.sleep(0.4)
    time.sleep(0.6)
    typed = page.evaluate("""(v) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop = pops[pops.length-1];
      if (!pop) return 'no-popup';
      const inp = pop.querySelector("input[data-tid='m4b_input']")
              || [...pop.querySelectorAll('input')].find(i => (i.placeholder||'').includes('自定义'));
      if (!inp) return 'no-input';
      const b = inp.getBoundingClientRect();
      window.__addBox = {x: Math.round(b.x + Math.min(b.width/2, 90)), y: Math.round(b.y + b.height/2)};
      return 'ok';
    }""", value)
    if typed != "ok":
        log(f"!! {label}: {typed}")
        page.keyboard.press("Escape")
        return False
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
        log(f"!! {label}: 添加按钮 {clicked}")
        page.keyboard.press("Escape")
        return False
    time.sleep(2.8)
    # 全页找新选项(可能在弹层外)
    picked = page.evaluate("""(want) => {
      const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const scopes = [pops[pops.length-1], document].filter(Boolean);
      for (const s of scopes) {
        const hit = [...s.querySelectorAll('*')]
            .find(e => e.children.length === 0 && (e.innerText||'').trim() === want);
        if (hit) {
          hit.scrollIntoView({block:'center'});
          const b = hit.getBoundingClientRect();
          window.__pickBox = {x: Math.round(b.x + Math.min(b.width/2, 280)),
                              y: Math.round(b.y + b.height/2)};
          return 'found';
        }
      }
      const pops2 = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      return 'not-found:' + (pops2.length ? (pops2[pops2.length-1].innerText||'').trim().slice(0,60) : '(无弹层)');
    }""", value)
    if picked == "found":
        box = page.evaluate("() => window.__pickBox")
        page.mouse.click(box["x"], box["y"])
        time.sleep(1.3)
        page.mouse.click(300, 150)
        time.sleep(1)
        cur = read_value(page, label)
        log(f"{label} → {cur}")
        return bool(cur and cur != "(空)")
    log(f"!! {label}: {picked}")
    page.keyboard.press("Escape")
    return False


def pick_existing(page, label, wants, multi=False, query=None):
    """从已有选项里选（不新增）。query 非空时先在下拉里搜索。"""
    if not open_popup(page, label):
        log(f"!! {label}: 弹层未出现")
        return False
    if query:
        # Arco 可搜索 Select 的搜索框就是可见的那个 input
        r = page.evaluate("""(q) => {
          const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
          const pop = pops.length ? pops[pops.length-1] : null;
          const scope = pop || document;
          const inp = [...scope.querySelectorAll('input')].filter(i => i.offsetParent !== null).pop();
          if (!inp) return null;
          inp.focus();
          const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
          setter.call(inp, q);
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          return 'searched';
        }""", query)
        log(f"搜索 {query!r}: {r}")
        time.sleep(2.2)
    ok = False
    for w in wants:
        r = page.evaluate("""(want) => {
          const pops = [...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
          const pop = pops[pops.length-1]; if (!pop) return null;
          const hit = [...pop.querySelectorAll('*')]
              .find(e => e.children.length === 0 && (e.innerText||'').trim() === want);
          if (!hit) return null;
          hit.scrollIntoView({block:'center'});
          const b = hit.getBoundingClientRect();
          return {x: Math.round(b.x + Math.min(b.width/2, 300)), y: Math.round(b.y + b.height/2)};
        }""", w)
        if r:
            page.mouse.click(r["x"], r["y"])
            log(f"选中 {w}")
            ok = True
            time.sleep(1.2)
        else:
            log(f"选项 {w} 未找到")
    if not multi:
        page.keyboard.press("Escape")
    else:
        page.mouse.click(300, 150)     # 多选:点外侧提交,不能 Escape
    time.sleep(1)
    log(f"{label} → {read_value(page, label)}")
    return ok


def read_value(page, label):
    return page.evaluate("""(l) => {
      const lb = [...document.querySelectorAll('span._title_80dgt_103')]
          .find(e => (e.textContent||'').trim() === l);
      if (!lb) return '(无字段)';
      let n = lb;
      for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement; if(n.querySelector('input')) break; }
      const v = [...n.querySelectorAll('input')].map(i => i.value).filter(Boolean);
      return v.length ? v.join('|').slice(0, 60) : '(空)';
    }""", label)


def type_text(page, label, value):
    c = center(page, find_select_js(label))
    if not c:
        log(f"!! {label}: 找不到")
        return False
    page.mouse.click(c["x"], c["y"])
    time.sleep(0.4)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(value, delay=20)
    time.sleep(0.7)
    log(f"{label} → {read_value(page, label)}")
    return True


# ---------------------------------------------------------------- 各步骤

def step_name(page):
    log("商品名")
    c = page.evaluate("""() => { const e = document.querySelector('#preview-product-title input');
      if (!e) return null; e.scrollIntoView({block:'center'});
      const r = e.getBoundingClientRect();
      return {x: Math.round(r.x+Math.min(r.width/2,300)), y: Math.round(r.y+r.height/2)}; }""")
    page.mouse.click(c["x"], c["y"])
    time.sleep(0.4)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(NAME, delay=8)
    time.sleep(1)
    v = page.evaluate("() => (document.querySelector('#preview-product-title input')||{}).value||''")
    log(f"商品名 {len(v)} 字符")
    return len(v) >= 25


def step_category(page):
    log("类目")
    cur = page.evaluate("() => (document.querySelector('[class*=cascader-select-view]')||{}).innerText||''")
    if "眼部护理" in cur:
        log("已是眼部护理")
        return True
    c = center(page, "document.querySelector('.p-cascader-select-view, [class*=cascader-select-view]')")
    page.mouse.click(c["x"], c["y"])
    time.sleep(2.5)
    for want in ("美妆个护", "护肤品", "眼部护理"):
        r = page.evaluate("""(want) => {
          const cols = [...document.querySelectorAll('.core-cascader-list-column')];
          for (let ci = cols.length - 1; ci >= 0; ci--) {
            const it = [...cols[ci].querySelectorAll('.core-cascader-list-item')]
                .find(e => (e.innerText||'').trim() === want);
            if (it) { it.scrollIntoView({block:'center'});
              const b = it.getBoundingClientRect();
              return {x: Math.round(b.x+b.width/2), y: Math.round(b.y+b.height/2)}; }
          }
          return null;
        }""", want)
        if not r:
            log(f"!! 找不到 {want}")
            return False
        page.mouse.click(r["x"], r["y"])
        log(f"选 {want}")
        time.sleep(2)
    cur = page.evaluate("() => (document.querySelector('[class*=cascader-select-view]')||{}).innerText||''")
    log(f"类目 → {cur.strip().replace(chr(10),' ')}")
    return "眼部护理" in cur


def step_desc(page):
    log("描述")
    c = center(page, "document.querySelector('.ProseMirror')")
    page.mouse.click(c["x"], c["y"])
    time.sleep(0.5)
    n = page.evaluate("""(text) => {
      const pm = document.querySelector('.ProseMirror'); if (!pm) return -1;
      pm.focus();
      const sel = window.getSelection(); sel.removeAllRanges();
      const rng = document.createRange(); rng.selectNodeContents(pm); sel.addRange(rng);
      document.execCommand('delete', false, null);
      text.split('\\n').forEach((ln, i) => {
        if (i > 0) document.execCommand('insertLineBreak', false, null);
        if (ln) document.execCommand('insertText', false, ln);
      });
      return (pm.innerText||'').length;
    }""", DESC)
    log(f"描述 {n} 字符")
    return n > 200


def step_image(page):
    log("主图")
    b64 = base64.b64encode(open(IMG, "rb").read()).decode()
    n = page.evaluate("""(b64) => {
      const bin = atob(b64); const arr = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      const dt = new DataTransfer();
      dt.items.add(new File([arr], 'eye_cream_main.jpg', {type: 'image/jpeg'}));
      const inps = [...document.querySelectorAll('input[type=file]')];
      // 主图框:优先 .jpg,其次 image/*,排除 .mp4/.pdf
      const t = inps.find(i => (i.accept||'').includes('.jpg') && !(i.accept||'').includes('pdf'))
             || inps.find(i => (i.accept||'') === 'image/*')
             || inps[0];
      if (!t) return -1;
      t.files = dt.files;
      t.dispatchEvent(new Event('change', {bubbles: true}));
      return t.files.length;
    }""", b64)
    log(f"注入 {n} 个文件")
    time.sleep(10)
    cnt = page.evaluate("""() => [...document.querySelectorAll('img')]
        .filter(e => e.src.includes('aphluv4xwc')).length""")
    log(f"页面图片 {cnt}")
    return n > 0


def step_sales(page):
    log("价格/库存/SKU")
    def ph(placeholder, val, alt=False):
        r = page.evaluate("""(a) => {
          const cands = [...document.querySelectorAll('input')]
            .filter(x => x.offsetParent !== null && (x.placeholder||'').includes(a.ph));
          const e = cands[cands.length - 1];
          if (!e) return null;
          e.scrollIntoView({block:'center'});
          const b = e.getBoundingClientRect();
          return {x: Math.round(b.x + Math.min(b.width/2, 150)), y: Math.round(b.y + b.height/2)};
        }""", {"ph": placeholder})
        if not r:
            log(f"!! 找不到 {placeholder}")
            return False
        page.mouse.click(r["x"], r["y"])
        time.sleep(0.35)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(val, delay=30)
        time.sleep(0.7)
        got = page.evaluate("""(a) => {
          const c = [...document.querySelectorAll('input')].filter(x => (x.placeholder||'').includes(a.ph));
          return c.length ? c[c.length-1].value : null;
        }""", {"ph": placeholder})
        log(f"{placeholder} → {got}")
        return bool(got)
    ph("零售价", PRICE)
    ph("数量", STOCK)
    ph("商家 SKU", SKU)
    return True


def step_dims(page):
    log("重量/尺寸")
    ok = type_text(page, "包裹重量", WEIGHT)
    for ph, v in zip(("高度", "宽度", "长度"), DIMS):
        r = page.evaluate("""(a) => {
          const e = [...document.querySelectorAll('input')]
            .find(x => x.offsetParent !== null && (x.placeholder||'') === a.ph);
          if (!e) return null;
          e.scrollIntoView({block:'center'});
          const b = e.getBoundingClientRect();
          return {x: Math.round(b.x + Math.min(b.width/2, 100)), y: Math.round(b.y + b.height/2)};
        }""", {"ph": ph})
        if not r:
            log(f"!! 找不到 {ph}")
            continue
        page.mouse.click(r["x"], r["y"])
        time.sleep(0.3)
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(v, delay=30)
        time.sleep(0.5)
    got = page.evaluate("""() => ['高度','宽度','长度'].map(ph => {
      const e = [...document.querySelectorAll('input')].find(x => (x.placeholder||'') === ph);
      return ph + '=' + (e ? e.value : '?');
    })""")
    log("尺寸 → " + ", ".join(got))
    return ok


def pick_radio(page, label="物流方式", want="默认"):
    """物流方式是 radio,不是下拉。"""
    log("物流方式")
    r = page.evaluate("""(want) => {
      const labs = [...document.querySelectorAll('label')];
      const e = labs.find(l => (l.innerText||'').trim() === want);
      if (!e) return null;
      e.scrollIntoView({block:'center'});
      const b = e.getBoundingClientRect();
      return {x: Math.round(b.x + b.width/2), y: Math.round(b.y + b.height/2)};
    }""", want)
    if not r:
        log("!! 找不到「默认」")
        return False
    page.mouse.click(r["x"], r["y"])
    time.sleep(1.2)
    checked = page.evaluate("""() => [...document.querySelectorAll('input[type=radio]')]
        .map(i => ({v: i.value, c: i.checked}))""")
    log(f"radio 状态: {checked}")
    return True


STEPS = [
    ("image", step_image),
    ("name", step_name),
    ("category", step_category),
    ("品牌", lambda p: pick_existing(p, "品牌", ["无品牌"], query="无品牌")),
    ("原产国", lambda p: pick_existing(p, "原产国/原产地", ["中国"], query="中国")),
    ("版本", lambda p: pick_existing(p, "版本", ["标准版"])),
    ("原料偏好", lambda p: pick_existing(p, "原料偏好", ["维他命C", "透明质酸", "神经酰胺"], multi=True)),
    ("desc", step_desc),
    ("sales", step_sales),
    ("dims", step_dims),
    ("物流方式", lambda p: pick_radio(p)),
    ("License type", lambda p: pick_existing(p, "License type",
                                             ["Cosmetic product notification form (CPNF)"])),
    ("License number", lambda p: add_and_pick(p, "License number", LIC_NO)),
    ("Date of issuance", lambda p: add_and_pick(p, "Date of issuance", LIC_DATE)),
    ("Place of issuance", lambda p: add_and_pick(p, "Place of issuance", LIC_PLACE)),
    ("制造商名称", lambda p: add_and_pick(p, "制造商/贸易商名称", MAKER)),
    ("制造商地址", lambda p: add_and_pick(p, "制造商/经销商地址", ADDR)),
]


def dump(page, tag=""):
    st = page.evaluate(r"""() => {
      const g = (l) => {
        const lb = [...document.querySelectorAll('span._title_80dgt_103')]
            .find(e => (e.textContent||'').trim() === l);
        if (!lb) return '(无)';
        let n = lb;
        for (let i=0;i<9&&n.parentElement;i++){ n=n.parentElement; if(n.querySelector('input')) break; }
        const v = [...n.querySelectorAll('input')].map(i => i.value).filter(Boolean);
        return v.length ? v.join('|').slice(0,44) : '(空)';
      };
      return {
        name: (document.querySelector('#preview-product-title input')||{}).value||'(空)',
        category: ((document.querySelector('[class*=cascader-select-view]')||{}).innerText||'').trim().replace(/\s+/g,' ').slice(0,50),
        imgs: [...document.querySelectorAll('img')].filter(e=>e.src.includes('aphluv4xwc')).length,
        descLen: ((document.querySelector('.ProseMirror')||{}).innerText||'').length,
        品牌: g('品牌'), 原产国: g('原产国/原产地'), 版本: g('版本'), 原料偏好: g('原料偏好'),
        License_type: g('License type'), License_no: g('License number'),
        Date: g('Date of issuance'), Place: g('Place of issuance'),
        制造商: g('制造商/贸易商名称'), 地址: g('制造商/经销商地址'),
        重量: g('包裹重量'), 物流方式: g('物流方式'),
        problems: [...document.querySelectorAll('*')].filter(e =>
            e.children.length===0 && /个问题/.test(e.textContent||''))
          .map(e=>(e.textContent||'').trim()).filter(t=>t.length<16),
      };
    }""")
    print(f"--- 状态 {tag} ---")
    for k, v in st.items():
        mark = "✓" if v not in ("(空)", "(无)", "", 0, 1) or k in ("imgs", "descLen") else " "
        print(f"  [{mark}] {k:<12} {str(v)[:58]}")
    return st


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--only", default=None, help="只跑某一步")
    a = ap.parse_args()
    if not (a.fill or a.submit):
        ap.error("需要 --fill 或 --submit")

    with sync_playwright() as pw:
        page = get_page(pw)
        page.keyboard.press("Escape")
        time.sleep(1)
        dump(page, "before")
        for nm, fn in STEPS:
            if a.only and nm != a.only:
                continue
            print(f"\n>>> {nm}")
            try:
                log(f"结果: {fn(page)}")
            except Exception as e:
                log(f"!! {nm} 异常: {type(e).__name__}: {str(e)[:150]}")
            time.sleep(0.6)
        dump(page, "after")
        page.screenshot(path=os.path.join(HERE, "notes", "tk178_build.png"), full_page=True)

        if a.submit:
            print("\n>>> 提交")
            page.evaluate("() => localStorage.removeItem('__ttRecBuf')")
            rec = open(os.path.join(HERE, "tt_scrape.py")).read() \
                .split('RECORDER = r"""')[1].split('"""')[0]
            page.evaluate(rec)
            page.evaluate("() => window.scrollTo(0,0)")
            time.sleep(1.2)
            page.get_by_text("提交审核", exact=True).first.click(timeout=10000)
            time.sleep(16)
            posts = json.loads(page.evaluate(
                "() => JSON.stringify((window.__ttRec.get()||[])"
                ".filter(r => r.method === 'POST' && (r.url||'').includes('seller-vn')))") or "[]")
            print(f"自家 POST {len(posts)} 条")
            for r in posts:
                print(f"  [{r.get('status')}] {r['url'].split('?')[0].replace('https://seller-vn.tiktok.com','')}"
                      f"  req={len(r.get('reqBody') or '')}B")
            for r in posts:
                if any(k in (r["url"] or "") for k in ("product/create", "msubmit", "product/edit")):
                    print("=" * 92)
                    print(r["url"].split("?")[0])
                    print("REQ :", (r.get("reqBody") or "")[:2500])
                    print("RESP:", (r.get("respBody") or "")[:600])
            json.dump(posts, open(os.path.join(HERE, "notes", "tk178_create_posts.json"), "w"),
                      ensure_ascii=False, indent=2)
            dump(page, "submitted")
            page.screenshot(path=os.path.join(HERE, "notes", "tk178_submitted.png"), full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
