#!/usr/bin/env python3
"""TikTok 卖家中心接口批量实测。

设计要点:请求从页面内 fetch 发出,自动带 cookie / CSRF / fp,不需要手工重建 header。
只用 GET 和参数为空的 POST 探路由;需要参数的接口从后端校验错误里提取参数名。

    python3 tt_probe.py --port CDP_PORT --file notes/tt_product_api.json
    python3 tt_probe.py --port CDP_PORT --only /api/v1/product/tab/count/get
    python3 tt_probe.py --port CDP_PORT --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_headless import attach  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SELLER = "7494XXXXXXXXXX00"

# 绝不实调的写接口:命中即跳过。宁可漏测,不可误改线上店铺。
DESTRUCTIVE = re.compile(
    r"(delete|remove|deactivate|recover|activate|"
    r"/create|/edit|/update|/save|/submit|/publish|/upload|"
    r"/set$|/set/|/mactivate|/mdelete|/mdeactivate|/msubmit|/mconfirm|"
    r"/increase|/decrease|/rollback|/confirm|/sign|/reject|/mark|"
    r"/move|/batch_create|/bulk_create|/precheck|/check$|/check/|"
    r"/migrate|/normalize|/appeal|/refresh|/translate|/generate|"
    r"/recommend|/calculate|/cal$|/mcal|/construct|/identify|"
    r"/link|/unlink|/initial|/freeze|/invite|/modify|/config_product|"
    r"/suggested|/collect|/relate|/relate/|/withdraw|/bind|/upload_details|"
    # 下面这批是二次收紧:名字像只读,实际有副作用
    r"/multi_confirm|/register_stock_lock|/request_stock_unlock|/segment|"
    r"/image_background|/partial_edit|/partial/edit|/refetch|/slice_switch|"
    r"/event/record|/set_|/update_status|/status/update|/config$|/rule/get$|"
    r"/submit/record|/multi_edit|/prettify|/from_seller|/tax_price_calc|"
    r"/update_config|/batch_save|/multi_region_listing/translate)",
    re.I)

# 这些名字里带 check/create 但是只读的例外(白名单)
READONLY_EXCEPTIONS = {
    "/api/v1/product/product_creation/preload",
    "/api/v1/product/regions/mget",
    "/api/v1/product/tab/count/get",
    "/api/v1/product/list/seller/warehouses",
    "/api/v1/product/commission/config/get",
    "/api/v1/product/comp/get_schema_v2",
    "/api/v1/product/local/product/schema/get",
    "/api/v1/product/optimize/meta/get",
    "/api/v1/product/optimize/data/get",
    "/api/v1/product/optimize/overview/get",
    "/api/v1/product/optimize/hosting/auth/get",
    "/api/v1/product/local/has_edit_pending_product/get",
    "/api/v1/product/local/selling_tools",
    "/api/v1/product/tab/count/get",
    "/api/v2/seller/onboard/v2/file/upload",
}

# 测试器:在一个 tab 里顺序打请求,把结果存到 window.__r
RUNNER = r"""
window.__ttProbe = async (specs, commonQ, stopOnFail) => {
  const out = window.__ttProbeResults || [];
  const csrf = (document.cookie.match(/csrf_token=([^;]+)/) || [])[1] || '';
  for (const s of specs) {
    const q = new URLSearchParams({ ...commonQ, ...(s.query || {}) });
    const url = s.path + (q.toString() ? '?' + q.toString() : '');
    const opt = {
      method: s.method || 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json, text/plain, */*',
        'X-CSRFToken': decodeURIComponent(csrf),
      },
    };
    if (s.body !== undefined && s.method !== 'GET') {
      opt.headers['Content-Type'] = 'application/json; charset=utf-8';
      opt.body = JSON.stringify(s.body);
    }
    const t0 = Date.now();
    let rec = { path: s.path, method: s.method, url: url, ok: false };
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 20000);
    opt.signal = ac.signal;
    try {
      const r = await fetch(url, opt);
      const txt = await r.text();
      rec.status = r.status;
      rec.ms = Date.now() - t0;
      rec.ctype = r.headers.get('content-type') || '';
      rec.body = txt.length > 4000 ? txt.slice(0, 4000) + '...[+' + (txt.length - 4000) + ']' : txt;
      rec.ok = r.ok;
    } catch (e) {
      rec.status = 0;
      rec.ms = Date.now() - t0;
      rec.body = 'FETCH_ERROR: ' + String(e);
    } finally {
      clearTimeout(timer);
    }
    out.push(rec);
    window.__ttProbeResults = out;
    if (stopOnFail && !rec.ok) break;
  }
  return out.length;
};
'installed'
"""


def parse_error_params(body: str) -> list[str]:
    """从后端校验错误里抽参数名。"""
    hits: set[str] = set()
    for pat in (r"[Ii]nvalid\s+\w+\.(\w+)", r"([a-z_]{3,40})\s*(?:is|必填|不能为空)",
                r"required\s+\w*\s*[:=]?\s*([a-z_]{3,40})", r"\"(\w+)\"\s*is required"):
        for m in re.finditer(pat, body):
            hits.add(m.group(1))
    return sorted(hits)


def classify(rec: dict) -> str:
    """先看 HTTP 状态,再看业务码。403 空 body 是网关级拒绝,不是路由不通。"""
    b = rec.get("body") or ""
    st = rec.get("status") or 0
    if "No matching route" in b[:200] or "404 page not found" in b[:200]:
        return "404_NO_ROUTE"
    if st == 401 or st == 403:
        return "NOAUTH_HTTP"          # 网关拒绝:通常缺参数或权限
    if st == 404:
        return "404_NO_ROUTE"
    if st >= 500:
        return "5xx"
    if st == 0:
        return "FETCH_FAIL"
    try:
        j = json.loads(b)
    except (json.JSONDecodeError, TypeError):
        return "NOT_JSON"
    if isinstance(j, dict) and "code" not in j:
        # 裸对象,例如 {"can_manage_global_seller":false}
        return "OK_NOENV" if b.strip() not in ("{}", "[]") else "EMPTY_200"
    code = j.get("code", j.get("status_code")) if isinstance(j, dict) else None
    if code == 0:
        return "OK"
    if code in (3, 10501, 1000002) or "permission" in str(j).lower() or "权限" in str(j):
        return "NOAUTH_BIZ"
    if code in (1000001, 1, 400) or "invalid" in str(j).lower() or "param" in str(j).lower():
        return "PARAM"
    return f"CODE_{code}"


# 明确黑名单:不管正则怎么判,这些一律不实调
NEVER_CALL = {
    "/api/v1/product/local/draft/partial_edit",
    "/api/v1/product/local/product/multi_confirm",
    "/api/v1/product/lock/register_stock_lock",
    "/api/v1/product/lock/request_stock_unlock",
    "/api/v1/product/local/product/precheck",
    "/api/v1/product/parcel/check",
    "/api/v1/product/global/parcel/check",
    "/api/v1/product/shipping_template/check",
    "/api/v1/product/logistics/service/check",
    "/api/v1/product/property/check",
    "/api/v1/product/prohibited/words/check",
    "/api/v1/product/image/quality/check",
    "/api/v1/product/product/info/quality/calculate",
    "/api/v1/product/publish/diagnosis/item/calculate",
    "/api/v1/product/diagnosis/item/calculate",
    "/api/v1/product/recommend/item/calculate",
    "/api/v1/product/stock/negative/close",
    "/api/v1/product/seller/update_config",
    "/api/v1/product/optimize/seller_detail/update",
    "/api/v1/product/comp/refetch_data",
    "/api/v1/product/comp/refetch_schema",
    "/api/v1/product/sku/stocks/increase",
    "/api/v1/product/sku/stocks/decrease",
    "/api/v1/product/stock/operation/update",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--file", default=os.path.join(HERE, "notes", "tt_product_api.json"))
    ap.add_argument("--only", default=None, help="只测该路径")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "notes", "tt_probe_result.json"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-writes", action="store_true",
                    help="危险:连写接口也发(空 body)。默认关闭")
    ap.add_argument("--sleep", type=float, default=0.25)
    a = ap.parse_args()

    # 构造待测清单
    specs: list[dict] = []
    if a.only:
        specs = [{"path": a.only, "method": "GET", "name": "cli"}]
    else:
        raw = json.load(open(a.file))
        items = raw.values() if isinstance(raw, dict) else raw
        for v in items:
            p = v["path"].replace("{param}", "1")
            m = v.get("method") or "POST"
            is_write = (bool(DESTRUCTIVE.search(p)) and p not in READONLY_EXCEPTIONS) \
                or p in NEVER_CALL
            specs.append({"path": p, "method": m, "name": v.get("name"),
                          "_write": is_write})
    specs.sort(key=lambda s: (s["_write"], s["path"]))

    skipped = [s for s in specs if s["_write"] and not a.include_writes]
    todo = [s for s in specs if not s["_write"] or a.include_writes]
    if a.limit:
        todo = todo[:a.limit]

    print(f"清单 {len(specs)} 个:只读 {len(specs)-len(skipped)}, 写 {len(skipped)}"
          f"(默认跳过)")
    print(f"本次实调 {len(todo)} 个")
    if a.dry_run:
        for s in todo:
            print(f"  {s['method']:<5} {s['path']}")
        print(f"\n跳过(写) {len(skipped)}:")
        for s in skipped:
            print(f"  {s['method']:<5} {s['path']}")
        return 0

    common = {"locale": "zh-CN", "language": "zh-CN",
              "oec_seller_id": SELLER, "seller_id": SELLER,
              "aid": "4068", "app_name": "i18n_ecom_shop"}

    results: list[dict] = []
    with attach(a.port) as p:
        print("注入测试器:", p.js(RUNNER))
        print("清空缓冲:", p.js("window.__ttProbeResults = []"))
        print("当前页:", p.url())
        # 分批,每批 12 个,避免单次 await 太久
        B = 12
        for i in range(0, len(todo), B):
            batch = todo[i:i + B]
            payload = [{"path": s["path"], "method": s["method"], "name": s["name"]}
                       for s in batch]
            n = p.js(f"window.__ttProbe({json.dumps(payload)}, {json.dumps(common)}, false)",
                     await_promise=True, timeout=600)
            got = json.loads(p.js("JSON.stringify(window.__ttProbeResults || [])") or "[]")
            results = got
            assert len(results) >= min(i + B, len(todo)) - 2, (
                f"结果丢失:期望约 {min(i+B,len(todo))} 实收 {len(results)}")
            print(f"  {min(i+B, len(todo))}/{len(todo)}  已收 {len(got)}")
            time.sleep(a.sleep)

    # 归类
    summary: dict[str, int] = {}
    for r in results:
        r["cls"] = classify(r)
        r["params"] = parse_error_params(r.get("body") or "")
        summary[r["cls"]] = summary.get(r["cls"], 0) + 1

    json.dump({"common_query": common, "destroyed_skipped": len(skipped),
               "results": results, "summary": summary,
               "skipped": [s["path"] for s in skipped]},
              open(a.out, "w"), ensure_ascii=False, indent=2)

    print(f"\n=== 结果分布 ===  {summary}")
    print(f"→ {a.out}\n")
    for cls in ("OK", "OK_NOENV", "PARAM", "NOAUTH_BIZ", "NOAUTH_HTTP",
                "404_NO_ROUTE", "5xx", "NOT_JSON", "EMPTY_200", "FETCH_FAIL"):
        rows = [r for r in results if r["cls"] == cls]
        if not rows:
            continue
        print(f"\n--- {cls} ({len(rows)}) ---")
        for r in rows:
            extra = ""
            if r["params"]:
                extra = "  参数: " + ",".join(r["params"][:6])
            print(f"  {r['method']:<5} {r['path'][:70]:<70} {r.get('status')} {r.get('ms')}ms{extra}")
    others = [r for r in results if r["cls"].startswith("CODE_")]
    if others:
        print(f"\n--- 其它业务码 ({len(others)}) ---")
        for r in others:
            print(f"  {r['method']:<5} {r['path'][:70]:<70} {r['cls']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
