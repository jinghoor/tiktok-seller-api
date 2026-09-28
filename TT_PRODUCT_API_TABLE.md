# TikTok 卖家中心 · 商品上架接口全表

自动生成自 `notes/tt_api_map_full.json`（从 7 个 API client bundle 静态提取）。
全量卖家中心接口 **568** 个，其中商品相关 **307** 个。

## 按业务域分组

| 业务域 | 接口数 |
|---|---|
| `global` | 44 |
| `optimize` | 40 |
| `oc` | 40 |
| `stock` | 32 |
| `local` | 21 |
| `product` | 13 |
| `size_chart` | 9 |
| `sku` | 6 |
| `multi_region_listing` | 6 |
| `seller_opportunity` | 6 |
| `brand` | 5 |
| `products` | 4 |
| `link` | 4 |
| `property` | 3 |
| `seller` | 3 |
| `gpr` | 3 |
| `spu` | 3 |
| `async_task` | 3 |
| `lock` | 3 |
| `comp` | 3 |
| `commission` | 3 |
| `bundles` | 3 |
| `creator_stock` | 3 |
| `category` | 2 |
| `desc` | 2 |
| `shipping_template` | 2 |
| `gpr_rule` | 2 |
| `image_translation_rule` | 2 |
| `external` | 2 |
| `diagnosis` | 2 |
| `category_rec` | 1 |
| `short_info_rec` | 1 |
| `guide` | 1 |
| `optimization` | 1 |
| `package` | 1 |
| `product_property_rec` | 1 |
| `product_name_rec` | 1 |
| `brand_rec` | 1 |
| `actions` | 1 |
| `gpr_overview` | 1 |
| `spuv2` | 1 |
| `bulletin` | 1 |
| `combo` | 1 |
| `tab` | 1 |
| `shipping` | 1 |
| `rp` | 1 |
| `growth_info` | 1 |
| `smart_publish` | 1 |
| `regions` | 1 |
| `msubmit` | 1 |
| `parcel` | 1 |
| `list` | 1 |
| `prohibited` | 1 |
| `download_instruction` | 1 |
| `images` | 1 |
| `promotion` | 1 |
| `logistics` | 1 |
| `guide_context` | 1 |
| `duplication` | 1 |
| `image` | 1 |
| `publish` | 1 |
| `recommend` | 1 |
| `growth_center` | 1 |

