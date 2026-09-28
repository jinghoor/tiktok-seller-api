#!/usr/bin/env python3
"""CDP 拦截 + 已调通的 UI 填充 → 抓真实 create 调用。

填充用的是已经在 TK178 上跑通过的那批函数（不是通用回退版）。
"""
from __future__ import annotations

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
NAME = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g - Bản Chuẩn API Test, "
        "Giảm Thâm Quầng Và Dưỡng Sáng Vùng Mắt")
DESC = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g\n\n"
        "Công thức làm sáng chuyên biệt giúp lấy lại làn da mịn màng, rạng rỡ cho vùng da quanh mắt.\n\n"
        "THÀNH PHẦN CHÍNH:\n- AXIT ASCORBIC: Giảm sạm màu, bề mặt và vết thâm.\n"
        "- AXIT CITRIC: Làm sáng hiệp đồng ở lớp trung bình, thúc đẩy tái tạo da.\n"
        "- NIACINAMIDE: Ức chế melanin ở lớp sâu, giúp da đều màu và sáng mịn.\n\n"
        "CÔNG DỤNG:\n- Giảm thâm quầng và bọng mắt\n- Dưỡng sáng vùng da quanh mắt\n"
        "- Hỗ trợ làm mờ nếp nhăn nhỏ\n- Cấp ẩm, giữ vùng mắt mềm mại\n\n"
        "CÁCH DÙNG: Lấy một lượng nhỏ kem, chấm nhẹ quanh vùng mắt rồi vỗ nhẹ cho thấm.\n\n"
        "THÔNG TIN SẢN PHẨM:\n- Dung tích: 20g (0.71oz)\n- Hạn sử dụng: 3 năm")
LIC_NO, LIC_DATE, LIC_PLACE = "GNUMBER_REDACTED", "2024-01-15", "Guangdong"
MAKER, ADDR = "Kormesic Cosmetics Co Ltd", "Baiyun District Guangzhou"
PRICE, STOCK, SKU = "200000", "100", "API-EYE-20G"

WATCH = ("/product/local/product", "/product/local/draft", "/product/msubmit",
         "/product/images/msubmit", "/product/comp/", "/product/sku/")


class Tap:
    def __init__(self, page):
        self.hits = []
        self.cdp = page.context.new_cdp_session(page)
        self.cdp.on("Fetch.requestPaused", self._on)
        self.cdp.send("Fetch.enable", {"patterns": [
            {"urlPattern": "*seller-vn.tiktok.com/api/v1/product/*", "requestStage": "Request"},
        ]})
        print("[tap] Fetch 拦截已开")

    def _on(self, p):
        rid = p.get("requestId")
        try:
            req = p.get("request", {})
            url = req.get("url", "")
            path = url.split("?")[0].replace("https://seller-vn.tiktok.com", "")
            body = req.get("postData", "")
            if any(w in path for w in WATCH):
                self.hits.append({"path": path, "method": req.get("method"),
                                  "url": url, "body": body, "len": len(body)})
                print(f"[tap] ★ {req.get('method')} {path}  {len(body)}B")
        except Exception as e:  # noqa: BLE001
            print("[tap] !!", type(e).__name__, str(e)[:100])
        try:
            self.cdp.send("Fetch.continueRequest", {"requestId": rid})
        except Exception:
            pass

    def stop(self):
        try:
            self.cdp.send("Fetch.disable")
        except Exception:
            pass


# ---- 已验证的填充原语 ----

def center(page, js):
    return page.evaluate(
        "(src) => { let e=null; try { e = eval(src); } catch (x) { return null; }"
        " if (e && typeof e === 'function') e = e(); if (!e) return null;"
        " e.scrollIntoView({block:'center'}); const r = e.getBoundingClientRect();"
        " return {x: Math.round(r.x + Math.min(r.width/2, 280)), y: Math.round(r.y + r.height/2)}; }",
        js)


def label_js(label, sel=None):
    inner = (f"node.querySelector({json.dumps(sel)})" if sel else "node")
    return ("(function(){"
            f" const L={json.dumps(label, ensure_ascii=False)};"
            " const lb=[...document.querySelectorAll('span._title_80dgt_103')]"
            "   .find(e=>(e.textContent||'').trim()===L);"
            " if(!lb) return null; let node=lb;"
            " for(let i=0;i<9&&node.parentElement;i++){node=node.parentElement;"
            "   if(node.querySelector('input,textarea,[contenteditable=true],[class*=select-view]')) break;}"
            f" return {inner}; }})")


