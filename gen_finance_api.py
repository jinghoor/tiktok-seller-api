#!/usr/bin/env python3
"""生成 FINANCE_API.md —— seller 中心【财务】板块全量接口手册。

数据源：notes/api_inventory/finance_paths.json
（由 extract_finance_paths.py 从 notes/fin_js + notes/fin_mf 抽取）
"""
from __future__ import annotations

import collections
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
rows = json.loads((HERE / "notes" / "api_inventory" / "finance_paths.json")
                  .read_text(encoding="utf-8"))

# 页面 → 接口族。操作员给的三个 URL 对应的就是这三块。
# 真流量捕获（capture_finance_live.py）—— 最高置信度来源
_LIVE = HERE / "notes" / "api_inventory" / "finance_live.json"
LIVE: dict[str, str] = {}          # path -> 真流量里的 method
LIVE_PAGES: dict[str, set] = {}
if _LIVE.exists():
    for _name, _pg in json.loads(_LIVE.read_text(encoding="utf-8")).items():
        for _r in _pg.get("requests", []):
            _u = _r["url"].split("?")[0]
            if "/api/" in _u:
                _p = "/api/" + _u.split("/api/", 1)[1]
                LIVE.setdefault(_p, _r["method"])
                LIVE_PAGES.setdefault(_p, set()).add(_name)


def eff_method(r) -> str:
    """★ 真流量捕获的方法优先于静态推断 —— 静态只能看 `method:` 附近，
    别名（a.UD）和相邻调用都会干扰，实测过 12 个被误标。"""
    return LIVE.get(r["path"], r["method"])


def live_badge(r) -> str:
    p = r["path"]
    if p in LIVE:
        return "✅" if LIVE[p] == r["method"] else "◑"   # ◑ = 静态方法标错，已用真值纠正
    return ""

PAGES = {
    "bills": "https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview",
    "deposit": "https://seller.tiktokshopglobalselling.com/deposit",
    "bill-payment": "https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN",
}

FAMILIES: list[tuple[str, str, str]] = [
    ("A. 对账单 / 账单明细（bills 页，新版 oec 网关）",
     r"^/api/oec/pay/merchant/statement/",
     "`view/*` 是账单主页；`profit_loss/*` 是损益下钻；`config/*` 是账单字段配置（26 个）"),
    ("B. 对账单 / 交易明细 / 余额明细（bills 页，旧版）",
     r"^/api/v1/pay/statement/",
     "`SearchStatement` / `SearchStatementOrder` / `SearchTransactionDetail` / `SearchAccountsBalance`"),
    ("C. 结算 / 提现 / 打款周期（deposit 页主体）",
     r"^/api/v1/pay/settlement/",
     "余额、提现、打款周期、协议、押金冻结、对账文件导出"),
    ("D. 打款账户 / 收款方式 / KYC",
     r"^/api/v1/pay/(payout|account)/",
     "卖家侧 PI（收款方式）读写；`pay/account/kyc/get` 是支付 KYC"),
    ("E. 达人结算与联盟对账单",
     r"^/api/v1/pay/(creator|affiliate)/",
     "达人佣金、达人提现、达人税务；`pay/affiliate/statement/*` 是联盟对账单"),
    ("F. 支付单聚合（seller / creator / biz）",
     r"^/api/v1/pay/biz/",
     "`pay/biz/order/{seller,creator}` 与聚合接口"),
    ("G. 支付前置 / 入驻 / 税务信息",
     r"^/api/v1/pay/(onboard|tax_info|tax_audit|meta)",
     "`pay/onboard_info/*`、`pay/tax_info/{get,set}`、`pay/meta/info/get`"),
    ("H. 账单支付 / 充值 / 收银台（bill-payment 页）",
     r"^/api/v1/finance/purchase/",
     "`Recharge` / `MPayOrder` / `AppendPay` / 收银台组件 / 余额"),
    ("I. 收单 / 资金流水（acquiring）",
     r"^/api/v1/finance/acquiring/",
     "支付单、退款单、保证金退款、资金流水明细、流水导出"),
    ("J. 财务助手 / 账期政策（assistant / billing policy）",
     r"^/api/v1/finance/(assistant|billing)/",
     "`finance/assistant/*` 财务测算；`finance/billing/policy/*` JBP / 返点 / 账期"),
    ("K. 税务 / 发票 / 1099 / DAC7",
     r"^/api/v1/tax/",
     "税号、发票、Form 1099-K"),
    ("L. 挂件版（widget，内嵌小窗用）",
     r"^/widget/api/v1/(pay|tax)/",
     "与上面同族但走 `/widget/api` 前缀，供 iframe / 挂件调用"),
    ("M. AI 损益分析（pnl_roi_agent）",
     r"^/api/oec/finance/ai_infra/",
     "账单解读、损益 ROI 分析、流式返回"),
    ("N. 押金 / 保证金（入驻侧）",
     r"^/api/v1/seller/(join/)?cross_border/deposit/|^/api/v1/seller/onboard/v1/cross_border/deposit/|pay/settlement/biz/deposit/",
     "首类目押金查询、押金冻结"),
]

