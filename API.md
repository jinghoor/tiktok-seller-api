# ad.aiadfly.com 广告管理接口逆向文档

来源：线上 bundle `index-CI-PN84-.js`（`https://ad.aiadfly.com/NUMBER_REDACTED/`，SHA256 `3f0107d1cb1d0eNUMBER_REDACTEDd21694fef1eaebb104b8a92789c49ecdedeb96c9`）
+ 浏览器实机流量 + 服务端返回码探测。共 **291 个唯一接口**（原始 293 条去重后），
全部做过覆盖测试；其中 76 个直接返回数据，33 个已被服务端移除。

---

## 1. 认证机制

**纯 header 认证，不使用 cookie。** 这一点很关键——客户端可以完全脱离浏览器运行。

| Header | 值 | 来源 |
|---|---|---|
| `AuthorizationFront` | JWT | 登录返回的 `data.token`（259 字符） |
| `CompanyExID` | 公司外部 ID，如 `10017794444062955153` | `GET /company/list` 返回数组的 `company_ex_id` |
| `country` | `CN` | |
| `lang` | `zh-CN` | |

JWT payload 字段：`user_ex_id` / `source` / `exp` / `jti` / `iss`(=chuangyi.top) / `nbf`，有效期 **3 天**。

### 登录

```
POST https://front-v1.aiadfly.com/front_api/user/login
{"account": "PHONE_REDACTED", "password": "<md5(明文密码)>"}
```

- 参数名是 `account`，手机号或邮箱都行
- 密码是 **MD5(去空格后的明文)**，前端 `md5(Ie.password.trim())`
- 成功：`code=0`，`data` 就是 userInfo（含 `token`、`user_id`、`name`、`menu_info`）
- 失败：`code=7 密码错误` / `code=404 用户不存在`

登录后调 `GET /front_api/company/list`（**GET，不是 POST**）拿公司列表，取 `company_ex_id` 填进 `CompanyExID` 头。

> **单会话**：登录会让同一账号的其它会话失效（旧会话报 `code=9` "账号在别处登录，请重新登录!"）。Python 端登录后，浏览器里的标签页会被挤下线。

### 其它认证相关接口

| 接口 | 说明 |
|---|---|
| `POST /front_api/user/check_fa` | `{account, password: md5(pwd)}`，探测是否需双因素 |
| `POST /front_api/user/login/qrcode/create` | 扫码登录-生成 |
| `POST /front_api/user/login/qrcode/status` | 扫码登录-轮询 |
| `DELETE /front_api/session` | 旧版登出（`/api/session` 路由已下线） |
| `GET /front_api/user/send_code` | 短信/邮件验证码 |

### 响应信封

`/front_api/*`：

```json
{"code": 0, "message": "ok", "request_id": "xxx", "data": {...}}
```

| code | 含义 |
|---|---|
| 0 | 成功 |
| 2 | 未携带 token |
| 7 | 密码错误 |
| 9 | 账号在别处登录 |
| 11 | company_ex_id 参数为空 |
| 400 / 401 | 无权限（部分服务用） |
| 404 | 用户不存在 / 路由不存在 |
| 999 | 业务校验失败（如"广告账号有误"），**message 里是真实原因** |

`ai_agent` 与 `finance-bff` 服务信封不同：`{"code": 400, "reason": "WITHOUT_TOKEN", "message": "..."}`。

路由不存在时返回 **HTTP 404 + 纯文本 `404 page not found`**（不是 JSON）。

---

## 2. 后端 host 分布（实测）

bundle 里的 7 个模块段是按**页面**分块的，域名声明不可直接当 host 用。实测结论：

覆盖测试对 **全部 291 个接口 × 6 个 host** 做了对比调用，结论是
**每个接口只在一个 host 上成立，0 个歧义** —— 所以归属被固化成
`spec/routes_builtin.json`，运行时零探测。

| 服务 | host | 实测承载接口数 | 独有接口示例 |
|---|---|---|---|
| 主网关 | `front-v1.aiadfly.com/front_api` | 160 | `/advertiser/list`、`/tiktok/gmv_max/list`、`/user/*`、`/notice/*` |
| 广告 BFF | `advertise-bff-v1.aiadfly.com/front_api` | 18 | `/tt/auth/list`、`/tt/bc/list`、`/ad/gmv_max_store_config/*`、`/ad/pixel/list`、`/kanban/google_adv_consume`、`/bc/query_auth` |
| AI Agent | `ai-agent-v1.aiadfly.com` | 52 | `/ai_agent/v1/*`、`/ai_agent/market/*` |
| 自动化 | `automation-v1.aiadfly.com/front_api` | 34 | `/tactic/*`、`/label*`、`/material*` |
| 资金 BFF | `finance-bff-v1.aiadfly.com/front_api` | 15 | `/wallet/*`、`/pay/*`、`/coupon/*` |
| 财务 | `finance-v1.aiadfly.com/front_api` | 10 | `/finance/settlement/*`、`/finance/rebate/*`、`/finance/account/payable/detail` |
| MCP Open | `mcp-open.aiadfly.com` | 2 | `/oauth/authorize_confirm`、`/decrypt/wlh_login_info` |

