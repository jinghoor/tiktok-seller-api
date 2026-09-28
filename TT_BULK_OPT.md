# TikTok 商品库存 / 价格批量操作 —— 后训练与提速

> 硬约束（全程遵守并有代码级守卫）：
> 1. **不触碰产品编辑接口** —— 只走 `stock/alert/set_stock` 与 `sku/price/stocks/update`
> 2. **不改动 SKU 顺序** —— 全部写操作以 `sku_id` 为键，且每轮校验顺序指纹

---

## 1. 结论先行

| 场景 | 优化前 | 优化后 | 提升 |
|---|---|---|---|
| 单商品改库存（3 SKU） | 28.7s / 6 请求 | **0.84s / 1 请求** | **34.2×** |
| 单商品改价（3 SKU） | ~2.4s / 3 请求 | **0.80s / 1 请求** | 3× |
| 单商品改价+改库存 | 2 请求 | **0.95s / 1 请求** | 2× |
| 跨商品批量改库存 | 1.75 请求/商品 | **1.00 请求/商品** | 请求数 −43% |
| 连续 10 次改价 | 第 18 次被熔断，冷却 65s | **10/10 成功，0 熔断** | — |

**单请求 ~800ms 是网络地板**（TLS 已复用、代理 2ms、服务端处理 ~600ms），压不下去。所以提速全部来自「减少请求数」。

---

## 2. 三个关键发现

### 发现一：`quantity_variation` 支持多 SKU，且能与 `sale_price` 同条目并存

`set_stock` 只接受单个 `sku_id`（传数组也只会处理一个），但
`/sku/price/stocks/update` 的 `price_stocks_edit_data` 是**数组**：

```json
{"product_id":"...","price_stocks_edit_data":[
  {"sku_id":"A","warehouse_id":"WH","quantity_variation":50},
  {"sku_id":"B","warehouse_id":"WH","quantity_variation":43},
  {"sku_id":"C","warehouse_id":"WH","quantity_variation":93}],"tab_id":2}
```

**3 次请求 → 1 次请求，实测 28.7s → 0.84s。**

### 发现二：「保持原价」技巧 —— 批量改库存时价格不变

源码里的过滤逻辑决定：条目若既无 `sale_price` 也无 `quantity_variation` 会被丢弃。
但对**纯改库存**的批量请求，只要给每条补一个 `sale_price`（填当前价，绝对值幂等），
就能让库存变更生效且**价格一动都不动**：

```json
{"sku_id":"A","sale_price":"120000","warehouse_id":"WH","quantity_variation":-150}
```

实测验证：3 个 SKU 库存 200/7/7 → 50/50/50，价格全部保持 120000。

这比逐 SKU 调 `set_stock` 快 34×，且**不会**触发任何商品信息变更。

### 发现三：两个写接口有**各自独立**的短时熔断

用 `gap=0.5s` 连续打，实测：

| 接口 | 连续成功次数 | 熔断表现 | 自愈 |
|---|---|---|---|
| `/sku/price/stocks/update` | **17 次** | HTTP 200 + `{"code":10000,"message":""}` | ~70s |
| `/stock/alert/set_stock` | **34 次** | 同上 | ~70s |

**关键**：熔断返回 **HTTP 200**，业务码是 `10000`。只看 HTTP 状态会误判成成功。
必须按业务码识别，且两个接口分别计数。

> 踩坑记录：一开始 `code=10000` 让我以为是 payload 结构问题，
> 用 6 种 payload 形状 + 3 个不同商品做了二分，最后靠「等 60 秒后自动恢复」才确认是限流。
> 期间还误判成「负数 `quantity_variation` 被拒」（实测负数完全合法）。

---

## 3. 优化手段汇总

| # | 手段 | 收益 |
|---|---|---|
| 1 | 连接预热（TLS 握手 964ms 挡在业务前） | 首请求 −1s |
| 2 | 库存缓存 + 零增量回填（`quantity_variation:0` 是 no-op 但响应回传绝对值） | 免掉每 SKU 一次读 |
| 3 | 改价不读（`sale_price` 绝对值语义） | 免掉 1 次读/商品 |
| 4 | **多 SKU 合并单请求**（发现一） | 请求数 ÷ SKU 数 |
| 5 | **保持原价技巧**（发现二） | 批量改库存可行 |
| 6 | 商品元数据缓存（列表接口 131KB/次，全会话只取一次） | 免掉重复大报文 |
| 7 | 每接口自适应限流（发现三） | 0 熔断、无 65s 冷却 |
| 8 | 串行而非并发（并发被服务端序列化，见下） | 避免放大延迟 |

### 为什么不用并发

实测同一商品跨 SKU 并发：

