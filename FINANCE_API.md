# seller 中心【财务】板块 —— 全量接口手册

> 对应页面：
> - `bills` — https://seller.tiktokshopglobalselling.com/finance/bills?subTab=on-hold&tab=overview
> - `deposit` — https://seller.tiktokshopglobalselling.com/deposit
> - `bill-payment` — https://seller.tiktokshopglobalselling.com/finance/bill-payment?shop_region=VN

> **来源**：从财务页自己的前端 bundle 抽取（`notes/fin_js/` 81 个 + `notes/fin_mf/` 19 个）。
> 不是猜的，每个路径都带抽到的调用点方法名。

**共 1024 个路径**，其中财务相关 **244 个**，随页面一起加载但非财务的 780 个（IM / i18n / 物流 / 入驻等，见附 C）。

| 实测标记 | 含义 |
|---|---|
| ✅ | **三个财务页首屏真实打过**（CDP 真流量捕获，218 个请求） |
| ◑ | 真流量里出现过，**且静态抽取的方法标错了** —— 表里已是真值 |
| 空 | 静态抽取到，未在首屏窗口内出现（多在二级 tab / 弹窗里懒调用） |

| 方法分布 | 数量 |
|---|---|
| `POST` | 155 |
| `?` | 82 |
| `GET` | 7 |

---

## 0. 总览

### 0.1 三个请求前缀（别混）

| 前缀 | 网关 | 用途 |
|---|---|---|
| `/api/v1/pay/...` | 旧卖家网关 | 结算 / 提现 / 打款 / 对账单（bills、deposit 页主用） |
| `/api/v1/finance/...` | 旧卖家网关 | 充值收银台（purchase）、收单资金（acquiring） |
| `/api/oec/pay/merchant/...` | **oec 网关** | 新版对账单（bills 页主体），**无版本段** |
| `/api/oec/finance/...` | **oec 网关** | AI 损益分析 |
| `/widget/api/v1/pay/...` | 旧网关 | 挂件 / iframe 内嵌版，与 `/api/v1/pay` 同族 |

### 0.2 ★ 三条抽取经验（自己续抓时必看）

财务这套 bundle 的路径有**三种写法**，少覆盖一种就会漏一大片：

| 写法 | 例子 | 漏了的后果 |
|---|---|---|
| 双引号字面量 | `"/api/v1/finance/purchase/recharge"` | 只抓到 87 个 |
| **反引号模板** | `` `${this.uriPrefix}/api/v1/finance/purchase/balance` `` | 退款/收银台全漏 |
| **`/api/v` + 模板变量** | `` `/api/v${e.version\|\|1}/pay/settlement/balance/get` `` | **整族 39 个结算接口全漏** —— 最容易踩 |

版本号取 `${...\|\|N}` 里的默认值（几乎都是 1）。方法名从包裹它的具名方法取：

```js
GetBalance(e,t){ const r=`${this.uriPrefix}/api/v${e.version||1}/pay/settlement/balance/get`; ... }
```

### 0.3 前端路由 ≠ 接口

`/finance/bills`、`/finance/transactions`、`/finance/bills_statement_version` 这些是**前端路由 / localStorage 键**，
不是接口。第一版抽取把它们当成 API 了，已剔除。

### 0.4 鉴权

卖家中心 cookie 会话（`sessionid`）+ 常规 `aid=6556` / `app_name=i18n_ecom_shop` query。
`/api/oec/` 族同样受签名墙约束（见 [AFFILIATE_API.md](.work/adfly/AFFILIATE_API.md) §0.2）。

---

## A. 对账单 / 账单明细（bills 页，新版 oec 网关）

*49 个 · `view/*` 是账单主页；`profit_loss/*` 是损益下钻；`config/*` 是账单字段配置（26 个）*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `?` | `/api/oec/pay/merchant/statement/advance/profit_loss/spu/list` | `SearchMerchantAdvancedSpuProfitLossList` |
|  | `?` | `/api/oec/pay/merchant/statement/advanced/profit_loss/create_download` | `CreateAdvancedDownloadTask` |
|  | `?` | `/api/oec/pay/merchant/statement/advanced/profit_loss/search_agg` | `SearchMerchantAdvancedProfitLoss` |
|  | `?` | `/api/oec/pay/merchant/statement/config/approve_requirement` | `ApproveStatementRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/constants/list` | `QueryItemConfigConstants` |
|  | `?` | `/api/oec/pay/merchant/statement/config/create_item_config` | `CreateStatementItemConfig` |
|  | `?` | `/api/oec/pay/merchant/statement/config/create_requirement` | `CreateStatementRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/deploy_statement_config_lane` | `DeployStatementConfigLane` |
|  | `?` | `/api/oec/pay/merchant/statement/config/diff_config` | `DiffConfig` |
|  | `?` | `/api/oec/pay/merchant/statement/config/draft/item_list` | `QueryItemDraftsByRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/draft/operation_detail` | `QueryStatementRequirementDraftDetailById` |
|  | `?` | `/api/oec/pay/merchant/statement/config/draft/template_list` | `QueryTemplateDraftsByRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/item/detail` | `QueryStatementItemConfigById` |
|  | `?` | `/api/oec/pay/merchant/statement/config/item/list` | `SearchItemList` |
|  | `?` | `/api/oec/pay/merchant/statement/config/operation_detail` | `QueryStatementRequirementOperationDetailById` |
|  | `?` | `/api/oec/pay/merchant/statement/config/query_template_draft_by_requirement` | `QueryTemplateDraftByRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/rebase_requirement` | `RebaseRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/requirement/list` | `SearchStatementRequirementPage` |
|  | `?` | `/api/oec/pay/merchant/statement/config/rollback_requirement` | `RollbackStatementRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/config/save_layout_template` | `SaveStatementLayoutTemplate` |
|  | `?` | `/api/oec/pay/merchant/statement/config/save_open_api_flow` | `SaveStatementOpenAPIFlow` |
|  | `?` | `/api/oec/pay/merchant/statement/config/save_report_template` | `SaveStatementReportTemplate` |
|  | `?` | `/api/oec/pay/merchant/statement/config/submit_config` | `SubmitConfig` |
|  | `?` | `/api/oec/pay/merchant/statement/config/template/detail` | `QueryTemplateProdById` |
|  | `?` | `/api/oec/pay/merchant/statement/config/template/list` | `SearchTemplateList` |
|  | `?` | `/api/oec/pay/merchant/statement/config/update_requirement` | `UpdateStatementRequirement` |
|  | `?` | `/api/oec/pay/merchant/statement/files` | `ListStatementFile` |
|  | `?` | `/api/oec/pay/merchant/statement/files/download` | `DownloadStatementFile` |
|  | `?` | `/api/oec/pay/merchant/statement/files/export` | `ExportStatementFile` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/config` | `GetMerchantProfitLossPageConfig` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/create_download` | `CreateDownloadTask` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/download_history` | `GetDownloadHistory` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/search_agg` | `SearchMerchantProfitLoss` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/skus` | `GetMerchantProfitLossOrderSkus` |
|  | `?` | `/api/oec/pay/merchant/statement/profit_loss/update_download` | `UpdateDownloadTask` |
|  | `?` | `/api/oec/pay/merchant/statement/view/amount_summary` | `QuerySummaryAmount` |
|  | `?` | `/api/oec/pay/merchant/statement/view/base_account_transactions` | `SearchBaseAccountTransactionList` |
| ◑ | `POST` | `/api/oec/pay/merchant/statement/view/config` | `GetMerchantStatementConfig` |
|  | `?` | `/api/oec/pay/merchant/statement/view/finance_static_info` | `QueryFinanceStaticInfo` |
|  | `?` | `/api/oec/pay/merchant/statement/view/fund_base_info` | `QuerySellerFinanceBasicInfo` |
|  | `?` | `/api/oec/pay/merchant/statement/view/negative_balance_transactions` | `SearchNegativeBalanceTransactions` |
|  | `?` | `/api/oec/pay/merchant/statement/view/onhold_orders` | `SearchOnholdOrderList` |
|  | `?` | `/api/oec/pay/merchant/statement/view/order_breakdown` | `SearchOrderBreakdown` |
|  | `?` | `/api/oec/pay/merchant/statement/view/reserve_orders` | `SearchReserveOrderList` |
|  | `?` | `/api/oec/pay/merchant/statement/view/settled_orders` | `SearchSettledOrderList` |
|  | `?` | `/api/oec/pay/merchant/statement/view/statements` | `SearchStatementList` |
|  | `?` | `/api/oec/pay/merchant/statement/view/summary_breakdown` | `SearchSummaryBreakdown` |
|  | `?` | `/api/oec/pay/merchant/statement/view/trade_order_fund_orders` | `SearchTradeOrderFundOrderList` |
|  | `?` | `/api/oec/pay/merchant/statement/view/trade_order_related_transactions` | `QueryTradeOrderRelatedTransaction` |

## B. 对账单 / 交易明细 / 余额明细（bills 页，旧版）

*11 个 · `SearchStatement` / `SearchStatementOrder` / `SearchTransactionDetail` / `SearchAccountsBalance`*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/statement/accounts/balance/list` | `SearchAccountsBalance` |
|  | `?` | `/api/v1/pay/statement/balance/detail/query` | `QueryBalanceDetail` |
|  | `?` | `/api/v1/pay/statement/fail/msg` | `GetStatementFailMsg` |
|  | `POST` | `/api/v1/pay/statement/gray` | `FetchStatementMerchantGrayInfo` |
|  | `?` | `/api/v1/pay/statement/list/detail` | `SearchStatement` |
| ◑ | `GET` | `/api/v1/pay/statement/notify/msg` | `GetNotifyMsg` |
| ◑ | `GET` | `/api/v1/pay/statement/order/list` | `SearchStatementOrder` |
| ◑ | `GET` | `/api/v1/pay/statement/payment/list` | `SearchPayment` |
|  | `?` | `/api/v1/pay/statement/popup/msg` | `GetPopupMessage` |
| ◑ | `GET` | `/api/v1/pay/statement/stat/info` | `GetAmountStatInfo` |
|  | `?` | `/api/v1/pay/statement/transaction/detail` | `SearchTransactionDetail` |

