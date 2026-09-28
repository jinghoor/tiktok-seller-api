#!/usr/bin/env python3
"""批量创建 GMV Max 广告：每个广告只放 1 个商品，ROI=14，促销日关闭，预算 200。

可断点续跑:已完成的商品 id 记在 notes/hub_done.json,重跑会跳过。

    python3 hub_batch.py --port CDP_PORT            # 处理全部剩余
    python3 hub_batch.py --port CDP_PORT --limit 1  # 只做 1 个(试跑)
    python3 hub_batch.py --port CDP_PORT --dry      # 只列商品不提交
"""
from __future__ import annotations
import argparse, json, re, sys, time, traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DONE = HERE / "notes" / "hub_done.json"
LOG = HERE / "notes" / "hub_batch.log"
ROI = "14"
BUDGET = "200.00"
SEL_ROI = '[data-testid="bid-select-index-9egWxE"]'
SEL_BUD = '[data-testid="budget-index-sC4ibw"]'
SEL_PROMO = '[data-testid="promotion-days-toggle-3EnDzt"]'
SEL_DRAWER = '[data-testid="product-select-index-6KM6mN"]'


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_done() -> set:
    if DONE.exists():
        try:
            return set(json.loads(DONE.read_text()))
        except Exception:
            return set()
    return set()


def save_done(s: set) -> None:
    DONE.parent.mkdir(parents=True, exist_ok=True)
    DONE.write_text(json.dumps(sorted(s), ensure_ascii=False, indent=1))


def go_dashboard(pg) -> None:
    if "/ads-creation/dashboard" not in pg.url:
        pg.goto("https://seller-vn.tiktok.com/ads-creation/dashboard", wait_until="domcontentloaded")
    pg.wait_for_timeout(4000)


def open_creation(pg) -> None:
    """从 dashboard 进入创建页。"""
    go_dashboard(pg)
    btn = pg.get_by_role("button", name=re.compile("创建 GMV Max 广告"))
    btn.click(timeout=20000)
    pg.wait_for_timeout(6000)
    if "/creation" not in pg.url:
        raise RuntimeError(f"没进入创建页: {pg.url[:90]}")


def pick_products(pg, need: int, exclude: set) -> list:
    """打开商品选择器,勾选 need 个未完成的商品。返回勾选的 id 列表。"""
    pg.evaluate("""() => {
        const r = document.querySelector('input[type=radio][value="specific"]');
        if (r) (r.closest('label') || r.parentElement || r).click();
    }""")
    pg.wait_for_timeout(3000)

    loc = pg.get_by_text("添加商品", exact=True)
    if not loc.count():
        raise RuntimeError("找不到【添加商品】")
    loc.last.click(timeout=15000)
    pg.wait_for_timeout(6000)
    if not pg.locator(SEL_DRAWER).count():
        raise RuntimeError("商品抽屉没打开")

    # 先在弹窗里搜出还没做的商品,再勾选
    rows = pg.evaluate("""() => {
        const out=[];
        for (const tr of document.querySelectorAll('tr')) {
            const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
            const m=t.match(/ID:\\s*(\\d{15,25})/);
            if (m) out.push(m[1]);
        }
        return out;
    }""")
    todo = [i for i in rows if i not in exclude][:need]
    if not todo:
        raise RuntimeError("没有可做的商品了")

    picked = pg.evaluate("""(ids) => {
        let n = 0;
        for (const tr of document.querySelectorAll('tr')) {
            const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
            const m=t.match(/ID:\\s*(\\d{15,25})/);
            if (!m || !ids.includes(m[1])) continue;
            const cb = tr.querySelector('input[type=checkbox]');
            if (cb && !cb.checked) { cb.click(); n++; }
        }
        return n;
    }""", todo)
    pg.wait_for_timeout(2000)

    got = pg.evaluate("""() => {
        const out=[];
        for (const tr of document.querySelectorAll('tr')) {
            const cb = tr.querySelector('input[type=checkbox]');
            if (!cb || !cb.checked) continue;
            const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
            const m=t.match(/ID:\\s*(\\d{15,25})/);
            if (m) out.push(m[1]);
        }
        return out;
    }""")
    log(f"    勾选 {picked} 个,实际选中 {len(got)}: {got}")

    # 真实鼠标点【确认】
    c = pg.get_by_text("确认", exact=True)
    tgt = None
    for i in range(c.count()):
        try:
            bx = c.nth(i).bounding_box()
            if bx and bx["width"] > 20:
                tgt = c.nth(i); break
        except Exception:
            pass
    if not tgt:
        raise RuntimeError("找不到确认按钮")
    tgt.click(timeout=15000)
    pg.wait_for_timeout(4000)

    # 等遮罩消失
    for _ in range(10):
        if not pg.locator(SEL_DRAWER).count():
            break
        pg.wait_for_timeout(1000)
    return got


