# 路由存在性测绘（不需要登录）

## 1. ★ 核心发现：两个响应能区分「路由存在」和「不存在」

网关的匹配顺序是 **先路由、后鉴权**。所以会话过期时：

| 响应 | 含义 |
|---|---|
| `98001002 请登录` | **路由存在** —— 请求已打到业务层，只是鉴权没过 |
| 业务 code（`binding:` / `NUMBER_REDACTED` / …） | **路由存在** |
| `No matching route` | **路由不存在** —— 网关注册表里没有 |
| `404 Not Found`（HTML / TLB） | **不存在**，且来自更外层网关 |

**这解决了一个卡点**：SHOP_XBORDER/SHOP_LOCAL 会话过期后我以为没法再实测了，
但实际上**路由存在性完全不依赖登录**。

## 2. 220 个 404 的根因（回查调用点后定性）

写了 `trace_endpoint.py`，拿路径特征片段在 738 个 bundle 里搜真实调用点。

结论：**220 个全是真接口，没有一个是前端路由误判。**

回查到的调用点长这样：

```js
SearchHscodeBase(e,t){ let i=`${this.uriPrefix}/api/v${e.version||1}/logistics/customs/hscode/hscode_base/query`;
                    return (0,r.ZP)(i,{method:"POST",headers:s.A,body:e},t) }
```

三个特征：

1. **版本由调用方给**（`${e.version||1}`）—— 不是固定 v1
2. **方法是 POST 带 body** —— 不是 GET
3. **前缀是 `uriPrefix` 运行时拼的** —— 主机/前缀不在 bundle 里

方法层面我用 `fix_methods_by_trace.py` 全量核过：

| 结果 | 数量 |
|---|---|
| 与调用点一致 | 878 |
| **冲突** | **0** |
| 仍未知 | 529 |

**0 冲突**说明方法抽取本身是准的。所以 404 既不是方法问题也不是版本问题，
而是**这些路径不在该店铺所在网关上**。

## 3. 谁在哪个网关上 —— 已有的证据

| 路径族 | 本土 SHOP_LOCAL (`seller-vn`) | 跨境 SHOP_X3 (`api16-normal-sg`) |
|---|---|---|
| `/api/v1/pay/settlement/*` | ◐ 路由存在（需登录） | ✅ 通 |
| `/api/v1/insights/*` | ◐ 路由存在（需登录） | ◐ 存在（缺 body） |
| `/api/oec/pay/merchant/statement/view/*` | ✅ 通（财务轮实测） | ✅ 通 |
| `/api/oec/pay/merchant/statement/config/*` | ✗ **无此路由** | ✗ 404 |
| `/api/v1/logistics/customs/*` | ✗ **无此路由** | ✗ 404 |
| `/api/v1/fulfillment/subsidy/*` | ✗ **无此路由** | ✗ 404 |

`/logistics/customs/*`（64 个）和 `/fulfillment/subsidy/*`（16 个）两边都没有 ——
bundle 里出现 `seller-us.tiktok.com` / `seller-uk.tiktok.com` 等域名，
**推测是特定市场（US/UK 半托管）专有**。要定论需要那个市场的店铺。

## 4. 全量测绘

```bash
python3 map_route_existence.py --shop tk89 --all      # 4873 个路由
```

小样（120 个）结果：

| 判定 | 数量 |
|---|---|
| ✗ 路由不存在 | 53 |
| ◐ 路由存在（需登录） | 43 |
| ◐ 路由存在（其它 code） | 8 |
| ✗ 404（外层网关） | 8 |
| ? 其它 | 8 |

**路由存在 51/120 = 42%**（本土店只注册了它自己那部分路由）

「不存在」的样例集中在 `/api/oec/pay/merchant/statement/config/*`（oec 网关专有）——
本土店走不到 oec 网关，与其本地化部署一致。

## 5. 新增工具

| 脚本 | 作用 |
|---|---|
| `trace_endpoint.py` | 拿路径片段回查 738 个 bundle 里的真实调用点（URL 表达式 / 方法 / body） |
| `fix_methods_by_trace.py` | 全量核方法：878 一致 / 0 冲突 |
| `map_route_existence.py` | 路由存在性测绘，**不需要登录** |
