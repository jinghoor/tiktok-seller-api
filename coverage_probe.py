#!/usr/bin/env python3
"""带 token 的全量接口覆盖测试。

对 293 个接口逐个实调,产出可用性矩阵。写入类接口(default-deny)一律跳过 ——
空 body 打 /delete、/bind、/transfer、/recharge 这类是真会改数据的。

判定:
  OK       code=0
  PARAM    接口存在但缺必填参数(code 非 0,message 指向参数)
  NOAUTH   有 token 但无权限(code 999/403/公司上下文缺失)
  GONE     HTTP 404 page not found
  ERROR    5xx / 网络层异常
输出 spec/coverage.json + coverage.md
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
import threading
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api import AdflyAuthError, AdflyClient, AdflyError, AdflyRouteError  # noqa: E402
from backend_map import normalize_endpoints  # noqa: E402

# 写操作判定:命中即跳过(默认拒绝)
WRITE_SEGMENTS = re.compile(
    r"(^|/)(add|create|edit|modify|update|delete|del|bind|unbind|remove|submit|"
    r"transfer|recharge|pay|exchange|reduce|clear|deduct|confirm|apply|import|"
    r"copy|extend|upload|complete|save|register|login|logout|reset|sign|cancel|"
    r"status/update|multi_edit|batch_edit|change_custom_passwd|upt_pass|"
    r"forget_pass|phone/update|email/update|send_code|edit_company_menu|"
    r"add_custom_anchor|re_gene_desc|regene|reupload|feedback|mark_read|archive)(/|$)",
    re.I,
)
WRITE_METHODS = {"DELETE", "PUT", "PATCH"}


# 分页风格:automation 与 finance_bff 的 pay/coupon 用嵌套 page_info,其余用平铺
NESTED_PAGING = {"automation"}
NESTED_PAGING_PREFIX = ("/pay/", "/coupon/", "/wallet/sub_company")


def body_for(row: dict, ctx: dict) -> dict:
    """按接口形态给一个最小合法 body —— 空 {} 会被大量接口判成 500。

    ctx 里带已探测到的真实 id,让 id 类接口也能真跑通。
    """
    path, backend = row["path"], row["backend"]
    if row["method"] != "POST":
        return {}
    if "export" in path or "download" in path:
        return {"start_date": ctx["start_date"], "end_date": ctx["end_date"]}
    nested = backend in NESTED_PAGING or path.startswith(NESTED_PAGING_PREFIX)
    paging = {"page_info": {"page": 1, "page_size": 5}} if nested else {"page": 1, "page_size": 5}
    body: dict = dict(paging)

    aid, sid, bc, cid, tta = (ctx["advertiser_id"], ctx["store_id"], ctx["store_authorized_bc_id"],
                              ctx["campaign_id"], ctx["tt_auth_id"])
    if any(k in path for k in ("report", "consume", "panel_report", "chart", "summary",
                               "daily", "kanban", "settlement", "payable", "bill", "rebate")):
        body.update({"start_date": ctx["start_date"], "end_date": ctx["end_date"]})
    if any(k in path for k in ("order_info",)) or "report" in path:
        body.setdefault("order_info", {"field": "spend", "order_type": "desc"})
    for key, val in (
        ("advertiser_id", aid), ("advertiser_ids", [aid]), ("tt_auth_id", tta),
        ("store_id", sid), ("store_authorized_bc_id", bc),
        ("bc_id", bc), ("campaign_id", cid), ("campaign_ids", [cid]),
        ("identity_id", ctx.get("identity_id", "")),
        ("item_group_id", ctx.get("item_group_id", "")),
        ("currency", "USD"), ("company_ex_id", ctx["company_ex_id"]),
        ("platform", 1), ("tactic_ex_id", ctx.get("tactic_ex_id", "")),
        ("material_group_id", ctx.get("material_group_id", "")),
    ):
        if f"{key}" in path.replace("-", "_"):
            body.setdefault(key, val)
    return body


def query_for(row: dict, ctx: dict) -> dict:
    """GET 接口的查询参数。"""
    if row["method"] != "GET":
        return {}
    path = row["path"]
    q: dict = {}
    if "platform" in path or path in ("/advertiser/config",):
        q["platform"] = 1
    if "get_auth_link" in path:
        q["platform"] = 1
    if "decrypt" in path:
        q["encrypted_payload"] = "x"
    return q


def is_write(row: dict) -> bool:
    if row["method"].upper() in WRITE_METHODS:
        return True
    return bool(WRITE_SEGMENTS.search(row["path"]))


def classify(exc: Exception | None, data) -> str:
    if exc is None:
        return "OK"
    if isinstance(exc, AdflyRouteError):
        return "GONE"
    if isinstance(exc, AdflyAuthError):
        return "AUTH"
    if isinstance(exc, AdflyError) and "二进制响应" in str(exc):
        return "OK(bytes)"
    if isinstance(exc, AdflyError):
        msg = f"{exc.message}"
        code = exc.code
        if code in (999, 403) or "无权限" in msg or "company_ex_id" in msg:
            return "NOAUTH"
        if "nil" in msg or "为空" in msg or "参数" in msg or "must be in list" in msg \
           or "required" in msg.lower() or "invalid" in msg.lower():
            return "PARAM"
        if any(k in msg for k in ("nil", "为空", "参数", "must be", "invalid", "required",
                                  "length", "record not found", "empty", "cannot be empty",
                                  "is_sure", "正确", "有误")):
            return "PARAM"
        if isinstance(code, int) and code >= 500:
            return "ERROR"
        if code == 999:
            return "BIZ"
        return "PARAM" if code not in (0,) else "OK"
    return "ERROR"


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    rows = json.loads((HERE / "adfly_api/spec/endpoints.json").read_text())
    normalize_endpoints(rows)   # 清单可能来自旧版提取,按共享映射兜底纠正
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    if not c.session.token:
        print("没有 token,先 python3 -m adfly_api login")
        return 2
    print(f"token 就绪,company_ex_id={c.session.company_ex_id},并发={limit}")

    targets, skipped = [], []
    for r in rows:
        (skipped if is_write(r) else targets).append(r)
    print(f"待测 {len(targets)} 个 / 写入类 {len(skipped)} 个")

    # 写入类接口做安全检查:空 body 打删除/绑定/转账接口,正确实现必须报参数错。
    # 报 code=0 说明空 body 就能改数据 —— 那是需要单独记录的严重问题。
    dangerous: list = []
    if "--probe-writes" in sys.argv:
        print(f"写入类安全检查({len(skipped)} 个,空 body)…")
        if "0" not in "".join(sys.argv):
            pass
        def check_write(row: dict) -> None:
            with sem_w:
                try:
                    c.call(row["backend"], row["method"], row["path"], {} if row["method"] == "POST" else None)
                    with lock_w:
                        dangerous.append({**row, "why": "空 body 返回成功"})
                except Exception:
                    pass  # 报错即正常
        sem_w, lock_w = threading.Semaphore(4), threading.Lock()
        with cf.ThreadPoolExecutor(4) as ex:
            list(ex.map(check_write, skipped))
        print(f"  空 body 就改数据成功的接口: {len(dangerous)}")
        for d in dangerous:
            print(f'    !! {d["method"]} {d["path"]}')
    print()

    # 先取真实上下文,给参数化接口喂真 id
    advs = c.advertisers()
    aid = advs[0]["advertiser_id"] if advs else ""
    try:
        auth = c.ads.get_gmv_max_auth_list() or {}
        tta = (auth.get("list") or [{}])[0].get("id") or 0
    except Exception:
        tta = 0
    store_id = bc = identity_id = item_group_id = ""
    AID_OK = "7642XXXXXXXXXX57"
    try:
        st = c.ads.get_gmv_max_store_list({"advertiser_id": AID_OK, "tt_auth_id": tta})
        s0 = (st or {}).get("list", [{}])[0]
        store_id, bc = s0.get("store_id", ""), s0.get("store_authorized_bc_id", "")
        idl = c.ads.get_gmv_max_identity_list({"advertiser_id": AID_OK, "store_id": store_id,
                                              "store_authorized_bc_id": bc, "tt_auth_id": tta})
        identity_id = ((idl or {}).get("list") or [{}])[0].get("identity_id", "")
    except Exception as e:
        print("  (店铺/身份上下文获取失败:", str(e)[:60], ")")
    try:
        gm = c.ads.get_gmv_max_list({"page": 1, "page_size": 1})
        first = ((gm or {}).get("list") or [{}])[0]
        campaign_id = first.get("campaign_id", "")
        item_group_id = (first.get("item_group_ids") or [""])[0]
    except Exception:
        campaign_id = ""
    ctx = {"advertiser_id": AID_OK or aid, "store_id": store_id,
           "store_authorized_bc_id": bc, "identity_id": identity_id,
           "item_group_id": item_group_id, "campaign_id": campaign_id,
           "tt_auth_id": tta, "company_ex_id": c.session.company_ex_id,
           "start_date": "2019-01-01", "end_date": "2035-12-31"}
    print(f"上下文: advertiser={ctx['advertiser_id']} tt_auth={tta} store={store_id or '-'} "
          f"identity={identity_id[:12] or '-'} campaign={campaign_id or '-'}")

    sem = threading.Semaphore(limit)
    lock = threading.Lock()
    results: list[dict] = []

    def one(row: dict) -> None:
        with sem:
            exc, data = None, None
            t0 = time.time()
            try:
                data = c.call(row["backend"], row["method"], row["path"],
                              body_for(row, ctx) if row["method"] == "POST" else None,
                              params=query_for(row, ctx) or None)
            except Exception as e:  # noqa: BLE001
                exc = e
            ms = int((time.time() - t0) * 1000)
            status = classify(exc, data)
            rec = {**row, "status": status, "ms": ms,
                   "msg": (str(exc)[:90] if exc else ""),
                   "n": (len(data.get("list", [])) if isinstance(data, dict) and isinstance(data.get("list"), list)
                         else (len(data) if isinstance(data, (list, dict)) else None))}
            with lock:
                results.append(rec)
                if len(results) % 40 == 0:
                    print(f"  {len(results)}/{len(targets)}")

    started = time.time()
    with cf.ThreadPoolExecutor(limit) as ex:
        list(ex.map(one, targets))
    elapsed = time.time() - started

    for r in skipped:
        results.append({**r, "status": "SKIP(write)", "ms": 0, "msg": "", "n": None})

    cnt = Counter(r["status"] for r in results)
    print(f"\n=== 覆盖结果 ({elapsed:.1f}s) ===")
    for k, v in cnt.most_common():
        print(f"  {k:12} {v:4}")

    print("\n=== 按后端 ===")
    for backend in sorted({r["backend"] for r in results}):
        sub = [r for r in results if r["backend"] == backend]
        s = Counter(x["status"] for x in sub)
        print(f"  {backend:12} " + "  ".join(f"{k}={v}" for k, v in s.most_common()))

    print("\n=== 延迟(排除 SKIP) ===")
    lat = sorted(r["ms"] for r in results if r["status"] != "SKIP(write)")
    if lat:
        n = len(lat)
        print(f"  n={n}  p50={lat[n//2]}ms  p90={lat[int(n*0.9)]}ms  p99={lat[int(n*0.99)]}ms  max={lat[-1]}ms")

    print("\n=== 非 OK 明细 ===")
    for r in sorted([x for x in results if x["status"] not in ("OK", "SKIP(write)")],
                    key=lambda x: (x["status"], x["backend"], x["path"])):
        print(f'  {r["status"]:6} {r["backend"]:11} {r["method"]:5} {r["path"]:46} {r["msg"][:60]}')

    (HERE / "adfly_api/spec/coverage.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

    # 生成 Markdown 报告
    md = ["# 接口覆盖测试报告", "",
          f"- 测试时间:{time.strftime('%Y-%m-%d %H:%M:%S')}",
          f"- 接口总数:**{len(results)}**,实测 {len(targets)},跳过写入类 {len(skipped)}",
          f"- 耗时 {elapsed:.1f}s,并发 {limit}", "",
          "## 汇总", "", "| 状态 | 数量 |", "|---|---|"]
    for k, v in cnt.most_common():
        md.append(f"| {k} | {v} |")
    md += ["", "## 按后端", "", "| 后端 | OK | PARAM | NOAUTH | GONE | ERROR | 跳过 |", "|---|---|---|---|---|---|---|"]
    for backend in sorted({r["backend"] for r in results}):
        s = Counter(x["status"] for x in results if x["backend"] == backend)
        md.append(f'| {backend} | {s.get("OK",0)} | {s.get("PARAM",0)} | {s.get("NOAUTH",0)} | '
                  f'{s.get("GONE",0)} | {s.get("ERROR",0)} | {s.get("SKIP(write)",0)} |')
    if lat:
        n = len(lat)
        md += ["", "## 延迟", "", f"n={n}, p50={lat[n//2]}ms, p90={lat[int(n*0.9)]}ms, "
               f"p99={lat[int(n*0.99)]}ms, max={lat[-1]}ms"]
    md += ["", "## 全部接口状态", "", "| 状态 | 后端 | 方法 | 路径 | 耗时 | 返回/错误 |",
           "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda x: (x["status"], x["backend"], x["path"])):
        md.append(f'| {r["status"]} | {r["backend"]} | {r["method"]} | `{r["path"]}` | '
                  f'{r["ms"]}ms | {(r["msg"] or (f"{r[chr(110)]} 条" if r["n"] is not None else ""))[:70]} |')
    (HERE / "coverage.md").write_text("\n".join(md), encoding="utf-8")
    print("\n写入 coverage.md 与 adfly_api/spec/coverage.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