> `advertise-bff-v1` 早期被误判为"公网 404"，实际是它的路由集与主网关**不同**：
> `/advertiser/list` 在它上面 404，而 `/tt/auth/list` 只在它上面存在。必须作为独立候选 host。

**归属规则**（`backend_map.py`，唯一权威）：
线上 bundle 的 7 个模块段按**页面**分块，与真实服务不对应 —— `finance` 段里塞了
Google Ads 的 `/snapshots/*`，`ai_agent` 段里塞了主网关的 `/notice/*`。
因此归属按「段 + 路径」双维度判定，规则见 `backend_map.py` 的 `PATH_RULES`。

---

## 3. 接口全集

按模块分组，共 291 个。完整表格见 `api_tables.md`，机器可读清单见 `adfly_api/spec/endpoints.json`。

| 模块 | 数量 | 覆盖 |
|---|---|---|
| advertise | 60 | 广告账户、商务中心授权、VSA 新建/修改/复制、GMVmax 全链、报表+导出 |
| finance | 85 | 结算、应收、返点、账单、Google/FB 消耗 |
| ai_agent | 84 | 对话、开户引导、GMVmax/VSA 建广告链路、OCR、合同 |
| automation | 32 | 策略(tactic)、标签(label)、素材组、广告/广告组列表 |
| finance_bff | 16 | 钱包、充值、优惠券、支付 |
| front | 14 | 登录、用户、公司、菜单、成员 |
| mcp_open | 2 | OAuth 授权确认、登录信息解密 |

---

## 4. 核心接口详解（含实测参数）

### 4.1 广告账户

```
POST /front_api/advertiser/list
{"page": 1, "page_size": 5000, "platform": 1}
```

实测返回 8 个账户。关键字段：

```json
{
  "advertiser_id": "7689XXXXXXXXXX05",
  "advertiser_name": "Adfly-Adfly-DAMAI-TK178-2931-1-8758-1",
  "company_ex_id": "10017794444062955153",
  "company_name": "广西大迈进出口贸易有限公司",
  "owner_bc_id": "7418XXXXXXXXXX24",
  "port": "CN", "currency": "USD", "platform": 1,
  "status": 1, "status_new": "STATUS_ENABLE", "bind_status": 2,
  "balance": 0, "can_clear": 1, "clear_amount": 0,
  "min_recharge_amount": 10, "pay_type": 0, "timezone": ""
}
```

其它账户接口：`/advertiser/config`(GET)、`/advertiser/apply`、`/advertiser/apply_list`、`/advertiser/list/export`、`/advertiser/advertiser_update`。

### 4.2 商务中心授权（BC）

**完整链路**（全部实测）：

```
1) GET  /advertiser/get_auth_link?platform=1     → 拿 TikTok OAuth 链接
2) 浏览器打开该链接，在 TikTok 侧完成授权           → 回调 redirect_uri
3) POST /advertiser/adv_bc_bind_list             → 查绑定任务（含 task_id）
4) POST /tt/bc/list {tiktok_auth_id}             → 查该授权下可操作的 BC
5) POST /advertiser/adv_bc_bind                  → 建绑定任务（⚠ 非幂等，见下）
```

#### 授权链接

```
GET /advertiser/get_auth_link?platform=1
```

**`platform` 必填**，缺了报 `code=999 server_invalid_platform`。实测返回：

```json
{"auth_link": "https://business-api.tiktok.com/portal/auth
   ?app_id=7323XXXXXXXXXX09
   &state=10017794444062955153_11017794444062945153_7323XXXXXXXXXX09_44517902644465904424
   &redirect_uri=https%3A%2F%2Ffront.aiadfly.com%2Ffront_api%2Fadvertiser%2Fadv_auth"}
```

`state` 结构（下划线分隔四段）：

| 位置 | 含义 | 实测值 |
|---|---|---|
| 0 | company_ex_id | `10017794444062955153` |
| 1 | user_ex_id | `11017794444062945153` |
| 2 | app_id | `7323XXXXXXXXXX09` |
| 3 | 随机 nonce | `44517902644465904424` |

`redirect_uri` 是 `https://front.aiadfly.com/front_api/advertiser/adv_auth` —— TikTok 授权完成后回这里，
服务端据 `state` 绑定到对应公司/用户。**这一步必须在浏览器完成，无法用纯 HTTP 客户端替代。**