## global (44)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/global/async_task/create` | CreateGlobalTask (+1) |
| POST | `/api/v1/product/global/brand/create` | CreateBrand (+1) |
| POST | `/api/v1/product/global/draft/save` | SavaGlobalDraft (+1) |
| POST | `/api/v1/product/global/guide_context/get` | GetGuideContext (+1) |
| GET | `/api/v1/product/global/material_center/account` | GetAccount (+1) |
| POST | `/api/v1/product/global/material_center/account/initial` | InitialAccount (+1) |
| POST | `/api/v1/product/global/material_center/file/list` | ListFileView (+1) |
| POST | `/api/v1/product/global/material_center/folder/create` | CreateFolder (+1) |
| POST | `/api/v1/product/global/material_center/folder/delete` | MDeleteFolder (+1) |
| POST | `/api/v1/product/global/material_center/folder/edit` | EditFolder (+1) |
| POST | `/api/v1/product/global/material_center/image/segment` | SegmentImage (+1) |
| POST | `/api/v1/product/global/material_center/image_background/optimize` | OptimizeImageBackground (+1) |
| POST | `/api/v1/product/global/material_center/material/batch_create` | BatchCreateMaterial (+1) |
| POST | `/api/v1/product/global/material_center/material/create` | CreateMaterial (+1) |
| POST | `/api/v1/product/global/material_center/material/delete` | MDeleteMaterial (+1) |
| POST | `/api/v1/product/global/material_center/material/edit` | EditMaterial (+1) |
| POST | `/api/v1/product/global/material_center/material/move` | BatchMoveMaterial (+1) |
| POST | `/api/v1/product/global/material_center/material/query` | QueryMaterials (+1) |
| POST | `/api/v1/product/global/material_center/slice_switch` | SetVideoSliceSwitch (+1) |
| POST | `/api/v1/product/global/parcel/check` | CheckGlobalProductParcel (+1) |
| POST | `/api/v1/product/global/price/calculate` | CalculateGlobalPrice (+1) |
| POST | `/api/v1/product/global/price/limit` | GetGlobalPriceLimit (+1) |
| POST | `/api/v1/product/global/price/mcalculate` | MCalculateGlobalPrice (+1) |
| POST | `/api/v1/product/global/product/publish` | PublishGlobalProduct (+1) |
| POST | `/api/v1/product/global/product/save_and_publish` | SaveAndPublishProduct (+1) |
| POST | `/api/v1/product/global/product/save_live` | SaveLiveProduct (+1) |
| POST | `/api/v1/product/global/product/stock/edit` | EditProductStock (+1) |
| POST | `/api/v1/product/global/products/delete` | MDeleteGlobalProducts (+1) |
| GET | `/api/v1/product/global/regions/mget` | MGetGlobalRegions (+1) |
| POST | `/api/v1/product/global/size_chart/batch_save` | BatchCreateSizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/config_product` | ConfigProductSizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/delete` | DeleteSizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/edit` | EditSizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/get_bind_info` | GetSizeChartBindInfo (+1) |
| POST | `/api/v1/product/global/size_chart/identify` | IdentifySizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/list_product_type` | ListSizeChartProductType (+1) |
| POST | `/api/v1/product/global/size_chart/save` | CreateSizeChart (+1) |
| POST | `/api/v1/product/global/size_chart/search` | SearchSizeChart (+1) |
| POST | `/api/v1/product/global/sku/price/edit` | EditPrice (+1) |
| POST | `/api/v1/product/global/sku/stock/edit` | EditStock (+1) |
| POST | `/api/v1/product/global/spu/match` | MatchSpu (+1) |
| POST | `/api/v1/product/global/texts_translation/get` | MGetTextsTranslation (+1) |
| POST | `/api/v1/product/global/third_party/link` | LinkThirdPartyProduct (+1) |
| POST | `/api/v1/product/global/third_party/unlink` | UnLinkThirdPartyProduct (+1) |

## optimize (40)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/optimize/appeal` | ProductInfoAppeal (+1) |
| GET | `/api/v1/product/optimize/data/get` | GetOptimizationData (+1) |
| POST | `/api/v1/product/optimize/generate_suggestion` | GenerateProductSuggestion (+1) |
| POST | `/api/v1/product/optimize/generate_title` | GenerateSellerSEOTitle (+1) |
| GET | `/api/v1/product/optimize/hosting/auth/get` | GetHostingAuth (+1) |
| POST | `/api/v1/product/optimize/hosting/auth/update` | UpdateHostingAuth (+1) |
| POST | `/api/v1/product/optimize/hosting/scope/update` | UpdateProductHostingScope (+1) |
| POST | `/api/v1/product/optimize/manual_intervention/create` | CreateManualIntervention (+1) |
| POST | `/api/v1/product/optimize/manual_intervention/detail` | GetManualIntervention (+1) |
| POST | `/api/v1/product/optimize/manual_intervention/search` | SearchManualInterventions (+1) |
| GET | `/api/v1/product/optimize/meta/get` | GetOptimizationMeta (+1) |
| PUT | `/api/v1/product/optimize/multi_edit` | MEditOptimizedProduct (+1) |
| POST | `/api/v1/product/optimize/optimization_performance/charts` | GetOptimizationPerformanceCharts (+1) |
| POST | `/api/v1/product/optimize/optimization_record/list` | ListOptimizationRecord (+1) |
| POST | `/api/v1/product/optimize/optimization_record/update` | UpdateOptimizationRecord (+1) |
| POST | `/api/v1/product/optimize/optimization_record/{param}/rollback` | RollbackOptimizationRecord (+1) |
| GET | `/api/v1/product/optimize/overview/get` | GetOptimizationOverview (+1) |
| POST | `/api/v1/product/optimize/page/get` | GetToBeOptimizedProductPage (+1) |
| GET | `/api/v1/product/optimize/search_ops/categories` | ListSearchOpsShopCategories (+1) |
| POST | `/api/v1/product/optimize/search_ops/optimize_title` | OptimizeSearchOpsTitle (+1) |
| POST | `/api/v1/product/optimize/search_ops/preview_optimization` | PreviewSearchOpsOptimization (+1) |
| POST | `/api/v1/product/optimize/search_ops/preview_title` | PreviewSearchOpsTitle (+1) |
| POST | `/api/v1/product/optimize/search_ops/submit_optimization` | SubmitSearchOpsOptimization (+1) |
| POST | `/api/v1/product/optimize/search_ops/video_comments/recommend` | RecommendSearchOpsVideoComment (+1) |
| POST | `/api/v1/product/optimize/search_ops/video_config` | SaveSearchOpsVideoConfig (+1) |
| POST | `/api/v1/product/optimize/search_ops/video_product_relations/query` | QuerySearchOpsVideoProductRelations (+1) |
| POST | `/api/v1/product/optimize/search_ops/video_relations/validate` | ValidateSearchOpsVideoRelations (+1) |
| POST | `/api/v1/product/optimize/seller_detail/update` | UpdateSellerDetail (+1) |
| POST | `/api/v1/product/optimize/size_chart/construct` | GetConstructedSizeChart (+1) |
| POST | `/api/v1/product/optimize/size_chart/match` | CalculateProductSizeChartMatchedResult (+1) |
| POST | `/api/v1/product/optimize/size_chart/template_binding_info` | GetSizeChartTemplateBindingInfo (+1) |
| POST | `/api/v1/product/optimize/title_strategy/create` | CreateOptimizationStrategy (+1) |
| POST | `/api/v1/product/optimize/title_strategy/detail` | GetOptimizationStrategyDetail (+1) |
| POST | `/api/v1/product/optimize/title_strategy/evaluation/create` | CreateOptimizationStrategyEvaluation (+1) |
| POST | `/api/v1/product/optimize/title_strategy/evaluation/result` | GetOptimizationStrategyEvaluationResult (+1) |
| POST | `/api/v1/product/optimize/title_strategy/evaluation/review` | ReviewOptimizationStrategyEvaluation (+1) |
| POST | `/api/v1/product/optimize/title_strategy/search` | SearchOptimizationStrategy (+1) |
| POST | `/api/v1/product/optimize/title_strategy/status/update` | UpdateOptimizationStrategyStatus (+1) |
| POST | `/api/v1/product/optimize/title_strategy/update` | UpdateOptimizationStrategy (+1) |
| POST | `/api/v1/product/optimize/translate` | Translate (+1) |

