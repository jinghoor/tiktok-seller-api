# adfly_api 全量接口文档（单文件合并版）

对 `https://ad.aiadfly.com/ad-manage` 的接口逆向产物合并成一份自洽文档。源材料：
`API.md`、`BILL_API.md`、`COMPANY_API.md`、`EXAMPLES.md`、`OPTIMIZATION.md`、`api_tables.md`、
`coverage.md`、`README.md`、`adfly_api/spec/*.json`、`adfly_api/transport.py`、`adfly_api/helpers.py`。

逆向来源：线上 bundle `index-CI-PN84-.js`（`https://ad.aiadfly.com/NUMBER_REDACTED/`，
SHA256 `3f0107d1cb1d0eNUMBER_REDACTEDd21694fef1eaebb104b8a92789c49ecdedeb96c9`）
+ 浏览器实机流量 + 服务端返回码探测。

## 0. 总览

| 项 | 值 |
|---|---|
| 唯一接口 | **291**（原始 293 条去重后） |
| 后端 host | **7** |
| 覆盖测试 | 实测 **199**，跳过写接口 **92** |
| 状态分布 | OK **76** / PARAM 47 / NOAUTH 32 / GONE 33 / ERROR 10 / AUTH 1 |
| 延迟 | p50 **63ms** / p90 279ms / p99 3.1s（含冷启动）/ max 30s |
| 客户端模块 | 8 个文件（7 个接口模块 + 包入口）；`def` 合计 **305**，减 7 个 `__init__` = **298 个业务方法** |
| 认证 | 纯 header，无 cookie：`AuthorizationFront`(JWT, 259 字符) + `CompanyExID` + `country: CN` + `lang: zh-CN` |
| JWT 有效期 | **3 天** |
| 预计算路由 | `adfly_api/spec/routes_builtin.json`，291 条，**0 个歧义** |
| 路由缓存 | `adfly_api/spec/routes.json`（运行时写入，已在 `.gitignore`） |

模块方法数分布（`adfly_api/modules/`，每个文件的 `def` 总数含 `__init__`）：

| 模块文件 | 类 | 方法数 | 负责的接口段 |
|---|---|---|---|
| `advertise.py` | `AdvertiseAPI` | 76 | 广告账户、BC 授权、VSA、GMVmax 全链、报表 + 导出 |
| `ai_agent.py` | `AiAgentAPI` | 70 | 对话、开户引导、GMVmax/VSA 建广告链、OCR、合同、market 系列、`/pay/*` 流水 |
| `finance.py` | `FinanceAPI` | 68 | 结算、应收、返点、Google Ads 残留、`/pay/*` 写 |
| `automation.py` | `AutomationAPI` | 36 | 策略(tactic)、标签(label)、素材组、广告/广告组/系列列表 |
| `front.py` | `FrontAPI` | 33 | 登录、用户、公司、权限菜单、通知、签约流 |
| `finance_bff.py` | `FinanceBffAPI` | 18 | 钱包、充值、优惠券、支付 |
| `mcp_open.py` | `McpOpenAPI` | 4 | OAuth 授权确认、登录信息解密 |
| `__init__.py` | `AdflyClient` | — | 聚合入口 + 常用捷径 |

> 「8 个模块文件」的口径 = 上表 8 行（7 个接口模块 + 包入口 `__init__.py`）；
> 其中 `modules/` 目录下是 7 个接口模块（另有 `modules/__init__.py` 只是 re-export，不含接口）。
> 方法数口径：`grep -c '^    def ' modules/*.py` 合计 **305**，减去 7 个 `__init__` = **298**
> 个接口方法。README / API.md 记的「289 / 293 / 302」是不同轮次的口径，未逐一对账 ——
> 上表数字为本次对源码的实测统计。

归属与解析：清单里的 `backend` 字段是 **bundle 段名**（按页面分块），不是 host；
真正承载某个路径的 host 由 `spec/routes_builtin.json` 给出，两者在多处不同（见 §3）。

---

## 1. 快速上手

```bash
python3 -m pip install requests certifi
```

```bash
cd "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly"

export ADFLY_PASSWORD='你的密码'
python3 -m adfly_api login --account PHONE_REDACTED

python3 -m adfly_api call advertise   POST /tiktok/gmv_max/list '{"page":1,"page_size":5}'
python3 -m adfly_api call finance_bff POST /wallet/list '{"currency":"USD"}'
python3 -m adfly_api raw  advertise   POST /tiktok/auth_list
python3 -m adfly_api list --grep gmv
```

```python
from adfly_api import AdflyClient

c = AdflyClient()                          # 读 .session.json 里的登录态
c.login("PHONE_REDACTED", "密码")              # 首次登录（会踢掉浏览器端会话）

print(len(c.advertisers()), "个广告账户")                                  # 8
print(c.ads.get_gmv_max_list({"page": 1, "page_size": 5})["count"])       # 62
c.download("advertise", "/tiktok/advertiser_report/export", "out.xlsx",   # 导出 xlsx
           {"start_date": "2026-09-01", "end_date": "2026-09-24"})
print(c.stats())
```

CLI 子命令：

| 命令 | 作用 |
|---|---|
| `login --account PHONE_REDACTED [--password ...]` | 登录并缓存 token；密码优先读 `ADFLY_PASSWORD`，否则交互输入 |
| `me [--show-token]` | 当前用户信息 |
| `token [--full] [--company <ex_id>]` | 打印（默认打码）/ 切换 token 与公司 |
| `list [--backend X] [--grep Y] [--path Z]` | 列出接口清单 |
| `call <backend> <METHOD> <path> [json]` | 调用，只打印 `data` |
| `raw  <backend> <METHOD> <path> [json]` | 调用，打印完整信封 |

全局参数：`--env {prod,test}`、`--state <path>`（默认 `~/.adfly/session.json`）、`--verbose`。

`AdflyClient` 的 7 个命名空间与常用捷径：

| 属性 | 类型 | 说明 |
|---|---|---|
| `c.ads` | `AdvertiseAPI` | 广告 BFF |
| `c.auto` | `AutomationAPI` | 自动化 |
| `c.wallet` | `FinanceBffAPI` | 资金 BFF |
| `c.fin` | `FinanceAPI` | 财务 |
| `c.agent` | `AiAgentAPI` | AI Agent |
| `c.front` | `FrontAPI` | 前端主服务 |
| `c.mcp` | `McpOpenAPI` | MCP Open |
| `c.t` | `Transport` | 传输层本体（`c.t.request(...)` / `c.t.paginate(...)`） |
| `c.call(group, method, path, body)` | — | 任意路径，返回 `data` |
| `c.raw(...)` | — | 同上，返回完整信封 `{code,message,request_id,data}` |
| `c.download(group, path, out, body)` | — | 导出接口落盘，返回文件路径 |
| `c.advertisers(page_size=5000)` | list | 广告账户列表 |
| `c.stores(advertiser_id, tt_auth_id)` | list | 店铺列表（GMVmax 前置） |
| `c.auth_accounts()` | list | 已授权 TikTok 账户（`tt_auth_id` 来源） |
| `c.gmv_max_campaigns(**body)` | list | GMVmax 系列列表 |
| `c.companies()` / `c.use_company(ex_id)` | — | 公司列表 / 切换公司上下文 |
| `c.me()` | dict | `/user/info` |
| `c.check_fa(account, password)` | dict | 探测是否需双因素 |
| `c.prewarm(workers=8)` | dict | 按全量清单预热路由缓存 |
| `c.stats()` | str | 运行统计 |

---

## 2. 认证机制

### 2.1 请求头（纯 header，不使用 cookie）

| Header | 值 | 来源 |
|---|---|---|
| `AuthorizationFront` | JWT | 登录返回的 `data.token`（259 字符） |
| `CompanyExID` | 公司外部 ID，如 `10017794444062955153` | `GET /company/list` 返回数组的 `company_ex_id` |
| `country` | `CN` | 固定 |
| `lang` | `zh-CN` | 固定 |

JWT payload 字段：`user_ex_id` / `source` / `exp` / `jti` / `iss`(= `chuangyi.top`) / `nbf`，有效期 **3 天**。

传输层默认还带：`Accept: application/json, text/plain, */*`、
`Content-Type: application/json; charset=UTF-8;`、`Origin: https://ad.aiadfly.com`、
`Referer: https://ad.aiadfly.com/`、Chrome UA 串。

> `GET /user/info` 返回的 `company_id` 是**空字符串** —— 公司上下文不在 body 字段里，只走 `CompanyExID` 头。

### 2.2 登录

```
POST https://front-v1.aiadfly.com/front_api/user/login
{"account": "PHONE_REDACTED", "password": "<md5(明文密码)>"}
```

| 项 | 值 |
|---|---|
| 参数名 | `account`（手机号或邮箱） |
| 密码变换 | **MD5(去空格后的明文)**，前端 `md5(Ie.password.trim())` |
| 成功 | `code=0`，`data` 就是 userInfo（含 `token`、`user_id`、`name`、`menu_info`） |
| 失败 | `code=7 密码错误` / `code=404 用户不存在` |

登录后调 `GET /front_api/company/list`（**GET，不是 POST**）拿公司列表，取 `company_ex_id` 填进 `CompanyExID` 头。
`GET /company/list?yt_platform=1` 是传输层尝试的第二个形态。

**单会话约束**：登录会让同一账号的其它会话失效（旧会话报 `code=9`「账号在别处登录，请重新登录!」）。
Python 端登录后，浏览器里的标签页会被挤下线。

### 2.3 其它认证相关接口

| 接口 | 说明 |
|---|---|
| `POST /front_api/user/check_fa` | `{account, password: md5(pwd)}`，探测是否需双因素 |
| `POST /front_api/user/login/qrcode/create` | 扫码登录 - 生成 |
| `POST /front_api/user/login/qrcode/status` | 扫码登录 - 轮询 |
| `DELETE /front_api/session` | 旧版登出（`/api/session` 路由已下线） |
| `GET /front_api/user/send_code` | 短信/邮件验证码 |

`config.json` 里另存了一套旧版 body 加密参数（`SECRET_KEY` / `SECRET_IV`，AES-128-CBC + PKCS7 → hex，
`transport.aes_encrypt_hex` 复现了它）—— 当前登录链已改为 `md5(password)`，不再使用。

### 2.4 响应信封

`/front_api/*`：

```json
{"code": 0, "message": "ok", "request_id": "xxx", "data": {...}}
```

| code | 含义 |
|---|---|
| 0 / 200 | 成功（客户端两者都当成功） |
| 2 | 未携带 token |
| 7 | 密码错误 |
| 8 / 10 / 11 | 登录态失效类（`transport.AUTH_ERROR_CODES = {2, 8, 9, 10, 11}`） |
| 9 | 账号在别处登录 |
| 11 | `company_ex_id` 参数为空 |
| 400 / 401 | 无权限（部分服务用） |
| 404 | 用户不存在 / 路由不存在 |
| 999 | 业务校验失败（如「广告账号有误」），**message 里是真实原因** |

`ai_agent` 与 `finance-bff` 服务信封不同：`{"code": 400, "reason": "WITHOUT_TOKEN", "message": "..."}`。
缺 `CompanyExID` 头报 `code=400 WITHOUT_COMPANY_HEADER`。

### 2.5 404 语义与路由未命中

路由不存在时返回 **HTTP 404 + 纯文本 `404 page not found`**（不是 JSON，chi 路由风格）。
客户端在 `Transport._is_route_miss()` 里按「status==404 且 body 前 200 字符含 `page not found`」判定，
命中即抛 `AdflyRouteError(404, "404 page not found")` —— 不静默失败。

`error` 层级：

| 异常 | 触发 |
|---|---|
| `AdflyError` | HTTP 通了但 `code != 0`（携带 `code` / `message` / `request_id` / `path`） |
| `AdflyAuthError` | `code ∈ {2,8,9,10,11}`，登录态失效 |
| `AdflyRouteError` | 路径在所有候选 host 上都不存在；或写操作路由无法确证（fail-closed） |
| `AdflyUsageError` | `helpers.py` 的本地参数校验失败（未发请求） |

---

## 3. 后端 host 分布与路由规则

bundle 里的 7 个模块段是按**页面**分块的，域名声明不可直接当 host 用。对**全部 291 个接口 × 6 个 host**
做了对比调用，结论是**每个接口只在一个 host 上成立，0 个歧义**，归属被固化成
`spec/routes_builtin.json`，运行时零探测。

| 服务 key | host | 承载接口数 | 独有/典型接口 |
|---|---|---|---|
| `front` | `https://front-v1.aiadfly.com/front_api` | **160** | `/advertiser/list`、`/tiktok/gmv_max/list`、`/user/*`、`/notice/*`、`/auth/*`、`/company/*` |
| `ai_agent_root` | `https://ai-agent-v1.aiadfly.com` | 52 | `/ai_agent/v1/*`、`/ai_agent/market/*`、`/public/data/report` |
| `automation` | `https://automation-v1.aiadfly.com/front_api` | 34 | `/tactic/*`、`/label*`、`/material*` |
| `advertise_bff` | `https://advertise-bff-v1.aiadfly.com/front_api` | 18 | `/tt/auth/list`、`/tt/bc/list`、`/ad/gmv_max_store_config/*`、`/ad/pixel/list`、`/kanban/google_adv_consume`、`/bc/query_auth`、`/bc/create`、`/pay/adv_*` |
| `finance_bff` | `https://finance-bff-v1.aiadfly.com/front_api` | 15 | `/wallet/*`、`/pay/trade_list`、`/pay/transfer*`、`/pay/online_*`、`/coupon/*` |
| `finance` | `https://finance-v1.aiadfly.com/front_api` | 10 | `/finance/rebate/*`、`/finance/settlement/{overdue-t7,detail/export}`、`/finance/account/payable/detail`、`/finance/company_detail/list` |
| `mcp_open` | `https://mcp-open.aiadfly.com` | 2 | `/oauth/authorize_confirm`、`/decrypt/wlh_login_info` |

> 加总 = 160 + 52 + 34 + 18 + 15 + 10 + 2 = **291**。
> `ai_agent` 在 `config.json` 里另有一个带段前缀的 base `https://ai-agent-v1.aiadfly.com/ai_agent`，
> 与 `ai_agent_root` 并存。
>
> `advertise-bff-v1` 早期被误判为「公网 404」，实际是它的路由集与主网关**不同**：
> `/advertiser/list` 在它上面 404，而 `/tt/auth/list` 只在它上面存在。必须作为独立候选 host。

### 3.1 模块 → 真实 host（按 `routes_builtin.json` 统计，与清单的 `backend` 不同）

| 模块（清单 backend） | front | advertise_bff | finance_bff | finance | automation | ai_agent_root | mcp_open | 合计 |
|---|---|---|---|---|---|---|---|---|
| front | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 31 |
| advertise | 60 | 13 | 0 | 0 | 1 | 0 | 0 | 74 |
| finance_bff | 1 | 0 | 15 | 0 | 0 | 0 | 0 | 16 |
| finance | 51 | 5 | 0 | 10 | 0 | 0 | 0 | 66 |
| automation | 1 | 0 | 0 | 0 | 33 | 0 | 0 | 34 |
| ai_agent | 16 | 0 | 0 | 0 | 0 | 52 | 0 | 68 |
| mcp_open | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 |

值得注意的跨宿主条目（容易踩）：

| 路径 | 清单 backend | 实际 host |
|---|---|---|
| `/finance/billset/{find,need,update}` | finance | **front** |
| `/finance/settlement/{list,detail/list}` | finance | **front** |
| `/finance/settlement/{detail/export,overdue-t7}` | finance | finance |
| `/bc/create`、`/pay/adv_{amount_clear,recharge,reduce}`、`/pay/coupon_recharge` | finance | **advertise_bff** |
| `/ad/list` | advertise | **automation** |
| `/pay/{bill_tips,airpay,llpay,pppay,pay_detail,...}`、`/pay/adv_*_list` | ai_agent | **front** |
| `/activity_link/by_code` | finance_bff | **front** |

### 3.2 候选组定义（`spec/config.json` 的 `groups`）

| 组名 | 候选 host 顺序 |
|---|---|
| `front` | front |
| `advertise` | front → advertise_bff → finance_bff |
| `finance_bff` | finance_bff → front |
| `finance` | finance → front |
| `automation` | automation → front |
| `ai_agent` | front → ai_agent_root → advertise_bff |
| `mcp_open` | mcp_open |

`groups` 只在**预计算表未命中**时用到；正常路径直接吃 `routes_builtin.json`，零探测。

### 3.3 归属规则（`backend_map.py`，唯一权威）

线上 bundle 的 7 个段按页面分块，与真实服务不对应 —— `finance` 段里塞了 Google Ads 的 `/snapshots/*`，
`ai_agent` 段里塞了主网关的 `/notice/*`。只按段决定 host 会让这些接口被打到错的域名上（静默 404）。
所以归属按「段 + 路径」双维度判定：

```python
SECTION_DEFAULT = {"front":"front","advertise":"advertise","automation":"automation",
                   "finance":"finance","finance_bff":"finance_bff","ai_agent":"ai_agent","mcp_open":"mcp_open"}

PATH_RULES = (          # 路径级覆盖，优先于段级
    ("/tt/", "advertise"), ("/kanban/", "advertise"), ("/ad/", "advertise"),
    ("/advertiser/get_pixel_token", "advertise"), ("/bc/query_auth", "advertise"),
    ("/material/", "automation"), ("/material_group/", "automation"),
    ("/tactic", "automation"), ("/label", "automation"), ("/advertiser_label_relation", "automation"),
    ("/notice/", "front"), ("/auth/", "front"), ("/company/", "front"),
    ("/user/", "front"), ("/sign/", "front"),
)

def group_for(section, path):        # 先扫 PATH_RULES 前缀，未命中落 SECTION_DEFAULT
    ...
```

`extract_endpoints.py` 与 `gen_modules.py` 都从这里取，保证清单与代码一致。
`extract_endpoints.py` 会把每行原始段名留在 `section` 字段，纠正后的值写进 `backend`。

### 3.4 环境

`config.json` 定义 `prod` / `test` 两套 base：

