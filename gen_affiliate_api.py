#!/usr/bin/env python3
"""生成 AFFILIATE_API.md —— 达人联盟全量接口手册。

数据源：
  notes/api_inventory/enriched.json   从联盟前端 46 个 bundle 抽取的路径 + HTTP 方法
  tk01_affiliate.py 的 ENDPOINTS 表   我们已接入的
  VERIFIED 集合                       本会话/主文档有 code=0 直接证据的
"""
import re, json, pathlib, collections

HERE = pathlib.Path(__file__).resolve().parent
rows = json.load(open(HERE / "notes/api_inventory/enriched.json", encoding="utf-8"))

OURS = {}
src = (HERE / "tk01_affiliate.py").read_text(encoding="utf-8")
tbl = re.search(r"^ENDPOINTS = \{(.*?)^\}", src, re.S | re.M).group(1)
for m in re.finditer(r'"([a-z_0-9]+)":\s*\("(GET|POST|PUT|PATCH|DELETE)",\s*"([^"]+)"\)', tbl):
    OURS[m.group(3)] = (m.group(2), m.group(1))
for f in ("tk01_im.py", "tk01_opportunity.py", "tk01_promo_client.py", "tk01_im_track.py"):
    s = (HERE / f).read_text(encoding="utf-8")
    for m in re.finditer(r'"(/api/v[0-9][A-Za-z0-9_/\-]*)"', s):
        OURS.setdefault(m.group(1), ("?", f.replace(".py", "")))

VERIFIED = set("""
/api/v1/affiliate/menu
/api/v1/affiliate/account/info
/api/v1/affiliate/account/info_v2
/api/v1/affiliate/config
/api/v1/affiliate/grayscale_strategy/check
/api/v1/affiliate/resource/list/get
/api/v1/affiliate/lux/invitation/available_list
/api/v1/affiliate/lux/creator/auth_profiles
/api/v1/affiliate/open_collaboration/opt_in/card/get
/api/v1/affiliate/partner/invite/creator/batch/create
/api/v1/affiliate/partner/invite/creator/mget
/api/v1/affiliate/product_selection/list
/api/v1/affiliate/sample/group/list
/api/v1/common/cdn_rule
/api/v1/oec/affiliate/creator/marketplace/find
/api/v1/oec/affiliate/creator/marketplace/option
/api/v1/oec/affiliate/creator/marketplace/profile
/api/v1/oec/affiliate/creator/marketplace/4partner/find
/api/v1/oec/affiliate/creator/marketplace/4partner/option
/api/v1/oec/affiliate/cmp/creator/rank/list/get
/api/v1/oec/affiliate/cmp/filter
/api/v1/oec/affiliate/cmp/contact_types
/api/v1/oec/affiliate/cmp/contact
/api/v1/oec/affiliate/seller/feature_control
/api/v1/oec/affiliate/seller/wish_list/search/creator
/api/v1/oec/affiliate/seller/invitation_group/invitation/limit
/api/v1/oec/affiliate/seller/invitation_group/general/config
/api/v1/oec/affiliate/seller/invitation_group/search
/api/v1/oec/affiliate/seller/invitation_group/detail
/api/v1/oec/affiliate/seller/invitation_group/create
/api/v1/oec/affiliate/seller/invitation_group/update
/api/v1/oec/affiliate/seller/invitation_group/creators_add
/api/v1/oec/affiliate/seller/invitation_group/terminate
/api/v1/oec/affiliate/seller/invitation_group/conflict_check
/api/v1/oec/affiliate/seller/invitation_group/conflict_check/resolve
/api/v1/oec/affiliate/seller/invitation_group/sensitive_text_check
/api/v1/oec/affiliate/seller/invitation_group/product_creator_relation
/api/v1/oec/affiliate/crm/creator/upper_limit/get
/api/v1/oec/affiliate/seller/im/get/token
/api/v1/im/shop_creator/shop/user/token/get
/api/v1/im/shop_creator/shop/conversation/search
/api/v1/insights/affiliate/creator/search/suggestions
""".split())


def mark(p):
    return "✅" if p in VERIFIED else ("◐" if p in OURS else "○")