## C. 结算 / 提现 / 打款周期（deposit 页主体）

*39 个 · 余额、提现、打款周期、协议、押金冻结、对账文件导出*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/pay/settlement/payout/query_payout_config` | `QueryPayoutConfigInfo` |
|  | `POST` | `/api/v1/pay/settlement/amount/get` | `GetSettlementAmount`, `GetSettlementAmountByGet` |
|  | `POST` | `/api/v1/pay/settlement/arrears/accept` | `ArrearsAccept` |
|  | `?` | `/api/v1/pay/settlement/auto/withdraw/config` | `ConfigAutoWithdraw` |
|  | `POST` | `/api/v1/pay/settlement/auto/withdraw/info/query` | `QueryAutoWithdrawInfo` |
|  | `POST` | `/api/v1/pay/settlement/balance/detail/query` | `QueryBalanceDetail` |
|  | `?` | `/api/v1/pay/settlement/balance/get` | `GetBalance` |
|  | `POST` | `/api/v1/pay/settlement/biz/deposit/freeze` | `FreezeDeposit` |
|  | `?` | `/api/v1/pay/settlement/detail/search` | `SearchSettlementDetail` |
|  | `POST` | `/api/v1/pay/settlement/details/order/fee/list` | `ListSettlementDetailsOrderFee` |
|  | `POST` | `/api/v1/pay/settlement/details/other/fee/list` | `ListSettlementDetailsOtherFee` |
|  | `POST` | `/api/v1/pay/settlement/file` | `GetSettlementFile` |
|  | `POST` | `/api/v1/pay/settlement/file/download` | `DownloadSettlementFile` |
|  | `POST` | `/api/v1/pay/settlement/file/export` | `ExportSettlementFile` |
|  | `?` | `/api/v1/pay/settlement/file/list` | `ListSettlementFiles` |
|  | `POST` | `/api/v1/pay/settlement/identity/type/get` | `GetIdentityType` |
|  | `POST` | `/api/v1/pay/settlement/identity/verify` | `VerifyIdentity` |
|  | `POST` | `/api/v1/pay/settlement/info/compliance/security/get` | `GetSecurityComplianceInfo` |
|  | `POST` | `/api/v1/pay/settlement/invoice/search` | `SearchInvoiceDetail` |
|  | `POST` | `/api/v1/pay/settlement/orders/list` | `ListSettlementOrders` |
|  | `POST` | `/api/v1/pay/settlement/payout/bind_card` | `BindCard` |
|  | `POST` | `/api/v1/pay/settlement/payout/cancel_agreement` | `CancelAgreement` |
|  | `POST` | `/api/v1/pay/settlement/payout/create_or_update_payout_cycle` | `CreateOrUpdatePayoutConfig` |
|  | `POST` | `/api/v1/pay/settlement/payout/init_agreement` | `InitAgreement` |
|  | `POST` | `/api/v1/pay/settlement/payout/manage_link` | `GetPayoutManageLink` |
|  | `POST` | `/api/v1/pay/settlement/payout/payment_date_info` | `QueryPaymentDateInfoMsg` |
|  | `POST` | `/api/v1/pay/settlement/payout/pi_infos` | `GetPayoutPiInfos` |
|  | `POST` | `/api/v1/pay/settlement/payout/query_agreement` | `QueryAgreement` |
| ◑ | `GET` | `/api/v1/pay/settlement/payout/reverse_block_check` | `PayoutReserveBlockCheck` |
|  | `POST` | `/api/v1/pay/settlement/payout/reverse_retry` | `PayoutReverseRetry` |
| ◑ | `GET` | `/api/v1/pay/settlement/settings` | `GetSettlementSettings` |
|  | `?` | `/api/v1/pay/settlement/terms/get` | `GetTerms` |
|  | `POST` | `/api/v1/pay/settlement/withdraw` | `Withdraw` |
|  | `POST` | `/api/v1/pay/settlement/withdraw/detail/query` | `QueryWithdrawDetail` |
|  | `?` | `/api/v1/pay/settlement/withdraw/fail/msg/query` | `QueryWithdrawFailMsg` |
|  | `POST` | `/api/v1/pay/settlement/withdraw/retry` | `WithdrawRetry` |
|  | `?` | `/api/v1/pay/settlement/withdraw/rules/get` | `GetWithdrawRules` |
|  | `POST` | `/api/v1/pay/settlement/withdraw/search` | `SearchWithdraw` |
|  | `POST` | `/api/v1/pay/settlement/withdraw/settlement_info` | `GetWithdrawSettlementInfo` |

## D. 打款账户 / 收款方式 / KYC

*10 个 · 卖家侧 PI（收款方式）读写；`pay/account/kyc/get` 是支付 KYC*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/account/info/get` | `GetAccountInfo` |
|  | `POST` | `/api/v1/pay/account/kyc/get` | `GetUserKycInfo` |
|  | `?` | `/api/v1/pay/payout/creator/get_commission` | `GetCommission` |
|  | `POST` | `/api/v1/pay/payout/creator/grayscale_ui` | `GetGrayscaleUI` |
|  | `POST` | `/api/v1/pay/payout/creator/withdraw` | `ManualWithdraw` |
|  | `POST` | `/api/v1/pay/payout/creator/withdraw_config` | `UpdateWithdrawConfig` |
|  | `?` | `/api/v1/pay/payout/creator/withdraw_settings` | `WithdrawSettings` |
|  | `POST` | `/api/v1/pay/payout/seller/get_pi_infos` | `MGetSellerPayoutPI` |
|  | `?` | `/api/v1/pay/payout/seller/payment/list` | `ListSellerPayment` |
|  | `POST` | `/api/v1/pay/payout/seller/set_pi_infos` | `MSetSellerPayoutPI` |

