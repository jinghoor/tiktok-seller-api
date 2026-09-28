# 真流量实测报告（阶段 3）

## 0. 环境状态

| 容器 | 店 | 端口 | 会话 | 用于实测 |
|---|---|---|---|---|
| SHOP_XBORDER | 跨境 VN | CDP_PORT | ❌ **已过期**（5/7 页面是登录页） | 否 |
| SHOP_LOCAL | 本土 VN | CDP_PORT | ❌ **已过期**（2/4 页面是登录页） | 否 |
| **SHOP_X3** | **跨境 TH** | **CDP_PORT** | ✅ **可用** | **是** |
| — | 未知 | CDP_PORT | ❌ 过期 | 否 |

SHOP_X3 的 seller_id 从 SLARDAR localStorage 读到：`7494XXXXXXXXXX90`；
余额接口返回 `THB / ฿` → 确认是**泰国店**。已注册进 `tk01_config.py`（key `tk56`）。

## 1. ★ 方法论发现：绑定错误 oracle 是个「存在性判据」

探测空 body 时，服务端会返回：

```
http=400
binding: expr_path=request, cause=missing required
```

**这不是错误，是「接口存在且可达」的证明** —— 它说明请求打到了业务绑定层，
只差 body 字段。早期分类器把它归成 `?`（无法识别），导致 SHOP_X3 的 271 个探测里
**151 个被错报为「未知」**，严重低估覆盖率。

修复后同一批数据的结论：

| 分类 | 数量 | 含义 |
|---|---|---|
| `◐ 缺 body(request)` | 151 | **存在可达**，body 缺 `request` 字段 |
| `✗ 404` | 56 | 路径/版本/方法不对（已自动试过 v2） |
| `✅ 通` | 29 | 参数齐全，返回 code=0 |
| `◐ 缺参数` | 21 | **存在可达**，参数不合法 |
| `?` | 6 | 响应非 JSON 且无绑定信息 |
| `其它(99999999)` | 3 | — |
| `◐ 缺 body(params)` | 2 | **存在可达**，缺 query 参数 |
| `其它(98001008)` | 1 | — |
| `其它(21001001)` | 1 | — |
| `其它(28001001)` | 1 | — |

**合计确认存在可达：203 / 271 = 74%**

## 2. ⚠ 记录更正：insights（数据罗盘）域是通的

我先后给过两个错误结论，现在都推翻：

| 结论 | 状态 | 真相 |
|---|---|---|
| insights 需要「特殊鉴权头」 | ❌ 撤回 | 当时 SHOP_XBORDER/SHOP_LOCAL 会话刚好过期 |
| insights 域不可用 | ❌ 撤回 | **SHOP_X3 实测：`/api/v1/insights/*` 返回 `binding: expr_path=request`**，即存在可达，只缺 body |

我把 `mf_data` 的请求头挖了一遍，`b3` 只是 `{"Content-Type":"application/json"}`，没有任何特殊头 ——
当时就该怀疑是会话问题而不是鉴权问题。

## 2.5 两批合并结果

探了 **653 个唯一接口**（去掉两批重叠），确认可达 **408 个 = 62%**。

| 分类 | 数量 |
|---|---|
| `◐ 缺 body(request)` | 309 |
| `✗ 404` | 220 |
| `◐ 缺参数` | 55 |
| `✅ 通` | 42 |
| `?` | 14 |
| `其它(99999999)` | 6 |
| `其它(28001001)` | 3 |
| `◐ 缺 body(params)` | 2 |
| `其它(98001008)` | 1 |
| `其它(21001001)` | 1 |

**按业务域（确认可达 / 其中 code=0）**

| 业务域 | 确认可达 | code=0 |
|---|---|---|
| 数据 / 罗盘 / 报表 | 346 | 26 |
| 履约 / 物流 / 面单 | 29 | 15 |
| 营销 / 促销 | 25 | 1 |
| ? | 6 | 0 |
| 订单 / 售后 | 2 | 0 |

> ⚠ 404 占比不低（220 个）。两种可能：① 我抽路径时把**前端路由**误当接口；
> ② 方法/版本不对（已自动试过 v2）。这批需要逐个回查 bundle 调用点确认。
> 但要注意：**404 不代表接口不存在** —— 有些在别的网关前缀下（`/widget/api/*`、
> `/api/fulfillment/*` 等已经验证是多前缀并存）。

## 3. 明细

### code=0（参数即通）