# 判定"是不是财务"：只看这几个前缀，白名单制（不做兜底猜测）
IS_FIN = re.compile(r"^/api/v1/finance/|^/api/v1/pay/|^/api/v1/tax/|^/widget/api/v1/(pay|tax)/|"
                    r"^/api/oec/pay/|^/api/oec/finance/|cross_border/deposit/")

fin_rows, noise_rows = [], []
for r in rows:
    (fin_rows if IS_FIN.search(r["path"]) else noise_rows).append(r)

L: list[str] = []
W = L.append
W("# seller 中心【财务】板块 —— 全量接口手册")
W("")
W("> 对应页面：")
for k, v in PAGES.items():
    W(f"> - `{k}` — {v}")
W("")
W("> **来源**：从财务页自己的前端 bundle 抽取（`notes/fin_js/` 81 个 + `notes/fin_mf/` 19 个）。")
W("> 不是猜的，每个路径都带抽到的调用点方法名。")
W("")
W(f"**共 {len(rows)} 个路径**，其中财务相关 **{len(fin_rows)} 个**，"
  f"随页面一起加载但非财务的 {len(noise_rows)} 个（IM / i18n / 物流 / 入驻等，见附 C）。")
W("")
W("| 实测标记 | 含义 |")
W("|---|---|")
W("| ✅ | **三个财务页首屏真实打过**（CDP 真流量捕获，218 个请求） |")
W("| ◑ | 真流量里出现过，**且静态抽取的方法标错了** —— 表里已是真值 |")
W("| 空 | 静态抽取到，未在首屏窗口内出现（多在二级 tab / 弹窗里懒调用） |")
W("")
W("| 方法分布 | 数量 |")
W("|---|---|")
for m, n in collections.Counter(eff_method(r) for r in fin_rows).most_common():
    W(f"| `{m}` | {n} |")