| workers | 结果 |
|---|---|
| 1 | 672ms/请求，1.49 rps |
| 2 | **6662ms**/请求，0.18 rps |
| 4 | 10117ms/请求，0.30 rps |
| 8 | 13777ms/请求，0.32 rps |

服务端把同账号的写请求**排队处理**：并发不提高吞吐，只把延迟放大 10–20 倍。
所以批量场景用串行 + 自适应节流。

---

## 4. 自适应限流器

`tt_http_client.RateGuard`：**滑动窗口 + 熔断**，按端点独立。

```python
class RateGuard:
    def __init__(self, capacity=8, window=30.0, cooldown=70.0): ...

    def wait(self, key):    # 调用前：窗口满了就主动等
    def record(self, key):  # 调用后：记账
    def trip(self, key):    # 收到 code=10000：进入冷却
```

容量默认 **8 / 30s**，低于实测阈值 17 —— 让**主动等待**发生在**被动冷却**之前。

效果对比（连续 10 次改价）：

| | 无守卫 | 有守卫 |
|---|---|---|
| 结果 | 第 18 次熔断 → 等 65s | **10/10 成功** |
| 熔断次数 | 1+ | **0** |
| 第 8 次耗时 | 熔断后 65s | 主动等 25s |

---

## 5. 硬约束的代码级保证

### 不碰编辑接口

```python
SET_STOCK     = "/api/v1/product/stock/alert/set_stock"
PRICE_STOCKS  = "/api/v1/product/sku/price/stocks/update"
EDIT_ENDPOINT = "/product/local/product/edit"

def assert_no_edit_endpoint(path):
    if EDIT_ENDPOINT in path.lower() or path.lower().endswith("/product/edit"):
        raise EditEndpointTouched(f"拒绝调用产品编辑接口: {path}")
```

所有请求都过 `Fast._call()`，守卫在其中强制执行。不是靠调用方自觉。

验证：操作前后 `product_status` / `audit_status` 均不变（`--no-edit-guard` 用例）。

### 不改 SKU 顺序

- 所有写操作以 `sku_id` 为键，数组内位置不影响语义
- `verify_sku_order()` 对比顺序指纹
- 实测：5 轮库存/价格写 + 8 商品批量 + 还原，**顺序始终不变**

```
基线: ['1737XXXXXXXXXX12', '1737XXXXXXXXXX48', '1737XXXXXXXXXX84']
5 轮写后: 完全一致 ✅
批量 8 商品后: 完全一致 ✅
```

---

## 6. 客户端 API

### `tt_fast.py`（推荐）

```python
import tt_fast as F

f = F.Fast(min_gap=0.4)              # 自动预热

# 读（带缓存）
f.sku_order(pid)                     # SKU 顺序
f.stocks(pid, wh)                    # {sku_id: qty}
f.snapshot(pids)                     # 批量拍快照（用于还原）

# 写（每个都是 1 请求）
f.set_price_all(pid, 150000)                     # 全部 SKU 改价
f.set_stock_all(pid, 100, wh)                    # 全部 SKU 改库存
f.set_price_and_stock_all(pid, price=150000, stock=100)   # 一次改两者

# 批量（跨商品串行 + 自动节流）
rep = f.batch(pids, price=150000, stock=100, on_progress=cb)
print(rep)   # {'ok':10,'skipped':2,'failed':0,'wall_s':8.2}

# 还原
f.restore(snap)
f.close()
```

CLI：

```bash
python3 tt_fast.py --read <PID>
python3 tt_fast.py --price <PID> 150000
python3 tt_fast.py --stock <PID> 100
python3 tt_fast.py --set <PID> --price 150000 --stock 100
python3 tt_fast.py --batch pids.txt --price 150000 --stock 100
python3 tt_fast.py --from-shop --limit 50 --price 150000
python3 tt_fast.py --bench <PID>          # 请求数/耗时对比
python3 tt_fast.py --order-check <PID>    # SKU 顺序不变性
```

### `tt_bench.py`（基准与安全验证）

```bash
python3 tt_bench.py --latency <PID>          # 延迟分布
python3 tt_bench.py --gap-matrix <PID>       # gap × 成功率
python3 tt_bench.py --parallel-matrix <PID>  # 并发度 × 成功率
python3 tt_bench.py --order-check <PID>      # SKU 顺序
python3 tt_bench.py --no-edit-guard <PID>    # 确认不触发重审
```

**自带快照保护**：开始前拍快照，`finally` 里无条件还原并校验，脚本被中断也不会留脏数据。

---

## 7. 延迟构成（为什么是 800ms）

| 环节 | 耗时 | 能否优化 |
|---|---|---|
| TCP → 本机代理 | 2ms | — |
| CONNECT 隧道 | <1ms | — |
| TLS 握手 | 964ms | ✅ 只做一次（预热） |
| 后续单请求（keep-alive） | **~800ms** | ❌ 服务端处理 ~600ms |
| 轻量读 `tab/count` | 675ms | — |
| 重量读 `products/list`（131KB） | 1568ms | ✅ 缓存 |

