#!/usr/bin/env python3
"""SHOP_XBORDER 批量创建 GMV Max —— 等占用释放后自动跑全量。

背景（实测确认）：
  · payload 结构正确 —— all_ad_data/check 对同一 payload 返回 code:0
    （响应体是 fake_campaign_id/fake_ad_id，说明它只做形状校验）
  · create 的失败原因**不是** payload，而是商品的互斥占用：
      product_roi2_mutex_error  商品已被 GMV Max/视频购物广告占用
      spu_id_not_legal_error    商品不具备投放资格
  · create 只有**页面环境**才返回上述精确错误码；Python 直连只回
    「出现错误，请重试」，无法排障
  · 试建请求会在写库前先占位，失败不回滚 —— 这是本轮把大量商品
    打上占用的原因（会自动释放，但释放是分批的、要等）

所以本脚本：轮询可用商品数 → 达到阈值后按清单批量创建 → 逐条记录结果。

用法:
  python3 tk01_run.py --watch            # 只观察占用释放进度
  python3 tk01_run.py --wait 100         # 等到可用≥100 再开跑
  python3 tk01_run.py --go               # 立刻开跑（不等待）
  python3 tk01_run.py --verify <pid>     # 单条验证
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_ads import TK01Ads, PageSession, SITE  # noqa: E402

TODO = HERE / "notes" / "tk01_todo.json"
DONE = HERE / "notes" / "tk01_done.json"
LOG = HERE / "notes" / "tk01_run.log"

ORG = "7385XXXXXXXXXX92"


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
    DONE.write_text(json.dumps(sorted(s), indent=1))


class Session:
    """统一的页面环境请求器（精确错误码只在这里拿得到）。"""

    def __init__(self, port: int = CDP_PORT):
        self.ps = PageSession(port=port)

    def close(self):
        self.ps.close()

    def _js_prelude(self) -> str:
        return """
  const S='7494XXXXXXXXXX00', A='7689XXXXXXXXXX09', ORG='%s';
  const m=document.cookie.match(/(?:^|;\\\\s*)csrftoken=([^;]*)/);
  const h={'content-type':'application/json','accept':'application/json, text/plain, */*'};
  if(m) h['x-csrftoken']=decodeURIComponent(m[1]);
  const base=`aadvid=${A}&oec_seller_id=${S}&locale=zh&language=zh`;