#### 可用商务中心

```
POST /tt/bc/list  {"tiktok_auth_id": 1960}
```

`tiktok_auth_id` 来自 `/tiktok/auth_list` 返回的 `id`（类型是 number）。实测返回：

```json
{"list": [{
  "bc_detail": {
    "bc_id": "7457XXXXXXXXXX28", "name": "VNKQQS20",
    "company": "CÔNG TY TNHH MTV THUẬN NAM ĐẮK NÔNG",
    "currency": "USD", "registered_area": "VN", "status": "ENABLE",
    "timezone": "Asia/Ho_Chi_Minh", "type": "SELF_SERVICE",
    "verification_status": "NOT_SUBMITTED"
  },
  "user_role": "ADMIN",
  "ext_user_role": {"finance_role": "MANAGER"}
}]}
```

#### 查账户挂靠的 BC

```
POST /advertiser/get_bind_bc  {"bc_id": "<账户的 owner_bc_id>", "advertiser_id": "...", "platform": 1}
→ [{"bc_id": "7626XXXXXXXXXX75", "bc_name": "Bnjg"}]
```

三个易错点：
- `bc_id` 传的是**账户自己的 `owner_bc_id`**（来自 `advertiser/list`），不是目标 BC
- **`platform` 必填** —— 不带会返回 `data=null`（不是报错，容易误判成"没有绑定"）
- 传目标 BC 的 id → `code=999 "No permission to view or operate."`

#### 绑定任务记录

```
POST /advertiser/adv_bc_bind_list  {"page":1,"page_size":50}
```

```json
{"task_id": "28017902444525234531", "platform": "1",
 "advertiser_id": "7689XXXXXXXXXX74", "advertiser_name": "Adfly-Adfly-DAMAI-...",
 "bc_id": "7626XXXXXXXXXX75", "company_ex_id": "10017794444062955153",
 "status": 2, "remark": "", "port": "CN",
 "created_at": "2026-09-24T18:08:51.839+08:00", "updated_at": "..."}
```

**status 含义**（实测，含一个反直觉点）：

| status | 含义 |
|---|---|
| 0 | 未知/初始 |
| 1 | 未知/中间态 |
| **2** | **有效（绑定生效）** —— 终态，前端以 `status === 2` 禁止再操作 |
| 3 | 未知/中间态 |
| 4 | 提交后未落定 |

⚠ **`4` 不等于失败。** 实测有记录先落 `4`、几分钟后自行变成 `2` —— 服务端是异步推进的。
所以判断"还在处理中"不能只看 status，要结合 `updated_at - created_at` 的时间差。

另有 `/advertiser/bc_un_bind_list`（待绑定）与 `/advertiser/adv_bc_bind_list/export`（导出 xlsx）。

#### 绑定 / 解绑

```
POST /advertiser/adv_bc_bind
{"advertiser_id": ["<id>"], "bc_id": "<目标 BC>", "task_id": "<任务 id>", "platform": 1}
```

字段名是**套出来的**，有两个坑：

- `advertiser_id` 是**数组** —— 传字符串会触发 Go 反序列化错误
  `json: cannot unmarshal string into Go struct field AdvBcBind...`
- 缺 `bc_id` 报 `bc_id(mcc_id)为空`；字段名不是 `advertiser_ids` / `bind_bc_ids`

> ⚠ **`adv_bc_bind` 不是幂等的，而且是真写。** 同一个 `adv+bc` 每调一次就新增一条
> 绑定任务记录 —— 实测重复调用后 `adv_bc_bind_list` 从 9 条涨到 11 条，且新记录
> 最终落到 `status=2`（绑定生效）。**没有"取消绑定任务"的接口**，唯一的撤销路径是
> `bc_un_bind_single` 解绑。
>
> 调用前必须先用 `adv_bc_bind_list` 查一遍，确认该 `adv+bc` 没有已有记录。

```
POST /advertiser/bc_un_bind_single
{"bc_id": "<owner_bc_id>", "un_bind_bc_id": "<要解绑的 BC>", "advertiser_id": "...", "platform": 1}
```

两个 bc 字段不是一个东西：`bc_id` 是账户自己所属的 BC，`un_bind_bc_id` 才是要摘掉的那个
（来自 `get_bind_bc` 或 `adv_bc_bind_list` 的 `bc_id`）。前端还提示：**解绑后需要重新授权**。

批量解绑用 `/advertiser/bc_un_bind_multi`（空 body 报 `广告账号为空`）。

#### 其它 BC 接口

