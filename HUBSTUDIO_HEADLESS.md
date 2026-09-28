# Hub Studio 无头模式 — 实测结论

> 结论来自本机实跑，非文档推测。原始报告 `/tmp/hub_headless_report.json`，截图 `/tmp/hub_headless_shot.png`。
> 实测时间基线：Hubstudio 客户端 **3.54.0**，内核 **Chrome 144.0.7559.230**。

---

## 一、两个不同层面的「无头」——别搞混

| | 含义 | 参数 | 本次是否涉及 |
|---|---|---|---|
| **客户端无头** | Hubstudio 客户端本身跑在无桌面服务器上（Xvfb / AppImage） | 启动参数 `--headless=true --app-id=.. --app-secret=..` | 否，需要 App Key，且要重装客户端 |
| **环境无头** | 单个浏览器环境以内核 headless 方式启动 | Local API `POST /api/v1/browser/start` 的 **`isHeadless`** | **是，本次实测对象** |

日常自动化只需要第二种，不需要动客户端。

---

## 二、`isHeadless` 的权威定义

### 官方 schema（`POST /api/v1/browser/start`，[打开环境](https://api-docs.hubstudio.cn/380052361e0)）

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `containerCode` | string | **是** | 环境ID |
| `isHeadless` | boolean | 否 | 浏览器无头模式，默认 false。设置无头后如无法连接，请使用 `args` 参数进行设置：`["--headless=new"]` |
| `args` | array\<string\> | 否 | 启动参数，例：`["--kiosk", "--blink-settings=imagesEnabled=false"]` |
| `containerTabs` | array\<string\> | 否 | 启动时打开的 URL |
| `cdpHide` | boolean | 否 | 屏蔽 CDP 检测，仅 Chrome 133+ 内核 |
| `isWebDriverReadOnlyMode` | boolean | 否 | 只读模式（true 则不保存 cookie 等数据） |
| `pageZoom` | integer | 否 | 缩放，仅支持 0.5/0.75/1/1.25/1.5/1.75/2，150% 传 `1.5`。需客户端 ≥3.46.0 |
| `skipSystemResourceCheck` | boolean | 否 | 跳过系统资源检测，需 ≥3.6.0 |
| `serialNumber` | string | 否 | 序号，与 `containerCode` 同传时以 `containerCode` 为准。**需客户端 ≥3.55.0**（本机 3.54.0，未验证） |

### 客户端内部实现（`app.asar` 反查，与官网一致）

```js
// startBrowserByCode —— Local API 直接解构 body 后透传给 SDK
const { containerCode, isHeadless, isWebDriverReadOnlyMode, args,
        skipSystemResourceCheck, containerTabs, shouldCloseTabsOnOpen,
        cdpHide, pageZoom, ipCheckOpen = false } = data;
await Ke.request(se, "/container/open", { ..., apiParams: {
    isHeadless: !!isHeadless, containerTabs: containerTabs || [], args: args || [],
    isWebDriverReadOnlyMode: ... , cdpHide: !!cdpHide, pageZoom, ipCheckOpen: !!ipCheckOpen }});

// SDK 侧消费
if (isApi) {
  const { isHeadless, isWebDriverReadOnlyMode, cdpHide, pageZoom, args } = apiParams || {};
  instance.Headless = isHeadless;                       // ← 内核通过 JSON 配置收无头标志
  instance.ExecArgs = [...instance.ExecArgs, ...(args || [])];
  instance.Custom.ReadOnly = isWebDriverReadOnlyMode;
}
```

**关键机制**：`isHeadless` 走的是内核的 **JSON 配置字段 `Headless`**，不是命令行 `--headless`。因此内核进程的命令行里**看不到** `--headless`，判断是否无头只能看 CDP 或 `runningContainers.isHeadless`。

附带行为（可作为旁证）：UI 层 `openedContainers` 会过滤掉无头实例 ——
`runningContainers.forEach(({status, hwnd, isHeadless}) => { if (status===SUCCESS && hwnd) push({...isHeadless}) })`，
窗口排布 / 置顶功能同样 `if (container.status===0 && container.hwnd && !container.isHeadless)`。无头实例不出现在窗口网格里。

