# tiktok-seller-api

TikTok Shop **卖家中心**全量接口逆向归档 + 可运行客户端。

覆盖两种店型：

| 店型 | 页面域 | API 域 |
|---|---|---|
| 跨境 | `seller.tiktokshopglobalselling.com` | `api16-normal-sg.tiktokshopglobalselling.com`（**独立域**） |
| 本土（以 VN 为例） | `seller-vn.tiktok.com` | **同源**，就是页面域 |

---

## 目录

| 路径 | 内容 |
|---|---|
| [`ALL_API_INVENTORY.md`](ALL_API_INVENTORY.md) | **全量接口主表** —— 4000+ 个唯一接口，按 18 个业务域分组 |
| [`API_GAP_REPORT.md`](API_GAP_REPORT.md) | 缺口报告：微前端 → 接口数、域覆盖、优先级 |
| [`AFFILIATE_API.md`](AFFILIATE_API.md) | 联盟中心（达人）564 个接口 + 实测状态 |
| [`FINANCE_API.md`](FINANCE_API.md) | 财务板块 244 个接口 + 导出/批量下载全链 + 调用配方 |
| [`TIKTOK_PROMOTION_API.md`](TIKTOK_PROMOTION_API.md) | 促销 / 商品机会 / 站内 IM / 验证码，主文档 |
| [`CRAWL_PLAN.md`](CRAWL_PLAN.md) | 全量爬取方法论与分阶段计划 |
| [`HUBSTUDIO_HEADLESS.md`](HUBSTUDIO_HEADLESS.md) | Hub Studio 指纹浏览器 headless 探测笔记 |
| `notes/api_inventory/` | 机器可读的接口清单（JSON） |
| `adfly_api/` | 另一个子项目：`ad.aiadfly.com` 广告管理客户端（291 接口） |

### 机器可读清单

```
notes/api_inventory/master.json          全量主表（path / method / domain / 来源）
notes/api_inventory/mf_all.json          11 个微前端各自的接口
notes/api_inventory/enriched.json        联盟中心
notes/api_inventory/finance_paths.json   财务
```

---

## 核心认知

### 1. 页面范围 = 11 个微前端

卖家中心是 **atlas / garfish 微前端**。页面 HTML 里有注册表，列出全部 11 个 `mf_*`：

| 微前端 | 接口数 | 业务域 |
|---|---|---|
| `mf_promotion` | 846 | 营销 / 促销 |
| `mf_workbench` | 805 | 工作台 / 首页 |
| `mf_finance` | 686 | 财务 |
| `mf_logistics_us` / `mf_logistics` | 625 / 565 | 履约 / 物流 / 面单 |
| `mf_product` | 582 | 商品 / 库存 / 定价 |
| `mf_merchant` | 405 | 商家 / 入驻 |
| `mf_reverse` | 344 | 售后 / 退货 |
| `mf_data` | 555 | 数据罗盘 |
| `mf_governance` | 214 | 治理 / 违规 |
| `mf_privatedomain` | 132 | 私域 / 粉丝 |

订单 / 客服 / 广告不在 `mf_*` 里，在 shell 主应用或独立页。

### 2. 抽接口的四个坑（都踩过）

1. **entry 和 chunk 在不同 CDN 上。** entry 在 `goofy-cdn`，chunk 在 `oecstatic`。
   唯一可靠来源是 webpack runtime 的 `__webpack_require__.p = "…"`，猜路径必 404。
2. **chunk 相对路径要补回 `static/`。** 取 `split("/")[-2:]` 得到 `js/x.js`（404），
   必须取 `mf_名` 之后的部分。
3. **路径有多种写法，少覆盖一种就漏一大片**：
   - 字面量 `"/api/v1/x"`
   - 反引号模板 `` `${prefix}/api/v1/x` ``
   - **`/api/v` + `${version||1}`** —— 最容易整族漏（财务就漏了 39 个结算接口）
   - **完全不带 `/api` 前缀**的（`/insights/seller/*`、`/qualification/center/*`），
     判据是路径字符串**紧邻** `method:"…"`（前端路由不会挨着 method）
   - 有的微前端 chunk 表藏在 `t.u=function(e){return"mf_x/static/js/"+e+"."+{id:"hash",…}[e]+".js"}`
     里而不是 `import()` 里
4. **方法别名 `a.UD` == GET。** 只认字符串字面量会把 100+ 个 GET 标成未知，
   再按 POST 试全是 404。

### 3. 零打扰抓取

自动化跑在操作员的真实浏览器里，**不能影响他正常用电脑**：

| 做法 | 结果 |
|---|---|
| `ctx.new_page()` 开页爬 | ❌ Chromium 默认**激活**新标签，会打扰人 |
| CDP `Target.createTarget({background:true})` | ❌ 不激活但 Playwright 不登记，回收困难 |
| **借已打开页面做页内 `fetch()`** | ✅ 采用 —— 零新建标签、零点击、零鼠标、零焦点 |

`fetch` 自带 cookie、同源/跨域都行，后台标签也能跑（只有 timer 会被节流）。
交互全部走 DOM 层 `el.click()` / `window.scrollTo()`，不产生 Input 事件。

---

## 客户端

| 模块 | 覆盖 |
|---|---|
| `tk01_finance.py` | 财务：余额 / 流水 / 对账单 / 发票 / **两段式批量下载** |
| `tk01_affiliate.py` | 联盟：达人广场 / 定向计划 / 邀约 |
| `tk01_im.py` | 站内 IM：protobuf 私有协议（cmd 100/200/203/301/604/2000） |
| `tk01_im_track.py` | 联盟邀约 × 站内 IM 联表跟踪 |
| `tk01_opportunity.py` | 商品机会提报 |
| `tk01_promo_client.py` | 促销创建 |
| `tk01_config.py` | 多店铺 / 多区域上下文 |

### 快速上手

```bash
python3 -m pip install playwright protobuf websocket-client
python3 -m playwright install chromium

# 店铺上下文
python3 tk01_config.py add myshop --region VN --seller-id <你的店铺ID> \
    --aid 6556 --port <CDP端口> \
    --api-host https://api16-normal-sg.tiktokshopglobalselling.com \
    --seller-origin https://seller.tiktokshopglobalselling.com
python3 tk01_config.py use myshop

# 财务
python3 tk01_finance.py balance
python3 tk01_finance.py order-list --status 2 --size 20
python3 tk01_finance.py file-list
```

> 客户端通过 **CDP 连接你已打开的浏览器**，借已有页面发请求。
> 它**不新建标签、不关你的页面**，`close()` 只释放自己的连接。

---

## 爬取工具

```
harvest_mf_all.py            抓 11 个微前端的 bundle 并抽接口（主力）
extract_affiliate_paths.py   联盟 bundle 抽接口
extract_finance_paths.py     财务 bundle 抽接口（覆盖多种路径写法）
build_api_master.py          汇总所有清单 → ALL_API_INVENTORY.md + 缺口报告
capture_finance_live.py      CDP 真流量捕获（拿真实 host / 参数 / body）
crawl_finance_quiet.py       静默版 UI 驱动抓取（后台标签 + DOM 点击）
probe_finance_api.py         借页面批量探测接口状态
notes/fin_js_list.py         抓页面 HTML + 首屏 JS
expand_finance_chunks.py     递归展开懒加载 chunk
```

---

## 免责

本项目用于**接口研究与互操作**，基于分析自有店铺账号的会话流量。
公开部分已做脱敏：店铺 ID、账号凭证、代理地址、真实业务数据、第三方个人信息全部移除。

使用前请确认符合目标平台的服务条款与当地法律。
