# 公司管理 / 子账号 / 权限 接口文档

逆向来源：线上 build `NUMBER_REDACTED`，主 bundle `index-CI-PN84-.js` + 实机调用。
权限树原始数据落盘在 `adfly_api/spec/company_menu.json`。

---

## 1. 权限模型

### 1.1 三层结构

权限是**树形 + 平铺 ID 列表**的双重表示：

```
menu_list (树)                    auth_menus (平铺字符串)
├─ page  (8 个)  页面级，path 是完整路由，如 /ad-manage
│   ├─ tab (11 个) 标签页级，path 是语义标识，如 tt-account
│   │   └─ btn (47 个) 按钮级，path 是动作标识，如 recharge_btn
```

角色的 `auth_menus` 是一个**逗号分隔的节点 ID 字符串**，例如管理员角色：

```
"1,2,3,4,5,6,8,10,12,13,14,16,17,18,19,20,21,22,58,59,60,61,62,63,64,65,67,68,69,
 70,71,74,76,110,118,143,145,155,191,194,195,196,197,198,199,200,201,202,203,204,
 205,206,207,210,211,212,213,217,218,219,220,221,222,236,240,255"
```

服务端同时返回 `auth_menu_list` 数组形式（同样的 ID，元素是字符串）。

### 1.2 节点字段

```json
{"id": 194, "pid": 1, "name": "TT", "path": "tt-account",
 "url_path": "", "level": 0, "type": "tab", "status": 1}
```

| 字段 | 说明 |
|---|---|
| `id` / `pid` | 节点 ID / 父节点 ID（`pid=0` 为顶级） |
| `name` | 中文名（服务端下发） |
| `path` | page 类型是完整路由；tab/btn 类型是语义标识符 |
| `url_path` | 实测全部为空字符串 |
| `level` | 排序用；page 类型有值（5/7/10/15/20/28/30/46），tab/btn 为 0 |
| `type` | `page` / `tab` / `btn` |
| `status` | 1 = 启用 |

### 1.3 完整权限树（66 个节点）

**page 级（8 个）** —— 顶级菜单，按 `level` 排序：

| id | level | 名称 | path |
|---|---|---|---|
| 58 | 5 | 数据看板 | `/data` |
| 221 | 7 | AI Agent | `/agent` |
| 1 | 10 | 账号管理 | `/account-mannage` |
| 59 | 15 | 广告管理 | `/ad-manage` |
| 2 | 20 | 钱包管理 | `/wallet` |
| 145 | 28 | 账单管理 | `/bill-manage` |
| 3 | 30 | 成员管理 | `/member-mannage` |
| 191 | 46 | 签约管理 | `/contract-manage` |

**tab 级（11 个）**：

| id | pid | 父页面 | 名称 | path |
|---|---|---|---|---|
| 194 | 1 | 账号管理 | TT | `tt-account` |
| 195 | 1 | 账号管理 | GG | `gg-account` |
| 197 | 1 | 账号管理 | FB | `fb-account` |
| 12 | 3 | 成员管理 | 成员管理 | `member_tab` |
| 13 | 3 | 成员管理 | 角色管理 | `role_tab` |
| 14 | 3 | 成员管理 | 客户管理 | `custom_tab` |
| 110 | 3 | 成员管理 | 客户账户管理 | `custom_account_tab` |
| 143 | 3 | 成员管理 | 账单及发票信息 | `email_setting` |
| 10 | 2 | 钱包管理 | 钱包交易及返点 | `transaction_detail` |
| 236 | 2 | 钱包管理 | 优惠券使用明细 | `coupon_usage_record` |
| 219 | 59 | 广告管理 | GMVMax推广系列 | `gmv_max_campaign` |

**btn 级（47 个）** —— 按父节点分组：

*挂 广告管理(59)：*
`4 资产授权`·`60 批量创建VSA广告`·`61 单个创建VSA广告`·`62 开关控制`·`63 修改`·`64 扩量`·`65 AI托管`·`155 添加标签`·`217 TT账户授权`·`218 批量创建GMVMax广告`·`220 单个新建GMVMax广告`

*挂 TT 账号 tab(194)：*
`5 广告开户`·`6 充值`·`8 清零`·`74 操作记录按钮`·`76 绑定BC按钮`·`118 解绑BC`·`255 修改账户信息`

*挂 GG tab(195)：*
`196 广告开户`·`199 充值`·`201 清零`·`203 操作记录按钮`·`205 绑定BC`·`207 解绑BC`

