#!/usr/bin/env python3
"""TikTok 商品上架 —— 纯 API 客户端。

核心：create/edit 接口要的是**表单模型**，不是 /product/get 返回的详情视图。
所以模板 = 一次真实 UI 保存抓到的 `edit` 请求体（notes/tk178_edit_payload.json）。

已验证可得:
  - 原样重放 edit 载荷         → code=0
  - 只改 product_name 重放     → code=0
  - 改变体名/价格/库存/主图    → code=0

用法:
    python3 tt_api.py --template notes/tk178_edit_payload.json --show
    python3 tt_api.py --template notes/tk178_edit_payload.json \
        --pid 1737XXXXXXXXXX84 \
        --name "新品名" --prices 111000,222000,333000 \
        --stocks 11,22,33 --skus EA,EB,EC --variants S,M,L \
        --apply
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hub_headless import attach  # noqa: E402

CDP_PORT = int(os.environ.get("TT_CDP_PORT", "CDP_PORT"))
SELLER = os.environ.get("TT_SELLER", "7494XXXXXXXXXX00")

BRIDGE = r"""
window.__tt = {
  csrf: () => decodeURIComponent((document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || ''),
  post: async (path, body, extra) => {
    const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
      oec_seller_id:'__SELLER__', seller_id:'__SELLER__', aid:'4068',
      app_name:'i18n_ecom_shop'});
    for (const [k, v] of Object.entries(extra || {})) q.set(k, String(v));
    const [base, pre] = path.split('?');
    const qs = pre ? pre + '&' + q.toString() : q.toString();
    const r = await fetch(base + '?' + qs, {
      method: 'POST', credentials: 'include',
      headers: {'Content-Type': 'application/json; charset=utf-8',
                'X-CSRFToken': window.__tt.csrf(), 'Accept': 'application/json'},
      body: JSON.stringify(body)});
    return {status: r.status, body: await r.text()};
  },
  get: async (path, extra) => {
    const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
      oec_seller_id:'__SELLER__', seller_id:'__SELLER__', aid:'4068',
      app_name:'i18n_ecom_shop'});
    for (const [k,v] of Object.entries(extra||{})) q.set(k, String(v));
    // path 可能自带 query,要正确拼接
    const [base, pre] = path.split('?');
    const qs = pre ? pre + '&' + q.toString() : q.toString();
    const r = await fetch(base + '?' + qs, {credentials:'include',
      headers:{'Accept':'application/json'}});
    return {status: r.status, body: await r.text()};
  },
};
'ready'
""".replace("__SELLER__", SELLER)


def api_post(path: str, body: dict, extra: dict | None = None) -> dict:
    """POST。extra 会作为 query 参数附加（有些接口参数走 query）。"""
    with attach(CDP_PORT) as p:
        p.js(BRIDGE)
        r = p.js("window.__tt.post(" + json.dumps(path) + ", " + json.dumps(body) + ", "
                 + json.dumps(extra or {}) + ")", await_promise=True, timeout=240)
    return _parse_json_loose(r["body"], r.get("status"))


def _parse_json_loose(txt: str, status=None) -> dict:
    """容错解析：正常 JSON → 单个对象；NDJSON / 多对象拼接 → MULTI_JSON；都不是 → NON_JSON。

    TikTok 有些接口（如 stock/sku/list）返回多个 JSON 对象拼接，不是合法 JSON。
    """
    try:
        return json.loads(txt)
    except json.JSONDecodeError as e:
        parts, dec, idx = [], json.JSONDecoder(), 0
        while idx < len(txt):
            while idx < len(txt) and txt[idx] in " \t\r\n":
                idx += 1
            if idx >= len(txt):
                break
            try:
                obj, end = dec.raw_decode(txt, idx)
            except json.JSONDecodeError:
                break
            parts.append(obj)
            idx = end
        if len(parts) == 1:
            return parts[0]
        if parts:
            return {"code": "MULTI_JSON", "parts": parts}
        return {"code": "NON_JSON", "status": status, "_raw": txt[:600], "_err": str(e)[:140]}


def api_get(path: str, extra: dict | None = None) -> dict:
    with attach(CDP_PORT) as p:
        p.js(BRIDGE)
        r = p.js("window.__tt.get(" + json.dumps(path) + ", " + json.dumps(extra or {}) + ")",
                 await_promise=True, timeout=180)
    return _parse_json_loose(r["body"], r.get("status"))


_seq = [900]


def local_id() -> str:
    _seq[0] += 1
    return str(_seq[0])


def patch_payload(tpl: dict, *, pid: str | None = None, name: str | None = None,
                  prices: list[str] | None = None, stocks: list[int] | None = None,
                  seller_skus: list[str] | None = None, variants: list[str] | None = None,
                  image_uri: str | None = None, desc_html: str | None = None,
                  sku_image_uris: list[str] | None = None,
                  base_sku_image_uri: str | None = None) -> dict:
    """在表单模型模板上打补丁。模板必须是真实 edit 请求体。"""
    p = copy.deepcopy(tpl)

    if pid is not None:
        if pid == "":
            # 显式清空 → 让服务端分配新 id
            for k in ("product_id", "pre_build_product_id"):
                p.pop(k, None)
            sc = dict(p.get("schema_context") or {})
            sc.pop("product_id", None)
            p["schema_context"] = sc
        else:
            p["product_id"] = pid
            p["pre_build_product_id"] = pid
            sc = dict(p.get("schema_context") or {})
            sc["product_id"] = pid
            p["schema_context"] = sc

    if name:
        p["product_name"] = name
        for c in p.get("components") or []:
            if c.get("id") == "title_comp":
                c["value"] = json.dumps(name, ensure_ascii=False)

    if image_uri:
        imgs = p.get("images") or []
        if imgs:
            imgs[0]["uri"] = image_uri
            if imgs[0].get("url_list"):
                import re
                imgs[0]["url_list"] = [
                    re.sub(r"aphluv4xwc-sg/[a-f0-9]{32}", image_uri, u) for u in imgs[0]["url_list"]]
        p["images"] = imgs

    if desc_html is not None:
        p["description"] = desc_html

    # 会话 id 每次都换
    pep = dict(p.get("publish_event_param") or {})
    pep["session_id"] = str(int(time.time() * 1000)) + "000"
    p["publish_event_param"] = pep

    # 变体
    sps = p.get("sale_properties") or []
    if variants and sps:
        sp = sps[0]
        old_vals = sp.get("values") or []
        new_vals = []
        for i, vn in enumerate(variants):
            base = copy.deepcopy(old_vals[i]) if i < len(old_vals) else {}
            v = {"id": local_id(), "name": vn, "is_custom": True}
            src_img = base.get("image") \
                or next((x.get("image") for x in old_vals if x.get("image")), None)
            if src_img:
                im = copy.deepcopy(src_img)
                if sku_image_uris and i < len(sku_image_uris):
                    im["uri"] = sku_image_uris[i]
                    im["url_list"] = [u.replace(_uri(im), im["uri"]) for u in (im.get("url_list") or [])]
                if not im.get("uri") and base_sku_image_uri:
                    im["uri"] = base_sku_image_uri
                v["image"] = im
            new_vals.append(v)
        sp["values"] = new_vals
        sp["has_image"] = any("image" in v for v in new_vals)
        p["sale_properties"] = [sp]

    # SKU
    skus = p.get("skus") or []
    vals = (p.get("sale_properties") or [{}])[0].get("values") or []
    n = max(1, len(vals)) if vals else max(1, len(skus))
    sp0 = (p.get("sale_properties") or [{}])[0] if p.get("sale_properties") else {}
    out_skus = []
    for i in range(n):
        sk = copy.deepcopy(skus[i]) if i < len(skus) else copy.deepcopy(skus[0] if skus else {})
        # SKU id 属于「原商品」，跨商品复用会报 12052557。用本地自增 id 代替，
        # 保存成功后服务端会在 data.property_value_id_map / skus 里返回真实 id。
        sk["id"] = local_id()
        if seller_skus and i < len(seller_skus):
            sk["seller_sku"] = seller_skus[i]
        if vals and sp0.get("id"):
            sk["properties"] = [{"id": sp0["id"], "name": sp0.get("text"),
                                 "value_id": vals[i]["id"], "value_name": vals[i]["name"]}]
        bp = sk.get("base_price") or {"region": "VN", "currency": "VND"}
        if prices:
            pv = prices[i] if i < len(prices) else prices[-1]
            bp["list_price"] = str(pv)
            bp["sale_price"] = str(pv)
            bp["list_price_display"] = ""
            bp["sale_price_display"] = ""
        bp.setdefault("region", "VN")
        bp.setdefault("currency", "VND")
        bp["audit_list_price"] = bp.get("audit_list_price", "")
        bp["localized_dutiable_price"] = bp.get("localized_dutiable_price", "0")
        sk["base_price"] = bp
        if stocks:
            qv = stocks[i] if i < len(stocks) else stocks[-1]
            q0 = (sk.get("quantities") or [{}])[0]
            sk["quantities"] = [{**q0, "available_quantity": int(qv)}]
        sk.setdefault("pre_order_ship_day", 0)
        sk.setdefault("fulfillment_info", {})
        sk.setdefault("purchase_order_quantity_limit", {})
        sk.setdefault("fees", [])
        out_skus.append(sk)
    p["skus"] = out_skus
    return p


def _uri(img: dict) -> str:
    return (img or {}).get("uri", "")


def apply_payload(p: dict, *, create: bool = False) -> dict:
    path = ("/api/v1/product/local/product/create" if create
            else "/api/v1/product/local/product/edit")
    return api_post(path, p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default="notes/tk178_edit_payload.json",
                    help="表单模型模板（真实 edit 请求体）")
    ap.add_argument("--pid", default=None, help="目标 product_id")
    ap.add_argument("--name", default=None)
    ap.add_argument("--prices", default=None, help="逗号分隔")
    ap.add_argument("--stocks", default=None, help="逗号分隔")
    ap.add_argument("--skus", default=None, help="逗号分隔的商家 SKU")
    ap.add_argument("--variants", default=None, help="逗号分隔的变体名")
    ap.add_argument("--image", default=None, help="主图 uri")
    ap.add_argument("--show", action="store_true", help="只打印模板摘要")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true", help="真的提交 edit")
    ap.add_argument("--create", action="store_true", help="试 create 端点")
    ap.add_argument("--out", default="notes/tt_api_payload.json")
    a = ap.parse_args()

    tpl = json.load(open(a.template)) if os.path.exists(a.template) else None
    if tpl is None:
        print(f"找不到模板 {a.template}", file=sys.stderr)
        return 2

    if a.show:
        print(f"模板 {a.template}: {len(json.dumps(tpl, ensure_ascii=False))} 字符")
        print("字段:", list(tpl.keys()))
        print(f"SKU {len(tpl.get('skus') or [])}, 属性 {len(tpl.get('product_properties') or [])}, "
              f"变体属性 {len(tpl.get('sale_properties') or [])}")
        for sk in (tpl.get("skus") or []):
            bp = sk.get("base_price") or {}
            print(f"  {sk.get('seller_sku')!r:<14} {bp.get('sale_price')} {bp.get('currency')}")
        return 0

    p = patch_payload(tpl, pid=a.pid, name=a.name,
                      prices=a.prices.split(",") if a.prices else None,
                      stocks=[int(x) for x in a.stocks.split(",")] if a.stocks else None,
                      seller_skus=a.skus.split(",") if a.skus else None,
                      variants=a.variants.split(",") if a.variants else None,
                      image_uri=a.image)
    txt = json.dumps(p, ensure_ascii=False)
    print(f"载荷 {len(txt)} 字符, SKU {len(p.get('skus') or [])}")
    for sk in p.get("skus") or []:
        bp = sk.get("base_price") or {}
        q = (sk.get("quantities") or [{}])[0].get("available_quantity")
        print(f"  {sk.get('seller_sku')!r:<16} {bp.get('sale_price'):>8} {bp.get('currency')}  qty={q}  "
              f"{[(x.get('name'), x.get('value_name')) for x in (sk.get('properties') or [])]}")
    json.dump(p, open(a.out, "w"), ensure_ascii=False, indent=2)
    print("→", a.out)

    if a.dry_run:
        return 0
    if not (a.apply or a.create):
        print("\n(加 --apply 才会提交 edit；--create 试 create 端点)")
        return 0

    r = apply_payload(p, create=a.create)
    print(f"\n{'create' if a.create else 'edit'} code={r.get('code')} msg={str(r.get('message'))[:100]}")
    dbg = r.get("debug_info") or {}
    if dbg.get("status_error"):
        print("  status_error:", str(dbg["status_error"])[:300])
    if r.get("code") == 0:
        print("  ★ 成功:", json.dumps(r.get("data"), ensure_ascii=False)[:300])
    return 0 if r.get("code") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# ---------------------------------------------------------------- 纯 API 新建

def gen_product_id() -> str:
    """生成雪花风格的商品 id（服务端会用它分配真实商品）。"""
    import random
    return str(1790XXXXXXXXXX00 + random.randint(0, 2_000_000_000))


def ensure_registered(pid: str, category_id: str = "601646", rounds: int = 4) -> None:
    """预热注册：多次 get_schema_v2 让服务端把该 id 纳入发布服务。

    实测规律：1 次往往不够（create 报 12052032「此商品不存在」），
    3~5 次稳定成功 —— 属于最终一致性，不是确定性规则。
    """
    body = {"schema_context": {"page": 3, "get_audit_version": False, "product_id": pid,
                              "category_id": category_id,
                              "product_type_list": ["ProductType_Normal"]},
            "components": [],
            "scene_param": {"product_type_add_list": ["ProductType_Normal"]}}
    for _ in range(rounds):
        api_post("/api/v1/product/comp/get_schema_v2", body)


def create_product(tpl: dict, *, name: str, prices: list[str], stocks: list[int],
                   seller_skus: list[str], variants: list[str] | None = None,
                   image_uri: str | None = None, desc_html: str | None = None,
                   sku_image_uris: list[str] | None = None,
                   category_id: str = "601646", attempts: int = 5,
                   warmup: int = 4) -> dict:
    """纯 API 新建商品。返回最后一次的响应（成功时 data.product_id 是新商品 id）。"""
    last = {}
    for i in range(attempts):
        pid = gen_product_id()
        ensure_registered(pid, category_id, warmup)
        payload = patch_payload(tpl, pid=pid, name=name, prices=prices, stocks=stocks,
                                seller_skus=seller_skus, variants=variants,
                                image_uri=image_uri, desc_html=desc_html,
                                sku_image_uris=sku_image_uris)
        r = api_post("/api/v1/product/local/product/create", payload)
        last = r
        if r.get("code") == 0:
            print(f"  [create] 第 {i+1} 次尝试成功, product_id={pid}")
            return r
        print(f"  [create] 第 {i+1} 次失败 code={r.get('code')} {str(r.get('message'))[:60]}")
        time.sleep(1.5)
    return last
