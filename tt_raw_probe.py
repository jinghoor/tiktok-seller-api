#!/usr/bin/env python3
"""原始响应诊断 —— 打印 status / content-type / body，绕过 JSON 解析。

用于排查「拿到非 JSON / 空响应」的接口。

    python3 tt_raw_probe.py [path method]
    python3 tt_raw_probe.py --suite        # 跑一组预设
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hub_headless import attach  # noqa: E402

SELLER = os.environ.get("TT_SELLER", "7494XXXXXXXXXX00")
PID = os.environ.get("TT_PID", "1790XXXXXXXXXX71")

RAW_JS = r"""
window.__ttRaw = async (path, method, extra, body) => {
  const q = new URLSearchParams({locale:'zh-CN', language:'zh-CN',
    oec_seller_id:'__SELLER__', seller_id:'__SELLER__', aid:'4068',
    app_name:'i18n_ecom_shop'});
  for (const [k, v] of Object.entries(extra || {})) q.set(k, String(v));
  const [base, pre] = path.split('?');
  const qs = pre ? pre + '&' + q.toString() : q.toString();
  const csrf = decodeURIComponent((document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || '');
  const opt = {method, credentials: 'include',
               headers: {'Accept': 'application/json', 'X-CSRFToken': csrf}};
  if (body !== null && method !== 'GET') {
    opt.headers['Content-Type'] = 'application/json; charset=utf-8';
    opt.body = JSON.stringify(body);
  }
  const r = await fetch(base + '?' + qs, opt);
  const t = await r.text();
  return {status: r.status, ct: r.headers.get('content-type') || '',
          len: t.length, body: t.slice(0, 500)};
};
'ok'
""".replace("__SELLER__", SELLER)

SUITE = [
    ("stock/sku/list POST", "/api/v1/product/stock/sku/list", "POST", {"product_id": PID}, {}),
    ("stock/sku/list GET", "/api/v1/product/stock/sku/list", "GET", None, {"product_id": PID}),
    ("stock/list POST", "/api/v1/product/stock/list", "POST", {}, {}),
    ("stock/list GET", "/api/v1/product/stock/list", "GET", None, {}),
    ("stock/product/list POST", "/api/v1/product/stock/product/list", "POST", {}, {}),
    ("stock/query/sku POST", "/api/v1/product/stock/query/sku", "POST", {"product_id": PID}, {}),
    ("stock/query/inventory_health POST",
     "/api/v1/product/stock/query/inventory_health", "POST", {}, {}),
    ("local/products/list GET", "/api/v1/product/local/products/list", "GET", None,
     {"page_number": 1, "page_size": 2}),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("method", nargs="?", default="POST")
    ap.add_argument("--body", default=None, help="JSON 字符串")
    ap.add_argument("--query", default=None, help="JSON 字符串")
    ap.add_argument("--suite", action="store_true")
    a = ap.parse_args()

    tests = SUITE if a.suite or not a.path else [
        (a.path, a.path, a.method,
         json.loads(a.body) if a.body else {}, json.loads(a.query) if a.query else {})]

    with attach(CDP_PORT) as p:
        p.js(RAW_JS)
        for name, path, m, body, extra in tests:
            r = p.js("window.__ttRaw(" + json.dumps(path) + "," + json.dumps(m) + ","
                     + json.dumps(extra) + "," + json.dumps(body) + ")",
                     await_promise=True, timeout=120)
            if not isinstance(r, dict):
                print(f"--- {name}\n    (非对象返回) {r}\n")
                continue
            print(f"--- {name}  [{m}]")
            print(f"    status={r['status']}  ct={r['ct']}  len={r['len']}")
            b = (r["body"] or "").strip()
            print(f"    {b[:300] if b else '(空 body)'}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