| 接口 | 参数 | 备注 |
|---|---|---|
| `/bc/create` | `tiktok_auth_id`(>0) | 新建 BC |
| `/bc/query_auth` | `auth_link_ex_id` | 查授权链接状态 |
| `/tt/bc/is_adv_bound` | `bc_id` | 某 BC 下是否有账户 |
| `/tt/admin_store/list` | `bc_id` | BC 下的店铺 |
| `/ai_agent/v1/advertiser/pre_bind_bc` | `{task_id, bind_bc_ids}` | AI Agent 路径的预绑定 |

### 4.3 GMVmax 推广系列（核心）

#### 查询

```
POST /front_api/tiktok/gmv_max/list
{"page": 1, "page_size": 10}
→ {"count": 62, "list": [...], "total_data": ...}
```

**实测返回 62 条**。单条字段（33 个，真实数据）：

```json
{
  "advertiser_id": "7686XXXXXXXXXX08", "advertiser_name": "DAMAI-SHOP_X3",
  "campaign_id": "1877XXXXXXXXXX22",
  "campaign_name": "商品 GMV Max_总收入_VUNOVA_1735XXXXXXXXXX50",
  "store_id": "8657XXXXXXXXXX38", "store_name": "",
  "shopping_ads_type": "PRODUCT",
  "product_specific_type": "CUSTOMIZED_PRODUCTS",
  "product_video_specific_type": "AUTO_SELECTION",
  "roas_bid": 20, "budget": 200,
  "schedule_type": "SCHEDULE_FROM_NOW",
  "schedule_start_time": "2026-09-24T17:50:53+08:00",
  "schedule_end_time": "2036-09-21T17:50:53+08:00",
  "status": "STATUS_DELIVERY_OK", "second_status": "CAMPAIGN_STATUS_ENABLE",
  "operation_status": "ENABLE",
  "item_group_ids": ["1735XXXXXXXXXX50"],
  "item_group_ids_str": "[\"1735XXXXXXXXXX50\"]",
  "cost": 0.01, "net_cost": 0, "orders": 0, "cost_per_order": 0,
  "gross_revenue": 0, "roi": 0,
  "port": "CN", "currency": "USD",
  "company_ex_id": "10017794444062955153", "user_ex_id": "auto",
  "create_time": "2026-09-24T09:54:10+08:00", "modify_time": "..."
}
```

#### 新建链路（4 步，全部实测）

```
1) POST /front_api/tiktok/auth_list            → tt_auth_id（实测 3 个授权）
2) POST /front_api/tiktok/gmv_max/store/list   {advertiser_id, tt_auth_id}
3) POST /front_api/tiktok/gmv_max/identity/get {advertiser_id, store_id, store_authorized_bc_id, tt_auth_id}
4) POST /front_api/tiktok/gmv_max/create       {batch:[...], tt_auth_id}
```

第 2 步实测拒绝无权限账户：`code=999 获取店铺列表失败: No permission to operate advertiser: <id>`。
8 个账户里只有 `7642XXXXXXXXXX57`(DAMAI-TK20) 能取到店铺。

第 2/3 步实测输出：

```json
// store/list
{"store_id": "8648XXXXXXXXXX10", "store_authorized_bc_id": "7457XXXXXXXXXX28",
 "is_gmv_max_available": true, "is_owner_bc": true, ...}

// identity/get → 3 个
[{"identity_id": "b0094b9c-c0e3-59dc-a9d6-d4c3cb3def11", "identity_type": "BC_AUTH_TT",
  "display_name": "Thủy Tinh Ca", "identity_authorized_bc_id": "7457XXXXXXXXXX28",
  "product_gmv_max_available": true, "live_gmv_max_available": true,
  "is_running_custom_shop_ads": false}]
```

#### `POST /tiktok/gmv_max/create` 请求体

从 bundle 的 `useSubmit$2` 提取的构造规则：`batch` 里是 campaign 对象，同时传 `tt_auth_id`；
`identity_id_list` / `item_group_list` / `tt_auth_id` / `promote_all_products` 在提交前被 `omit` 掉，
`schedule_start_time` 格式化成 `YYYY-MM-DD HH:mm:ss`，`promote_all_products=true` 时
`product_specific_type` 变成 `ALL` 且 `item_group_ids` 也去掉。

```json
{
  "batch": [{
    "advertiser_id": "7642XXXXXXXXXX57",
    "store_id": "8648XXXXXXXXXX10",
    "store_authorized_bc_id": "7457XXXXXXXXXX28",
    "campaign_name": "商品 GMV Max_总收入_VUNOVA_xxx",
    "shopping_ads_type": "PRODUCT",
    "product_specific_type": "CUSTOMIZED_PRODUCTS",
    "product_video_specific_type": "AUTO_SELECTION",
    "optimization_goal": "VALUE",
    "deep_bid_type": "VO_MIN_ROAS",
    "roas_bid": 3,
    "budget": 300,
    "schedule_type": "SCHEDULE_FROM_NOW",
    "schedule_start_time": "2026-09-24 17:50:53",
    "schedule_end_time": "2036-09-21 17:50:53",
    "item_group_ids": ["1735XXXXXXXXXX50"],
    "identity_list": [{ ...identity/get 的元素... }]
  }],
  "tt_auth_id": 1960
}
```

