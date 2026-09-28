#!/usr/bin/env python3
"""重放抓到的真实请求 —— 用真实 query/body 测接口,而不是空探测。

空 body 探测在卖家中心会被网关直接 403,必须带真实参数才有意义。

    python3 tt_replay.py --cap notes/cap_product_create.json
    python3 tt_replay.py --cap notes/cap_product_create.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hub_headless import attach  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

RUNNER = r"""
window.__ttReplay = async (items) => {
  const out = window.__ttReplayResults || [];
  for (const it of items) {
    const t0 = Date.now();
    const rec = { name: it.name, method: it.method, url: it.url, ok: false };
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 25000);
    try {
      const opt = { method: it.method, credentials: 'include', signal: ac.signal,
                    headers: { 'Accept': 'application/json, text/plain, */*' } };
      if (it.body) {
        opt.headers['Content-Type'] = 'application/json; charset=utf-8';
        opt.body = it.body;
      }
      const r = await fetch(it.url, opt);
      const txt = await r.text();
      rec.status = r.status;
      rec.ms = Date.now() - t0;
      rec.len = txt.length;
      rec.body = txt.length > 6000 ? txt.slice(0, 6000) + '...[+' + (txt.length - 6000) + ']' : txt;
      rec.ok = r.ok;
    } catch (e) {
      rec.status = 0; rec.ms = Date.now() - t0; rec.body = 'ERR: ' + String(e);
    } finally { clearTimeout(timer); }
    out.push(rec);
    window.__ttReplayResults = out;
  }
  return out.length;
};
'installed'
"""


def norm(u: str) -> str:
    """去掉一次性防伪参数,重放过期会失败。"""
    import urllib.parse as up
    p = up.urlsplit(u)
    q = up.parse_qsl(p.query, keep_blank_values=True)
    drop = {"msToken", "X-Bogus", "X-Gnarly", "X-Tts-Oec-Bsid", "verifyFp", "fp", "_signature"}
    q = [(k, v) for k, v in q if k not in drop]
    return up.urlunsplit((p.scheme, p.netloc, p.path, up.urlencode(q), ""))


def classify(rec: dict) -> str:
    b = rec.get("body") or ""
    st = rec.get("status") or 0
    if "No matching route" in b[:200]:
        return "NO_ROUTE"
    if st in (401, 403):
        return "DENIED"
    if st == 404:
        return "NO_ROUTE"
    if st >= 500 or st == 0:
        return f"HTTP_{st}"
    try:
        j = json.loads(b)
    except (json.JSONDecodeError, TypeError):
        return "NON_JSON"
    if isinstance(j, dict) and "code" not in j:
        return "OK_RAW"
    code = j.get("code") if isinstance(j, dict) else None
    return "OK" if code == 0 else f"CODE_{code}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--cap", nargs="+",
                    default=[os.path.join(HERE, "notes", "cap_product_create.json")])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "notes", "tt_replay_result.json"))
    ap.add_argument("--include-writes", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.3)
    a = ap.parse_args()

    # 汇总所有抓包里的自家请求,按 (method, path) 去重,保留首次出现的完整 url
    seen: dict[tuple[str, str], dict] = {}
    for f in a.cap:
        if not os.path.exists(f):
            print(f"  跳过不存在的 {f}", file=sys.stderr)
            continue
        d = json.load(open(f))
        recs = d.get("records") if isinstance(d, dict) else d
        for r in recs:
            u = r.get("url") or ""
            if "seller-vn.tiktok.com" not in u:
                continue
            if not u.startswith("https://"):
                u = "https://seller-vn.tiktok.com" + u
            path = u.split("?")[0].replace("https://seller-vn.tiktok.com", "")
            if not path.startswith("/api/"):
                continue
            key = (r.get("method") or "GET", path)
            if key in seen:
                continue
            seen[key] = {"name": path.rsplit("/", 2)[-2:][0] + "/" + path.rsplit("/", 1)[-1],
                         "method": r.get("method") or "GET",
                         "url": norm(u),
                         "body": r.get("reqBody") if isinstance(r.get("reqBody"), str) else None,
                         "orig_status": r.get("status")}

    items = list(seen.values())
    print(f"抓到 {len(items)} 个唯一 (方法,路径) 自家请求")
    if a.dry_run:
        for i in items:
            print(f"  {i['method']:<5} {i['url'][:150]}")
            if i["body"]:
                print(f"        body: {i['body'][:150]}")
        return 0

    results: list[dict] = []
    with attach(a.port) as p:
        print("注入重放器:", p.js(RUNNER))
        print("清空结果:", p.js("window.__ttReplayResults = []"))
        print("页:", p.url())
        B = 10
        for i in range(0, len(items), B):
            batch = items[i:i + B]
            p.js(f"window.__ttReplay({json.dumps(batch)})", await_promise=True, timeout=300)
            results = json.loads(p.js("JSON.stringify(window.__ttReplayResults || [])") or "[]")
            print(f"  {min(i+B,len(items))}/{len(items)}  已收 {len(results)}")
            time.sleep(a.sleep)

    for r in results:
        r["cls"] = classify(r)
    import collections
    c = collections.Counter(r["cls"] for r in results)
    json.dump({"summary": dict(c), "results": results},
              open(a.out, "w"), ensure_ascii=False, indent=2)
    print(f"\n=== 结果分布 === {dict(c)}")
    print(f"→ {a.out}\n")
    for cls in sorted(c, key=lambda k: (k != "OK", k)):
        rows = [r for r in results if r["cls"] == cls]
        print(f"\n--- {cls} ({len(rows)}) ---")
        for r in rows:
            u = r["url"].split("?")[0].replace("https://seller-vn.tiktok.com", "")
            print(f"  {r.get('status')} {r['method']:<5} {u[:72]:<72} {r.get('len','')}B")
            if cls != "OK":
                print(f"        {(r.get('body') or '')[:180]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