| key | prod | test |
|---|---|---|
| front | `https://front-v1.aiadfly.com/front_api` | `https://test-front-new.aiadfly.com/front_api` |
| finance_bff | `https://finance-bff-v1.aiadfly.com/front_api` | `https://finance-bff-dev.aiadfly.com/front_api` |
| finance | `https://finance-v1.aiadfly.com/front_api` | `https://finance-dev.aiadfly.com/front_api` |
| automation | `https://automation-v1.aiadfly.com/front_api` | `https://automation-dev.aiadfly.com/front_api` |
| ai_agent_root | `https://ai-agent-v1.aiadfly.com` | `https://aiagent-dev.aiadfly.com` |
| ai_agent | `https://ai-agent-v1.aiadfly.com/ai_agent` | `https://aiagent-dev.aiadfly.com/ai_agent` |
| mcp_open | `https://mcp-open.aiadfly.com` | `https://mcp-open-dev.aiadfly.com` |
| advertise_bff | `https://advertise-bff-v1.aiadfly.com/front_api` | `https://advertise-bff-dev.aiadfly.com/front_api` |

test 环境未做实测验证。

---

## 4. 客户端结构

```
adfly_api/
├── __init__.py        AdflyClient（聚合 7 个模块 + 会话 + 捷径 + prewarm/stats）
├── __main__.py        python -m adfly_api 入口
├── cli.py             命令行
├── transport.py       传输层：路由解析/探测、登录、重试、错误映射、翻页、下载（707 行）
├── helpers.py         结构化辅助层（536 行）
├── modules/           7 个接口模块（自动生成，勿手改）
│   ├── advertise.py   AdvertiseAPI
│   ├── ai_agent.py    AiAgentAPI
│   ├── automation.py  AutomationAPI
│   ├── finance.py     FinanceAPI
│   ├── finance_bff.py FinanceBffAPI
│   ├── front.py       FrontAPI
│   └── mcp_open.py    McpOpenAPI
└── spec/              清单与缓存
    ├── config.json            后端 base + groups + auth 定义
    ├── endpoints.json         291 条接口清单（fn/method/path/backend/line/section）
    ├── routes_builtin.json    291 条预计算精确路由（"<group>::<path>" → "<hostkey>|<path>"）
    ├── routes.json            运行时探测缓存（.gitignore）
    ├── coverage.json          291 条覆盖测试结果（status/ms/msg/n）
    ├── coverage_summary.json  覆盖统计汇总
    ├── params.json            90 条参数探测记录（34 条摸清必填字段）
    ├── host_matrix.json       全量 host 对比矩阵（判定归属的依据）
    ├── unavailable.json       33 条死接口清单
    ├── company_menu.json      66 节点权限树原始数据
    ├── company_endpoints.json 公司/子账号/权限接口清单
    └── bill_endpoints.json    账单接口清单
```

模块方法签名统一是 `def xxx(self, body=None, **kw)`，透传给 `Transport.post/get`；
docstring 里带实测必需字段与可用 body 样例（34 个方法有）。模块类上的
`BACKENDS` / `_GROUP_DEFAULT` 只用于生成期自检，运行期 host 由 `Transport.resolve()` 决定。

`.session.json` 存 token / `company_ex_id` / user / companies / country / lang，写盘后 `chmod 600`；
`session.valid` 只看 `token` 非空。字段顺序不变，未知字段在读入时忽略。

---

## 5. 传输层机制

### 5.1 路由缓存与预计算表

三层，优先级从高到低：

1. **预计算表** `spec/routes_builtin.json` —— 全量实测产出，命中即用，计 `route_builtin_hits`。
2. **运行时缓存** `spec/routes.json` —— 探测命中后写入，计 `route_cache_hits`。格式
   `{"<group>::<path>": {"cache_key": ..., "route": "<hostkey>|<path>"}}`；
   兼容 v1 的纯字符串格式（自动升级成 `<host>|`）。
3. **探测** —— 按 `groups` 候选 × 路径变体依次试，命中即缓存。

预计算表的 value 是 `<hostkey>|<path>`（`<path>` 不带前导 `/`）；若 `hostkey` 不在当前环境
（例如切到 test），会打 log 并继续走缓存/探测，不会静默用错 host。

`build_routes.py` 生成这张表的三级策略，按顺序：

1. **实测矩阵 `host_matrix.json`** —— `host_compare.py` 对每个接口在 6 个候选 host 上实调，
   取业务响应一致（而非仅 HTTP 200）的那个，得到精确归属。key 形态是 `"<group>::<METHOD> <path>"`，
   生成时拆出 `<path>`。
2. **手写精确表 `EXCLUSIVE`** —— 只在某一个 host 上 OK 的接口清单，按 host 分组硬编码：

   | host | 条目 |
   |---|---|
   | `advertise_bff` | `/ad/pixel/list`、`/ad/store_app_info/get`、`/bc/create`、`/bc/query_auth`、`/tt/bc/list`、`/tt/bc/is_adv_bound`、`/tt/admin_store/list`、`/ad/gmv_max_store_config/{get,list,list_by_store_id,delete}`、`/kanban/google_adv_consume{,/export}`、`/pay/adv_amount_clear`、`/pay/adv_recharge`、`/pay/adv_reduce`、`/pay/coupon_recharge` |
   | `finance_bff` | `/wallet/list`、`/wallet/{currency,wallet,company}/exchange`、`/wallet/sub_company/list`、`/wallet/calculate_reverse_exchange_amount`、`/pay/trade_list{,/export}`、`/pay/transfer{,/_detail}`、`/pay/online_worldfrist`、`/pay/online_cogolinks`、`/pay/pay_detail`、`/coupon/{list,detail/list,has_point}`、`/activity_link/by_code` |
   | `finance` | `/finance/account/payable/detail`、`/finance/company_detail/list`、`/finance/rebate/{company_detail/confirm,recharge,rule/list,rule_detail/list,adv_detail/list,export}`、`/finance/settlement/{detail/export,overdue-t7}`、`/finance/billset/{find,update}` |
   | `automation` | `/tactic/{add,edit,list,find,delete,bind,unbind,status/update,adv/list}`、`/label/{list,add,del}`、`/label_category/{list,add,del}`、`/advertiser_label_relation/{find,bind,unbind}`、`/tactic_action_log/{list,export}`、`/tactic_change_log/{list,export}`、`/material/list`、`/material_group/{list,add,edit,del,detail}`、`/ad/list`、`/adgroup/list`、`/campaign/list`、`/advertiser/list` |
| `ai_agent_root` | `/ai_agent/v1/session_id/create`、`/ai_agent/v1/message/reset`、`/ai_agent/v1/adv/list`、`/ai_agent/market/session_id/create` |

   另有一条规则：路径以 `/ai_agent/` 开头且 `ai_agent_base` 可用 → 直接判 `ai_agent_root`。
3. **组内默认** —— 上面都没命中时，按 `groups` 候选顺序（并用 `MEASURED` 的实测命中数给候选排序）取第一个。

生成脚本会打印 `实测命中 N / 手写精确 N / 组默认 N / 无 host N` 四个计数。

### 5.2 `_variants()` 路径变体

`ai_agent` 段的路径自带 `/ai_agent/` 段，但同一段里也混了 `/notice/*` 这类主网关路径。
所以一个 host 上要试两种形态：

```python
urls = [cls._join(base_url, path)]
stripped = re.sub(r"^/ai_agent(?=/)", "", "/" + path.lstrip("/"))
if stripped != "/" + path.lstrip("/"):
    urls.append(base_url + stripped)
```

> 只试原路径曾导致 `bell_list` 被静默打到错的服务上。

`_join()` 处理「base 自带 `/ai_agent` 而路径也以 `/ai_agent/` 开头」的叠段，避免拼成
`.../ai_agent/ai_agent/...`。

`_candidates()` 对 `ai_agent` 组还会按路径形态给候选排序（自带 `/ai_agent/` 段 → `ai_agent_root` 排前），
把探测次数从「总是试两个」降到「通常一次命中」。

### 5.3 探测判定：hit / miss / maybe

`_probe_one(url)` 用 `POST` + 空 body，超时 `min(timeout, 12)`，`probe_attempts` 默认 2 次：

| 判定 | 条件 | 用途 |
|---|---|---|
| `_HIT` | 非 404、非 5xx | 记为归属 |
| `_MISS` | HTTP 404 且 body 含 `page not found` | 继续下一个候选 |
| `_MAYBE` | HTTP ≥ 500，或网络异常 | 记入 `maybe[]`，**不作为归属证据** |

5xx 不能作为归属证据：参数对但服务端内部错时别的 host 也会同样报错 ——
实测 `automation` 对 `/advertiser/list` 回 500，`front` 才是真身。

### 5.4 写操作 fail-closed

| 情况 | 读操作（GET/HEAD） | 写操作（POST/PUT/PATCH/DELETE） |
|---|---|---|
| 有候选返回 `_MAYBE` | 用第一个候选，让真实业务错误暴露 | **抛 `AdflyRouteError`**，提示显式传 `group=` |
| 全部候选 `_MISS` | 回退第一个候选 | **抛 `AdflyRouteError`**，不猜 host |

`_writes_to_state(method)` 是唯一判据。这是为了防止「写错服务」。

### 5.5 超时分类重放

按**失败阶段**区分安全性 —— 调试期反复遇到 TLS 握手超时，原来的重试逻辑对写操作太脆：

| 失败类型 | 请求是否已发出 | 写操作（POST） | 读操作（GET） |
|---|---|---|---|
| `ConnectTimeout` / TLS 握手超时 | 否 | **重放 1 次** | 重放满 `retries` |
| `ConnectionError` | 否 | **重放 1 次** | 重放满 `retries` |
| `ReadTimeout` | 可能已处理 | **不重放**（计 `unsafe_timeouts`） | 重放满 `retries` |

实现要点：`attempts = (retries + 1) if idempotent else 2` ——
循环上界对写操作也留一次，真正的收紧在循环内按失败类型决定。
（原实现 `range(attempts)` 对非幂等请求就是 `range(1)`，内层「连接阶段可重放」永不执行 ——
这个 bug 是单元测试 `TestTimeoutReplaySafety` 抓出来的。）

离线验证记录：

```
ConnectTimeout     POST  2 次调用   OK(重放一次)
ReadTimeout        POST  1 次调用   OK(不重放)
ReadTimeout        GET   3 次调用   OK(重放满 retries)
ConnectionError    POST  2 次调用   OK
```

默认幂等判据：`method in ("GET", "HEAD")`；也可显式 `idempotent=True/False` 覆盖 ——
`download()` 固定传 `idempotent=False`。

### 5.6 429 / 503 退避与 5xx 重试

| 状态 | 行为 |
|---|---|
| 429 / 503 | 读 `Retry-After`（上限 30s）退避；无该头则 `1.0 * 2**attempt`。已是最后一次且非幂等 → 抛 `AdflyError(429/503, "被限流,Retry-After=...")` |
| ≥ 500 | 还有剩余尝试则 `0.6 * 2**attempt` 后重试 |
| 超时 | `0.6 * 2**attempt + random()*0.3` |
| 其它 `RequestException` | `0.4 * 2**attempt + random()*0.2` |

`Retry-After` 值解析失败（`ValueError`）时回落到指数退避。

### 5.7 连接池

`requests.Session` + 自定义 `HTTPAdapter`：`pool_connections` / `pool_maxsize` = `max(10, pool_size)`，
默认 `pool_size=32`；`max_retries=0`（重试自己控，不用 urllib3 的）；`pool_block=False`。
默认 pool_maxsize=10 时并发 32 会反复建连，实测换用后每次省约 60% 延迟。

### 5.8 可选自动重登

`c.t.enable_auto_relogin(account, password)` 记住凭证（**不落盘**）后，
遇 `code ∈ AUTH_ERROR_CODES` 会加锁重登一次并立即重放该请求；
并发下只有一个线程真正去登（`_relogin_lock`）。默认不启用，统计计数写在 `stats["relogins"]`。

`AUTH_ERROR_CODES = {2, 8, 9, 10, 11}` —— README 里简写为「遇 code=2/9 自动重登」，代码实际是这 5 个。

### 5.9 prewarm

```python
c.prewarm(workers=8)              # 按 spec/endpoints.json 全量 (backend, path, method) 预热
c.t.prewarm([("advertise", "/tiktok/gmv_max/list", "POST"), ...], workers=8)
```

已缓存的 `(group, path)` 跳过；返回 `{"resolved": n, "skipped": m}`；
失败项只打 debug log，不抛。线程池 `ThreadPoolExecutor(max_workers=workers)`。

### 5.10 stats

`c.stats()` → `Transport.stats_report()`，人类可读一行：

```
业务请求 N / 探测 N / 重试 N / 重登 N / 路由命中(预计算 N + 缓存 N) / 错误 N  (探测占比 x.x%[, 写操作遇读超时 N 次])
```

计数字段：`requests`、`probes`、`retries`、`relogins`、`route_cache_hits`、`route_builtin_hits`、
`errors`、`unsafe_timeouts`。

### 5.11 分页与下载

```python
c.t.paginate(group, path, body=None, page_size=100, max_pages=200)   # 生成器，逐条吐 list 元素
```

翻页逻辑：`body.update({"page": page, "page_size": page_size})`，元素取自 `data["list"]` 或 `data["data"]`；
空列表或不足 `page_size` 即停。

```python
c.download("advertise", "/tiktok/advertiser_report/export", "out/adv.xlsx", body)
```

走 `response_type="blob"`，自动 `mkdir -p` 父目录，返回落盘路径。

### 5.12 响应的特殊形态

| 形态 | 判定 | 客户端行为 |
|---|---|---|
| 二进制（xlsx/csv） | `content-type` 含 `spreadsheet`/`octet-stream`，或 body 以 `PK` / BOM 开头 | `c.call()` 时抛 `AdflyError(200, "二进制响应(导出文件),请用 download() ...")` |
| SSE 流 | `content-type` 含 `event-stream` | 抛 `AdflyError(200, "SSE 流式响应(content-type=...)")`，实测 `/ai_agent/market/stream/stop` |
| 非 JSON | 解析失败且非上述 | 抛 `AdflyError(code, "非 JSON 响应(content-type=?): ...")`，实测 `/advertiser/get_panda_token` |
| 非标准信封 | 有 `code` 键但无 `data` | 原样返回 envelope |
| `code ∈ {0, 200}` | — | `raw=False` 返回 `data`；`raw=True` 返回完整信封 |

---

## 6. 核心业务链路详解

### 6.1 广告账户

```
POST /front_api/advertiser/list
{"page": 1, "page_size": 5000, "platform": 1}
```

实测返回 **8 个账户**。关键字段（真实数据）：

```json
{
  "advertiser_id": "7689XXXXXXXXXX05",
  "advertiser_name": "Adfly-Adfly-DAMAI-TK178-2931-1-8758-1",
  "company_ex_id": "10017794444062955153",
  "company_name": "广西大迈进出口贸易有限公司",
  "owner_bc_id": "7418XXXXXXXXXX24",
  "port": "CN", "currency": "USD", "platform": 1,
  "status": 1, "status_new": "STATUS_ENABLE", "bind_status": 2,
  "balance": 0, "can_clear": 1, "clear_amount": 0,
  "min_recharge_amount": 10, "pay_type": 0, "timezone": ""
}
```

其它账户接口：

| 接口 | 方法 | 说明 |
|---|---|---|
| `/advertiser/config` | GET | OK，5 条 |
| `/advertiser/apply` | POST | 开户申请（写） |
| `/advertiser/apply_list` | POST | OK，4 条 |
| `/advertiser/apply_list/export` | POST | OK(bytes) |
| `/advertiser/apply_detail` | POST | AUTH —— `code=11 开户记录不存在`（唯一 AUTH 状态） |
| `/advertiser/list/export` | POST | OK(bytes) |
| `/advertiser/advertiser_update` | POST | 实测 NOAUTH（`batch is empty`） |
| `/advertiser/get_apply_limit_num` | POST | OK，1 条 |
| `/advertiser/tt_create_task_list` | POST | OK，3 条（创建广告日志，见 §6.5） |
| `/tiktok/advertiser_balance_get` | POST | OK，0 条 |

### 6.2 商务中心授权（BC）

**完整链路（全部实测）**：

```
1) GET  /advertiser/get_auth_link?platform=1     → 拿 TikTok OAuth 链接
2) 浏览器打开该链接，在 TikTok 侧完成授权           → 回调 redirect_uri
3) POST /advertiser/adv_bc_bind_list             → 查绑定任务（含 task_id）
4) POST /tt/bc/list {tiktok_auth_id}             → 查该授权下可操作的 BC
5) POST /advertiser/adv_bc_bind                  → 建绑定任务（非幂等，见下）
```

#### 授权链接

```
GET /front_api/advertiser/get_auth_link?platform=1
```

**`platform` 必填**，缺了报 `code=999 server_invalid_platform`。
实测返回：

```json
{"auth_link": "https://business-api.tiktok.com/portal/auth
   ?app_id=7323XXXXXXXXXX09
   &state=10017794444062955153_11017794444062945153_7323XXXXXXXXXX09_44517902644465904424
   &redirect_uri=https%3A%2F%2Ffront.aiadfly.com%2Ffront_api%2Fadvertiser%2Fadv_auth"}
```

`state` 结构（下划线分隔四段）：

| 位置 | 含义 | 实测值 |
|---|---|---|
| 0 | company_ex_id | `10017794444062955153` |
| 1 | user_ex_id | `11017794444062945153` |
| 2 | app_id | `7323XXXXXXXXXX09` |
| 3 | 随机 nonce | `44517902644465904424` |

`redirect_uri` 是 `https://front.aiadfly.com/front_api/advertiser/adv_auth` —— TikTok 授权完成后回这里，
服务端据 `state` 绑定到对应公司/用户。**这一步必须在浏览器完成，无法用纯 HTTP 客户端替代。**

`platform` 枚举（`helpers.auth_link` docstring）：`1`=TikTok、`2`=FaceBook、`3`=Google、`4`=ASA。
默认 `platform=1`。服务端另返回 `link_ex_id`（等于 `state` 第 4 段），轮询查授权结果要用它。

#### 查授权结果

```
POST /bc/query_auth  {"company_ex_id": "<ex_id>", "auth_link_ex_id": "<link_ex_id>"}
```

实测必填 `auth_link_ex_id:string`（已实调跑通）。前端拿到授权链接后就开轮询，
直到 `data.result` 出现才算授权成功。`helpers.check_auth_result(c, link_ex_id, timeout=..., interval=3.0)`
封装了它：`timeout=0` 只查一次，返回 `{result, auth, polls}`。

#### 可用商务中心

```
POST /tt/bc/list  {"tiktok_auth_id": 1960}
```

实测返回：

```json
{"list": [{
  "bc_detail": {
    "bc_id": "7457XXXXXXXXXX28", "name": "VNKQQS20",
    "company": "CÔNG TY TNHH MTV THUẬN NAM ĐẮK NÔNG",
    "currency": "USD", "registered_area": "VN", "status": "ENABLE",
    "timezone": "Asia/Ho_Chi_Minh", "type": "SELF_SERVICE",
    "verification_status": "NOT_SUBMITTED"
  },
  "user_role": "ADMIN",
  "ext_user_role": {"finance_role": "MANAGER"}
}]}
```