枚举值（bundle 常量）：
- `shopping_ads_type`: `PRODUCT`
- `product_specific_type`: `CUSTOMIZED_PRODUCTS` | `ALL`
- `product_video_specific_type`: `AUTO_SELECTION`
- `optimization_goal`: `VALUE`
- `deep_bid_type`: `VO_MIN_ROAS`
- `schedule_type`: `SCHEDULE_FROM_NOW`
- 默认值 `roas_bid=3`, `budget=300`（`genDefaultCampaignData`）
- `tt_auth_id` 在 `identity/get` 里是 **Number**，`store/list` 里原样传

#### 前置校验（建广告前必须调）

```
POST /front_api/tiktok/gmv_max/occupied_custom_shop_ads/list
{"batch": [
  {"advertiser_id": "...", "store_id": "...", "occupied_asset_type": "SPU", "asset_ids": ["<item_group_id>"]},
  {"advertiser_id": "...", "store_id": "...", "occupied_asset_type": "IDENTITY_BC_AUTH_TT", "asset_ids": ["<identity_id>"]}
], "tt_auth_id": 1960}
```

`occupied_asset_type` 枚举：`IDENTITY_BC_AUTH_TT` | `SPU`。返回冲突列表，非空时前端弹确认框。

#### 其它 GMVmax 接口

| 接口 | 方法 | 参数 |
|---|---|---|
| `/tiktok/gmv_max/detail` | POST | `{campaign_id}` |
| `/tiktok/gmv_max/update` | POST | 同 create 结构 |
| `/tiktok/gmv_max/copy` | POST | 复制 |
| `/tiktok/gmv_max/refresh` | POST | 手动更新（实测 `{}` 即可） |
| `/tiktok/gmv_max/get_refresh_time` | POST | `{}` → `{"refresh_time":"...","status":2}` |
| `/tiktok/gmv_max/export` | POST | 导出 |
| `/tiktok/gmv_max/group_item_report` | POST | 商品维度报表 |
| `/tiktok/gmv_max/post_item_report` | POST | 素材维度报表 |
| `/tiktok/gmv_max/store/shop_ad_usage_check` | POST | `{advertiser_id, store_id, tt_auth_id}` |
| `/tiktok/gmv_max/import` | POST | 导入 |
| `/tiktok/gmv_max/add_custom_anchor_video` | POST | 加自定义锚点视频 |
| `/ad/gmv_max_store_config/{list,get,delete,list_by_store_id}` | POST | 店铺配置 |

### 4.4 VSA / 普通广告

| 接口 | 方法 | 说明 |
|---|---|---|
| `/tiktok/create_advertisement` | POST | 单个新建 |
| `/tiktok/create_advertisement_new` | POST | **批量新建**（VSA） |
| `/tiktok/ad_detail` | POST | 广告详情 |
| `/tiktok/ad_modify` | POST | 修改广告 |
| `/tiktok/adgroup_detail` / `adgroup_modify` | POST | 广告组 |
| `/tiktok/campaign_detail` / `campaign_modify` | POST | 推广系列 |
| `/tiktok/adgroup_extend` | POST | 扩量 |
| `/tiktok/copy_advertisement` | POST | 复制 |
| `/tiktok/modify_campaign_status_multi` | POST | 批量开关 |
| `/tiktok/get_opt_campaign` | POST | 可选推广系列 |
| `/tiktok/get_videos` / `get_video_url` | POST | 素材 |
| `/tiktok/get_ad_detail_list` | POST | 广告明细 |
| `/ad/smart_plus/v2/create` | POST | Smart+ 新建（走 advertise 域） |
| `/ad/pixel/list` | POST | ⚠ 当前版本 404 |

**批量创建表单默认值**（`batchCreateAdvAPI` 对应的 VSA 表单）：

```json
{"objective_type": "PRODUCT_SALES", "campaign_product_source": "STORE",
 "campaign_name": "", "budget_mode": "BUDGET_MODE_INFINITE", "budget": null,
 "advertiser_id": null}
```

### 4.5 报表

所有报表接口 body 结构一致：

```json
{
  "order_info": {"field": "spend", "order_type": "desc"},
  "page": 1, "page_size": 10,
  "start_date": "2026-09-18", "end_date": "2026-09-24",
  "advertiser_ids": ["..."], "campaign_ids": ["..."],
  "fields": [{"label": "账户名称", "value": "advertiser_name"}]
}
```

