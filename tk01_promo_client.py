#!/usr/bin/env python3
"""TikTok Shop 促销活动 API 客户端 —— 跨境店 SHOP_XBORDER / ExampleShop（shop_region=VN）。

所有字段结构都是从促销前端 bundle 逆向 + 服务端实测确认的，不是猜的：
  notes/promo_bundle/DiscountCreateAndEdit.*.js   ← 表单 → payload 的构造点
  notes/promo_bundle/promotion.sg_tts_cb.js       ← API 类定义 + 枚举值

已验证的接口（真实调用返回 code=0）:
  GET  /api/v1/promotion/config                          折扣限制
  GET  /api/v1/promotion/list_seller_gray_config         灰度开关
  POST /api/v1/promotion/discount/list                   活动列表
  GET  /api/v1/promotion/discount/get?promotion_id=…     活动详情
  POST /api/v1/promotion/discount/create                 创建活动  ← 会产生真实数据
  POST /api/v1/promotion/discount/update                 修改活动  ← 会产生真实数据

认证：必须带全量 cookie（含 HttpOnly 的 sessionid），从浏览器 CDP 端口取。
      document.cookie 拿不到 sessionid，会返回 98001002 请登录后再操作。

用法:
  python3 tk01_promo_client.py config
  python3 tk01_promo_client.py discounts
  python3 tk01_promo_client.py get 7689XXXXXXXXXX52
  python3 tk01_promo_client.py products [关键词]        # 商品 + sku_id + 当前价
  python3 tk01_promo_client.py create --name 测试 --product 1736XXXXXXXXXX16 \\
      --discount 15 --start 2026-10-05 --end 2026-10-20 [--dry-run]
  python3 tk01_promo_client.py update <promotion_id> [--name X] [--start D] [--end D]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import requests  # noqa: E402
from tt_http_client import TT, cookies_via_cdp  # noqa: E402

try:
    from tk01_config import API_HOST as HOST
except Exception:
    HOST = "https://api16-normal-sg.tiktokshopglobalselling.com"
SITE = "https://seller.tiktokshopglobalselling.com"
try:
    from tk01_config import SELLER
except Exception:
    SELLER = "7494XXXXXXXXXX00"
AID = "6556"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")
try:
    from tk01_config import DEFAULT_PORT
except Exception:
    DEFAULT_PORT = CDP_PORT

# ── 枚举（promotion.sg_tts_cb.js @6441350 实测提取） ──
DISCOUNT_TYPE = {"PERCENTAGE_OFF": 1, "FIXED_PRICE": 2}          # 百分比 / 一口价
LIMIT_DIMENSION = {"DEFAULT": 0, "SKU": 1, "SPU": 4}             # 指定变体 / 指定商品
STATUS = {1: "待开始", 2: "进行中", 3: "已结束"}
# 限购维度（promotion.sg_tts_cb.js @6442075 的 DZ 枚举，实测确认）
LIMIT_DIM = {"NOT_APPLY": 0, "SKU": 1, "SPU": 4,
             "SKU_TOTAL": 100, "SPU_TOTAL": 101, "NO_LIMIT": -1}
# 服务端业务规则（2026-09-26 实测）: 同时设置总限购+用户限购时，商品数上限为 3。
#   n=2 ✅  n=3 ✅  n=4 ❌  n=5 ❌（换任何数值组合都是 ❌，且只回 code=10000 无 message）
#   不限购、或只设其中一个限购时，任意商品数都可以。
MAX_DUAL_LIMIT_PRODUCTS = 3
# 一口价活动（fixed_price）的商品数上限 —— 实测 1个✅ 2个✅ 3个❌ code=10000
MAX_FIXED_PRODUCTS = 2

# ── 错误码（实测遇到过的） ──
ERRORS = {
    0: "成功",
    98001002: "请登录后再操作 —— cookie 不全，缺 HttpOnly 的 sessionid",
    98001004: "部分信息填写错误 —— 必填字段缺失或类型不对",
    10000: "参数错误（calc_future 等接口的通用拒绝）",
    17003013: "promotion invalid price —— 商品价格/折扣结构不合法",
    17003104: "promotion invalid time period —— 时间窗非法（end 必须在未来）",
    17003115: "该活动名称已存在 —— 换名或用 update",
    17003118: "update promotion info which is ongoing —— 进行中的活动不能改（含改时间窗），"
              "要停只能等它自然结束或在 UI 上操作",
}


def _ts(d: str) -> str:
    """把 'YYYY-MM-DD' / 'YYYY-MM-DD HH:MM:SS' / 纯数字 统一成秒级字符串时间戳。

    服务端要的是字符串，不是数字 —— 传 int 会得到 98001004。
    """
    d = str(d).strip()
    if d.isdigit():
        return d
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return str(int(datetime.strptime(d, fmt).timestamp()))
        except ValueError:
            continue
    raise ValueError(f"时间格式无法解析: {d!r}（用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）")


class PromoClient:
    def __init__(self, port: int = DEFAULT_PORT, timeout: float = 30.0):
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

    # ── 底层 ──
    def call(self, path: str, body=None, method: str = "POST", params=None) -> dict:
        url = HOST + path
        p = {**self.P, **(params or {})}
        if method.upper() == "GET":
            r = self.s.get(url, params=p, timeout=self.timeout)
        else:
            r = self.s.request(method.upper(), url, params=p,
                               json=body if body is not None else {}, timeout=self.timeout)
        t = r.text
        if not t.lstrip().startswith(("{", "[")):
            return {"code": getattr(self, "_http_code", None), "_http": r.status_code,
                    "_raw": t[:300], "_hint": "非 JSON —— 检查路径/域/方法"}
        try:
            return r.json()
        except Exception:
            return {"_http": r.status_code, "_raw": t[:300]}

    def call_checked(self, path: str, body=None, method: str = "POST", params=None) -> dict:
        """失败时抛出带错误码含义的异常，避免静默吞掉 98001004。"""
        r = self.call(path, body, method, params)
        if r.get("code") != 0:
            raise PromoError(r.get("code"), r.get("message"), path, body or params)
        return r

    # ── 配置 / 列表 ──
    def config(self) -> dict:
        """折扣限制：幅度上下限、时长上下限（1%~99%，600s~365d）"""
        return self.call("/api/v1/promotion/config", method="GET")

    def gray_config(self) -> dict:
        """24 个灰度开关：early_bird_price / promo_code / support_bmsm_* 等"""
        return self.call("/api/v1/promotion/list_seller_gray_config", method="GET")

    def summary(self) -> dict:
        return self.call("/api/v1/promotion/get_summary", method="GET")

    def risk_info(self) -> dict:
        return self.call("/api/v1/promotion/shop_risk_info/get", method="GET")

    def discounts(self, page: int = 1, page_size: int = 20) -> list[dict]:
        r = self.call_checked("/api/v1/promotion/discount/list",
                              {"page": page, "page_size": page_size})
        return (r.get("data") or {}).get("seller_discounts") or []

    def discount_get(self, promotion_id: str) -> dict:
        """注意是 GET + query。POST 会 404；用 promotion_id 作参数名（不是 discount_id/id）。"""
        r = self.call_checked("/api/v1/promotion/discount/get", method="GET",
                              params={"promotion_id": str(promotion_id)})
        return (r.get("data") or {}).get("seller_discount") or {}

    # ── 写操作 ──
    def discount_create(self, *, name: str, start, end, products: list[dict],
                        dimension: int = LIMIT_DIMENSION["SPU"],
                        check_overlap: bool | None = None,
                        check_strikethrough_price: bool | None = None,
                        extra: dict | None = None) -> str:
        """创建商品折扣。返回 promotion_id。

        products: [{"product_id": "1736…", "discount_percentage": "15"}, …]
                  discount_percentage 是「减百分之几」的字符串（"15" = 打 85 折）
                  dimension=SPU(4) 时按商品建；SKU(1) 时需在元素里带 sku_id
        注意: seller_agreement 不接受布尔值（传 True 直接 98001004），不要传。
        """
        body = {
            "period": {"start_time": _ts(start), "end_time": _ts(end)},
            "promotion_name": name,
            "promotion_limit_dimension": dimension,
            "products_single_discount": products,
        }
        if check_overlap is not None:
            body["check_overlap"] = check_overlap
        if check_strikethrough_price is not None:
            body["check_strikethrough_price"] = check_strikethrough_price
        if extra:
            body.update(extra)
        r = self.call_checked("/api/v1/promotion/discount/create", body)
        return str((r.get("data") or {}).get("promotion_id", ""))

    def discount_update(self, promotion_id: str, *, name: str | None = None,
                        start=None, end=None, products: list[dict] | None = None,
                        dimension: int | None = None,
                        extra: dict | None = None) -> dict:
        """改活动。未给的字段从当前活动读回来补全 —— 因为 promote_limit_dimension
        和 period 都是服务端必需项，只改名字也必须把它们带上。"""
        cur = self.discount_get(promotion_id)
        per = cur.get("period") or {}
        body = {
            "promotion_id": str(promotion_id),          # 必须字符串，int 会 98001004
            "promotion_name": name or cur.get("name") or "",
            "period": {"start_time": _ts(start or per.get("start_time")),
                       "end_time": _ts(end or per.get("end_time"))},
            "promotion_limit_dimension": dimension if dimension is not None
            else cur.get("promotion_limit_dimension", LIMIT_DIMENSION["SPU"]),
        }
        if products is not None:
            body["products_single_discount"] = products
        if extra:
            body.update(extra)
        return self.call_checked("/api/v1/promotion/discount/update", body)

    # ── 批量建促销：统一入口（多商品 / 百分比或一口价 / SPU或SKU / 限购） ──

    @staticmethod
    def _limit(qty, dimension: int) -> dict:
        """构造限购对象。

        服务端要的是【对象】不是数字 —— 直接传 int 会 98001004：
          {"limit_dimension": 101, "purchase_max_quantity": 5}
        dimension 取值见 LIMIT_DIM：SPU_TOTAL=101 / SKU_TOTAL=100 / SPU=4 / SKU=1 / NO_LIMIT=-1
        qty=None 表示不限购，仍显式下发 NO_LIMIT（-1 + purchase_max_quantity=-1）。
        """
        if qty is None:
            return {"limit_dimension": LIMIT_DIM["NO_LIMIT"], "purchase_max_quantity": -1}
        return {"limit_dimension": dimension, "purchase_max_quantity": int(qty)}

    @classmethod
    def build_products(cls, products: list[dict],
                       dimension: str | None = None) -> tuple[list[dict], int, str]:
        """友好格式 → 服务端 payload。返回 (数组, promotion_limit_dimension, 折扣种类)。

        友好格式（percent 与 fixed_price 二选一；同一活动不能混用，服务端只认其一）：

          SPU 维度（按商品，默认）:
            {"product_id": "1736…", "percent": "10"}                        # 减 10%
            {"product_id": "1736…", "fixed_price": "32000"}                 # 一口价
            {"product_id": "1736…", "percent": "15", "total_limit": 5, "user_limit": 2}

          SKU 维度（按变体，元素里带 skus 即自动切换）:
            {"product_id": "1736…", "skus": [
                {"sku_id": "…", "percent": "10"},
                {"sku_id": "…", "fixed_price": "58000", "total_limit": 3}]}

        要点：
          - percent / fixed_price 一律转字符串，传数字会被拒
          - 一口价必须**低于**该 SKU 原价，等于或高于原价会 code=10000
          - SKU 维度下折扣值与限购都写在 skus[] 元素内（SPU 维度写顶层）
        """
        has_sku = any(p.get("skus") for p in products)
        dim = (LIMIT_DIMENSION[dimension] if dimension
               else (LIMIT_DIMENSION["SKU"] if has_sku else LIMIT_DIMENSION["SPU"]))
        if dim == LIMIT_DIMENSION["SKU"] and not has_sku:
            raise ValueError("dimension=SKU 时每个商品必须带 skus 列表")

        kinds: set[str] = set()
        for p in products:
            for n in (p.get("skus") or [p]):
                if n.get("percent") is not None:
                    kinds.add("percent")
                if n.get("fixed_price") is not None:
                    kinds.add("fixed")
        if len(kinds) > 1:
            raise ValueError("同一活动不能混用 percent 与 fixed_price —— 服务端只认 "
                             "products_single_discount 或 products_fixed_price 之一")
        if not kinds:
            raise ValueError("每个商品至少要给 percent 或 fixed_price")
        kind = kinds.pop()

        total_dim = (LIMIT_DIM["SKU_TOTAL"] if dim == LIMIT_DIMENSION["SKU"]
                     else LIMIT_DIM["SPU_TOTAL"])
        user_dim = (LIMIT_DIM["SKU"] if dim == LIMIT_DIMENSION["SKU"] else LIMIT_DIM["SPU"])
        val_key = "discount_percentage" if kind == "percent" else "fixed_price_value"
        src_key = "percent" if kind == "percent" else "fixed_price"

        def node_of(n: dict, pid: str) -> dict:
            out = {"product_id": str(n.get("product_id") or pid or "")}
            if n.get("sku_id"):
                out["sku_id"] = str(n["sku_id"])
            out[val_key] = str(n[src_key])
            if n.get("total_limit") is not None:
                out["total_purchase_limit"] = cls._limit(n["total_limit"], total_dim)
            if n.get("user_limit") is not None:
                out["user_purchase_limit"] = cls._limit(n["user_limit"], user_dim)
            return out

        built: list[dict] = []
        for p in products:
            pid = str(p.get("product_id") or "")
            if p.get("skus"):
                entry: dict = {"product_id": pid}
                if p.get(src_key) is not None:
                    entry[val_key] = str(p[src_key])
                entry["skus"] = [node_of({**s, "product_id": s.get("product_id") or pid}, pid)
                                 for s in p["skus"]]
                built.append(entry)
            else:
                built.append(node_of(p, pid))
        return built, dim, kind

    @staticmethod
    def check_server_rules(products: list[dict], dimension: str | None = None) -> list[str]:
        """本地预检服务端业务规则 —— 违规时服务端只回一个无 message 的 code=10000，
        拿不到任何线索，所以必须在本地拦下并给出可操作提示。

        已实测规则：同时设 total_limit + user_limit 时商品数 ≤ MAX_DUAL_LIMIT_PRODUCTS(3)。
        """
        try:
            arr, _, _ = PromoClient.build_products(products, dimension)
        except ValueError as e:
            return [str(e)]
        problems: list[str] = []
        dual = [n for n in arr
                if n.get("total_purchase_limit") and n.get("user_purchase_limit")]
        if dual and len(arr) > MAX_DUAL_LIMIT_PRODUCTS:
            problems.append(
                f"同时设置「总限购」与「用户限购」时，商品数最多 {MAX_DUAL_LIMIT_PRODUCTS} 个，"
                f"本活动有 {len(arr)} 个 —— 服务端只会回 code=10000 且不带 message。"
                f"解法：拆成多个活动（promo_plan_split 或 batch --auto-split），"
                f"或只保留一个限购字段")
        return problems

    @staticmethod
    def promo_plan_split(job: dict, max_per_activity: int = MAX_DUAL_LIMIT_PRODUCTS) -> list[dict]:
        """把违反「双限购商品数上限」的 plan 拆成若干合规 plan。

        只有当每个商品的限购都写在商品对象里（而不是 plan 顶层的 total_limit/user_limit）
        时才拆得动 —— 顶层限购意味着全部商品同样受限，此时同样按 max_per_activity 切。
        不需要拆时原样返回长度 1 的列表。
        """
        prods = job.get("products") or []
        dim = job.get("dimension")
        if not prods:
            return [job]
        # 双限购判定：顶层给了两个，或每个商品各自带了两个
        top_dual = job.get("total_limit") is not None and job.get("user_limit") is not None
        try:
            arr, _, _ = PromoClient.build_products(prods, dim)
        except ValueError:
            return [job]
        per_prod_dual = all(n.get("total_purchase_limit") and n.get("user_purchase_limit")
                            for n in arr)
        if not (top_dual or per_prod_dual) or len(prods) <= max_per_activity:
            return [job]

        base = job.get("name", "promo")
        out: list[dict] = []
        for i in range(0, len(prods), max_per_activity):
            chunk = prods[i:i + max_per_activity]
            part = dict(job)
            part["name"] = f"{base}-{i // max_per_activity + 1}"
            part["products"] = chunk
            out.append(part)
        return out

    def promo_create(self, *, name: str, start, end, products: list[dict],
                     dimension: str | None = None,
                     check_overlap: bool | None = None,
                     check_strikethrough_price: bool | None = None,
                     extra: dict | None = None) -> str:
        """建一个促销活动（支持批量商品 / 百分比或一口价 / SPU或SKU / 限购）。返回 promotion_id。

        products 见 build_products 的友好格式说明。
        """
        problems = self.check_server_rules(products, dimension)
        if problems:
            raise ValueError("；".join(problems))
        arr, dim, kind = self.build_products(products, dimension)
        key = "products_single_discount" if kind == "percent" else "products_fixed_price"
        body: dict = {
            "period": {"start_time": _ts(start), "end_time": _ts(end)},
            "promotion_name": name,
            "promotion_limit_dimension": dim,
            key: arr,
        }
        if check_overlap is not None:
            body["check_overlap"] = check_overlap
        if check_strikethrough_price is not None:
            body["check_strikethrough_price"] = check_strikethrough_price
        if extra:
            body.update(extra)
        r = self.call_checked("/api/v1/promotion/discount/create", body)
        return str((r.get("data") or {}).get("promotion_id", ""))

    def promo_create_batch(self, jobs: list[dict], *, park_after: bool = False,
                           on_error: str = "continue") -> list[dict]:
        """批量建多个活动。jobs = [{"name":…, "start":…, "end":…, "products":[…], …}, …]

        park_after=True 时建完立即推到远期（做测试时用，避免活动真的生效）。
        on_error="stop" 时遇错中断，否则继续跑完其余 job。
        """
        out: list[dict] = []
        for idx, j in enumerate(jobs, 1):
            rec: dict = {"index": idx, "name": j.get("name", "")}
            try:
                pid = self.promo_create(**j)
                rec.update({"ok": True, "promotion_id": pid})
                if park_after and pid:
                    self.discount_park(pid)
                    rec["parked"] = True
            except PromoError as e:
                rec.update({"ok": False, "code": e.code, "error": e.message})
                if on_error == "stop":
                    out.append(rec)
                    raise
            except Exception as e:                       # 参数装配错误等
                rec.update({"ok": False, "error": str(e)[:160]})
                if on_error == "stop":
                    out.append(rec)
                    raise
            out.append(rec)
            flag = "OK " if rec["ok"] else "ERR"
            print(f"  [{flag}] {idx:>3}/{len(jobs)} {str(rec['name'])[:30]:32} "
                  f"{rec.get('promotion_id') or rec.get('error', '')}", flush=True)
        return out

    def promo_list_products(self, promotion_id: str, page: int = 1,
                            page_size: int = 50) -> list[dict]:
        """读回活动里的商品 —— 验证批量建活动是否真的关联上了。

        返回项含 product_id / product_name / inventory_quantity / sale_price_range /
        total_sku_count / selected_sku_count / selected。
        注：该接口**不返回**折扣值与限购值，这两项只能在 UI 的编辑页确认。
        """
        r = self.call_checked("/api/v1/promotion/list_products",
                              {"promotion_id": str(promotion_id),
                               "page": page, "page_size": page_size})
        return (r.get("data") or {}).get("item_products") or []

    def product_detail(self, product_id: str) -> dict:
        """商品详情（含 skus[].base_price.{sale_price,promotion_price}）—— 做一口价前用它取原价。"""
        r = self.call_checked("/api/v1/product/local/product/get", method="GET",
                              params={"product_id": str(product_id)})
        return (r.get("data") or {}).get("product") or {}

    def product_list(self, tab_id: int = 1, page_size: int = 50) -> list[dict]:
        """商品列表（走 api16 域，用促销同一套 cookie）。"""
        r = self.call_checked("/api/v1/product/web/local/products/list", method="GET",
                              params={"tab_id": tab_id, "page_size": page_size, "page": 1})
        return (r.get("data") or {}).get("products") or []

    def sku_prices(self, product_id: str) -> dict[str, str]:
        """{sku_id: 原价} —— 算一口价用，避免一口价 ≥ 原价被服务端拒（code=10000）。"""
        pr = self.product_detail(product_id)
        return {str(s.get("id")): str(((s.get("base_price") or {}).get("sale_price")) or "")
                for s in (pr.get("skus") or [])}

    # ── 一口价（fixed_price）────────────────────────────────────────────
    # ⚠️ 为什么必须经浏览器页面发请求:
    #   fixed_price/* 的请求要带 X-Bogus / X-Gnarly / msToken 三个签名参数，
    #   它们是 TikTok 的 webmssdk.js 在页面里注入到 fetch/XHR 上的。
    #   直连（requests）一律 code=10000，而且服务端不给任何 message —— 这就是
    #   之前把 payload 结构试了 15+ 遍都失败的真因：不是字段错，是缺签名。
    #   discount/* 不需要签名，所以直连一直可用。

    # 为什么不用 await_promise:
    #   页面在后台会被浏览器节流，fetch 可能长时间不 resolve；
    #   用 Runtime.evaluate + awaitPromise 时 CDP 会一直等，最终 socket 超时
    #   （表现为 "Connection timed out" / 140s 硬超时）。
    #   改成"先发出去、把结果写进 window.__promo_r、再轮询读回来"就稳了。
    PAGE_FETCH_JS = """
    (() => {
      window.__promo_r = null;
      fetch(%s, {method: "POST",
        headers: {"content-type": "application/json"},
        body: %s, credentials: "include"})
        .then(r => r.text().then(t => {window.__promo_r = JSON.stringify({status: r.status, body: t});}))
        .catch(e => {window.__promo_r = JSON.stringify({error: String(e)});});
      return "sent";
    })()
    """

    @staticmethod
    def ensure_page(port: int = DEFAULT_PORT) -> list[dict]:
        """没有 seller 页面时自动开一个 —— 否则所有走页面签名的调用都会失败。"""
        tabs = PromoClient._promo_pages(port)
        if tabs:
            return tabs
        try:
            PromoClient.open_seller_page(port)
            return PromoClient._promo_pages(port)
        except Exception:
            return []

    @staticmethod
    def _promo_pages(port: int = DEFAULT_PORT) -> list[dict]:
        """列出可用的 seller.* 页面（按 URL 偏好排序，创建/编辑页优先）。"""
        import json as _json
        import urllib.request as _u
        tabs = [t for t in _json.load(_u.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=8))
                if t.get("type") == "page"
                and "seller.tiktokshopglobalselling.com" in (t.get("url") or "")
                and t.get("webSocketDebuggerUrl")]
        pref = ("discount/create", "discount/edit", "tool-choose", "management")
        def rank(t):
            u = t.get("url") or ""
            for i, k in enumerate(pref):
                if k in u:
                    return i
            return len(pref)
        return sorted(tabs, key=rank)

    @staticmethod
    def open_seller_page(port: int = DEFAULT_PORT, *, wait: float = 10.0) -> dict:
        """新开一个 seller 页面（后台 tab 睡死时用来替换）。"""
        import json as _json
        import urllib.parse as _up
        import urllib.request as _u
        url = ("https://seller.tiktokshopglobalselling.com/promotion/"
               "marketing-tools/tool-choose?shop_region=VN")
        req = _u.Request(f"http://127.0.0.1:{port}/json/new?" + _up.quote(url, safe=""),
                         method="PUT")
        t = _json.load(_u.urlopen(req, timeout=15))
        time.sleep(wait)
        return t

    @staticmethod
    def _page_alive(pg) -> bool:
        """轻量探活：后台被节流的页面连 1+1 都返回不了。"""
        try:
            return pg.js("1+1", timeout=8) == 2
        except Exception:
            return False

    @staticmethod
    def _promo_page(port: int, *, timeout: float = 60.0):
        """取一个 seller 页面用来发签名请求（优先创建/编辑页）。

        页面被浏览器节流时 Runtime.evaluate 会挂住，所以调用方应做多页面重试 ——
        见 call_via_page。
        """
        from hub_headless import CDPPage
        tabs = PromoClient._promo_pages(port)
        if not tabs:
            raise RuntimeError("没有已登录的 seller 页面 —— 请先打开卖家中心任意页面")
        pg = CDPPage(tabs[0]["webSocketDebuggerUrl"], timeout=timeout)
        pg.enable("Runtime")
        return pg

    @staticmethod
    def _captcha_guard(port: int):
        """惰性导入验证码处理器（没有 tt_captcha.py 也能跑）。"""
        try:
            from tt_captcha import CaptchaGuard
            return CaptchaGuard(port)
        except Exception:
            return None

    def captcha_present(self, port: int = DEFAULT_PORT) -> bool:
        """当前 TikTok 页面是否弹了验证码。"""
        g = self._captcha_guard(port)
        if g is None:
            return False
        try:
            pg = g.open()
            try:
                st = g.detect(pg)
                return bool(st.get("btn") or st.get("text_hit"))
            finally:
                pg.close()
        except Exception:
            return False

    def solve_captcha(self, port: int = DEFAULT_PORT, *, retries: int = 5) -> bool:
        """滑掉当前验证码。返回是否通过。"""
        g = self._captcha_guard(port)
        if g is None:
            return False
        return g.solve(retries=retries)

    def call_via_page(self, path: str, body: dict, *, port: int = DEFAULT_PORT,
                      params: str | None = None, retries: int = 4,
                      auto_captcha: bool = True) -> dict:
        """在浏览器页面上下文里 POST —— 自动带上 SDK 签名。

        页面被节流时 Runtime.evaluate 会挂住，所以轮换多个 seller 页面重试。
        """
        import json as _json
        qs = params or ("locale=zh-CN&language=zh-CN"
                        f"&oec_seller_id={SELLER}&aid={AID}&app_name=i18n_ecom_shop")
        url = f"{HOST}{path}?{qs}"
        js = self.PAGE_FETCH_JS % (_json.dumps(url),
                                   _json.dumps(_json.dumps(body, ensure_ascii=False)))
        from hub_headless import CDPPage
        tabs = self.ensure_page(port)
        if not tabs:
            raise RuntimeError("无法获得 seller 页面（自动开页也失败）")
        last_err: Exception | None = None
        solved_captcha = False
        for attempt in range(max(1, retries)):
            if attempt and attempt % max(1, len(tabs)) == 0:
                # 所有已有页面都试过了还是失败 —— 后台 tab 睡死了，换一个新的
                try:
                    tabs = [self.open_seller_page(port)]
                except Exception:
                    pass
            tab = tabs[attempt % len(tabs)]
            pg = None
            try:
                pg = CDPPage(tab["webSocketDebuggerUrl"], timeout=25)
                pg.enable("Runtime", "Page")
                if not self._page_alive(pg):
                    raise TimeoutError("页面无响应（被节流）")
                try:
                    pg.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
                except Exception:
                    pass
                pg.js(js, timeout=20)                       # 只负责发出去，不等结果
                raw = None
                for _ in range(60):                          # 轮询最多 30 秒
                    time.sleep(0.5)
                    try:
                        raw = pg.js("window.__promo_r", timeout=15)
                    except Exception:
                        continue
                    if raw:
                        break
                if not raw:
                    raise TimeoutError("轮询 30s 未拿到响应")
                out = json.loads(raw)
                if "error" in out:
                    raise PromoError(0, f"页面 fetch 失败: {out['error']}", path, body)
                try:
                    result = json.loads(out.get("body") or "{}")
                except Exception:
                    result = {"_http": out.get("status"), "_raw": (out.get("body") or "")[:300]}

                # code=10000 无 message 有两种可能：缺签名 / 风控要验证。
                # 后者可以在页面里看到验证码 —— 那就滑掉再重发原请求。
                if result.get("code") == 10000 and auto_captcha and not solved_captcha:
                    try:
                        from tt_captcha import CaptchaGuard
                        g = CaptchaGuard(port)
                        st = g.detect(pg)
                        if st.get("btn") or st.get("text_hit"):
                            print(f"  ⚠️ 命中风控验证码 → 自动滑动（{path.split('/')[-1]}）")
                            if g.solve(pg, retries=5):
                                solved_captcha = True
                                continue          # 滑过之后重发原请求
                            print("  ✗ 验证码未通过，交给上层重试")
                    except Exception as e:
                        print("  验证码处理异常:", str(e)[:90])
                return result
            except Exception as e:
                last_err = e
                time.sleep(1.0)
            finally:
                if pg is not None:
                    try:
                        pg.close()
                    except Exception:
                        pass
        raise RuntimeError(f"call_via_page 重试 {retries} 次仍失败: {str(last_err)[:140]}")

    def promo_create_fixed(self, *, name: str, start, end, products: list[dict],
                           dimension: str = "SKU", check_overlap: bool = True,
                           check_strikethrough_price: bool = False,
                           port: int = DEFAULT_PORT) -> str:
        """创建一口价活动（走浏览器签名）。返回 promotion_id。

        products 友好格式（一口价天然是 SKU 级的）:
          [{"product_id": "1735…",
            "price_limit": "0",
            "skus": {"1735…": "30000", "1735…": "22000"}}]
        也接受 skus 为列表: [{"sku_id": "…", "fixed_price": "30000"}, …]

        price_limit 是服务端必需字段（缺了就是 code=10000），默认 "0" 已实测可用。
        一口价必须低于该 SKU 原价。
        """
        built = []
        for p in products:
            pid = str(p.get("product_id") or "")
            sk = p.get("skus") or {}
            if isinstance(sk, dict):
                skus = [{"sku_id": str(s), "product_id": pid, "fixed_price_value": str(v)}
                        for s, v in sk.items()]
            else:
                skus = [{"sku_id": str(s.get("sku_id")),
                         "product_id": str(s.get("product_id") or pid),
                         "fixed_price_value": str(s.get("fixed_price") or s.get("fixed_price_value"))}
                        for s in sk]
            if not skus:
                raise ValueError(f"商品 {pid} 没有 skus")
            built.append({"product_id": pid,
                          "price_limit": str(p.get("price_limit", "0")),
                          "skus": skus})
        body = {
            "period": {"start_time": _ts(start), "end_time": _ts(end)},
            "promotion_name": name,
            "promotion_limit_dimension": LIMIT_DIMENSION.get(dimension, 1)
            if isinstance(dimension, str) else dimension,
            "products_fixed_price": built,
            "check_overlap": check_overlap,
            "check_strikethrough_price": check_strikethrough_price,
        }
        r = self.call_via_page("/api/v1/promotion/fixed_price/create", body, port=port)
        if r.get("code") != 0:
            raise PromoError(r.get("code"), r.get("message"),
                             "/api/v1/promotion/fixed_price/create", body)
        return str((r.get("data") or {}).get("promotion_id", ""))

    def promo_park_fixed(self, promotion_id: str, *, days: int = 400,
                         port: int = DEFAULT_PORT) -> dict:
        """把一口价活动推到远期。

        一口价活动必须用 fixed_price/update —— 用 discount/update 会被拒
        （17003109 promotion invalid update）。实测这个端点**不需要**签名，可直连。
        """
        now = int(time.time())
        cur = self.discount_get(promotion_id)
        return self.call_checked("/api/v1/promotion/fixed_price/update", {
            "promotion_id": str(promotion_id),
            "promotion_name": cur.get("name", "")[:60],
            "period": {"start_time": str(now + 86400 * days),
                       "end_time": str(now + 86400 * (days + 30))},
            "promotion_limit_dimension": cur.get("promotion_limit_dimension", 1)})

    def park_any(self, promotion_id: str, *, days: int = 400,
                 port: int = DEFAULT_PORT) -> dict:
        """按活动类型自动选对的 update 端点来 park。"""
        cur = self.discount_get(promotion_id)
        if cur.get("seller_discount_type") == 2:
            return self.promo_park_fixed(promotion_id, days=days, port=port)
        return self.discount_park(promotion_id, days=days)

    # ── 商品维度的活动扫描 / 改价 ─────────────────────────────────────

    def scan_product_promotions(self, product_id: str, *, with_sku_detail: bool = True,
                                port: int = DEFAULT_PORT, gap: float = 1.0) -> list[dict]:
        """扫描某商品参与了哪些活动 —— **1 个请求**搞定。

        关键：产品详情的 `promotion_infos` 直接列出该商品参与的活动
        （外加 `product_discount_promotion` 指向商品级折扣活动），
        所以不需要遍历整个活动列表。

        with_sku_detail=True 时，再对命中的活动调 list_products_by_cursor
        拿该商品的 SKU 级现价（这个接口需要签名，会慢一些）。
        """
        target = str(product_id)
        d = self.product_detail(target)
        infos = list(d.get("promotion_infos") or [])
        pdp = d.get("product_discount_promotion") or {}
        if pdp.get("promotion_id"):
            infos.append(pdp)
        seen, out = set(), []
        for info in infos:
            pid = str(info.get("promotion_id") or "")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            rec: dict = {"promotion_id": pid,
                         "name": info.get("promotion_name"),
                         "product_name": d.get("product_name"),
                         "product_status": d.get("product_status")}
            try:                                     # 直连，便宜
                act = self.discount_get(pid)
                rec.update({"type": act.get("seller_discount_type"),
                            "type_text": {1: "百分比折扣", 2: "一口价"}.get(
                                act.get("seller_discount_type")),
                            "status": act.get("status"),
                            "status_text": STATUS.get(act.get("status")),
                            "start": (act.get("period") or {}).get("start_time"),
                            "end": (act.get("period") or {}).get("end_time"),
                            "dimension": act.get("promotion_limit_dimension")})
            except Exception as e:
                rec["error"] = str(e)[:100]
            if with_sku_detail:
                try:                                 # 需签名，慢
                    detail = self.list_products_by_cursor(pid, limit=100, port=port)
                    mine = next((x for x in detail if str(x.get("product_id")) == target), None)
                    if mine:
                        rec["discount_percentage"] = mine.get("discount_percentage")
                        rec["estimated_discounted_price_range"] = mine.get(
                            "estimated_discounted_price_range")
                        rec["purchase_limit"] = mine.get("total_purchase_limit")
                        rec["user_purchase_limit"] = mine.get("user_purchase_limit")
                        rec["skus"] = [{"sku_id": x.get("sku_id"), "sku_name": x.get("sku_name"),
                                        "fixed_price": x.get("fixed_price"),
                                        "fixed_price_value": x.get("fixed_price_value"),
                                        "in_promotion": x.get("in_promotion")}
                                       for x in (mine.get("skus") or [])]
                except Exception as e:
                    rec["detail_error"] = str(e)[:100]
                time.sleep(gap)
            out.append(rec)
        return out

    def update_product_fixed_price(self, product_id: str, sku_prices: dict,
                                   *, promotion_ids: list[str] | None = None,
                                   port: int = DEFAULT_PORT, gap: float = 3.0,
                                   dry_run: bool = False) -> list[dict]:
        """改某商品在若干**一口价**活动里的价格。

        ⚠️ 已实测（用 2 商品活动验证过）: fixed_price/update 是【增量】语义 ——
           只传目标商品，同活动里其他商品会自动保留、不会被删。
           本方法仍默认先读全量、把其他商品原样带上（双保险）。

        sku_prices: {"<sku_id>": "<新价>"}；未列出的 SKU 保持原价。
        promotion_ids 为 None 时自动扫描该商品所在的一口价活动。
        """
        target = str(product_id)
        if promotion_ids is None:
            promotion_ids = [h["promotion_id"] for h in
                             self.scan_product_promotions(target, port=port)
                             if h.get("type") == 2]
        out: list[dict] = []
        for pid in promotion_ids:
            try:
                act = self.discount_get(pid)
                if act.get("seller_discount_type") != 2:
                    out.append({"promotion_id": pid, "ok": False,
                                "error": "不是一口价活动(type!=2)"})
                    continue
                detail = self.list_products_by_cursor(pid, limit=100, port=port)
                products, found = [], False
                for pr in detail:
                    pr_pid = str(pr.get("product_id"))
                    skus = []
                    for sk in (pr.get("skus") or []):
                        sid = str(sk.get("sku_id"))
                        cur = sk.get("fixed_price_value") or "0"
                        if pr_pid == target:
                            found = True
                            newv = str(sku_prices.get(sid, cur))
                        else:
                            newv = cur
                        item = {"sku_id": sid, "product_id": pr_pid, "fixed_price_value": newv}
                        if pr_pid == target and sk.get("total_purchase_limit"):
                            item["total_purchase_limit"] = sk["total_purchase_limit"]
                        skus.append(item)
                    if skus:
                        products.append({"product_id": pr_pid,
                                         "price_limit": str(pr.get("price_limit", "0")),
                                         "skus": skus})
                if not found:
                    out.append({"promotion_id": pid, "ok": False,
                                "error": f"活动里没有商品 {target}"})
                    continue
                if dry_run:
                    out.append({"promotion_id": pid, "ok": True, "dry_run": True,
                                "would_send": products})
                    continue
                r = self.call_checked("/api/v1/promotion/fixed_price/update", {
                    "promotion_id": str(pid), "promotion_name": act.get("name", ""),
                    "period": act.get("period"),
                    "promotion_limit_dimension": act.get("promotion_limit_dimension", 1),
                    "products_fixed_price": products})
                out.append({"promotion_id": pid, "ok": True, "code": r.get("code"),
                            "products_sent": len(products)})
            except Exception as e:
                out.append({"promotion_id": pid, "ok": False, "error": str(e)[:140]})
            time.sleep(gap)
        return out

    # ── 查看（活动明细 / 报表 / 反查）──────────────────────────────────

    def list_products_by_cursor(self, promotion_id: str, *, limit: int = 200,
                                port: int = DEFAULT_PORT) -> list[dict]:
        """活动里的商品**完整明细** —— 含每个 SKU 的价格/库存/划线价。

        比 list_products 强得多：那个只有 10 个字段、拿不到折扣值和限购值。
        这个返回（实测）:
          product 级: product_id / product_name / inventory_quantity / sale_price_range
                      / purchase_limit / fixed_price_value / image
          sku 级:     sku_id / sku_name / in_promotion / inventory_quantity
                      / sale_price_range / fixed_price_value / discount_percentage
                      / strikethrough_price_info / alert_info

        ⚠️ 该接口需要请求签名（X-Bogus），直连返回 code=10000，必须走页面上下文。
        """
        r = self.call_via_page("/api/v1/promotion/list_products_by_cursor", {
            "promotion_id": str(promotion_id), "need_smart_discount": False,
            "extra_info_list": [], "use_streamline": True,
            "cursor": 0, "limit": limit}, port=port)
        if r.get("code") != 0:
            raise PromoError(r.get("code"), r.get("message"),
                             "/api/v1/promotion/list_products_by_cursor",
                             {"promotion_id": promotion_id})
        return (r.get("data") or {}).get("item_products") or []

    def promo_detail(self, promotion_id: str, *, port: int = DEFAULT_PORT) -> dict:
        """一个活动的完整画像：基本信息 + 商品 + 每个 SKU 的促销价/库存/限购。"""
        act = self.discount_get(promotion_id)
        prods = self.list_products_by_cursor(promotion_id, port=port)
        sku_n = sum(len(p.get("skus") or []) for p in prods)
        return {"promotion": act, "products": prods,
                "product_count": len(prods), "sku_count": sku_n}

    def promo_report(self, promotion_id: str, *, port: int = DEFAULT_PORT) -> str:
        """把活动明细渲染成人类可读的多行报表。"""
        d = self.promo_detail(promotion_id, port=port)
        a = d["promotion"]
        typ = {1: "百分比折扣", 2: "一口价"}.get(a.get("seller_discount_type"), "?")
        dim = {0: "默认", 1: "指定变体", 4: "指定商品"}.get(a.get("promotion_limit_dimension"), "?")
        st = STATUS.get(a.get("status"), a.get("status"))
        p = a.get("period") or {}
        out = [f"活动 {a.get('id')}  [{typ} / {dim}]  {st}",
               f"  名称: {a.get('name')}",
               f"  时间: {p.get('start_time')} ~ {p.get('end_time')}",
               f"  商品 {d['product_count']} 个 / SKU {d['sku_count']} 个"]
        for pr in d["products"]:
            out.append(f"  · {pr.get('product_id')}  {(pr.get('product_name') or '')[:40]}")
            # 百分比活动的折扣值在 product 级；一口价在 sku 级（下面逐个打）
            line = (f"      库存={pr.get('inventory_quantity')}  "
                    f"原价={_range_str(pr.get('sale_price_range'))}")
            pct = pr.get("discount_percentage")
            if pct and str(pct) not in ("0", ""):
                line += f"  折扣={pct}%"
            est = pr.get("estimated_discounted_price_range") or {}
            if est.get("lowest_price_value"):
                line += (f"  折后={est.get('lowest_price_value')}"
                         f"~{est.get('highest_price_value')}")
            tpl = pr.get("total_purchase_limit") or {}
            if tpl.get("purchase_max_quantity") is not None:
                line += (f"  总限购={tpl.get('purchase_max_quantity')}"
                         f"(剩{tpl.get('purchase_limit_available')})")
            upl = pr.get("user_purchase_limit") or {}
            if upl.get("purchase_max_quantity") is not None:
                line += f"  客户限购={upl.get('purchase_max_quantity')}"
            out.append(line)
            for s in (pr.get("skus") or []):
                fp = s.get("fixed_price_value")
                price = s.get("fixed_price") if fp and str(fp) != "0" else "-"
                strike = (s.get("strikethrough_price_info") or {}).get("formatted_strikethrough_price")
                out.append(f"      - {s.get('sku_id')}  {str(s.get('sku_name'))[:14]:16}"
                           f" 促销价={str(price):13} 划线价={str(strike or '-'):11}"
                           f" 库存={s.get('inventory_quantity')}"
                           f" 参与={'是' if s.get('in_promotion') else '否'}")
        return "\n".join(out)

    def promo_find_by_product(self, product_id: str, *, port: int = DEFAULT_PORT) -> list[dict]:
        """反查：某个商品当前挂在哪些活动里（遍历活动列表逐个比对）。"""
        target = str(product_id)
        hits = []
        for it in self.discounts(1, 100):
            try:
                prods = self.list_products_by_cursor(it["id"], limit=50, port=port)
            except Exception:
                continue
            if any(str(p.get("product_id")) == target for p in prods):
                hits.append(it)
        return hits

    def promo_export(self, out_path: str, *, port: int = DEFAULT_PORT,
                     limit: int = 100) -> int:
        """把所有活动连同商品/SKU 明细导出成 JSON。返回活动数。"""
        rows = []
        for it in self.discounts(1, limit):
            try:
                detail = self.promo_detail(it["id"], port=port)
            except Exception as e:
                detail = {"promotion": it, "error": str(e)[:120]}
            rows.append(detail)
        Path(out_path).write_text(json.dumps(rows, ensure_ascii=False, indent=1))
        return len(rows)

    def discount_park(self, promotion_id: str, *, days: int = 400) -> dict:
        """把活动窗口推到远期，让它在可见范围内永不生效 —— 折扣活动的清理方式。

        为什么不是"改成很快结束"：折扣活动**没有** deactivate/delete/stop 接口
        （bundle 里只有 create/get/list/update），也不能把 end_time 改到过去
        （17003104 promotion invalid time period）。若改成 now+2min ~ now+1h，
        活动会**真的生效一小时并给商品打折** —— 生产店铺上这是事故。
        推到 400 天后则永远不会命中。

        已用此法处理 4 个测试活动: 7689XXXXXXXXXX99 / 7689XXXXXXXXXX14 /
        7689XXXXXXXXXX66 / 7689XXXXXXXXXX52
        """
        now = int(time.time())
        return self.discount_update(promotion_id,
                                    start=str(now + 86400 * days),
                                    end=str(now + 86400 * (days + 30)))

    # ── 商品 / SKU ──
    def products_with_skus(self, keyword: str = "", limit: int = 50) -> list[dict]:
        """商品列表 + 每个商品的 sku_id 和当前价。

        create 需要 product_id；dimension=SKU(1) 时还需要 sku_id。
        用商品列表接口而不是 /product/local/product/get —— 后者直连返回 code=10000。
        """
        tt = TT(port=DEFAULT_PORT)
        try:
            out: list[dict] = []
            for tab in (1, 2):
                page = 1
                while len(out) < limit and page <= 5:
                    r = tt.get("/api/v1/product/web/local/products/list"
                               f"?tab_id={tab}&page_size=50&page={page}")
                    d = (r.get("json") or {}).get("data") or {}
                    prods = d.get("products") or []
                    for pr in prods:
                        name = pr.get("product_name") or ""
                        if keyword and keyword.lower() not in name.lower():
                            continue
                        out.append({
                            "product_id": str(pr.get("product_id")),
                            "name": name[:70],
                            "status": pr.get("product_status"),
                            "skus": [{"sku_id": str(s.get("id")),
                                      "seller_sku": s.get("seller_sku"),
                                      "price": (s.get("price") or {}).get("sale_price")
                                               or (s.get("price") or {}).get("price")}
                                     for s in (pr.get("skus") or [])],
                        })
                        if len(out) >= limit:
                            break
                    if not d.get("has_more") or not prods:
                        break
                    page += 1
            return out
        finally:
            try:
                tt.close()
            except Exception:
                pass


class PromoError(RuntimeError):
    def __init__(self, code, message, path, body):
        self.code, self.message, self.path, self.body = code, message, path, body
        hint = ERRORS.get(code, "")
        # code=10000/98001004 这类服务端不给 message，别让它显示成 None
        msg = message or ("(服务端未返回 message)" if code else "")
        super().__init__(f"[{code}] {msg}  ({hint})\n  {path}\n  {json.dumps(body, ensure_ascii=False)[:400]}")


# ───────────────────────── CLI ─────────────────────────

def _range_str(rng) -> str:
    """把 {"lowest_price_value": "36000", "highest_price_value": "90000"} 渲染成 36000~90000"""
    if not isinstance(rng, dict):
        return "-"
    lo, hi = rng.get("lowest_price_value"), rng.get("highest_price_value")
    return f"{lo}~{hi}" if lo != hi else str(lo)


def _normalize_plan(j: dict) -> dict:
    """把 plan JSON 转成 promo_create 的 kwargs。

    简化写法 —— products 只写商品 id，折扣/限购取顶层字段：
      {"name": "秋季促销", "start": "2026-10-05", "end": "2026-10-20",
       "discount": "15", "total_limit": 5, "products": ["1736…", "1736…"]}
    混合写法 —— 每个商品各自带参数：
      {"name": "…", "products": [{"product_id": "A", "percent": "10"},
                                 {"product_id": "B", "fixed_price": "32000"}]}
    start / end 省略时: start=明天, end=start+15天。
    """
    tomorrow = datetime.now() + timedelta(days=1)
    start = j.get("start") or tomorrow.strftime("%Y-%m-%d")
    end = j.get("end") or (datetime.strptime(_fmt_date(start), "%Y-%m-%d")
                           + timedelta(days=15)).strftime("%Y-%m-%d")
    d, fp = j.get("discount"), j.get("fixed_price")
    norm: list[dict] = []
    for p in (j.get("products") or []):
        if isinstance(p, str):
            item: dict = {"product_id": p}
            if fp is not None:
                item["fixed_price"] = str(fp)
            elif d is not None:
                item["percent"] = str(d)
            if j.get("total_limit") is not None:
                item["total_limit"] = j["total_limit"]
            if j.get("user_limit") is not None:
                item["user_limit"] = j["user_limit"]
            norm.append(item)
        else:
            norm.append(p)
    out: dict = {"name": j["name"], "start": start, "end": end, "products": norm}
    for k in ("dimension", "check_overlap", "check_strikethrough_price"):
        if j.get(k) is not None:
            out[k] = j[k]
    return out


def _fmt_date(d: str) -> str:
    """'YYYY-MM-DD' 或时间戳 → 'YYYY-MM-DD'（给 timedelta 用）。"""
    d = str(d).strip()
    if d.isdigit():
        return datetime.fromtimestamp(int(d)).strftime("%Y-%m-%d")
    return d[:10]


PLAN_TEMPLATE = {
    "_说明": "单活动 = 对象；批量 = 对象数组。percent 与 fixed_price 二选一，同一活动不能混。",
    "name": "秋季促销-示例",
    "start": "2026-10-05",
    "end": "2026-10-20",
    "discount": "15",
    "total_limit": 5,
    "user_limit": 2,
    "products": ["1736XXXXXXXXXX16", "1736XXXXXXXXXX24"],
    "_进阶_一口价": {"fixed_price": "32000", "products": ["1736XXXXXXXXXX16"]},
    "_进阶_SKU维度": {"dimension": "SKU",
                   "products": [{"product_id": "1736XXXXXXXXXX16",
                                 "skus": [{"sku_id": "1736XXXXXXXXXX28", "percent": "10"},
                                          {"sku_id": "1736XXXXXXXXXX64", "fixed_price": "58000",
                                           "total_limit": 3}]}]},
}


def _print(r) -> None:
    print(json.dumps(r, ensure_ascii=False, indent=1)[:4000])


def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok Shop 促销活动 API 客户端 (SHOP_XBORDER)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("config")
    sub.add_parser("gray")
    sub.add_parser("summary")
    sub.add_parser("discounts")
    p_get = sub.add_parser("get"); p_get.add_argument("promotion_id")
    p_prod = sub.add_parser("products"); p_prod.add_argument("keyword", nargs="?", default="")

    p_promo = sub.add_parser("promo", help="按 JSON plan 建一个活动")
    p_promo.add_argument("--file", "-f", required=True, help="plan JSON 路径")
    p_promo.add_argument("--dry-run", action="store_true")

    p_batch = sub.add_parser("batch", help="按 JSON 数组批量建活动")
    p_batch.add_argument("--file", "-f", required=True)
    p_batch.add_argument("--park-after", action="store_true",
                         help="建完立即推到远期(测试用，避免活动真的生效)")
    p_batch.add_argument("--dry-run", action="store_true")
    p_batch.add_argument("--stop-on-error", action="store_true")
    p_batch.add_argument("--auto-split", action="store_true",
                         help=f"自动把「双限购且商品数>{MAX_DUAL_LIMIT_PRODUCTS}」的 plan 拆成多个活动")

    p_rep = sub.add_parser("report", help="活动明细报表(商品/SKU/促销价/限购)")
    p_rep.add_argument("promotion_id")

    p_det = sub.add_parser("detail", help="活动完整明细(JSON)")
    p_det.add_argument("promotion_id")

    p_find = sub.add_parser("find", help="反查某商品挂在哪些活动里")
    p_find.add_argument("product_id")

    p_exp = sub.add_parser("export", help="把所有活动连同商品明细导出 JSON")
    p_exp.add_argument("out", nargs="?", default="notes/promo_export.json")

    p_sc = sub.add_parser("scan", help="扫描某商品参与了哪些活动(1 个请求)")
    p_sc.add_argument("product_id")
    p_sc.add_argument("--no-sku", action="store_true", help="不取 SKU 级现价(更快)")

    p_sp = sub.add_parser("set-price", help="改某商品在一口价活动里的价格")
    p_sp.add_argument("product_id")
    p_sp.add_argument("--activity", "-a", action="append", default=[],
                      help="指定活动 id，可重复；不传则自动扫描该商品的一口价活动")
    p_sp.add_argument("--sku", action="append", default=[],
                      help="SKU_ID=新价，可重复；不传则对所有 SKU 用 --price")
    p_sp.add_argument("--price", help="统一新价（配合不传 --sku 使用）")
    p_sp.add_argument("--dry-run", action="store_true")

    p_lp = sub.add_parser("list-products", help="读回活动里的商品(验证批量关联)")
    p_lp.add_argument("promotion_id")

    sub.add_parser("new-plan", help="打印 plan JSON 模板")

    p_c = sub.add_parser("create")
    p_c.add_argument("--name", required=True)
    p_c.add_argument("--product", required=True, help="product_id，逗号分隔可多个")
    p_c.add_argument("--discount", default="15", help="减百分之几，如 15 = 打 85 折")
    p_c.add_argument("--start", required=True, help="YYYY-MM-DD 或时间戳")
    p_c.add_argument("--end", required=True)
    p_c.add_argument("--dimension", type=int, default=LIMIT_DIMENSION["SPU"])
    p_c.add_argument("--dry-run", action="store_true", help="只打印 payload，不调用")

    p_u = sub.add_parser("update")
    p_u.add_argument("promotion_id")
    p_u.add_argument("--name"); p_u.add_argument("--start"); p_u.add_argument("--end")

    p_e = sub.add_parser("park", help="把活动推到远期使其永不生效(折扣活动的清理方式)")
    p_e.add_argument("promotion_id")
    p_e.add_argument("--days", type=int, default=400)

    a = ap.parse_args()
    C = PromoClient(port=a.port)

    if a.cmd == "config":      _print(C.config())
    elif a.cmd == "gray":      _print(C.gray_config())
    elif a.cmd == "summary":   _print(C.summary())
    elif a.cmd == "discounts":
        for it in C.discounts():
            print(f"  {it['id']}  status={STATUS.get(it['status'], it['status'])}  "
                  f"type={it['seller_discount_type']}  {it['period']['start_time']}~{it['period']['end_time']}  {it['name']}")
    elif a.cmd == "get":       _print(C.discount_get(a.promotion_id))
    elif a.cmd == "products":
        rows = C.products_with_skus(a.keyword)
        for r in rows:
            print(json.dumps(r, ensure_ascii=False)[:400])
        if not rows:
            print("（无结果 —— TT.products 未实现时请用 tk01_prod_detail 系接口取 sku_id）")
    elif a.cmd == "new-plan":
        print(json.dumps(PLAN_TEMPLATE, ensure_ascii=False, indent=2))

    elif a.cmd in ("promo", "batch"):
        raw = json.loads(Path(a.file).read_text())
        plans = raw if isinstance(raw, list) else [raw]
        plans = [p for p in plans if not str(p.get("name", "")).startswith("_")]
        jobs = [_normalize_plan(p) for p in plans]
        if a.dry_run:
            for j in jobs:
                arr, dim, kind = PromoClient.build_products(j["products"], j.get("dimension"))
                print(json.dumps({"name": j["name"], "start": _ts(j["start"]),
                                  "end": _ts(j["end"]), "dimension": dim, "kind": kind,
                                  "count": len(arr), "payload": arr},
                                 ensure_ascii=False, indent=1))
            print(f"--dry-run：{len(jobs)} 个活动，未调用")
            return
        if a.cmd == "promo":
            pid = C.promo_create(**jobs[0])
            print(f"✅ promotion_id = {pid}")
            print("   payload:", json.dumps(
                PromoClient.build_products(jobs[0]["products"], jobs[0].get("dimension"))[0],
                ensure_ascii=False))
        else:
            if getattr(a, "auto_split", False):
                expanded: list[dict] = []
                for j in jobs:
                    expanded.extend(PromoClient.promo_plan_split(j))
                if len(expanded) != len(jobs):
                    print(f"自动拆分: {len(jobs)} 个 plan → {len(expanded)} 个活动")
                jobs = expanded
            res = C.promo_create_batch(jobs, park_after=a.park_after,
                                       on_error="stop" if a.stop_on_error else "continue")
            ok = sum(1 for r in res if r["ok"])
            out = HERE / "notes" / "batch_result.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
            print(f"\n成功 {ok}/{len(res)}   → {out}")
            for r in res:
                if not r["ok"]:
                    print(f"  失败: {r['name']}  [{r.get('code')}] {r.get('error')}")

    elif a.cmd == "report":
        print(C.promo_report(a.promotion_id))

    elif a.cmd == "detail":
        _print(C.promo_detail(a.promotion_id))

    elif a.cmd == "find":
        hits = C.promo_find_by_product(a.product_id)
        print(f"商品 {a.product_id} 命中 {len(hits)} 个活动:")
        for it in hits:
            print(f"  {it['id']}  [{STATUS.get(it['status'], it['status'])}]  "
                  f"{it['period']['start_time']}~{it['period']['end_time']}  {it['name'][:34]}")

    elif a.cmd == "export":
        n = C.promo_export(a.out)
        print(f"已导出 {n} 个活动的完整明细 → {a.out}")

    elif a.cmd == "scan":
        hits = C.scan_product_promotions(a.product_id, with_sku_detail=not a.no_sku)
        print(f"商品 {a.product_id} 参与 {len(hits)} 个活动:")
        for h in hits:
            print(f"  {h['promotion_id']}  [{h.get('type_text')}/{h.get('status_text')}]  "
                  f"{str(h.get('name'))[:34]}")
            if h.get("skus"):
                for sk in h["skus"]:
                    print(f"      {sk['sku_id']}  {str(sk.get('sku_name'))[:12]:14}"
                          f" 现价={sk.get('fixed_price') or '-'}")
            if h.get("purchase_limit"):
                print(f"      总限购={h['purchase_limit'].get('purchase_max_quantity')}")

    elif a.cmd == "set-price":
        prices: dict = {}
        for kv in a.sku:
            if "=" in kv:
                k, v = kv.split("=", 1)
                prices[k.strip()] = v.strip()
        acts = a.activity or None
        if not prices:
            if not a.price:
                sys.exit("需要 --sku SKU=价 或 --price 统一定价")
            # 不指定 SKU 时，按活动里的现价统一定价
            targets = acts or [h["promotion_id"] for h in
                               C.scan_product_promotions(a.product_id, with_sku_detail=False)
                               if h.get("type") == 2]
            for pid in targets:
                detail = C.list_products_by_cursor(pid, limit=100)
                mine = next((x for x in detail
                             if str(x.get("product_id")) == str(a.product_id)), None)
                for sk in ((mine or {}).get("skus") or []):
                    prices[str(sk.get("sku_id"))] = str(a.price)
        res = C.update_product_fixed_price(a.product_id, prices,
                                           promotion_ids=acts, dry_run=a.dry_run)
        for r in res:
            flag = "OK " if r.get("ok") else "ERR"
            print(f"  [{flag}] {r.get('promotion_id')}  "
                  f"{r.get('error') or ('dry-run' if r.get('dry_run') else 'code=' + str(r.get('code')))}")

    elif a.cmd == "list-products":
        rows = C.promo_list_products(a.promotion_id)
        print(f"共 {len(rows)} 个商品:")
        for it in rows:
            sr = it.get("sale_price_range") or {}
            print(f"  {it.get('product_id')}  {(it.get('product_name') or '')[:34]:36} "
                  f"stock={it.get('inventory_quantity'):<6} "
                  f"price={sr.get('lowest_price')}~{sr.get('highest_price')}  "
                  f"sku={it.get('selected_sku_count')}/{it.get('total_sku_count')}")

    elif a.cmd == "create":
        products = [{"product_id": p.strip(), "discount_percentage": str(a.discount)}
                    for p in a.product.split(",") if p.strip()]
        payload = {"period": {"start_time": _ts(a.start), "end_time": _ts(a.end)},
                   "promotion_name": a.name,
                   "promotion_limit_dimension": a.dimension,
                   "products_single_discount": products}
        print("payload:", json.dumps(payload, ensure_ascii=False))
        if a.dry_run:
            print("--dry-run，未调用")
            return
        pid = C.discount_create(name=a.name, start=a.start, end=a.end,
                                products=products, dimension=a.dimension)
        print(f"✅ 已创建 promotion_id = {pid}")
    elif a.cmd == "update":
        _print(C.discount_update(a.promotion_id, name=a.name, start=a.start, end=a.end))
    elif a.cmd == "park":
        _print(C.discount_park(a.promotion_id, days=a.days))
        print(f"✅ {a.promotion_id} 已推到 {a.days} 天后")


if __name__ == "__main__":
    try:
        main()
    except PromoError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
