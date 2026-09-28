#!/usr/bin/env python3
"""把散落各处的接口清单汇总成主表 + 出差集/缺口报告。

输入（存在即读）：
  notes/api_inventory/mf_all.json          微前端抽取（本轮主力）
  notes/api_inventory/enriched.json        联盟中心（bundle 抽取）
  notes/api_inventory/finance_paths.json   财务（bundle 抽取）
  notes/tt_api_map_full.json               早期商品/广告抽取
  tk01_*.py / tt_captcha.py 等客户端里的路径字面量

输出：
  ALL_API_INVENTORY.md      全量接口主表（按业务域分组）
  API_GAP_REPORT.md         差集 / 缺口报告
  notes/api_inventory/master.json
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
AI = HERE / "notes" / "api_inventory"

# ── 业务域分类：按路径前缀，顺序即优先级 ──
DOMAINS: list[tuple[str, str]] = [
    ("履约 / 物流 / 面单", r"^/(widget/)?api/(v\d+/)?fulfillment/|^/api/v\d+/(logistics|shipping)/|^/api/v\d+/seller/(warehouses|delivery)"),
    ("财务 / 结算 / 税务", r"/pay/|/finance/|/tax/|/settlement|/invoice|/acquiring|/payout|deposit/get"),
    ("联盟 / 达人", r"/affiliate/|/alliance/|/creator/marketplace|/invitation_group|/crm/|/partner/|open_collaboration"),
    ("商品 / 库存 / 定价", r"^/api/v\d+/(product|products|inventory|sku|catalog|category|brand)|/product/(create|edit|manage)|/multi_region_listing|/pricing|/sea_product"),
    ("订单 / 售后", r"^/(widget/)?api/v\d+/(order|orders|reverse|return|refund)|^/(api/)?reverse/|/fulfillment/order|/order/"),
    ("营销 / 促销", r"^/api/v\d+/(promotion|marketing|coupon|voucher|discount|flash)|/promotion/|/campaign/|^/api/v2/promotion"),
    ("数据 / 罗盘 / 报表", r"/insights/|/compass/|/data_infra|/analytics|/report|/dashboard|/statistic|/growth_center"),
    ("消息 / IM / 通知", r"/im/|/message|/notification/|/chat|/shop_im|/conversation"),
    ("治理 / 违规 / 申诉", r"/governance|/violation|/warning|/appeal|/qualification|/compliance"),
    ("商家 / 入驻 / 资质", r"/seller/join|/onboard|/merchant|/account/|/entity|/shop_setting|/seller/(account|profile)"),
    ("店铺运营 / 工作台", r"/workbench|/homepage|/seller/(home|tasks|popup|banner|menu|badge)|/task-center|/island"),
    ("私域 / 粉丝 / 会员", r"/privatedomain|/fans|/member|/crm_toc|/sea_seller"),
    ("广告 / 投放", r"/ads/|/ads-creation|/adcode|/campaign/"),
    ("账号安全 / 通行证", r"/passport/|/two_step_verification|/totp|/account_verification|/login"),
    ("客服消息 / 站内信", r"/gs_message/|/helpdesk|/sellerassistant/|/message_center|/msg_card|/chat/"),
    ("直播 / 达人运营", r"/live_center/|/seller/creator/|/official_creator|/live_manager|/live_app"),
    ("学习中心 / 内容", r"/learning_center/|/university|/creativityhub|/guide/|/edu_comp"),
    ("店铺授权 / 子账号 / 角色", r"/seller/delegation/|/custom_role/|/seller/semi/|/sub_account|/seller_settings/"),
    ("内容创作 / 视频中心", r"/video_center/|/seller/logo/|/university/cms|/seller_template/|/image/(upload|url)|/multimedia/|/aigc"),
    ("商品成长 / 优化 / 机会", r"/pop/product_growth|/dbmp/|/pop/product/optimize|/seller/growth|/product/opportunit|/optimizer|/sales-accelerator"),
    ("交易（/trade 前缀，另一套）", r"^/(widget/)?api/v\d+/trade/"),
    ("全球仓 / 跨境 / 区域", r"/seller/global/|/seller/region/|/seller/toko/|/cross_border|/multi_region"),
    ("达人外联 / 任务消息", r"/seller/outreach/|/task_message|/seller/sell/mission|/cb/seller/incentives"),
    ("开店 / 入驻清单", r"/seller/open_shop/|/open_shop"),
    ("平台基础设施", r"/i18n_conf|/common/|/arch/|/config_center|/grayscale|/sentry|/feelgood|/bs/|/map/|/address_component|/cdn_rule|/session_replay|/recording|/ticket/|/sdk/|/web-cookie|/init/|/user/webid|/sitebuilder|/dynamic_configs|/debugs"),
]

VERIFIED_SRC = {
    "联盟中心": re.compile(r"^/api/v1/(affiliate|oec/affiliate|im|insights/affiliate)"),
    "财务": re.compile(r"^/(api/v1/(pay|finance|tax)|api/oec/(pay|finance)|widget/api/v1/(pay|tax))"),
}


def domain_of(p: str) -> str:
    for name, pat in DOMAINS:
        if re.search(pat, p):
            return name
    return "其他 / 未分类"


def norm(p: str) -> str:
    p = re.sub(r"\$\{[^}]*\}", "{v}", p)
    p = re.sub(r"\?.*$", "", p)
    return re.sub(r"/+$", "", p)


def load_all():
    """返回 {path: {sources:set, methods:Counter, names:set}}"""
    acc: dict[str, dict] = {}

    def add(p, src, method=None, name=None):
        if not p or len([x for x in p.split("/") if x]) < 3:
            return
        if not p.startswith("/"):
            p = "/" + p
        e = acc.setdefault(p, {"sources": set(), "methods": collections.Counter(),
                               "names": set()})
        e["sources"].add(src)
        if method and method != "?":
            e["methods"][method] += 1
        if name:
            e["names"].add(name)

    # 1) 微前端
    f = AI / "mf_all.json"
    if f.exists():
        d = json.loads(f.read_text(encoding="utf-8"))
        for mf, v in d.items():
            for r in v.get("endpoints", []):
                add(norm(r["path"]), f"微前端:{mf}", r.get("method"),
                    (r.get("names") or [None])[0])
    # 2) 联盟
    f = AI / "enriched.json"
    if f.exists():
        for r in json.loads(f.read_text(encoding="utf-8")):
            add(norm(r["path"]), "联盟bundle", r.get("method"))
    # 3) 财务
    f = AI / "finance_paths.json"
    if f.exists():
        for r in json.loads(f.read_text(encoding="utf-8")):
            add(norm(r["path"]), "财务bundle", r.get("method"),
                (r.get("names") or [None])[0])
    # 4) 早期抽取
    for nm in ("tt_api_map_full.json", "tt_api_map.json"):
        f = HERE / "notes" / nm
        if not f.exists():
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            for k, v in d.items():
                m = None
                p = k
                mm = re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+(.*)$", k)
                if mm:
                    m, p = mm.group(1), mm.group(2)
                elif isinstance(v, dict):
                    m = v.get("method")
                    p = v.get("path") or v.get("url") or k
                add(norm(p), f"早期:{nm.replace('.json','')}", m)
    # 5) 我们自己客户端里的（保证不漏）
    for py in sorted(HERE.glob("tk*.py")) + [HERE / "tt_captcha.py"]:
        if not py.exists():
            continue
        s = py.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'"((?:/?(?:widget/)?api|/oec)/[A-Za-z0-9_/\-{}]{3,120})"', s):
            add(norm(m.group(1)), f"客户端:{py.stem}")
    return acc


def dedup_prefixless(paths: dict) -> tuple[dict, int]:
    """合并「缺 /api 前缀」的重复条目。

    微前端里同一批接口有两种写法：``uriPrefix + "/api/v1/insights/x"`` 和
    单独抽出来的 ``"/insights/x"``（后者来自"路径紧邻 method"的邻接判据，
    因为 uriPrefix 是运行时的，抽不到）。后者补上 ``/api/vN`` 后往往**已经在表里**。

    实测：791 个无前缀条目里 **668 个是纯重复**（`/insights/*`、`/qualification/*`、
    `/seller/onboard/*`、`/seller/growth_center/*`），只有 123 个是真的独立服务
    前缀（`/passport/*` 登录、`/aff/*` 会员、`/easesafe/*`）。

    不合并的后果有两个：主表虚高 668 条；而且这些条目探测时返回
    **http=200 + 空 body**（打到了 SPA 而不是 API），白白污染实测结果。
    """
    noprefix = [p for p in list(paths)
                if not p.startswith("/api") and not p.startswith("/widget")]
    merged = 0
    for p in noprefix:
        target = next((c for c in (f"/api/v1{p}", f"/api/v2{p}") if c in paths), None)
        if target is None:
            continue
        for k, v in paths[p].items():
            if k == "sources":
                paths[target]["sources"] = sorted(set(paths[target].get("sources", [])) | set(v))
            elif k == "names":
                paths[target]["names"] = sorted(set(paths[target].get("names", [])) | set(v))
            elif not paths[target].get(k):
                paths[target][k] = v
        del paths[p]
        merged += 1
    return paths, merged


def main():
    acc = load_all()
    raw_n = len(acc)
    acc, merged = dedup_prefixless(acc)
    print(f"汇总唯一接口 {raw_n} 个 → 合并缺前缀重复 {merged} 个 → 实得 {len(acc)} 个")

    by_domain = collections.defaultdict(list)
    for p, e in acc.items():
        by_domain[domain_of(p)].append((p, e))

    # 主表
    L = []
    W = L.append
    W("# 卖家中心全量接口清单（主表）")
    W("")
    W("> 汇总来源：微前端 bundle 抽取 + 联盟/财务专项 + 早期抽取 + 客户端实现。")
    W("> 自动生成，重跑 `python3 build_api_master.py` 刷新。")
    W("")
    tot = len(acc)
    src_cnt = collections.Counter()
    for e in acc.values():
        for s in e["sources"]:
            src_cnt[s.split(":")[0]] += 1
    W(f"**唯一接口 {tot} 个**；来源分布：" +
      " / ".join(f"{k} {v}" for k, v in src_cnt.most_common()))
    W("")
    W("| 业务域 | 接口数 |")
    W("|---|---|")
    for name, _ in DOMAINS + [("其他 / 未分类", "")]:
        n = len(by_domain.get(name, []))
        if n:
            W(f"| {name} | {n} |")
    W("")
    for name, _ in DOMAINS + [("其他 / 未分类", "")]:
        items = by_domain.get(name)
        if not items:
            continue
        items.sort(key=lambda kv: kv[0])
        W(f"## {name}（{len(items)}）")
        W("")
        W("| 方法 | 路径 | 来源 | 调用点 |")
        W("|---|---|---|---|")
        for p, e in items:
            m = e["methods"].most_common(1)[0][0] if e["methods"] else "?"
            src = ",".join(sorted(x.split(":")[0] for x in e["sources"]))
            nms = ", ".join(f"`{x}`" for x in sorted(e["names"])[:2])
            W(f"| `{m}` | `{p}` | {src} | {nms} |")
        W("")
    (HERE / "ALL_API_INVENTORY.md").write_text("\n".join(L), encoding="utf-8")

    # 缺口报告
    known_verified = set()
    for name, rx in VERIFIED_SRC.items():
        known_verified |= {p for p in acc if rx.search(p)}
    L2 = []
    W2 = L2.append
    W2("# 接口缺口报告")
    W2("")
    W2("## 1. 按业务域的覆盖情况")
    W2("")
    W2("| 业务域 | 接口数 | 已实测过? | 说明 |")
    W2("|---|---|---|---|")
    KNOWN = {
        "财务 / 结算 / 税务": "✅ 已做（FINANCE_API.md，89 个实测 + 全链下载验证）",
        "联盟 / 达人": "✅ 已做（AFFILIATE_API.md，564 个 / 35 实测）",
        "消息 / IM / 通知": "◐ 部分（站内 IM protobuf 全通，通知类未爬）",
        "营销 / 促销": "◐ 部分（促销创建已通，优惠券/活动未爬）",
        "商品 / 库存 / 定价": "◐ 部分（商品发布/库存有零散记录，未成体系）",
        "履约 / 物流 / 面单": "❌ 空白 —— 本轮新发现 250+ 接口",
        "数据 / 罗盘 / 报表": "❌ 空白",
        "治理 / 违规 / 申诉": "❌ 空白",
        "商家 / 入驻 / 资质": "❌ 空白",
        "店铺运营 / 工作台": "❌ 空白",
        "私域 / 粉丝 / 会员": "❌ 空白",
        "订单 / 售后": "❌ 空白",
        "广告 / 投放": "◐ 部分",
        "平台基础设施": "◐ 部分（i18n/currency 已通）",
    }
    for name, _ in DOMAINS + [("其他 / 未分类", "")]:
        items = by_domain.get(name)
        if not items:
            continue
        W2(f"| {name} | {len(items)} | | {KNOWN.get(name, '未评估')} |")
    W2("")
    W2("## 2. 缺口优先级（建议爬取顺序）")
    W2("")
    gaps = []
    for name, _ in DOMAINS + [("其他 / 未分类", "")]:
        n = len(by_domain.get(name, []))
        if not n:
            continue
        k = KNOWN.get(name, "")
        if k.startswith("❌"):
            gaps.append((n, name, k))
    for i, (n, name, k) in enumerate(sorted(gaps, reverse=True), 1):
        W2(f"{i}. **{name}** —— {n} 个接口，{k}")
    W2("")
    (HERE / "API_GAP_REPORT.md").write_text("\n".join(L2), encoding="utf-8")

    (AI / "master.json").write_text(json.dumps(
        {p: {"sources": sorted(e["sources"]),
             "method": e["methods"].most_common(1)[0][0] if e["methods"] else "?",
             "names": sorted(e["names"])[:3],
             "domain": domain_of(p)} for p, e in acc.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"→ ALL_API_INVENTORY.md ({len(L)} 行)")
    print(f"→ API_GAP_REPORT.md ({len(L2)} 行)")
    print(f"→ notes/api_inventory/master.json")
    print("\n域分布:")
    for name, _ in DOMAINS + [("其他 / 未分类", "")]:
        n = len(by_domain.get(name, []))
        if n:
            print(f"  {n:>5}  {name}")


if __name__ == "__main__":
    main()