## oc (40)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/oc/seller_product_opportunity/app_home/lead_top` | GetAppHomeLeadList |
| POST | `/api/v1/product/oc/seller_product_opportunity/app_home/pop/lead_top` | GetAppHomePOPLeadList |
| POST | `/api/v1/product/oc/seller_product_opportunity/auto_submit/set` | SetAutoSubmit |
| POST | `/api/v1/product/oc/seller_product_opportunity/contract/check` | CheckSignedSPOContract |
| POST | `/api/v1/product/oc/seller_product_opportunity/contract/sign` | SignSPOContract |
| GET | `/api/v1/product/oc/seller_product_opportunity/excel/relate/get` | GetRelateSPOProductTemplate |
| POST | `/api/v1/product/oc/seller_product_opportunity/excel/relate/upload` | UploadRelateSPOProduct |
| GET | `/api/v1/product/oc/seller_product_opportunity/exist/same/product/lead` | GetExistSameProductLead |
| POST | `/api/v1/product/oc/seller_product_opportunity/initial/list` | ListSPOInitial |
| POST | `/api/v1/product/oc/seller_product_opportunity/mark` | MarkSpo |
| GET | `/api/v1/product/oc/seller_product_opportunity/opportunity_type_by_region/get` | GetShowOpportunityTypeByRegion |
| POST | `/api/v1/product/oc/seller_product_opportunity/optimization_items_by_country/list` | ListOptimizationItemsByCountry |
| POST | `/api/v1/product/oc/seller_product_opportunity/optimization_tasks/update_status` | UpdateSPOOptimizationTaskStatus |
| POST | `/api/v1/product/oc/seller_product_opportunity/pop/filter/get` | GetPOPSellerShopFilter |
| POST | `/api/v1/product/oc/seller_product_opportunity/product/performance/Card` | GetSocMySubmissionProductPerformanceCard |
| POST | `/api/v1/product/oc/seller_product_opportunity/product/performance/list` | GetSocMySubmissionProductPerformanceList |
| POST | `/api/v1/product/oc/seller_product_opportunity/product/stock/update` | UpdateProductStock |
| POST | `/api/v1/product/oc/seller_product_opportunity/reasons/list` | ListSellerRejectSPOReasons |
| POST | `/api/v1/product/oc/seller_product_opportunity/recruit/mark` | RecruitMark |
| POST | `/api/v1/product/oc/seller_product_opportunity/reject` | SellerRejectSPO |
| POST | `/api/v1/product/oc/seller_product_opportunity/relate` | RelateProductToSPO |
| GET | `/api/v1/product/oc/seller_product_opportunity/seller/batch_listing/opportunity/count` | GetBatchListingOpportunityCount |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/batch_listing/task/create` | CreateBatchListingTask |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/brand/recommend` | BrandRecommend |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/eu/config` | GetEUSellerConfig |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/lead/detail` | GetLeadDetail |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/lead/list` | ListLead |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/lead/show_field` | GetLeadShowField |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/lead/tag/list` | ListLeadTag |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/leafcate/recommend` | LeafCateRecommend |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/new_shop_set_up/lead/list` | ListNewShopSetUpLead |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/pop/config` | GetPOPSellerConfig |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/report/summary` | SellerReportSummary |
| POST | `/api/v1/product/oc/seller_product_opportunity/seller/seasonal_festival/tag/list` | GetSeasonalFestivalTagList |
| GET | `/api/v1/product/oc/seller_product_opportunity/shop_experience_score/get` | GetShopExperienceScore |
| POST | `/api/v1/product/oc/seller_product_opportunity/shop_filter/get` | GetShopFilter |
| POST | `/api/v1/product/oc/seller_product_opportunity/submit/record/list` | GetSocMySubmissionSubmitRecordList |
| POST | `/api/v1/product/oc/seller_product_opportunity/tts_product/search` | SearchTtsProducts |
| POST | `/api/v1/product/oc/seller_product_opportunity/tts_product/trending/search` | SearchTrendingTtsProducts |
| POST | `/api/v1/product/oc/seller_product_opportunity/upload_details/get` | GetSPOUploadDetails |

## stock (32)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/stock/alert/export_reple_file` | ExportReplenishmentFile |
| POST | `/api/v1/product/stock/alert/query_export_progress` | QueryReplenishFileGenProgress |
| POST | `/api/v1/product/stock/alert/sales/forecast_option/update` | UpdateSalesForecastOption |
| POST | `/api/v1/product/stock/alert/set_seller_alert` | SetSellerAlertStock |
| POST | `/api/v1/product/stock/alert/set_stock` | SetInShopStock |
| POST | `/api/v1/product/stock/ckp/list` | ListCkpStock |
| POST | `/api/v1/product/stock/flow/list` | ListStockFlow |
| POST | `/api/v1/product/stock/list` | ListProductStock |
| POST | `/api/v1/product/stock/negative/check` | CheckNegative |
| POST | `/api/v1/product/stock/negative/close` | CloseNegative |
| POST | `/api/v1/product/stock/operation/query_task_progress` | QueryStockOperationSettingTask |
| POST | `/api/v1/product/stock/operation/update` | UpdateStockOperationSetting |
| POST | `/api/v1/product/stock/product/list` | ListProduct |
| POST | `/api/v1/product/stock/query/inventory_health` | QueryInventoryHealth |
| POST | `/api/v1/product/stock/query/sku` | QuerySKUStock |
| POST | `/api/v1/product/stock/query/warehouse/stock_sale_type` | QueryWarehouseStockSaleType |
| POST | `/api/v1/product/stock/restock/download_file` | DownloadRestockFile |
| POST | `/api/v1/product/stock/restock/query_history` | QueryRestockHistory |
| POST | `/api/v1/product/stock/restock/query_task_progress` | QueryRestockTaskProgress |
| POST | `/api/v1/product/stock/restock/upload_file` | UploadRestockFile |
| POST | `/api/v1/product/stock/restriction/delete` | DeleteRestriction |
| POST | `/api/v1/product/stock/restriction/detail/list` | ListRestrictionDetail |
| POST | `/api/v1/product/stock/restriction/list` | ListRestriction |
| POST | `/api/v1/product/stock/restriction/product/list` | ListRestrictionProduct |
| POST | `/api/v1/product/stock/restriction/query_task_progress` | QueryRestrictionTaskProgress |
| POST | `/api/v1/product/stock/restriction/update` | UpdateRestriction |
| POST | `/api/v1/product/stock/sku/count/list` | CountSKUType |
| POST | `/api/v1/product/stock/sku/list` | ListSKU |
| POST | `/api/v1/product/stock/sku/order/list` | ListSKUOrder |
| POST | `/api/v1/product/stock/status_count/list` | CountProductStockStatus |
| POST | `/api/v1/product/stock/unlink` | Unlink |
| POST | `/api/v1/product/stock/warehouse/deactivatable/check` | CheckWarehouseDeactivatable |