def segs(p):
    """剥掉 /api/vN/、oec/、affiliate/ 三层前缀，剩下的第一段才是业务域。"""
    s = re.sub(r"^/api/v\d+/", "", p)
    s = re.sub(r"^oec/", "", s)
    s = re.sub(r"^affiliate/", "", s)
    return [x for x in s.split("/") if x]


# 分组规则：(组名, 判定函数) —— 顺序即优先级
def g_account(s):
    if s[0] in ("seller", "creator") and len(s) > 1 and s[1] in ("shop", "search", "dismiss"):
        return True
    return s[0] in ("menu", "account", "config", "resource", "has_agent", "log_out_agent",
                    "approve", "diagnosis", "platform", "shop_setting", "violation",
                    "request", "request_status", "new_request", "name_list", "shop",
                    "scopemetas")


def g_home(s):
    return s[0] in ("homepage", "banner", "guidance_page", "guide", "announcement",
                    "errorpage", "promotion_position", "backend")


def g_infra(s):
    return bool(s) and s[0] in ("common", "i18n_conf", "sentry_verify", "bs", "sitebuilder",
                                "feelgood", "user", "reverse", "media")


def g_marketplace(s):
    if s[0] == "lux" and len(s) > 1 and s[1] == "creator":
        return True
    return (s[0] in ("creator_marketplace", "creator_application", "creator_data") or
            (s[0] == "creator" and len(s) > 1 and s[1] in
             ("marketplace", "search", "detail", "rankings", "vertical-list", "vertical",
              "settings", "config", "profile")))


def g_invite(s):
    if s[0] == "seller" and len(s) > 1 and s[1] in ("invitation_group", "invitation",
                                                    "previous_invitation", "effective_time"):
        return True
    if s[0] == "creator" and len(s) > 1 and s[1] == "invitation":
        return True
    if s[0] == "lux" and len(s) > 1 and s[1] in ("invitation",):
        return True
    if s[0] == "lux" and len(s) > 2 and s[1] == "plan" and s[2].startswith("target_plan"):
        return True
    if s[0] == "lux" and len(s) > 2 and s[1] == "plan" and s[2] == "creator":
        return True
    if s[0] in ("target_plan", "plan", "plan_detail", "plan_status", "shop_plan",
                "meta_plan", "sub_plan", "campaign", "collaboration", "creator"):
        return True
    if s[0] == "collaboration" and len(s) > 1 and s[1] == "target-invitation":
        return True
    return False


def g_open(s):
    if s[0] in ("open_collaboration", "open_plan", "auction_stock"):
        return True
    if s[0] == "collaboration" and len(s) > 1 and s[1] in ("open-collaboration",
                                                           "auction-stock", "auction"):
        return True
    return False


def g_sample(s):
    if s[0] == "opt_in" and len(s) > 1 and s[1] == "sample":
        return True
    return s[0] == "sample" or (s[0] == "lux" and len(s) > 1 and s[1] == "sample")


def g_crm(s):
    if s[0] in ("crm", "crm_toc", "relation", "master", "review", "assets"):
        return True
    if s[0] == "seller" and len(s) > 1 and s[1] in ("wish_list", "contact_info", "quota",
                                                    "creator_manage", "block_creator"):
        return True
    return bool(re.search(r"creator-management|creator_manage", "/".join(s)))


def g_msg(s):
    if s[0] in ("notification", "im", "message", "broadcast", "channel"):
        return True
    if s[0] in ("seller", "creator") and len(s) > 1 and s[1] == "im":
        return True
    if s[0] == "lux" and len(s) > 1 and s[1] == "notification":
        return True
    return bool(re.search(r"im_messages|/im/|notification", "/".join(s)))


def g_product(s):
    if s[0] in ("product_selection", "product", "product_category", "commission_unique",
                "recommend_commission", "suggest_commission", "shoppable_photo_discount"):
        return True
    if s[0] == "lux" and len(s) > 1 and s[1] in ("product",):
        return True
    if s[0] == "lux" and len(s) > 2 and s[1] == "plan" and s[2].startswith("product"):
        return True
    if s[0] == "seller" and len(s) > 1 and s[1] == "shoppable_photo_discount":
        return True
    return False