## E. 达人结算与联盟对账单

*9 个 · 达人佣金、达人提现、达人税务；`pay/affiliate/statement/*` 是联盟对账单*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/affiliate/statement/file/download` | `DownloadAffiliateStatementFile` |
|  | `POST` | `/api/v1/pay/affiliate/statement/file/export` | `ExportAffiliateStatementFile` |
|  | `?` | `/api/v1/pay/affiliate/statement/file/export/history` | `ListAffiliateStatementFileExportHistory` |
|  | `POST` | `/api/v1/pay/affiliate/statement/orders` | `SearchPartnerStatement` |
|  | `POST` | `/api/v1/pay/creator/onboard` | `OnboardForCreator` |
|  | `POST` | `/api/v1/pay/creator/onboard_info/get` | `GetOnboardInfoForCreator` |
|  | `POST` | `/api/v1/pay/creator/onboard_info/set` | `SetOnboardInfoForCreator` |
|  | `POST` | `/api/v1/pay/creator/tax_info/get` | `GetTaxInfoForCreator` |
|  | `POST` | `/api/v1/pay/creator/tax_info/set` | `SetTaxInfoForCreator` |

## F. 支付单聚合（seller / creator / biz）

*3 个 · `pay/biz/order/{seller,creator}` 与聚合接口*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/biz/order/aggregation/creator` | `GetCreatorBizOrderAggregation` |
|  | `POST` | `/api/v1/pay/biz/order/creator` | `SearchCreatorBizOrder` |
|  | `POST` | `/api/v1/pay/biz/order/seller` | `SearchSellerBizOrder` |

## G. 支付前置 / 入驻 / 税务信息

*8 个 · `pay/onboard_info/*`、`pay/tax_info/{get,set}`、`pay/meta/info/get`*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/meta/info/get` | `GetMetaInfo` |
|  | `POST` | `/api/v1/pay/onboard` | `Onboard` |
|  | `POST` | `/api/v1/pay/onboard_info/get` | `GetOnboardInfo` |
|  | `POST` | `/api/v1/pay/onboard_info/set` | `SetOnboardInfo` |
|  | `POST` | `/api/v1/pay/onboard_info/ubo_status/get` | `GetUboStatus` |
|  | `POST` | `/api/v1/pay/tax_audit` | `TaxAudit` |
|  | `POST` | `/api/v1/pay/tax_info/get` | `GetTaxInfo` |
|  | `POST` | `/api/v1/pay/tax_info/set` | `SetTaxInfo` |

## H. 账单支付 / 充值 / 收银台（bill-payment 页）

*7 个 · `Recharge` / `MPayOrder` / `AppendPay` / 收银台组件 / 余额*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/finance/purchase/append_pay` | `AppendPay` |
|  | `POST` | `/api/v1/finance/purchase/balance` | `GetBalance` |
|  | `POST` | `/api/v1/finance/purchase/cashier/component` | `GetCashierComponent` |
|  | `POST` | `/api/v1/finance/purchase/order/mget` | `MGetPurchaseOrder` |
|  | `POST` | `/api/v1/finance/purchase/pay` | `MPayOrder` |
|  | `POST` | `/api/v1/finance/purchase/recharge` | `Recharge` |
|  | `POST` | `/api/v1/finance/purchase/recharge/order` | `GetRechargeOrder` |

## I. 收单 / 资金流水（acquiring）

*19 个 · 支付单、退款单、保证金退款、资金流水明细、流水导出*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
| ✅ | `POST` | `/api/v1/finance/acquiring/payment/biz_order/list` | `ListAcquiringBizPayOrders` |
| ✅ | `POST` | `/api/v1/finance/acquiring/query/account` | `QueryUserAccountWithBalanceInfo` |
|  | `POST` | `/api/v1/finance/acquiring/agreement/cancel` | `CancelAgreement` |
|  | `POST` | `/api/v1/finance/acquiring/agreement/init` | `InitAgreement` |
|  | `POST` | `/api/v1/finance/acquiring/agreement/query` | `QueryAgreement` |
|  | `POST` | `/api/v1/finance/acquiring/balance_withdraw` | `BalanceWithdraw` |
|  | `POST` | `/api/v1/finance/acquiring/creator_flow/get_flow_details` | `MGetFundingFlowDetails` |
|  | `POST` | `/api/v1/finance/acquiring/light_refund/order/list` | `ListAcquiringLightRefundOrders` |
|  | `POST` | `/api/v1/finance/acquiring/payment/limit/query` | `QueryPaymentLimit` |
|  | `POST` | `/api/v1/finance/acquiring/payment/order/continue_pay` | `ContinuePay` |
|  | `POST` | `/api/v1/finance/acquiring/payment/order/list` | `ListAcquiringPayOrders` |
|  | `POST` | `/api/v1/finance/acquiring/payment/order/pay` | `Pay` |
|  | `POST` | `/api/v1/finance/acquiring/refund/get_payout_url` | `GetRefundPayoutUrl` |
|  | `POST` | `/api/v1/finance/acquiring/refund/order/list` | `ListAcquiringRefundOrders` |
|  | `POST` | `/api/v1/finance/acquiring/security_deposit_refund/order/list` | `ListSecurityDepositRefundOrders` |
|  | `POST` | `/api/v1/finance/acquiring/spend/order/list` | `ListAcquiringSpendOrders` |
|  | `POST` | `/api/v1/finance/acquiring/transaction/file/create` | `CreateAcquiringTransactionFile` |
|  | `POST` | `/api/v1/finance/acquiring/transaction/file/download` | `DownloadAcquiringTransactionFile` |
|  | `POST` | `/api/v1/finance/acquiring/transaction/file/list` | `ListAcquiringTransactionFiles` |

## J. 财务助手 / 账期政策（assistant / billing policy）