## local (21)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/local/bundle/create` | CreateLocalBundle (+1) |
| POST | `/api/v1/product/local/bundle/edit` | EditLocalBundle (+1) |
| POST | `/api/v1/product/local/bundles/list` | ListLocalBundles (+1) |
| POST | `/api/v1/product/local/draft/partial_edit` | PartialEditLocalDraft (+1) |
| POST | `/api/v1/product/local/draft/save` | SaveLocalDraft (+3) |
| POST | `/api/v1/product/local/edit/template` | GetProductLocalEditTemplate (+1) |
| POST | `/api/v1/product/local/edit_image/list` | ListEditImageProduct (+1) |
| GET | `/api/v1/product/local/has_edit_pending_product/get` | HasEditPendingProduct (+1) |
| POST | `/api/v1/product/local/image/save` | SaveLocalImageDraft (+1) |
| POST | `/api/v1/product/local/product/bulk_create` | CreateBulkLocalProduct (+1) |
| POST | `/api/v1/product/local/product/create` | CreateLocalProduct (+3) |
| POST | `/api/v1/product/local/product/edit` | EditLocalProduct (+3) |
| POST | `/api/v1/product/local/product/edit_description_prettify` | SubmitDescPrettification (+1) |
| POST | `/api/v1/product/local/product/multi_confirm` | MConfirmProducts (+1) |
| POST | `/api/v1/product/local/product/package/recommend/update` | BulkUpdateRecomProductPackage (+1) |
| POST | `/api/v1/product/local/product/partial/edit` | PartialEditLocalProduct (+1) |
| POST | `/api/v1/product/local/product/precheck` | PreCheckProduct (+1) |
| POST | `/api/v1/product/local/product/schema/get` | GetProductSchema (+1) |
| POST | `/api/v1/product/local/same_products/list` | ListLocalSameProducts (+1) |
| GET | `/api/v1/product/local/selling_tools` | GetSellingToolsPage (+1) |
| POST | `/api/v1/product/local/upload` | UploadCreateProduct (+1) |

