#!/usr/bin/env python3
"""TikTok 商品上架 —— 纯 API 客户端。

不用 UI。核心思路：
  1. 从一个「模板商品」拉全量数据（GET /product/local/product/get）
  2. 把它改写成 create 载荷（去掉 product_id，换掉变量字段）
  3. POST /product/local/product/create

模板商品的作用是提供那些**无法凭空构造**的常量：
  - product_properties 的属性值 id（如「中国」=7683XXXXXXXXXX22、「CPNF」=1298953）
  - sale_property 的属性 id（如「Thông số」=100089）
  - components 里 product_property_normal / product_property_compliance 的 JSON
  - schema_context 的形状

用法:
    python3 tt_product.py --template 1737XXXXXXXXXX80 --dump-template
    python3 tt_product.py --template 1737XXXXXXXXXX80 \
        --name "新品名" --price 190000 --stock 50 --create
    python3 tt_product.py --list
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hub_headless import attach  # noqa: E402

CDP_PORT = int(os.environ.get("TT_CDP_PORT", "CDP_PORT"))
SELLER = os.environ.get("TT_SELLER", "7494XXXXXXXXXX00")
AID = "4068"
APP = "i18n_ecom_shop"
HOST = "https://seller-vn.tiktok.com"

# 页面内 API 桥（自动带 cookie / CSRFToken / fp）
BRIDGE = r"""
window.__tt = {
  base: (extra) => {
    const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
      oec_seller_id: '__SELLER__', seller_id: '__SELLER__',
      aid: '__AID__', app_name: '__APP__'});
    for (const [k, v] of Object.entries(extra || {})) q.set(k, String(v));
    return q.toString();
  },
  csrf: () => decodeURIComponent((document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''),
  post: async (path, body, extra) => {
    const r = await fetch(path + '?' + window.__tt.base(extra), {
      method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/json; charset=utf-8',
                'X-CSRFToken': window.__tt.csrf(), 'Accept': 'application/json'},
      body: JSON.stringify(body),
    });
    return {status: r.status, body: await r.text()};
  },
  get: async (path, extra) => {
    const r = await fetch(path + '?' + window.__tt.base(extra), {
      credentials: 'include', headers: {'Accept': 'application/json'}});
    return {status: r.status, body: await r.text()};
  },
};
'ready'
""".replace("__SELLER__", SELLER).replace("__AID__", AID).replace("__APP__", APP)


def _bridge(page):
    page.js(BRIDGE)


def api_get(path: str, extra: dict | None = None) -> dict:
    with attach(CDP_PORT) as p:
        _bridge(p)
        r = p.js("window.__tt.get(" + json.dumps(path) + ", " + json.dumps(extra or {}) + ")",
                 await_promise=True, timeout=180)
    return json.loads(r["body"])


def api_post(path: str, body: dict, extra: dict | None = None) -> dict:
    with attach(CDP_PORT) as p:
        _bridge(p)
        r = p.js("window.__tt.post(" + json.dumps(path) + ", " + json.dumps(body) + ", "
                 + json.dumps(extra or {}) + ")", await_promise=True, timeout=240)
    return json.loads(r["body"])


def get_product(pid: str) -> dict:
    j = api_get("/api/v1/product/local/product/get", {"product_id": pid})
    if j.get("code") != 0:
        raise RuntimeError(f"取商品失败: {j.get('code')} {j.get('message')}")
    return (j.get("data") or {}).get("product") or {}


def list_products(tab: str = "2", size: int = 8) -> dict:
    return api_get("/api/v1/product/local/products/list", {
        "page_number": "1", "page_size": str(size), "sku_number": "0",
        "is_need_target_stock": "true", "same_product_page_size": "3",
        "product_sort_fields": "3", "product_sort_types": "0", "tab_id": tab})


# ---------------------------------------------------------------- 会话内自增 id
_ID_SEQ = [900]
_ID_LOCK = time.time()


def local_id() -> str:
    """页面表单给临时对象用的本地 id（新 SKU 需要）。"""
    _ID_SEQ[0] += 1
    return str(_ID_SEQ[0])


def new_id() -> str:
    """服务端风格的长 id。"""
    return str(int(time.time() * 1000)) + "000"


def build_create_payload(tpl: dict, *, name: str | None = None,
                         prices: list[str] | None = None,
                         stocks: list[int] | None = None,
                         seller_skus: list[str] | None = None,
                         var_names: list[str] | None = None,
                         image_uri: str | None = None,
                         desc_html: str | None = None,
                         sku_image_uris: list[str] | None = None) -> dict:
    """从模板商品改写出一份 create 载荷。

    模板提供所有常量；这里只替换真正变化的部分。
    """
    # ---- 顶层：去掉 product_id，其余照抄
    out = {k: v for k, v in tpl.items()
           if k not in ("product_id", "pre_build_product_id", "product_status", "audit_status",
                        "product_status_view", "sale_price_ranges", "showcase_bind_count",
                        "suspend_reason", "combo_product_info", "model_ref", "create_time")}
    out["product_name"] = name or tpl.get("product_name")
    out["product_source"] = 4
    out["page_type"] = 1
    out["from_new_oc"] = False
    out["publish_event_param"] = {"click_source": 1, "biz_scene": ["hazmat"],
                                  "session_id": new_id()[:26]}
    out["comp_submit_data"] = {}
    out["logistics_services"] = []

    # schema_context：保留模板形状，只换 category_id / 去掉 product_id
    sc = json.loads(json.dumps(tpl.get("schema_context") or {}, ensure_ascii=False))
    sc.pop("product_id", None)
    if not sc:
        sc = {"page": 3, "product_type_list": ["ProductType_Normal"],
              "extra": {"capabilities": "standard_product_capability",
                        "identity": "GEC.TTS.SEA.VN", "session_id": new_id()[:26]}}
    sc["category_id"] = str(out.get("category_id") or tpl.get("category_id") or "")
    sc.setdefault("page", 3)
    sc.setdefault("product_type_list", ["ProductType_Normal"])
    sc.setdefault("get_audit_version", True)
    out["schema_context"] = sc
    # 顶层 category_id 确保是字符串
    out["category_id"] = str(tpl.get("category_id") or "")

    # ---- 主图
    imgs = tpl.get("images") or []
    if image_uri:
        base = imgs[0] if imgs else {}
        out["images"] = [{"uri": image_uri,
                          "url_list": [u.replace(_uri_of(base), image_uri)
                                       for u in (base.get("url_list") or [])] or [],
                          "width": base.get("width", 800),
                          "height": base.get("height", 800)}]
    else:
        out["images"] = imgs

    # ---- 描述
    out["description"] = desc_html if desc_html is not None else tpl.get("description")

    # ---- 属性：照抄模板（值 id 是服务端发的，不能凭空造）
    out["product_properties"] = tpl.get("product_properties") or []

    # ---- 变体
    tpl_sp = (tpl.get("sale_properties") or [])
    tpl_vals = (tpl_sp[0].get("values") or []) if tpl_sp else []
    if var_names and tpl_sp:
        sp = json.loads(json.dumps(tpl_sp[0], ensure_ascii=False))
        sp["has_image"] = bool(sku_image_uris)
        sp["is_custom"] = True
        newvals = []
        for i, vn in enumerate(var_names):
            v = {"id": local_id(), "name": vn, "is_custom": True}
            if sku_image_uris and i < len(sku_image_uris) and tpl_vals:
                # 借用模板里的图片结构
                src = next((x for x in tpl_vals if x.get("image")), None)
                if src:
                    im = json.loads(json.dumps(src["image"], ensure_ascii=False))
                    im["uri"] = sku_image_uris[i]
                    v["image"] = im
            newvals.append(v)
        sp["values"] = newvals
        out["sale_properties"] = [sp]
    else:
        out["sale_properties"] = tpl_sp

    # ---- SKU
    tpl_skus = tpl.get("skus") or []
    base_sku = json.loads(json.dumps(tpl_skus[0], ensure_ascii=False)) if tpl_skus else {}
    n = len(out["sale_properties"][0].get("values") or []) if out["sale_properties"] else 1
    n = max(1, n)
    sp_id = out["sale_properties"][0]["id"] if out["sale_properties"] else None
    vals = out["sale_properties"][0].get("values") or [] if out["sale_properties"] else []
    wh = base_sku.get("quantities", [{}])[0].get("warehouse_id") if base_sku else None

    skus = []
    for i in range(n):
        sk = json.loads(json.dumps(base_sku, ensure_ascii=False)) if base_sku else {}
        sk["id"] = new_id() + str(i)
        sk["seller_sku"] = (seller_skus[i] if seller_skus and i < len(seller_skus)
                            else (sk.get("seller_sku") or ""))
        if vals and sp_id:
            sk["properties"] = [{"id": sp_id,
                                 "name": out["sale_properties"][0].get("text"),
                                 "value_id": vals[i]["id"],
                                 "value_name": vals[i]["name"]}]
        else:
            sk["properties"] = []
        price = (prices[i] if prices and i < len(prices)
                 else (prices[0] if prices else None))
        bp = sk.get("base_price") or {"region": "VN", "currency": "VND"}
        if price:
            bp["list_price"] = str(price)
            bp["sale_price"] = str(price)
            bp["list_price_display"] = ""
            bp["sale_price_display"] = ""
        bp.setdefault("region", "VN")
        bp.setdefault("currency", "VND")
        bp["localized_dutiable_price"] = bp.get("localized_dutiable_price", "0")
        bp["audit_list_price"] = bp.get("audit_list_price", "")
        sk["base_price"] = bp
        qty = (stocks[i] if stocks and i < len(stocks) else (stocks[0] if stocks else 100))
        sk["quantities"] = [{"available_quantity": int(qty), "quantity_variation": 0,
                             "warehouse_id": wh}]
        sk["pre_order_ship_day"] = 0
        sk["fulfillment_info"] = {}
        sk["purchase_order_quantity_limit"] = {}
        sk["fees"] = []
        skus.append(sk)
    out["skus"] = skus

    # ---- components：标题 + 属性 JSON 要与顶层对齐
    comps = json.loads(json.dumps(tpl.get("components") or [], ensure_ascii=False))
    for c in comps:
        if c.get("id") == "title_comp":
            c["value"] = json.dumps(out["product_name"], ensure_ascii=False)
        if c.get("id") == "product_property_normal":
            props = {str(p["id"]): [] for p in out["product_properties"]
                     if str(p.get("id")) in ("100149", "100216", "100334", "100335", "100337",
                                             "100338", "100340", "100341", "100342", "100344",
                                             "100345", "100346", "100347", "100357", "101310",
                                             "101489", "101490", "101574", "101610", "101611",
                                             "101614", "101623", "101624", "101625", "101626",
                                             "101627", "101734")}
            for p in out["product_properties"]:
                key = str(p.get("id"))
                if key in props:
                    props[key] = [{"id": v.get("id"), "name": v.get("name"),
                                   "is_custom": v.get("is_custom", False)}
                                  for v in (p.get("values") or [])]
            c["value"] = json.dumps(props, ensure_ascii=False)
        if c.get("id") == "product_property_compliance":
            comp = {str(p["id"]): [] for p in out["product_properties"]
                    if str(p.get("id")) in ("102872", "102999", "103000", "103001")}
            for p in out["product_properties"]:
                key = str(p.get("id"))
                if key in comp:
                    comp[key] = [{"id": v.get("id"), "name": v.get("name"),
                                  "is_custom": v.get("is_custom", False)}
                                 for v in (p.get("values") or [])]
            if comp:
                c["value"] = json.dumps(comp, ensure_ascii=False)
    out["components"] = comps
    return out


def _uri_of(img: dict) -> str:
    return (img or {}).get("uri", "")


def create_product(payload: dict) -> dict:
    return api_post("/api/v1/product/local/product/create", payload)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=None, help="模板商品 id")
    ap.add_argument("--dump-template", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tab", default="2")
    ap.add_argument("--name", default=None)
    ap.add_argument("--price", default=None, help="单个价格，或逗号分隔多价")
    ap.add_argument("--stock", default="100", help="单个库存，或逗号分隔")
    ap.add_argument("--sku", default=None, help="逗号分隔的商家 SKU")
    ap.add_argument("--variants", default=None, help="逗号分隔的变体名（如 1,2,3）")
    ap.add_argument("--image", default=None, help="主图 uri")
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="只打印载荷，不发请求")
    a = ap.parse_args()

    if a.list:
        j = list_products(a.tab)
        d = j.get("data") or {}
        print(f"tab={a.tab} total={d.get('total_product_count')}")
        for x in (d.get("products") or []):
            print(f"  {x.get('product_id')}  {(x.get('product_name') or '')[:60]}")
        return 0

    if not a.template:
        ap.error("需要 --template")

    tpl = get_product(a.template)
    print(f"模板: {tpl.get('product_name','')[:60]}")
    print(f"  SKU {len(tpl.get('skus') or [])} 个, "
          f"属性 {len(tpl.get('product_properties') or [])} 项, "
          f"变体属性 {len(tpl.get('sale_properties') or [])} 组")
    if a.dump_template:
        out = os.path.join(HERE, "notes", "tt_product_template.json")
        json.dump(tpl, open(out, "w"), ensure_ascii=False, indent=2)
        print("→", out)
        return 0

    prices = a.price.split(",") if a.price else None
    stocks = [int(x) for x in a.stock.split(",")] if a.stock else None
    skus = a.sku.split(",") if a.sku else None
    variants = a.variants.split(",") if a.variants else None

    payload = build_create_payload(tpl, name=a.name, prices=prices, stocks=stocks,
                                   seller_skus=skus, var_names=variants, image_uri=a.image)
    txt = json.dumps(payload, ensure_ascii=False)
    print(f"\n载荷 {len(txt)} 字符, SKU {len(payload.get('skus') or [])} 个")
    for sk in payload.get("skus") or []:
        bp = sk.get("base_price") or {}
        q = (sk.get("quantities") or [{}])[0].get("available_quantity")
        print(f"  {sk.get('seller_sku')!r:<16} {bp.get('sale_price'):>8} {bp.get('currency')}  qty={q}")

    out = os.path.join(HERE, "notes", "tt_create_payload_built.json")
    json.dump(payload, open(out, "w"), ensure_ascii=False, indent=2)
    print("载荷 →", out)

    if a.dry_run:
        return 0
    if not a.create:
        print("\n(加 --create 才会真的提交)")
        return 0

    print("\n提交…")
    r = create_product(payload)
    print("status:", r.get("status"), " code:", r.get("code"), " msg:", r.get("message"))
    print(json.dumps(r, ensure_ascii=False)[:800])
    json.dump(r, open(os.path.join(HERE, "notes", "tt_create_result.json"), "w"),
              ensure_ascii=False, indent=2)
    return 0 if r.get("code") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