*5 个 · `finance/assistant/*` 财务测算；`finance/billing/policy/*` JBP / 返点 / 账期*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/finance/assistant/calculate` | `CalculateCommission` |
|  | `POST` | `/api/v1/finance/assistant/config` | `GetPricingAssistantConfig` |
|  | `POST` | `/api/v1/finance/billing/policy/enrollment/query` | `QueryPolicyEnrollment` |
|  | `POST` | `/api/v1/finance/billing/policy/jbp_process/query` | `QueryJbpProcess` |
|  | `POST` | `/api/v1/finance/billing/policy/rebate_order/query` | `QueryRebateOrderList` |

## K. 税务 / 发票 / 1099 / DAC7

*61 个 · 税号、发票、Form 1099-K*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/tax/bmbe` | `SubmitBMBE`, `BMBEAuditHistory` |
|  | `?` | `/api/v1/tax/certificate/file` | `DownloadFile` |
|  | `?` | `/api/v1/tax/china_entity_income_report/search` | `SearchChinaEntityIncomeReportListInfo` |
|  | `?` | `/api/v1/tax/china_entity_income_report_apply_time_list/get` | `GetApplyReportTimeForChinaEntityIncome` |
|  | `?` | `/api/v1/tax/china_entity_income_report_detail/download` | `DownloadChinaEntityIncomeReportDetail` |
|  | `POST` | `/api/v1/tax/china_entity_income_report_exchange_rate/get` | `GetExchangeRateForChinaEntityIncome` |
|  | `?` | `/api/v1/tax/china_entity_income_report_taxpayer_list/get` | `GetTaxpayerNameForChinaEntityIncome` |
|  | `POST` | `/api/v1/tax/contract/download_file` | `DownloadContract` |
|  | `POST` | `/api/v1/tax/contract/download_invoice` | `DownloadContractInovice` |
|  | `POST` | `/api/v1/tax/contract/search` | `SearchContract` |
|  | `POST` | `/api/v1/tax/declare/query` | `QueryTaxDeclare` |
|  | `POST` | `/api/v1/tax/declare/submit` | `TaxDeclare` |
|  | `POST` | `/api/v1/tax/entity_change/tax_task` | `GetEntityChangeTaxTask` |
|  | `?` | `/api/v1/tax/estimated_gmv` | `EstimatedGMV` |
|  | `POST` | `/api/v1/tax/faq/tax_document` | `GetTaxDocumentFaqList` |
|  | `POST` | `/api/v1/tax/file/upload` | `UploadFile` |
|  | `POST` | `/api/v1/tax/form1099k/detail/download` | `DownloadFormDetail1099` |
|  | `POST` | `/api/v1/tax/form1099k/detail/generate` | `GenerateFormDetail1099k` |
|  | `?` | `/api/v1/tax/form1099k/detail/get_list` | `GetFormDetail1099List` |
|  | `?` | `/api/v1/tax/form1099k/download` | `DownloadForm1099` |
|  | `?` | `/api/v1/tax/form1099k/get_list` | `GetForm1099List` |
|  | `POST` | `/api/v1/tax/ful_inv/get_list` | `GetFulInvList` |
|  | `POST` | `/api/v1/tax/ful_inv/upload` | `UploadFulInv` |
|  | `POST` | `/api/v1/tax/get_country_list` | `GetCountryList` |
|  | `POST` | `/api/v1/tax/global_seller_info/clear` | `ClearGlobalSellerEntityInfo` |
|  | `POST` | `/api/v1/tax/global_seller_info/get` | `GetGlobalSellerEntityInfo` |
|  | `POST` | `/api/v1/tax/global_seller_info/set` | `UpsertGlobalSellerEntityInfo` |
|  | `POST` | `/api/v1/tax/grayscale` | `QueryGrayscaleStatus` |
|  | `POST` | `/api/v1/tax/invoice/details_export` | `ExportInvoiceDetails` |
|  | `POST` | `/api/v1/tax/invoice/export` | `BatchExportInvoice` |
|  | `?` | `/api/v1/tax/invoice/export_task` | `ListExportedFiles` |
|  | `?` | `/api/v1/tax/invoice/file` | `DownloadFile` |
|  | `POST` | `/api/v1/tax/invoice/pay` | `PayInvoice` |
|  | `POST` | `/api/v1/tax/invoice/search` | `SearchInvoice` |
|  | `POST` | `/api/v1/tax/meta/info/get` | `GetTaxMetaInfo` |
|  | `POST` | `/api/v1/tax/nfe_tool/get` | `GetNFeToolCfg` |
|  | `POST` | `/api/v1/tax/nfe_tool/refresh` | `RefreshNFeToolCfg` |
|  | `POST` | `/api/v1/tax/nfe_tool/set` | `SetNFeToolCfg` |
|  | `POST` | `/api/v1/tax/reimbursement/fee_list` | `FeeList` |
|  | `?` | `/api/v1/tax/reimbursement/history_task` | `ListReimbursementTask` |
|  | `POST` | `/api/v1/tax/reimbursement/invoice_search` | `SearchInvoiceForReimbursement` |
|  | `POST` | `/api/v1/tax/reimbursement/task` | `SubmitReimbursementTask`, `GetReimbursementTask` |
|  | `POST` | `/api/v1/tax/reimbursement/tax_info` | `DefaultTaxInfo` |
|  | `?` | `/api/v1/tax/report/search` | `SearchReport` |
|  | `POST` | `/api/v1/tax/sd` | `SubmitSD`, `SDAuditHistory` |
|  | `?` | `/api/v1/tax/shop_entity` | `ShopEntity` |
|  | `POST` | `/api/v1/tax/statement_letter` | `SubmitSL`, `SLAuditHistory` |
|  | `POST` | `/api/v1/tax/tax_amount` | `CalculateTax` |
|  | `POST` | `/api/v1/tax/tax_info/clear` | `ClearSellerTax` |
|  | `?` | `/api/v1/tax/tax_info/confirm` | `ConfirmTaxInfo` |
|  | `POST` | `/api/v1/tax/tax_info/get` | `GetSellerTax` |
|  | `POST` | `/api/v1/tax/tax_info/get_us_display_info` | `GetUsDisplayInfo` |
|  | `POST` | `/api/v1/tax/tax_info/set` | `SetSellerTax` |
|  | `POST` | `/api/v1/tax/tax_info/set_addr` | `SetSellerAddress` |
|  | `POST` | `/api/v1/tax/tax_info/submit_verify` | `SubmitVerify` |
|  | `POST` | `/api/v1/tax/tax_info/upsert_seller_invoice_payment_info` | `UpsertSellerInvoicePaymentInfo` |
|  | `POST` | `/api/v1/tax/vcs/config/deactivate` | `DeactivateVCSConfig` |
|  | `POST` | `/api/v1/tax/vcs/config/list` | `ListVCSConfigVersion` |
|  | `?` | `/api/v1/tax/vcs/config/ptc_codes` | `GetPTCCodes` |
|  | `POST` | `/api/v1/tax/vcs/config/upsert` | `UpsertVCSConfig` |
|  | `POST` | `/api/v1/tax/wht_certificate` | `SubmitWhtCertificate`, `WhtCertificateHistory` |

## L. 挂件版（widget，内嵌小窗用）