`tiktok_auth_id` 来自 `/tiktok/auth_list` 返回的 `id`（**类型是 number**，实测 1960）。
`/tt/auth/list` 实测 3 条。

#### 查账户挂靠的 BC

```
POST /advertiser/get_bind_bc  {"bc_id": "<账户的 owner_bc_id>", "advertiser_id": "...", "platform": 1}
→ [{"bc_id": "7626XXXXXXXXXX75", "bc_name": "Bnjg"}]
```

三个易错点：

- `bc_id` 传的是**账户自己的 `owner_bc_id`**（来自 `advertiser/list`），不是目标 BC
- **`platform` 必填** —— 不带会返回 `data=null`（不是报错，容易误判成「没有绑定」）
- 传目标 BC 的 id → `code=999 "No permission to view or operate."`

#### 绑定任务记录

```
POST /advertiser/adv_bc_bind_list  {"page":1,"page_size":50}
```

```json
{"task_id": "28017902444525234531", "platform": "1",
 "advertiser_id": "7689XXXXXXXXXX74", "advertiser_name": "Adfly-Adfly-DAMAI-...",
 "bc_id": "7626XXXXXXXXXX75", "company_ex_id": "10017794444062955153",
 "status": 2, "remark": "", "port": "CN",
 "created_at": "2026-09-24T18:08:51.839+08:00", "updated_at": "..."}
```

**status 含义**（实测，含一个反直觉点）：

| status | 含义 |
|---|---|
| 0 | 未知/初始 |
| 1 | 未知/中间态 |
| **2** | **有效（绑定生效）** —— 终态，前端以 `status === 2` 禁止再操作 |
| 3 | 未知/中间态 |
| 4 | 提交后未落定 |

**`4` 不等于失败。** 实测有记录先落 `4`、几分钟后自行变成 `2` —— 服务端是异步推进的。
判断「还在处理中」不能只看 status，要结合 `updated_at - created_at` 的时间差。
`helpers.pending_bind_records(c)` 就是按「时间差 < 5 秒」找刚提交未推进的记录。

另有 `/advertiser/bc_un_bind_list`（待绑定，OK，3 条）与
`/advertiser/adv_bc_bind_list/export`（导出 xlsx，OK(bytes)）。

#### 绑定 / 解绑

```
POST /advertiser/adv_bc_bind
{"advertiser_id": ["<id>"], "bc_id": "<目标 BC>", "task_id": "<任务 id>", "platform": 1}
```

字段名是**套出来的**，有两个坑：

- `advertiser_id` 是**数组** —— 传字符串会触发 Go 反序列化错误
  `json: cannot unmarshal string into Go struct field AdvBcBind...`
- 缺 `bc_id` 报 `bc_id(mcc_id)为空`；字段名不是 `advertiser_ids` / `bind_bc_ids`

字段名定位过程（类型错误反推）：

```
{"advertiser_id": "字符串"} → json: cannot unmarshal string into Go struct field AdvBcBind...
{"advertiser_id": ["数组"]} → bc_id(mcc_id)为空
{"advertiser_id": [...], "bc_id": "..."}  → code=0
```

顺手排除了 `advertiser_ids` / `adv_ids` / `advertiser_id_list` 等一票猜测 ——
它们全都返回「广告账号id列表为空」，说明字段名不是这些。

**`adv_bc_bind` 不是幂等的，而且是真写。** 同一个 `adv+bc` 每调一次就新增一条绑定任务记录 ——
实测重复调用后 `adv_bc_bind_list` 从 9 条涨到 11 条，且新记录最终落到 `status=2`（绑定生效）。
**没有「取消绑定任务」的接口**，唯一的撤销路径是 `bc_un_bind_single` 解绑。
调用前必须先用 `adv_bc_bind_list` 查一遍，确认该 `adv+bc` 没有已有记录。

事故记录（`OPTIMIZATION.md`）：用 `adv_bc_bind` 做参数探测时真的创建了 3 条绑定任务记录 ——
`adv_bc_bind_list` 从 9 条涨到 11 条（两次调用，其中一次带全 0 的假 task_id）再加 1 条更早的探测。
初次看到 `status=4` 时判断为「失败记录」，后续复查发现已变成 `status=2`。
账户 `7689XXXXXXXXXX05` 上留下 3 条指向 BC `7626XXXXXXXXXX75` 的记录，时间戳集中在 04:04。

```
POST /advertiser/bc_un_bind_single
{"bc_id": "<owner_bc_id>", "un_bind_bc_id": "<要解绑的 BC>", "advertiser_id": "...", "platform": 1}
```

两个 bc 字段不是一个东西：`bc_id` 是账户自己所属的 BC，`un_bind_bc_id` 才是要摘掉的那个
（来自 `get_bind_bc` 或 `adv_bc_bind_list` 的 `bc_id`）。前端还提示：**解绑后需要重新授权**。

批量解绑用 `/advertiser/bc_un_bind_multi`（空 body 报 `广告账号为空`）。
`helpers.normalize_bc_ids(text)` 复现前端的 `normalizeBindBcIdsForApi`，
把中文全角逗号 `，`、多余空格规范化成逗号分隔字符串。

#### 其它 BC 接口

| 接口 | 参数 | 备注 |
|---|---|---|
| `/bc/create` | `tiktok_auth_id`(>0) | 新建 BC（承载在 advertise_bff） |
| `/bc/query_auth` | `auth_link_ex_id` | 查授权链接状态 |
| `/tt/bc/is_adv_bound` | `bc_id`, `advertiser_id`, `tt_auth_id` | 某 BC 下是否有账户 |
| `/tt/admin_store/list` | `tiktok_auth_id`, `bc_id` | BC 下的店铺 |
| `/ai_agent/v1/advertiser/pre_bind_bc` | `{task_id, bind_bc_ids}` | AI Agent 路径的预绑定 |
| `/advertiser/adv_bc_bind`（ai_agent 路径） | — | 实测 `code=999 广告账号id列表为空`（NOAUTH） |

### 6.3 GMVmax 推广系列（核心）

#### 查询

```
POST /front_api/tiktok/gmv_max/list
{"page": 1, "page_size": 10}
→ {"count": 62, "list": [...], "total_data": ...}
```

**实测返回 62 条**。单条字段（33 个，真实数据）：

```json
{
  "advertiser_id": "7686XXXXXXXXXX08", "advertiser_name": "DAMAI-SHOP_X3",
  "campaign_id": "1877XXXXXXXXXX22",
  "campaign_name": "商品 GMV Max_总收入_VUNOVA_1735XXXXXXXXXX50",
  "store_id": "8657XXXXXXXXXX38", "store_name": "",
  "shopping_ads_type": "PRODUCT",
  "product_specific_type": "CUSTOMIZED_PRODUCTS",
  "product_video_specific_type": "AUTO_SELECTION",
  "roas_bid": 20, "budget": 200,
  "schedule_type": "SCHEDULE_FROM_NOW",
  "schedule_start_time": "2026-09-24T17:50:53+08:00",
  "schedule_end_time": "2036-09-21T17:50:53+08:00",
  "status": "STATUS_DELIVERY_OK", "second_status": "CAMPAIGN_STATUS_ENABLE",
  "operation_status": "ENABLE",
  "item_group_ids": ["1735XXXXXXXXXX50"],
  "item_group_ids_str": "[\"1735XXXXXXXXXX50\"]",
  "cost": 0.01, "net_cost": 0, "orders": 0, "cost_per_order": 0,
  "gross_revenue": 0, "roi": 0,
  "port": "CN", "currency": "USD",
  "company_ex_id": "10017794444062955153", "user_ex_id": "auto",
  "create_time": "2026-09-24T09:54:10+08:00", "modify_time": "..."
}
```

按账户过滤 / 排序：

```python
c.ads.get_gmv_max_list({
    "page": 1, "page_size": 50,
    "advertiser_ids": ["7686XXXXXXXXXX08"],
    "order_info": {"field": "cost", "order_type": "desc"},
})
```

#### 新建链路（4 步，全部实测）

```
1) POST /front_api/tiktok/auth_list            → tt_auth_id（实测 3 个授权）
2) POST /front_api/tiktok/gmv_max/store/list   {advertiser_id, tt_auth_id}
3) POST /front_api/tiktok/gmv_max/identity/get {advertiser_id, store_id, store_authorized_bc_id, tt_auth_id}
4) POST /front_api/tiktok/gmv_max/create       {batch:[...], tt_auth_id}
```

第 2 步实测拒绝无权限账户：`code=999 获取店铺列表失败: No permission to operate advertiser: <id>`。
8 个账户里只有 `7642XXXXXXXXXX57`(DAMAI-TK20) 能取到店铺。

第 2/3 步实测输出：

```json
// store/list
{"store_id": "8648XXXXXXXXXX10", "store_authorized_bc_id": "7457XXXXXXXXXX28",
 "is_gmv_max_available": true, "is_owner_bc": true, ...}

// identity/get → 3 个
[{"identity_id": "b0094b9c-c0e3-59dc-a9d6-d4c3cb3def11", "identity_type": "BC_AUTH_TT",
  "display_name": "Thủy Tinh Ca", "identity_authorized_bc_id": "7457XXXXXXXXXX28",
  "product_gmv_max_available": true, "live_gmv_max_available": true,
  "is_running_custom_shop_ads": false}]
```

#### `POST /tiktok/gmv_max/create` 请求体

从 bundle 的 `useSubmit$2` 提取的构造规则：`batch` 里是 campaign 对象，同时传 `tt_auth_id`；
`identity_id_list` / `item_group_list` / `tt_auth_id` / `promote_all_products` 在提交前被 `omit` 掉，
`schedule_start_time` 格式化成 `YYYY-MM-DD HH:mm:ss`，`promote_all_products=true` 时
`product_specific_type` 变成 `ALL` 且 `item_group_ids` 也去掉。

```json
{
  "batch": [{
    "advertiser_id": "7642XXXXXXXXXX57",
    "store_id": "8648XXXXXXXXXX10",
    "store_authorized_bc_id": "7457XXXXXXXXXX28",
    "campaign_name": "商品 GMV Max_总收入_VUNOVA_xxx",
    "shopping_ads_type": "PRODUCT",
    "product_specific_type": "CUSTOMIZED_PRODUCTS",
    "product_video_specific_type": "AUTO_SELECTION",
    "optimization_goal": "VALUE",
    "deep_bid_type": "VO_MIN_ROAS",
    "roas_bid": 3,
    "budget": 300,
    "schedule_type": "SCHEDULE_FROM_NOW",
    "schedule_start_time": "2026-09-24 17:50:53",
    "schedule_end_time": "2036-09-21 17:50:53",
    "item_group_ids": ["1735XXXXXXXXXX50"],
    "identity_list": [{ ...identity/get 的元素... }]
  }],
  "tt_auth_id": 1960
}
```

枚举值（bundle 常量）：

| 字段 | 取值 |
|---|---|
| `shopping_ads_type` | `PRODUCT` |
| `product_specific_type` | `CUSTOMIZED_PRODUCTS` 或 `ALL` |
| `product_video_specific_type` | `AUTO_SELECTION` |
| `optimization_goal` | `VALUE` |
| `deep_bid_type` | `VO_MIN_ROAS` |
| `schedule_type` | `SCHEDULE_FROM_NOW`（`helpers.SCHEDULE_TYPES` 另有 `fixed` → `SCHEDULE_FIXED`） |

默认值 `roas_bid=3`, `budget=300`（`genDefaultCampaignData`）。
`tt_auth_id` 在 `identity/get` 里是 **Number**，`store/list` 里原样传。

**完整 4 步可跑代码**：

```python
AID = "7642XXXXXXXXXX57"      # 唯一有店铺权限的账户
TTA = 1960                       # tt_auth_id，来自 auth_list

auth = c.auth_accounts();  tta = auth[0]["id"]                       # 步骤 1
store = c.stores(AID, tta)[0]                                        # 步骤 2
store_id, bc_id = store["store_id"], store["store_authorized_bc_id"]
identities = c.ads.get_gmv_max_identity_list({                        # 步骤 3
    "advertiser_id": AID, "store_id": store_id,
    "store_authorized_bc_id": bc_id, "tt_auth_id": tta,
})["list"]
c.ads.check_occupied_custom_shop_ads({                                 # 前置占用校验
    "batch": [{"advertiser_id": AID, "store_id": store_id,
               "occupied_asset_type": "SPU", "asset_ids": ["1735XXXXXXXXXX50"]}],
    "tt_auth_id": tta,
})
c.ads.create_gmv_max_ad({                                              # 提交
    "batch": [{
        "advertiser_id": AID, "store_id": store_id, "store_authorized_bc_id": bc_id,
        "campaign_name": "商品 GMV Max_总收入_TEST",
        "shopping_ads_type": "PRODUCT",
        "product_specific_type": "CUSTOMIZED_PRODUCTS",
        "product_video_specific_type": "AUTO_SELECTION",
        "optimization_goal": "VALUE", "deep_bid_type": "VO_MIN_ROAS",
        "roas_bid": 3, "budget": 300,
        "schedule_type": "SCHEDULE_FROM_NOW",
        "schedule_start_time": "2026-09-25 10:00:00",
        "schedule_end_time": "2036-09-21 10:00:00",
        "item_group_ids": ["1735XXXXXXXXXX50"],
        "identity_list": identities[:1],
    }],
    "tt_auth_id": tta,
})
```

改预算 / ROI（改已有系列，先取详情再回传合并）：

```python
existing = c.ads.get_gmv_max_list({"page": 1, "page_size": 1})["list"][0]
c.ads.edit_gmv_max_ad(H.gmv_max_edit(existing, budget=500, roas_bid=4, tt_auth_id=TTA))
```

#### 前置校验（建广告前必须调）

```
POST /front_api/tiktok/gmv_max/occupied_custom_shop_ads/list
{"batch": [
  {"advertiser_id": "...", "store_id": "...", "occupied_asset_type": "SPU", "asset_ids": ["<item_group_id>"]},
  {"advertiser_id": "...", "store_id": "...", "occupied_asset_type": "IDENTITY_BC_AUTH_TT", "asset_ids": ["<identity_id>"]}
], "tt_auth_id": 1960}
```

`occupied_asset_type` 枚举：`IDENTITY_BC_AUTH_TT` 或 `SPU`。返回冲突列表，非空时前端弹确认框。
实测状态 OK（返回体无 `list`，按空处理）。`helpers.gmv_max_occupancy_batch(...)` 负责拼这个 body。

#### 其它 GMVmax 接口

| 接口 | 方法 | 参数 / 实测 |
|---|---|---|
| `/tiktok/gmv_max/detail` | POST | `{campaign_id}`；实测 OK，32 条 |
| `/tiktok/gmv_max/update` | POST | 同 create 结构（写） |
| `/tiktok/gmv_max/copy` | POST | 复制（写） |
| `/tiktok/gmv_max/refresh` | POST | 手动更新（实测 `{}` 即可，OK，183ms） |
| `/tiktok/gmv_max/get_refresh_time` | POST | `{}` → `{"refresh_time":"...","status":2}`；实测 OK，2 条 |
| `/tiktok/gmv_max/get_detail_info` | POST | 实测 NOAUTH `code=999 record not found` |
| `/tiktok/gmv_max/export` | POST | 导出 xlsx（OK(bytes)） |
| `/tiktok/gmv_max/group_item_report` | POST | 商品维度报表；实测 NOAUTH `record not found` |
| `/tiktok/gmv_max/post_item_report` | POST | 素材维度报表；实测 OK，0 条 |
| `/tiktok/gmv_max/store/shop_ad_usage_check` | POST | `{advertiser_id, store_id, tt_auth_id}` |
| `/tiktok/gmv_max/import` | POST | 导入 |
| `/ad/gmv_max_store_config/{list,get,delete,list_by_store_id}` | POST | 店铺配置；`list` / `list_by_store_id` OK（0 条），`get` PARAM |
| `/ai_agent/v1/ad/gmv_max/{store/list,store/config,identity/list,store/product/list,store_id/validate,occupied_custom_shop_ads/list}` | POST | AI Agent 路径的同名能力，见 §6.8 |

### 6.4 VSA / 普通广告

| 接口 | 方法 | 改写实测状态 |
|---|---|---|
| `/tiktok/create_advertisement` | POST | NOAUTH `商品或素材参数有误` |
| `/tiktok/create_advertisement_new` | POST | NOAUTH `广告账号为空`（**批量新建，VSA**） |
| `/tiktok/ad_detail` | POST | NOAUTH |
| `/tiktok/ad_modify` | POST | NOAUTH |
| `/tiktok/adgroup_detail` / `adgroup_modify` | POST | NOAUTH |
| `/tiktok/campaign_detail` / `campaign_modify` | POST | NOAUTH |
| `/tiktok/adgroup_extend` | POST | NOAUTH（扩量） |
| `/tiktok/copy_advertisement` | POST | NOAUTH（复制） |
| `/tiktok/modify_campaign_status_multi` | POST | 批量开关 |
| `/tiktok/get_opt_campaign` | POST | OK，0 条（可选推广系列） |
| `/tiktok/get_videos` / `get_video_url` | POST | NOAUTH（素材） |
| `/tiktok/get_ad_detail_list` | POST | NOAUTH（广告明细） |
| `/tiktok/get_config` | POST | NOAUTH `advertiser_id nil` |
| `/tiktok/identity_get` | POST | PARAM `Key: 'IdentityListReq.AccessToken' Error...` |
| `/tiktok/adv_unionpay_check` | POST | NOAUTH `license_no: value is required but missing`（1349ms） |
| `/ad/smart_plus/v2/create` | POST | Smart+ 新建（走 advertise 域） |
| `/ad/pixel/list` | POST | PARAM，必填 `advertiser_id:string` —— **注意源文档 `API.md` 标它「当前版本 404」，实测路由通** |
| `/ad/store_app_info/get` | POST | PARAM，必填 `query:string, country:string` |
| `/ad/list` | POST | ERROR `failed to find adgroup info`（承载 host 是 automation） |

**批量创建表单默认值**（`batchCreateAdvAPI` 对应的 VSA 表单）：

```json
{"objective_type": "PRODUCT_SALES", "campaign_product_source": "STORE",
 "campaign_name": "", "budget_mode": "BUDGET_MODE_INFINITE", "budget": null,
 "advertiser_id": null}
```

### 6.5 报表与导出

所有报表接口 body 结构一致：

