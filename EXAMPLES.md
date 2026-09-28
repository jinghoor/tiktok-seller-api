# 常用场景示例（全部为实测通过的调用）

## 0. 登录

```python
from adfly_api import AdflyClient
from pathlib import Path

c = AdflyClient(state_path=Path("adfly_api/.session.json"))
c.login("PHONE_REDACTED", "你的密码")        # 会缓存 token 到 .session.json
print(c.session.company_ex_id)           # 10017794444062955153
print(c.me()["name"], c.me()["phone"])   # 何阳鸿 PHONE_REDACTED
```

命令行等价：

```bash
python -m adfly_api login --account PHONE_REDACTED
python -m adfly_api me --show-token
```

---

## 1. 拉广告账户

```python
for a in c.advertisers():
    print(a["advertiser_id"], a["advertiser_name"], a["balance"], a["currency"], a["owner_bc_id"])
```

实测输出 8 个账户（含 `DAMAI-SHOP_X3`、`DAMAI-TK20` 等）。

---

## 2. 拉 GMVmax 推广系列（62 条）

```python
data = c.ads.get_gmv_max_list({"page": 1, "page_size": 100})
print(data["count"])            # 62
for it in data["list"]:
    print(it["campaign_id"], it["campaign_name"], it["roas_bid"], it["budget"],
          it["second_status"], it["cost"], it["currency"])
```

翻页全量取：

```python
for it in c.t.paginate("advertise", "/tiktok/gmv_max/list", page_size=50):
    print(it["campaign_id"], it["campaign_name"])
```

按账户过滤 / 排序：

```python
c.ads.get_gmv_max_list({
    "page": 1, "page_size": 50,
    "advertiser_ids": ["7686XXXXXXXXXX08"],
    "order_info": {"field": "cost", "order_type": "desc"},
})
```

---

## 3. 拉报表

```python
rpt = c.ads.get_ad_account_report_list({
    "order_info": {"field": "spend", "order_type": "desc"},
    "start_date": "2026-09-01", "end_date": "2026-09-24",
    "page": 1, "page_size": 50,
})
for row in rpt["list"]:
    print(row)
```

导出 Excel 落盘：

```python
c.download("advertise", "/tiktok/advertiser_report/export",
           "out/advertiser_report.xlsx",
           {"order_info": {"field": "spend", "order_type": "desc"},
            "start_date": "2026-09-01", "end_date": "2026-09-24",
            "fields": [{"label": "账户名称", "value": "advertiser_name"},
                       {"label": "消耗", "value": "spend"}]})
```

---

## 4. 新建 GMVmax 广告（完整 4 步）

```python
AID = "7642XXXXXXXXXX57"      # 唯一有店铺权限的账户
TTA = 1960                       # tt_auth_id，来自 auth_list

# 步骤 1：授权列表
auth = c.auth_accounts()
tta = auth[0]["id"]

# 步骤 2：店铺
store = c.stores(AID, tta)[0]
store_id, bc_id = store["store_id"], store["store_authorized_bc_id"]

# 步骤 3：投放身份
identities = c.ads.get_gmv_max_identity_list({
    "advertiser_id": AID, "store_id": store_id,
    "store_authorized_bc_id": bc_id, "tt_auth_id": tta,
})["list"]

# 步骤 4：前置占用校验（正式建之前必调，返回冲突列表）
c.ads.check_occupied_custom_shop_ads({
    "batch": [{"advertiser_id": AID, "store_id": store_id,
               "occupied_asset_type": "SPU", "asset_ids": ["1735XXXXXXXXXX50"]}],
    "tt_auth_id": tta,
})

# 提交
c.ads.create_gmv_max_ad({
    "batch": [{
        "advertiser_id": AID,
        "store_id": store_id,
        "store_authorized_bc_id": bc_id,
        "campaign_name": "商品 GMV Max_总收入_TEST",
        "shopping_ads_type": "PRODUCT",
        "product_specific_type": "CUSTOMIZED_PRODUCTS",
        "product_video_specific_type": "AUTO_SELECTION",
        "optimization_goal": "VALUE",
        "deep_bid_type": "VO_MIN_ROAS",
        "roas_bid": 3,
        "budget": 300,
        "schedule_type": "SCHEDULE_FROM_NOW",
        "schedule_start_time": "2026-09-25 10:00:00",
        "schedule_end_time": "2036-09-21 10:00:00",
        "item_group_ids": ["1735XXXXXXXXXX50"],
        "identity_list": identities[:1],
    }],
    "tt_auth_id": tta,
})
```

**改预算 / ROI（改已有系列）**：

```python
c.ads.edit_gmv_max_ad({"batch": [{**existing, "budget": 500, "roas_bid": 4}], "tt_auth_id": tta})
```