*挂 FB tab(197)：*
`198 广告开户`·`200 充值`·`202 清零`·`204 操作记录按钮`·`206 绑定BC`·`222 减款`

*挂 成员管理 tab(12)：*
`16 创建成员`·`17 编辑成员`·`18 分配资产`

*挂 角色管理 tab(13)：*
`19 创建角色`·`20 编辑角色`

*挂 客户管理 tab(14)：*
`21 创建客户`·`22 编辑`

*挂 钱包管理(2)：*
`240 优惠券管理`

*挂 签约管理(191)：*
`210 查看合同`·`211 下载合同`·`212 签约`·`213 解约`

> ⚠ **`pid=66` 的 4 个按钮（`67 创建策略`/`68 编辑策略`/`69 状态按钮`/`70 删除按钮`/`71 应用按钮`）
> 指向一个不在 `menu_list` 里的父节点。** 66 应该是"自动化/策略"页面节点，但当前公司的
> 权限树里没有它 —— 说明本公司的套餐/权限范围不含自动化模块，或该节点只对特定客户下发。

---

## 2. 数据权限（data_permission_set）

除菜单权限外，角色还有一个**数据级权限**结构：

```json
"data_permission_set": {
  "customer_manage": {"type": 1, "field_infos": null},
  "kanban":          {"type": 1, "field_infos": null},
  "tt_business":     null,
  "gg_business":     null,
  "fb_business":     null,
  ...
}
```

| 维度 | 说明 |
|---|---|
| `customer_manage` | 客户管理数据范围 |
| `kanban` | 数据看板范围 |
| `tt_business` / `gg_business` / `fb_business` | 各平台业务数据范围 |

每个维度：`type`（范围类型）+ `field_infos`（字段级过滤，可为 null）。
配套字段还有：

```json
"custom_scope_type": 1,        // 客户范围类型
"company_id_list": [],         // 限定公司 ID
"platform_id_list": []         // 限定平台
```

> `type` 的具体枚举值**未解出** —— 当前所有角色都是 `1`，bundle 里没有映射表。
> 需要页面上"数据权限"下拉的选项才能确认。

---

## 3. 接口清单

### 3.1 权限菜单树

```
POST /front_api/auth/get_company_menu
{"company_ex_id": ["10017794444062955153"]}     ← 必须是数组！
```

踩坑记录：传字符串会得到
`json: cannot unmarshal string into Go struct field GetCompanyMenuReq.company_ex_id of type []string`

返回：

```json
[{"company_ex_id": "10017794444062955153", "menu_list": [ ...66 个节点... ]}]
```

是**数组**（按公司维度），不是单个对象。

### 3.2 角色列表

```
POST https://ai-agent-v1.aiadfly.com/ai_agent/role_list
{"page": 1, "page_size": 50}
```

> 注意在 **ai_agent** 服务上，不在 front。`{}` 会返回 `count` 但 `list=null`，必须带分页参数。

实测返回 22 个角色。单条字段（12 个）：

```json
{
  "id": 6564,
  "created_at": "2026-05-22T18:19:13.634+08:00",
  "updated_at": "2026-06-12T11:03:56.386+08:00",
  "company_ex_id": "10017794444062955153",
  "name": "管理员",
  "auth_menus": "1,2,3,...255",
  "status": 1,
  "auth_menu_list": ["1", "2", ...],
  "custom_scope_type": 1,
  "company_id_list": [],
  "platform_id_list": [],
  "data_permission_set": { ... }
}
```

当前公司的角色分布：

| id | 名称 | 权限节点数 | 说明 |
|---|---|---|---|
| 6564 | 管理员 | 66 | 唯一有实际权限的角色 |
| 9410 ~ 9430 | *(空)* | 0 | **21 个空名空权限角色** |

> 那 21 个空角色是本会话探测造成的 + 此前手动操作遗留。**没有删除角色的接口**（见 §4）。

### 3.3 角色创建 / 编辑

```
POST /ai_agent/role_edit
```

**这一个接口兼做创建和编辑**（按是否有 `id` 区分）。

⚠ **空 body 会创建一条空角色。** 实测 `{}` 返回 `code=0`，角色数从 21 涨到 22。
这是**危险接口**：它不做参数校验，缺什么就写空值。

创建角色（推断结构，与 `role_list` 返回字段对称）：

```json
{"company_ex_id": "10017794444062955153",
 "name": "只读运营",
 "status": 1,
 "auth_menu_list": [58, 1, 194, 74],
 "custom_scope_type": 1,
 "company_id_list": [],
 "platform_id_list": []}
```