```json
{
  "order_info": {"field": "spend", "order_type": "desc"},
  "page": 1, "page_size": 10,
  "start_date": "2026-09-18", "end_date": "2026-09-24",
  "advertiser_ids": ["..."], "campaign_ids": ["..."],
  "fields": [{"label": "账户名称", "value": "advertiser_name"}]
}
```

| 接口 | 维度 | 实测 |
|---|---|---|
| `/tiktok/advertiser_report` | 广告账户 | OK，5 条，1015ms |
| `/tiktok/campaign_report` | 推广系列 | OK，3 条，285ms |
| `/tiktok/adgroup_report` | 广告组 | OK，3 条，553ms |
| `/tiktok/ad_report` | 广告 | OK，3 条，2335ms |
| `/tiktok/panel_report` | 面板 | OK，2 条，220ms（承载 host = finance） |
| `/advertiser/adv_consume_report` | 消耗 | OK，5 条，310ms |
| `/advertiser/adv_fb_consume_report` | FB 消耗 | OK，3 条，128ms |
| `/kanban/google_adv_consume` | Google 消耗 | OK，0 条，111ms |
| `/kanban/google_adv_consume/export` | 同上导出 | ERROR `unknown request error` |
| 各自 `/export` 后缀 | 导出 xlsx（`responseType: blob`） | OK(bytes) |

导出接口超时设 12 分钟（前端 `timeout: 12*60*1e3`）。
客户端用 `c.download(...)`；用 `c.call()` 会抛「二进制响应(导出文件)」提示。

`helpers.report_body(...)` 的默认行为：日期不传取最近 N 天（默认 7），
`order_type` 只允许 `asc`/`desc`，`page`/`page_size` >= 1。
`helpers.iter_report(c, path, page_size=100, group="advertise", **kwargs)` 按页拉全量。

### 6.6 创建广告日志

```
POST /front_api/advertiser/tt_create_task_list
{"start_date": "2026-09-18", "end_date": "2026-09-24", "page": 1, "page_size": 10}
```

实测 OK，3 条。

### 6.7 钱包 / 资金（finance-bff）

```
POST https://finance-bff-v1.aiadfly.com/front_api/wallet/list
{"currency": "USD"}
```

**`currency` 必填**，枚举 `[USD JPY THB ...]`（实测传 `CNY` 报 `code=400 value must be in list`）。
`helpers.WALLET_CURRENCIES = ("USD","JPY","THB")` 在本地拦截。

返回：

```json
{"wallets":[{"currency":"JPY","balance":0,"balance_usd":0}, ...],
 "credit": ..., "currency_available": ..., "available_usd": ...}
```

| 接口 | 备注 |
|---|---|
| `/wallet/currency/exchange` | 写 |
| `/wallet/wallet/exchange` | 写 |
| `/wallet/sub_company/list` | 必填 `company_ex_id:string`（实调跑通）；覆盖测试里 ReadTimeout 30s |
| `/wallet/company/exchange` | 写 |
| `/wallet/calculate_reverse_exchange_amount` | ERROR `内部错误` |
| `/pay/trade_list` | SKIP(write 分类)，实调 `total_number=20`（含 `bill_id`，见 §6.9） |
| `/pay/transfer`、`/pay/transfer_detail` | 写 |
| `/pay/online_cogolinks`、`/pay/online_worldfrist` | 写 |
| `/coupon/list`、`/coupon/detail/list`、`/coupon/has_point` | OK，各 5/5/1 条 |
| `/activity_link/by_code` | NOAUTH `code is empty`（承载 host = front） |

`/pay/*` 与 `/coupon/*` 的分页用嵌套 `{"page_info": {"page": 1, "page_size": N}}`（`/pay/trade_list` 除外，
它被归到写类未实调，但 `BILL_API.md` 的实调用的是 `page_info`）。

**充值 / 清零 / 减款（承载 host = advertise_bff）**：

| 接口 | 行为 |
|---|---|
| `POST /pay/adv_recharge` | 广告账户充值（写） |
| `POST /pay/adv_amount_clear` | 广告账户清零。空 body 被拒（`DeductAdvFrontRequest.Details` 校验）—— **字段名是 `details`，不是 `list`** |
| `POST /pay/adv_reduce` | **静默忽略未知字段**：返回 `code=0` 但不生效 |
| `POST /pay/coupon_recharge` | 优惠券充值（写） |

### 6.8 AI Agent

Base 是 `https://ai-agent-v1.aiadfly.com`，**路径自带 `/ai_agent/` 段**，
且需要 `CompanyExID` 头（缺 header 报 `code=400 WITHOUT_COMPANY_HEADER`）：

```
GET  https://ai-agent-v1.aiadfly.com/ai_agent/v1/user/profile
→ {"has_adv":..., "has_product_type":..., "is_onboarding":..., "is_can_recharge":...}
```

实测 OK 的 GET 类接口：

| 接口 | 实测 |
|---|---|
| `/ai_agent/v1/user/profile` | OK，6 条 |
| `/ai_agent/v1/user/guide_task` | OK，5 条 |
| `/ai_agent/v1/support/info` | OK，1 条 |
| `/ai_agent/v1/message/get_prompt` | OK，2 条 |
| `/ai_agent/v1/session_id/get` | OK，2 条 |
| `/ai_agent/v1/chat/list` | OK，0 条 |
| `/ai_agent/market/session_id/get` | OK，2 条 |
| `/ai_agent/market/chat/list` | OK，0 条 |
| `/ai_agent/market/video/list` | OK，0 条 |

覆盖范围：

| 组 | 接口 |
|---|---|
| 对话 | `/v1/chat/{list,history,completion}`、`/ai_agent/market/chat/{list,history}` |
| 会话 | `/v1/session_id/{create,get}`、`/ai_agent/market/session_id/{create,get}` |
| 开户引导 | `/v1/ad/guide/adv_apply/reset`、`/v1/ad/guide/ad_create/reset`、`/v1/advertiser/{apply,pre_bind_bc,adv_bc_bind}` |
| GMVmax | `/v1/ad/gmv_max/{create,store/list,store/config,identity/list,store/product/list,store_id/validate,occupied_custom_shop_ads/list}` |
| VSA | `/v1/ad/vsa/{create,store/list,store/product/list,video/search,region/search,public_info/get,interest_category/list,identity/get}` |
| TT 资产 | `/v1/ad/tt/{account/list,asset/list}` |
| 其它 | `/v1/ocr`、`/v1/qrcode/{generate,query}`、`/v1/rebate/{list,confirm}`、`/v1/contract/sign`、`/v1/sign/draft/addr/acquire`、`/v1/file/cloud_url/get`、`/v1/message/{get,save,reset,feedback}`、`/v1/user/confirm_first_recharge`、`/v1/adv/list` |
| market | `/ai_agent/market/{creative/re_gene_desc,image/regene,image/reupload,message/save,stream/stop,video/batch,video/terminate}` |
| 支付流水 | `/pay/{bill_tips,airpay,llpay,pppay,pay_detail,wallet_adjust_detail,adv_recharge_list,adv_recharge_list/export,adv_amount_clear_list,adv_amount_clear_list/export}`（承载 host = front） |

`/ai_agent/v1/*` 的实测报错（PARAM 类，说明路由通、参数缺）：
`invalid XxxRequest.Field: ...`（protoc-gen-validate 风格）、
`code=500 qrcode_type is required`、`code=500 ticket cannot be empty`、
`code=500 is_sure must be 1`、`code=500 region[] is invalid`、
`code=500 record not found`（`occupied_custom_shop_ads/list`）。

### 6.9 账单模块

逆向来源：主 bundle finance 段的 15 个 API 定义 + 懒加载 chunk `index-rhJNxbMm.js`（46 KB，
`/bill-manage` 页面代码）+ 实机调用。

页面路由 `/bill-manage`（`PAGE_ROOT_ROUTER_MAP.billManage`）。页面代码只从主 bundle 引入 3 个账单 API：

| chunk 别名 | 主 bundle 函数名 | 接口 |
|---|---|---|
| `Z` | `getSettlementListAPI` | `POST /finance/settlement/list` |
| `V` | `getSettlementOverdueT7API` | `POST /finance/settlement/overdue-t7` |
| `U` | `payAdvAmountClearAPI` | `POST /pay/adv_amount_clear` |

> 别名映射通过读主 bundle 末尾的 `export { 内部名 as 别名 }` 表（294 条）反查。

#### 表格列（从 i18n 提取）

| i18n key | 列名 |
|---|---|
| `bill.manage.media_platform` | 媒体平台（TikTok / GG / FB / ASA） |
| `bill.manage.advertiser_name` | 广告账户名称 |
| `bill.manage.advertiser_id` | 广告账户ID |
| `bill.manage.advertiser_port` | 广告账户端口 |
| `bill.manage.port` | 端口 |
| `bill.manage.bill_period` | 账单周期 |
| `bill.manage.generate_time` | 生成时间 |
| `bill.manage.due_date` | 账单截止日期 |
| `bill.manage.bill_status` | 账单状态（见下枚举） |
| `bill.manage.completion_time` | 完结时间 |
| `bill.manage.currency` | 币种 |
| `bill.manage.bill_amount` | 账单金额 |
| `bill.manage.paid_amount` | 已支付金额 |
| `bill.manage.period_recharge` | 周期内充值 |
| `bill.manage.period_balance` | 周期内余额 |
| `bill.manage.promotion_cost` | 推广费用 |
| `bill.manage.promotion_service_fee` | 推广服务费 |
| `bill.manage.tax` | 税金 |
| `bill.manage.coupon_amount` | 优惠券使用金额 |
| `bill.manage.actions` | 操作（查看明细 / 查看INV / 下载明细表） |

筛选器：日期范围、账单状态、端口。

#### 接口清单

```
POST https://finance-v1.aiadfly.com/front_api/finance/settlement/list
```

实测：`page` / `page_size` / `start_date` / `end_date` 都被接受，但**当前公司返回 `count=0`** ——
没有任何账单（`billset/need` 返回 `need:false`，`bill_tips` 返回 `has_generated_bill:false`）。
**列表的响应字段没能实机取样**，上表列名来自页面代码而非真实数据。

```json
{"page": 1, "page_size": 20,
 "start_date": "2026-08-01", "end_date": "2026-09-30",
 "bill_status": 1, "port": "CN", "currency": "USD"}
```

响应信封：`{"code":0, "data":{"count":N, "list":[...], "total_data":...}}`。

| 接口 | 实测 |
|---|---|
| `POST /front_api/finance/settlement/detail/list` | `count=0`（无账单） |
| `POST /front_api/finance/settlement/detail/export` | 落盘成功但只有 **137 字节** —— 空表。body `{"company_ex_id": "10017794444062955153", "page": 1, "page_size": 50}`。137 字节是 xlsx 的最小合法结构，说明**导出接口本身通**，只是没有数据可导 |
| `POST /front_api/finance/billset/find` | OK，16 条，**账单模块唯一能取到真实数据的接口** |
| `GET  /front_api/finance/billset/need` | OK → `{"need": false}`；响应极慢（>10s） |
| `POST /front_api/finance/billset/update` | 写 |
| `POST /front_api/finance/account/payable/detail` | 必填 `company_ex_id:string` |
| `POST /front_api/finance/settlement/overdue-t7` | OK → `{"has_overdue_t7": false}` |
| `GET  https://ai-agent-v1.aiadfly.com/ai_agent/pay/bill_tips` | → `{"has_generated_bill": false, "has_overdue_bill": false}`（**在 ai_agent 服务上，不在 finance**） |

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

| 字段组 | 含义 |
|---|---|
| `contract_email` | 签约邮箱 |
| `recipient_email` / `cc_email` | 账单接收邮箱 / 抄送（多个用英文逗号分隔） |
| `cus_invoice_name` / `cus_invoice_address` | 发票抬头 / 地址 |
| `self_invoice_info_id` | 自定义开票信息 ID（空 = 未启用） |
| `{tt,gg,fb,asa}_bill_cycle_type` | 各平台的**账单周期类型**（0 = 默认） |
| `{tt,gg,fb,asa}_pay_term` | 各平台的**付款期限**（0 = 默认） |

四个平台前缀：`tt`=TikTok、`gg`=Google、`fb`=Facebook、`asa`=Apple Search Ads。

`finance/account/payable/detail` 实测返回（无账单时）：

```json
{"month_details": {}, "total_cost": {}, "total_late_fee": {},
 "overdue_bill_count": 0, "total_topay_amount_usd": 0, "total_late_fee_usd": 0}
```

`month_details` / `total_cost` / `total_late_fee` 是**按币种 keyed 的 map**（空对象说明无数据）。

#### 账单状态枚举

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

枚举里有 8 个值，但筛选下拉 `billSendStatusOptions` **只列了 1~5**。
另外 3 个（`deferred` / `regenerating` / `waitToSend`）只是列表里的展示态，不能用作查询条件。
bundle 只打包了 ms-MY / en-US / th-TH 三种 i18n，中文走服务端下发（`getI18nText` / 运行时拉取），
所以中文列名取自页面上实际看到的。

#### 关联：钱包流水里有 bill_id

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
这是在没有账单数据的情况下，唯一能确认「账单 → 资金」这条链路的结构证据。

`type` 枚举（从流水实证 + i18n）：`1`=钱包充值、`3`=广告账户充值、`5`=广告账户清零、`6`=返还类。

#### 返点（账单相关，当前全 500）

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
判断：公司没有配置返点规则，服务端在这种情况下抛 500 而不是返回空列表。

### 6.10 公司管理 / 子账号 / 权限

权限树原始数据落盘在 `adfly_api/spec/company_menu.json`。

#### 权限模型

权限是**树形 + 平铺 ID 列表**的双重表示：

```
menu_list (树)                    auth_menus (平铺字符串)
├─ page  (8 个)  页面级，path 是完整路由，如 /ad-manage
│   ├─ tab (11 个) 标签页级，path 是语义标识，如 tt-account
│   │   └─ btn (47 个) 按钮级，path 是动作标识，如 recharge_btn
```

共 **66 个节点**。角色的 `auth_menus` 是一个**逗号分隔的节点 ID 字符串**，例如管理员角色：

```
1,2,3,4,5,6,8,10,12,13,14,16,17,18,19,20,21,22,58,59,60,61,62,63,64,65,67,68,69,
70,71,74,76,110,118,143,145,155,191,194,195,196,197,198,199,200,201,202,203,204,
205,206,207,210,211,212,213,217,218,219,220,221,222,236,240,255
```

服务端同时返回 `auth_menu_list` 数组形式（同样的 ID，元素是字符串）。

节点字段：

```json
{"id": 194, "pid": 1, "name": "TT", "path": "tt-account",
 "url_path": "", "level": 0, "type": "tab", "status": 1}
```

| 字段 | 说明 |
|---|---|
| `id` / `pid` | 节点 ID / 父节点 ID（`pid=0` 为顶级） |
| `name` | 中文名（服务端下发） |
| `path` | page 类型是完整路由；tab/btn 类型是语义标识符 |
| `url_path` | 实测全部为空字符串 |
| `level` | 排序用；page 类型有值（5/7/10/15/20/28/30/46），tab/btn 为 0 |
| `type` | `page` / `tab` / `btn` |
| `status` | 1 = 启用 |

**page 级（8 个）** —— 顶级菜单，按 `level` 排序：

| id | level | 名称 | path |
|---|---|---|---|
| 58 | 5 | 数据看板 | `/data` |
| 221 | 7 | AI Agent | `/agent` |
| 1 | 10 | 账号管理 | `/account-mannage` |
| 59 | 15 | 广告管理 | `/ad-manage` |
| 2 | 20 | 钱包管理 | `/wallet` |
| 145 | 28 | 账单管理 | `/bill-manage` |
| 3 | 30 | 成员管理 | `/member-mannage` |
| 191 | 46 | 签约管理 | `/contract-manage` |

**tab 级（11 个）**：

| id | pid | 父页面 | 名称 | path |
|---|---|---|---|---|
| 194 | 1 | 账号管理 | TT | `tt-account` |
| 195 | 1 | 账号管理 | GG | `gg-account` |
| 197 | 1 | 账号管理 | FB | `fb-account` |
| 12 | 3 | 成员管理 | 成员管理 | `member_tab` |
| 13 | 3 | 成员管理 | 角色管理 | `role_tab` |
| 14 | 3 | 成员管理 | 客户管理 | `custom_tab` |
| 110 | 3 | 成员管理 | 客户账户管理 | `custom_account_tab` |
| 143 | 3 | 成员管理 | 账单及发票信息 | `email_setting` |
| 10 | 2 | 钱包管理 | 钱包交易及返点 | `transaction_detail` |
| 236 | 2 | 钱包管理 | 优惠券使用明细 | `coupon_usage_record` |
| 219 | 59 | 广告管理 | GMVMax推广系列 | `gmv_max_campaign` |

**btn 级（47 个）** —— 按父节点分组：

*挂 广告管理(59)，11 个：*
`4 资产授权`(`auth_btn`)·`60 批量创建VSA广告`(`create_vsa_batch`)·`61 单个创建VSA广告`(`create_vsa`)·
`62 开关控制`(`switch`)·`63 修改`(`modify`)·`64 扩量`(`extend`)·`65 AI托管`(`ai-trusteeship`)·
`155 添加标签`(`bind-label`)·`217 TT账户授权`(`tt_account_auth_btn`)·`218 批量创建GMVMax广告`(`create_gmv_max_batch`)·
`220 单个新建GMVMax广告`(`create_gmv_max`)

*挂 TT 账号 tab(194)，7 个：*
`5 广告开户`(`ad_account_btn`)·`6 充值`(`recharge_btn`)·`8 清零`(`clear_zero_btn`)·
`74 操作记录按钮`(`operation_record_btn`)·`76 绑定BC按钮`(`bind_bc_btn`)·`118 解绑BC`(`un_bind_bc_btn`)·
`255 修改账户信息`(`edit_adv_btn`)

*挂 GG tab(195)，6 个：*
`196 广告开户`·`199 充值`·`201 清零`·`203 操作记录按钮`·`205 绑定BC`·`207 解绑BC`

*挂 FB tab(197)，6 个：*
`198 广告开户`·`200 充值`·`202 清零`·`204 操作记录按钮`·`206 绑定BC`·`222 减款`(`deduct_btn`)

*挂 成员管理 tab(12)，3 个：* `16 创建成员`(`create`)·`17 编辑成员`(`edit`)·`18 分配资产`(`allocation`)

*挂 角色管理 tab(13)，2 个：* `19 创建角色`(`create`)·`20 编辑角色`(`edit`)

