# 卖家中心全量接口清单（主表）

> 汇总来源：微前端 bundle 抽取 + 联盟/财务专项 + 早期抽取 + 客户端实现。
> 自动生成，重跑 `python3 build_api_master.py` 刷新。

**唯一接口 4205 个**；来源分布：微前端 5812 / 财务bundle 1024 / 早期 638 / 联盟bundle 552 / 客户端 131

| 业务域 | 接口数 |
|---|---|
| 履约 / 物流 / 面单 | 384 |
| 财务 / 结算 / 税务 | 251 |
| 联盟 / 达人 | 524 |
| 商品 / 库存 / 定价 | 431 |
| 订单 / 售后 | 169 |
| 营销 / 促销 | 408 |
| 数据 / 罗盘 / 报表 | 502 |
| 消息 / IM / 通知 | 157 |
| 治理 / 违规 / 申诉 | 72 |
| 商家 / 入驻 / 资质 | 310 |
| 店铺运营 / 工作台 | 89 |
| 私域 / 粉丝 / 会员 | 2 |
| 账号安全 / 通行证 | 25 |
| 客服消息 / 站内信 | 18 |
| 直播 / 达人运营 | 27 |
| 学习中心 / 内容 | 84 |
| 店铺授权 / 子账号 / 角色 | 25 |
| 内容创作 / 视频中心 | 153 |
| 商品成长 / 优化 / 机会 | 63 |
| 交易（/trade 前缀，另一套） | 64 |
| 全球仓 / 跨境 / 区域 | 36 |
| 达人外联 / 任务消息 | 21 |
| 开店 / 入驻清单 | 17 |
| 平台基础设施 | 47 |
| 其他 / 未分类 | 326 |

## 履约 / 物流 / 面单（384）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/fulfillment/actions/na/upload` | 微前端,微前端,微前端 | `ActionsUploadImageNA` |
| `POST` | `/api/v1/fulfillment/checklist/list` | 微前端,微前端,微前端 | `ChecklistInfo` |
| `POST` | `/api/v1/fulfillment/config_center/get` | 微前端,微前端,微前端 | `GetConfigCenter` |
| `GET` | `/api/v1/fulfillment/default/seller/get` | 微前端,微前端,微前端 | `GetSellerDefault` |
| `POST` | `/api/v1/fulfillment/delivery_template/download` | 微前端,微前端,微前端 | `DownloadSellerBatchDeliveryTemplate` |
| `POST` | `/api/v1/fulfillment/delivery_template/export` | 微前端,微前端,微前端 | `ExportSellerBatchDeliveryTemplate` |
| `POST` | `/api/v1/fulfillment/doc/print_status/verify` | 微前端,微前端,微前端 | `DocPrintStatusVerify` |
| `POST` | `/api/v1/fulfillment/doc_record/generate` | 微前端 | `GenDocRecord` |
| `POST` | `/api/v1/fulfillment/export/err_file` | 微前端,微前端,微前端 | `ExportErrFile` |
| `POST` | `/api/v1/fulfillment/export/file_submit` | 微前端,微前端,微前端 | `ExportFileSubmit` |
| `POST` | `/api/v1/fulfillment/export/file_upload` | 微前端,微前端,微前端 | `ExportFileUpload` |
| `POST` | `/api/v1/fulfillment/fulfill_info/list` | 微前端,微前端,微前端 | `ListFulfillInfo` |
| `PUT` | `/api/v1/fulfillment/insurance/na/set_affidavit_auto_send` | 微前端 | `SetAffidavitAutoSendSwitch` |
| `POST` | `/api/v1/fulfillment/insurance/na/set_affidavit_auto_send_app` | 微前端,微前端 | `SetAffidavitAutoSendSwitchApp` |
| `POST` | `/api/v1/fulfillment/insurance/na/upload_affidavit` | 微前端 | `UploadAffidavit` |
| `POST` | `/api/v1/fulfillment/invoice/list` | 微前端 | `InvoiceInfo` |
| `POST` | `/api/v1/fulfillment/invoice_no/save` | 微前端,微前端,微前端 | `SaveInvoiceNumber` |
| `GET` | `/api/v1/fulfillment/logistic_detail/list` | 微前端,微前端,微前端 | `ListLogisticDetail` |
| `POST` | `/api/v1/fulfillment/logistics/provider/list` | 微前端,微前端,微前端 | `ListProvider` |
| `POST` | `/api/v1/fulfillment/logistics_service/list` | 微前端,微前端 | `ListLogisticsServiceList` |
| `POST` | `/api/v1/fulfillment/order/history` | 微前端 | `ListSellerMainOrderHistory` |
| `POST` | `/api/v1/fulfillment/package/create` | 微前端,微前端,微前端 | `CreatePackage` |
| `POST` | `/api/v1/fulfillment/package/delivery_update` | 微前端,微前端,微前端 | `UpdateSOFDeliveryResult` |
| `POST` | `/api/v1/fulfillment/package/list` | 微前端,微前端,微前端 | `ListPackage` |
| `POST` | `/api/v1/fulfillment/package/mcreate` | 微前端,微前端,微前端 | `MCreatePackage` |
| `POST` | `/api/v1/fulfillment/package/update` | 微前端,微前端,微前端 | `UpdatePkg` |
| `POST` | `/api/v1/fulfillment/picking_list/getdata` | 微前端 | `GetPickingListData` |
| `POST` | `/api/v1/fulfillment/pickinglist/success` | 微前端,微前端,微前端 | `SetPickingListPrintSuccess` |
| `POST` | `/api/v1/fulfillment/reach/banner_list` | 微前端,微前端,微前端 | `ListPlatformReachRules` |
| `POST` | `/api/v1/fulfillment/reach/rules/violation_list` | 微前端,微前端,微前端 | `PlatformRuleViolation` |
| `POST` | `/api/v1/fulfillment/request_doc` | 微前端 | `RequestDocument` |
| `POST` | `/api/v1/fulfillment/reverse/shipping/send_by_platform/rts` | 微前端,微前端 | `ReadyToShipSendByPlatformReverse` |
| `GET` | `/api/v1/fulfillment/seller_create_label_setting/na/get` | 微前端 | `GetSellerCreateLabelSetting` |
| `POST` | `/api/v1/fulfillment/seller_create_label_setting/na/update` | 微前端 | `UpdateSellerCreateLabelSetting` |
| `POST` | `/api/v1/fulfillment/seller_express/get` | 微前端,微前端,微前端 | `GetSellerExpress` |
| `GET` | `/api/v1/fulfillment/seller_print_setting/na/get` | 微前端 | `GetSellerPrintSetting` |
| `POST` | `/api/v1/fulfillment/seller_print_setting/na/update` | 微前端 | `UpdateSellerPrintSetting` |
| `POST` | `/api/v1/fulfillment/seller_setting/biz_switch` | 微前端,微前端,微前端 | `GetSellerBizSwitch` |
| `POST` | `/api/v1/fulfillment/ship_template/download` | 微前端,微前端,微前端 | `DownloadSellerBatchShipTemplate` |
| `POST` | `/api/v1/fulfillment/ship_template/export` | 微前端,微前端,微前端 | `ExportSellerBatchShipTemplateRequest` |
| `GET` | `/api/v1/fulfillment/shipping/inoperable_packages/get` | 微前端,微前端,微前端 | `GetInOperablePackages` |
| `POST` | `/api/v1/fulfillment/shipping/na/fulfillment_decision` | 微前端,微前端,微前端 | `GetFulfillmentDecision` |
| `POST` | `/api/v1/fulfillment/shipping/na/insurance_price` | 微前端,微前端,微前端 | `MCalculateInsurancePrice` |
| `POST` | `/api/v1/fulfillment/shipping/na/send_by_platform/rts` | 微前端,微前端,微前端 | `ReadyToShipSendByPlatformNA` |
| `POST` | `/api/v1/fulfillment/shipping/na/shipping_provider_fee` | 微前端,微前端,微前端 | `GetShippingProviderFee` |
| `POST` | `/api/v1/fulfillment/shipping/na/shipping_service` | 微前端,微前端 | `GetFulfillmentShippingServiceNA` |
| `POST` | `/api/v1/fulfillment/shipping/na_dm/send_by_platform/rts` | 微前端,微前端 | `ReadyToShipSendByPlatformNADM` |
| `POST` | `/api/v1/fulfillment/shipping/options` | 微前端,微前端,微前端 | `GetSellerShippingSettingOptions` |
| `POST` | `/api/v1/fulfillment/shipping/outbound/set` | 微前端,微前端,微前端 | `UpdateOutboundCheckStatus` |
| `POST` | `/api/v1/fulfillment/shipping/recommendation/get` | 微前端,微前端,微前端 | `GetSellerShippingRecommend` |
| `POST` | `/api/v1/fulfillment/shipping/send_by_platform/rts` | 微前端,微前端,微前端 | `ReadyToShipSendByPlatform` |
| `POST` | `/api/v1/fulfillment/shipping/send_by_seller/rts` | 微前端,微前端,微前端 | `ReadyToShipSendBySeller` |
| `POST` | `/api/v1/fulfillment/shipping_doc/generate` | 微前端 | `GenShippingDoc` |
| `POST` | `/api/v1/fulfillment/shipping_label/list` | 微前端 | `ShippingLabel` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/create` | 微前端,微前端 | `CreateSellerPickupTypeConf` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/get` | 微前端,微前端 | `GetSellerPickupTypeConf` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/platform_change_ticket/create` | 微前端 | `CreatePickupTypeChangeTicket` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/platform_change_ticket/get` | 微前端 | `GetPlatformPickupTypeChangeTicket` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/rts_setting` | 微前端,微前端 | `GetPickupTypeRTSSetting` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type/update` | 微前端,微前端 | `UpdateSellerPickupTypeConf` |
| `POST` | `/api/v1/fulfillment/strategy/pickup_type_config/get_starling_key` | 微前端,微前端 | `GetPickupTypeConfStarlingKey` |
| `POST` | `/api/v1/fulfillment/strategy/shipping_profile/create` | 微前端 | `CreateSellerShippingProfile` |
| `POST` | `/api/v1/fulfillment/strategy/shipping_profile/get` | 微前端 | `GetSellerShippingProfile` |
| `POST` | `/api/v1/fulfillment/strategy/shipping_profile/get_amount_currency` | 微前端 | `GetSellerShippingProfileAmountCurrency` |
| `POST` | `/api/v1/fulfillment/strategy/shipping_profile/get_dimension_and_weight_unit_conversion` | 微前端 | `ShippingProfileDimensionAndWeightUnitConversion` |
| `GET` | `/api/v1/fulfillment/subsidy/analysis/get` | 微前端,微前端 | `GetSellerAnalysis` |
| `POST` | `/api/v1/fulfillment/subsidy/detail/download` | 微前端,微前端,微前端 | `DownloadSubsidyDetail` |
| `POST` | `/api/v1/fulfillment/subsidy/detail/export` | 微前端,微前端,微前端 | `ExportSubsidyDetail` |
| `POST` | `/api/v1/fulfillment/subsidy/detail/list` | 微前端,微前端 | `ListSubsidyDetail` |
| `GET` | `/api/v1/fulfillment/subsidy/program/get` | 微前端,微前端 | `GetProgram` |
| `POST` | `/api/v1/fulfillment/subsidy/program/quit_or_join` | 微前端,微前端 | `QuitOrJoinProgram` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/approval_callback` | 微前端,微前端 | `SubsidyStrategyApprovalCallback` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/cancel_approval` | 微前端,微前端 | `CancelApproval` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/create` | 微前端,微前端 | `CreateSubsidyStrategy` |
| `GET` | `/api/v1/fulfillment/subsidy/strategy/get` | 微前端,微前端 | `GetSubsidyStrategy` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/list` | 微前端,微前端 | `ListSubsidyStrategy` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/submit_approval` | 微前端,微前端 | `SubmitApproval` |
| `POST` | `/api/v1/fulfillment/subsidy/strategy/update` | 微前端,微前端 | `UpdateSubsidyStrategy` |
| `POST` | `/api/v1/logistics/app_market/provider/property/contact` | 微前端,微前端 | `ContactProvider` |
| `POST` | `/api/v1/logistics/app_market/provider/property/get` | 微前端,微前端 | `GetProviderProperty` |
| `POST` | `/api/v1/logistics/app_market/provider/property/search` | 微前端,微前端 | `SearchProviderProperty` |
| `POST` | `/api/v1/logistics/compliance/details/query` | 微前端,财务bundle | `QueryComplianceDetailsByPackageID` |
| `POST` | `/api/v1/logistics/compliance/package/download` | 微前端,财务bundle | `DownloadCompliancePackage` |
| `POST` | `/api/v1/logistics/compliance/package/search` | 微前端,财务bundle | `SearchCompliancePackage` |
| `POST` | `/api/v1/logistics/customs/category/download` | 微前端,财务bundle | `CustomsCategoryDownload` |
| `POST` | `/api/v1/logistics/customs/category/search` | 微前端,财务bundle | `CustomsCategorySearch` |
| `POST` | `/api/v1/logistics/customs/category/update` | 微前端,财务bundle | `CustomsCategoryUpdate` |
| `POST` | `/api/v1/logistics/customs/category/upload` | 微前端,财务bundle | `CustomsCategoryUpload` |
| `POST` | `/api/v1/logistics/customs/category_label/search` | 微前端,财务bundle | `CategoryLabelSearch` |
| `POST` | `/api/v1/logistics/customs/category_label/update` | 微前端,财务bundle | `CategoryLabelUpdate` |
| `POST` | `/api/v1/logistics/customs/category_label/upload` | 微前端,财务bundle | `CategoryLabelUpload` |
| `POST` | `/api/v1/logistics/customs/country_ability/open` | 微前端,财务bundle | `GetAllCustomsCountryAbility` |
| `POST` | `/api/v1/logistics/customs/declare_mode/list` | 微前端,财务bundle | `SearchCustomsDeclareTypeConfig` |
| `POST` | `/api/v1/logistics/customs/declare_mode/upload` | 微前端,财务bundle | `UploadCustomsDeclareTypeConfig` |
| `POST` | `/api/v1/logistics/customs/export_mwb/list` | 微前端,财务bundle | `ListExportCustomsMasterWaybill` |
| `POST` | `/api/v1/logistics/customs/export_package_detail/download` | 微前端,财务bundle | `DownloadExportCustomsPackageDetail` |
| `POST` | `/api/v1/logistics/customs/export_package_detail/list` | 微前端,财务bundle | `ListExportCustomsPackageDetail` |
| `POST` | `/api/v1/logistics/customs/file/download` | 微前端,财务bundle | `DownloadCustomsFile` |
| `POST` | `/api/v1/logistics/customs/hscode/algorithm/list` | 微前端,财务bundle | `ListAlgorithmHscode` |
| `POST` | `/api/v1/logistics/customs/hscode/check/upload` | 微前端,财务bundle | `UploadAlgorithmHscodeCheckResult` |
| `POST` | `/api/v1/logistics/customs/hscode/classification_review/get` | 微前端,财务bundle | `ClassificationReviewGet` |
| `POST` | `/api/v1/logistics/customs/hscode/classify_review/list` | 微前端,财务bundle | `ListClassificationReview` |
| `POST` | `/api/v1/logistics/customs/hscode/detail/download` | 微前端,财务bundle | `DownloadHscodeDetail` |
| `POST` | `/api/v1/logistics/customs/hscode/detail/list` | 微前端,财务bundle | `ListHscodeDetail` |
| `POST` | `/api/v1/logistics/customs/hscode/detail/upload` | 微前端,财务bundle | `UploadHscodeDetail` |
| `POST` | `/api/v1/logistics/customs/hscode/expert_review/download` | 微前端,财务bundle | `DownloadExpertReview` |
| `POST` | `/api/v1/logistics/customs/hscode/hscode_base/download` | 微前端,财务bundle | `DownloadHscodeBase` |
| `POST` | `/api/v1/logistics/customs/hscode/hscode_base/query` | 微前端,财务bundle | `SearchHscodeBase` |
| `POST` | `/api/v1/logistics/customs/hscode/pr/list` | 微前端,财务bundle | `ListHscodePR` |
| `POST` | `/api/v1/logistics/customs/hscode/pr/upload` | 微前端,财务bundle | `UploadHscodePR` |
| `POST` | `/api/v1/logistics/customs/hscode/return_hscode/list` | 微前端,财务bundle | `ListPassedHscode` |
| `POST` | `/api/v1/logistics/customs/hscode/return_hscode_log/list` | 微前端,财务bundle | `ListReturnHscodeLog` |
| `POST` | `/api/v1/logistics/customs/hscode/scene_lane/get` | 微前端,财务bundle | `GetLaneScene` |
| `POST` | `/api/v1/logistics/customs/hscode/scene_rule/create` | 微前端,财务bundle | `CreateSceneRule` |
| `POST` | `/api/v1/logistics/customs/hscode/scene_rule/get` | 微前端,财务bundle | `GetSceneRule` |
| `POST` | `/api/v1/logistics/customs/hscode/scene_rule/list` | 微前端,财务bundle | `ListSceneRule` |
| `POST` | `/api/v1/logistics/customs/hscode/scene_rule/update` | 微前端,财务bundle | `UpdateSceneRule` |
| `POST` | `/api/v1/logistics/customs/hscode/third_party_lib/download` | 微前端,财务bundle | `DownloadThirdPartyLib` |
| `POST` | `/api/v1/logistics/customs/invoice/get` | 微前端,财务bundle | `GetCustomsInvoice` |
| `POST` | `/api/v1/logistics/customs/ipr/search` | 微前端,财务bundle | `IprSearch` |
| `POST` | `/api/v1/logistics/customs/ipr/update` | 微前端,财务bundle | `IprUpdate` |
| `POST` | `/api/v1/logistics/customs/ipr/upload` | 微前端,财务bundle | `IprUpload` |
| `POST` | `/api/v1/logistics/customs/log/create` | 微前端,财务bundle | `CreateCustomsLog` |
| `POST` | `/api/v1/logistics/customs/log/query` | 微前端,财务bundle | `QueryCustomsLog` |
| `?` | `/api/v1/logistics/customs/mwb/detail` | 微前端,财务bundle | `GetCustomsMasterWaybillDetail` |
| `POST` | `/api/v1/logistics/customs/mwb/download` | 微前端,财务bundle | `DownloadCustomsMasterWaybill` |
| `POST` | `/api/v1/logistics/customs/mwb/list` | 微前端,财务bundle | `ListCustomsMasterWaybill` |
| `POST` | `/api/v1/logistics/customs/mwb/repush` | 微前端,财务bundle | `RePushCustomsMasterWaybill` |
| `POST` | `/api/v1/logistics/customs/mwb_package/download` | 微前端,财务bundle | `DownloadMasterWaybillPackage` |
| `POST` | `/api/v1/logistics/customs/mwb_settlement_info/get` | 微前端,财务bundle | `GetMWBSettlementInfo` |
| `POST` | `/api/v1/logistics/customs/mwb_status/list` | 微前端,财务bundle | `ListCustomsMasterWaybillStatus` |
| `POST` | `/api/v1/logistics/customs/operation/log` | 微前端,财务bundle | `ListCustomsOperationLog` |
| `POST` | `/api/v1/logistics/customs/package/list` | 微前端,财务bundle | `ListCustomsPackage` |
| `POST` | `/api/v1/logistics/customs/package/repush` | 微前端,财务bundle | `RePushCustomsPackage` |
| `POST` | `/api/v1/logistics/customs/page/config/get` | 微前端,财务bundle | `GetCustomsPageConfig` |
| `POST` | `/api/v1/logistics/customs/port_code/list` | 微前端,财务bundle | `ListCustomsPortCode` |
| `POST` | `/api/v1/logistics/customs/prealert_email/log` | 微前端,财务bundle | `GetCustomsPreAlertEmailLog` |
| `POST` | `/api/v1/logistics/customs/prealert_email/preview` | 微前端,财务bundle | `GetCustomsPrealertEmailPreview` |
| `POST` | `/api/v1/logistics/customs/prealert_email/send` | 微前端,财务bundle | `SendCustomsPrealertEmail` |
| `POST` | `/api/v1/logistics/customs/price_rule/create` | 微前端,财务bundle | `CreateCustomsPriceRule` |
| `POST` | `/api/v1/logistics/customs/price_rule/list` | 微前端,财务bundle | `ListCustomsPriceRule` |
| `POST` | `/api/v1/logistics/customs/price_rule/update` | 微前端,财务bundle | `UpdateCustomsPriceRule` |
| `POST` | `/api/v1/logistics/customs/product/get` | 微前端,财务bundle | `GetCustomsProduct` |
| `POST` | `/api/v1/logistics/customs/product_detail/download` | 微前端,财务bundle | `DownloadCustomsProductDetail` |
| `POST` | `/api/v1/logistics/customs/product_detail/get` | 微前端,财务bundle | `GetCustomsProductDetail` |
| `POST` | `/api/v1/logistics/customs/rule_center/rule_option` | 微前端,财务bundle | `ListCustomsDeclarationRuleOption` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/abolish` | 微前端,财务bundle | `AbolishCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/approve` | 微前端,财务bundle | `ApproveCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/create` | 微前端,财务bundle | `CreateCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/detail` | 微前端,财务bundle | `GetCustomsDeclarationSceneDetail` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/launch` | 微前端,财务bundle | `LaunchCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/list` | 微前端,财务bundle | `ListCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/reject` | 微前端,财务bundle | `RejectCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/rule_center/scene/update` | 微前端,财务bundle | `UpdateCustomsDeclarationScene` |
| `POST` | `/api/v1/logistics/customs/screen/open` | 微前端,财务bundle | `OpenCustomsScreen` |
| `POST` | `/api/v1/logistics/customs/screenshot/approve` | 微前端,财务bundle | `ApproveScreenshot` |
| `POST` | `/api/v1/logistics/customs/sensitive_word/search` | 微前端,财务bundle | `SensitiveWordSearch` |
| `POST` | `/api/v1/logistics/customs/sensitive_word/update` | 微前端,财务bundle | `SensitiveWordUpdate` |
| `POST` | `/api/v1/logistics/customs/sensitive_word/upload` | 微前端,财务bundle | `SensitiveWordUpload` |
| `POST` | `/api/v1/logistics/customs/short_product_name/detail` | 微前端,财务bundle | `GetShortProductNameDetail` |
| `POST` | `/api/v1/logistics/customs/short_product_name/download` | 微前端,财务bundle | `DownloadShortProductName` |
| `POST` | `/api/v1/logistics/customs/short_product_name/manual_check` | 微前端,财务bundle | `ManualCheckShortProductName` |
| `POST` | `/api/v1/logistics/customs/short_product_name/manual_confirm` | 微前端,财务bundle | `ManualConfirmShortProductName` |
| `POST` | `/api/v1/logistics/customs/short_product_name/review` | 微前端,财务bundle | `ManualReviewProductName` |
| `?` | `/api/v1/logistics/customs/short_product_name/search` | 微前端,财务bundle | `SearchShortProductName` |
| `POST` | `/api/v1/logistics/customs/short_product_name/upload` | 微前端,财务bundle | `UploadShortProductNameCheckResult` |
| `POST` | `/api/v1/logistics/customs/sku/download` | 微前端,财务bundle | `DownloadCustomsSku` |
| `POST` | `/api/v1/logistics/customs/sku/query` | 微前端,财务bundle | `SearchCustomsSku` |
| `POST` | `/api/v1/logistics/customs/transaction_certificate/get` | 微前端,财务bundle | `GetTransactionCertificate` |
| `POST` | `/api/v1/logistics/customs_declaration_management/file/upload` | 微前端,财务bundle | `UploadStockingVatFile` |
| `POST` | `/api/v1/logistics/customs_declaration_management/fulfillment/list` | 微前端,财务bundle | `ListStockingFulfillment` |
| `POST` | `/api/v1/logistics/customs_declaration_management/mwb_declaration/list` | 微前端,财务bundle | `ListStockingMwbDeclaration` |
| `POST` | `/api/v1/logistics/customs_declaration_management/sku/list` | 微前端,财务bundle | `ListDeclarationSku` |
| `POST` | `/api/v1/logistics/district/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetDistricts` |
| `POST` | `/api/v1/logistics/district/list` | 微前端,微前端,微前端,微前端,财务bundle | `ListDistricts` |
| `POST` | `/api/v1/logistics/free_shipping_settings/check_promotion_exists` | 微前端 | `CheckStoreWideFreeShippingExists` |
| `POST` | `/api/v1/logistics/free_shipping_settings/create_promotion` | 微前端 | `CreateStoreWideFreeShipping` |
| `DELETE` | `/api/v1/logistics/free_shipping_settings/delete_promotion` | 微前端 | `DeleteStoreWideFreeShipping` |
| `POST` | `/api/v1/logistics/free_shipping_settings/enroll_hidden_price_promotion` | 微前端 | `EnrollHiddenPricePromotion` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_analytics` | 微前端 | `GetFreeShippingAnalyticsData` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_analytics_components` | 微前端 | `GetShippingAnalyticsComponents` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_benefits` | 微前端 | `GetFreeShippingBenefits` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_cfg_components` | 微前端 | `GetShippingConfigComponents` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_hide_price_sku` | 微前端 | `GetHidePriceProductDetail` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_industry_recommend_threshold` | 微前端 | `GetRecommendThresholdForSeller` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_new_rate_card_seller_status` | 微前端 | `GetNewRateCardSellerStatus` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_product_free_shipping_info` | 微前端 | `GetProductFreeShippingInfo` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_rec_components` | 微前端 | `GetShippingRecommendationComponents` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_slider_data` | 微前端 | `GetFreeShippingSliderData` |
| `POST` | `/api/v1/logistics/free_shipping_settings/get_threshold` | 微前端 | `GetStoreWideFreeShippingThreshold` |
| `POST` | `/api/v1/logistics/free_shipping_settings/is_whitelist_seller` | 微前端 | `GetIsWhitelistSeller` |
| `POST` | `/api/v1/logistics/free_shipping_settings/list_free_shipping_product` | 微前端 | `ListFreeShippingProduct` |
| `POST` | `/api/v1/logistics/free_shipping_settings/list_new_rate_card_product` | 微前端 | `GetNewRateCardProduct` |
| `POST` | `/api/v1/logistics/free_shipping_settings/list_shipping_setting_banner` | 微前端 | `ListShippingSettingBanner` |
| `POST` | `/api/v1/logistics/free_shipping_settings/recommend_free_shipping_product` | 微前端 | `RecommendFreeShippingProduct` |
| `POST` | `/api/v1/logistics/free_shipping_settings/update_new_rate_card_product` | 微前端 | `UpdateNewRateCardProduct` |
| `POST` | `/api/v1/logistics/free_shipping_settings/update_product_free_shipping_status` | 微前端 | `UpdateProductFreeShippingStatus` |
| `POST` | `/api/v1/logistics/free_shipping_settings/update_threshold` | 微前端 | `UpdateStoreWideFreeShippingThreshold` |
| `POST` | `/api/v1/logistics/line_haul/mawb/abnormal_report/download` | 微前端,财务bundle | `DownloadMAWBAbnormalReport` |
| `POST` | `/api/v1/logistics/line_haul/mawb/recover` | 微前端,财务bundle | `RecoverLineHaulMawb` |
| `POST` | `/api/v1/logistics/line_haul/mawb/report/download` | 微前端,财务bundle | `DownloadMAWBReport` |
| `?` | `/api/v1/logistics/line_haul/mwb_status/list` | 微前端,财务bundle | `ListMAWBStatus` |
| `POST` | `/api/v1/logistics/line_haul/port_code/list` | 微前端,财务bundle | `ListMAWBPortCode` |
| `POST` | `/api/v1/logistics/line_haul/transport_means` | 微前端,财务bundle | `ListTransportMeans` |
| `POST` | `/api/v1/logistics/provider/management/air_audit/bag_audit_detail/list` | 微前端 | `ListBagAuditDetail` |
| `POST` | `/api/v1/logistics/provider/management/air_audit/mwb_audit_result_detail/get` | 微前端 | `GetMwbAuditResultDetail` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/cabin_change_config/list` | 微前端 | `ListCabinChangeConfig` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/cabin_change_reason_type/list` | 微前端 | `ListCabinChangeReasonType` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/cabin_resource/change` | 微前端 | `ChangeCabinResource` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/list_big_bag` | 微前端,微前端 | `ListBigBag` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/list_cabin_resource` | 微前端,微前端 | `ListCabinResource` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/update_mawb_no_by_excel` | 微前端,微前端 | `UpdateMawbNoByExcel` |
| `POST` | `/api/v1/logistics/provider/management/cabin_management/warehouse_code/list` | 微前端,微前端 | `ListWarehouseCode` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/batch_create` | 微前端,微前端 | `BatchCreateDifferenceForm` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/create` | 微前端,微前端 | `CreateDifferenceForm` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/download` | 微前端,微前端 | `DownloadDifferenceForm` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/pkg_info` | 微前端,微前端 | `MGetDifferenceFormPkgInfo` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/warehouse_info` | 微前端,微前端 | `GetProviderWarehouseInfo` |
| `POST` | `/api/v1/logistics/provider/management/difference_form/weight_appeal/download` | 微前端,微前端 | `DownloadDifferenceFormWeightAppealList` |
| `POST` | `/api/v1/logistics/provider/management/difference_form_pkg/search` | 微前端,微前端 | `SearchDifferenceFormPkg` |
| `POST` | `/api/v1/logistics/provider/management/infra/message/list` | 微前端,微前端 | `ListLPPReachMessage` |
| `POST` | `/api/v1/logistics/provider/management/infra/message/mark_read` | 微前端,微前端 | `MarkLPPReachMessageRead` |
| `POST` | `/api/v1/logistics/provider/management/infra/upload_task/search` | 微前端,微前端 | `SearchUploadTask` |
| `POST` | `/api/v1/logistics/provider/management/laneproduct/list` | 微前端,微前端 | `MGetLaneProductsPage` |
| `POST` | `/api/v1/logistics/provider/management/laneproduct/region/list` | 微前端,微前端 | `MGetRegionLaneProducts` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/cabin/resource` | 微前端,微前端 | `GetCabinResource` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/currency` | 微前端,微前端 | `ListAirlineQuotationCurrency` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/detail` | 微前端,微前端 | `GetAirlineQuotationDetail` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/file/get` | 微前端,微前端 | `GetQuotationUploadTemplateFile` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/import` | 微前端,微前端 | `ImportAirlineQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/list` | 微前端,微前端 | `ListAirlineQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/air/quotation/operate` | 微前端,微前端 | `OperateAirlineQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/land/quotation/detail` | 微前端 | `GetLandQuotationDetail` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/land/quotation/import` | 微前端 | `ImportLandQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/land/quotation/list` | 微前端 | `ListLandQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/land/quotation/operate` | 微前端 | `OperateLandQuotation` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/month/penalty/detail/download` | 微前端,微前端 | `DownloadLinehaulMonthPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/month/penalty/detail/search` | 微前端,微前端 | `SearchLinehaulMonthPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/penalty/appeal` | 微前端,微前端 | `LinehaulPenaltyAppeal` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/penalty/assessment/search` | 微前端,微前端 | `SearchLinehaulPenaltyAssessment` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/penalty/confirm` | 微前端,微前端 | `LinehaulPenaltyConfirm` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/penalty/detail/download` | 微前端,微前端 | `DownloadLinehaulPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/linehaul/penalty/detail/search` | 微前端,微前端 | `SearchLinehaulPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/penalty/appeal/upload` | 微前端,微前端 | `UploadPenaltyAppeal` |
| `POST` | `/api/v1/logistics/provider/management/penalty/assessment/search` | 微前端,微前端 | `SearchPenaltyAssessment` |
| `POST` | `/api/v1/logistics/provider/management/penalty/confirm/search` | 微前端,微前端 | `SearchPenaltyConfirm` |
| `POST` | `/api/v1/logistics/provider/management/penalty/confirm/upload` | 微前端,微前端 | `UploadPenaltyConfirm` |
| `POST` | `/api/v1/logistics/provider/management/penalty/detail/download` | 微前端,微前端 | `DownloadPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/penalty/detail/search` | 微前端,微前端 | `SearchPenaltyDetail` |
| `POST` | `/api/v1/logistics/provider/management/penalty/detail/view` | 微前端,微前端 | `GetPenaltyDetailView` |
| `POST` | `/api/v1/logistics/provider/management/penalty/get_enum` | 微前端,微前端 | `GetEnumForPenalty` |
| `POST` | `/api/v1/logistics/provider/management/penalty/record/confirm` | 微前端,微前端 | `ConfirmPenaltyRecord` |
| `POST` | `/api/v1/logistics/provider/management/penalty/rule/list` | 微前端,微前端 | `ListPenaltyRule` |
| `POST` | `/api/v1/logistics/provider/management/quotation/auth` | 微前端,微前端 | `QuotationAuth` |
| `POST` | `/api/v1/logistics/provider/management/quotation/bsa/version/list` | 微前端,微前端 | `ListBSAVersion` |
| `POST` | `/api/v1/logistics/provider/management/quotation/delivery/timeliness/list` | 微前端,微前端 | `ListDeliveryTimeliness` |
| `POST` | `/api/v1/logistics/provider/management/quotation/delivery/wave/list` | 微前端,微前端 | `ListDeliveryWave` |
| `POST` | `/api/v1/logistics/provider/management/quotation/detail` | 微前端,微前端 | `GetQuotationDetail` |
| `POST` | `/api/v1/logistics/provider/management/quotation/draft` | 微前端,微前端 | `SaveQuotationDraft` |
| `POST` | `/api/v1/logistics/provider/management/quotation/effective/template` | 微前端,微前端 | `EffectiveQuotationTemplate` |
| `POST` | `/api/v1/logistics/provider/management/quotation/list` | 微前端,微前端 | `ListQuotationPage` |
| `POST` | `/api/v1/logistics/provider/management/quotation/logs` | 微前端,微前端 | `ListOperationLogs` |
| `POST` | `/api/v1/logistics/provider/management/quotation/pickup_point/list` | 微前端,微前端 | `ListPickupPoint` |
| `POST` | `/api/v1/logistics/provider/management/quotation/port/list` | 微前端,微前端 | `ListPortCode` |
| `POST` | `/api/v1/logistics/provider/management/quotation/region/list` | 微前端,微前端 | `ListRegion` |
| `POST` | `/api/v1/logistics/provider/management/quotation/source/list` | 微前端,微前端 | `ListQuotationSource` |
| `POST` | `/api/v1/logistics/provider/management/quotation/submit` | 微前端,微前端 | `SubmitQuotation` |
| `POST` | `/api/v1/logistics/provider/management/quotation/update` | 微前端,微前端 | `UpdateQuotation` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/carton/download` | 微前端,微前端 | `DownloadTruckTransferCarton` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/carton/exception/upload` | 微前端,微前端 | `UploadTruckTransferCartonException` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/carton/search` | 微前端,微前端 | `ListTruckTransferCarton` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/carton/status/get_all` | 微前端,微前端 | `GetAllBigBagActionCode` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/city/get_all` | 微前端,微前端 | `GetAllTruckTransferCity` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/package/download` | 微前端,微前端 | `DownloadTruckTransferPackage` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/package/search` | 微前端,微前端 | `SearchTruckTransferPackage` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/package/status/update` | 微前端,微前端 | `UpdateTruckTransferPackageStatus` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/port/get_all` | 微前端,微前端 | `GetAllPorts` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/transfer_order/create` | 微前端,微前端 | `CreateTruckTransferOrder` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/transfer_order/detail/get` | 微前端,微前端 | `GetTruckTransferOrderDetail` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/transfer_order/file/upload` | 微前端,微前端 | `UploadTruckTransferOrderFile` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/transfer_order/search` | 微前端,微前端 | `ListTruckTransferOrder` |
| `POST` | `/api/v1/logistics/provider/management/truck_transfer/transfer_order/update` | 微前端,微前端 | `UpdateTruckTransferOrder` |
| `POST` | `/api/v1/logistics/provider/management/waybill/download` | 微前端 | `DownloadPrintWaybill` |
| `POST` | `/api/v1/logistics/provider/management/waybill/list` | 微前端 | `ListPrintWaybillLog` |
| `POST` | `/api/v1/logistics/provider/management/waybill/print` | 微前端,微前端 | `PrintWaybill` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/batch_details` | 微前端 | `GetTokoGreyBatchDetails` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/detail_file/download` | 微前端 | `DownloadGreyBatchShopDetailFile` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/edit_grey_batch` | 微前端 | `EditTokoGreyBatch` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/import` | 微前端 | `ImportTokoBatchGreyRecord` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/list` | 微前端 | `GetSeaTokoBatchGreyRecordList` |
| `POST` | `/api/v1/logistics/sea_allocation/grey/update_shop_status` | 微前端 | `UpdateTokoGreyBatchShopStatus` |
| `POST` | `/api/v1/logistics/sea_allocation/pre_allocation_task/confirm` | 微前端 | `ConfirmPreAllocationTask` |
| `POST` | `/api/v1/logistics/sea_allocation/pre_allocation_task/file/export` | 微前端 | `ExportPreAllocationTaskFile` |
| `POST` | `/api/v1/logistics/sea_allocation/pre_allocation_task/file/update` | 微前端 | `UpdatePreAllocationTaskFile` |
| `POST` | `/api/v1/logistics/sea_allocation/pre_allocation_task/file/validate` | 微前端 | `ValidatePreAllocationTaskFile` |
| `POST` | `/api/v1/logistics/sea_allocation/pre_allocation_task/page` | 微前端 | `PagePreAllocationTask` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/create` | 微前端 | `CreateAllocSimulation` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/delete` | 微前端 | `DeleteAllocSimulation` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/detail/get` | 微前端 | `GetAllocSimulationDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/page` | 微前端 | `PageAllocSimulation` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/plan/address_level/page` | 微前端 | `GetSimulationPlanAddressLevelData` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/plan/detail/data` | 微前端 | `GetSimulationPlanDetailData` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/plan/overview` | 微前端 | `GetSimulationPlanOverview` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/plan/provider/distribution` | 微前端 | `GetSimulationPlanProviderDistribution` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/plan/start` | 微前端 | `StartSimulationPlan` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/strategy/release` | 微前端 | `ReleaseSimulationAllocation` |
| `POST` | `/api/v1/logistics/sea_allocation/simulation/update` | 微前端 | `UpdateAllocSimulation` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/capacity/limit/delete` | 微前端 | `DeleteAllocCapacitLimit` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/capacity/limit/page` | 微前端 | `PageAllocCapacityLimitDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/capacity/limit/update` | 微前端 | `UpdateAllocCapacityLimit` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/capacity/page` | 微前端 | `PageAllocCapacityDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/create` | 微前端 | `CreateAllocStrategy` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/detail/export` | 微前端 | `ExportStrategyDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/detail/get` | 微前端 | `GetAllocStrategyDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/detail/page/get` | 微前端 | `PageAllocStrategyDetails` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/detail/search` | 微前端 | `AllocSearchDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/details/upload/page` | 微前端 | `PageAllocHistoryUploadDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/batch` | 微前端 | `BatchImportDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/create` | 微前端 | `CreateFactorDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/default/create` | 微前端 | `CreateDefaultProvider` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/default/delete` | 微前端 | `DeleteDefaultProvider` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/default/get` | 微前端 | `GetDefaultProvider` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/default/update` | 微前端 | `UpdateDefaultProvider` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/delete` | 微前端 | `DeleteFactorDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/factor/detail/update` | 微前端 | `UpdateFactorDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/file/validate` | 微前端 | `ValidateAllocStrategyFile` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/page` | 微前端 | `PageAllocStrategy` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/release` | 微前端 | `ReleaseAllocStrategy` |
| `POST` | `/api/v1/logistics/sea_allocation/strategy/update` | 微前端 | `UpdateAllocStrategy` |
| `POST` | `/api/v1/logistics/sea_allocation/toko/diff` | 微前端 | `GetTOKOAllocationDiff` |
| `POST` | `/api/v1/logistics/sea_allocation/toko/diff/details` | 微前端 | `PageTokoAllocDiffDetail` |
| `POST` | `/api/v1/logistics/sea_allocation/tts/diff` | 微前端 | `GetTTSAllocationDiff` |
| `POST` | `/api/v1/logistics/sea_allocation/tts/diff/details` | 微前端 | `PageAllocDiffDetail` |
| `POST` | `/api/v1/logistics/seller/pickup_subscription/apply` | 微前端,微前端 | `ApplyPickupSubscription` |
| `POST` | `/api/v1/logistics/seller/pickup_subscription/cancel` | 微前端,微前端 | `CancelPickupSubscription` |
| `POST` | `/api/v1/logistics/supplier/qualification/submit` | 微前端,微前端 | `SubmitSupplierQualification` |
| `POST` | `/api/v1/logistics/valuation/declare_callback/upload` | 微前端,财务bundle | `UploadProviderDeclareCallback` |
| `POST` | `/api/v1/logistics/valuation/item/download` | 微前端,财务bundle | `DownloadItemValuation` |
| `POST` | `/api/v1/logistics/valuation/provider_order/detail` | 微前端,财务bundle | `GetProviderOrderValuationDetail` |
| `POST` | `/api/v1/logistics/valuation/provider_order/download` | 微前端,财务bundle | `DownloadProviderOrderValuation` |
| `POST` | `/api/v1/logistics/valuation/provider_order/search` | 微前端,财务bundle | `SearchProviderOrderValuation` |
| `POST` | `/api/v1/logistics/valuation/tax_bill/upload` | 微前端,财务bundle | `UploadTaxBill` |
| `POST` | `/api/v1/seller/delivery/get` | 微前端,微前端,微前端,财务bundle | `GetSellerDelivery` |
| `POST` | `/api/v1/seller/delivery/update` | 微前端,微前端,微前端,财务bundle | `UpdateSellerDelivery` |
| `POST` | `/api/v1/seller/warehouses/add` | 微前端,微前端,微前端,财务bundle | `AddSellerWarehouses` |
| `POST` | `/api/v1/seller/warehouses/del` | 微前端,微前端,微前端,财务bundle | `DelSellerWarehouses` |
| `GET` | `/api/v1/seller/warehouses/get` | 微前端,微前端,微前端,财务bundle | `GetSellerWarehouses` |
| `POST` | `/api/v1/seller/warehouses/get_tt_return_warehouses` | 微前端,微前端,微前端,财务bundle | `GetTTReturnWarehouses` |
| `POST` | `/api/v1/seller/warehouses/task` | 微前端,微前端,微前端,财务bundle | `SellerWarehouseTask` |
| `POST` | `/api/v1/seller/warehouses/update` | 微前端,微前端,微前端,财务bundle | `UpdateSellerWarehouses` |
| `POST` | `/widget/api/v1/fulfillment/checklist/list` | 微前端,微前端,微前端 | `ChecklistInfoForWidget` |
| `GET` | `/widget/api/v1/fulfillment/default/seller/get` | 微前端,微前端,微前端 | `GetSellerDefaultForWidget` |
| `POST` | `/widget/api/v1/fulfillment/delivery_template/download` | 微前端,微前端,微前端 | `DownloadSellerBatchDeliveryTemplateForWidget` |
| `POST` | `/widget/api/v1/fulfillment/delivery_template/export` | 微前端,微前端,微前端 | `ExportSellerBatchDeliveryTemplateForWidget` |
| `POST` | `/widget/api/v1/fulfillment/doc/print_status/verify` | 微前端,微前端,微前端 | `DocPrintStatusVerifyForWidget` |
| `POST` | `/widget/api/v1/fulfillment/doc_record/generate` | 微前端 | `GenDocRecordForWidget` |
| `POST` | `/widget/api/v1/fulfillment/fulfill_info/list` | 微前端,微前端,微前端 | `ListFulfillInfoForWidget` |
| `POST` | `/widget/api/v1/fulfillment/invoice/list` | 微前端 | `InvoiceInfoForWidget` |
| `POST` | `/widget/api/v1/fulfillment/invoice_no/save` | 微前端,微前端,微前端 | `SaveInvoiceNumberForWidget` |
| `GET` | `/widget/api/v1/fulfillment/logistic_detail/list` | 微前端,微前端,微前端 | `ListLogisticDetailForWidget` |
| `POST` | `/widget/api/v1/fulfillment/logistics/provider/list` | 微前端,微前端,微前端 | `ListProviderForWidget` |
| `POST` | `/widget/api/v1/fulfillment/order/history` | 微前端 | `ListSellerMainOrderHistoryForWidget` |
| `POST` | `/widget/api/v1/fulfillment/package/create` | 微前端,微前端,微前端 | `CreatePackageForWidget` |
| `POST` | `/widget/api/v1/fulfillment/package/delivery_update` | 微前端,微前端,微前端 | `UpdateSOFDeliveryResultForWidget` |
| `POST` | `/widget/api/v1/fulfillment/package/list` | 微前端,微前端,微前端 | `ListPackageForWidget` |
| `POST` | `/widget/api/v1/fulfillment/package/mcreate` | 微前端,微前端,微前端 | `MCreatePackageForWidget` |
| `POST` | `/widget/api/v1/fulfillment/package/update` | 微前端,微前端,微前端 | `UpdatePkgForWidget` |
| `POST` | `/widget/api/v1/fulfillment/picking_list/getdata` | 微前端 | `GetPickingListDataForWidget` |
| `POST` | `/widget/api/v1/fulfillment/pickinglist/success` | 微前端,微前端,微前端 | `SetPickingListPrintSuccessForWidget` |
| `POST` | `/widget/api/v1/fulfillment/reach/banner_list` | 微前端,微前端,微前端 | `ListPlatformReachRulesForWidget` |
| `POST` | `/widget/api/v1/fulfillment/reach/rules/violation_list` | 微前端,微前端,微前端 | `PlatformRuleViolationForWidget` |
| `POST` | `/widget/api/v1/fulfillment/request_doc` | 微前端 | `RequestDocumentForWidget` |
| `POST` | `/widget/api/v1/fulfillment/seller_express/get` | 微前端,微前端,微前端 | `GetSellerExpressForWidget` |
| `POST` | `/widget/api/v1/fulfillment/seller_setting/biz_switch` | 微前端,微前端,微前端 | `GetSellerBizSwitchForWidget` |
| `POST` | `/widget/api/v1/fulfillment/ship_template/download` | 微前端,微前端,微前端 | `DownloadSellerBatchShipTemplateForWidget` |
| `POST` | `/widget/api/v1/fulfillment/ship_template/export` | 微前端,微前端,微前端 | `ExportSellerBatchShipTemplateRequestForWidget` |
| `GET` | `/widget/api/v1/fulfillment/shipping/inoperable_packages/get` | 微前端,微前端,微前端 | `GetInOperablePackagesForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping/options` | 微前端,微前端,微前端 | `GetSellerShippingSettingOptionsForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping/outbound/set` | 微前端,微前端,微前端 | `UpdateOutboundCheckStatusForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping/recommendation/get` | 微前端,微前端,微前端 | `GetSellerShippingRecommendForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping/send_by_platform/rts` | 微前端,微前端,微前端 | `ReadyToShipSendByPlatformForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping/send_by_seller/rts` | 微前端,微前端,微前端 | `ReadyToShipSendBySellerForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping_doc/generate` | 微前端 | `GenShippingDocForWidget` |
| `POST` | `/widget/api/v1/fulfillment/shipping_label/list` | 微前端 | `ShippingLabelForWidget` |

## 财务 / 结算 / 税务（251）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/analyze` | 财务bundle | `Analyze` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/analyze/stream` | 财务bundle | `AnalyzeStream` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/eval/statement/billing-order-explain` | 财务bundle | `StatementBillingOrderExplainEval` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/feedback` | 财务bundle | `SubmitFeedback` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/guidance/evaluate` | 财务bundle | `EvaluateGuidance` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/statement/billing-order-explain` | 财务bundle | `StatementBillingOrderExplain` |
| `POST` | `/api/oec/finance/ai_infra/pnl_roi_agent/statement/billing-order-explain-stream` | 财务bundle | `StatementBillingOrderExplainStream` |
| `?` | `/api/oec/finance/ai_infra/statement-explain-list` | 财务bundle | `GetStatementExplainList` |
| `?` | `/api/oec/pay/merchant/statement/advance/profit_loss/spu/list` | 财务bundle | `SearchMerchantAdvancedSpuProfitLossList` |
| `?` | `/api/oec/pay/merchant/statement/advanced/profit_loss/create_download` | 财务bundle | `CreateAdvancedDownloadTask` |
| `?` | `/api/oec/pay/merchant/statement/advanced/profit_loss/search_agg` | 财务bundle | `SearchMerchantAdvancedProfitLoss` |
| `?` | `/api/oec/pay/merchant/statement/config/approve_requirement` | 财务bundle | `ApproveStatementRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/constants/list` | 财务bundle | `QueryItemConfigConstants` |
| `?` | `/api/oec/pay/merchant/statement/config/create_item_config` | 财务bundle | `CreateStatementItemConfig` |
| `?` | `/api/oec/pay/merchant/statement/config/create_requirement` | 财务bundle | `CreateStatementRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/deploy_statement_config_lane` | 财务bundle | `DeployStatementConfigLane` |
| `?` | `/api/oec/pay/merchant/statement/config/diff_config` | 财务bundle | `DiffConfig` |
| `?` | `/api/oec/pay/merchant/statement/config/draft/item_list` | 财务bundle | `QueryItemDraftsByRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/draft/operation_detail` | 财务bundle | `QueryStatementRequirementDraftDetailById` |
| `?` | `/api/oec/pay/merchant/statement/config/draft/template_list` | 财务bundle | `QueryTemplateDraftsByRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/item/detail` | 财务bundle | `QueryStatementItemConfigById` |
| `?` | `/api/oec/pay/merchant/statement/config/item/list` | 财务bundle | `SearchItemList` |
| `?` | `/api/oec/pay/merchant/statement/config/operation_detail` | 财务bundle | `QueryStatementRequirementOperationDetailById` |
| `?` | `/api/oec/pay/merchant/statement/config/query_template_draft_by_requirement` | 财务bundle | `QueryTemplateDraftByRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/rebase_requirement` | 财务bundle | `RebaseRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/requirement/list` | 财务bundle | `SearchStatementRequirementPage` |
| `?` | `/api/oec/pay/merchant/statement/config/rollback_requirement` | 财务bundle | `RollbackStatementRequirement` |
| `?` | `/api/oec/pay/merchant/statement/config/save_layout_template` | 财务bundle | `SaveStatementLayoutTemplate` |
| `?` | `/api/oec/pay/merchant/statement/config/save_open_api_flow` | 财务bundle | `SaveStatementOpenAPIFlow` |
| `?` | `/api/oec/pay/merchant/statement/config/save_report_template` | 财务bundle | `SaveStatementReportTemplate` |
| `?` | `/api/oec/pay/merchant/statement/config/submit_config` | 财务bundle | `SubmitConfig` |
| `?` | `/api/oec/pay/merchant/statement/config/template/detail` | 财务bundle | `QueryTemplateProdById` |
| `?` | `/api/oec/pay/merchant/statement/config/template/list` | 财务bundle | `SearchTemplateList` |
| `?` | `/api/oec/pay/merchant/statement/config/update_requirement` | 财务bundle | `UpdateStatementRequirement` |
| `?` | `/api/oec/pay/merchant/statement/files` | 客户端,财务bundle | `ListStatementFile` |
| `?` | `/api/oec/pay/merchant/statement/files/download` | 客户端,财务bundle | `DownloadStatementFile` |
| `?` | `/api/oec/pay/merchant/statement/files/export` | 客户端,财务bundle | `ExportStatementFile` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/config` | 财务bundle | `GetMerchantProfitLossPageConfig` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/create_download` | 客户端,财务bundle | `CreateDownloadTask` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/download_history` | 客户端,财务bundle | `GetDownloadHistory` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/search_agg` | 客户端,财务bundle | `SearchMerchantProfitLoss` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/skus` | 财务bundle | `GetMerchantProfitLossOrderSkus` |
| `?` | `/api/oec/pay/merchant/statement/profit_loss/update_download` | 财务bundle | `UpdateDownloadTask` |
| `?` | `/api/oec/pay/merchant/statement/view/amount_summary` | 客户端,财务bundle | `QuerySummaryAmount` |
| `?` | `/api/oec/pay/merchant/statement/view/base_account_transactions` | 财务bundle | `SearchBaseAccountTransactionList` |
| `?` | `/api/oec/pay/merchant/statement/view/config` | 客户端,财务bundle | `GetMerchantStatementConfig` |
| `?` | `/api/oec/pay/merchant/statement/view/finance_static_info` | 财务bundle | `QueryFinanceStaticInfo` |
| `?` | `/api/oec/pay/merchant/statement/view/fund_base_info` | 客户端,财务bundle | `QuerySellerFinanceBasicInfo` |
| `?` | `/api/oec/pay/merchant/statement/view/negative_balance_transactions` | 客户端,财务bundle | `SearchNegativeBalanceTransactions` |
| `?` | `/api/oec/pay/merchant/statement/view/onhold_orders` | 客户端,财务bundle | `SearchOnholdOrderList` |
| `?` | `/api/oec/pay/merchant/statement/view/order_breakdown` | 客户端,财务bundle | `SearchOrderBreakdown` |
| `?` | `/api/oec/pay/merchant/statement/view/reserve_orders` | 客户端,财务bundle | `SearchReserveOrderList` |
| `?` | `/api/oec/pay/merchant/statement/view/settled_orders` | 客户端,财务bundle | `SearchSettledOrderList` |
| `?` | `/api/oec/pay/merchant/statement/view/statements` | 客户端,财务bundle | `SearchStatementList` |
| `?` | `/api/oec/pay/merchant/statement/view/summary_breakdown` | 客户端,财务bundle | `SearchSummaryBreakdown` |
| `?` | `/api/oec/pay/merchant/statement/view/trade_order_fund_orders` | 财务bundle | `SearchTradeOrderFundOrderList` |
| `?` | `/api/oec/pay/merchant/statement/view/trade_order_related_transactions` | 财务bundle | `QueryTradeOrderRelatedTransaction` |
| `POST` | `/api/v1/finance/acquiring/agreement/cancel` | 微前端,财务bundle | `CancelAgreement` |
| `POST` | `/api/v1/finance/acquiring/agreement/init` | 微前端,财务bundle | `InitAgreement` |
| `POST` | `/api/v1/finance/acquiring/agreement/query` | 微前端,财务bundle | `QueryAgreement` |
| `POST` | `/api/v1/finance/acquiring/balance_withdraw` | 微前端,财务bundle | `BalanceWithdraw` |
| `POST` | `/api/v1/finance/acquiring/creator_flow/get_flow_details` | 微前端,财务bundle | `MGetFundingFlowDetails` |
| `POST` | `/api/v1/finance/acquiring/light_refund/order/list` | 微前端,财务bundle | `ListAcquiringLightRefundOrders` |
| `POST` | `/api/v1/finance/acquiring/payment/biz_order/list` | 微前端,财务bundle | `ListAcquiringBizPayOrders` |
| `POST` | `/api/v1/finance/acquiring/payment/limit/query` | 微前端,财务bundle | `QueryPaymentLimit` |
| `POST` | `/api/v1/finance/acquiring/payment/order/continue_pay` | 微前端,财务bundle | `ContinuePay` |
| `POST` | `/api/v1/finance/acquiring/payment/order/list` | 微前端,财务bundle | `ListAcquiringPayOrders` |
| `POST` | `/api/v1/finance/acquiring/payment/order/pay` | 微前端,财务bundle | `Pay` |
| `POST` | `/api/v1/finance/acquiring/query/account` | 客户端,微前端,财务bundle | `QueryUserAccountWithBalanceInfo` |
| `POST` | `/api/v1/finance/acquiring/refund/get_payout_url` | 微前端,财务bundle | `GetRefundPayoutUrl` |
| `POST` | `/api/v1/finance/acquiring/refund/order/list` | 微前端,财务bundle | `ListAcquiringRefundOrders` |
| `POST` | `/api/v1/finance/acquiring/security_deposit_refund/order/list` | 微前端,财务bundle | `ListSecurityDepositRefundOrders` |
| `POST` | `/api/v1/finance/acquiring/spend/order/list` | 微前端,财务bundle | `ListAcquiringSpendOrders` |
| `POST` | `/api/v1/finance/acquiring/transaction/file/create` | 客户端,微前端,财务bundle | `CreateAcquiringTransactionFile` |
| `POST` | `/api/v1/finance/acquiring/transaction/file/download` | 客户端,微前端,财务bundle | `DownloadAcquiringTransactionFile` |
| `POST` | `/api/v1/finance/acquiring/transaction/file/list` | 客户端,微前端,财务bundle | `ListAcquiringTransactionFiles` |
| `POST` | `/api/v1/finance/assistant/calculate` | 微前端,财务bundle | `CalculateCommission` |
| `POST` | `/api/v1/finance/assistant/config` | 客户端,微前端,财务bundle | `GetPricingAssistantConfig` |
| `POST` | `/api/v1/finance/billing/policy/enrollment/query` | 微前端,财务bundle | `QueryPolicyEnrollment` |
| `POST` | `/api/v1/finance/billing/policy/jbp_process/query` | 客户端,微前端,财务bundle | `QueryJbpProcess` |
| `POST` | `/api/v1/finance/billing/policy/rebate_order/query` | 微前端,财务bundle | `QueryRebateOrderList` |
| `POST` | `/api/v1/finance/purchase/append_pay` | 微前端,财务bundle | `AppendPay` |
| `POST` | `/api/v1/finance/purchase/balance` | 微前端,财务bundle | `GetBalance` |
| `POST` | `/api/v1/finance/purchase/cashier/component` | 微前端,财务bundle | `GetCashierComponent` |
| `POST` | `/api/v1/finance/purchase/order/mget` | 微前端,财务bundle | `MGetPurchaseOrder` |
| `POST` | `/api/v1/finance/purchase/pay` | 微前端,财务bundle | `MPayOrder` |
| `POST` | `/api/v1/finance/purchase/recharge` | 微前端,财务bundle | `Recharge` |
| `POST` | `/api/v1/finance/purchase/recharge/order` | 微前端,财务bundle | `GetRechargeOrder` |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/pay/status` | 联盟bundle |  |
| `POST` | `/api/v1/pay/account/info/get` | 微前端,财务bundle | `GetAccountInfo` |
| `POST` | `/api/v1/pay/account/kyc/get` | 微前端,财务bundle | `GetUserKycInfo` |
| `POST` | `/api/v1/pay/affiliate/statement/file/download` | 微前端,财务bundle | `DownloadAffiliateStatementFile` |
| `POST` | `/api/v1/pay/affiliate/statement/file/export` | 微前端,财务bundle | `ExportAffiliateStatementFile` |
| `GET` | `/api/v1/pay/affiliate/statement/file/export/history` | 微前端,财务bundle | `ListAffiliateStatementFileExportHistory` |
| `POST` | `/api/v1/pay/affiliate/statement/orders` | 财务bundle | `SearchPartnerStatement` |
| `POST` | `/api/v1/pay/biz/order/aggregation/creator` | 财务bundle | `GetCreatorBizOrderAggregation` |
| `POST` | `/api/v1/pay/biz/order/creator` | 财务bundle | `SearchCreatorBizOrder` |
| `POST` | `/api/v1/pay/biz/order/seller` | 财务bundle | `SearchSellerBizOrder` |
| `POST` | `/api/v1/pay/creator/onboard` | 微前端,财务bundle | `OnboardForCreator` |
| `POST` | `/api/v1/pay/creator/onboard_info/get` | 微前端,财务bundle | `GetOnboardInfoForCreator` |
| `POST` | `/api/v1/pay/creator/onboard_info/set` | 微前端,财务bundle | `SetOnboardInfoForCreator` |
| `POST` | `/api/v1/pay/creator/tax_info/get` | 微前端,财务bundle | `GetTaxInfoForCreator` |
| `POST` | `/api/v1/pay/creator/tax_info/set` | 微前端,财务bundle | `SetTaxInfoForCreator` |
| `POST` | `/api/v1/pay/meta/info/get` | 微前端,财务bundle | `GetMetaInfo` |
| `POST` | `/api/v1/pay/onboard` | 微前端,财务bundle | `Onboard` |
| `POST` | `/api/v1/pay/onboard_info/get` | 微前端,财务bundle | `GetOnboardInfo` |
| `POST` | `/api/v1/pay/onboard_info/set` | 微前端,财务bundle | `SetOnboardInfo` |
| `POST` | `/api/v1/pay/onboard_info/ubo_status/get` | 微前端,财务bundle | `GetUboStatus` |
| `?` | `/api/v1/pay/payout/creator/get_commission` | 微前端,财务bundle | `GetCommission` |
| `POST` | `/api/v1/pay/payout/creator/grayscale_ui` | 微前端,财务bundle | `GetGrayscaleUI` |
| `POST` | `/api/v1/pay/payout/creator/withdraw` | 微前端,财务bundle | `ManualWithdraw` |
| `POST` | `/api/v1/pay/payout/creator/withdraw_config` | 微前端,财务bundle | `UpdateWithdrawConfig` |
| `?` | `/api/v1/pay/payout/creator/withdraw_settings` | 微前端,财务bundle | `WithdrawSettings` |
| `POST` | `/api/v1/pay/payout/seller/get_pi_infos` | 微前端,财务bundle | `MGetSellerPayoutPI` |
| `?` | `/api/v1/pay/payout/seller/payment/list` | 微前端,财务bundle | `ListSellerPayment` |
| `POST` | `/api/v1/pay/payout/seller/set_pi_infos` | 微前端,财务bundle | `MSetSellerPayoutPI` |
| `POST` | `/api/v1/pay/settlement/amount/get` | 客户端,微前端,财务bundle | `GetSettlementAmount` |
| `POST` | `/api/v1/pay/settlement/arrears/accept` | 微前端,财务bundle | `ArrearsAccept` |
| `GET` | `/api/v1/pay/settlement/auto/withdraw/config` | 微前端,财务bundle | `ConfigAutoWithdraw` |
| `POST` | `/api/v1/pay/settlement/auto/withdraw/info/query` | 客户端,微前端,财务bundle | `QueryAutoWithdrawInfo` |
| `POST` | `/api/v1/pay/settlement/balance/detail/query` | 微前端,财务bundle | `QueryBalanceDetail` |
| `GET` | `/api/v1/pay/settlement/balance/get` | 客户端,微前端,财务bundle | `GetBalance` |
| `POST` | `/api/v1/pay/settlement/biz/deposit/freeze` | 微前端,财务bundle | `FreezeDeposit` |
| `GET` | `/api/v1/pay/settlement/detail/search` | 微前端,财务bundle | `SearchSettlementDetail` |
| `POST` | `/api/v1/pay/settlement/details/order/fee/list` | 微前端,财务bundle | `ListSettlementDetailsOrderFee` |
| `POST` | `/api/v1/pay/settlement/details/other/fee/list` | 微前端,财务bundle | `ListSettlementDetailsOtherFee` |
| `POST` | `/api/v1/pay/settlement/file` | 微前端,财务bundle | `GetSettlementFile` |
| `POST` | `/api/v1/pay/settlement/file/download` | 客户端,微前端,财务bundle | `DownloadSettlementFile` |
| `POST` | `/api/v1/pay/settlement/file/export` | 客户端,微前端,财务bundle | `ExportSettlementFile` |
| `GET` | `/api/v1/pay/settlement/file/list` | 客户端,微前端,财务bundle | `ListSettlementFiles` |
| `POST` | `/api/v1/pay/settlement/identity/type/get` | 微前端,财务bundle | `GetIdentityType` |
| `POST` | `/api/v1/pay/settlement/identity/verify` | 微前端,财务bundle | `VerifyIdentity` |
| `POST` | `/api/v1/pay/settlement/info/compliance/security/get` | 客户端,微前端,财务bundle | `GetSecurityComplianceInfo` |
| `POST` | `/api/v1/pay/settlement/invoice/search` | 微前端,财务bundle | `SearchInvoiceDetail` |
| `POST` | `/api/v1/pay/settlement/orders/list` | 微前端,财务bundle | `ListSettlementOrders` |
| `POST` | `/api/v1/pay/settlement/payout/bind_card` | 微前端,财务bundle | `BindCard` |
| `POST` | `/api/v1/pay/settlement/payout/cancel_agreement` | 微前端,财务bundle | `CancelAgreement` |
| `POST` | `/api/v1/pay/settlement/payout/create_or_update_payout_cycle` | 微前端,财务bundle | `CreateOrUpdatePayoutConfig` |
| `POST` | `/api/v1/pay/settlement/payout/init_agreement` | 微前端,财务bundle | `InitAgreement` |
| `POST` | `/api/v1/pay/settlement/payout/manage_link` | 微前端,财务bundle | `GetPayoutManageLink` |
| `POST` | `/api/v1/pay/settlement/payout/payment_date_info` | 微前端,财务bundle | `QueryPaymentDateInfoMsg` |
| `POST` | `/api/v1/pay/settlement/payout/pi_infos` | 微前端,财务bundle | `GetPayoutPiInfos` |
| `POST` | `/api/v1/pay/settlement/payout/query_agreement` | 微前端,财务bundle | `QueryAgreement` |
| `POST` | `/api/v1/pay/settlement/payout/query_payout_config` | 客户端,微前端,财务bundle | `QueryPayoutConfigInfo` |
| `GET` | `/api/v1/pay/settlement/payout/reverse_block_check` | 客户端,微前端,财务bundle | `PayoutReserveBlockCheck` |
| `POST` | `/api/v1/pay/settlement/payout/reverse_retry` | 微前端,财务bundle | `PayoutReverseRetry` |
| `GET` | `/api/v1/pay/settlement/settings` | 客户端,微前端,财务bundle | `GetSettlementSettings` |
| `GET` | `/api/v1/pay/settlement/terms/get` | 微前端,财务bundle | `GetTerms` |
| `POST` | `/api/v1/pay/settlement/withdraw` | 微前端,财务bundle | `Withdraw` |
| `POST` | `/api/v1/pay/settlement/withdraw/detail/query` | 微前端,财务bundle | `QueryWithdrawDetail` |
| `GET` | `/api/v1/pay/settlement/withdraw/fail/msg/query` | 客户端,微前端,财务bundle | `QueryWithdrawFailMsg` |
| `POST` | `/api/v1/pay/settlement/withdraw/retry` | 微前端,财务bundle | `WithdrawRetry` |
| `GET` | `/api/v1/pay/settlement/withdraw/rules/get` | 客户端,微前端,财务bundle | `GetWithdrawRules` |
| `POST` | `/api/v1/pay/settlement/withdraw/search` | 微前端,财务bundle | `SearchWithdraw` |
| `POST` | `/api/v1/pay/settlement/withdraw/settlement_info` | 微前端,财务bundle | `GetWithdrawSettlementInfo` |
| `POST` | `/api/v1/pay/statement/accounts/balance/list` | 财务bundle | `SearchAccountsBalance` |
| `?` | `/api/v1/pay/statement/balance/detail/query` | 客户端,财务bundle | `QueryBalanceDetail` |
| `?` | `/api/v1/pay/statement/fail/msg` | 财务bundle | `GetStatementFailMsg` |
| `POST` | `/api/v1/pay/statement/gray` | 客户端,财务bundle | `FetchStatementMerchantGrayInfo` |
| `?` | `/api/v1/pay/statement/list/detail` | 客户端,财务bundle | `SearchStatement` |
| `?` | `/api/v1/pay/statement/notify/msg` | 客户端,财务bundle | `GetNotifyMsg` |
| `?` | `/api/v1/pay/statement/order/list` | 客户端,财务bundle | `SearchStatementOrder` |
| `?` | `/api/v1/pay/statement/payment/list` | 客户端,财务bundle | `SearchPayment` |
| `?` | `/api/v1/pay/statement/popup/msg` | 财务bundle | `GetPopupMessage` |
| `?` | `/api/v1/pay/statement/stat/info` | 客户端,财务bundle | `GetAmountStatInfo` |
| `?` | `/api/v1/pay/statement/transaction/detail` | 客户端,财务bundle | `SearchTransactionDetail` |
| `POST` | `/api/v1/pay/tax_audit` | 微前端,财务bundle | `TaxAudit` |
| `POST` | `/api/v1/pay/tax_info/get` | 微前端,财务bundle | `GetTaxInfo` |
| `POST` | `/api/v1/pay/tax_info/set` | 微前端,财务bundle | `SetTaxInfo` |
| `GET` | `/api/v1/seller/growth_center/reward_penalty/settlement_period_compliance/get` | 早期 |  |
| `POST` | `/api/v1/seller/join/cross_border/deposit/get` | 微前端,财务bundle | `GetFirstCategoryDeposit` |
| `GET` | `/api/v1/seller/onboard/v1/cross_border/deposit/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderFirstCategoryDeposit` |
| `GET` | `/api/v1/seller/settlement/account/get` | 客户端,微前端,微前端,微前端,财务bundle | `GetSettlementAccount` |
| `POST` | `/api/v1/seller/tax/get` | 微前端,微前端,微前端,财务bundle | `GetSellerTax` |
| `POST` | `/api/v1/seller/tax/set` | 微前端,微前端,微前端,财务bundle | `SetSellerTax` |
| `POST` | `/api/v1/tax/bmbe` | 微前端,财务bundle | `SubmitBMBE` |
| `?` | `/api/v1/tax/certificate/file` | 微前端,财务bundle | `DownloadFile` |
| `GET` | `/api/v1/tax/china_entity_income_report/search` | 微前端,财务bundle | `SearchChinaEntityIncomeReportListInfo` |
| `GET` | `/api/v1/tax/china_entity_income_report_apply_time_list/get` | 微前端,财务bundle | `GetApplyReportTimeForChinaEntityIncome` |
| `GET` | `/api/v1/tax/china_entity_income_report_detail/download` | 微前端,财务bundle | `DownloadChinaEntityIncomeReportDetail` |
| `POST` | `/api/v1/tax/china_entity_income_report_exchange_rate/get` | 微前端,财务bundle | `GetExchangeRateForChinaEntityIncome` |
| `GET` | `/api/v1/tax/china_entity_income_report_taxpayer_list/get` | 微前端,财务bundle | `GetTaxpayerNameForChinaEntityIncome` |
| `POST` | `/api/v1/tax/contract/download_file` | 微前端,财务bundle | `DownloadContract` |
| `POST` | `/api/v1/tax/contract/download_invoice` | 微前端,财务bundle | `DownloadContractInovice` |
| `POST` | `/api/v1/tax/contract/search` | 微前端,财务bundle | `SearchContract` |
| `POST` | `/api/v1/tax/declare/query` | 微前端,财务bundle | `QueryTaxDeclare` |
| `POST` | `/api/v1/tax/declare/submit` | 微前端,财务bundle | `TaxDeclare` |
| `POST` | `/api/v1/tax/entity_change/tax_task` | 微前端,财务bundle | `GetEntityChangeTaxTask` |
| `?` | `/api/v1/tax/estimated_gmv` | 微前端,财务bundle | `EstimatedGMV` |
| `POST` | `/api/v1/tax/faq/tax_document` | 微前端,财务bundle | `GetTaxDocumentFaqList` |
| `POST` | `/api/v1/tax/file/upload` | 微前端,财务bundle | `UploadFile` |
| `POST` | `/api/v1/tax/form1099k/detail/download` | 微前端,财务bundle | `DownloadFormDetail1099` |
| `POST` | `/api/v1/tax/form1099k/detail/generate` | 微前端,财务bundle | `GenerateFormDetail1099k` |
| `GET` | `/api/v1/tax/form1099k/detail/get_list` | 微前端,财务bundle | `GetFormDetail1099List` |
| `GET` | `/api/v1/tax/form1099k/download` | 微前端,财务bundle | `DownloadForm1099` |
| `GET` | `/api/v1/tax/form1099k/get_list` | 微前端,财务bundle | `GetForm1099List` |
| `POST` | `/api/v1/tax/ful_inv/get_list` | 微前端,财务bundle | `GetFulInvList` |
| `POST` | `/api/v1/tax/ful_inv/upload` | 微前端,财务bundle | `UploadFulInv` |
| `POST` | `/api/v1/tax/get_country_list` | 微前端,财务bundle | `GetCountryList` |
| `POST` | `/api/v1/tax/global_seller_info/clear` | 微前端,财务bundle | `ClearGlobalSellerEntityInfo` |
| `POST` | `/api/v1/tax/global_seller_info/get` | 微前端,财务bundle | `GetGlobalSellerEntityInfo` |
| `POST` | `/api/v1/tax/global_seller_info/set` | 微前端,财务bundle | `UpsertGlobalSellerEntityInfo` |
| `POST` | `/api/v1/tax/grayscale` | 微前端,财务bundle | `QueryGrayscaleStatus` |
| `POST` | `/api/v1/tax/invoice/details_export` | 客户端,微前端,财务bundle | `ExportInvoiceDetails` |
| `POST` | `/api/v1/tax/invoice/export` | 客户端,微前端,财务bundle | `BatchExportInvoice` |
| `GET` | `/api/v1/tax/invoice/export_task` | 客户端,微前端,财务bundle | `ListExportedFiles` |
| `GET` | `/api/v1/tax/invoice/file` | 客户端,微前端,财务bundle | `DownloadFile` |
| `POST` | `/api/v1/tax/invoice/pay` | 微前端,财务bundle | `PayInvoice` |
| `POST` | `/api/v1/tax/invoice/search` | 客户端,微前端,财务bundle | `SearchInvoice` |
| `POST` | `/api/v1/tax/meta/info/get` | 微前端,财务bundle | `GetTaxMetaInfo` |
| `POST` | `/api/v1/tax/nfe_tool/get` | 微前端,财务bundle | `GetNFeToolCfg` |
| `POST` | `/api/v1/tax/nfe_tool/refresh` | 微前端,财务bundle | `RefreshNFeToolCfg` |
| `POST` | `/api/v1/tax/nfe_tool/set` | 微前端,财务bundle | `SetNFeToolCfg` |
| `POST` | `/api/v1/tax/reimbursement/fee_list` | 微前端,财务bundle | `FeeList` |
| `GET` | `/api/v1/tax/reimbursement/history_task` | 微前端,财务bundle | `ListReimbursementTask` |
| `POST` | `/api/v1/tax/reimbursement/invoice_search` | 微前端,财务bundle | `SearchInvoiceForReimbursement` |
| `POST` | `/api/v1/tax/reimbursement/task` | 微前端,财务bundle | `SubmitReimbursementTask` |
| `POST` | `/api/v1/tax/reimbursement/tax_info` | 微前端,财务bundle | `DefaultTaxInfo` |
| `GET` | `/api/v1/tax/report/search` | 客户端,微前端,财务bundle | `SearchReport` |
| `POST` | `/api/v1/tax/sd` | 微前端,财务bundle | `SubmitSD` |
| `?` | `/api/v1/tax/shop_entity` | 客户端,微前端,财务bundle | `ShopEntity` |
| `POST` | `/api/v1/tax/statement_letter` | 微前端,财务bundle | `SubmitSL` |
| `POST` | `/api/v1/tax/tax_amount` | 微前端,财务bundle | `CalculateTax` |
| `POST` | `/api/v1/tax/tax_info/clear` | 微前端,财务bundle | `ClearSellerTax` |
| `GET` | `/api/v1/tax/tax_info/confirm` | 微前端,财务bundle | `ConfirmTaxInfo` |
| `POST` | `/api/v1/tax/tax_info/get` | 客户端,微前端,财务bundle | `GetSellerTax` |
| `POST` | `/api/v1/tax/tax_info/get_us_display_info` | 微前端,财务bundle | `GetUsDisplayInfo` |
| `POST` | `/api/v1/tax/tax_info/set` | 微前端,财务bundle | `SetSellerTax` |
| `POST` | `/api/v1/tax/tax_info/set_addr` | 微前端,财务bundle | `SetSellerAddress` |
| `POST` | `/api/v1/tax/tax_info/submit_verify` | 微前端,财务bundle | `SubmitVerify` |
| `POST` | `/api/v1/tax/tax_info/upsert_seller_invoice_payment_info` | 微前端,财务bundle | `UpsertSellerInvoicePaymentInfo` |
| `POST` | `/api/v1/tax/vcs/config/deactivate` | 微前端,财务bundle | `DeactivateVCSConfig` |
| `POST` | `/api/v1/tax/vcs/config/list` | 微前端,财务bundle | `ListVCSConfigVersion` |
| `GET` | `/api/v1/tax/vcs/config/ptc_codes` | 微前端,财务bundle | `GetPTCCodes` |
| `POST` | `/api/v1/tax/vcs/config/upsert` | 微前端,财务bundle | `UpsertVCSConfig` |
| `POST` | `/api/v1/tax/wht_certificate` | 微前端,财务bundle | `SubmitWhtCertificate` |
| `?` | `/api/v2/pay/settlement/file/list` | 客户端 |  |
| `POST` | `/widget/api/v1/pay/creator/tax_info/get` | 微前端,财务bundle | `WidgetGetTaxInfoForCreator` |
| `POST` | `/widget/api/v1/pay/creator/tax_info/set` | 微前端,财务bundle | `WidgetSetTaxInfoForCreator` |
| `POST` | `/widget/api/v1/pay/meta/info/get` | 微前端,财务bundle | `WidgetGetMetaInfo` |
| `POST` | `/widget/api/v1/pay/settlement/payout/manage_link` | 微前端,财务bundle | `WidgetGetPayoutManageLink` |
| `POST` | `/widget/api/v1/pay/settlement/payout/pi_infos` | 微前端,财务bundle | `WidgetGetPayoutPiInfos` |
| `POST` | `/widget/api/v1/pay/tax_audit` | 微前端,财务bundle | `WidgetTaxAudit` |
| `POST` | `/widget/api/v1/pay/tax_info/get` | 微前端,财务bundle | `WidgetGetTaxInfo` |
| `POST` | `/widget/api/v1/pay/tax_info/set` | 微前端,财务bundle | `WidgetSetTaxInfo` |
| `GET` | `/widget/api/v1/seller/growth_center/reward_penalty/settlement_period_compliance/get` | 早期 |  |
| `POST` | `/widget/api/v1/tax/file/upload` | 微前端,财务bundle | `WidgetUploadFile` |
| `POST` | `/widget/api/v1/tax/meta/info/get` | 微前端,财务bundle | `WidgetGetTaxMetaInfo` |
| `GET` | `/widget/api/v1/tax/tax_info/get` | 微前端,财务bundle | `WidgetGetSellerTax` |
| `POST` | `/widget/api/v1/tax/tax_info/get_us_display_info` | 微前端,财务bundle | `WidgetGetUsDisplayInfo` |
| `POST` | `/widget/api/v1/tax/tax_info/set` | 微前端,财务bundle | `WidgetSetSellerTax` |

## 联盟 / 达人（524）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/v1/affiliate/account/all_sellers/get` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/account/info` | 客户端,联盟bundle |  |
| `GET` | `/api/v1/affiliate/account/info_v2` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/announcement/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/announcement/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/announcement/read` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/approve/check` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets/creator-management` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets/creator-management/bulk-im` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets/creator/bulk-im` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets/quota/overview` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/assets/video-analysis` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/auction_stock/products/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/auction_stock/summary` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/app/account/info` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/category/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/homepage/external_link_program/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/mupdate` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/types/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/backend/homepage/feature_switch/update` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/homepage/information_card/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/homepage/todo_dashboard/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/backend/homepage/todo_list/confirm` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/backend/homepage/todo_list/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/banner` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/contact_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/detail/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/edit` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/modify_sample_quota` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/partner/search` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/partners/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/product/approve` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/product/cancel` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/product_performance/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/products/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/register` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/register_contact_info` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/registered_products/edit` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/registered_products/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/seller/permission/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/seller/product/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/campaign/single_product_performance/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/campaign/update/status` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/cmp/contact` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/cmp/contact_types` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/auction-stock` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/open-collaboration` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/open-collaboration/bulk-edit` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/open-collaboration/creator-applications` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/open-collaboration/growth-products` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-description` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/campaign-edit` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/edit` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/flat-fee/send-result` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/collaboration/target-invitation/select` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/commission_unique/check` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/config` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/creator` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator/rankings` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/creator/search` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator/vertical-list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator_application/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator_data/filter_option/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator_marketplace/filled/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/creator_marketplace/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/creator_marketplace/mget` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/errorpage` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/export_history` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/export_link` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/export_order` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/export_order_task` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/export_order_v2` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/grayscale_strategy/check` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/guide/articles` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/has_agent` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/homepage` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/log_out_agent` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/article` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/creator/auth_profiles` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/creator/profile` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/feelgood/c_token` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/feelgood/token` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/image/c_url` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/image/upload_token` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/image/url` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/lux/invitation/available_list` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/invitation/c_detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/invitation/creator/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/invitation/detail` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/lux/notification/im/latest` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/lux/notification/im/message` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/lux/notification/im/unread` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/lux/notification/im/unread_count` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/partner/product/filter` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/partner/product/ranking/entry` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/partner/product/ranking/tab` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/creator/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/product/c_detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/product/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/product/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/target_plan/c_detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/target_plan/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/plan/target_plan/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/product/c_detail_list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/product/category/children` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/product/category/childrenv2` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/sample/apply` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/sample/c_info` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/sample/info` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/lux/screenshot` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/lux/screenshot/status` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/menu` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/affiliate/meta_plan/search` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/name_list/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/new_request/count` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/classify/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/config` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/ec_permission` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/get_latest_creator_notification` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/group/schemas` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/conversation/update` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/conversation/update_tag` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/entrance_check` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/im/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/permission` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/relation/update` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/im/seller_category` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/im/shop_quota` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/list_schemas` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/mark_as_clicked` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/notification/mark_as_read` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/notification/unread_count` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_collaboration/ad/account_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/ad_commission/suggest_commission/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/affected_promotion_info/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/auction_commission/detail` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/authorized_ad_video/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/commission_history/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/commission_version/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/creator_application/batch_review` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/creator_application/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/opt_in/card/get` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/open_collaboration/product_creator_relation/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_collaboration/product_creator_relation/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/product_creator_relation/terminate` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/ad_commission/upsert` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_collaboration/promote_products/async_task/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/async_task/submit` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/auction_commission/upsert` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_collaboration/promote_products/count` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/gmv_max/suggest` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/gmv_max/upsert` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/terminate` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_collaboration/promote_products/upsert` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/batch_create` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/create` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/delete` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/excel_check` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/list_search` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_plan/allowlist/performance` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_plan/allowlist/pre_create` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/open_plan/allowlist/pre_create_v2` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/open_plan/allowlist/pre_delete` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/opt_in/sample/check` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/orders` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/agency` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/agency/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/collaboration-overview` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/discover-partners` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/discover-partners/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/exclusive` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/exclusive/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/find-mcn` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/find-mcn/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/find-mcn/share` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/initiated` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/initiated/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/initiated/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/invite/creator/batch/create` | 客户端 |  |
| `?` | `/api/v1/affiliate/partner/invite/creator/mget` | 客户端 |  |
| `?` | `/api/v1/affiliate/partner/marketplace` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/marketplace/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/partner-collabs` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/partner-collabs/agency/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/partner-collabs/exclusive/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/partner-collabs/seller/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/partner-collabs/seller/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/registered` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/registered/detail` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/partner/root` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/bind` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/plan/check_exist` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/check_if_has_plans_by_seller_id` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/creator_count` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/gen_share_url` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/plan/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/mget_seller_landing_task_extra` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/mset_seller_landing_task_extra` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/recommend_commissions/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan/sync` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/plan_detail/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/plan_status/update` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform/account/root` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform/account/shop` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform/homepage` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform/homepage/announcements` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/platform/personalization-settings` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/product/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/product/search` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/product/selection_status/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/product_category/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/product_selection/list` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/promotion_position` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/recommend_commission/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/relation/operate` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/relation/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/request/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/request_status/update` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/resource/action/report` | 联盟bundle |  |
| `GET` | `/api/v1/affiliate/resource/list/get` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/affiliate/review/creator/metrics` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/review/creator/reviews` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/apply/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/approved_fail/count` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/approved_fail/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/auto_placement_rule/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/auto_placement_rule/save` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/groi/join` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/groi/perf/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/groi/perf/summary` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/groi/seller_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/group/action` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/group/label_menu` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/group/list` | 客户端,联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/group_order/config` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/group_order/submit` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/hint/search` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/im_fulfillment_reminder/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/notice` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/performance` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/placement_rule/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/placement_rule/open_plan_hosting/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/placement_rule/save` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/recommendation/approval/banner` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/recommendation/approval/inference/trigger` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/recommendation/approval/preference/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/recommendation/approval/result` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/refundable/apply/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/refundable/tab/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/review/delete` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/review/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/review/save` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/rule/async_task/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/rule/async_task/submit` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/rule/del` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/rule/mget` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/rule/save` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/sample-request` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/sample-settings` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/seller_setting/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/seller_setting/save` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/settings/product/batch_save` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/settings/product/config` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/settings/product/detail` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/settings/product/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/settings/product/mget` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/settings/product/save` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/shipment/info` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/sku_config/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/support4pl/status` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sample/tab/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/tag/delete` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/ui/version/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/sample/ui/version/set` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/seller/contact_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/seller/contact_info/update` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/seller/effective_time/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/seller/invitation/contact_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/seller/invitation/contact_info/update` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/shop_plan/create` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/shop_plan/get` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/shop_plan/update` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/shop_setting/change` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/shop_setting/get` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/sub_plan/list` | 联盟bundle |  |
| `POST` | `/api/v1/affiliate/suggest_commission/default` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/violation/shop/list` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/violation/unread/check` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/withhold_tax/info` | 联盟bundle |  |
| `?` | `/api/v1/affiliate/withhold_tax/set` | 联盟bundle |  |
| `POST` | `/api/v1/insights/affiliate/creator/search/suggestions` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/insights/affiliate/creator/video/list` | 联盟bundle |  |
| `POST` | `/api/v1/insights/seller/shop/video/affiliate/creator/list/search` | 微前端,微前端 | `GetSellerShopVideoAffiliateCreatorListSearchQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/affiliate/list` | 微前端,微前端 | `GetProductTrafficAffiliateListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/shop/affiliate/list` | 微前端 | `GetProductTrafficShopAffiliateListQuery` |
| `?` | `/api/v1/oec/affiliate/campaign/config/options/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/creator/ec/stats` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/cmp/creator/invite/list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/creator/rank/list/get` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/filter` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/main/industries` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/cmp/shop/invite/send` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/available_date/get` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/compass/creator_detail/creator_profile/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/creator_detail/detail_list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/export_task/create` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/compass/export_task/export` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/export_task/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/outreach/creator/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/outreach/funnel_conversion/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/outreach/key_metrics/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/posted_video_list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/product_detail/core_performance/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/product_detail/detail_list/get` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/compass/product_detail/product_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/product_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/sample/core_performance/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/sample/decomposition/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/sample/detail_list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/sample/funnel_conversion/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/transaction/core_performance/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/transaction/decomposition/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/compass/transaction/detail_list/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/config` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/card/message` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/entrance/check` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/im/get/token` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/last_new_message` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/options` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/permission` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/im/product/info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/product/pack` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/im/translate/message` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/accept` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/audit/result` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/auth/banner` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/auth/banner/cancel` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/brand/video/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/campaign/action` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/fe/resource` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/filter` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/campaign/info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/campaign/product_search` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/collection/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/confirm_page/confirm` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/confirm_page/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/decline` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/decline/feedback` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/detail` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/entrance` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/filter/config` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/new/clear` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/new_feature_remind` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/product/search` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/invitation/products` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/reactive` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/recommend` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/search` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/unread/clear` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/invitation/unread/count` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/marketplace/4partner/find` | 客户端 |  |
| `?` | `/api/v1/oec/affiliate/creator/marketplace/4partner/option` | 客户端 |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/ai/find` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/content/stats` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/creator/profile/stats` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/find` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/follower/stats` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/invitation_recommend_creator` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/mcn/info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/option` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/profile` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/recommendation` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/search` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/search_new` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/arrival` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/category/creator` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/marketplace/vertical/category/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/search/platform_quest` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/settings/contact` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/settings/contact/update` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/creator/settings/preference` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/settings/preference/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/creator/vertical/category/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/block_creator/create` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/block_creator/delete` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/block_creator/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/block_creator/query` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/cmp/search` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/batch_create` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/crm/creator/batch_task/result/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/batch_task/submit` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/crm/creator/block/setting/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/block/setting/update` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/crm/creator/content/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/create` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/delete` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/crm/creator/detail_info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/import` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/import_check` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/product/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/tag/bind` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/creator/target_collaboration/list` | 联盟bundle |  |
| `GET` | `/api/v1/oec/affiliate/crm/creator/upper_limit/get` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/im_messages/batch_send` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/material/check` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/tag/create` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/tag/delete` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/crm/tag/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm/tag/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/crm_toc/block_creator/query` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/recommend_invitation/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/recommend_product/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/diagnosis/outreach/sample_info/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/diagnosis/recommendation/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/guidance_page/creator_fans_portrait` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/guidance_page/creator_recommendation` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/guidance_page/creator_stats` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/opportunity_product/search` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/scopemetas` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/dismiss` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/feature_control` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/card/message` | 联盟bundle |  |
| `GET` | `/api/v1/oec/affiliate/seller/im/get/token` | 客户端,客户端,联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/im/product/info` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/im/product/list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/remind/can` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/remind/send` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/settings/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/settings/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/template/message` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/im/translate/message` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/detail` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/approve` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/edit` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video/post` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/creator/video_list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/brand_deal/pay` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation/products_info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/create` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/detail` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/brand_deal/update` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/banner` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/create` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/creator_set` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/criteria` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/product_set` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/shop_validate` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/campaign/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/commission/history` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/conflict_check` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/conflict_check/resolve` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/count` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/create` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator/relevancy/prediction` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator_promotion_detail` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creator_video_list` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/creators_add` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/detail` | 客户端,联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/invitation_group/detail/creators` | 联盟bundle |  |
| `GET` | `/api/v1/oec/affiliate/seller/invitation_group/general/config` | 客户端,联盟bundle |  |
| `GET` | `/api/v1/oec/affiliate/seller/invitation_group/invitation/limit` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/latest_basic_info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/product/intra_check` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/product_creator_relation` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/promotion/configs` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/rate_limit_info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/re_update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/recommend/cache` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/creator` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/invitation` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/search/product` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/sensitive_text_check` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/share/short_url` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/terminate` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/update` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/invitation_group/vertical/conflict` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/previous_invitation/use_status` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/quota/connected_creators` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/quota/connection/check` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/quota/info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/search/feedback/submit` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/search/initial_questions/get` | 联盟bundle |  |
| `?` | `/api/v1/oec/affiliate/seller/shop/info` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/shoppable_photo_discount/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/shoppable_photo_discount/update` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/wish_list/search/creator` | 客户端,联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/seller/wish_list/update/creator` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/shop/settings/get` | 联盟bundle |  |
| `POST` | `/api/v1/oec/affiliate/shop/settings/update` | 联盟bundle |  |
| `?` | `/api/v1/partner/profile/partner_info` | 客户端 |  |
| `POST` | `/api/v2/affiliate/open_plan/create` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/open_plan/delete` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/open_plan/list` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/open_plan/product_selection/list` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/open_plan/update` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/shop_plan/create` | 联盟bundle |  |
| `?` | `/api/v2/affiliate/shop_plan/get` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/shop_plan/quit` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/shop_plan/update` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/target_plan/create` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/target_plan/product_selection/guide_new_seller/list` | 联盟bundle |  |
| `POST` | `/api/v2/affiliate/target_plan/update` | 联盟bundle |  |

## 商品 / 库存 / 定价（431）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/product/actions/list` | 微前端,早期 | `ListProductActions` |
| `POST` | `/api/v1/product/async_task/create` | 微前端,早期 | `CreateTask` |
| `POST` | `/api/v1/product/async_task/delete` | 微前端,早期 | `DeleteTask` |
| `POST` | `/api/v1/product/async_task/list` | 微前端 | `ListTask` |
| `POST` | `/api/v1/product/async_task/update` | 早期 |  |
| `GET` | `/api/v1/product/audit/product/get` | 微前端 | `GetAuditProduct` |
| `?` | `/api/v1/product/bid/bids/list` | 微前端 | `ListBids` |
| `POST` | `/api/v1/product/bid/cancel` | 微前端 | `CancelBid` |
| `?` | `/api/v1/product/bid/get` | 微前端 | `GetBidResult` |
| `?` | `/api/v1/product/bid/reference-products/list` | 微前端 | `ListReferenceProducts` |
| `POST` | `/api/v1/product/bid/seller-attribute/set` | 微前端 | `ConfigureSellerAttribute` |
| `POST` | `/api/v1/product/bid/seller-data/get` | 微前端 | `GetSellerData` |
| `POST` | `/api/v1/product/bid/seller-products/list` | 微前端 | `ListSellerProducts` |
| `POST` | `/api/v1/product/bid/set` | 微前端 | `SetBid` |
| `POST` | `/api/v1/product/brand/check` | 微前端,微前端,早期,早期 | `CheckBrand` |
| `POST` | `/api/v1/product/brand/create` | 微前端,微前端,早期,早期 | `CreateBrand` |
| `POST` | `/api/v1/product/brand/delete` | 微前端,微前端,早期,早期 | `DeleteBrand` |
| `POST` | `/api/v1/product/brand/detail` | 微前端,微前端,早期,早期 | `BrandDetail` |
| `GET` | `/api/v1/product/brand/list` | 微前端 | `ListBrand` |
| `GET` | `/api/v1/product/brand/suggest` | 微前端 | `SuggestBrands` |
| `POST` | `/api/v1/product/brand/update` | 微前端,微前端,早期,早期 | `UpdateBrand` |
| `POST` | `/api/v1/product/brand_rec/list` | 微前端,早期 | `ListRecommendedBrands` |
| `GET` | `/api/v1/product/bulletin/list` | 微前端,早期 | `GetProductBulletins` |
| `POST` | `/api/v1/product/bundles/mactivate` | 微前端,微前端,早期,早期 | `MActivateBundles` |
| `POST` | `/api/v1/product/bundles/mdeactivate` | 微前端,微前端,早期,早期 | `MDeactivateBundles` |
| `POST` | `/api/v1/product/bundles/mdelete` | 微前端,微前端,早期,早期 | `MDeleteBundles` |
| `GET` | `/api/v1/product/categories/search` | 微前端 | `SearchCategories` |
| `GET` | `/api/v1/product/category/bind_info/get` | 微前端 | `GetCategoryBindInfo` |
| `POST` | `/api/v1/product/category/bind_info/multi_get` | 微前端 | `MultiGetCategoryBindInfo` |
| `POST` | `/api/v1/product/category/migrate` | 微前端,早期 | `MigrateCategory` |
| `GET` | `/api/v1/product/category/template/list` | 微前端 | `GetCategoryTemplateList` |
| `POST` | `/api/v1/product/category/template/submit` | 微前端,早期 | `SubmitCategoryTemplate` |
| `POST` | `/api/v1/product/category/template/value` | 微前端 | `GetCategoryTemplateValue` |
| `POST` | `/api/v1/product/category_rec/list` | 微前端,早期 | `ListRecommendedCategories` |
| `GET` | `/api/v1/product/child_categories/list` | 微前端 | `ListChildCategories` |
| `POST` | `/api/v1/product/combo/sku/quantity/get` | 早期 |  |
| `POST` | `/api/v1/product/commission/config/get` | 微前端,微前端,早期,早期 | `GetCommissionConfig` |
| `POST` | `/api/v1/product/commission/delete` | 微前端,微前端,早期,早期 | `DeleteCommission` |
| `POST` | `/api/v1/product/commission/set` | 微前端,微前端,早期,早期 | `SetCommission` |
| `POST` | `/api/v1/product/comp/get_schema` | 微前端 | `GetSchema` |
| `POST` | `/api/v1/product/comp/get_schema_v2` | 早期 |  |
| `POST` | `/api/v1/product/comp/refetch_data` | 早期 |  |
| `POST` | `/api/v1/product/comp/refetch_schema` | 早期 |  |
| `GET` | `/api/v1/product/creator_stock/creator/list` | 微前端,微前端 | `SearchCreator` |
| `POST` | `/api/v1/product/creator_stock/list` | 微前端,微前端,早期 | `ListCreatorStock` |
| `GET` | `/api/v1/product/creator_stock/product/list` | 微前端,微前端 | `SearchCreatorProduct` |
| `GET` | `/api/v1/product/creator_stock/status/check` | 微前端,微前端 | `CheckCreatorStockStatus` |
| `POST` | `/api/v1/product/creator_stock/status/update` | 微前端,微前端,早期 | `UpdateCreatorStockStatus` |
| `POST` | `/api/v1/product/creator_stock/submit` | 微前端,微前端,早期 | `SubmitCreatorStock` |
| `GET` | `/api/v1/product/cross/shop/search` | 微前端 | `CrossShopSearchProduct` |
| `POST` | `/api/v1/product/desc/create_generate_task` | 微前端,早期 | `CreateDescGenerateTask` |
| `POST` | `/api/v1/product/desc/pull_generate_result` | 微前端,早期 | `PullDescGenerateResult` |
| `?` | `/api/v1/product/description_prettify/html_to_image` | 微前端 | `ConvertHtmlToImage` |
| `?` | `/api/v1/product/description_prettify/templates` | 微前端 | `GetDescriptionTemplates` |
| `POST` | `/api/v1/product/diagnosis/item/calculate` | 微前端,早期 | `CalculateProductDiagnosticItems` |
| `GET` | `/api/v1/product/diagnosis/overview/get` | 微前端,早期,早期 | `GetSellerDiagnosisOverview` |
| `GET` | `/api/v1/product/download_instruction/list` | 微前端,早期,早期 | `ListProductDownloadInstruction` |
| `POST` | `/api/v1/product/duplication/title/check` | 微前端,微前端,早期,早期 | `CheckTitleDuplication` |
| `POST` | `/api/v1/product/external/detail` | 早期 |  |
| `POST` | `/api/v1/product/external/search` | 早期 |  |
| `POST` | `/api/v1/product/global/async_task/create` | 微前端,早期 | `CreateGlobalTask` |
| `POST` | `/api/v1/product/global/async_task/list` | 微前端 | `ListGlobalTask` |
| `POST` | `/api/v1/product/global/brand/create` | 微前端,早期 | `CreateBrand` |
| `GET` | `/api/v1/product/global/brand/list` | 微前端 | `ListGlobalBrand` |
| `GET` | `/api/v1/product/global/brand/suggest` | 微前端 | `SuggestGlobalBrands` |
| `GET` | `/api/v1/product/global/categories/search` | 微前端 | `SearchGlobalCategories` |
| `GET` | `/api/v1/product/global/category/bind_info/get` | 微前端 | `GetGlobalCategoryBindInfo` |
| `GET` | `/api/v1/product/global/category_rec/list` | 微前端 | `ListRecommendedCategories` |
| `GET` | `/api/v1/product/global/child_categories/list` | 微前端 | `ListGlobalChildCategories` |
| `POST` | `/api/v1/product/global/draft/save` | 微前端,早期 | `SavaGlobalDraft` |
| `GET` | `/api/v1/product/global/global_third_party/get` | 微前端 | `GetGlobalAndThirdPartyProduct` |
| `POST` | `/api/v1/product/global/guide_context/get` | 微前端,早期 | `GetGuideContext` |
| `POST` | `/api/v1/product/global/material_center/account` | 微前端,早期 | `GetAccount` |
| `POST` | `/api/v1/product/global/material_center/account/initial` | 微前端,早期 | `InitialAccount` |
| `POST` | `/api/v1/product/global/material_center/file/list` | 微前端,早期 | `ListFileView` |
| `POST` | `/api/v1/product/global/material_center/folder/create` | 微前端,早期 | `CreateFolder` |
| `POST` | `/api/v1/product/global/material_center/folder/delete` | 微前端,早期 | `MDeleteFolder` |
| `POST` | `/api/v1/product/global/material_center/folder/edit` | 微前端,早期 | `EditFolder` |
| `POST` | `/api/v1/product/global/material_center/folder/list` | 微前端 | `ListFolderTree` |
| `POST` | `/api/v1/product/global/material_center/image/segment` | 微前端,早期 | `SegmentImage` |
| `POST` | `/api/v1/product/global/material_center/image_background/optimize` | 微前端,早期 | `OptimizeImageBackground` |
| `POST` | `/api/v1/product/global/material_center/material/batch_create` | 微前端,早期 | `BatchCreateMaterial` |
| `POST` | `/api/v1/product/global/material_center/material/create` | 微前端,早期 | `CreateMaterial` |
| `POST` | `/api/v1/product/global/material_center/material/delete` | 微前端,早期 | `MDeleteMaterial` |
| `POST` | `/api/v1/product/global/material_center/material/edit` | 微前端,早期 | `EditMaterial` |
| `POST` | `/api/v1/product/global/material_center/material/move` | 微前端,早期 | `BatchMoveMaterial` |
| `POST` | `/api/v1/product/global/material_center/material/query` | 微前端,早期 | `QueryMaterials` |
| `POST` | `/api/v1/product/global/material_center/slice_switch` | 微前端,早期 | `SetVideoSliceSwitch` |
| `POST` | `/api/v1/product/global/notifications/get` | 微前端 | `GetNotifications` |
| `POST` | `/api/v1/product/global/parcel/check` | 微前端,早期 | `CheckGlobalProductParcel` |
| `POST` | `/api/v1/product/global/price/calculate` | 微前端,早期 | `CalculateGlobalPrice` |
| `POST` | `/api/v1/product/global/price/limit` | 微前端,早期 | `GetGlobalPriceLimit` |
| `POST` | `/api/v1/product/global/price/mcalculate` | 微前端,早期 | `MCalculateGlobalPrice` |
| `POST` | `/api/v1/product/global/product/get` | 微前端 | `GetGlobalProduct` |
| `POST` | `/api/v1/product/global/product/publish` | 微前端,早期 | `PublishGlobalProduct` |
| `POST` | `/api/v1/product/global/product/save_and_publish` | 微前端,早期 | `SaveAndPublishProduct` |
| `POST` | `/api/v1/product/global/product/save_live` | 微前端,早期 | `SaveLiveProduct` |
| `POST` | `/api/v1/product/global/product/stock/edit` | 微前端,早期 | `EditProductStock` |
| `GET` | `/api/v1/product/global/product_creation/preload` | 微前端 | `PreloadGlobalProductCreation` |
| `GET` | `/api/v1/product/global/product_creation/preload_all_categories` | 微前端 | `PreloadAllGlobalCategories` |
| `POST` | `/api/v1/product/global/products/delete` | 微前端,早期 | `MDeleteGlobalProducts` |
| `GET` | `/api/v1/product/global/products/list` | 微前端 | `ListGlobalProducts` |
| `GET` | `/api/v1/product/global/regions/mget` | 微前端,早期 | `MGetGlobalRegions` |
| `POST` | `/api/v1/product/global/size_chart/batch_save` | 微前端,早期 | `BatchCreateSizeChart` |
| `POST` | `/api/v1/product/global/size_chart/config_product` | 微前端,早期 | `ConfigProductSizeChart` |
| `POST` | `/api/v1/product/global/size_chart/delete` | 微前端,早期 | `DeleteSizeChart` |
| `POST` | `/api/v1/product/global/size_chart/edit` | 微前端,早期 | `EditSizeChart` |
| `POST` | `/api/v1/product/global/size_chart/get_bind_info` | 微前端,早期 | `GetSizeChartBindInfo` |
| `POST` | `/api/v1/product/global/size_chart/identify` | 微前端,早期 | `IdentifySizeChart` |
| `POST` | `/api/v1/product/global/size_chart/list_product_type` | 微前端,早期 | `ListSizeChartProductType` |
| `POST` | `/api/v1/product/global/size_chart/save` | 微前端,早期 | `CreateSizeChart` |
| `POST` | `/api/v1/product/global/size_chart/search` | 微前端,早期 | `SearchSizeChart` |
| `POST` | `/api/v1/product/global/sku/price/edit` | 微前端,早期 | `EditPrice` |
| `POST` | `/api/v1/product/global/sku/stock/edit` | 微前端,早期 | `EditStock` |
| `POST` | `/api/v1/product/global/skus/list` | 微前端 | `ListGlobalProductSKUs` |
| `POST` | `/api/v1/product/global/spu/match` | 微前端,早期 | `MatchSpu` |
| `POST` | `/api/v1/product/global/tab/count/get` | 微前端 | `GetGlobalProductTabCount` |
| `POST` | `/api/v1/product/global/texts_translation/get` | 微前端,早期 | `MGetTextsTranslation` |
| `POST` | `/api/v1/product/global/third_party/link` | 微前端,早期 | `LinkThirdPartyProduct` |
| `GET` | `/api/v1/product/global/third_party/list` | 微前端 | `ListThirdPartyProducts` |
| `POST` | `/api/v1/product/global/third_party/unlink` | 微前端,早期 | `UnLinkThirdPartyProduct` |
| `GET` | `/api/v1/product/global/unpublished/products/list` | 微前端 | `ListUnpublishedGlobalProducts` |
| `POST` | `/api/v1/product/global/warehouses/mget` | 微前端 | `MGetGlobalSellerWarehouses` |
| `POST` | `/api/v1/product/gpr/compliance_review/confirm` | 早期 |  |
| `POST` | `/api/v1/product/gpr/high_potential/silent_mode/event/record` | 早期 |  |
| `POST` | `/api/v1/product/gpr/source/precheck` | 早期 |  |
| `POST` | `/api/v1/product/gpr_overview/get` | 微前端,早期 | `GetGprOverview` |
| `POST` | `/api/v1/product/gpr_rule/compliance_property/list` | 早期 |  |
| `POST` | `/api/v1/product/gpr_rule/submit` | 微前端,早期 | `SubmitGprRules` |
| `POST` | `/api/v1/product/growth_info/submit` | 早期 |  |
| `POST` | `/api/v1/product/guide/instructions/get` | 微前端,早期 | `GetGuideInstructions` |
| `POST` | `/api/v1/product/guide_context/get` | 微前端,微前端,早期,早期 | `GetGuideContext` |
| `POST` | `/api/v1/product/image/quality/check` | 微前端,微前端,早期,早期 | `CheckImageQuality` |
| `POST` | `/api/v1/product/image_translation_rule/get` | 早期 |  |
| `POST` | `/api/v1/product/image_translation_rule/submit` | 早期 |  |
| `POST` | `/api/v1/product/images/msubmit` | 客户端,微前端,微前端,早期,早期 | `MSubmitProductImage` |
| `POST` | `/api/v1/product/link/create` | 微前端,早期 | `MCreateLinks` |
| `POST` | `/api/v1/product/link/deactivate` | 微前端,早期 | `MDeactivateLinks` |
| `POST` | `/api/v1/product/link/edit` | 微前端,早期 | `EditLink` |
| `POST` | `/api/v1/product/link/get` | 微前端 | `GetLink` |
| `GET` | `/api/v1/product/link/recommend` | 微前端 | `SearchRecommendedLinks` |
| `POST` | `/api/v1/product/link/search` | 微前端,早期 | `SearchLinks` |
| `GET` | `/api/v1/product/list/seller/warehouses` | 微前端,早期,早期 | `ListSellerWarehouses` |
| `POST` | `/api/v1/product/local/bundle/create` | 微前端,微前端,早期,早期 | `CreateLocalBundle` |
| `POST` | `/api/v1/product/local/bundle/edit` | 微前端,微前端,早期,早期 | `EditLocalBundle` |
| `POST` | `/api/v1/product/local/bundle/get` | 微前端 | `GetLocalBundle` |
| `POST` | `/api/v1/product/local/bundles/list` | 微前端,微前端,早期,早期 | `ListLocalBundles` |
| `POST` | `/api/v1/product/local/draft/partial_edit` | 微前端,早期 | `PartialEditLocalDraft` |
| `POST` | `/api/v1/product/local/draft/save` | 客户端,微前端,微前端,早期,早期 | `SaveLocalDraft` |
| `POST` | `/api/v1/product/local/edit/template` | 微前端,微前端,早期,早期 | `GetProductLocalEditTemplate` |
| `POST` | `/api/v1/product/local/edit_image/list` | 微前端,微前端,早期,早期 | `ListEditImageProduct` |
| `POST` | `/api/v1/product/local/edit_pending/list` | 微前端 | `ListEditPendingProduct` |
| `GET` | `/api/v1/product/local/has_edit_pending_product/get` | 微前端,早期,早期 | `HasEditPendingProduct` |
| `POST` | `/api/v1/product/local/image/save` | 微前端,微前端,早期,早期 | `SaveLocalImageDraft` |
| `POST` | `/api/v1/product/local/product/action/pre_check` | 微前端 | `ProductActionPreCheck` |
| `POST` | `/api/v1/product/local/product/bulk_create` | 微前端,早期 | `CreateBulkLocalProduct` |
| `POST` | `/api/v1/product/local/product/copy` | 微前端 | `CopyLocalProduct` |
| `POST` | `/api/v1/product/local/product/create` | 客户端,微前端,微前端,早期,早期 | `CreateLocalProduct` |
| `POST` | `/api/v1/product/local/product/edit` | 客户端,微前端,微前端,早期,早期 | `EditLocalProduct` |
| `POST` | `/api/v1/product/local/product/edit_description_prettify` | 微前端,早期 | `SubmitDescPrettification` |
| `POST` | `/api/v1/product/local/product/extra/get` | 微前端 | `GetLocalProductExtra` |
| `GET` | `/api/v1/product/local/product/get` | 客户端,微前端 | `GetLocalProduct` |
| `GET` | `/api/v1/product/local/product/get_1p` | 微前端 | `GetFirstPartyProduct` |
| `POST` | `/api/v1/product/local/product/get_description_prettify` | 微前端 | `GetDescPrettification` |
| `POST` | `/api/v1/product/local/product/multi_confirm` | 微前端,早期 | `MConfirmProducts` |
| `POST` | `/api/v1/product/local/product/package/recommend/update` | 微前端,早期 | `BulkUpdateRecomProductPackage` |
| `POST` | `/api/v1/product/local/product/partial/edit` | 微前端,早期 | `PartialEditLocalProduct` |
| `POST` | `/api/v1/product/local/product/precheck` | 客户端,微前端,早期 | `PreCheckProduct` |
| `POST` | `/api/v1/product/local/product/schema/get` | 微前端,早期 | `GetProductSchema` |
| `GET` | `/api/v1/product/local/product/skus/list` | 微前端 | `ListLocalProductSKUs` |
| `GET` | `/api/v1/product/local/product/subscribe/get` | 微前端 | `GetProductSubscribe` |
| `GET` | `/api/v1/product/local/product/subscribe/save` | 微前端 | `SaveProductSubscribe` |
| `GET` | `/api/v1/product/local/products/list` | 微前端 | `ListLocalProducts` |
| `POST` | `/api/v1/product/local/same_products/list` | 早期 |  |
| `GET` | `/api/v1/product/local/selling_tools` | 早期 |  |
| `?` | `/api/v1/product/local/status/get` | 微前端 | `GetInstantProductStatus` |
| `POST` | `/api/v1/product/local/upload` | 微前端,微前端,早期,早期 | `UploadCreateProduct` |
| `POST` | `/api/v1/product/lock/clearance/set` | 早期 |  |
| `POST` | `/api/v1/product/lock/register_stock_lock` | 微前端,早期 | `RegisterStockLock` |
| `POST` | `/api/v1/product/lock/request_stock_unlock` | 微前端,早期 | `RequestStockUnlock` |
| `POST` | `/api/v1/product/logistics/service/check` | 微前端,微前端,早期,早期 | `CheckLogisticsService` |
| `POST` | `/api/v1/product/msubmit` | 客户端,微前端,早期,早期 | `MPublishProduct` |
| `POST` | `/api/v1/product/multi_region_listing/exchange_rate/get` | 微前端,早期 | `GetExchangeRateList` |
| `POST` | `/api/v1/product/multi_region_listing/rp_manufacturer/list` | 微前端,早期 | `GetRpAndManufacturerList` |
| `POST` | `/api/v1/product/multi_region_listing/rule/get` | 微前端,早期 | `MultiGetRegionRuleInfo` |
| `POST` | `/api/v1/product/multi_region_listing/same_product/get` | 微前端 | `GetGlobalListingSameProduct` |
| `POST` | `/api/v1/product/multi_region_listing/sku/price/stocks/update` | 微前端,早期 | `UpdateRegionSkuPriceStocks` |
| `POST` | `/api/v1/product/multi_region_listing/tax_price_calc` | 微前端,早期 | `MCalPreTaxPrice2SalePrice` |
| `POST` | `/api/v1/product/multi_region_listing/translate` | 微前端,早期 | `MTranslateContent` |
| `GET` | `/api/v1/product/notifications/get` | 微前端 | `GetNotifications` |
| `?` | `/api/v1/product/oc/seller_product_opportunity` | 客户端 |  |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/app_home/lead_top` | 微前端,早期 | `GetAppHomeLeadList` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/app_home/pop/lead_top` | 微前端,早期 | `GetAppHomePOPLeadList` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/auto_submit/set` | 微前端,早期 | `SetAutoSubmit` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/contract/check` | 微前端,早期 | `CheckSignedSPOContract` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/contract/sign` | 微前端,早期 | `SignSPOContract` |
| `GET` | `/api/v1/product/oc/seller_product_opportunity/excel/relate/get` | 微前端,早期 | `GetRelateSPOProductTemplate` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/excel/relate/upload` | 微前端,早期 | `UploadRelateSPOProduct` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/exist/same/product/lead` | 微前端,早期 | `GetExistSameProductLead` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/initial/list` | 微前端,早期 | `ListSPOInitial` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/mark` | 微前端,早期 | `MarkSpo` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/opportunity_type_by_region/get` | 微前端,早期 | `GetShowOpportunityTypeByRegion` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/optimization_items_by_country/list` | 微前端,早期 | `ListOptimizationItemsByCountry` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/optimization_tasks/list` | 微前端 | `ListSPOOptimizationTasks` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/optimization_tasks/update_status` | 微前端,早期 | `UpdateSPOOptimizationTaskStatus` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/pop/filter/get` | 微前端,早期 | `GetPOPSellerShopFilter` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/product/performance/Card` | 微前端,早期 | `GetSocMySubmissionProductPerformanceCard` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/product/performance/list` | 微前端,早期 | `GetSocMySubmissionProductPerformanceList` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/product/stock/get` | 微前端 | `GetProductStock` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/product/stock/update` | 微前端,早期 | `UpdateProductStock` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/reasons/list` | 微前端,早期 | `ListSellerRejectSPOReasons` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/recruit/mark` | 微前端,早期 | `RecruitMark` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/reject` | 微前端,早期 | `SellerRejectSPO` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/relate` | 微前端,早期 | `RelateProductToSPO` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/report/list` | 微前端 | `ListSPOReport` |
| `GET` | `/api/v1/product/oc/seller_product_opportunity/seller/batch_listing/opportunity/count` | 早期 |  |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/batch_listing/task/create` | 早期 |  |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/brand/recommend` | 微前端,早期 | `BrandRecommend` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/eu/config` | 微前端,早期 | `GetEUSellerConfig` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/lead/detail` | 微前端,早期 | `GetLeadDetail` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/lead/list` | 微前端,早期 | `ListLead` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/lead/show_field` | 微前端,早期 | `GetLeadShowField` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/lead/tag/list` | 微前端,早期 | `ListLeadTag` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/leafcate/recommend` | 微前端,早期 | `LeafCateRecommend` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/new_shop_set_up/lead/list` | 微前端,早期 | `ListNewShopSetUpLead` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/pop/config` | 微前端,早期 | `GetPOPSellerConfig` |
| `?` | `/api/v1/product/oc/seller_product_opportunity/seller/product/get` | 微前端 | `GetLiveProductsFromSeller` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/report/summary` | 微前端,早期 | `SellerReportSummary` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/seller/seasonal_festival/tag/list` | 微前端,早期 | `GetSeasonalFestivalTagList` |
| `?` | `/api/v1/product/oc/seller_product_opportunity/sensitive_words/check` | 微前端 | `CheckProductTitleWords` |
| `GET` | `/api/v1/product/oc/seller_product_opportunity/shop_experience_score/get` | 微前端,早期 | `GetShopExperienceScore` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/shop_filter/get` | 微前端,早期 | `GetShopFilter` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/submit/record/list` | 微前端,早期 | `GetSocMySubmissionSubmitRecordList` |
| `?` | `/api/v1/product/oc/seller_product_opportunity/traffic/list` | 微前端 | `ListSPOProductTraffic` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/tts_product/search` | 微前端,早期 | `SearchTtsProducts` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/tts_product/trending/search` | 微前端,早期 | `SearchTrendingTtsProducts` |
| `POST` | `/api/v1/product/oc/seller_product_opportunity/upload_details/get` | 微前端,早期 | `GetSPOUploadDetails` |
| `POST` | `/api/v1/product/optimization/refresh` | 微前端,早期 | `RefreshProductOptimization` |
| `POST` | `/api/v1/product/optimization/report/metrics` | 微前端 | `ReportOptimizationMetrics` |
| `POST` | `/api/v1/product/optimize/appeal` | 早期 |  |
| `POST` | `/api/v1/product/optimize/comp/get_schema` | 微前端 | `GetSchema` |
| `POST` | `/api/v1/product/optimize/data/get` | 微前端,早期 | `GetOptimizationData` |
| `POST` | `/api/v1/product/optimize/generate_suggestion` | 微前端,早期 | `GenerateProductSuggestion` |
| `POST` | `/api/v1/product/optimize/generate_title` | 早期 |  |
| `GET` | `/api/v1/product/optimize/hosting/auth/get` | 早期 |  |
| `POST` | `/api/v1/product/optimize/hosting/auth/update` | 早期 |  |
| `POST` | `/api/v1/product/optimize/hosting/scope/update` | 早期 |  |
| `POST` | `/api/v1/product/optimize/manual_intervention/create` | 早期 |  |
| `POST` | `/api/v1/product/optimize/manual_intervention/detail` | 早期 |  |
| `POST` | `/api/v1/product/optimize/manual_intervention/search` | 早期 |  |
| `POST` | `/api/v1/product/optimize/meta/get` | 微前端,早期 | `GetOptimizationMeta` |
| `PUT` | `/api/v1/product/optimize/multi_edit` | 微前端,早期 | `MEditOptimizedProduct` |
| `POST` | `/api/v1/product/optimize/optimization_performance/charts` | 早期 |  |
| `POST` | `/api/v1/product/optimize/optimization_record/list` | 早期 |  |
| `POST` | `/api/v1/product/optimize/optimization_record/update` | 早期 |  |
| `POST` | `/api/v1/product/optimize/optimization_record/{param}/rollback` | 早期 |  |
| `GET` | `/api/v1/product/optimize/overview/get` | 微前端,早期 | `GetOptimizationOverview` |
| `POST` | `/api/v1/product/optimize/page/get` | 微前端,早期 | `GetToBeOptimizedProductPage` |
| `?` | `/api/v1/product/optimize/product/get` | 微前端 | `GetOptimizationProduct` |
| `?` | `/api/v1/product/optimize/product/multi_get` | 微前端 | `MGetOptimizationProduct` |
| `?` | `/api/v1/product/optimize/products/get` | 微前端 | `GetOptimizationProducts` |
| `GET` | `/api/v1/product/optimize/search_ops/categories` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/optimize_title` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/preview_optimization` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/preview_title` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/submit_optimization` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/video_comments/recommend` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/video_config` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/video_product_relations/query` | 早期 |  |
| `POST` | `/api/v1/product/optimize/search_ops/video_relations/validate` | 早期 |  |
| `POST` | `/api/v1/product/optimize/seller_detail/update` | 微前端,早期 | `UpdateSellerDetail` |
| `POST` | `/api/v1/product/optimize/size_chart/construct` | 微前端,早期 | `GetConstructedSizeChart` |
| `POST` | `/api/v1/product/optimize/size_chart/match` | 微前端,早期 | `CalculateProductSizeChartMatchedResult` |
| `POST` | `/api/v1/product/optimize/size_chart/template_binding_info` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/create` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/detail` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/evaluation/create` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/evaluation/result` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/evaluation/review` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/search` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/status/update` | 早期 |  |
| `POST` | `/api/v1/product/optimize/title_strategy/update` | 早期 |  |
| `POST` | `/api/v1/product/optimize/translate` | 微前端,早期 | `Translate` |
| `POST` | `/api/v1/product/package/recommend` | 微前端,早期 | `RecommendPackage` |
| `POST` | `/api/v1/product/parcel/check` | 微前端,微前端,早期,早期 | `CheckProductParcel` |
| `POST` | `/api/v1/product/pdp_link/get` | 微前端 | `GetPDPH5Link` |
| `POST` | `/api/v1/product/price/app_notify` | 微前端 | `NotifyPriceChangeForApp` |
| `POST` | `/api/v1/product/price/change_price` | 微前端 | `PriceChange` |
| `PUT` | `/api/v1/product/price/diagnosis/list` | 微前端 | `ListPriceDiagnoses` |
| `?` | `/api/v1/product/price/diagnosis/overview/get` | 微前端 | `GetPriceDiagnosisOverView` |
| `POST` | `/api/v1/product/price/get_price_info` | 微前端 | `GetPriceInfo` |
| `PUT` | `/api/v1/product/price/notify` | 微前端 | `NotifyPriceChange` |
| `POST` | `/api/v1/product/price/subsidy_list` | 微前端 | `ListSubsidyOrder` |
| `POST` | `/api/v1/product/price_appeal/create` | 微前端 | `CreatePriceAppeal` |
| `POST` | `/api/v1/product/price_appeal/get_reason` | 微前端 | `ListAvailableAppealReasons` |
| `?` | `/api/v1/product/price_appeals/list` | 微前端 | `ListPriceAppeals` |
| `POST` | `/api/v1/product/product/info/quality/calculate` | 微前端,早期 | `CalculateProductInfoQuality` |
| `GET` | `/api/v1/product/product_creation/preload` | 微前端 | `PreloadProductCreation` |
| `GET` | `/api/v1/product/product_creation/preload_all_categories` | 微前端 | `PreloadAllCategories` |
| `POST` | `/api/v1/product/product_name_rec/list` | 微前端,早期 | `ListRecommendedProductNames` |
| `POST` | `/api/v1/product/product_property_rec/list` | 微前端,早期 | `ListRecommendedProductProperties` |
| `POST` | `/api/v1/product/products/activate` | 微前端,微前端,早期,早期 | `MActivateProducts` |
| `POST` | `/api/v1/product/products/deactivate` | 微前端,微前端,早期,早期 | `MDeactivateProducts` |
| `POST` | `/api/v1/product/products/delete` | 微前端,微前端,早期,早期 | `MDeleteProducts` |
| `POST` | `/api/v1/product/products/recover` | 微前端,微前端,早期,早期 | `MRecoverProducts` |
| `POST` | `/api/v1/product/prohibited/words/check` | 微前端,微前端,早期,早期 | `CheckProhibitedWords` |
| `POST` | `/api/v1/product/promotion/price/get` | 微前端,微前端,早期,早期 | `GetPromotionPrice` |
| `POST` | `/api/v1/product/property/check` | 微前端,早期 | `CheckProductProperty` |
| `POST` | `/api/v1/product/property/migrate` | 微前端,早期 | `MigrateProperty` |
| `POST` | `/api/v1/product/property/normalize_size` | 微前端,早期 | `NormalizeSize` |
| `POST` | `/api/v1/product/publish/diagnosis/item/calculate` | 微前端,早期 | `CalculateProductDiagnosticItemsForPublish` |
| `GET` | `/api/v1/product/quick_listing/search` | 微前端 | `QuickListingSuggestion` |
| `POST` | `/api/v1/product/recommend/item/calculate` | 微前端,早期 | `CalculateProductRecommendedItems` |
| `GET` | `/api/v1/product/regions/mget` | 微前端,早期,早期 | `MGetRegions` |
| `POST` | `/api/v1/product/rp/create_from_seller` | 早期 |  |
| `?` | `/api/v1/product/search/optimized/get` | 微前端 | `GetSearchOptimizationProduct` |
| `POST` | `/api/v1/product/seller/manufacturer/create` | 微前端,早期 | `CreateSellerManufacturer` |
| `POST` | `/api/v1/product/seller/manufacturer/list` | 微前端,早期 | `ListSellerManufacturer` |
| `POST` | `/api/v1/product/seller/update_config` | 早期 |  |
| `POST` | `/api/v1/product/seller_opportunity/collect` | 微前端,早期 | `CollectItem` |
| `POST` | `/api/v1/product/seller_opportunity/niche/get_suggested_word` | 微前端,早期 | `GetSuggestedWord` |
| `POST` | `/api/v1/product/seller_opportunity/niche/list` | 微前端,早期 | `ListNiches` |
| `POST` | `/api/v1/product/seller_opportunity/niche/list_collected` | 微前端,早期 | `ListCollectedNiches` |
| `POST` | `/api/v1/product/seller_opportunity/niche/product/list` | 微前端,早期 | `ListNicheProducts` |
| `POST` | `/api/v1/product/seller_opportunity/niche/product/list_collected` | 微前端,早期 | `ListCollectedNicheProducts` |
| `POST` | `/api/v1/product/shipping/fee/estimate` | 微前端,微前端,早期,早期 | `EstimateShippingFee` |
| `POST` | `/api/v1/product/shipping_template/check` | 微前端,微前端,早期,早期 | `CheckSellerShippingTemplate` |
| `POST` | `/api/v1/product/shipping_template/list` | 微前端,早期 | `GetShippingTemplateList` |
| `POST` | `/api/v1/product/short_info_rec/list` | 早期 |  |
| `POST` | `/api/v1/product/size_chart/batch_save` | 微前端,微前端,早期,早期 | `BatchCreateSizeChart` |
| `POST` | `/api/v1/product/size_chart/config_product` | 微前端,微前端,早期,早期 | `ConfigProductSizeChart` |
| `POST` | `/api/v1/product/size_chart/delete` | 微前端,微前端,早期,早期 | `DeleteSizeChart` |
| `POST` | `/api/v1/product/size_chart/edit` | 微前端,微前端,早期,早期 | `EditSizeChart` |
| `POST` | `/api/v1/product/size_chart/get_bind_info` | 微前端,微前端,早期,早期 | `GetSizeChartBindInfo` |
| `POST` | `/api/v1/product/size_chart/identify` | 微前端,微前端,早期,早期 | `IdentifySizeChart` |
| `POST` | `/api/v1/product/size_chart/list_product_type` | 微前端,微前端,早期,早期 | `ListSizeChartProductType` |
| `POST` | `/api/v1/product/size_chart/save` | 微前端,微前端,早期,早期 | `CreateSizeChart` |
| `POST` | `/api/v1/product/size_chart/search` | 微前端,微前端,早期,早期 | `SearchSizeChart` |
| `POST` | `/api/v1/product/sku/price/cal` | 微前端,微前端,早期,早期 | `CalCrossBoardSKUPrice` |
| `POST` | `/api/v1/product/sku/price/stocks/update` | 微前端,微前端,早期,早期 | `UpdateSKUPriceStocks` |
| `POST` | `/api/v1/product/sku/price/update` | 微前端,微前端,早期,早期 | `UpdateSKUPrice` |
| `POST` | `/api/v1/product/sku/prices/mcal` | 微前端,微前端,早期,早期 | `MCalCrossBoardSKUPrices` |
| `POST` | `/api/v1/product/sku/stocks/decrease` | 微前端,微前端,早期,早期 | `DecreaseSKUStocks` |
| `POST` | `/api/v1/product/sku/stocks/increase` | 微前端,微前端,早期,早期 | `IncreaseSKUStocks` |
| `POST` | `/api/v1/product/smart_publish/image_publish/task/create` | 早期 |  |
| `POST` | `/api/v1/product/spu/match` | 微前端,微前端,早期,早期 | `MatchSpu` |
| `POST` | `/api/v1/product/spu/recommend` | 微前端,早期 | `RecommendSPU` |
| `POST` | `/api/v1/product/spu/search` | 微前端,早期 | `SearchSpuAndCspu` |
| `POST` | `/api/v1/product/spuv2/search` | 早期 |  |
| `POST` | `/api/v1/product/stock/alert/export_reple_file` | 微前端,微前端,早期 | `ExportReplenishmentFile` |
| `POST` | `/api/v1/product/stock/alert/query_export_progress` | 微前端,微前端,早期 | `QueryReplenishFileGenProgress` |
| `POST` | `/api/v1/product/stock/alert/sales/forecast_option/update` | 微前端,微前端,早期 | `UpdateSalesForecastOption` |
| `POST` | `/api/v1/product/stock/alert/set_seller_alert` | 微前端,微前端,早期 | `SetSellerAlertStock` |
| `POST` | `/api/v1/product/stock/alert/set_stock` | 微前端,微前端,早期 | `SetInShopStock` |
| `GET` | `/api/v1/product/stock/banner/check` | 微前端,微前端 | `CheckBanner` |
| `GET` | `/api/v1/product/stock/banner/close` | 微前端,微前端 | `CloseBanner` |
| `POST` | `/api/v1/product/stock/ckp/list` | 早期 |  |
| `POST` | `/api/v1/product/stock/flow/list` | 微前端,微前端,早期 | `ListStockFlow` |
| `POST` | `/api/v1/product/stock/list` | 微前端,微前端,早期 | `ListProductStock` |
| `POST` | `/api/v1/product/stock/negative/check` | 微前端,微前端,早期 | `CheckNegative` |
| `POST` | `/api/v1/product/stock/negative/close` | 微前端,微前端,早期 | `CloseNegative` |
| `POST` | `/api/v1/product/stock/operation/query_task_progress` | 早期 |  |
| `POST` | `/api/v1/product/stock/operation/update` | 早期 |  |
| `POST` | `/api/v1/product/stock/product/list` | 早期 |  |
| `POST` | `/api/v1/product/stock/query/inventory_health` | 微前端,微前端,早期 | `QueryInventoryHealth` |
| `POST` | `/api/v1/product/stock/query/sku` | 微前端,微前端,早期 | `QuerySKUStock` |
| `POST` | `/api/v1/product/stock/query/warehouse/stock_sale_type` | 微前端,微前端,早期 | `QueryWarehouseStockSaleType` |
| `POST` | `/api/v1/product/stock/restock/download_file` | 早期 |  |
| `POST` | `/api/v1/product/stock/restock/query_history` | 早期 |  |
| `POST` | `/api/v1/product/stock/restock/query_task_progress` | 早期 |  |
| `POST` | `/api/v1/product/stock/restock/upload_file` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/delete` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/detail/list` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/list` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/product/list` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/query_task_progress` | 早期 |  |
| `POST` | `/api/v1/product/stock/restriction/update` | 早期 |  |
| `POST` | `/api/v1/product/stock/sku/count/list` | 微前端,微前端,早期 | `CountSKUType` |
| `POST` | `/api/v1/product/stock/sku/list` | 微前端,微前端,早期 | `ListSKU` |
| `POST` | `/api/v1/product/stock/sku/order/list` | 微前端,微前端,早期 | `ListSKUOrder` |
| `POST` | `/api/v1/product/stock/status_count/list` | 微前端,微前端,早期 | `CountProductStockStatus` |
| `POST` | `/api/v1/product/stock/unlink` | 早期 |  |
| `POST` | `/api/v1/product/stock/warehouse/deactivatable/check` | 微前端,微前端,早期 | `CheckWarehouseDeactivatable` |
| `GET` | `/api/v1/product/tab/count/get` | 微前端,早期,早期 | `GetProductTabCount` |
| `?` | `/api/v1/product/web/categories/search` | 微前端 | `SearchWebCategories` |
| `GET` | `/api/v1/product/web/local/products/list` | 客户端,客户端,微前端 | `ListWebLocalProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/order/product/manage` | 微前端 | `ManageSalesSubOrderProducts` |
| `?` | `/api/v1/sea_product/growth/ab/version/set` | 微前端 | `SetAbTestVersion` |
| `?` | `/api/v1/sea_product/growth/announcement/get` | 微前端 | `GetAnnouncementData` |
| `?` | `/api/v1/sea_product/growth/batch/recommendation/tasks` | 微前端 | `GetBatchRecommendationTasks` |
| `?` | `/api/v1/sea_product/growth/business/log/set` | 微前端 | `SetBusinessLog` |
| `?` | `/api/v1/sea_product/growth/early_bird/rel_product/get` | 微前端 | `GetSellerEarlyBirdRelProduct` |
| `?` | `/api/v1/sea_product/growth/home_page/sdk/product/get` | 微前端 | `GetHomePageSDKProduct` |
| `POST` | `/api/v1/sea_product/growth/latest_date` | 微前端 | `GetLatestDate` |
| `POST` | `/api/v1/sea_product/growth/product_data_drawer` | 微前端 | `GetProductDataDrawer` |
| `POST` | `/api/v1/sea_product/growth/product_list` | 微前端 | `GetProductListData` |
| `POST` | `/api/v1/sea_product/growth/sales_inheritance/authorize/set` | 微前端 | `SetSellerSalesInheritanceAuthorize` |
| `POST` | `/api/v1/sea_product/growth/sales_inheritance/show/get` | 微前端 | `GetSellerSalesInheritanceShow` |
| `POST` | `/api/v1/sea_product/growth/seller/overview` | 微前端 | `GetSellerOverviewData` |
| `POST` | `/api/v1/sea_product/growth/set_task_complete` | 微前端 | `SetTaskComplete` |
| `POST` | `/api/v1/sea_product/growth/shop_data_drawer` | 微前端 | `GetShopDataDrawer` |
| `?` | `/api/v1/sea_product/growth/smart/custody/ad_isv_oauth2` | 微前端 | `CustodyAdIsvOAuth2` |
| `?` | `/api/v1/sea_product/growth/smart/custody/ad_isv_oauth2_shop` | 微前端 | `CustodyAdIsvOAuth2Shop` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/authorize` | 微前端 | `SmartGrowthCustodyAuthorize` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/candidate/product/performance` | 微前端 | `GetCandidateProductPerformance` |
| `?` | `/api/v1/sea_product/growth/smart/custody/eligible/product/list` | 微前端 | `GetSmartGrowthEligibleProductList` |
| `?` | `/api/v1/sea_product/growth/smart/custody/overview` | 微前端 | `GetSmartGrowthCustodyOverview` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/product/suspend` | 微前端 | `SuspendSmartGrowthProduct` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/program/ai_video` | 微前端 | `GetSmartGrowthCustodyAiVideo` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/program/ai_video/delete` | 微前端 | `DeleteAiVideo` |
| `?` | `/api/v1/sea_product/growth/smart/custody/program/ai_video/delete_reason/list` | 微前端 | `DeleteAiVideoReasonList` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/program/ai_video/read` | 微前端 | `ReadAiVideo` |
| `POST` | `/api/v1/sea_product/growth/smart/custody/program/create` | 微前端 | `CreateSmartGrowthCustodyProgram` |
| `?` | `/api/v1/sea_product/growth/smart/custody/program/detail` | 微前端 | `SmartGrowthCustodyProgramDetail` |
| `?` | `/api/v1/sea_product/growth/smart/custody/program/list` | 微前端 | `SmartGrowthCustodyProgramList` |
| `?` | `/api/v1/sea_product/growth/smart/custody/program/performance` | 微前端 | `SmartGrowthCustodyProgramPerformance` |
| `?` | `/api/v1/sea_product/growth/smart/custody/program/suspend` | 微前端 | `SuspendSmartGrowthProgram` |
| `?` | `/api/v1/sea_product/growth/smart/custody/promotion/program` | 微前端 | `GetSmartGrowthProgramIdByPromotion` |
| `?` | `/api/v1/sea_product/growth/smart/custody/shop_bind_info` | 微前端 | `CustodyGetShopBindInfo` |
| `?` | `/api/v1/sea_product/growth/smart_shop/custody/home_widget` | 微前端 | `GetShopSmartGrowthHomeWidget` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/product_search` | 微前端 | `SearchShopSmartGrowthProduct` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program/list_sku` | 微前端 | `GetShopSmartGrowthSkuByProducts` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program/predict_sales` | 微前端 | `PredictShopSmartGrowthSales` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program/stats` | 微前端 | `GetShopSmartGrowthProgramStats` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program/upsert` | 微前端 | `UpsertShopSmartGrowthProgram` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program_candidate` | 微前端 | `GetShopSmartGrowthProgram` |
| `POST` | `/api/v1/sea_product/growth/smart_shop/custody/program_strategy/get` | 微前端 | `GetShopSmartGrowthProgramStrategy` |
| `?` | `/api/v1/sea_product/growth/smart_shop/custody/reject_reason` | 微前端 | `GetStrategyRejectReason` |
| `POST` | `/api/v1/sea_product/growth/update_task_status` | 微前端 | `UpdateTaskStatus` |
| `?` | `/api/v2/product/oc/seller_product_opportunity/submit/record/list` | 客户端 |  |
| `POST` | `/instant/api/v1/product/local/product/create` | 早期,早期 |  |

## 订单 / 售后（169）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/insights/seller/shop/logistics/product/order/list` | 微前端,微前端,微前端 | `GetSellerShopLogisticsProductOrderListQuery` |
| `POST` | `/api/v1/insights/seller/shop/logistics/product/order/list/export` | 微前端,微前端,微前端 | `GetSellerShopLogisticsProductOrderListExportQuery` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/order/budget/change` | 微前端 | `ChangeSalesSubOrderBudget` |
| `?` | `/api/v1/promotion/campaign/seller/sales_subscription/order/budget/get` | 微前端 | `GetSalesSubOrderBudget` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/order/budget_record/get` | 微前端 | `GetSalesSubOrderBudgetRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/order/create` | 微前端 | `CreateSalesSubOrder` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/order/list` | 微前端 | `ListSalesSubOrderLines` |
| `?` | `/api/v1/promotion/campaign/seller/sales_subscription/order/operation_record/list` | 微前端 | `ListSalesSubOrderOperationRecords` |
| `GET` | `/api/v1/reverse/NFe/get` | 微前端 | `GetReverseOrderNFe` |
| `POST` | `/api/v1/reverse/NFe/operate` | 微前端 | `OperateReverseOrderNFe` |
| `GET` | `/api/v1/reverse/aftersales_dashboard` | 微前端 | `GetAftersalesDashboard` |
| `POST` | `/api/v1/reverse/appeal/add_evidence` | 微前端 | `AddAppealEvidence` |
| `POST` | `/api/v1/reverse/appeal/apply` | 微前端 | `ApplyAppeal` |
| `POST` | `/api/v1/reverse/appeal/get_details` | 微前端 | `GetAppealDetail` |
| `POST` | `/api/v1/reverse/appeal/preview` | 微前端 | `GetAppealPreview` |
| `POST` | `/api/v1/reverse/arbitration/add_evidence` | 微前端 | `AddArbitrationEvidence` |
| `POST` | `/api/v1/reverse/arbitration/get` | 微前端 | `GetArbitrationDetail` |
| `POST` | `/api/v1/reverse/automatic_strategy/create` | 微前端 | `CreateAutomaticStrategy` |
| `POST` | `/api/v1/reverse/automatic_strategy/list` | 微前端 | `ListSellerAutomaticStrategy` |
| `POST` | `/api/v1/reverse/automatic_strategy/update` | 微前端 | `UpdateAutomaticStrategy` |
| `GET` | `/api/v1/reverse/automatic_strategy_template/get` | 微前端 | `GetAutomaticStrategyTemplate` |
| `POST` | `/api/v1/reverse/banner/list` | 微前端 | `ListPlatformRules` |
| `GET` | `/api/v1/reverse/banner/platform_managed_review_banner` | 微前端 | `GetPlatformManagedReviewBanner` |
| `POST` | `/api/v1/reverse/banner/update` | 微前端 | `UpdatePlatformRule` |
| `POST` | `/api/v1/reverse/compensation/get` | 微前端 | `GetCompensationDetail` |
| `POST` | `/api/v1/reverse/component/actions/list` | 微前端 | `ListAvailableActions` |
| `POST` | `/api/v1/reverse/component/orders/get` | 微前端 | `GetReverseCard` |
| `POST` | `/api/v1/reverse/component/orders/list` | 微前端 | `ListReverseCards` |
| `POST` | `/api/v1/reverse/component/preview/orders/get` | 微前端 | `GetReverseCardForPreview` |
| `POST` | `/api/v1/reverse/component/preview/orders/list` | 微前端 | `ListReverseCardsForPreview` |
| `POST` | `/api/v1/reverse/dashboard/get` | 微前端 | `GetUrgentDashboard` |
| `POST` | `/api/v1/reverse/download_file` | 微前端 | `DownloadFile` |
| `POST` | `/api/v1/reverse/dtc/final_sale/add` | 微前端 | `AddReverseDTCFinalSale` |
| `POST` | `/api/v1/reverse/dtc/final_sale/delete` | 微前端 | `DeleteReverseDTCFinalSale` |
| `POST` | `/api/v1/reverse/dtc/final_sale/products_list` | 微前端 | `GetReverseDTCFinalSaleProducts` |
| `POST` | `/api/v1/reverse/get_available_after_sale_period_options` | 微前端 | `GetAvailableAfterSalePeriodOptions` |
| `POST` | `/api/v1/reverse/get_cancellation_window_setting` | 微前端 | `GetCancellationWindowSetting` |
| `POST` | `/api/v1/reverse/get_request_cancel_window_setting` | 微前端 | `GetRequestCancelWindowSetting` |
| `GET` | `/api/v1/reverse/get_return_metrics_info` | 微前端 | `GetReturnMetricsInfo` |
| `GET` | `/api/v1/reverse/get_top_return_by_product_id` | 微前端 | `GetTopReturnByProductId` |
| `GET` | `/api/v1/reverse/get_top_return_by_reason` | 微前端 | `GetTopReturnByReason` |
| `POST` | `/api/v1/reverse/gray_info` | 微前端 | `GetGrayInfo` |
| `POST` | `/api/v1/reverse/how_to_fulfill` | 微前端 | `GetHowToFulfillDoc` |
| `GET` | `/api/v1/reverse/list_return_reason` | 微前端 | `ListReturnReason` |
| `POST` | `/api/v1/reverse/orders/actions/add_tracking_number` | 微前端 | `ActionAddTrackingNumber` |
| `POST` | `/api/v1/reverse/orders/actions/appeal/cancel` | 微前端 | `SellerCancelApplyAppeal` |
| `POST` | `/api/v1/reverse/orders/actions/appeal/create` | 微前端 | `SellerApplyAppeal` |
| `GET` | `/api/v1/reverse/orders/actions/appeal/get` | 微前端 | `ActionCheckAppealRecords` |
| `POST` | `/api/v1/reverse/orders/actions/check_return_logistics` | 微前端 | `ActionCheckReturnLogistics` |
| `POST` | `/api/v1/reverse/orders/actions/check_return_records` | 微前端 | `ActionCheckReturnRecords` |
| `POST` | `/api/v1/reverse/orders/actions/delay_receiving` | 微前端 | `ActionDelayReceiving` |
| `POST` | `/api/v1/reverse/orders/actions/direct_refund` | 微前端 | `ActionDirectRefund` |
| `POST` | `/api/v1/reverse/orders/actions/edit_tracking_number` | 微前端 | `ActionEditTrackingNumber` |
| `POST` | `/api/v1/reverse/orders/actions/m_cancel_order` | 微前端 | `ActionMCancelOrder` |
| `POST` | `/api/v1/reverse/orders/actions/negotiate_edit` | 微前端 | `ActionNegotiateEdit` |
| `POST` | `/api/v1/reverse/orders/actions/partial_refund` | 微前端 | `ActionPartialRefund` |
| `GET` | `/api/v1/reverse/orders/actions/quality_check_info` | 微前端 | `GetReverseFulfillmentByROrderId` |
| `POST` | `/api/v1/reverse/orders/actions/return_apply_accept` | 微前端 | `ActionReturnApplyAccept` |
| `POST` | `/api/v1/reverse/orders/actions/return_apply_reject` | 微前端 | `ActionReturnApplyReject` |
| `POST` | `/api/v1/reverse/orders/actions/return_parcel_accept` | 微前端 | `ActionReturnParcelAccept` |
| `POST` | `/api/v1/reverse/orders/actions/return_parcel_reject` | 微前端 | `ActionReturnParcelReject` |
| `POST` | `/api/v1/reverse/orders/actions/start_reverse` | 微前端 | `ActionStartReverse` |
| `POST` | `/api/v1/reverse/orders/cancel_reasons/get` | 微前端 | `GetReverseCancelReasons` |
| `POST` | `/api/v1/reverse/orders/check_action_executable` | 微前端 | `CheckActionExecutable` |
| `POST` | `/api/v1/reverse/orders/check_limit` | 微前端 | `CheckReverseLimit` |
| `POST` | `/api/v1/reverse/orders/download_file` | 微前端 | `DownloadReverseMainOrder` |
| `POST` | `/api/v1/reverse/orders/export` | 微前端 | `ExportReverseMainOrders` |
| `GET` | `/api/v1/reverse/orders/get` | 微前端 | `GetSellerReverseMainOrderDetail` |
| `POST` | `/api/v1/reverse/orders/get_can_reverse_details` | 微前端 | `GetCanReverseDetails` |
| `POST` | `/api/v1/reverse/orders/get_export_history` | 微前端 | `GetExportHistory` |
| `POST` | `/api/v1/reverse/orders/get_next_reverse_order` | 微前端 | `GetSellerNextReverseMainOrder` |
| `POST` | `/api/v1/reverse/orders/issue_refund_preview` | 微前端 | `GetIssueRefundPreview` |
| `POST` | `/api/v1/reverse/orders/list` | 微前端 | `ListSellerReverseMainOrders` |
| `POST` | `/api/v1/reverse/orders/list_logistics_service` | 微前端 | `ListLogisticsService` |
| `POST` | `/api/v1/reverse/orders/list_seller_announcement` | 微前端 | `ListSellerAppAnnouncements` |
| `POST` | `/api/v1/reverse/orders/order_lines/list` | 微前端 | `ListSellerReverseOrderLines` |
| `POST` | `/api/v1/reverse/orders/partial_refund_preview` | 微前端 | `GetPartialRefundPreview` |
| `POST` | `/api/v1/reverse/orders/reverse_amount` | 微前端 | `CalReverseAmount` |
| `POST` | `/api/v1/reverse/orders/reverse_preview` | 微前端 | `GetReversePreview` |
| `POST` | `/api/v1/reverse/orders/reverse_reasons/get` | 微前端 | `GetReverseReasons` |
| `POST` | `/api/v1/reverse/orders/tag` | 微前端 | `SetReverseOrderTag` |
| `POST` | `/api/v1/reverse/platform_audit/add_evidence` | 微前端 | `AddPlatformAuditEvidence` |
| `POST` | `/api/v1/reverse/platform_audit/get` | 微前端 | `GetPlatformAuditDetail` |
| `POST` | `/api/v1/reverse/preview/accept_reverse` | 微前端 | `GetAcceptReversePreview` |
| `POST` | `/api/v1/reverse/preview/add_tracking_number` | 微前端 | `GetAddTrackingNumberPreview` |
| `POST` | `/api/v1/reverse/preview/cancel_order` | 微前端 | `GetCancelOrderPreview` |
| `POST` | `/api/v1/reverse/preview/customize_policy` | 微前端 | `GetCustomizePolicyPreview` |
| `POST` | `/api/v1/reverse/preview/direct_refund` | 微前端 | `GetDirectRefundPreview` |
| `POST` | `/api/v1/reverse/preview/reject_reverse` | 微前端 | `GetRejectReversePreview` |
| `POST` | `/api/v1/reverse/preview/replacement_setting` | 微前端 | `GetReplacementSettingPreview` |
| `POST` | `/api/v1/reverse/search_fuzzy` | 微前端 | `SearchFuzzyInfo` |
| `POST` | `/api/v1/reverse/search_layout` | 微前端 | `GetSearchLayout` |
| `POST` | `/api/v1/reverse/seller_function/update` | 微前端 | `UpdateSellerFunctionConfig` |
| `POST` | `/api/v1/reverse/seller_rule/list` | 微前端 | `ListSellerSettingRule` |
| `POST` | `/api/v1/reverse/update_cancellation_window_setting` | 微前端 | `UpdateCancellationWindowSetting` |
| `POST` | `/api/v1/reverse/update_request_cancel_window_setting` | 微前端 | `UpdateRequestCancelWindowSetting` |
| `POST` | `/api/v1/seller/onboard/order/get` | 微前端,财务bundle | `GetOnboardOrder` |
| `GET` | `/api/v1/seller/order/conf/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSellerOrderListConf` |
| `POST` | `/api/v1/shop_im/shop/order/check_support_direct_lsp` | 财务bundle | `CheckSupportDirectLSP` |
| `POST` | `/api/v1/shop_im/shop/order/get_buyer_order_outer_url` | 微前端,财务bundle | `GetBuyerOrderOuterURL` |
| `?` | `/api/v1/shop_im/shop/order/get_simple_info` | 微前端,财务bundle | `GetSimpleOrderInfo` |
| `?` | `/api/v1/shop_im/shop/order/mget_contact_buyer_link` | 微前端,财务bundle | `MGetContactBuyerLinkByOrder` |
| `POST` | `/widget/api/v1/reverse/appeal/add_evidence` | 微前端 | `AddAppealEvidenceForWidget` |
| `POST` | `/widget/api/v1/reverse/appeal/apply` | 微前端 | `ApplyAppealForWidget` |
| `POST` | `/widget/api/v1/reverse/appeal/get_details` | 微前端 | `GetAppealDetailForWidget` |
| `POST` | `/widget/api/v1/reverse/appeal/preview` | 微前端 | `GetAppealPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/arbitration/add_evidence` | 微前端 | `AddArbitrationEvidenceForWidget` |
| `POST` | `/widget/api/v1/reverse/arbitration/get` | 微前端 | `GetArbitrationDetailForWidget` |
| `POST` | `/widget/api/v1/reverse/automatic_strategy/create` | 微前端 | `CreateAutomaticStrategyForWidget` |
| `POST` | `/widget/api/v1/reverse/automatic_strategy/list` | 微前端 | `ListSellerAutomaticStrategyForWidget` |
| `POST` | `/widget/api/v1/reverse/automatic_strategy/update` | 微前端 | `UpdateAutomaticStrategyForWidget` |
| `GET` | `/widget/api/v1/reverse/automatic_strategy_template/get` | 微前端 | `GetAutomaticStrategyTemplateForWidget` |
| `POST` | `/widget/api/v1/reverse/banner/list` | 微前端 | `ListPlatformRulesForWidget` |
| `POST` | `/widget/api/v1/reverse/banner/update` | 微前端 | `UpdatePlatformRuleForWidget` |
| `POST` | `/widget/api/v1/reverse/compensation/get` | 微前端 | `GetCompensationDetailForWidget` |
| `POST` | `/widget/api/v1/reverse/dashboard/get` | 微前端 | `GetUrgentDashboardForWidget` |
| `POST` | `/widget/api/v1/reverse/download_file` | 微前端 | `DownloadFileForWidget` |
| `POST` | `/widget/api/v1/reverse/get_cancellation_window_setting` | 微前端 | `GetCancellationWindowSettingForWidget` |
| `POST` | `/widget/api/v1/reverse/gray_info` | 微前端 | `GetGrayInfoForWidget` |
| `POST` | `/widget/api/v1/reverse/how_to_fulfill` | 微前端 | `GetHowToFulfillDocForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/add_tracking_number` | 微前端 | `ActionAddTrackingNumberForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/appeal/cancel` | 微前端 | `SellerCancelApplyAppealForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/appeal/create` | 微前端 | `SellerApplyAppealForWidget` |
| `GET` | `/widget/api/v1/reverse/orders/actions/appeal/get` | 微前端 | `ActionCheckAppealRecordsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/check_return_logistics` | 微前端 | `ActionCheckReturnLogisticsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/check_return_records` | 微前端 | `ActionCheckReturnRecordsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/delay_receiving` | 微前端 | `ActionDelayReceivingForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/direct_refund` | 微前端 | `ActionDirectRefundForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/edit_tracking_number` | 微前端 | `ActionEditTrackingNumberForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/m_cancel_order` | 微前端 | `ActionMCancelOrderForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/partial_refund` | 微前端 | `ActionPartialRefundForWidget` |
| `GET` | `/widget/api/v1/reverse/orders/actions/quality_check_info` | 微前端 | `GetReverseFulfillmentByROrderIdForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/return_apply_accept` | 微前端 | `ActionReturnApplyAcceptForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/return_apply_reject` | 微前端 | `ActionReturnApplyRejectForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/return_parcel_accept` | 微前端 | `ActionReturnParcelAcceptForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/return_parcel_reject` | 微前端 | `ActionReturnParcelRejectForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/actions/start_reverse` | 微前端 | `ActionStartReverseForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/cancel_reasons/get` | 微前端 | `GetReverseCancelReasonsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/check_action_executable` | 微前端 | `CheckActionExecutableForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/check_limit` | 微前端 | `CheckReverseLimitForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/download_file` | 微前端 | `DownloadReverseMainOrderForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/export` | 微前端 | `ExportReverseMainOrdersForWidget` |
| `GET` | `/widget/api/v1/reverse/orders/get` | 微前端 | `GetSellerReverseMainOrderDetailForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/get_can_reverse_details` | 微前端 | `GetCanReverseDetailsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/get_export_history` | 微前端 | `GetExportHistoryForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/get_next_reverse_order` | 微前端 | `GetSellerNextReverseMainOrderForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/issue_refund_preview` | 微前端 | `GetIssueRefundPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/list` | 微前端 | `ListSellerReverseMainOrdersForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/list_logistics_service` | 微前端 | `ListLogisticsServiceForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/list_seller_announcement` | 微前端 | `ListSellerAppAnnouncementsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/order_lines/list` | 微前端 | `ListSellerReverseOrderLinesForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/partial_refund_preview` | 微前端 | `GetPartialRefundPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/reverse_amount` | 微前端 | `CalReverseAmountForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/reverse_preview` | 微前端 | `GetReversePreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/reverse_reasons/get` | 微前端 | `GetReverseReasonsForWidget` |
| `POST` | `/widget/api/v1/reverse/orders/tag` | 微前端 | `SetReverseOrderTagForWidget` |
| `POST` | `/widget/api/v1/reverse/platform_audit/add_evidence` | 微前端 | `AddPlatformAuditEvidenceForWidget` |
| `POST` | `/widget/api/v1/reverse/platform_audit/get` | 微前端 | `GetPlatformAuditDetailForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/accept_reverse` | 微前端 | `GetAcceptReversePreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/add_tracking_number` | 微前端 | `GetAddTrackingNumberPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/cancel_order` | 微前端 | `GetCancelOrderPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/customize_policy` | 微前端 | `GetCustomizePolicyPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/direct_refund` | 微前端 | `GetDirectRefundPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/reject_reverse` | 微前端 | `GetRejectReversePreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/preview/replacement_setting` | 微前端 | `GetReplacementSettingPreviewForWidget` |
| `POST` | `/widget/api/v1/reverse/search_fuzzy` | 微前端 | `SearchFuzzyInfoForWidget` |
| `POST` | `/widget/api/v1/reverse/search_layout` | 微前端 | `GetSearchLayoutForWidget` |
| `POST` | `/widget/api/v1/reverse/seller_function/update` | 微前端 | `UpdateSellerFunctionConfigForWidget` |
| `POST` | `/widget/api/v1/reverse/update_cancellation_window_setting` | 微前端 | `UpdateCancellationWindowSettingForWidget` |

## 营销 / 促销（408）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/insights/seller/shop/campaign/annual/stats` | 微前端,微前端,微前端 | `GetSellerShopAnnualCampaignStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/banner/display` | 微前端,微前端 | `GetSellerShopCampaignBannerDisplayQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/bcp/core/stats` | 微前端,微前端,微前端 | `GetSellerShopCampaignBCPCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/bcp/status` | 微前端,微前端,微前端 | `GetSellerShopCampaignBCPEnrollmentStatus` |
| `POST` | `/api/v1/insights/seller/shop/campaign/info` | 微前端,微前端,微前端 | `GetSellerShopCampaignInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/list` | 微前端,微前端,微前端 | `GetSellerShopCampaignListQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/list/export` | 微前端,微前端,微前端 | `GetSellerShopCampaignListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/offline/product/list` | 微前端,微前端,微前端 | `GetSellerShopCampaignOfflineProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/realtime/product/list` | 微前端,微前端,微前端 | `GetSellerShopCampaignRealtimeProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/realtime/stats` | 微前端,微前端,微前端 | `GetSellerShopCampaignRealtimeStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/report/stats` | 微前端,微前端,微前端 | `GetSellerShopCampaignReportStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/target` | 微前端,微前端,微前端 | `SetSellerShopCampaignTargetQuery` |
| `POST` | `/api/v1/insights/seller/shop/campaign/trend/stats` | 微前端,微前端,微前端 | `GetSellerShopCampaignTrendStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/marketing/campaign/list` | 微前端,微前端,微前端 | `GetSellerShopOverviewMarketingCampaignListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/marketing/promotion/list` | 微前端,微前端,微前端 | `GetSellerShopOverviewMarketingPromotionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/today/campaign/info` | 微前端,微前端,微前端 | `ShopOverviewPerformanceTodayCampaignInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/creator/performance/list` | 微前端,微前端 | `GetSellerShopPromotionCreatorPerformanceListQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/creator/performance/list/export` | 微前端,微前端 | `ShopPromotionCreatorPerformanceListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/detail/stats` | 微前端,微前端,微前端 | `GetSellerShopPromotionDetailStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/info` | 微前端,微前端,微前端 | `GetSellerShopPromotionInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/list` | 微前端,微前端,微前端 | `GetSellerShopPromotionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/list/export` | 微前端,微前端,微前端 | `GetSellerShopPromotionListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/period/stats` | 微前端,微前端 | `GetSellerShopPromotionPeriodStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/product/list` | 微前端,微前端 | `GetSellerShopPromotionProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/product/list/export` | 微前端,微前端 | `GetSellerShopPromotionProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/promotion/stats` | 微前端,微前端,微前端 | `GetSellerShopPromotionStatsQuery` |
| `POST` | `/api/v1/promotion/add_on/config` | 微前端,早期 | `AddOnPromotionConfig` |
| `POST` | `/api/v1/promotion/agent/mget_promotion_card` | 微前端,早期 | `MGetAgentPromotionCard` |
| `POST` | `/api/v1/promotion/agent/replace_recommended_tool_config` | 微前端,早期 | `ReplaceRecommendedPromotionToolConfig` |
| `POST` | `/api/v1/promotion/allocation/create` | 微前端,微前端,微前端,早期 | `CreateAllocation` |
| `POST` | `/api/v1/promotion/allocation/delete` | 微前端,微前端,微前端,早期 | `DeleteAllocation` |
| `POST` | `/api/v1/promotion/allocation/list` | 微前端,微前端,微前端,早期 | `ListAllocations` |
| `POST` | `/api/v1/promotion/allocation/prizes/get` | 微前端,微前端,微前端,早期 | `GetAllocationPrizes` |
| `POST` | `/api/v1/promotion/allocation/prizes/update` | 微前端,微前端,微前端,早期 | `UpdateAllocationPrizes` |
| `POST` | `/api/v1/promotion/app/buy_more_save_more/create` | 微前端,微前端,微前端,早期 | `CreateBuyMoreSaveMoreFromApp` |
| `?` | `/api/v1/promotion/app/buy_more_save_more/get` | 微前端,微前端 | `GetBuyMoreSaveMoreFromApp` |
| `POST` | `/api/v1/promotion/app/buy_more_save_more/list` | 微前端,微前端 | `ListBuyMoreSaveMoreFromApp` |
| `POST` | `/api/v1/promotion/app/buy_more_save_more/update` | 微前端,微前端,微前端,早期 | `UpdateBuyMoreSaveMoreFromApp` |
| `POST` | `/api/v1/promotion/app/config` | 微前端,微前端,微前端 | `GetSellerAppPromotionConfig` |
| `?` | `/api/v1/promotion/app/config/get` | 微前端,微前端 | `GetSellerBackendConfigFromApp` |
| `POST` | `/api/v1/promotion/app/flash_sale/create` | 微前端,微前端,微前端,早期 | `CreateFlashSaleFromApp` |
| `?` | `/api/v1/promotion/app/flash_sale/get` | 微前端,微前端 | `GetFlashSaleFromApp` |
| `POST` | `/api/v1/promotion/app/flash_sale/list` | 微前端,微前端 | `ListFlashSaleFromApp` |
| `POST` | `/api/v1/promotion/app/home_page_info` | 微前端,微前端,微前端,早期 | `GetSellerPromotionHomePageInfo` |
| `POST` | `/api/v1/promotion/app/list_products` | 微前端,微前端,微前端 | `ListProductsInPromotionFromApp` |
| `POST` | `/api/v1/promotion/app/mget_item_data` | 微前端,微前端,微前端,早期 | `MGetAppItemData` |
| `POST` | `/api/v1/promotion/app/price_details/get` | 微前端,微前端,微前端,早期 | `MGetAPPPriceDetail` |
| `POST` | `/api/v1/promotion/app/product_discount/create` | 微前端,微前端,微前端,早期 | `CreateProductDiscount` |
| `?` | `/api/v1/promotion/app/product_discount/get` | 微前端,微前端 | `GetProductDiscount` |
| `?` | `/api/v1/promotion/app/product_discount/list` | 微前端,微前端 | `ListProductDiscount` |
| `POST` | `/api/v1/promotion/app/recommended_promotion_tool/list` | 微前端,微前端,微前端,早期 | `ListRecommendedToolForApp` |
| `POST` | `/api/v1/promotion/app/search_products` | 微前端,微前端,微前端,早期 | `SearchProductsFromApp` |
| `POST` | `/api/v1/promotion/app/seller_allow_list/get` | 微前端,微前端 | `GetSellerInAllowListFromApp` |
| `POST` | `/api/v1/promotion/app/voucher/create` | 微前端,微前端,微前端,早期 | `CreateVoucherFromApp` |
| `POST` | `/api/v1/promotion/app/voucher/destroy` | 微前端,微前端,微前端,早期 | `DestroyVoucherFromApp` |
| `POST` | `/api/v1/promotion/app/voucher/get` | 微前端,微前端 | `GetVoucherFromApp` |
| `POST` | `/api/v1/promotion/app/voucher/list` | 微前端,微前端 | `ListVoucherFromApp` |
| `POST` | `/api/v1/promotion/app/voucher/list_products` | 微前端,微前端 | `ListProductsInVoucherFromApp` |
| `POST` | `/api/v1/promotion/attention_needed/dismiss` | 微前端,早期 | `DismissAttentionNeeded` |
| `POST` | `/api/v1/promotion/batch_upload/products/get_template_excel` | 微前端,微前端 | `GetTemplateExcelDownloadUrl` |
| `POST` | `/api/v1/promotion/batch_upload/products/upload` | 微前端,微前端,微前端,早期 | `UploadAndParseExcel` |
| `POST` | `/api/v1/promotion/bundle_deal/create` | 微前端,微前端,微前端,早期 | `CreateBundleDeal` |
| `?` | `/api/v1/promotion/bundle_deal/get` | 微前端,微前端 | `GetBundleDeal` |
| `POST` | `/api/v1/promotion/bundle_deal/list` | 微前端,微前端 | `ListBundleDeal` |
| `POST` | `/api/v1/promotion/bundle_deal/update` | 微前端,微前端,微前端,早期 | `UpdateBundleDeal` |
| `POST` | `/api/v1/promotion/buy_more_save_more/create` | 微前端,微前端,微前端,早期 | `CreateBuyMoreSaveMore` |
| `?` | `/api/v1/promotion/buy_more_save_more/get` | 微前端,微前端 | `GetBuyMoreSaveMore` |
| `?` | `/api/v1/promotion/buy_more_save_more/list` | 微前端,微前端 | `ListBuyMoreSaveMore` |
| `POST` | `/api/v1/promotion/buy_more_save_more/update` | 微前端,微前端,微前端,早期 | `UpdateBuyMoreSaveMore` |
| `POST` | `/api/v1/promotion/calc_future_seller_promotion_price` | 微前端,早期 | `CalcFutureSellerPromotionPrice` |
| `?` | `/api/v1/promotion/campaign/seller/action_record/list` | 微前端 | `ListCampaignApprovalActionRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/agreement/detail` | 微前端 | `GetAgreement` |
| `POST` | `/api/v1/promotion/campaign/seller/agreement/sign` | 微前端 | `SignAgreement` |
| `POST` | `/api/v1/promotion/campaign/seller/app_parents_campaigns/list` | 微前端 | `ListAppParentCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/download` | 微前端 | `DownloadAutoEnrollData` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/get` | 微前端 | `GetAutoEnrollInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/product/delete` | 微前端 | `DeleteAutoEnrollProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/product/list` | 微前端 | `ListAutoEnrollProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/result_popup/close` | 微前端 | `GetAutoEnrollResultPopUpClose` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/result_popup/get` | 微前端 | `GetAutoEnrollResultPopUpInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/submit` | 微前端 | `SubmitAutoEnroll` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/submit_product` | 微前端 | `SubmitAutoEnrollProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/submit_product_cache` | 微前端 | `SubmitAutoEnrollProductCache` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll/switch` | 微前端 | `AutoEnrollSwitch` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_enroll_register/product/list` | 微前端 | `ListAutoEnrollRegisterProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/auto_register_agreement` | 微前端 | `UpdateAutoRegisterAgreement` |
| `POST` | `/api/v1/promotion/campaign/seller/backend_categories/list` | 微前端 | `ListBackendCategories` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_async_opt_products` | 微前端 | `BatchAsyncOperateProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_async_opt_products_close` | 微前端 | `BatchAsyncOperateProductsClose` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_async_set_commission_rate_and_free_sample` | 微前端 | `BatchAsyncSetCommissionRateAndFreeSample` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_progress` | 微前端 | `GetBatchProgress` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_progress_close` | 微前端 | `BatchProgressClose` |
| `POST` | `/api/v1/promotion/campaign/seller/batch_withdraw` | 微前端 | `BatchWithdrawCampaignProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/brand/material_product/list` | 微前端 | `ListSellerMaterialProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/brands/list` | 微前端 | `ListBrands` |
| `POST` | `/api/v1/promotion/campaign/seller/bundle/get` | 微前端 | `BundleDetail` |
| `?` | `/api/v1/promotion/campaign/seller/bundle/list` | 微前端 | `ListBundle` |
| `POST` | `/api/v1/promotion/campaign/seller/bundle/registration_list` | 微前端 | `ListBundleRegisterRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/bundle/submit_registration` | 微前端 | `BundleSubmitRegistrationInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/bundle_ads/ops_registration/list` | 微前端 | `ListOpsRegisterBundleAdsRecord` |
| `?` | `/api/v1/promotion/campaign/seller/bundle_group/detail` | 微前端 | `GetBundleGroupDetail` |
| `?` | `/api/v1/promotion/campaign/seller/bundle_group/list` | 微前端 | `ListBundleGroup` |
| `?` | `/api/v1/promotion/campaign/seller/campaign/get` | 微前端 | `GetCampaignInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/campaign/summary_info` | 微前端 | `GetSummaryInfoByScene` |
| `POST` | `/api/v1/promotion/campaign/seller/campaign_eligibility/verify` | 微前端 | `VerifyCampaignEligibility` |
| `POST` | `/api/v1/promotion/campaign/seller/campaign_mission_challenge_info/list` | 微前端 | `GetCampaignMissionChallengeCard` |
| `POST` | `/api/v1/promotion/campaign/seller/change_approval` | 微前端 | `ChangeApproval` |
| `?` | `/api/v1/promotion/campaign/seller/check/cookies` | 微前端 | `CheckCookies` |
| `POST` | `/api/v1/promotion/campaign/seller/check_and_fulfill_product` | 微前端 | `ProductRegistrationCheckAndFulfill` |
| `POST` | `/api/v1/promotion/campaign/seller/check_register_condition` | 微前端 | `CheckRegisterCondition` |
| `POST` | `/api/v1/promotion/campaign/seller/child_categories/list` | 微前端 | `ListChildCategories` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_parent_campaigns/list` | 微前端 | `ListCofundParentCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/associate_sub_campaigns/list` | 微前端 | `ListCofundAssociateSubCampaigns` |
| `?` | `/api/v1/promotion/campaign/seller/cofund_program/get` | 微前端 | `GetCofundProgram` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/list` | 微前端 | `ListCofundPrograms` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/list_v2` | 微前端 | `ListCofundProgramsV2` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/seller_budget/history_records` | 微前端 | `ListCofundProgramBudgetRecords` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/seller_budget/set` | 微前端 | `SetCofundProgramBudget` |
| `POST` | `/api/v1/promotion/campaign/seller/cofund_program/seller_budget_plan/set` | 微前端 | `SetCofundProgramBudgetPlan` |
| `?` | `/api/v1/promotion/campaign/seller/com_campaign/new_list` | 微前端 | `ListNewComCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/com_campaigns/list` | 微前端 | `ListComCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/com_campaigns_joined/list` | 微前端 | `ListJoinedComCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/common_info/update` | 微前端 | `UpdateCampaignCommonInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/config/banner` | 微前端 | `GetSellerCampaignBannerConfig` |
| `POST` | `/api/v1/promotion/campaign/seller/count` | 微前端 | `CountCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/count_products` | 微前端 | `CountCampaignProducts` |
| `?` | `/api/v1/promotion/campaign/seller/creator/get` | 微前端 | `GetCreatorInfo` |
| `?` | `/api/v1/promotion/campaign/seller/creator/list` | 微前端 | `GetShopCreator` |
| `POST` | `/api/v1/promotion/campaign/seller/data/metrics_card/get` | 微前端 | `GetMetricsCardData` |
| `POST` | `/api/v1/promotion/campaign/seller/data/metrics_daily/get` | 微前端 | `GetMetricsDailyData` |
| `POST` | `/api/v1/promotion/campaign/seller/data/metrics_table/list` | 微前端 | `ListMetricsTableData` |
| `POST` | `/api/v1/promotion/campaign/seller/data/promotion_calendar/get` | 微前端 | `GetPromotionCalendar` |
| `POST` | `/api/v1/promotion/campaign/seller/enrollment/action_record_list` | 微前端 | `ListEnrollmentActionRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/enrollment/change_approval` | 微前端 | `EnrollmentChangeApproval` |
| `POST` | `/api/v1/promotion/campaign/seller/feedback` | 微前端 | `CampaignFeedback` |
| `POST` | `/api/v1/promotion/campaign/seller/file/upload` | 微前端 | `UploadFile` |
| `POST` | `/api/v1/promotion/campaign/seller/get` | 微前端 | `GetSubCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/get_payment_bill` | 微前端 | `GetPaymentBill` |
| `POST` | `/api/v1/promotion/campaign/seller/get_register_regions` | 微前端 | `ListSellerRegisterRegions` |
| `POST` | `/api/v1/promotion/campaign/seller/get_semi_managed_performance` | 微前端 | `GetSemiManagedPerformance` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/campaign_info` | 微前端 | `GetCampaignSellerGMVMaxInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/list_approval` | 微前端 | `ListGMVMaxApprovalProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/list_product` | 微前端 | `ListGMVMaxProductsBySeller` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/mget_product` | 微前端 | `MGetGMVMaxProductsInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/permission` | 微前端 | `CheckGMVMaxPermission` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/retry` | 微前端 | `RetryGMVMaxBySeller` |
| `POST` | `/api/v1/promotion/campaign/seller/gmv_max/sign_for_Creation` | 微前端 | `SignForCreation` |
| `?` | `/api/v1/promotion/campaign/seller/investment_hub/guidance` | 微前端 | `GetStrategyGuidance` |
| `?` | `/api/v1/promotion/campaign/seller/investment_hub/interpretation` | 微前端 | `GetInvestmentInterpretation` |
| `POST` | `/api/v1/promotion/campaign/seller/investment_hub/metric/get` | 微前端 | `GetInvestmentMetric` |
| `?` | `/api/v1/promotion/campaign/seller/investment_hub/tags/get` | 微前端 | `GetInvestmentSellerTags` |
| `?` | `/api/v1/promotion/campaign/seller/investment_hub/time_config/get` | 微前端 | `GetInvestmentHubTimeConfig` |
| `POST` | `/api/v1/promotion/campaign/seller/job/download/v` | 微前端 | `DownloadJobFile` |
| `POST` | `/api/v1/promotion/campaign/seller/job/get_template` | 微前端 | `GetJobTemplate` |
| `POST` | `/api/v1/promotion/campaign/seller/job/list` | 微前端 | `ListJob` |
| `POST` | `/api/v1/promotion/campaign/seller/job/mget` | 微前端 | `MGetJob` |
| `POST` | `/api/v1/promotion/campaign/seller/job/submit` | 微前端 | `SubmitJob` |
| `?` | `/api/v1/promotion/campaign/seller/list` | 微前端 | `ListSubCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/list_next_recommend_sub_campaigns` | 微前端 | `ListNextRecommendSubCampaigns` |
| `?` | `/api/v1/promotion/campaign/seller/list_products` | 微前端 | `ListCampaignProducts` |
| `?` | `/api/v1/promotion/campaign/seller/list_registered_campaigns` | 微前端 | `ListRegisteredCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/list_registered_products` | 微前端 | `ListRegisteredProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/add` | 微前端 | `AddLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/batch_add` | 微前端 | `BatchAddLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/batch_update_event` | 微前端 | `BatchUpdateLiveEvent` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/cancel` | 微前端 | `CancelLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/change_approval` | 微前端 | `ChangeLiveSessionApproval` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/detail` | 微前端 | `GetLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/gmv_max/retry` | 微前端 | `RetryLivestreamGMVMax` |
| `?` | `/api/v1/promotion/campaign/seller/live_session/list` | 微前端 | `ListLiveSession` |
| `?` | `/api/v1/promotion/campaign/seller/live_session/overlap_list` | 微前端 | `ListOverlapLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_session/update` | 微前端 | `UpdateLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/live_stream/detail` | 微前端 | `GetLiveStream` |
| `POST` | `/api/v1/promotion/campaign/seller/live_stream/gmv_max/qualification` | 微前端 | `CheckLivestreamGMVMaxQualification` |
| `?` | `/api/v1/promotion/campaign/seller/live_stream/list` | 微前端 | `ListLiveStream` |
| `?` | `/api/v1/promotion/campaign/seller/live_stream/progress` | 微前端 | `GetCampaignGmvTarget` |
| `POST` | `/api/v1/promotion/campaign/seller/livestream_group/list_sessions` | 微前端 | `ListLivestreamGroupSessions` |
| `POST` | `/api/v1/promotion/campaign/seller/marketing/cards/get` | 微前端 | `GetSellerMarketingCards` |
| `POST` | `/api/v1/promotion/campaign/seller/material/get` | 微前端 | `GetSellerMaterial` |
| `POST` | `/api/v1/promotion/campaign/seller/material/list` | 微前端 | `ListSellerMaterials` |
| `POST` | `/api/v1/promotion/campaign/seller/material/modify` | 微前端 | `ModifySellerMaterial` |
| `POST` | `/api/v1/promotion/campaign/seller/material/submit` | 微前端 | `SubmitMaterialEnrollment` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/cofund_programs` | 微前端 | `ListRegisteredPrograms` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/list_live_session` | 微前端 | `ListRegisteredLiveSession` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/parent_campaigns` | 微前端 | `ListRegisteredParentCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/product_campaign_dimension` | 微前端 | `ListRegisteredProductCampaignDimension` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/product_dimension` | 微前端 | `ListRegisteredProductDimension` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/list_registered/type_campaigns` | 微前端 | `ListRegisteredComCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/mgt/registered_stat` | 微前端 | `RegisteredStat` |
| `POST` | `/api/v1/promotion/campaign/seller/one_link_register/list_campaigns` | 微前端 | `ListOneLinkComCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/one_link_register/submit_product` | 微前端 | `SubmitOneLinkBatchRegisterProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/out_reach/callback` | 微前端 | `OutreachCallBack` |
| `?` | `/api/v1/promotion/campaign/seller/parent_campaign/detail` | 微前端 | `GetParentCampaignDetails` |
| `POST` | `/api/v1/promotion/campaign/seller/parent_campaigns_recommend/list` | 微前端 | `ListRecommendParentCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/parents_campaigns/list` | 微前端 | `ListParentCampaigns` |
| `POST` | `/api/v1/promotion/campaign/seller/popup/action` | 微前端 | `OperatePopupAction` |
| `POST` | `/api/v1/promotion/campaign/seller/popup/query` | 微前端 | `QueryPopupDisplayInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/access` | 微前端 | `GetSellerPriceExemptionAccess` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/application/create` | 微前端 | `CreateSellerPriceExemptionApplication` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/application/detail/list` | 微前端 | `ListSellerPriceExemptionApplicationDetails` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/application/list` | 微前端 | `ListSellerPriceExemptionApplications` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/application/recall` | 微前端 | `RecallSellerPriceExemptionApplication` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/file/upload` | 微前端 | `UploadSellerPriceExemptionFile` |
| `POST` | `/api/v1/promotion/campaign/seller/price_exemption/product/check` | 微前端 | `CheckSellerPriceExemptionProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/product/change_approval` | 微前端 | `ChangeProductApproval` |
| `?` | `/api/v1/promotion/campaign/seller/product_grouping/list` | 微前端 | `ListLivestreamProductGroup` |
| `POST` | `/api/v1/promotion/campaign/seller/product_grouping/list_product` | 微前端 | `ListLivestreamSessionProduct` |
| `?` | `/api/v1/promotion/campaign/seller/product_schedule/list` | 微前端 | `ListCampaignProductSchedule` |
| `POST` | `/api/v1/promotion/campaign/seller/product_set/operation_records/list` | 微前端 | `ListProductSetProductOperationRecords` |
| `POST` | `/api/v1/promotion/campaign/seller/product_set/products/list` | 微前端 | `ListProductSetProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/product_set/products/search` | 微前端 | `SearchProductSetProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/product_strategy/get` | 微前端 | `GetProductStrategyBanner` |
| `?` | `/api/v1/promotion/campaign/seller/program/payment/list` | 微前端 | `ListPaymentRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/program/payment/submit` | 微前端 | `SubmitPayment` |
| `POST` | `/api/v1/promotion/campaign/seller/program/register_record_list` | 微前端 | `ListProgramRegisterRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/recommend/list_product` | 微前端 | `ListRecommendProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/recommend_campaign/list` | 微前端 | `ListRecSubCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/register_remind` | 微前端 | `RegisterRemind` |
| `POST` | `/api/v1/promotion/campaign/seller/register_remind_close` | 微前端 | `RegisterRemindClose` |
| `POST` | `/api/v1/promotion/campaign/seller/register_task/campaign/list` | 微前端 | `ListRegisterTaskCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/register_task/event/feedback` | 微前端 | `RegisterTaskFeedbackEvent` |
| `POST` | `/api/v1/promotion/campaign/seller/register_task/statistic/get` | 微前端 | `MGetRegisterTaskStatisticInfo` |
| `?` | `/api/v1/promotion/campaign/seller/registered_program/detail` | 微前端 | `GetRegisteredProgramDetail` |
| `POST` | `/api/v1/promotion/campaign/seller/registration_info/list` | 微前端 | `ListRegistrationInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/reminds/change` | 微前端 | `ChangeCampaignReminds` |
| `POST` | `/api/v1/promotion/campaign/seller/reminds/list` | 微前端 | `ListCampaignReminds` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/list` | 微前端 | `ListResourcePkg` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/material/delete` | 微前端 | `SellerDeleteMaterials` |
| `?` | `/api/v1/promotion/campaign/seller/resource_pkg/material/list` | 微前端 | `ListResourcePkgMaterial` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/material/submit` | 微前端 | `SubmitMaterial` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/material_register_record/list` | 微前端 | `ListResourcePkgMaterialRegisterRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/register` | 微前端 | `RegisterResourcePkg` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/register_record/get` | 微前端 | `GetResourcePkgRegisterDetail` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/register_record/list` | 微前端 | `ListResourcePkgRegisterRecord` |
| `POST` | `/api/v1/promotion/campaign/seller/resource_pkg/suggestion/list` | 微前端 | `ListResourcePkgSuggestion` |
| `?` | `/api/v1/promotion/campaign/seller/resource_pkg_associated_campaign/list` | 微前端 | `ListResourcePkgAssociatedCampaign` |
| `?` | `/api/v1/promotion/campaign/seller/resource_pkg_group/get` | 微前端 | `GetResourcePkgGroupDetail` |
| `?` | `/api/v1/promotion/campaign/seller/resource_pkg_group/list` | 微前端 | `ListResourcePkgGroup` |
| `POST` | `/api/v1/promotion/campaign/seller/retention_target_shop/check` | 微前端 | `CheckRetentionTargetShop` |
| `POST` | `/api/v1/promotion/campaign/seller/retention_target_shop/discount_pool/add` | 微前端 | `AddShopToRetentionDiscountPool` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_offering/get` | 微前端 | `GetSalesOfferings` |
| `?` | `/api/v1/promotion/campaign/seller/sales_offering/list` | 微前端 | `ListSalesOfferings` |
| `POST` | `/api/v1/promotion/campaign/seller/sales_subscription/reverse_order/create` | 微前端 | `CreateSalesSubReverseOrder` |
| `POST` | `/api/v1/promotion/campaign/seller/search_products` | 微前端 | `SearchCampaignProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/seller_calendar/get` | 微前端 | `GetSellerCalendar` |
| `POST` | `/api/v1/promotion/campaign/seller/seller_region_creator/info` | 微前端 | `GetSellerRegionCreatorInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/seller_tasks/list` | 微前端 | `ListCampaignSellerTasks` |
| `?` | `/api/v1/promotion/campaign/seller/semi_managed/managed_info` | 微前端 | `GetSemiManagedManagedInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/sku_in_product/get` | 微前端 | `GetSKUInProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/sku_tier_prices/mget` | 微前端 | `MGetCampaignSkuTierPrices` |
| `POST` | `/api/v1/promotion/campaign/seller/skus_in_products/mget` | 微前端 | `MGetSKUsInProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/smp/get_sc_popup` | 微前端 | `GetSMPPromotionSCHomepagePopup` |
| `POST` | `/api/v1/promotion/campaign/seller/starling_keys/convert` | 微前端 | `ConvertStarlingKeys` |
| `POST` | `/api/v1/promotion/campaign/seller/submit` | 微前端 | `SubmitProduct` |
| `POST` | `/api/v1/promotion/campaign/seller/submit_campaign` | 微前端 | `SubmitCampaign` |
| `POST` | `/api/v1/promotion/campaign/seller/submit_registration_info` | 微前端 | `SubmitRegistrationInfo` |
| `POST` | `/api/v1/promotion/campaign/seller/suggest_registered_products` | 微前端 | `SuggestRegisteredProducts` |
| `POST` | `/api/v1/promotion/campaign/seller/verify` | 微前端 | `SellerVerify` |
| `POST` | `/api/v1/promotion/campaign/seller/video/get` | 微前端 | `GetVideoInfo` |
| `?` | `/api/v1/promotion/campaign/seller/wait_handle_product/get` | 微前端 | `GetWaitHandleProductList` |
| `GET` | `/api/v1/promotion/common_info/get` | 微前端,微前端,早期 | `GetCommonInfo` |
| `?` | `/api/v1/promotion/config` | 客户端,客户端,微前端,微前端 | `GetSellerPromotionConfig` |
| `?` | `/api/v1/promotion/config/get` | 微前端,微前端 | `GetSellerBackendConfig` |
| `POST` | `/api/v1/promotion/creator_exclusive_price/create` | 微前端,微前端,微前端,早期 | `CreateCreatorExclusivePricePromotion` |
| `POST` | `/api/v1/promotion/creator_exclusive_price/update` | 微前端,微前端,微前端,早期 | `UpdateCreatorExclusivePricePromotion` |
| `POST` | `/api/v1/promotion/data_report` | 微前端,微前端,早期 | `DataReport` |
| `POST` | `/api/v1/promotion/destroy` | 微前端,微前端,早期 | `DestroyPromotion` |
| `POST` | `/api/v1/promotion/diagnosis_recommend_strategy/list` | 微前端,微前端,微前端,早期 | `ListDiagnosisAndRecommendStrategy` |
| `POST` | `/api/v1/promotion/discount/create` | 客户端,客户端,微前端,微前端,微前端,早期 | `CreateDiscount` |
| `POST` | `/api/v1/promotion/discount/get` | 客户端,微前端,微前端 | `GetSellerDiscount` |
| `POST` | `/api/v1/promotion/discount/list` | 客户端,客户端,微前端,微前端,微前端,早期 | `ListSellerDiscounts` |
| `POST` | `/api/v1/promotion/discount/update` | 客户端,微前端,微前端,微前端,早期 | `UpdateDiscountPromotion` |
| `POST` | `/api/v1/promotion/fixed_price/create` | 客户端,微前端,微前端,微前端,早期 | `CreateFixedPrice` |
| `POST` | `/api/v1/promotion/fixed_price/get` | 微前端,微前端 | `GetFixedPrice` |
| `POST` | `/api/v1/promotion/fixed_price/list` | 微前端,微前端,微前端,早期 | `ListFixedPrice` |
| `POST` | `/api/v1/promotion/fixed_price/update` | 客户端,微前端,微前端,微前端,早期 | `UpdateFixedPrice` |
| `POST` | `/api/v1/promotion/flash_sale/batch_update` | 微前端,微前端,微前端,早期 | `BatchUpdateFlashSale` |
| `POST` | `/api/v1/promotion/flash_sale/create` | 微前端,微前端,微前端,早期 | `CreateFlashSale` |
| `POST` | `/api/v1/promotion/flash_sale/get` | 微前端,微前端 | `GetFlashSale` |
| `?` | `/api/v1/promotion/flash_sale/list` | 微前端,微前端 | `ListFlashSale` |
| `POST` | `/api/v1/promotion/flash_sale/update` | 微前端,微前端,微前端,早期 | `UpdateFlashSale` |
| `POST` | `/api/v1/promotion/free_shipping/create` | 微前端,微前端,微前端,早期 | `CreateFreeShipping` |
| `POST` | `/api/v1/promotion/free_shipping/get` | 微前端,微前端 | `GetFreeShipping` |
| `POST` | `/api/v1/promotion/free_shipping/list` | 微前端,微前端,微前端,早期 | `ListFreeShippings` |
| `POST` | `/api/v1/promotion/free_shipping/risk` | 微前端,微前端,早期 | `RiskFreeShipping` |
| `POST` | `/api/v1/promotion/free_shipping/update` | 微前端,微前端,微前端,早期 | `UpdateFreeShipping` |
| `POST` | `/api/v1/promotion/free_shipping/update_default` | 微前端,早期 | `UpdateDefaultFreeShipping` |
| `POST` | `/api/v1/promotion/get_latest_promotions_by_pid` | 微前端,微前端,早期 | `MGetLatestPromotionsByProductIDs` |
| `GET` | `/api/v1/promotion/get_main_page` | 微前端,微前端,早期 | `GetMainPage` |
| `POST` | `/api/v1/promotion/get_promotions_by_product_id` | 微前端,微前端 | `GetPromotionsByProductID` |
| `POST` | `/api/v1/promotion/get_seller_feature` | 微前端,微前端,早期 | `GetSellerFeature` |
| `GET` | `/api/v1/promotion/get_seller_status` | 微前端,微前端,早期 | `GetSellerStatus` |
| `POST` | `/api/v1/promotion/get_summary` | 客户端,客户端,微前端,微前端 | `GetSummary` |
| `POST` | `/api/v1/promotion/gift_with_purchase/create` | 微前端,微前端,微前端,早期 | `CreateGiftWithPurchase` |
| `?` | `/api/v1/promotion/gift_with_purchase/get` | 微前端,微前端 | `GetGiftWithPurchase` |
| `?` | `/api/v1/promotion/gift_with_purchase/list` | 微前端,微前端 | `ListGiftWithPurchase` |
| `POST` | `/api/v1/promotion/gift_with_purchase/update` | 微前端,微前端,微前端,早期 | `UpdateGiftWithPurchase` |
| `POST` | `/api/v1/promotion/list` | 微前端,微前端,早期 | `ListPromotion` |
| `POST` | `/api/v1/promotion/list_products` | 客户端,微前端,微前端,早期 | `ListProductsInPromotion` |
| `POST` | `/api/v1/promotion/list_products_by_cursor` | 客户端,微前端,微前端,早期 | `ListProductsInPromotionByCursor` |
| `POST` | `/api/v1/promotion/list_seller_gray_config` | 客户端,客户端,微前端,微前端,早期 | `ListSellerGrayConfig` |
| `POST` | `/api/v1/promotion/list_skus` | 微前端,微前端,早期 | `ListAvailableSkusByProduct` |
| `POST` | `/api/v1/promotion/list_strikethrough_price` | 微前端,微前端,早期 | `ListStrikethroughPrice` |
| `POST` | `/api/v1/promotion/live_app/create` | 微前端,微前端,微前端,早期 | `CreateVoucherForLive` |
| `POST` | `/api/v1/promotion/live_app/get` | 微前端,微前端,微前端,早期 | `GetVoucherForLive` |
| `POST` | `/api/v1/promotion/live_app/get_basic_config` | 微前端,微前端,早期 | `GetBasicConfigForLive` |
| `GET` | `/api/v1/promotion/live_app/get_common_info` | 微前端,微前端,早期 | `GetCommonInfoForLive` |
| `POST` | `/api/v1/promotion/live_app/get_shop_risk_info` | 微前端,微前端,微前端,早期 | `GetShopRiskInfoForLive` |
| `POST` | `/api/v1/promotion/live_app/search_products` | 微前端,微前端,微前端,早期 | `SearchProductsForLive` |
| `POST` | `/api/v1/promotion/live_app/update` | 微前端,微前端,微前端,早期 | `UpdateVoucherForLive` |
| `POST` | `/api/v1/promotion/live_manager/config` | 微前端 | `GetSellerPromotionConfigForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/list_seller_gray_config` | 微前端,早期 | `ListSellerGrayConfigForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/mget_item_data` | 微前端,微前端,早期 | `MGetItemDataForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/recommended_promotion_tool/list` | 微前端,微前端,早期 | `ListRecommendedPromotionForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/seller_experiment_info/get` | 微前端,微前端,早期 | `GetSellerExperimentInfoForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/shop_risk_info/get` | 微前端 | `GetShopRiskInfoForLiveManager` |
| `POST` | `/api/v1/promotion/live_manager/voucher/create` | 微前端,微前端,早期 | `CreateVoucherForLiveManager` |
| `POST` | `/api/v1/promotion/mget_item_data` | 客户端,微前端,微前端,早期 | `MGetItemData` |
| `POST` | `/api/v1/promotion/mget_skpp_promotions_by_pid` | 微前端,早期 | `MGetSKPPPromotionsByProductID` |
| `POST` | `/api/v1/promotion/plan/add_one_fee_recommend_product` | 微前端,早期 | `AddOneFeeRecommendProduct` |
| `POST` | `/api/v1/promotion/plan/create` | 微前端,微前端,微前端,早期 | `CreatePromotionPlan` |
| `POST` | `/api/v1/promotion/plan/data_overview` | 微前端,微前端,微前端,早期 | `GetPromotionPlanDataOverview` |
| `POST` | `/api/v1/promotion/plan/deactivate` | 微前端,微前端,微前端,早期 | `DeactivatePromotionPlan` |
| `POST` | `/api/v1/promotion/plan/get` | 微前端,微前端,微前端,早期 | `GetPromotionPlan` |
| `POST` | `/api/v1/promotion/plan/list` | 微前端,微前端,微前端,早期 | `ListPromotionPlan` |
| `POST` | `/api/v1/promotion/plan/list_one_fee_recommend_product` | 微前端,早期 | `ListOneFeeRecommendProduct` |
| `POST` | `/api/v1/promotion/plan/list_product` | 微前端,微前端,微前端,早期 | `ListPromotionPlanProduct` |
| `POST` | `/api/v1/promotion/plan/product_label` | 微前端,微前端,微前端,早期 | `GetPromotionPlanProductLabel` |
| `POST` | `/api/v1/promotion/plan/update` | 微前端,微前端,微前端,早期 | `UpdatePromotionPlan` |
| `POST` | `/api/v1/promotion/plan/update_product` | 微前端,微前端,微前端,早期 | `UpdatePromotionPlanProduct` |
| `POST` | `/api/v1/promotion/price/calc_estimate_promotion_price` | 微前端,微前端,微前端,早期 | `CalcEstimatePromotionPrice` |
| `POST` | `/api/v1/promotion/price/calc_future_promotion_price` | 微前端,微前端,微前端,早期 | `CalcFuturePromotionPrice` |
| `POST` | `/api/v1/promotion/price/calc_promotion_stacking_info` | 微前端,微前端,微前端,早期 | `CalcPromotionStackingInfo` |
| `POST` | `/api/v1/promotion/price/get_promotion_stacking_info` | 微前端,微前端,微前端,早期 | `GetPromotionStackingInfo` |
| `POST` | `/api/v1/promotion/price_details/get` | 微前端,微前端,微前端,早期 | `MGetPriceDetail` |
| `POST` | `/api/v1/promotion/price_guardrail/batch_set` | 微前端,早期 | `BatchSetPriceGuardrailSafetyPrice` |
| `POST` | `/api/v1/promotion/price_guardrail/detail` | 微前端,早期 | `GetPriceGuardrailDetail` |
| `POST` | `/api/v1/promotion/price_guardrail/download/template` | 微前端 | `DownloadPriceGuardrailTemplate` |
| `POST` | `/api/v1/promotion/price_guardrail/list` | 微前端,早期 | `ListPriceGuardrailOverview` |
| `POST` | `/api/v1/promotion/price_guardrail/progress_bar` | 微前端,早期 | `GetPriceGuardrailProgressBar` |
| `POST` | `/api/v1/promotion/price_stacking_detail/get` | 微前端,早期 | `GetSkuPriceStackingDetail` |
| `POST` | `/api/v1/promotion/prize/create` | 微前端,微前端,微前端,早期 | `CreatePrizes` |
| `POST` | `/api/v1/promotion/prize/delete` | 微前端,微前端,微前端,早期 | `DeletePrize` |
| `POST` | `/api/v1/promotion/prize/get` | 微前端,微前端,微前端,早期 | `GetPrizes` |
| `POST` | `/api/v1/promotion/prize/list` | 微前端,微前端,微前端,早期 | `ListPrizes` |
| `POST` | `/api/v1/promotion/prize/update_quantity` | 微前端,微前端,微前端,早期 | `UpdatePrizeQuantity` |
| `POST` | `/api/v1/promotion/promo_code/create` | 微前端,微前端,微前端,早期 | `CreateSellerPromoCode` |
| `POST` | `/api/v1/promotion/promo_code/delete` | 微前端,微前端,微前端,早期 | `DeleteSellerPromoCode` |
| `POST` | `/api/v1/promotion/promo_code/generate` | 微前端,微前端,微前端,早期 | `GenerateSellerPromoCode` |
| `POST` | `/api/v1/promotion/promo_code/get` | 微前端,微前端,微前端,早期 | `GetSellerPromoCode` |
| `POST` | `/api/v1/promotion/promo_code/update` | 微前端,微前端,微前端,早期 | `UpdateSellerPromoCode` |
| `POST` | `/api/v1/promotion/promo_code/validate` | 微前端,微前端,微前端,早期 | `ValidateSellerPromoCode` |
| `POST` | `/api/v1/promotion/recommended_creators/get` | 微前端 | `GetRecommendedCreators` |
| `POST` | `/api/v1/promotion/recommended_promotion_tool/list` | 微前端,微前端,微前端,早期 | `ListRecommendedPromotionTool` |
| `POST` | `/api/v1/promotion/recommended_promotion_tools/label_list` | 微前端,微前端,微前端,早期 | `ListSellerRecommendedLabel` |
| `POST` | `/api/v1/promotion/recommended_promotion_tools/list` | 微前端,微前端 | `ListRecommendedPromotionTools` |
| `POST` | `/api/v1/promotion/recommended_promotion_tools/live_overview` | 微前端,微前端,早期 | `ListSellerRecommendedLiveOverview` |
| `POST` | `/api/v1/promotion/restrict_categories/list` | 微前端,微前端 | `ListRestrictCategories` |
| `POST` | `/api/v1/promotion/risk_price_product/get` | 微前端,早期 | `GetRiskPriceProducts` |
| `POST` | `/api/v1/promotion/search_bundles` | 微前端,微前端,早期 | `SearchBundles` |
| `POST` | `/api/v1/promotion/search_creator` | 微前端,微前端,早期 | `SearchCreatorByNameOrID` |
| `POST` | `/api/v1/promotion/search_products` | 微前端,微前端,早期 | `SearchProducts` |
| `?` | `/api/v1/promotion/seller_allow_list/get` | 微前端,微前端 | `GetSellerInAllowList` |
| `POST` | `/api/v1/promotion/seller_audit_log/query` | 微前端,微前端,早期 | `QueryAuditLog` |
| `POST` | `/api/v1/promotion/seller_experiment_info/get` | 微前端,微前端,微前端,早期 | `GetSellerExperimentInfo` |
| `POST` | `/api/v1/promotion/seller_platform/list` | 微前端,微前端,微前端,早期 | `ListSellerPlatformPromotions` |
| `POST` | `/api/v1/promotion/seller_platform/update` | 微前端,微前端,微前端,早期 | `UpdateSellerPlatformPromotions` |
| `POST` | `/api/v1/promotion/seller_points/create` | 微前端,早期 | `CreateSellerPoints` |
| `POST` | `/api/v1/promotion/seller_points/deactivate` | 微前端,早期 | `DeactivateSellerPoints` |
| `POST` | `/api/v1/promotion/seller_points/get` | 微前端,早期 | `GetSellerPoints` |
| `POST` | `/api/v1/promotion/seller_points/list_products` | 微前端,早期 | `ListSellerPointsProducts` |
| `POST` | `/api/v1/promotion/seller_points/update` | 微前端,早期 | `UpdateSellerPoints` |
| `POST` | `/api/v1/promotion/seller_recently_used_tools/list` | 微前端,微前端,微前端,早期 | `ListSellerRecentlyUsedTools` |
| `POST` | `/api/v1/promotion/shop_metrics/overview/get` | 微前端,微前端,微前端,早期 | `GetPromotionShopMetricsOverview` |
| `POST` | `/api/v1/promotion/shop_risk_info/get` | 客户端,客户端,微前端,微前端,微前端 | `GetShopRiskInfo` |
| `POST` | `/api/v1/promotion/single_discount/get` | 微前端,微前端 | `GetSingleDiscount` |
| `POST` | `/api/v1/promotion/single_discount/list` | 微前端,微前端,微前端,早期 | `ListSingleDiscounts` |
| `POST` | `/api/v1/promotion/smart_plan/list_recommended_tools` | 微前端,早期 | `ListSmartPlanRecommendedTools` |
| `POST` | `/api/v1/promotion/sns_product_discount/check_deactivate` | 微前端,微前端,微前端,早期 | `CheckSNSPromoDeactivate` |
| `POST` | `/api/v1/promotion/sns_product_discount/create` | 微前端,微前端,微前端,早期 | `CreateSNSProductDiscount` |
| `POST` | `/api/v1/promotion/sns_product_discount/get` | 微前端,微前端 | `GetSNSProductDiscount` |
| `POST` | `/api/v1/promotion/sns_product_discount/products/batch_operate` | 微前端,早期 | `BatchOperateSNSProducts` |
| `POST` | `/api/v1/promotion/sns_product_discount/products/check_deactivate` | 微前端,早期 | `CheckSNSProductsDeactivate` |
| `POST` | `/api/v1/promotion/sns_product_discount/products/get_operation_context` | 微前端,早期 | `GetSNSProductOperationContext` |
| `POST` | `/api/v1/promotion/sns_product_discount/products/list` | 微前端,早期 | `ListSNSProducts` |
| `POST` | `/api/v1/promotion/sns_product_discount/update` | 微前端,微前端,微前端,早期 | `UpdateSNSPromotion` |
| `POST` | `/api/v1/promotion/tool_info/list` | 微前端,微前端,微前端,早期 | `ListPromotionToolInfo` |
| `POST` | `/api/v1/promotion/toolbox/seller_audit_log/query` | 微前端 |  |
| `POST` | `/api/v1/promotion/tools_metrics/overview/get` | 微前端,微前端,微前端,早期 | `GetPromotionToolsMetricsOverview` |
| `POST` | `/api/v1/promotion/update_products` | 微前端,微前端,早期 | `UpdateProductsInPromotion` |
| `POST` | `/api/v1/promotion/update_skus` | 微前端,微前端,早期 | `UpdateSkusInPromotion` |
| `POST` | `/api/v1/promotion/voucher/check_conflict` | 微前端,微前端,微前端,早期 | `CheckConflictVoucher` |
| `POST` | `/api/v1/promotion/voucher/check_voucher_overlap` | 微前端,微前端,微前端,早期 | `CheckSellerVoucherOverlap` |
| `POST` | `/api/v1/promotion/voucher/create` | 微前端,微前端,微前端,早期 | `CreateVoucher` |
| `POST` | `/api/v1/promotion/voucher/destroy` | 微前端,微前端,微前端,早期 | `DestroyVoucher` |
| `POST` | `/api/v1/promotion/voucher/get` | 微前端,微前端,微前端,早期 | `GetVoucher` |
| `POST` | `/api/v1/promotion/voucher/list` | 客户端,微前端,微前端,微前端,早期 | `ListVoucher` |
| `POST` | `/api/v1/promotion/voucher/list_products` | 微前端,微前端,微前端,早期 | `ListProductsInVoucherByCursor` |
| `POST` | `/api/v1/promotion/voucher/update` | 微前端,微前端,微前端,早期 | `UpdateVoucher` |
| `POST` | `/api/v2/promotion/app/voucher/create` | 微前端,微前端,微前端,早期 | `CreateVoucherFromAppV2` |
| `POST` | `/api/v2/promotion/app/voucher/get` | 微前端,微前端,微前端 | `GetVoucherFromAppV2` |
| `?` | `/api/v2/promotion/app/voucher/list` | 微前端,微前端,微前端 | `ListVoucherFromAppV2` |
| `POST` | `/api/v2/promotion/voucher/create` | 微前端,微前端,微前端,早期 | `CreateVoucherV2` |
| `POST` | `/api/v2/promotion/voucher/get` | 微前端,微前端,微前端,早期 | `GetVoucherV2` |
| `POST` | `/api/v2/promotion/voucher/list` | 微前端,微前端,微前端,早期 | `ListVoucherV2` |
| `POST` | `/api/v2/promotion/voucher/update` | 微前端,微前端,微前端,早期 | `UpdateVoucherV2` |
| `GET` | `/widget/api/v1/promotion/list_seller_gray_config` | 微前端,微前端,早期 | `ListSellerGrayConfigForWidget` |
| `POST` | `/widget/api/v1/promotion/mget_item_data` | 微前端,微前端,早期 | `MGetItemDataForWidget` |

## 数据 / 罗盘 / 报表（502）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/v1/insights/creator-outreach` | 联盟bundle |  |
| `POST` | `/api/v1/insights/pop/product/optimize/data/get` | 微前端,微前端,微前端 | `GetPopOptimizationData` |
| `POST` | `/api/v1/insights/pop/product/optimize/optimized/list` | 微前端,微前端,微前端 | `GetPopOptimizedProductPage` |
| `?` | `/api/v1/insights/profile/creator` | 微前端 |  |
| `?` | `/api/v1/insights/profile/shop` | 微前端 |  |
| `?` | `/api/v1/insights/sample-analysis` | 联盟bundle |  |
| `POST` | `/api/v1/insights/seller/core/stats` | 微前端,微前端,微前端 | `GetSellerCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/core/stats/export` | 微前端,微前端,微前端 | `GetSellerCoreStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/creator/list` | 微前端,微前端,微前端 | `GetSellerCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/creator/list/export` | 微前端,微前端,微前端 | `GetSellerCreatorListExportQuery` |
| `POST` | `/api/v1/insights/seller/creator/live/diagnosis/stats` | 微前端,微前端,微前端 | `GetSellerCreatorLiveDiagnosisStatsQuery` |
| `POST` | `/api/v1/insights/seller/creator/live/list` | 微前端,微前端,微前端 | `GetSellerCreatorLiveListQuery` |
| `POST` | `/api/v1/insights/seller/creator/product/list` | 微前端,微前端,微前端 | `GetSellerCreatorProductListQuery` |
| `POST` | `/api/v1/insights/seller/creator/video/list` | 微前端,微前端,微前端 | `GetSellerCreatorVideoListQuery` |
| `POST` | `/api/v1/insights/seller/data/overview/creator/list` | 微前端,微前端,微前端 | `GetSellerDataOverviewCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/live/creator/list` | 微前端,微前端,微前端 | `GetSellerLiveCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/live/creator/list/search` | 微前端,微前端,微前端 | `GetSellerLiveCreatorListSearchQuery` |
| `POST` | `/api/v1/insights/seller/live/diagnosis/creator/details` | 微前端,微前端,微前端 | `GetSellerLiveDiagnosisCreatorDetailsQuery` |
| `POST` | `/api/v1/insights/seller/live/diagnosis/creator/list` | 微前端,微前端,微前端 | `GetSellerLiveDiagnosisCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/live/diagnosis/creator/suggestion/list` | 微前端,微前端,微前端 | `GetSellerLiveDiagnosisCreatorSuggestionListQuery` |
| `POST` | `/api/v1/insights/seller/live/list` | 微前端,微前端,微前端 | `GetSellerLiveListQuery` |
| `POST` | `/api/v1/insights/seller/live/list/export` | 微前端,微前端,微前端 | `GetSellerLiveListExportQuery` |
| `POST` | `/api/v1/insights/seller/live/optimizer/account/suggestion` | 微前端,微前端,微前端 | `GetSellerLiveOptimizerAccountSuggestion` |
| `POST` | `/api/v1/insights/seller/live/optimizer/session/suggestion` | 微前端,微前端,微前端 | `GetSellerLiveOptimizerSessionSuggestion` |
| `POST` | `/api/v1/insights/seller/live/optimizer/summary` | 微前端,微前端,微前端 | `GetSellerLiveOptimizerSummary` |
| `POST` | `/api/v1/insights/seller/live/performance/creator/list` | 微前端,微前端,微前端 | `GetSellerLivePerformanceCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/live/product/list` | 微前端,微前端,微前端 | `GetSellerLiveProductListQuery` |
| `POST` | `/api/v1/insights/seller/live/stats` | 微前端,微前端,微前端 | `GetSellerLiveStatsQuery` |
| `POST` | `/api/v1/insights/seller/live/stats/export` | 微前端,微前端,微前端 | `GetSellerLiveStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/notifications` | 微前端,微前端,微前端 | `GetNotificationQuery` |
| `POST` | `/api/v1/insights/seller/notifications/get` | 微前端,微前端,微前端 | `GetSellerNotificationQuery` |
| `POST` | `/api/v1/insights/seller/notifications/set` | 微前端,微前端,微前端 | `SetSellerNotificationQuery` |
| `POST` | `/api/v1/insights/seller/shop/ab_experiment/enabled` | 微前端,微前端,微前端 | `GetSellerShopABExperimentEnabledQuery` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/export` | 微前端,微前端 | `GetShopDiagnosisIndicatorListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/list` | 微前端,微前端 | `GetShopDiagnosisIndicatorListQuery` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/list_v2` | 微前端 | `GetShopDiagnosisIndicatorListQueryV2` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/report/export` | 微前端,微前端 | `ShopDiagnosisReportExportFile` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/report/stats` | 微前端,微前端 | `ShopDiagnosisReportStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/stats` | 微前端,微前端 | `GetShopDiagnosisIndicatorStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/analytics/insights/stats_v2` | 微前端 | `GetShopDiagnosisIndicatorStatsQueryV2` |
| `?` | `/api/v1/insights/seller/shop/associated/creators` | 微前端,微前端 | `GetSellerShopAssociatedCreators` |
| `POST` | `/api/v1/insights/seller/shop/authorization/get` | 微前端,微前端,微前端 | `GetSellerShopAuthQuery` |
| `POST` | `/api/v1/insights/seller/shop/authorization/set` | 微前端,微前端,微前端 | `SetSellerShopAuthQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/boosted/impression/product/list` | 微前端,微前端,微前端 | `SellerShopCenterBoostedImpressionProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/boosted/impression/product/list/export` | 微前端,微前端,微前端 | `ShopCenterBoostedImpressionProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/boosted/impression/product/stats` | 微前端,微前端,微前端 | `ShopCenterBoostedImpressionProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/boosted/impression/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterBoostedImpressionStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/channel/product/list` | 微前端,微前端,微前端 | `GetSellerShopCenterChannelProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/channel/product/list/export` | 微前端,微前端,微前端 | `GetSellerShopCenterChannelProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/channel/product/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterChannelProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/channel/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterChannelStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/channel/stats/export` | 微前端,微前端,微前端 | `GetSellerShopCenterChannelStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/main/core/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterMainCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/main/core/stats/export` | 微前端,微前端,微前端 | `GetSellerShopCenterMainCoreStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/product/list/categories` | 微前端,微前端,微前端 | `GetSellerShopCenterHotProductsCategoriesQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/rank/shop/category/list` | 微前端,微前端,微前端 | `GetSellerShopCenterRankShopCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/rank/shop/list` | 微前端,微前端,微前端 | `GetSellerShopCenterRankShopListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/core/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterRecommendationCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/core/stats/export` | 微前端,微前端,微前端 | `ShopCenterRecommendationCoreStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/products/issues/list` | 微前端,微前端,微前端 | `ShopCenterRecommendationProductsIssuesListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/products/issues/list/export` | 微前端,微前端,微前端 | `CenterRecommendationProductsIssuesListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/products/newly_passed/list` | 微前端,微前端,微前端 | `CenterRecommendationProductsNewlyPassedListQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/products/newly_passed/list/export` | 微前端,微前端,微前端 | `RecommendationProductsNewlyPassedListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/recommendation/status/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterRecommendationStatusStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/ttp/channel/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterTtpChannelStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/ttp/main/core/stats` | 微前端,微前端,微前端 | `GetSellerShopCenterTtpMainCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/center/ttp/product/list` | 微前端,微前端,微前端 | `GetSellerShopCenterTtpHotProductsQuery` |
| `POST` | `/api/v1/insights/seller/shop/data/available/date` | 微前端,微前端,微前端 | `GetSellerShopPageDataReadyTimeQuery` |
| `POST` | `/api/v1/insights/seller/shop/export/file` | 微前端,微前端,微前端 | `GetSellerShopExportFileQuery` |
| `POST` | `/api/v1/insights/seller/shop/export/task/list` | 微前端,微前端,微前端 | `GetSellerShopExportTaskListQuery` |
| `POST` | `/api/v1/insights/seller/shop/gtm/display/judge` | 微前端,微前端 | `GetSellerShopProgramGtmDisplayJudgeQuery` |
| `POST` | `/api/v1/insights/seller/shop/gtm/display/save` | 微前端,微前端 | `GetSellerShopProgramGtmDisplaySaveQuery` |
| `POST` | `/api/v1/insights/seller/shop/high_value_customer/account_list` | 微前端 | `GetSellerLiveHighValueCustomerAccountListQuery` |
| `POST` | `/api/v1/insights/seller/shop/im/agent/list` | 微前端,微前端,微前端 | `GetSellerShopIMAgentStatsListQuery` |
| `POST` | `/api/v1/insights/seller/shop/im/agent/list/export` | 微前端,微前端,微前端 | `GetSellerShopIMAgentStatsListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/im/agent/stats` | 微前端,微前端,微前端 | `GetSellerShopIMAgentStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/im/stats` | 微前端,微前端,微前端 | `GetSellerShopIMStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/info` | 微前端,微前端,微前端 | `GetSellerShopInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/keyword/details/list` | 微前端,微前端,微前端 | `GetSellerShopSearchKeywordDetailsListQuery` |
| `POST` | `/api/v1/insights/seller/shop/keyword/details/list/export` | 微前端,微前端,微前端 | `GetSellerShopSearchKeywordDetailsListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/keyword/list` | 微前端,微前端,微前端 | `GetSellerShopSearchKeywordListQuery` |
| `POST` | `/api/v1/insights/seller/shop/keyword/list/export` | 微前端,微前端,微前端 | `GetSellerShopSearchKeywordListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/account/stats` | 微前端,微前端 | `GetSellerShopLiveAccountStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/account/stats/export` | 微前端,微前端 | `GetSellerShopLiveAccountStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/account/stats/tooltip` | 微前端,微前端 | `GetSellerShopLiveAccountStatsTooltipQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/ads/diagnosis` | 微前端,微前端,微前端 | `GetSellerShopLiveAdsDiagnosis` |
| `POST` | `/api/v1/insights/seller/shop/live/benchmark_category/list` | 微前端,微前端 | `GetSellerShopLiveBenchmarkCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnose/core` | 微前端,微前端 | `GetSellerLiveDiagnoseCoreQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/benchmark_live/list` | 微前端,微前端 | `GetSellerShopLiveDiagnosisBenchmarkLiveListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/core/info` | 微前端,微前端 | `GetSellerShopLiveDiagnosisCoreInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/info/export` | 微前端,微前端 | `GetSellerShopLiveDiagnosisInfoExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/label/info` | 微前端,微前端 | `GetSellerShopLiveDiagnosisLabelInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/metric_card` | 微前端 | `GetSellerShopLiveDiagnosisMetricCardQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/status/list` | 微前端 | `GetSellerShopLiveDiagnosisStatusListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/diagnosis/violation/list` | 微前端,微前端 | `GetSellerShopLiveDiagnosisViolationListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/key_metric/tooltips` | 微前端 | `GetSellerLiveKeyMetricQueryTooltips` |
| `POST` | `/api/v1/insights/seller/shop/live/linked_account/list` | 微前端,微前端 | `GetSellerShopLiveLinkedAccountListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/list` | 微前端,微前端 | `GetSellerShopLiveListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/list/export` | 微前端,微前端 | `GetSellerShopLiveListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/list/tooltip` | 微前端,微前端 | `GetSellerShopLiveListTooltipQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/recent/query/list` | 微前端 | `GetSellerShopLiveRecentQueryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/stats` | 微前端,微前端 | `GetSellerShopLiveStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/stats/export` | 微前端,微前端 | `GetSellerShopLiveStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/stats/tooltip` | 微前端,微前端 | `GetSellerShopLiveStatsTooltipQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/account/stats` | 微前端,微前端 | `GetSellerShopLiveTrafficAccountStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/account/stats/export` | 微前端,微前端 | `GetSellerShopLiveTrafficAccountStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/channel/stats` | 微前端,微前端,微前端 | `GetSellerShopLiveTrafficChannelStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/live/stats` | 微前端,微前端 | `GetSellerShopLiveTrafficLiveStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/live/stats/export` | 微前端,微前端 | `GetSellerShopLiveTrafficLiveStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/live/traffic/stats` | 微前端,微前端,微前端 | `GetSellerShopLiveTrafficStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/logistics/product/list` | 微前端,微前端,微前端 | `GetSellerShopLogisticsProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/logistics/product/list/export` | 微前端,微前端,微前端 | `GetSellerShopLogisticsProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/logistics/provider/list` | 微前端,微前端,微前端 | `GetSellerShopLogisticsProviderListQuery` |
| `POST` | `/api/v1/insights/seller/shop/logistics/stats` | 微前端,微前端,微前端 | `GetSellerShopLogisticsStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/blueocean/rank` | 微前端,微前端,微前端 | `ShopMarketQueryBlueOceanKeywordRankListQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/blueocean/rank/export` | 微前端,微前端,微前端 | `MarketQueryBlueOceanKeywordRankListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/blueocean/trend` | 微前端,微前端,微前端 | `ShopMarketQueryBlueOceanKeywordTrendStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/high_potential/rank/list` | 微前端,微前端,微前端 | `ShopMarketQueryHighPotentialKeywordRankListQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/high_potential/rank/list/export` | 微前端,微前端,微前端 | `QueryHighPotentialKeywordRankListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/high_potential/stats` | 微前端,微前端,微前端 | `ShopMarketQueryHighPotentialKeywordStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/popular/rank` | 微前端,微前端,微前端 | `SellerShopMarketQueryPopularKeywordRankListQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/popular/rank/export` | 微前端,微前端,微前端 | `ShopMarketQueryPopularKeywordRankListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/popular/trend` | 微前端,微前端,微前端 | `ShopMarketQueryPopularKeywordTrendStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/skyrocketing/rank` | 微前端,微前端,微前端 | `ShopMarketQuerySkyrocketingKeywordRankListQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/skyrocketing/rank/export` | 微前端,微前端,微前端 | `MarketQuerySkyrocketingKeywordRankListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/market/query/skyrocketing/trend` | 微前端,微前端,微前端 | `ShopMarketQuerySkyrocketingKeywordTrendStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/negative/review/available/date` | 微前端,微前端 | `GetSellerShopNegativeReviewAvailableDateQuery` |
| `POST` | `/api/v1/insights/seller/shop/negative/review/product/list` | 微前端,微前端,微前端 | `GetSellerShopNegativeReviewProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/negative/review/stats` | 微前端,微前端,微前端 | `GetSellerShopNegativeReviewStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/opportunity/center/product/card/stats` | 微前端,微前端,微前端 | `GetSellerShopOpportunityCenterProductCardStats` |
| `POST` | `/api/v1/insights/seller/shop/os_data` | 微前端 | `GetOsDataQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/ads_banner/info` | 微前端,微前端 | `GetSellerShopOverviewAdsBannerInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/diagnosis/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewDiagnosisStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/gmv_snapshot/live/list` | 微前端,微前端,微前端 | `GetSellerShopOverviewGmvSnapshotLiveListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/gmv_snapshot/product_card/list` | 微前端,微前端,微前端 | `SellerShopOverviewGmvSnapshotProductCardListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/gmv_snapshot/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewGmvSnapshotStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/gmv_snapshot/video/list` | 微前端,微前端,微前端 | `GetSellerShopOverviewGmvSnapshotVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/marketing/creator/list` | 微前端,微前端,微前端 | `GetSellerShopOverviewMarketingCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/marketing/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewMarketingStatsQuery` |
| `?` | `/api/v1/insights/seller/shop/overview/performance/carousel/display` | 微前端,微前端 | `SellerShopOverviewPerformanceCarouselDisplayQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/latest_date` | 微前端,微前端,微前端 | `GrossRevenueBreakdownLatestReadyDateQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/latest_date_v2` | 微前端,微前端 | `GrossRevenueBreakdownLatestReadyDateV2Query` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/stats` | 微前端,微前端,微前端 | `PerformanceGrossRevenueBreakdownStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/stats_v2` | 微前端,微前端 | `PerformanceGrossRevenueBreakdownStatsV2Query` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/insights/stats` | 微前端,微前端 | `GetSellerShopOverviewPerformanceInsightsStats` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/nrr/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewPerformanceNRRStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewPerformanceStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/stats/export` | 微前端,微前端,微前端 | `GetSellerShopOverviewPerformanceStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/today/live/list` | 微前端,微前端,微前端 | `SellerShopOverviewPerformanceTodayLiveListQuery` |
| `POST` | `/api/v1/insights/seller/shop/overview/performance/today/stats` | 微前端,微前端,微前端 | `GetSellerShopOverviewPerformanceTodayStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/performance/stats` | 微前端,微前端,微前端 | `GetSellerShopPagePerformanceStats` |
| `POST` | `/api/v1/insights/seller/shop/performance/stats/export` | 微前端,微前端,微前端 | `GetSellerShopPagePerformanceStatsExport` |
| `POST` | `/api/v1/insights/seller/shop/photo/analytics/photo/stats` | 微前端 | `GetSellerShopPhotoAnalyticsPhotoStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/photo/analytics/photo/stats/export` | 微前端 | `GetSellerShopPhotoAnalyticsPhotoStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/photo/analytics/product/list` | 微前端 | `GetSellerShopPhotoAnalyticsProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/photo/analytics/product/list/export` | 微前端 | `GetSellerShopPhotoAnalyticsProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/diagnosis` | 微前端,微前端,微前端 | `MGetSellerShopProductCardDiagnosis` |
| `POST` | `/api/v1/insights/seller/shop/product/card/list` | 微前端,微前端,微前端 | `GetSellerShopProductCardListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductCardListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/product/traffic/stats/export` | 微前端,微前端,微前端 | `ShopProductCardProductTrafficStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/traffic/sources/list` | 微前端,微前端,微前端 | `GetSellerShopProductCardTrafficSourcesListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/traffic/stats` | 微前端,微前端,微前端 | `GetSellerShopProductCardTrafficStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/traffic/stats/export` | 微前端,微前端,微前端 | `GetSellerShopProductCardTrafficStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/user/action` | 微前端,微前端,微前端 | `GetSellerShopProductCardUserActionQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/card/user/suggestion/list` | 微前端,微前端,微前端 | `GetSellerShopProductCardUserSuggestionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/category/list` | 微前端,微前端,微前端 | `GetSellerShopProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/channel/content` | 微前端,微前端,微前端 | `GetSellerShopProductChannelContentQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/creator/list` | 微前端,微前端,微前端 | `GetSellerShopProductCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/creator/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductCreatorListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/diagnosis/list` | 微前端,微前端,微前端 | `GetSellerShopProductDiagnosisListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/diagnosis/quality/list` | 微前端,微前端,微前端 | `GetSellerShopProductDiagnosisQualityListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/diagnosis/stats` | 微前端,微前端,微前端 | `GetSellerShopProductDiagnosisStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/info` | 微前端,微前端,微前端 | `GetSellerShopProductInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/list` | 微前端,微前端,微前端 | `GetSellerShopProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/live/list` | 微前端,微前端,微前端 | `GetSellerShopProductLiveListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/live/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductLiveListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/search` | 微前端,微前端,微前端 | `GetSellerShopProductSearchQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/sku/list` | 微前端,微前端,微前端 | `GetSellerShopProductSKUListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/sku/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductSKUListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/stats` | 微前端,微前端,微前端 | `GetSellerShopProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/video/list` | 微前端,微前端,微前端 | `GetSellerShopProductVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/video/list/export` | 微前端,微前端,微前端 | `GetSellerShopProductVideoListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/product/voc/detail` | 微前端,微前端 | `GetSellerShopProductVocDetailQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/bcd/category/info` | 微前端,微前端 | `GetSellerShopProgramBcdProductCategoryQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/bcd/product/list` | 微前端,微前端 | `GetSellerShopProgramBcdProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/bcd/register/info` | 微前端,微前端 | `GetSellerShopProgramBcdRegisterInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/bcd/stats` | 微前端,微前端 | `GetSellerShopProgramBcdStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/eams/register/info` | 微前端,微前端 | `GetSellerShopProgramEamsRegisterInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/flashsale/category/info` | 微前端,微前端 | `GetSellerShopProgramFlashSaleProductCategoryQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/flashsale/product/list` | 微前端,微前端 | `GetSellerShopProgramFlashSaleProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/flashsale/register/info` | 微前端,微前端 | `GetSellerShopProgramFlashSaleRegisterInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/flashsale/stats` | 微前端,微前端 | `GetSellerShopProgramFlashSaleStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/page/display/list` | 微前端,微前端 | `GetSellerShopProgramCoFundingPageDisplayQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/shipping/register/info` | 微前端,微前端,微前端 | `GetSellerShopProgramShippingRegisterInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/shipping/stats` | 微前端,微前端,微前端 | `GetSellerShopProgramShippingStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/program/vxp_plus/status` | 微前端 | `GetSellerShopProgramVxpPlusStatusQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/category/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/livestream/category/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankLivestreamCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/livestream/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankLivestreamListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/product/category/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/product/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/video/list` | 微前端,微前端,微前端 | `GetSellerShopScoreRankVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/rank/video_inspiration/latest_date` | 微前端,微前端 | `GetSellerShopVideoInspirationLatestReadyDate` |
| `POST` | `/api/v1/insights/seller/shop/rank/video_inspiration/list` | 微前端,微前端,微前端 | `GetSellerShopVideoInspirationRankingList` |
| `POST` | `/api/v1/insights/seller/shop/rank/video_inspiration/skill/list` | 微前端,微前端,微前端 | `GetSellerShopVideoInspirationSkillList` |
| `POST` | `/api/v1/insights/seller/shop/rank/video_inspiration/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoInspirationStats` |
| `POST` | `/api/v1/insights/seller/shop/rank/video_inspiration/tiktok_data/token` | 微前端,微前端 | `GetSellerShopVideoInspirationTikTokDataToken` |
| `POST` | `/api/v1/insights/seller/shop/search/optimisation/product/optimised/list` | 微前端,微前端,微前端 | `GetSellerShopSearchProductOptimisedTitleListQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/optimisation/product/optimised/stats` | 微前端,微前端,微前端 | `GetSellerShopSearchOptimisedTitleStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/optimisation/product/optimised/trend` | 微前端,微前端,微前端 | `SellerShopSearchProductOptimisedTitleTrendQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/optimisation/product/sale/keyword/stats` | 微前端,微前端,微前端 | `GetSellerShopSearchProductSaleKeywordDetailsQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/optimisation/product/sale/list` | 微前端,微前端,微前端 | `GetSellerShopSearchProductSaleListQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/store/keyword/details/list` | 微前端,微前端,微前端 | `GetSellerShopSearchStoreKeywordDetailsListQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/store/keyword/details/list/export` | 微前端,微前端,微前端 | `ShopSearchStoreKeywordDetailsListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/store/keyword/list` | 微前端,微前端,微前端 | `GetSellerShopSearchStoreKeywordListQuery` |
| `POST` | `/api/v1/insights/seller/shop/search/store/keyword/list/export` | 微前端,微前端,微前端 | `GetSellerShopSearchStoreKeywordListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/service/shipping/stats` | 微前端,微前端,微前端 | `GetSellerShopServiceShippingStats` |
| `POST` | `/api/v1/insights/seller/shop/short/video/center/video/list` | 微前端,微前端,微前端 | `GetSellerShopShortVideoCenterVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/short/video/center/video/list/export` | 微前端,微前端,微前端 | `GetSellerShopShortVideoCenterVideoListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/short/video/product/list` | 微前端,微前端,微前端 | `GetSellerShopShortVideoProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/short/video/stats` | 微前端,微前端,微前端 | `GetSellerShopShortVideoStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/available/date` | 微前端,微前端 | `GetShopSpillOverAvailableDateQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/contribution/list` | 微前端 | `GetShopSpillOverContributionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/data_source` | 微前端,微前端 | `GetShopSpillOverDataSourceQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/add` | 微前端,微前端 | `AddShopSpillOverReport` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/contribution/list` | 微前端 | `GetShopSpillOverReportContributionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/contribution/list/export` | 微前端 | `GetShopSpillOverReportContributionListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/delete` | 微前端,微前端 | `DeleteShopSpillOverReport` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/list` | 微前端,微前端 | `GetShopSpillOverReportListQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/stats` | 微前端,微前端 | `GetShopSpillOverReportStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/stats/export` | 微前端,微前端 | `GetShopSpillOverReportStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/update` | 微前端,微前端 | `UpdateShopSpillOverReport` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/user_profile` | 微前端,微前端 | `GetShopSpillOverReportUserProfileQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/report/user_profile/export` | 微前端,微前端 | `GetShopSpillOverReportUserProfileExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/stats` | 微前端,微前端 | `GetShopSpillOverStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/spillover/user_profile` | 微前端,微前端 | `GetShopSpillOverUserProfileQuery` |
| `POST` | `/api/v1/insights/seller/shop/toko/feature_flag` | 微前端,微前端,微前端 | `GetSellerTokoIntegrationFeatureFlag` |
| `POST` | `/api/v1/insights/seller/shop/us/overview/data/export` | 微前端,微前端 | `GetSellerShopUsOverviewDataExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/us/overview/today/data/available` | 微前端,微前端 | `GetSellerShopUsOverviewTodayDataAvailableQuery` |
| `POST` | `/api/v1/insights/seller/shop/user/composition` | 微前端,微前端,微前端 | `GetSellerShopUserCompositionListQuery` |
| `POST` | `/api/v1/insights/seller/shop/user/portrait` | 微前端,微前端,微前端 | `GetSellerShopUserPortraitListQuery` |
| `POST` | `/api/v1/insights/seller/shop/user/stats` | 微前端,微前端,微前端 | `GetSellerShopUserCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/user/trend` | 微前端,微前端,微前端 | `GetSellerShopUserTrendQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/ads/diagnosis` | 微前端,微前端,微前端 | `GetSellerShopVideoAdsDiagnosis` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/account/performance/list` | 微前端,微前端,微前端 | `ShopVideoAnalyticsAccountPerformanceListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/ads/info` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsAdsInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/creator/list` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/inspiration/list` | 微前端 | `GetSellerShopVideoAnalyticsVideoInspirationQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/photo/list` | 微前端,微前端 | `GetSellerShopVideoAnalyticsPhotoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/photo/list/export` | 微前端,微前端 | `GetSellerShopVideoAnalyticsPhotoListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/photo_product/list` | 微前端,微前端 | `GetSellerShopVideoAnalyticsPhotoProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/photo_product/list/export` | 微前端 | `ShopVideoAnalyticsPhotoProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/product/related/video/list` | 微前端,微前端,微前端 | `ShopVideoAnalyticsProductRelatedVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/traffic/channel/stats` | 微前端,微前端,微前端 | `SellerShopVideoAnalyticsTrafficChannelStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/traffic/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsTrafficStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/boost/info` | 微前端,微前端 | `GetSellerShopVideoAnalyticsBoostInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/content/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoContentStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/diagnosis` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoDiagnosisQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/diagnosis/suggestion/info` | 微前端,微前端,微前端 | `ShopVideoAnalyticsDiagnosisSuggestionInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/info` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/key_metric/tooltips` | 微前端 | `GetSellerShopVideoKeyMetricQueryTooltips` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/list` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/list/export` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoListExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/product/list` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoProductListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/product/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/profile/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoProfileStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/analytics/video/stats/export` | 微前端,微前端,微前端 | `GetSellerShopVideoAnalyticsVideoStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/content/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoContentStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/creator/list` | 微前端,微前端,微前端 | `GetSellerShopVideoCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/check` | 微前端 | `CheckVideoDiagnosis` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/content_analysis` | 微前端 | `VideoDiagnosisContentAnalysis` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/default_state` | 微前端 | `GetVideoDiagnosisDefaultState` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/penalty` | 微前端 | `GetVideoPenaltyInfo` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/trend` | 微前端 | `GetVideoDataTrend` |
| `POST` | `/api/v1/insights/seller/shop/video/diagnosis/video_second_trend` | 微前端 | `GetVideoSecondTrend` |
| `POST` | `/api/v1/insights/seller/shop/video/info` | 微前端,微前端,微前端 | `GetSellerShopVideoInfoQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/list` | 微前端,微前端,微前端 | `GetSellerShopVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/list/export` | 微前端,微前端,微前端 | `GetSellerShopVideoExportQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/product/related/video/list` | 微前端,微前端,微前端 | `GetSellerShopVideoProductRelatedVideoListQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/product/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/profile/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoProfileStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/traffic/channel/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoTrafficChannelStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/traffic/stats` | 微前端,微前端,微前端 | `GetSellerShopVideoTrafficStatsQuery` |
| `POST` | `/api/v1/insights/seller/shop/video/traffic_card/list` | 微前端,微前端,微前端 | `GetSellerShopVideoTrafficCardList` |
| `POST` | `/api/v1/insights/seller/shop/video/traffic_card/redeem` | 微前端,微前端,微前端 | `SetSellerShopVideoTrafficCardRedeem` |
| `POST` | `/api/v1/insights/seller/store/stats` | 微前端,微前端,微前端 | `GetSellerStoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/core/stats` | 微前端,微前端 | `GetSellerDataOverviewCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/core/stats/export` | 微前端,微前端 | `GetSellerDataOverviewCoreStatsExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/ongoing_live/list` | 微前端,微前端 | `GetSellerDataOverviewOngoingLivesListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/post_purchase/stats` | 微前端,微前端 | `GetSellerDataOverviewPostPurchaseStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/revenue_ranking/stats` | 微前端,微前端 | `GetSellerDataOverviewRevenueRankingStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/data_overview/todays_performance/stats` | 微前端,微前端 | `GetSellerDataOverviewTodaysPerformanceStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/edm/get_auth_info` | 微前端 | `GetSellerEDMAuthInfo` |
| `POST` | `/api/v1/insights/seller/ttp/edm/set_auth_info` | 微前端,微前端 | `SetSellerEDMAuthInfo` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/ace/stats` | 微前端,微前端 | `GetAceStats` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/affiliate_retarget_creator/list` | 微前端,微前端 | `SalesOpportunityAffiliateRetargetCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/creator/list` | 微前端,微前端 | `GetSellerSalesOpportunityFullSiteCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/product/list` | 微前端,微前端 | `GetSellerSalesOpportunityProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/suggestion/feedback` | 微前端,微前端 | `GetSellerSalesOpportunitySuggestionFeedbackQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/suggestion/list` | 微前端,微前端 | `GetSellerSalesOpportunitySuggestionListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/video_filter/list` | 微前端,微前端 | `GetSellerSalesOpportunityVideoFilterListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/opportunity_insights/viewer_traffic/stats` | 微前端,微前端 | `GetSellerSalesOpportunityViewerTrafficQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/category/list/latest/offline` | 微前端,微前端 | `GetSellerLatestOfflineProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/content/list` | 微前端,微前端 | `GetSellerProductContentListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/content/list/export` | 微前端,微前端 | `GetSellerProductContentListExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/core/stats` | 微前端,微前端 | `GetSellerProductCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/creator/list` | 微前端,微前端 | `GetSellerProductCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/creator/list/export` | 微前端,微前端 | `GetSellerProductCreatorListExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/detail/info` | 微前端,微前端 | `GetProductDetailInfoQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/inventory` | 微前端,微前端 | `GetSellerProductInventoryQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/list` | 微前端,微前端 | `GetSellerProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/list/export` | 微前端,微前端 | `GetSellerProductListExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/list/export/v2` | 微前端,微前端 | `GetSellerProductListExportQueryV2` |
| `POST` | `/api/v1/insights/seller/ttp/product/list/v2` | 微前端,微前端 | `GetSellerProductListQueryV2` |
| `POST` | `/api/v1/insights/seller/ttp/product/optimisation` | 微前端,微前端 | `GetSellerProductOptimisationQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/price/tracking` | 微前端,微前端 | `GetSellerProductPriceTrackingQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_performance/stats` | 微前端,微前端 | `GetSellerProductPerformanceStats` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_recommendation/list` | 微前端,微前端 | `GetSellerRecommendedProductList` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_recommendation/not_recommended/list` | 微前端,微前端 | `GetSellerNotRecommendedProductList` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_reward/stats` | 微前端,微前端 | `GetSellerProductRewardStats` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_subscription/behavior/order_type` | 微前端,微前端 | `GetProductSubscriptionBehaviorOrderTypeQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_subscription/export` | 微前端,微前端 | `GetProductSubscriptionExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/product_subscription/products/list` | 微前端,微前端 | `GetProductSubscriptionProductsListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/reversed/stats` | 微前端,微前端 | `GetSellerProductReversedStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/review` | 微前端,微前端 | `GetSellerProductReviewQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/sku/count_by_stock_status` | 微前端,微前端 | `GetSellerProductSKUCountByStockStatusQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/sku/list` | 微前端,微前端 | `GetSellerProductSKUListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/sku/list/export` | 微前端,微前端 | `GetSellerProductSKUListExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/live/list` | 微前端,微前端 | `GetProductTrafficLiveListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/shop/live/list` | 微前端 | `GetProductTrafficShopLiveListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/shop/total/list` | 微前端 | `GetProductTrafficShopTotalListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/shop/video/list` | 微前端 | `GetProductTrafficShopVideoListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/total/list` | 微前端,微前端 | `GetProductTrafficTotalListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product/traffic/video/list` | 微前端,微前端 | `GetProductTrafficVideoListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product_traffic/export` | 微前端,微前端 | `GetProductTrafficExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/product_traffic/stats/get` | 微前端,微前端 | `GetProductTrafficStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/realtime/ongoing_live/list` | 微前端,微前端 | `GetSellerOngoingLivesListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/core/stats` | 微前端,微前端 | `GetSellerSalesCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/creator/list` | 微前端,微前端 | `GetSellerSalesCreatorListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/dayofweek/core/stats` | 微前端,微前端 | `GetSellerSalesCoreStatsByDayOfWeekAndHourQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/ecommerce_video/list` | 微前端,微前端 | `GetSellerSalesEcommerceVideoListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/ecommerce_video/list/export` | 微前端,微前端 | `GetSellerSalesEcommerceVideoListExportQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/gross_revenue_with_subsidy/stats` | 微前端,微前端 | `GetSellerSalesGrossRevenueWithSubsidyStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/live_count_and_duration/stats` | 微前端,微前端 | `GetLiveCountAndDurationQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/product/list` | 微前端,微前端 | `GetSellerSalesProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sales/realtime/core/stats` | 微前端,微前端 | `GetRealtimeSellerSalesRealtimeCoreStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/seller_center/homepage/stats` | 微前端,微前端 | `GetSellerCenterHomepageStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/cancel_and_returns/orders/stats` | 微前端,微前端 | `SellerServiceCancelledAndReturnedOrdersStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/cancel_and_returns/product/list` | 微前端,微前端 | `SellerServiceCancelledAndReturnedProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/cancel_and_returns/product_category/list` | 微前端,微前端 | `CancelledAndReturnedProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/order_complaints/product/list` | 微前端,微前端 | `GetSellerServiceOrderComplaintsProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/order_complaints/product_category/list` | 微前端,微前端 | `ServiceOrderComplaintsProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/order_complaints/stats` | 微前端,微前端 | `GetSellerServiceOrderComplaintsStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/review/product/list` | 微前端,微前端 | `GetSellerServiceReviewProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/review/product_category/list` | 微前端,微前端 | `GetSellerServiceReviewProductCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/service/review/score_distribution/stats` | 微前端,微前端 | `GetSellerServiceReviewScoreDistributionQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/creator/publish/info` | 微前端,微前端 | `GetSellerCreatorPublishInfoQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/live/highlight/category/script_skills/list` | 微前端,微前端 | `SellerShopLiveHighlightCategoryScriptSkillsList` |
| `POST` | `/api/v1/insights/seller/ttp/shop/live/highlight/list` | 微前端,微前端 | `GetSellerShopLiveHighlightList` |
| `POST` | `/api/v1/insights/seller/ttp/shop/live_performance/stats` | 微前端,微前端 | `GetSellerShopLivePerformanceStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/low/quality/video/stats` | 微前端,微前端 | `GetShopLowQualityVideoStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/os_api/latest_available/date` | 微前端,微前端 | `GetLatestAvailableDate` |
| `POST` | `/api/v1/insights/seller/ttp/shop/product/card/trending/product/info` | 微前端,微前端 | `GetSellerShopProductCardTrendingProductInfoQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/product/card/trending/product/list` | 微前端,微前端 | `GetSellerShopProductCardTrendingProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/product/card/trending/product/recommendation/category/list` | 微前端,微前端 | `TrendingProductRecommendationCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/product/card/trending/product/stats` | 微前端,微前端 | `GetSellerShopProductCardTrendingProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop/video/post/suggestion/info` | 微前端,微前端 | `GetSellerVideoPostSuggestionInfoQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop_page/product/list` | 微前端,微前端 | `GetShopPageProductPerformanceListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/shop_page/stats` | 微前端,微前端 | `GetShopPagePerformanceStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sub_campaign/live/list` | 微前端,微前端 | `GetSellerSubCampaignLiveListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sub_campaign/product/list` | 微前端,微前端 | `GetSellerSubCampaignProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sub_campaign/product/stats` | 微前端,微前端 | `GetSellerSubCampaignProductStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sub_campaign/stats` | 微前端,微前端 | `GetSellerSubCampaignStatsQuery` |
| `POST` | `/api/v1/insights/seller/ttp/sub_campaign/video/list` | 微前端,微前端 | `GetSellerSubCampaignVideoListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/task/product/list` | 微前端 | `GetSellerTaskProductListQuery` |
| `POST` | `/api/v1/insights/seller/ttp/task/stats` | 微前端 | `GetSellerTaskStatsQuery` |
| `POST` | `/api/v1/insights/seller/unified/query` | 微前端 | `UnifiedSellerQueryV2` |
| `POST` | `/api/v1/insights/seller/unified/query/export` | 微前端 | `UnifiedSellerQueryExportV2` |
| `POST` | `/api/v1/insights/seller/unified/query/tooltips` | 微前端 | `UnifiedSellerToolTipsQuery` |
| `POST` | `/api/v1/insights/seller/us/shop/rank/category/list` | 微前端,微前端,微前端 | `GetSellerUsShopScoreRankCategoryListQuery` |
| `POST` | `/api/v1/insights/seller/us/shop/rank/list` | 微前端,微前端,微前端 | `GetSellerUsShopScoreRankListQuery` |
| `POST` | `/api/v1/insights/shopify/seller/shop/data/available/date` | 微前端,微前端,微前端 | `GetShopifySellerShopPageDataReadyTimeQuery` |
| `POST` | `/api/v1/insights/shopify/seller/shop/video/analytics/creator/list` | 微前端,微前端,微前端 | `ShopifySellerShopVideoAnalyticsCreatorListQuery` |
| `POST` | `/api/v1/insights/shopify/seller/shop/video/analytics/video/list` | 微前端,微前端,微前端 | `GetShopifySellerShopVideoAnalyticsVideoListQuery` |
| `?` | `/api/v1/insights/transaction-analysis` | 联盟bundle |  |
| `?` | `/api/v1/insights/transaction-analysis/creator-detail` | 联盟bundle |  |
| `?` | `/api/v1/insights/transaction-analysis/product-detail` | 联盟bundle |  |
| `POST` | `/api/v1/insights/unified_data_gateway/seller/query` | 微前端 | `UnifiedSellerQuery` |
| `POST` | `/api/v1/insights/unified_data_gateway/universal/product/category/info` | 微前端 | `ProductCategoryInfoQuery` |
| `POST` | `/api/v1/insights/unified_data_gateway/universal/product/category/search` | 微前端 | `ProductCategorySearchQuery` |
| `POST` | `/api/v1/insights/unified_data_gateway/universal/queries` | 微前端 | `UnifiedQueries` |
| `POST` | `/api/v1/insights/unified_data_gateway/universal/query` | 微前端 | `UnifiedQuery` |
| `POST` | `/api/v1/insights/unified_data_gateway/widget/query` | 微前端 | `UnifiedWidgetQuery` |
| `?` | `/api/v1/insights/video-analysis` | 联盟bundle |  |
| `POST` | `/api/v1/pop/product/optimize/compass/mget` | 微前端 | `MGetProductsForMultiEdit` |
| `POST` | `/api/v1/seller/creator/tip/report` | 微前端,微前端 | `ReportShopCreatorTipRead` |
| `POST` | `/api/v1/seller/growth_center/appeal_center/cancel` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/appeal_center/config/get` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/appeal_center/is_appealable` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/appeal_center/record/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/appeal_center/submit` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/benefit/is_show_benefit` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/creator/action_needed/query` | 早期 |  |
| `GET` | `/api/v1/seller/growth_center/creator/entrance_knowledge/get` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/creator/violation/appeal/submit` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/creator/violation/overview` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/creator/violation/record/query` | 早期 |  |
| `GET` | `/api/v1/seller/growth_center/dynamic_settlement/get` | 早期 |  |
| `GET` | `/api/v1/seller/growth_center/entrance_knowledge/get` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/guard/appeal/submit` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/guard/collection_appeal/create` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/image/upload/token` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/overview/action_needed/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/overview/policy_violations_module/query` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/penalize/rule/get` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/quiz/create` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/quiz/paper/commit` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/quiz/start` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/related_creator/get` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/reward_penalty/appeal/submit` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/reward_penalty/overview/get` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/metrics_module/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/platform/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/product/violation/record/query` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/unviewed_info/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/violation/aggregate/download` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/violation/quick_filter/query` | 微前端 |  |
| `POST` | `/api/v1/seller/growth_center/shop/violation/record/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/violation/record/status/viewed/by_enforcement_plan_id/update` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/violation/records/list` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/warning/quick_filter/query` | 微前端 |  |
| `POST` | `/api/v1/seller/growth_center/shop/warning/record/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/shop/warning/records/list` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/video/upload/token` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation/appeal/pre_validation` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation/appeal/submit` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/violation/banned` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation/correction/detail/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation/correction/form/query` | 微前端,早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation/correction/submit` | 微前端,早期 |  |
| `GET` | `/api/v1/seller/growth_center/violation/list/action_needed` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/violation_id/by_enforced_object/query` | 早期 |  |
| `POST` | `/api/v1/seller/growth_center/warning/record/viewed` | 微前端,早期 |  |
| `?` | `/api/v1/seller/message/report_banner` | 微前端 | `ReportBanner` |
| `?` | `/api/v1/seller/message/report_popup` | 微前端 | `ReportPopupMessage` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/action/report` | 微前端,微前端,微前端,微前端,财务bundle | `ReportCrossBorderAction` |
| `POST` | `/api/v1/seller/outreach/report_complete` | 微前端 | `ReportComplete` |
| `POST` | `/api/v1/seller/outreach/report_exposure` | 微前端 | `ReportExposure` |
| `POST` | `/api/v1/seller/outreach/task_message/report_action` | 微前端 | `ReportAction` |
| `POST` | `/api/v1/seller/sell/v2/plan/report/setting` | 微前端 | `ReportPlanSetting` |
| `POST` | `/api/v1/seller/sell/v2/report/suggestion` | 微前端 | `ReportSellerSuggestion` |
| `POST` | `/api/v1/seller/source/report` | 微前端,财务bundle | `SetSellerSource` |
| `?` | `/api/v1/seller/tasks/statistics/get` | 微前端,微前端 | `SellerTasksStatistics` |
| `?` | `/api/v1/sentry_verify/report_user_event` | 联盟bundle |  |
| `POST` | `/api/v1/shop_im/shop/conversation/report_focus_session` | 微前端,财务bundle | `ReportFocusSession` |
| `POST` | `/api/v1/shop_im/shop/risk/report_customer` | 微前端,财务bundle | `ReportCustomer` |
| `?` | `/api/v2/data_infra/metric_platform/version_management/get_data` | 微前端 |  |
| `?` | `/api/v2/data_infra/metric_query/version_management/query_snapshot` | 微前端 |  |
| `POST` | `/seller/growth_center/grey_test/contain_country` | 微前端 |  |
| `POST` | `/widget/api/v1/pop/product/optimize/compass/mget` | 微前端 | `MGetProductsForMultiEditForWidget` |
| `POST` | `/widget/api/v1/product/optimization/report/metrics` | 微前端 | `ReportOptimizationMetricsForWidget` |
| `GET` | `/widget/api/v1/seller/growth_center/benefit/is_show_benefit` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/creator/entrance_knowledge/get` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/creator/violation/appeal/submit` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/creator/violation/overview` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/dynamic_settlement/get` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/entrance_knowledge/get` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/guard/appeal/submit` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/guard/collection_appeal/create` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/image/upload/token` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/overview/action_needed/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/overview/policy_violations_module/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/quiz/create` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/quiz/paper/commit` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/quiz/start` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/related_creator/get` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/metrics_module/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/platform/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/unviewed_info/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/violation/aggregate/download` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/violation/quick_filter/query` | 微前端 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/violation/record/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/violation/records/list` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/warning/quick_filter/query` | 微前端 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/warning/record/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/shop/warning/records/list` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/video/upload/token` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/violation/appeal/pre_validation` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/violation/appeal/submit` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/violation/banned` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/violation/correction/detail/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/violation/correction/form/query` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/violation/correction/submit` | 早期 |  |
| `GET` | `/widget/api/v1/seller/growth_center/violation/list/action_needed` | 早期 |  |
| `POST` | `/widget/api/v1/seller/growth_center/warning/record/viewed` | 早期 |  |
| `POST` | `/widget/api/v1/seller/outreach/report_complete` | 微前端 | `ReportCompleteForWidget` |
| `POST` | `/widget/api/v1/seller/outreach/task_message/report_action` | 微前端 | `ReportActionForWidget` |
| `POST` | `/widget/api/v1/seller/sell/v2/plan/report/setting` | 微前端 | `WidgetReportPlanSetting` |

## 消息 / IM / 通知（157）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/conversation` | 微前端 | `GetConversationID` |
| `?` | `/api/v1/im/conversation/create` | 客户端 |  |
| `?` | `/api/v1/im/search/search_conversation_by_users` | 客户端 |  |
| `?` | `/api/v1/im/shop_creator/shop/conversation/search` | 客户端 |  |
| `?` | `/api/v1/im/shop_creator/shop/user/token/get` | 客户端,客户端 |  |
| `POST` | `/api/v1/legacy/conversation/history` | 微前端 | `LoadLegacyConversationHistory` |
| `?` | `/api/v1/message/get_by_user_init` | 客户端 |  |
| `POST` | `/api/v1/message/modify` | 微前端 | `ModifyMessage` |
| `GET` | `/api/v1/proxy/seller/helpdesk/conversation/get` | 微前端,微前端 | `GetHelpdeskConversation` |
| `GET` | `/api/v1/seller/assistance/chatbot/history` | 财务bundle |  |
| `POST` | `/api/v1/seller/customer_service/im/base_info/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetIMBaseInfo` |
| `POST` | `/api/v1/seller/message/batch_mark_read` | 微前端 | `BatchMarkRead` |
| `POST` | `/api/v1/seller/message/check_mark_others_as_read_ab` | 微前端 | `CheckMarkOthersAsReadAB` |
| `POST` | `/api/v1/seller/message/clear_others_red_point` | 微前端 | `ClearOthersRedPoint` |
| `POST` | `/api/v1/seller/message/clear_red_point` | 微前端 | `ClearRedPoint` |
| `POST` | `/api/v1/seller/message/focus_config/set` | 微前端 | `SetFocusConfig` |
| `?` | `/api/v1/seller/message/get` | 微前端 | `GetMessage` |
| `?` | `/api/v1/seller/message/get_msg_tabs` | 微前端 | `GetMsgTabs` |
| `?` | `/api/v1/seller/message/get_page_channels` | 微前端 | `GetPageChannels` |
| `?` | `/api/v1/seller/message/list` | 微前端 | `ListMessage` |
| `POST` | `/api/v1/seller/message/mark_read` | 微前端 | `MarkMessageRead` |
| `?` | `/api/v1/seller/message/pull` | 微前端 | `PullMessage` |
| `?` | `/api/v1/seller/message/pull_by_category` | 微前端 | `PullMessageByCategory` |
| `?` | `/api/v1/seller/message/pull_by_category_v2` | 微前端 | `PullMessageByCategoryV2` |
| `?` | `/api/v1/seller/messagev2/get` | 微前端 | `GetMessageV2` |
| `GET` | `/api/v1/sellerassistant/conversations/list` | 财务bundle |  |
| `?` | `/api/v1/shop_im/multi_shop/user/get_info_list` | 微前端,财务bundle | `GetShopInfoList`, `ReportFocusSession` |
| `POST` | `/api/v1/shop_im/shop/batch_decrypt_token` | 微前端,财务bundle | `BatchDecryptToken` |
| `POST` | `/api/v1/shop_im/shop/card/get_card_template_data` | 微前端,财务bundle | `GetCardTemplateData` |
| `POST` | `/api/v1/shop_im/shop/config/cancel_audit_record` | 微前端,财务bundle | `CancelAuditRecord` |
| `POST` | `/api/v1/shop_im/shop/config/check_sensitive_text` | 财务bundle | `CheckSensitiveText` |
| `POST` | `/api/v1/shop_im/shop/config/get_auto_messages_setting` | 微前端,财务bundle | `GetShopAutoMessagesSetting` |
| `POST` | `/api/v1/shop_im/shop/config/get_greeting_config` | 微前端,财务bundle | `GetShopGreetingConfig` |
| `POST` | `/api/v1/shop_im/shop/config/get_shop_and_customer_service_config` | 微前端,财务bundle | `SetShopConfig` |
| `POST` | `/api/v1/shop_im/shop/config/get_shop_config` | 微前端,财务bundle | `CancelAuditRecord`, `GetShopConfig` |
| `POST` | `/api/v1/shop_im/shop/config/set_auto_messages_setting` | 微前端,财务bundle | `SetShopAutoMessagesSetting` |
| `POST` | `/api/v1/shop_im/shop/config/set_automatic_robot_setting` | 微前端,财务bundle | `SetShopAutomaticRobotSetting` |
| `POST` | `/api/v1/shop_im/shop/config/set_greeting_config` | 微前端,财务bundle | `SetShopGreetingConfig` |
| `POST` | `/api/v1/shop_im/shop/config/set_shop_config` | 微前端,财务bundle | `SetShopConfig` |
| `POST` | `/api/v1/shop_im/shop/config/set_working_time` | 微前端,财务bundle | `SetShopWorkingTime` |
| `POST` | `/api/v1/shop_im/shop/conversation/admin_transfer_conversation` | 微前端,财务bundle | `AdminTransferConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/assign_conversation` | 微前端,财务bundle | `AssignConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/can_create_conversation` | 微前端,财务bundle | `CanCreateConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/close_conversation` | 微前端,财务bundle | `CloseConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/create_conversation` | 微前端,财务bundle | `CreateConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/create_conversation_by_order` | 微前端,财务bundle | `CreateConversationByOrder` |
| `POST` | `/api/v1/shop_im/shop/conversation/create_tag_meta` | 微前端,财务bundle | `CreateConversationTagMeta` |
| `POST` | `/api/v1/shop_im/shop/conversation/export` | 财务bundle | `ExportConversation` |
| `?` | `/api/v1/shop_im/shop/conversation/get_conversation_count_and_wait_user_count` | 微前端,财务bundle | `GetWaitUserCountForSellerCenter` |
| `POST` | `/api/v1/shop_im/shop/conversation/get_conversation_info` | 微前端,财务bundle | `GetConversationInfo` |
| `POST` | `/api/v1/shop_im/shop/conversation/get_conversation_info_v2` | 财务bundle | `GetConversationInfoV2` |
| `?` | `/api/v1/shop_im/shop/conversation/get_customer_service_reception_data` | 微前端,财务bundle |  |
| `POST` | `/api/v1/shop_im/shop/conversation/get_history_msgs` | 微前端,财务bundle | `GetHistoryMsg` |
| `POST` | `/api/v1/shop_im/shop/conversation/get_read_index` | 微前端,财务bundle | `GetUserConversationReadIndex` |
| `?` | `/api/v1/shop_im/shop/conversation/get_translation_info` | 微前端,财务bundle | `GetConversationTranslationInfo` |
| `?` | `/api/v1/shop_im/shop/conversation/get_wait_user_count` | 微前端,财务bundle | `GetWaitUserCount`, `Info` |
| `?` | `/api/v1/shop_im/shop/conversation/get_wait_user_count_for_seller_center` | 微前端,财务bundle | `GetWaitUserCountForSellerCenter` |
| `POST` | `/api/v1/shop_im/shop/conversation/list` | 微前端,财务bundle | `ListConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/list_customer_service_conversation` | 微前端,财务bundle | `ListCustomerServiceConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/list_tag_meta` | 微前端,财务bundle | `GetConversationInfoV2`, `Info` |
| `POST` | `/api/v1/shop_im/shop/conversation/list_unassigned_conversation` | 微前端,财务bundle | `ListUnassignedConversations` |
| `POST` | `/api/v1/shop_im/shop/conversation/mark_tags` | 微前端,财务bundle | `MarkConversationTags` |
| `POST` | `/api/v1/shop_im/shop/conversation/mget_conversation_meta_info` | 微前端,财务bundle | `MGetConversationMetaInfo` |
| `POST` | `/api/v1/shop_im/shop/conversation/mset_conversation_meta_info` | 微前端,财务bundle | `MSetConversationMetaInfo` |
| `POST` | `/api/v1/shop_im/shop/conversation/search` | 微前端,财务bundle | `SearchConversation` |
| `POST` | `/api/v1/shop_im/shop/conversation/search_es` | 微前端,财务bundle | `SearchConversationEs` |
| `POST` | `/api/v1/shop_im/shop/conversation/send_template_card` | 微前端,财务bundle | `SendTemplateCard` |
| `POST` | `/api/v1/shop_im/shop/conversation/set_no_response_needed` | 微前端,财务bundle | `SetConversationNoResponseNeeded` |
| `POST` | `/api/v1/shop_im/shop/conversation/set_no_response_needed_by_token` | 微前端,财务bundle | `SetConversationNoResponseNeededByToken` |
| `POST` | `/api/v1/shop_im/shop/conversation/set_total_unread_count` | 微前端,财务bundle | `SetTotalUnreadCount` |
| `POST` | `/api/v1/shop_im/shop/conversation/set_translation_config` | 微前端,财务bundle | `SetConversationTranslationConfig` |
| `POST` | `/api/v1/shop_im/shop/conversation/transfer_conversation` | 微前端,财务bundle | `TransferConversation` |
| `POST` | `/api/v1/shop_im/shop/current_timestamp/get` | 微前端,财务bundle |  |
| `POST` | `/api/v1/shop_im/shop/data_analysis/export_daily_agent_performance_table` | 微前端,财务bundle | `ExportDailyAgentPerformanceTable` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/export_shop_summary_data` | 财务bundle | `ExportShopSummaryData` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/export_shop_trend_data` | 财务bundle | `ExportShopTrendData` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/get_agent_performance_table` | 微前端,财务bundle | `GetAgentPerformanceTable` |
| `?` | `/api/v1/shop_im/shop/data_analysis/get_chat_details` | 微前端,财务bundle | `GetChatDetails` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/get_chat_overview` | 微前端,财务bundle | `GetChatOverview` |
| `?` | `/api/v1/shop_im/shop/data_analysis/get_dashboard_metrics` | 财务bundle | `GetDashboardMetrics` |
| `?` | `/api/v1/shop_im/shop/data_analysis/get_mainpage_metrics` | 微前端,财务bundle | `GetMainPageMetrics` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/get_shop_performance` | 微前端,财务bundle | `GetShopPerformance` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/get_shop_summary_data` | 财务bundle | `GetShopSummaryData` |
| `POST` | `/api/v1/shop_im/shop/data_analysis/get_shop_trend_data` | 财务bundle | `GetShopTrendData` |
| `?` | `/api/v1/shop_im/shop/email/get_notification_customer_service_ids` | 财务bundle | `SetUserInfoWorkBench` |
| `POST` | `/api/v1/shop_im/shop/email/set_notification_customer_service_ids` | 财务bundle | `SetEmailNotificationCustomerServiceIDs` |
| `?` | `/api/v1/shop_im/shop/feedback/get_feel_good` | 微前端,财务bundle | `GetSimpleOrderInfo` |
| `?` | `/api/v1/shop_im/shop/get_can_be_assign_customer_services` | 微前端,财务bundle | `GetCanBeAssignedCustomerServices` |
| `?` | `/api/v1/shop_im/shop/get_current_customer_service` | 微前端,财务bundle | `GetCardTemplateData`, `TemplateData` |
| `?` | `/api/v1/shop_im/shop/get_customer_service` | 微前端,财务bundle |  |
| `POST` | `/api/v1/shop_im/shop/get_customer_services_for_transfer` | 微前端,财务bundle | `GetCustomerServicesForTransfer` |
| `POST` | `/api/v1/shop_im/shop/get_shop_experiment_config` | 微前端,财务bundle | `UploadImg` |
| `POST` | `/api/v1/shop_im/shop/get_voucher_list` | 微前端,财务bundle | `GetVoucherList` |
| `POST` | `/api/v1/shop_im/shop/knowledge/product/delete` | 财务bundle | `DeleteProductKnowledge` |
| `?` | `/api/v1/shop_im/shop/knowledge/product/list` | 财务bundle | `ListProductKnowledge` |
| `POST` | `/api/v1/shop_im/shop/knowledge/product/save` | 财务bundle | `SaveProductKnowledge` |
| `POST` | `/api/v1/shop_im/shop/knowledge/shop/delete` | 财务bundle | `DeleteShopKnowledge` |
| `?` | `/api/v1/shop_im/shop/knowledge/shop/list` | 财务bundle | `ListShopKnowledge` |
| `POST` | `/api/v1/shop_im/shop/knowledge/shop/save` | 财务bundle | `SaveShopKnowledge` |
| `POST` | `/api/v1/shop_im/shop/knowledge/shop/tag/list` | 财务bundle | `ListShopKnowledge` |
| `POST` | `/api/v1/shop_im/shop/knowledge/suggestion/decide` | 财务bundle | `DecideKnowledgeSuggestion` |
| `?` | `/api/v1/shop_im/shop/knowledge/suggestion/list` | 财务bundle | `ListKnowledgeSuggestions` |
| `POST` | `/api/v1/shop_im/shop/order_extra_info/list` | 财务bundle | `ListOrderExtraInfo` |
| `?` | `/api/v1/shop_im/shop/product/get_detail` | 微前端,财务bundle | `GetProductDetail` |
| `?` | `/api/v1/shop_im/shop/product/list_local_products` | 微前端,财务bundle | `ListLocalProducts` |
| `POST` | `/api/v1/shop_im/shop/product/mget_detail` | 财务bundle | `MGetProductsDetail` |
| `?` | `/api/v1/shop_im/shop/pull_read_index/sleep_time` | 微前端,财务bundle | `MGetUserInfo`, `MGetUserInfoV2` |
| `POST` | `/api/v1/shop_im/shop/reverse_type/list` | 微前端,财务bundle | `ListOrderReverseType` |
| `?` | `/api/v1/shop_im/shop/review/detail` | 财务bundle | `GetReviewDetail` |
| `?` | `/api/v1/shop_im/shop/review/search` | 财务bundle | `SearchReview` |
| `POST` | `/api/v1/shop_im/shop/risk/block_buyer` | 财务bundle | `BlockBuyer` |
| `POST` | `/api/v1/shop_im/shop/risk/can_report_customer` | 微前端,财务bundle | `CanReportCustomer` |
| `POST` | `/api/v1/shop_im/shop/risk/get_block_buyer_list` | 财务bundle | `GetBlockBuyerList` |
| `POST` | `/api/v1/shop_im/shop/risk/get_report_reasons` | 微前端,财务bundle | `GetReportReasons` |
| `POST` | `/api/v1/shop_im/shop/risk/unblock_buyer` | 财务bundle | `UnblockBuyer` |
| `POST` | `/api/v1/shop_im/shop/translate` | 微前端,财务bundle | `Translate` |
| `POST` | `/api/v1/shop_im/shop/upload_img` | 微前端,财务bundle | `UploadImg` |
| `POST` | `/api/v1/shop_im/shop/user/admin_search_customer_service` | 微前端,财务bundle | `AdminSearchCustomerService` |
| `POST` | `/api/v1/shop_im/shop/user/admin_update_customer_service_config` | 微前端,财务bundle | `AdminUpdateCustomerServiceConfig` |
| `POST` | `/api/v1/shop_im/shop/user/batch_get_im_id` | 微前端,财务bundle | `BatchGetImId` |
| `POST` | `/api/v1/shop_im/shop/user/get_customer_service_config` | 微前端,财务bundle | `AdminUpdateCustomerServiceConfig` |
| `?` | `/api/v1/shop_im/shop/user/get_shop_and_customer_service_info` | 微前端,财务bundle |  |
| `?` | `/api/v1/shop_im/shop/user/get_shop_live_metrics` | 财务bundle | `GetShopLiveMetrics` |
| `POST` | `/api/v1/shop_im/shop/user/get_target_idc` | 微前端,财务bundle | `GetTargetIDC` |
| `?` | `/api/v1/shop_im/shop/user/get_token` | 微前端,财务bundle | `UpdateCustomerServiceStatus` |
| `?` | `/api/v1/shop_im/shop/user/get_user_info_workbench` | 财务bundle | `GetUserInfoWorkBench` |
| `POST` | `/api/v1/shop_im/shop/user/info` | 微前端,财务bundle | `GetUserInfo` |
| `?` | `/api/v1/shop_im/shop/user/list_shop_customer_service_info` | 微前端,财务bundle | `ListShopCustomerServiceInfo` |
| `POST` | `/api/v1/shop_im/shop/user/mget_info` | 微前端,财务bundle | `MGetUserInfo` |
| `POST` | `/api/v1/shop_im/shop/user/mget_info_v2` | 财务bundle | `MGetUserInfoV2` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/check` | 微前端,财务bundle | `CheckQuickReply` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/create` | 微前端,财务bundle | `CreateQuickReply` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/delete` | 微前端,财务bundle | `DeleteQuickReply` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/list` | 微前端,财务bundle | `ListQuickReply` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/list_for_search` | 微前端,财务bundle | `ListQuickReplyForSearch` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply/update` | 微前端,财务bundle | `UpdateQuickReply` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply_group/change_rank` | 微前端,财务bundle | `ChangeQuickReplyGroupRank` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply_group/check` | 微前端,财务bundle | `CheckQuickReplyGroup` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply_group/create` | 微前端,财务bundle | `CreateQuickReplyGroup` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply_group/delete` | 微前端,财务bundle | `DeleteQuickReplyGroup` |
| `?` | `/api/v1/shop_im/shop/user/quick_reply_group/list` | 微前端,财务bundle | `ListQuickReplyGroup` |
| `POST` | `/api/v1/shop_im/shop/user/quick_reply_group/update` | 微前端,财务bundle | `UpdateQuickReplyGroup` |
| `POST` | `/api/v1/shop_im/shop/user/set_customer_service` | 微前端,财务bundle | `SetCustomerService` |
| `POST` | `/api/v1/shop_im/shop/user/set_customer_service_config` | 微前端,财务bundle | `SetCustomerServiceConfig` |
| `POST` | `/api/v1/shop_im/shop/user/set_user_info_workbench` | 财务bundle | `SetUserInfoWorkBench` |
| `POST` | `/api/v1/shop_im/shop/user/update_customer_service_status` | 微前端,财务bundle | `UpdateCustomerServiceStatus` |
| `POST` | `/api/v1/shop_im/shop/workbench/data/list` | 财务bundle | `ListWorkbenchData` |
| `POST` | `/api/v2/conversations` | 微前端 |  |
| `POST` | `/api/v3/conversation/clear_unread_msg` | 微前端 | `ClearConversationUnreadMsg` |
| `POST` | `/fbt/api/landing/message/seller_web_action` | 微前端 |  |
| `POST` | `/widget/api/v1/seller/message/clear_red_point` | 微前端 | `ClearRedPointForWidget` |
| `POST` | `/widget/api/v1/seller/message/focus_config/set` | 微前端 | `SetFocusConfigForWidget` |
| `POST` | `/widget/api/v1/seller/message/get_msg_tabs` | 微前端 | `GetMsgTabsForWeidget` |
| `?` | `/widget/api/v1/seller/message/list` | 微前端 | `ListMessageForWidget` |
| `POST` | `/widget/api/v1/seller/message/mark_read` | 微前端 | `MarkMessageReadForWidget` |
| `?` | `/widget/api/v1/seller/message/pull_by_category_v2` | 微前端 | `PullMessageByCategoryV2ForWidget` |
| `POST` | `/widget/api/v1/seller/messagev2/get` | 微前端 | `GetMessageV2ForWidget` |

## 治理 / 违规 / 申诉（72）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/seller/join/cross_border/qualification_todo_draft/submit` | 微前端,财务bundle | `SubmitCrossBorderQualificationTodoDraft` |
| `POST` | `/api/v1/seller/onboard/v1/appeal_info/get` | 微前端,微前端,财务bundle | `GetRcsAppealInfo` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/appeal` | 微前端,微前端,微前端,微前端,财务bundle | `AppealCrossBorderOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/appeal_with_token` | 微前端,微前端,财务bundle | `OnboardAppealWithToken` |
| `GET` | `/api/v1/seller/onboard/v1/local/appeal_url/get` | 微前端,微前端,财务bundle | `GetSeaPipoAppealUrl` |
| `POST` | `/api/v1/seller/onboard/v2/appeal/get` | 财务bundle | `GetRcsAppealInfo` |
| `POST` | `/api/v1/seller/onboard/v2/appeal/rcs` | 财务bundle | `OnboardAppealRCS` |
| `POST` | `/api/v1/seller/onboard/v2/appeal/rcs_with_token` | 财务bundle | `OnboardAppealWithToken` |
| `POST` | `/qualification/center/black_word/check` | 微前端 |  |
| `POST` | `/qualification/center/category/banner_close` | 微前端 |  |
| `POST` | `/qualification/center/category/submit` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/category_epr/delete` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/category_epr/edit` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/category_epr/submit` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/epr/delete` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/epr/edit` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/epr/multisubmit` | 微前端 |  |
| `POST` | `/qualification/center/epr_upload/epr/submit` | 微前端 |  |
| `POST` | `/qualification/center/file/upload` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/category_epr/delete` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/category_epr/edit` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/category_epr/submit` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/epr/delete` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/epr/edit` | 微前端 |  |
| `POST` | `/qualification/center/fs/epr_upload/epr/submit` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/create` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/product/batch_link` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/product/link` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/product/list` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/product/unlink` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/translate` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/manufacturer/update` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/create` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/delete` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/product/batch_link` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/product/link` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/product/list` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/product/unlink` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/translate` | 微前端 |  |
| `POST` | `/qualification/center/fs/item/rp/update` | 微前端 |  |
| `POST` | `/qualification/center/fs/product_qualification_task/list` | 微前端 |  |
| `POST` | `/qualification/center/fs/seller_service/submit` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/create` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/product/batch_link` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/product/link` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/product/list` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/product/unlink` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/translate` | 微前端 |  |
| `POST` | `/qualification/center/item/manufacturer/update` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/create` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/delete` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/batch_link` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/link` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/list` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/relation/set` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/relations/change` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/product/unlink` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/translate` | 微前端 |  |
| `POST` | `/qualification/center/item/rp/update` | 微前端 |  |
| `POST` | `/qualification/center/multi_product_qualification_task/list` | 微前端 |  |
| `POST` | `/qualification/center/ocr` | 微前端 |  |
| `POST` | `/qualification/center/product_qualification_task/detail` | 微前端 |  |
| `POST` | `/qualification/center/product_qualification_task/get` | 微前端 |  |
| `POST` | `/qualification/center/product_qualification_task/list` | 微前端 |  |
| `POST` | `/qualification/center/rule/list` | 微前端 |  |
| `POST` | `/qualification/center/seller_service/submit` | 微前端 |  |
| `POST` | `/qualification/center/seller_task_unique_epr/list` | 微前端 |  |
| `POST` | `/qualification/center/task/verification/jumio/callback` | 微前端 |  |
| `POST` | `/qualification/center/task/verification/submit` | 微前端 |  |
| `POST` | `/qualification/center/trademark/banner_close` | 微前端 |  |
| `POST` | `/qualification/center/trademark/submit` | 微前端 |  |
| `POST` | `/widget/api/v1/seller/onboard/v2/appeal/rcs` | 财务bundle | `WidgetOnboardAppealRCS` |

## 商家 / 入驻 / 资质（310）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/app/seller/entity/get` | 微前端,财务bundle | `GetAppEntity` |
| `POST` | `/api/v1/app/seller/profile/address_consent/set` | 微前端,财务bundle | `SetAppAddressConsent` |
| `POST` | `/api/v1/seller/account/common/cerberus/resource/edit` | 财务bundle | `EditCerberusResource` |
| `?` | `/api/v1/seller/account/common/cerberus/resource/get` | 财务bundle | `GetCerberusResource` |
| `POST` | `/api/v1/seller/account/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAccount` |
| `GET` | `/api/v1/seller/account/switch/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetAccountSwitch` |
| `POST` | `/api/v1/seller/account/update` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `UpdateAccount` |
| `GET` | `/api/v1/seller/account_verification/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAccountVerification` |
| `POST` | `/api/v1/seller/entity/file/upload` | 微前端,财务bundle | `UploadFile` |
| `POST` | `/api/v1/seller/entity/file_url/get` | 微前端,财务bundle | `GetFileURL` |
| `POST` | `/api/v1/seller/entity/get` | 微前端,财务bundle | `GetEntity` |
| `POST` | `/api/v1/seller/entity/update` | 微前端,财务bundle | `UpdateEntity` |
| `POST` | `/api/v1/seller/entity/v2/change` | 财务bundle | `SubmitEntityChange` |
| `POST` | `/api/v1/seller/entity/v2/get` | 财务bundle | `GetEntityInfo` |
| `POST` | `/api/v1/seller/entity/v2/pipo/kyb/submit` | 财务bundle | `SubmitEntityPIPOKyb` |
| `POST` | `/api/v1/seller/entity/v2/task/complete` | 财务bundle | `CompleteEntityTask` |
| `POST` | `/api/v1/seller/entity/v2/task/detail` | 财务bundle | `GetEntityTaskDetail` |
| `POST` | `/api/v1/seller/entity/v2/task/list` | 财务bundle | `GetEntityTaskList` |
| `POST` | `/api/v1/seller/entity/v2/task/submit` | 财务bundle | `SubmitEntityTask` |
| `POST` | `/api/v1/seller/entity/v2/update` | 财务bundle | `SubmitEntityUpdate` |
| `POST` | `/api/v1/seller/gs_message/merchant_headlines_feedback` | 微前端,微前端,微前端,财务bundle | `MerchantHeadlinesFeedback` |
| `POST` | `/api/v1/seller/join/create_seller` | 微前端,财务bundle | `CreateSeller` |
| `POST` | `/api/v1/seller/join/cross_border/business_type_todo/submit` | 微前端,财务bundle | `SubmitCrossBorderBusinessTypeTodo` |
| `POST` | `/api/v1/seller/join/cross_border/business_type_todo_draft/submit` | 微前端,财务bundle | `SubmitCrossBorderBusinessTypeTodoDraft` |
| `POST` | `/api/v1/seller/join/cross_border/change_greater_market_region/confirm` | 微前端,财务bundle | `ConfirmCrossBorderChangeGreaterMarketRegion` |
| `POST` | `/api/v1/seller/join/cross_border/create_shop/submit` | 微前端,财务bundle | `SubmitCreateShop` |
| `POST` | `/api/v1/seller/join/cross_border/onboard_info/get` | 微前端,财务bundle | `GetCrossBorderOnboardInfo` |
| `POST` | `/api/v1/seller/join/cross_border/shop_setting_todo_draft/submit` | 微前端,财务bundle | `SubmitCrossBorderShopSettingTodoDraft` |
| `POST` | `/api/v1/seller/join/cross_border/todo0/submit` | 微前端,财务bundle | `SubmitTodo0` |
| `POST` | `/api/v1/seller/join/cross_border/todo1/save-draft` | 微前端,财务bundle | `SaveDraftCrossBorderJoinTodo1` |
| `POST` | `/api/v1/seller/join/cross_border/todo1/submit` | 微前端,财务bundle | `SubmitCrossBorderJoinTodo1` |
| `POST` | `/api/v1/seller/join/cross_border/todo2/submit` | 微前端,财务bundle | `SubmitCrossBorderJoinTodo2` |
| `POST` | `/api/v1/seller/join/entity/verify` | 微前端,财务bundle | `VerifyEntity` |
| `POST` | `/api/v1/seller/join/extended_field/submit` | 微前端,财务bundle | `SubmitExtendedField` |
| `POST` | `/api/v1/seller/join/get` | 微前端,财务bundle | `GetSellerJoin` |
| `POST` | `/api/v1/seller/join/invitation_code/submit` | 微前端,财务bundle | `SubmitInvitationCode` |
| `POST` | `/api/v1/seller/join/local/company_certificate/save-draft` | 微前端,财务bundle | `SaveDraftSubmitCompanyCertificate` |
| `POST` | `/api/v1/seller/join/local/personal_certificate/save-draft` | 微前端,财务bundle | `SaveDraftLocalPersonalCertificate` |
| `POST` | `/api/v1/seller/join/markets/get` | 微前端,财务bundle | `GetMarkets` |
| `POST` | `/api/v1/seller/join/ocr` | 微前端,财务bundle | `Ocr` |
| `POST` | `/api/v1/seller/join/register_create_seller` | 微前端,财务bundle | `RegisterCreateSeller` |
| `POST` | `/api/v1/seller/join/todo1/submit` | 微前端,财务bundle | `SubmitTodo1` |
| `POST` | `/api/v1/seller/join/todo2/company/submit` | 微前端,财务bundle | `SubmitCompanyCertificate` |
| `POST` | `/api/v1/seller/join/todo2/person/submit` | 微前端,财务bundle | `SubmitPersonalCertificate` |
| `POST` | `/api/v1/seller/join/tt_account/verification_code/send` | 微前端,财务bundle | `SendTtAccountVerificationCode` |
| `POST` | `/api/v1/seller/join/tt_account/verify` | 微前端,财务bundle | `VerifyTtAccount` |
| `GET` | `/api/v1/seller/merchant/attestation/region/get` | 微前端,财务bundle | `GetCrossBorderMerchantAttestationRegion` |
| `POST` | `/api/v1/seller/merchant/attestation/state/get` | 微前端,财务bundle | `GetCrossBorderMerchantAttestationState` |
| `POST` | `/api/v1/seller/merchant/attestation/submit` | 微前端,微前端,财务bundle | `SubmitCrossBorderMerchantAttestation` |
| `POST` | `/api/v1/seller/merchant_vat_id/create` | 微前端,微前端,微前端,财务bundle | `CreateMerchantVatID` |
| `POST` | `/api/v1/seller/onboard/company/verify` | 微前端,财务bundle | `VerifyOnboardCompanyInfo` |
| `GET` | `/api/v1/seller/onboard/config/get` | 微前端,财务bundle | `GetOnboardConfig` |
| `GET` | `/api/v1/seller/onboard/detail` | 微前端,财务bundle | `GetOnboardInfoDetail` |
| `GET` | `/api/v1/seller/onboard/local/draft/get` | 微前端,财务bundle | `GetOnboardLocalDraft` |
| `POST` | `/api/v1/seller/onboard/local/sg/personal/extra_submit` | 微前端,财务bundle | `ExtraSubmitOnboardLocalSGPersonal` |
| `POST` | `/api/v1/seller/onboard/local/us/draft/get` | 微前端,财务bundle | `GetOnboardLocalUSDraft` |
| `POST` | `/api/v1/seller/onboard/local/us/draft/save` | 微前端,财务bundle | `SaveOnboardLocalUSDraft` |
| `POST` | `/api/v1/seller/onboard/local/us/extra_submit` | 微前端,财务bundle | `ExtraSubmitOnboardLocalUS` |
| `POST` | `/api/v1/seller/onboard/local/us/submit` | 微前端,财务bundle | `SubmitOnboardLocalUSInfo` |
| `POST` | `/api/v1/seller/onboard/personal/verify` | 微前端,财务bundle | `VerifyOnboardPersonalInfo` |
| `POST` | `/api/v1/seller/onboard/seller/verify` | 微前端,财务bundle | `VerifyOnboardSellerInfo` |
| `POST` | `/api/v1/seller/onboard/seller_with_invitation_code/create` | 微前端,财务bundle | `CreateSellerWithInvitationCode` |
| `POST` | `/api/v1/seller/onboard/submit` | 微前端,财务bundle | `SubmitOnboardInfo` |
| `POST` | `/api/v1/seller/onboard/v1/address_validation` | 微前端,微前端,微前端,微前端,财务bundle | `ValidateAddress` |
| `POST` | `/api/v1/seller/onboard/v1/company_name/verify` | 微前端,微前端,微前端,微前端,财务bundle | `VerifyOnboardCompanyName` |
| `POST` | `/api/v1/seller/onboard/v1/company_trading_name/verify` | 微前端,微前端,财务bundle | `VerifyOnboardCompanyTradingName` |
| `GET` | `/api/v1/seller/onboard/v1/config_aggr/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetOnboardConfigAggr` |
| `POST` | `/api/v1/seller/onboard/v1/contact/verify` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `VerifyOnboardContact` |
| `GET` | `/api/v1/seller/onboard/v1/cross_border/config/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderOnboardConfig` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveCrossBorderOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/entity/get` | 微前端,微前端,财务bundle | `GetCrossBorderEntity` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/entity_number/verify` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `VerifyCrossBorderEntityNumber` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/experienced_platform/verify` | 微前端,微前端,微前端,微前端,财务bundle | `VerifyCrossBorderExperiencedPlatform` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/global_seller/create` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `CreateCrossBorderGlobalSeller` |
| `GET` | `/api/v1/seller/onboard/v1/cross_border/onboard/route/get` | 微前端,财务bundle | `GetCrossBorderOnboardRoute` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/onboard/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderOnboardState` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/open_shop/draft/get` | 微前端,财务bundle | `GetCrossBorderOpenShopDraft` |
| `GET` | `/api/v1/seller/onboard/v1/cross_border/open_shop/route/get` | 微前端,财务bundle | `GetCrossBorderOpenShopRoute` |
| `GET` | `/api/v1/seller/onboard/v1/cross_border/open_shop/states/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderOpenShopStates` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/shop/open` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitOpenShopCrossBorder` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/shop/pre_check` | 微前端,微前端,微前端,财务bundle | `PreCheckCrossBorderOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitCrossBorderOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/ubo/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitCrossBorderUBO` |
| `POST` | `/api/v1/seller/onboard/v1/cross_border/ubo_check/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCrossBorderUBOCheckState` |
| `POST` | `/api/v1/seller/onboard/v1/docusign/envelope/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetDocusignEnvelope` |
| `POST` | `/api/v1/seller/onboard/v1/docusign/envelope/send` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SendDocusignEnvelope` |
| `POST` | `/api/v1/seller/onboard/v1/docusign_callback` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `DocusignCallback` |
| `POST` | `/api/v1/seller/onboard/v1/entity_number/verify` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `VerifyEntityNumber` |
| `POST` | `/api/v1/seller/onboard/v1/faqs/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetOnboardFAQs` |
| `POST` | `/api/v1/seller/onboard/v1/feature_tag/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetFeatureTag` |
| `POST` | `/api/v1/seller/onboard/v1/invitation_code/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitInvitationCode` |
| `POST` | `/api/v1/seller/onboard/v1/invitation_code_tag/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetInvitationCodeTag` |
| `POST` | `/api/v1/seller/onboard/v1/jumio/ocr` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `JumioOcr` |
| `GET` | `/api/v1/seller/onboard/v1/jumio_config/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetJumioConfig` |
| `POST` | `/api/v1/seller/onboard/v1/jumio_link/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetJumioLink` |
| `POST` | `/api/v1/seller/onboard/v1/local/br/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalBROnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/br/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalBROnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/br/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalBROnboard` |
| `GET` | `/api/v1/seller/onboard/v1/local/config/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalOnboardConfig` |
| `POST` | `/api/v1/seller/onboard/v1/local/es/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalESOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/es/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalESOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/es/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalESOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalIDOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalIDOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalIDOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalIDOnboard` |
| `GET` | `/api/v1/seller/onboard/v1/local/id/toko_fast_onboard/criteria/check` | 微前端,微前端,微前端,财务bundle | `TOKOFastOnboardingCriteriaPreCheck` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/toko_fast_onboard/start` | 微前端,微前端,微前端,微前端,财务bundle | `StartTOKOFastOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/toko_fast_onboard/submit` | 微前端,微前端,微前端,微前端,财务bundle | `SubmitTOKOFastOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/toko_fast_onboard/toko_data/prefill` | 微前端,微前端,微前端,财务bundle | `GetTOKOData` |
| `POST` | `/api/v1/seller/onboard/v1/local/irl/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalIRLOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/irl/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalIRLOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/irl/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalIRLOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/my/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalMYOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/my/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalMYOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/my/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalMYOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/my/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalMYOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/ph/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalPHOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/ph/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalPHOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/ph/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalPHOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/ph/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalPHOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/sandbox/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitSandboxLocalOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/sg/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalSGOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/sg/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalSGOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/sg/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalSGOnboard` |
| `GET` | `/api/v1/seller/onboard/v1/local/sg/singpass_info/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSingpassInfo` |
| `GET` | `/api/v1/seller/onboard/v1/local/sg/singpass_link/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSingpassLink` |
| `POST` | `/api/v1/seller/onboard/v1/local/sg/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalSGOnboard` |
| `GET` | `/api/v1/seller/onboard/v1/local/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalOnboardState` |
| `POST` | `/api/v1/seller/onboard/v1/local/th/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalTHOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/th/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalTHOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/th/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalTHOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/th/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalTHOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/uk/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUKOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/uk/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalUKOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/uk/full/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUKFullOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/uk/gray_tag/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUKOnboardGrayTag` |
| `POST` | `/api/v1/seller/onboard/v1/local/uk/staged/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUKStagedOnboard` |
| `GET` | `/api/v1/seller/onboard/v1/local/us/backfill/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUSOnboardBackFillState` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/backfill/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUSOnboardBackFill` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUSOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalUSOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/full_stage/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalUSFullStageOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/full_stage/extra/ubo/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSaveLocalUSOnboardUBOInfoDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/full_stage/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUSFullStageOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/overview/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUSOnboardOverView` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/post_onboard/extra_submit` | 微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalUSPostOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/post_onboard/state` | 微前端,微前端,微前端,财务bundle | `GetLocalUSPostOnboardState` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/post_onboard/submit` | 微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUSPostOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/raw_lead` | 微前端,微前端,微前端,微前端,财务bundle | `CreateRawLead` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/sandbox/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitSandboxLocalUSOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalUSOnboardState` |
| `POST` | `/api/v1/seller/onboard/v1/local/us/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalUSOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/vn/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocalVNOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/vn/draft/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveLocalVNOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v1/local/vn/extra/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ExtraSubmitLocalVNOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/local/vn/submit` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SubmitLocalVNOnboard` |
| `POST` | `/api/v1/seller/onboard/v1/register_create_seller` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `RegisterCreateSeller` |
| `POST` | `/api/v1/seller/onboard/v1/shop_name/verify` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `VerifyOnboardShopName` |
| `POST` | `/api/v1/seller/onboard/v2/additional_submit` | 微前端,微前端,财务bundle | `AdditionalSubmitOnboard` |
| `POST` | `/api/v1/seller/onboard/v2/address_validation` | 微前端,微前端,财务bundle | `ValidateAddress` |
| `GET` | `/api/v1/seller/onboard/v2/admission/check` | 财务bundle | `OnboardAdmissionCheck` |
| `GET` | `/api/v1/seller/onboard/v2/admission/get_info` | 财务bundle | `GetAdmissionInfo` |
| `POST` | `/api/v1/seller/onboard/v2/auth_token/gen` | 财务bundle | `GenAuthToken` |
| `POST` | `/api/v1/seller/onboard/v2/company_vat_number/verify` | 财务bundle | `VerifyCompanyVatNumber` |
| `POST` | `/api/v1/seller/onboard/v2/config/category/search` | 财务bundle | `SearchCategoryConfig` |
| `GET` | `/api/v1/seller/onboard/v2/config/get` | 微前端,微前端,财务bundle | `GetOnboardConfig` |
| `POST` | `/api/v1/seller/onboard/v2/control` | 财务bundle | `OnboardControl` |
| `POST` | `/api/v1/seller/onboard/v2/draft/get` | 微前端,微前端,财务bundle | `GetOnboardDraft` |
| `POST` | `/api/v1/seller/onboard/v2/draft/save` | 微前端,微前端,财务bundle | `SaveOnboardDraft` |
| `GET` | `/api/v1/seller/onboard/v2/entity_info/get` | 财务bundle | `GetGlobalSellerEntityInfo` |
| `POST` | `/api/v1/seller/onboard/v2/entity_info/verify` | 财务bundle | `VerifyEntityInfo` |
| `POST` | `/api/v1/seller/onboard/v2/entity_number/verify` | 微前端,微前端,财务bundle | `VerifyEntityNumber` |
| `POST` | `/api/v1/seller/onboard/v2/exemption/precheck` | 财务bundle | `OnboardExemptionPrecheck` |
| `POST` | `/api/v1/seller/onboard/v2/expansion/precheck` | 财务bundle | `ExpansionPreCheck` |
| `POST` | `/api/v1/seller/onboard/v2/faqs/get` | 微前端,微前端,财务bundle | `GetOnboardFAQs` |
| `POST` | `/api/v1/seller/onboard/v2/fe_config/get` | 微前端,微前端,财务bundle | `GetFEConfig` |
| `POST` | `/api/v1/seller/onboard/v2/fe_config/post` | 微前端,微前端,财务bundle | `PostFEConfig` |
| `POST` | `/api/v1/seller/onboard/v2/fe_pre_load_config/get` | 微前端,微前端,财务bundle | `GetFEPreLoadConfig` |
| `GET` | `/api/v1/seller/onboard/v2/file/download` | 财务bundle | `DownloadFile` |
| `POST` | `/api/v1/seller/onboard/v2/file/upload` | 财务bundle | `UploadFile` |
| `POST` | `/api/v1/seller/onboard/v2/global_seller_contact/verify` | 微前端,微前端,财务bundle | `VerifyGlobalSellerContact` |
| `POST` | `/api/v1/seller/onboard/v2/global_seller_name/verify` | 微前端,微前端,财务bundle | `VerifyGlobalSellerName` |
| `POST` | `/api/v1/seller/onboard/v2/invitation_code/check_invitation_code` | 财务bundle | `CheckInvitationCode` |
| `POST` | `/api/v1/seller/onboard/v2/invitation_code/check_invitation_uniform_code` | 财务bundle | `CheckInvitationUniformCode` |
| `POST` | `/api/v1/seller/onboard/v2/lark/callback` | 财务bundle | `LarkCallback` |
| `POST` | `/api/v1/seller/onboard/v2/lark/callback/strategy` | 财务bundle | `OnboardStrategyLarkCallback` |
| `POST` | `/api/v1/seller/onboard/v2/legal_entity_option/get` | 财务bundle | `GetLegalEntityOption` |
| `POST` | `/api/v1/seller/onboard/v2/precheck/kyb/query/by_global_seller` | 财务bundle | `QueryKYBValidationByGlobalSeller` |
| `POST` | `/api/v1/seller/onboard/v2/precheck/kyb/query/by_kyb` | 财务bundle | `QueryKYBValidationByInfo` |
| `POST` | `/api/v1/seller/onboard/v2/precheck/kyb/validate` | 财务bundle | `ValidateKYBInfo` |
| `POST` | `/api/v1/seller/onboard/v2/precheck/kyc/query/by_global_seller` | 财务bundle | `QueryKYCValidationByGlobalSeller` |
| `POST` | `/api/v1/seller/onboard/v2/precheck/kyc/validate` | 财务bundle | `ValidateKYCInfo` |
| `POST` | `/api/v1/seller/onboard/v2/register_create_global_seller` | 微前端,微前端,财务bundle | `RegisterCreateGlobalSeller` |
| `POST` | `/api/v1/seller/onboard/v2/rfc_number/verify` | 微前端,微前端,财务bundle | `VerifyRFCNumber` |
| `POST` | `/api/v1/seller/onboard/v2/sentry_list_profile/get` | 微前端,微前端,财务bundle | `GetSentryListProfile` |
| `POST` | `/api/v1/seller/onboard/v2/shop_contact/submit` | 微前端,微前端,财务bundle | `SubmitShopContact` |
| `POST` | `/api/v1/seller/onboard/v2/state/get` | 微前端,微前端,财务bundle | `GetOnboardState` |
| `GET` | `/api/v1/seller/onboard/v2/strategy/get` | 财务bundle | `GetOnboardStrategy` |
| `GET` | `/api/v1/seller/onboard/v2/sub_orders/get` | 财务bundle | `GetSubOrders` |
| `POST` | `/api/v1/seller/onboard/v2/submit` | 微前端,微前端,财务bundle | `SubmitOnboard` |
| `POST` | `/api/v1/seller/onboard/v2/terminate` | 财务bundle | `TerminateOnboard` |
| `POST` | `/api/v1/seller/onboard/vendor/contact/save` | 微前端 | `SaveVerifiedContact` |
| `POST` | `/api/v1/seller/onboard/vendor/contact_code/send` | 微前端 | `SendContactVerificationCode` |
| `POST` | `/api/v1/seller/onboard/vendor/info/get` | 微前端 | `GetOnboardVendorInfo` |
| `POST` | `/api/v1/seller/onboard/vendor/invitation_code/submit` | 微前端 | `SubmitOnboardInvitationCode` |
| `POST` | `/api/v1/seller/onboard/vendor/ocr` | 微前端 | `Ocr` |
| `?` | `/api/v1/seller/onboard/vendor/translation/translate` | 微前端 | `GetTranslation` |
| `POST` | `/api/v1/seller/profile/address_consent/set` | 微前端,财务bundle | `SetAddressConsent` |
| `POST` | `/api/v1/seller/profile/bound_contact/verify` | 微前端,财务bundle | `VerifyBoundContact` |
| `POST` | `/api/v1/seller/profile/bound_contact_email/update` | 微前端,财务bundle | `UpdateBoundContactEmail` |
| `?` | `/api/v1/seller/profile/config` | 微前端 | `GetSellerProfileConfig` |
| `POST` | `/api/v1/seller/profile/contact/get` | 微前端,财务bundle | `GetMaskedContactInfo` |
| `POST` | `/api/v1/seller/profile/contact_code/send` | 微前端,财务bundle | `SendContactVerificationCode` |
| `POST` | `/api/v1/seller/profile/contact_email_code/send` | 微前端,财务bundle | `SendContactEmailCode` |
| `POST` | `/api/v1/seller/profile/contact_v2/get` | 微前端,财务bundle | `GetSellerContactInfo` |
| `POST` | `/api/v1/seller/profile/whatsapp_number/update` | 微前端,财务bundle | `UpdateWhatsappNum` |
| `POST` | `/api/v1/usseller/onboard/v1/company_info/validate` | 微前端 | `ValidateCompanyNameAndAddress` |
| `?` | `/api/v1/usseller/onboard/v1/company_info/validate/counter` | 微前端 | `GetCompanyNameAndAddressValidateCounter` |
| `POST` | `/api/v1/usseller/onboard/v1/company_info/validate/query` | 微前端 | `GetCompanyNameAndAddressValidateResult` |
| `POST` | `/api/v1/usseller/onboard/v1/local/post_onboard/state` | 微前端 | `GetLocalPostOnboardState` |
| `POST` | `/api/v1/usseller/onboard/v1/local/post_onboard/submit` | 微前端 | `SubmitLocalPostOnboard` |
| `POST` | `/api/v1/usseller/onboard/v1/local/us/landing_page/seller_info` | 微前端 | `SaveLandingPageSellerInfo` |
| `POST` | `/api/v1/usseller/onboard/v1/local/us/raw_lead` | 微前端 | `CreateRawLead` |
| `POST` | `/api/v1/usseller/onboard/v1/registration_channel` | 微前端 | `QueryGlobalSellerRegistrationChannel` |
| `POST` | `/api/v2/seller/onboard/v2/file/upload` | 微前端,财务bundle |  |
| `POST` | `/passport/web/account/verify` | 微前端,微前端 |  |
| `POST` | `/widget/api/v1/seller/entity/file/upload` | 微前端,财务bundle | `WidgetUploadFile` |
| `POST` | `/widget/api/v1/seller/entity/file_url/get` | 微前端,财务bundle | `WidgetGetFileURL` |
| `POST` | `/widget/api/v1/seller/entity/v2/change` | 财务bundle | `WidgetSubmitEntityChange` |
| `POST` | `/widget/api/v1/seller/entity/v2/get` | 财务bundle | `WidgetGetEntityInfo` |
| `POST` | `/widget/api/v1/seller/entity/v2/pipo/kyb/submit` | 财务bundle | `WidgetSubmitEntityPIPOKyb` |
| `POST` | `/widget/api/v1/seller/entity/v2/task/complete` | 财务bundle | `WidgetCompleteEntityTask` |
| `POST` | `/widget/api/v1/seller/entity/v2/task/detail` | 财务bundle | `WidgetGetEntityTaskDetail` |
| `POST` | `/widget/api/v1/seller/entity/v2/task/list` | 财务bundle | `WidgetGetEntityTaskList` |
| `POST` | `/widget/api/v1/seller/entity/v2/task/submit` | 财务bundle | `WidgetSubmitEntityTask` |
| `POST` | `/widget/api/v1/seller/entity/v2/update` | 财务bundle | `WidgetSubmitEntityUpdate` |
| `POST` | `/widget/api/v1/seller/join/ocr` | 微前端,财务bundle | `WidgetOcr` |
| `POST` | `/widget/api/v1/seller/onboard/v1/address_validation` | 微前端,微前端,微前端,财务bundle | `WidgetValidateAddress` |
| `POST` | `/widget/api/v1/seller/onboard/v1/company_trading_name/verify` | 微前端,财务bundle | `WidgetVerifyOnboardCompanyTradingName` |
| `GET` | `/widget/api/v1/seller/onboard/v1/config_aggr/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetOnboardConfigAggr` |
| `POST` | `/widget/api/v1/seller/onboard/v1/contact/verify` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetVerifyOnboardContact` |
| `POST` | `/widget/api/v1/seller/onboard/v1/cross_border/experienced_platform/verify` | 微前端,微前端,财务bundle | `WidgetVerifyCrossBorderExperiencedPlatform` |
| `POST` | `/widget/api/v1/seller/onboard/v1/docusign/envelope/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetDocusignEnvelope` |
| `POST` | `/widget/api/v1/seller/onboard/v1/docusign/envelope/send` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSendDocusignEnvelope` |
| `POST` | `/widget/api/v1/seller/onboard/v1/entity_number/verify` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetVerifyEntityNumber` |
| `POST` | `/widget/api/v1/seller/onboard/v1/faqs/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetOnboardFAQs` |
| `POST` | `/widget/api/v1/seller/onboard/v1/feature_tag/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetFeatureTag` |
| `POST` | `/widget/api/v1/seller/onboard/v1/jumio/ocr` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetJumioOcr` |
| `GET` | `/widget/api/v1/seller/onboard/v1/jumio_config/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetJumioConfig` |
| `POST` | `/widget/api/v1/seller/onboard/v1/jumio_link/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetJumioLink` |
| `GET` | `/widget/api/v1/seller/onboard/v1/local/config/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalOnboardConfig` |
| `GET` | `/widget/api/v1/seller/onboard/v1/local/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalOnboardState` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/uk/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalUKOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/uk/draft/save` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSaveLocalUKOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/uk/full/submit` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSubmitLocalUKFullOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/uk/gray_tag/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalUKOnboardGrayTag` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/uk/staged/submit` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSubmitLocalUKStagedOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/draft/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalUSOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/draft/save` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSaveLocalUSOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/full_stage/extra/submit` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetExtraSubmitLocalUSFullStageOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/full_stage/extra/ubo/draft/save` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetExtraSaveLocalUSOnboardUBOInfoDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/full_stage/submit` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetSubmitLocalUSFullStageOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/overview/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalUSOnboardOverView` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/post_onboard/extra_submit` | 微前端,微前端,微前端,财务bundle | `WidgetExtraSubmitLocalUSPostOnboard` |
| `GET` | `/widget/api/v1/seller/onboard/v1/local/us/post_onboard/state` | 微前端,微前端,微前端,财务bundle | `WidgetGetLocalUSPostOnboardState` |
| `POST` | `/widget/api/v1/seller/onboard/v1/local/us/post_onboard/submit` | 微前端,微前端,微前端,财务bundle | `WidgetSubmitLocalUSPostOnboard` |
| `GET` | `/widget/api/v1/seller/onboard/v1/local/us/state/get` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetGetLocalUSOnboardState` |
| `POST` | `/widget/api/v1/seller/onboard/v1/register_create_seller` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetRegisterCreateSeller` |
| `POST` | `/widget/api/v1/seller/onboard/v1/shop_name/verify` | 微前端,微前端,微前端,微前端,财务bundle | `WidgetVerifyOnboardShopName` |
| `POST` | `/widget/api/v1/seller/onboard/v2/additional_submit` | 微前端,微前端,财务bundle | `WidgetAdditionalSubmitOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/v2/address_validation` | 微前端,微前端,财务bundle | `WidgetValidateAddress` |
| `POST` | `/widget/api/v1/seller/onboard/v2/company_vat_number/verify` | 财务bundle | `WidgetVerifyCompanyNumber` |
| `POST` | `/widget/api/v1/seller/onboard/v2/config/category/search` | 财务bundle | `WidgetSearchCategoryConfig` |
| `GET` | `/widget/api/v1/seller/onboard/v2/config/get` | 微前端,微前端,财务bundle | `WidgetGetOnboardConfig` |
| `POST` | `/widget/api/v1/seller/onboard/v2/control` | 财务bundle | `WidgetOnboardControl` |
| `POST` | `/widget/api/v1/seller/onboard/v2/draft/get` | 微前端,微前端,财务bundle | `WidgetGetOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v2/draft/save` | 微前端,微前端,财务bundle | `WidgetSaveOnboardDraft` |
| `POST` | `/widget/api/v1/seller/onboard/v2/entity_info/verify` | 财务bundle | `WidgetVerifyEntityInfo` |
| `POST` | `/widget/api/v1/seller/onboard/v2/entity_number/verify` | 微前端,微前端,财务bundle | `WidgetVerifyEntityNumber` |
| `POST` | `/widget/api/v1/seller/onboard/v2/faqs/get` | 微前端,微前端,财务bundle | `WidgetGetOnboardFAQs` |
| `POST` | `/widget/api/v1/seller/onboard/v2/fe_config/get` | 微前端,微前端,财务bundle | `WidgetGetFEConfig` |
| `GET` | `/widget/api/v1/seller/onboard/v2/file/download` | 财务bundle | `WidgetDownloadFile` |
| `POST` | `/widget/api/v1/seller/onboard/v2/file/upload` | 财务bundle | `WidgetUploadFile` |
| `POST` | `/widget/api/v1/seller/onboard/v2/global_seller_contact/verify` | 微前端,微前端,财务bundle | `WidgetVerifyGlobalSellerContact` |
| `POST` | `/widget/api/v1/seller/onboard/v2/global_seller_name/verify` | 微前端,微前端,财务bundle | `WidgetVerifyGlobalSellerName` |
| `POST` | `/widget/api/v1/seller/onboard/v2/invitation_code/check_invitation_code` | 财务bundle | `WidgetCheckInvitationCode` |
| `POST` | `/widget/api/v1/seller/onboard/v2/invitation_code/check_invitation_uniform_code` | 财务bundle | `WidgetCheckInvitationUniformCode` |
| `POST` | `/widget/api/v1/seller/onboard/v2/precheck/kyb/query/by_global_seller` | 财务bundle | `WidgetQueryKYBValidationByGlobalSeller` |
| `POST` | `/widget/api/v1/seller/onboard/v2/precheck/kyb/query/by_kyb` | 财务bundle | `WidgetQueryKYBValidationByInfo` |
| `POST` | `/widget/api/v1/seller/onboard/v2/precheck/kyb/validate` | 财务bundle | `WidgetValidateKYBInfo` |
| `POST` | `/widget/api/v1/seller/onboard/v2/precheck/kyc/query/by_global_seller` | 财务bundle | `WidgetQueryKYCValidationByGlobalSeller` |
| `POST` | `/widget/api/v1/seller/onboard/v2/precheck/kyc/validate` | 财务bundle | `WidgetValidateKYCInfo` |
| `POST` | `/widget/api/v1/seller/onboard/v2/register_create_global_seller` | 微前端,微前端,财务bundle | `WidgetRegisterCreateGlobalSeller` |
| `POST` | `/widget/api/v1/seller/onboard/v2/rfc_number/verify` | 微前端,微前端,财务bundle | `WidgetVerifyRFCNumber` |
| `POST` | `/widget/api/v1/seller/onboard/v2/sentry_list_profile/get` | 微前端,微前端,财务bundle | `WidgetGetSentryListProfile` |
| `POST` | `/widget/api/v1/seller/onboard/v2/shop_contact/submit` | 微前端,微前端,财务bundle | `WidgetSubmitShopContact` |
| `GET` | `/widget/api/v1/seller/onboard/v2/state/get` | 微前端,微前端,财务bundle | `WidgetGetOnboardState` |
| `POST` | `/widget/api/v1/seller/onboard/v2/strategy/get` | 财务bundle | `WidgetGetOnboardStrategy` |
| `POST` | `/widget/api/v1/seller/onboard/v2/submit` | 微前端,微前端,财务bundle | `WidgetSubmitOnboard` |
| `POST` | `/widget/api/v1/seller/onboard/vendor/contact/save` | 微前端 | `WidgetSaveVerifiedContact` |
| `POST` | `/widget/api/v1/seller/onboard/vendor/contact_code/send` | 微前端 | `WidgetSendContactVerificationCode` |
| `POST` | `/widget/api/v1/seller/onboard/vendor/info/get` | 微前端 | `WidgetGetOnboardVendorInfo` |
| `POST` | `/widget/api/v1/seller/onboard/vendor/invitation_code/submit` | 微前端 | `WidgetSubmitOnboardInvitationCode` |
| `POST` | `/widget/api/v1/seller/profile/contact_code/send` | 微前端,财务bundle | `WidgetSendContactVerificationCode` |
| `POST` | `/widget/api/v1/usseller/onboard/v1/company_info/validate` | 微前端 | `WidgetValidateCompanyNameAndAddress` |
| `?` | `/widget/api/v1/usseller/onboard/v1/company_info/validate/counter` | 微前端 | `WidgetGetCompanyNameAndAddressValidateCounter` |
| `POST` | `/widget/api/v1/usseller/onboard/v1/company_info/validate/query` | 微前端 | `WidgetGetCompanyNameAndAddressValidateResult` |
| `POST` | `/widget/api/v1/usseller/onboard/v1/registration_channel` | 微前端 | `WidgetQueryGlobalSellerRegistrationChannel` |

## 店铺运营 / 工作台（89）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/cb/seller/tasks/exposed/save` | 微前端 | `SaveExposedTask` |
| `GET` | `/api/v1/cb/seller/tasks/island/get` | 微前端 | `GetIslandTaskList` |
| `POST` | `/api/v1/cb/seller/tasks/overview/get` | 微前端 | `OverviewSellerTask` |
| `GET` | `/api/v1/cb/seller/tasks/peaks/get` | 微前端 | `PeaksSellerTask` |
| `GET` | `/api/v1/cb/seller/tasks/sections/get_all` | 微前端 | `GetCBSectionsTaskList` |
| `GET` | `/api/v1/cb/seller/tasks/step/get_all` | 微前端 | `GetCBStepTaskList` |
| `POST` | `/api/v1/pop/product/optimize/data/homepage/get` | 微前端 | `GetHomePageOptimizationDataCard` |
| `GET` | `/api/v1/seller/badge/is_read/get` | 微前端,微前端,微前端,微前端,财务bundle | `CheckSingleBadgeIsRead` |
| `POST` | `/api/v1/seller/badge/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `UpdateBadgeStatus` |
| `POST` | `/api/v1/seller/home/fs/get_assess_personas` | 微前端,微前端,微前端,微前端,财务bundle | `FsAssessPersonasCard` |
| `POST` | `/api/v1/seller/home/fs/get_must_read_list` | 微前端,微前端,微前端,财务bundle | `GetMustReadList` |
| `POST` | `/api/v1/seller/home/fs/get_todo_list` | 微前端,微前端,微前端,微前端,财务bundle | `FsTodoCardData` |
| `POST` | `/api/v1/seller/home/get_activity_marketing` | 微前端,微前端,微前端,微前端,财务bundle | `MarketingCard` |
| `POST` | `/api/v1/seller/home/get_assess_personas` | 微前端,微前端,微前端,微前端,财务bundle | `AssessPersonasCard` |
| `POST` | `/api/v1/seller/home/get_clue_card` | 微前端,微前端,微前端,微前端,财务bundle | `ClueCard` |
| `POST` | `/api/v1/seller/home/get_supplier_guidance` | 微前端,微前端,微前端,微前端,财务bundle | `SupplierGuidanceCard` |
| `POST` | `/api/v1/seller/home/get_task_card` | 微前端,微前端,微前端,微前端,财务bundle | `ListSupplierTask` |
| `POST` | `/api/v1/seller/home/get_todo_list` | 微前端,微前端,微前端,微前端,财务bundle | `TodoCardData` |
| `GET` | `/api/v1/seller/home_card/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetHomeCard` |
| `POST` | `/api/v1/seller/home_stage/get` | 微前端,微前端,微前端,微前端,财务bundle | `CheckLifeStage` |
| `GET` | `/api/v1/seller/home_task/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetHomeTask` |
| `?` | `/api/v1/seller/homepage/get` | 微前端,微前端 | `AwemeGetHomepage` |
| `GET` | `/api/v1/seller/homepage_allowlist/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetHomePageAllowList` |
| `POST` | `/api/v1/seller/homepage_widgets_group/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetHomepageWidgetsGroup` |
| `GET` | `/api/v1/seller/live_center/homepage/get` | 微前端 | `GetLiveHomepage` |
| `GET` | `/api/v1/seller/live_center/homepage_module/get` | 微前端 | `AwemeGetLiveHomepageModule` |
| `GET` | `/api/v1/seller/live_center/v2/homepage/get` | 微前端 | `GetLiveHomepageV2` |
| `GET` | `/api/v1/seller/livecenter/homepage/get` | 微前端 | `GetHomePage` |
| `GET` | `/api/v1/seller/menu/badge/get` | 微前端,微前端,微前端,财务bundle | `GetBadge` |
| `POST` | `/api/v1/seller/menu/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetMenu` |
| `POST` | `/api/v1/seller/menu/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SetMenu` |
| `POST` | `/api/v1/seller/menu/switch` | 微前端,微前端,微前端,微前端,财务bundle | `SwitchMenu` |
| `POST` | `/api/v1/seller/popup/get_popup_list` | 微前端,微前端,微前端,微前端,财务bundle | `GetPopupLists` |
| `POST` | `/api/v1/seller/popup/list` | 微前端 | `ListPopupMessage` |
| `POST` | `/api/v1/seller/popup/popup_callback` | 微前端,微前端,微前端,微前端,财务bundle | `PopupCallback` |
| `?` | `/api/v1/seller/tasks/banner` | 微前端,微前端 | `GetMissionBanner` |
| `POST` | `/api/v1/seller/tasks/batch_claim_reward` | 早期 |  |
| `?` | `/api/v1/seller/tasks/claim_reward` | 微前端,微前端 | `ClaimTaskReward` |
| `?` | `/api/v1/seller/tasks/claim_reward_v2` | 微前端,微前端 | `ClaimTaskRewardV2` |
| `POST` | `/api/v1/seller/tasks/claim_reward_v3` | 早期 |  |
| `?` | `/api/v1/seller/tasks/config/get` | 微前端,微前端 | `GetTaskConfig` |
| `POST` | `/api/v1/seller/tasks/create_store_wide_free_shipping` | 早期 |  |
| `POST` | `/api/v1/seller/tasks/event/post` | 微前端,微前端,早期 | `PostEvent` |
| `?` | `/api/v1/seller/tasks/get_all` | 微前端,微前端 | `GetAllTask` |
| `?` | `/api/v1/seller/tasks/growth/modal` | 微前端,微前端 | `GetGrowthModal` |
| `POST` | `/api/v1/seller/tasks/join` | 微前端,微前端,早期 | `JoinSellerTask` |
| `?` | `/api/v1/seller/tasks/list` | 微前端,微前端 | `ListSellerTask` |
| `?` | `/api/v1/seller/tasks/mission/detail/get` | 微前端,微前端 | `TaskDetail` |
| `?` | `/api/v1/seller/tasks/missions/center/get` | 微前端,微前端 | `AppMissionCenter` |
| `?` | `/api/v1/seller/tasks/notify` | 微前端,微前端 | `GetMissionNotify` |
| `GET` | `/api/v1/seller/tasks/overview` | 微前端,微前端,早期 | `GetOverviewTask` |
| `POST` | `/api/v1/seller/tasks/overview/get` | 微前端,微前端 | `OverviewSellerTask` |
| `GET` | `/api/v1/seller/tasks/popup_task/auto_popup` | 微前端,微前端,早期 | `AutoPopupControl` |
| `GET` | `/api/v1/seller/tasks/popup_task/entry/get` | 微前端,微前端,早期 | `GetSellerPopupTaskEntry` |
| `POST` | `/api/v1/seller/tasks/popup_task/get` | 微前端,微前端 | `GetSellerPopupTask` |
| `POST` | `/api/v1/seller/tasks/popup_task/join` | 微前端,微前端,早期 | `JoinSellerPopupTask` |
| `?` | `/api/v1/seller/tasks/program/get` | 微前端,微前端 | `GetSellerProgram` |
| `?` | `/api/v1/seller/tasks/program/stage/unlock` | 微前端,微前端 | `UnlockSellerProgramStage` |
| `POST` | `/api/v1/seller/tasks/reward_history` | 微前端,微前端,早期 | `GetTaskRewardHistory` |
| `?` | `/api/v1/seller/tasks/step/get_all` | 微前端,微前端 | `GetStepTaskList` |
| `?` | `/api/v1/seller/tasks/step/get_all_v2` | 微前端,微前端 | `GetStepTaskV2List` |
| `?` | `/api/v1/seller/tasks/step/get_all_v3` | 微前端,微前端 | `GetStepTaskV3List` |
| `?` | `/api/v1/seller/tasks/step/get_all_v4` | 微前端,微前端 | `GetStepTaskV4List` |
| `POST` | `/api/v1/seller/tasks/step/get_all_v5` | 微前端,微前端 | `GetStepTaskV5List` |
| `GET` | `/api/v1/seller/tasks/step/recommend/get` | 早期 |  |
| `GET` | `/api/v1/seller/tasks/step/showcase` | 微前端,微前端,早期 | `GetStepTaskShowCase` |
| `POST` | `/api/v1/seller/tasks/step/skip/mission` | 微前端,微前端,早期 | `SkipStartMission` |
| `POST` | `/api/v1/seller/tasks/update_progress` | 微前端,微前端,早期 | `UpdateProgress` |
| `GET` | `/api/v1/seller/video_center/app/homepage/get` | 微前端 | `GetAppVideoHomepage` |
| `GET` | `/api/v1/seller/video_center/homepage/get` | 微前端 | `GetVideoHomepage` |
| `GET` | `/api/v1/seller/video_center/homepage_module/get` | 微前端 | `AwemeGetVideoHomepageModule` |
| `GET` | `/api/v1/seller/workbench/base_info` | 财务bundle |  |
| `POST` | `/api/v1/seller/workbench/get_all_sellers` | 微前端,微前端,微前端,微前端,财务bundle | `GetAllSellers` |
| `POST` | `/api/v1/seller/workbench/outreach/callback` | 微前端,微前端,财务bundle | `OutreachCallBack` |
| `POST` | `/api/v1/webapp/seller/menu/get` | 微前端,微前端,微前端,财务bundle | `GetMenuWebApp` |
| `POST` | `/aweme/api/v1/seller/tasks/claim_reward` | 早期 |  |
| `POST` | `/aweme/api/v1/seller/tasks/claim_reward_v2` | 早期 |  |
| `POST` | `/aweme/api/v1/seller/tasks/join` | 早期 |  |
| `GET` | `/aweme/api/v1/seller/tasks/list` | 早期 |  |
| `POST` | `/aweme/api/v1/seller/tasks/update_progress` | 早期 |  |
| `POST` | `/widget/api/v1/seller/badge/set` | 微前端,微前端,微前端,微前端,财务bundle | `UpdateBadgeStatusForWidget` |
| `POST` | `/widget/api/v1/seller/tasks/claim_reward_v2` | 微前端,微前端 | `WidgetClaimTaskRewardV2` |
| `POST` | `/widget/api/v1/seller/tasks/event/post` | 微前端,微前端,早期 | `WidgetPostEvent` |
| `?` | `/widget/api/v1/seller/tasks/growth/modal` | 微前端,微前端 | `WidgetGetGrowthModal` |
| `POST` | `/widget/api/v1/seller/tasks/join` | 微前端,微前端,早期 | `WidgetJoinSellerTask` |
| `?` | `/widget/api/v1/seller/tasks/notify` | 微前端,微前端 | `WidgetGetMissionNotify` |
| `?` | `/widget/api/v1/seller/tasks/program/stage/unlock` | 微前端,微前端 | `WidgetUnlockSellerProgramStage` |
| `POST` | `/widget/api/v1/seller/tasks/update_progress` | 微前端,微前端,早期 | `WidgetUpdateProgress` |
| `GET` | `/widget/api/v1/seller/video_center/homepage/get` | 微前端 | `WidgetGetVideoHomepage` |

## 私域 / 粉丝 / 会员（2）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/aff/member/switch` | 微前端 |  |
| `POST` | `/passport/aff/mobile/member/switch` | 微前端 |  |

## 账号安全 / 通行证（25）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/v1/login` | 微前端 |  |
| `POST` | `/passport/auth/bind_with_mobile_login` | 微前端 |  |
| `POST` | `/passport/auth/login` | 微前端 |  |
| `GET` | `/passport/common/register/web/bind_verify_info` | 微前端 |  |
| `POST` | `/passport/mobile/check_code` | 微前端 |  |
| `POST` | `/passport/mobile/send_code` | 微前端 |  |
| `POST` | `/passport/mobile/unbind_limited_unusable_mobile` | 微前端 |  |
| `POST` | `/passport/pin/check` | 微前端 |  |
| `POST` | `/passport/pin/reset_by_ticket` | 微前端 |  |
| `POST` | `/passport/pin/set` | 微前端 |  |
| `POST` | `/passport/pin/verify` | 微前端 |  |
| `POST` | `/passport/safe/two_step_verification/add_auth_device` | 微前端 |  |
| `POST` | `/passport/safe/two_step_verification/add_verification` | 微前端 |  |
| `POST` | `/passport/safe/two_step_verification/remove_auth_device` | 微前端 |  |
| `POST` | `/passport/safe/two_step_verification/remove_verification` | 微前端 |  |
| `POST` | `/passport/web/email/check_code` | 微前端 |  |
| `POST` | `/passport/web/email/send_code` | 微前端 |  |
| `POST` | `/passport/web/email/verify` | 微前端 |  |
| `POST` | `/passport/web/login_by_ticket` | 微前端 |  |
| `POST` | `/passport/web/mobile/check_code` | 微前端 |  |
| `POST` | `/passport/web/oidc/callback` | 微前端 |  |
| `POST` | `/passport/web/send_code` | 微前端 |  |
| `POST` | `/passport/web/totp/register` | 微前端 |  |
| `POST` | `/passport/web/totp/unregister` | 微前端 |  |
| `POST` | `/passport/web/totp/verify` | 微前端 |  |

## 客服消息 / 站内信（18）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/proxy/seller/helpdesk/entrance/get` | 微前端,微前端 | `GetByEntrance` |
| `GET` | `/api/v1/proxy/seller/helpdesk/unread_msg/get` | 微前端,微前端 | `GetUserUnreadMsg` |
| `POST` | `/api/v1/proxy/seller/helpdesk/user/get` | 微前端,微前端 | `GenIMUser` |
| `POST` | `/api/v1/seller/gs_message/batch_mark_read_user_message` | 微前端,微前端,微前端,财务bundle | `BatchMarkReadUserMessage` |
| `POST` | `/api/v1/seller/gs_message/check_new_message` | 微前端,微前端,微前端,微前端,财务bundle | `CheckNewPlatformMessage` |
| `POST` | `/api/v1/seller/gs_message/get_merchant_headlines` | 微前端,微前端,微前端,财务bundle | `GetMerchantHeadlines` |
| `POST` | `/api/v1/seller/gs_message/get_merchant_headlines_config` | 微前端,微前端,微前端,财务bundle | `GetMerchantHeadlinesConfig` |
| `POST` | `/api/v1/seller/gs_message/get_user_message_statistic` | 微前端,微前端,微前端,微前端,财务bundle | `GetUserMessageStatistics` |
| `POST` | `/api/v1/seller/gs_message/mark_read_user_message` | 微前端,微前端,微前端,微前端,财务bundle | `MarkReadUserMessage` |
| `POST` | `/api/v1/seller/gs_message/mark_remind_user_message` | 微前端,微前端,微前端,微前端,财务bundle | `MarkRemindUserMessage` |
| `POST` | `/api/v1/seller/gs_message/user_message_detail` | 微前端,微前端,微前端,微前端,财务bundle | `GetUserMessageDetail` |
| `POST` | `/api/v1/seller/gs_message/user_message_list` | 微前端,微前端,微前端,微前端,财务bundle | `GetUserMessageList` |
| `GET` | `/api/v1/seller/msg_card/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetMsgCard` |
| `GET` | `/api/v1/seller/msg_card/set` | 微前端,微前端,微前端,微前端,财务bundle | `SetMsgCard` |
| `GET` | `/api/v1/sellerassistant/discover_chatbotevent` | 微前端 | `DiscoverChatbotEvent` |
| `GET` | `/api/v1/sellerassistant/discover_sst` | 微前端 | `DiscoverSST` |
| `POST` | `/api/v1/sellerassistant/event_status/set` | 微前端 | `SetEventStatus` |
| `POST` | `/api/v1/sellerassistant/sst/dismiss` | 微前端 | `DismissSST` |

## 直播 / 达人运营（27）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/v1/seller/creator/agg/get` | 微前端,微前端 | `GetAppShopCreator` |
| `POST` | `/api/v1/seller/creator/agg/verify/invite` | 微前端,微前端 | `VerifyAndInviteCreator` |
| `POST` | `/api/v1/seller/creator/availability/verify` | 微前端,微前端 | `VerifyCreatorAvailability` |
| `?` | `/api/v1/seller/creator/get` | 微前端,微前端 | `GetShopCreators` |
| `POST` | `/api/v1/seller/creator/info/get` | 微前端,微前端 | `GetShopCreatorInfo` |
| `POST` | `/api/v1/seller/creator/info/verify` | 微前端,微前端 | `VerifyCreatorInfo` |
| `POST` | `/api/v1/seller/creator/invitation/send` | 微前端,微前端 | `SendShopCreatorInvitation` |
| `POST` | `/api/v1/seller/creator/official_creator/bind` | 微前端,微前端 | `BindOfficialShopCreator` |
| `POST` | `/api/v1/seller/creator/official_creator/get` | 微前端,微前端 | `GetOfficialShopCreator` |
| `POST` | `/api/v1/seller/creator/official_creator/upgrade` | 微前端,微前端 | `UpgradeOfficialShopCreator` |
| `POST` | `/api/v1/seller/creator/qrcode/check` | 微前端,微前端 | `CheckQRCodeStatus` |
| `POST` | `/api/v1/seller/creator/remain/get` | 微前端,微前端 | `GetShopCreatorRoleRemainCondition` |
| `POST` | `/api/v1/seller/creator/unbind` | 微前端,微前端 | `UnbindShopCreator` |
| `POST` | `/api/v1/seller/creator/unbind_apply/get` | 微前端,微前端 | `GetUnbindApply` |
| `POST` | `/api/v1/seller/creator/unbind_apply/update` | 微前端,微前端 | `UpdateUnbindApply` |
| `POST` | `/api/v1/seller/live_center/event/post` | 微前端 | `PostLiveEvent` |
| `GET` | `/api/v1/seller/live_center/inspiration/get` | 微前端 | `GetLiveInspiration` |
| `GET` | `/api/v1/seller/live_center/live_base_info/get` | 微前端 | `GetSellerLiveBaseInfo` |
| `POST` | `/api/v1/seller/live_center/live_product/add` | 微前端 | `AddLiveProducts` |
| `POST` | `/api/v1/seller/live_center/live_product/delete` | 微前端 | `DelLiveProducts` |
| `GET` | `/api/v1/seller/live_center/live_product/get` | 微前端 | `GetLiveProducts` |
| `GET` | `/api/v1/seller/live_center/modal/get` | 微前端 | `GetLiveModal` |
| `POST` | `/api/v1/seller/live_center/product/search` | 微前端 | `SearchProductForLive` |
| `GET` | `/api/v1/seller/live_center/scripts/get` | 微前端 | `GetVideoScripts` |
| `POST` | `/api/v1/seller/live_center/tips/get` | 微前端 | `GetLiveTips` |
| `GET` | `/api/v1/seller/live_center/tips/options/get` | 微前端 | `GetLiveTipOptions` |
| `POST` | `/api/v1/seller/official_creator_contract/set` | 微前端,微前端,微前端,财务bundle | `SetOfficialCreatorContract` |

## 学习中心 / 内容（84）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/seller/creativityhub/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetSellerCreativityHubInfo` |
| `GET` | `/api/v1/seller/edu_comp/academy/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetEduCompAcademy` |
| `GET` | `/api/v1/seller/edu_comp/faq/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetEduCompFAQ` |
| `?` | `/api/v1/seller/learning_center/banner/get` | 微前端 | `GetBanner` |
| `?` | `/api/v1/seller/learning_center/banner/v2/get` | 微前端 | `GetBannerV2` |
| `?` | `/api/v1/seller/learning_center/contents/get` | 微前端 | `GetContentsTree` |
| `?` | `/api/v1/seller/learning_center/contents/list` | 微前端 | `ListContents` |
| `?` | `/api/v1/seller/learning_center/course_detail/get` | 微前端 | `GetCourseDetail` |
| `?` | `/api/v1/seller/learning_center/courses/list` | 微前端 | `ListCourses` |
| `?` | `/api/v1/seller/learning_center/creator/get` | 微前端 | `GetCreator` |
| `POST` | `/api/v1/seller/learning_center/feedback/create` | 微前端 | `CreateUserCommentFeedback` |
| `?` | `/api/v1/seller/learning_center/h5/home/get` | 微前端 | `GetH5Home` |
| `POST` | `/api/v1/seller/learning_center/home/explore/get` | 微前端 | `GetExplore` |
| `?` | `/api/v1/seller/learning_center/home/faq/get` | 微前端 | `GetHomeFaq` |
| `?` | `/api/v1/seller/learning_center/home/growth/get` | 微前端 | `GetHomeGrowth` |
| `GET` | `/api/v1/seller/learning_center/id/get` | 微前端 | `GetLearningCenterId` |
| `?` | `/api/v1/seller/learning_center/knowledge/list` | 微前端 | `ListKnowledge` |
| `?` | `/api/v1/seller/learning_center/knowledge_detail/get` | 微前端 | `GetKnowledgeDetail` |
| `?` | `/api/v1/seller/learning_center/knowledge_detail/simple/get` | 微前端 | `GetKnowledgeDetailSimple` |
| `?` | `/api/v1/seller/learning_center/module/contents/list` | 微前端 | `ListModuleContents` |
| `?` | `/api/v1/seller/learning_center/modules/get` | 微前端 | `GetModules` |
| `?` | `/api/v1/seller/learning_center/obj_detail/get` | 微前端 | `GetObjDetail` |
| `?` | `/api/v1/seller/learning_center/policy/courses/get` | 微前端 | `GetPolicyCourses` |
| `?` | `/api/v1/seller/learning_center/policy/latest/get` | 微前端 | `GetLatestPolicy` |
| `?` | `/api/v1/seller/learning_center/policy/notice/get` | 微前端 | `GetPolicyNotice` |
| `GET` | `/api/v1/seller/learning_center/recommend/content/list` | 微前端 | `ListRecommendContent` |
| `GET` | `/api/v1/seller/learning_center/recommend_reads/get` | 微前端 | `AcademyRecommendReads` |
| `GET` | `/api/v1/seller/learning_center/recommend_reads_default/get` | 微前端 | `AcademyRecommendReadsDefault` |
| `POST` | `/api/v1/seller/learning_center/search` | 微前端 | `SearchByKeyword` |
| `GET` | `/api/v1/seller/learning_center/site_links/get` | 微前端 | `GetSiteLinks` |
| `GET` | `/api/v1/seller/learning_center/sitemap/urls/get` | 微前端 | `GetSitemapUrls` |
| `POST` | `/api/v1/seller/learning_center/star/create` | 微前端 | `CreateFiveStarComment` |
| `POST` | `/api/v1/seller/learning_center/star/get` | 微前端 | `GetFiveStarComment` |
| `?` | `/api/v1/seller/learning_center/video/play_info/get` | 微前端 | `GetVideoPlayInfo` |
| `POST` | `/api/v1/seller/university/cms/catalog/content/add` | 微前端 | `AddContentToCatalog` |
| `POST` | `/api/v1/seller/university/cms/catalog/content/unbind` | 微前端 | `UnbindContentToCatalog` |
| `POST` | `/api/v1/seller/university/cms/catalog/create` | 微前端 | `CreateCatalog` |
| `POST` | `/api/v1/seller/university/cms/catalog/delete` | 微前端 | `DeleteCatalog` |
| `POST` | `/api/v1/seller/university/cms/catalog/get` | 微前端 | `GetCatalog` |
| `POST` | `/api/v1/seller/university/cms/catalog/update` | 微前端 | `UpdateCatalog` |
| `POST` | `/api/v1/seller/university/cms/content/config/list` | 微前端 | `ListReviewContentConfig` |
| `POST` | `/api/v1/seller/university/cms/content/config/publish` | 微前端 | `PublishReviewContentConfig` |
| `POST` | `/api/v1/seller/university/cms/content/config/update` | 微前端 | `UpdateReviewContentConfig` |
| `POST` | `/api/v1/seller/university/cms/content/config/verify` | 微前端 | `VerifyReviewContentConfig` |
| `?` | `/api/v1/seller/university/cms/content/course/tree/get` | 微前端 | `GetCourseTree` |
| `?` | `/api/v1/seller/university/cms/content/detail/get` | 微前端 | `GetKnowledgeDetailV2` |
| `POST` | `/api/v1/seller/university/cms/content/move` | 微前端 | `MoveContent` |
| `POST` | `/api/v1/seller/university/cms/content/position/list` | 微前端 | `ListArticlePositions` |
| `POST` | `/api/v1/seller/university/cms/content/search` | 微前端 | `SearchContent` |
| `POST` | `/api/v1/seller/university/cms/content/status/update` | 微前端 | `UpdateContentStatus` |
| `?` | `/api/v1/seller/university/cms/contents_tree/get` | 微前端 | `GetContentsTreeCMS` |
| `POST` | `/api/v1/seller/university/cms/course/create` | 微前端 | `CreateCourseCMS` |
| `POST` | `/api/v1/seller/university/cms/course/get` | 微前端 | `GetCourseCMS` |
| `POST` | `/api/v1/seller/university/cms/course/search` | 微前端 | `SearchCourse` |
| `POST` | `/api/v1/seller/university/cms/course/status/update` | 微前端 | `UpdateCourseStatus` |
| `POST` | `/api/v1/seller/university/cms/course/update` | 微前端 | `UpdateCourseCMS` |
| `POST` | `/api/v1/seller/university/cms/file/save` | 微前端 | `SaveFile` |
| `POST` | `/api/v1/seller/university/cms/image/save` | 微前端 | `SaveImage` |
| `POST` | `/api/v1/seller/university/cms/knowledge/delete` | 微前端 | `DeleteKnowledge` |
| `POST` | `/api/v1/seller/university/cms/knowledge/get` | 微前端 | `GetKnowledgeCMS` |
| `POST` | `/api/v1/seller/university/cms/knowledge/publish` | 微前端 | `PublishKnowledge` |
| `POST` | `/api/v1/seller/university/cms/knowledge/save` | 微前端 | `SaveKnowledge` |
| `POST` | `/api/v1/seller/university/cms/knowledge/search` | 微前端 | `SearchKnowledgeCMS` |
| `?` | `/api/v1/seller/university/cms/lang/get` | 微前端 | `GetCountryLanguage` |
| `POST` | `/api/v1/seller/university/cms/module/config/create` | 微前端 | `CreateModuleConfig` |
| `POST` | `/api/v1/seller/university/cms/module/config/get` | 微前端 | `GetModuleConfig` |
| `POST` | `/api/v1/seller/university/cms/module/config/search` | 微前端 | `SearchModuleConfig` |
| `POST` | `/api/v1/seller/university/cms/module/config/status/update` | 微前端 | `UpdateModuleConfigStatus` |
| `POST` | `/api/v1/seller/university/cms/module/config/update` | 微前端 | `UpdateModuleConfig` |
| `?` | `/api/v1/seller/university/cms/option/get` | 微前端 | `GetRegionLanguageOption` |
| `POST` | `/api/v1/seller/university/cms/tag/create` | 微前端 | `CreateTag` |
| `POST` | `/api/v1/seller/university/cms/tag/delete` | 微前端 | `DeleteTag` |
| `POST` | `/api/v1/seller/university/cms/tag/get` | 微前端 | `GetTag` |
| `POST` | `/api/v1/seller/university/cms/tag/update` | 微前端 | `UpdateTag` |
| `POST` | `/api/v1/seller/university/cms/tag_relation/add` | 微前端 | `AddTagRelation` |
| `POST` | `/api/v1/seller/university/cms/tag_tree/get` | 微前端 | `GetTagTreeCMS` |
| `POST` | `/api/v1/seller/university/cms/upload/key/get` | 微前端 | `GetUploadKey` |
| `POST` | `/api/v1/seller/university/cms/video/play_info/get` | 微前端 | `GetVideoPlayInfo` |
| `POST` | `/api/v1/seller/university/cms/video/save` | 微前端 | `SaveVideo` |
| `GET` | `/api/v1/seller/university/entrance_knowledge_list/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetEntranceKnowledgeList` |
| `GET` | `/api/v1/seller/university/home/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetUniversityHome` |
| `POST` | `/api/v1/seller/university/knowledge/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetUniversityKnowledge` |
| `POST` | `/api/v1/seller/university/knowledge_feedback/create` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `CreateKnowledgeFeedback` |
| `GET` | `/widget/api/v1/seller/learning_center/video/play_info/get` | 微前端 | `WidgetGetVideoPlayInfo` |

## 店铺授权 / 子账号 / 角色（25）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/v1/seller/custom_role/allowed_config_menu/get` | 微前端 | `GetCustomRoleAllowedConfigMenu` |
| `POST` | `/api/v1/seller/custom_role/menu/get` | 微前端 | `GetCustomRoleMenu` |
| `POST` | `/api/v1/seller/custom_role/menu/set` | 微前端 | `SetCustomRoleMenu` |
| `POST` | `/api/v1/seller/custom_role/resource/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetCustomRoleResource` |
| `POST` | `/api/v1/seller/custom_role/resource/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SetCustomRoleResource` |
| `POST` | `/api/v1/seller/custom_role/resource_config_list/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCustomRoleResourceConfigList` |
| `POST` | `/api/v1/seller/delegation/am/abort` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `LogoutDelegationByAm` |
| `GET` | `/api/v1/seller/delegation/history/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetDelegationLoginHistory` |
| `GET` | `/api/v1/seller/delegation/info` | 微前端,微前端,微前端,微前端,财务bundle | `GetDelegationInfo` |
| `POST` | `/api/v1/seller/delegation/mode/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SetDelegationMode` |
| `POST` | `/api/v1/seller/delegation/seller/abort` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `AbortDelegationBySeller` |
| `POST` | `/api/v1/seller/semi/store/get` | 微前端 | `GetSemiStores` |
| `POST` | `/api/v1/seller/semi/store/link` | 微前端 | `LinkSemiStore` |
| `POST` | `/api/v1/seller/semi/store/unlink` | 微前端 | `UnlinkSemiStore` |
| `?` | `/api/v1/seller/semi/upgrade/get` | 微前端 | `GetSemiUpgrade` |
| `POST` | `/api/v1/seller/sub_account/add` | 微前端,微前端,微前端,财务bundle | `AddSubAccount` |
| `POST` | `/api/v1/seller/sub_account/bind` | 微前端,微前端,微前端,财务bundle | `BindSubAccount` |
| `POST` | `/api/v1/seller/sub_account/delete` | 微前端,微前端,微前端,财务bundle | `DeleteSubAccount` |
| `POST` | `/api/v1/seller/sub_account/list` | 微前端,微前端,微前端,财务bundle | `ListSubAccount` |
| `GET` | `/api/v1/seller/sub_account/roles/get` | 微前端,微前端,微前端,财务bundle | `GetRoles` |
| `POST` | `/api/v1/seller/sub_account/update` | 微前端,微前端,微前端,财务bundle | `UpdateSubAccount` |
| `GET` | `/api/v1/seller_settings/seller_whitelist/get` | 微前端,微前端,微前端 | `GetSellerWhiteList` |
| `GET` | `/api/v1/seller_settings/settings/get` | 微前端,微前端,微前端 | `GetSellerSettings` |
| `GET` | `/widget/api/v1/seller_settings/seller_whitelist/get` | 微前端,微前端,微前端 | `GetSellerWhiteListForWidget` |
| `GET` | `/widget/api/v1/seller_settings/settings/get` | 微前端,微前端,微前端 | `GetSellerSettingsForWidget` |

## 内容创作 / 视频中心（153）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `GET` | `/api/v1/app/multimedia/image/upload_token/get` | 微前端,微前端,微前端 | `GetAppImageUploadToken` |
| `POST` | `/api/v1/image/upload` | 微前端 | `History` |
| `GET` | `/api/v1/multimedia/file/upload_token/get` | 微前端,微前端,微前端 | `GetFileUploadToken` |
| `GET` | `/api/v1/multimedia/image/get` | 微前端,微前端,微前端 | `GetImage` |
| `GET` | `/api/v1/multimedia/image/upload_token/get` | 微前端,微前端,微前端 | `GetImageUploadToken` |
| `?` | `/api/v1/multimedia/upload_completion/notify` | 微前端 | `NotifyUploadCompletion` |
| `?` | `/api/v1/multimedia/video/get` | 微前端 | `GetVideo` |
| `GET` | `/api/v1/multimedia/video/upload_token/get` | 微前端,微前端,微前端 | `GetVideoUploadToken` |
| `POST` | `/api/v1/multimedia/white_background/check` | 微前端,微前端,微前端,早期 | `CheckWhiteBackgroundImage` |
| `POST` | `/api/v1/multimedia/white_background/get` | 微前端,微前端,微前端,早期 | `GetWhiteBackgroundImage` |
| `POST` | `/api/v1/seller/logo/aigc/add` | 微前端 | `AddAigcLogoTask` |
| `?` | `/api/v1/seller/logo/aigc/detail` | 微前端 | `GetAigcLogoTaskDetail` |
| `POST` | `/api/v1/seller/logo/aigc/list` | 微前端 | `ListAigcLogoTasks` |
| `POST` | `/api/v1/seller/logo/aigc/submit` | 微前端 | `SubmitAigcLogoTask` |
| `POST` | `/api/v1/seller/video_center/app/pre_gen_video/get` | 微前端 | `GetAPPVideoAutoGenTask` |
| `POST` | `/api/v1/seller/video_center/app/product_pre_gen_video/submit` | 微前端 | `SubmitAPPProductVideoAutoGenTask` |
| `POST` | `/api/v1/seller/video_center/benchmark_account/list` | 微前端 | `ListBenchmarkAccount` |
| `GET` | `/api/v1/seller/video_center/config/get` | 微前端 | `GetConfig` |
| `POST` | `/api/v1/seller/video_center/creator_info/get` | 微前端 | `GetCreatorInfo` |
| `POST` | `/api/v1/seller/video_center/education/get` | 微前端 | `GetVideoEducationPage` |
| `POST` | `/api/v1/seller/video_center/education/simple/get` | 微前端 | `GetSimpleEducationPage` |
| `POST` | `/api/v1/seller/video_center/event/post` | 微前端 | `PostContentEvent` |
| `POST` | `/api/v1/seller/video_center/favorite/update` | 微前端 | `UpdateFavorite` |
| `GET` | `/api/v1/seller/video_center/hashtag/detail` | 微前端 | `GetHashtagDetail` |
| `GET` | `/api/v1/seller/video_center/hashtag/filter` | 微前端 | `GetHashtagFilter` |
| `POST` | `/api/v1/seller/video_center/hashtag/rank_list` | 微前端 | `GetHashtagRankList` |
| `GET` | `/api/v1/seller/video_center/live_highlights/edit/query` | 微前端 | `QueryHighlightEdit` |
| `POST` | `/api/v1/seller/video_center/live_highlights/edit/submit` | 微前端 | `SubmitHighlightEdit` |
| `POST` | `/api/v1/seller/video_center/live_highlights/list` | 微前端 | `ListLiveHighlights` |
| `GET` | `/api/v1/seller/video_center/outreach_landing_page/get` | 微前端 | `GetOutreachLandingPage` |
| `POST` | `/api/v1/seller/video_center/outreach_landing_page/post_to_tiktok` | 微前端 | `Post2TT` |
| `POST` | `/api/v1/seller/video_center/post/add_product/check` | 微前端 | `CheckAddProduct` |
| `POST` | `/api/v1/seller/video_center/post/title/check` | 微前端 | `CheckPostTitle` |
| `POST` | `/api/v1/seller/video_center/post_task/cancel` | 微前端 | `CancelPostTask` |
| `POST` | `/api/v1/seller/video_center/post_task/list` | 微前端 | `GetPostTaskList` |
| `POST` | `/api/v1/seller/video_center/pre_check_task/config/get` | 微前端 | `GetVideoPreCheckConfig` |
| `POST` | `/api/v1/seller/video_center/pre_check_task/list` | 微前端 | `ListVideoPreCheckTask` |
| `POST` | `/api/v1/seller/video_center/pre_check_task/rate` | 微前端 | `RateVideoPreCheckTaskResult` |
| `POST` | `/api/v1/seller/video_center/pre_check_task/submit` | 微前端 | `SubmitVideoPreCheckTask` |
| `POST` | `/api/v1/seller/video_center/pre_gen_video/get` | 微前端 | `GetVideoAutoGenTask` |
| `POST` | `/api/v1/seller/video_center/pre_gen_video/history/get` | 微前端 | `GetVideoAutoGenTaskHistory` |
| `POST` | `/api/v1/seller/video_center/pre_gen_video/upload_task/get` | 微前端 | `GetPostVideoRecord` |
| `POST` | `/api/v1/seller/video_center/pre_gen_video/upload_task/submit` | 微前端 | `SubmitPostVideoTask` |
| `POST` | `/api/v1/seller/video_center/pre_gen_video/upload_task/upsert` | 微前端 | `UpsertPostVideoRecord` |
| `POST` | `/api/v1/seller/video_center/product/gen_title` | 微前端 | `GenProductTitle` |
| `POST` | `/api/v1/seller/video_center/product/search` | 微前端 | `SearchProduct` |
| `GET` | `/api/v1/seller/video_center/product_detail/get` | 微前端 | `AwemeGetProductDetail` |
| `POST` | `/api/v1/seller/video_center/product_pre_gen_video/cancel` | 微前端 | `CancelProductVideoAutoGenTask` |
| `POST` | `/api/v1/seller/video_center/product_pre_gen_video/submit` | 微前端 | `SubmitProductVideoAutoGenTask` |
| `POST` | `/api/v1/seller/video_center/product_recommend_video/list` | 微前端 | `ListProductRecommendVideo` |
| `GET` | `/api/v1/seller/video_center/sc_homepage/widget/get` | 微前端 | `GetVideoSCHomepageWidget` |
| `POST` | `/api/v1/seller/video_center/setting/get` | 微前端 | `GetVideoCenterSetting` |
| `POST` | `/api/v1/seller/video_center/setting/save` | 微前端 | `SaveVideoCenterSetting` |
| `GET` | `/api/v1/seller/video_center/sound/detail` | 微前端 | `GetSoundDetail` |
| `POST` | `/api/v1/seller/video_center/sound/rank_list` | 微前端 | `GetSoundRankList` |
| `GET` | `/api/v1/seller/video_center/template/detail/get` | 微前端 | `GetTemplateDetail` |
| `POST` | `/api/v1/seller/video_center/template/list` | 微前端 | `ListTemplates` |
| `GET` | `/api/v1/seller/video_center/text_tips/get` | 微前端 | `GetTextTips` |
| `POST` | `/api/v1/seller/video_center/tips/list` | 微前端 | `ListVideoTips` |
| `GET` | `/api/v1/seller/video_center/tips/options/get` | 微前端 | `GetTipOptions` |
| `POST` | `/api/v1/seller/video_center/video/dump/get` | 微前端 | `GetSellerContentVideoInfo` |
| `POST` | `/api/v1/seller/video_center/video_draft_job/query` | 微前端 | `QueryVideoDraftJob` |
| `POST` | `/api/v1/seller/video_center/video_draft_job/submit` | 微前端 | `SubmitVideoDraftJob` |
| `GET` | `/api/v1/seller/video_center/video_feed/overview/get` | 微前端 | `GetVideoOverview` |
| `POST` | `/api/v1/seller/video_center/video_pre_data/gen` | 微前端 | `GenVideoPreData` |
| `POST` | `/api/v1/seller/video_center/video_render_job/batch_submit` | 微前端 | `BatchSubmitVideoRenderJob` |
| `POST` | `/api/v1/seller/video_center/video_render_job/query` | 微前端 | `QueryVideoRenderJob` |
| `POST` | `/api/v1/seller/video_center/video_render_job/submit` | 微前端 | `SubmitVideoRenderJob` |
| `POST` | `/api/v1/seller/video_center/video_url_data/gen` | 微前端 | `GenVideoUrlData` |
| `POST` | `/api/v1/seller_template/binding_info/get` | 微前端,微前端 | `GetTemplateBindingInfo` |
| `POST` | `/api/v1/seller_template/binding_template/batch_binding` | 微前端 | `BatchBindingTemplate` |
| `POST` | `/api/v1/seller_template/binding_template/binding` | 微前端,微前端 | `BindingTemplate` |
| `POST` | `/api/v1/seller_template/binding_template/get` | 微前端,微前端 | `MGetSellerBindingTemplate` |
| `POST` | `/api/v1/seller_template/create` | 微前端,微前端,微前端 | `CreateSellerTemplate` |
| `POST` | `/api/v1/seller_template/create_default_template` | 微前端 | `CreateDefaultTemplate` |
| `POST` | `/api/v1/seller_template/delete` | 微前端,微前端,微前端 | `DeleteTemplate` |
| `POST` | `/api/v1/seller_template/get_available_template_pricing_mode` | 微前端 | `GetAvailableTemplatePricingMode` |
| `POST` | `/api/v1/seller_template/get_available_template_to_region` | 微前端 | `GetAvailableTemplateToRegion` |
| `POST` | `/api/v1/seller_template/get_available_template_type` | 微前端 | `GetAvailableTemplateType` |
| `POST` | `/api/v1/seller_template/get_region` | 微前端,微前端 | `GetTemplateRegion` |
| `POST` | `/api/v1/seller_template/get_warehouse_relation` | 微前端,微前端 | `GetTemplateWarehouseRelation` |
| `POST` | `/api/v1/seller_template/improper_fee_template/get` | 微前端,微前端 | `GetSellerImProperFeeTemplates` |
| `POST` | `/api/v1/seller_template/key_info_list/get` | 微前端,微前端 | `GetSellerTemplatesKeyInfo` |
| `POST` | `/api/v1/seller_template/modify` | 微前端,微前端,微前端 | `ModifySellerTemplate` |
| `POST` | `/api/v1/seller_template/recommend_rule/get` | 微前端,微前端 | `GetRecommendationRulePrice` |
| `POST` | `/api/v1/seller_template/rule_proper_fee/get` | 微前端,微前端 | `GetTemplateRuleProperFee` |
| `GET` | `/api/v1/seller_template/shipping_info/get` | 微前端,微前端,微前端 | `GetSellerShippingInfo` |
| `GET` | `/api/v1/seller_template/template_detail/get` | 微前端,微前端,微前端 | `GetTemplateDetail` |
| `POST` | `/api/v1/seller_template/template_detail/update` | 微前端,微前端,微前端 | `UpdateSellerTemplate` |
| `POST` | `/api/v1/seller_template/template_meta/get_region_config` | 微前端,微前端 | `GetTemplateRegionConfig` |
| `GET` | `/api/v1/seller_template/template_meta/list` | 微前端,微前端,微前端 | `ListTemplateMeta` |
| `POST` | `/api/v1/seller_template/template_proper_fee/get` | 微前端,微前端 | `GetTemplateProperFee` |
| `POST` | `/api/v1/seller_template/us/create` | 微前端,微前端 | `USCreateSellerTemplate` |
| `POST` | `/api/v1/seller_template/us/modify` | 微前端,微前端 | `USModifySellerTemplate` |
| `POST` | `/api/v1/seller_template/us/platform_pricing_service/get` | 微前端,微前端 | `GetTemplatePlatformPricingSubscribableService` |
| `POST` | `/api/v1/seller_template/us/template_detail/get` | 微前端,微前端 | `USGetTemplateDetail` |
| `POST` | `/api/v1/seller_template/us/template_detail/list` | 微前端,微前端 | `USListTemplateDetail` |
| `POST` | `/api/v1/seller_template/us/warehouse/add` | 微前端,微前端 | `USAddWarehouseToTemplate` |
| `POST` | `/api/v1/seller_template/warehouse_template_binding/get` | 微前端 | `GetTemplateWarehouseBindingInfo` |
| `GET` | `/widget/api/v1/multimedia/image/get` | 微前端,微前端,微前端 | `GetImageForWidget` |
| `GET` | `/widget/api/v1/multimedia/image/upload_token/get` | 微前端,微前端,微前端 | `GetImageUploadTokenForWidget` |
| `?` | `/widget/api/v1/multimedia/upload_completion/notify` | 微前端 | `NotifyUploadCompletionForWidget` |
| `POST` | `/widget/api/v1/seller/video_center/benchmark_account/list` | 微前端 | `WidgetListBenchmarkAccount` |
| `POST` | `/widget/api/v1/seller/video_center/creator_info/get` | 微前端 | `WidgetGetCreatorInfo` |
| `POST` | `/widget/api/v1/seller/video_center/event/post` | 微前端 | `WidgetPostContentEvent` |
| `POST` | `/widget/api/v1/seller/video_center/favorite/update` | 微前端 | `WidgetUpdateFavorite` |
| `GET` | `/widget/api/v1/seller/video_center/hashtag/detail` | 微前端 | `WidgetGetHashtagDetail` |
| `GET` | `/widget/api/v1/seller/video_center/hashtag/filter` | 微前端 | `WidgetGetHashtagFilter` |
| `POST` | `/widget/api/v1/seller/video_center/hashtag/rank_list` | 微前端 | `WidgetGetHashtagRankList` |
| `GET` | `/widget/api/v1/seller/video_center/live_highlights/edit/query` | 微前端 | `WidgetQueryHighlightEdit` |
| `POST` | `/widget/api/v1/seller/video_center/live_highlights/edit/submit` | 微前端 | `WidgetSubmitHighlightEdit` |
| `POST` | `/widget/api/v1/seller/video_center/live_highlights/list` | 微前端 | `WidgetListLiveHighlights` |
| `POST` | `/widget/api/v1/seller/video_center/post/add_product/check` | 微前端 | `WidgetCheckAddProduct` |
| `POST` | `/widget/api/v1/seller/video_center/post/title/check` | 微前端 | `WidgetCheckPostTitle` |
| `POST` | `/widget/api/v1/seller/video_center/post_task/cancel` | 微前端 | `WidgetCancelPostTask` |
| `POST` | `/widget/api/v1/seller/video_center/post_task/list` | 微前端 | `WidgetGetPostTaskList` |
| `POST` | `/widget/api/v1/seller/video_center/pre_gen_video/get` | 微前端 | `WidgetGetVideoAutoGenTask` |
| `POST` | `/widget/api/v1/seller/video_center/pre_gen_video/upload_task/submit` | 微前端 | `WidgetSubmitPostVideoTask` |
| `POST` | `/widget/api/v1/seller/video_center/product/gen_title` | 微前端 | `WidgetGenProductTitle` |
| `POST` | `/widget/api/v1/seller/video_center/product/search` | 微前端 | `WidgetSearchProduct` |
| `POST` | `/widget/api/v1/seller/video_center/product_pre_gen_video/submit` | 微前端 | `WidgetSubmitProductVideoAutoGenTask` |
| `GET` | `/widget/api/v1/seller/video_center/sc_homepage/widget/get` | 微前端 | `WidgetGetVideoSCHomepageWidget` |
| `POST` | `/widget/api/v1/seller/video_center/setting/get` | 微前端 | `WidgetGetVideoCenterSetting` |
| `POST` | `/widget/api/v1/seller/video_center/setting/save` | 微前端 | `WidgetSaveVideoCenterSetting` |
| `GET` | `/widget/api/v1/seller/video_center/sound/detail` | 微前端 | `WidgetGetSoundDetail` |
| `POST` | `/widget/api/v1/seller/video_center/sound/rank_list` | 微前端 | `WidgetGetSoundRankList` |
| `GET` | `/widget/api/v1/seller/video_center/template/detail/get` | 微前端 | `WidgetGetTemplateDetail` |
| `POST` | `/widget/api/v1/seller/video_center/template/list` | 微前端 | `WidgetListTemplates` |
| `GET` | `/widget/api/v1/seller/video_center/text_tips/get` | 微前端 | `WidgetGetTextTips` |
| `POST` | `/widget/api/v1/seller/video_center/tips/list` | 微前端 | `WidgetListVideoTips` |
| `GET` | `/widget/api/v1/seller/video_center/tips/options/get` | 微前端 | `WidgetGetTipOptions` |
| `POST` | `/widget/api/v1/seller/video_center/video_draft_job/query` | 微前端 | `WidgetQueryVideoDraftJob` |
| `POST` | `/widget/api/v1/seller/video_center/video_draft_job/submit` | 微前端 | `WidgetSubmitVideoDraftJob` |
| `POST` | `/widget/api/v1/seller/video_center/video_pre_data/gen` | 微前端 | `WidgetGenVideoPreData` |
| `POST` | `/widget/api/v1/seller/video_center/video_render_job/batch_submit` | 微前端 | `WidgetBatchSubmitVideoRenderJob` |
| `POST` | `/widget/api/v1/seller/video_center/video_render_job/query` | 微前端 | `WidgetQueryVideoRenderJob` |
| `POST` | `/widget/api/v1/seller/video_center/video_url_data/gen` | 微前端 | `WidgetGenVideoUrlData` |
| `POST` | `/widget/api/v1/seller_template/create` | 微前端,微前端,微前端 | `CreateSellerTemplateForWidget` |
| `POST` | `/widget/api/v1/seller_template/delete` | 微前端,微前端,微前端 | `DeleteTemplateForWidget` |
| `POST` | `/widget/api/v1/seller_template/get_region` | 微前端,微前端 | `GetTemplateRegionForWidget` |
| `POST` | `/widget/api/v1/seller_template/get_warehouse_relation` | 微前端,微前端 | `GetTemplateWarehouseRelationForWidget` |
| `POST` | `/widget/api/v1/seller_template/improper_fee_template/get` | 微前端,微前端 | `GetSellerImProperFeeTemplatesForWidget` |
| `POST` | `/widget/api/v1/seller_template/modify` | 微前端,微前端,微前端 | `ModifySellerTemplateForWidget` |
| `POST` | `/widget/api/v1/seller_template/rule_proper_fee/get` | 微前端,微前端 | `GetTemplateRuleProperFeeForWidget` |
| `GET` | `/widget/api/v1/seller_template/shipping_info/get` | 微前端,微前端,微前端 | `GetSellerShippingInfoForWidget` |
| `GET` | `/widget/api/v1/seller_template/template_detail/get` | 微前端,微前端,微前端 | `GetTemplateDetailForWidget` |
| `POST` | `/widget/api/v1/seller_template/template_detail/update` | 微前端,微前端,微前端 | `UpdateSellerTemplateForWidget` |
| `GET` | `/widget/api/v1/seller_template/template_meta/list` | 微前端,微前端,微前端 | `ListTemplateMetaForWidget` |
| `POST` | `/widget/api/v1/seller_template/template_proper_fee/get` | 微前端,微前端 | `GetTemplateProperFeeForWidget` |
| `POST` | `/widget/api/v1/seller_template/us/create` | 微前端,微前端 | `USCreateSellerTemplateForWidget` |
| `POST` | `/widget/api/v1/seller_template/us/modify` | 微前端,微前端 | `USModifySellerTemplateForWidget` |
| `POST` | `/widget/api/v1/seller_template/us/template_detail/get` | 微前端,微前端 | `USGetTemplateDetailForWidget` |
| `POST` | `/widget/api/v1/seller_template/us/template_detail/list` | 微前端,微前端 | `USListTemplateDetailForWidget` |

## 商品成长 / 优化 / 机会（63）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/dbmp/pop/product_growth/category/authorized` | 微前端 | `GetAuthorizedCategoriesForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/ready_time` | 微前端 | `GetModuleReadyTimeForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/audit` | 微前端 | `AuditSellerShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/check` | 微前端 | `CheckShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/create` | 微前端 | `CreateSellerShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/delete` | 微前端 | `DelSellerShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/edit` | 微前端 | `EditSellerShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/mget` | 微前端 | `MGetShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/seller_shop_rel/search` | 微前端 | `SearchSellerShopRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/shop/list` | 微前端 | `ListShopInfo` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/sim_product_rel/export` | 微前端 | `ExportSimProductRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/sim_products/sim_product_rel/list` | 微前端 | `ListSimProductRel` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/favorite` | 微前端 | `SaveOrUpdateFavoriteForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/content` | 微前端 | `GetContentTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/live` | 微前端 | `GetLiveTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/new` | 微前端 | `GetTopNewProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/overall` | 微前端 | `GetOverallTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/prod_card` | 微前端 | `GetProductCardTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/third_party/live` | 微前端 | `GetLiveThirdPartyTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/third_party/video` | 微前端 | `GetVideoThirdPartyTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_selling/product/video` | 微前端 | `GetVideoTopProductListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/top_viewed/video/list` | 微前端 | `GetTopViewedVideoListForDBMP` |
| `POST` | `/api/v1/dbmp/pop/product_growth/upload_task/create` | 微前端 | `CreateUploadTask` |
| `POST` | `/api/v1/dbmp/pop/product_growth/video` | 微前端 | `QueryVideosForDBMP` |
| `POST` | `/api/v1/pop/product/optimize/data/get` | 微前端 | `GetOptimizationData` |
| `POST` | `/api/v1/pop/product/optimize/meta/get` | 微前端 | `GetOptimizationMeta` |
| `PUT` | `/api/v1/pop/product/optimize/multi_edit` | 微前端 | `MEditOptimizedProduct` |
| `POST` | `/api/v1/pop/product/optimize/multi_get` | 微前端 | `MGetOptimizationProduct` |
| `POST` | `/api/v1/pop/product/optimize/page/get` | 微前端 | `GetToBeOptimizedProductPage` |
| `POST` | `/api/v1/pop/product/optimize/seo/rank` | 微前端 | `GetOptimizeProductSeoWordRank` |
| `POST` | `/api/v1/pop/product/optimize/seo_gain/mget` | 微前端 | `MGetOptimizeProductSeoExpectGain` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose` | 微前端 | `GetProductAiDiagnose` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/ads_list` | 微前端 | `GetProductAiDiagnoseAdsList` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/cfg` | 微前端 | `GetProductAiDiagnoseConfig` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/content_list` | 微前端 | `GetProductAiDiagnoseContentList` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/content_list/cnt` | 微前端 | `GetProductAiDiagnoseContentListCnt` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/feedback` | 微前端 | `SubmitProductAiDiagnoseFeedback` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/id` | 微前端 | `GetProductAiDiagnoseMsgId` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/product_stats` | 微前端 | `GetProductAiDiagnoseStats` |
| `POST` | `/api/v1/pop/product_growth/ai/diagnose/product_trend` | 微前端 | `GetProductAiDiagnoseTrend` |
| `POST` | `/api/v1/pop/product_growth/category/authorized` | 微前端 | `GetAuthorizedCategories` |
| `POST` | `/api/v1/pop/product_growth/ready_time` | 微前端 | `GetModuleReadyTime` |
| `POST` | `/api/v1/pop/product_growth/top_selling/favorite` | 微前端 | `SaveOrUpdateFavorite` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/content` | 微前端 | `GetContentTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/live` | 微前端 | `GetLiveTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/new` | 微前端 | `GetTopNewProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/overall` | 微前端 | `GetOverallTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/prod_card` | 微前端 | `GetProductCardTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/third_party/live` | 微前端 | `GetLiveThirdPartyTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/third_party/video` | 微前端 | `GetVideoThirdPartyTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_selling/product/video` | 微前端 | `GetVideoTopProductList` |
| `POST` | `/api/v1/pop/product_growth/top_viewed/video/list` | 微前端 | `GetTopViewedVideoList` |
| `POST` | `/api/v1/pop/product_growth/video` | 微前端 | `QueryVideos` |
| `?` | `/api/v1/seller/growth/opportunity/config/get` | 微前端,微前端 | `GetGrowthOpportunitiesConfig` |
| `GET` | `/api/v1/seller/growth/opportunity/education/get` | 微前端,微前端,早期 | `GetGrowthOpportunitiesEducations` |
| `?` | `/api/v1/seller/growth/opportunity/history/get` | 微前端,微前端 | `GetGrowthOpportunitiesHistory` |
| `GET` | `/api/v1/seller/growth/opportunity/home/get` | 微前端,微前端,早期 | `GetGrowthOpportunitiesHome` |
| `?` | `/api/v1/seller/growth/opportunity/widget/get` | 微前端,微前端 | `GetGrowthOpportunitiesWidget` |
| `POST` | `/widget/api/v1/pop/product/optimize/data/get` | 微前端 | `GetOptimizationDataForWidget` |
| `POST` | `/widget/api/v1/pop/product/optimize/meta/get` | 微前端 | `GetOptimizationMetaForWidget` |
| `POST` | `/widget/api/v1/pop/product/optimize/page/get` | 微前端 | `GetToBeOptimizedProductPageForWidget` |
| `POST` | `/widget/api/v1/pop/product/optimize/seo/rank` | 微前端 | `GetOptimizeProductSeoWordRankForWidget` |
| `POST` | `/widget/api/v1/pop/product/optimize/seo_gain/mget` | 微前端 | `MGetOptimizeProductSeoExpectGainForWidget` |

## 交易（/trade 前缀，另一套）（64）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `GET` | `/api/v1/trade/compensation/get` | 微前端 | `GetSellerCompensationDetail` |
| `POST` | `/api/v1/trade/orders/buyer` | 微前端 | `ListMainOrderBuyerInfo` |
| `POST` | `/api/v1/trade/orders/confirm_rts` | 微前端 | `ConfirmRTSSellerOrders` |
| `GET` | `/api/v1/trade/orders/download` | 微前端 | `DownloadSellerMainOrders` |
| `POST` | `/api/v1/trade/orders/export` | 微前端 | `ExportSellerMainOrders` |
| `POST` | `/api/v1/trade/orders/export/list` | 微前端 | `ListSellerExportRecords` |
| `GET` | `/api/v1/trade/orders/get` | 微前端 | `GetSellerMainOrder` |
| `POST` | `/api/v1/trade/orders/list` | 微前端 | `ListSellerMainOrders` |
| `POST` | `/api/v1/trade/orders/note/list` | 微前端 | `ListSellerNotes` |
| `POST` | `/api/v1/trade/orders/note/set` | 微前端 | `SetSellerNote` |
| `POST` | `/api/v1/trade/orders/order_index/list` | 微前端 | `ListSellerOrderIndex` |
| `POST` | `/api/v1/trade/orders/order_lines/list` | 微前端 | `ListSellerOrderLines` |
| `GET` | `/api/v1/trade/orders/order_service_status/get` | 微前端 | `GetUserOrderServiceStatus` |
| `POST` | `/api/v1/trade/orders/pick_up_conf` | 微前端 | `ListMainOrderPickUpConfig` |
| `POST` | `/api/v1/trade/orders/refund` | 微前端 | `RefundSellerOrders` |
| `POST` | `/api/v1/trade/orders/refund_preview` | 微前端 | `RefundSellerOrdersPreview` |
| `POST` | `/api/v1/trade/orders/rts` | 微前端 | `RTSSellerOrders` |
| `GET` | `/api/v1/trade/orders/shipment_patterns` | 微前端 | `ListShipmentProviderPattern` |
| `GET` | `/api/v1/trade/orders/tabs` | 微前端 | `GetSellerOrderTabs` |
| `POST` | `/api/v1/trade/orders/tag` | 微前端 | `SetOrderTag` |
| `POST` | `/api/v1/trade/orders/verify_rts` | 微前端 | `VerifyRTSSellerOrders` |
| `GET` | `/api/v1/trade/orders/warehouse/list` | 微前端 | `ListSellerSaleWarehouse` |
| `POST` | `/api/v1/trade/package/action` | 微前端 | `StartSellerFulfillUnitAction` |
| `GET` | `/api/v1/trade/package/get` | 微前端 | `GetSellerFulfillUnit` |
| `POST` | `/api/v1/trade/package/list` | 微前端 | `ListSellerFulfillUnits` |
| `POST` | `/api/v1/trade/shipping/bulk_index` | 微前端 | `ListMainOrderBulkShippingIndex` |
| `POST` | `/api/v1/trade/shipping/bulk_index_package` | 微前端 | `ListPackageBulkShippingIndex` |
| `POST` | `/api/v1/trade/shipping/fee/estimated` | 微前端 | `ListSellerEstimatedShippingFee` |
| `POST` | `/api/v1/trade/shipping/settings/create` | 微前端 | `CreateSellerFulfillSetting` |
| `GET` | `/api/v1/trade/shipping/settings/get` | 微前端 | `ListSellerFulfillSetting` |
| `POST` | `/api/v1/trade/shipping/settings/update` | 微前端 | `UpdateSellerFulfillSetting` |
| `POST` | `/api/v1/trade/tracking_numbers/verify` | 微前端 | `MVerifySellerTrackingNo` |
| `GET` | `/widget/api/v1/trade/compensation/get` | 微前端 | `GetSellerCompensationDetailForWidget` |
| `POST` | `/widget/api/v1/trade/orders/buyer` | 微前端 | `ListMainOrderBuyerInfoForWidget` |
| `POST` | `/widget/api/v1/trade/orders/confirm_rts` | 微前端 | `ConfirmRTSSellerOrdersForWidget` |
| `GET` | `/widget/api/v1/trade/orders/download` | 微前端 | `DownloadSellerMainOrdersForWidget` |
| `POST` | `/widget/api/v1/trade/orders/export` | 微前端 | `ExportSellerMainOrdersForWidget` |
| `POST` | `/widget/api/v1/trade/orders/export/list` | 微前端 | `ListSellerExportRecordsForWidget` |
| `GET` | `/widget/api/v1/trade/orders/get` | 微前端 | `GetSellerMainOrderForWidget` |
| `POST` | `/widget/api/v1/trade/orders/list` | 微前端 | `ListSellerMainOrdersForWidget` |
| `POST` | `/widget/api/v1/trade/orders/note/list` | 微前端 | `ListSellerNotesForWidget` |
| `POST` | `/widget/api/v1/trade/orders/note/set` | 微前端 | `SetSellerNoteForWidget` |
| `POST` | `/widget/api/v1/trade/orders/order_index/list` | 微前端 | `ListSellerOrderIndexForWidget` |
| `POST` | `/widget/api/v1/trade/orders/order_lines/list` | 微前端 | `ListSellerOrderLinesForWidget` |
| `GET` | `/widget/api/v1/trade/orders/order_service_status/get` | 微前端 | `GetUserOrderServiceStatusForWidget` |
| `POST` | `/widget/api/v1/trade/orders/pick_up_conf` | 微前端 | `ListMainOrderPickUpConfigForWidget` |
| `POST` | `/widget/api/v1/trade/orders/refund` | 微前端 | `RefundSellerOrdersForWidget` |
| `POST` | `/widget/api/v1/trade/orders/refund_preview` | 微前端 | `RefundSellerOrdersPreviewForWidget` |
| `POST` | `/widget/api/v1/trade/orders/rts` | 微前端 | `RTSSellerOrdersForWidget` |
| `GET` | `/widget/api/v1/trade/orders/shipment_patterns` | 微前端 | `ListShipmentProviderPatternForWidget` |
| `GET` | `/widget/api/v1/trade/orders/tabs` | 微前端 | `GetSellerOrderTabsForWidget` |
| `POST` | `/widget/api/v1/trade/orders/tag` | 微前端 | `SetOrderTagForWidget` |
| `POST` | `/widget/api/v1/trade/orders/verify_rts` | 微前端 | `VerifyRTSSellerOrdersForWidget` |
| `GET` | `/widget/api/v1/trade/orders/warehouse/list` | 微前端 | `ListSellerSaleWarehouseForWidget` |
| `POST` | `/widget/api/v1/trade/package/action` | 微前端 | `StartSellerFulfillUnitActionForWidget` |
| `GET` | `/widget/api/v1/trade/package/get` | 微前端 | `GetSellerFulfillUnitForWidget` |
| `POST` | `/widget/api/v1/trade/package/list` | 微前端 | `ListSellerFulfillUnitsForWidget` |
| `POST` | `/widget/api/v1/trade/shipping/bulk_index` | 微前端 | `ListMainOrderBulkShippingIndexForWidget` |
| `POST` | `/widget/api/v1/trade/shipping/bulk_index_package` | 微前端 | `ListPackageBulkShippingIndexForWidget` |
| `POST` | `/widget/api/v1/trade/shipping/fee/estimated` | 微前端 | `ListSellerEstimatedShippingFeeForWidget` |
| `POST` | `/widget/api/v1/trade/shipping/settings/create` | 微前端 | `CreateSellerFulfillSettingForWidget` |
| `GET` | `/widget/api/v1/trade/shipping/settings/get` | 微前端 | `ListSellerFulfillSettingForWidget` |
| `POST` | `/widget/api/v1/trade/shipping/settings/update` | 微前端 | `UpdateSellerFulfillSettingForWidget` |
| `POST` | `/widget/api/v1/trade/tracking_numbers/verify` | 微前端 | `MVerifySellerTrackingNoForWidget` |

## 全球仓 / 跨境 / 区域（36）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `GET` | `/api/v1/seller/cross_border/delivery/get` | 微前端,微前端,微前端,财务bundle | `GetCrossBorderSellerDelivery` |
| `POST` | `/api/v1/seller/global/fe_gray_setting/get` | 微前端,微前端,微前端,财务bundle | `GetFEGraySetting` |
| `POST` | `/api/v1/seller/global/platform_warehouses/add` | 微前端,微前端,微前端,财务bundle | `AddPlatformWarehouses` |
| `POST` | `/api/v1/seller/global/platform_warehouses/available/get` | 微前端,微前端,微前端,财务bundle | `GetAvailablePlatformWarehouses` |
| `POST` | `/api/v1/seller/global/platform_warehouses/delete` | 微前端,微前端,微前端,财务bundle | `DeletePlatformWarehouses` |
| `GET` | `/api/v1/seller/global/warehouse/param_rule/get` | 微前端,微前端,微前端,财务bundle | `WarehouseParameterRule` |
| `POST` | `/api/v1/seller/global/warehouse/prefill` | 微前端,微前端,微前端,财务bundle | `PrefillWarehouseInfo` |
| `POST` | `/api/v1/seller/global/warehouse/shop/indictor` | 微前端 | `GetShopIndicatorDetail` |
| `POST` | `/api/v1/seller/global/warehouses/add` | 微前端,微前端,微前端,财务bundle | `AddGlobalSellerWarehouses` |
| `GET` | `/api/v1/seller/global/warehouses/available_region/get` | 微前端,微前端,微前端,财务bundle | `GetAvailableRegions` |
| `GET` | `/api/v1/seller/global/warehouses/deactivated_warehouse/get` | 微前端,微前端,微前端,财务bundle | `GetDeactivatedSellerWarehouse` |
| `POST` | `/api/v1/seller/global/warehouses/default/set` | 微前端,微前端,微前端,财务bundle | `SetDefaultWarehouse` |
| `POST` | `/api/v1/seller/global/warehouses/delete` | 微前端,微前端,微前端,财务bundle | `DeleteGlobalSellerWarehouses` |
| `GET` | `/api/v1/seller/global/warehouses/get` | 微前端,微前端,微前端,财务bundle | `GetGlobalSellerWarehouses` |
| `GET` | `/api/v1/seller/global/warehouses/permission/get` | 微前端,微前端,微前端,财务bundle | `GetGlobalSellerWarehousesPermission` |
| `POST` | `/api/v1/seller/global/warehouses/priority/set` | 微前端,微前端,微前端,财务bundle | `SetWarehousePriority` |
| `POST` | `/api/v1/seller/global/warehouses/status_transfer` | 微前端,微前端,微前端,财务bundle | `SellerWarehouseStatusTransfer` |
| `POST` | `/api/v1/seller/global/warehouses/switch` | 微前端,微前端,微前端,财务bundle | `SwitchGlobalWarehouses` |
| `POST` | `/api/v1/seller/global/warehouses/update` | 微前端,微前端,微前端,财务bundle | `UpdateGlobalSellerWarehouses` |
| `POST` | `/api/v1/seller/region/auto/complete/detail` | 微前端,微前端,微前端,财务bundle | `GetAutoCompleteRegionDetail` |
| `POST` | `/api/v1/seller/region/auto/complete/list` | 微前端,微前端,微前端,财务bundle | `ListAutoCompleteRegion` |
| `POST` | `/api/v1/seller/toko/binding` | 微前端 | `Binding` |
| `POST` | `/api/v1/seller/toko/cancel/process` | 微前端 | `CancelProcess` |
| `POST` | `/api/v1/seller/toko/consolidation/product_merge/query` | 微前端 | `ConsolidationProductMergeQuery` |
| `?` | `/api/v1/seller/toko/consolidation/status` | 微前端 | `QueryConsolidationStatus` |
| `POST` | `/api/v1/seller/toko/integration/enter` | 微前端 | `IntegrationEnter` |
| `POST` | `/api/v1/seller/toko/integration/profile` | 微前端 | `IntegrationTokoProfile` |
| `POST` | `/api/v1/seller/toko/integration/query` | 微前端 | `IntegrationQuery` |
| `POST` | `/api/v1/seller/toko/integration/submit` | 微前端 | `IntegrationSubmit` |
| `?` | `/api/v1/seller/toko/integration/success_query` | 微前端 | `IntegrationSuccessQuery` |
| `?` | `/api/v1/seller/toko/novation_agreement/query` | 微前端 | `NovationAgreementResultQuery` |
| `POST` | `/api/v1/seller/toko/novation_agreement/submit` | 微前端 | `NovationAgreementSubmission` |
| `POST` | `/widget/api/v1/seller/global/warehouses/add` | 微前端,微前端,微前端,财务bundle | `AddGlobalSellerWarehousesForWidget` |
| `POST` | `/widget/api/v1/seller/global/warehouses/status_transfer` | 微前端,微前端,微前端,财务bundle | `SellerWarehouseStatusTransferForWidget` |
| `POST` | `/widget/api/v1/seller/region/auto/complete/detail` | 微前端,微前端,微前端,财务bundle | `WidgetGetAutoCompleteRegionDetail` |
| `POST` | `/widget/api/v1/seller/region/auto/complete/list` | 微前端,微前端,微前端,财务bundle | `WidgetListAutoCompleteRegion` |

## 达人外联 / 任务消息（21）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `GET` | `/api/v1/cb/seller/incentives/algo/tasks/get` | 微前端 | `GetAlgoSellerTasks` |
| `GET` | `/api/v1/cb/seller/incentives/overview/get` | 微前端 | `GetIncentivesOverview` |
| `GET` | `/api/v1/cb/seller/incentives/program/get` | 微前端 | `GetIncentivesProgram` |
| `GET` | `/api/v1/cb/seller/incentives/program/popUp/get` | 微前端 | `GetIncentivesProgramPopUp` |
| `GET` | `/api/v1/cb/seller/incentives/tasks/get` | 微前端 | `GetIncentiveSellerTask` |
| `GET` | `/api/v1/cb/seller/incentives/unclaimed/get` | 微前端 | `GetUnclaimedIncentives` |
| `POST` | `/api/v1/seller/outreach/callback` | 微前端 | `OutreachCallBack` |
| `POST` | `/api/v1/seller/outreach/prompt/update_prompt_ts` | 微前端 | `UpdatePromptTS` |
| `?` | `/api/v1/seller/outreach/task_message/latest` | 微前端 | `ListLatestTaskMsg` |
| `?` | `/api/v1/seller/outreach/task_message/list` | 微前端 | `ListTaskMsg` |
| `?` | `/api/v1/seller/outreach/task_message/pull` | 微前端 | `PullTaskMsgByCategory` |
| `?` | `/api/v1/seller/outreach/task_message/unread_get` | 微前端 | `MGetUnReadTaskMsg` |
| `POST` | `/api/v1/seller/sell/mission/widget/dismiss` | 微前端 | `DismissSellerMissionWidget` |
| `POST` | `/api/v1/seller/sell/mission/widget/get` | 微前端 | `GetSellerMissionWidget` |
| `?` | `/api/v1/seller/sell/mission_vo/get` | 微前端 | `GetSellerMissionVO` |
| `?` | `/widget/api/v1/seller/outreach/task_message/latest` | 微前端 | `ListLatestTaskMsgForWidget` |
| `?` | `/widget/api/v1/seller/outreach/task_message/list` | 微前端 | `ListTaskMsgForWidget` |
| `?` | `/widget/api/v1/seller/outreach/task_message/pull` | 微前端 | `PullTaskMsgByCategoryForWidget` |
| `POST` | `/widget/api/v1/seller/outreach/task_message/unread_get` | 微前端 | `MGetUnReadTaskMsgForWidget` |
| `POST` | `/widget/api/v1/seller/sell/mission/widget/dismiss` | 微前端 | `WidgetDismissSellerMissionWidget` |
| `POST` | `/widget/api/v1/seller/sell/mission/widget/get` | 微前端 | `WidgetGetSellerMissionWidget` |

## 开店 / 入驻清单（17）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/seller/open_shop/v2/batch_create_seller` | 财务bundle | `BatchCreateSeller` |
| `POST` | `/api/v1/seller/open_shop/v2/batch_submit` | 财务bundle | `BatchSubmitOpenShop` |
| `POST` | `/api/v1/seller/open_shop/v2/draft/get` | 微前端,微前端,财务bundle | `GetOpenShopDraft` |
| `POST` | `/api/v1/seller/open_shop/v2/draft/save` | 微前端,微前端,财务bundle | `SaveOpenShopDraft` |
| `POST` | `/api/v1/seller/open_shop/v2/register_create_seller` | 微前端,微前端,财务bundle | `RegisterCreateSeller` |
| `POST` | `/api/v1/seller/open_shop/v2/shop_name/verify` | 微前端,微前端,财务bundle | `VerifyShopName` |
| `GET` | `/api/v1/seller/open_shop/v2/state/get` | 微前端,微前端,财务bundle | `GetOpenShopState` |
| `POST` | `/api/v1/seller/open_shop/v2/state/list` | 微前端,微前端,财务bundle | `GetOpenShopStateList` |
| `POST` | `/api/v1/seller/open_shop/v2/state/list/all` | 财务bundle | `GetAllOpenShopStateList` |
| `POST` | `/api/v1/seller/open_shop/v2/submit` | 微前端,微前端,财务bundle | `SubmitOpenShop` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/draft/get` | 微前端,微前端,财务bundle | `WidgetGetOpenShopDraft` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/draft/save` | 微前端,微前端,财务bundle | `WidgetSaveOpenShopDraft` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/register_create_seller` | 微前端,微前端,财务bundle | `WidgetRegisterCreateSeller` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/shop_name/verify` | 微前端,微前端,财务bundle | `WidgetVerifyShopName` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/state/get` | 微前端,微前端,财务bundle | `WidgetGetOpenShopState` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/state/list` | 微前端,微前端,财务bundle | `WidgetGetOpenShopStateList` |
| `POST` | `/widget/api/v1/seller/open_shop/v2/submit` | 微前端,微前端,财务bundle | `WidgetSubmitOpenShop` |

## 平台基础设施（47）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `?` | `/api/feelgood/v1/answer` | 联盟bundle |  |
| `GET` | `/api/v1/address_component/config` | 微前端,微前端,微前端,财务bundle | `GetAddressComponentConfig` |
| `GET` | `/api/v1/app/common/get` | 微前端,微前端,微前端,财务bundle | `GetAppCommon` |
| `GET` | `/api/v1/arch/config_center_gw/get_config` | 微前端,财务bundle | `GetConfig` |
| `GET` | `/api/v1/arch/config_center_gw/mget_config_by_app_name` | 微前端,微前端,微前端,财务bundle | `MGetConfigByAppName` |
| `GET` | `/api/v1/arch/config_center_gw/mget_config_by_config_name` | 微前端,财务bundle | `MGetConfigByConfigName` |
| `?` | `/api/v1/bs/rt` | 联盟bundle |  |
| `?` | `/api/v1/bs/setting` | 联盟bundle |  |
| `?` | `/api/v1/common/cdn_rule` | 客户端 |  |
| `?` | `/api/v1/common/region_domain` | 微前端,微前端 |  |
| `POST` | `/api/v1/debugs/reverse/orders/list_main_orders` | 微前端 | `ListUserMainOrderIds` |
| `POST` | `/api/v1/dynamic_configs/get` | 微前端,微前端 | `GetDynamicConfigs` |
| `POST` | `/api/v1/i18n_conf/currency/format_currency` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `FormatCurrency` |
| `POST` | `/api/v1/i18n_conf/currency/format_currency_v2` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `FormatCurrencyV2` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_currency_code` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetCurrencyByCurrencyCode` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_geo_name_id` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetCurrencyByGEONameID` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_by_region_code` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetCurrencyByRegionCode` |
| `GET` | `/api/v1/i18n_conf/currency/get_currency_list` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetCurrencySupportCurrencyList` |
| `GET` | `/api/v1/i18n_conf/currency/get_region_list` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetCurrencySupportRegionList`, `GetDSTResult` |
| `POST` | `/api/v1/i18n_conf/datetime/format_locale` | 微前端,微前端,微前端,联盟bundle,财务bundle | `FormatLocale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_locale` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetLanguageByLocale` |
| `GET` | `/api/v1/i18n_conf/language/get_language_by_region_code` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetLanguageByRegionCode` |
| `GET` | `/api/v1/i18n_conf/language/get_locales_by_region_code` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetLocalesByRegionCode` |
| `GET` | `/api/v1/i18n_conf/region/get_eu_region_info` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetEuRegionInfo` |
| `GET` | `/api/v1/i18n_conf/timezone/get_default_timezone` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetDefaultTimezone` |
| `POST` | `/api/v1/i18n_conf/timezone/get_dst_result` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetDSTResult` |
| `GET` | `/api/v1/i18n_conf/timezone/get_exact_timezone` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetExactTimezone` |
| `GET` | `/api/v1/i18n_conf/timezone/get_icann_timezone` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetIANATimezone` |
| `GET` | `/api/v1/i18n_conf/timezone/get_region_timezone_info` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetRegionTimezoneInfo`, `GetUTCOffsetHour` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetUTCOffset` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_hour` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetUTCOffsetHour` |
| `GET` | `/api/v1/i18n_conf/timezone/get_utc_offset_sec` | 微前端,微前端,微前端,微前端,微前端,联盟bundle,财务bundle | `GetUTCOffsetSec` |
| `POST` | `/api/v1/seller/common/check_verification_code` | 微前端,微前端,微前端,微前端,财务bundle | `CommonCheckVerificationCode` |
| `GET` | `/api/v1/seller/common/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSeller` |
| `POST` | `/api/v1/seller/common/send_verification_code` | 微前端,微前端,微前端,微前端,财务bundle | `CommonSendVerificationCode` |
| `POST` | `/api/v1/seller/feelgood/access_token/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetFeelGoodAccessToken` |
| `?` | `/api/v1/sentry_verify/get_idv` | 联盟bundle |  |
| `?` | `/api/v1/sentry_verify/verify_idv` | 联盟bundle |  |
| `GET` | `/api/v1/webapp/seller/common/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSellerWebApp` |
| `?` | `/api/v2/sitebuilder` | 联盟bundle |  |
| `POST` | `/api/v3/init/session/core` | 微前端 | `InitSessionCore` |
| `POST` | `/api/v3/init/session/feature` | 微前端 | `InitSessionFeature` |
| `POST` | `/common/current_timestamp/get` | 联盟bundle |  |
| `POST` | `/user_info/common/v1/web_sdk_init` | 微前端 |  |
| `?` | `/v1/user/webid` | 联盟bundle |  |
| `POST` | `/widget/api/v1/debugs/reverse/orders/list_main_orders` | 微前端 | `ListUserMainOrderIdsForWidget` |
| `POST` | `/widget/api/v1/dynamic_configs/get` | 微前端,微前端 | `GetDynamicConfigsForWidget` |

## 其他 / 未分类（326）

| 方法 | 路径 | 来源 | 调用点 |
|---|---|---|---|
| `POST` | `/api/v1/app/seller/cancel_conds/verify` | 微前端 | `VerifyAppCancellationConds` |
| `POST` | `/api/v1/app/seller/cancel_criteria/get` | 微前端 | `GetAPPCancellationCriteria` |
| `?` | `/api/v1/bidding/bid/details` | 微前端 | `GetBidDetails` |
| `?` | `/api/v1/bidding/seller/bidding-config` | 微前端 | `GetBiddingConfig` |
| `?` | `/api/v1/bidding/seller/overview` | 微前端 | `GetBiddingSellerOverview` |
| `?` | `/api/v1/bidding/seller/spotlight` | 微前端 | `ListSellerBiddersSpotlight` |
| `?` | `/api/v1/bidding/top/spotlight` | 微前端 | `ListTopBiddersSpotlight` |
| `GET` | `/api/v1/cb/seller/start/tasks/status/get` | 微前端 | `GetPopStartTaskStatus` |
| `POST` | `/api/v1/config` | 微前端 | `InitSessionCore` |
| `?` | `/api/v1/imagex/url` | 微前端 | `InitSessionFeature` |
| `?` | `/api/v1/jwt` | 微前端 |  |
| `?` | `/api/v1/operation/form_open/user_page/query_by_code` | 微前端 |  |
| `GET` | `/api/v1/operation/fulfillment/logistic_detail/list` | 微前端,微前端,微前端 | `OperationListLogisticDetail` |
| `?` | `/api/v1/pearl/bff/cb-queen/dynamic-config/public/detail` | 微前端 |  |
| `POST` | `/api/v1/pop/product/category/list` | 微前端 | `GetProductCategoryListQuery` |
| `POST` | `/api/v1/resource/upload/token` | 微前端 |  |
| `?` | `/api/v1/selfsvc/getfaq` | 微前端 |  |
| `POST` | `/api/v1/seller/address_verify/verify` | 微前端,微前端 | `VerifyAddressByLogistics` |
| `GET` | `/api/v1/seller/ads_optimizers/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAdsOptimizersCard` |
| `GET` | `/api/v1/seller/affiliate_card/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAffiliateCard` |
| `GET` | `/api/v1/seller/allowed_geo_l0/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAllowedGeoL0` |
| `POST` | `/api/v1/seller/app/logistics_service/get_subscribable_service` | 微前端,微前端 | `GetSellerSubscribableServiceForApp` |
| `POST` | `/api/v1/seller/async_task/info/save` | 早期 |  |
| `POST` | `/api/v1/seller/audit/dismiss` | 微前端 | `DismissLatestAuditRecord` |
| `POST` | `/api/v1/seller/auth/tt_user_info/get` | 微前端,微前端 | `GetTTUserInfoByAuth` |
| `POST` | `/api/v1/seller/bag/create` | 微前端,微前端 | `CreateSellerBag` |
| `POST` | `/api/v1/seller/bag/create_file/create` | 微前端,微前端 | `ExportCreateBagFile` |
| `POST` | `/api/v1/seller/bag/create_file/download` | 微前端,微前端 | `DownloadCreateBagFile` |
| `POST` | `/api/v1/seller/bag/label/download` | 微前端,微前端 | `DownloadSellerBagLabel` |
| `POST` | `/api/v1/seller/bag/list` | 微前端,微前端 | `ListSellerBag` |
| `POST` | `/api/v1/seller/bag/package/download` | 微前端,微前端 | `DownloadSellerBagPackage` |
| `POST` | `/api/v1/seller/bag/package/list` | 微前端,微前端 | `ListSellerBagPackage` |
| `POST` | `/api/v1/seller/bag/providers/list` | 微前端,微前端 | `GetSellerBagShippingProviders` |
| `GET` | `/api/v1/seller/bonus_invoice_ability/get` | 微前端,微前端 | `GetBonusInvoiceAbility` |
| `POST` | `/api/v1/seller/bonus_invoice_ability/upsert` | 微前端,微前端 | `UpsertBonusInvoiceAbility` |
| `POST` | `/api/v1/seller/brand/get` | 微前端,微前端,微前端,财务bundle | `GetSellerBrand` |
| `?` | `/api/v1/seller/business_mode/get` | 微前端 | `GetSellerBusinessMode` |
| `POST` | `/api/v1/seller/c2b/qrcode/check` | 微前端,微前端 | `CheckC2BQRCodeStatus` |
| `POST` | `/api/v1/seller/c2b/trial_period/skip` | 微前端,微前端 | `SkipC2BTrialPeriod` |
| `POST` | `/api/v1/seller/capacity_template/create_or_update` | 微前端,微前端 | `CreateOrUpdateSellerCapacityTemplate` |
| `POST` | `/api/v1/seller/capacity_template/disable` | 微前端,微前端 | `DisableSellerCapacityTemplate` |
| `GET` | `/api/v1/seller/capacity_template/get` | 微前端,微前端 | `GetSellerCapacityTemplate` |
| `POST` | `/api/v1/seller/capacity_template/permission/check` | 微前端,微前端 | `CheckSellerCapacityPermission` |
| `GET` | `/api/v1/seller/cb/start/tasks/get` | 微前端 | `GetStartTaskList` |
| `POST` | `/api/v1/seller/check_and_cache_register_info` | 微前端,微前端,微前端,财务bundle | `CheckAndCacheRegisterInfo` |
| `POST` | `/api/v1/seller/check_invite_code` | 微前端,微前端,微前端,财务bundle | `CheckInviteCode` |
| `GET` | `/api/v1/seller/common_extra/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCommonExtra` |
| `?` | `/api/v1/seller/contract/detail` | 微前端 | `GetSellerContractDetail` |
| `?` | `/api/v1/seller/contract/list` | 微前端 | `ListSellerContracts` |
| `POST` | `/api/v1/seller/contract/notify/get` | 微前端 | `ListNotification` |
| `POST` | `/api/v1/seller/contract/notify/skip` | 微前端 | `SkipNotification` |
| `POST` | `/api/v1/seller/contract/sign` | 微前端 | `SignContract` |
| `POST` | `/api/v1/seller/creator_availability/verify` | 微前端,微前端,微前端,财务bundle | `VerifyCreatorAvailability` |
| `POST` | `/api/v1/seller/creator_info/verify` | 微前端,微前端,微前端,财务bundle | `VerifyCreatorInfo` |
| `POST` | `/api/v1/seller/district/match` | 微前端,财务bundle | `MatchDistrict` |
| `POST` | `/api/v1/seller/dynamic_commission/ads_tr_detail/list` | 早期 |  |
| `GET` | `/api/v1/seller/dynamic_commission/banner/get` | 早期 |  |
| `GET` | `/api/v1/seller/dynamic_commission/landing_page/get` | 早期 |  |
| `POST` | `/api/v1/seller/dynamic_commission/product_info/list` | 早期 |  |
| `GET` | `/api/v1/seller/dynamic_commission/unified_waiver/get` | 早期 |  |
| `GET` | `/api/v1/seller/ext_attr/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetSellerExtAttr` |
| `?` | `/api/v1/seller/fbt_opportunities/get` | 微前端 | `GetSellerFbtOpportunities` |
| `POST` | `/api/v1/seller/feishu/bind` | 微前端,微前端,微前端,财务bundle | `BindFeishu` |
| `GET` | `/api/v1/seller/feishu/get_binding_staff` | 微前端,微前端,微前端,财务bundle | `GetBindingFeishuStaff` |
| `POST` | `/api/v1/seller/feishu/get_invite_user` | 微前端,微前端,微前端,财务bundle | `GetInviteUserForFeishu` |
| `GET` | `/api/v1/seller/feishu/get_recommend_groups` | 微前端,微前端,微前端,财务bundle | `GetRecommendFeishuGroups` |
| `?` | `/api/v1/seller/get` | 微前端 | `GetSeller` |
| `POST` | `/api/v1/seller/get_all_unified_seller` | 微前端,微前端,微前端,财务bundle | `GetAllUnifiedSeller` |
| `POST` | `/api/v1/seller/get_invite_code` | 微前端,微前端,财务bundle | `GetInviteCode` |
| `POST` | `/api/v1/seller/get_main_account_safe_phone` | 微前端,微前端,微前端,财务bundle | `GetMainAccountSafePhone` |
| `POST` | `/api/v1/seller/get_register_source` | 微前端,微前端,微前端,财务bundle | `GetRegisterSource` |
| `POST` | `/api/v1/seller/get_subscription_services` | 微前端,微前端,财务bundle | `GetSubscriptionServices` |
| `POST` | `/api/v1/seller/get_unread_download_task_count` | 微前端,微前端,微前端,财务bundle | `GetUnreadDownloadTaskCount` |
| `GET` | `/api/v1/seller/global_product_permission/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetGlobalProductPermission` |
| `GET` | `/api/v1/seller/global_seller_onboard_info/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetGlobalSellerOnboardInfo` |
| `POST` | `/api/v1/seller/global_seller_withdraw/cancel` | 微前端 | `CancelGlobalSellerWithdraw` |
| `POST` | `/api/v1/seller/global_seller_withdraw/confirm` | 微前端 | `ConfirmGlobalSellerWithdraw` |
| `POST` | `/api/v1/seller/global_seller_withdraw/get` | 微前端 | `GetGlobalSellerWithdraw` |
| `POST` | `/api/v1/seller/global_seller_withdraw/publicity_period_open` | 微前端 | `OpenGlobalSellerWithdrawPublicityPeriod` |
| `POST` | `/api/v1/seller/global_shop_name/verify` | 微前端,财务bundle | `VerifyGlobalShopName` |
| `POST` | `/api/v1/seller/go_seller_center` | 微前端,微前端,微前端,微前端,财务bundle | `GoSellerCenter` |
| `POST` | `/api/v1/seller/h5/register/reach` | 微前端,财务bundle | `ReachSellerAfterRegisterForH5Optimization` |
| `POST` | `/api/v1/seller/help_info/course_detail/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetCourseDetail` |
| `GET` | `/api/v1/seller/help_info/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetHelpInfo` |
| `GET` | `/api/v1/seller/help_info/knowledge_detail/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetKnowledgeDetail` |
| `POST` | `/api/v1/seller/holiday_mode/list` | 微前端,微前端,微前端,财务bundle | `ListHolidayMode` |
| `POST` | `/api/v1/seller/holiday_mode/set` | 微前端,微前端,微前端,财务bundle | `SetHolidayMode` |
| `GET` | `/api/v1/seller/incentives/overview/get` | 微前端,微前端,早期 | `GetIncentivesOverview` |
| `?` | `/api/v1/seller/incentives/tasks/list` | 微前端,微前端 | `ListIncentivesTasks` |
| `POST` | `/api/v1/seller/info/check` | 微前端,微前端 | `CheckSellerInfo` |
| `GET` | `/api/v1/seller/livecenter/category/get` | 微前端 | `GetCategory` |
| `GET` | `/api/v1/seller/livecenter/livestream/detail/get` | 微前端 | `GetLivestreamCenterDetail` |
| `GET` | `/api/v1/seller/livecenter/livestream/summary/get` | 微前端 | `GetLivestreamCenterSummary` |
| `GET` | `/api/v1/seller/livecenter/video/detail/get` | 微前端 | `GetShortVideoCenterDetail` |
| `POST` | `/api/v1/seller/livecenter/video_feed/list` | 微前端 | `ListVideoFeed` |
| `POST` | `/api/v1/seller/livestream/event/post` | 微前端 | `PostEvent` |
| `GET` | `/api/v1/seller/locales/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetLocales` |
| `POST` | `/api/v1/seller/logistics/service_performance` | 微前端,微前端 | `GetSellerLogisticsPerformance` |
| `POST` | `/api/v1/seller/logistics/shop_performance` | 微前端,微前端 | `GetSellerShopPerformance` |
| `POST` | `/api/v1/seller/logistics/switch_option_for_warehouse` | 微前端,微前端 | `SwitchOptionForWarehouse` |
| `POST` | `/api/v1/seller/logistics_details/get_fail_reason` | 微前端,微前端 | `GetFailReasons` |
| `POST` | `/api/v1/seller/logistics_mode/set` | 微前端,微前端,微前端,财务bundle | `SetSellerPreferLogisticsMode` |
| `POST` | `/api/v1/seller/logistics_service/active_seller_subscription` | 微前端,微前端 | `ActiveSellerSubscription` |
| `POST` | `/api/v1/seller/logistics_service/address/cbt_available_check` | 微前端 | `CheckAddrCBTAvailable` |
| `POST` | `/api/v1/seller/logistics_service/banned_option/get` | 微前端,微前端 | `GetSellerBannedOption` |
| `POST` | `/api/v1/seller/logistics_service/batch_get_subscribable_service` | 微前端 | `BatchGetSellerSubscribableService` |
| `POST` | `/api/v1/seller/logistics_service/cbt_available_check` | 微前端,微前端 | `CheckCBTAvailable` |
| `POST` | `/api/v1/seller/logistics_service/cbt_downgrade` | 微前端,微前端 | `DowngradeCBT2Real4pl` |
| `POST` | `/api/v1/seller/logistics_service/disable_subscribed_service` | 微前端,微前端 | `DisableSellerSubscribedService` |
| `POST` | `/api/v1/seller/logistics_service/eu_banned_option/get` | 微前端 | `GetEuSellerBannedOption` |
| `POST` | `/api/v1/seller/logistics_service/exit_new_4pl` | 微前端,微前端 | `ExitNew4PLService` |
| `POST` | `/api/v1/seller/logistics_service/get_eu_global_seller_subscribable_service` | 微前端 | `GetEuGlobalSellerSubscribableService` |
| `POST` | `/api/v1/seller/logistics_service/get_service_list` | 微前端 | `GetServiceList` |
| `POST` | `/api/v1/seller/logistics_service/get_subscribable_service` | 微前端,微前端 | `GetSellerSubscribableService` |
| `POST` | `/api/v1/seller/logistics_service/get_subscribed_aggregated_data` | 微前端,微前端 | `GetSellerSubscribedAggregatedData` |
| `POST` | `/api/v1/seller/logistics_service/get_subscribed_service` | 微前端,微前端 | `GetSellerSubscribedService` |
| `POST` | `/api/v1/seller/logistics_service/join_new_4pl` | 微前端,微前端 | `JoinNew4PLService` |
| `POST` | `/api/v1/seller/logistics_service/m_update_subscribe_service` | 微前端,微前端 | `MUpdateSubscribeServices` |
| `POST` | `/api/v1/seller/logistics_service/real4pl_join_register/status` | 微前端,微前端 | `GetReal4plJoinRegisterStatus` |
| `POST` | `/api/v1/seller/logistics_service/real4pl_join_register/warehouse/status` | 微前端,微前端 | `GetReal4plJoinWarehouseRegisterStatus` |
| `POST` | `/api/v1/seller/logistics_service/subscribe_service` | 微前端,微前端 | `SubscribeService` |
| `POST` | `/api/v1/seller/logistics_service/subscribe_service_auto` | 微前端,微前端 | `SubscribeServiceAuto` |
| `POST` | `/api/v1/seller/logistics_service/warehouse/prefer_provider/check` | 微前端 | `CheckWarehousePreferProvider` |
| `POST` | `/api/v1/seller/logistics_service/warehouse/prefer_provider/get` | 微前端 | `GetWarehousePreferProvider` |
| `POST` | `/api/v1/seller/logistics_trackingno/mget_match_providers` | 微前端,微前端 | `MGetMatchProviders` |
| `POST` | `/api/v1/seller/logout_seller_center` | 微前端,微前端,财务bundle | `LogoutSellerCenter` |
| `POST` | `/api/v1/seller/mall_status/apply` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveMallStatus` |
| `POST` | `/api/v1/seller/mall_status/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetMallStatus` |
| `POST` | `/api/v1/seller/marketing_opt/set` | 微前端,微前端,微前端,财务bundle | `SetMarketingOption` |
| `POST` | `/api/v1/seller/multi_seller_bind` | 微前端,微前端,微前端,财务bundle | `MultiSellerBind` |
| `POST` | `/api/v1/seller/namespace/badge_list/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetUnreadBadges` |
| `POST` | `/api/v1/seller/navigation_bar/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetNavigationBar` |
| `POST` | `/api/v1/seller/navigation_bar/read` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ReadNavigationBar` |
| `POST` | `/api/v1/seller/network/country/check` | 微前端,财务bundle | `NetworkCountryCheck` |
| `POST` | `/api/v1/seller/org_account/bind` | 微前端,微前端 | `BindOrgAccount` |
| `POST` | `/api/v1/seller/org_account/list` | 微前端,微前端 | `ListOrgAccount` |
| `POST` | `/api/v1/seller/org_account/verify` | 微前端,微前端 | `VerifyOrgAccount` |
| `POST` | `/api/v1/seller/overview_metrics/get` | 微前端 | `GetSellerOverviewMetrics` |
| `POST` | `/api/v1/seller/package/list` | 微前端,微前端 | `ListSellerPackage` |
| `POST` | `/api/v1/seller/package/overview/count` | 微前端,微前端 | `CountPackageOverview` |
| `POST` | `/api/v1/seller/package/tag/update` | 微前端,微前端 | `MUpdatePackageTag` |
| `GET` | `/api/v1/seller/payment_manage_link/get` | 微前端,微前端,微前端,财务bundle | `GetPaymentManageLink` |
| `POST` | `/api/v1/seller/pc/register/reach` | 微前端,财务bundle | `ReachSellerAfterRegisterForPCOptimization` |
| `GET` | `/api/v1/seller/permissions/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetPermissions` |
| `GET` | `/api/v1/seller/pipo_scene_link/get` | 微前端,微前端,微前端,财务bundle | `GetPipoSceneLink` |
| `POST` | `/api/v1/seller/pkg_center/bag/tab` | 微前端,微前端 | `GetPkgCenterBagTab` |
| `POST` | `/api/v1/seller/pkg_center/bag/track_details` | 微前端,微前端 | `GetBagTrackDetails` |
| `POST` | `/api/v1/seller/poll/init` | 微前端 | `Init` |
| `POST` | `/api/v1/seller/poll/long` | 微前端 | `LongPoll` |
| `POST` | `/api/v1/seller/poll/msg/ack` | 微前端 | `MsgAck` |
| `?` | `/api/v1/seller/poll/short` | 微前端 | `ShortPoll` |
| `POST` | `/api/v1/seller/postcode/format/verify` | 微前端,财务bundle | `VerifyPostcodeFormat` |
| `POST` | `/api/v1/seller/postcode/verify` | 微前端,财务bundle | `VerifyPostcode` |
| `POST` | `/api/v1/seller/prediction` | 微前端 | `GetPrediction` |
| `POST` | `/api/v1/seller/processing_time/get` | 微前端,微前端 | `GetSellerProcessingTimeConf` |
| `POST` | `/api/v1/seller/processing_time/set` | 微前端,微前端 | `SetSellerProcessingTimeConf` |
| `POST` | `/api/v1/seller/program/get` | 微前端,微前端 | `GetSellerProgramStatus` |
| `POST` | `/api/v1/seller/program/update` | 微前端,微前端 | `UpdateSellerProgramStatus` |
| `POST` | `/api/v1/seller/provider/get_agreement_license` | 微前端,微前端 | `GetProviderAgreementLicense` |
| `POST` | `/api/v1/seller/provider/register_account` | 微前端,微前端 | `RegisterProviderAccount` |
| `POST` | `/api/v1/seller/register/check` | 微前端,财务bundle | `NetworkCheck` |
| `POST` | `/api/v1/seller/register_account_for_seller_center` | 微前端,微前端,微前端,财务bundle | `RegisterContactForSellerCenter` |
| `POST` | `/api/v1/seller/register_contact_for_brand_hosting` | 微前端,微前端,微前端,财务bundle | `RegisterContactForBrandHosting` |
| `POST` | `/api/v1/seller/registration/get_details` | 微前端,微前端 | `GetSellerRegistrationDetails` |
| `POST` | `/api/v1/seller/registration/get_status` | 微前端,微前端 | `GetSellerRegistrationStatus` |
| `POST` | `/api/v1/seller/registration/register` | 微前端,微前端 | `RegisterSeller` |
| `POST` | `/api/v1/seller/sandbox_full_onboard/v2/submit` | 微前端,微前端,财务bundle | `SubmitSandboxFullOnboard` |
| `POST` | `/api/v1/seller/search/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GlobalSearchByKeywords` |
| `GET` | `/api/v1/seller/search_query_suggestion/get` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `GetQuerySuggestion` |
| `POST` | `/api/v1/seller/sell/app_sub_page/get` | 微前端 | `GetAppSubPage` |
| `?` | `/api/v1/seller/sell/config/get` | 微前端 | `GetSellOnTTConfig` |
| `GET` | `/api/v1/seller/sell/inspiration/get` | 微前端 | `GetInspirationInfo` |
| `POST` | `/api/v1/seller/sell/resource/pack` | 微前端 | `PackResource` |
| `GET` | `/api/v1/seller/sell/sub_page/get` | 微前端 | `GetSubPage` |
| `GET` | `/api/v1/seller/sell/tips/get` | 微前端 | `GetTips` |
| `GET` | `/api/v1/seller/sell/v2/benchmark/get` | 微前端 | `GetBenchmarkData` |
| `POST` | `/api/v1/seller/sell/v2/detail/get` | 微前端 | `GetSellOnTiktokV2MainPage` |
| `GET` | `/api/v1/seller/sell/v2/follow_item/get` | 微前端 | `GetFollowItemList` |
| `GET` | `/api/v1/seller/sell/v2/follow_item/update` | 微前端 | `SetFollowItemList` |
| `POST` | `/api/v1/seller/sell/v2/plan/update` | 微前端 | `SetSellerPlan` |
| `POST` | `/api/v1/seller/sell/v2/seller_action/event/post` | 微前端 | `PostActionEvent` |
| `POST` | `/api/v1/seller/sell/v2/seller_action/update_progress` | 微前端 | `UpdateSellerActionCondProgress` |
| `GET` | `/api/v1/seller/sell/v2/suggestion_history/get` | 微前端 | `GetSuggestionHistory` |
| `GET` | `/api/v1/seller/sell/v2/weekly_report/get` | 微前端 | `GetWeeklyReport` |
| `GET` | `/api/v1/seller/sell/v3/algo/mission/list` | 微前端 | `GetAlgoSellerMission` |
| `GET` | `/api/v1/seller/sell/v3/detail/get` | 微前端 | `GetSellOnTiktokV3` |
| `GET` | `/api/v1/seller/sell/v3/history/get` | 微前端 | `GetSellerTaskHistory` |
| `?` | `/api/v1/seller/sell/v4/detail/get` | 微前端 | `GetSellOnTiktokV4` |
| `?` | `/api/v1/seller/sell/v4/mission_pool/get` | 微前端 | `GetSellerMissionPool` |
| `GET` | `/api/v1/seller/sell/ways/get` | 微前端 | `GetWaysToSellList` |
| `POST` | `/api/v1/seller/seller_delivery_blocker/create_or_update` | 微前端,微前端 | `MCreateOrUpdateSellerDeliveryBlocker` |
| `POST` | `/api/v1/seller/seller_delivery_blocker/get_by_warehouse` | 微前端,微前端 | `GetSellerDeliveryBlockerByWarehouse` |
| `POST` | `/api/v1/seller/seller_delivery_blocker/get_region_config` | 微前端,微前端 | `GetSellerDeliveryBlockerRegionConfig` |
| `GET` | `/api/v1/seller/seller_financing_link/get` | 微前端,微前端,微前端,财务bundle | `GetSellerFinancingLink` |
| `?` | `/api/v1/seller/seller_insurance_session/get` | 微前端,微前端,财务bundle | `GetSellerInsuranceSession` |
| `POST` | `/api/v1/seller/seller_map/read` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `ReadSellerMap` |
| `GET` | `/api/v1/seller/seller_wallet_link/get` | 微前端,微前端,微前端,财务bundle | `GetSellerWalletLink` |
| `POST` | `/api/v1/seller/shipment_provider/update` | 微前端,微前端,微前端,财务bundle | `UpdateSellerShipmentProvider` |
| `POST` | `/api/v1/seller/shipping/get_seller_visible_shipping_service` | 微前端,微前端 | `GetSellerVisibleShippingService` |
| `POST` | `/api/v1/seller/shipping/get_seller_warehouse_address` | 微前端,微前端 | `GetSellerWarehouseAddress` |
| `POST` | `/api/v1/seller/shipping/get_shipping_fee` | 微前端,微前端 | `GetFeeByShippingService` |
| `POST` | `/api/v1/seller/shop/get` | 微前端 | `GetShop` |
| `POST` | `/api/v1/seller/shop/seller_profile/submit` | 微前端 | `SubmitSellerProfile` |
| `?` | `/api/v1/seller/shop/setup/status/get` | 微前端 | `GetShopSetupStatus` |
| `POST` | `/api/v1/seller/shop/timezone/update` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `UpdateShopTimeZone` |
| `POST` | `/api/v1/seller/shop/vat/submit` | 微前端 | `SubmitVat` |
| `POST` | `/api/v1/seller/shop/warehouse/submit` | 微前端 | `SubmitWarehouse` |
| `GET` | `/api/v1/seller/shop_creator/get` | 微前端,微前端,微前端,财务bundle | `GetShopCreator` |
| `POST` | `/api/v1/seller/shop_creator/invitation/send` | 微前端,微前端,微前端,财务bundle | `SendShopCreatorInvitation` |
| `POST` | `/api/v1/seller/shop_creator/unbind` | 微前端,微前端,微前端,财务bundle | `UnbindShopCreator` |
| `POST` | `/api/v1/seller/shop_creator/unbound_roles/get` | 微前端,微前端,微前端,财务bundle | `GetShopCreatorUnboundRoles` |
| `POST` | `/api/v1/seller/shop_holiday_mode/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetShopHolidayMode` |
| `POST` | `/api/v1/seller/shop_holiday_mode/mget` | 微前端,微前端,财务bundle | `MGetShopHolidayMode` |
| `POST` | `/api/v1/seller/shop_holiday_mode/mset` | 微前端,微前端,微前端,财务bundle | `MSetShopHolidayMode` |
| `POST` | `/api/v1/seller/shop_holiday_mode/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SetShopHolidayMode` |
| `GET` | `/api/v1/seller/shop_limit_status/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetShopLimitStatus` |
| `POST` | `/api/v1/seller/shop_metrics/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetShopMetrics` |
| `POST` | `/api/v1/seller/shop_metrics/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveShopMetricsPreference` |
| `POST` | `/api/v1/seller/shop_name/update` | 微前端 | `UpdateShopName` |
| `POST` | `/api/v1/seller/shop_name/verify` | 微前端,微前端,财务bundle | `VerifyShopName` |
| `POST` | `/api/v1/seller/smart_bundle/get` | 微前端,微前端 | `GetSellerSmartBundleConfig` |
| `POST` | `/api/v1/seller/smart_bundle/status/get` | 微前端,微前端 | `GetSellerSmartBundleConfigStatus` |
| `POST` | `/api/v1/seller/smart_bundle/update` | 微前端,微前端 | `CreateOrUpdateSellerSmartBundleConfig` |
| `GET` | `/api/v1/seller/special_paylater_link/get` | 微前端,微前端,微前端,财务bundle | `GetSpecialPayLaterLink` |
| `POST` | `/api/v1/seller/tags/click/save` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `SaveTagsClickEvent` |
| `POST` | `/api/v1/seller/tags/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetTags` |
| `POST` | `/api/v1/seller/tax_num/get` | 微前端,微前端,微前端,财务bundle | `GetSellerTaxV2` |
| `POST` | `/api/v1/seller/tax_num/set` | 微前端,微前端,微前端,财务bundle | `SetSellerTaxV2` |
| `POST` | `/api/v1/seller/tax_registered_number/update` | 微前端,微前端,微前端,财务bundle | `UpdateSellerTaxRegisterNum` |
| `POST` | `/api/v1/seller/term/set` | 微前端,微前端,微前端,微前端,微前端,财务bundle | `TermAccept` |
| `POST` | `/api/v1/seller/ticket_token/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetTicketToken` |
| `POST` | `/api/v1/seller/tools` | 微前端,微前端,微前端,微前端,财务bundle | `CommonTool` |
| `GET` | `/api/v1/seller/trademark/brand_name/get` | 微前端,微前端,微前端,财务bundle | `GetBrandName` |
| `POST` | `/api/v1/seller/trademark/del` | 微前端,微前端,微前端,财务bundle | `DelTrademark` |
| `POST` | `/api/v1/seller/trademark/detail` | 微前端,微前端,微前端,财务bundle | `DetailTrademark` |
| `POST` | `/api/v1/seller/trademark/list` | 微前端,微前端,微前端,财务bundle | `ListTrademark` |
| `GET` | `/api/v1/seller/trademark/permission/get` | 微前端,微前端,微前端,财务bundle | `GetTrademarkPermission` |
| `GET` | `/api/v1/seller/trademark/receipt/brand/get` | 微前端,微前端,微前端,财务bundle | `GetReceiptBrandList` |
| `POST` | `/api/v1/seller/trademark/submit` | 微前端,微前端,微前端,财务bundle | `SubmitTrademark` |
| `POST` | `/api/v1/seller/trademark/submit_profile/get` | 微前端,微前端,微前端,财务bundle | `GetSubmitTrademarkProfile` |
| `GET` | `/api/v1/seller/trademark/valid` | 微前端,微前端,微前端,财务bundle | `ValidTrademark` |
| `POST` | `/api/v1/seller/update` | 微前端 | `UpdateShopLogo` |
| `POST` | `/api/v1/seller/user/check_user_auth` | 微前端,微前端,微前端,微前端,财务bundle | `CheckUserAuth` |
| `POST` | `/api/v1/seller/user/get_info` | 微前端,微前端,微前端,微前端,财务bundle | `GetUserInfo` |
| `POST` | `/api/v1/seller/white_list/batch_check` | 微前端,微前端 | `BatchCheckWhiteList` |
| `POST` | `/api/v1/seller/white_list/check` | 微前端,微前端 | `CheckWhiteList` |
| `POST` | `/api/v1/seller/widget/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetWidget` |
| `POST` | `/api/v1/seller/withdraw/cancel` | 微前端 | `CancelSellerWithdraw` |
| `POST` | `/api/v1/seller/withdraw/get` | 微前端 | `GetSellerWithdraw` |
| `POST` | `/api/v1/seller/withdraw/promote` | 微前端 | `PromoteSellerWithdraw` |
| `POST` | `/api/v1/seller/withdraw/publicity_period/open` | 微前端 | `OpenPublicityPeriod` |
| `POST` | `/api/v1/seller/x_data_delivery/performance_data` | 微前端,微前端 | `GetSellerXDayDeliveryPerformanceData` |
| `POST` | `/api/v1/seller/x_day_delivery/attribution/get` | 微前端 | `GetSellerXDayDeliveryAttribution` |
| `?` | `/api/v1/seller/x_day_delivery/attribution_gray/get` | 微前端 | `GetSellerXDayDeliveryAttributionGray` |
| `POST` | `/api/v1/seller/x_day_delivery/opportunity_lane` | 微前端 | `GetSellerXDayDeliveryOpportunityLane` |
| `POST` | `/api/v1/seller/xdd_auto_enroll_task/get` | 微前端 | `GetSellerXDDAutoEnrollTask` |
| `POST` | `/api/v1/seller/xdd_auto_enroll_task/update` | 微前端 | `UpdateSellerXDDAutoEnrollTask` |
| `POST` | `/api/v1/seller_warehouse/list/all_operation_time` | 微前端,微前端 | `ListAllSellerWarehouseOperationTime` |
| `POST` | `/api/v1/seller_warehouse/save/operation_time` | 微前端,微前端 | `SaveSellerWarehouseOperationTime` |
| `POST` | `/api/v1/seller_warehouse/x_data_delivery/performance_data` | 微前端,微前端 | `GetSellerWarehouseXDayDeliveryPerformanceData` |
| `POST` | `/api/v1/shop/profile/complaint_address/update` | 微前端,财务bundle | `UpdateComplaintAddress` |
| `POST` | `/api/v1/shop/profile/contact/get` | 微前端,财务bundle | `GetShopContactInfo` |
| `POST` | `/api/v1/shop/warehouses/add` | 微前端,微前端 | `AddShopWarehouses` |
| `POST` | `/api/v1/shop/warehouses/default/batch_set` | 微前端 | `BatchSetDefaultWarehouse` |
| `POST` | `/api/v1/shop/warehouses/default/set` | 微前端,微前端 | `SetDefaultWarehouse` |
| `GET` | `/api/v1/shop/warehouses/get` | 微前端,微前端 | `GetShopWarehouses` |
| `POST` | `/api/v1/shop/warehouses/update` | 微前端,微前端 | `UpdateShopWarehouses` |
| `POST` | `/api/v1/token` | 微前端 | `OpenScreenContent` |
| `POST` | `/api/v1/webapp/seller/check_user_auth` | 微前端,微前端,微前端,微前端,财务bundle | `CheckUserAuthWebApp` |
| `GET` | `/api/v1/webapp/seller/get_all_unified_seller` | 微前端,微前端,微前端,财务bundle | `GetAllUnifiedSellerWebApp` |
| `POST` | `/api/v2/intelligent_i18n/open_screen_init` | 微前端 | `GetOpenScreenI18nInit` |
| `?` | `/api/v2/nodes` | 微前端 |  |
| `POST` | `/api/v3/intelligent/question` | 微前端 | `TakeIntelligentQuestion` |
| `POST` | `/api/v3/open/screen/content` | 微前端 | `OpenScreenContent` |
| `POST` | `/api/v3/recommended/content` | 微前端 | `TakeRecommendedContent` |
| `POST` | `/api/v3/session/heartbeat` | 微前端 | `SessionHeartbeat` |
| `POST` | `/api/v3/session/takeaction` | 微前端 | `SessionTakeAction` |
| `POST` | `/api/v3/video/play_info` | 微前端 | `VideoPlayInfo` |
| `POST` | `/api/v3/video/upload_token` | 微前端 | `VideoUploadToken` |
| `POST` | `/baike/v2/api/highlight_ignore/set` | 微前端 |  |
| `GET` | `/bytemap/v1/config/region_profile` | 微前端,微前端 |  |
| `POST` | `/easesafe/oec_tax_qualification/upload` | 微前端 |  |
| `POST` | `/fbt/api/landing/add_seller_to_fbt_waitlist` | 微前端 |  |
| `GET` | `/fbt/api/landing/enroll_product_value_plus` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_all_value_plus_products` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_content_for_module` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_merchant_by_fs_seller` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_merchant_by_seller` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_merchant_onboarding_cost` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_seller_in_opt_out_from_free_shipping_status` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_seller_latest_enrollment_stats` | 微前端 |  |
| `POST` | `/fbt/api/landing/get_vat_status_by_fs_seller` | 微前端 |  |
| `POST` | `/fbt/api/landing/go_to_fbt` | 微前端 |  |
| `POST` | `/fbt/api/landing/print_goods_barcode` | 微前端 |  |
| `POST` | `/fbt/api/landing/search_content_by_keywords` | 微前端 |  |
| `GET` | `/instant/api/v1/product/product_creation/preload` | 早期,早期 |  |
| `GET` | `/maps/api/js` | 微前端,微前端 |  |
| `POST` | `/maps/api/key` | 微前端 |  |
| `POST` | `/pssresource/external/upload` | 微前端,微前端 |  |
| `GET` | `/v1/seller_warehouses/status` | 微前端 |  |
| `POST` | `/widget/api/v1/logistics/district/list` | 微前端,微前端,微前端,财务bundle | `WidgetListDistricts` |
| `GET` | `/widget/api/v1/product/local/product/subscribe/get` | 微前端 | `GetProductSubscribeForWidget` |
| `GET` | `/widget/api/v1/product/local/product/subscribe/save` | 微前端 | `SaveProductSubscribeForWidget` |
| `POST` | `/widget/api/v1/product/prohibited/words/check` | 微前端,早期,早期 | `CheckProhibitedWordsForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/batch_save` | 微前端,早期,早期 | `BatchCreateSizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/config_product` | 微前端,早期,早期 | `ConfigProductSizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/delete` | 微前端,早期,早期 | `DeleteSizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/edit` | 微前端,早期,早期 | `EditSizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/get_bind_info` | 微前端,早期,早期 | `GetSizeChartBindInfoForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/identify` | 微前端,早期,早期 | `IdentifySizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/list_product_type` | 微前端,早期,早期 | `ListSizeChartProductTypeForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/save` | 微前端,早期,早期 | `CreateSizeChartForWidget` |
| `POST` | `/widget/api/v1/product/size_chart/search` | 微前端,早期,早期 | `SearchSizeChartForWidget` |
| `GET` | `/widget/api/v1/seller/affiliate_card/get` | 微前端,微前端,微前端,微前端,财务bundle | `GetAffiliateCardForWidget` |
| `GET` | `/widget/api/v1/seller/livecenter/category/get` | 微前端 | `WidgetGetCategory` |
| `POST` | `/widget/api/v1/seller/livecenter/video_feed/list` | 微前端 | `WidgetListVideoFeed` |
| `POST` | `/widget/api/v1/seller/livestream/event/post` | 微前端 | `WidgetPostEvent` |
| `POST` | `/widget/api/v1/seller/marketing_opt/set` | 微前端,微前端,微前端,财务bundle | `WidgetSetMarketingOption` |
| `POST` | `/widget/api/v1/seller/postcode/format/verify` | 微前端,财务bundle | `WidgetVerifyPostcodeFormat` |
| `POST` | `/widget/api/v1/seller/postcode/verify` | 微前端,财务bundle | `WidgetVerifyPostcode` |
| `POST` | `/widget/api/v1/seller/sell/config/get` | 微前端 | `WidgetGetSellOnTTConfig` |
| `GET` | `/widget/api/v1/seller/sell/v3/algo/mission/list` | 微前端 | `WidgetGetAlgoSellerMission` |
| `GET` | `/widget/api/v1/seller/sell/v3/detail/get` | 微前端 | `WidgetGetSellOnTiktokV3` |
| `POST` | `/widget/api/v1/seller/warehouses/add` | 微前端,微前端,微前端,财务bundle | `AddSellerWarehousesForWidget` |
| `POST` | `/widget/api/v1/seller/white_list/check` | 微前端,微前端 | `CheckWhiteListForWidget` |
| `POST` | `/wsos_v2/oec_promotion_backends_file_system/upload` | 微前端 |  |
