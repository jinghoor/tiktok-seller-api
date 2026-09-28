# 全量接口客户端 —— 后训练产物

主表里 **4205 个接口**全部变成可查询、可调用的索引，每个都带方法与实测状态。

## 0. 实测总览

| 项 | 数量 |
|---|---|
| 接口总数 | **4205** |
| 实测**存在**（本土店网关注册了） | **2045** |
| 实测不存在 | 1697 |
| 其中 **`code=0`**（参数已猜对，可直接用） | **389** |

> 数据来源：本土店(SHOP_LOCAL) 4205 条全量路由测绘 + 跨境店(SHOP_X3/SHOP_XBORDER) 986 条探测。
> 「存在」判据见 [`ROUTE_EXISTENCE.md`](ROUTE_EXISTENCE.md) —— 网关**先路由后鉴权**，
> 因此 `98001002 请登录` / `98001004 参数错误` / `binding: ...` 都证明**路由存在**。

## 1. 客户端结构

```
tk_base.py    传输层基座 —— 借已打开页面做页内 fetch（零打扰）
tk_api.py     全量索引 + 可调用客户端（覆盖 4205 个）
tk01_config.py  多店铺/多区域上下文

tk01_finance.py    财务域深度客户端（89 个实测 + 两段式批量下载）
tk01_affiliate.py  联盟域深度客户端（564 个 / 35 实测）
tk01_im.py         站内 IM protobuf 私有协议
tk01_opportunity.py 商品机会提报
tk01_promo_client.py 促销创建
```

### 分工

- **`tk_api.py`** —— 广度：任何接口都能调，带自动方法选择和实测状态
- **`tk01_*.py`** —— 深度：某个域的完整业务封装（参数、枚举、两段式流程）

## 2. 快速上手

```bash
# 域清单 + 存在率
python3 tk_api.py domains

# 按关键词搜（带实测状态标注）
python3 tk_api.py search insights
python3 tk_api.py search settlement --verified ok      # 只要 code=0 的

# 列出某域可直接调用的接口
python3 tk_api.py verified --domain 财务 --ok-only

# 实测调一个
python3 tk_api.py call /api/v1/pay/settlement/settings --shop tk89
python3 tk_api.py call /api/v1/insights/seller/core/stats \
    --method POST --body '{"request":{}}' --shop tk89

# 现测几个（并发 + 超时）
python3 tk_api.py probe /api/v1/x /api/v1/y --shop tk89
```

```python
from tk_api import Api, ApiIndex

# 查询
idx = ApiIndex()
for r in idx.search('settlement', verified='ok'):
    print(r['method'], r['path'], r['code'])

# 调用
with Api('tk89') as a:
    print(a.shop_info)                 # 自动判定本土/跨境，选对 api_base
    print(a.call('/api/v1/pay/settlement/settings'))
    data = a.call_ready('/api/v1/seller/common/get')   # code!=0 时抛异常

# 批量（并发 + 每个请求独立超时，一个卡住不拖垮整批）
with Api('tk89') as a:
    for r in a.probe(a.ready[:50]):
        print(r['path'], r['code'])
```

## 3. 店型差异（客户端自动处理）

| | 跨境 | 本土 |
|---|---|---|
| 页面域 | `seller.tiktokshopglobalselling.com` | `seller-vn.tiktok.com` |
| API 域 | `api16-normal-sg.tiktokshopglobalselling.com`（**独立域**） | **同源** = 页面域 |
| `aid` | 6556 | 4068 |
| 时区 | `Asia/Bangkok` | `Asia/Ho_Chi_Minh` |

`BaseClient.is_local` 自动判定，`api_base` 自动选对。跨域 fetch 也能带 cookie ——
页内 `fetch` 不受同源限制。

## 4. 各域可训练度

