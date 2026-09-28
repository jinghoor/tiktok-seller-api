"""结构化辅助层:把高频工作流封装成不容易拼错的函数。

模块方法(modules/*.py)是 1:1 映射接口的薄封装,够灵活但要求调用方自己拼
payload —— 例如报表要 {"order_info":..., "fields":[...],"start_date":...}。
这里把常用的几类封起来,参数有默认值、字段名有校验。

    from adfly_api.helpers import (
        gmv_max_create_payload, gmv_max_edit, report_body, export_report,
        find_gmv_max_ready_account, bc_auth_link, wallet_balances,
    )
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence

# ---- 枚举(GMVmax 相关的服务端常量,取自 bundle 与实测响应) ----

SHOPPING_ADS_TYPE = "PRODUCT"
PRODUCT_SPECIFIC_TYPE = {"custom": "CUSTOMIZED_PRODUCTS", "all": "ALL"}
PRODUCT_VIDEO_SPECIFIC_TYPE = "AUTO_SELECTION"
OPTIMIZATION_GOAL = "VALUE"
DEEP_BID_TYPE = "VO_MIN_ROAS"
SCHEDULE_TYPES = {"now": "SCHEDULE_FROM_NOW", "fixed": "SCHEDULE_FIXED"}
OCCUPIED_ASSET_TYPE = {"spu": "SPU", "identity": "IDENTITY_BC_AUTH_TT"}
WALLET_CURRENCIES = ("USD", "JPY", "THB")

REPORT_ORDERS = ("asc", "desc")
CAMPAIGN_STATUS_ENABLE = "CAMPAIGN_STATUS_ENABLE"
CAMPAIGN_STATUS_DISABLE = "CAMPAIGN_STATUS_DISABLE"


class AdflyUsageError(ValueError):
    """调用方传错了参数(不是服务端拒绝)。"""


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AdflyUsageError(msg)


def _fmt_dt(value) -> Optional[str]:
    """接受 datetime/date/字符串,统一成服务端要的 'YYYY-MM-DD HH:mm:ss'。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (date,)):
        return value.strftime("%Y-%m-%d 00:00:00")
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    raise AdflyUsageError(f"时间格式无法识别: {value!r}")


def _fmt_date(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (date,)) or hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    raise AdflyUsageError(f"日期格式无法识别: {value!r}")


# ---------------- GMVmax ----------------

def gmv_max_create_payload(
    *,
    advertiser_id: str,
    store_id: str,
    store_authorized_bc_id: str,
    campaign_name: str,
    roas_bid: float,
    budget: float,
    tt_auth_id: Any,
    item_group_ids: Optional[Sequence[str]] = None,
    identity_list: Optional[Sequence[Dict[str, Any]]] = None,
    promote_all_products: bool = False,
    schedule_start_time: Any = None,
    schedule_end_time: Any = None,
    schedule_type: str = "now",
    product_video_specific_type: str = PRODUCT_VIDEO_SPECIFIC_TYPE,
) -> Dict[str, Any]:
    """组装 POST /tiktok/gmv_max/create 的请求体。

    提交前服务端会做资产占用校验;`promote_all_products=True` 时不传 item_group_ids,
    且 product_specific_type 变成 ALL —— 与前端 useSubmit 的行为一致。
    """
    _check(bool(advertiser_id), "advertiser_id 必填")
    _check(bool(store_id), "store_id 必填(来自 gmv_max/store/list)")
    _check(bool(store_authorized_bc_id), "store_authorized_bc_id 必填(来自 gmv_max/store/list)")
    _check(bool(campaign_name), "campaign_name 必填")
    _check(float(roas_bid) > 0, "roas_bid 必须 > 0")
    _check(float(budget) > 0, "budget 必须 > 0")
    _check(schedule_type in SCHEDULE_TYPES, f"schedule_type 只能是 {list(SCHEDULE_TYPES)}")
    st = SCHEDULE_TYPES[schedule_type]
    if st == "SCHEDULE_FIXED":
        _check(schedule_start_time is not None, "固定排期必须给 schedule_start_time")

    item_ids = [str(i) for i in (item_group_ids or []) if i]
    if not promote_all_products:
        _check(bool(item_ids), "非全店推广必须给 item_group_ids(商品 ID 列表)")

    campaign: Dict[str, Any] = {
        "advertiser_id": str(advertiser_id),
        "store_id": str(store_id),
        "store_authorized_bc_id": str(store_authorized_bc_id),
        "campaign_name": campaign_name,
        "shopping_ads_type": SHOPPING_ADS_TYPE,
        "product_specific_type": (PRODUCT_SPECIFIC_TYPE["all"] if promote_all_products
                                  else PRODUCT_SPECIFIC_TYPE["custom"]),
        "product_video_specific_type": product_video_specific_type,
        "optimization_goal": OPTIMIZATION_GOAL,
        "deep_bid_type": DEEP_BID_TYPE,
        "roas_bid": roas_bid,
        "budget": budget,
        "schedule_type": st,
    }
    if not promote_all_products:
        campaign["item_group_ids"] = item_ids
    if schedule_start_time is not None:
        campaign["schedule_start_time"] = _fmt_dt(schedule_start_time)
    if schedule_end_time is not None:
        campaign["schedule_end_time"] = _fmt_dt(schedule_end_time)
    if identity_list:
        campaign["identity_list"] = list(identity_list)

    return {"batch": [campaign], "tt_auth_id": tt_auth_id}


