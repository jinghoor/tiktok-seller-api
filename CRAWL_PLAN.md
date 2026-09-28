# 卖家中心全量接口爬取 + 后训练 计划

目标：跨境店（`seller.tiktokshopglobalselling.com` / SHOP_XBORDER）+ 本土店（`seller-vn.tiktok.com` / SHOP_LOCAL）
**所有页面**的接口全量归档、实测、后训练成可调用能力。

---

## 0. 现状盘点（已完成的部分）

| 域 | 产物 | 接口数 | 状态 |
|---|---|---|---|
| 联盟中心（达人） | `AFFILIATE_API.md` | **564** | ✅ 静态抽取 + 13 组分类 + 35 个实测 |
| 财务 | `FINANCE_API.md` | **244**（bundles 里 1024 条路径） | ✅ 静态 + 真流量 + 89 个实测 + 全链下载跑通 |
| 站内 IM | `tk01_im.py` §40 | protobuf 全通 | ✅ 真发过消息 |
| 促销 | `TIKTOK_PROMOTION_API.md` §1-19 | 85 refs | ✅ 批量新建验证 |
| 商品机会 | §20-22 | 全套 | ✅ 61% 命中实测 |
| 商品/广告 | `notes/tt_api_map_full.json` | 568 | ◐ 早期抽取，未按域整理 |
| 商品/库存/订单 | `tk178_*` / `tk01_*` 系列 | 部分 | ◐ 零散 |

**已归档接口去重后约 1900+ 条**，但分布不均：财务和联盟很细，商品/订单/物流/治理/数据/达人私域几乎空白。

---

## 1. ★ 关键认知：页面范围 = 11 个微前端

卖家中心不是单体应用，是 **atlas/garfish 微前端**。从页面 HTML 的注册表里拿到全部 11 个：

| 微前端 | 版本 | 业务域 | 预估接口量 |
|---|---|---|---|
| `mf_finance` | 1.0.0.4610 | 财务（已单独爬过） | **686** ✅ |
| `mf_product` | 1.0.0.1014 | 商品管理 / 发布 / 库存 / 定价 | 大 |
| `mf_promotion` | 1.0.0.2782 | 营销 / 促销 / 优惠券 | 大 |
| `mf_logistics` | 1.0.0.5461 | 物流 / 发货 / 面单 | 大 |
| `mf_logistics_us` | 1.0.0.2822 | 物流（美区变体） | 中 |
| `mf_merchant` | 1.0.0.1187 | 商家入驻 / 资质 / 店铺设置 | 中 |
| `mf_governance` | 1.0.0.2526 | 治理 / 违规 / 申诉 | 中 |
| `mf_reverse` | 1.0.0.568 | 逆向 / 退货退款 | 中 |
| `mf_data` | 1.0.0.1879 | 数据罗盘 / 分析 | 中 |
| `mf_privatedomain` | 1.0.0.176 | 私域 / 粉丝 / 会员 | 小 |
| `mf_workbench` | 1.0.0.4436 | 工作台 / 首页 / 待办 | 小 |

**这 11 个就是"所有页面"**。订单/客服/广告/联盟不在 mf_* 里，是主应用（`sc-gs`）或独立页，
单独处理。

---

## 2. 爬取方法（已跑通，零打扰）

### 2.1 静态抽取（主干，量最大）

```
harvest_mf_all.py
  entry:  //lf16-oversea.goofy-cdn.com/.../mf_xxx/<ver>/TTS/unihan/mf_xxx.js
  chunk:  __webpack_require__.p 里读 publicPath
          = https://lf16-scmcdn.oecstatic.com/obj/oec-magellan-sg/i18n/ecom/TTS/unihan/
          拼 <mf>/static/js/<id>.<hash>.js
```

**四个必踩的坑（都已解决）**：

1. **entry 和 chunk 在两个不同 CDN 上** —— entry 在 `goofy-cdn`，chunk 在 `oecstatic`。
   靠 webpack runtime 的 `__webpack_require__.p="…"` 才知道，别猜路径。
2. **chunk 相对路径要补全 `static/`** —— 取 `split("/")[-2:]` 会得到 `js/x.js`（404），
   必须取 `mf_名` 之后的部分 = `static/js/x.js`。
3. **路径是拼接的，三种写法都要覆盖**：
   - 字面量 `"/api/v1/x"`
   - 反引号模板 `` `${prefix}/api/v1/x` ``
   - **`/api/v` + `${version||1}`**（最容易整族漏）
4. **方法别名**：`method:a.UD` == **GET**。只认字符串字面量会把 100+ 个 GET 标成 `?`，
   再按 POST 试全是 404。

### 2.2 真流量补全（拿真实 body / 参数 / 状态）

```
crawl_finance_quiet.py 的通用化版本
  借操作员已打开的页面 → 页内 fetch（同源/跨域都行）→ 零新建标签、零点击、零焦点
```

**绝不使用** `ctx.new_page()`（Chromium 默认激活标签，会打扰操作员）。
**绝不使用** `Target.createTarget({background:true})`（Playwright 不登记，回收困难）。

### 2.3 实测（分清"存在"和"能用"）