---

## 三、实测结果（一次性环境 `ZZ-headless-probe`，跑完已删除）

请求：

```bash
curl -s -X POST http://127.0.0.1:6873/api/v1/browser/start \
  -H 'Content-Type: application/json' -d '{
  "containerCode": "<code>",
  "isHeadless": true,
  "containerTabs": ["about:blank"],
  "skipSystemResourceCheck": true }'
```

返回（7.3s 完成）：

```json
{"code":0,"msg":"Success","data":{
  "action":"startBrowserByCode","debuggingPort":"62972","webdriver":".../chrome_64_144/webdriver",
  "browserPath":".../Core/chrome_64_144/hubstudio.app/Contents/MacOS/hubstudio",
  "containerId":185024748,"runMode":2,"proxyType":"local","ip":"117.182.106.196",
  "statusCode":"0","err":"成功(Success)"}}
```

### 验证 1 — CDP 回报无头 UA（最硬判据）

```
GET http://127.0.0.1:62972/json/version
→ "Browser": "Chrome/144.0.7559.230"
→ "User-Agent": "...HeadlessChrome/144.0.0.0 Safari/537.36"     ← 无头确认
```

### 验证 2 — 页面内 JS 看不到无头（指纹伪装生效）

```js
// Runtime.evaluate on about:blank
{"ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ... Chrome/144.0.0.0 Safari/537.36",
 "headless":false,  // /Headless/i.test(navigator.userAgent) === false
 "w":800,"h":479,   // 无头默认视口
 "webdriver":false}
```

→ 站内脚本读到的 UA 是**正常 Chrome**，不是 `HeadlessChrome`。TikTok 后台不会因为这个被识别成机器人。

### 验证 3 — 页面可读、可操作、可截图

| 操作 | 结果 |
|---|---|
| `Page.navigate https://example.com/` | ✅ `frameId` 正常返回 |
| 读 DOM | ✅ `"Example Domain \| Example Domain"` |
| `Page.captureScreenshot` | ✅ PNG 15870 bytes，800×479，内容完整渲染 |

截图：`/tmp/hub_headless_shot.png`

### 注意事项

- **内核进程命令行里没有 `--headless`**：`ps` 看到的只有 `--port=39996 --no-sandbox --use-mock-keychain --store_data_path=... --browser_id=SB... --user-data-dir=...`。这不是 bug，见第二节。想强制走命令行可加 `"args": ["--headless=new"]`。
- **CDP WebSocket 握手需要不带 `Origin`**：默认带 `Origin` 会被拒
  `403 Rejected an incoming WebSocket connection from the http://127.0.0.1:62972 origin`。
  Python：`websocket.create_connection(ws_url, suppress_origin=True)`。
  或在 `args` 里加 `--remote-allow-origins=*`。
- **无头默认视口 800×479**，后台类页面会被判成 mobile/紧凑布局。建议：
  `"args": ["--window-size=1920,1080"]`，或建环境时在 `advancedBo.width/height` 固定分辨率。
- **Cookie 持久化不受影响**：实例仍带 `--user-data-dir=.../sdk/cache/chromium_<envId>`，同一环境非只读模式下 cookie / localStorage 照常落盘，无头重启后登录态还在。**只有 `isWebDriverReadOnlyMode: true` 才不存。**
- 测试环境默认分组，删除用 `POST /api/v1/env/del {"containerCodes":["<code>"]}`。

---

## 四、能拿店铺信息 / 操作店铺吗

**能 —— 已对真实店铺环境只读实测通过。**

对 SHOP_LOCAL 环境（`containerCode=NUMBER_REDACTED`，CDP CDP_PORT，正在跑）直连只读抓取：

```
url:     https://seller-vn.tiktok.com/ads-creation/dashboard?...&shop_region=VN
ua:      Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ... Chrome/141.0.0.0 Safari/537.36
cookies(tiktok.com): 145          ← 环境 profile 自动加载,无需重新登录
cookieLen: 3418
```