def gmv_max_edit(
    existing: Dict[str, Any],
    *,
    budget: Optional[float] = None,
    roas_bid: Optional[float] = None,
    campaign_name: Optional[str] = None,
    tt_auth_id: Any,
) -> Dict[str, Any]:
    """基于 gmv_max/list 或 detail 返回的现有系列改字段。

    服务端要求把完整对象回传,所以这里做 merge 而不是只发增量。
    """
    _check(isinstance(existing, dict) and existing.get("campaign_id"), "existing 必须是含 campaign_id 的系列对象")
    if budget is not None:
        _check(budget > 0, "budget 必须 > 0")
    if roas_bid is not None:
        _check(roas_bid > 0, "roas_bid 必须 > 0")
    merged = dict(existing)
    # 只读字段回传会被服务端忽略或报错,去掉更稳
    for k in ("cost", "net_cost", "orders", "cost_per_order", "gross_revenue", "roi",
              "create_time", "modify_time", "store_name", "advertiser_name", "status",
              "second_status", "operation_status", "row_data", "task_data_id",
              "item_group_ids_str", "port", "currency", "company_ex_id", "user_ex_id"):
        merged.pop(k, None)
    if budget is not None:
        merged["budget"] = budget
    if roas_bid is not None:
        merged["roas_bid"] = roas_bid
    if campaign_name is not None:
        merged["campaign_name"] = campaign_name
    for k in ("schedule_start_time", "schedule_end_time"):
        if merged.get(k):
            merged[k] = str(merged[k]).replace("T", " ").split("+")[0][:19]
    return {"batch": [merged], "tt_auth_id": tt_auth_id}


def gmv_max_occupancy_batch(
    *,
    advertiser_id: str,
    store_id: str,
    item_group_ids: Iterable[str] = (),
    identity_ids: Iterable[str] = (),
) -> Dict[str, Any]:
    """组装建广告前的资产占用校验 body(POST /tiktok/gmv_max/occupied_custom_shop_ads/list)。"""
    batch: List[Dict[str, Any]] = []
    for i in item_group_ids:
        if i:
            batch.append({"advertiser_id": str(advertiser_id), "store_id": str(store_id),
                          "occupied_asset_type": OCCUPIED_ASSET_TYPE["spu"], "asset_ids": [str(i)]})
    for i in identity_ids:
        if i:
            batch.append({"advertiser_id": str(advertiser_id), "store_id": str(store_id),
                          "occupied_asset_type": OCCUPIED_ASSET_TYPE["identity"], "asset_ids": [str(i)]})
    return {"batch": batch}


# ---------------- 报表 ----------------