| 接口 | 维度 | 实测 |
|---|---|---|
| `/tiktok/advertiser_report` | 广告账户 | 200,count=8 |
| `/tiktok/campaign_report` | 推广系列 | 200,count=0 |
| `/tiktok/adgroup_report` | 广告组 | 200,count=0 |
| `/tiktok/ad_report` | 广告 | 200,count=0 |
| `/tiktok/panel_report` | 面板 | |
| `/advertiser/adv_consume_report` | 消耗 | |
| 各自 `/export` 后缀 | 导出 xlsx（`responseType: blob`） | 实测 200 |

导出接口超时设 12 分钟（前端 `timeout: 12*60*1e3`）。

### 4.6 创建广告日志

```
POST /front_api/advertiser/tt_create_task_list
{"start_date": "2026-09-18", "end_date": "2026-09-24", "page": 1, "page_size": 10}
```

### 4.7 钱包 / 资金（finance-bff）

```
POST https://finance-bff-v1.aiadfly.com/front_api/wallet/list
{"currency": "USD"}
```

**`currency` 必填**，枚举 `[USD JPY THB ...]`（实测传 `CNY` 报 `code=400 value must be in list`）。

返回：`{"wallets":[{"currency":"JPY","balance":0,"balance_usd":0},...],"credit":...,"currency_available":...,"available_usd":...}`

其它：`/wallet/currency/exchange`、`/wallet/wallet/exchange`、`/wallet/sub_company/list`、
`/wallet/company/exchange`、`/wallet/calculate_reverse_exchange_amount`、
`/pay/trade_list`、`/pay/transfer`、`/pay/adv_recharge`、`/pay/adv_amount_clear`、
`/coupon/list`、`/coupon/detail/list`、`/coupon/has_point`
（`/pay/*` 与 `/coupon/*` 的分页用 `page_info: {page, page_size}`）

### 4.8 财务（finance）

```
POST https://finance-v1.aiadfly.com/front_api/finance/settlement/list
{"page": 1, "page_size": 5}
```

注意这组路径**自带 `/finance/` 前缀**，用 `page`/`page_size` 平铺分页：
`/finance/billset/{find,need,update}`、`/finance/settlement/{list,detail/list,detail/export,overdue-t7}`、
`/finance/account/payable/detail`、`/finance/company_detail/list`、
`/finance/rebate/{rule/list,rule_detail/list,adv_detail/list,recharge,export,company_detail/confirm}`

### 4.9 自动化（automation）

分页用 **`page_info` 嵌套**，不是平铺：

```
POST https://automation-v1.aiadfly.com/front_api/tactic/list
{"page_info": {"page": 1, "page_size": 10}}
→ {"page_info": {"total_number":"0","page":1,"page_size":10,"total_page":0}, "list": []}
```

> ⚠ 传平铺 `{"page":1,"page_size":5}` 会得到 `code=500 unknown request error`。

| 分组 | 接口 |
|---|---|
| 策略 | `/tactic/{add,edit,list,find,delete,bind,unbind,status/update}`、`/tactic/adv/list` |
| 日志 | `/tactic_action_log/{list,export}`、`/tactic_change_log/{list,export}` |
| 标签 | `/label/{list,add,del}`、`/label_category/{list,add,del}`、`/advertiser_label_relation/{find,bind,unbind}` |
| 素材 | `/material_group/{list,add,edit,del,detail}`、`/material/{list,edit}` |
| 广告 | `/ad/{list,gmv_adv,gmv_max,google_app}`、`/adgroup/list`、`/campaign/list`、`/advertiser/list` |

### 4.10 AI Agent

Base 是 `https://ai-agent-v1.aiadfly.com`，**路径自带 `/ai_agent/` 段**，且需要 `CompanyExID` 头（缺 header 报 `code=400 WITHOUT_COMPANY_HEADER`）：

```
GET  https://ai-agent-v1.aiadfly.com/ai_agent/v1/user/profile
→ {"has_adv":..., "has_product_type":..., "is_onboarding":..., "is_can_recharge":...}
```

覆盖：对话 `/v1/chat/{list,history,completion}`、会话 `/v1/session_id/{create,get}`、
开户引导 `/v1/ad/guide/adv_apply/reset`、`/v1/advertiser/{apply,pre_bind_bc,adv_bc_bind}`、
GMVmax `/v1/ad/gmv_max/{create,store/list,store/config,identity/list,occupied_custom_shop_ads/list}`、
VSA `/v1/ad/vsa/{create,store/list,video/search,region/search,public_info/get,interest_category/list}`、
`/v1/ocr`、`/v1/qrcode/{generate,query}`、`/v1/rebate/{list,confirm}`、`/v1/contract/sign`、
market 系列 `/ai_agent/market/*`（chat/creative/image/video）

### 4.11 MCP Open

