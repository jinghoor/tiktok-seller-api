#!/usr/bin/env python3
"""对 291 个接口在多个候选 host 上做对比调用,确定每个组该用哪个 host。

判定"同一服务"的依据不是 HTTP 200,而是**业务响应是否一致**:
同一个接口打到对的 host 和不支持它的 host 上,响应码分布差异明显
(不支持的 host 会给 code=999/404 文案 或 纯 404 page not found)。

输出 spec/host_matrix.json + 控制台汇总。
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import sys
import warnings
from collections import Counter
from pathlib import Path

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api import AdflyClient  # noqa: E402
from adfly_api.spec import config  # noqa: E402

BODY = {"page": 1, "page_size": 5}
ROWS = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
HOSTS = ["front", "advertise_bff", "finance_bff", "finance", "automation", "ai_agent_root"]
# 只测 POST + 无参路径,避免 GET 的 query 差异干扰
TARGETS = ROWS  # 全量,GET 也一起对比(用空 body / 最小 query)


def main() -> None:
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    if not c.session.token:
        print("需要先登录")
        sys.exit(2)
    p = c.t
    bases = config()["backends"]["prod"]
    H = p._headers({"Content-Type": "application/json; charset=UTF-8;"})

    def probe(args):
        base_key, row = args
        url = bases[base_key] + row["path"]
        method = row["method"]
        kw = {"json": BODY} if method == "POST" else {"params": {"platform": 1}}
        try:
            r = p.http.request(method, url, headers=H, timeout=8, **kw)
        except Exception as e:
            return base_key, row, "ERR", type(e).__name__
        t = r.text[:200].replace("\n", " ")
        if "page not found" in t:
            return base_key, row, "MISS", ""
        ctype = r.headers.get("Content-Type", "")
        # 导出接口直接回 xlsx 二进制,没有 JSON 信封 —— 收到二进制就说明路由对了
        if "spreadsheet" in ctype or "octet-stream" in ctype or r.content[:2] == b"PK":
            return base_key, row, "OK", "xlsx"
        try:
            env = json.loads(r.text)          # 全量解析,别截断(截断会误判 NONJSON)
        except Exception:
            return base_key, row, "NONJSON", t[40:110]
        code = env.get("code")
        msg = (env.get("message") or env.get("reason") or "")
        if code == 0:
            return base_key, row, "OK", ""
        # 500 不算"路由可达":参数对但服务端内部错,换 host 也可能一样,不能作为归属证据
        if code == 500:
            return base_key, row, "ERR500", msg[:50]
        # 参数/权限类报错说明路由是通的,只是这次调用缺东西
        if code in (400, 401, 403, 11, 999) and (
                "无权限" in msg or "nil" in msg or "为空" in msg or "invalid" in msg.lower()
                or "must be" in msg or "value" in msg.lower() or "参数" in msg):
            return base_key, row, "REACHED", msg[:60]
        if code == 0 or isinstance(env.get("data"), (list, dict)) and not msg:
            return base_key, row, "OK", ""
        return base_key, row, ("REACHED" if code in (400, 401, 403, 999) else f"code={code}"), msg[:60]

    jobs = [(b, r) for r in TARGETS for b in HOSTS]
    print(f"对比调用 {len(jobs)} 次({len(TARGETS)} 接口 × {len(HOSTS)} host)…")
    matrix: dict = {}
    with cf.ThreadPoolExecutor(16) as ex:
        for i, (base_key, row, verdict, detail) in enumerate(ex.map(probe, jobs), 1):
            key = f'{row["backend"]}::{row["method"]} {row["path"]}'
            matrix.setdefault(key, {})[base_key] = {"v": verdict, "d": detail}
            if i % 300 == 0:
                print(f"  {i}/{len(jobs)}")

    (HERE / "adfly_api/spec/host_matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=1), encoding="utf-8")

    # 汇总:每个组内,各 host 的 OK 占比
    print("\n=== 每个组在各 host 上的 OK 数 ===")
    print(f'{"组":14}' + "".join(f"{h:>16}" for h in HOSTS))
    for group in sorted({r["backend"] for r in TARGETS}):
        keys = [k for k in matrix if k.startswith(group + "::")]
        if not keys:
            continue
        print(f"{group:14}" + "".join(
            f"{sum(1 for k in keys if matrix[k].get(h,{}).get('v') in ('OK','REACHED')):>16}" for h in HOSTS))

    # 找出"只在某一个 host 上 OK"的接口 —— 这些是 host 归属的决定性证据
    print("\n=== 决定性证据:仅在一个 host 上 OK 的接口 ===")
    only: dict = {}
    for k, v in matrix.items():
        oks = [h for h, x in v.items() if x["v"] in ("OK", "REACHED")]
        if len(oks) == 1:
            only.setdefault(oks[0], []).append(k.split("::", 1)[1])
    for h, ks in sorted(only.items(), key=lambda x: -len(x[1])):
        print(f"\n  ## {h} ({len(ks)} 个独有)")
        for k in ks[:14]:
            print(f"     {k}")
        if len(ks) > 14:
            print(f"     … 另有 {len(ks)-14} 个")

    # 双 host 都 OK 的接口 —— 需要靠规则选
    both = {k: [h for h, x in v.items() if x["v"] in ("OK", "REACHED")] for k, v in matrix.items()}
    multi = {k: h for k, h in both.items() if len(h) > 1}
    print(f"\n=== 多 host 都能 OK 的接口: {len(multi)} 个(这些用候选顺序决定)===")
    for k, hs in list(multi.items())[:10]:
        print(f"  {k}  ->  {hs}")


if __name__ == "__main__":
    main()