*挂 客户管理 tab(14)，2 个：* `21 创建客户`(`create`)·`22 编辑`(`edit`)

*挂 钱包管理(2)，1 个：* `240 优惠券管理`(`coupon_manage_btn`)

*挂 签约管理(191)，4 个：* `210 查看合同`(`review_btn`)·`211 下载合同`(`download_btn`)·
`212 签约`(`sign_btn`)·`213 解约`(`unsign_btn`)

*挂 pid=66（该父节点不在 menu_list 里），5 个：*
`67 创建策略`(`create-strategy`)·`68 编辑策略`(`edit-strategy`)·`69 状态按钮`(`status`)·
`70 删除按钮`(`remove`)·`71 应用按钮`(`apply`)

> 计数关系：66 = 8 page + 11 tab + 47 btn；其中 47 btn 里 42 个挂在树内的父节点上，
> **5 个挂在不存在的 `pid=66`**。66 应该是「自动化/策略」页面节点，但当前公司的权限树里没有它 ——
> 说明本公司的套餐/权限范围不含自动化模块，或该节点只对特定客户下发。

#### 数据权限 `data_permission_set`

除菜单权限外，角色还有一个**数据级权限**结构：

```json
"data_permission_set": {
  "customer_manage": {"type": 1, "field_infos": null},
  "kanban":          {"type": 1, "field_infos": null},
  "tt_business":     null,
  "gg_business":     null,
  "fb_business":     null
}
```

| 维度 | 说明 |
|---|---|
| `customer_manage` | 客户管理数据范围 |
| `kanban` | 数据看板范围 |
| `tt_business` / `gg_business` / `fb_business` | 各平台业务数据范围 |

每个维度：`type`（范围类型）+ `field_infos`（字段级过滤，可为 null）。配套字段还有：

```json
"custom_scope_type": 1,        // 客户范围类型
"company_id_list": [],         // 限定公司 ID
"platform_id_list": []         // 限定平台
```

`type` 的具体枚举值**未解出** —— 当前所有角色都是 `1`，bundle 里没有映射表。

#### 接口清单

**权限菜单树**：

```
POST /front_api/auth/get_company_menu
{"company_ex_id": ["10017794444062955153"]}     ← 必须是数组！
```

踩坑记录：传字符串会得到
`json: cannot unmarshal string into Go struct field GetCompanyMenuReq.company_ex_id of type []string`。

返回：

```json
[{"company_ex_id": "10017794444062955153", "menu_list": [ ...66 个节点... ]}]
```

是**数组**（按公司维度），不是单个对象。

**角色列表**：

```
POST https://ai-agent-v1.aiadfly.com/ai_agent/role_list
{"page": 1, "page_size": 50}
```

在 **ai_agent** 服务上，不在 front。`{}` 会返回 `count` 但 `list=null`，必须带分页参数。
实测返回 **22 个角色**。单条字段（12 个）：

```json
{
  "id": 6564,
  "created_at": "2026-05-22T18:19:13.634+08:00",
  "updated_at": "2026-06-12T11:03:56.386+08:00",
  "company_ex_id": "10017794444062955153",
  "name": "管理员",
  "auth_menus": "1,2,3,...255",
  "status": 1,
  "auth_menu_list": ["1", "2", ...],
  "custom_scope_type": 1,
  "company_id_list": [],
  "platform_id_list": [],
  "data_permission_set": { ... }
}
```

当前公司的角色分布：

| id | 名称 | 权限节点数 | 说明 |
|---|---|---|---|
| 6564 | 管理员 | 66 | 唯一有实际权限的角色 |
| 9410 ~ 9430 | *(空)* | 0 | **21 个空名空权限角色** |

那 21 个空角色是本会话探测造成的 + 此前手动操作遗留。

**角色创建 / 编辑**：

```
POST /ai_agent/role_edit
```

**这一个接口兼做创建和编辑**（按是否有 `id` 区分）。

**空 body 会创建一条空角色。** 实测 `{}` 返回 `code=0`，角色数从 21 涨到 22。
这个接口不做参数校验，缺什么就写空值。

创建角色（**从 `role_list` 返回字段对称推断，未实测验证**）：

```json
{"company_ex_id": "10017794444062955153",
 "name": "只读运营",
 "status": 1,
 "auth_menu_list": [58, 1, 194, 74],
 "custom_scope_type": 1,
 "company_id_list": [],
 "platform_id_list": []}
```

编辑角色（带 `id`）：

```json
{"id": 9430, "name": "只读运营", "status": 1, "auth_menu_list": [...]}
```

**成员列表**：

```
POST /front_api/user/list
{"page": 1, "page_size": 20}
```

实测 **`count=0`** —— 当前公司没有子账号。

试过的参数都不影响结果：`company_ex_id`（字符串/数组）、`platform`、`page_num`、
`page_info` 嵌套分页，全部 `count=0`。判断**确实是空数据**，不是参数问题。
所以**成员列表的响应字段没能取样**。

查询表单字段（页面截图 + 代码印证）：成员名称 / 手机号 / 邮箱 / 状态（下拉）/ 角色（下拉，
数据源是 `role_list` 的 `name`）。
表格列：**成员名称 / 手机号 / 邮箱 / 角色 / 最后登录时间 / 操作**。

**创建成员表单**（从截图提取）：

```
* 成员名称       文本
* 注册方式       单选：手机号 | 邮箱
* 手机号         文本（选"手机号"注册时）
* 角色           下拉，必填
* 状态           下拉，必填
```

对应 `POST /front_api/user/register`。字段名未实测（该接口返回自定义码 `code=11` 不暴露字段名）。

**当前登录账号的权限来源** —— `GET /user/info` 实测：

```json
{"user_id": "11017794444062945153", "name": "何阳鸿", "phone": "PHONE_REDACTED",
 "super": 2, "role_id": 0, "is_test_user": false, "menu_info": []}
```

**`super: 2` + `role_id: 0` + `menu_info: []`** —— 说明超管**不走角色权限体系**，权限是隐式全开的。
这也解释了为什么角色表里没有一个绑到当前账号上。企业里给子账号分配权限时，
走的是 `role_id` → `role.auth_menus` 这条链。

**成员创建 / 编辑**：

```
POST /front_api/user/register     → code=11 参数有误
POST /front_api/user/edit         → code=11 发送方法类型有误
```

两个接口空 body 都返回 `code=11`（自定义业务码，不是 proto 校验），**不暴露字段名**。
`/user/edit` 的报错是「**发送方法类型有误**」而不是「参数有误」——
说明它可能要求特定的请求方式（比如 `PUT`），或者 body 里需要一个 `type` 字段区分操作类型。

**客户管理**：

```
POST /front_api/company/custom_list   → count=0（无客户数据）
POST /front_api/company/edit          → code=11 公司名称已存在
POST /front_api/company/change_custom_passwd
```

`/company/edit` 的报错「公司名称已存在」说明空 body 时会用空字符串去匹配公司名，撞上了已有记录。
**这个接口会对公司主记录做修改。**

**角色权限批量修改**：

```
POST /front_api/auth/edit_company_menu          → code=999 获取公司信息失败
POST /front_api/auth/multi_edit_company_menu    → 404（所有 host 都不存在）
```

**成员自身信息**：

| 接口 | 说明 |
|---|---|
| `GET /front_api/user/info` | 含 `menu_info`（当前用户权限）+ `role_id`；OK，13 条 |
| `POST /front_api/user/upt_pass` | 改密码 |
| `POST /front_api/user/phone/update` | 换手机 |
| `POST /front_api/user/email/update` | 换邮箱 |
| `GET /front_api/user/send_code` | 发验证码 |
| `POST /front_api/user/get_business` | 查所属业务；OK，34 条 |
| `POST /front_api/user/check_fa` | 查是否需双因素；实测 `code=404 用户不存在` |

**公司信息**：

| 接口 | 说明 |
|---|---|
| `POST /front_api/company/get_ports_list` | 开户端口列表；OK，9 条 |
| `POST /front_api/company/country_list` | 国家列表；OK，5 条 |
| `POST /front_api/company/list` | **已下线**（GET 也 404）—— 公司列表改由登录后单独获取 |
| `POST /front_api/company/custom_list` | 客户列表；OK，0 条 |

**高危及死接口**：

| 接口 | 空 body 行为 |
|---|---|
| `/role_edit` | **创建一条空角色**（实测角色数 +1） |
| `/company/edit` | 用空公司名做匹配，报「公司名称已存在」 |
| `/pay/adv_reduce` | 返回 `code=0` 但不生效（静默忽略字段） |
| `/pay/adv_amount_clear` | 空 body 被拒（`DeductAdvFrontRequest.Details` 校验）—— 这个反而是安全的 |

**没有删除角色的接口。** 双向确认：

| 证据 | 结论 |
|---|---|
| `/role_*` 接口只有 `role_list` + `role_edit` 两个 | 服务端无 delete 端点 |
| 权限树里 `角色管理 tab(13)` 下只有 `19 创建角色` + `20 编辑角色` | 页面也没暴露删除入口 |

所以角色表里的空角色**通过 API 和页面都删不掉**，唯一处理路径是联系 AM。
（`role_edit` 是否支持 `status=0` 软删未验证。）

### 6.11 MCP Open

| 接口 | 说明 |
|---|---|
| `GET https://mcp-open.aiadfly.com/decrypt/wlh_login_info` | 需 `encrypted_...` 参数；实测 `code=400 decrypt payload failed` |
| `POST https://mcp-open.aiadfly.com/oauth/authorize_confirm` | `{"company_ex_id": "..."}` 必填；实测 `code=400 {"error":"company_ex_id is required"}` |

### 6.12 文件上传

```
GET  /front_api/file/sign       → COS 签名
POST /front_api/file/complete   → 上传完成回调
```

两个都被归到写类，未实调。

---

## 7. helpers 结构化辅助层

模块方法是 1:1 薄封装，payload 要自己拼。`adfly_api/helpers.py` 把高频工作流封起来，
带**本地参数校验**（不用等服务端 400）。

逐个数出来的公开 API：

| 类别 | 数量 | 说明 |
|---|---|---|
| 公开函数 | **24** | 不含 `_check` / `_fmt_dt` / `_fmt_date` 三个私有工具 |
| 公开异常类 | 1 | `AdflyUsageError` |
| 模块级枚举常量 / 映射表 | 12 | 定义在 §7.1 |

（任务书里写的「22 个 helper」与实际计数不符 —— 以本文的 24 个函数为准，逐个列在 §7.2~§7.5。）

```python
from adfly_api import AdflyClient
from adfly_api import helpers as H

c = AdflyClient()
print(H.wallet_balances(c, "USD"))          # {'wallets': [...], 'available_usd': 55}
```

### 7.1 枚举常量与异常

| 名字 | 值 / 含义 |
|---|---|
| `AdflyUsageError` | `ValueError` 子类 —— 调用方传错参数（不是服务端拒绝，请求未发出） |
| `SHOPPING_ADS_TYPE` | `"PRODUCT"` |
| `PRODUCT_SPECIFIC_TYPE` | `{"custom": "CUSTOMIZED_PRODUCTS", "all": "ALL"}` |
| `PRODUCT_VIDEO_SPECIFIC_TYPE` | `"AUTO_SELECTION"` |
| `OPTIMIZATION_GOAL` | `"VALUE"` |
| `DEEP_BID_TYPE` | `"VO_MIN_ROAS"` |
| `SCHEDULE_TYPES` | `{"now": "SCHEDULE_FROM_NOW", "fixed": "SCHEDULE_FIXED"}` |
| `OCCUPIED_ASSET_TYPE` | `{"spu": "SPU", "identity": "IDENTITY_BC_AUTH_TT"}` |
| `WALLET_CURRENCIES` | `("USD", "JPY", "THB")` |
| `REPORT_ORDERS` | `("asc", "desc")` |
| `CAMPAIGN_STATUS_ENABLE` / `CAMPAIGN_STATUS_DISABLE` | `"CAMPAIGN_STATUS_ENABLE"` / `"CAMPAIGN_STATUS_DISABLE"` |
| `BIND_STATUS` | `{0:"未知/初始", 1:"未知/中间态", 2:"有效(绑定生效)", 3:"未知/中间态", 4:"提交后未落定"}` |

### 7.2 GMVmax

| helper | 作用 | 本地校验 |
|---|---|---|
| `gmv_max_create_payload(*, advertiser_id, store_id, store_authorized_bc_id, campaign_name, roas_bid, budget, tt_auth_id, item_group_ids=None, identity_list=None, promote_all_products=False, schedule_start_time=None, schedule_end_time=None, schedule_type="now", product_video_specific_type="AUTO_SELECTION")` | 组装 `POST /tiktok/gmv_max/create` 请求体 | 必填非空；`roas_bid`/`budget` > 0；`schedule_type` ∈ `SCHEDULE_TYPES`；`fixed` 必须给开始时间；非全店推广必须给 `item_group_ids`。`promote_all_products=True` 时去掉 `item_group_ids` 且 `product_specific_type` → `ALL` |
| `gmv_max_edit(existing, *, budget=None, roas_bid=None, campaign_name=None, tt_auth_id)` | 基于 `gmv_max/list` 或 `detail` 的现有系列改字段，**merge 而不是只发增量** | `existing` 必须有 `campaign_id`；值 > 0。自动剥掉只读字段：`cost`/`net_cost`/`orders`/`cost_per_order`/`gross_revenue`/`roi`/`create_time`/`modify_time`/`store_name`/`advertiser_name`/`status`/`second_status`/`operation_status`/`row_data`/`task_data_id`/`item_group_ids_str`/`port`/`currency`/`company_ex_id`/`user_ex_id`；时间字段统一成 `YYYY-MM-DD HH:mm:ss` |
| `gmv_max_occupancy_batch(*, advertiser_id, store_id, item_group_ids=(), identity_ids=())` | 组装建广告前的资产占用校验 body | 空值过滤 |
| `gmv_max_identities(c, *, advertiser_id, store_id, store_authorized_bc_id, tt_auth_id)` | 取投放身份 | 四个参数缺一不可 |
| `find_gmv_max_ready_account(c, advertiser_ids=None)` | 找出**真正可用**的账户（该账户在 TikTok 侧对授权有操作权限 + 能取到店铺） | 返回元素含 `advertiser_id` / `advertiser_name` / `tt_auth_id` / `stores` / `store_id` / `store_authorized_bc_id` |

```python
ready = H.find_gmv_max_ready_account(c)
acct  = ready[0]
ids   = H.gmv_max_identities(c, advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
                             store_authorized_bc_id=acct["store_authorized_bc_id"],
                             tt_auth_id=acct["tt_auth_id"])
payload = H.gmv_max_create_payload(
    advertiser_id=acct["advertiser_id"], store_id=acct["store_id"],
    store_authorized_bc_id=acct["store_authorized_bc_id"],
    campaign_name="商品 GMV Max_TEST", roas_bid=3, budget=300,
    tt_auth_id=acct["tt_auth_id"], item_group_ids=["1735XXXXXXXXXX50"],
    identity_list=ids[:1])
c.ads.create_gmv_max_ad(payload)

existing = c.ads.get_gmv_max_list({"page": 1, "page_size": 1})["list"][0]
c.ads.edit_gmv_max_ad(H.gmv_max_edit(existing, budget=500, tt_auth_id=acct["tt_auth_id"]))
```

### 7.3 报表

| helper | 作用 |
|---|---|
| `report_body(*, days=7, start_date=None, end_date=None, page=1, page_size=50, order_by="spend", order_type="desc", advertiser_ids=None, campaign_ids=None, adgroup_ids=None, ad_ids=None, fields=None)` | 报表请求体；日期不传取最近 N 天 |
| `export_fields(labels)` | `[("账户名称","advertiser_name"), ...]` → `fields` 数组 |
| `iter_report(c, path="/tiktok/advertiser_report", page_size=100, group="advertise", **kwargs)` | 按页拉完整报表的生成器 |

```python
for row in H.iter_report(c, "/tiktok/advertiser_report", days=30, order_by="spend"):
    print(row["advertiser_name"], row["spend"])
```

### 7.4 分页与钱包

| helper | 作用 |
|---|---|
| `paging_nested(page=1, page_size=20)` | → `{"page_info": {"page": ..., "page_size": ...}}`；automation 与 finance_bff 的 `/pay/*`、`/coupon/*` 必须用它 |
| `paging_flat(page=1, page_size=20)` | → `{"page": ..., "page_size": ...}`；front / advertise / finance / ai_agent 用它 |
| `check_currency(currency)` | 本地校验币种枚举，传 `CNY` 立刻抛 `AdflyUsageError` |
| `wallet_balances(c, currency="USD")` | 返回 `{wallets, credit, currency_available, available_usd}` |

### 7.5 商务中心（BC）授权

| helper | 作用 |
|---|---|
| `auth_link(c, platform=1)` | 取授权链接，并把 `state` 拆成 `{auth_link, link_ex_id, app_id, state, redirect_uri, company_ex_id, user_ex_id, nonce}` |
| `check_auth_result(c, link_ex_id, company_ex_id=None, timeout=0.0, interval=3.0)` | 轮询 `/bc/query_auth`，返回 `{result, auth, polls}` |
| `tt_bc_list(c, tiktok_auth_id)` | 该授权下的 BC 列表 |
| `advertiser_bcs(c, advertiser_id, owner_bc_id, platform=1)` | 账户挂靠的 BC 列表（`bc_id` 传 `owner_bc_id`，`platform` 必填） |
| `raw_advertiser_bcs(c, advertiser_id, owner_bc_id, platform=1)` | 同上但返回 `(列表, 原始响应)`，用于区分「没有绑定」和「参数不对」 |
| `bind_records(c, advertiser_id=None, status=None, page_size=50)` | 查绑定任务记录，可按 `advertiser_id` / `status` 过滤 |
| `pending_bind_records(c, unsettled_only=True)` | 按 `updated_at - created_at < 5s` 找疑似未落定的记录，做「别重复提交」的护栏 |
| `bind_body(*, advertiser_id, bc_id, task_id="", platform=1)` | 组装 `adv_bc_bind` body（`advertiser_id` 自动包成数组） |
| `unbind_single_body(*, owner_bc_id, un_bind_bc_id, advertiser_id, platform=1)` | 组装 `bc_un_bind_single` body（两个 bc 字段不同义） |
| `bc_bind_body(*, bc_id, advertiser_ids)` | 旧版绑定 body，`{"bc_id":..., "advertiser_ids":[...]}` |
| `bc_unbind_body(*, bc_id, advertiser_id=None, advertiser_ids=None)` | 单个用 `advertiser_id`，批量用 `advertiser_ids` |
| `normalize_bc_ids(text)` | 复现前端 `normalizeBindBcIdsForApi`：中文全角逗号、多余空格 → 逗号分隔字符串 |