W("")
W("---")
W("")
W("## 0. 总览")
W("")
W("### 0.1 三个请求前缀（别混）")
W("")
W("| 前缀 | 网关 | 用途 |")
W("|---|---|---|")
W("| `/api/v1/pay/...` | 旧卖家网关 | 结算 / 提现 / 打款 / 对账单（bills、deposit 页主用） |")
W("| `/api/v1/finance/...` | 旧卖家网关 | 充值收银台（purchase）、收单资金（acquiring） |")
W("| `/api/oec/pay/merchant/...` | **oec 网关** | 新版对账单（bills 页主体），**无版本段** |")
W("| `/api/oec/finance/...` | **oec 网关** | AI 损益分析 |")
W("| `/widget/api/v1/pay/...` | 旧网关 | 挂件 / iframe 内嵌版，与 `/api/v1/pay` 同族 |")
W("")
W("### 0.2 ★ 三条抽取经验（自己续抓时必看）")
W("")
W("财务这套 bundle 的路径有**三种写法**，少覆盖一种就会漏一大片：")
W("")
W("| 写法 | 例子 | 漏了的后果 |")
W("|---|---|---|")
W("| 双引号字面量 | `\"/api/v1/finance/purchase/recharge\"` | 只抓到 87 个 |")
W("| **反引号模板** | `` `${this.uriPrefix}/api/v1/finance/purchase/balance` `` | 退款/收银台全漏 |")
W("| **`/api/v` + 模板变量** | `` `/api/v${e.version\\|\\|1}/pay/settlement/balance/get` `` | **整族 39 个结算接口全漏** —— 最容易踩 |")
W("")
W("版本号取 `${...\\|\\|N}` 里的默认值（几乎都是 1）。方法名从包裹它的具名方法取：")
W("")
W("```js")
W("GetBalance(e,t){ const r=`${this.uriPrefix}/api/v${e.version||1}/pay/settlement/balance/get`; ... }")
W("```")
W("")
W("### 0.3 前端路由 ≠ 接口")
W("")
W("`/finance/bills`、`/finance/transactions`、`/finance/bills_statement_version` 这些是**前端路由 / localStorage 键**，")
W("不是接口。第一版抽取把它们当成 API 了，已剔除。")
W("")
W("### 0.4 鉴权")
W("")
W("卖家中心 cookie 会话（`sessionid`）+ 常规 `aid=6556` / `app_name=i18n_ecom_shop` query。")
W("`/api/oec/` 族同样受签名墙约束（见 [AFFILIATE_API.md](.work/adfly/AFFILIATE_API.md) §0.2）。")
W("")
W("---")
W("")
for title, pat, note in FAMILIES:
    rx = re.compile(pat)
    hit = [r for r in rows if rx.search(r["path"])]
    if not hit:
        continue
    W(f"## {title}")
    W("")
    W(f"*{len(hit)} 个 · {note}*")
    W("")
    W("| 实测 | 方法 | 路径 | 调用点方法名 |")
    W("|---|---|---|---|")
    for r in sorted(hit, key=lambda x: (live_badge(x) != "✅", x["path"])):
        nm = ", ".join(f"`{n}`" for n in r["names"]) if r["names"] else ""
        W(f"| {live_badge(r)} | `{eff_method(r)}` | `{r['path']}` | {nm} |")
    W("")

W("---")
W("")
W("## 附 A. 三个页面分别打哪些接口")
W("")
W("### A.1 `/finance/bills?subTab=on-hold&tab=overview`（账单总览 / 待结算）")
W("")
for p in ["/api/oec/pay/merchant/statement/view/statements",
          "/api/oec/pay/merchant/statement/view/amount_summary",
          "/api/oec/pay/merchant/statement/view/summary_breakdown",
          "/api/oec/pay/merchant/statement/view/onhold_orders",
          "/api/oec/pay/merchant/statement/view/settled_orders",
          "/api/oec/pay/merchant/statement/view/reserve_orders",
          "/api/oec/pay/merchant/statement/view/order_breakdown",
          "/api/oec/pay/merchant/statement/view/fund_base_info",
          "/api/oec/pay/merchant/statement/view/negative_balance_transactions",
          "/api/oec/pay/merchant/statement/view/order_breakdown",
          "/api/oec/pay/merchant/statement/view/config",
          "/api/oec/pay/merchant/statement/profit_loss/search_agg",
          "/api/oec/pay/merchant/statement/files/export"]:
    W(f"- `{p}`")
W("")
W("`subTab=on-hold` 对应的就是 `view/onhold_orders`；`view/settled_orders` 是已结算；")
W("`view/reserve_orders` 是预留/保证金；`view/negative_balance_transactions` 是负余额流水。")
W("")
W("### A.2 `/deposit`（余额 / 提现 / 打款）")
W("")
for p in ["/api/v1/pay/settlement/balance/get",
          "/api/v1/pay/settlement/balance/detail/query",
          "/api/v1/pay/settlement/amount/get",
          "/api/v1/pay/settlement/settings",
          "/api/v1/pay/settlement/withdraw",
          "/api/v1/pay/settlement/withdraw/search",
          "/api/v1/pay/settlement/withdraw/rules/get",
          "/api/v1/pay/settlement/withdraw/settlement_info",
          "/api/v1/pay/settlement/withdraw/detail/query",
          "/api/v1/pay/settlement/withdraw/fail/msg/query",
          "/api/v1/pay/settlement/auto/withdraw/config",
          "/api/v1/pay/settlement/auto/withdraw/info/query",
          "/api/v1/pay/settlement/payout/pi_infos",
          "/api/v1/pay/settlement/payout/manage_link",
          "/api/v1/pay/settlement/payout/create_or_update_payout_cycle",
          "/api/v1/pay/settlement/payout/bind_card",
          "/api/v1/pay/settlement/file/export",
          "/api/v1/pay/settlement/file/list",
          "/api/v1/pay/settlement/biz/deposit/freeze"]:
    W(f"- `{p}`")