*13 个 · 与上面同族但走 `/widget/api` 前缀，供 iframe / 挂件调用*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/widget/api/v1/pay/creator/tax_info/get` | `WidgetGetTaxInfoForCreator` |
|  | `POST` | `/widget/api/v1/pay/creator/tax_info/set` | `WidgetSetTaxInfoForCreator` |
|  | `POST` | `/widget/api/v1/pay/meta/info/get` | `WidgetGetMetaInfo` |
|  | `POST` | `/widget/api/v1/pay/settlement/payout/manage_link` | `WidgetGetPayoutManageLink` |
|  | `POST` | `/widget/api/v1/pay/settlement/payout/pi_infos` | `WidgetGetPayoutPiInfos` |
|  | `POST` | `/widget/api/v1/pay/tax_audit` | `WidgetTaxAudit` |
|  | `POST` | `/widget/api/v1/pay/tax_info/get` | `WidgetGetTaxInfo` |
|  | `POST` | `/widget/api/v1/pay/tax_info/set` | `WidgetSetTaxInfo` |
|  | `POST` | `/widget/api/v1/tax/file/upload` | `WidgetUploadFile` |
|  | `POST` | `/widget/api/v1/tax/meta/info/get` | `WidgetGetTaxMetaInfo` |
|  | `?` | `/widget/api/v1/tax/tax_info/get` | `WidgetGetSellerTax` |
|  | `POST` | `/widget/api/v1/tax/tax_info/get_us_display_info` | `WidgetGetUsDisplayInfo` |
|  | `POST` | `/widget/api/v1/tax/tax_info/set` | `WidgetSetSellerTax` |

## M. AI 损益分析（pnl_roi_agent）

*8 个 · 账单解读、损益 ROI 分析、流式返回*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/analyze` | `Analyze` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/analyze/stream` | `AnalyzeStream` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/eval/statement/billing-order-explain` | `StatementBillingOrderExplainEval` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/feedback` | `SubmitFeedback`, `GetFeedbackStatus` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/guidance/evaluate` | `EvaluateGuidance` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/statement/billing-order-explain` | `StatementBillingOrderExplain` |
|  | `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/statement/billing-order-explain-stream` | `StatementBillingOrderExplainStream` |
|  | `?` | `/api/oec/finance/ai_infra/statement-explain-list` | `GetStatementExplainList` |

## N. 押金 / 保证金（入驻侧）

*3 个 · 首类目押金查询、押金冻结*

| 实测 | 方法 | 路径 | 调用点方法名 |
|---|---|---|---|
|  | `POST` | `/api/v1/pay/settlement/biz/deposit/freeze` | `FreezeDeposit` |
|  | `POST` | `/api/v1/seller/join/cross_border/deposit/get` | `GetFirstCategoryDeposit` |
|  | `GET` | `/api/v1/seller/onboard/v1/cross_border/deposit/get` | `GetCrossBorderFirstCategoryDeposit` |

---

## 附 A. 三个页面分别打哪些接口

### A.1 `/finance/bills?subTab=on-hold&tab=overview`（账单总览 / 待结算）

- `/api/oec/pay/merchant/statement/view/statements`
- `/api/oec/pay/merchant/statement/view/amount_summary`
- `/api/oec/pay/merchant/statement/view/summary_breakdown`
- `/api/oec/pay/merchant/statement/view/onhold_orders`
- `/api/oec/pay/merchant/statement/view/settled_orders`
- `/api/oec/pay/merchant/statement/view/reserve_orders`
- `/api/oec/pay/merchant/statement/view/order_breakdown`
- `/api/oec/pay/merchant/statement/view/fund_base_info`
- `/api/oec/pay/merchant/statement/view/negative_balance_transactions`
- `/api/oec/pay/merchant/statement/view/order_breakdown`
- `/api/oec/pay/merchant/statement/view/config`
- `/api/oec/pay/merchant/statement/profit_loss/search_agg`
- `/api/oec/pay/merchant/statement/files/export`

`subTab=on-hold` 对应的就是 `view/onhold_orders`；`view/settled_orders` 是已结算；
`view/reserve_orders` 是预留/保证金；`view/negative_balance_transactions` 是负余额流水。

### A.2 `/deposit`（余额 / 提现 / 打款）

- `/api/v1/pay/settlement/balance/get`
- `/api/v1/pay/settlement/balance/detail/query`
- `/api/v1/pay/settlement/amount/get`
- `/api/v1/pay/settlement/settings`
- `/api/v1/pay/settlement/withdraw`
- `/api/v1/pay/settlement/withdraw/search`
- `/api/v1/pay/settlement/withdraw/rules/get`
- `/api/v1/pay/settlement/withdraw/settlement_info`
- `/api/v1/pay/settlement/withdraw/detail/query`
- `/api/v1/pay/settlement/withdraw/fail/msg/query`
- `/api/v1/pay/settlement/auto/withdraw/config`
- `/api/v1/pay/settlement/auto/withdraw/info/query`
- `/api/v1/pay/settlement/payout/pi_infos`
- `/api/v1/pay/settlement/payout/manage_link`
- `/api/v1/pay/settlement/payout/create_or_update_payout_cycle`
- `/api/v1/pay/settlement/payout/bind_card`
- `/api/v1/pay/settlement/file/export`
- `/api/v1/pay/settlement/file/list`
- `/api/v1/pay/settlement/biz/deposit/freeze`

### A.3 `/finance/bill-payment?shop_region=VN`（账单支付 / 充值）

- `/api/v1/finance/purchase/balance`
- `/api/v1/finance/purchase/recharge`
- `/api/v1/finance/purchase/recharge/order`
- `/api/v1/finance/purchase/pay`
- `/api/v1/finance/purchase/append_pay`
- `/api/v1/finance/purchase/order/mget`
- `/api/v1/finance/purchase/cashier/component`
- `/api/v1/pay/statement/payment/list`
- `/api/v1/pay/statement/list/detail`
- `/api/v1/finance/acquiring/payment/order/pay`
- `/api/v1/finance/acquiring/payment/order/list`
- `/api/v1/finance/acquiring/query/account`

## 附 B. 怎么自己续抓

```bash
# 1. 财务页 HTML（★ 直连，走本地代理会超时）
python3 notes/fin_js_list.py          # 读浏览器实时 cookie → 拉 3 个财务页 → 下首屏 JS

# 2. 展开懒加载 chunk（两种命名都要覆盖：x.js 和 x.hash.js）
python3 expand_finance_chunks.py      # 跑到文件数不再增加为止

# 3. deposit 页的微前端本体（在 atlas 注册表里，不在 HTML 的 script 标签里）
python3 fetch_mf_finance.py           # mf_finance/1.0.0.4610/TTS/unihan/mf_finance.js + 18 个 chunk

# 4. 抽接口（三种路径写法都要覆盖）
python3 extract_finance_paths.py

# 5. 生成本手册
python3 gen_finance_api.py
```

**四个坑**：

1. **直连，不要走本地代理** —— 该域走代理会 25s 超时，直连 0.6s 拿 494KB。
2. **懒加载 chunk 两种命名**：`payoutCycleSetting.k7hkdehg.js`（具名+hash）和 `b5xeyaup.js`（8 位 id 即文件名）。
   早期正则只覆盖前者，chunk 展开不全 → 接口抽不全。
3. **`mf_finance` 不在 HTML 的 script 标签里**，藏在 atlas 注册表的 `source_url` 字段：
   `//lf16-oversea.goofy-cdn.com/obj/goofy-sg/gftar/i18n/ecom/shop/mf_finance/<ver>/TTS/unihan/mf_finance.js`
   它是 webpack module federation，chunk 在 `oec-magellan-sg/i18n/ecom/TTS/unihan/mf_finance/static/js/`。
4. **`/api/v` + `${version||1}` 模板** —— 见 §0.2，这条最容易整族漏掉。

**没有 sourcemap**：所有 `.js.map` 一律 404，只能读压缩后的代码。

## 附 C. 随财务页加载但非财务的接口

共 780 个，属 IM / i18n / 物流 / 入驻 / 地图 / 公共组件。仅列前缀分布：

| 前缀 | 数量 |
|---|---|
| `/api/v1/seller/onboard` | 162 |
| `/api/v1/shop_im/shop` | 126 |
| `/widget/api/v1/seller` | 92 |
| `/api/v1/logistics/customs` | 85 |
| `/api/v1/seller/join` | 26 |
| `/api/v1/seller/global` | 17 |
| `/api/v1/seller/entity` | 12 |
| `/api/v1/seller/gs_message` | 10 |
| `/api/v1/seller/open_shop` | 10 |
| `/api/v1/seller/home` | 9 |
| `/api/v1/seller/trademark` | 9 |
| `/api/v1/i18n_conf/timezone` | 8 |
| `/api/v1/seller/profile` | 8 |
| `/api/v1/i18n_conf/currency` | 7 |
| `/api/v1/logistics/line_haul` | 6 |
| `/api/v1/logistics/valuation` | 6 |
| `/api/v1/seller/sub_account` | 6 |
| `/api/v1/seller/warehouses` | 6 |
| `/api/v1/seller/account` | 5 |
| `/api/v1/seller/delegation` | 5 |
| `/api/v1/logistics/customs_declaration_management` | 4 |
| `/api/v1/seller/feishu` | 4 |