- `POST` `/api/v1/fulfillment/delivery_template/export`
- `POST` `/api/v1/fulfillment/doc_record/generate`
- `POST` `/api/v1/fulfillment/logistics/provider/list`
- `POST` `/api/v1/fulfillment/reach/banner_list`
- `POST` `/api/v1/fulfillment/reach/rules/violation_list`
- `POST` `/api/v1/fulfillment/seller_express/get`
- `POST` `/api/v1/fulfillment/seller_setting/biz_switch`
- `POST` `/api/v1/fulfillment/ship_template/export`
- `GET` `/api/v1/fulfillment/shipping/inoperable_packages/get`
- `POST` `/api/v1/fulfillment/shipping/options`
- `POST` `/api/v1/fulfillment/strategy/pickup_type/get`
- `POST` `/api/v1/fulfillment/strategy/pickup_type/rts_setting`
- `POST` `/api/v1/fulfillment/strategy/shipping_profile/get`
- `POST` `/api/v1/fulfillment/strategy/shipping_profile/get_amount_currency`
- `POST` `/api/v1/fulfillment/strategy/shipping_profile/get_dimension_and_weight_unit_conversion`
- `GET` `/api/v1/insights/profile/shop`
- `POST` `/api/v1/insights/seller/notifications/get`
- `GET` `/api/v1/insights/seller/shop/associated/creators`
- `POST` `/api/v1/insights/seller/shop/campaign/bcp/status`
- `POST` `/api/v1/insights/seller/shop/export/task/list`
- `POST` `/api/v1/insights/seller/shop/high_value_customer/account_list`
- `POST` `/api/v1/insights/seller/shop/live/recent/query/list`
- `POST` `/api/v1/insights/seller/shop/overview/ads_banner/info`
- `POST` `/api/v1/insights/seller/shop/overview/diagnosis/stats`
- `GET` `/api/v1/insights/seller/shop/overview/performance/carousel/display`
- `POST` `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/latest_date`
- `POST` `/api/v1/insights/seller/shop/overview/performance/gross_revenue/breakdown/latest_date_v2`
- `POST` `/api/v1/insights/seller/shop/product/card/diagnosis`
- `POST` `/api/v1/insights/seller/shop/product/diagnosis/list`
- `POST` `/api/v1/insights/seller/shop/product/diagnosis/quality/list`
- `POST` `/api/v1/insights/seller/shop/product/diagnosis/stats`
- `POST` `/api/v1/insights/seller/shop/program/bcd/category/info`
- `POST` `/api/v1/insights/seller/shop/program/bcd/product/list`
- `POST` `/api/v1/insights/seller/shop/program/bcd/register/info`
- `POST` `/api/v1/insights/seller/shop/program/eams/register/info`
- `POST` `/api/v1/insights/seller/shop/program/flashsale/category/info`
- `POST` `/api/v1/insights/seller/shop/program/flashsale/product/list`
- `POST` `/api/v1/insights/seller/shop/program/flashsale/register/info`
- `POST` `/api/v1/insights/seller/shop/program/page/display/list`
- `POST` `/api/v1/insights/seller/shop/program/vxp_plus/status`
- `POST` `/api/v1/insights/seller/shop/video/analytics/ads/info`
- `POST` `/api/v1/insights/seller/ttp/seller_center/homepage/stats`

### 存在但需补 body/参数（前 60）

- `POST` `/api/v1/fulfillment/checklist/list` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/export/err_file` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/export/file_submit` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/export/file_upload` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/invoice/list` — ◐ 缺参数
- `GET` `/api/v1/fulfillment/logistic_detail/list` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/package/delivery_update` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/package/list` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/package/mcreate` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/pickinglist/success` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/request_doc` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/ship_template/download` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/shipping/recommendation/get` — ◐ 缺参数
- `POST` `/api/v1/fulfillment/shipping_doc/generate` — ◐ 缺参数
- `POST` `/api/v1/insights/seller/core/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/core/stats/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/creator/live/diagnosis/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/data/overview/creator/list` — ◐ 缺参数
- `POST` `/api/v1/insights/seller/live/creator/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/creator/list/search` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/diagnosis/creator/details` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/diagnosis/creator/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/diagnosis/creator/suggestion/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/list/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/optimizer/account/suggestion` — ◐ 缺 body(params)
- `POST` `/api/v1/insights/seller/live/optimizer/session/suggestion` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/optimizer/summary` — ◐ 缺 body(params)
- `POST` `/api/v1/insights/seller/live/performance/creator/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/live/stats/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/notifications` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/list_v2` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/report/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/report/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/analytics/insights/stats_v2` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/authorization/get` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/annual/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/bcp/core/stats` — ◐ 缺参数
- `POST` `/api/v1/insights/seller/shop/campaign/info` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/list/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/offline/product/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/realtime/product/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/realtime/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/report/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/target` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/campaign/trend/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/boosted/impression/product/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/boosted/impression/product/list/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/boosted/impression/product/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/boosted/impression/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/channel/product/list` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/channel/product/list/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/channel/stats` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/channel/stats/export` — ◐ 缺 body(request)
- `POST` `/api/v1/insights/seller/shop/center/main/core/stats` — ◐ 缺 body(request)

## 4. 复现

```bash
python3 probe_api_master.py --shop tk56 --p0 --limit 240
python3 probe_api_master.py --shop tk56 --p1 --limit 300 --offset 240
```

**零打扰**：借操作员已打开的同源页面做页内 `fetch`，不新建标签、不点击、不抢焦点。
SHOP_X3 实测页面数 7 → 7 未变。