""" % ORG

    def claimed(self) -> list | str:
        js = "(async()=>{" + self._js_prelude() + """
  try{
    const r=await fetch('/oec_ads/shopping/v1/creation/shop_claimed_products?'+base+'&org_id='+ORG,
      {method:'POST',headers:h,credentials:'include',body:'{}'});
    return JSON.stringify(((await r.json()).data||{}).claimed_product_list||[]);
  }catch(e){return JSON.stringify('ERR '+e.name);}
})()"""
        out = self.ps.pg.js(js, await_promise=True, timeout=120)
        try:
            return json.loads(out)
        except Exception:
            return out or "?"

    def available(self, exclude_mutex: str = "true") -> int:
        js = "(async()=>{" + self._js_prelude() + """
  let n=0;
  for(let p=1;p<=8;p++){
    const q=base+'&org_id='+ORG+'&exclude_mutex=%s&new_product_only=false';
    const r=await fetch('/oec_ads/shopping/v1/creation/search_spu?'+q,
      {method:'POST',headers:h,credentials:'include',
       body:JSON.stringify({page_info:{page_index:p,page_size:50},
         sort_param:{sort_field:9,sort_order:0},spu_scope:1,title:'',
         spu_ids:[],sku_ids:[],mutex_scene:2})});
    const j=await r.json(); const infos=((j.data||{}).spu_infos)||[];
    if(!infos.length) break; n+=infos.length; if(infos.length<50) break;
    await new Promise(r=>setTimeout(r,250));
  }
  return String(n);
})()""" % exclude_mutex
        out = self.ps.pg.js(js, await_promise=True, timeout=180)
        try:
            return int(out)
        except Exception:
            return -1

    # ── 页面健康检查 ──
    # 踩坑：提报过程中页面可能被导航走（本店实测跳到了 /ads-creation/dashboard），
    # 之后 Runtime.evaluate 就报 "Execution context was destroyed."，
    # 整批任务中断。所以在每批之前确认页面还在创建页。
    CREATE_URL = "https://seller.tiktokshopglobalselling.com/ads-creation/creation?mpa=1"

    def ensure_page(self, *, retries: int = 3) -> bool:
        for i in range(retries):
            try:
                url = self.ps.pg.js("location.href") or ""
                if "/ads-creation/creation" in url:
                    return True
                log(f"    页面在 {url[-50:]}，导航回创建页…")
                self.ps.pg.send("Page.navigate", {"url": self.CREATE_URL})
                for _ in range(15):
                    time.sleep(2)
                    try:
                        if (self.ps.pg.js("document.body.innerText.length") or 0) > 500:
                            return True
                    except Exception:
                        pass
            except Exception as e:
                log(f"    页面检查失败({i+1}): {str(e)[:60]}")
                time.sleep(3)
        return False

    def create_many(self, items: list[dict], c: TK01Ads, *, gap: float = 2.5) -> list[dict]:
        """一次页面调用批量创建（逐个 fetch，带间隔）。"""
        pls = [c.build_payload_for(t) for t in items]
        js = "(async()=>{" + self._js_prelude() + """
  const arr=%(arr)s; const out=[]; const path='/oec_ads/shopping/v1/creation/all_ad_data/create';
  for (const it of arr){
    const ac=new AbortController(); const t=setTimeout(()=>ac.abort(),70000);
    try{
      const r=await fetch(path+'?'+base,{method:'POST',headers:h,credentials:'include',
        signal:ac.signal,body:JSON.stringify(it)});
      out.push({resp:(await r.text()).slice(0,500)});
    }catch(e){ out.push({resp:'ERR '+e.name}); }
    finally{ clearTimeout(t); }
    await new Promise(r=>setTimeout(r,%(gap)d));
  }
  return JSON.stringify(out);
})()""" % {"arr": json.dumps(pls, ensure_ascii=False), "gap": int(gap * 1000)}
        if not self.ensure_page():
            log("    ⚠ 页面无法恢复，本批跳过")
            return [{"product_id": t["product_id"], "ad_name": t["ad_name"],
                     "kind": "OTHER", "campaign_id": None, "ad_id": None,
                     "text": "PAGE_LOST"} for t in items]
        try:
            raw = self.ps.pg.js(js, await_promise=True, timeout=self.ps.timeout)
        except Exception as e:
            log(f"    ⚠ 本批执行失败: {str(e)[:70]}；恢复页面后重试")
            if not self.ensure_page():
                return [{"product_id": t["product_id"], "ad_name": t["ad_name"],
                         "kind": "OTHER", "campaign_id": None, "ad_id": None,
                         "text": "PAGE_LOST"} for t in items]
            time.sleep(3)
            raw = self.ps.pg.js(js, await_promise=True, timeout=self.ps.timeout)
        outs = json.loads(raw or "[]")
        res = []
        for t, o in zip(items, outs):
            txt = o.get("resp", "")
            try:
                j = json.loads(txt)
            except Exception:
                j = None
            d = (j.get("data") or {}) if isinstance(j, dict) else {}
            res.append({"product_id": t["product_id"], "ad_name": t["ad_name"],
                        "kind": PageSession.classify(txt),
                        "campaign_id": d.get("campaign_id"), "ad_id": d.get("ad_id"),
                        "text": txt[:220]})
        return res


def cmd_watch(s: Session, a) -> int:
    log("=== 观察占用释放 ===")
    for i in range(a.rounds):
        cl = s.claimed()
        av = s.available("true")
        log(f"  认领={len(cl) if isinstance(cl, list) else cl}  可用={av}")
        if a.wait and av >= a.wait:
            log(f"✅ 可用达到 {av} ≥ {a.wait}，可以开跑")
            return 0
        if i < a.rounds - 1:
            time.sleep(a.interval)
    return 0


def cmd_run(s: Session, a) -> int:
    todo = json.loads(TODO.read_text(encoding="utf-8"))
    done = load_done()
    pend = [t for t in todo if t["product_id"] not in done]
    log(f"=== SHOP_XBORDER 批量创建开始 ===")
    log(f"清单 {len(todo)} 条，已完成 {len(done)}，待建 {len(pend)}")

    if a.wait:
        for i in range(a.wait_rounds):
            av = s.available("true")
            log(f"  等待占用释放… 可用={av}（目标 {a.wait}）")
            if av >= a.wait:
                break
            time.sleep(a.interval)
    if a.limit:
        pend = pend[:a.limit]

    c = TK01Ads()

    # ① 只读预检：先砍掉下架/已删除等永久不可投商品
    #    为什么不直接 create：create 失败也占位（会把商品打到 mutex），
    #    而 validate 无副作用。这一步能把无效请求从 82/152 降到 0。
    if not a.no_validate and pend:
        log(f"预检 {len(pend)} 条…")
        keep, dropped = s.ps.valid_only(pend)
        from collections import Counter
        cnt = Counter(dropped.values())
        log(f"  可投 {len(keep)} / 剔除 {len(dropped)}  {dict(cnt)}")
        if a.drop_out:
            import json as _j
            Path(a.drop_out).write_text(_j.dumps(dropped, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
            log(f"  剔除明细已写 {a.drop_out}")
        pend = keep
        if not pend:
            log("无可投商品，退出")
            return 0

    made = ok = 0
    for i in range(0, len(pend), a.batch):
        chunk = pend[i:i + a.batch]
        res = s.create_many(chunk, c, gap=a.gap)
        for r in res:
            made += 1
            flag = {"OK": "✅", "MUTEX": "⛔", "NOT_LEGAL": "✗", "OTHER": "?"}[r["kind"]]
            log(f"  [{made}/{len(pend)}] {flag} {r['ad_name']}"
                + (f"  campaign={r['campaign_id']}" if r["kind"] == "OK" else f"  {r['text'][:90]}"))
            if r["kind"] == "OK":
                ok += 1
                done.add(r["product_id"]); save_done(done)
        time.sleep(a.pause)
    log(f"=== 结束: 本次成功 {ok}/{made}，累计 {len(done)} ===")
    return 0


def cmd_verify(s: Session, a) -> int:
    todo = {t["product_id"]: t for t in json.loads(TODO.read_text(encoding="utf-8"))}
    t = todo.get(a.verify)
    if not t:
        log(f"! {a.verify} 不在清单里")
        return 1
    c = TK01Ads()
    res = s.create_many([t], c, gap=1)
    r = res[0]
    log(f"verify {a.verify} → kind={r['kind']}")
    log(f"  campaign={r['campaign_id']} ad={r['ad_id']}")
    log(f"  {r['text']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--wait", type=int, default=0, help="等待可用数达到该值")
    ap.add_argument("--rounds", type=int, default=30)
    ap.add_argument("--wait-rounds", type=int, default=30)
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--gap", type=float, default=2.5)
    ap.add_argument("--pause", type=float, default=5.0)
    ap.add_argument("--no-validate", action="store_true", help="跳过预检（不推荐）")
    ap.add_argument("--drop-out", default="notes/tk01_dropped.json",
                    help="被剔除商品的明细输出路径")
    ap.add_argument("--verify", metavar="PID")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    a = ap.parse_args()

    s = Session(a.port)
    try:
        if a.verify: return cmd_verify(s, a)
        if a.watch:  return cmd_watch(s, a)
        if a.go:     return cmd_run(s, a)
        ap.print_help()
        return 0
    finally:
        s.close()


if __name__ == "__main__":
    raise SystemExit(main())