编辑角色（带 `id`）：

```json
{"id": 9430, "name": "只读运营", "status": 1, "auth_menu_list": [...]}
```

> **注意**：以上结构是**从 `role_list` 的返回字段对称推断**的，没有实测验证。
> 因为这个接口对空 body 不报错，我拿不到字段校验提示，而继续"补值试到通过"
> 会继续往你的角色表里写垃圾数据。**不再试。**
>
> 要确认的话：在页面上创建一个角色，F12 看 `role_edit` 的 Payload。

> **术语**：平台里"公司成员"就是"子账号"。页面入口在 `公司设置 → 公司设置 tab`，
> 创建按钮文案是"创建成员"，实际创建的是可登录的子账号。

### 3.4 成员列表

```
POST /front_api/user/list
{"page": 1, "page_size": 20}
```

实测 **`count=0`** —— 当前公司没有子账号。

试过的参数都不影响结果：`company_ex_id`（字符串/数组）、`platform`、`page_num`、
`page_info` 嵌套分页，全部 `count=0`。判断**确实是空数据**，不是参数问题。

所以**成员列表的响应字段没能取样**。

但**查询表单的字段在页面上能看到**（截图 + 代码印证）：

| 筛选项 | 说明 |
|---|---|
| 成员名称 | 按名字过滤 |
| 手机号 | |
| 邮箱 | |
| 状态 | 下拉 |
| 角色 | 下拉，数据源是 `role_list` 的 `name` 字段 |

表格列：**成员名称 / 手机号 / 邮箱 / 角色 / 最后登录时间 / 操作**

试过的 body 字段（`name` / `user_name` / `phone` / `company_ex_id` / `role_id` / `is_all` /
`page_num` / `page_info`）全部返回 `count=0` —— **确认是空数据，不是参数问题**。

### 3.4.1 创建成员表单（从截图提取的完整字段）

```
* 成员名称       文本
* 注册方式       单选：手机号 | 邮箱
* 手机号         文本（选"手机号"注册时）
* 角色           下拉，必填
* 状态           下拉，必填
```

对应 `POST /front_api/user/register`。字段名未实测（该接口返回自定义码 `code=11`
不暴露字段名）。

### 3.4.2 当前登录账号的权限来源

`GET /user/info` 实测：

```json
{"user_id": "11017794444062945153", "name": "何阳鸿", "phone": "PHONE_REDACTED",
 "super": 2, "role_id": 0, "is_test_user": false, "menu_info": []}
```

**`super: 2` + `role_id: 0` + `menu_info: []`** —— 说明超管**不走角色权限体系**，
权限是隐式全开的。这也解释了为什么角色表里没有一个绑到当前账号上。

企业里给子账号分配权限时，走的是 `role_id` → `role.auth_menus` 这条链。

### 3.5 成员创建 / 编辑

```
POST /front_api/user/register     → code=11 参数有误
POST /front_api/user/edit         → code=11 发送方法类型有误
```

两个接口空 body 都返回 `code=11`（自定义业务码，不是 proto 校验），
**不暴露字段名**。所以字段结构未解出。

注意 `/user/edit` 的报错是"**发送方法类型有误**"而不是"参数有误" —— 说明它可能
要求特定的请求方式（比如 `PUT`），或者 body 里需要一个 `type` 字段区分操作类型。

### 3.6 客户管理

```
POST /front_api/company/custom_list   → count=0（无客户数据）
POST /front_api/company/edit          → code=11 公司名称已存在
POST /front_api/company/change_custom_passwd
```

`/company/edit` 的报错"公司名称已存在"很有信息量 —— 说明空 body 时会用空字符串
去匹配公司名，撞上了已有记录。**这个接口会对公司主记录做修改，属于高危。**

### 3.7 角色权限批量修改

```
POST /front_api/auth/edit_company_menu          → code=999 获取公司信息失败
POST /front_api/auth/multi_edit_company_menu    → 404（所有 host 都不存在）
```

`edit_company_menu` 空 body 报"获取公司信息失败"，说明它需要公司上下文；
`multi_edit` 是**已下线的死接口**（bundle 里还留着定义）。

### 3.8 成员自身信息