## product (13)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/product/info/quality/calculate` | CalculateProductInfoQuality (+1) |
| POST | `/instant/api/v1/product/local/product/create` | CreateLocalInstantProduct (+1) |
| GET | `/instant/api/v1/product/product_creation/preload` | PreloadInstantProductCreation (+1) |
| POST | `/widget/api/v1/product/prohibited/words/check` | CheckProhibitedWordsForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/batch_save` | BatchCreateSizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/config_product` | ConfigProductSizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/delete` | DeleteSizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/edit` | EditSizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/get_bind_info` | GetSizeChartBindInfoForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/identify` | IdentifySizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/list_product_type` | ListSizeChartProductTypeForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/save` | CreateSizeChartForWidget (+1) |
| POST | `/widget/api/v1/product/size_chart/search` | SearchSizeChartForWidget (+1) |

## size_chart (9)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/size_chart/batch_save` | BatchCreateSizeChart (+1) |
| POST | `/api/v1/product/size_chart/config_product` | ConfigProductSizeChart (+1) |
| POST | `/api/v1/product/size_chart/delete` | DeleteSizeChart (+1) |
| POST | `/api/v1/product/size_chart/edit` | EditSizeChart (+1) |
| POST | `/api/v1/product/size_chart/get_bind_info` | GetSizeChartBindInfo (+1) |
| POST | `/api/v1/product/size_chart/identify` | IdentifySizeChart (+1) |
| POST | `/api/v1/product/size_chart/list_product_type` | ListSizeChartProductType (+1) |
| POST | `/api/v1/product/size_chart/save` | CreateSizeChart (+1) |
| POST | `/api/v1/product/size_chart/search` | SearchSizeChart (+1) |