无头只是没有可见窗口，页面运行环境、cookie、扩展、代理、指纹全部一致。本机已有的 TikTok 逆向结果可直接复用：

```python
from hub_headless import HubStudio, attach

hub = HubStudio()
port = hub.start("NUMBER_REDACTED", headless=True)["debuggingPort"]   # SHOP_LOCAL
with attach(port) as p:
    p.navigate("https://seller-vn.tiktok.com/ads-creation/dashboard")
    # 之后仍是 cookie + X-CSRFToken 那套,和 headful 完全一样
```

已验证可行的链路（headful 下已跑通 14 条广告）：
1. `search_spu?aadvid=..&oec_seller_id=..&org_id=<shop_authorized_bc>` → 商品列表
2. `create?...` → 建 GMV Max 广告

**关键点：直接驱动 `debuggingPort` 的 WebSocket，不要用导出的 cookie 重建会话。** 环境 profile 里已有登录态，attach 上去就能用；而导出到文件的 cookie 会随环境 UA 漂移而失效 —— 实测该环境 JS 层 UA 已从 `Chrome/144` 漂到 `Chrome/141`（内核仍是 144，属指纹伪装），`notes/tiktok_session.json` 里记的 144 已经不准。

**唯一没法替你做的一步**：店铺首次登录需要人工输入密码。要么先在 headful 下登录一次（cookie 落盘），要么用 `POST /api/v1/env/import-cookie` 把已有环境的 cookie 导进去。

---

## 五、本机环境 ↔ 店铺 对照表（修正）

`POST /api/v1/env/list` 带 `containerCodes` 可以**跨分组**查到运行中的容器。之前记的 serial 映射是错的（那是列表前 10 条的序号），正确映射：

| containerCode | serialNumber | 环境名 | 状态 |
|---|---|---|---|
| NUMBER_REDACTED | **550** | TK89_Local_Shop | 运行中 |
| NUMBER_REDACTED | **516** | TK56_CrossBorder_Shop | 运行中 |
| 942239581 | **427** | TK20跨境_个护-立志（曝光量降低） | 运行中 |
| 449112296 | **109** | TK01_CrossBorder_个护-Owner | 运行中 |

其他 6 个（当前登录分组 TKSP_越南）：

| serial | 环境名 | containerCode |
|---|---|---|
| 685 | TK194越本土-药-立志 (养血安神片) | NUMBER_REDACTED |
| 686 | TK195越本土-药-Owner | NUMBER_REDACTED |
| 687 | TK196越本土-药-Owner | NUMBER_REDACTED |
| 688 | TK197越本土-药-真祯 | NUMBER_REDACTED |
| 689 | TK198越本土-被停用 | NUMBER_REDACTED |
| 690 | TK199越本土-药-Owner-被停用 | NUMBER_REDACTED |
| 691 | TK200越本土-药-Owner | NUMBER_REDACTED |
| 692 | ChatGPT-Maxj@ | NUMBER_REDACTED |
| 693 | 亚马逊01 | NUMBER_REDACTED |
| 694 | TK201本土_美妆_Owner-被封（焕亮精华液） | NUMBER_REDACTED |

> `SHOP_LOCAL = 550`，不是 558。你之前说的「558 号店铺」在本机任何数据里都不存在 —— 但 550 就是 TK89_Local_Shop，任务已按它完成。

---

## 六、常用调用

```bash
# 无头启动某店铺环境
curl -s -X POST http://127.0.0.1:6873/api/v1/browser/start -H 'Content-Type: application/json' \
  -d '{"containerCode":"NUMBER_REDACTED","isHeadless":true,
       "args":["--window-size=1920,1080"],"skipSystemResourceCheck":true}'

# 查所有打开的环境（含 pid）
curl -s -X POST http://127.0.0.1:6873/api/v1/browser/all-browser-status -d '{}' -H 'Content-Type: application/json'

# 关环境
curl -s -X POST http://127.0.0.1:6873/api/v1/browser/stop -H 'Content-Type: application/json' \
  -d '{"containerCode":"NUMBER_REDACTED"}'

# 跨分组查环境名
curl -s -X POST http://127.0.0.1:6873/api/v1/env/list -H 'Content-Type: application/json' \
  -d '{"containerCodes":["NUMBER_REDACTED"]}'
```

