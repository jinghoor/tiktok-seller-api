#!/usr/bin/env python3
"""TikTok 商家中心 GMV Max 广告接口客户端(逆向自 Hub Studio 实抓请求)。

    python3 tiktok_ads.py products                 # 列可投商品
    python3 tiktok_ads.py create --spu <id>        # 创建 1 个(ROI=14,促销日关,预算200)
    python3 tiktok_ads.py batch [--limit N]        # 批量:每个商品建 1 个广告
    python3 tiktok_ads.py created                  # 查已创建的广告计划

依赖会话:notes/tiktok_session.json (由 hub_session.py 从浏览器导出)
"""
from __future__ import annotations
import argparse, json, sys, time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

HERE = Path(__file__).resolve().parent
SESSION = HERE / "notes" / "tiktok_session.json"
TEMPLATE = HERE / "notes" / "tiktok_payload_template.json"
DONE = HERE / "notes" / "tiktok_done.json"
LOG = HERE / "notes" / "tiktok_batch.log"

BASE = "https://seller-vn.tiktok.com"
OEC_SELLER_ID = "7494XXXXXXXXXX00"   # oec_seller_id
AADVID = "7689XXXXXXXXXX74"          # DAMAI-SHOP_LOCAL 广告账户
SHOP_ID = "7494XXXXXXXXXX00"         # ad_info.shop_id (与 oec_seller_id 同值)
SHOP_BC = "7626XXXXXXXXXX75"         # shop_authorized_bc

ROI = "14.0"
BUDGET = "200.00"


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


class TikTokAds:
    def __init__(self, session_path: Path = SESSION):
        if not session_path.exists():
            raise SystemExit(f"缺少会话文件 {session_path};先跑 hub_session.py")
        raw = json.loads(session_path.read_text(encoding="utf-8"))
        self.cookies = {c["name"]: c["value"] for c in raw["cookies"]}
        self.ua = raw.get("ua") or "Mozilla/5.0"
        self.csrf = self.cookies.get("csrftoken", "")
        self.s = requests.Session()
        for c in raw["cookies"]:
            self.s.cookies.set(c["name"], c["value"], domain=c.get("domain", ""),
                               path=c.get("path", "/"))
        self.s.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.ua,
            "Origin": BASE,
            "Referer": f"{BASE}/ads-creation/creation",
            "X-CSRFToken": self.csrf,
        })

    # ---------- 通用 ----------

    def _post(self, path: str, body: Dict[str, Any], params: Dict[str, str],
              timeout: int = 30) -> Dict[str, Any]:
        url = BASE + path
        r = self.s.post(url, params=params, json=body, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        try:
            j = r.json()
        except ValueError:
            raise RuntimeError(f"非 JSON 响应: {r.text[:200]}")
        if j.get("code") not in (0, None):
            raise RuntimeError(f"业务错误 code={j.get('code')} msg={j.get('msg')!r}")
        return j

    def _create_params(self) -> Dict[str, str]:
        return {"locale": "zh", "language": "zh",
                "oec_seller_id": OEC_SELLER_ID, "aadvid": AADVID}

    # ---------- 商品 ----------

    def products(self, page_index: int = 1, page_size: int = 100,
                 sort_field: int = 9, sort_order: int = 0) -> List[Dict[str, Any]]:
        """可投商品列表。exclude_mutex=true 时只返回未被其他计划占用的。"""
        body = {"page_info": {"page_index": page_index, "page_size": page_size},
                "sort_param": {"sort_field": sort_field, "sort_order": sort_order},
                "spu_scope": 1, "title": "", "spu_ids": [], "sku_ids": [], "mutex_scene": 2}
        # org_id 必填 —— 少了会报 code=3 "没有使用当前店铺商品投放的权限"(实测踩过)
        params = {**self._create_params(), "exclude_mutex": "true",
                  "new_product_only": "false", "org_id": SHOP_BC}
        j = self._post("/oec_ads/shopping/v1/creation/search_spu", body, params)
        return (((j.get("data") or {}).get("spu_infos")) or [])

    @staticmethod
    def spu_id(item: Dict[str, Any]) -> str:
        return str(((item.get("spu") or {}).get("spu_id")) or "")

    @staticmethod
    def title_of(item: Dict[str, Any]) -> str:
        spu = item.get("spu") or {}
        return str(spu.get("title") or spu.get("spu_title") or "")[:60]

    # ---------- 建广告 ----------

    def build_payload(self, spu_id: str, *, campaign_name: str = "",
                      start_time: Optional[str] = None, now: Optional[datetime] = None) -> Dict[str, Any]:
        tpl = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        now = now or datetime.now()
        st = start_time or now.strftime("%Y-%m-%d %H:%M:%S")
        stamp = now.strftime("%Y%m%d%H%M%S")
        tpl["campaign_info"]["campaign_name"] = campaign_name or f"商品 GMV Max_总收入_Kira Skincare_{stamp}"
        tpl["ad_info"]["name"] = f"广告组_Kira Skincare_{st}"
        tpl["ad_info"]["start_time"] = st
        tpl["ad_info"]["product_list"] = [{"spu_id": str(spu_id)}]
        # 硬性要求(即使模板已符合也再钉一次)
        tpl["ad_info"]["roas_bid"] = ROI
        tpl["ad_info"]["budget"] = BUDGET
        tpl["ad_info"]["budget_mode"] = 0
        tpl["campaign_info"]["budget"] = BUDGET
        tpl["campaign_info"]["budget_mode"] = 0
        tpl["ad_info"]["promotion_days_setting"]["is_enable"] = False
        tpl["ad_info"]["promotion_days_setting"]["benchmark_roas_bid"] = float(ROI)
        return tpl

    def create(self, spu_id: str, **kw) -> Dict[str, Any]:
        payload = self.build_payload(spu_id, **kw)
        j = self._post("/oec_ads/shopping/v1/creation/all_ad_data/create",
                       payload, self._create_params(), timeout=60)
        return j.get("data") or {}

    def check_mutex(self, spu_ids: List[str]) -> Dict[str, Any]:
        """建之前查互斥(同一商品不能同时有多个 GMV Max)。"""
        j = self._post("/oec_ads/shopping/v1/roi2/mutex_roi1/query",
                       {"mutex_asset_ids": [str(i) for i in spu_ids],
                        "mutex_asset_id_type": 101}, {})
        return j.get("data") or {}


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


def cmd_products(c: TikTokAds, a) -> int:
    items = c.products(page_size=100)
    print(f"可投商品(未占用): {len(items)}")
    for it in items:
        print(f"  {c.spu_id(it):22} {c.title_of(it)}")
    return 0


def cmd_create(c: TikTokAds, a) -> int:
    print(f"创建前互斥检查 {a.spu} …")
    try:
        print(f"  mutex: {json.dumps(c.check_mutex([a.spu]), ensure_ascii=False)[:200]}")
    except Exception as e:
        print(f"  mutex 查询失败(继续): {e}")
    st = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"提交 spu={a.spu}  start_time={st}  ROI={ROI}  促销日=关  预算={BUDGET}")
    if a.dry:
        print("  [dry] 不提交")
        return 0
    d = c.create(a.spu, start_time=st)
    print(f"  ✓ campaign_id={d.get('campaign_id')}  ad_id={d.get('ad_id')}")
    done = load_done(); done.add(str(a.spu)); save_done(done)
    return 0