---

## 附 D. ★ 本土店（`seller-vn.tiktok.com`）财务三页 —— 已跑通

容器 **TK89_Local_Shop，Hub Studio CDP **`CDP_PORT`**。

> ⚠️ 别用 CDP_PORT —— 那是**另一个**容器，只有过期的 `seller-vn` cookie，它的两个标签页停在
> `/account/register`，会把 302 到登录页误判成"会话失效"。认容器要认扩展标题。

### D.0 本土店 vs 跨境店：四个关键差异（实测）

| 项 | 跨境（SHOP_XBORDER） | 本土（SHOP_LOCAL） |
|---|---|---|
| 页面域 | `seller.tiktokshopglobalselling.com` | **`seller-vn.tiktok.com`** |
| **API 主机** | `api16-normal-sg.tiktokshopglobalselling.com` | **`seller-vn.tiktok.com`（同源！）** |
| **`aid`** | `6556` | **`4068`** |
| `shop_id` | `7494XXXXXXXXXX00` | **`7494XXXXXXXXXX00`** |
| `app_name` | `i18n_ecom_shop` | `i18n_ecom_shop`（同） |
| `timezone_name` | `Asia/Bangkok` | **`Asia/Ho_Chi_Minh`** |

★ **本土店的卖家 API 是同源的** —— 128 个请求里 116 个打到 `https://seller-vn.tiktok.com/api/...`，
**没有**独立的 `api16-normal-*` 主机。跨境店才走独立 API 域。

★★ **`aid` 不一样**（4068 vs 6556）。拿跨境的 query 去打本土店必然失败。

### D.1 三页真实打到的接口（CDP 真流量，128 请求 / 20 个财务接口）

**`/finance/transactions?tab=settled_tab`**（5）

| 方法 | 路径 | 关键 query |
|---|---|---|
| `GET` | `/api/v1/pay/statement/order/list` | `page_type=6&pagination_type=1&size=5&settlement_status=2&statement_version=0&need_total_amount=false` |
| `GET` | `/api/v1/pay/settlement/settings` | `locale=zh-CN` |
| `GET` | `/api/v1/pay/statement/stat/info` | 标准 aid/seller 块 |
| `GET` | **`/api/v2/pay/settlement/file/list`** | ★ 唯一的 v2，见 D.3 |
| `POST` | `/api/oec/pay/merchant/statement/view/config` | 标准 aid/seller 块 |

**`/finance/withdraw-new`**（7）—— 全是 `GET`，`scene_type=3` 是提现场景

| 方法 | 路径 | 关键 query |
|---|---|---|
| `GET` | `/api/v1/pay/settlement/balance/get` | `locale=zh-CN&device_platform=web` |
| `GET` | `/api/v1/pay/statement/balance/detail/query` | `transaction_type=1&offset=0&limit=10` |
| `GET` | `/api/v1/pay/settlement/withdraw/fail/msg/query` | `scene_type=3` |
| `GET` | `/api/v1/pay/settlement/withdraw/rules/get` | — |
| `GET` | `/api/v1/pay/settlement/auto/withdraw/info/query` | `scene_type=3` |
| `GET` | `/api/v1/pay/settlement/info/compliance/security/get` | `scene_type=3&info_type=1` |
| `GET` | `/api/v1/seller/settlement/account/get` | — |

**`/finance/invoice`**（3）

| 方法 | 路径 | 关键 query |
|---|---|---|
| `GET` | `/api/v1/tax/invoice/search` | `pagination_type=1&from=0&size=20&billing_party=2&tax_type…` |
| `GET` | `/api/v1/tax/invoice/export_task` | — |
| `GET` | `/api/v1/tax/tax_info/get` | — |

### D.2 ★ 这批接口全是 GET —— 印证了方法别名问题

`balance/get`、`withdraw/rules/get`、`auto/withdraw/info/query`、`fail/msg/query` 这几个，
静态抽取时标成 `?`，我按 POST 试全是 **404**。

真流量证明它们是 **GET**：源码里写的是 `method:a.UD`（别名，不是字符串字面量）
——`a.UD` == **GET**。见 §0.2 第 3 条。

### D.3 `/api/v2/pay/settlement/file/list` 是 v2

说明 `${e.version||1}` 的默认值**不总是 1**。抽接口时不能一律按 v1 试；
手册里凡标 `?` 又搜不到 v1 的，值得再试 v2。

### D.4 复现

```bash
# 端口写死 CDP_PORT（SHOP_LOCAL）；脚本自带登录检测，会话失效会直接报错而不是默默爬登录页
nohup python3 capture_local_finance.py CDP_PORT > notes/vn_local2.out 2>&1 &
# → notes/vn_local_live.json   主机 + 全部真实 URL/query/body
# → notes/vn_local/js/         页内 fetch 下来的 bundle
```

页面数核对：**4 → 4 ✅**（一次只开一个页，`ctx.new_page()` 登记可回收，finally 必关）。

---

## 附 E. ★ 全量财务接口实测矩阵（本土 SHOP_LOCAL vs 跨境 SHOP_XBORDER）

方法：**借操作员已打开的同源页面做页内 `fetch`** —— 零新建标签、零点击、零焦点变化。
共探 89 个只读接口；155 个写操作按纪律**跳过**，避免在账号里留下垃圾导出任务。

| 结果 | 本土 SHOP_LOCAL | 跨境 SHOP_XBORDER |
|---|---|---|
| `404（路径/版本/方法不对）` | 24 | 125 |
| `缺参数（接口存在）` | 30 | 13 |
| `该店无此路由` | 25 | 0 |
| `通` | 7 | 5 |
| `AI 网关异常` | 4 | 2 |
| `需用户上下文` | 2 | 2 |
| `需 widget 鉴权` | 3 | 0 |
| `系统错误，请稍后重试。` | 2 | 1 |
| `unmarshal lane info ` | 1 | 1 |
| `internal error` | 2 | 0 |
| `?` | 1 | 0 |
| `binding: expr_path=m` | 0 | 1 |

### E.1 ★ 区域差异 —— 仅本土店有（23 个）

跨境店对这些一律返回 `No matching route`：

- `/api/v1/finance/acquiring/agreement/init`
- `/api/v1/finance/acquiring/balance_withdraw`
- `/api/v1/finance/acquiring/refund/order/list`
- `/api/v1/finance/acquiring/spend/order/list`
- `/api/v1/finance/assistant/calculate`
- `/api/v1/finance/assistant/config`
- `/api/v1/tax/bmbe`
- `/api/v1/tax/certificate/file`
- `/api/v1/tax/contract/download_file`
- `/api/v1/tax/contract/download_invoice`
- `/api/v1/tax/contract/search`
- `/api/v1/tax/estimated_gmv`
- `/api/v1/tax/global_seller_info/set`
- `/api/v1/tax/nfe_tool/set`
- `/api/v1/tax/reimbursement/task`
- `/api/v1/tax/report/search`
- `/api/v1/tax/sd`
- `/api/v1/tax/shop_entity`
- `/api/v1/tax/statement_letter`
- `/api/v1/tax/tax_amount`
- `/api/v1/tax/tax_info/get_us_display_info`
- `/api/v1/tax/tax_info/upsert_seller_invoice_payment_info`
- `/api/v1/tax/wht_certificate`

