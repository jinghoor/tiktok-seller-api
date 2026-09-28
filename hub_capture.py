#!/usr/bin/env python3
"""抓 TikTok GMV Max 提报请求:跑一次 UI 创建,记录全部 XHR/fetch。

产出 notes/tiktok_create_api.json —— 含 endpoint / headers / body / 响应。
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else CDP_PORT
SEL_ROI = '[data-testid="bid-select-index-9egWxE"]'
SEL_PROMO = '[data-testid="promotion-days-toggle-3EnDzt"]'
SEL_DRAWER = '[data-testid="product-select-index-6KM6mN"]'

RECORDER = r"""
(() => {
  if (window.__rec) return 'already';
  window.__rec = [];
  const cap = (v, n=200000) => { try { const s = typeof v === 'string' ? v : JSON.stringify(v); 
    return s && s.length > n ? s.slice(0,n)+'…[trunc]' : s; } catch { return '<unserializable>'; } };
  const of = window.fetch;
  window.fetch = async function(...a) {
    const req = a[0], init = a[1] || {};
    const url = typeof req === 'string' ? req : (req && req.url) || '';
    const method = (init.method || (req && req.method) || 'GET').toUpperCase();
    const body = init.body || null;
    const rec = {kind:'fetch', url, method, headers: init.headers ? Object.fromEntries(new Headers(init.headers).entries()) : {}, body: cap(body)};
    try {
      const resp = await of.apply(this, a);
      let t=''; try { t = await resp.clone().text(); } catch(e) {}
      rec.status = resp.status; rec.response = cap(t);
    } catch(e) { rec.error = String(e); }
    window.__rec.push(rec);
    return resp;
  };
  const OX = window.XMLHttpRequest;
  function RX(){
    const x = new OX(); const st = {method:'GET', url:'', headers:{}, body:null};
    const oOpen=x.open, oSend=x.send, oSet=x.setRequestHeader;
    x.open=function(m,u,...r){ st.method=(m||'GET').toUpperCase(); st.url=String(u); return oOpen.call(x,m,u,...r); };
    x.setRequestHeader=function(k,v){ st.headers[k]=v; return oSet.call(x,k,v); };
    x.send=function(b){
      st.body = cap(b);
      x.addEventListener('loadend', () => {
        let r=''; try { r = x.responseType===''||x.responseType==='text' ? x.responseText : '['+x.responseType+']'; } catch(e){}
        window.__rec.push({kind:'xhr', url:new URL(st.url, location.origin).href, method:st.method,
          headers:st.headers, body:st.body, status:x.status, response:cap(r)});
      });
      return oSend.call(x,b);
    };
    return x;
  }
  RX.prototype = OX.prototype;
  window.XMLHttpRequest = RX;
  return 'installed';
})()
"""


def run() -> int:
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
        pg = next(x for c in b.contexts for x in c.pages if "ads-creation" in x.url)

        # 回 dashboard 再进创建页,确保干净状态
        pg.goto("https://seller-vn.tiktok.com/ads-creation/dashboard", wait_until="domcontentloaded")
        pg.wait_for_timeout(4000)
        pg.get_by_role("button", name=re.compile("创建 GMV Max 广告")).click(timeout=20000)
        pg.wait_for_timeout(6000)
        print(f"创建页: {pg.url[:90]}")

        # 装记录器(进创建页之后装,这样能抓到提交)
        print("注入记录器:", pg.evaluate(RECORDER))

        # 选定商品
        pg.evaluate("""() => { const r=document.querySelector('input[type=radio][value="specific"]');
            if(r)(r.closest('label')||r.parentElement||r).click(); }""")
        pg.wait_for_timeout(2500)
        pg.get_by_text("添加商品", exact=True).last.click(timeout=15000)
        pg.wait_for_timeout(6000)

        ids = pg.evaluate("""() => {
            const out=[];
            for (const tr of document.querySelectorAll('tr')) {
                const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
                const m=t.match(/ID:\\s*(\\d{15,25})/);
                if (m) out.push(m[1]);
            }
            return out;
        }""")
        print(f"可选商品 {len(ids)} 个")
        if not ids: return 1
        target = ids[0]

        pg.evaluate("""(tid) => {
            for (const tr of document.querySelectorAll('tr')) {
                const t=(tr.innerText||'').trim().replace(/\\s+/g,' ');
                const m=t.match(/ID:\\s*(\\d{15,25})/);
                if (!m || m[1] !== tid) continue;
                const cb = tr.querySelector('input[type=checkbox]');
                if (cb && !cb.checked) cb.click();
                return;
            }
        }""", target)
        pg.wait_for_timeout(1500)

        c = pg.get_by_text("确认", exact=True)
        for i in range(c.count()):
            bx = c.nth(i).bounding_box()
            if bx and bx["width"] > 20:
                c.nth(i).click(timeout=15000); break
        pg.wait_for_timeout(4000)

        # ROI + 促销日关
        inp = pg.locator(f"{SEL_ROI} input")
        inp.click(timeout=15000); inp.click(click_count=3)
        pg.keyboard.press("Backspace"); pg.wait_for_timeout(300)
        if inp.input_value().strip():
            for _ in range(12): pg.keyboard.press("Backspace")
        inp.type("14", delay=90); pg.keyboard.press("Tab"); pg.wait_for_timeout(2000)
        sw = pg.locator(SEL_PROMO)
        if sw.get_attribute("aria-checked") == "true":
            sw.click(timeout=10000); pg.wait_for_timeout(2500)

        st = pg.evaluate("""() => {
            const txt=document.body.innerText;
            const m=txt.match(/商品列表\\s*\\(已选择\\s*(\\d+)\\s*件商品\\)/);
            return {roi:(document.querySelector('[data-testid="bid-select-index-9egWxE"]')||{}).getAttribute?.('value'),
                    promo:(document.querySelector('[data-testid="promotion-days-toggle-3EnDzt"]')||{}).getAttribute?.('aria-checked'),
                    selected:m?m[1]:null};
        }""")
        print("提交前:", json.dumps(st, ensure_ascii=False), " 商品:", target)

        # 清空记录器,然后点发布
        pg.evaluate("() => { window.__rec = []; }")
        loc = pg.get_by_text("发布", exact=True)
        for i in range(loc.count()):
            bx = loc.nth(i).bounding_box()
            if bx and bx["width"] > 20:
                loc.nth(i).click(timeout=15000); break
        print("已点发布,收集请求…")
        pg.wait_for_timeout(8000)

        rec = pg.evaluate("() => JSON.stringify(window.__rec || [])")
        data = json.loads(rec) if rec else []
        print(f"\n捕获到 {len(data)} 个请求")
        # 挑出非 GET 的、且 URL 含 ads/creative/gmv 的
        interesting = [r for r in data if r.get("method") not in ("GET", None)
                       and r.get("url") and not re.search(r"(analytics|log|track|beacon|\.gif)", r["url"], re.I)]
        print(f"其中非 GET 业务请求: {len(interesting)}")
        for r in interesting:
            print(f"  {r['method']:5} {r['status']}  {r['url'][:120]}")
            if r.get("body"):
                print(f"        body({len(r['body'])}): {r['body'][:300]}")

        out = HERE / "notes" / "tiktok_create_api.json"
        out.write_text(json.dumps({"target_product": target, "requests": data},
                                  ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n全部请求已存 {out}")
        pg.screenshot(path=str(HERE / "notes" / "hub_capture_after.png"))
        b.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