## sku (6)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/sku/price/cal` | CalCrossBoardSKUPrice (+1) |
| POST | `/api/v1/product/sku/price/stocks/update` | UpdateSkuPriceStocks (+3) |
| POST | `/api/v1/product/sku/price/update` | UpdateSKUPrice (+1) |
| POST | `/api/v1/product/sku/prices/mcal` | MCalCrossBoardSKUPrices (+1) |
| POST | `/api/v1/product/sku/stocks/decrease` | DecreaseSKUStocks (+1) |
| POST | `/api/v1/product/sku/stocks/increase` | IncreaseSKUStocks (+1) |

## multi_region_listing (6)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/multi_region_listing/exchange_rate/get` | GetExchangeRateList (+1) |
| POST | `/api/v1/product/multi_region_listing/rp_manufacturer/list` | GetRpAndManufacturerList (+1) |
| POST | `/api/v1/product/multi_region_listing/rule/get` | MultiGetRegionRuleInfo (+1) |
| POST | `/api/v1/product/multi_region_listing/sku/price/stocks/update` | UpdateRegionSkuPriceStocks (+1) |
| POST | `/api/v1/product/multi_region_listing/tax_price_calc` | MCalPreTaxPrice2SalePrice (+1) |
| POST | `/api/v1/product/multi_region_listing/translate` | MTranslateContent (+1) |

## seller_opportunity (6)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/seller_opportunity/collect` | CollectItem |
| POST | `/api/v1/product/seller_opportunity/niche/get_suggested_word` | GetSuggestedWord |
| POST | `/api/v1/product/seller_opportunity/niche/list` | ListNiches |
| POST | `/api/v1/product/seller_opportunity/niche/list_collected` | ListCollectedNiches |
| POST | `/api/v1/product/seller_opportunity/niche/product/list` | ListNicheProducts |
| POST | `/api/v1/product/seller_opportunity/niche/product/list_collected` | ListCollectedNicheProducts |