def cmd_batch(c: TikTokAds, a) -> int:
    done = load_done()
    log(f"=== 批量开始  已完成 {len(done)} ===")
    items = c.products(page_size=100)
    todo = [c.spu_id(i) for i in items if c.spu_id(i) and c.spu_id(i) not in done]
    log(f"可投 {len(items)} 个,待做 {len(todo)} 个")
    if a.limit:
        todo = todo[:a.limit]
    made = 0
    for i, spu in enumerate(todo, 1):
        try:
            st = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            d = c.create(spu, start_time=st)
            cid, aid = d.get("campaign_id"), d.get("ad_id")
            log(f"  [{i}/{len(todo)}] ✓ spu={spu}  campaign={cid}  ad={aid}")
            done.add(spu); save_done(done); made += 1
            time.sleep(a.sleep)
        except Exception as e:
            log(f"  [{i}/{len(todo)}] ✗ spu={spu} 失败: {type(e).__name__}: {str(e)[:160]}")
            if not a.keep_going:
                break
    log(f"=== 批量结束:本次 {made} 个,累计 {len(done)} ===")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("products").set_defaults(func=cmd_products)
    p1 = sub.add_parser("create")
    p1.add_argument("--spu", required=True)
    p1.add_argument("--dry", action="store_true")
    p1.set_defaults(func=cmd_create)
    p2 = sub.add_parser("batch")
    p2.add_argument("--limit", type=int, default=0)
    p2.add_argument("--sleep", type=float, default=2.0)
    p2.add_argument("--keep-going", action="store_true")
    p2.set_defaults(func=cmd_batch)
    a = ap.parse_args()
    c = TikTokAds()
    return a.func(c, a)


if __name__ == "__main__":
    raise SystemExit(main())