**复制系列**：`c.ads.copy_campaign({...})`

---

## 5. 编辑普通广告（VSA）

```python
# 详情
c.ads.get_tiktok_ad_detail({"ad_id": "..."})
c.ads.get_tiktok_ad_group_detail({"adgroup_id": "..."})
c.ads.get_tiktok_ad_aampaign_info({"campaign_id": "..."})

# 修改（先取详情，改字段，回传）
detail = c.ads.get_tiktok_ad_detail({"ad_id": "..."})
detail["ad_name"] = "新名字"
c.ads.modify_tiktok_ad(detail)

# 批量开关
c.ads.call("POST", "/tiktok/modify_campaign_status_multi", {
    "campaign_ids": ["1877XXXXXXXXXX22"], "operation_status": "DISABLE"})

# 扩量 / 复制
c.ads.adgroup_extend({...})
c.ads.copy_adv_group({...})
```

---

## 6. 商务中心授权

```python
# 1) 拿授权链接（丢给浏览器打开完成 TikTok OAuth）
link = c.call("advertise", "GET", "/advertiser/get_auth_link", params=None)["auth_link"]
# 注意:必须带 platform=1
link = c.t.request("GET", "/advertiser/get_auth_link", group="advertise",
                   params={"platform": 1})["auth_link"]

# 2) 已绑定 / 未绑定
bound   = c.ads.get_account_bind_bc_list({"page": 1, "page_size": 50})
unbound = c.ads.get_advertiser_bind_bc_list({"page": 1, "page_size": 50})

# 3) 绑定 / 解绑
c.ads.call("POST", "/advertiser/adv_bc_bind", {"bc_id": "7418XXXXXXXXXX24",
          "advertiser_ids": ["7689XXXXXXXXXX05"]})
c.ads.account_un_bind_bc_single({"advertiser_id": "7689XXXXXXXXXX05",
                                 "bc_id": "7418XXXXXXXXXX24"})
c.ads.account_un_bind_bc_multi({"advertiser_ids": ["...", "..."], "bc_id": "..."})
```

---

## 7. 钱包 / 资金

```python
c.wallet.list_wallet({"currency": "USD"})      # currency 必填！
c.wallet.get_coupon_list({"page_info": {"page": 1, "page_size": 20}})
c.wallet.get_trade_list({"page_info": {"page": 1, "page_size": 20}})
c.wallet.get_currency_exchange({"from_currency": "USD", "to_currency": "CNY", "amount": 100})
```

---

## 8. 自动化策略 / 标签

```python
# 分页必须用 page_info 嵌套
c.auto.automation_get_list_tactic({"page_info": {"page": 1, "page_size": 20}})
c.auto.get_label_list({"page_info": {"page": 1, "page_size": 50}})
c.auto.get_advertiser_list({"page_info": {"page": 1, "page_size": 100}})

c.auto.add_label({"label_name": "重点", "category_id": "..."})
c.auto.bind_label_relation({"advertiser_ids": ["..."], "label_ids": ["..."]})
c.auto.automation_add_tactic({...})
c.auto.automation_update_tactic_status({"tactic_ids": ["..."], "status": 1})
```

---

## 9. 财务

```python
c.fin.get_settlement_list({"page": 1, "page_size": 20})
c.fin.get_settlement_detail({"page": 1, "page_size": 20, "settlement_id": "..."})
c.fin.get_payable_detail({"page": 1, "page_size": 20})
c.fin.get_bill_set_need()
```

---

## 10. 多公司切换

```python
for co in c.companies():
    print(co["company_ex_id"], co["company_name"])

c.use_company("10017794444062955153")     # 切过去，后续请求自动带上
```

---

## 11. 调没有封装的接口

```python
# 返回 data
c.call("advertise", "POST", "/tiktok/gmv_max/get_refresh_time", {})
# 返回完整信封（看 code / request_id）
c.raw("advertise", "POST", "/tiktok/gmv_max/list", {"page": 1, "page_size": 5})
# 完整 URL 也行
c.t.request("GET", "https://front-v1.aiadfly.com/front_api/user/info", group="front")
```

命令行：

```bash
python -m adfly_api list --grep gmv
python -m adfly_api call advertise POST /gmv_max_list_body.json ...
python -m adfly_api call advertise POST /tiktok/gmv_max/list '{"page":1,"page_size":5}'
python -m adfly_api raw  advertise POST /tiktok/auth_list
```

---

## 12. 批量拉取 + 落 CSV

```python
import csv

rows = []
for it in c.t.paginate("advertise", "/tiktok/gmv_max/list", page_size=50):
    rows.append({
        "campaign_id": it["campaign_id"], "name": it["campaign_name"],
        "advertiser_id": it["advertiser_id"], "roas_bid": it["roas_bid"],
        "budget": it["budget"], "status": it["second_status"],
        "cost": it["cost"], "currency": it["currency"],
    })

with open("gmvmax.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(f"导出 {len(rows)} 条")
```