| 接口 | 说明 |
|---|---|
| `GET https://mcp-open.aiadfly.com/decrypt/wlh_login_info` | 需 `encrypted_...` 参数 |
| `POST https://mcp-open.aiadfly.com/oauth/authorize_confirm` | `{"company_ex_id": "..."}` 必填 |

### 4.12 文件上传

```
GET  /front_api/file/sign       → COS 签名
POST /front_api/file/complete   → 上传完成回调
```

### 4.13 覆盖测试结论

对 199 个非写接口逐个实调（`coverage.md` 有全部明细）：

| 状态 | 数量 | 说明 |
|---|---|---|
| OK | 76 | 直接返回数据（含 10 个 xlsx 导出） |
| PARAM | 47 | 路由通，本次调用缺必填参数 |
| NOAUTH | 32 | 路由通，当前账号无该账户/店铺权限 |
| GONE | 33 | **服务端已移除**，见 `spec/unavailable.json` |
| ERROR | 10 | 服务端 5xx，需数据前置条件 |
| AUTH | 1 | 需先开户 |

**33 个已移除的接口**（任何 host 上都不存在，属 Google Ads 功能残留）：

```
/ad/get  /add_custom_anchor_video  /advertisers/list  /auth/list  /auth/multi_edit_company_menu
/campaign/get  /campaigns/list  /campaigns/export  /conversion_actions/list  /export
/geo_targets/suggest  /group_items  /image_assets/list  /languages/list  /list
/material/daily  /material/export  /material/summary  /play_install_conversion_actions/list
/series/chart  /series/summary  /session/list  /snapshots/account/{list,export}
/snapshots/ad_asset_snapshots/{list,export}  /snapshots/ad_group/{list,export}
/snapshots/campaign/{list,export}  /summary  /video_assets/list  /youtube_video/get
```

调用这些会得到 `AdflyRouteError`（`code=404, 404 page not found`），不是静默失败。

**需数据前置条件的接口**（路由正常，但空数据时报 5xx）：

| 接口 | 报错 |
|---|---|
| `/automation/ad/list`、`/adgroup/list` | `failed to find adgroup info` |
| `/automation/campaign/list` | `failed to find campaign info` |
| `/finance/rebate/rule/list`、`rule_detail/list` | `unknown request error`（账号无返点规则） |
| `/finance/rebate/export`、`settlement/detail/export` | `record not found` |
| `/wallet/calculate_reverse_exchange_amount` | `内部错误` |
| `/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list` | `record not found` |

### 4.14 易踩的参数坑（实测）

| 接口 | 坑 |
|---|---|
| `/advertiser/get_auth_link` | **必须带 `?platform=1`**，否则 `code=999 server_invalid_platform` |
| `/advertiser/get_bind_bc` | 无 `advertiser_id` 时返回 `data=null`（不是报错） |
| `/tiktok/gmv_max/identity/get` | 必须同时给 `advertiser_id` + `store_id` + `store_authorized_bc_id` + `tt_auth_id` |
| `/tiktok/gmv_max/store/list` | 对无 TikTok 权限的账户报 `No permission to operate advertiser: <id>` |
| `/wallet/list` | `currency` 必填，枚举 `[USD JPY THB ...]` |
| `/user/check_fa` | 只用于探测，返回值与登录接口不同 |
| `/finance/billset/need` | 存在但响应极慢（>10s），同组 `/billset/find` 正常 |
| `/ai_agent/*` | 需要 `CompanyExID` 头，缺了报 `code=400 WITHOUT_COMPANY_HEADER` |
| 导出接口 | 返回 xlsx 二进制，用 `c.download(...)`；用 `c.call` 会抛"二进制响应"提示 |

## 5. 分页与导出约定

| 服务 | 分页 | 导出 |
|---|---|---|
| front / advertise / finance / ai_agent | `{"page":1,"page_size":N}` 平铺 | 路径加 `/export` |
| automation | `{"page_info":{"page":1,"page_size":N}}` | 同上 |
| finance_bff（pay/coupon） | `{"page_info":{...}}` | 同上 |

分页响应：`{"count": N, "list": [...], "total_data": ...}`；
automation 是 `{"page_info": {...}, "list": [...]}`。

导出接口返回二进制（`responseType: blob`），客户端用 `c.download(...)` 落盘。

---

## 6. 代码与产物

| 文件 | 说明 |
|---|---|
| `adfly_api/` | Python 客户端包（293 个方法） |
| `adfly_api/spec/endpoints.json` | 293 接口清单（backend/method/path/前端函数名） |
| `adfly_api/spec/routes.json` | 运行时解析出的 host 缓存 |
| `api_tables.md` | 全量接口 Markdown 表格 |
| `extract_endpoints.py` | 从 bundle 重新提取接口（版本升级后重跑） |
| `gen_modules.py` | 由清单生成 Python 模块 |
| `verify_client.py` | 实机验证脚本 |
| `test_routing.py` | 多 host 路由验证 |
| `probe_routes.py` / `probe_matrix.py` | 路由与前缀探测工具 |
| `code/v2/bundle.pretty.js` | 美化后的线上 bundle（197060 行） |

