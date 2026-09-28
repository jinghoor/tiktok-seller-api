#!/usr/bin/env python3
"""SHOP_XBORDER（ExampleShop 跨境店）GMV Max 广告批量创建 —— 纯 API。

与 tiktok_ads.py 的差异（账户/域名不同，不能混用）：
  · 后台域      seller.tiktokshopglobalselling.com（跨境店，非 seller-vn）
  · 商品 API 域 api16-normal-sg.tiktokshopglobalselling.com（aid=6556）
  · oec_seller_id / shop_id      7494XXXXXXXXXX00
  · aadvid                       7689XXXXXXXXXX09
  · org_id (shop_authorized_bc)  7385XXXXXXXXXX92   ← Hello House3
  · ROI 20.0（SHOP_LOCAL 那套是 14.0）

固定的广告参数（按需求）：
  · 每个 GMV Max 只放 1 个商品（product_list 长度恒为 1）
  · 广告日（促销日）关闭：promotion_days_setting.is_enable = false
  · 无结束时间：schedule_type = 1（持续投放）
  · 预算 200.00 美元，budget_mode = 0（日预算）
  · 广告名 = 产品中文简称-主SKU-product_id

用法:
  python3 tk01_ads.py products                 # 列出有销量的可供商品
  python3 tk01_ads.py names                    # 打印将使用的广告名（干跑）
  python3 tk01_ads.py create --spu <id> --name <广告名> --dry
  python3 tk01_ads.py create --spu <id> --name <广告名>
  python3 tk01_ads.py batch [--limit N] [--sleep 5]
  python3 tk01_ads.py created                  # 查看已建广告
依赖: notes/tiktok_session_tk01.json（hub_session2.py 导出）
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
SESSION = HERE / "notes" / "tiktok_session_tk01.json"
TEMPLATE = HERE / "notes" / "tiktok_payload_template.json"
DONE = HERE / "notes" / "tk01_done.json"
LOG = HERE / "notes" / "tk01_batch.log"
TODO = HERE / "notes" / "tk01_todo.json"

SITE = "https://seller.tiktokshopglobalselling.com"
API = "https://api16-normal-sg.tiktokshopglobalselling.com"

OEC_SELLER_ID = "7494XXXXXXXXXX00"
AADVID = "7689XXXXXXXXXX09"
SHOP_ID = "7494XXXXXXXXXX00"
SHOP_BC = "7385XXXXXXXXXX92"

ROI = "20.0"
BUDGET = "200.00"
# 实测：只有 2 和 5 能过"购物广告类型"校验；2 报"推广目标有误"，故取 5
PROMOTION_FLOW_TYPE = 5
# adjusted_roas_bid = roas_bid * (roas_bid_multiplier/100)。multiplier=90 → ×0.9
ROAS_BID_MULTIPLIER = 90
def _adjusted(roi: str) -> str:
    return f"{float(roi) * ROAS_BID_MULTIPLIER / 100:.1f}"
ADJUSTED_ROI = _adjusted(ROI)
# create 在页面环境才返回精确错误码；直连只回通用错误
ERR_MUTEX = "product_roi2_mutex_error"
ERR_NOT_LEGAL = "spu_id_not_legal_error"


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


class TK01Ads:
    def __init__(self, session_path: Path = SESSION):
        if not session_path.exists():
            raise SystemExit(f"缺少会话 {session_path}；先跑 hub_session2.py <port> {session_path}")
        raw = json.loads(session_path.read_text(encoding="utf-8"))
        self.cookies = {c["name"]: c["value"] for c in raw["cookies"]}
        self.ua = raw.get("ua") or "Mozilla/5.0"
        self.s = requests.Session()
        for c in raw["cookies"]:
            self.s.cookies.set(c["name"], c["value"],
                               domain=c.get("domain", ""), path=c.get("path", "/"))
        self.s.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.ua,
            "Origin": SITE,
            "Referer": f"{SITE}/ads-creation/creation",
            "X-CSRFToken": self.cookies.get("csrftoken", ""),
        })

    # ---------- 通用 ----------

    # 两个域的用途不同（实测）：
    #   API  (api16-normal-sg...)  → 商家中心的商品类接口
    #   SITE (seller...globalselling.com) → 广告后台接口，创建必须走这里
    def _post(self, path: str, body: dict, params: dict, timeout: int = 60,
              host: str = SITE) -> dict:
        r = self.s.post(host + path, params=params, json=body, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        try:
            j = r.json()
        except ValueError:
            raise RuntimeError(f"非 JSON: {r.text[:160]}")
        if j.get("code") not in (0, None):
            raise RuntimeError(f"业务错误 code={j.get('code')} msg={j.get('msg') or j.get('message')!r}")
        return j

    def _params(self) -> dict:
        return {"locale": "zh", "language": "zh",
                "oec_seller_id": OEC_SELLER_ID, "aadvid": AADVID}

    # ---------- 商品 ----------

    def products(self, page_index: int = 1, page_size: int = 50) -> list[dict]:
        body = {"page_info": {"page_index": page_index, "page_size": page_size},
                "sort_param": {"sort_field": 9, "sort_order": 0},
                "spu_scope": 1, "title": "", "spu_ids": [], "sku_ids": [], "mutex_scene": 2}
        p = {**self._params(), "exclude_mutex": "true",
             "new_product_only": "false", "org_id": SHOP_BC}
        j = self._post("/oec_ads/shopping/v1/creation/search_spu", body, p, host=API)
        return ((j.get("data") or {}).get("spu_infos")) or []

    def check_mutex(self, spu_ids: list[str]) -> dict:
        j = self._post("/oec_ads/shopping/v1/roi2/mutex_roi1/query",
                       {"mutex_asset_ids": [str(i) for i in spu_ids],
                        "mutex_ad_object_type": "", "mutex_asset_id_type": 101},
                       self._params(), timeout=30)
        return j.get("data") or {}

    # ---------- payload ----------

    def build_payload(self, spu_id: str, campaign_name: str, *,
                      start_time: str | None = None) -> dict:
        """按需求钉死全部参数。

        与 SHOP_LOCAL 版的区别：ROI=20.0，且把 ROI 关联的三个字段一起对齐，
        避免出现「主 ROI 20、基准 ROI 14」这种不一致的中间态。
        """
        tpl = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        st = start_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tpl["campaign_info"]["campaign_name"] = campaign_name
        tpl["ad_info"]["name"] = campaign_name
        tpl["ad_info"]["start_time"] = st           # 缺它会报 0000-00-00 datetime
        tpl["ad_info"]["product_list"] = [{"spu_id": str(spu_id)}]   # 恒 1 个商品

        # ROI = 20
        # 关键：adjusted_roas_bid 不能等于 roas_bid，否则服务端报
        #   i18n_key = promotion_days_v2_adjusted_roas_bid_not_equal
        #   （HTTP 200 + code=3「出现错误，请重试。」，直连时完全看不出来）
        # 实测 20 → adjusted_roas_bid 必须是 "18.0"（= 20 * 0.9，即 roas_bid_multiplier/100）
        tpl["ad_info"]["roas_bid"] = ROI
        tpl["ad_info"]["promotion_days_setting"]["benchmark_roas_bid"] = int(float(ROI))
        tpl["ad_info"]["promotion_days_setting"]["adjusted_roas_bid"] = ADJUSTED_ROI

        # 广告日关闭
        tpl["ad_info"]["promotion_days_setting"]["is_enable"] = False

        # 预算 200 / 日预算 / 无结束时间
        tpl["ad_info"]["budget"] = BUDGET
        tpl["ad_info"]["budget_mode"] = 0
        tpl["campaign_info"]["budget"] = BUDGET
        tpl["campaign_info"]["budget_mode"] = 0
        tpl["ad_info"]["schedule_type"] = 1
        tpl.pop("ad_info.schedule_end_time", None)

        # 店铺/账户
        tpl["ad_info"]["shop_id"] = SHOP_ID
        tpl["ad_info"]["shop_authorized_bc"] = SHOP_BC
        return tpl

    def create(self, spu_id: str, campaign_name: str, *, start_time: str | None = None) -> dict:
        """创建 GMV Max 广告。

        ⚠ 直连（Python）调 create 时服务端只回通用「出现错误，请重试」，
        拿不到真实原因。**页面环境**（浏览器内 fetch）才会返回精确错误码：
          · product_roi2_mutex_error  商品已被 GMV Max/购物广告占用
          · spu_id_not_legal_error    该商品不具备投放资格
        所以排障/批量判定资格请用 PageSession.create()。
        """
        payload = self.build_payload(spu_id, campaign_name, start_time=start_time)
        j = self._post("/oec_ads/shopping/v1/creation/all_ad_data/create",
                       payload, self._params(), timeout=90)
        return j.get("data") or {}

    def build_payload_for(self, t: dict, *, start_time: str | None = None) -> dict:
        """按清单条目构造 payload，并钉上 SHOP_XBORDER 实测正确的 promotion_flow_type。"""
        p = self.build_payload(t["product_id"], t["ad_name"], start_time=start_time)
        p["ad_info"]["promotion_flow_type"] = PROMOTION_FLOW_TYPE
        return p


# ---------- 状态 ----------

def load_done() -> set:
    if DONE.exists():
        try:
            return set(json.loads(DONE.read_text()))
        except Exception:
            return set()
    return set()


def save_done(s: set) -> None:
    DONE.parent.mkdir(parents=True, exist_ok=True)
    DONE.write_text(json.dumps(sorted(s), indent=1))


def load_todo() -> list[dict]:
    if not TODO.exists():
        raise SystemExit(f"缺少 {TODO}；先跑选品/翻译")
    return json.loads(TODO.read_text(encoding="utf-8"))


# ---------- 命令 ----------

def cmd_names(c: TK01Ads, a) -> int:
    todo = load_todo()
    done = load_done()
    todo = [t for t in todo if t["product_id"] not in done]
    print(f"待建广告 {len(todo)} 条（已完成 {len(done)}）\n")
    for i, t in enumerate(todo, 1):
        print(f"{i:3}. {t['ad_name']}")
        print(f"     销量={t['sales']}  类目={t['cat']}")
    print(f"\n合计 {len(todo)} 条")
    return 0


def cmd_products(c: TK01Ads, a) -> int:
    items = c.products(page_size=100)
    print(f"可投商品（未被占用）: {len(items)}")
    for it in items[:40]:
        s = it.get("spu") or {}
        print(f"  {s.get('spu_id')}  sales={s.get('total_sales')}  {(s.get('title') or '')[:52]}")
    return 0


def cmd_create(c: TK01Ads, a) -> int:
    todo = {t["product_id"]: t for t in load_todo()}
    name = a.name
    if not name:
        t = todo.get(str(a.spu))
        if not t:
            print(f"! {a.spu} 不在待建清单里，必须显式 --name")
        else:
            name = t["ad_name"]
    print(f"spu={a.spu}\n广告名={name}\nROI={ROI} 预算={BUDGET} 广告日=关 结束时间=无")
    if a.dry:
        p = c.build_payload(str(a.spu), name or "dry_run")
        print("\n[dry] payload 关键字段:")
        for k in ("campaign_name",):
            print(f"  campaign_info.{k} = {p['campaign_info'][k]}")
        for k in ("name", "roas_bid", "budget", "budget_mode", "schedule_type",
                  "start_time", "shop_id", "shop_authorized_bc", "product_list"):
            print(f"  ad_info.{k} = {json.dumps(p['ad_info'][k], ensure_ascii=False)}")
        pd = p["ad_info"]["promotion_days_setting"]
        print(f"  promotion_days_setting.is_enable = {pd['is_enable']}")
        print(f"  promotion_days_setting.benchmark_roas_bid = {pd['benchmark_roas_bid']}")
        print(f"  promotion_days_setting.adjusted_roas_bid = {pd['adjusted_roas_bid']}")
        return 0
    d = c.create(str(a.spu), name or "无名称")
    print(f"  ✓ campaign_id={d.get('campaign_id')}  ad_id={d.get('ad_id')}")
    done = load_done()
    done.add(str(a.spu))
    save_done(done)
    return 0


def cmd_batch(c: TK01Ads, a) -> int:
    todo = load_todo()
    done = load_done()
    pend = [t for t in todo if t["product_id"] not in done]
    if a.limit:
        pend = pend[:a.limit]
    log(f"=== SHOP_XBORDER 批量开始: 待建 {len(pend)} 条 (已完成 {len(done)}) ROI={ROI} 广告日=关 ===")
    made = 0
    for i, t in enumerate(pend, 1):
        try:
            d = c.create(t["product_id"], t["ad_name"])
            log(f"  [{i}/{len(pend)}] ✓ {t['ad_name']}  campaign={d.get('campaign_id')} ad={d.get('ad_id')}")
            done.add(t["product_id"])
            save_done(done)
            made += 1
        except Exception as e:
            log(f"  [{i}/{len(pend)}] ✗ {t['ad_name']} 失败: {type(e).__name__}: {str(e)[:150]}")
            if not a.keep_going:
                break
        time.sleep(a.sleep)
    log(f"=== 结束: 本次 {made} 条，累计 {len(done)} ===")
    return 0


def cmd_created(c: TK01Ads, a) -> int:
    """已建广告计划列表（走 dashboard 的统计接口）。"""
    r = c.s.post(SITE + "/oec_ads/shopping/v1/oec/stat/post_campaign_list",
                 params={"aadvid": AADVID, "language": "zh", "locale": "zh",
                         "oec_seller_id": OEC_SELLER_ID},
                 json={"page": 1, "page_size": 50, "campaign_type": [], "order_field": 1,
                       "order_type": 0, "search_key": ""}, timeout=60)
    j = r.json()
    data = j.get("data") or {}
    lst = data.get("campaign_list") or data.get("list") or []
    print(f"code={j.get('code')} 计划数={len(lst)}")
    for x in lst[:40]:
        print(f"  {x.get('campaign_id')}  {x.get('campaign_name')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("products").set_defaults(func=cmd_products)
    sub.add_parser("names").set_defaults(func=cmd_names)
    sub.add_parser("created").set_defaults(func=cmd_created)
    p1 = sub.add_parser("create")
    p1.add_argument("--spu", required=True)
    p1.add_argument("--name", default="")
    p1.add_argument("--dry", action="store_true")
    p1.set_defaults(func=cmd_create)
    p2 = sub.add_parser("batch")
    p2.add_argument("--limit", type=int, default=0)
    p2.add_argument("--sleep", type=float, default=5.0)
    p2.add_argument("--keep-going", action="store_true", default=True)
    p2.set_defaults(func=cmd_batch)
    a = ap.parse_args()
    return a.func(TK01Ads(), a)


if __name__ == "__main__":
    raise SystemExit(main())


# ─────────────────── 页面环境会话（推荐用于 create） ───────────────────
# 为什么必须走页面：
#   1. 页面同域同 cookie，最接近真实调用；
#   2. create 的 query 里页面会带 msToken / _signature / X-Bogus（可空，但环境一致）；
#   3. **关键**：直连只回「出现错误，请重试」，页面环境才回 product_roi2_mutex_error /
#      spu_id_not_legal_error，排障和资格判定都靠它。
class PageSession:
    def __init__(self, port: int = CDP_PORT, timeout: float = 300.0):
        import urllib.request as _u
        from hub_headless import CDPPage
        tabs = json.loads(_u.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=8).read())
        page = next((x for x in tabs if x.get("type") == "page" and "seller" in (x.get("url") or "")), None)
        if page is None:
            raise RuntimeError(f"端口 {port} 上没有卖家中心页面")
        self.pg = CDPPage(page["webSocketDebuggerUrl"], timeout=timeout)
        self.pg.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
        self.timeout = timeout

    def close(self):
        try: self.pg.close()
        except Exception: pass

    def _run(self, path: str, payloads: list[dict], *, method: str = "POST",
             gap: float = 2.0, per_timeout: int = 70) -> list[dict]:
        """在页面里批量发请求，返回每条的原始响应文本。"""
        js = """(async()=>{
  const S='%(seller)s', A='%(adv)s';
  const m=document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]*)/);
  const h={'content-type':'application/json; charset=utf-8',
           'accept':'application/json, text/plain, */*'};
  if(m) h['x-csrftoken']=decodeURIComponent(m[1]);
  const q=`aadvid=${A}&oec_seller_id=${S}&locale=zh&language=zh`;
  const arr=%(arr)s; const out=[];
  for (const it of arr){
    const ac=new AbortController(); const t=setTimeout(()=>ac.abort(),%(pt)d);
    try{
      const r=await fetch(%(path)s+'?'+q,{method:'%(method)s',headers:h,
        credentials:'include',signal:ac.signal,body:JSON.stringify(it)});
      out.push({ok:true, resp:(await r.text()).slice(0,600)});
    }catch(e){ out.push({ok:false, resp:'ERR '+e.name}); }
    finally{ clearTimeout(t); }
    await new Promise(r=>setTimeout(r, %(gap)d));
  }
  return JSON.stringify(out);
})()""" % {"seller": OEC_SELLER_ID, "adv": AADVID, "arr": json.dumps(payloads, ensure_ascii=False),
           "path": json.dumps(path), "method": method, "pt": per_timeout, "gap": int(gap * 1000)}
        raw = self.pg.js(js, await_promise=True, timeout=self.timeout)
        out = json.loads(raw or "[]")
        res = []
        for o in out:
            txt = o.get("resp", "")
            try:
                j = json.loads(txt)
            except Exception:
                j = None
            res.append({"json": j, "text": txt})
        return res

    @staticmethod
    def classify(text: str) -> str:
        if '"code":0' in text: return "OK"
        if ERR_MUTEX in text or "mutex" in text: return "MUTEX"
        if ERR_NOT_LEGAL in text or "不可用" in text: return "NOT_LEGAL"
        return "OTHER"

    def qualify(self, todos: list[dict], c: "TK01Ads", *, batch: int = 10) -> dict:
        """用 create 判定资格（会短暂占位，但这是唯一准确的判据）。"""
        from tk01_ads import TK01Ads as _T
        out = {}
        for i in range(0, len(todos), batch):
            chunk = todos[i:i+batch]
            pls = [c.build_payload_for(t) for t in chunk]
            for t, r in zip(chunk, self._run("/oec_ads/shopping/v1/creation/all_ad_data/create", pls)):
                out[t["product_id"]] = {"kind": self.classify(r["text"]), "text": r["text"][:200],
                                        "name": t["ad_name"]}
        return out

    # ── 只读预检：官方 validate_product_list ──
    # 这是**唯一无副作用的资格判定**（对比：create 失败也占位，check 只验形状）
    # 响应：{"validation_result":[{"spu_id","is_valid","invalid_reason_code"}]}
    #   invalid_reason_code 1 = 商品不具备投放资格（实测对应 spu_id_not_legal_error）
    #   invalid_reason_code 3 = 被互斥占用（实测对应 product_roi2_mutex_error）
    #   is_valid=true 才值得发 create
    REASON = {1: "NOT_LEGAL", 3: "MUTEX"}

    def validate_batch(self, pids: list[str], *, batch: int = 25) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i in range(0, len(pids), batch):
            chunk = [str(x) for x in pids[i:i + batch]]
            js = """(async()=>{
  const S='%(seller)s', A='%(adv)s', ORG='%(org)s';
  const m=document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]*)/);
  const h={'content-type':'application/json','accept':'application/json, text/plain, */*'};
  if(m) h['x-csrftoken']=decodeURIComponent(m[1]);
  const q=`is_new_product_mode=false&aadvid=${A}&org_id=${ORG}&oec_seller_id=${S}&locale=zh&language=zh`;
  try{
    const r=await fetch('/oec_ads/shopping/v1/creation/validate_product_list?'+q,
      {method:'POST',headers:h,credentials:'include',
       body:JSON.stringify({spu_scope:1, mutex_scene:2, spu_ids:%(ids)s, sku_ids:[]})});
    return JSON.stringify(((await r.json()).data||{}).validation_result||[]);
  }catch(e){ return '[]'; }
})()""" % {"seller": OEC_SELLER_ID, "adv": AADVID, "org": SHOP_BC,
           "ids": json.dumps(chunk)}
            raw = self.pg.js(js, await_promise=True, timeout=self.timeout)
            for r in json.loads(raw or "[]"):
                code = r.get("invalid_reason_code")
                out[str(r.get("spu_id"))] = {
                    "valid": bool(r.get("is_valid")),
                    "reason": self.REASON.get(code, str(code) if code else "OK"),
                }
        return out

    def valid_only(self, todos: list[dict]) -> tuple[list[dict], dict]:
        """筛出真正可投的条目，返回 (可投列表, 剔除明细)。"""
        v = self.validate_batch([t["product_id"] for t in todos])
        keep, drop = [], {}
        for t in todos:
            r = v.get(t["product_id"]) or {}
            if r.get("valid"):
                keep.append(t)
            else:
                drop[t["product_id"]] = r.get("reason", "UNKNOWN")
        return keep, drop

    def create_batch(self, todos: list[dict], c: "TK01Ads", *, batch: int = 8,
                     gap: float = 2.5, on_result=None) -> list[dict]:
        """真正批量创建。逐条记结果，失败不中断。"""
        made = []
        for i in range(0, len(todos), batch):
            chunk = todos[i:i+batch]
            pls = [c.build_payload_for(t) for t in chunk]
            for t, r in zip(chunk, self._run("/oec_ads/shopping/v1/creation/all_ad_data/create",
                                             pls, gap=gap)):
                j = r["json"] or {}
                d = (j.get("data") or {}) if isinstance(j, dict) else {}
                rec = {"product_id": t["product_id"], "ad_name": t["ad_name"],
                       "kind": self.classify(r["text"]),
                       "campaign_id": d.get("campaign_id"), "ad_id": d.get("ad_id"),
                       "text": r["text"][:200]}
                made.append(rec)
                if on_result: on_result(rec)
        return made