### E.1b 仅跨境店有（4 个）

- `/api/v1/tax/china_entity_income_report/search`
- `/api/v1/tax/china_entity_income_report_apply_time_list/get`
- `/api/v1/tax/china_entity_income_report_detail/download`
- `/api/v1/tax/china_entity_income_report_taxpayer_list/get`

### E.2 三个必须知道的坑

1. **跨境店的 API 不在页面域上。** 本土店同源（`seller-vn.tiktok.com/api/...`），
   跨境店必须打 `api16-normal-sg.tiktokshopglobalselling.com`。
   拿页面域去打跨境 API 会**落到 SPA 回退返回 HTML** —— 不是 404，
   极易误判成「接口存在但报错」。第一遍就是这么错的，71 个被标成未知。
2. **方法错得到的是 404，不是参数错。** 例：`POST /api/v1/tax/tax_info/get` → 404，
   而真流量里 `GET /api/v1/tax/tax_info/get` 成功。静态抽的 `?` 绝大多数其实是 GET
   （源码写 `method:a.UD`，别名不是字面量）。
3. **`/widget/api/v1/tax/*` 需要另一套鉴权** → `98001002 请登录后再操作`，页面 cookie 不够。

### E.3 ★ 导出 / 批量下载链路（38 个接口）

真实下载机制 —— 从 `GET /api/v1/tax/invoice/file` 的响应体确认：

```json
{"code":0,"message":"success","download_url":
  "/wsos_v2/oec-tax/object/wsos6a78cd36058d0b01?expire=REDACTED
   &skipCookie=true&timeStamp=REDACTED&sign=94118b0d56af…"}
```

**两段式**，四个步骤：

| 步 | 做什么 | 接口族 |
|---|---|---|
| 1 | 建导出任务 | `.../export`、`.../create_download`、`.../details_export`、`.../file/export` |
| 2 | 轮询状态 / 列历史 | `.../export_task`、`.../file/list`、`.../download_history` |
| 3 | 拿**带签名的临时下载地址** | `.../file`、`.../download` |
| 4 | GET 那个 `download_url` 取二进制 | `expire` / `timeStamp` / `sign` 三个参数缺一不可 |

实测两个 `file/list` 都返回 `{"data":{}}`（还没有导出任务），
`tax/invoice/file` 则直接给出了可用的签名地址 —— **说明下载地址是现签现用的，会过期**。

### E.4 导出族 10 个子族

- **结算对账文件（v1/v2 都有）** — 0 个，匹配 `pay/settlement/file`
- **对账单文件（oec 新版）** — 0 个，匹配 `statement/files`
- **损益报告导出** — 0 个，匹配 `statement/(advanced/)?profit_loss/`
- **发票导出** — 6 个，匹配 `tax/invoice`
- **1099-K 表单** — 10 个，匹配 `form1099k`
- **合同/发票下载** — 4 个，匹配 `tax/contract/download`
- **税务证明文件** — 2 个，匹配 `tax/certificate/file`
- **收单资金流水导出** — 2 个，匹配 `acquiring/transaction/file`
- **联盟对账单导出** — 0 个，匹配 `pay/affiliate/statement/file`
- **中国实体收入报告** — 6 个，匹配 `china_entity_income_report`

### E.5 探测脚本

```bash
python3 probe_finance_api.py local   # 本土 SHOP_LOCAL（借 seller-vn homepage 做 fetch 源）
python3 probe_finance_api.py cb      # 跨境 SHOP_XBORDER（借 finance/bills 页，打 API 域）
```

结果落 `notes/finance_probe_{local,cb}.json`。脚本自身不新建任何标签，
结束时打印页面数核对（实测 7 → 7、4 → 4）。

---

## 附 F. ★ 后训练：财务 API 调用配方（已实测，非推测）

训练产物 = **`tk01_finance.py`** —— 一个能直接跑的客户端，
把下面这些「域 / aid / 方法 / 参数 / 返回形状」全部固化，不用再重新发现。

### F.1 传输层（最关键的一条）

| 做法 | 结果 |
|---|---|
| `ctx.new_page()` 开页爬 | ❌ Chromium 默认**激活**新标签，会打扰操作员 |
| CDP `Target.createTarget({background:true})` | ❌ 不激活但 Playwright 不登记，回收困难 |
| **借已打开的页面做页内 `fetch()`** | ✅ **本客户端采用** —— 零新建标签、零点击、零鼠标、零焦点 |

`fetch` 自带 cookie、同源/跨域都行，后台标签也能跑（只有 timer 被节流）。

### F.2 域与鉴权块（两个店不一样）

| 项 | 跨境 SHOP_XBORDER | 本土 SHOP_LOCAL |
|---|---|---|
| API 基址 | `api16-normal-sg.tiktokshopglobalselling.com` | `seller-vn.tiktok.com`（**同源**） |
| `aid` / `app_id` | `6556` | **`4068`** |
| `seller_id` | `7494XXXXXXXXXX00` | `7494XXXXXXXXXX00` |
| CDP 端口 | `CDP_PORT` | `CDP_PORT` |
| `app_name` | `i18n_ecom_shop` | `i18n_ecom_shop` |

Query 块（每请求必带）：

```
aid=<aid>&app_id=<aid>&app_name=i18n_ecom_shop&device_platform=web
&oec_seller_id=<sid>&seller_id=<sid>&locale=zh-CN&language=zh-CN
```

### F.3 已验证接口 + 真实返回（2026-09-28 实测）

| 接口 | 方法 | 本土 SHOP_LOCAL | 跨境 SHOP_XBORDER | 返回形状 |
|---|---|---|---|---|
| `/api/v1/pay/settlement/settings` | `GET` | — | ✅ | `{app_finance_setting, app_config, reserve_version, statement_version}` |
| `/api/v1/pay/settlement/balance/get` | `GET` | ✅ `12,765₫` | — | `{amount:{amount,currency,symbol,format_with_symbol}}` |
| `/api/v1/pay/statement/balance/detail/query` | `GET` | ✅ total=85 | — | `{total, has_more, details[{balance_transaction_id, trade_type, order_amount}]}` |
| `/api/v1/pay/statement/order/list` | `GET` | ✅ | ✅ | `{search_next_cursor, search_next_has_more, order_records[{statement_detail_id, trade_order_id, placed_time}]}` |
| `/api/v1/tax/invoice/search` | `GET` | ✅ | — | `{invoice_details[{invoice_sn, amount}]}` — 实测 `TOKVN2026XXXXXXXXXX82 / 567,407₫` |
| `/api/v1/seller/settlement/account/get` | `GET` | — | ✅ | `{payment_method:'PINGPONG', wallet_id:'********055a', status, country_code:'CN'}` |
| `/api/v1/pay/settlement/file/list` | `GET` | ✅ 空 | — | `{data:{}}`（还没有导出任务） |
| `/api/v2/pay/settlement/file/list` | `GET` | ✅ 空 | — | 同上 —— 有真实数据时优先 v2 |
| `/api/oec/pay/merchant/statement/view/config` | `POST` | ✅ | ✅ | 账单页配置 |
| `/api/oec/pay/merchant/statement/view/onhold_orders` | `POST` | ✅ | — | `{order_records, total_count}` —— bills 页 `subTab=on-hold` 就是它 |
| `/api/v1/finance/billing/policy/jbp_process/query` | `POST` | ✅ | ✅ | JBP 账期政策 |
| `/api/v1/finance/assistant/config` | `POST` | ✅ | 该店无此路由 | 财务助手配置 |
| `/api/v1/tax/invoice/export_task` | `GET` | ✅ | ✅ | 导出任务列表 |
| `/api/oec/pay/merchant/statement/files` | `GET` | — | ✗ `Unsupported path(Janus)` | 该网关不提供，别浪费请求 |