def pick(page, label, wants, query=None, multi=False):
    c = center(page, label_js(label, ".core-select,.core-cascader,[role=combobox]"))
    if not c:
        print(f"    !! {label}: 找不到"); return False
    page.mouse.click(c["x"], c["y"]); time.sleep(2.2)
    if query:
        page.evaluate("""(q) => {
          const pops=[...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
          const pop=pops[pops.length-1]; const scope=pop||document;
          const inp=[...scope.querySelectorAll('input')].filter(i=>i.offsetParent!==null).pop();
          if(!inp) return;
          inp.focus();
          const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
          s.call(inp,q); inp.dispatchEvent(new Event('input',{bubbles:true}));
        }""", query)
        time.sleep(2.2)
    ok = False
    for w in wants:
        r = page.evaluate("""(w) => {
          const pops=[...document.querySelectorAll('.core-select-popup,.core-cascader-popup')]
            .filter(e=>e.offsetParent!==null);
          const pop=pops[pops.length-1]; if(!pop) return null;
          const hit=[...pop.querySelectorAll('*')].find(e=>e.children.length===0&&(e.innerText||'').trim()===w);
          if(!hit) return null;
          hit.scrollIntoView({block:'center'});
          const b=hit.getBoundingClientRect();
          return {x:Math.round(b.x+Math.min(b.width/2,280)), y:Math.round(b.y+b.height/2)};
        }""", w)
        if r:
            page.mouse.click(r["x"], r["y"]); print(f"    选中 {w}"); ok = True; time.sleep(1.2)
        else:
            print(f"    !! 选项 {w} 未找到")
    if multi:
        page.mouse.click(300, 150)
    else:
        page.keyboard.press("Escape")
    time.sleep(1)
    return ok


def add_opt(page, label, value):
    c = center(page, label_js(label, ".core-select,.core-cascader,[role=combobox]"))
    if not c:
        print(f"    !! {label}: 找不到"); return False
    page.mouse.click(c["x"], c["y"]); time.sleep(2.2)
    r = page.evaluate("""() => {
      const pops=[...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop=pops[pops.length-1]; if(!pop) return 'no-popup';
      const inp=pop.querySelector("input[data-tid='m4b_input']")
              || [...pop.querySelectorAll('input')].find(i=>(i.placeholder||'').includes('自定义'));
      if(!inp) return 'no-input';
      const b=inp.getBoundingClientRect();
      return {x:Math.round(b.x+Math.min(b.width/2,90)), y:Math.round(b.y+b.height/2)};
    }""")
    if not isinstance(r, dict):
        print(f"    !! {r}"); return False
    page.mouse.click(r["x"], r["y"]); time.sleep(0.4)
    page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
    page.keyboard.type(value, delay=35); time.sleep(0.8)
    c2 = page.evaluate("""() => {
      const pops=[...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop=pops[pops.length-1]; if(!pop) return 'no-popup';
      const btn=pop.querySelector("button[data-tid='m4b_button']")
              || [...pop.querySelectorAll('button')].find(b=>(b.innerText||'').trim()==='添加');
      if(!btn) return 'no-btn'; btn.click(); return 'clicked';
    }""")
    if c2 != "clicked":
        print(f"    !! 添加: {c2}"); return False
    time.sleep(2.5)
    r2 = page.evaluate("""(w) => {
      const pops=[...document.querySelectorAll('.core-select-popup')].filter(e=>e.offsetParent!==null);
      const pop=pops[pops.length-1];
      const hit=[...pop.querySelectorAll('*')].find(e=>e.children.length===0&&(e.innerText||'').trim()===w);
      if(!hit) return null;
      const b=hit.getBoundingClientRect();
      return {x:Math.round(b.x+Math.min(b.width/2,280)), y:Math.round(b.y+b.height/2)};
    }""", value)
    if r2:
        page.mouse.click(r2["x"], r2["y"]); time.sleep(1.3)
        page.mouse.click(300, 150); time.sleep(1)
        print(f"    {label} = {value}")
        return True
    print(f"    !! {label} 选项未出现")
    page.keyboard.press("Escape")
    return False