| 业务域 | 总数 | 实测存在 | **code=0** | 存在率 | 深度客户端 |
|---|---|---|---|---|---|
| 数据 / 罗盘 / 报表 | 502 | 412 | **49** | 82% | — |
| 营销 / 促销 | 408 | 288 | **41** | 70% | — |
| 联盟 / 达人 | 524 | 255 | **25** | 48% | `tk01_affiliate.py` ✅ |
| 商品 / 库存 / 定价 | 431 | 235 | **74** | 54% | — |
| 商家 / 入驻 / 资质 | 310 | 139 | **24** | 44% | — |
| 其他 / 未分类 | 326 | 127 | **37** | 38% | — |
| 财务 / 结算 / 税务 | 251 | 118 | **28** | 47% | `tk01_finance.py` ✅ |
| 订单 / 售后 | 169 | 80 | **9** | 47% | — |
| 消息 / IM / 通知 | 157 | 78 | **10** | 49% | `tk01_im.py` ✅（protobuf） |
| 内容创作 / 视频中心 | 153 | 73 | **24** | 47% | — |
| 履约 / 物流 / 面单 | 384 | 70 | **23** | 18% | — |
| 交易（/trade 前缀，另一套） | 64 | 31 | **5** | 48% | — |
| 店铺运营 / 工作台 | 89 | 28 | **14** | 31% | — |
| 直播 / 达人运营 | 27 | 20 | **4** | 74% | — |
| 全球仓 / 跨境 / 区域 | 36 | 19 | **3** | 52% | — |
| 商品成长 / 优化 / 机会 | 63 | 16 | **5** | 25% | `tk01_opportunity.py` ✅ |
| 学习中心 / 内容 | 84 | 14 | **1** | 16% | — |
| 店铺授权 / 子账号 / 角色 | 25 | 14 | **8** | 56% | — |
| 开店 / 入驻清单 | 17 | 10 | **1** | 58% | — |
| 平台基础设施 | 47 | 8 | **2** | 17% | — |
| 治理 / 违规 / 申诉 | 72 | 5 | **0** | 6% | — |
| 客服消息 / 站内信 | 18 | 4 | **2** | 22% | — |
| 达人外联 / 任务消息 | 21 | 1 | **0** | 4% | — |
| 私域 / 粉丝 / 会员 | 2 | 0 | **0** | 0% | — |
| 账号安全 / 通行证 | 25 | 0 | **0** | 0% | — |

**读法**：`code=0` 的意思是「我用空 body / 猜的参数调，服务端接受了」。
这类接口**拿来即用**；其余「存在」的只需补对 body 字段。

## 5. 已验证可直接调用的接口（前 60）