---

## 6. 参数参考（从服务端校验器提取）

服务端用的是 protoc-gen-validate 风格校验，报错直接给出消息名、字段路径和约束：

```
invalid GetPixelListRequest.AdvertiserId: value length must be at least 1 runes
        └─ proto 消息          └─ 字段              └─ 约束
```

据此提取了 **34 个接口 / 55 个必填字段**，其中 8 个用真实数据完全跑通，
26 个字段摸清后被业务层拒绝（数据不存在/无权限）。完整数据在 `spec/params.json`，
已回填进各模块方法的 docstring：

```python
>>> help(c.ads.get_pixel_list)
POST /ad/pixel/list  (前端 getPixelListAPI)
实测必需字段(1 个,字段已摸清): advertiser_id:string
可用 body 样例: {"advertiser_id": "7689XXXXXXXXXX05", "page": 1, "page_size": 5}
```

字段类型分布：string 44 / number 8 / enum 3。

典型多字段接口：

| 接口 | 实测必需字段 |
|---|---|
| `/ai_agent/v1/ad/gmv_max/identity/list` | advertiser_id, store_id, store_authorized_bc_id (+tt_auth_id) |
| `/ai_agent/v1/ad/gmv_max/store/product/list` | advertiser_id, bc_id, store_id |
| `/ai_agent/v1/ad/gmv_max/store_id/validate` | advertiser_id, store_id, tt_auth_id |
| `/wallet/list` | currency(枚举 `[USD JPY THB]`) |
| `/tactic/find`、`/tactic/adv/list` | tactic_ex_id |
| `/ai_agent/v1/ocr` | url, type(枚举) |

**提取方式**：反复调用接口，把服务端抱怨的字段用合成值填上，直到它不再抱怨。
合成值优先用真实 id（真实广告账户、店铺、系列），所以部分接口能真正返回数据而不只是过校验。
脚本 `extract_params.py`，产物 `spec/params.json`。

## 7. 结构化辅助层（helpers）

模块方法是 1:1 薄封装，payload 要自己拼。`adfly_api/helpers.py` 把高频工作流封起来，
带**本地参数校验**（不用等服务端 400）：

```python
from adfly_api import AdflyClient
from adfly_api import helpers as H

c = AdflyClient()

# 钱包：currency 枚举本地拦截，不用等服务端报 400
H.wallet_balances(c, "USD")                       # {'wallets': [...], 'available_usd': 55}

# 分页：automation / pay / coupon 必须用嵌套 page_info
c.auto.automation_get_list_tactic(H.paging_nested(1, 20))
c.wallet.get_coupon_list(H.paging_nested(1, 20))
c.ads.get_advertiser_list(H.paging_flat(1, 50))

# 报表：日期默认最近 7 天，一次拉全
for row in H.iter_report(c, "/tiktok/advertiser_report", days=30):
    print(row)

# 建 GMVmax：找出**真正可用**的账户（实测 8 个里只有部分能取到店铺）
ready = H.find_gmv_max_ready_account(c)
acct = ready[0]
ids = H.gmv_max_identities(c, advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
                           store_authorized_bc_id=acct["store_authorized_bc_id"],
                           tt_auth_id=acct["tt_auth_id"])
payload = H.gmv_max_create_payload(
    advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
    store_authorized_bc_id=acct["store_authorized_bc_id"],
    campaign_name="商品 GMV Max_TEST", roas_bid=3, budget=300,
    tt_auth_id=acct["tt_auth_id"], item_group_ids=["1735XXXXXXXXXX50"],
    identity_list=ids[:1])
# payload 直接丢给 c.ads.create_gmv_max_ad(payload)

# 改已有系列：自动剥离只读字段再 merge
existing = c.ads.get_gmv_max_list({"page": 1, "page_size": 1})["list"][0]
c.ads.edit_gmv_max_ad(H.gmv_max_edit(existing, budget=500, tt_auth_id=acct["tt_auth_id"]))

# BC 绑定/解绑
H.bc_bind_body(bc_id="...", advertiser_ids=["..."])
H.bc_unbind_body(bc_id="...", advertiser_id="...")
```

本地校验覆盖：`store_id` / `store_authorized_bc_id` / `campaign_name` 必填，
`roas_bid`、`budget` > 0，固定排期必须给开始时间，非全店推广必须给 `item_group_ids`，
`currency` 枚举，`order_type` 枚举，分页 >= 1 —— 全部在发请求前拦掉。