def fill(page):
    # 主图
    b64 = base64.b64encode(open(IMG, "rb").read()).decode()
    page.evaluate("""(b64) => {
      const bin=atob(b64); const arr=new Uint8Array(bin.length);
      for(let i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i);
      const dt=new DataTransfer();
      dt.items.add(new File([arr],'m.jpg',{type:'image/jpeg'}));
      const inps=[...document.querySelectorAll('input[type=file]')];
      const t=inps.find(i=>(i.accept||'').includes('.jpg')&&!(i.accept||'').includes('pdf'))
             || inps.find(i=>(i.accept||'')==='image/*') || inps[0];
      if(t){t.files=dt.files; t.dispatchEvent(new Event('change',{bubbles:true}));}
    }""", b64)
    time.sleep(9)
    print("  主图 ok")

    # 名称
    ns = "#preview-product-title input"
    page.evaluate("""(s) => { const e=document.querySelector(s);
      if(e){e.scrollIntoView({block:'center'}); e.click(); e.focus();} }""", ns)
    time.sleep(0.4)
    page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
    page.keyboard.type(NAME, delay=8); time.sleep(1.2)
    print("  名称:", len(page.evaluate(f"() => (document.querySelector({json.dumps(ns)})||{{}}).value||''")))

    # 类目
    c = center(page, "document.querySelector('.p-cascader-select-view,[class*=cascader-select-view]')")
    page.mouse.click(c["x"], c["y"]); time.sleep(2.5)
    for want in ("美妆个护", "护肤品", "眼部护理"):
        r = page.evaluate("""(w) => {
          const cols=[...document.querySelectorAll('.core-cascader-list-column')];
          for(let ci=cols.length-1;ci>=0;ci--){
            const it=[...cols[ci].querySelectorAll('.core-cascader-list-item')]
              .find(e=>(e.innerText||'').trim()===w);
            if(it){it.scrollIntoView({block:'center'}); const b=it.getBoundingClientRect();
              return {x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)};}
          } return null;
        }""", want)
        if not r:
            print(f"    !! 类目 {want}"); break
        page.mouse.click(r["x"], r["y"]); time.sleep(2)
    print("  类目:", page.evaluate("() => (document.querySelector('[class*=cascader-select-view]')||{}).innerText||''").strip().replace("\n", " "))

    # 描述
    c = center(page, "document.querySelector('.ProseMirror')")
    page.mouse.click(c["x"], c["y"]); time.sleep(0.6)
    n = page.evaluate("""(t) => {
      const pm=document.querySelector('.ProseMirror'); if(!pm) return -1;
      pm.focus();
      const s=window.getSelection(); s.removeAllRanges();
      const r=document.createRange(); r.selectNodeContents(pm); s.addRange(r);
      document.execCommand('delete',false,null);
      t.split('\\n').forEach((ln,i)=>{ if(i>0) document.execCommand('insertLineBreak',false,null);
        if(ln) document.execCommand('insertText',false,ln); });
      return (pm.innerText||'').length;
    }""", DESC)
    print("  描述:", n)

    print("  品牌"); pick(page, "品牌", ["无品牌"], query="无品牌")
    print("  原产国"); add_opt(page, "原产国/原产地", "China")
    print("  版本"); pick(page, "版本", ["标准版"])
    print("  原料偏好"); pick(page, "原料偏好", ["维他命C", "透明质酸", "神经酰胺"], multi=True)

    # 价格/库存/SKU(表头批量框 + 表格行)
    def ph(placeholder, val):
        r = page.evaluate("""(a) => {
          const c=[...document.querySelectorAll('input')].filter(x=>x.offsetParent!==null
            && (x.placeholder||'').includes(a.ph));
          const e=c[c.length-1]; if(!e) return null;
          e.scrollIntoView({block:'center'}); const b=e.getBoundingClientRect();
          return {x:Math.round(b.x+Math.min(b.width/2,120)), y:Math.round(b.y+b.height/2)};
        }""", {"ph": placeholder})
        if not r:
            print(f"    !! {placeholder}"); return
        page.mouse.click(r["x"], r["y"]); time.sleep(0.35)
        page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
        page.keyboard.type(val, delay=30); time.sleep(0.7)
    ph("零售价", PRICE); ph("数量", STOCK); ph("商家 SKU", SKU)
    # 表格单元格
    for i, v in enumerate((STOCK, PRICE, SKU)):
        r = page.evaluate("""(k) => {
          const ins=[...document.querySelectorAll('table input.core-input')].filter(i=>i.offsetParent!==null);
          const e=ins[k]; if(!e) return null;
          e.scrollIntoView({block:'center'}); const b=e.getBoundingClientRect();
          return {x:Math.round(b.x+Math.min(b.width/2,60)), y:Math.round(b.y+b.height/2)};
        }""", i)
        if r:
            page.mouse.click(r["x"], r["y"]); time.sleep(0.3)
            page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
            page.keyboard.type(v, delay=30); time.sleep(0.5)
    print("  销售信息 ok")

    # 重量 + 尺寸
    for label, val in (("包裹重量", "80"),):
        c = center(page, label_js(label, ".core-input"))
        if c:
            page.mouse.click(c["x"], c["y"]); time.sleep(0.3)
            page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
            page.keyboard.type(val, delay=30); time.sleep(0.6)
    for i, (ph_, v) in enumerate((("高度", "12"), ("宽度", "4"), ("长度", "3"))):
        r = page.evaluate("""(a) => {
          const e=[...document.querySelectorAll('input')].find(x=>(x.placeholder||'')===a.ph);
          if(!e) return null; e.scrollIntoView({block:'center'});
          const b=e.getBoundingClientRect();
          return {x:Math.round(b.x+Math.min(b.width/2,80)), y:Math.round(b.y+b.height/2)};
        }""", {"ph": ph_})
        if r:
            page.mouse.click(r["x"], r["y"]); time.sleep(0.3)
            page.keyboard.press("Meta+A"); page.keyboard.press("Backspace")
            page.keyboard.type(v, delay=30); time.sleep(0.45)
    print("  物流 ok")

    print("  License type"); pick(page, "License type",
                              ["Cosmetic product notification form (CPNF)"])
    print("  License number"); add_opt(page, "License number", LIC_NO)
    print("  Date"); add_opt(page, "Date of issuance", LIC_DATE)
    print("  Place"); add_opt(page, "Place of issuance", LIC_PLACE)
    print("  制造商"); add_opt(page, "制造商/贸易商名称", MAKER)
    print("  地址"); add_opt(page, "制造商/经销商地址", ADDR)


