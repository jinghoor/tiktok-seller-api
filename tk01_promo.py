#!/usr/bin/env python3
"""TikTok 促销活动 API 客户端（SHOP_XBORDER / ExampleShop 跨境店）。

已实测可用：
  · GET  /api/v1/promotion/config                    折扣限制（幅度/时长）
  · GET  /api/v1/promotion/list_seller_gray_config   灰度开关
  · POST /api/v1/promotion/discount/list             折扣列表
  · POST /api/v1/promotion/voucher/list              券列表（需补参数）
  · POST /api/v1/promotion/mget_item_data            商品数据

待补齐：discount/create 的完整字段（见 TIKTOK_PROMOTION_API.md §8）

认证要点（踩过）：
  ① 促销 API 在 api16-normal-sg.tiktokshopglobalselling.com，主域返回 HTML
  ② 必须用 HttpOnly cookie（sessionid）。document.cookie 取不到，
     要用 CDP Network.getAllCookies → tt_http_client.cookies_via_cdp()

用法:
  python3 tk01_promo.py --config                 # 折扣限制
  python3 tk01_promo.py --gray                   # 灰度开关
  python3 tk01_promo.py --discounts              # 折扣列表
  python3 tk01_promo.py --vouchers               # 券列表
  python3 tk01_promo.py --items <product_id>     # 商品数据
  python3 tk01_promo.py --probe                  # 探测接口可用性
  python3 tk01_promo.py --call <path> [--method M] [--body JSON]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import requests  # noqa: E402
from tt_http_client import cookies_via_cdp  # noqa: E402

HOST = "https://api16-normal-sg.tiktokshopglobalselling.com"
SITE = "https://seller.tiktokshopglobalselling.com"
SELLER = "7494XXXXXXXXXX00"
AID = "6556"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")


class PromoAPI:
    def __init__(self, port: int = CDP_PORT, timeout: float = 30.0):
        # 关键：必须取全量 cookie（含 HttpOnly 的 sessionid），
        # 否则一律返回 {"code":98001002,"message":"请登录后再操作"}
        cookies = cookies_via_cdp(port)
        self.cookies = cookies
        self.timeout = timeout
        self.s = requests.Session()
        for k, v in cookies.items():
            self.s.cookies.set(k, v, domain=".tiktokshopglobalselling.com")
        self.s.headers.update({
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": SITE,
            "referer": f"{SITE}/promotion/marketing-tools/tool-choose",
            "user-agent": UA,
            "x-csrftoken": cookies.get("csrftoken", ""),
        })
        self.P = {"locale": "zh-CN", "language": "zh-CN",
                  "oec_seller_id": SELLER, "seller_id": SELLER,
                  "aid": AID, "app_name": "i18n_ecom_shop"}

    def call(self, path: str, body=None, method: str = "POST", params=None):
        url = HOST + path
        p = {**self.P, **(params or {})}
        if method.upper() == "GET":
            r = self.s.get(url, params=p, timeout=self.timeout)
        else:
            r = self.s.request(method.upper(), url, params=p,
                               json=body if body is not None else {},
                               timeout=self.timeout)
        t = r.text
        if not t.lstrip().startswith(("{", "[")):
            return {"_http": r.status_code, "_raw": t[:300],
                    "_hint": "非 JSON —— 检查路径/域是否正确"}
        try:
            return r.json()
        except Exception:
            return {"_http": r.status_code, "_raw": t[:300]}

    # ---- 已实测可用 ----

    def config(self):
        """折扣限制：幅度、最短/最长时长"""
        return self.call("/api/v1/promotion/config", method="GET")

    def gray(self):
        return self.call("/api/v1/promotion/list_seller_gray_config", method="GET")

    def discounts(self, page: int = 1, page_size: int = 20):
        return self.call("/api/v1/promotion/discount/list",
                         {"page": page, "page_size": page_size})

    def vouchers(self, page: int = 1, page_size: int = 20):
        return self.call("/api/v1/promotion/voucher/list",
                         {"page": page, "page_size": page_size})

    def items(self, product_ids: list[str]):
        return self.call("/api/v1/promotion/mget_item_data",
                         {"item_ids": [str(i) for i in product_ids]})

    def summary(self):
        return self.call("/api/v1/promotion/get_summary", method="GET")

    def risk_info(self):
        return self.call("/api/v1/promotion/shop_risk_info/get", method="GET")

    # ---- 待补齐字段 ----

    def create_discount(self, body: dict):
        """⚠ body 字段名尚未完全逆向，见 TIKTOK_PROMOTION_API.md §8"""
        return self.call("/api/v1/promotion/discount/create", body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--config", action="store_true")
    ap.add_argument("--gray", action="store_true")
    ap.add_argument("--discounts", action="store_true")
    ap.add_argument("--vouchers", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--items", metavar="PRODUCT_ID")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--call", metavar="PATH")
    ap.add_argument("--method", default="POST")
    ap.add_argument("--body", default=None, help="JSON 字符串")
    a = ap.parse_args()

    api = PromoAPI(a.port)

    def show(j):
        if "_raw" in j:
            print(f"  ⚠ {j.get('_hint','')}")
            print(f"    HTTP={j.get('_http')} raw={j.get('_raw')[:150]}")
            return
        code = j.get("code")
        mark = "✅" if code == 0 else "⚠"
        print(f"  {mark} code={code} msg={j.get('message') or j.get('msg') or ''}")
        print(f"  {json.dumps(j, ensure_ascii=False)[:600]}")

    if a.probe:
        for name, fn in [("config", api.config), ("gray", api.gray),
                         ("discounts", api.discounts), ("vouchers", api.vouchers),
                         ("summary", api.summary), ("risk_info", api.risk_info)]:
            print(f"\n=== {name} ===")
            show(fn())
        return 0
    if a.config:    show(api.config());    return 0
    if a.gray:      show(api.gray());      return 0
    if a.discounts:
        j = api.discounts()
        lst = ((j.get("data") or {}).get("seller_discounts")) or []
        print(f"折扣活动 {len(lst)} 条")
        for d in lst:
            p = d.get("period") or {}
            print(f"  {d.get('id')}  status={d.get('status')}  type={d.get('seller_discount_type')}"
                  f"  {str(d.get('name'))[:36]}  {p.get('start_time')}~{p.get('end_time')}")
        return 0
    if a.vouchers:  show(api.vouchers());  return 0
    if a.summary:   show(api.summary());   return 0
    if a.items:     show(api.items([a.items])); return 0
    if a.call:
        body = json.loads(a.body) if a.body else None
        show(api.call(a.call, body, a.method))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