`probe_finance_api.py` 的通用化版本：借页面批量打接口，按响应分类
（`code=0` / 缺参数 / 无此路由 / 404 / 需额外鉴权）。

**纪律**：写操作（create/submit/pay/export 等）默认**跳过**，避免在操作员账号里留垃圾数据；
确需触发时单独跑并记录后果。

---

## 3. 执行计划（分 6 阶段）

### 阶段 1：全部 11 个微前端静态抽取 ⏳ 进行中

| 步骤 | 说明 |
|---|---|
| 1.1 | `harvest_mf_all.py` 跑完 11 个 mf_* |
| 1.2 | 处理 publicPath 异常的几个（`mf_data`/`mf_governance` 只下到 1 个文件）——它们的 chunk 表结构不同，需从 `mf-stats.js` / `federation-manifest` 或运行时目录猜 |
| 1.3 | 主应用 `sc-gs`（navbar/sidebar/pop）抽接口 —— 订单/客服/广告/工作台在这一层 |
| 1.4 | 按域聚合 → `ALL_API_INVENTORY.md` |

**产出**：全量静态清单（预估 3000-5000 条唯一路径）

### 阶段 2：差集分析

把阶段 1 的并集与已有清单（联盟 564 / 财务 244 / IM / 促销 / 机会 / 商品 568）做差集，
输出**按业务域分组的未爬取缺口表**，标注每个缺口属于哪个微前端、哪个页面。

**产出**：`API_GAP_REPORT.md`

### 阶段 3：真流量爬取补全

对每个微前端对应的**真实页面**（两个店型各跑一遍）：
1. 借已打开页面做页内 fetch，把阶段 2 的缺口接口批量打一遍
2. 对需要真实参数的，读 bundle 里的调用点补参数
3. 记录状态：✅可用 / ◐缺参数 / ✗404 / ⛔该店无此路由

**产出**：`notes/probe_<mf>.json` + 缺口收敛

### 阶段 4：页面 → 接口映射表

对**每个页面路由**，输出它加载时打哪些接口（真流量捕获 + bundle 静态归属）。
这张表是后续自动化的基础。

**产出**：`PAGE_API_MAP.md`

### 阶段 5：两店差异矩阵

跨境 vs 本土逐接口对比（财务那轮已跑出方法：仅本土 23 个 / 仅跨境 4 个）。
扩展到全部域，标注：
- 域差异（同源 vs 独立 API 域）
- `aid` 差异（6556 vs 4068）
- 路由差异（`/finance/bills` vs `/finance/transactions`）
- 接口存在性差异

**产出**：`REGION_DIFF_MATRIX.md`

### 阶段 6：后训练

对每个域产出**可运行客户端 + 调用配方**，形态对齐 `tk01_finance.py`：

| 域 | 客户端 | 关键能力 |
|---|---|---|
| 商品 | `tk01_product.py` | 列表/详情/发布/编辑/库存/定价 |
| 订单 | `tk01_order.py` | 列表/详情/发货/面单/售后 |
| 物流 | `tk01_logistics.py` | 运单/轨迹/面单打印 |
| 营销 | `tk01_marketing.py` | 促销/优惠券/活动 |
| 数据 | `tk01_analytics.py` | 罗盘/报表/导出 |
| 治理 | `tk01_governance.py` | 违规/申诉 |
| 逆向 | `tk01_reverse.py` | 退货退款 |
| 商家 | `tk01_merchant.py` | 资质/店铺设置 |
| 私域 | `tk01_privatedomain.py` | 粉丝/会员 |
| 工作台 | `tk01_workbench.py` | 待办/首页 |

每个客户端统一：
- 走 `tk01_config.py` 的店铺上下文（自动选域/aid/端口）
- 借页面页内 fetch（零打扰）
- 统一错误分类 + `runs.jsonl` 日志
- 内置 `selftest()` 自检
- 配一节 `*_API.md` 调用配方（含真实返回形状）

**总产出**：`ALL_API_TRAINED.md`（总索引）+ 10 个客户端 + 各自的手册

---

## 4. 风险与纪律

| 风险 | 对策 |
|---|---|
| 打扰操作员 | 只用借页面 fetch；绝不开新标签；结束核对页面数 |
| 在账号里留垃圾数据 | 写操作默认跳过；确需触发先声明后果 |
| 触发风控 | 请求间加 0.3-0.6s；单批 ≤ 25 个；不在短时间内重复打同一接口 |
| 环境漂移 | **`python3` 可能不是有 playwright 的那个** —— 固定用 `/Library/Frameworks/Python.framework/Versions/3.10/bin/python3` |
| 版本漂移 | bundle 带版本号，前端发版后重跑 harvester 即可 |

---

## 5. 当前进度（本轮）

- ✅ 目标建立
- ✅ 确认页面范围 = 11 个微前端
- ✅ `harvest_mf_all.py` 跑通（4 个坑全解）
- ✅ `mf_finance` 完成：19 文件 / 9.8 MB / **686 接口**
- ⏳ 其余 10 个微前端抓取中
- ⏳ `mf_data` / `mf_governance` 的 chunk 结构与其他不同，待单独处理
- ⬜ 阶段 2-6