def g_data(s):
    return s[0] in ("cmp", "compass", "insights", "statistics", "analytics",
                    "dashboard", "rank", "rankings", "performance", "export_history",
                    "export_link") or "/".join(s).startswith(("insights/",))


def g_order(s):
    return (s[0] in ("orders", "order", "settle", "payout", "finance", "invoice",
                     "withhold_tax", "export_order", "export_order_task",
                     "export_order_v2") or
            bool(re.match(r"^(export_order|orders?$|settle|payout|finance|invoice)", s[0])))


def g_partner(s):
    return s[0] == "partner" or (s[0] == "lux" and len(s) > 1 and s[1] == "partner")


def g_task(s):
    return bool(re.search(r"task|bulk|batch|merge|adcode|keyword|automation|tag",
                          "/".join(s)))


GROUPS = [
    ("1. 账号 / 网关 / 配置 / 平台设置", g_account),
    ("2. 首页 / 平台运营位 / 公告 / 引导", g_home),
    ("3. 达人广场 / 达人搜索 / 达人画像", g_marketplace),
    ("4. 定向计划 / 达人邀约（核心业务）", g_invite),
    ("5. 公开合作 / 竞价库存", g_open),
    ("6. 样品寄样", g_sample),
    ("7. 达人管理 / CRM / 关系 / 名单", g_crm),
    ("8. 消息 / 站内 IM / 通知", g_msg),
    ("9. 商品 / 选品 / 佣金", g_product),
    ("10. 排行榜 / 数据 / 报表 / 导出", g_data),
    ("11. 订单 / 结算 / 税务", g_order),
    ("12. Partner / MCN", g_partner),
    ("13. 基础设施 / 媒体上传 / i18n / 风控 / 其他", lambda s: True),
]

groups = collections.OrderedDict((g, []) for g, _ in GROUPS)
for r in rows:
    s = segs(r["path"])
    for name, fn in GROUPS:
        if fn(s):
            groups[name].append(r)
            break

L = []
W = L.append
n_v = sum(1 for r in rows if mark(r["path"]) == "✅")
n_o = sum(1 for r in rows if mark(r["path"]) == "◐")
n_x = sum(1 for r in rows if mark(r["path"]) == "○")

W("# 达人联盟（Affiliate）API 全量接口手册")
W("")
W("> **来源**：从联盟中心**自己的前端 bundle** 抽取全部路径字面量，再与本地已验证集合交叉比对。")
W(f"> 数据源 `notes/aff_js/`（46 个 bundle / 33 MB）、`notes/api_inventory/enriched.json`。")
W("")
W("| 标记 | 含义 |")
W("|---|---|")
W("| ✅ | **实测通过** —— 本会话或主文档有 `code=0` 的直接证据，请求参数已知 |")
W("| ◐ | 已接入 `tk01_affiliate.py` 等客户端，报文格式已知，但未单独跑过验证 |")
W("| ○ | 前端 bundle 中存在，尚未接入 |")
W("")
W(f"**共 {len(rows)} 个接口** — ✅ {n_v} / ◐ {n_o} / ○ {n_x}（✅ 是**在这 564 个之内**的统计；")
W(f"我们累计实测通过 42 个，多出的几个不在这个 bundle 列表里，见附 A）。")
W(f"能定出 HTTP 方法的 {sum(1 for r in rows if r['method'] != '?')} 个"
  f"（**POST {sum(1 for r in rows if r['method'] == 'POST')}** / "
  f"GET {sum(1 for r in rows if r['method'] == 'GET')}）。")
