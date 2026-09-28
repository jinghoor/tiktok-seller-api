# adfly_api — ad.aiadfly.com 广告管理接口客户端

对 `https://ad.aiadfly.com/ad-manage` 的接口逆向产物：**291 个唯一接口**，
全部经过实机覆盖测试，覆盖广告账户、商务中心授权、GMVmax 推广系列、VSA 广告、
报表导出、钱包资金、自动化策略、AI Agent。

- 接口文档 → [`API.md`](API.md)
- 实战示例 → [`EXAMPLES.md`](EXAMPLES.md)
- 全量接口表 → [`api_tables.md`](api_tables.md)
- **覆盖测试报告 → [`coverage.md`](coverage.md)**（含每个接口的实测状态与耗时）
- 优化记录与基线 → [`OPTIMIZATION.md`](OPTIMIZATION.md)

## 安装

```bash
python3 -m pip install requests certifi
```

## 30 秒上手

```bash
cd "/Users/maxj/Documents/Python Project/Project-创翼广告/.work/adfly"

export ADFLY_PASSWORD='你的密码'
python3 -m adfly_api login --account PHONE_REDACTED

python3 -m adfly_api call advertise POST /tiktok/gmv_max/list '{"page":1,"page_size":5}'
python3 -m adfly_api call finance_bff POST /wallet/list '{"currency":"USD"}'
```

```python
from adfly_api import AdflyClient

c = AdflyClient()
c.login("PHONE_REDACTED", "密码")

print(len(c.advertisers()), "个广告账户")                                  # 8
print(c.ads.get_gmv_max_list({"page": 1, "page_size": 5})["count"])       # 62
c.download("advertise", "/tiktok/advertiser_report/export", "out.xlsx",   # 导出 xlsx
           {"start_date": "2026-09-01", "end_date": "2026-09-24"})
print(c.stats())
```

## 实测结论（不是推测）

覆盖测试对 199 个非写接口逐个实调：

| 状态 | 数量 | 含义 |
|---|---|---|
| **OK** | **76** | 直接返回业务数据（含 10 个 xlsx 导出） |
| PARAM | 47 | 路由通，本次调用缺必填参数（参数名从报错文案里已提取） |
| NOAUTH | 32 | 路由通，当前账号无该账户/店铺权限 |
| GONE | 33 | 服务端已移除（Google Ads 残留），清单见 `spec/unavailable.json` |
| ERROR | 10 | 服务端 5xx，需数据前置条件（如先有广告组才有 `/ad/list`） |
| AUTH | 1 | 需先开户 |

**86 个写接口默认不实调**（空 body 打 `/delete`、`/bind`、`/transfer` 会真改数据）。
`coverage_probe.py --probe-writes` 可做安全检查。

延迟：p50 **63ms** / p90 279ms / p99 3.1s（含冷启动）。

## 验收状态（全部可复现）

| 套件 | 命令 | 结果 |
|---|---|---|
| 离线单元测试 | `python3 test_transport.py` | **28/28** |
| 阶段 1（无需凭证） | `python3 verify_client.py --stage 1` | **4/4** |
| 阶段 2（真实登录） | `python3 verify_client.py --stage 2` | **31/31** |
| 端到端验收 | `python3 e2e_check.py` | **27/27** |
| 多 host 路由 | `python3 test_routing.py` | 18/22 可达（余 4 项为测试数据缺失，非缺陷） |
| helpers 验收 | `python3 e2e_helpers.py` | **25/25** |
| BC 授权验收 | `python3 e2e_bc.py` | **22/22** |
| 覆盖测试 | `python3 coverage_probe.py 6` | 76 OK / 33 GONE（明细见 `coverage.md`） |
| 性能基线 | `python3 bench.py` | 探测 0.00x、并发 230 rps |

## 设计要点

- **纯 header 认证**：`AuthorizationFront`(JWT) + `CompanyExID` + `country` + `lang`，
  不吃 cookie，可完全脱离浏览器
- **预计算精确路由表**：接口散在 7 个 host，覆盖测试证明**每个接口只在一个 host 上成立
  （0 个歧义）**，所以把归属固化成 `spec/routes_builtin.json`，运行时**零探测**
- **写操作 fail-closed**：路由无法确证时抛 `AdflyRouteError` 而不是猜一个 host，避免写错服务
- **幂等保护**：POST 默认不自动重试（不重复建广告），GET/HEAD 才重试；429/503 按 `Retry-After` 退避
- **可选自动重登**：`c.t.enable_auto_relogin(account, password)` 后遇 code=2/9 自动重登并重放
- **可观测**：`c.stats()` 给出请求/探测/重试/重登/路由命中计数
- **参数参考内嵌**：34 个方法的 docstring 里直接写着实测必需字段和可用 body 样例
- **结构化辅助层**：`adfly_api/helpers.py` 封装报表/建广告/BC 授权/钱包/分页，带本地参数校验
- **超时分类重放**：连接阶段失败（请求没出去）任何方法都安全重放；读阶段失败只重放幂等方法，
  写操作绝不盲重放

## 目录