```python
L = H.auth_link(c)                      # ① 拿授权链接（platform 必填）
print(L["auth_link"], L["company_ex_id"], L["user_ex_id"], L["nonce"])

for bc in H.tt_bc_list(c, 1960):        # ② 这个授权下有哪些 BC
    d = bc["bc_detail"]
    print(d["bc_id"], d["name"], d["company"], d["currency"], d["registered_area"], bc["user_role"])

adv  = c.advertisers()[0]
mine = H.advertiser_bcs(c, adv["advertiser_id"], adv["owner_bc_id"])     # ③ 账户挂了哪些 BC

for r in H.bind_records(c, page_size=50):                                # ④ 提交前必查
    print(r["task_id"], r["advertiser_id"], r["bc_id"], H.BIND_STATUS.get(r["status"]), r["created_at"])

pending = [r for r in H.pending_bind_records(c) if r["advertiser_id"] == adv["advertiser_id"]]
if not pending:
    c.call("advertise", "POST", "/advertiser/adv_bc_bind",
           H.bind_body(advertiser_id=adv["advertiser_id"], bc_id="7626XXXXXXXXXX75"))

c.call("advertise", "POST", "/advertiser/bc_un_bind_single",              # ⑥ 解绑
       H.unbind_single_body(owner_bc_id=adv["owner_bc_id"],
                            un_bind_bc_id="7626XXXXXXXXXX75",
                            advertiser_id=adv["advertiser_id"]))

H.normalize_bc_ids("123，456，789")     # -> '123,456,789'
```

### 7.6 本地校验覆盖清单

`store_id` / `store_authorized_bc_id` / `campaign_name` 必填，`roas_bid`、`budget` > 0，
固定排期必须给开始时间，非全店推广必须给 `item_group_ids`，`currency` 枚举，
`order_type` 枚举，分页 >= 1 —— 全部在发请求前拦掉。

---

## 8. 易踩的参数坑（实测）

| 接口 | 坑 |
|---|---|
| `/advertiser/get_auth_link` | **必须带 `?platform=1`**，否则 `code=999 server_invalid_platform` |
| `/advertiser/get_bind_bc` | **`platform` 必填**，不带返回 `data=null`（不是报错，容易误判成「没有绑定」）；`bc_id` 要传账户自己的 `owner_bc_id`；传目标 BC 的 id → `code=999 No permission to view or operate.`。无 `advertiser_id` 时同样返回 `data=null` |
| `/advertiser/adv_bc_bind` | `advertiser_id` 必须是**数组**（传字符串触发 Go 反序列化错误 `json: cannot unmarshal string into Go struct field AdvBcBind...`）；字段名不是 `advertiser_ids` / `adv_ids` / `advertiser_id_list`（这些报「广告账号id列表为空」）；缺 `bc_id` 报 `bc_id(mcc_id)为空` |
| `/advertiser/adv_bc_bind`（语义） | **非幂等 + 真写**：同一 `adv+bc` 每调一次新增一条任务记录，且新记录最终落 `status=2`。没有「取消绑定任务」接口，唯一撤销路径是 `bc_un_bind_single` |
| `/advertiser/bc_un_bind_single` | `bc_id`（账户自己的 BC）与 `un_bind_bc_id`（要摘掉的那个）是两个不同的 BC；解绑后需要重新授权 |
| `/advertiser/adv_bc_bind_list` | `status=4` **不等于失败** —— 实测会自行转成 `2`（终态「绑定生效」）。判「处理中」要结合 `updated_at - created_at` |
| `/auth/get_company_menu` | `company_ex_id` 必须是**数组**，传字符串报 `json: cannot unmarshal string into Go struct field GetCompanyMenuReq.company_ex_id of type []string`；返回也是**数组**（按公司维度），不是单个对象 |
| `/tiktok/gmv_max/identity/get` | 必须**同时**给 `advertiser_id` + `store_id` + `store_authorized_bc_id` + `tt_auth_id`。缺任一：`code=999 advertiser_id or store_id or store_authorized_bc_id nil` |
| `/tiktok/gmv_max/store/list` | 对无 TikTok 权限的账户报 `code=999 获取店铺列表失败: No permission to operate advertiser: <id>`；缺 `advertiser_id` 报 `advertiser_id nil` |
| `/tiktok/gmv_max/store/shop_ad_usage_check` | 缺参报 `advertiser_id or store_id  nil`（注意两个空格） |
| `/tiktok/gmv_max/create` | 提交前必须调 `occupied_custom_shop_ads/list` 做资产占用校验；`schedule_start_time` 服务端要 `YYYY-MM-DD HH:mm:ss`（前端提交时格式化，`list` 返回的是 `+08:00` 的 ISO 串）；`SCHEDULE_FROM_NOW` **仍需显式给 `schedule_start_time`** |
| `/tt/bc/list`、`/tt/admin_store/list` | `tiktok_auth_id` 是 **number**（实测 1960），来自 `/tiktok/auth_list` 的 `id`；缺参报 `value must be greater than 0` / `value length must be at least 1 runes`。`tt_auth_id` 类型不统一：`identity/get` 要 Number，`store/list` 原样传 |
| `/wallet/list` | `currency` 必填，枚举 `[USD JPY THB ...]`；传 `CNY` 报 `code=400 value must be in list` |
| `/user/check_fa` | 只用于探测，返回值与登录接口不同（`code=404 用户不存在`） |
| `/finance/billset/need` | 存在但响应极慢（>10s），同组 `/billset/find` 正常 |
| `/finance/rebate/*` | 无返点配置时**全 500**（`unknown request error`），不是返回空列表 |
| `/finance/settlement/detail/export`、`/finance/rebate/export` | 无数据时 `code=500 record not found` |
| `/ai_agent/v1/*` | 需要 `CompanyExID` 头，缺了报 `code=400 WITHOUT_COMPANY_HEADER`；路径自带 `/ai_agent/` 段，但同段里混了 `/notice/*`、`/pay/*` 这类主网关路径（见 §5.2） |
| automation 分页 | 传平铺 `{"page":1,"page_size":5}` 得到 `code=500 unknown request error`，必须 `{"page_info":{...}}` |
| `/pay/adv_amount_clear` | 字段名是 **`details` 不是 `list`**，空 body 被 `DeductAdvFrontRequest.Details` 校验拒掉 |
| `/pay/adv_reduce` | **静默忽略未知字段**：返回 `code=0` 但不生效 |
| `/role_edit` | **空 body 会创建一条空角色**（实测角色数 +1），不做参数校验 |
| `/user/register`、`/user/edit` | 返回自定义码 `code=11`，不暴露字段名；`/user/edit` 报的是「发送方法类型有误」而非「参数有误」 |
| `/company/edit` | 空 body 用空公司名匹配，报 `code=11 公司名称已存在`，会动公司主记录 |
| 导出接口 | 返回 xlsx 二进制，用 `c.download(...)`；用 `c.call` 会抛「二进制响应(导出文件)」提示 |
| `/advertiser/get_panda_token` | 返回非 JSON（`content-type=?`），客户端抛「非 JSON 响应」 |
| `/ai_agent/market/stream/stop` | 返回 SSE（`content-type=text/event-stream`），客户端抛「SSE 流式响应」 |
| Google Ads 残留路径 | `/snapshots/*`、`/campaigns/*`、`/series/*` 等 33 条在任何 host 上都不存在，调用得 `AdflyRouteError` |

来源文档里没有的条目（对照说明）：

| 任务列举项 | 处理 |
|---|---|
| `adv_reduce` 静默忽略未知字段 | 已在源文档命中（`COMPANY_API.md` §4），保留 |
| `adv_amount_clear` 字段是 `details` 不是 `list` | 已在源文档命中（`DeductAdvFrontRequest.Details` 校验），保留 |
| `search_spu` 缺 `org_id` 报 `code=3` | **本次要读的源文档里没有这一条**（`search_spu` / `org_id` / `code=3` 在 `README/API/BILL/COMPANY/EXAMPLES/OPTIMIZATION/api_tables/coverage` 与 `spec/*.json` 中均无命中）。**未验证**，未写入本表 |

---

## 9. 覆盖测试结论

测试时间 `2026-09-25 03:56:41`，接口总数 **291**，实测 **199**，跳过写入类 **92**，
耗时 30.2s，并发 6。原始逐条结果在 `adfly_api/spec/coverage.json`，汇总在 `coverage_summary.json`。

### 9.1 状态分布

| 状态 | 数量 | 含义 |
|---|---|---|
| **OK** | **76** | 直接返回业务数据（= 66 条 OK + 10 条 `OK(bytes)` xlsx 导出） |
| PARAM | 47 | 路由通，本次调用缺必填参数（参数名从报错文案里已提取） |
| NOAUTH | 32 | 路由通，当前账号无该账户/店铺权限 |
| GONE | 33 | 服务端已移除（Google Ads 残留），清单见 `spec/unavailable.json` |
| ERROR | 10 | 服务端 5xx，需数据前置条件（如先有广告组才有 `/ad/list`） |
| AUTH | 1 | 需先开户（`/advertiser/apply_detail`） |
| SKIP(write) | 92 | 写接口，默认不实调 |

> 口径说明：`coverage.json` 的原始分类是 `OK 66 / PARAM 45 / NOAUTH 32 / GONE 33 / ERROR 12 /
> OK(bytes) 10 / AUTH 1 / SKIP(write) 92`（合计 291）。上面的 PARAM 47 / ERROR 10 是合并后的口径 ——
> 差额来自 `coverage.md` 里把 `/ai_agent/v1/rebate/list`（原始 500 `get company_ex_id error`）与
> `/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list`（原始 500 `record not found`）计入 PARAM，
> 并按「需数据前置条件」重新归类 ERROR。两套口径都保留在此。

### 9.2 按后端（`coverage.json` 原始分类）

| 后端段 | OK | OK(bytes) | PARAM | NOAUTH | GONE | ERROR | AUTH | SKIP(write) | 合计 |
|---|---|---|---|---|---|---|---|---|---|
| front | 9 | 0 | 1 | 0 | 2 | 0 | 0 | 19 | 31 |
| advertise | 22 | 7 | 9 | 24 | 1 | 2 | 1 | 8 | 74 |
| finance_bff | 3 | 0 | 0 | 1 | 0 | 3 | 0 | 9 | 16 |
| finance | 10 | 0 | 3 | 4 | 27 | 3 | 0 | 19 | 66 |
| automation | 8 | 2 | 3 | 0 | 3 | 3 | 0 | 15 | 34 |
| ai_agent | 14 | 1 | 28 | 2 | 0 | 1 | 0 | 22 | 68 |
| mcp_open | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 2 |
| **合计** | **66** | **10** | **45** | **32** | **33** | **12** | **1** | **92** | **291** |

`OK + OK(bytes) = 76` 即 §9.1 的 OK 计数；`GONE 33` 全部落在 finance(27) + automation(3) + front(2) + advertise(1)。

### 9.3 延迟

`coverage_summary.json`：`n=199, p50=63ms, p90=279ms, p99=3067ms, max=30031ms`。
`coverage.md` 报告里另记了一套 `n=199, p50=67ms, p90=236ms, p99=30013ms, max=30023ms`
（同一份 JSON 不同轮次的取值）。两套都列出，实际以 `coverage_summary.json` 为准。
p99 / max 由 `finance-bff-v1` 上两条 `ReadTimeout`（30 s）拉高。

### 9.4 33 个已移除的接口（GONE）

任何 host 上都不存在，属 Google Ads 功能残留：

```
/ad/get                /add_custom_anchor_video   /advertisers/list      /auth/list
/auth/multi_edit_company_menu  /campaign/get      /campaigns/list        /campaigns/export
/conversion_actions/list       /export            /geo_targets/suggest   /group_items
/image_assets/list             /languages/list    /list                  /material/daily
/material/export               /material/summary  /play_install_conversion_actions/list
/series/chart                  /series/summary    /session/list
/snapshots/account/{list,export}
/snapshots/ad_asset_snapshots/{list,export}
/snapshots/ad_group/{list,export}
/snapshots/campaign/{list,export}
/summary                       /video_assets/list /youtube_video/get
```

调用这些会得到 `AdflyRouteError`（`code=404, 404 page not found`），不是静默失败。

### 9.5 需数据前置条件的接口（路由正常，空数据时报 5xx）

| 接口 | 报错 |
|---|---|
| `/automation/ad/list`、`/adgroup/list` | `failed to find adgroup info` |
| `/automation/campaign/list` | `failed to find campaign info` |
| `/automation/material_group/detail` | `unknown request error` |
| `/finance/rebate/rule/list`、`rule_detail/list`、`adv_detail/list` | `unknown request error`（账号无返点规则） |
| `/finance/rebate/export`、`/finance/settlement/detail/export` | `record not found` |
| `/wallet/calculate_reverse_exchange_amount` | `内部错误` |
| `/advertise/kanban/google_adv_consume/export` | `unknown request error` |
| `/ai_agent/v1/ad/gmv_max/store/config` | `unknown request error` |
| `/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list` | `record not found` |
| `/ai_agent/v1/rebate/list` | `get company_ex_id error` |
| `/ai_agent/v1/file/cloud_url/get` | `region[] is invalid` |
| `/automation/tactic_change_log/list` | `find tactic_action_log data empty` |

`/wallet/list` 与 `/wallet/sub_company/list` 在覆盖测试里是 **ReadTimeout 30s**（`finance-bff-v1`），
单独实调能正常返回 —— 属于偶发网络/服务端慢，不是接口不可用。

### 9.6 92 个写接口清单（默认不实调）

| 后端段 | 接口 |
|---|---|
| front(19) | `/auth/edit_company_menu`、`/company/change_custom_passwd`、`/company/edit`、`/notice/mark_read`、`/sign/contract/download`、`/sign/flow/list`、`/sign/need`、`/sign/recission/addr/acquire`、`/sign/tosign/addr/acquire`、`/user/edit`、`/user/email/update`、`/user/forget_pass`、`/user/login`、`/user/login/qrcode/create`、`/user/login/qrcode/status`、`/user/phone/update`、`/user/register`、`/user/send_code`、`/user/upt_pass` |
| ai_agent(22) | `/ai_agent/market/creative/re_gene_desc`、`/ai_agent/market/image/regene`、`/ai_agent/market/image/reupload`、`/ai_agent/market/message/save`、`/ai_agent/market/session_id/create`、`/ai_agent/v1/ad/guide/ad_create/reset`、`/ai_agent/v1/ad/guide/adv_apply/reset`、`/ai_agent/v1/message/feedback`、`/ai_agent/v1/message/reset`、`/ai_agent/v1/message/save`、`/ai_agent/v1/session_id/create`、`/ai_agent/v1/sign/draft/addr/acquire`、`/pay/adv_amount_clear_list`、`/pay/adv_amount_clear_list/export`、`/pay/adv_recharge_list`、`/pay/adv_recharge_list/export`、`/pay/airpay`、`/pay/bill_tips`、`/pay/llpay`、`/pay/pay_detail`、`/pay/pppay`、`/pay/wallet_adjust_detail` |
| automation(15) | `/advertiser_label_relation/bind`、`/advertiser_label_relation/unbind`、`/label/add`、`/label/del`、`/label_category/add`、`/label_category/del`、`/material_group/add`、`/material_group/del`、`/material_group/edit`、`/tactic/add`、`/tactic/bind`、`/tactic/delete`、`/tactic/edit`、`/tactic/status/update`、`/tactic/unbind` |
| finance(19) | `/ad_group/status/update`、`/ad_group/update`、`/bc/create`、`/campaign/status/update`、`/campaign/update`、`/copy/suggest`、`/creative/remove`、`/finance/billset/update`、`/finance/rebate/company_detail/confirm`、`/finance/rebate/recharge`、`/pay/adv_amount_clear`、`/pay/adv_recharge`、`/pay/adv_reduce`、`/pay/coupon_recharge`、`/session/create`、`/session/delete`、`/session/update`、`/submit`、`/update` |
| finance_bff(9) | `/pay/online_cogolinks`、`/pay/online_worldfrist`、`/pay/trade_list`、`/pay/trade_list/export`、`/pay/transfer`、`/pay/transfer_detail`、`/wallet/company/exchange`、`/wallet/currency/exchange`、`/wallet/wallet/exchange` |
| advertise(8) | `/ad/gmv_max_store_config/delete`、`/ad/update`、`/advertiser/apply`、`/file/complete`、`/file/sign`、`/tiktok/gmv_max/copy`、`/tiktok/gmv_max/create`、`/tiktok/gmv_max/update` |

加总 19 + 22 + 15 + 19 + 9 + 8 = **92**。

**86 个写接口默认不实调**是 README / `OPTIMIZATION.md` 的口径，与 `coverage.json` 里的
`SKIP(write) = 92` 差 6 条；源文档没有给出这 6 条的口径推导，**未验证**，两处数字都按原样保留。
`coverage_probe.py --probe-writes` 可做写操作安全检查。

---

## 10. 已知未解项

| 项 | 状态 | 原因 / 补齐路径 |
|---|---|---|
| `settlement/list` 真实响应字段 | **未取样** | 公司无账单，`count=0` |
| `settlement/detail/list` 字段 | **未取样** | 同上 |
| `/user/list` 响应字段 | **未取样** | 公司无子账号，`count=0` |
| `/user/register`、`/user/edit` 字段 | **未解出** | 返回自定义码 `code=11`，不暴露字段名 |
| `/role_edit` 精确 body | **未解出** | 空 body 直接通过，拿不到校验提示；继续试会写垃圾数据 |
| `data_permission_set.*.type` 枚举 | **未解出** | 当前全为 `1`，bundle 无映射表 |
| `custom_scope_type` 枚举 | **未解出** | 同上 |
| `bill_cycle_type` / `pay_term` 枚举 | **未解出** | 当前全是 0，bundle 里没有映射表，需要页面下拉选项 |
| 返点接口的 body 结构 | **未解出** | 全部 500，服务端在无配置时不返回校验错误，拿不到字段提示 |
| `pid=66` 的父节点 | **未解出** | 不在当前公司权限树里（推测是自动化模块，未开通） |
| BC 解绑是否真生效 | **未验证** | 未执行真解绑（会改生产数据） |
| `role_edit` 是否支持 `status=0` 软删 | **未验证** | 它在空 body 时就写数据，不适合再试 |
| test 环境 | **未实测** | `config.json` 里有全套 dev base，但未跑过 |
| `search_spu` / `org_id` / `code=3` | **本次任务列举，但源文档无此条目** | 未验证 |