---

## 13. 用 helpers 少写一半代码

```python
from adfly_api import AdflyClient
from adfly_api import helpers as H

c = AdflyClient()

# 报表:日期默认最近 N 天,自动翻页
for row in H.iter_report(c, "/tiktok/advertiser_report", days=30, order_by="spend"):
    print(row["advertiser_name"], row["spend"])

# 找真正能建 GMVmax 的账户(实测 8 个里只有 1 个满足)
for a in H.find_gmv_max_ready_account(c):
    print(a["advertiser_id"], a["advertiser_name"], "store:", a["store_id"])

# 钱包(currency 本地校验)
print(H.wallet_balances(c, "JPY")["available_usd"])

# 分页风格别搞混
c.auto.automation_get_list_tactic(H.paging_nested(1, 20))   # 嵌套
c.ads.get_advertiser_list(H.paging_flat(1, 50))             # 平铺

# 建广告:payload 组装 + 本地校验,拼错立刻报,不用等服务端
p = H.gmv_max_create_payload(advertiser_id="...", store_id="...", store_authorized_bc_id="...",
                             campaign_name="商品 GMV Max_TEST", roas_bid=3, budget=300,
                             tt_auth_id=1960, item_group_ids=["1735XXXXXXXXXX50"])
c.ads.create_gmv_max_ad(p)
```

**看 docstring 就知道要传什么** —— 34 个方法的参数是实测出来的：

```python
>>> help(c.ads.get_pixel_list)
POST /ad/pixel/list  (前端 getPixelListAPI)
实测必需字段(1 个,字段已摸清): advertiser_id:string
可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}

>>> help(c.agent.get_gmv_max_identity_list)
POST /ai_agent/v1/ad/gmv_max/identity/list  (前端 getGMVMaxIdentityList)
实测必需字段(3 个,字段已摸清): advertiser_id:string, store_id:string, store_authorized_bc_id:string
```

---

## 14. 商务中心（BC）授权完整流程

```python
from adfly_api import AdflyClient
from adfly_api import helpers as H

c = AdflyClient()
adv = c.advertisers()[0]

# ① 拿授权链接（platform 必填！）
L = H.auth_link(c)
print(L["auth_link"])        # 丢到浏览器打开，TikTok 侧完成授权
print(L["company_ex_id"], L["user_ex_id"], L["nonce"])   # state 拆出来的四段
# redirect_uri = https://front.aiadfly.com/front_api/advertiser/adv_auth
# ↑ 授权完成后由服务端处理，纯 HTTP 客户端替代不了这一步

# ② 看这个 TikTok 授权下有哪些商务中心
for bc in H.tt_bc_list(c, 1960):
    d = bc["bc_detail"]
    print(d["bc_id"], d["name"], d["company"], d["currency"], d["registered_area"], bc["user_role"])

# ③ 看某个广告账户挂靠了哪些 BC
mine = H.advertiser_bcs(c, adv["advertiser_id"], adv["owner_bc_id"])
print(mine)                  # [{'bc_id': '7626XXXXXXXXXX75', 'bc_name': 'Bnjg'}]
# 注意：bc_id 传 owner_bc_id；platform 必填，否则返回 null

# ④ 查绑定任务状态（提交前必查！）
for r in H.bind_records(c, page_size=50):
    print(r["task_id"], r["advertiser_id"], r["bc_id"],
          H.BIND_STATUS.get(r["status"]), r["created_at"])

# ⑤ 绑定 —— ⚠ 非幂等，每调一次新增一条任务记录
pending = [r for r in H.pending_bind_records(c) if r["advertiser_id"] == adv["advertiser_id"]]
if pending:
    print("已有处理中的任务，别重复提交:", pending)
else:
    c.call("advertise", "POST", "/advertiser/adv_bc_bind",
           H.bind_body(advertiser_id=adv["advertiser_id"], bc_id="7626XXXXXXXXXX75"))
    # advertiser_id 传数组 —— helpers 已处理

# ⑥ 解绑（owner_bc_id 和 un_bind_bc_id 是两个不同的 BC）
c.call("advertise", "POST", "/advertiser/bc_un_bind_single",
       H.unbind_single_body(owner_bc_id=adv["owner_bc_id"],
                            un_bind_bc_id="7626XXXXXXXXXX75",
                            advertiser_id=adv["advertiser_id"]))
# 解绑后需要重新授权

# 表单输入规范化（处理中文全角逗号）
H.normalize_bc_ids("123，456，789")     # -> '123,456,789'
```