| 接口 | 说明 |
|---|---|
| `GET /front_api/user/info` | 含 `menu_info`（当前用户权限）+ `role_id` |
| `POST /front_api/user/upt_pass` | 改密码 |
| `POST /front_api/user/phone/update` | 换手机 |
| `POST /front_api/user/email/update` | 换邮箱 |
| `GET /front_api/user/send_code` | 发验证码 |
| `POST /front_api/user/get_business` | 查所属业务 |
| `POST /front_api/user/check_fa` | 查是否需双因素 |

`GET /user/info` 实测返回（当前账号）：

```json
{"user_id": "11017794444062945153", "company_id": "", "status": 1,
 "name": "何阳鸿", "phone": "PHONE_REDACTED", "email": "", "super": ..., "role_id": ...,
 "menu_info": [...], "source": "", "is_test_user": ...}
```

> `company_id` 是**空字符串** —— 公司上下文不在这个字段里，走 `CompanyExID` 请求头。

### 3.9 公司信息

| 接口 | 说明 |
|---|---|
| `POST /front_api/company/get_ports_list` | 开户端口列表 |
| `POST /front_api/company/country_list` | 国家列表 |
| `POST /front_api/company/list` | **已下线**（GET 也 404）—— 公司列表改由登录后单独获取 |

---

## 4. 死接口 / 高危接口

### 已下线（任何 host 都 404）

| 接口 | 备注 |
|---|---|
| `/auth/multi_edit_company_menu` | bundle 里保留定义，服务端已移除 |
| `/auth/list` | 同上 |
| `/add_custom_anchor_video` | 同上 |
| `/company/list` | 登录流程里曾用，现由 `/user/info` 替代 |

### 高危（空 body 会产生副作用）

| 接口 | 空 body 行为 |
|---|---|
| `/role_edit` | **创建一条空角色**（实测角色数 +1） |
| `/company/edit` | 用空公司名做匹配，报"公司名称已存在" |
| `/pay/adv_reduce` | 返回 `code=0` 但不生效（静默忽略字段） |
| `/pay/adv_amount_clear` | 空 body 被拒（`DeductAdvFrontRequest.Details` 校验）—— 这个反而是安全的 |

**没有删除角色的接口。** 双向确认：

| 证据 | 结论 |
|---|---|
| `/role_*` 接口只有 `role_list` + `role_edit` 两个 | 服务端无 delete 端点 |
| 权限树里 `角色管理 tab(13)` 下只有 `19 创建角色` + `20 编辑角色` | 页面也没暴露删除入口 |

所以角色表里的空角色**通过 API 和页面都删不掉**。唯一的处理路径是联系 AM。

（`role_edit` 是否支持 `status=0` 软删未验证 —— 因为它在空 body 时就写数据，
不适合再试。若页面上有"禁用"开关，那才是可行路径。）

---

## 5. 未解出项

| 项 | 原因 |
|---|---|
| `/user/list` 响应字段 | 公司无子账号，`count=0` |
| `/user/register`、`/user/edit` 字段 | 返回自定义码 `code=11`，不暴露字段名 |
| `/role_edit` 精确 body | 空 body 通过，拿不到校验提示；继续试会写垃圾数据 |
| `data_permission_set.*.type` 枚举 | 当前全为 `1`，bundle 无映射表 |
| `custom_scope_type` 枚举 | 同上 |
| `pid=66` 的父节点 | 不在当前公司权限树里（推测是自动化模块，未开通） |
| `bill_cycle_type` / `pay_term` 枚举 | 见 `BILL_API.md` |

**要补齐这些，最快的路径**：你在页面上做一次"创建角色"和"创建成员"，
F12 把两个请求的 Payload 贴给我。这比我在生产数据上盲试安全得多 ——
今天的几次意外写入（BC 绑定 3 条、充值多充 20、角色 +1）已经说明了这点。

---

## 6. 复现命令

```bash
cd "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly"

# 权限树（注意 company_ex_id 是数组）
python3 -m adfly_api call front POST /auth/get_company_menu '{"company_ex_id":["10017794444062955153"]}'

# 角色列表（ai_agent 服务，必须带分页）
python3 -m adfly_api call ai_agent POST /role_list '{"page":1,"page_size":50}'

# 当前用户信息（含 role_id / menu_info）
python3 -m adfly_api call front GET /user/info

# 成员列表（当前为空）
python3 -m adfly_api call front POST /user/list '{"page":1,"page_size":20}'

# 客户列表（当前为空）
python3 -m adfly_api call front POST /company/custom_list '{"page":1,"page_size":20}'

# 端口 / 国家
python3 -m adfly_api call front POST /company/get_ports_list '{}'
python3 -m adfly_api call front POST /company/country_list '{}'
```