W("")
W("### A.3 `/finance/bill-payment?shop_region=VN`（账单支付 / 充值）")
W("")
for p in ["/api/v1/finance/purchase/balance",
          "/api/v1/finance/purchase/recharge",
          "/api/v1/finance/purchase/recharge/order",
          "/api/v1/finance/purchase/pay",
          "/api/v1/finance/purchase/append_pay",
          "/api/v1/finance/purchase/order/mget",
          "/api/v1/finance/purchase/cashier/component",
          "/api/v1/pay/statement/payment/list",
          "/api/v1/pay/statement/list/detail",
          "/api/v1/finance/acquiring/payment/order/pay",
          "/api/v1/finance/acquiring/payment/order/list",
          "/api/v1/finance/acquiring/query/account"]:
    W(f"- `{p}`")
W("")
W("## 附 B. 怎么自己续抓")
W("")
W("```bash")
W("# 1. 财务页 HTML（★ 直连，走本地代理会超时）")
W("python3 notes/fin_js_list.py          # 读浏览器实时 cookie → 拉 3 个财务页 → 下首屏 JS")
W("")
W("# 2. 展开懒加载 chunk（两种命名都要覆盖：x.js 和 x.hash.js）")
W("python3 expand_finance_chunks.py      # 跑到文件数不再增加为止")
W("")
W("# 3. deposit 页的微前端本体（在 atlas 注册表里，不在 HTML 的 script 标签里）")
W("python3 fetch_mf_finance.py           # mf_finance/1.0.0.4610/TTS/unihan/mf_finance.js + 18 个 chunk")
W("")
W("# 4. 抽接口（三种路径写法都要覆盖）")
W("python3 extract_finance_paths.py")
W("")
W("# 5. 生成本手册")
W("python3 gen_finance_api.py")
W("```")
W("")
W("**四个坑**：")
W("")
W("1. **直连，不要走本地代理** —— 该域走代理会 25s 超时，直连 0.6s 拿 494KB。")
W("2. **懒加载 chunk 两种命名**：`payoutCycleSetting.k7hkdehg.js`（具名+hash）和 `b5xeyaup.js`（8 位 id 即文件名）。")
W("   早期正则只覆盖前者，chunk 展开不全 → 接口抽不全。")
W("3. **`mf_finance` 不在 HTML 的 script 标签里**，藏在 atlas 注册表的 `source_url` 字段：")
W("   `//lf16-oversea.goofy-cdn.com/obj/goofy-sg/gftar/i18n/ecom/shop/mf_finance/<ver>/TTS/unihan/mf_finance.js`")
W("   它是 webpack module federation，chunk 在 `oec-magellan-sg/i18n/ecom/TTS/unihan/mf_finance/static/js/`。")
W("4. **`/api/v` + `${version||1}` 模板** —— 见 §0.2，这条最容易整族漏掉。")
W("")
W("**没有 sourcemap**：所有 `.js.map` 一律 404，只能读压缩后的代码。")
W("")
W("## 附 C. 随财务页加载但非财务的接口")
W("")
W(f"共 {len(noise_rows)} 个，属 IM / i18n / 物流 / 入驻 / 地图 / 公共组件。仅列前缀分布：")
W("")
W("| 前缀 | 数量 |")
W("|---|---|")
cnt = collections.Counter()
for r in noise_rows:
    seg = [x for x in r["path"].split("/") if x]
    cnt["/".join(seg[:4])] += 1
for k, v in cnt.most_common(22):
    W(f"| `/{k}` | {v} |")
W("")

(HERE / "FINANCE_API.md").write_text("\n".join(L), encoding="utf-8")
print(f"FINANCE_API.md: {len(L)} 行")
print(f"  财务相关 {len(fin_rows)} / 非财务 {len(noise_rows)} / 总 {len(rows)}")
for title, pat, _ in FAMILIES:
    n = len([r for r in rows if re.search(pat, r["path"])])
    if n:
        print(f"  {n:>4}  {title}")
