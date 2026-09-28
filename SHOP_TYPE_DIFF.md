# 两店型差异矩阵（阶段 5）

## 1. 实测覆盖

| 店铺 | 类型 | 端口 | 测绘方法 | 覆盖 |
|---|---|---|---|---|
| SHOP_LOCAL | **本土 VN**（`seller-vn`） | CDP_PORT | `map_route_existence.py --all` | **4205 / 4205（全量）** |
| SHOP_X3 | **跨境 TH**（`api16-normal-sg`） | CDP_PORT | `probe_api_master.py` | 653 |
| SHOP_XBORDER | 跨境 VN | CDP_PORT | `probe_api_master.py` | 333 |

> SHOP_XBORDER/SHOP_X3 的容器在测绘中途被 Hub Studio 关闭（端口拒连），所以跨境侧只有部分覆盖。
> SHOP_LOCAL 跑完了全量，是本次最完整的一张地图。

## 2. SHOP_LOCAL 全量结果（本土 VN 网关）

- **路由存在 1983 / 4205 = 47%**，其中 **385 个 `code=0`**（参数齐全，直接可用）
- 路由不存在 1757、未定 465

按业务域的存在率（本土 VN 网关注册了什么）:

| 业务域 | 有 | 无 | ? | 存在率 |
|---|---|---|---|---|
| 直播 / 达人运营 | 20 | 7 | 0 | **74%** |
| 数据 / 罗盘 / 报表 | 361 | 101 | 40 | **71%** |
| 营销 / 促销 | 288 | 115 | 5 | **70%** |
| 开店 / 入驻清单 | 10 | 7 | 0 | **58%** |
| 店铺授权 / 子账号 / 角色 | 14 | 11 | 0 | **56%** |
| 商品 / 库存 / 定价 | 235 | 186 | 10 | **54%** |
| 全球仓 / 跨境 / 区域 | 19 | 12 | 5 | **52%** |
| 消息 / IM / 通知 | 78 | 69 | 10 | **49%** |
| 交易（/trade 前缀，另一套） | 31 | 10 | 23 | **48%** |
| 内容创作 / 视频中心 | 73 | 35 | 45 | **47%** |
| 订单 / 售后 | 80 | 25 | 64 | **47%** |
| 财务 / 结算 / 税务 | 117 | 114 | 20 | **46%** |
| 联盟 / 达人 | 245 | 277 | 2 | **46%** |
| 商家 / 入驻 / 资质 | 139 | 122 | 49 | **44%** |
| 其他 / 未分类 | 127 | 157 | 42 | **38%** |
| 店铺运营 / 工作台 | 28 | 49 | 12 | **31%** |
| 商品成长 / 优化 / 机会 | 16 | 42 | 5 | **25%** |
| 客服消息 / 站内信 | 4 | 10 | 4 | **22%** |
| 履约 / 物流 / 面单 | 70 | 281 | 33 | **18%** |
| 平台基础设施 | 8 | 34 | 5 | **17%** |
| 学习中心 / 内容 | 14 | 70 | 0 | **16%** |
| 治理 / 违规 / 申诉 | 5 | 4 | 63 | **6%** |
| 达人外联 / 任务消息 | 1 | 14 | 6 | **4%** |
| 账号安全 / 通行证 | 0 | 4 | 21 | **0%** |

**读法**：「存在率」= 该业务域有多少比例的静态抽取接口真正注册在了本土店网关上。

- **最高**：直播/达人 74%、数据罗盘 71%、营销促销 70%、开店入驻 58%、店铺授权 56%
- **最低**：履约物流 **18%**、治理违规 **6%**、账号安全 **0%**、达人外联 4%

低不是「接口不存在」，而是**这些域的大部分接口属于另一个店型/网关** ——
履约物流那 82% 大概率在跨境侧（`mf_logistics_us` 的 US 半托管），见下节。

## 3. 店铺类型交叉表（SHOP_LOCAL 本土 vs SHOP_X3 跨境）

| 分类 | 数量 |
|---|---|
| 共有 | 351 |
| 仅tk89 | 4 |
| 仅tk56 | 50 |
| 都无 | 108 |
| 未测 | 4473 |

> 只在两店都测过的路径上可比（SHOP_X3 只测了 653 个，所以「未测」很多）

### 仅跨境有（本土无）—— 50 个

集中在 **`/api/v1/insights/seller/ttp/*`**（TTP 数据总览）和 `/insights/seller/shop/associated/creators`：

```
?     /api/v1/insights/seller/shop/associated/creators
?     /api/v1/insights/seller/shop/overview/performance/carousel/display
POST  /api/v1/insights/seller/ttp/data_overview/core/stats
POST  /api/v1/insights/seller/ttp/data_overview/core/stats/export
POST  /api/v1/insights/seller/ttp/data_overview/ongoing_live/list
POST  /api/v1/insights/seller/ttp/data_overview/post_purchase/stats
POST  /api/v1/insights/seller/ttp/data_overview/revenue_ranking/stats
POST  /api/v1/insights/seller/ttp/data_overview/todays_performance/stats
POST  /api/v1/insights/seller/ttp/opportunity_insights/ace/stats
POST  /api/v1/insights/seller/ttp/opportunity_insights/affiliate_retarget_creator/list
POST  /api/v1/insights/seller/ttp/opportunity_insights/creator/list
POST  /api/v1/insights/seller/ttp/opportunity_insights/product/list
POST  /api/v1/insights/seller/ttp/opportunity_insights/suggestion/feedback
POST  /api/v1/insights/seller/ttp/opportunity_insights/suggestion/list
POST  /api/v1/insights/seller/ttp/opportunity_insights/video_filter/list
POST  /api/v1/insights/seller/ttp/opportunity_insights/viewer_traffic/stats
POST  /api/v1/insights/seller/ttp/realtime/ongoing_live/list
POST  /api/v1/insights/seller/ttp/sales/core/stats
```

### 仅本圭有（跨境无）—— 4 个

- `POST` `/api/v1/fulfillment/config_center/get`
- `POST` `/api/v1/fulfillment/logistics_service/list`
- `POST` `/api/v1/insights/pop/product/optimize/optimized/list`
- `POST` `/api/v1/insights/seller/us/shop/rank/list`

「跨境无」这四个要谨慎 —— SHOP_X3 是**泰国**店且只测了 653 个，
更可能是**没测到**而不是真的没有。

### 两店都没有 —— 108 个

| 业务域 | 数量 |
|---|---|
| 履约 / 物流 / 面单 | 83 |
| 数据 / 罗盘 / 报表 | 23 |
| 商家 / 入驻 / 资质 | 1 |
| 营销 / 促销 | 1 |

履约/物流占了 83 个 —— 与 SHOP_LOCAL 那 18% 存在率吻合，
佐证 `/logistics/customs/*`、`/fulfillment/subsidy/*` 属于**第三类店铺**（US/UK 半托管）。

## 4. 结论

1. **店型差异是真实且显著的** —— 同一份静态清单在本土店只有 47% 注册，
   差异集中在履约物流（18%）和治理违规（6%）
2. **跨境侧多出 TTP 数据总览**（`/insights/seller/ttp/*`），本土店没有
3. **`/logistics/customs/*`（64 个）两边都没有** —— 需要 US/UK 半托管店铺才能验证
4. 本土店的 `code=0` 有 385 个，这些是**可直接调用**的接口（参数已被我猜对）
