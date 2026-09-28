#!/usr/bin/env python3
"""GMV Max 创建流程 —— 分步执行，每步都验证。

    python3 hub_flow.py --port CDP_PORT --step select-products
    python3 hub_flow.py --port CDP_PORT --step add-one --product <id>
    python3 hub_flow.py --port CDP_PORT --step set-roi --roi 14
    python3 hub_flow.py --port CDP_PORT --step status
"""
from __future__ import annotations
import argparse, json, sys, time
from playwright.sync_api import sync_playwright

CREATION = "/ads-creation/creation"


def get_page(b):
    for c in b.contexts:
        for pg in c.pages:
            if CREATION in pg.url:
                return pg
    raise SystemExit("找不到创建页")


def click_radio(pg, value: str) -> bool:
    """点 value 匹配的 radio 的可见标签。"""
    ok = pg.evaluate("""(v) => {
        const r = document.querySelector(`input[type=radio][value="${v}"]`);
        if (!r) return false;
        const box = r.closest('label') || r.parentElement;
        const tgt = box || r;
        tgt.click();
        return true;
    }""", value)
    return bool(ok)


def dump_state(pg, label=""):
    st = pg.evaluate("""() => {
        const out = {};
        const val = e => e ? (e.getAttribute('value') ?? '') : null;
        out.type   = val(document.querySelector('input[type=radio][value=all]:checked, input[type=radio][value=specific]:checked'));
        // 商品类型:找 checked 的 radio
        const radios = {};
        for (const r of document.querySelectorAll('input[type=radio]')) {
            if (r.checked) radios[r.value] = true;
        }
        out.checkedRadios = Object.keys(radios);
        const roi = document.querySelector('[data-testid="bid-select-index-9egWxE"]');
        const bud = document.querySelector('[data-testid="budget-index-sC4ibw"]');
        out.roi = roi ? roi.getAttribute('value') : null;
        out.budget = bud ? bud.getAttribute('value') : null;
        const sw = document.querySelector('.promotion-days-switch-label');
        out.promotionDaysSwitch = sw ? (sw.className||'').includes('checked') : null;
        // 商品计数
        const m = document.body.innerText.match(/清单中的商品：\\s*(\\d+)/);
        out.productCount = m ? m[1] : null;
        out.productTypeText = (document.body.innerText.match(/(所有商品|选定商品|排除商品)/g)||[]).join(',');
        return out;
    }""")
    print(f"  [{label}] {json.dumps(st, ensure_ascii=False)}")
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--step", required=True)
    ap.add_argument("--roi", default="14")
    ap.add_argument("--product", default=None)
    a = ap.parse_args()

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{a.port}")
        pg = get_page(b)
        print(f"页面: {pg.url[:100]}")

        if a.step == "status":
            dump_state(pg, "当前")

        elif a.step == "select-products":
            print("选中【选定商品】…")
            ok = click_radio(pg, "specific")
            print(f"  点击结果: {ok}")
            time.sleep(4)
            dump_state(pg, "选后")
            txt = pg.evaluate("() => document.body.innerText")
            # 打印商品区域文本
            i = txt.find("选定商品")
            print("\n--- 商品区文本 ---")
            print(txt[max(0,i-120):i+900])

        elif a.step == "set-roi":
            print(f"设置 ROI = {a.roi}")
            sel = '[data-testid="bid-select-index-9egWxE"] input'
            el = pg.query_selector(sel)
            if not el:
                print("找不到 ROI input"); sys.exit(1)
            print(f"  设置前: {el.input_value()!r}")
            el.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Meta+A")
            el.fill(a.roi)
            pg.keyboard.press("Tab")
            time.sleep(1.5)
            el2 = pg.query_selector(sel)
            host = pg.query_selector('[data-testid="bid-select-index-9egWxE"]')
            comp_val = host.get_attribute("value") if host else None
            print(f"  设置后: input={el2.input_value()!r}  组件 value={comp_val!r}")

        elif a.step == "add-one":
            print("点【新增】打开商品选择弹窗…")
            clicked = pg.evaluate("""() => {
                for (const e of document.querySelectorAll('button, [role=button], div')) {
                    const t=(e.innerText||'').trim();
                    if (t === '新增' || t === '添加商品') { e.click(); return t; }
                }
                return null;
            }""")
            print(f"  点到: {clicked!r}")
            time.sleep(4)
            dump_state(pg, "弹窗后")
            # 弹窗里的结构
            dlg = pg.evaluate("""() => {
                const d = document.querySelector('[role=dialog], .theme-arco-modal, [class*="modal"]');
                if (!d) return 'no dialog';
                return {text: d.innerText.slice(0, 1200)};
            }""")
            print("\n--- 弹窗 ---")
            print(json.dumps(dlg, ensure_ascii=False)[:1400])
        else:
            print(f"未知步骤 {a.step}")
        b.close()


if __name__ == "__main__":
    main()