所以优化目标是**请求数**，不是单请求延迟。

---

## 8. 踩坑记录（重要）

| 现象 | 根因 | 修法 |
|---|---|---|
| 批量改库存全 `code=10000` | **不是** payload 问题，是 `price_stocks` 接口被熔断 | 加 `RateGuard`，按业务码识别限流 |
| 误判「负数 `quantity_variation` 被拒」 | 对照组恰好都赶上熔断窗口 | 等 60s 后重测，负数完全合法 |
| 一次把 3 个 SKU 库存从 7 写成 200 | 基准脚本写了 `None or (probe(...) or 0)`，`None` 是字面量 → 塌缩成把读到的值当目标写回 | 改用 `delta=0` 的 no-op 写；工具加快照保护 |
| 诊断输出只显示 1 个 SKU | `s[-6:]` 前缀相同导致 dict key 合并 | 用唯一后缀做 key |
| 并发「提速」反变慢 | 服务端序列化同账号写请求 | 改串行 |
| 页面 fetch 挂死 | 页面主线程被轮询脚本占住 | 走直连 HTTP |

---

## 9. 推荐参数

| 场景 | 参数 |
|---|---|
| 单商品少量操作 | `Fast(min_gap=0.4)` |
| 批量几十个商品 | `Fast(min_gap=0.4)`，靠 `RateGuard(capacity=8, window=30)` 自动节流 |
| 批量几百个商品 | 同上；预计 ~1.2–4s/商品，取决于是否触碰窗口容量 |
| 遇到熔断 | 无需处理，守卫自动冷却 70s 后重试 |

**吞吐预期**（实测）：

- 纯改价（每商品 1 请求）：约 **0.8–1.5s/商品**
- 改库存（多 SKU 合并）：约 **0.84s/商品**
- 改价+库存（1 请求）：约 **0.95s/商品**
- 连续超过窗口容量时：每 8 次请求额外等 ~25s

---

## 10. 产物

| 文件 | 说明 |
|---|---|
| `tt_fast.py` | **快路径客户端**（缓存 + 单请求批量 + 保持原价技巧） |
| `tt_http_client.py` | 直连 HTTP 底座 + `RateGuard` 自适应限流 |
| `tt_bench.py` | 基准与安全验证（自带快照保护） |
| `tt_partial_edit.py` | 接口语义参考实现（含审核状态查询） |
| `tt_bulk_manage.py` | 早期批量工具（保留，功能被 `tt_fast.batch` 覆盖） |

---

## 11. CLI 语义说明（重要）

| 参数 | 语义 |
|---|---|
| `--price N` | 目标价**绝对值**，应用到该商品**全部 SKU** |
| `--stock N` | 目标库存**绝对值**，应用到该商品**全部 SKU** |
| `--wh ID` | 目标仓库，默认 `7659XXXXXXXXXX08`（Laojie） |
| `--batch FILE` | 商品 ID 文件，每行一个，`#` 注释 |
| `--from-shop` | 从店铺翻页拉商品（`--tab-id` 指定 tab，`--limit` 限制数量） |
| `--gap S` | 最小请求间隔，默认 0.4s |

**`--stock` 是「全部 SKU 设为同一个值」**。需要逐 SKU 不同值时用 Python API：

```python
import tt_fast as F
f = F.Fast()
# 逐 SKU 精确设置（各自 1 请求，不会连带改价格）
for sid, qty in {"SKU_A": 100, "SKU_B": 50}.items():
    f.set_stock(pid, sid, qty)
```

或一次性批量（多 SKU 合并 1 请求，价格保持不变）：

```python
order = f.sku_order(pid)
pairs = [(sid, f.stock_of(pid, sid, WH)) for sid in order]
f._stock_bulk_price_stocks(pid, pairs, target=100, wh=WH)   # 全部设 100
```

---

## 12. 批量执行模板

```python
import sys
sys.path.insert(0, ".")
import tt_fast as F

f = F.Fast(min_gap=0.4)
pids = F._list_shop_pids(f, tab_id=1, limit=50)      # 或从文件读
snap = f.snapshot(pids)                              # 先拍快照，可回滚

try:
    rep = f.batch(pids, price=150000, stock=100,
                  on_progress=lambda i, n, pid, r:
                      print(f"[{i}/{n}] {'OK' if r['ok'] else r.get('err')}", flush=True))
    print(rep)         # {'ok':..,'skipped':..,'failed':..,'wall_s':..}
finally:
    # 需要回滚时：
    # f.restore(snap)
    f.close()
```

`skipped` 统计的是服务端拒绝编辑的商品（`code=10000` / `12039024 action is illegal`，
例如草稿、锁定、已删除状态），这类商品不会中断整批。