def set_roi(pg, val: str) -> str:
    inp = pg.locator(f"{SEL_ROI} input")
    host = pg.locator(SEL_ROI)
    inp.click(timeout=15000)
    inp.click(click_count=3, timeout=8000)
    pg.wait_for_timeout(300)
    pg.keyboard.press("Backspace")
    pg.wait_for_timeout(300)
    if inp.input_value().strip():
        for _ in range(12):
            pg.keyboard.press("Backspace")
        pg.wait_for_timeout(300)
    inp.type(val, delay=90)
    pg.wait_for_timeout(500)
    pg.keyboard.press("Tab")
    pg.wait_for_timeout(2000)
    return host.get_attribute("value") or ""


def ensure_promo_off(pg) -> bool:
    sw = pg.locator(SEL_PROMO)
    cur = sw.get_attribute("aria-checked")
    if cur == "true":
        sw.scroll_into_view_if_needed()
        pg.wait_for_timeout(400)
        sw.click(timeout=10000)
        pg.wait_for_timeout(2500)
    return (sw.get_attribute("aria-checked") == "false")


def publish(pg) -> None:
    loc = pg.get_by_text("发布", exact=True)
    tgt = None
    for i in range(loc.count()):
        try:
            bx = loc.nth(i).bounding_box()
            if bx and bx["width"] > 20:
                tgt = loc.nth(i); break
        except Exception:
            pass
    if not tgt:
        raise RuntimeError("找不到发布按钮")
    tgt.click(timeout=15000)
    # 等跳回 dashboard
    for _ in range(20):
        pg.wait_for_timeout(1500)
        if "/dashboard" in pg.url:
            return
    raise RuntimeError(f"发布后没跳回 dashboard: {pg.url[:90]}")


def state(pg) -> dict:
    return pg.evaluate("""(sels) => {
        const q = s => document.querySelector(s);
        const txt = document.body.innerText;
        const m = txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
        return {
          promo: q(sels.p) ? q(sels.p).getAttribute('aria-checked') : null,
          roi: q(sels.r) ? q(sels.r).getAttribute('value') : null,
          budget: q(sels.b) ? q(sels.b).getAttribute('value') : null,
          selected: m ? m[1] : null,
          name: (document.querySelector('input[placeholder*="广告计划名称"]')||{}).value || null,
        };
    }""", {"p": SEL_PROMO, "r": SEL_ROI, "b": SEL_BUD})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--limit", type=int, default=0, help="最多做几个(0=全部)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    done = load_done()
    log(f"=== 开始  port={a.port}  已完成 {len(done)} 个 ===")

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{a.port}")
        pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)
        made = 0
        n = 0
        while True:
            if a.limit and made >= a.limit:
                log(f"达到 limit={a.limit},停止")
                break
            n += 1
            log(f"--- 第 {n} 轮 ---")
            try:
                open_creation(pg)
                ids = pick_products(pg, 1, done)
                if not ids:
                    log("无可选商品,结束"); break
                pid = ids[0]
                if a.dry:
                    log(f"[dry] 本可提交商品 {pid}")
                    break
                roi = set_roi(pg, ROI)
                promo_ok = ensure_promo_off(pg)
                st = state(pg)
                log(f"    设置: roi={roi} budget={st['budget']} promo={st['promo']} selected={st['selected']}")
                if st["selected"] != "1" or st["promo"] != "false" or not roi.startswith("14"):
                    raise RuntimeError(f"设置不符,放弃提交: {st}")
                publish(pg)
                done.add(pid); save_done(done)
                made += 1
                log(f"    ✓ 已提交 商品={pid}  (累计 {made})")
            except Exception as e:
                log(f"    ✗ 失败: {type(e).__name__}: {e}")
                log(traceback.format_exc()[-600:])
                try:
                    pg.screenshot(path=str(HERE / "notes" / f"hub_fail_{n}.png"))
                    log(f"    截图 notes/hub_fail_{n}.png")
                except Exception:
                    pass
                break
        b.close()
    log(f"=== 结束:本次提交 {made} 个,累计记录 {len(done)} 个 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
