#!/usr/bin/env python3
"""TikTok Shop 【财务】客户端 —— 本土店 + 跨境店统一接口。

## 一、为什么传输层是"借页面做页内 fetch"

财务接口有两个硬约束：

| 店型 | API 域 | 说明 |
|---|---|---|
| **本土**（`seller-vn.tiktok.com`） | **同源**，就是页面域 | 没有独立 API 域 |
| **跨境**（`seller.tiktokshopglobalselling.com`） | `api16-normal-sg.tiktokshopglobalselling.com` | **独立域，跨域** |

跨域 fetch 实测**放行**（CORS 允许，`code=0`）。而**拿页面域去打跨境 API 会落到 SPA 回退返回 HTML**
——不是 404，极易误判（第一遍 71 个接口因此被标成"未知"）。

所以本客户端：
- **借操作员已经打开的页面**做 fetch 源 —— 页内 `fetch()` 天然带 cookie、同源/跨域都行
- **不新建任何标签、不点击、不移动鼠标、不抢焦点**（`ctx.new_page()` 会激活标签，会打扰人，禁用）
- 后台标签也能跑：只有 timer 会被节流，`fetch` 不会

## 二、`aid` 不一样（★ 最容易错的地方）

| 店 | `aid` | `app_id` | `seller_id` |
|---|---|---|---|
| 跨境 SHOP_XBORDER | `6556` | `6556` | `7494XXXXXXXXXX00` |
| 本土 SHOP_LOCAL | `4068` | `4068` | `7494XXXXXXXXXX00` |

拿跨境的 query 打本土店必失败。这些都在 `tk01_config.py` 的 `shops.json` 里。

## 三、方法：绝大多数是 GET

源码里写的是 `method:a.UD`（**别名，不是字符串字面量**），`a.UD` == **GET**。
静态抽出来标 `?` 的，绝大多数其实是 GET —— 拿 POST 打会得到 **404**（不是参数错）。

## 四、★ 批量下载是两段式

```
1) 建导出任务   POST .../export  |  .../create_download  |  .../details_export
2) 轮询 / 列历史 GET  .../export_task | .../file/list | .../download_history
3) 换签名地址   GET  .../file
   → {"code":0,"download_url":"/wsos_v2/oec-tax/object/xxx?expire=…&timeStamp=…&sign=…"}
4) GET 那个 download_url 取二进制（expire/timeStamp/sign 缺一不可，现签现用会过期）
```

## 五、用法

```bash
python3 tk01_finance.py --shop tk01 settings          # 结算配置（含 statement_version）
python3 tk01_finance.py --shop tk01 statements --list  # 对账单
python3 tk01_finance.py --shop tk89 balance           # 余额
python3 tk01_finance.py --shop tk89 order-list --status 2   # 已结算交易
python3 tk01_finance.py --shop tk89 invoice           # 发票列表
python3 tk01_finance.py --shop tk89 file-list         # 结算文件导出历史
python3 tk01_finance.py --shop tk89 download <url> -o out.xlsx
python3 tk01_finance.py --shop tk89 batch-export --kind statement   # 完整两段式
```
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import tk01_config as CFG  # noqa: E402

# 业务域 → (方法, 路径)。method 用实测值：源码里 a.UD 别名 = GET。
READ = {
    # 结算 / 余额 / 提现
    "settings":            ("GET",  "/api/v1/pay/settlement/settings"),
    "balance":             ("GET",  "/api/v1/pay/settlement/balance/get"),
    "balance_detail":      ("GET",  "/api/v1/pay/statement/balance/detail/query"),
    "amount_get":          ("GET",  "/api/v1/pay/settlement/amount/get"),
    "settlement_account":  ("GET",  "/api/v1/seller/settlement/account/get"),
    "withdraw_rules":      ("GET",  "/api/v1/pay/settlement/withdraw/rules/get"),
    "auto_withdraw_info":  ("GET",  "/api/v1/pay/settlement/auto/withdraw/info/query"),
    "compliance_security": ("GET",  "/api/v1/pay/settlement/info/compliance/security/get"),
    "withdraw_fail_msg":   ("GET",  "/api/v1/pay/settlement/withdraw/fail/msg/query"),
    "payout_config":       ("POST", "/api/v1/pay/settlement/payout/query_payout_config"),
    "payout_block_check":  ("GET",  "/api/v1/pay/settlement/payout/reverse_block_check"),
    # 对账单 / 交易明细
    "stat_info":           ("GET",  "/api/v1/pay/statement/stat/info"),
    "order_list":          ("GET",  "/api/v1/pay/statement/order/list"),
    "payment_list":        ("GET",  "/api/v1/pay/statement/payment/list"),
    "notify_msg":          ("GET",  "/api/v1/pay/statement/notify/msg"),
    "transaction_detail":  ("GET",  "/api/v1/pay/statement/transaction/detail"),
    "statement_list":      ("POST", "/api/v1/pay/statement/list/detail"),
    "statement_gray":      ("POST", "/api/v1/pay/statement/gray"),
    # 导出文件（v1/v2 都有，见 file_list）
    "file_list":           ("GET",  "/api/v1/pay/settlement/file/list"),
    "file_list_v2":        ("GET",  "/api/v2/pay/settlement/file/list"),
    "file_export":         ("POST", "/api/v1/pay/settlement/file/export"),
    # ★ file/list（导出历史）与 file/download 都是 **GET 带 query**，不是 POST：
    #   源码 `queryStringify(t)` + `method:a.UD`，a.UD == GET。标 POST 会 404。
    "file_download":       ("GET",  "/api/v1/pay/settlement/file/download"),
    # 发票 / 税务
    "invoice_search":      ("GET",  "/api/v1/tax/invoice/search"),
    "invoice_export_task": ("GET",  "/api/v1/tax/invoice/export_task"),
    "invoice_file":        ("GET",  "/api/v1/tax/invoice/file"),
    "invoice_export":      ("POST", "/api/v1/tax/invoice/export"),
    "invoice_details_export": ("POST", "/api/v1/tax/invoice/details_export"),
    "tax_info":            ("GET",  "/api/v1/tax/tax_info/get"),
    "shop_entity":         ("GET",  "/api/v1/tax/shop_entity"),
    "tax_report_search":   ("GET",  "/api/v1/tax/report/search"),
    # 收单资金流水
    "acquiring_account":   ("POST", "/api/v1/finance/acquiring/query/account"),
    "acquiring_txn_list":  ("POST", "/api/v1/finance/acquiring/transaction/file/list"),
    "acquiring_txn_create": ("POST", "/api/v1/finance/acquiring/transaction/file/create"),
    "acquiring_txn_download": ("POST", "/api/v1/finance/acquiring/transaction/file/download"),
    # 财务助手 / 账期政策
    "assistant_config":    ("POST", "/api/v1/finance/assistant/config"),
    "billing_jbp":         ("POST", "/api/v1/finance/billing/policy/jbp_process/query"),
    # oec 新版对账单（无版本段）
    "oec_view_config":     ("POST", "/api/oec/pay/merchant/statement/view/config"),
    "oec_statements":      ("POST", "/api/oec/pay/merchant/statement/view/statements"),
    "oec_amount_summary":  ("POST", "/api/oec/pay/merchant/statement/view/amount_summary"),
    "oec_onhold":          ("POST", "/api/oec/pay/merchant/statement/view/onhold_orders"),
    "oec_settled":         ("POST", "/api/oec/pay/merchant/statement/view/settled_orders"),
    "oec_reserve":         ("POST", "/api/oec/pay/merchant/statement/view/reserve_orders"),
    "oec_negative":        ("POST", "/api/oec/pay/merchant/statement/view/negative_balance_transactions"),
    "oec_fund_base":       ("POST", "/api/oec/pay/merchant/statement/view/fund_base_info"),
    "oec_order_breakdown": ("POST", "/api/oec/pay/merchant/statement/view/order_breakdown"),
    "oec_summary_breakdown": ("POST", "/api/oec/pay/merchant/statement/view/summary_breakdown"),
    "oec_file_list":       ("GET",  "/api/oec/pay/merchant/statement/files"),
    "oec_file_export":     ("POST", "/api/oec/pay/merchant/statement/files/export"),
    "oec_file_download":   ("GET",  "/api/oec/pay/merchant/statement/files/download"),
    "oec_pl_search":       ("POST", "/api/oec/pay/merchant/statement/profit_loss/search_agg"),
    "oec_pl_create_dl":    ("POST", "/api/oec/pay/merchant/statement/profit_loss/create_download"),
    "oec_pl_history":      ("POST", "/api/oec/pay/merchant/statement/profit_loss/download_history"),
}

# 完整两段式的候选组合：建任务 → 轮询 → 换签名地址
EXPORT_KINDS = {
    "statement": {"create": "file_export", "poll": "file_list", "fetch": "file_download"},
    "statement_v2": {"create": "file_export", "poll": "file_list_v2", "fetch": "file_download"},
    "invoice":   {"create": "invoice_export", "poll": "invoice_export_task", "fetch": "invoice_file"},
    "invoice_detail": {"create": "invoice_details_export", "poll": "invoice_export_task", "fetch": "invoice_file"},
    "acquiring": {"create": "acquiring_txn_create", "poll": "acquiring_txn_list", "fetch": "acquiring_txn_download"},
    "profit_loss": {"create": "oec_pl_create_dl", "poll": "oec_pl_history", "fetch": "oec_file_download"},
    "oec_file":  {"create": "oec_file_export", "poll": "oec_file_list", "fetch": "oec_file_download"},
}


class FinanceError(RuntimeError):
    pass


# ── 从 bundle 挖出的枚举（不是猜的）──
FILE_TYPE = {"settlement_detail": 1, "onhold_unsettled": 7, "onhold_unreleased_reserve": 8}
FILE_STATUS = {1: "导出中", 2: "已导出", 3: "已查看"}
TIME_TYPE = {"settlement_to_account": 1}
STATEMENT_VERSION = {"zero": 0}


class FinanceClient:
    """财务 API。传输 = 借操作员已打开的页面做页内 fetch（零打扰）。"""

    def __init__(self, shop: str | None = None, *, port: int | None = None,
                 page_hint: str | None = None, verbose: bool = False):
        self.shop = CFG.load_shop(shop)
        self.key = self.shop["_key"]
        self.port = port or self.shop["cdp_port"]
        self.page_hint = page_hint
        self.verbose = verbose
        self._pw = None
        self._browser = None
        self._page = None

    # ── 域与鉴权块 ──
    @property
    def is_local(self) -> bool:
        """本土店：卖家中心域名本身就是 API 域（同源）。"""
        return "tiktokshopglobalselling" not in self.shop["seller_origin"]

    @property
    def api_base(self) -> str:
        return self.shop["seller_origin"] if self.is_local else self.shop["api_host"]

    @property
    def page_origin(self) -> str:
        return self.shop["seller_origin"]

    @property
    def query_block(self) -> str:
        sid = self.shop["seller_id"]
        aid = self.shop["aid"]
        return (f"aid={aid}&app_id={aid}&app_name={self.shop['api_app_name']}"
                f"&device_platform=web&oec_seller_id={sid}&seller_id={sid}"
                f"&locale=zh-CN&language=zh-CN")

    # ── 借页面 ──
    def _connect(self):
        if self._page is not None:
            return self._page
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
        ctx = self._browser.contexts[0]
        pages = [p for p in ctx.pages if not p.url.startswith("chrome-extension")]
        if self.page_hint:
            hit = next((p for p in pages if self.page_hint in p.url), None)
            if hit:
                self._page = hit
        if self._page is None:
            # 只要同源就行 —— 卖家中心的任意页面都能当 fetch 源
            self._page = next((p for p in pages if p.url.startswith(self.page_origin)), None)
        if self._page is None:
            # 退而求其次：API 域上的页面（本土店就是页面域）
            self._page = next((p for p in pages if p.url.startswith(self.api_base)), None)
        if self._page is None:
            raise FinanceError(
                f"没找到可借的页面（端口 {self.port}，需要 {self.page_origin} 下任意一个已打开的页面）。"
                f"现有页面：{[p.url[:70] for p in pages]}")
        if self.verbose:
            print(f"  [借页面] {self._page.url[:88]}", file=sys.stderr)
        return self._page

    def close(self):
        # 绝不关操作员的页面、绝不 close 浏览器
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
        self._page = None
        self._pw = None

    # ── 页内 fetch ──
    JS_FETCH = """async (job) => {
      try {
        const opt = { method: job.method, credentials: 'include',
                      headers: { 'content-type': 'application/json; charset=utf-8',
                                 'accept': 'application/json, text/plain, */*' } };
        if (job.method !== 'GET' && job.body !== null && job.body !== undefined)
          opt.body = JSON.stringify(job.body);
        const r = await fetch(job.url, opt);
        const ab = await r.arrayBuffer();
        const u8 = new Uint8Array(ab);
        let s = ''; for (let i = 0; i < u8.length; i += 8192)
          s += String.fromCharCode.apply(null, u8.subarray(i, i + 8192));
        return JSON.stringify({ http: r.status, b64: btoa(s) });
      } catch (e) {
        return JSON.stringify({ http: 0, err: String(e).slice(0, 200) });
      }
    }"""

    def _fetch_raw(self, url: str, method: str = "GET", body=None,
                   *, as_b64: bool = False):
        pg = self._connect()
        out = json.loads(pg.evaluate(self.JS_FETCH,
                                     {"url": url, "method": method,
                                      "body": body if body is not None else None}))
        if out.get("http") == 0:
            raise FinanceError(f"fetch 失败 {url[:110]}: {out.get('err')}")
        raw = base64.b64decode(out["b64"])
        if as_b64:
            return out["http"], raw
        txt = raw.decode("utf-8", "replace")
        try:
            return out["http"], json.loads(txt)
        except Exception:
            return out["http"], {"_non_json": txt[:400]}

    def call(self, name: str, *, params: dict | None = None, body=None,
             version: int | None = None, path: str | None = None,
             method: str | None = None):
        """调一个已登记的业务接口。"""
        if path is None:
            if name not in READ:
                raise FinanceError(f"未知接口 {name!r}；可用：{sorted(READ)}")
            m, path = READ[name]
            method = method or m
        method = (method or "GET").upper()
        if version and "/v1/" in path:
            path = path.replace("/v1/", f"/v{version}/")
        q = self.query_block
        if params:
            q += "&" + "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.api_base}{path}?{q}"
        http, data = self._fetch_raw(url, method, body)
        ok = isinstance(data, dict) and data.get("code") == 0
        if self.verbose or not ok:
            code = data.get("code") if isinstance(data, dict) else None
            msg = (data.get("message") if isinstance(data, dict) else str(data)[:80])
            print(f"  [{name}] http={http} code={code} {msg}"[:200], file=sys.stderr)
        return data

    def try_v1_then_v2(self, name: str, **kw):
        """先 v1 再 v2 —— 实测 `pay/settlement/file/list` 只有 v2 能通。"""
        r = self.call(name, **kw)
        if isinstance(r, dict) and r.get("code") not in (0, None):
            alt = name.replace("file_list", "file_list_v2")
            if alt in READ and alt != name:
                r2 = self.call(alt, **kw)
                if isinstance(r2, dict) and r2.get("code") == 0:
                    r2["_used_version"] = 2
                    return r2
        return r

    # ── 业务封装 ──
    def settings(self):
        return self.call("settings")

    def balance(self):
        return self.try_v1_then_v2("balance") if "balance_v2" in READ else self.call("balance")

    def statements(self, *, summary_types: str = "1,2,3",
                   page_size: int = 20, page_num: int = 1):
        return self.call("oec_statements",
                         body={"page_size": page_size, "page_num": page_num})

    def amount_summary(self, summary_types: str = "1,2,3"):
        # 服务端点名要这个字段：`summary_types is required`
        return self.call("oec_amount_summary", body={"summary_types": summary_types})

    def onhold_orders(self, *, page_size: int = 20, page_num: int = 1):
        return self.call("oec_onhold", body={"page_size": page_size, "page_num": page_num})

    def settled_orders(self, *, page_size: int = 20, page_num: int = 1):
        return self.call("oec_settled", body={"page_size": page_size, "page_num": page_num})

    def order_list(self, *, settlement_status: int = 2, size: int = 20, frm: int = 0,
                   page_type: int = 6):
        """`/api/v1/pay/statement/order/list`（GET）。
        `settlement_status`: 2 = 已结算（settled_tab），1 = 待结算。"""
        return self.call("order_list", params={
            "from": frm, "size": size, "page_type": page_type,
            "pagination_type": 1, "settlement_status": settlement_status,
            "statement_version": 0, "need_total_amount": "false",
            "terminal_type": 1, "no_need_sku_record": "true"})

    def balance_detail(self, *, transaction_type: int = 1, limit: int = 10, offset: int = 0):
        return self.call("balance_detail", params={
            "transaction_type": transaction_type, "limit": limit, "offset": offset})

    def invoice_search(self, *, size: int = 20, frm: int = 0, billing_party: int = 2):
        return self.call("invoice_search", params={
            "pagination_type": 1, "from": frm, "size": size,
            "billing_party": billing_party})

    def export_statement_file(self, begin_date: str, end_date: str, *,
                              file_type: int | str = 1, time_type: int | None = 1,
                              statement_version: int = 0):
        """建一条账单导出任务 —— 它会出现在「导出历史记录」里。

        `begin_date` / `end_date`: `YYYY-MM-DD`。
        `file_type`: 1=结算明细，7=待结算未结算订单明细，8=待结算未释放预留明细（见 FILE_TYPE）。
        `time_type`: 1 = 结算到账时间（交易明细页用）；传 None 则不带上。
        """
        if isinstance(file_type, str):
            file_type = FILE_TYPE[file_type]
        period = {"begin_date": begin_date, "end_date": end_date}
        if time_type is not None:
            period["time_type"] = time_type
        body = {"period": period, "file_type": file_type,
                "statement_version": statement_version}
        return self.call("file_export", body=body), body

    def export_history(self):
        """★ 导出历史记录。响应里 `files[]` 每条含 `file_id` / `status`。

        `status`: 1=导出中 2=已导出 3=已查看（FILE_STATUS）。
        """
        r = self.call("file_list")
        if isinstance(r, dict) and r.get("code") == 0:
            r["_decoded"] = self._decode_files(r)
        return r

    @staticmethod
    def _decode_files(r) -> list:
        """把 files[] 里每个 file_id 的 status 翻成人话（不改原数据）。"""
        out = []

        def walk(o):
            if isinstance(o, dict):
                if "file_id" in o:
                    out.append({**o, "status_text": FILE_STATUS.get(o.get("status"),
                                                                    f"status={o.get('status')}")})
                for v in o.values():
                    if isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(r)
        return out

    def download_history_file(self, file_id: str):
        """按 file_id 从导出历史下载（GET 带 query）。"""
        return self.call("file_download", params={"file_id": file_id})

    def file_list(self):
        """结算文件导出历史。★ 实测只有 v2 有数据，所以两个都试。"""
        r1 = self.call("file_list")
        if not (isinstance(r1, dict) and r1.get("code") == 0 and r1.get("data")):
            r2 = self.call("file_list_v2")
            if isinstance(r2, dict) and r2.get("code") == 0:
                r2["_v1_result"] = r1
                return r2
        return r1

    # ── ★ 两段式下载 ──
    @staticmethod
    def _extract_download_url(r) -> str | None:
        """从各种响应形状里挖出签名下载地址。"""
        if not isinstance(r, dict):
            return None
        cands = []

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and (
                            k in ("download_url", "url", "file_url", "signed_url")
                            or v.startswith("/wsos") or "sign=" in v and "expire=" in v):
                        cands.append(v)
                    elif isinstance(v, (dict, list)):
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(r)
        return cands[0] if cands else None

    def poll_ready(self, probe: str, *, tries: int = 12, delay: float = 3.0,
                   ready=None, **kw):
        """轮询直到导出任务就绪。默认判据：响应里出现 download_url。"""
        last = None
        for i in range(tries):
            last = self.call(probe, **kw)
            url = self._extract_download_url(last)
            if url and (ready is None or ready(last)):
                return last, url
            if ready and ready(last):
                return last, self._extract_download_url(last)
            time.sleep(delay)
        return last, self._extract_download_url(last)

    def download(self, url: str, dest: str | Path) -> dict:
        """GET 那个签名地址取二进制。相对路径会补上 api_base。"""
        full = url if url.startswith("http") else f"{self.api_base}{url}"
        http, raw = self._fetch_raw(full, "GET", as_b64=True)
        p = Path(dest)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        return {"http": http, "path": str(p), "bytes": len(raw),
                "sha256_head": __import__("hashlib").sha256(raw).hexdigest()[:16]}

    def batch_export(self, kind: str = "statement", *, out_dir: str | Path = "notes/fin_dl",
                     create_body=None, poll_tries: int = 12, save: bool = True):
        """完整两段式：建任务 → 轮询 → 换签名地址 → 下载。"""
        if kind not in EXPORT_KINDS:
            raise FinanceError(f"未知导出类型 {kind}；可用：{sorted(EXPORT_KINDS)}")
        spec = EXPORT_KINDS[kind]
        log = {"shop": self.key, "kind": kind, "steps": []}
        r1 = self.call(spec["create"],
                       body=create_body if create_body is not None else {})
        if isinstance(r1, tuple):        # export_statement_file 返回 (resp, body)
            r1, create_body = r1
        log["steps"].append({"step": "create", "iface": spec["create"], "resp": r1})
        task_url = self._extract_download_url(r1)
        if task_url:
            log["steps"].append({"step": "direct_url_from_create"})
            if save:
                log["download"] = self.download(task_url, Path(out_dir) / f"{self.key}_{kind}")
            return log
        r2, url = self.poll_ready(spec["poll"], tries=poll_tries)
        log["steps"].append({"step": "poll", "iface": spec["poll"], "resp": r2})
        if not url:
            try:
                r3 = self.call(spec["fetch"])
                log["steps"].append({"step": "fetch", "iface": spec["fetch"], "resp": r3})
                url = self._extract_download_url(r3)
            except Exception as e:
                log["steps"].append({"step": "fetch", "error": str(e)[:200]})
        if url:
            log["download_url"] = url[:160]
            if save:
                log["download"] = self.download(url, Path(out_dir) / f"{self.key}_{kind}")
        else:
            log["note"] = "没拿到 download_url —— 可能是任务还在生成，或该店这个接口不需要"
        try:
            from tk01_log import log_run
            log_run("fin_export", target=f"{self.key}:{kind}",
                    ok=bool(url), params={"kind": kind},
                    result={"url": bool(url), "bytes": (log.get("download") or {}).get("bytes")},
                    note="tk01_finance.batch_export")
        except Exception:
            pass
        return log


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok Shop 财务 API 客户端")
    ap.add_argument("--shop", default=None, help="店铺 key（shops.json）；默认 active")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--page-hint", default=None, help="指定借哪个页面（URL 子串）")
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("settings", "balance", "amount-get", "settlement-account", "withdraw-rules",
                 "auto-withdraw", "compliance", "stat-info", "file-list", "oec-file-list",
                 "invoice", "invoice-export-task", "tax-info", "shop-entity",
                 "pl-history", "payout-config", "payout-block-check"):
        sub.add_parser(name)
    p = sub.add_parser("call"); p.add_argument("iface"); p.add_argument("--body", default=None)
    p.add_argument("--params", default=None); p.add_argument("--version", type=int, default=None)
    p = sub.add_parser("order-list"); p.add_argument("--status", type=int, default=2)
    p.add_argument("--size", type=int, default=20); p.add_argument("--page-type", type=int, default=6)
    p = sub.add_parser("balance-detail"); p.add_argument("--type", type=int, default=1)
    p.add_argument("--limit", type=int, default=10)
    p = sub.add_parser("statements"); p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--page-num", type=int, default=1)
    p = sub.add_parser("onhold"); p.add_argument("--page-size", type=int, default=20)
    p = sub.add_parser("settled"); p.add_argument("--page-size", type=int, default=20)
    p = sub.add_parser("amount-summary"); p.add_argument("--types", default="1,2,3")
    p = sub.add_parser("download"); p.add_argument("url"); p.add_argument("-o", "--out", required=True)
    p = sub.add_parser("batch-export"); p.add_argument("--kind", default="statement")
    p.add_argument("--out-dir", default="notes/fin_dl"); p.add_argument("--body", default=None)
    a = ap.parse_args()

    C = FinanceClient(a.shop, port=a.port, page_hint=a.page_hint, verbose=a.verbose)
    try:
        if a.cmd == "call":
            r = C.call(a.iface, body=json.loads(a.body) if a.body else None,
                       params=json.loads(a.params) if a.params else None, version=a.version)
        elif a.cmd == "order-list":
            r = C.order_list(settlement_status=a.status, size=a.size, page_type=a.page_type)
        elif a.cmd == "balance-detail":
            r = C.balance_detail(transaction_type=a.type, limit=a.limit)
        elif a.cmd == "statements":
            r = C.statements(page_size=a.page_size, page_num=a.page_num)
        elif a.cmd == "onhold":
            r = C.onhold_orders(page_size=a.page_size)
        elif a.cmd == "settled":
            r = C.settled_orders(page_size=a.page_size)
        elif a.cmd == "amount-summary":
            r = C.amount_summary(a.types)
        elif a.cmd == "download":
            r = C.download(a.url, a.out)
        elif a.cmd == "batch-export":
            r = C.batch_export(a.kind, out_dir=a.out_dir,
                               create_body=json.loads(a.body) if a.body else None)
        elif a.cmd == "invoice":
            r = C.invoice_search()
        elif a.cmd == "file-list":
            r = C.file_list()
        elif a.cmd == "settings":
            r = C.settings()
        elif a.cmd == "balance":
            r = C.balance()
        else:
            mapping = {
                "amount-get": "amount_get", "settlement-account": "settlement_account",
                "withdraw-rules": "withdraw_rules", "auto-withdraw": "auto_withdraw_info",
                "compliance": "compliance_security", "stat-info": "stat_info",
                "oec-file-list": "oec_file_list", "invoice-export-task": "invoice_export_task",
                "tax-info": "tax_info", "shop-entity": "shop_entity",
                "pl-history": "oec_pl_history", "payout-config": "payout_config",
                "payout-block-check": "payout_block_check",
            }
            r = C.call(mapping[a.cmd])
        print(json.dumps(r, ensure_ascii=False, indent=2)[:6000])
    except FinanceError as e:
        print(f"  ✗ {e}")
        sys.exit(2)
    finally:
        C.close()


if __name__ == "__main__":
    main()