W("")
W("> HTTP 方法的取法：窗口 = [本路径字面量结束, 下一个字面量开始)，只在这一段里找 `method:\"…\"`；")
W("> 实测过的 42 个用实测方法覆盖推测值，其余取不到记 `?`。")
W("> `/oec/` 族几乎全是 POST —— 这是它和旧 `/api/v1/affiliate/*` 族最大的手感差别。")
W("")
W("---")
W("")
W("## 0. 总览")
W("")
W("### 0.1 域")
W("")
W("| 用途 | 域 | 说明 |")
W("|---|---|---|")
W("| 联盟中心（主） | `affiliate.tiktokshopglobalselling.com` | **两套路径族都在这个域上** |")
W("| 站内 IM（私有 protobuf） | `oec-im-tt-sg.tiktokglobalshopv.com/` **动态** | 由 `/api/v1/im/shop_creator/shop/user/token/get` 返回，见主文档 §40 |")
W("| MCN / Partner | `api-partner-va.tiktokshop.com` | `partner_info` 等 |")
W("")
W("### 0.2 ★ 两套路径族（行为完全不同，别混）")
W("")
W("| 路径族 | 网关 | 实测特征 |")
W("|---|---|---|")
W("| `/api/v1/affiliate/*` | 旧网关 | 参数直给、多为 `GET`；响应里 `region` 字段正常 |")
W("| `/api/v1/oec/affiliate/*` | 新网关 | 多为 `POST`；**缺 `oec_region` + 浏览器指纹块一律 `98001004`，且 `region:\"\"`** |")
W("")
W("`98001004` 是双关码：既是**参数错**也是**签名缺**。判据就是看响应里的 `region` 是不是空串。")
W("")
W("### 0.3 `/oec/` 族请求必备 query")
W("")
W("```")
W("user_language, aid=6556, app_name=i18n_ecom_alliance, device_id,")
W("oec_region=VN, oec_seller_id=<seller_id>,")
W("fp, device_platform=web, screen_width, screen_height, browser_*, timezone_name")
W("```")
W("")
W("17 个业务参数 + 4 个签名参数（`msToken` / `X-Bogus` / `X-Gnarly` / `X-Tts-Oec-Bsid`）。")
W("**签名只能由页面自己的 `byted_acrawler.frontierSign` 产生** —— 见主文档 §36 / §37。")
W("")
W("### 0.4 编码")
W("")
W("| 编码 | 用途 | 端点 |")
W("|---|---|---|")
W("| JSON | 绝大多数 | `Content-Type: application/json; charset=utf-8` |")
W("| **protobuf** | 站内 IM | `Content-Type: application/x-protobuf`，见主文档 §40 |")
W("| multipart | 图片 / 主题文件上传 | `affiliate/lux/image/*`、`affiliate/lux/screenshot` |")
W("")
W("### 0.5 分页字段名按族不同（踩过的）")
W("")
W("| 接口族 | 分页字段 |")
W("|---|---|")
W("| 定向计划 `invitation_group/search` | `cur_page` / `page_size` |")
W("| 达人广场 `marketplace/find` | `next_pagination.search_key`（**服务端签名游标，不能自造**） |")
W("| 排行榜 `cmp/creator/rank/list/get` | `rank_list_meta` 块 |")
W("| 商品机会（非联盟） | `page_number` / `page_size` |")
W("")
W("---")
W("")
for name, items in groups.items():
    if not items:
        continue
    items = sorted(items, key=lambda r: (mark(r["path"]) != "✅",
                                         mark(r["path"]) != "◐", r["path"]))
    nv = sum(1 for r in items if mark(r["path"]) == "✅")
    W(f"## {name}")
    W("")
    W(f"*{len(items)} 个 · ✅ {nv}*")
    W("")
    W("| | 方法 | 路径 | 本地实现 |")
    W("|---|---|---|---|")
    for r in items:
        p = r["path"]
        impl = f"`{OURS[p][1]}`" if p in OURS else ""
        W(f"| {mark(p)} | `{r['method']}` | `{p}` | {impl} |")
    W("")