## brand (5)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/brand/check` | CheckBrand (+1) |
| POST | `/api/v1/product/brand/create` | CreateBrand (+1) |
| POST | `/api/v1/product/brand/delete` | DeleteBrand (+1) |
| POST | `/api/v1/product/brand/detail` | BrandDetail (+1) |
| POST | `/api/v1/product/brand/update` | UpdateBrand (+1) |

## products (4)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/products/activate` | MActivateProducts (+3) |
| POST | `/api/v1/product/products/deactivate` | MDeactivateProducts (+3) |
| POST | `/api/v1/product/products/delete` | MDeleteProducts (+3) |
| POST | `/api/v1/product/products/recover` | MRecoverProducts (+3) |

## link (4)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/link/create` | MCreateLinks (+1) |
| POST | `/api/v1/product/link/deactivate` | MDeactivateLinks (+1) |
| POST | `/api/v1/product/link/edit` | EditLink (+1) |
| POST | `/api/v1/product/link/search` | SearchLinks (+1) |

## property (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/property/check` | CheckProductProperty (+1) |
| POST | `/api/v1/product/property/migrate` | MigrateProperty (+1) |
| POST | `/api/v1/product/property/normalize_size` | NormalizeSize (+1) |

## seller (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/seller/manufacturer/create` | CreateSellerManufacturer (+1) |
| POST | `/api/v1/product/seller/manufacturer/list` | ListSellerManufacturer (+1) |
| POST | `/api/v1/product/seller/update_config` | UpdateShopConfig (+1) |

## gpr (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/gpr/compliance_review/confirm` | ConfirmGprComplianceReview (+1) |
| POST | `/api/v1/product/gpr/high_potential/silent_mode/event/record` | RecordGprHpsmEvent (+1) |
| POST | `/api/v1/product/gpr/source/precheck` | GprSourcePrecheck (+1) |

## spu (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/spu/match` | MatchSpu (+1) |
| POST | `/api/v1/product/spu/recommend` | RecommendSPU (+1) |
| POST | `/api/v1/product/spu/search` | SearchSpuAndCspu (+1) |

## async_task (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/async_task/create` | CreateTask (+1) |
| POST | `/api/v1/product/async_task/delete` | DeleteTask (+1) |
| POST | `/api/v1/product/async_task/update` | UpdateTask (+1) |

## lock (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/lock/clearance/set` | SetProductsClearance (+1) |
| POST | `/api/v1/product/lock/register_stock_lock` | RegisterStockLock (+1) |
| POST | `/api/v1/product/lock/request_stock_unlock` | RequestStockUnlock (+1) |

## comp (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/comp/get_schema_v2` | GetSchemaV2 (+1) |
| POST | `/api/v1/product/comp/refetch_data` | RefetchData (+1) |
| POST | `/api/v1/product/comp/refetch_schema` | RefetchSchema (+1) |

## commission (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/commission/config/get` | GetCommissionConfig (+1) |
| POST | `/api/v1/product/commission/delete` | DeleteCommission (+1) |
| POST | `/api/v1/product/commission/set` | SetCommission (+1) |

## bundles (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/bundles/mactivate` | MActivateBundles (+1) |
| POST | `/api/v1/product/bundles/mdeactivate` | MDeactivateBundles (+1) |
| POST | `/api/v1/product/bundles/mdelete` | MDeleteBundles (+1) |

## creator_stock (3)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/creator_stock/list` | ListCreatorStock |
| POST | `/api/v1/product/creator_stock/status/update` | UpdateCreatorStockStatus |
| POST | `/api/v1/product/creator_stock/submit` | SubmitCreatorStock |

## category (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/category/migrate` | MigrateCategory (+1) |
| POST | `/api/v1/product/category/template/submit` | SubmitCategoryTemplate (+1) |

## desc (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/desc/create_generate_task` | CreateDescGenerateTask (+1) |
| POST | `/api/v1/product/desc/pull_generate_result` | PullDescGenerateResult (+1) |

