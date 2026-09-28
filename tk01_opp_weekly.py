#!/usr/bin/env python3
"""商品机会提报 —— 按 operator 正式规则实现的周度流水线。

## 规则（来自 operator，2026-09）

1. **只提报与该商品同一类目的机会**（关键词机会 + 商品机会都算）
2. 提报前**先找相似/同款商品** —— 越相似成功率越高
3. **成功率不是最终标准。** 不管产品是否贴合那个关键词/机会，
   只要**提报成功就有流量扶持**。所以**不能为了堆成功率而放弃低相似度的机会**。
   → 目标函数是「**成功提报的绝对条数**」，不是命中率百分比。
4. **一周提报一次**即可。
5. **要快。** 且店铺很多产品是**同一款商品重复铺货的链接**
   → 按标题聚类后，一个簇只占一次名额，能显著提速。

## 与旧脚本的区别

旧的 `smart_plan` 是**按命中率**优化的：相似度 <0.7 一律丢弃。
按规则 3 那样做会主动放弃流量机会，**方向是错的**。
本模块默认**不设相似度门槛**，只用相似度**排序**（名额有限时优先塞更相似的），
并且把主力指标换成"成功条数"。

## 速度设计

- 类目从 `seller/lead/list` 的 `level3_cate_name_key`（`magellan_<id>`）解析，
  **不逐个拉 lead_detail** —— 这是最大的提速点（几百次调用 → 几次）
- 按 lead 分组：一个机会一次 `/relate`，一次最多 49 个商品
- 商品按标题聚类，`--mode rep` 时一个簇只出一个代表

用法:
  python3 tk01_opp_weekly.py catalog                 # 拉店铺商品（含 L3 类目）
  python3 tk01_opp_weekly.py clusters --sim 0.75     # 商品聚类，看重复铺货情况
  python3 tk01_opp_weekly.py pool                    # 拉全部机会，按类目归类
  python3 tk01_opp_weekly.py plan --mode rep         # 生成周度计划
  python3 tk01_opp_weekly.py run --yes               # 执行
  python3 tk01_opp_weekly.py verify --minutes 60     # 按时戳核对（算成功条数）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_opportunity import OpportunityClient, OppError, PRE, HERE as OPP_HERE  # noqa: E402

CATALOG_FILE = HERE / "notes" / "weekly_catalog.json"
POOL_FILE = HERE / "notes" / "weekly_pool.json"
PLAN_FILE = HERE / "notes" / "weekly_plan.json"
RESULT_FILE = HERE / "notes" / "weekly_result.json"

# 服务端硬限制：一次 relate 最多 49 个商品（>=50 直接拒）
MAX_ITEMS_PER_CALL = 49


# ───────────────────────── 工具 ─────────────────────────

def toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[^\W_]+", (s or "").lower(), re.UNICODE) if len(w) >= 3}


def jaccard(a: str, b: str) -> float:
    A, B = toks(a), toks(b)
    return len(A & B) / len(A | B) if (A | B) else 0.0


def cate_id_from_key(key: str | None) -> str | None:
    """`magellan_873480` → `873480`。

    机会列表接口**不返回** level3_cate_id，只给 level3_cate_name_key。
    逐条拉 lead_detail 取类目要几百次调用；解析 key 是零成本。
    """
    if not key:
        return None
    m = re.search(r"(\d+)$", str(key))
    return m.group(1) if m else None


def load_catalog() -> dict:
    """读回 catalog() 落盘的商品表（兼容旧的扁平格式）。"""
    raw = json.loads(CATALOG_FILE.read_text())
    return raw["products"] if isinstance(raw, dict) and "products" in raw else raw


# ───────────────────────── 主流程 ─────────────────────────

class WeeklySubmitter:
    def __init__(self, *, port: int = CDP_PORT, gap: float = 1.3):
        self.O = OpportunityClient(port=port, gap=gap)
        self.gap = gap

    def close(self):
        self.O.close()

    # ---- 1. 商品目录（含 L3 类目）----
    def catalog(self, *, page_size: int = 100, max_pages: int = 30) -> dict:
        """全部商品 + L3 类目。

        ⚠️ `/api/v1/product/web/local/products/list` 是**游标分页**：
        它接受 `page` 参数但**完全忽略它**（page=1/2/3/10 返回同一批），
        真正的翻页要拿 `data.next_cursor` 回传。配合 `has_more` 判断结束。
        `data.total_product_count` 是总数（实测 591；游标能取到 491 个 online 的）。

        旧实现写死 `page=1`，所以只拿到 100 个 —— 会严重低估重复铺货的程度。
        """
        from tk01_promo_client import PromoClient
        C = PromoClient(port=self.O.port)
        out: dict[str, dict] = {}
        cursor = None
        total = None
        for page in range(1, max_pages + 1):
            params: dict = {"tab_id": 1, "page_size": page_size}
            if cursor:
                params["cursor"] = cursor
            try:
                r = C.call("/api/v1/product/web/local/products/list", method="GET", params=params)
            except Exception as e:
                print(f"  商品列表第 {page} 页失败: {str(e)[:70]}", flush=True)
                break
            d = r.get("data") or {}
            if total is None:
                total = d.get("total_product_count")
            rows = d.get("products") or []
            if not rows:
                break
            for rr in rows:
                pid = str(rr.get("product_id") or "")
                if not pid:
                    continue
                cats = rr.get("categories") or []
                out[pid] = {"title": (rr.get("product_name") or "").strip(),
                            "l3": str(cats[-1].get("id")) if cats else None,
                            "l3_name": (cats[-1].get("local_name") or cats[-1].get("name")) if cats else None,
                            "status": rr.get("product_status"),
                            "sales": rr.get("product_sales")}
            if page % 2 == 0:
                print(f"    第 {page} 页 → 累计 {len(out)}", flush=True)
            if not d.get("has_more"):
                break
            nc = d.get("next_cursor")
            if not nc or nc == cursor:
                break
            cursor = nc
            time.sleep(0.6)
        CATALOG_FILE.write_text(json.dumps(
            {"total_product_count": total, "fetched": len(out), "products": out},
            ensure_ascii=False, indent=1))
        return out

    # ---- 2. 商品聚类（规则 5：重复铺货）----
    @staticmethod
    def clusters(catalog: dict, *, sim: float = 0.75) -> list[dict]:
        """同 L3 类目内按标题相似度聚类，吸收重复铺货的链接。

        贪心：每个商品要么开一个新簇，要么并入相似度最高的已有簇。
        簇代表取标题最长的一个（信息量最大，通常也最贴近机会名）。
        """
        by_cate: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for pid, info in catalog.items():
            by_cate[info.get("l3") or "?"].append((pid, info["title"]))

        out = []
        for l3, items in by_cate.items():
            items = sorted(items, key=lambda x: -len(x[1]))     # 长标题先做簇心
            groups: list[dict] = []
            for pid, title in items:
                best, bi = 0.0, -1
                for i, g in enumerate(groups):
                    s = jaccard(title, g["rep_title"])
                    if s > best:
                        best, bi = s, i
                if bi >= 0 and best >= sim:
                    groups[bi]["members"].append({"pid": pid, "title": title, "sim": round(best, 3)})
                else:
                    groups.append({"l3": l3, "rep_pid": pid, "rep_title": title,
                                   "members": [{"pid": pid, "title": title, "sim": 1.0}]})
            for g in groups:
                g["size"] = len(g["members"])
            out += groups
        out.sort(key=lambda g: (g["l3"], -g["size"]))
        return out

    # ---- 3. 机会池（按类目归类，用 name_key 解析）----
    def pool(self, *, types=(2, 3, 4, 201, 202), max_pages: int = 6) -> dict:
        leads: dict[str, dict] = {}
        for tp in types:
            for pg in range(1, max_pages + 1):
                try:
                    d = self.O.list_leads(page=pg, size=100, opportunity_type=tp)
                except OppError as e:
                    print(f"  type={tp} page={pg} 失败: {str(e.message)[:60]}", flush=True)
                    break
                rows = d.get("lead_list") or []
                if not rows:
                    break
                for x in rows:
                    lid = str(x.get("lead_id"))
                    if lid in leads:
                        continue
                    leads[lid] = {
                        "lead_id": lid,
                        "lead_name": x.get("lead_name") or "",
                        "opportunity_type": x.get("opportunity_type"),
                        "l3": cate_id_from_key(x.get("level3_cate_name_key")),
                        "l3_name": x.get("level3_cate_name"),
                        "l2": cate_id_from_key(x.get("level2_cate_name_key")),
                        "search_volume": x.get("search_volume"),
                        "online_products": x.get("online_products"),
                        "is_your_product": x.get("is_your_product"),
                        "potential_score": x.get("potential_score"),
                    }
                if len(rows) < 100:
                    break
                time.sleep(self.gap * 0.5)
        POOL_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=1))
        return leads

    # ---- 4. 周度计划 ----
    def plan(self, *, catalog: dict, clusters: list[dict], leads: dict,
             submitted: dict | None = None, mode: str = "rep",
             max_per_lead: int = MAX_ITEMS_PER_CALL,
             prefer_similar: bool = True) -> dict:
        """给每个同 L3 类目的机会，挑该店**同类目**的商品塞进去。

        mode:
          rep — 一个商品簇只出代表（最快，覆盖最广；重复铺货的链接不重复占名额）
          all — 簇内全部链接都提（量大，但一个簇会吃满多个名额）

        规则 3：**不设相似度门槛**。相似度只用于排序，名额满了才被挤掉。
        """
        submitted = submitted or {}
        # 类目 → 该店的候选商品
        cand_by_cate: dict[str, list[dict]] = defaultdict(list)
        if mode == "rep":
            for g in clusters:
                cand_by_cate[g["l3"]].append({"pid": g["rep_pid"], "title": g["rep_title"],
                                              "cluster_size": g["size"]})
        else:
            for g in clusters:
                for m in g["members"]:
                    cand_by_cate[g["l3"]].append({"pid": m["pid"], "title": m["title"],
                                                  "cluster_size": g["size"]})

        plan, skipped = [], []
        for lid, ld in leads.items():
            l3 = ld.get("l3")
            if not l3:
                skipped.append({"lead_id": lid, "reason": "无 level3_cate_name_key"})
                continue
            cands = cand_by_cate.get(l3)
            if not cands:
                skipped.append({"lead_id": lid, "l3": l3,
                                "reason": f"本店没有 L3={l3} 的商品（规则1：只提同类目）"})
                continue
            seen = set(submitted.get(lid, []))
            cands = [c for c in cands if c["pid"] not in seen]
            if not cands:
                skipped.append({"lead_id": lid, "l3": l3, "reason": "该类目商品已全部提报过"})
                continue
            # 规则 2：越相似越优先（但不设门槛）
            for c in cands:
                c["sim"] = round(jaccard(c["title"], ld["lead_name"]), 3)
            if prefer_similar:
                cands.sort(key=lambda c: (-c["sim"], c["pid"]))
            chosen = cands[:max_per_lead]
            plan.append({
                "lead_id": lid, "l3": l3, "l3_name": ld.get("l3_name"),
                "opportunity_name": ld["lead_name"],
                "opportunity_type": ld.get("opportunity_type"),
                "search_volume": ld.get("search_volume"),
                "n_candidates": len(cands), "n_chosen": len(chosen),
                "sim_max": chosen[0]["sim"] if chosen else None,
                "sim_min": chosen[-1]["sim"] if chosen else None,
                "items": [{"pid": c["pid"], "sim": c["sim"]} for c in chosen],
            })
        def _vol(p):
            try:
                return -int(p.get("search_volume") or 0)
            except (TypeError, ValueError):
                return 0
        plan.sort(key=lambda p: (_vol(p), p["lead_id"]))
        return {"mode": mode, "grain": "lead",
                "n_leads_total": len(leads), "n_leads_plannable": len(plan),
                "n_pairs": sum(p["n_chosen"] for p in plan),
                "n_calls": len(plan),
                "plan": plan, "skipped": skipped}

    # ---- 5. 执行（超时不算失败）----
    def run(self, plan: list[dict], *, apply: bool = False) -> dict:
        """一个机会一次 `/relate`。

        ⚠️ 客户端超时**不代表没提交** —— 实测 20 个机会全部报超时，
        记录却照样落库。所以超时也计入 `attempted`，成败一律靠 `verify` 回读。
        """
        out = {"calls": 0, "attempted": 0, "ok_resp": 0, "timeout": 0,
               "http_err": [], "applied": apply}
        for i, p in enumerate(plan, 1):
            pids = [str(x["pid"]) for x in p["items"]][:MAX_ITEMS_PER_CALL]
            if not apply:
                out["calls"] += 1
                out["attempted"] += len(pids)
                continue
            out["calls"] += 1
            out["attempted"] += len(pids)
            def _one(ids):
                """发一次 relate，返回 (code, message)。"""
                rr = self.O._post(f"{PRE}/relate",
                                  self.O.build_relate_body(
                                      p["lead_id"], ids,
                                      opportunity_type=p.get("opportunity_type")))
                return rr.get("code"), str(rr.get("message") or "")

            try:
                code, msg = _one(pids)
                if code != 0 and "less than 50" in msg:
                    # 「一次最多 49 个」是按【该机会已关联总数】算的：老机会常已挂
                    # 几十个，一次塞满就超限。自适应折半，比预先查 related_pairs 划算。
                    for size in (24, 12, 6, 3, 1):
                        sent = 0
                        last_msg = ""
                        for i in range(0, len(pids), size):
                            c2, m2 = _one(pids[i:i + size])
                            if c2 == 0:
                                sent += len(pids[i:i + size])
                            else:
                                last_msg = m2
                        if sent:
                            out["ok_resp"] += 1
                            out["split_sent"] = out.get("split_sent", 0) + sent
                            out["http_err"].append({
                                "lead_id": p["lead_id"],
                                "note": f"超限 → 按 {size} 拆分后成功 {sent}",
                            })
                            code = 0
                            break
                        if not last_msg:
                            break
                    else:
                        out["http_err"].append({"lead_id": p["lead_id"],
                                                "message": f"折半拆分后仍失败: {msg[:70]}"})
                if code == 0:
                    if not any(e.get("lead_id") == p["lead_id"] for e in out["http_err"]):
                        out["ok_resp"] += 1
                elif msg:
                    out["http_err"].append({"lead_id": p["lead_id"],
                                            "code": code, "message": msg[:90]})
                else:
                    out["http_err"].append({"lead_id": p["lead_id"],
                                            "code": code, "message": "(空 message)"})
            except OppError as e:
                msg = str(e)
                if "未拿到响应" in msg:
                    out["timeout"] += 1
                else:
                    out["http_err"].append({"lead_id": p["lead_id"], "error": msg[:110]})
            if i % 5 == 0:
                print(f"    进度 {i}/{len(plan)}  应答成功 {out['ok_resp']}  "
                      f"超时 {out['timeout']}  业务错 {len(out['http_err'])}", flush=True)
        return out

    # ---- 6. 核对：算「成功条数」而不是命中率 ----
    def verify(self, leads: set[str], *, minutes: int = 90,
               catalog: dict | None = None) -> dict:
        """按时戳统计最近一次运行的结果。

        规则 3 的指标是**绝对条数**，所以这里主报 `approved_pairs` / `approved_listings`。
        `approved_listings` 用簇去重后的"不同商品"数 —— 重复铺货的链接不该重复计数。
        """
        cut = time.time() - minutes * 60
        found: dict[tuple[str, str], tuple[str, float]] = {}
        for st, tag in ((self.O.APPROVE_OK, "已批准"), (self.O.APPROVE_REJECT, "已被拒")):
            for pg in range(1, 13):
                try:
                    d = self.O.submit_records(page=pg, size=100,
                                              approve_status=st, seller_operation_list=[])
                except OppError:
                    break
                rs = d["record_list"]
                if not rs:
                    break
                stop = False
                for x in rs:
                    ts = int(x.get("submit_time") or 0) / 1000
                    if ts < cut:
                        stop = True
                        break
                    lid = str(x.get("lead_id"))
                    if leads and lid not in leads:
                        continue
                    pid = str((x.get("tts_product_info") or {}).get("id"))
                    found.setdefault((lid, pid), (tag, ts))
                if stop or len(rs) < 100:
                    break

        ok = {k for k, v in found.items() if v[0] == "已批准"}
        bad = {k for k, v in found.items() if v[0] == "已被拒"}
        # 按类目/簇去重统计"不同商品"
        rep = {}
        if catalog:
            clusters = self.clusters(catalog)
            for g in clusters:
                for m in g["members"]:
                    rep[m["pid"]] = g["rep_pid"]
        uniq = {rep.get(pid, pid) for _, pid in ok}
        return {"window_min": minutes, "found": len(found),
                "approved_pairs": len(ok), "rejected_pairs": len(bad),
                "approved_listings": len(uniq),
                "hit_rate": round(len(ok) / len(found), 3) if found else None,
                "by_lead": {lid: sum(1 for k in ok if k[0] == lid) for lid in sorted({k[0] for k in ok})},
                "detail": {f"{k[0]}|{k[1]}": v[0] for k, v in found.items()}}


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="商品机会周度提报（按 operator 5 条规则）")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--gap", type=float, default=1.3)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("catalog")
    p = sub.add_parser("clusters"); p.add_argument("--sim", type=float, default=0.75)
    sub.add_parser("pool")
    p = sub.add_parser("plan"); p.add_argument("--mode", choices=["rep", "all"], default="rep")
    p.add_argument("--sim", type=float, default=0.75)
    p.add_argument("--max-per-lead", type=int, default=MAX_ITEMS_PER_CALL)
    p.add_argument("--types", default="2,3,4,201,202")
    p = sub.add_parser("run"); p.add_argument("--yes", action="store_true")
    p.add_argument("--limit", type=int, default=0, help="只跑前 N 个机会（分批用）")
    p.add_argument("--offset", type=int, default=0)
    p = sub.add_parser("verify"); p.add_argument("--minutes", type=int, default=90)

    a = ap.parse_args()
    W = WeeklySubmitter(port=a.port, gap=a.gap)
    try:
        if a.cmd == "catalog":
            c = W.catalog()
            by = defaultdict(int)
            for v in c.values():
                by[v.get("l3_name") or v.get("l3")] += 1
            print(f"店铺商品 {len(c)} 个，按 L3 类目:")
            for k, n in sorted(by.items(), key=lambda x: -x[1]):
                print(f"  {n:>4}  {k}")

        elif a.cmd == "clusters":
            c = load_catalog()
            gs = W.clusters(c, sim=a.sim)
            tot = sum(g["size"] for g in gs)
            print(f"相似度 ≥{a.sim} 聚类: {len(gs)} 个簇 / {tot} 个链接")
            print(f"  平均每簇 {tot/max(len(gs),1):.1f} 个 → "
                  f"用代表提报可省 {(1-len(gs)/max(tot,1))*100:.0f}% 名额")
            for g in sorted(gs, key=lambda x: -x["size"])[:20]:
                print(f"  [{g['size']}个] L3={g['l3']}  {g['rep_pid']}  {g['rep_title'][:52]}")

        elif a.cmd == "pool":
            leads = W.pool()
            by = defaultdict(int)
            for v in leads.values():
                by[(v.get("l3"), v.get("l3_name"))] += 1
            print(f"机会池 {len(leads)} 个，按 L3 类目:")
            for (l3, nm), n in sorted(by.items(), key=lambda x: -x[1])[:25]:
                print(f"  {n:>4}  L3={l3}  {nm}")

        elif a.cmd == "plan":
            catalog = load_catalog()
            leads = json.loads(POOL_FILE.read_text())
            gs = W.clusters(catalog, sim=a.sim)
            r = W.plan(catalog=catalog, clusters=gs, leads=leads, mode=a.mode,
                       max_per_lead=a.max_per_lead)
            print(f"模式={r['mode']}  机会池 {r['n_leads_total']} → 可提报 {r['n_leads_plannable']} 个")
            print(f"  商品对 {r['n_pairs']}  调用次数 {r['n_calls']}（一个机会一次）")
            print(f"  相似度范围 {min((p['sim_min'] or 0) for p in r['plan']):.2f} ~ "
                  f"{max((p['sim_max'] or 0) for p in r['plan']):.2f}"
                  if r["plan"] else "  （无可提报机会）")
            for p in r["plan"][:20]:
                print(f"  L3={p['l3']} vol={p['search_volume']} "
                      f"选{p['n_chosen']}/{p['n_candidates']} sim={p['sim_min']}~{p['sim_max']}"
                      f"  {str(p['opportunity_name'])[:44]}")
            sk = defaultdict(int)
            for s in r["skipped"]:
                sk[s["reason"][:34]] += 1
            print(f"\n  跳过 {len(r['skipped'])} 个机会，原因分布:")
            for k, n in sorted(sk.items(), key=lambda x: -x[1])[:8]:
                print(f"    {n:>4}  {k}")
            PLAN_FILE.write_text(json.dumps(r, ensure_ascii=False, indent=1))
            print(f"\n→ {PLAN_FILE}")

        elif a.cmd == "run":
            r = json.loads(PLAN_FILE.read_text())
            plan = r["plan"][a.offset:]
            if a.limit:
                plan = plan[:a.limit]
            n_pairs = sum(p["n_chosen"] for p in plan)
            print(f"{'真写' if a.yes else 'dry-run'}："
                  f"{len(plan)} 个机会 / {n_pairs} 对（总计划 {r['n_leads_plannable']} 个机会）")
            t0 = time.time()
            res = W.run(plan, apply=a.yes)
            dt = time.time() - t0
            if res["calls"]:
                print(f"  耗时 {dt/60:.1f} 分钟  ({dt/res['calls']:.1f}s/次调用)")
            print(f"\n调用 {res['calls']}  拟提交 {res['attempted']} 对")
            print(f"  应答成功 {res['ok_resp']}  超时 {res['timeout']}  业务错 {len(res['http_err'])}")
            for e in res["http_err"][:10]:
                print(f"    ✗ {e.get('lead_id')} {e.get('code','')} "
                      f"{str(e.get('message') or e.get('error'))[:74]}")
            RESULT_FILE.write_text(json.dumps(res, ensure_ascii=False, indent=1))

        elif a.cmd == "verify":
            r = json.loads(PLAN_FILE.read_text())
            leads = {p["lead_id"] for p in r["plan"]}
            catalog = load_catalog()
            v = W.verify(leads, minutes=a.minutes, catalog=catalog)
            print(f"最近 {a.minutes} 分钟:")
            print(f"  ★ 成功提报 {v['approved_pairs']} 条"
                  f"（去重后不同商品 {v['approved_listings']} 个）")
            print(f"    被拒 {v['rejected_pairs']} 条   命中率 {v['hit_rate']}")
            print(f"    按命中率算并不重要 —— 规则3 看的是上面的成功条数")
            print(f"  按机会:")
            for lid, n in v["by_lead"].items():
                print(f"    {n:>3} 条  {lid}")
            json.dump(v, open(PLAN_FILE.parent / "weekly_verified.json", "w"),
                      ensure_ascii=False, indent=1)
    finally:
        W.close()


if __name__ == "__main__":
    try:
        main()
    except OppError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("中断", file=sys.stderr)
    except Exception:
        import traceback
        traceback.print_exc()