### F.4 参数配方（照抄就能用）

```python
C = FinanceClient("tk89")            # 或 "tk01"

C.balance()                                    # 余额
C.balance_detail(transaction_type=1, limit=10) # 余额流水（实测 total=85）
C.order_list(settlement_status=2, size=20)     # 2=已结算
C.order_list(settlement_status=1, size=20)     # 1=待结算（on-hold）
C.invoice_search(size=20, billing_party=2)     # 发票
C.settings()                                   # 结算配置（拿 statement_version）
C.file_list()                                  # 导出历史（内部自动 v1→v2 回退）
C.onhold_orders(page_size=20)                  # oec 新版待结算
C.settled_orders(page_size=20)                 # oec 新版已结算
C.amount_summary("1,2,3")                      # 必须给 summary_types，否则 NUMBER_REDACTED
```

### F.5 批量下载：两段式，照这个顺序

```python
C.batch_export("statement")   # 完整四步，落盘 notes/fin_dl/<shop>_statement
C.batch_export("invoice")
C.batch_export("acquiring")   # 收单流水
C.batch_export("profit_loss") # 损益报告
```

内部四步：

```
1) POST  …/export  | …/create_download | …/details_export     建任务
2) GET   …/export_task | …/file/list | …/download_history     轮询
3) GET   …/file   →  {"download_url":"/wsos_v2/…?expire=…&timeStamp=…&sign=…"}
4) GET   那个 download_url → 二进制
```

**签名地址现签现用会过期** —— `expire` / `timeStamp` / `sign` 三个参数缺一不可。

### F.6 踩坑速查（按「会浪费你一次调试」排序）

1. **方法错得到的是 404，不是参数错。** 源码写 `method:a.UD`（别名），`a.UD` == **GET**。
   静态抽的 `?` 绝大多数是 GET。`POST tax/tax_info/get` → 404，`GET` → 成功。
2. **跨境店的 API 不在页面域上。** 拿 `seller.tiktokshopglobalselling.com` 打 API 路径
   会落到 **SPA 回退返回 HTML** —— 不是 404，只是 http=200 + HTML。极易误判。
3. **`aid` 不一样**（跨境 6556 / 本土 4068）。串了就是 `invalid params` 或空数据。
4. **`/widget/api/v1/tax/*` 要另一套鉴权** → `98001002 请登录后再操作`，页面 cookie 不够。
5. **`summary_types is required`（NUMBER_REDACTED）** —— `amount_summary` 必带该字段。
6. **`/api/oec/...` 无版本段** —— 别按 `/api/v1/oec/` 拼。

### F.7 客户端自检

```bash
python3 tk01_finance.py --shop tk89 balance        # 期望 12,765₫（会变）
python3 tk01_finance.py --shop tk01 settings       # 期望 code=0 + statement_version
python3 tk01_finance.py --shop tk89 order-list --status 2 --size 3   # 期望 order_records 非空
```

`tk01_finance.py` 依赖 `tk01_config.py`（店铺上下文）。**不新建任何标签、不关你的页面**，
`close()` 只释放自己的 Playwright 连接。

---

## 附 G. ★ 导出历史记录（`file/list`）—— 全链路已实测跑通

操作员指出：批量下载账单时，文件会先落到「导出历史记录」里。这条链路现在完整验证过了。

### G.1 真实响应结构（实测，不是推测）

```
GET /api/v1/pay/settlement/file/list
```

```
{"code":0,"message":"success","data":{"files":[
  {"file_id":"7690XXXXXXXXXX35",
   "file_name":"Onhold-unsettled-orders-/-/().xlsx",
   "period":{"begin_date":"1970/01/01","end_date":"1970/01/01"},
   "status":2, "create_time":"1790534989608", "export_time":"1790534989608"}
]}}
```

| 字段 | 含义 |
|---|---|
| `file_id` | ★ **下载的钥匙**，传给 `file/download` |
| `file_name` | 文件名（模板占位符没替换时会出现 `/-/()`） |
| `status` | **1=导出中，2=已导出，3=已查看**（实测下载后自动 2 → 3） |
| `create_time` / `export_time` | epoch 毫秒（字符串） |
| `period` | 该文件覆盖区间；`1970/01/01` 说明按 file_type 整体导出，不按区间 |

### G.2 枚举（从 bundle 挖出，非猜测）

```js
FileType = { SETTLEMENT_DETAIL: 1, ONHOLD_UNSETTLED_ORDER_DETAIL: 7, ONHOLD_UNRELEASED_RESERVE_DETAIL: 8 }
SettlementFileStatus = { EXPORTING: 1, EXPORTED: 2, VIEWED: 3 }
TimeType = { SettlementToAccount: 1 }
PaginationType = { FROM_SIZE: 1, SEARCH_NEXT: 2, SEARCH_PREVIOUS: 3, FROM_SIZE_REVERSE: 4 }
```

### G.3 建导出任务 —— body 形状（缺字段的报错各不相同）

```
{"period": {"begin_date": "2026-06-30", "end_date": "2026-09-28", "time_type": 1},
 "file_type": 7, "version": 1, "statement_version": 0}
```

| 症状 | 原因 |
|---|---|
| `98001001 系统错误，请稍后重试` | **缺 `version`** |
| `22008000 暂无数据可导出` | body 已通过校验，**该区间 / 该 file_type 确实没数据** |
| `code=0 success` | 任务已建，去 `file/list` 拿 `file_id` |

实测：`file_type=1`（结算明细）在 SHOP_LOCAL 上近 14 / 90 / 180 天**全部** `22008000`；
**`file_type=7`（待结算订单明细）立刻成功**。

### G.4 下载：按 file_id 换签名地址

```
GET /api/v1/pay/settlement/file/download?file_id=7690XXXXXXXXXX35
```

```
{"code":0,"data":{"url":"/wsos_v2/oec_pay_settle/object/wsos6ab96542c05f4b06
  ?timeStamp=REDACTED&sign=REDACTED…"}}
```

★ 键名是 **`data.url`**，不是 `download_url`（发票那边才是 `download_url`）—— 两处不一样，代码里两种都认。

### G.5 端到端实测结果

```
1) POST file/export  {file_type:7, version:1, statement_version:0}  → code=0
2) GET  file/list     files[0] = {file_id: 7690XXXXXXXXXX35, status: 2 已导出}
3) GET  file/download?file_id=…  → data.url = /wsos_v2/oec_pay_settle/object/…
4) GET  那个 url      → 15482 字节，文件头 PK\x03\x04（真 xlsx）
5) 再查 file/list     status 自动变 3（已查看）
```

落盘：`notes/fin_dl/tk89_onhold.xlsx`（15,482 B，sha256 头 `4242c2a2b2f730b3`）。

### G.6 客户端调用

```python
C = FinanceClient("tk89")
C.export_statement_file("2026-06-30", "2026-09-28", file_type=7)  # 建任务
h = C.export_history()            # 导出历史，自动把 status 翻成中文
for f in h["_decoded"]:
    print(f["file_id"], f["status_text"], f["file_name"])
d = C.download_history_file(fid)   # 换签名地址
C.download(d["data"]["url"], "out.xlsx")   # 落盘
```

`export_history()` 额外挂一个 `_decoded` 列表（不改原响应），每条带 `status_text`；
`file_list()` 保持返回原始响应。