W("---")
W("")
W("## 附 A.0 ★ 值得优先开荒的未接入接口（按主题）")
W("")
W("这些是 ✅/◐ 之外、且直接补业务闭环的。挑的都是路径语义明确的。")
W("")
SEED = [
    ("批量私信 / IM 群发", r"bulk-im|im_messages/batch_send|im/product/list|affiliate/crm/im|notification/im"),
    ("样品全流程（54 个接口没人碰）", r"affiliate/(lux/)?sample|opt_in/sample"),
    ("达人 CRM / 名单 / 标签 / 拉黑", r"affiliate/(crm|crm_toc)/|creator_manage|/tag|block_creator|wish_list|relation/"),
    ("订单 / 业绩 / 导出", r"export_order|affiliate/orders|statistic|performance|product_performance"),
    ("达人资产 / 素材库 / 配额", r"affiliate/assets"),
    ("活动 Campaign（另一套邀约体系）", r"affiliate/campaign/"),
    ("MCN / Partner 域", r"affiliate/partner/"),
    ("公开合作 / 竞价库存", r"open_collaboration|open_plan|auction_stock|collaboration/open"),
    ("商品 / 佣金 / 选品", r"lux/plan/product|lux/product|commission|product_selection|product_category|opportunity_product"),
    ("达人画像 / 授权", r"lux/creator|creator/profile/|marketplace/creator/profile|review/creator"),
]
for title, pat in SEED:
    hit = [r for r in rows if re.search(pat, r["path"], re.I)
           and mark(r["path"]) == "○"]
    if not hit: continue
    W(f"### {title}（{len(hit)} 个未接入）")
    W("")
    for r in sorted(hit, key=lambda x: x["path"])[:14]:
        W(f"- `{r['method']}` `{r['path']}`")
    if len(hit) > 14:
        W(f"- …还有 {len(hit) - 14} 个，见对应分组表")
    W("")