## shipping_template (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/shipping_template/check` | CheckSellerShippingTemplate (+1) |
| POST | `/api/v1/product/shipping_template/list` | GetShippingTemplateList (+1) |

## gpr_rule (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/gpr_rule/compliance_property/list` | GetGprComplianceProperties (+1) |
| POST | `/api/v1/product/gpr_rule/submit` | SubmitGprRules (+1) |

## image_translation_rule (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/image_translation_rule/get` | GetImageTranslationRule (+1) |
| POST | `/api/v1/product/image_translation_rule/submit` | SubmitImageTranslationRule (+1) |

## external (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/external/detail` | GetExternalProductDetail (+1) |
| POST | `/api/v1/product/external/search` | SearchExternalProduct (+1) |

## diagnosis (2)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/diagnosis/item/calculate` | CalculateProductDiagnosticItems (+1) |
| GET | `/api/v1/product/diagnosis/overview/get` | GetSellerDiagnosisOverview (+1) |

## category_rec (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/category_rec/list` | ListRecommendedCategoriesPost (+1) |

## short_info_rec (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/short_info_rec/list` | ListRecommendedProductShortInfoByImages (+1) |

## guide (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/guide/instructions/get` | GetGuideInstructions (+1) |

## optimization (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/optimization/refresh` | RefreshProductOptimization (+1) |

## package (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/package/recommend` | RecommendPackage (+1) |

## product_property_rec (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/product_property_rec/list` | ListRecommendedProductProperties (+1) |

## product_name_rec (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/product_name_rec/list` | ListRecommendedProductNames (+1) |

## brand_rec (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/brand_rec/list` | ListRecommendedBrands (+1) |

## actions (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/actions/list` | ListProductActions (+1) |

## gpr_overview (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/gpr_overview/get` | GetGprOverview (+1) |

## spuv2 (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/spuv2/search` | SearchSpuV2AndCspu (+1) |

## bulletin (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| GET | `/api/v1/product/bulletin/list` | GetProductBulletins (+1) |

## combo (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/combo/sku/quantity/get` | GetComboSKUQuantity (+1) |

## tab (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| GET | `/api/v1/product/tab/count/get` | GetProductTabCount (+3) |

## shipping (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/shipping/fee/estimate` | EstimateShippingFee (+3) |

## rp (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/rp/create_from_seller` | CreateRPFromSeller (+1) |

## growth_info (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/growth_info/submit` | SubmitSkppProductGrowthInfo (+1) |

## smart_publish (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/smart_publish/image_publish/task/create` | CreateSmartPublishByImageTask (+1) |

## regions (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| GET | `/api/v1/product/regions/mget` | MGetRegions (+1) |

## msubmit (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/msubmit` | MPublishProduct (+1) |

## parcel (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/parcel/check` | CheckProductParcel (+1) |

## list (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| GET | `/api/v1/product/list/seller/warehouses` | ListSellerWarehouses (+1) |

## prohibited (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/prohibited/words/check` | CheckProhibitedWords (+1) |

## download_instruction (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| GET | `/api/v1/product/download_instruction/list` | ListProductDownloadInstruction (+1) |

## images (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/images/msubmit` | MSubmitProductImage (+1) |

## promotion (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/promotion/price/get` | GetPromotionPrice (+1) |

## logistics (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/logistics/service/check` | CheckLogisticsService (+1) |

## guide_context (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/guide_context/get` | GetGuideContext (+1) |

## duplication (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/duplication/title/check` | CheckTitleDuplication (+1) |

## image (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/image/quality/check` | CheckImageQuality (+1) |

## publish (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/publish/diagnosis/item/calculate` | CalculateProductDiagnosticItemsForPublish (+1) |

## recommend (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/product/recommend/item/calculate` | CalculateProductRecommendedItems (+1) |

## growth_center (1)

| METHOD | PATH | client 方法名 |
|---|---|---|
| POST | `/api/v1/seller/growth_center/shop/product/violation/record/query` | QueryShopProductViolationDetail |
