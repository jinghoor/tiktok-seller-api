#!/usr/bin/env python3
"""收尾：在已准备好的 discount/create 页面上填折扣值 → 批量更新 → 提交 → 抓 discount/create payload。

用于 promo_create_capture.py 的 --prepare-only 之后接着跑，或流程中途失败手工续跑。

定位要点(踩过的坑):
  - 这个 SPA 里 input 的 offsetParent 为 null,不能用 offsetParent!==null 做可见性过滤
  - `% 折扣` 文本在页面上出现两次(列头 / 批量操作区),要选祖先里确实含 input 的那个
  - 活动名称 input 也是 .theme-arco-input-size-large,靠 placeholder 非空区分
  - Playwright 回调里只能读 post_data 这类本地缓存属性,调 res.text() 会死锁
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "notes" / "promo_create_payload.json"

JS_BATCH_INPUT_INDEX = """() => {
  const all=[...document.querySelectorAll('input')];
  // A: 从「% 折扣」文本往上找真正包着 input 的那个容器
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
  // B: 兜底 —— size-large 且无 placeholder 的 text input(活动名称那个有 placeholder)
  const c=all.filter(e=>e.type==='text' && (e.className||'').includes('size-large')
                        && !e.disabled && !e.placeholder);
  return c.length ? all.indexOf(c[c.length-1]) : -1;
}"""


def main() -> None:
    captured: list[dict] = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:CDP_PORT")
        page = next(x for x in b.contexts[0].pages if "discount/create" in x.url)
        txt = page.evaluate("document.body.innerText")
        assert "件商品" in txt, "页面不是「已选好商品」状态，先跑 promo_create_capture.py"

        idx = page.evaluate(JS_BATCH_INPUT_INDEX)
        print("折扣输入框 index:", idx)
        assert idx >= 0, "定位折扣输入框失败"
        inp = page.locator("input").nth(idx)
        inp.click()
        inp.fill("10")
        time.sleep(1)
        print("填入:", inp.input_value())

        print("点「批量更新」")
        page.locator("button", has_text="批量更新").first.click()
        time.sleep(3)
        applied = page.evaluate("""() => {
          const m=document.body.innerText.match(/([\\d.]+)₫ - ([\\d.]+)₫[\\s\\S]{0,60}?% 折扣[\\s\\S]{0,60}?([\\d.]+)₫ - ([\\d.]+)₫/);
          return m ? m.slice(1).join(' | ') : 'pattern-miss';
        }""")
        print("行折扣检查(原价|折扣后):", applied)

        def on_request(req):
            try:
                u = req.url
                if "/api/v1/promotion/" not in u or req.method == "OPTIONS":
                    return
                captured.append({"method": req.method,
                                 "path": u.split("?")[0].split(".com")[-1],
                                 "url": u, "body": req.post_data})
            except Exception as e:
                captured.append({"_hook_err": str(e)[:120]})

        page.on("request", on_request)

        print("\n点「同意并发布」")
        btn = page.locator("button", has_text="同意并发布").first
        print("  disabled:", btn.is_disabled())
        btn.click()
        for _ in range(25):
            time.sleep(1)
            if any((c.get("path") or "").endswith("/discount/create") for c in captured):
                time.sleep(3)
                break

    print(f"\n=== 捕获 {len(captured)} 条 ===")
    for c in captured:
        print(f"  {c['method']:5} {(c.get('path') or '')[:80]}  body={len(c.get('body') or '')}")

    creates = [c for c in captured if (c.get("path") or "").endswith("/discount/create")]
    if creates:
        c = creates[-1]
        raw = c.get("body") or ""
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            "path": c["path"], "method": c["method"],
            "body": json.loads(raw) if raw.lstrip().startswith(("{", "[")) else None,
            "body_raw": raw, "all_requests": captured,
        }, ensure_ascii=False, indent=2))
        print(f"\n=== payload → {OUT} ===\n{raw[:3000]}")
    else:
        print("\n未捕获 discount/create")


if __name__ == "__main__":
    main()