def main() -> int:
    with sync_playwright() as pw:
        page = get_page(pw)
        tap = Tap(page)
        try:
            print("打开创建页…")
            page.goto("https://seller-vn.tiktok.com/product/create?shop_region=VN",
                      wait_until="domcontentloaded")
            time.sleep(20)
            page.set_viewport_size({"width": 1680, "height": 2400}); time.sleep(2)
            page.keyboard.press("Escape"); time.sleep(1)
            print("URL:", page.url)
            fill(page)
            print("\n--- 提交 ---")
            page.evaluate("() => window.scrollTo(0,0)"); time.sleep(1.5)
            btn = page.evaluate("""() => {
              const b=[...document.querySelectorAll('button')].find(x=>x.offsetParent!==null
                && (x.innerText||'').trim()==='提交审核');
              const r=b.getBoundingClientRect();
              return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)};
            }""")
            page.mouse.click(btn["x"], btn["y"]); time.sleep(8)
            dlg = page.evaluate("""() => {
              const d=[...document.querySelectorAll('button')].filter(x=>x.offsetParent!==null
                && (x.innerText||'').trim()==='提交');
              return d.map(x=>{const r=x.getBoundingClientRect();
                return {x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2)};});
            }""")
            if dlg:
                page.mouse.click(dlg[-1]["x"], dlg[-1]["y"]); print("已点弹窗提交")
            time.sleep(20)
        finally:
            tap.stop()
            json.dump({"hits": tap.hits}, open(os.path.join(HERE, "notes", "tk178_create_real.json"),
                                              "w"), ensure_ascii=False, indent=2)
            print(f"\n抓到 {len(tap.hits)} 个:")
            for h in tap.hits:
                print(f"  {h['method']} {h['path']}  {h['len']}B")
            page.screenshot(path=os.path.join(HERE, "notes", "tk178_create_real.png"),
                            full_page=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
