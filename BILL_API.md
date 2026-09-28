# 账单模块接口文档

逆向来源：线上 build `NUMBER_REDACTED`
- 主 bundle `index-CI-PN84-.js` 的 finance 模块段（15 个 API 定义）
- 懒加载 chunk `index-rhJNxbMm.js`（46 KB）—— `/bill-manage` 页面的实际页面代码
- 实机调用确认

## 1. 页面结构

路由 `/bill-manage`（`PAGE_ROOT_ROUTER_MAP.billManage`）。

页面代码只从主 bundle 引入 3 个账单相关 API：

| chunk 别名 | 主 bundle 函数名 | 接口 |
|---|---|---|
| `Z` | `getSettlementListAPI` | `POST /finance/settlement/list` |
| `V` | `getSettlementOverdueT7API` | `POST /finance/settlement/overdue-t7` |
| `U` | `payAdvAmountClearAPI` | `POST /pay/adv_amount_clear` |

> 别名映射是通过读主 bundle 末尾的 `export { 内部名 as 别名 }` 表（294 条）反查出来的。

## 2. 表格列（从 i18n 提取的完整字段清单）

| i18n key | 列名 | 说明 |
|---|---|---|
| `bill.manage.media_platform` | 媒体平台 | TikTok / GG / FB / ASA |
| `bill.manage.advertiser_name` | 广告账户名称 | |
| `bill.manage.advertiser_id` | 广告账户ID | |
| `bill.manage.advertiser_port` | 广告账户端口 | |
| `bill.manage.port` | 端口 | |
| `bill.manage.bill_period` | 账单周期 | |
| `bill.manage.generate_time` | 生成时间 | |
| `bill.manage.due_date` | 账单截止日期 | |
| `bill.manage.bill_status` | 账单状态 | 见 §4 枚举 |
| `bill.manage.completion_time` | 完结时间 | |
| `bill.manage.currency` | 币种 | |
| `bill.manage.bill_amount` | 账单金额 | |
| `bill.manage.paid_amount` | 已支付金额 | |
| `bill.manage.period_recharge` | 周期内充值 | |
| `bill.manage.period_balance` | 周期内余额 | |
| `bill.manage.promotion_cost` | 推广费用 | |
| `bill.manage.promotion_service_fee` | 推广服务费 | |
| `bill.manage.tax` | 税金 | |
| `bill.manage.coupon_amount` | 优惠券使用金额 | |
| `bill.manage.actions` | 操作 | 查看明细 / 查看INV / 下载明细表 |

筛选器：日期范围（`bill.manage.date_range_placeholder`）、账单状态（`bill.manage.status_placeholder`）、端口（`bill.manage.port_placeholder`）。

## 3. 接口清单

### 3.1 账单列表

```
POST https://finance-v1.aiadfly.com/front_api/finance/settlement/list
```

实测：`page` / `page_size` / `start_date` / `end_date` 都被接受，但**你这个公司当前返回 `count=0`** ——
没有任何账单（`billset/need` 返回 `need:false`，`bill_tips` 返回 `has_generated_bill:false`）。
所以**列表的响应字段没能实机取样**，上表列名来自页面代码而非真实数据。

参数形式（与其它 finance 接口一致）：

```json
{"page": 1, "page_size": 20,
 "start_date": "2026-08-01", "end_date": "2026-09-30",
 "bill_status": 1, "port": "CN", "currency": "USD"}
```

响应信封：`{"code":0, "data":{"count":N, "list":[...], "total_data":...}}`

### 3.2 账单明细

```
POST /front_api/finance/settlement/detail/list
```
同样返回 `count=0`（无账单）。

### 3.3 明细导出

```
POST /front_api/finance/settlement/detail/export
```
实测落盘成功，但只有 137 字节 —— 空表。参数形式：

```json
{"company_ex_id": "10017794444062955153", "page": 1, "page_size": 50}
```

> 137 字节是 xlsx 的最小合法结构，说明**导出接口本身通**，只是没有数据可导。

### 3.4 账单设置（有真实数据）

```
POST /front_api/finance/billset/find      → 查当前设置
GET  /front_api/finance/billset/need      → 是否需要补设置  {"need": false}
POST /front_api/finance/billset/update    → 更新设置（写操作）
```

`billset/find` 实测返回：

```json
{
  "bill_set_ex_id": "32017896144378506309",
  "company_ex_id": "10017794444062955153",
  "contract_email": "user@example.com",
  "recipient_email": "user@example.com",
  "cc_email": "",
  "cus_invoice_name": "广西大迈进出口贸易有限公司",
  "cus_invoice_address": "中国(广西)自由贸易试验区南宁片区凯旋路15号南宁绿地中心3号楼602",
  "self_invoice_info_id": "",
  "tt_bill_cycle_type": 0,  "tt_pay_term": 0,
  "gg_bill_cycle_type": 0,  "gg_pay_term": 0,
  "fb_bill_cycle_type": 0,  "fb_pay_term": 0,
  "asa_bill_cycle_type": 0, "asa_pay_term": 0
}
```

**这是账单模块唯一能取到真实数据的接口。** 结构说明：

| 字段组 | 含义 |
|---|---|
| `contract_email` | 签约邮箱 |
| `recipient_email` / `cc_email` | 账单接收邮箱 / 抄送（多个用英文逗号分隔） |
| `cus_invoice_name` / `cus_invoice_address` | 发票抬头 / 地址 |
| `self_invoice_info_id` | 自定义开票信息 ID（空 = 未启用） |
| `{tt,gg,fb,asa}_bill_cycle_type` | 各平台的**账单周期类型**（0 = 默认） |
| `{tt,gg,fb,asa}_pay_term` | 各平台的**付款期限**（0 = 默认） |

