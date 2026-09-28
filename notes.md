# notes.md — SHOP_XBORDER 跨店(越南) 自动化工作笔记

## 目标 / 已完成 / 证据 / 下一步

### 目标
联盟达人链路打通 + 促销批量 + 商品机会提报 + 站内 IM 批量消息 + 邀约后跟踪。

### 本轮（2026-09-28）新增

| 项 | 状态 | 证据 / 产物 |
|---|---|---|
| 店铺上下文配置化（多店铺/多区域） | ✅ | `tk01_config.py` + `shops.json`，已接入 3 个 client |
| 运行日志 `runs.jsonl` | ✅ | `tk01_log.py`，`log_run()` 已接进建计划/加达人/终止/邀约/IM 发送 |
| **站内 IM protobuf** | ✅ | `tk01_im.py`、`tiktok.proto`/`tiktok_pb2.py`；`TIKTOK_PROMOTION_API.md` §40 |
| **IM 批量消息** | ✅ 真发验证 | `cmd=100` 真发 2 条成功（`server_message_id` 7690XXXXXXXXXX84 / 7690XXXXXXXXXX08，`check_code=0`，cmd=301 回读落库）；`send_batch()` 4~9s 随机节流、连续 3 败中止 |
| **达人邀约后跟踪** | ✅ | `tk01_im_track.py`、`notes/aff_invite_tracking.json`；文档 §41 |
| **联盟 API 全量整理** | ✅ | `AFFILIATE_API.md`（**564 个接口**，13 组，带 HTTP 方法）；抽取脚本 `extract_affiliate_paths.py` + `gen_affiliate_api.py` |
| **财务板块 API 爬取** | ✅ | `FINANCE_API.md`（静态 **1024 路径 / 244 财务**，14 族）+ 真流量捕获 218 请求；脚本 `capture_finance_live.py` / `extract_finance_paths.py` / `gen_finance_api.py` |

### IM 链路实测结论

- **拉会话用 cmd=200**（`v2/message/get_by_user`）。cmd=203 只回 `per_user_cursor`，**不发历史**。
  路径与 cmd 串了 → `request.MessagesPerUserInitV2Body is empty`。
- 会话索引由消息流聚合；达人映射来自 `ext.creator_oec_id`（建会话事件 `command_type:8`）。
- 实测：`89 条消息 → 17 个会话`，`has_more=False`。
- `message_type`: 1000=文本，50001=系统事件。**新建会话带一条空内容 role=4 的系统通知，
  不算达人回话**（但它的 sender 就是达人 im_id）。
- **建会话** `api/v1/im/conversation/create`：`role:1` 的 uid 必须是 `shop_id`
  （`7494XXXXXXXXXX00`），不是 IM `user_id`。实测建出 `7690XXXXXXXXXX92`、`7690XXXXXXXXXX39`。
- **按用户名搜会话** `api/v1/im/search/search_conversation_by_users` 一次给出
  `core_infos` + `biz_ext`(含 creator_oec_id/handle/avatar) + `setting_infos` + `conv_participants`。
- 联盟侧 `conversation/search?uname=` 恒返回空，**废弃**。
- 同一 CDP 端点两个 Playwright sync 实例会报 `Playwright Sync API inside the asyncio loop` → 复用连接。

### 邀约跟踪联表

- 键 = `creator_oec_id`（达人另有 im_id，别混）。
- `invitation_group/search` → `data.invitation_list`；`detail` → `data.invitation.creator_id_list`。
- `search/creator` 全变体 `98001004`，**放弃**（detail 信息更全）。
- 实测：计划 `7690XXXXXXXXXX47` 10 达人，IM 命中 2、达人回话 0、无会话 8
  （既有 15 个会话全是主动私信进来的达人，不是我们邀约的）。

### 下一步
1. `ensure` 把剩下 8 个受邀达人建会话 → `followup` 群发跟进（换真实话术）。
3. 商品机会模块（已按要求暂停）。

### 联盟 API 全量清单怎么来的（可重跑）

从联盟中心**自己的前端 bundle** 抽的，不是猜的：

```
notes/aff_js_list.py            读已打开的联盟页资源清单（只读，不抢焦点）
  → notes/aff_js_urls.json      49 个 JS
  → notes/aff_js/               46 个 bundle / 33 MB（主 bundle 是 16.7 MB 的达人子模块）
extract_affiliate_paths.py      → notes/api_inventory/enriched.json（路径 + 方法）
gen_affiliate_api.py            → AFFILIATE_API.md
```

三个坑：路径是 `"/api/v" + version + "/oec/affiliate/..."` **拼接**的，只能抓尾部字面量；
方法窗口必须取 `[本字面量, 下一个字面量)`，放宽会串到下一个调用；`adcode`/`keyword`/`task`
那类接口是**同行自己 ERP 的 `/web/*`**，TikTok 联盟侧不存在。

### 财务板块（新）

主机：`api16-normal-sg.tiktokshopglobalselling.com`（**真流量捕获确认**）。

四个前缀：`/api/v1/pay/*`（结算/提现/对账单）、`/api/v1/finance/*`（充值/收单）、
`/api/oec/pay/merchant/statement/*`（新版对账单，无版本段）、`/widget/api/v1/pay/*`（挂件版）。

