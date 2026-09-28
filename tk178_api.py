#!/usr/bin/env python3
"""TK178 上架 —— 纯 API 客户端。

不再碰 UI。所有请求从页面上下文 fetch（自动带 cookie / CSRFToken / fp）。

已知：
  - 创建接口  POST /api/v1/product/local/product/create
  - 预检接口  POST /api/v1/product/local/product/precheck   （纯校验，无副作用）
  - 图片上传  GET  /api/v1/multimedia/image/upload_token/get → 上传到 TOS → GET /api/v1/multimedia/image/get?uri=
  - 字段结构  从 notes/tk178_create_payload.json 的真实 draft/save 请求取得

    python3 tk178_api.py --upload          # 上传图片，打印 uri
    python3 tk178_api.py --precheck        # 只校验，看服务端报什么
    python3 tk178_api.py --create          # 真建
    python3 tk178_api.py --list            # 确认商品是否出现
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_headless import attach  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CDP_PORT = int(os.environ.get("TK178_CDP_PORT", "CDP_PORT"))
IMG = os.path.join(HERE, "notes", "product_img", "eye_cream_main.jpg")

SELLER = "7494XXXXXXXXXX00"
AID = "4068"
APP = "i18n_ecom_shop"
CATEGORY = "601646"            # 美妆个护 > 护肤品 > 眼部护理
WAREHOUSE = "7659XXXXXXXXXX08"   # Laojie(默认仓)
SALE_PRICE = "200000"          # 20 万越南盾
STOCK = "100"
PRODUCT_NAME = ("Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g - "
                "Giảm Thâm Quầng, Sáng Da, Chống Lão Hóa Vùng Mắt")
DESCRIPTION = """<p>Kem Dưỡng Mắt KORMESIC Multi Effect Eye Cream 20g</p>
<p>Công thức làm sáng chuyên biệt giúp lấy lại làn da mịn màng, rạng rỡ cho vùng da quanh mắt.</p>
<p>THÀNH PHẦN CHÍNH:<br/>- AXIT ASCORBIC: Giảm sạm màu, bề mặt và vết thâm.<br/>
- AXIT CITRIC: Làm sáng hiệp đồng ở lớp trung bình, thúc đẩy tái tạo da.<br/>
- NIACINAMIDE: Ức chế melanin ở lớp sâu, giúp da đều màu và sáng mịn.</p>
<p>CÔNG DỤNG:<br/>- Giảm thâm quầng và bọng mắt<br/>- Dưỡng sáng vùng da quanh mắt<br/>
- Hỗ trợ làm mờ nếp nhăn nhỏ<br/>- Cấp ẩm, giữ vùng mắt mềm mại</p>
<p>CÁCH DÙNG: Lấy một lượng nhỏ kem, chấm nhẹ quanh vùng mắt rồi vỗ nhẹ cho thấm. Dùng 2 lần mỗi ngày.</p>
<p>THÔNG TIN SẢN PHẨM:<br/>- Dung tích: 20g (0.71oz)<br/>- Hạn sử dụng: 3 năm kể từ ngày sản xuất<br/>
- Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp</p>"""

# 属性值:从真实 draft/save payload 抄的 id
PROP_LICENSE_TYPE = {"id": "102872", "value": {"id": "1298953",
                     "name": "Cosmetic product notification form (CPNF)"}}
PROP_LICENSE_NO = {"id": "102999", "value": {"id": "736", "name": "GNUMBER_REDACTED"}}
PROP_ORIGIN = {"id": "100149", "value": {"id": "1000850", "name": "中国"}}

PAGE_JS = r"""
window.__tt = {
  base: (extra) => {
    const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
      oec_seller_id: '__SELLER__', seller_id: '__SELLER__',
      aid: '__AID__', app_name: '__APP__'});
    for (const [k, v] of Object.entries(extra || {})) q.set(k, v);
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
    const t = await r.text();
    return {status: r.status, body: t};
  },
  get: async (path, extra) => {
    const r = await fetch(path + '?' + window.__tt.base(extra), {
      credentials: 'include', headers: {'Accept': 'application/json'}});
    return {status: r.status, body: await r.text()};
  },
};
'ready'
""".replace("__SELLER__", SELLER).replace("__AID__", AID).replace("__APP__", APP)


def upload_image(port: int) -> str | None:
    """走 token → 直传 TOS → image/get 拿 uri。"""
    b64 = base64.b64encode(open(IMG, "rb").read()).decode()
    print(f"图片 {os.path.getsize(IMG)} bytes")
    js = r"""
    (async () => {
      const b64 = "__B64__";
      // 1) 拿 STS 上传凭证
      const tok = await window.__tt.get('/api/v1/multimedia/image/upload_token/get');
      const tj = JSON.parse(tok.body);
      if (tj.code !== 0) return JSON.stringify({stage:'token', ...tj});
      const sts = tj.data;
      // 2) 直传。uri 由后端在签名里给定,这里用固定规范路径 + 随机 id
      const rand = [...crypto.getRandomValues(new Uint8Array(16))]
                   .map(b => b.toString(16).padStart(2,'0')).join('');
      const uri = 'tos-alisg-i-aphluv4xwc-sg/' + rand;
      const bin = atob(b64);
      const arr = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      const upUrl = 'https://tos-d-alisg16-up.byteoversea.com/upload/v1/' + uri;
      const up = await fetch(upUrl, {
        method: 'POST',
        headers: {'Authorization': 'STS ' + sts.session_token,
                  'Content-Type': 'application/octet-stream',
                  'X-Amz-Content-Sha256': 'UNSIGNED-PAYLOAD'},
        body: arr,
      });
      const upTxt = await up.text();
      // 3) 让后端登记
      const reg = await window.__tt.get('/api/v1/multimedia/image/get', {uri: uri});
      return JSON.stringify({stage:'done', uri, upStatus: up.status, upBody: upTxt.slice(0,200),
                             reg: reg.body.slice(0, 400)});
    })()
    """.replace("__B64__", b64)
    with attach(port) as p:
        p.js(PAGE_JS)
        r = json.loads(p.js(js, await_promise=True, timeout=240))
    print(json.dumps(r, ensure_ascii=False, indent=2)[:1200])
    return r.get("uri") if r.get("stage") == "done" else None


def build_payload(uri: str, *, draft_id: str | None = None) -> dict:
    """按真实 draft/save 结构组装 create 载荷,并补上价格/库存/图片。"""
    sku_id = str(int(time.time() * 1000)) + "000"
    p = {
        "product_name": PRODUCT_NAME,
        "category_id": CATEGORY,
        "brand_id": "0",
        "description": DESCRIPTION,
        "images": [{"uri": uri}],
        "product_properties": [
            {"id": PROP_LICENSE_TYPE["id"], "values": [PROP_LICENSE_TYPE["value"]]},
            {"id": PROP_LICENSE_NO["id"], "values": [PROP_LICENSE_NO["value"]]},
            {"id": PROP_ORIGIN["id"], "values": [PROP_ORIGIN["value"]]},
        ],
        "package_weight": "0.08",
        "package_dimension_unit": 2,
        "package_dimension_v2": {"package_width": "4", "package_height": "12",
                                 "package_length": "3"},
        "is_cod_open": True,
        "warehouse_id": WAREHOUSE,
        "product_source": 4,
        "logistics_services": [],
        "is_not_for_sale": False,
        "sale_platforms": [0],
        "is_auction_product": False,
        "sale_properties": [],
        "skus": [{
            "seller_sku": "KOR-EYE-20G",
            "quantities": [{"available_quantity": int(STOCK), "warehouse_id": WAREHOUSE}],
            "pre_order_ship_day": 0,
            # 价格字段结构抄自已有商品 base_price
            "base_price": {"region": "VN", "currency": "VND",
                           "list_price": None, "sale_price": SALE_PRICE},
            "fees": [],
            "properties": [],
        }],
        "is_merged_product": False,
        "components": [
            {"id": "title_comp", "value": json.dumps(PRODUCT_NAME)},
            {"id": "virtual_unboxing_comp", "value": "false"},
            {"id": "blindbox_comp", "value": "false"},
            {"id": "qualification_normal_comp",
             "value": json.dumps({"8647XXXXXXXXXX89": {"upload_res": {"images": [], "pdf_files": []}}})},
            {"id": "qualification_comp_cascade_compliance", "value": "{}"},
            {"id": "product_property_normal",
             "value": json.dumps({"100149": [{"id": "1000850", "name": "中国", "is_custom": False}]},
                                 ensure_ascii=False)},
            {"id": "product_property_compliance",
             "value": json.dumps({
                 "102872": [{"id": "1298953", "name": "Cosmetic product notification form (CPNF)",
                             "is_custom": False}],
                 "102999": [{"id": "736", "name": "GNUMBER_REDACTED", "is_custom": True}],
                 "103000": [], "103001": []}, ensure_ascii=False)},
        ],
        "is_operate_combo": False,
        "from_new_oc": False,
        "page_type": 1,
    }
    if draft_id:
        p["product_id"] = draft_id
        p["pre_build_product_id"] = draft_id
    return p


def call(port: int, fn: str, body: dict | None = None, extra: dict | None = None) -> dict:
    js = f"(async () => {{ window.__tt ||= null; return 'no'; }})()"
    with attach(port) as p:
        p.js(PAGE_JS)
        if fn == "precheck":
            r = p.js(f"window.__tt.post('/api/v1/product/local/product/precheck', "
                     f"{json.dumps(body)}, {json.dumps(extra or {})})",
                     await_promise=True, timeout=180)
        elif fn == "create":
            r = p.js(f"window.__tt.post('/api/v1/product/local/product/create', "
                     f"{json.dumps(body)}, {json.dumps(extra or {})})",
                     await_promise=True, timeout=240)
        elif fn == "list":
            r = p.js(f"window.__tt.get('/api/v1/product/local/products/list', "
                     f"{json.dumps(extra or {})})", await_promise=True, timeout=180)
        elif fn == "preload":
            r = p.js(f"window.__tt.get('/api/v1/product/product_creation/preload', "
                     f"{json.dumps(extra or {})})", await_promise=True, timeout=180)
        else:
            raise ValueError(fn)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--precheck", action="store_true")
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--preload", action="store_true")
    ap.add_argument("--uri", default=None, help="复用已上传的 uri")
    ap.add_argument("--price", default=SALE_PRICE)
    a = ap.parse_args()

    if a.upload:
        uri = upload_image(CDP_PORT)
        if uri:
            json.dump({"uri": uri}, open(os.path.join(HERE, "notes", "tk178_img_uri.json"), "w"))
            print("uri:", uri, "→ notes/tk178_img_uri.json")
        return 0 if uri else 1

    if a.preload:
        r = call(CDP_PORT, "preload")
        j = json.loads(r["body"])
        print("code:", j.get("code"), " 字段数:", len((j.get("data") or {})))
        return 0

    if a.list:
        r = call(CDP_PORT, "list", extra={"page_number": "1", "page_size": "10",
                                         "sku_number": "0", "is_need_target_stock": "true",
                                         "same_product_page_size": "3",
                                         "product_sort_fields": "3", "product_sort_types": "0",
                                         "tab_id": "2"})
        j = json.loads(r["body"])
        d = j.get("data") or {}
        print(f"code={j.get('code')} 总数={d.get('total_product_count')}")
        for x in (d.get("products") or [])[:10]:
            print(f"  {x.get('product_id')}  {(x.get('product_name') or '')[:60]}")
        return 0

    uri = a.uri
    if not uri:
        fp = os.path.join(HERE, "notes", "tk178_img_uri.json")
        if os.path.exists(fp):
            uri = json.load(open(fp)).get("uri")
    if not uri:
        print("没有 uri,先跑 --upload", file=sys.stderr)
        return 2

    payload = build_payload(uri, draft_id=None)
    if a.price:
        payload["skus"][0]["base_price"]["sale_price"] = a.price
    out = os.path.join(HERE, "notes", "tk178_api_payload.json")
    json.dump(payload, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"载荷 {len(json.dumps(payload))} 字节 → {out}")

    if a.precheck:
        r = call(CDP_PORT, "precheck", payload)
        print("precheck status:", r["status"])
        print(r["body"][:2500])
    if a.create:
        r = call(CDP_PORT, "create", payload)
        print("create status:", r["status"])
        print(r["body"][:2500])
        json.dump(r, open(os.path.join(HERE, "notes", "tk178_create_result.json"), "w"),
                  ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