| 方法 | 路径 |
|---|---|
| `?` | `/api/v1/insights/profile/shop` |
| `POST` | `/api/v2/promotion/voucher/list` |
| `POST` | `/api/v1/finance/acquiring/payment/biz_order/list` |
| `POST` | `/api/v1/finance/assistant/config` |
| `POST` | `/api/v1/finance/billing/policy/jbp_process/query` |
| `POST` | `/api/v1/logistics/district/list` |
| `POST` | `/api/v1/pay/meta/info/get` |
| `POST` | `/api/v1/pay/onboard_info/ubo_status/get` |
| `GET` | `/api/v1/pay/settlement/balance/get` |
| `POST` | `/api/v1/pay/settlement/biz/deposit/freeze` |
| `GET` | `/api/v1/pay/settlement/file/list` |
| `POST` | `/api/v1/pay/settlement/payout/manage_link` |
| `POST` | `/api/v1/pay/settlement/payout/pi_infos` |
| `GET` | `/api/v1/pay/settlement/payout/reverse_block_check` |
| `GET` | `/api/v1/pay/settlement/settings` |
| `POST` | `/api/v1/pay/settlement/withdraw/detail/query` |
| `GET` | `/api/v1/pay/settlement/withdraw/fail/msg/query` |
| `GET` | `/api/v1/pay/settlement/withdraw/rules/get` |
| `GET` | `/api/v1/seller/account/switch/get` |
| `GET` | `/api/v1/seller/affiliate_card/get` |
| `GET` | `/api/v1/seller/allowed_geo_l0/get` |
| `GET` | `/api/v1/seller/common/get` |
| `GET` | `/api/v1/seller/common_extra/get` |
| `POST` | `/api/v1/seller/custom_role/resource/get` |
| `GET` | `/api/v1/seller/delegation/info` |
| `POST` | `/api/v1/seller/delegation/mode/set` |
| `POST` | `/api/v1/seller/delivery/update` |
| `GET` | `/api/v1/seller/ext_attr/get` |
| `GET` | `/api/v1/seller/global/warehouses/deactivated_warehouse/get` |
| `GET` | `/api/v1/seller/global/warehouses/get` |
| `GET` | `/api/v1/seller/global/warehouses/permission/get` |
| `GET` | `/api/v1/seller/global_product_permission/get` |
| `GET` | `/api/v1/seller/global_seller_onboard_info/get` |
| `GET` | `/api/v1/seller/home_card/get` |
| `GET` | `/api/v1/seller/home_task/get` |
| `GET` | `/api/v1/seller/homepage_allowlist/get` |
| `POST` | `/api/v1/seller/join/extended_field/submit` |
| `POST` | `/api/v1/seller/join/local/personal_certificate/save-draft` |
| `GET` | `/api/v1/seller/locales/get` |
| `POST` | `/api/v1/seller/logout_seller_center` |
| `POST` | `/api/v1/seller/menu/switch` |
| `GET` | `/api/v1/seller/msg_card/get` |
| `GET` | `/api/v1/seller/onboard/config/get` |
| `GET` | `/api/v1/seller/onboard/detail` |
| `GET` | `/api/v1/seller/onboard/local/draft/get` |
| `GET` | `/api/v1/seller/onboard/v1/config_aggr/get` |
| `GET` | `/api/v1/seller/onboard/v1/jumio_config/get` |
| `GET` | `/api/v1/seller/onboard/v1/local/config/get` |
| `POST` | `/api/v1/seller/onboard/v1/local/id/toko_fast_onboard/start` |
| `GET` | `/api/v1/seller/onboard/v1/local/state/get` |
| `GET` | `/api/v1/seller/order/conf/get` |
| `GET` | `/api/v1/seller/permissions/get` |
| `GET` | `/api/v1/seller/pipo_scene_link/get` |
| `POST` | `/api/v1/seller/profile/contact/get` |
| `GET` | `/api/v1/seller/seller_financing_link/get` |
| `POST` | `/api/v1/seller/seller_map/read` |
| `GET` | `/api/v1/seller/settlement/account/get` |
| `POST` | `/api/v1/seller/shop_creator/unbind` |
| `GET` | `/api/v1/seller/shop_limit_status/get` |
| `GET` | `/api/v1/seller/special_paylater_link/get` |

## 6. 已知限制

1. **容器必须开着且已登录** —— 客户端借操作员已打开的页面发请求，没有页面就无法工作。
   报错信息会列出可用页面，照它开一个同源标签即可。
2. **「不存在」不等于接口无效** —— 见 [`SHOP_TYPE_DIFF.md`](SHOP_TYPE_DIFF.md)，
   本土店只注册了 47%；`/logistics/customs/*`（64 个）两边都没有，疑似 US/UK 半托管专有。
3. **`?` 未定的 465 个** —— 部分是请求超时（已加 `AbortController` 超时，重测可解）。
4. **写操作未做批量验证** —— 为避免在账号里造成副作用，探测跳过了写接口。
5. **签名墙**：`marketplace/find` 需要 `msToken`/`X-Bogus`/`X-Gnarly`/`X-Tts-Oec-Bsid` 四个头，
   且必须让应用自己发请求 —— 页内 `fetch` 不带这四个。