**抽取踩的四个坑**（都写进 `FINANCE_API.md` 附 B）：
1. **直连，不要走本地代理** —— 走代理 25s 超时，直连 0.6s 拿 494KB。
2. 懒加载 chunk 两种命名：`payoutCycleSetting.k7hkdehg.js` 和 `b5xeyaup.js`（8 位 id 即名）。
3. `mf_finance` 不在 HTML 的 script 标签里，藏在 atlas 注册表的 `source_url`。
4. ★ **路径有 `/api/v` + `${version||1}` 模板形态** —— 只匹配 `v\d` 会整族漏掉 39 个结算接口。

**方法别信静态推断**：代码里写 `method:a.UD`（别名），字面量只占一部分。
`a.UD` == **GET**（实测）。静态标错的 8 个已用真流量纠正。

### 本土店（TK89_Local_Shop

- Hub Studio CDP **CDP_PORT**（HeadlessChrome），域 `seller-vn.tiktok.com`，
  **shop_id `7494XXXXXXXXXX00`**（从 localStorage `__finance_statement_config_v1__` 里读到）。
- 目标三页：`/finance/transactions?tab=settled_tab`、`/finance/withdraw-new`、`/finance/invoice`。
- ⚠ **登录会话已失效** —— 三页全 302 到 `/account/login`，抓不到真实接口和当地 API 主机。
- 本土店与跨境店**共用同一套财务微前端**，路径一致；静态清单已覆盖三页
  （transactions 11 / withdraw-new 28 / invoice 12），见 `FINANCE_API.md` 附 D。
- 补完只需在 SHOP_LOCAL 窗口登录一次，然后 `python3 capture_local_finance.py`（端口已写死 CDP_PORT，
  脚本含登录检测；实测页面数 2 → 2 无残留）。
- 该域直连 / SOCKS5 都是 000，本地代理 302 —— 所以必须在**容器浏览器内**做（页内 fetch + CDP 监听）。

### 财务接口全量探测（零打扰做法）

**关键教训：`ctx.new_page()` 会激活标签 → 打扰操作员。**
改用：借操作员**已打开**的同源页面，页内 `fetch()` 打接口。`fetch` 带 cookie、同源，
且后台标签也能跑（只有 timer 会被节流）。全程零新建标签、零点击、零鼠标、零焦点变化。

- `probe_finance_api.py local|cb` —— 批量探 89 个只读接口；155 个写操作**跳过**（不留垃圾导出任务）
- 结果：`notes/finance_probe_{local,cb}.json`；对照矩阵 `FINANCE_API.md` 附 E
- 实测：本土 101 条 / 跨境 150 条；**仅本土有 23 个**（跨境 `No matching route`）、仅跨境 4 个

**三个坑**：
1. 跨境店 API **不在页面域**上（要打 `api16-normal-sg.*`）；拿页面域打会**落到 SPA 回退返回 HTML**，
   不是 404 —— 极易误判。第一遍 71 个因此被标成未知。
2. 方法错 → **404**（不是参数错）。`POST tax/tax_info/get` 404，`GET` 成功。
3. `/widget/api/v1/tax/*` 要另一套鉴权（`98001002 请登录`）。

**批量下载机制**：两段式 —— 建导出任务 → 轮询 → `.../file` 返回**带签名的临时地址**
（`expire`/`timeStamp`/`sign`）→ GET 该地址取二进制。现签现用，会过期。

### 财务后训练产物

**`tk01_finance.py`** —— 训练好的财务客户端（本土 + 跨境统一接口）。

- 传输：**借已打开页面做页内 `fetch`**，零新建标签 / 零点击 / 零焦点
- 域与鉴权按店铺自动选：本土同源 + `aid=4068`；跨境 `api16-normal-sg.*` + `aid=6556`
- 方法用**实测值**（`a.UD` 别名 = GET），不照抄静态抽取
- `batch_export(kind)` 走完整两段式；`download(url)` 处理签名地址

自检：
```bash
python3 tk01_finance.py --shop tk89 balance   # 实测 12,765₫
python3 tk01_finance.py --shop tk01 settings  # 实测 code=0
```

实测通过的返回：余额 12,765₫ / 余额流水 total=85 / 发票 `TOKVN2026XXXXXXXXXX82` 567,407₫ /
结算账户 `PINGPONG ********055a` / 已结算订单列表（含游标）。详见 `FINANCE_API.md` 附 F。

### 导出历史记录（已打穿）

`GET /api/v1/pay/settlement/file/list` → `data.files[]`，每条：
`{file_id, file_name, period, status, create_time, export_time}`
**status: 1=导出中 2=已导出 3=已查看**（下载后自动 2→3）。
下载：`GET file/download?file_id=<id>` → **`data.url`**（不是 `download_url`）→ GET 取二进制。

建任务 body：`{period:{begin_date,end_date,time_type:1}, file_type, version:1, statement_version:0}`
- 缺 `version` → `98001001 系统错误`
- `22008000 暂无数据可导出` = body 已过校验但该区间没数据
- SHOP_LOCAL 上 `file_type=1` 全区间无数据；**`file_type=7`（待结算订单）立刻成功**

实测全链：建任务 → 历史 `file_id=7690XXXXXXXXXX35` → 签名地址 → **15,482 B 真 xlsx**（`PK\x03\x04`）。
详见 `FINANCE_API.md` 附 G。

### 关键常量
- shop_id / oec_seller_id: `7494XXXXXXXXXX00`
- IM self user_id: `5038XXXXXXXXXX14`（IM 域）/ `7494XXXXXXXXXX00`（店铺域）
- IM api_url: `https://oec-im-tt-sg.tiktokglobalshopv.com/`（**动态**，含 token，10 分钟刷）
- CDP `CDP_PORT`，region `VN`，tz `Asia/Bangkok`