W("---")
W("")
W("## 附 A. 已打通接口的关键参数（速查）")
W("")
W("详见 [TIKTOK_PROMOTION_API.md](.work/adfly/TIKTOK_PROMOTION_API.md) 各节。")
W("")
W("| 接口 | 请求要点 | 响应要点 | 主文档 |")
W("|---|---|---|---|")
W("| `/api/v1/affiliate/menu` | `GET` 无参 | 20 条路由，导航表来源 | §29 |")
W("| `/api/v1/affiliate/account/info_v2` | `GET` | 店铺/账号 | §25 |")
W("| `.../seller/invitation_group/invitation/limit` | `GET` | `{max_creator_num:50,max_product_num:100}` | §30 |")
W("| `.../seller/invitation_group/search` | `POST {\"cur_page\":1,\"page_size\":10}` | `data.invitation_list[]`（**不是** `invitation_groups`） | §41.2 |")
W("| `.../seller/invitation_group/detail` | `POST {\"invitation_group_id\":\"<字符串>\"}` | `data.invitation.creator_id_list[]`（**不是** `invitation_group`） | §41.2 |")
W("| `.../seller/invitation_group/create` | `POST {\"invitation_group\":{...}}` **必须包一层** | `data.invitation.id` | §30 / §31 |")
W("| `.../seller/invitation_group/update` | `POST {\"invitation\":{...}}` 外层键名不同 | — | §30 |")
W("| `.../seller/invitation_group/creators_add` | `POST {\"group_id\":...,\"creator_ids\":[...]}` | `{success_cnt,conflict_cnt,invited_cnt}` | §34 |")
W("| `.../seller/invitation_group/terminate` | `POST {\"invitation_group_id\":...}` | — | §31 |")
W("| `.../seller/invitation_group/invitation/limit` | `GET` | 邀约上限 | §30 |")
W("| `/api/v1/oec/affiliate/crm/creator/upper_limit/get` | `GET` | `{total_limit:30000,…}` | §25 |")
W("| `.../creator/marketplace/find` | **必须由 app 自己发起**（4 个签名） | 11 页 × 12 = 132 达人 | §36 / §37 / §38 |")
W("| `.../creator/marketplace/option` | `POST` 筛选器 | brands 400 / cats 25 / price 5 / lang 2 | §28 |")
W("| `.../creator/marketplace/profile` | `POST {\"creator_oec_id\":…,\"profile_types\":[1]}` | 达人画像 | §28 |")
W("| `.../cmp/creator/rank/list/get` | `rank_list_meta` = `{rank_type:1,rank_period:1,rank_date:\"YYYY-MM-DD\",indus_cate:\"All\",content_type:1}` | 榜单 | §28 |")
W("| `.../cmp/filter` | `POST` | 榜单筛选器 | §28 |")
W("| `.../cmp/contact_types` + `/cmp/contact` | `POST` | 联系方式 | §28 |")
W("| `.../seller/feature_control` | `POST` | 功能开关 | §25 |")
W("| `.../seller/wish_list/search/creator` | `POST` | 收藏夹里的达人 | §28 |")
W("| `/api/v1/affiliate/product_selection/list` | `POST` `cur_page`/`page_size`/`source` | `total_num=624` | §28 |")
W("| `/api/v1/affiliate/sample/group/list` | `POST tab`/`search_params`/`order_params` | 样品组 | §28 |")
W("| `/api/v1/affiliate/lux/creator/auth_profiles` | `POST` | 达人授权画像 | §28 |")
W("| `/api/v1/affiliate/open_collaboration/opt_in/card/get` | `POST` | 平台运营位 | §25 |")
W("| `/api/v1/im/shop_creator/shop/user/token/get` | `GET` | IM token + **动态 api_url** | §40.1 |")
W("| `/api/v1/oec/affiliate/seller/im/get/token` | `GET` | 同上，备选，**`user` 字段名不同** | §40.1 |")
W("| `/api/v1/insights/affiliate/creator/search/suggestions` | `POST` | 搜索联想 | §28 |")
W("")
W("### 站内 IM（第二套协议，见 §40）")
W("")
W("| cmd | 路径 | 作用 |")
W("|---|---|---|")
W("| 200 | `{api_url}v2/message/get_by_user` | **拉会话/消息流（全量）** |")
W("| 203 | `{api_url}v2/message/get_by_user_init` | 初始化游标（只回小增量窗口） |")
W("| 301 | `{api_url}v1/message/get_by_conversation` | 会话内消息 |")
W("| 100 | `{api_url}v1/message/send` | 发消息 |")
W("| 604 | `{api_url}v3/conversation/mark_read` | 标记已读 |")
W("| 2000 | `{api_url}v3/conversation/get_read_index` | 读位置 |")
W("| 2001 | `{api_url}v3/conversation/get_min_index` | 最小 index |")
W("| — | `{api_url}api/v1/im/conversation/create` | **建会话（JSON）** |")
W("| — | `{api_url}api/v1/im/search/search_conversation_by_users` | **按用户名搜会话（JSON）** |")
W("")
W("## 附 B. 怎么自己续抓（bundle 更新后重跑）")
W("")
W("```bash")
W("# 1. 从【已打开的】联盟页读资源清单（只读：不导航、不新建页、不抢焦点）")
W("nohup python3 notes/aff_js_list.py > notes/aff_js_list.out 2>&1 &")
W("")
W("# 2. 下载 bundle（静态 CDN，走本地代理 127.0.0.1:7890，TLS MITM 要 -k）")
W("#    46 个 / 33 MB，清单见 notes/aff_js_manifest.json")
W("")
W("# 3. 抽路径 + 方法 → notes/api_inventory/enriched.json")
W("nohup python3 extract_affiliate_paths.py")
W("")
W("# 4. 重新生成本手册")
W("python3 gen_affiliate_api.py")
W("```")
W("")
W("**抓取的三个坑**：")
W("")
W("1. 路径是**拼接**的，不能整串 grep：")
W("   `\"\".concat(this.uriPrefix, \"/api/v\").concat(e.version || \"1\", \"/oec/affiliate/xxx\")`")
W("   → 只能抓**尾部字面量** `/oec/...`，版本从 `version || \"N\"` 取。")
W("2. 方法窗口要看 `[本字面量, 下一个字面量)`，放宽到固定 400 字符会串到下一个调用的 method。")
W("3. `ok`/`region` 之类的短串不要当路径 —— 长度阈值 >= 6 且必须含 `/`。")
W("")
W("**主 bundle 位置**：")
W("")
W("| bundle | 大小 | 内容 |")
W("|---|---|---|")
W("| `.../goofy-sg/gftar/i18n/ecom_alliance/creator_submodule_global/1.0.0.734/index.js` | **16.7 MB** | 达人子模块，达人广场 / 邀约 / 样品 绝大部分接口在这 |")
W("| `.../oec-magellan-sg/i18n/ecom/alliance/seller/static/js/main.91b51ba4.js` | 1.0 MB | 主应用路由 |")
W("| `.../apps/message-feedback/*/im-modal.*.js` | 108 KB | IM 弹窗 |")
W("")

(HERE / "AFFILIATE_API.md").write_text("\n".join(L), encoding="utf-8")
print(f"AFFILIATE_API.md: {len(L)} 行 / {len(rows)} 接口")
for g, it in groups.items():
    if it:
        print(f"  {len(it):>4}  {g}")