四个平台前缀：`tt`=TikTok、`gg`=Google、`fb`=Facebook、`asa`=Apple Search Ads。

### 3.5 应付明细

```
POST /front_api/finance/account/payable/detail
{"company_ex_id": "10017794444062955153"}
```

实测返回（无账单时）：
```json
{"month_details": {}, "total_cost": {}, "total_late_fee": {},
 "overdue_bill_count": 0, "total_topay_amount_usd": 0, "total_late_fee_usd": 0}
```

`month_details` / `total_cost` / `total_late_fee` 是**按币种 keyed 的 map**（空对象说明无数据）。

### 3.6 逾期检查

```
POST /front_api/finance/settlement/overdue-t7
{"company_ex_id": "10017794444062955153"}
→ {"has_overdue_t7": false}
```
账单页用它决定是否显示"您有逾期账单，请回款后再进行操作"的拦截提示。

### 3.7 账单提示

```
GET https://ai-agent-v1.aiadfly.com/ai_agent/pay/bill_tips
→ {"has_generated_bill": false, "has_overdue_bill": false}
```

> 注意这个在 **ai_agent** 服务上，不在 finance。

### 3.8 关联：钱包流水里有 bill_id

```
POST https://finance-bff-v1.aiadfly.com/front_api/pay/trade_list
{"page_info": {"page": 1, "page_size": 20}}
```

实测 `total_number=20`。单条字段（22 个）：

```json
["record_id", "type", "time", "status", "change_amount", "balance", "pre_balance",
 "currency", "currency_amount", "company_ex_id", "company_name", "bill_id",
 "consumption_tax", "country", "wallet_currency", "reject_reason", "adv_port",
 "actual_amount", "pay_channel", "pay_channel_name", "operation_source",
 "display_pay_channel"]
```

**`bill_id` 就是账单与钱包流水的关联键** —— 账单支付会在钱包流水里以带 `bill_id` 的记录出现。
这是在没有账单数据的情况下，唯一能确认"账单 → 资金"这条链路的结构证据。

`type` 枚举（从流水实证 + i18n）：`1`=钱包充值、`3`=广告账户充值、`5`=广告账户清零、`6`=返还类。

### 3.9 返点（账单相关，当前全 500）

```
POST /front_api/finance/rebate/rule/list
POST /front_api/finance/rebate/rule_detail/list
POST /front_api/finance/rebate/adv_detail/list
POST /front_api/finance/rebate/company_detail/confirm   (写)
POST /front_api/finance/rebate/recharge                 (写)
POST /front_api/finance/rebate/export
POST /front_api/finance/company_detail/list
```

实测**全部返回 `code=500 unknown request error`**，带 `company_ex_id` 也一样。
判断：**你的公司没有配置返点规则**，服务端在这种情况下的处理是抛 500 而不是返回空列表（服务端缺陷）。

## 4. 账单状态枚举

从 bundle 的 `billSendStatusTypeEunm` + `billSendStatusTypeMap` 提取：

| 值 | 内部名 | 英文 | 马来文 |
|---|---|---|---|
| 1 | `due` | 待付款 | Menunggu bayaran |
| 2 | `partiallyPay` | 部分付款 | Bayaran sebahagian |
| 3 | `finished` | 已完成 | Selesai |
| 4 | `overdue` | 逾期 | Lewat bayar |
| 5 | `postponeding` | 延期处理中 | Dalam penangguhan |
| — | `deferred` | 已延期 | Ditangguh |
| — | `regenerating` | 重新生成中 | Sedang dijana semula |
| — | `waitToSend` | 待发送 | Menunggu penghantaran |

> 枚举里有 8 个值，但筛选下拉 `billSendStatusOptions` **只列了 1~5**。
> 另外 3 个（`deferred` / `regenerating` / `waitToSend`）没进筛选器 —— 它们应该只是列表里的展示态，
> 不能用作查询条件。
>
> **中文文案没抓到**：bundle 只打包了 ms-MY / en-US / th-TH 三种 i18n，中文走服务端下发
> （`getI18nText` / 运行时拉取）。所以中文列名取自页面上实际看到的，不是从 bundle 提取的。

## 5. 未解出的部分

| 项 | 状态 | 原因 |
|---|---|---|
| `settlement/list` 真实响应字段 | **未取样** | 公司无账单，`count=0` |
| `settlement/detail/list` 字段 | **未取样** | 同上 |
| `bill_cycle_type` / `pay_term` 的枚举值 | **未解出** | 当前全是 0，bundle 里没有映射表，需要页面上的下拉选项 |
| 返点接口的 body 结构 | **未解出** | 全部 500，服务端在无配置时不返回校验错误，拿不到字段提示 |

**要补齐这几项，需要一个有账单数据的账号**，或者你打开账单设置页把
"账单周期"和"付款期限"下拉里的选项念给我。

## 6. 复现命令

```bash
cd "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly"

# 账单设置(有数据)
python3 -m adfly_api call finance POST /finance/billset/find '{}'
python3 -m adfly_api call finance GET  /finance/billset/need

# 账单列表(当前空)
python3 -m adfly_api call finance POST /finance/settlement/list '{"page":1,"page_size":20}'

# 应付明细 / 逾期
python3 -m adfly_api call finance POST /finance/account/payable/detail '{"company_ex_id":"10017794444062955153"}'
python3 -m adfly_api call finance POST /finance/settlement/overdue-t7 '{"company_ex_id":"10017794444062955153"}'

# 账单提示
python3 -m adfly_api call ai_agent GET /pay/bill_tips

# 钱包流水(含 bill_id)
python3 -m adfly_api call finance_bff POST /pay/trade_list '{"page_info":{"page":1,"page_size":20}}'
```