要补齐前几项最快的路径：在有账单数据的账号上跑 `settlement/list`；
或在页面上做一次「创建角色」和「创建成员」，F12 把两个请求的 Payload 抓下来。

---

## 11. 测试套件与运行方式

| 套件 | 命令 | 状态 |
|---|---|---|
| 离线单元测试 | `python3 test_transport.py` | **31/31** |
| 阶段 1（无需凭证） | `python3 verify_client.py --stage 1` | **4/4** |
| 阶段 2（真实登录） | `python3 verify_client.py --stage 2` | **31/31** |
| 端到端验收 | `python3 e2e_check.py` | **27/27** |
| helpers 验收 | `python3 e2e_helpers.py` | **25/25** |
| BC 授权验收 | `python3 e2e_bc.py` | **22/22** |
| 多 host 路由 | `python3 test_routing.py` | **18/22** 可达（余 4 项为测试数据缺失，非缺陷） |
| 覆盖测试 | `python3 coverage_probe.py 6` | 76 OK / 33 GONE（明细见 `coverage.md`） |
| 性能基线 | `python3 bench.py` | 探测 0.00x、并发 230 rps |

`verify_client.py` 的两种跑法：

```bash
python3 verify_client.py --stage 1
python3 verify_client.py --stage 2 --account PHONE_REDACTED --password '***'
python3 verify_client.py --stage 2 --token <JWT> --company <ex_id>
```

`test_transport.py` 的 31 个用例（按唯一方法名统计：`grep -o 'def test_[a-z_0-9]*' test_transport.py | sort -u | wc -l`
= 31）按类分组：

| 测试类 | 覆盖 |
|---|---|
| `TestCrypto` | `md5` 与前端一致、AES-CBC hex 已知向量 |
| `TestUrlVariants` | `_join` 不叠 `/ai_agent`、变体去重、404 指纹识别 |
| `TestOverrideMap` | `PATH_RULES` 命中、`normalize` 保留 `section` |
| `TestSession` | 往返读写、缺失/损坏文件、未知字段忽略 |
| `TestRouteCache` | 记录并重载、v1 字符串缓存升级 |
| `TestErrorMapping` | 认证码 → `AdflyAuthError`、业务错误携带 code/request_id、404 → `AdflyRouteError`、二进制提示、成功只返回 `data` |
| `TestFailClosedWrites` | 路由不可确证时写操作被阻断、读操作回退首候选、写不重试而 GET 重试 |
| `TestTimeoutReplaySafety` | ConnectTimeout 对 POST 也重放、ReadTimeout 不重放 POST、ReadTimeout 重放 GET |
| `TestCandidateOrdering` | `ai_agent` 路径候选排序、未知组名回落 |
| `TestBuiltinPriority` | 预计算表优先于运行时缓存、探测 500 不算命中 |
| `TestEndpointManifest` | 清单结构、method+path 无重复 |

验收脚本全部只做读取与 body 组装，不提交写操作（`e2e_bc.py` / `e2e_helpers.py` / `e2e_check.py`
文件头明确写了这一点）。

---

## 12. 全量接口清单（291 条）

来源：bundle 静态提取 + 归属实测纠正。`host` 列取自 `spec/routes_builtin.json`（真实承载 host），
`状态` / `耗时` / `实现记录` 取自 `coverage.json`（`SKIP(write)` 表示写入类未实调）。
清单里的 `backend` 段名与 `host` 不同见 §3.1。

### front（31）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/auth/edit_company_menu` | front | SKIP(write) | — | — |
| POST | `/auth/get_company_menu` | front | OK | 60ms | — |
| POST | `/auth/list` | front | GONE | 68ms | [code=404] 404 page not found |
| POST | `/auth/multi_edit_company_menu` | front | GONE | 56ms | [code=404] 404 page not found |
| POST | `/company/change_custom_passwd` | front | SKIP(write) | — | — |
| POST | `/company/country_list` | front | OK | 175ms | 5 条 |
| POST | `/company/custom_list` | front | OK | 116ms | 0 条 |
| POST | `/company/edit` | front | SKIP(write) | — | — |
| POST | `/company/get_ports_list` | front | OK | 170ms | 9 条 |
| POST | `/notice/archive_list` | front | OK | 70ms | 3 条 |
| GET | `/notice/bell_list` | front | OK | 71ms | 2 条 |
| POST | `/notice/mark_read` | front | SKIP(write) | — | — |
| POST | `/sign/contract/download` | front | SKIP(write) | — | — |
| POST | `/sign/flow/list` | front | SKIP(write) | — | — |
| POST | `/sign/need` | front | SKIP(write) | — | — |
| POST | `/sign/recission/addr/acquire` | front | SKIP(write) | — | — |
| POST | `/sign/tosign/addr/acquire` | front | SKIP(write) | — | — |
| POST | `/user/check_fa` | front | PARAM | 166ms | [code=404] 用户不存在 |
| POST | `/user/edit` | front | SKIP(write) | — | — |
| POST | `/user/email/update` | front | SKIP(write) | — | — |
| POST | `/user/forget_pass` | front | SKIP(write) | — | — |
| POST | `/user/get_business` | front | OK | 199ms | 34 条 |
| GET | `/user/info` | front | OK | 150ms | 13 条 |
| POST | `/user/list` | front | OK | 74ms | 3 条 |
| POST | `/user/login` | front | SKIP(write) | — | — |
| POST | `/user/login/qrcode/create` | front | SKIP(write) | — | — |
| POST | `/user/login/qrcode/status` | front | SKIP(write) | — | — |
| POST | `/user/phone/update` | front | SKIP(write) | — | — |
| POST | `/user/register` | front | SKIP(write) | — | — |
| GET | `/user/send_code` | front | SKIP(write) | — | — |
| POST | `/user/upt_pass` | front | SKIP(write) | — | — |

### advertise（74）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/ad/get` | front | GONE | 72ms | [code=404] 404 page not found |
| POST | `/ad/gmv_max_store_config/delete` | advertise_bff | SKIP(write) | — | — |
| POST | `/ad/gmv_max_store_config/get` | advertise_bff | PARAM | 59ms | [code=400] invalid GetGmvMaxStoreConfigRequest.GmvMaxStoreConfigId: va |
| POST | `/ad/gmv_max_store_config/list` | advertise_bff | OK | 61ms | — |
| POST | `/ad/gmv_max_store_config/list_by_store_id` | advertise_bff | OK | 57ms | — |
| POST | `/ad/list` | automation | ERROR | 70ms | [code=500] failed to find adgroup info |
| POST | `/ad/pixel/list` | advertise_bff | PARAM | 170ms | [code=400] invalid GetPixelListRequest.AdvertiserId: value length must |
| POST | `/ad/store_app_info/get` | advertise_bff | PARAM | 71ms | [code=400] invalid GetStoreAppInfoRequest.Query: value length must be  |
| POST | `/ad/update` | front | SKIP(write) | — | — |
| POST | `/advertiser/apply` | front | SKIP(write) | — | — |
| POST | `/advertiser/apply_detail` | front | AUTH | 66ms | [code=11] 开户记录不存在 |
| POST | `/advertiser/apply_list` | front | OK | 68ms | 4 条 |
| POST | `/advertiser/apply_list/export` | front | OK(bytes) | 85ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/advertiser/bc_un_bind_multi` | front | NOAUTH | 58ms | [code=999] 广告账号为空 |
| POST | `/advertiser/bc_un_bind_single` | front | NOAUTH | 54ms | [code=999] 广告账号id为空 |
| GET | `/advertiser/config` | front | OK | 157ms | 5 条 |
| POST | `/advertiser/get_apply_limit_num` | front | OK | 61ms | 1 条 |
| POST | `/advertiser/get_bind_bc` | front | NOAUTH | 55ms | [code=999] 广告账号id为空 |
| GET | `/advertiser/get_panda_token` | front | PARAM | 59ms | [code=200] 非 JSON 响应(content-type=?): |
| POST | `/advertiser/list` | front | OK | 1556ms | 0 条 |
| POST | `/advertiser/list/export` | front | OK(bytes) | 1524ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/advertiser/tt_create_task_list` | front | OK | 59ms | 3 条 |
| POST | `/bc/query_auth` | advertise_bff | PARAM | 156ms | [code=400] invalid QueryAuthRequest.AuthLinkExId: value length must be |
| POST | `/file/complete` | front | SKIP(write) | — | — |
| GET | `/file/sign` | front | SKIP(write) | — | — |
| POST | `/kanban/google_adv_consume` | advertise_bff | OK | 111ms | 0 条 |
| POST | `/kanban/google_adv_consume/export` | advertise_bff | ERROR | 156ms | [code=500] unknown request error |
| POST | `/tiktok/ad_detail` | front | NOAUTH | 60ms | [code=999] 广告账号为空 |
| POST | `/tiktok/ad_modify` | front | NOAUTH | 55ms | [code=999] 广告账号为空 |
| POST | `/tiktok/ad_report` | front | OK | 2335ms | 3 条 |
| POST | `/tiktok/ad_report/export` | front | OK(bytes) | 2255ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tiktok/adgroup_detail` | front | NOAUTH | 53ms | [code=999] 广告账号为空 |
| POST | `/tiktok/adgroup_extend` | front | NOAUTH | 55ms | [code=999] 广告账号为空 |
| POST | `/tiktok/adgroup_modify` | front | NOAUTH | 53ms | [code=999] 广告账号为空 |
| POST | `/tiktok/adgroup_report` | front | OK | 553ms | 3 条 |
| POST | `/tiktok/adgroup_report/export` | front | OK(bytes) | 532ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tiktok/adv_unionpay_check` | front | NOAUTH | 1349ms | [code=999] license_no: value is required but missing |
| POST | `/tiktok/advertiser_balance_get` | front | OK | 55ms | — |
| POST | `/tiktok/advertiser_report` | front | OK | 1015ms | — |
| POST | `/tiktok/advertiser_report/export` | front | OK(bytes) | 1020ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tiktok/advertiser_update` | front | NOAUTH | 60ms | [code=999] batch is empty |
| POST | `/tiktok/auth_list` | front | OK | 62ms | 3 条 |
| POST | `/tiktok/campaign_detail` | front | NOAUTH | 60ms | [code=999] 广告账号为空 |
| POST | `/tiktok/campaign_modify` | front | NOAUTH | 52ms | [code=999] 广告账号为空 |
| POST | `/tiktok/campaign_report` | front | OK | 285ms | 3 条 |
| POST | `/tiktok/campaign_report/export` | front | OK(bytes) | 273ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tiktok/copy_advertisement` | front | NOAUTH | 54ms | [code=999] 广告账号为空 |
| POST | `/tiktok/create_advertisement` | front | NOAUTH | 67ms | [code=999] 商品或素材参数有误 |
| POST | `/tiktok/create_advertisement_new` | front | NOAUTH | 53ms | [code=999] 广告账号为空 |
| POST | `/tiktok/get_ad_detail_list` | front | NOAUTH | 57ms | [code=999] 广告账号为空 |
| POST | `/tiktok/get_config` | front | NOAUTH | 68ms | [code=999] advertiser_id nil |
| POST | `/tiktok/get_opt_campaign` | front | OK | 58ms | 0 条 |
| POST | `/tiktok/get_video_url` | front | NOAUTH | 56ms | [code=999] 帖子id为空 |
| POST | `/tiktok/get_videos` | front | NOAUTH | 55ms | [code=999] 广告账号为空 |
| POST | `/tiktok/gmv_max/copy` | front | SKIP(write) | — | — |
| POST | `/tiktok/gmv_max/create` | front | SKIP(write) | — | — |
| POST | `/tiktok/gmv_max/detail` | front | OK | 59ms | 32 条 |
| POST | `/tiktok/gmv_max/export` | front | OK(bytes) | 59ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tiktok/gmv_max/get_detail_info` | front | NOAUTH | 69ms | [code=999] record not found |
| POST | `/tiktok/gmv_max/get_refresh_time` | front | OK | 60ms | 2 条 |
| POST | `/tiktok/gmv_max/group_item_report` | front | NOAUTH | 63ms | [code=999] record not found |
| POST | `/tiktok/gmv_max/identity/get` | front | NOAUTH | 56ms | [code=999] advertiser_id or store_id or store_authorized_bc_id nil |
| POST | `/tiktok/gmv_max/list` | front | OK | 66ms | 5 条 |
| POST | `/tiktok/gmv_max/occupied_custom_shop_ads/list` | front | OK | 57ms | — |
| POST | `/tiktok/gmv_max/post_item_report` | front | OK | 53ms | 0 条 |
| POST | `/tiktok/gmv_max/refresh` | front | OK | 183ms | — |
| POST | `/tiktok/gmv_max/store/list` | front | NOAUTH | 56ms | [code=999] advertiser_id nil |
| POST | `/tiktok/gmv_max/store/shop_ad_usage_check` | front | NOAUTH | 57ms | [code=999] advertiser_id or store_id  nil |
| POST | `/tiktok/gmv_max/update` | front | SKIP(write) | — | — |
| POST | `/tiktok/identity_get` | front | PARAM | 57ms | [code=400] {"code":999,"message":"Key: 'IdentityListReq.AccessToken' E |
| POST | `/tt/admin_store/list` | advertise_bff | PARAM | 60ms | [code=400] invalid ListTikTokAdminStoreRequest.TiktokAuthId: value mus |
| POST | `/tt/auth/list` | advertise_bff | OK | 74ms | 3 条 |
| POST | `/tt/bc/is_adv_bound` | advertise_bff | PARAM | 54ms | [code=400] invalid IsBcAdvIdBoundRequest.BcId: value length must be at |
| POST | `/tt/bc/list` | advertise_bff | PARAM | 60ms | [code=400] invalid ListTikTokBcRequest.TiktokAuthId: value must be gre |

### finance_bff（16）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/activity_link/by_code` | front | NOAUTH | 56ms | [code=999] code is empty |
| POST | `/coupon/detail/list` | finance_bff | OK | 271ms | 5 条 |
| POST | `/coupon/has_point` | finance_bff | OK | 176ms | 1 条 |
| POST | `/coupon/list` | finance_bff | OK | 356ms | 5 条 |
| POST | `/pay/online_cogolinks` | finance_bff | SKIP(write) | — | — |
| POST | `/pay/online_worldfrist` | finance_bff | SKIP(write) | — | — |
| POST | `/pay/trade_list` | finance_bff | SKIP(write) | — | — |
| POST | `/pay/trade_list/export` | finance_bff | SKIP(write) | — | — |
| POST | `/pay/transfer` | finance_bff | SKIP(write) | — | — |
| POST | `/pay/transfer_detail` | finance_bff | SKIP(write) | — | — |
| POST | `/wallet/calculate_reverse_exchange_amount` | finance_bff | ERROR | 158ms | [code=500] 内部错误 |
| POST | `/wallet/company/exchange` | finance_bff | SKIP(write) | — | — |
| POST | `/wallet/currency/exchange` | finance_bff | SKIP(write) | — | — |
| POST | `/wallet/list` | finance_bff | ERROR | 30023ms | HTTPSConnectionPool(host='finance-bff-v1.aiadfly.com', port=443): Read |
| POST | `/wallet/sub_company/list` | finance_bff | ERROR | 30013ms | HTTPSConnectionPool(host='finance-bff-v1.aiadfly.com', port=443): Read |
| POST | `/wallet/wallet/exchange` | finance_bff | SKIP(write) | — | — |

### finance（66）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/ad_group/status/update` | front | SKIP(write) | — | — |
| POST | `/ad_group/update` | front | SKIP(write) | — | — |
| POST | `/add_custom_anchor_video` | front | GONE | 66ms | [code=404] 404 page not found |
| POST | `/advertiser/adv_consume_report` | front | OK | 310ms | 5 条 |
| POST | `/advertiser/adv_fb_consume_report` | front | OK | 128ms | 3 条 |
| POST | `/advertiser/bind_adv` | front | NOAUTH | 73ms | [code=999] platform invalid |
| POST | `/advertiser/bind_adv_list` | front | OK | 73ms | — |
| POST | `/advertiser/bind_adv_option_list` | front | NOAUTH | 58ms | [code=999] platform invalid |
| POST | `/advertiser/unbind_adv` | front | NOAUTH | 55ms | [code=999] platform invalid |
| POST | `/advertisers/list` | front | GONE | 57ms | [code=404] 404 page not found |
| POST | `/bc/create` | advertise_bff | SKIP(write) | — | — |
| POST | `/campaign/get` | front | GONE | 72ms | [code=404] 404 page not found |
| POST | `/campaign/status/update` | front | SKIP(write) | — | — |
| POST | `/campaign/update` | front | SKIP(write) | — | — |
| POST | `/campaigns/export` | front | GONE | 70ms | [code=404] 404 page not found |
| POST | `/campaigns/list` | front | GONE | 67ms | [code=404] 404 page not found |
| POST | `/conversion_actions/list` | front | GONE | 65ms | [code=404] 404 page not found |
| POST | `/copy/suggest` | front | SKIP(write) | — | — |
| POST | `/creative/remove` | front | SKIP(write) | — | — |
| POST | `/export` | front | GONE | 62ms | [code=404] 404 page not found |
| POST | `/finance/account/payable/detail` | finance | PARAM | 169ms | [code=400] invalid GetAccountPayableDetailRequest.CompanyExId: value l |
| POST | `/finance/billset/find` | front | OK | 68ms | 16 条 |
| GET | `/finance/billset/need` | front | OK | 59ms | 1 条 |
| POST | `/finance/billset/update` | front | SKIP(write) | — | — |
| POST | `/finance/company_detail/list` | finance | OK | 182ms | 0 条 |
| POST | `/finance/rebate/adv_detail/list` | finance | ERROR | 97ms | [code=500] unknown request error |
| POST | `/finance/rebate/company_detail/confirm` | finance | SKIP(write) | — | — |
| POST | `/finance/rebate/export` | finance | PARAM | 98ms | [code=500] record not found |
| POST | `/finance/rebate/recharge` | finance | SKIP(write) | — | — |
| POST | `/finance/rebate/rule/list` | finance | ERROR | 55ms | [code=500] unknown request error |
| POST | `/finance/rebate/rule_detail/list` | finance | ERROR | 58ms | [code=500] unknown request error |
| POST | `/finance/settlement/detail/export` | finance | PARAM | 227ms | [code=500] record not found |
| POST | `/finance/settlement/detail/list` | front | OK | 63ms | 0 条 |
| POST | `/finance/settlement/list` | front | OK | 65ms | 3 条 |
| POST | `/finance/settlement/overdue-t7` | finance | OK | 67ms | 1 条 |
| POST | `/geo_targets/suggest` | front | GONE | 65ms | [code=404] 404 page not found |
| POST | `/group_items` | front | GONE | 64ms | [code=404] 404 page not found |
| POST | `/image_assets/list` | front | GONE | 63ms | [code=404] 404 page not found |
| POST | `/languages/list` | front | GONE | 56ms | [code=404] 404 page not found |
| POST | `/list` | front | GONE | 70ms | [code=404] 404 page not found |
| POST | `/pay/adv_amount_clear` | advertise_bff | SKIP(write) | — | — |
| POST | `/pay/adv_recharge` | advertise_bff | SKIP(write) | — | — |
| POST | `/pay/adv_reduce` | advertise_bff | SKIP(write) | — | — |
| POST | `/pay/coupon_recharge` | advertise_bff | SKIP(write) | — | — |
| POST | `/play_install_conversion_actions/list` | front | GONE | 67ms | [code=404] 404 page not found |
| POST | `/series/chart` | front | GONE | 72ms | [code=404] 404 page not found |
| POST | `/series/summary` | front | GONE | 69ms | [code=404] 404 page not found |
| POST | `/session/create` | front | SKIP(write) | — | — |
| POST | `/session/delete` | front | SKIP(write) | — | — |
| POST | `/session/list` | front | GONE | 67ms | [code=404] 404 page not found |
| POST | `/session/update` | front | SKIP(write) | — | — |
| POST | `/snapshots/account/export` | front | GONE | 68ms | [code=404] 404 page not found |
| POST | `/snapshots/account/list` | front | GONE | 65ms | [code=404] 404 page not found |
| POST | `/snapshots/ad_asset_snapshots/export` | front | GONE | 78ms | [code=404] 404 page not found |
| POST | `/snapshots/ad_asset_snapshots/list` | front | GONE | 70ms | [code=404] 404 page not found |
| POST | `/snapshots/ad_group/export` | front | GONE | 79ms | [code=404] 404 page not found |
| POST | `/snapshots/ad_group/list` | front | GONE | 67ms | [code=404] 404 page not found |
| POST | `/snapshots/campaign/export` | front | GONE | 88ms | [code=404] 404 page not found |
| POST | `/snapshots/campaign/list` | front | GONE | 68ms | [code=404] 404 page not found |
| POST | `/submit` | front | SKIP(write) | — | — |
| POST | `/summary` | front | GONE | 67ms | [code=404] 404 page not found |
| POST | `/tiktok/campaign_modify` | front | NOAUTH | 66ms | [code=999] 广告账号为空 |
| POST | `/tiktok/panel_report` | front | OK | 220ms | 2 条 |
| POST | `/update` | front | SKIP(write) | — | — |
| POST | `/video_assets/list` | front | GONE | 77ms | [code=404] 404 page not found |
| POST | `/youtube_video/get` | front | GONE | 66ms | [code=404] 404 page not found |

