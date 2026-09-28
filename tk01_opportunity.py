#!/usr/bin/env python3
"""TikTok Shop 商品机会（Product Opportunity）API 客户端 —— SHOP_XBORDER 跨境店。

端点全貌来自页面自带的 API 封装 JS：
  /obj/she-op-static/i18n/ecom/next/product_opportunity_home/js/
      oec_product_seller_product_opportunity_api.g8gmfrvq.js
解析脚本把它拆成 47 个 (op, version, method, path)，存于 notes/opp_api_table.json：
  uriPrefix + /api/v{version||1}/product/oc/seller_product_opportunity/<path>
version 由调用方给，缺省 1 —— submit/record/list 实际用的是 v2。

## ⚠️ 传输层铁律：必须在页面上下文里发请求

直连（requests / urllib）打这些端点会返回 **{"code": 0} 且没有 message** ——
这是"请求没被服务端当真"的假成功，不是成功。实测证据：20 次直连 POST /relate
全部返回 code=0/无 message，但只有 1 次真的写进去了（缺签名的那次被静默丢弃）。

所以本模块**不使用** requests，全部经 Chrome 页面 fetch：
  seller.tiktokshopglobalselling.com 的页面上，webmssdk 会给请求注入
  X-Bogus / X-Gnarly / msToken / X-Tts-Oec-Bsid 等签名参数。

## ⚠️ 为什么不用 awaitPromise

页面在后台时 `Runtime.evaluate(awaitPromise=true)` 会一直挂着（fetch 可能
永不 resolve，连 AbortController 的 setTimeout 都不一定跑）。
做法：先 `fetch()` 出去（不等它），把结果写进 `window.__opr`，再轮询读回来。

## 参数包装有两套（踩过坑）

  flat    : {"lead_id": "…"}                     ← seller/lead/detail、relate
  params  : {"params": {"page_number": 1, …}}     ← submit/record/list、
                                                    product/performance/Card

用错包装：flat 套了 params → `12071012 soc invalid param`。
本文件里每个方法都标注了自己的包装方式。

## 报名字段（用 Go 反序列化错误挖出来的，已实测执行成功）

    product_serv.RelateProductToSPORequest.relate_product_items []product_serv.RelateProductItem
    RelateProductItem.tts_product_id  → int64（字符串会报 value out of range）

    POST /relate  body = {"lead_id": "<id>", "relate_product_items": [{"tts_product_id": 1736…}]}

一次成功的 /relate 会在「我的提报 → 已被拒/已批准」里留下一行记录，
所以它是**真写操作**，默认 apply=False 不发。

## 提报结果筛选语义（实测）

    approve_status = 1  → 已批准（审核通过）
    approve_status = 2  → 已被拒（不传 approve_status 时默认也是这档）
    approve_status = 3  → 空
    seller_operation_list = []      → 不过滤（总数 = 成功提报商品数）
    seller_operation_list = [1,2]   → 页面 UI 默认视图
    seller_operation_list = [1]     → 只留 op=1
    seller_operation = 1 / 2 / 4 都是真实取值

用法:
  python3 tk01_opportunity.py leads [--type 3] [--page 1] [--size 20]
  python3 tk01_opportunity.py detail <lead_id>
  python3 tk01_opportunity.py submits [--status 1|2] [--pages 3]
  python3 tk01_opportunity.py stats               # 提报成绩卡
  python3 tk01_opportunity.py why                 # 失败原因分布（采样）
  python3 tk01_opportunity.py relate <lead_id> <product_id> [--yes]
  python3 tk01_opportunity.py endpoints
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse as up
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ── 店铺上下文：从 tk01_config 读（多店铺 / 多区域）──
# 原来是写死的；现在改 `shops.json` 或用 `python3 tk01_config.py use <name>` 切换。
# 下面这几个名字保留成模块级常量，是为了兼容既有代码。
try:
    from tk01_config import (DEFAULT_PORT, API_HOST as HOST, SELLER, AID,
                             API_APP_NAME as APP, REGION, SELLER_ORIGIN as PAGE_ORIGIN,
                             TIMEZONE_NAME)
except Exception:                                  # config 缺失时的兜底
    DEFAULT_PORT = CDP_PORT
    HOST = "https://api16-normal-sg.tiktokshopglobalselling.com"
    SELLER = "7494XXXXXXXXXX00"
    AID = "6556"
    APP = "i18n_ecom_shop"
    REGION = "VN"
    TIMEZONE_NAME = "Asia/Bangkok"

PRE = "/api/v1/product/oc/seller_product_opportunity"
ENDPOINTS_FILE = HERE / "notes" / "opp_api_table.json"

# opportunity_type（从抓包与代码常量归纳）
# 内部名称来自第三方参考实现的源码常量（见文档 §26.1）。
# 注意：请求 opportunity_type=2 时，返回行里的 opportunity_type 常是 202
# —— 服务端做了映射，别以为参数没生效。
OPP_TYPE = {
    1: "类目机会",
    2: "关键词机会 (keyword，服务端常回 202 trending_keyword)",
    3: "高潜力商品 (high_potential_products)",
    4: "低竞争类目 (leaf category)",
    201: "most_wanted（最想要）",
    202: "trending_keyword（趋势关键词）",
}
# 提报表的第二层 tab
SUBMIT_TAB = {
    "category": "类目",
    "new_product": "新发商品",
    "relate_existing": "提报已有商品",
    "submitted": "已提报的商品",
}


class OppError(RuntimeError):
    def __init__(self, code, message, path="", body=None):
        self.code, self.message, self.path, self.body = code, message, path, body
        super().__init__(f"[{code}] {message}  ({path})")


# ───────────────────────── 传输层 ─────────────────────────

class PageChannel:
    """在卖家后台页面里发请求 —— 唯一能拿到真实结果的方式。

    直连 requests 会得到假 code=0；本类彻底不用 requests。
    """

    _JS_SEND = """(() => {
      window.%(key)s = null;
      var opt = {method: %(method)s, credentials: "include", headers: %(headers)s};
      %(bodyline)s
      fetch(%(url)s, opt)
        .then(function (r) { return r.text().then(function (t) {
          window.%(key)s = r.status + "|" + t; }); })
        .catch(function (e) { window.%(key)s = "EXC|" + String(e); });
      return "sent";
    })()"""

    def __init__(self, port: int = DEFAULT_PORT, *, gap: float = 1.2, verbose: bool = False,
                 host: str | None = None, app_name: str | None = None,
                 seller_id: str | None = None, page_match: str = "product/opportunity",
                 base_query: dict | None = None):
        """host/app_name/seller_id 可覆盖 —— 联盟中心是另一个域 + 另一个 app_name。

          seller 侧   : api16-normal-sg.tiktokshopglobalselling.com / i18n_ecom_shop
          联盟中心侧  : affiliate.tiktokshopglobalselling.com    / i18n_ecom_alliance
        """
        self.port = port
        self.gap = gap
        self.verbose = verbose
        self.host = host or HOST
        self.app_name = app_name or APP
        self.seller_id = seller_id or SELLER
        self.page_match = page_match
        # ⚠️ query 基座必须可配。
        # seller 侧要 locale/language/oec_seller_id/seller_id；
        # 联盟侧只认 user_language/aid/app_name/device_id —— 多塞参数会被
        # 服务端判 98001004 Invalid parameters（实测）。
        self.base_query = base_query
        self._pw = None
        self._browser = None
        self._ctx = None
        self._page = None
        self._cdp = None
        self._last = 0.0
        self._n = 0
        self._since_captcha = 0
        self._sign_params: dict = {}

    # ---- 生命周期 ----
    def _ensure(self):
        if self._page is not None:
            try:
                self._page.evaluate("1+1")
                return
            except Exception:
                self._page = None
        from playwright.sync_api import sync_playwright

        if self._pw is None:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}")
        self._ctx = self._browser.contexts[0]

        # 优先用已经在商品机会页的标签；没有就找一个 seller 页；再没有才开新页
        # ⚠️ 必须按【域名】匹配，不能只匹配路径。
        # 例："/affiliate/" 会同时命中
        #   affiliate.tiktokshopglobalselling.com/affiliate/creator   ← 要的
        #   seller.tiktokshopglobalselling.com/affiliate/landing      ← 不要
        # 选错了 iframe 的 origin 就落在另一个域，跨域 fetch 报 "Failed to fetch"。
        want_host = self.host.replace("https://", "").replace("http://", "").split("/")[0]
        cands = [p for p in self._ctx.pages
                 if want_host in p.url and self.page_match in p.url]
        cands += [p for p in self._ctx.pages if want_host in p.url]
        cands += [p for p in self._ctx.pages if self.page_match in p.url]
        cands += [p for p in self._ctx.pages if "tiktokshopglobalselling.com" in p.url]
        for p in cands:
            try:
                p.evaluate("1+1")
                self._page = p
                break
            except Exception:
                continue
        if self._page is None:
            # ⚠️ 不自动开新标签页 —— 那会抢焦点并在桌面上堆页面。
            # 找不到可用页面就报错，让调用方决定（例如显式 use_quiet_window()）。
            raise OppError(None, "找不到可用的 seller/affiliate 页面。"
                                 "请先打开一个对应域名的标签页，"
                                 "或显式调用 use_quiet_window()。")
        try:
            self._cdp = self._ctx.new_cdp_session(self._page)
            self._cdp.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
            # ⚠️ 关键：必须把标签页拉到前台。
            # 实测在后台标签页里 fetch 永不 resolve（Chrome 挂起后台页的网络），
            # 表现成"服务端超时/风控挂起"，其实跟服务端无关。
            # 而且后台页里 document.visibilityState==='hidden' 时，
            # TikTok 的验证码 SDK 会把挑战 iframe 保持 display:none，
            # 于是挑战永远渲染不出来、请求永远等不到响应。
            # bringToFront 之后同样的 /relate 2 秒内就返回。
            # ⚠️ 只有"我们自己开的页面"才允许 bringToFront。
            # 对操作者正在用的标签页绝不能这么做（会抢他前台）。
            if getattr(self._page, "_dsh_quiet", False) or getattr(self, "_own_page", False):
                self._cdp.send("Page.bringToFront")
                time.sleep(0.3)
        except Exception:
            self._cdp = None

    def close(self):
        for closer in (lambda: self._browser and self._browser.close(),
                       lambda: self._pw and self._pw.stop()):
            try:
                closer()
            except Exception:
                pass
        self._pw = self._browser = self._ctx = self._page = self._cdp = None

    # ---- 限速 ----
    def _throttle(self):
        dt = time.time() - self._last
        if dt < self.gap:
            time.sleep(self.gap - dt)
        self._last = time.time()


    # ---- 签名参数采集 ----
    # 参考工具（ThirdParty2）用 declarativeNetRequest 持续采集真实请求 URL 里的
    # msToken / X-Bogus / X-Gnarly / X-Tts-Oec-Bsid / fp，再带着它们自己发请求。
    # 只带 X-Bogus 的请求看起来"不像"真实调用 —— 这是验证码敏感度的一个来源。
    # 这里用同样思路：抓一次页面自身签名过的请求，把参数缓存下来复用。
    _JS_HARVEST = """(() => {
      if (window.__hv_installed) { window.__hv = []; return 'reset'; }
      window.__hv_installed = true;
      window.__hv = [];
      const KEYS = ['msToken','X-Bogus','X-Gnarly','X-Tts-Oec-Bsid','fp',
                    'device_platform','cookie_enabled','screen_width','screen_height',
                    'browser_language','browser_platform','browser_name','browser_version',
                    'browser_online','timezone_name','channel','aid','app_name'];
      const grab = u => { try {
          const q = new URL(u, location.origin).searchParams; const o = {};
          for (const k of KEYS) { const v = q.get(k); if (v) o[k] = v; }
          if (Object.keys(o).length >= 3) window.__hv.push(o);
        } catch(e){} };
      const _o = XMLHttpRequest.prototype.open, _s = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.open = function(m,u){ grab(u); return _o.apply(this,arguments); };
      const _f = window.fetch;
      window.fetch = function(i, init){
        try { grab((typeof i==='string') ? i : (i && i.url) || ''); } catch(e){}
        return _f.apply(this, arguments);
      };
      return 'installed';
    })()"""

    SIGN_KEYS = ("msToken", "X-Gnarly", "X-Tts-Oec-Bsid", "fp", "device_platform",
                 "cookie_enabled", "screen_width", "screen_height", "browser_language",
                 "browser_platform", "browser_name", "browser_version", "browser_online",
                 "timezone_name", "channel")

    def harvest_signature_params(self, *, quiet: bool = False) -> dict:
        """从 `performance` 资源计时里读【页面实际发出的完整 URL】，采集签名参数。

        为什么不用 hook：webmssdk 的 fetch/XHR 包装在**更内层**，
        我在外层 hook 只能看到加签名【之前】的 URL（实测抓到 0 个参数）。
        `performance.getEntriesByType('resource')` 记录的是真正发出去的 URL，
        包含 SDK 注入的全部签名参数 —— 这才是可靠来源。

        实测（真实页面请求）：
            msToken=REDACTED… （跨请求稳定）
            X-Tts-Oec-Bsid=REDACTED…（跨请求稳定）
            X-Bogus        = 按 URL 变  → 我们用 frontierSign 现算
            X-Gnarly       = 按请求变  → 不缓存
            fp             = 这些请求里根本没有，说明不是每次都需要
        """
        self._ensure()
        # 借页面自己的 fetch 发一个读请求，SDK 会给它签名
        try:
            self._page.evaluate("""(() => {
              fetch('/api/v1/product/oc/seller_product_opportunity/contract/check?aid=6556',
                    {method:'POST', credentials:'include',
                     headers:{'content-type':'application/json'}, body:'{}'})
                .catch(()=>{});
              return 'sent'; })()""")
        except Exception:
            pass
        js = """JSON.stringify((()=>{
          const out=[];
          const es=[...performance.getEntriesByType('resource')]
            .filter(e=>/\\/api\\//.test(e.name)).slice(-25);
          for (const e of es) {
            try { const q=new URL(e.name).searchParams;
              const o={}; let n=0;
              for (const k of ['msToken','X-Gnarly','X-Tts-Oec-Bsid','fp','aid','app_name',
                               'device_platform','screen_width','screen_height',
                               'browser_language','browser_platform','browser_name',
                               'browser_version','browser_online','timezone_name','channel',
                               'cookie_enabled']) {
                const v=q.get(k); if (v) { o[k]=v; n++; }
              }
              if (n>=3) out.push(o);
            } catch(err){}
          }
          return out;})())"""
        STABLE = ("msToken", "X-Tts-Oec-Bsid", "device_platform", "screen_width",
                  "screen_height", "browser_language", "browser_platform", "browser_name",
                  "browser_version", "browser_online", "timezone_name", "channel",
                  "cookie_enabled")
        for _ in range(8):
            time.sleep(0.35)
            try:
                arr = json.loads(self._page.evaluate(js) or "[]")
            except Exception:
                arr = []
            if arr:
                # 取出现次数最多的那个（稳定参数投票）
                counts: dict[str, dict] = {}
                for o in arr:
                    key = o.get("msToken", "")
                    counts.setdefault(key, {}).update(o)
                best = max(counts.values(), key=len) if counts else {}
                got = {k: v for k, v in best.items() if k in STABLE}
                if got:
                    self._sign_params.update(got)
                    self._sign_params["_samples"] = len(arr)
                    if not quiet:
                        print(f"    [sign] 从 {len(arr)} 个真实请求采到 "
                              f"{sorted(got)}", flush=True)
                    return self._sign_params
        if not quiet:
            print("    [sign] 未采集到签名参数", flush=True)
        return self._sign_params



    # ─────────── Worker 传输：不抢前台、不被 SDK 扣住 ───────────
    #
    # 借鉴同行的 `offscreen` 思路（见 manifest 的 "offscreen" 权限 +
    # tabs/offscreen.html）：**它们根本不在标签页里发请求**，
    # Offscreen Document 是扩展的隐藏文档，没有标签页、没有可见性问题。
    #
    # 我没有扩展上下文，但**页面里的 Blob Worker 等价**：
    #   - 同源（`Origin: https://affiliate.tiktokshopglobalselling.com`，不是 iframe 的 null）
    #   - **没有 webmssdk** → 不存在"promise 被 SDK 扣住等验证码"→ 不会挂起
    #   - 不需要页面在前台 → **不抢操作者的焦点**
    #
    # 签名仍在页面里做（Worker 里没有 byted_acrawler），
    # 把签好的 URL 传给 Worker 发出去。

    _JS_WORKER = """(async () => {
      const req = %(req)s;
      // ① 页面里签名
      let url = req.url, sigKeys = null;
      try {
        const sig = window.byted_acrawler.frontierSign(
            {url: req.url, method: req.method, body: req.body});
        if (sig) { const u = new URL(req.url);
                   for (const k in sig) u.searchParams.set(k, sig[k]);
                   url = u.toString(); sigKeys = Object.keys(sig); }
      } catch (e) {}
      // ② Blob Worker 里发请求（同源、无 SDK、不受可见性门控）
      const code = `
        self.onmessage = async (ev) => {
          const { url, method, headers, body } = ev.data;
          try {
            const opt = { method, credentials: 'include', headers };
            if (body !== null && body !== undefined) opt.body = body;
            const r = await fetch(url, opt);
            const hdr = r.headers.get('bdturing-verify');
            self.postMessage({ ok: true, status: r.status, hdr: hdr,
                               body: await r.text() });
          } catch (err) {
            self.postMessage({ ok: false, err: String(err).slice(0, 200) });
          }
        };
      `;
      const w = new Worker(URL.createObjectURL(
          new Blob([code], {type: 'application/javascript'})));
      const pr = new Promise(res => { w.onmessage = ev => res(ev.data); });
      w.postMessage({url: url, method: req.method, headers: req.headers,
                     body: req.body});
      const to = new Promise(res => setTimeout(
          () => res({ok: false, err: 'TIMEOUT_' + req.timeout + 'ms'}), req.timeout));
      const res = await Promise.race([pr, to]);
      try { w.terminate(); } catch (e) {}
      res.sig = sigKeys;
      res.signed = (url !== req.url);
      return JSON.stringify(res);
    })()"""

    def worker_call(self, path: str, body=None, *, method: str = "POST",
                    params: dict | None = None, timeout_ms: int = 20000) -> dict:
        """经页面 Blob Worker 发请求 —— **不抢前台**，且不会被 SDK 扣住。

        对比三种传输：
          `raw_call`    iframe 原生 fetch → 联盟域被判插件（Origin: null）
          `call`        页面 fetch        → 需要页面在前台（会抢焦点）
          `worker_call` Blob Worker       → 同源 + 无 SDK + 不需要前台  ★用这个
        """
        self._ensure()
        self._throttle()
        q = dict(self.base_query) if self.base_query is not None else {
            "user_language": "zh-CN", "locale": "zh-CN", "language": "zh-CN",
            "oec_seller_id": self.seller_id, "aid": AID, "app_name": self.app_name}
        if params:
            q.update({k: v for k, v in params.items() if v is not None})
        url = self.host + path + "?" + up.urlencode(q)
        js_body = (json.dumps(body, ensure_ascii=False)
                   if (method.upper() != "GET" and body is not None) else None)
        req = {"url": url, "method": method.upper(), "body": js_body,
               "timeout": timeout_ms,
               "headers": {"content-type": "application/json; charset=utf-8",
                           "x-tt-oec-region": REGION}}
        try:
            raw = self._page.evaluate(self._JS_WORKER % {"req": json.dumps(req, ensure_ascii=False)})
        except Exception as e:
            raise OppError(None, f"worker_call evaluate 失败: {str(e)[:120]}", path, body)
        try:
            out = json.loads(raw)
        except Exception:
            raise OppError(None, f"worker_call 返回不可解析: {str(raw)[:120]}", path, body)
        if not out.get("ok"):
            raise OppError(None, f"worker fetch 失败: {str(out.get('err'))[:140]}", path, body)
        res = {"_http": out.get("status")}
        if out.get("hdr"):
            try:
                res["_captcha"] = json.loads(out["hdr"])
            except Exception:
                res["_captcha"] = {"raw": out["hdr"]}
        try:
            res.update(json.loads(out.get("body") or "{}"))
        except Exception:
            res["_raw"] = (out.get("body") or "")[:300]
        return res

    # ─────────── 静默模式：不抢操作者的前台 ───────────
    #
    # 约束（§27 实测）：
    #   标签页必须是**所在窗口的活动标签**，`document.visibilityState` 才是 'visible'，
    #   fetch 才会 resolve、验证码才会渲染、Input 拖拽才打得到元素。
    #
    # 但**窗口不需要被聚焦** —— visibilityState 只看"是不是本窗口的活动标签"，
    # 不看"窗口有没有焦点"。所以：
    #
    #   ✗ `Page.bringToFront`  → 会抢操作者的前台（绝对不能对着他的窗口做）
    #   ✓ **建一个独立窗口**，它自己的活动标签天然是 visible，且不抢焦点
    #
    # `Target.createTarget({newWindow:true, background:true})` 就是干这个的：
    # 新开一个窗口，但不激活它。

    QUIET_WINDOW_KEY = "__dsh_quiet_target"

    def _quiet_page_url(self) -> str:
        host = self.host
        if "affiliate" in host:
            return f"{host}/affiliate/creator?shop_region={REGION}&shop_id={self.seller_id}"
        return f"{host}/product/opportunity?shop_region={REGION}"

    def use_quiet_window(self) -> bool:
        """把工作标签页换到一个**不抢焦点**的独立窗口里。

        ⚠️ 这个函数曾经造成过事故：调用一次就建一个窗口，而 Playwright 的
        `ctx.pages` 又同步不到新窗口，于是**桌面上堆了 10 个重复标签**。
        现在加了两道锁：
          1. 幂等 —— 已有自有窗口就直接复用，绝不再建
          2. 全局上限 1 个
        用完**必须**调 `release_quiet_window()` 关掉。
        """
        try:
            # 锁 1/2：已有自有窗口 → 复用
            for pg in self._ctx.pages if self._ctx else []:
                if getattr(pg, "_dsh_quiet", False):
                    self._page = pg
                    return True
            if getattr(self, "_quiet_made", False):
                return False          # 锁 2：本进程只允许建一个
            self._ensure()
            # 复用已有的静默窗口
            for pg in self._ctx.pages:
                if getattr(pg, "_dsh_quiet", False):
                    self._page = pg
                    return True
            if self._cdp is None:
                return False
            res = self._cdp.send("Target.createTarget", {
                "url": self._quiet_page_url(),
                "newWindow": True,
                "background": True,          # ★ 不激活新窗口
            })
            tid = res.get("targetId")
            if not tid:
                return False
            self._quiet_made = True
            time.sleep(3)
            for pg in self._ctx.pages:
                try:
                    if pg.url.startswith(self.host) and not getattr(pg, "_dsh_quiet", False):
                        # 认领刚开的那个（最新创建、且不在我们已知集合里）
                        if not getattr(self, "_known_urls", None) or pg.url not in self._known_urls:
                            pass
                except Exception:
                    continue
            # 用 CDP 确认新 target 对应的 page
            try:
                listing = json.loads(__import__("urllib.request").request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/list", timeout=8).read())
                wt = next((t for t in listing if t.get("id") == tid), None)
                if wt and wt.get("webSocketDebuggerUrl"):
                    for pg in self._ctx.pages:
                        if pg.url == wt.get("url") or pg.url.startswith(self.host):
                            self._page = pg
                            setattr(pg, "_dsh_quiet", True)
                            self._cdp = self._ctx.new_cdp_session(pg)
                            try:
                                self._cdp.send("Emulation.setFocusEmulationEnabled",
                                               {"enabled": True})
                            except Exception:
                                pass
                            return True
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"    [quiet] 建独立窗口失败: {str(e)[:80]}", flush=True)
            return False

    def release_quiet_window(self) -> bool:
        """关掉静默窗口（用完清理，别在操作者桌面留东西）。"""
        try:
            for pg in list(self._ctx.pages):
                if getattr(pg, "_dsh_quiet", False):
                    pg.close()
                    return True
        except Exception:
            pass
        return False

    # ---- 验证码 ----
    _CAPTCHA_JS = """JSON.stringify((()=>{
      const w = document.querySelector('.captcha_verify_container');
      const pc = document.querySelector('img.captcha_verify_img_slide');
      if (!w && !pc) return {present:false};
      const scopes = [w, document.getElementById('captcha_container'), document].filter(Boolean);
      let bg = null;
      for (const s of scopes) {
        const c = [...s.querySelectorAll('img')].filter(x => x !== pc && x.naturalWidth >= 200);
        if (c.length) { bg = c[0]; break; }
      }
      return {present:true, hasBg:!!bg, hasPc:!!pc};
    })())"""

    def captcha_present(self) -> dict:
        """廉价探测（~5ms，复用已有 Playwright 页面，不开新 websocket）。"""
        try:
            return json.loads(self._page.evaluate(self._CAPTCHA_JS) or "{}")
        except Exception:
            return {}

    def handle_captcha(self, *, force: bool = True, quiet: bool = False) -> bool:
        """页面挂着验证码就滑掉，否则后续 fetch 会永远不 resolve。

        实测：连续写请求若干次后，服务端要求验证码，SDK 在页面里渲染挑战，
        而**未解决的挑战会把之后所有请求一起卡死**（表现为 20s 无响应）。
        所以在高频写循环里必须周期性清它 —— 这是"提报速度"的关键，
        不是可选项。

        返回 True = 当前无挑战 或 已解决。
        """
        import urllib.request as _ur
        from hub_headless import CDPPage
        from tt_captcha import CaptchaGuard
        try:
            tabs = json.loads(_ur.urlopen(
                f"http://127.0.0.1:{self.port}/json/list", timeout=8).read())
        except Exception:
            return True
        ws = next((t.get("webSocketDebuggerUrl") for t in tabs
                   if t.get("type") == "page" and t.get("url") == self._page.url), None)
        if not ws:
            return True
        pg = CDPPage(ws, timeout=25)
        try:
            pg.enable("Runtime", "Page")
            # ⚠️ 拖拽要求页面可见（§27）。但**绝不能对操作者的标签页 bringToFront**。
            # 规矩：
            #   - 这是我们自己的静默窗口 / 自己开的页 → 允许置前
            #   - 是操作者的标签页 → 只做 setFocusEmulationEnabled（不抢焦点），
            #     并且**提示调用方先在静默窗口里跑**
            mine = getattr(self._page, "_dsh_quiet", False) or getattr(self, "_own_page", False)
            if mine:
                try:
                    pg.send("Page.bringToFront")
                    time.sleep(0.4)
                except Exception:
                    pass
            else:
                try:
                    pg.send("Emulation.setFocusEmulationEnabled", {"enabled": True})
                except Exception:
                    pass
                if not quiet:
                    print("    [captcha] 注意：当前用的是操作者的标签页，"
                          "拖拽可能不生效 —— 建议先 use_quiet_window()", flush=True)
            st = CaptchaGuard.detect(pg)
            if not (st.get("btn") or st.get("text_hit")):
                return True
            g = CaptchaGuard.geometry(pg)
            if not g.get("ok"):
                # 半渲染的僵死挑战：直接清掉，比留着卡死强
                if not quiet:
                    print(f"    [captcha] 僵死挑战(hasBg={g.get('hasBg')}) → 清理", flush=True)
                CaptchaGuard.close(pg)
                return True
            if not quiet:
                print(f"    [captcha] 检测到滑块 bg={g.get('bgNat')} → 滑动", flush=True)
            ok = CaptchaGuard(self.port).solve(pg, retries=4, force=force)
            if not quiet:
                print(f"    [captcha] 结果 {ok}", flush=True)
            return ok
        except Exception as e:
            if not quiet:
                print(f"    [captcha] 异常 {str(e)[:70]}", flush=True)
            return False
        finally:
            try:
                pg.close()
            except Exception:
                pass


    _JS_RAW = """(async () => {
      const req = %(req)s;
      const ifr = document.createElement('iframe');
      ifr.style.cssText = 'width:0;height:0;border:0;position:absolute;left:-9999px';
      document.body.appendChild(ifr);
      await new Promise(r => setTimeout(r, 60));
      let out;
      try {
        const w = ifr.contentWindow;          // about:blank 同源 iframe：
                                              // 它的 fetch 是【原生未包装】的，
                                              // webmssdk 只 patch 主文档的 fetch/XHR。
                                              // 所以请求不会被 SDK 扣住等验证码。
        let url = req.url;
        try {                                  // 自己签名，不依赖 SDK 注入
          const a = window.byted_acrawler;
          if (a && a.frontierSign) {
            const sig = a.frontierSign({url: url, method: req.method, body: req.body});
            if (sig) { const u = new URL(url); for (const k in sig) u.searchParams.set(k, sig[k]); url = u.toString(); }
          }
        } catch (e) {}
        const ctrl = new AbortController();
        const to = setTimeout(() => ctrl.abort(), req.timeout);
        const opt = {method: req.method, credentials: 'include', headers: req.headers,
                     signal: ctrl.signal};
        if (req.body) opt.body = req.body;
        const r = await w.fetch(url, opt);
        clearTimeout(to);
        const hdr = r.headers.get('bdturing-verify');
        let cap = null;
        if (hdr) { try { cap = JSON.parse(hdr); } catch (e) { cap = {raw: hdr}; } }
        out = {status: r.status, captcha: cap, body: await r.text(), signedUrl: url};
      } catch (e) { out = {error: String(e).slice(0, 200)}; }
      ifr.remove();
      return JSON.stringify(out);
    })()"""

    def raw_call(self, path: str, body=None, *, method: str = "POST",
                 params: dict | None = None, timeout_ms: int = 15000) -> dict:
        """经【未包装的原生 fetch】发送，并自行签名。

        为什么要这样：

        1. **不挂起。** 主文档的 `window.fetch` 被 webmssdk 包装过，当服务端要求
           验证码时 SDK 会把 promise 扣住等验证码 —— 表现就是"20s 无响应"。
           `about:blank`（同源）iframe 的 `contentWindow.fetch` 是原生的，
           请求立刻返回（实测 1.2s vs 20s）。
        2. **能读到 `bdturing-verify` 响应头。** 服务端要求人机校验时把挑战参数
           放在这个头里（`detail` / `fp` / `type` / `subtype` / `region`）。
           走页面 fetch 时头被 SDK 吃掉，什么也看不到。
        3. **签名自己算。** `byted_acrawler.frontierSign({url,method,body})`
           返回 `{"X-Bogus": "..."}`（页面里装着签名引擎，直接调它）。
        """
        self._ensure()
        self._throttle()
        q = dict(self.base_query) if self.base_query is not None else {
            "user_language": "zh-CN", "locale": "zh-CN", "language": "zh-CN",
            "oec_seller_id": self.seller_id, "aid": AID, "app_name": self.app_name}
        if params:
            q.update({k: v for k, v in params.items() if v is not None})
        if not params or "no_sign" not in (params or {}):
            for k, v in self._sign_params.items():      # 复现真实调用的完整 query
                if k.startswith("_"):
                    continue
                q.setdefault(k, v)
        url = self.host + path + "?" + up.urlencode(q)
        js_body = None
        if method.upper() != "GET" and body is not None:
            js_body = json.dumps(body, ensure_ascii=False)
        req = {"url": url, "method": method.upper(), "body": js_body,
               "timeout": timeout_ms,
               "headers": {"content-type": "application/json", "x-tt-oec-region": REGION}}
        js = self._JS_RAW % {"req": json.dumps(req, ensure_ascii=False)}
        try:
            raw = self._page.evaluate(js)
        except Exception as e:
            raise OppError(None, f"raw_call evaluate 失败: {str(e)[:120]}", path, body)
        try:
            out = json.loads(raw)
        except Exception:
            raise OppError(None, f"raw_call 返回不可解析: {str(raw)[:120]}", path, body)
        if out.get("error"):
            raise OppError(None, f"raw_call fetch 异常: {out['error'][:140]}", path, body)
        cap = out.get("captcha")
        if cap:
            out["_captcha"] = cap
        try:
            out["json"] = json.loads(out.get("body") or "{}")
        except Exception:
            out["json"] = {"_raw": (out.get("body") or "")[:300]}
        return out

    # ---- 写请求：让 SDK 接管验证码，渲染出来就滑掉 ----
    def call_write(self, path: str, body=None, *, params: dict | None = None,
                   max_rounds: int = 3, wait: float = 40.0,
                   on_event=None) -> dict:
        """写请求专用通道。

        `/relate` 在当前账号风险等级下**每次都要人机校验**（实测：请求体完整、
        签名参数完整也一样）。不绕过 SDK 才能拿到它自动接管的验证码流程：

          1. 用**页面 fetch** 发请求 —— webmssdk 看到 code=10000/bdturing-verify
             会触发 autoRender 并把 promise 扣住
          2. 挑战渲染到 DOM（`img.captcha_verify_img_slide` + 背景图）
          3. 用 `tt_captcha` 滑掉它 —— ⚠️ 背景图必须从拼图块往上找共同容器，
             否则会抓到商品主图（1254×1254），缺口全算错
          4. 滑过后 SDK 自己调 `/captcha/verifyV2`，被扣住的请求随即 resolve

        失败模式与处理：
          - `hasPc:false`（拼图块图消失）→ 挑战已废，close 掉重发，别空转
          - 一直不渲染 → 倒计时结束后 close + 重发（有上限）
        """
        import urllib.request as _ur
        from hub_headless import CDPPage
        from tt_captcha import CaptchaGuard
        self._ensure()
        q = dict(self.base_query) if self.base_query is not None else {
            "user_language": "zh-CN", "locale": "zh-CN", "language": "zh-CN",
            "oec_seller_id": self.seller_id, "aid": AID, "app_name": self.app_name}
        if params:
            q.update({k: v for k, v in params.items() if v is not None})
        url = self.host + path + "?" + up.urlencode(q)
        js_body = json.dumps(body, ensure_ascii=False) if body is not None else "null"

        try:
            ws = next((t.get("webSocketDebuggerUrl") for t in json.loads(
                _ur.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=8).read())
                if t.get("type") == "page" and t.get("url") == self._page.url), None)
        except Exception:
            ws = None
        if not ws:
            raise OppError(None, "拿不到页面 websocket", path, body)
        pg = CDPPage(ws, timeout=25)
        try:
            pg.enable("Runtime", "Page")
            try:
                pg.send("Page.bringToFront")   # 同上：不置前拖拽无效
                time.sleep(0.4)
            except Exception:
                pass
            for rnd in range(1, max_rounds + 1):
                self._n += 1
                key = f"__opw{self._n % 1000}"
                js = """(() => {
                  window.%(key)s = null;
                  fetch(%(url)s, {method:"POST", credentials:"include",
                    headers:{"content-type":"application/json","x-tt-oec-region":"VN"},
                    body: %(body)s})
                    .then(r => r.text().then(t => { window.%(key)s = r.status + "|" + t; }))
                    .catch(e => { window.%(key)s = "EXC|" + String(e); });
                  return "sent";
                })()""" % {"key": key, "url": json.dumps(url), "body": json.dumps(js_body)}
                try:
                    self._page.evaluate(js)
                except Exception as e:
                    raise OppError(None, f"evaluate 失败: {str(e)[:100]}", path, body)
                if on_event:
                    on_event("sent", rnd)

                deadline = time.time() + wait
                solved = False
                while time.time() < deadline: CONTACT_REDACTED(0.6)
                    try:
                        raw = self._page.evaluate(f"window.{key}")
                    except Exception:
                        raw = None
                    if raw:
                        if raw.startswith("EXC|"):
                            raise OppError(None, f"fetch 异常: {raw[4:][:120]}", path, body)
                        st, _, text = raw.partition("|")
                        try:
                            return json.loads(text)
                        except Exception:
                            return {"_http": st, "_raw": text[:300]}
                    geo = CaptchaGuard.geometry(pg)
                    if geo.get("ok") and not solved:
                        if on_event:
                            on_event("captcha", rnd)
                        # ⚠️ auto_render=False：solve() 默认失败后会调 render()
                        # ——那会 close 掉当前挑战再重建，导致拼图块图消失
                        # （实测 hasPc:false 连环出现，空转到超时）。
                        # 挑战是服务端为本轮请求生成的，绝不能中途销毁。
                        ok = CaptchaGuard(self.port).solve(pg, retries=3, force=True,
                                                           auto_render=False)
                        solved = ok
                        if on_event:
                            on_event("solved" if ok else "solve_failed", rnd)
                    elif not geo.get("ok") and geo.get("hasBg") and not geo.get("hasPc"):
                        # 挑战废了（拼图块图没了）—— 清掉重发，别空转
                        CaptchaGuard.close(pg)
                        time.sleep(1.0)
                        break
                else:
                    CaptchaGuard.close(pg)
                if on_event:
                    on_event("retry", rnd)
                time.sleep(1.2)
            raise OppError(None, f"{max_rounds} 轮都没拿到响应", path, body)
        finally:
            try:
                pg.close()
            except Exception:
                pass

    # ---- 实际发送 ----
    def call(self, path: str, body=None, *, method: str = "POST",
             params: dict | None = None, timeout: float = 20.0,
             auto_captcha: bool = True) -> dict:
        self._ensure()
        self._throttle()

        # ⚠️ 写请求必须**发送前**查验证码。事后处理的话这一次已经白等 20s，
        # 实测吞吐掉到 22.7s/次（1068 个机会 = 6.7 小时）。
        # captcha_present() 只有 ~5ms（复用已有页面），所以每次都查得起。
        if auto_captcha and method.upper() != "GET":
            st = self.captcha_present()
            if st.get("present"):
                self.handle_captcha(quiet=True)

        q = dict(self.base_query) if self.base_query is not None else {
            "locale": "zh-CN", "language": "zh-CN",
            "oec_seller_id": self.seller_id, "seller_id": self.seller_id,
            "aid": AID, "app_name": self.app_name}
        if params:
            q.update({k: v for k, v in params.items() if v is not None})
        url = self.host + path + "?" + up.urlencode(q)

        headers = {"content-type": "application/json", "x-tt-oec-region": REGION}
        bodyline = ""
        if method.upper() != "GET" and body is not None:
            bodyline = f"opt.body = {json.dumps(json.dumps(body, ensure_ascii=False))};"

        self._n += 1
        key = f"__opr{self._n % 1000}"
        js = self._JS_SEND % {"key": key, "url": json.dumps(url),
                              "method": json.dumps(method.upper()),
                              "headers": json.dumps(headers), "bodyline": bodyline}
        try:
            self._page.evaluate(js)
        except Exception as e:
            raise OppError(None, f"页面 evaluate 失败: {str(e)[:120]}", path, body)

        deadline = time.time() + timeout
        while time.time() < deadline: CONTACT_REDACTED(0.4)
            try:
                raw = self._page.evaluate(f"window.{key}")
            except Exception:
                continue
            if not raw:
                continue
            if raw.startswith("EXC|"):
                raise OppError(None, f"页面 fetch 抛异常: {raw[4:][:160]}", path, body)
            status, _, text = raw.partition("|")
            try:
                return json.loads(text)
            except Exception:
                return {"_http": status, "_raw": text[:300],
                        "_hint": "非 JSON —— 检查路径/方法（GET 路由发 POST 会得到 404 HTML）"}
        if auto_captcha and method.upper() != "GET":
            self.handle_captcha(quiet=True)
        raise OppError(None, f"轮询 {timeout:.0f}s 未拿到响应（页面被节流或服务端挂起）", path, body)


# ───────────────────────── 业务层 ─────────────────────────

class OpportunityClient:
    """商品机会接口封装。所有请求经 PageChannel（页面上下文）。"""

    def __init__(self, port: int = DEFAULT_PORT, *, gap: float = 1.2, verbose: bool = False):
        self.ch = PageChannel(port, gap=gap, verbose=verbose)
        self.port = port
        self.gap = gap

    def close(self):
        self.ch.close()

    # ---- 内部 ----
    # 写端点集合 —— 这些走 call_write（页面 fetch + 前台 + 验证码处理），
    # 不用 raw_call。实测 raw_call 的 iframe 会让服务端每次都要求验证码，
    # 而页面 fetch 在同条件下一次都不要（见文档 §27）。
    WRITE_PATHS = ("/relate", "/reject", "/mark", "/recruit/mark",
                   "/invitation_group", "/auto_submit", "/contract/sign",
                   "/product/stock/update", "/batch_listing")

    def _post(self, path, body, *, check: bool = True) -> dict:
        if any(w in path for w in self.WRITE_PATHS):
            r = self.ch.call_write(path, body)
        else:
            r = self.ch.call(path, body, method="POST")
        if check and self._failed(r):
            raise OppError(r.get("code"), r.get("message") or r.get("_raw"), path, body)
        return r

    def _get(self, path, params=None, *, check: bool = True) -> dict:
        r = self.ch.call(path, None, method="GET", params=params)
        if check and self._failed(r):
            raise OppError(r.get("code"), r.get("message") or r.get("_raw"), path, params)
        return r

    @staticmethod
    def _failed(r: dict) -> bool:
        """直连缺签名会返回 code=0 却没 message —— 也当作失败，避免静默吞。"""
        if "_raw" in r or "_hint" in r:
            return True
        c = r.get("code")
        if c is None:
            return True
        if c != 0:
            return True
        # code=0 且没有 message → 请求没被当真
        return "message" not in r

    # ─────────── 一、查看商品机会 ───────────

    def list_leads(self, *, page: int = 1, size: int = 20, opportunity_type: int | None = None,
                   sort_field: int = 1, use_like: bool = False,
                   traffic_source: str = "seller_organic",
                   tab_code_filter: list[str] | None = None) -> dict:
        """商品机会列表（flat 包装）。返回原始 data（含 lead_list / total_product_count）。"""
        body: dict = {"page_number": page, "page_size": size,
                      "use_like": use_like, "sort_field": sort_field,
                      "traffic_source": traffic_source}
        if opportunity_type is not None:
            body["opportunity_type"] = opportunity_type
        if tab_code_filter:
            body["tab_code_filter"] = tab_code_filter
        r = self._post(f"{PRE}/seller/lead/list", body)
        return r.get("data") if isinstance(r.get("data"), dict) else {"lead_list": r.get("data") or []}

    def lead_detail(self, lead_id: str) -> dict:
        """机会详情（**flat** 包装）。返回 L1/L2/L3 类目 + lead_segment + 搜索量等。"""
        return self._post(f"{PRE}/seller/lead/detail", {"lead_id": str(lead_id)}).get("data") or {}

    def lead_show_field(self, lead_id: str) -> dict:
        return self._post(f"{PRE}/seller/lead/show_field", {"lead_id": str(lead_id)}).get("data") or {}

    def list_tags(self, *, lead_type: int = 3) -> dict:
        return self._post(f"{PRE}/seller/lead/tag/list", {"lead_type": lead_type}).get("data") or {}

    def shop_filter(self, *, opportunity_type: int = 3) -> dict:
        """筛选器字典（品牌 / 特殊筛选：匹配的商品、暂无匹配的商品 …）。"""
        r = self._post(f"{PRE}/shop_filter/get",
                       {"opportunity_type": [opportunity_type], "need_aggregated": True})
        return r.get("data") or {}

    # ─────────── 二、搜索机会商品 ───────────

    def search_tts_products(self, search_text: str, *, page: int = 1,
                            size: int = 20, extra: dict | None = None) -> dict:
        """搜索店铺内可用于提报的商品。

        实测：`search_text` + `page_number` 是必填（缺了服务端绑定错误会点名），
        但 15+ 种参数组合都返回 data=null —— 可能还需要 tour_id 之类的上下文。
        别把它当"无结果"。
        """
        body = {"search_text": search_text, "page_number": page, "page_size": size}
        if extra:
            body.update(extra)
        return self._post(f"{PRE}/tts_product/search", body, check=False).get("data")

    def search_trending(self, **kw) -> dict:
        """趋势商品搜索。传 page_number/page_size 会报 12051002，参数未定，保留透传。"""
        return self._post(f"{PRE}/tts_product/trending/search", kw, check=False).get("data")

    def live_products_of_seller(self, lead_id: str, **extra) -> dict:
        """GetLiveProductsFromSeller → GET /seller/product/get。

        ⚠️ 该路由在 v1/v2/v3 下都 404（GET 和 POST 都试过）。JS 里确实定义了它，
        说明线上部署路径或版本与 JS 不一致，或它挂在不接受 GET 的网关上。
        先如实返回错误，不要假装可用。
        """
        p = {"lead_id": str(lead_id)}
        p.update(extra)
        return self._get(f"{PRE}/seller/product/get", p, check=False)

    # ─────────── 三、提报（写） ───────────

    def relate_template(self) -> str:
        """批量提报用的 Excel 模板下载地址。"""
        r = self._get(f"{PRE}/excel/relate/get")
        return ((r.get("data") or {}) or {}).get("download_url", "")

    def check_exist_same_product(self, lead_id: str, product_ids=None) -> dict:
        """同名/同款商品检查。路由 GET /exist/same/product/lead 实测 404，保留探针。"""
        p = {"lead_id": str(lead_id)}
        if product_ids:
            p["tts_product_ids"] = ",".join(str(x) for x in product_ids)
        return self._get(f"{PRE}/exist/same/product/lead", p, check=False)

    def relate(self, lead_id: str, product_ids: list[str] | list[int], *,
               apply: bool = False, opportunity_type: int | None = None,
               titles: dict | None = None) -> dict:
        """把一个或多个商品提报（报名）到某个机会 —— **真写操作**。

        请求体已实测确认（flat 包装，无 params）：
            {"lead_id": "7512XXXXXXXXXX66",
             "relate_product_items": [{"tts_product_id": "1736XXXXXXXXXX20"}]}

        ⚠️ `tts_product_id` 必须是**字符串**（不是数字）。
        Go 结构体里它就是 string，服务端内部再 strconv.ParseInt 成 int64：

            传数字 1      → 400 json: cannot unmarshal number into Go struct field
                            RelateProductItem.relate_product_items.tts_product_id of type string
            传字符串 1e19 → 12050002 current product id is invalid,
                            err:strconv.ParseInt: parsing "…": value out of range
                             ← 证明这是"字符串字段 + 内部转 int64"

        字段来源：Go 的反序列化错误直接吐出结构体名 —
            product_serv.RelateProductToSPORequest.relate_product_items []RelateProductItem

        写进去之后会在「我的提报」里留一行；被拒时 failure_reason 通常是
        「商品与机会提报要求不符」。apply=False 只做预检不发送。
        """
        body = self.build_relate_body(lead_id, product_ids,
                                      opportunity_type=opportunity_type, titles=titles)
        if not apply:
            return {"dry_run": True, "would_post": body}
        return self._post(f"{PRE}/relate", body)

    # 真实调用的固定字段（从页面 URL 与参考实现里取得的观测值）
    RELATE_SOURCE = 1
    RELATE_TRAFFIC_SOURCE = "seller_organic"
    RELATE_TOUR_ID = "7398XXXXXXXXXX01"

    def build_relate_body(self, lead_id, product_ids, *, opportunity_type=None,
                          titles: dict | None = None) -> dict:
        """构造与前端真实调用一致的 relate 请求体。

        前端（以及参考实现 ThirdParty2）实际发的是 6 个字段，早先只发 2 个：

            {"lead_id": …, "source": 1,
             "traffic_source": "seller_organic",     ← 观测自 oc_source=seller_organic
             "tour_id": "7398097457458277680901",    ← 观测自页面 URL
             "opportunity_type": null,
             "relate_product_items": [...]}

        并且 **opportunity_type === 2（关键词机会）时**，数组元素还要带
        `title` 与 `update_title: true` —— 平台会按关键词改商品标题：

            {"tts_product_id": …, "title": "<商品标题>", "update_title": true}

        字段少很可能就是"看起来不像真实调用"、进而被要求验证码的原因之一。
        """
        items = []
        for pid in product_ids:
            pid = str(pid)
            if opportunity_type == 2 and titles and titles.get(pid):
                items.append({"tts_product_id": pid, "title": titles[pid],
                              "update_title": True})
            else:
                items.append({"tts_product_id": pid})
        return {"lead_id": str(lead_id),
                "source": self.RELATE_SOURCE,
                "traffic_source": self.RELATE_TRAFFIC_SOURCE,
                "tour_id": self.RELATE_TOUR_ID,
                "opportunity_type": opportunity_type,
                "relate_product_items": items}

    def relate_many(self, lead_id: str, product_ids, *, apply: bool = False) -> dict:
        """一次把**多个**商品提报给同一个机会 —— 这才是批量提报的正解。

        `relate_product_items` 本来就是数组，一次调用可以塞多个商品：
            {"lead_id": …, "relate_product_items": [{tts_product_id},{tts_product_id},…]}

        实测旁证：07-31 21:00:47 那批「已批准」记录有 4 条同秒落库 ——
        就是一次多商品调用，不是四次单发。
        """
        return self.relate(lead_id, product_ids, apply=apply)

    def related_pairs(self, lead_id: str, *, size: int = 100) -> set[tuple[str, str]]:
        """某个机会下已经提报过的 (lead_id, product_id) —— 避免重复提报。

        实测 `lead_id` 传给服务端**不被采纳**（返回的仍是全局最新 100 条），
        所以这里额外做客户端过滤。代价是覆盖面只有最新 size×2 条记录，
        对"最近提交过什么"够用，对全量去重不够（全量 8 万条翻不完）。
        """
        out: set[tuple[str, str]] = set()
        for st in (self.APPROVE_OK, self.APPROVE_REJECT):
            try:
                d = self.submit_records(page=1, size=size, approve_status=st,
                                        seller_operation_list=[], lead_id=lead_id)
            except OppError:
                continue
            for x in d["record_list"]:
                if str(x.get("lead_id")) != str(lead_id):
                    continue                      # 服务端没过滤，客户端自己筛
                pid = str((x.get("tts_product_info") or {}).get("id") or "")
                if pid:
                    out.add((str(x.get("lead_id")), pid))
        return out

    def execute_plan(self, plan: list[dict], *, apply: bool = False,
                     min_hits: int | None = None, skip_existing: bool = True,
                     max_leads: int | None = None, on_progress=None) -> dict:
        """按预检计划执行提报 —— 按 lead 分组，一次调用提交该 lead 下的全部合格商品。

        plan 元素形如 {"lead_id":…, "product_id":…, "hits":N}（submission_plan 的输出）。
        - min_hits 以下的一律拒绝提交（这是"提报效率"的全部意义）
        - skip_existing=True 时先查该 lead 已提报过的商品并剔除
        - apply=False 只回放将要发出的请求体，不发
        """
        thr = self.MIN_HITS if min_hits is None else min_hits
        grouped: dict[str, list[dict]] = {}
        for x in plan:
            if int(x.get("hits", 0)) >= thr:
                grouped.setdefault(str(x["lead_id"]), []).append(x)
        if max_leads is not None:
            grouped = dict(list(grouped.items())[:max_leads])

        out = {"threshold": thr, "leads": len(grouped), "would_submit": 0,
               "submitted": 0, "skipped_existing": 0,
               "rejected_low_hits": sum(1 for x in plan if int(x.get("hits", 0)) < thr),
               "results": []}

        for lid, items in grouped.items():
            pids = [str(x["product_id"]) for x in items]
            if skip_existing:
                seen = self.related_pairs(lid)
                keep = [p for p in pids if (lid, p) not in seen]
                out["skipped_existing"] += len(pids) - len(keep)
                pids = keep
            if not pids:
                out["results"].append({"lead_id": lid, "submitted": [], "note": "已全部提报过"})
                continue
            out["would_submit"] += len(pids)
            if not apply:
                out["results"].append({"lead_id": lid, "dry_run": True,
                                       "would_post": {"lead_id": lid, "relate_product_items":
                                                      [{"tts_product_id": str(p)} for p in pids]}})
                continue
            try:
                r = self._post(f"{PRE}/relate",
                               {"lead_id": lid,
                                "relate_product_items": [{"tts_product_id": str(p)} for p in pids]})
                out["submitted"] += len(pids)
                out["results"].append({"lead_id": lid, "submitted": pids,
                                       "code": r.get("code"), "message": r.get("message")})
            except OppError as e:
                out["results"].append({"lead_id": lid, "submitted": [], "error": str(e)})
            if on_progress:
                on_progress(lid, len(pids))
        return out

    # ─────────── 四、提报结果 ───────────

    APPROVE_OK, APPROVE_REJECT = 1, 2

    def submit_records(self, *, page: int = 1, size: int = 20,
                       approve_status: int | None = None,
                       seller_operation_list: list[int] | None = None,
                       lead_id: str | None = None) -> dict:
        """我的提报记录 —— **v2 + POST**，body 是单层 `params`。

        真实请求（抓包）：
            POST /api/v2/product/oc/seller_product_opportunity/submit/record/list
            {"params": {"page_number":1,"page_size":20,
                        "approve_status":1,"seller_operation_list":[1,2]}}

        历史坑：老版客户端用了 `{"params":{"params":{…}}}` 双层嵌套 → code=0 但 total_cnt=0。
        另外 query 里必须带 `seller_id`（PageChannel 已带上）。
        total 只在 page_size >= 20 时返回。
        """
        inner: dict = {"page_number": page, "page_size": size}
        if approve_status is not None:
            inner["approve_status"] = approve_status
        if seller_operation_list is not None:
            inner["seller_operation_list"] = seller_operation_list
        if lead_id is not None:
            inner["lead_id"] = str(lead_id)
        path = f"/api/v2/product/oc/seller_product_opportunity/submit/record/list"
        d = self._post(path, {"params": inner}).get("data") or {}
        return {"total": d.get("total"), "record_list": d.get("record_list") or []}

    def approved(self, **kw) -> dict:
        kw.setdefault("seller_operation_list", [1, 2])
        return self.submit_records(approve_status=self.APPROVE_OK, **kw)

    def rejected(self, **kw) -> dict:
        kw.setdefault("seller_operation_list", [1, 2])
        return self.submit_records(approve_status=self.APPROVE_REJECT, **kw)

    def product_performance(self) -> dict:
        """提报成绩卡：total_submit_num / success_submit_spo_num / failed_submit_spo_num …"""
        return self._post(f"{PRE}/product/performance/Card",
                          {"params": {"biz_type": 0}}).get("data") or {}

    def reject_reasons(self) -> dict:
        return self._post(f"{PRE}/reasons/list", {}).get("data") or {}

    def endpoints(self) -> list[dict]:
        try:
            return json.loads(ENDPOINTS_FILE.read_text())
        except Exception:
            return []

    # ─────────── 五、分析 ───────────

    def failure_reasons(self, *, pages: int = 5, size: int = 100) -> Counter:
        """采样已被拒记录，统计 failure_reason 分布。"""
        c: Counter = Counter()
        for pg in range(1, pages + 1):
            d = self.rejected(page=pg, size=size)
            rows = d["record_list"]
            if not rows:
                break
            for x in rows:
                c[((x.get("spo_audit_result") or {}).get("failure_reason")
                   or x.get("failure_reason") or "<空>")] += 1
        return c

    def dup_analysis(self, *, pages: int = 10, size: int = 100) -> dict:
        """失败记录去重 —— 判断是"重复提报"还是"盲铺所有机会"。

        实测结论：唯一 (货品, 机会) 对 ≈ 记录数 → 是**盲铺**，不是重复。
        """
        prods, leads, pairs = Counter(), Counter(), Counter()
        n = 0
        for pg in range(1, pages + 1):
            rows = self.rejected(page=pg, size=size)["record_list"]
            if not rows:
                break
            n += len(rows)
            for x in rows:
                pid = str((x.get("tts_product_info") or {}).get("id"))
                lid = str(x.get("lead_id"))
                prods[pid] += 1
                leads[lid] += 1
                pairs[(pid, lid)] += 1
        return {"sample": n, "uniq_product": len(prods), "uniq_lead": len(leads),
                "uniq_pair": len(pairs), "top_product": prods.most_common(5),
                "top_lead": leads.most_common(5), "top_pair": pairs.most_common(5)}

    # ─────────── 六、准入预检（提报效率的核心）───────────
    #
    # ❌ 这一节的历史规则（segment token 命中数）**已被实测推翻**，保留仅为存档：
    #
    #   曾经的假设（从 100 条已批准 + 200 条已被拒反推）：
    #     标题命中 lead_segment 的 token 数（不区分大小写） vs 审核结果
    #       0 个 → 成功  0 / 失败  39   成功率   0.0%
    #       3 个 → 成功 46 / 失败   5   成功率  90.2%
    #       4 个 → 成功  8 / 失败   0   成功率 100.0%
    #     → 结论"命中 ≥3 就有 94%"。**拿它真打了 20 笔，20 笔全部被拒。**
    #
    #   为什么会被骗：
    #     1) 只取了 approved(page=1) —— 时间倒序的第一页，集中在少数机会上
    #     2) lead_segment 只覆盖 31/48 个机会，缺失被 any() 静默算成"不命中"
    #     3) 子串匹配有假阳性（机会 token "Gel" 能撞进毫不相关的长标题）
    #
    #   跨页重算（500 已批准 + 200 已被拒）后假设反转：
    #     segment ≥1 命中 →  已批准 26%  vs  已被拒 40%   ← 反相关 / 噪音
    #
    # 真正的判别式在**机会侧**，不在商品侧：
    #     成功样本 48 机会 / 142 商品；失败样本 17 机会 / 143 商品
    #     机会交集 = 1，商品交集 = 85
    #   → 同一商品在某些机会获批、在另一些被拒。所以要看"这个机会开不开放"。
    #   → open_leads() 读 notes/open_leads.json（4227 条批准记录的全量真值表）。
    #
    # 这个 MIN_HITS 常量只保留给 open_leads 未覆盖时的粗排，**不要再当准入规则用**。

    MIN_HITS = 3

    OPEN_LEADS_FILE = HERE / "notes" / "open_leads.json"

    def open_leads(self, *, min_approvals: int = 5) -> dict:
        """「开放机会」真值表 —— 由 4227 条批准记录全量统计得出。

        返回 {lead_id: {approvals, opportunity_name, approved_product_ids, …}}，
        按批准数倒序。**只往这些机会提报**才是提报效率的正确做法。

        生成方式（`python3 tk01_opportunity.py pull-approved`）：
            approve_status=1, seller_operation_list=[] 逐页翻到空
        """
        try:
            d = json.loads(self.OPEN_LEADS_FILE.read_text())
        except Exception:
            return {}
        return {k: v for k, v in (d.get("leads") or {}).items()
                if v.get("approvals", 0) >= min_approvals}

    def refill_open_leads(self, *, max_pages: int = 60) -> dict:
        """重新拉全量批准记录并重建 notes/open_leads.json。"""
        import collections
        rows, page = [], 1
        while page <= max_pages:
            d = self.approved(page=page, size=100)
            rs = d["record_list"]
            if not rs:
                break
            rows += rs
            if len(rs) < 100:
                break
            page += 1
        per: dict[str, list] = collections.defaultdict(list)
        for x in rows:
            lid = str(x.get("lead_id"))
            per[lid].append({"pid": str((x.get("tts_product_info") or {}).get("id")),
                             "title": (x.get("tts_product_info") or {}).get("name") or "",
                             "oname": x.get("opportunity_name") or ""})
        leads = {}
        for lid, items in per.items():
            leads[lid] = {"approvals": len(items),
                          "opportunity_name": items[0]["oname"],
                          "approved_product_ids": sorted({i["pid"] for i in items}),
                          "sample_approved_titles": [i["title"][:80] for i in items[:2]]}
        leads = dict(sorted(leads.items(), key=lambda kv: -kv[1]["approvals"]))
        out = {"source": "approved records", "rows": len(rows), "n_leads": len(leads),
               "n_open_ge5": sum(1 for v in leads.values() if v["approvals"] >= 5),
               "leads": leads}
        self.OPEN_LEADS_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1))
        return out

    @staticmethod
    def jaccard(a: str, b: str) -> float:
        """标题词集合的 Jaccard 相似度 —— 只用于**排除**明显不相关（<0.34 基本必挂），
        不用于准入：本店标题是关键词堆砌型，长标题撞词太容易。"""
        import re as _re
        tk = lambda s: {w for w in _re.findall(r"[^\W_]+", (s or "").lower(), _re.UNICODE) if len(w) >= 3}
        A, B = tk(a), tk(b)
        return len(A & B) / len(A | B) if (A | B) else 0.0

    @staticmethod
    def segment_hits(title: str, tokens: list[str]) -> list[str]:
        """标题命中了几个 segment token（不区分大小写）。

        ⚠️ 保留但**不要用来判断准入** —— 见本节顶部：这个规则已被 20/20 实测证伪。
        """
        t = (title or "").lower()
        return [k for k in (tokens or []) if k and k.lower() in t]

    def eligibility(self, lead_id: str, title: str, *, tokens: list[str] | None = None,
                    min_hits: int | None = None, require_open: bool = True) -> dict:
        """判断「这个商品标题能不能提报这个机会」。

        ⚠️ 警告：这里的 token 命中判定**不是有效性规则**（实测 20/20 反例）。
        真正起作用的是 `require_open`：机会是否在开放真值表里。

        返回 {ok, open, approvals, reasons}
        """
        opens = self.open_leads(min_approvals=1)
        rec = opens.get(str(lead_id))
        approvals = (rec or {}).get("approvals", 0)
        reasons = []
        if require_open and approvals == 0:
            reasons.append(f"该机会历史批准数为 0（{lead_id}）—— 本店做不了这类机会，别打")
        if title and rec and rec.get("sample_approved_titles"):
            best = max((self.jaccard(title, t) for t in rec["sample_approved_titles"]), default=0.0)
            if best < 0.34:
                reasons.append(f"与已获批商品标题最高相似度 {best:.2f} < 0.34，基本必挂")
            return {"ok": not reasons, "open": approvals > 0, "approvals": approvals,
                    "best_similarity": round(best, 3),
                    "opportunity_name": rec.get("opportunity_name"), "reasons": reasons}
        return {"ok": not reasons, "open": approvals > 0, "approvals": approvals,
                "opportunity_name": (rec or {}).get("opportunity_name"), "reasons": reasons}

    def product_titles(self, *, tab_id: int = 1, page_size: int = 100,
                       max_pages: int = 5) -> dict[str, str]:
        """{product_id: product_name} —— 走促销那套商品列表（直连可用）。"""
        from tk01_promo_client import PromoClient
        C = PromoClient(port=self.port)
        out: dict[str, str] = {}
        for pg in range(1, max_pages + 1):
            try:
                rows = C.product_list(tab_id=tab_id, page_size=page_size)
            except Exception:
                break
            if not rows:
                break
            for x in rows:
                pid = str(x.get("product_id") or "")
                if pid:
                    out[pid] = x.get("product_name") or ""
            if len(rows) < page_size:
                break
            time.sleep(1.0)
        return out

    def submission_plan(self, leads: list[dict], titles: dict[str, str], *,
                        min_hits: int | None = None, lead_details: dict | None = None) -> dict:
        """给定机会列表与店铺商品标题，算出该提报哪些 (机会, 商品) 对。

        返回 plan 里每条都带预测命中数与判定理由 —— 提交前先看这个，
        命中 < min_hits 的一律不提。
        """
        thr = self.MIN_HITS if min_hits is None else min_hits
        details = lead_details or {}
        plan, skipped = [], []
        for ld in leads:
            lid = str(ld.get("lead_id"))
            if lid not in details:
                try:
                    details[lid] = self.lead_detail(lid)
                except OppError as e:
                    skipped.append({"lead_id": lid, "reason": f"详情拉取失败: {e.message}"})
                    continue
            tokens = details[lid].get("lead_segment") or []
            if not tokens:
                skipped.append({"lead_id": lid, "reason": "lead_segment 为空（实测必挂）"})
                continue
            for pid, title in titles.items():
                hits = self.segment_hits(title, tokens)
                if len(hits) >= thr:
                    plan.append({"lead_id": lid, "product_id": pid, "hits": len(hits),
                                 "hit_words": hits,
                                 "opportunity_name": details[lid].get("lead_name"),
                                 "product_name": (title or "")[:60]})
                else:
                    skipped.append({"lead_id": lid, "product_id": pid, "hits": len(hits),
                                    "reason": f"命中 {len(hits)} < {thr}"})
        plan.sort(key=lambda x: (-x["hits"], x["lead_id"]))
        return {"threshold": thr, "n_leads": len(leads), "n_products": len(titles),
                "n_plan": len(plan), "n_skipped": len(skipped),
                "plan": plan, "skipped": skipped[:50]}

    # ─────────── 七、已验证可用的提报流程（实测 60%，最优子集 95%）───────────
    #
    # 规则来源：一轮 15 个开放机会 / 70 对的实打实测 —— 30 批准 / 20 拒绝 = 60%
    # （你的历史基线是 4%，提升 15×）。拆开看：
    #
    #   按机会 L3 类目:  873480 痘痘护理 → 19/20 = 95%
    #                    875016 掏耳工具 → 14/30 = 47%
    #                    601733 面罩     →  0/1  （本店不做）
    #   按选品相似度:    0.9-1.0 → 83%   0.7-0.9 → 74%
    #                    0.4-0.7 → 33%   0.0-0.4 → 54%
    #
    # 所以两条过滤叠加：**机会 L3 == 商品 L3** 且 **标题相似度 >= 0.7**。
    # 服务端自己给了这条规则：
    #   12050002 The selected product category does not match the lead category.

    SIM_THRESHOLD = 0.7

    def product_catalog(self, *, page_size: int = 100, max_pages: int = 5) -> dict:
        """{pid: {title, l3}} —— 带 L3 类目，用于与机会类目对齐。"""
        from tk01_promo_client import PromoClient
        C = PromoClient(port=self.port)
        out: dict[str, dict] = {}
        for _ in range(max_pages):
            try:
                rows = C.product_list(tab_id=1, page_size=page_size)
            except Exception:
                break
            if not rows:
                break
            for r in rows:
                pid = str(r.get("product_id") or "")
                if not pid:
                    continue
                cats = r.get("categories") or []
                out[pid] = {"title": r.get("product_name") or "",
                            "l3": str(cats[-1].get("id")) if cats else None}
            if len(rows) < page_size:
                break
            time.sleep(1.0)
        return out

    def smart_plan(self, *, max_leads: int = 15, per_lead: int = 5,
                   min_approvals: int = 5, sim: float | None = None,
                   same_category_only: bool = True,
                   approved: dict | None = None) -> dict:
        """按已验证的规则生成提报计划。

        1. 取有历史批准的机会（开放真值表）
        2. 取机会 L3 类目；只保留 L3 相同的商品（消掉全部"类目不符"拒绝）
        3. 按与已获批商品标题的相似度排序，取相似度 >= sim 的前 per_lead 个
        4. 排除该机会已提报过的 (lead_id, product_id)
        """
        thr = self.SIM_THRESHOLD if sim is None else sim
        A = approved or json.loads(
            (HERE / "notes" / "approved_full.json").read_text())["per_lead"]
        catalog = self.product_catalog()
        ranked = sorted(((k, len(v)) for k, v in A.items()), key=lambda x: -x[1])

        plan, skipped = [], []
        for lid, _ in ranked:
            if len({p["lead_id"] for p in plan}) >= max_leads:
                break
            appr = A[lid]
            seen = {x["pid"] for x in appr}
            ats = [x["title"] for x in appr if x["title"]]
            try:
                lead_l3 = str(self.lead_detail(lid).get("level3_cate_id") or "")
            except OppError as e:
                skipped.append({"lead_id": lid, "reason": f"详情失败 {e.message[:40]}"})
                continue
            cands = []
            for pid, info in catalog.items():
                if pid in seen:
                    continue
                if same_category_only and lead_l3 and info["l3"] and info["l3"] != lead_l3:
                    continue
                s = max((self.jaccard(info["title"], at) for at in ats), default=0.0)
                if s >= thr:
                    cands.append((s, pid, info["title"]))
            cands.sort(reverse=True)
            top = cands[:per_lead]
            if not top:
                skipped.append({"lead_id": lid, "reason": f"L3={lead_l3} 无相似度≥{thr} 的候选"})
                continue
            plan.append({"lead_id": lid, "lead_l3": lead_l3, "approvals": len(appr),
                         "opportunity_name": appr[0]["oname"],
                         "items": [{"pid": p, "score": round(s, 3), "title": t[:60]}
                                   for s, p, t in top]})
        return {"sim_threshold": thr, "n_leads": len(plan),
                "n_pairs": sum(len(p["items"]) for p in plan),
                "plan": plan, "skipped": skipped}

    def run_plan(self, plan: list[dict], *, apply: bool = False) -> dict:
        """执行 smart_plan 的产物，并按 (lead_id, product_id) 汇总请求结果。"""
        out = {"leads": len(plan), "submitted": 0, "ok_leads": 0, "errors": []}
        for p in plan:
            pids = [str(x["pid"]) for x in p["items"]]
            if not apply:
                out["submitted"] += len(pids)
                continue
            try:
                r = self._post(f"{PRE}/relate",
                               {"lead_id": p["lead_id"],
                                "relate_product_items": [{"tts_product_id": x} for x in pids]})
                if r.get("code") == 0:
                    out["ok_leads"] += 1
                    out["submitted"] += len(pids)
                else:
                    out["errors"].append({"lead_id": p["lead_id"], "code": r.get("code"),
                                          "message": r.get("message")})
            except OppError as e:
                out["errors"].append({"lead_id": p["lead_id"], "error": str(e)[:120]})
        return out

    def verify_recent(self, want: set[tuple[str, str]], *,
                      within_sec: int = 3600, max_pages: int = 10) -> dict:
        """核对刚落库的提报结果 —— **必须按时戳过滤**。

        不按时戳过滤会把历史上同样的 (lead, product) 对的拒绝记录算进本次结果，
        导致命中率被严重低估（实测差 30 vs 20 和 30 vs 4 两种口径）。
        """
        cut = time.time() - within_sec
        found: dict[tuple[str, str], tuple[str, float]] = {}
        for st, tag in ((self.APPROVE_OK, "已批准"), (self.APPROVE_REJECT, "已被拒")):
            for pg in range(1, max_pages + 1):
                try:
                    d = self.submit_records(page=pg, size=100,
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
                        break          # 记录按时间倒序，越过窗口就停
                    k = (str(x.get("lead_id")),
                         str((x.get("tts_product_info") or {}).get("id")))
                    if k in want and k not in found:
                        found[k] = (tag, ts)
                if stop or len(rs) < 100:
                    break
        ok = sum(1 for v in found.values() if v[0] == "已批准")
        bad = sum(1 for v in found.values() if v[0] == "已被拒")
        return {"want": len(want), "found": len(found), "approved": ok, "rejected": bad,
                "missing": len(want) - len(found),
                "hit_rate": round(ok / (ok + bad), 3) if (ok + bad) else None,
                "detail": {f"{k[0]}|{k[1]}": v[0] for k, v in found.items()}}


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok 商品机会 API 客户端（页面上下文传输）")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--gap", type=float, default=1.2, help="请求间隔秒（防验证码）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("leads"); p.add_argument("--type", type=int, default=3)
    p.add_argument("--page", type=int, default=1); p.add_argument("--size", type=int, default=10)
    p.add_argument("--sort", type=int, default=1)
    p = sub.add_parser("detail"); p.add_argument("lead_id")
    p = sub.add_parser("submits"); p.add_argument("--status", type=int, choices=[1, 2])
    p.add_argument("--page", type=int, default=1); p.add_argument("--size", type=int, default=20)
    sub.add_parser("stats")
    p = sub.add_parser("why"); p.add_argument("--pages", type=int, default=5)
    p = sub.add_parser("dup"); p.add_argument("--pages", type=int, default=10)
    p = sub.add_parser("relate"); p.add_argument("lead_id"); p.add_argument("product_ids", nargs="+")
    p.add_argument("--yes", action="store_true", help="真的发出去（写操作）")
    sub.add_parser("endpoints")
    p = sub.add_parser("search"); p.add_argument("text")
    p = sub.add_parser("elig"); p.add_argument("lead_id"); p.add_argument("title")
    p.add_argument("--min-hits", type=int)
    p = sub.add_parser("plan"); p.add_argument("--type", type=int, default=3)
    p.add_argument("--leads", type=int, default=10); p.add_argument("--min-hits", type=int, default=3)
    p.add_argument("--dump", help="把计划写到该 JSON 文件")
    sub.add_parser("titles")
    p = sub.add_parser("openleads"); p.add_argument("--min", type=int, default=5)
    sub.add_parser("pull-approved")
    p = sub.add_parser("smart"); p.add_argument("--leads", type=int, default=15)
    p.add_argument("--per-lead", type=int, default=5); p.add_argument("--sim", type=float, default=0.7)
    p.add_argument("--min-approvals", type=int, default=5)
    p.add_argument("--any-category", action="store_true")
    p.add_argument("--save", default="notes/smart_plan.json")
    p = sub.add_parser("runsmart"); p.add_argument("--plan-file", default="notes/smart_plan.json")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--wait", type=int, default=20, help="提交后等待秒数再核对")
    p = sub.add_parser("execute")
    p.add_argument("--plan-file", default="notes/submission_plan.json")
    p.add_argument("--min-hits", type=int, default=3)
    p.add_argument("--max-leads", type=int)
    p.add_argument("--no-skip-existing", action="store_true")
    p.add_argument("--yes", action="store_true", help="真的发出去（写操作）")

    a = ap.parse_args()
    O = OpportunityClient(port=a.port, gap=a.gap)
    try:
        if a.cmd == "leads":
            d = O.list_leads(page=a.page, size=a.size, opportunity_type=a.type, sort_field=a.sort)
            rows = d.get("lead_list") or []
            print(f"total_product_count={d.get('total_product_count')} 本页 {len(rows)} 条")
            for x in rows:
                print(f"  {x.get('lead_id')} [{OPP_TYPE.get(x.get('opportunity_type'), x.get('opportunity_type'))}] "
                      f"{str(x.get('lead_name'))[:44]}")
                print(f"      类目={x.get('level1_cate_name')}/{x.get('level2_cate_name')}/{x.get('level3_cate_name')}"
                      f"  搜索量={x.get('search_volume')}  在线商品={x.get('online_products')}")
        elif a.cmd == "detail":
            print(json.dumps(O.lead_detail(a.lead_id), ensure_ascii=False, indent=1)[:3000])
        elif a.cmd == "submits":
            d = O.submit_records(page=a.page, size=a.size, approve_status=a.status,
                                 seller_operation_list=[1, 2])
            print(f"total={d['total']}")
            for x in d["record_list"]:
                ar = x.get("spo_audit_result") or {}
                print(f"  rt={ar.get('result_value')} op={x.get('seller_operation')} "
                      f"lead={x.get('lead_id')} pid={(x.get('tts_product_info') or {}).get('id')} "
                      f"{str(x.get('opportunity_name'))[:34]} | {ar.get('failure_reason') or ''}")
        elif a.cmd == "stats":
            print(json.dumps(O.product_performance(), ensure_ascii=False, indent=1))
        elif a.cmd == "why":
            for r, c in O.failure_reasons(pages=a.pages).most_common(15):
                print(f"  {c:>6}  {r}")
        elif a.cmd == "dup":
            print(json.dumps(O.dup_analysis(pages=a.pages), ensure_ascii=False, indent=1))
        elif a.cmd == "relate":
            r = O.relate(a.lead_id, a.product_ids, apply=a.yes)
            print(json.dumps(r, ensure_ascii=False, indent=1)[:1200])
        elif a.cmd == "endpoints":
            eps = O.endpoints()
            print(f"共 {len(eps)} 个端点:")
            for e in sorted(eps, key=lambda x: x["path"]):
                print(f"  v{e['ver']} {e['method']:5} {'?' if e['query'] else ' '} "
                      f"/{e['path']:52} {e['op']}")
        elif a.cmd == "search":
            print(json.dumps(O.search_tts_products(a.text), ensure_ascii=False)[:1200])
        elif a.cmd == "elig":
            print(json.dumps(O.eligibility(a.lead_id, a.title, min_hits=a.min_hits),
                             ensure_ascii=False, indent=1))
        elif a.cmd == "titles":
            t = O.product_titles()
            print(f"店铺商品 {len(t)} 个:")
            for pid, name in list(t.items())[:20]:
                print(f"  {pid}  {(name or '')[:64]}")
        elif a.cmd == "openleads":
            d = O.open_leads(min_approvals=a.min)
            print(f"开放机会（历史批准 ≥{a.min} 次）: {len(d)} 个")
            for lid, v in list(d.items())[:40]:
                print(f"  {v['approvals']:>4}×  {lid}  {str(v.get('opportunity_name'))[:50]}")
                print(f"        已获批商品 {len(v.get('approved_product_ids') or [])} 个")
        elif a.cmd == "pull-approved":
            r = O.refill_open_leads()
            print(f"拉取已批准记录 {r['rows']} 条 → 机会 {r['n_leads']} 个，"
                  f"其中 ≥5 次批准 {r['n_open_ge5']} 个")
            print("→ notes/open_leads.json")
        elif a.cmd == "smart":
            r = O.smart_plan(max_leads=a.leads, per_lead=a.per_lead, sim=a.sim,
                             min_approvals=a.min_approvals,
                             same_category_only=not a.any_category)
            print(f"相似度门槛 ≥{r['sim_threshold']}  机会 {r['n_leads']} 个  "
                  f"拟提交 {r['n_pairs']} 对")
            for p in r["plan"]:
                print(f"\n  {p['lead_id']}  L3={p['lead_l3']}  历史批准 {p['approvals']}")
                print(f"      {str(p['opportunity_name'])[:56]}")
                for it in p["items"]:
                    print(f"      {it['score']:.3f}  {it['pid']}  {it['title']}")
            for s in r["skipped"][:6]:
                print(f"  [跳过] {s['lead_id']}  {s['reason']}")
            Path(a.save).write_text(json.dumps(r, ensure_ascii=False, indent=1))
            print(f"\n→ {a.save}")
        elif a.cmd == "runsmart":
            pf = Path(a.plan_file)
            if not pf.exists():
                raise OppError(None, f"找不到 {pf}（先跑 smart）", "runsmart")
            plan = json.loads(pf.read_text())["plan"]
            n = sum(len(p["items"]) for p in plan)
            print(f"计划 {len(plan)} 个机会 / {n} 对  {'（真写）' if a.yes else '（dry-run）'}")
            if not a.yes:
                for p in plan[:5]:
                    print(f"  [dry] {p['lead_id']} → {len(p['items'])} 个")
                print("加 --yes 才真的提交")
                return
            before = O.product_performance()
            print(f"提交前 total={before['total_submit_num']} success={before['success_submit_spo_num']}")
            r = O.run_plan(plan, apply=True)
            print(f"通过 {r['ok_leads']}/{r['leads']} 个机会，提交 {r['submitted']} 对，"
                  f"错误 {len(r['errors'])}")
            for e in r["errors"][:8]:
                print(f"  ✗ {e.get('lead_id')} {e.get('code','')} {str(e.get('message') or e.get('error'))[:70]}")
            want = {(p["lead_id"], str(x["pid"])) for p in plan for x in p["items"]}
            print(f"\n等 {a.wait}s 后按时戳核对…")
            time.sleep(a.wait)
            v = O.verify_recent(want)
            print(f"  落库 {v['found']}/{v['want']}（差额为历史重复，不建新记录）")
            print(f"  已批准 {v['approved']} / 已被拒 {v['rejected']}")
            if v["hit_rate"] is not None:
                print(f"  ★ 本次命中率 {v['hit_rate']*100:.1f}%   （你的历史基线 4%）")
            after = O.product_performance()
            print(f"  计数器: success +{after['success_submit_spo_num']-before['success_submit_spo_num']}"
                  f"  failed +{after['failed_submit_spo_num']-before['failed_submit_spo_num']}"
                  f"  （异步聚合，偏小）")
        elif a.cmd == "plan":
            d = O.list_leads(page=1, size=a.leads, opportunity_type=a.type)
            leads = d.get("lead_list") or []
            print(f"机会 {len(leads)} 个，取店铺商品标题…")
            titles = O.product_titles()
            print(f"商品 {len(titles)} 个，进行准入预检（门槛 ≥{a.min_hits} 命中）…")
            r = O.submission_plan(leads, titles, min_hits=a.min_hits)
            print(f"\n可提报 {r['n_plan']} 对 / 跳过 {r['n_skipped']} 对 "
                  f"（机会 {r['n_leads']} × 商品 {r['n_products']}）")
            for x in r["plan"][:40]:
                print(f"  ✓ {x['hits']}命中 {x['hit_words']}  lead={x['lead_id']} pid={x['product_id']}")
                print(f"      {str(x['opportunity_name'])[:44]}  ←  {x['product_name']}")
            if a.dump:
                Path(a.dump).write_text(json.dumps(r, ensure_ascii=False, indent=1))
                print(f"\n→ {a.dump}")
        elif a.cmd == "execute":
            pf = Path(a.plan_file)
            if not pf.exists():
                raise OppError(None, f"找不到计划文件 {pf}（先跑 plan --dump …）", "execute")
            plan = json.loads(pf.read_text())["plan"]
            print(f"计划 {len(plan)} 对，门槛 ≥{a.min_hits} 命中"
                  f"{'（真写）' if a.yes else '（dry-run）'}")
            r = O.execute_plan(plan, apply=a.yes, min_hits=a.min_hits,
                               skip_existing=not a.no_skip_existing,
                               max_leads=a.max_leads,
                               on_progress=lambda lid, n: print(f"  → lead={lid} 提交 {n} 个", flush=True))
            print(f"\n机会 {r['leads']} 个 / 将提交 {r['would_submit']} 对 / "
                  f"实际提交 {r['submitted']} / 已提报过跳过 {r['skipped_existing']} / "
                  f"低命中拒绝 {r['rejected_low_hits']}")
            for x in r["results"]:
                if x.get("would_post"):
                    print(f"  [dry] lead={x['lead_id']} → "
                          f"{len(x['would_post']['relate_product_items'])} 个商品")
                elif x.get("submitted"):
                    print(f"  [ok ] lead={x['lead_id']} → {len(x['submitted'])} 个  "
                          f"code={x.get('code')} {x.get('message')}")
                elif x.get("error"):
                    print(f"  [ERR] lead={x['lead_id']} → {x['error'][:110]}")
                else:
                    print(f"  [ - ] lead={x['lead_id']} → {x.get('note','')}")
    finally:
        O.close()


if __name__ == "__main__":
    try:
        main()
    except OppError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        import traceback
        traceback.print_exc()
