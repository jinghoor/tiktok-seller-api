#!/usr/bin/env python3
"""TikTok Shop 联盟中心（Affiliate Center）API 客户端 —— SHOP_XBORDER 跨境店。

## 与 Seller 侧的区别（踩过）

| | Seller Center | 联盟中心 |
|---|---|---|
| 域 | `api16-normal-sg.tiktokshopglobalselling.com` | **`affiliate.tiktokshopglobalselling.com`** |
| app_name | `i18n_ecom_shop` | **`i18n_ecom_alliance`** |
| 语言参数 | `locale` / `language` | **`user_language`** |
| 页面 | `/product/opportunity` | `/affiliate/creator` |

签名要求相同（webmssdk 注入 `X-Bogus` / `X-Gnarly` / `msToken` /
`X-Tts-Oec-Bsid` / `fp`），所以复用 `PageChannel.raw_call`
（about:blank iframe 里的原生 fetch + `byted_acrawler.frontierSign` 自签名）。

## ⚠️ 当前实测的可用边界（务必先读，别浪费时间）

### 已确认可用的端点（全部 code=0）

| 端点 | 关键参数 / 返回 |
|---|---|
| `GET  /api/v1/affiliate/menu` | 8 个板块 |
| `GET  /api/v1/affiliate/account/info_v2` | 账号 + global_seller |
| `GET  /api/v1/oec/.../invitation_group/invitation/limit` | `{max_creator_num:50, max_product_num:100}` |
| `GET  /api/v1/oec/.../crm/creator/upper_limit/get` | `{total_limit:30000, shop_manage_tag_limit:600}` |
| `GET  /api/v1/oec/affiliate/seller/im/get/token` | IM token |
| `POST /api/v1/oec/affiliate/creator/marketplace/option` | 筛选器：品牌 400 / 类目 25 / 价格带 5 / 语言 2 |
| `POST /api/v1/oec/affiliate/cmp/filter` | 筛选器开关 |
| `POST /api/v1/oec/affiliate/seller/feature_control` | 灰度 AB 参数 |
| `POST /api/v1/oec/affiliate/seller/wish_list/search/creator` | 心愿单达人 |
| `POST /api/v1/affiliate/grayscale_strategy/check` | 灰度开关字典 |
| `POST /api/v1/oec/.../invitation_group/general/config` | 定向计划通用配置 |
| `POST /api/v1/oec/.../invitation_group/search` | `{"cur_page":1,"page_size":10}` |
| `POST /api/v1/affiliate/product_selection/list` | `{"cur_page":1,"page_size":10,"source":0}` → `total_num=624` |

### ⚠️ 三个踩过的坑（每个都花了很多时间）

**坑 1：`/oec/` 路由必须带 `oec_region` + `oec_seller_id`**
少了就一律 `98001004`，而且响应里 `"region": ""` 是空串（这就是线索）。
我第一次抓包把 URL 截断到 400 字符，正好把这两个参数截掉了。

**坑 2：`marketplace/find` 还需要完整的浏览器指纹块**
`fp` / `device_platform` / `cookie_enabled` / `screen_width` / `screen_height` /
`browser_language` / `browser_platform` / `browser_name` / `browser_version` /
`browser_online` / `timezone_name`。补上后当场通了（12 个达人）。
`fp` 直接取页面里的 `window.OECCaptcha.getFp()`，不用自己造。

**坑 3：不能用 iframe 原生 fetch（在 seller 侧能用，联盟侧不行）**
iframe 的 about:blank 文档 `Origin` 是 `null`、没有 `Referer`，服务端判成插件：
```
{"code":100000,"message":"Please remove the plugin and try again"}
```
实测**连"原样完整签名 URL"用 iframe 重放都被拒** —— 所以不是签名问题，
是请求来源特征。联盟域必须走**页面自己的 fetch**。

### 分页字段名：`cur_page` / `page_size`

联盟侧不是 `page`/`size`。用错的字段名会得到：
```
400 binding: expr_path=page_size, cause=missing required parameter
```
这两个名字是用**绑定错误预言机**逐个问出来的（同商品机会那套方法）。

### `find` 的间歇性已被重试治住（实测）

```
size=3  30.3s  code=98001004   ← 首轮失败
size=6  21.5s  code=0  n=6     ← 重载 fp 后重试成功
翻页 2 页 → 12 行（search_key 游标）
```

做法：`call()` 里遇到 `98001004` 就**重新取 fp**（`OECCaptcha.getFp()`）并最多重试 2 次。
成功率上去了，代价是**每次调用可能 20~30s**（重试要等）。

触发页面的顺序（实测复现）：先进 `/affiliate/creator/marketplace`，
再进 `/affiliate/creator/search`，app 才会真正打 `find`。
单独 goto search 不会触发（SPA 有缓存）。

### 仍未攻下

| 端点 | 现象 | 推测 |
|---|---|---|
| `POST /api/v1/oec/affiliate/cmp/creator/rank/list/get` | `98001004`（返回带 `msg` 键） | 需要**合法的 `rank_list_meta`** —— 可能要从排行榜页面自己的配置接口取 |
| `POST /api/v1/affiliate/sample/group/list` | `98001004`（返回带 `has_more`/`total_count` 但为 null） | 参考实现的响应解析是 `data.response.agg_info`，说明按聚合返回 —— 可能缺 `agg_type` 之类的字段，或需要先有样品数据 |

### 达人数据字段（`find` 返回）

`creator_oecuid` / `handle` / `nickname` / `avatar` / `follower_cnt` / `category` /
`brand_safe_tag` / `ec_live_gpm` / `ec_video_gpm`（带货转化）/
`ec_live_avg_uv` / `ec_video_engagement` / `creator_fulfillment_score_90d`（90天履约评分）/
`creator_fulfillment_reviews` / `has_collaborated` / `has_invited_before_90d` /
`is_creator_blocked_by_shop` / `invoice_available` / `is_high_sample_dispatch_rate`

翻页用 `next_pagination.search_key` 游标（服务端签名过，不能自己造）。

### 旧的失败记录（已解决，留档）

`/api/v1/affiliate/*` 与 `/api/v1/oec/*` 的行为**完全不同**：

| 路径族 | 实测结果 |
|---|---|
| `GET  /api/v1/affiliate/menu` | ✅ code=0 |
| `GET  /api/v1/oec/affiliate/seller/invitation_group/invitation/limit` | ✅ code=0 |
| `GET  /api/v1/oec/affiliate/crm/creator/upper_limit/get` | ✅ code=0 |
| `POST /api/v1/affiliate/grayscale_strategy/check` | ✅ code=0 |
| `POST /api/v1/oec/affiliate/creator/marketplace/find`（达人广场搜索） | ✅ **已打通**（带 fp 重试，见下） |
| `POST /api/v1/oec/affiliate/creator/marketplace/option`（筛选器） | ❌ 98001004 |
| `POST /api/v1/oec/affiliate/cmp/filter` | ❌ 98001004 |
| `POST /api/v1/oec/affiliate/seller/feature_control` | ❌ 98001004 |
| `POST /api/v1/oec/affiliate/seller/wish_list/search/creator` | ❌ 98001004 |

失败响应固定是：
```json
{"code":98001004,"message":"Invalid parameters. Please verify your input before retrying","region":""}
```

**注意 `"region":""` 是空的** —— `/oec/` 网关没识别出地区，说明它依赖某样我还没复现的东西。

已经排除的原因（都试过，结果一样）：
- body 形状（抓包里的原样 body）
- query 参数（抓包的**完整**参数集，含 `fp`/`device_platform`/`screen_*`）
- `shop_region` / `region` / `oec_region` / `is_hot_api`
- 传输方式：页面 fetch、页面 XHR、iframe 原生 fetch 三种都试了
- 多塞 seller 侧参数会额外触发 `98001004`，已改为可配置 `base_query` 消除

而**页面自己发同样的 URL 是成功的**（抓包里 `marketplace/find` 返回了真实
`creator_profile_list`）→ 端点没问题，是我的请求上下文缺东西。

**下一步（最有希望）**：真实请求是 `type: xhr` + `same-origin` + 带 `referer`，
且 query 里同时有 `X-Bogus` / `X-Gnarly` / `X-Tts-Oec-Bsid`。
参考工具（ThirdParty/ ThirdParty2）**不自己生成签名，而是把真实请求的整套签名参数
采集下来复用**（declarativeNetRequest 监听 → storage）。
所以做法应是：先让页面真实点一次达人广场，用
`performance.getEntriesByType('resource')` 抓下那次 `/oec/` 请求的**完整
签名块**（含 `X-Gnarly`，它只对我们没有），再在短窗口内用同一签名块重放同端点。

## 接口来源

1. 实盘抓包（`notes/affiliate_capture.json`，39 条请求 / 16 个端点）
2. 参考实现 `Project-dalian` 的 `dist2.0.9-接口与功能文档.md` §7、§8

用法:
  python3 tk01_affiliate.py account            # 账号 / 全局店铺信息
  python3 tk01_affiliate.py menu               # 左侧导航（看有哪些板块）
  python3 tk01_affiliate.py options            # 筛选器字典（品牌/类目/…）
  python3 tk01_affiliate.py creators [--query x] [--pages 3]
  python3 tk01_affiliate.py profile <creator_oecuid>
  python3 tk01_affiliate.py rank [--size 20]
  python3 tk01_affiliate.py limits             # 邀约上限 / CRM 导入上限
  python3 tk01_affiliate.py suggestions <text>
  python3 tk01_affiliate.py groups             # 定向计划列表
  python3 tk01_affiliate.py samples            # 寄样/样品申请列表
  python3 tk01_affiliate.py endpoints          # 打印已知端点清单
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_opportunity import PageChannel, OppError, AID  # noqa: E402

# ── 店铺上下文：从 tk01_config 读（多店铺 / 多区域）──
try:
    from tk01_config import (AFFILIATE_HOST as AFF_HOST,
                             AFFILIATE_APP_NAME as AFF_APP,
                             SELLER as SHOP_ID, REGION, DEFAULT_PORT,
                             TIMEZONE_NAME)
except Exception:
    AFF_HOST = "https://affiliate.tiktokshopglobalselling.com"
    AFF_APP = "i18n_ecom_alliance"
    SHOP_ID = "7494XXXXXXXXXX00"
    REGION = "VN"
    TIMEZONE_NAME = "Asia/Bangkok"

# 抓包 + 参考文档归纳出的端点表
ENDPOINTS = {
    # ── 账号 / 配置 ──
    "account_info":        ("GET",  "/api/v1/affiliate/account/info"),
    "account_info_v2":     ("GET",  "/api/v1/affiliate/account/info_v2"),
    "config":              ("GET",  "/api/v1/affiliate/config"),
    "menu":                ("GET",  "/api/v1/affiliate/menu"),
    "resource_list":       ("GET",  "/api/v1/affiliate/resource/list/get"),
    "grayscale_check":     ("POST", "/api/v1/affiliate/grayscale_strategy/check"),
    "feature_control":     ("POST", "/api/v1/oec/affiliate/seller/feature_control"),
    "cdn_rule":            ("GET",  "/api/v1/common/cdn_rule"),
    # ── 达人广场（核心）──
    "marketplace_find":    ("POST", "/api/v1/oec/affiliate/creator/marketplace/find"),
    "marketplace_option":  ("POST", "/api/v1/oec/affiliate/creator/marketplace/option"),
    "marketplace_profile": ("POST", "/api/v1/oec/affiliate/creator/marketplace/profile"),
    "creator_rank":        ("POST", "/api/v1/oec/affiliate/cmp/creator/rank/list/get"),
    "cmp_filter":          ("POST", "/api/v1/oec/affiliate/cmp/filter"),
    "search_suggestions":  ("POST", "/api/v1/insights/affiliate/creator/search/suggestions"),
    "wishlist_search":     ("POST", "/api/v1/oec/affiliate/seller/wish_list/search/creator"),
    # ── 邀约 / 定向计划 ──
    "invitation_limit":    ("GET",  "/api/v1/oec/affiliate/seller/invitation_group/invitation/limit"),
    "group_general_cfg":   ("GET",  "/api/v1/oec/affiliate/seller/invitation_group/general/config"),
    "group_search":        ("POST", "/api/v1/oec/affiliate/seller/invitation_group/search"),
    "group_detail":        ("POST", "/api/v1/oec/affiliate/seller/invitation_group/detail"),
    "group_create":        ("POST", "/api/v1/oec/affiliate/seller/invitation_group/create"),
    "group_update":        ("POST", "/api/v1/oec/affiliate/seller/invitation_group/update"),
    "group_search_creator": ("POST", "/api/v1/oec/affiliate/seller/invitation_group/search/creator"),
    "group_creators_add":  ("POST", "/api/v1/oec/affiliate/seller/invitation_group/creators_add"),
    "group_terminate":     ("POST", "/api/v1/oec/affiliate/seller/invitation_group/terminate"),
    "group_conflict":      ("POST", "/api/v1/oec/affiliate/seller/invitation_group/conflict_check"),
    "group_conflict_fix":  ("POST", "/api/v1/oec/affiliate/seller/invitation_group/conflict_check/resolve"),
    "group_text_check":    ("POST", "/api/v1/oec/affiliate/seller/invitation_group/sensitive_text_check"),
    "product_creator_rel": ("POST", "/api/v1/oec/affiliate/seller/invitation_group/product_creator_relation"),
    # ── 样品 / 商品 / CRM ──
    "sample_group_list":   ("POST", "/api/v1/affiliate/sample/group/list"),
    "product_selection":   ("POST", "/api/v1/affiliate/product_selection/list"),
    "crm_upper_limit":     ("GET",  "/api/v1/oec/affiliate/crm/creator/upper_limit/get"),
    "crm_batch_send":      ("POST", "/api/v1/oec/affiliate/crm/im_messages/batch_send"),
    "im_token":            ("GET",  "/api/v1/oec/affiliate/seller/im/get/token"),
    "im_token_shop":       ("GET",  "/api/v1/im/shop_creator/shop/user/token/get"),
    "avail_invitation":    ("GET",  "/api/v1/affiliate/lux/invitation/available_list"),
    # ── 平台运营位 ──
    "opt_in_card":         ("POST", "/api/v1/affiliate/open_collaboration/opt_in/card/get"),
    # ── MCN / Partner 域（api-partner-va.tiktokshop.com）──
    "partner_info":        ("GET",  "/api/v1/partner/profile/partner_info"),
    "partner_batch_invite": ("POST", "/api/v1/affiliate/partner/invite/creator/batch/create"),
    "partner_invite_mget": ("POST", "/api/v1/affiliate/partner/invite/creator/mget"),
    "partner_find":        ("POST", "/api/v1/oec/affiliate/creator/marketplace/4partner/find"),
    "partner_option":      ("POST", "/api/v1/oec/affiliate/creator/marketplace/4partner/option"),
}


class AffiliateClient:
    """联盟中心接口封装。所有请求走页面上下文（raw_call）。"""

    def __init__(self, *, port: int = CDP_PORT, gap: float = 0.8):
        self.fp = ""
        self.ch = PageChannel(port, gap=gap, host=AFF_HOST, app_name=AFF_APP,
                              seller_id=SHOP_ID, page_match="/affiliate/creator",
                              base_query=dict(self._base_params()))
        self.port = port
        self.load_fp()
        # load_fp 之后再刷一次 base_query（里面含 fp）
        self.ch.base_query = dict(self._base_params())

    def close(self):
        self.ch.close()

    # ---- 内部 ----
    # ★ 这套 query 是打通 `/oec/` 路由的关键（实测对比出来的）
    #
    # 只带 user_language/aid/app_name/device_id → 一律 98001004，
    # 响应里 "region": "" 是空的。
    # 补上 `oec_region` + `oec_seller_id` 后 → 4/5 个 `/oec/` 端点通了。
    # 再补上**浏览器指纹块**（fp / device_platform / screen_* / browser_* /
    # timezone_name）后 → 达人广场搜索 `marketplace/find` 也通了。
    #
    # 实测真实请求是 17 个业务参数 + 4 个签名参数（msToken / X-Bogus /
    # X-Gnarly / X-Tts-Oec-Bsid，后三个由页面 SDK 注入）。
    #
    # 注意：真实 `find` 请求里**没有** `oec_region`，也**没有** `is_hot_api`
    # （文档说"强制含 is_hot_api=true"，实测不加也能通）。
    def _base_params(self) -> dict:
        return {
            "user_language": "zh-CN", "aid": AID, "app_name": AFF_APP,
            "device_id": "0",
            "oec_seller_id": SHOP_ID, "shop_region": REGION,
            "fp": self.fp,
            "device_platform": "web", "cookie_enabled": "true",
            "screen_width": "1512", "screen_height": "982",
            "browser_language": "vi-VN", "browser_platform": "MacIntel",
            "browser_name": "Mozilla",
            "browser_version": ("5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/140.0.0.0 Safari/537.36"),
            "browser_online": "true", "timezone_name": TIMEZONE_NAME,
        }

    def load_fp(self) -> str:
        """取设备指纹 —— 页面里 `OECCaptcha.getFp()` 就有，不必自己造。"""
        try:
            self.ch._ensure()
            v = self.ch._page.evaluate(
                "(()=>{try{return (window.OECCaptcha&&OECCaptcha.getFp)?OECCaptcha.getFp():'';}"
                "catch(e){return '';}})()")
            self.fp = str(v or "")
        except Exception:
            self.fp = ""
        return self.fp

    def call(self, name: str, body=None, *, extra: dict | None = None,
             raw: bool = False) -> dict:
        if name not in ENDPOINTS:
            raise KeyError(f"未知端点 {name}")
        method, path = ENDPOINTS[name]
        p: dict = {}
        if extra:
            p.update(extra)
        # ── 混合传输：Worker 优先，遇"插件检测"再回落页面 fetch ──
        #
        # 三个候选（实测结论）：
        #   raw_call(iframe)    → 联盟域一律 100000（Origin: null），**永远别用**
        #   worker_call(Worker) → 同源、无 SDK、**不抢前台**，而且能把
        #                         服务端的验证码要求（code=10000 + bdturing 头）
        #                         **暴露出来**（页面 fetch 会把它隐藏成"挂起"）
        #   call(页面 fetch)     → SDK 完整签名，但需要页面在前台（会抢焦点）
        #
        # 实测 Worker 能过的：邀约上限 / 导航表 / 筛选字典 / 排行榜 …
        # Worker 过不了的：`marketplace/find`（要 SDK 的 X-Gnarly 等完整签名）
        #   → 那些回落到页面 fetch
        payload = body if method == "POST" else None
        r = None
        if not p.get("_force_page"):
            try:
                r = self.ch.worker_call(path, payload, method=method)
            except Exception:
                r = None
            if isinstance(r, dict) and r.get("code") in (100000, 10000):
                # 100000 = 被判插件（Worker 只签了 X-Bogus）
                # 10000  = 服务端软挑战（同样是因为签名不完整）
                # 两者都回落页面 fetch —— SDK 的完整签名（含 X-Gnarly）不会被挑战
                if r.get("code") == 10000 and not raw:
                    r["_worker_captcha"] = bool(r.get("_captcha"))
                r = None
        if r is None:
            r = self.ch.call(path, payload, method=method, params=p or None)
        # `marketplace/find` 会间歇性 98001004 —— 实测同一个 body 有时通有时不通，
        # 怀疑与 fp / msToken 的时效有关。失败就重新取 fp 再试一次。
        if isinstance(r, dict) and r.get("code") == 98001004:
            # 不论 fp 是否变化都重试 —— 实测 fp 常常不变但重试就通
            for attempt in (1, 2):
                self.load_fp()
                self.ch.base_query = dict(self._base_params())
                time.sleep(0.7 * attempt)
                r2 = self.ch.call(path, body if method == "POST" else None,
                                  method=method, params=p or None)
                if isinstance(r2, dict) and r2.get("code") == 0:
                    return r2
                r = r2
        if raw:
            return r
        return r if isinstance(r, dict) else {}

    # ---- 账号 / 配置 ----
    def account(self) -> dict:
        return self.call("account_info_v2", extra={"account_type": 1}).get("data") or {}

    def menu(self) -> list:
        return self.call("menu", extra={"only_menu": "false"}).get("data") or []

    def invitation_limit(self) -> dict:
        return self.call("invitation_limit").get("data") or {}

    def crm_upper_limit(self) -> dict:
        return self.call("crm_upper_limit").get("data") or {}

    # ---- 筛选器 ----
    OPTION_TYPES = [3, 2, 1, 4, 5, 8, 6, 7]

    def options(self, types=None) -> dict:
        """达人广场筛选器字典（品牌 / 类目 / 地区 / 粉丝量 …）。

        实测 option_type：3,2,1,4,5,8,6,7 —— 参考实现也是按这个顺序请求的。
        """
        ts = types or self.OPTION_TYPES
        r = self.call("marketplace_option",
                      {"option_req_params_list": [{"option_type": t} for t in ts]})
        return r.get("options") or {}

    def cmp_filter(self) -> dict:
        return self.call("cmp_filter", {}).get("filters") or []

    # ---- 达人广场（核心）----
    # ★ 触发 `find` 的正确页面序列（实测复现两次）
    #
    # 单独 goto `/affiliate/creator/search` 不会让 app 发 `find`；
    # 必须先经过 `/affiliate/creator/marketplace` 再进 `search`，
    # app 的搜索才会真正打出去（顺序很关键）。
    MARKET_URL = ("https://affiliate.tiktokshopglobalselling.com/affiliate/creator/marketplace"
                  "?shop_region=VN&shop_id=" + SHOP_ID)
    SEARCH_URL = ("https://affiliate.tiktokshopglobalselling.com/affiliate/creator/search"
                  "?shop_region=VN&shop_id=" + SHOP_ID)

    def ensure_find_page(self) -> bool:
        """⚠️ **已停用**（默认不做事）。

        曾经想"开静默窗口"来满足 `find` 的页面上下文要求，结果：
        - `Target.createTarget({newWindow:true})` 每次都**新建一个窗口**
        - Playwright 的 `ctx.pages` 同步不到（即便拉长到 28 秒）
        - 于是每调用一次就多一个窗口，**在操作者桌面上堆了 10 个重复标签**

        已把造成堆积的窗口一并关掉，这里改为**永不建窗口**。
        `find` 需要页面上下文时，由操作者自己把某个标签页放到
        `/affiliate/creator/search`，或者显式调用 `use_quiet_window()`
        并**自己负责关掉**。

        返回 False 表示"没有可用的自有页面"，调用方照常发请求即可。
        """
        return False

    def ensure_marketplace_page(self) -> str:
        """确保页面停在「达人广场」上再发 `find`。

        实测规律：页面在 `/affiliate/creator/search` 时 `find` 通过；
        页面在别处时同一个 body 稳定返回 98001004。
        服务端显然校验了页面上下文，所以发请求前先把页面摆对。
        """
        try:
            self.ch._ensure()
            cur = self.ch._page.url
            if self.page_ok(cur):
                return cur
            # ⚠️ 绝不 goto 操作者的标签页 —— 那会打断他正在做的事。
            # 需要切页时请自己开一个页面并标记 `_dsh_quiet`，或在 UI 上手动切。
            if not getattr(self.ch._page, "_dsh_quiet", False):
                print("    [aff] 当前页面不在 /affiliate/creator/search，"
                      "但它是操作者的标签页 —— 不导航。", flush=True)
                return cur
            self.load_fp()
            self.ch.base_query = dict(self._base_params())
            return self.ch._page.url
        except Exception as e:
            print(f"    [aff] 切页失败: {str(e)[:80]}", flush=True)
            return ""

    @staticmethod
    def page_ok(url: str) -> bool:
        return "/affiliate/creator/search" in (url or "")

    def find_creators(self, *, query: str = "", page: int = 0, size: int = 12,
                      filter_params: dict | None = None, algorithm: int = 1,
                      search_key: str | None = None) -> dict:
        """达人广场搜索。

        真实请求体（抓包）：
            {"query":"", "pagination":{"size":12,"page":0},
             "filter_params":{}, "algorithm":1}

        返回里带游标：`next_pagination = {has_more, next_page, search_key, next_item_cursor}`
        —— 翻页要把 `search_key` 一起回传（服务端签名过，不能自己造）。
        """
        pag: dict = {"size": size, "page": page}
        if search_key:
            pag["search_key"] = search_key
        body = {"query": query, "pagination": pag,
                "filter_params": filter_params or {}, "algorithm": algorithm}
        # ⚠️ 真实请求里**没有** is_hot_api（文档说"强制含"，实测不加才通）
        #
        # 注意：**不再自动导航操作者的标签页**。早先 `ensure_marketplace_page()`
        # 会把他的标签页 goto 到 /affiliate/creator/search —— 那是干扰。
        # 需要切页时由调用方显式 `ensure_marketplace_page()`。
        #
        # `find` 是全站最挑剔的端点（要 SDK 完整签名 + 浏览器指纹块），
        # 且**间歇性** 98001004。`call()` 里那层"重载 fp 重试"不够，
        # 这里再加一层：每次失败都重新取 fp，最多 4 轮。
        # 让请求带上正确的页面上下文（走自有的静默页面，不碰操作者标签页）
        if not any(getattr(pg, "_dsh_quiet", False) for pg in self.ch._ctx.pages) \
                if getattr(self.ch, "_ctx", None) else True:
            self.ensure_find_page()
        last = {}
        for attempt in range(4):
            if attempt:
                self.load_fp()
                self.ch.base_query = dict(self._base_params())
                time.sleep(0.8 + attempt * 0.6)
            try:
                last = self.call("marketplace_find", body)
            except Exception as e:
                last = {"code": None, "message": str(e)[:80]}
            if isinstance(last, dict) and (last.get("code") == 0
                                           or last.get("creator_profile_list") is not None):
                return last
        return last

    def all_creators(self, *, query: str = "", pages: int = 3, size: int = 12,
                     filter_params: dict | None = None) -> list[dict]:
        """翻页拉达人列表（用返回的 search_key 续页）。"""
        out, page, sk = [], 0, None
        for _ in range(pages):
            r = self.find_creators(query=query, page=page, size=size,
                                   filter_params=filter_params, search_key=sk)
            lst = r.get("creator_profile_list") or []
            if not lst:
                break
            out += lst
            np = r.get("next_pagination") or {}
            if not np.get("has_more"):
                break
            page = np.get("next_page", page + 1)
            sk = np.get("search_key")
        return out

    def creator_profile(self, creator_oecuid: str) -> dict:
        """达人详情。

        ⚠️ 字段名是 **`creator_oec_id`**（带下划线），不是 `creator_oecuid`
        —— 写错就是 `98001004`。body 形状（抓包确认）：

            {"creator_oec_id": "<达人id>", "profile_types": [1]}

        返回 `creator_profile`（handle / nickname / bio / avatar / 各项指标）
        + `creator_connect_info`（联系方式可达性）。
        入口页面：`/affiliate/creator/detail?cid=<达人id>&pair_source=authorized`
        """
        r = self.call("marketplace_profile",
                      {"creator_oec_id": str(creator_oecuid), "profile_types": [1]})
        return r.get("creator_profile") or r.get("data") or r

    # 排行榜的 rank_list_meta 真实结构（抓包确认，缺一个字段就 98001004）
    #
    #   rank_type    : 榜单类型（1 = 综合）
    #   rank_period  : 周期（1 = 日？）
    #   rank_date    : "YYYY-MM-DD"（服务端会归一化到最新可用日期）
    #   indus_cate   : 行业类目，"All" 或具体类目
    #   content_type : 内容类型（1 = 全部）
    #
    # 入口页面：`/affiliate/creator/rankings`
    # 返回 `data.total` / `data.creator_rank_info_list`
    #   （rank_position / rank_score / follower_cnt / creator_handle）
    RANK_META = {"rank_type": 1, "rank_period": 1, "indus_cate": "All",
                 "content_type": 1}

    def creator_rank(self, *, size: int = 20, page: int = 1,
                     rank_date: str | None = None,
                     rank_list_meta: dict | None = None) -> dict:
        meta = dict(self.RANK_META)
        meta["rank_date"] = rank_date or time.strftime("%Y-%m-%d")
        if rank_list_meta:
            meta.update(rank_list_meta)
        return self.call("creator_rank",
                         {"rank_list_meta": meta, "size": size, "page": page})

    def rank_creators(self, *, pages: int = 2, size: int = 50,
                      indus_cate: str = "All") -> list[dict]:
        """翻页拉排行榜（每页最多 200 条 total）。"""
        out = []
        for pg in range(1, pages + 1):
            r = self.creator_rank(size=size, page=pg, rank_list_meta={"indus_cate": indus_cate})
            lst = ((r.get("data") or {}).get("creator_rank_info_list")) or []
            if not lst:
                break
            out += lst
            if len(lst) < size:
                break
        return out

    def wishlist_creators(self, *, query: str = "", size: int = 20) -> dict:
        return self.call("wishlist_search", {"request": {"size": size, "query": query}})

    def suggestions(self, text: str = "", *, size: int = 20) -> list:
        r = self.call("search_suggestions",
                      {"request": {"query": text, "sug_scene": 1, "size": size}})
        return ((r.get("data") or {}).get("sug_contents")) or []

    # ---- 邀约 / 定向计划 ----
    def groups(self, *, page: int = 1, size: int = 10, extra: dict | None = None) -> dict:
        """定向计划分页查询。

        ⚠️ 联盟侧分页字段是 **`cur_page` / `page_size`**（不是 `page`/`size`）。
        用错的字段名会得到 `400 binding: expr_path=page_size, cause=missing required parameter`。
        这两个名字是用绑定错误预言机逐个问出来的。
        """
        body = {"cur_page": page, "page_size": size}
        if extra:
            body.update(extra)
        return self.call("group_search", body)

    def group_detail(self, group_id: str) -> dict:
        return self.call("group_detail", {"invitation_group_id": str(group_id)})

    def group_creators(self, group_id: str, *, page: int = 1, size: int = 10) -> dict:
        return self.call("group_search_creator",
                         {"invitation_group_id": str(group_id),
                          "cur_page": page, "page_size": size})

    def group_general_config(self) -> dict:
        return self.call("group_general_cfg").get("data") or {}

    def check_text(self, text: str) -> dict:
        return self.call("group_text_check", {"text": text})

    # ---- 样品 / 商品 ----
    def sample_groups(self, *, tab: int = 10, page: int = 1, size: int = 50,
                      search_key: int = 1, search_type: int = 2, value: str = "",
                      order_key: int = 7, order_type: int = 2) -> dict:
        """寄样 / 样品申请列表。

        ⚠️ 缺 `tab` / `search_params` / `order_params` 一律 `98001004` ——
        这三个字段是抓包才拿到的，光试 `{cur_page,page_size}` 永远试不出来。

        真实 body（抓包确认）：
            {"tab":10,"cur_page":1,"page_size":50,
             "search_params":[{"search_key":1,"search_type":2,"value":""}],
             "order_params":[{"order_key":7,"order_type":2}]}

        返回 `{has_more, total_count, view_type, is_predict_fulfillment_rate}`。
        本店 `total_count=0`（还没样品申请），所以之前看着像接口坏了。
        入口页面：`/affiliate/sample/sample-request`
        """
        return self.call("sample_group_list", {
            "tab": tab, "cur_page": page, "page_size": size,
            "search_params": [{"search_key": search_key, "search_type": search_type,
                               "value": value}],
            "order_params": [{"order_key": order_key, "order_type": order_type}]})

    def product_selection(self, *, page: int = 1, size: int = 10, source: int = 0,
                          extra: dict | None = None) -> dict:
        """联盟选品列表（可发给达人的商品）。

        必填字段（绑定错误预言机问出来的）：`page_size` → `cur_page` → `source`。
        实测 `{"cur_page":1,"page_size":10,"source":0}` → code=0，`total_num=624`。
        """
        body = {"cur_page": page, "page_size": size, "source": source}
        if extra:
            body.update(extra)
        return self.call("product_selection", body)


    # ─────────── 定向计划：创建与加人（§30 从同行源码反解）───────────
    #
    # ⚠️ 三个必踩的坑：
    #   1. body 必须包一层 `{"invitation_group": {...}}` —— 发扁平字段必 98001004
    #   2. Content-Type 带 `; charset=utf-8`
    #   3. `target_commission` 是【百分比 ×100】的整数（15% → 1500）
    #   4. `end_time` 是【字符串形式的 epoch 毫秒】，不在合理区间时服务端纠到 now+7天

    # 联系字段码表（field 值）
    CONTACT_FIELDS = {"whatsApp": 6, "email": 7, "line": 41, "zalo": 42,
                      "facebook": 44, "telegram": 45, "phone": 46}

    @staticmethod
    def contacts_info(email: str = "") -> list[dict]:
        """`contacts_info` 模板 —— 7 个联系字段，值留空即不展示。"""
        return [
            {"key": "whatsApp", "title": "", "field": 6,  "value": "", "country_code": ""},
            {"key": "facebook", "title": "", "field": 44, "value": ""},
            {"key": "telegram", "title": "", "field": 45, "value": "", "country_code": ""},
            {"key": "line",     "title": "", "field": 41, "value": "", "country_code": ""},
            {"key": "zalo",     "title": "", "field": 42, "value": "", "country_code": ""},
            {"key": "email",    "title": "", "field": 7,  "value": email or "",
             "country_code": "US#1"},
            {"key": "phone",    "title": "", "field": 46, "value": "", "country_code": ""},
        ]

    @staticmethod
    def product_list(items: list[dict]) -> list[dict]:
        """`product_list` —— items 形如 [{"product_id":…, "commission_rate":15}]。

        ⚠️ `commission_rate` 传**百分比数值**（15 表示 15%），这里会 ×100
        变成服务端要的 `target_commission: 1500`。传小数（0.15）会差 100 倍。
        """
        out = []
        for it in items:
            rate = it.get("commission_rate", it.get("target_commission", 0))
            rate = float(rate)
            if rate <= 1:                       # 容忍误传小数
                rate *= 100
            row = {"product_id": str(it["product_id"]),
                   "target_commission": int(round(rate * 100))}
            if it.get("target_ads_commission") is not None:
                row["target_ads_commission"] = int(round(float(it["target_ads_commission"]) * 100))
            out.append(row)
        return out

    @staticmethod
    def creator_id_list(creator_ids) -> list[dict]:
        """`creator_id_list` —— 每个达人包一层 `base_info`。

        注意字段名：这里吃 **`creator_oec_id`**，而广场搜索返回的是 `creator_oecuid`。
        """
        return [{"base_info": {"creator_id": "", "nick_name": "",
                               "creator_oec_id": str(c)}} for c in creator_ids]

    @staticmethod
    def default_end_time(days: int = 7) -> str:
        """`end_time` 默认值 —— 字符串 epoch 毫秒（服务端规则：<=now+5min 会纠到 +7 天）。"""
        return str(int((time.time() + days * 86400) * 1000))

    def build_group_body(self, *, name: str, creator_ids, products: list[dict],
                         has_free_sample: bool = True,
                         is_free_sample_auto_review: bool = False,
                         end_time: str | None = None, message: str = "",
                         email: str = "",
                         delivery_requirements: dict | None = None) -> dict:
        """构造 `invitation_group/create` 的完整 body（含外层包装）。"""
        return {"invitation_group": {
            "name": name,
            "contacts_info": self.contacts_info(email),
            "free_sample_rule": {
                "has_free_sample": bool(has_free_sample),
                "is_free_sample_auto_review": bool(is_free_sample_auto_review),
                "sample_setting_type": 2 if is_free_sample_auto_review else 1,
            },
            "product_list": self.product_list(products),
            "creator_id_list": self.creator_id_list(creator_ids),
            "end_time": end_time or self.default_end_time(),
            "message": message,
            "delivery_requirements": delivery_requirements or {"content_option": 1},
        }}

    def create_group(self, *, name: str, creator_ids, products: list[dict],
                     apply: bool = False, **kw) -> dict:
        """创建定向计划。**写操作**，apply=False 只回放 body。"""
        body = self.build_group_body(name=name, creator_ids=creator_ids,
                                     products=products, **kw)
        if not apply:
            return {"dry_run": True, "would_post": body}
        r = self.call("group_create", body)
        try:
            from tk01_log import log_run
            log_run("create_group", target=str(name),
                    ok=(r.get("code") == 0),
                    params={"n_creators": len(list(creator_ids)),
                            "n_products": len(products)},
                    result={"plan_id": (((r.get("data") or {}).get("invitation") or {}).get("id")),
                            "code": r.get("code"), "message": str(r.get("message"))[:80]})
        except Exception:
            pass
        return r

    def group_creators_add(self, group_id: str, creator_ids, *, apply: bool = False) -> dict:
        """向已有定向计划补达人。**写操作**（本会话实测通过）。

        ⚠️ 字段名和 `create` **完全不同** —— 这是试了 9 个变体才试出来的：

            {"group_id": "<计划id>", "creator_ids": ["<达人id>", …]}

        - `group_id`      不是 `invitation_group_id`
        - `creator_ids`   是**扁平字符串数组**，不是 `creator_id_list` 那套双层 `base_info`

        响应：`{"data": {"success_cnt": n, "conflict_cnt": n, "invited_cnt": n}}`
        `conflict_cnt > 0` 表示该达人已在别的计划里冲突。
        """
        body = {"group_id": str(group_id), "creator_ids": [str(c) for c in creator_ids]}
        if not apply:
            return {"dry_run": True, "would_post": body}
        r = self.call("group_creators_add", body)
        try:
            from tk01_log import log_run
            log_run("creators_add", target=str(group_id), ok=(r.get("code") == 0),
                    params={"n_creators": len(body["creator_ids"])},
                    result={"data": (r.get("data") or {}), "code": r.get("code")})
        except Exception:
            pass
        return r


    # ─────────── 一条龙：广场捞人 → 过滤 → 建定向计划 ───────────
    #
    # 这条链路**不需要 `creators_add`** —— `create` 的 body 本来就带
    # `creator_id_list` 数组，上限 `max_creator_num`（本店 50）。
    # 只有"计划建好后再追加"才需要 creators_add，而那种情况直接新建计划即可。

    def scout_creators(self, *, query: str = "", want: int = 50,
                       min_followers: int = 0, pages: int = 6, size: int = 20,
                       exclude_collaborated: bool = False,
                       exclude_invited_90d: bool = True,
                       exclude_blocked: bool = True,
                       dedup: bool = True) -> list[dict]:
        """从达人广场捞人并按条件过滤。

        过滤字段（都来自 `marketplace/find` 的返回）：
          `follower_cnt`              粉丝数
          `has_collaborated`          是否已合作过
          `has_invited_before_90d`    90 天内是否已邀约过
          `is_creator_blocked_by_shop` 是否被本店拉黑

        `min_followers` **不会**像 §22 那样拿成功率当门槛 —— 这里是硬性业务条件，
        达不到的直接跳过（省名额），符合条件的按广场排序取前 `want` 个。
        """
        got: list[dict] = []
        seen: set[str] = set()
        for pg in range(pages):
            try:
                r = self.find_creators(query=query, page=pg, size=size)
            except Exception as e:
                print(f"    [scout] 第 {pg} 页失败: {str(e)[:70]}", flush=True)
                break
            lst = r.get("creator_profile_list") or []
            if not lst:
                break
            for c in lst:
                def g(k):
                    v = c.get(k)
                    return v.get("value") if isinstance(v, dict) else v
                cid = str(g("creator_oecuid") or "")
                if not cid or (dedup and cid in seen):
                    continue
                seen.add(cid)
                fol = int(g("follower_cnt") or 0)
                if fol < min_followers:
                    continue
                if exclude_collaborated and g("has_collaborated"):
                    continue
                if exclude_invited_90d and g("has_invited_before_90d"):
                    continue
                if exclude_blocked and g("is_creator_blocked_by_shop"):
                    continue
                got.append({"creator_oec_id": cid, "handle": str(g("handle") or ""),
                            "nickname": str(g("nickname") or ""),
                            "follower_cnt": fol,
                            "category": str(g("category") or ""),
                            "fulfillment_90d": g("creator_fulfillment_score_90d"),
                            "raw": c})
                if len(got) >= want:
                    return got
            np = r.get("next_pagination") or {}
            if not np.get("has_more"):
                break
        return got

    def invite_batch(self, *, name: str, creator_ids, products: list[dict],
                     apply: bool = False, **kw) -> dict:
        """一条龙：把捞到的达人一次性建进一个定向计划。

        `creator_ids` 超过 `max_creator_num`（本店 50）时**自动分桶**建多个计划，
        计划名加序号后缀。
        """
        limit = 50
        try:
            limit = int((self.invitation_limit() or {}).get("max_creator_num") or 50)
        except Exception:
            pass
        ids = [str(c) for c in creator_ids]
        chunks = [ids[i:i + limit] for i in range(0, len(ids), limit)] or [[]]
        out = {"limit_per_plan": limit, "n_creators": len(ids), "n_plans": len(chunks),
               "plans": []}
        for i, chunk in enumerate(chunks, 1):
            nm = name if len(chunks) == 1 else f"{name}-{i}"
            body = self.build_group_body(name=nm, creator_ids=chunk,
                                         products=products, **kw)
            if not apply:
                out["plans"].append({"name": nm, "n_creators": len(chunk),
                                     "dry_run": True, "would_post": body})
                continue
            try:
                r = self.call("group_create", body)
                gid = (((r.get("data") or {}).get("invitation") or {}).get("id"))
                out["plans"].append({"name": nm, "n_creators": len(chunk),
                                     "code": r.get("code"),
                                     "message": str(r.get("message"))[:60],
                                     "plan_id": gid,
                                     "share_url": r.get("share_short_url")})
            except Exception as e:
                out["plans"].append({"name": nm, "n_creators": len(chunk),
                                     "error": str(e)[:110]})
        if apply:
            try:
                from tk01_log import log_run
                log_run("invite_batch", target=name,
                        ok=all(p_.get("code") == 0 for p_ in out["plans"]),
                        params={"n_creators": len(ids), "n_products": len(products),
                                "limit_per_plan": limit},
                        result={"n_plans": out["n_plans"],
                                "plan_ids": [p_.get("plan_id") for p_ in out["plans"]]})
            except Exception:
                pass
        return out

    def group_detail(self, group_id: str) -> dict:
        """计划详情。body `{"invitation_group_id": "<字符串 id>"}` —— 实测通过。"""
        r = self.call("group_detail", {"invitation_group_id": str(group_id)})
        return ((r.get("data") or {}).get("invitation")) or r

    def terminate_group(self, group_id: str, *, apply: bool = False) -> dict:
        """终止定向计划（**写操作**）。"""
        body = {"invitation_group_id": str(group_id)}
        if not apply:
            return {"dry_run": True, "would_post": body}
        r = self.call("group_terminate", body)
        try:
            from tk01_log import log_run
            log_run("terminate_group", target=str(group_id), ok=(r.get("code") == 0),
                    result={"code": r.get("code"), "message": str(r.get("message"))[:60]})
        except Exception:
            pass
        return r


    # ─────────── 达人广场：让 app 自己发请求，我只接响应 ───────────
    #
    # ★ 这是唯一能拿到 `find` 数据的办法（§36/§37 实测结论）：
    #   服务端认的不是签名，是"这条请求是不是 app 自己的代码发的"。
    #   我的传输永远凑不齐 find 要求的 4 个签名，Worker/iframe 一律被判插件。
    #
    # 做法：点「发现达人」→ 滚动列表 → app 自己用 search_key 游标翻页 →
    #       用 `page.on("response")` 把每页响应接住。
    #   **完全不构造请求、不碰签名。**
    #
    # 实测：11 页 × 12 个 = 去重 132 个达人，全部 code=0。

    def harvest_creators(self, *, target_pages: int = 12, scroll_rounds: int = 40,
                         on_progress=None) -> list[dict]:
        """让页面自己去达人广场翻页，拦截响应收集达人。

        需要页面上有「发现达人」入口（`/affiliate/creator`）。
        会用 `page.on("response")` 接 `marketplace/find` 的响应。
        """
        from playwright.sync_api import sync_playwright
        self.ch._ensure()
        pages: list[dict] = []

        def _on_resp(r):
            try:
                if "marketplace/find" in r.url:
                    pages.append({"url": r.url[:200], "status": r.status, "body": r.text()})
            except Exception:
                pass

        pg = self.ch._page
        pg.on("response", _on_resp)
        # ① 点「发现达人」
        try:
            pg.evaluate("""(()=>{const e=[...document.querySelectorAll('a,li,div,span,button')]
              .filter(x=>(x.innerText||'').trim()==='发现达人' && x.getBoundingClientRect().width>0);
              if(e.length) e[0].click(); return e.length;})()""")
        except Exception:
            pass
        time.sleep(9)
        # ② 滚动促发翻页
        for i in range(scroll_rounds):
            before = len(pages)
            try:
                pg.evaluate("""(()=>{
                  const c=[...document.querySelectorAll('div')].filter(e=>{
                    const b=e.getBoundingClientRect();
                    return b.width>500 && b.height>300 && e.scrollHeight > e.clientHeight + 200;});
                  if(c.length){ c.sort((a,b)=>b.scrollHeight-a.scrollHeight);
                                c[0].scrollTop = c[0].scrollHeight; }
                  window.scrollTo(0, document.body.scrollHeight);
                })()""")
            except Exception:
                break
            time.sleep(3.0)
            if on_progress and len(pages) > before:
                on_progress(len(pages))
            if len(pages) >= target_pages:
                break

        # ③ 解析去重
        out, seen = [], set()
        for p_ in pages:
            try:
                j = json.loads(p_["body"])
            except Exception:
                continue
            for c in (j.get("creator_profile_list") or []):
                def g(k):
                    v = c.get(k)
                    return v.get("value") if isinstance(v, dict) else v
                uid = str(g("creator_oecuid") or "")
                if not uid or uid in seen:
                    continue
                seen.add(uid)
                out.append({"creator_oec_id": uid,
                            "handle": str(g("handle") or ""),
                            "nickname": str(g("nickname") or ""),
                            "follower_cnt": int(g("follower_cnt") or 0),
                            "category": str(g("category") or ""),
                            "fulfillment_90d": g("creator_fulfillment_score_90d"),
                            "has_collaborated": g("has_collaborated"),
                            "has_invited_before_90d": g("has_invited_before_90d"),
                            "is_blocked": g("is_creator_blocked_by_shop"),
                            "raw": c})
        try:
            pg.remove_listener("response", _on_resp)
        except Exception:
            pass
        return out

    # ---- 汇总 ----
    def overview(self) -> dict:
        """一次拉齐联盟中心的关键口径（给周报用）。"""
        out: dict = {}
        for key, fn in (("account", self.account),
                        ("invitation_limit", self.invitation_limit),
                        ("crm_upper_limit", self.crm_upper_limit),
                        ("group_general_config", self.group_general_config)):
            try:
                out[key] = fn()
            except Exception as e:
                out[key] = {"_error": str(e)[:120]}
        try:
            out["cmp_filter"] = self.cmp_filter()
        except Exception as e:
            out["cmp_filter"] = {"_error": str(e)[:120]}
        try:
            r = self.find_creators(size=1)
            out["marketplace_total_hint"] = {
                "has_more": (r.get("next_pagination") or {}).get("has_more"),
                "keys": sorted(r.keys()),
            }
        except Exception as e:
            out["marketplace_total_hint"] = {"_error": str(e)[:120]}
        return out


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok Shop 联盟中心 API 客户端")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--gap", type=float, default=0.8)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("account"); sub.add_parser("menu"); sub.add_parser("limits")
    sub.add_parser("options"); sub.add_parser("overview")
    sub.add_parser("groups"); sub.add_parser("samples")
    p = sub.add_parser("creators"); p.add_argument("--query", default="")
    p.add_argument("--pages", type=int, default=2); p.add_argument("--size", type=int, default=12)
    p.add_argument("--dump")
    p = sub.add_parser("profile"); p.add_argument("creator_oecuid")
    p = sub.add_parser("rank"); p.add_argument("--size", type=int, default=20)
    p = sub.add_parser("suggestions"); p.add_argument("text", nargs="?", default="")
    p = sub.add_parser("scout"); p.add_argument("--query", default="")
    p.add_argument("--want", type=int, default=20); p.add_argument("--min-followers", type=int, default=0)
    p.add_argument("--pages", type=int, default=5)
    p = sub.add_parser("invite"); p.add_argument("--name", required=True)
    p.add_argument("--want", type=int, default=20); p.add_argument("--min-followers", type=int, default=0)
    p.add_argument("--query", default=""); p.add_argument("--product-ids", default="")
    p.add_argument("--commission", type=float, default=15.0)
    p.add_argument("--yes", action="store_true")
    p = sub.add_parser("detail"); p.add_argument("group_id")
    p = sub.add_parser("terminate"); p.add_argument("group_id"); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("harvest"); p.add_argument("--pages", type=int, default=12)
    p.add_argument("--min-followers", type=int, default=0); p.add_argument("--dump",
        default="notes/aff_creators_harvested.json")
    p = sub.add_parser("addcreators"); p.add_argument("group_id")
    p.add_argument("--creators", required=True, help="逗号分隔的达人 id")
    p.add_argument("--yes", action="store_true")
    sub.add_parser("endpoints")

    a = ap.parse_args()
    if a.cmd == "endpoints":
        print(f"共 {len(ENDPOINTS)} 个端点:")
        for n, (m, p) in sorted(ENDPOINTS.items(), key=lambda x: x[1][1]):
            print(f"  {m:5} {p:74} {n}")
        return

    A = AffiliateClient(port=a.port, gap=a.gap)
    try:
        if a.cmd == "account":
            print(json.dumps(A.account(), ensure_ascii=False, indent=1)[:2500])
        elif a.cmd == "menu":
            for m in A.menu():
                print(f"  {str(m.get('id')):22} {str(m.get('path')):34} "
                      f"{m.get('default_name') or m.get('starling_key')}")
        elif a.cmd == "limits":
            print("邀约上限:", json.dumps(A.invitation_limit(), ensure_ascii=False))
            print("CRM 上限:", json.dumps(A.crm_upper_limit(), ensure_ascii=False))
        elif a.cmd == "options":
            o = A.options()
            for t, v in sorted(o.items(), key=lambda x: str(x[0])):
                lst = (v or {}).get("option_list") or []
                head = ", ".join(str(x.get("name")) for x in lst[:8])
                print(f"  type={t:4} {len(lst):>4} 项   {head[:90]}")
        elif a.cmd == "overview":
            print(json.dumps(A.overview(), ensure_ascii=False, indent=1)[:3000])
        elif a.cmd == "creators":
            rows = A.all_creators(query=a.query, pages=a.pages, size=a.size)
            print(f"达人 {len(rows)} 行")
            for c in rows[:30]:
                uid = (c.get("creator_oecuid") or {}).get("value") if isinstance(
                    c.get("creator_oecuid"), dict) else c.get("creator_oecuid")
                nick = (c.get("nickname") or c.get("nick_name") or
                        (c.get("creator_profile") or {}).get("nickname") or "")
                print(f"  {str(uid):22} {str(nick)[:34]}")
            if a.dump:
                Path(a.dump).write_text(json.dumps(rows, ensure_ascii=False, indent=1))
                print(f"→ {a.dump}")
        elif a.cmd == "profile":
            print(json.dumps(A.creator_profile(a.creator_oecuid),
                             ensure_ascii=False, indent=1)[:3000])
        elif a.cmd == "rank":
            rows = A.rank_creators(pages=1, size=min(a.size, 50))
            print(f"榜单 {len(rows)} 行")
            for c in rows[:30]:
                L = c.get("creator_handle") or ""
                print(f"  #{str(c.get('rank_position')):>4}  score={c.get('rank_score')}  "
                      f"粉丝={c.get('follower_cnt')}  {str(L)[:30]}")
        elif a.cmd == "suggestions":
            for s in A.suggestions(a.text):
                print(f"  {json.dumps(s, ensure_ascii=False)[:120]}")
        elif a.cmd == "groups":
            print(json.dumps(A.groups(), ensure_ascii=False, indent=1)[:2500])
        elif a.cmd == "scout":
            rows = A.scout_creators(query=a.query, want=a.want,
                                    min_followers=a.min_followers, pages=a.pages)
            print(f"捞到 {len(rows)} 个达人")
            for c in rows[:30]:
                print(f"  {c['creator_oec_id']:22} {c['handle'][:22]:24} "
                      f"粉丝={c['follower_cnt']:>8}  {c['category'][:16]}  履约={c['fulfillment_90d']}")
        elif a.cmd == "invite":
            rows = A.scout_creators(query=a.query, want=a.want,
                                    min_followers=a.min_followers)
            print(f"捞到 {len(rows)} 个达人")
            if not rows:
                print("  没捞到，退出"); return
            pids = [x for x in a.product_ids.split(",") if x]
            if not pids:
                sel = A.product_selection(page=1, size=5)
                pids = [str(p.get("product_id")) for p in (sel.get("products") or [])][:3]
                print(f"  未指定商品，自动取选品列表前 {len(pids)} 个")
            products = [{"product_id": p, "commission_rate": a.commission} for p in pids]
            r = A.invite_batch(name=a.name,
                               creator_ids=[c["creator_oec_id"] for c in rows],
                               products=products, apply=a.yes)
            print(f"  上限 {r['limit_per_plan']}/计划  {r['n_creators']} 达人 → {r['n_plans']} 个计划")
            for p in r["plans"]:
                if p.get("dry_run"):
                    print(f"  [dry] {p['name']}  {p['n_creators']} 达人")
                else:
                    print(f"  {p['name']}  code={p.get('code')} plan_id={p.get('plan_id')} "
                          f"{p.get('message') or p.get('error','')[:60]}")
        elif a.cmd == "detail":
            print(json.dumps(A.group_detail(a.group_id), ensure_ascii=False, indent=1)[:2500])
        elif a.cmd == "harvest":
            rows = A.harvest_creators(target_pages=a.pages,
                                      on_progress=lambda n: print(f"    接住第 {n} 页", flush=True))
            if a.min_followers:
                rows = [c for c in rows if c["follower_cnt"] >= a.min_followers]
            print(f"共 {len(rows)} 个达人")
            for c in rows[:30]:
                flag = "已合作" if c.get("has_collaborated") else ("90天邀过" if c.get("has_invited_before_90d") else "")
                print(f"  {c['creator_oec_id']:22} {c['handle'][:22]:24} "
                      f"粉丝={c['follower_cnt']:>8}  {flag}")
            Path(a.dump).write_text(json.dumps(rows, ensure_ascii=False, indent=1))
            print(f"→ {a.dump}")
        elif a.cmd == "addcreators":
            ids=[x for x in a.creators.split(",") if x]
            r=A.group_creators_add(a.group_id, ids, apply=a.yes)
            if a.yes:
                d=(r.get("data") or {})
                print(f"  code={r.get('code')}  成功={d.get('success_cnt')} "
                      f"冲突={d.get('conflict_cnt')} 已邀={d.get('invited_cnt')}")
            else:
                print(json.dumps(r, ensure_ascii=False, indent=1)[:400])
        elif a.cmd == "terminate":
            r = A.terminate_group(a.group_id, apply=a.yes)
            print(json.dumps(r, ensure_ascii=False, indent=1)[:600] if not a.yes
                  else f"code={r.get('code')} {r.get('message')}")
        elif a.cmd == "samples":
            print(json.dumps(A.sample_groups(), ensure_ascii=False, indent=1)[:2500])
    finally:
        A.close()


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