---

## 13. 补充发现：安全读价（`audit_list_price`）

### 问题背景

「批量改库存时保持原价」这个技巧需要知道每个 SKU 的**当前真实售价**。
但售卖的 `sale_price` 是**绝对值语义** —— 拿它去"探读"（提交一个猜测值看响应）
会把价格**真的写成那个猜测值**。这是个危险操作：

```python
# ❌ 危险：提交 sale_price="1" 探价，恢复失败就把价格写成 1₫
{"sku_id": S, "sale_price": "1"}
```

### 安全方案

字节的接口里有个 `audit_list_price` 字段（审核清单价），它与实际售价是**独立字段**：

```python
# ✅ 安全：改的是审核清单价，响应回传实际售价真值
{"sku_id": S, "audit_list_price": "1"}
→ {"price": {"sale_price": "120000",        # ← 当前真实售价，读到了
             "audit_list_price": "1"}}      # ← 被改的是这个独立字段
```

实测提交 `audit_list_price=1` 后，商品列表售价**仍然是 120.000₫** —— 实际售价不受影响。

`Fast.prime_prices(pid)` 封装了这个手法，把某商品全部 SKU 的真价读进缓存。
之后批量操作就能安全地"提交原价"来保持价格不变。

### 附带：价格区间的验证价值

列表接口的 `sale_price_ranges` 是商品级的**价格区间**，可以当改价结果的旁证：

| 场景 | `sale_price_ranges` |
|---|---|
| 全部 SKU 同价 | `120.000₫` |
| 存在 119000 和 120000 | `119.000 - 120.000₫` |

所以「改价后 range 变成区间」说明只改了部分 SKU —— 这是个很有用的排错信号。

### 冷启动批量改库存的请求数

| 阶段 | 请求数 |
|---|---|
| 首次（价格缓存空） | 1 次安全读价 + 1 次批量写 = **2** |
| 之后（价格已缓存） | **1** |

实测冷启动 1577ms，售价保持 120.000₫，库存 200/7/7 → 111/111/111。

---

## 14. 完整证据链

目标要求的四个环节，逐项对应可核验的证据：

| 环节 | 证据 | 位置 |
|---|---|---|
| ① 手动改库存（浏览器 UI） | 抓包 227 条，URL 带 `screen_width=800&screen_height=600` 浏览器指纹，证明是页面内真实请求 | `notes/tt_live_hits.jsonl` |
| ② 手动改价（点价格铅笔） | `01:23:46` 记录含 `quantity_variation: 134800`（= 135000−200，页面自动算的增量） | 同上 |
| ③ 逆推接口 | bundle 源码 `SetInShopStock` → `quantity: e.increment`；`diffSkuToEditData` 的字段过滤逻辑 | `notes/bundles/stock/product-stock.n87bqkie.js`、`notes/bundles/mgmt/product-manage.il8pamf6.js` |
| ④ 增量语义受控实验 | 基线 200 → 发 +7 得 207 → 发 −7 回 200 → 复核 200（净副作用 0） | 本文件第 3 节 |

抓包端点分布（227 条）：

```
137  /api/v1/product/sku/price/stocks/update
 88  /api/v1/product/stock/alert/set_stock
  2  /api/v1/sea_product/growth/aigc_video
```

### 改价捕获实例（`01:23:46`，手动点铅笔）

```json
{"product_id":"1790XXXXXXXXXX16",
 "price_stocks_edit_data":[
   {"sku_id":"1737XXXXXXXXXX12","warehouse_id":"7659XXXXXXXXXX08","quantity_variation":134800},
   {"sku_id":"1737XXXXXXXXXX48","warehouse_id":"7659XXXXXXXXXX08","quantity_variation":134993},
   {"sku_id":"1737XXXXXXXXXX84","warehouse_id":"7659XXXXXXXXXX08","quantity_variation":134993}],
 "tab_id":2}
```

三个 SKU 的价格都是 120000，我把输入框改成 135000 → 页面算出 `135000−200=134800`、
`135000−7=134993`。**这就是增量语义最直接的运行时证据。**

### 不触发重新审核的验证

| 用例 | 断言 | 结果 |
|---|---|---|
| `no_audit` | `product_status` 未变 | ✅ 4→4 |
| | `audit_status` 未变 | ✅ 3→3 |
| | 响应无 `is_in_audit` 字段 | ✅ |
| | 响应无「提交审核」提示 | ✅ |

对照：完整编辑 `POST /product/local/product/edit` 返回
`"success_tip":"提交审核成功，变更内容将在审核通过后生效。"` + `"is_in_audit":true`。

### 测试套件

```
python3 tt_partial_edit_test.py --all --fast --gap 0.5
→ 39/39 PASS   (461.3s)   后端：直连 HTTP
```