def report_body(
    *,
    days: int = 7,
    start_date: Any = None,
    end_date: Any = None,
    page: int = 1,
    page_size: int = 50,
    order_by: str = "spend",
    order_type: str = "desc",
    advertiser_ids: Optional[Sequence[str]] = None,
    campaign_ids: Optional[Sequence[str]] = None,
    adgroup_ids: Optional[Sequence[str]] = None,
    ad_ids: Optional[Sequence[str]] = None,
    fields: Optional[Sequence[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """报表请求体。日期不传就取最近 N 天。"""
    _check(order_type in REPORT_ORDERS, f"order_type 只能是 {REPORT_ORDERS}")
    _check(page >= 1 and page_size >= 1, "page / page_size 必须 >= 1")
    end = end_date or date.today()
    start = start_date or (end if not isinstance(end, str) else date.today()) - timedelta(days=days - 1)
    body: Dict[str, Any] = {
        "order_info": {"field": order_by, "order_type": order_type},
        "start_date": _fmt_date(start),
        "end_date": _fmt_date(end),
        "page": page,
        "page_size": page_size,
    }
    for key, val in (("advertiser_ids", advertiser_ids), ("campaign_ids", campaign_ids),
                     ("adgroup_ids", adgroup_ids), ("ad_ids", ad_ids)):
        if val:
            body[key] = [str(v) for v in val]
    if fields:
        body["fields"] = list(fields)
    return body


def export_fields(labels: Sequence[Sequence[str]]) -> List[Dict[str, str]]:
    """[("账户名称","advertiser_name"), ...] → fields 数组(导出接口要这个)。"""
    return [{"label": str(lbl), "value": str(val)} for lbl, val in labels]


# ---------------- 商务中心授权 ----------------

def bc_bind_body(*, bc_id: str, advertiser_ids: Sequence[str]) -> Dict[str, Any]:
    _check(bool(bc_id), "bc_id 必填")
    ids = [str(i) for i in advertiser_ids if i]
    _check(bool(ids), "advertiser_ids 不能为空")
    return {"bc_id": str(bc_id), "advertiser_ids": ids}


def bc_unbind_body(*, bc_id: str, advertiser_id: Optional[str] = None,
                   advertiser_ids: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """单个解绑用 advertiser_id;批量用 advertiser_ids。"""
    _check(bool(bc_id), "bc_id 必填")
    if advertiser_id:
        return {"bc_id": str(bc_id), "advertiser_id": str(advertiser_id)}
    ids = [str(i) for i in (advertiser_ids or []) if i]
    _check(bool(ids), "advertiser_id 或 advertiser_ids 至少给一个")
    return {"bc_id": str(bc_id), "advertiser_ids": ids}


# ---------------- 钱包 ----------------

def check_currency(currency: str) -> str:
    _check(currency in WALLET_CURRENCIES,
           f"currency 只能是 {list(WALLET_CURRENCIES)}(服务端枚举校验,传 CNY 会 400)")
    return currency


def paging_nested(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """automation 与 finance_bff 的 /pay/*、/coupon/* 要嵌套 page_info。

    传平铺 {"page":1} 会得到 500 unknown request error。
    """
    return {"page_info": {"page": page, "page_size": page_size}}


def paging_flat(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """front / advertise / finance / ai_agent 用平铺分页。"""
    return {"page": page, "page_size": page_size}


# ---------------- 组合流程 ----------------

def find_gmv_max_ready_account(c, advertiser_ids: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """找出真正具备 GMVmax 建广告条件的账户。

    两个前提:该广告账户在 TikTok 侧对该授权有操作权限 + 能取到店铺。
    实测 8 个账户里只有部分满足 —— 不查就提交会得到
    "获取店铺列表失败: No permission to operate advertiser: <id>"。
    """
    auth = (c.ads.get_gmv_max_auth_list() or {}).get("list") or []
    if not auth:
        return []
    tta = auth[0]["id"]
    advs = c.advertisers()
    if advertiser_ids:
        advs = [a for a in advs if a["advertiser_id"] in set(advertiser_ids)]
    ready = []
    for a in advs:
        try:
            st = (c.ads.get_gmv_max_store_list({"advertiser_id": a["advertiser_id"],
                                                "tt_auth_id": tta}) or {}).get("list") or []
        except Exception:
            continue
        if st:
            ready.append({"advertiser_id": a["advertiser_id"],
                          "advertiser_name": a.get("advertiser_name"),
                          "tt_auth_id": tta, "stores": st,
                          "store_id": st[0].get("store_id"),
                          "store_authorized_bc_id": st[0].get("store_authorized_bc_id")})
    return ready


def gmv_max_identities(c, *, advertiser_id: str, store_id: str,
                       store_authorized_bc_id: str, tt_auth_id: Any) -> List[Dict[str, Any]]:
    """取投放身份。四个参数缺一不可(只给 advertiser_id 会报参数错)。"""
    d = c.ads.get_gmv_max_identity_list({
        "advertiser_id": advertiser_id, "store_id": store_id,
        "store_authorized_bc_id": store_authorized_bc_id, "tt_auth_id": tt_auth_id})
    return (d or {}).get("list") or []


def iter_report(c, path: str = "/tiktok/advertiser_report", page_size: int = 100,
                group: str = "advertise", **kwargs) -> Iterable[Dict[str, Any]]:
    """按页拉完整报表。总条数取自响应的 count。"""
    page = 1
    while True:
        data = c.call(group, "POST", path, report_body(page=page, page_size=page_size, **kwargs)) or {}
        items = data.get("list") or []
        for it in items:
            yield it
        if not items or len(items) < page_size:
            return
        page += 1


def wallet_balances(c, currency: str = "USD") -> Dict[str, Any]:
    """钱包余额(按 currency 取,顺带返回全部币种)。"""
    check_currency(currency)
    d = c.wallet.list_wallet({"currency": currency}) or {}
    return {"wallets": d.get("wallets") or [], "credit": d.get("credit"),
            "currency_available": d.get("currency_available"),
            "available_usd": d.get("available_usd")}


# ---------------- 商务中心(BC)授权 ----------------
#
# 完整链路(全部实测):
#
#   1) GET  /advertiser/get_auth_link?platform=1        → auth_link(TikTok OAuth)
#   2) 浏览器打开 auth_link 走完 TikTok 授权             → TikTok 回调 redirect_uri
#   3) POST /advertiser/adv_bc_bind_list                → 查绑定任务(含 task_id)
#   4) POST /tt/bc/list {tiktok_auth_id}                → 查该授权下可用的 BC
#   5) POST /advertiser/adv_bc_bind                     → 建绑定任务(见下方警告)
#
# ⚠ adv_bc_bind 不是幂等的,而且是**真写**:
#   同一个 adv+bc 每调一次就新增一条绑定任务记录。实测重复调用后 adv_bc_bind_list
#   从 9 条涨到 11 条,且新建的记录 status 会落到 2(绑定生效)。
#   没有"取消绑定任务"的接口 —— 唯一的撤销路径是解绑(bc_un_bind_single)。
#   调用前必须先用 bind_records() 查一遍,确认没有同 adv+bc 的记录。

# 绑定任务状态。实测:现有记录全部落在 2,前端以 `status === 2` 作为不可再操作的判据。
# 注意:2 是**终态(绑定生效)**,不是"处理中" —— 有记录中途从 4 变成 2,说明服务端异步推进后
# 落定在 2。所以判断"还在处理中"不能只靠 status,要结合 created_at 与 updated_at 的时间差。
BIND_STATUS = {
    0: "未知/初始",
    1: "未知/中间态",
    2: "有效(绑定生效)",   # 终态;前端 status===2 即禁止再操作
    3: "未知/中间态",
    4: "提交后未落定",     # 观察到会自行转成 2,不能直接当失败
}


def auth_link(c, platform: int = 1) -> Dict[str, str]:
    """取 TikTok 授权链接。

    platform 必填 —— 少了会得到 code=999 server_invalid_platform(踩过)。
    platform: 1=TikTok, 2=FaceBook, 3=Google, 4=ASA。

    返回 {auth_link, link_ex_id, app_id, state, redirect_uri,
          company_ex_id, user_ex_id, nonce}。

    授权完成后用 link_ex_id 轮询 check_auth_result() 确认。
    """

    d = c.t.request("GET", "/advertiser/get_auth_link", group="advertise",
                    params={"platform": platform}) or {}
    link = d.get("auth_link", "")
    _check(bool(link), "服务端没返回 auth_link")
    import urllib.parse as up
    q = up.parse_qs(up.urlparse(link).query)
    state = (q.get("state") or [""])[0]
    parts = state.split("_")
    return {
        "auth_link": link,
        # 服务端另有 link_ex_id 字段,等于 state 的第 4 段;轮询查授权结果要用它
        "link_ex_id": d.get("link_ex_id") or (parts[3] if len(parts) > 3 else ""),
        "app_id": (q.get("app_id") or [""])[0],
        "state": state,
        "redirect_uri": (q.get("redirect_uri") or [""])[0],
        "company_ex_id": parts[0] if len(parts) > 0 else "",
        "user_ex_id": parts[1] if len(parts) > 1 else "",
        "nonce": parts[3] if len(parts) > 3 else "",
    }


def check_auth_result(c, link_ex_id: str, company_ex_id: Optional[str] = None,
                      timeout: float = 0.0, interval: float = 3.0) -> Dict[str, Any]:
    """查/轮询授权结果(POST /bc/query_auth)。

    前端拿到授权链接后就开这个轮询,直到 data.result 出现才算授权成功。
    timeout=0 时只查一次;>0 时按 interval 轮询直到超时。
    返回 {result, auth, polls} —— result 为空 dict/None 表示还没完成。
    """
    _check(bool(link_ex_id), "link_ex_id 必填(来自 auth_link() 或 state 第 4 段)")
    company = company_ex_id or c.session.company_ex_id
    _check(bool(company), "company_ex_id 必填")
    import time as _t
    deadline = _t.time() + timeout
    polls = 0
    while True:
        polls += 1
        d = c.call("advertise", "POST", "/bc/query_auth",
                   {"company_ex_id": company, "auth_link_ex_id": link_ex_id}) or {}
        if d.get("result"):
            return {"result": d["result"], "auth": d.get("auth"), "polls": polls}
        if timeout <= 0 or _t.time() >= deadline: CONTACT_REDACTED {"result": None, "auth": None, "polls": polls}
        _t.sleep(interval)


def tt_bc_list(c, tiktok_auth_id: Any) -> List[Dict[str, Any]]:
    """该 TikTok 授权下可操作的商务中心列表(POST /tt/bc/list)。

    返回元素形如:
        {bc_detail: {bc_id, name, company, currency, registered_area, status,
                     timezone, type, verification_status},
         user_role: "ADMIN", ext_user_role: {finance_role: "MANAGER"}}
    """
    _check(bool(tiktok_auth_id), "tiktok_auth_id 必填(来自 /tiktok/auth_list 的 id)")
    d = c.call("advertise", "POST", "/tt/bc/list", {"tiktok_auth_id": tiktok_auth_id}) or {}
    return d.get("list") or []


def advertiser_bcs(c, advertiser_id: str, owner_bc_id: str,
                   platform: int = 1) -> List[Dict[str, Any]]:
    """某广告账户挂靠的 BC 列表(POST /advertiser/get_bind_bc)。

    语义(实测):
      * bc_id 传**账户自己的 owner_bc_id**(来自 advertiser/list),
        返回该账户已挂靠的 BC 数组 [{bc_id, bc_name}]
      * **platform 必填** —— 不带会返回 data=null(不是报错,容易误判成"没有绑定")
      * 传目标 BC 的 id → code=999 "No permission to view or operate."

    返回 null 时按空列表处理;调用方要区分"没有绑定"和"参数不对",
    可以看下面的 raw_advertiser_bcs()。
    """
    _check(bool(owner_bc_id), "bc_id 必填(传广告账户的 owner_bc_id)")
    return raw_advertiser_bcs(c, advertiser_id, owner_bc_id, platform=platform)[0]


def raw_advertiser_bcs(c, advertiser_id: str, owner_bc_id: str,
                       platform: int = 1) -> tuple:
    """同 advertiser_bcs,但返回 (列表, 原始响应) —— 便于区分"没有绑定"和"参数不对"。"""
    _check(bool(owner_bc_id), "bc_id 必填(传广告账户的 owner_bc_id)")
    raw = c.raw("advertise", "POST", "/advertiser/get_bind_bc",
                {"bc_id": owner_bc_id, "advertiser_id": advertiser_id, "platform": platform})
    d = raw.get("data")
    if isinstance(d, list):
        return d, raw
    if isinstance(d, dict):
        return d.get("list") or d.get("data") or [], raw
    return [], raw


def bind_records(c, advertiser_id: Optional[str] = None, status: Optional[int] = None,
                 page_size: int = 50) -> List[Dict[str, Any]]:
    """查绑定任务记录(POST /advertiser/adv_bc_bind_list)。

    记录字段:task_id / advertiser_id / bc_id / status / remark / port / created_at。
    当前 0 个筛选参数时返回全量,可按 advertiser_id、status 过滤。
    """
    d = c.call("advertise", "POST", "/advertiser/adv_bc_bind_list",
               {"page": 1, "page_size": page_size,
                **({"advertiser_id": advertiser_id} if advertiser_id else {})}) or {}
    rows = d.get("list") or []
    if status is not None:
        rows = [r for r in rows if r.get("status") == status]
    return rows


def pending_bind_records(c, unsettled_only: bool = True) -> List[Dict[str, Any]]:
    """疑似未落定的绑定任务。

    不能只按 status 判断 —— 实测 status=2 是终态"生效",4 也会自行转成 2。
    这里按 updated_at - created_at 的时间差找"刚提交还没被服务端推进过"的记录,
    用于"提交前别重复"的护栏;unsettled_only=False 时返回全部记录。
    """
    rows = bind_records(c, page_size=200)
    if not unsettled_only:
        return rows
    out = []
    for r in rows:
        try:
            from datetime import datetime
            fmt = "%Y-%m-%dT%H:%M:%S"
            a = datetime.strptime(str(r["created_at"])[:19], fmt)
            b = datetime.strptime(str(r["updated_at"])[:19], fmt)
            if (b - a).total_seconds() < 5:
                out.append(r)
        except (KeyError, ValueError):
            continue
    return out


def bind_body(*, advertiser_id: str, bc_id: str, task_id: str = "", platform: int = 1) -> Dict[str, Any]:
    """组装 POST /advertiser/adv_bc_bind 的请求体。

    字段名是实测出来的:advertiser_id 是**数组**(传字符串会触发 Go 反序列化类型错误),
    bc_id 是目标商务中心。缺 bc_id 报 "bc_id(mcc_id)为空"。
    """
    _check(bool(advertiser_id), "advertiser_id 必填")
    _check(bool(bc_id), "bc_id 必填(目标商务中心 id)")
    return {"advertiser_id": [str(advertiser_id)], "bc_id": str(bc_id),
            "task_id": str(task_id), "platform": platform}


def unbind_single_body(*, owner_bc_id: str, un_bind_bc_id: str, advertiser_id: str,
                       platform: int = 1) -> Dict[str, Any]:
    """单个解绑(POST /advertiser/bc_un_bind_single)。

    两个 bc 字段不是一个东西:
      owner_bc_id    账户自己所属的 BC(来自 advertiser/list 的 owner_bc_id)
      un_bind_bc_id  要解绑掉的那个 BC(来自 get_bind_bc / adv_bc_bind_list)
    """
    _check(bool(owner_bc_id), "owner_bc_id 必填")
    _check(bool(un_bind_bc_id), "un_bind_bc_id 必填(要解绑的 BC)")
    _check(bool(advertiser_id), "advertiser_id 必填")
    return {"bc_id": str(owner_bc_id), "un_bind_bc_id": str(un_bind_bc_id),
            "advertiser_id": str(advertiser_id), "platform": platform}


def normalize_bc_ids(text: str) -> str:
    """把用户输入的 BC id 列表规范化 —— 复现前端的 normalizeBindBcIdsForApi。

    处理中文全角逗号、多余空格,输出逗号分隔字符串(前端表单就是这个格式)。
    """
    return ",".join(p.strip() for p in str(text).replace("，", ",").split(",") if p.strip())