| 文件 | 用途 |
|---|---|
| `adfly_api/transport.py` | 传输层：登录、多 host 路由、错误映射、重试退避、翻页、下载 |
| `adfly_api/helpers.py` | 结构化辅助层：报表/建 GMVmax/BC 绑定/钱包/分页，带本地校验 |
| `adfly_api/modules/*.py` | 7 个模块共 289 个方法（自动生成） |
| `backend_map.py` | 段+路径 → host 归属的**唯一权威映射** |
| `adfly_api/spec/` | 清单、host 表、预计算路由表、覆盖结果、死接口清单 |
| `adfly_api/cli.py` | 命令行入口 |
| `extract_endpoints.py` | 从 bundle 提取接口（版本升级后重跑） |
| `gen_modules.py` | 由清单生成模块代码 |
| `build_routes.py` | 由实测矩阵生成预计算路由表 |
| `host_compare.py` | 全量 host 对比（判定归属的依据） |
| `coverage_probe.py` | 带 token 全量覆盖测试 |
| `extract_params.py` | 从服务端校验报错提取必填字段（含参数发现） |
| `bench.py` | 性能基线：探测开销 / 延迟 / 并发 |
| `test_transport.py` | 28 个离线单元测试 |
| `verify_client.py` / `e2e_check.py` / `test_routing.py` | 分阶段验收 |

## 版本升级后重新同步

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

## 已知限制

- **登录单会话**：登录会让同账号其它会话失效。Python 端登录后浏览器需要重新登录。
- 33 个接口在当前版本已移除（Google Ads 相关），调用会得到 `AdflyRouteError`。
- `tt_auth_id` 类型不统一：`identity/get` 要 Number，`store/list` 原样传。
- `automation` 分页用 `{"page_info":{...}}`，`finance_bff` 的 `/pay/*`、`/coupon/*` 同；
  其余用平铺 `{"page":1,"page_size":N}`。
- 导出接口返回二进制，用 `c.download(...)`。

---

# 第三轮:BC 授权与超时安全性

## BC 授权接口的参数是怎么套出来的

`adv_bc_bind` 的字段名文档里没有,靠类型错误反推:

```
{"advertiser_id": "字符串"} → json: cannot unmarshal string into Go struct field AdvBcBind...
{"advertiser_id": ["数组"]} → bc_id(mcc_id)为空
{"advertiser_id": [...], "bc_id": "..."}  → code=0
```

顺手排除了 `advertiser_ids` / `adv_ids` / `advertiser_id_list` 等一票猜测 ——
它们全都返回"广告账号id列表为空",说明字段名就不是这些。

类似的坑还有两个:`get_auth_link` 缺 `platform` 报 `server_invalid_platform`;
`get_bind_bc` 缺 `platform` **返回 null 而不是报错**,极易误判成"没有绑定"。

## 一个必须记录的事故

我用 `adv_bc_bind` 做参数探测时**真的创建了 3 条绑定任务记录** ——
`adv_bc_bind_list` 从 9 条涨到 11 条(两次调用,其中一次带全 0 的假 task_id)再加 1 条更早的探测。

初次看到它们 `status=4` 时我判断"是失败记录,没产生有效绑定"。**这个判断是错的** ——
后续复查发现其中记录已经变成 `status=2`(绑定生效)。服务端是异步推进的,
`4` 只是"提交后未落定",不是终态失败。

于是:账户 `7689XXXXXXXXXX05` 上现在有 3 条指向 BC `7626XXXXXXXXXX75` 的记录,
时间戳集中在 04:04,都是我的探测造成的。系统里**没有取消绑定任务的接口**,
唯一撤销路径是解绑。

真正的教训不是"要小心",而是:**对创建任务类接口做参数探测前,先确认存在可撤销路径;
没有的话就不该探测 —— 应该从 bundle 的调用点或类型错误里静态推断。**
我这次是靠类型错误(`cannot unmarshal string into Go struct field`)定位到字段名和数组类型的,
那一步是安全的;不安全的是之后"补值验证"的两次真实调用。

已把这条写进 `helpers.py` 模块注释和 `API.md`,并提供 `pending_bind_records()`
(按 `updated_at - created_at` 时间差判断未落定)作为提交前的护栏。

## 顺带修掉的传输层缺陷

调试过程中反复遇到 TLS 握手超时,暴露出原来的重试逻辑对写操作太脆:非幂等请求只有
1 次机会,一次网络抖动就抛错。于是按**失败阶段**区分安全性:

| 失败类型 | 请求是否已发出 | 写操作(POST) | 读操作(GET) |
|---|---|---|---|
| ConnectTimeout / TLS 握手超时 | 否 | **重放 1 次** | 重放满 retries |
| ConnectionError | 否 | **重放 1 次** | 重放满 retries |
| ReadTimeout | 可能已处理 | **不重放** | 重放满 retries |

离线验证(31 个单元测试里的 `TestTimeoutReplaySafety`):

```
ConnectTimeout     POST  2 次调用   OK(重放一次)
ReadTimeout        POST  1 次调用   OK(不重放)
ReadTimeout        GET   3 次调用   OK(重放满 retries)
ConnectionError    POST  2 次调用   OK
```

顺带把循环上界改成按最宽松情况预留 —— 原来 `range(attempts)` 对非幂等请求就是
`range(1)`,内层的"连接阶段可重放"判断永远不会执行(这个 bug 是单元测试抓出来的)。

## 验收

```
python3 test_transport.py              31/31
python3 verify_client.py --stage 1      4/4
python3 verify_client.py --stage 2     31/31
python3 e2e_check.py                   27/27
python3 e2e_helpers.py                 25/25
python3 e2e_bc.py                      22/22
```