### automation（34）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/adgroup/list` | automation | ERROR | 81ms | [code=500] failed to find adgroup info |
| POST | `/advertiser/list` | front | OK | 1263ms | 0 条 |
| POST | `/advertiser_label_relation/bind` | automation | SKIP(write) | — | — |
| POST | `/advertiser_label_relation/find` | automation | OK | 83ms | 5 条 |
| POST | `/advertiser_label_relation/unbind` | automation | SKIP(write) | — | — |
| POST | `/campaign/list` | automation | ERROR | 64ms | [code=500] failed to find campaign info |
| POST | `/label/add` | automation | SKIP(write) | — | — |
| POST | `/label/del` | automation | SKIP(write) | — | — |
| POST | `/label/list` | automation | OK | 76ms | 1 条 |
| POST | `/label_category/add` | automation | SKIP(write) | — | — |
| POST | `/label_category/del` | automation | SKIP(write) | — | — |
| POST | `/label_category/list` | automation | OK | 67ms | 1 条 |
| POST | `/material/daily` | automation | GONE | 69ms | [code=404] 404 page not found |
| POST | `/material/export` | automation | GONE | 77ms | [code=404] 404 page not found |
| POST | `/material/list` | automation | OK | 67ms | 0 条 |
| POST | `/material/summary` | automation | GONE | 73ms | [code=404] 404 page not found |
| POST | `/material_group/add` | automation | SKIP(write) | — | — |
| POST | `/material_group/del` | automation | SKIP(write) | — | — |
| POST | `/material_group/detail` | automation | ERROR | 63ms | [code=500] unknown request error |
| POST | `/material_group/edit` | automation | SKIP(write) | — | — |
| POST | `/material_group/list` | automation | OK | 73ms | 1 条 |
| POST | `/tactic/add` | automation | SKIP(write) | — | — |
| POST | `/tactic/adv/list` | automation | PARAM | 148ms | [code=400] invalid ListTacticAdvRequest.TacticExId: value length must  |
| POST | `/tactic/bind` | automation | SKIP(write) | — | — |
| POST | `/tactic/delete` | automation | SKIP(write) | — | — |
| POST | `/tactic/edit` | automation | SKIP(write) | — | — |
| POST | `/tactic/find` | automation | PARAM | 171ms | [code=400] invalid FindTacticRequest.TacticExId: value length must be  |
| POST | `/tactic/list` | automation | OK | 178ms | 0 条 |
| POST | `/tactic/status/update` | automation | SKIP(write) | — | — |
| POST | `/tactic/unbind` | automation | SKIP(write) | — | — |
| POST | `/tactic_action_log/export` | automation | OK(bytes) | 299ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tactic_action_log/list` | automation | OK | 236ms | 0 条 |
| POST | `/tactic_change_log/export` | automation | OK(bytes) | 75ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/tactic_change_log/list` | automation | PARAM | 70ms | [code=500] find tactic_action_log data empty |

### ai_agent（68）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| POST | `/advertiser/adv_bc_bind` | front | NOAUTH | 90ms | [code=999] 广告账号id列表为空 |
| POST | `/advertiser/adv_bc_bind_list` | front | OK | 76ms | 5 条 |
| POST | `/advertiser/adv_bc_bind_list/export` | front | OK(bytes) | 78ms | [code=200] 二进制响应(导出文件),请用 download() 或 response_type='blob' |
| POST | `/advertiser/bc_un_bind_list` | front | OK | 85ms | 3 条 |
| POST | `/ai_agent/market/chat/history` | ai_agent_root | PARAM | 151ms | [code=400] invalid ChatHistoryRequest.SessionId: value length must be  |
| GET | `/ai_agent/market/chat/list` | ai_agent_root | OK | 59ms | 0 条 |
| POST | `/ai_agent/market/creative/re_gene_desc` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/market/image/regene` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/market/image/reupload` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/market/message/save` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/market/session_id/create` | ai_agent_root | SKIP(write) | — | — |
| GET | `/ai_agent/market/session_id/get` | ai_agent_root | OK | 59ms | 2 条 |
| POST | `/ai_agent/market/stream/stop` | ai_agent_root | PARAM | 3056ms | [code=200] SSE 流式响应(content-type=text/event-stream) |
| GET | `/ai_agent/market/video/batch` | ai_agent_root | PARAM | 49ms | [code=400] invalid GetVideoBatchRequest.BatchId: value length must be  |
| GET | `/ai_agent/market/video/list` | ai_agent_root | OK | 59ms | 0 条 |
| POST | `/ai_agent/market/video/terminate` | ai_agent_root | PARAM | 58ms | [code=400] invalid TerminateVideoRequest.VideoId: value length must be |
| POST | `/ai_agent/v1/ad/campaign/list` | ai_agent_root | PARAM | 62ms | [code=400] invalid ListCampaignRequest.MessageId: value length must be |
| POST | `/ai_agent/v1/ad/gmv_max/identity/list` | ai_agent_root | PARAM | 74ms | [code=400] invalid ListGmvMaxIdentityRequest.AdvertiserId: value lengt |
| POST | `/ai_agent/v1/ad/gmv_max/occupied_custom_shop_ads/list` | ai_agent_root | PARAM | 175ms | [code=500] record not found |
| POST | `/ai_agent/v1/ad/gmv_max/store/config` | ai_agent_root | ERROR | 56ms | [code=500] unknown request error |
| POST | `/ai_agent/v1/ad/gmv_max/store/list` | ai_agent_root | PARAM | 61ms | [code=400] invalid ListGmvMaxStoreRequest.AdvertiserId: value length m |
| POST | `/ai_agent/v1/ad/gmv_max/store/product/list` | ai_agent_root | PARAM | 64ms | [code=400] invalid ListGmvMaxStoreProductRequest.AdvertiserId: value l |
| POST | `/ai_agent/v1/ad/gmv_max/store_id/validate` | ai_agent_root | PARAM | 77ms | [code=400] invalid ValidateGmvMaxStoreIdRequest.AdvertiserId: value le |
| POST | `/ai_agent/v1/ad/guide/ad_create/reset` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/v1/ad/guide/adv_apply/reset` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/v1/ad/tt/account/list` | ai_agent_root | PARAM | 60ms | [code=400] invalid ListTikTokAccountRequest.BcId: value length must be |
| POST | `/ai_agent/v1/ad/tt/asset/list` | ai_agent_root | PARAM | 74ms | [code=400] invalid ListTikTokAssetRequest.BcId: value length must be a |
| POST | `/ai_agent/v1/ad/vsa/identity/get` | ai_agent_root | PARAM | 55ms | [code=400] invalid GetIdentityRequest.AdvertiserId: value length must  |
| POST | `/ai_agent/v1/ad/vsa/interest_category/list` | ai_agent_root | PARAM | 51ms | [code=400] invalid ListInterestCategoryRequest.AdvertiserId: value len |
| POST | `/ai_agent/v1/ad/vsa/public_info/get` | ai_agent_root | PARAM | 56ms | [code=400] invalid GetAdCreatePublicInfoRequest.AdvertiserId: value le |
| POST | `/ai_agent/v1/ad/vsa/region/search` | ai_agent_root | PARAM | 56ms | [code=400] invalid SearchRegionRequest.AdvertiserId: value length must |
| POST | `/ai_agent/v1/ad/vsa/store/list` | ai_agent_root | PARAM | 56ms | [code=400] invalid ListStoreRequest.AdvertiserId: value length must be |
| POST | `/ai_agent/v1/ad/vsa/store/product/list` | ai_agent_root | PARAM | 56ms | [code=400] invalid ListStoreProductRequest.AdvertiserId: value length  |
| POST | `/ai_agent/v1/ad/vsa/video/search` | ai_agent_root | PARAM | 56ms | [code=400] invalid SearchVideoRequest.AdvertiserId: value length must  |
| POST | `/ai_agent/v1/adv/list` | ai_agent_root | OK | 182ms | 0 条 |
| POST | `/ai_agent/v1/chat/history` | ai_agent_root | PARAM | 168ms | [code=400] invalid ChatHistoryRequest.SessionId: value length must be  |
| GET | `/ai_agent/v1/chat/list` | ai_agent_root | OK | 75ms | 0 条 |
| POST | `/ai_agent/v1/file/cloud_url/get` | ai_agent_root | PARAM | 62ms | [code=500] region[] is invalid |
| POST | `/ai_agent/v1/guide/adv_recharge` | ai_agent_root | PARAM | 64ms | [code=400] invalid GuideAdvRechargeRequest.Amount: value must be great |
| POST | `/ai_agent/v1/message/feedback` | ai_agent_root | SKIP(write) | — | — |
| GET | `/ai_agent/v1/message/get` | ai_agent_root | PARAM | 51ms | [code=400] invalid MessageGetRequest.MessageId: value length must be a |
| GET | `/ai_agent/v1/message/get_prompt` | ai_agent_root | OK | 72ms | 2 条 |
| POST | `/ai_agent/v1/message/reset` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/v1/message/save` | ai_agent_root | SKIP(write) | — | — |
| POST | `/ai_agent/v1/ocr` | ai_agent_root | PARAM | 66ms | [code=400] invalid OCRRequest.Url: value length must be at least 1 run |
| POST | `/ai_agent/v1/qrcode/generate` | ai_agent_root | PARAM | 74ms | [code=500] qrcode_type is required |
| POST | `/ai_agent/v1/qrcode/query` | ai_agent_root | PARAM | 64ms | [code=500] ticket cannot be empty |
| POST | `/ai_agent/v1/rebate/list` | ai_agent_root | NOAUTH | 61ms | [code=500] get company_ex_id error |
| POST | `/ai_agent/v1/session_id/create` | ai_agent_root | SKIP(write) | — | — |
| GET | `/ai_agent/v1/session_id/get` | ai_agent_root | OK | 156ms | 2 条 |
| POST | `/ai_agent/v1/sign/draft/addr/acquire` | ai_agent_root | SKIP(write) | — | — |
| GET | `/ai_agent/v1/support/info` | ai_agent_root | OK | 63ms | 1 条 |
| POST | `/ai_agent/v1/user/confirm_first_recharge` | ai_agent_root | PARAM | 59ms | [code=500] is_sure must be 1 |
| GET | `/ai_agent/v1/user/guide_task` | ai_agent_root | OK | 63ms | 5 条 |
| GET | `/ai_agent/v1/user/profile` | ai_agent_root | OK | 57ms | 6 条 |
| POST | `/pay/adv_amount_clear_list` | front | SKIP(write) | — | — |
| POST | `/pay/adv_amount_clear_list/export` | front | SKIP(write) | — | — |
| POST | `/pay/adv_recharge_list` | front | SKIP(write) | — | — |
| POST | `/pay/adv_recharge_list/export` | front | SKIP(write) | — | — |
| POST | `/pay/airpay` | front | SKIP(write) | — | — |
| GET | `/pay/bill_tips` | front | SKIP(write) | — | — |
| POST | `/pay/llpay` | front | SKIP(write) | — | — |
| POST | `/pay/pay_detail` | front | SKIP(write) | — | — |
| POST | `/pay/pppay` | front | SKIP(write) | — | — |
| POST | `/pay/wallet_adjust_detail` | front | SKIP(write) | — | — |
| POST | `/public/data/report` | ai_agent_root | PARAM | 58ms | [code=400] invalid DataReportRequest.PageId: value length must be at l |
| POST | `/role_edit` | front | OK | 80ms | — |
| POST | `/role_list` | front | OK | 88ms | 5 条 |

### mcp_open（2）

| 方法 | 路径 | host | 状态 | 耗时 | 实现记录 |
|---|---|---|---|---|---|
| GET | `/decrypt/wlh_login_info` | mcp_open | PARAM | 162ms | [code=400] decrypt payload failed |
| POST | `/oauth/authorize_confirm` | mcp_open | NOAUTH | 166ms | [code=400] {"error":"company_ex_id is required"} |


---

## 13. 目录与工具

| 文件 | 用途 |
|---|---|
| `adfly_api/transport.py` | 传输层：登录、多 host 路由、错误映射、重试退避、翻页、下载（707 行） |
| `adfly_api/helpers.py` | 结构化辅助层：报表/建 GMVmax/BC 绑定/钱包/分页，带本地校验（536 行） |
| `adfly_api/modules/*.py` | 7 个接口模块，`def` 共 305，减 `__init__` 为 298 个业务方法（自动生成） |
| `adfly_api/cli.py` | 命令行入口 |
| `adfly_api/__init__.py` | `AdflyClient` 聚合入口 + 常用捷径 |
| `adfly_api/spec/` | 清单、host 表、预计算路由表、覆盖结果、死接口清单 |
| `backend_map.py` | 段 + 路径 → host 归属的**唯一权威映射** |
| `extract_endpoints.py` | 从 bundle 提取接口（版本升级后重跑） |
| `gen_modules.py` | 由清单生成模块代码 |
| `build_routes.py` | 由实测矩阵生成预计算路由表 |
| `host_compare.py` | 全量 host 对比（判定归属的依据），产出 `spec/host_matrix.json` |
| `coverage_probe.py` | 带 token 全量覆盖测试（`--probe-writes` 做写安全检查） |
| `extract_params.py` | 从服务端校验报错提取必填字段，产出 `spec/params.json` |
| `bench.py` | 性能基线：探测开销 / 连接复用 / 延迟 / 并发 / prewarm |
| `test_transport.py` | 31 个离线单元测试 |
| `verify_client.py` | 分阶段验收（`--stage 1` / `--stage 2`） |
| `e2e_check.py` / `e2e_helpers.py` / `e2e_bc.py` | 端到端 / helpers / BC 授权验收 |
| `test_routing.py` | 多 host 路由验证 |
| `code/v2/bundle.pretty.js` | 美化后的线上 bundle（197060 行） |

`.gitignore`：`__pycache__/`、`*.pyc`、`adfly_api/.session.json`、`adfly_api/spec/routes.json`。

### 版本升级后重新同步

```bash
# 1) 找当前 bundle
curl -s "https://ad.aiadfly.com/ad-manage" | grep -oE '/[0-9]+/index-[A-Za-z0-9_-]+.js'
# 2) 下载 + 美化
curl -s -o code/v2/index.js "https://ad.aiadfly.com/<build>/index-XXXX.js"
npx prettier@3 --parser babel --print-width 120 code/v2/index.js > code/v2/bundle.pretty.js
# 3) 提取 → 重测归属 → 生成代码与路由表 → 验收
python3 extract_endpoints.py      # 需按新 bundle 调整脚本里的 SECTIONS 行号
python3 host_compare.py           # 实测各 host 归属
python3 build_routes.py           # 固化预计算路由表
python3 gen_modules.py
python3 test_transport.py && python3 e2e_check.py
```

### 设计要点

- **纯 header 认证**：`AuthorizationFront`(JWT) + `CompanyExID` + `country` + `lang`，不吃 cookie，可完全脱离浏览器
- **预计算精确路由表**：接口散在 7 个 host，覆盖测试证明每个接口只在一个 host 上成立（0 个歧义），归属固化成 `spec/routes_builtin.json`，运行时零探测
- **写操作 fail-closed**：路由无法确证时抛 `AdflyRouteError` 而不是猜一个 host
- **幂等保护**：POST 默认不自动重试（不重复建广告），GET/HEAD 才重试；429/503 按 `Retry-After` 退避
- **超时分类重放**：连接阶段失败任何方法都安全重放；读阶段失败只重放幂等方法
- **可选自动重登**：`c.t.enable_auto_relogin(account, password)` 后遇失效码自动重登并重放
- **可观测**：`c.stats()` 给出请求/探测/重试/重登/路由命中计数
- **参数参考内嵌**：34 个方法的 docstring 里直接写着实测必需字段和可用 body 样例
- **结构化辅助层**：`helpers.py` 封装报表/建广告/BC 授权/钱包/分页，带本地参数校验