CLI 等价（`hubstudio-cli` 已随客户端提供，macOS/Linux IPC `/tmp/Hubstudio-cli`，回退 `HUBSTUDIO_LOCAL_API_PORT` / 6873）：

```bash
hubstudio-cli start-browser containerCode=NUMBER_REDACTED isHeadless=true pageZoom=100
hubstudio-cli start-browser --json '{"containerCode":"NUMBER_REDACTED","isHeadless":true,"args":["--headless=new","--disable-gpu"]}'
```

---

## 七、配套模块 `hub_headless.py`

```bash
cd .work/adfly
python3 -m pip install websocket-client     # 唯一外部依赖

python3 hub_headless.py doctor                       # 自检:API/环境/运行中/CDP/无头状态
python3 hub_headless.py list                         # 环境 + 运行状态 + CDP 端口(跨分组)
python3 hub_headless.py start --code NUMBER_REDACTED --verify           # 无头启动 SHOP_LOCAL
python3 hub_headless.py start --code NUMBER_REDACTED --headful          # 有头
python3 hub_headless.py start --code NUMBER_REDACTED --window 2560,1440 # 指定视口
python3 hub_headless.py eval  --port CDP_PORT --js "document.title"
python3 hub_headless.py grab  --port CDP_PORT --url https://seller-vn.tiktok.com/ \
        --cookie-domain tiktok.com --shot /tmp/x.png --full-page
python3 hub_headless.py stop  --code NUMBER_REDACTED
```

Python 调用：

```python
from hub_headless import HubStudio, attach, attach_or_start

hub = HubStudio()

# 已在跑 → 复用(不会重启你正在用的窗口);没跑 → 无头起一个
with attach_or_start("NUMBER_REDACTED", headless=True) as p:
    p.navigate("https://seller-vn.tiktok.com/ads-creation/dashboard")
    print(p.title())
    print(len(p.cookies("tiktok.com")), "cookies")
    print(p.js("document.querySelector('h1')?.innerText"))
    p.screenshot("/tmp/dash.png", full_page=True)

hub.is_headless("NUMBER_REDACTED")   # True/False/None,判据是 CDP 的 HeadlessChrome
hub.running()                   # 所有运行中容器
hub.env_list(["NUMBER_REDACTED"])    # 跨分组查
```

设计要点：
- `start()` 默认**复用**正在运行的实例，不会先杀后起；要重启显式传 `force=True`。
- `attach()` 内部已处理 `suppress_origin=True`，不会再撞 403。
- 无头启动默认注入 `--window-size=1920,1080` + `--headless=new` 双保险。
- 所有 API 失败抛 `HubAPIError`，带原始 `code`/`msg`。

---

## 八、已知限制

1. `pageZoom` 需客户端 ≥3.46.0（本机 3.54.0 ✅）；`serialNumber` 需 ≥3.55.0（本机 3.54.0 ❌，本次用 `containerCode`）。
2. 无头 + `--headless=new` 双保险未做压力测试；本次单次启动 7.3s，`isHeadless` 单独即可生效。
3. 写操作（建广告 / 改库存）在无头下的端到端复现**未做** —— 需要真实写店铺，等你指定环境和操作再做。
4. `hubstudio-cli` 的 IPC socket（`/tmp/Hubstudio-cli`）本机不存在，`client_version()` 返回 None。CLI 随用随启，不影响 HTTP Local API 与 `hub_headless.py` 的任何功能。
5. 环境列表接口按登录分组返回；跨分组必须显式传 `containerCodes`，没有「列出全部组」的接口。
