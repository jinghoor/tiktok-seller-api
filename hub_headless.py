#!/usr/bin/env python3
"""Hub Studio 无头客户端。

把「启动无头环境 → 接 CDP → 读页面 / 执行 JS / 抓 XHR」收敛成几行调用。

    from hub_headless import HubStudio, attach_or_start

    hub = HubStudio()
    port = hub.start("NUMBER_REDACTED", headless=True, window="1920,1080")   # SHOP_LOCAL
    with attach_or_start(port) as page:
        page.navigate("https://seller-vn.tiktok.com/")
        print(page.text("h1"))
        print(page.js("document.cookie.length"))

CLI:

    python3 hub_headless.py list
    python3 hub_headless.py start --code NUMBER_REDACTED [--headful] [--window 1920,1080]
    python3 hub_headless.py eval   --port 62972 --js "document.title"
    python3 hub_headless.py grab   --port 62972 --url https://seller-vn.tiktok.com/
    python3 hub_headless.py stop   --code NUMBER_REDACTED
    python3 hub_headless.py doctor            # 环境自检

已知限制写在 HUBSTUDIO_HEADLESS.md。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from typing import Any, Iterator

LOCAL_API = "http://127.0.0.1:6873"
DEFAULT_TIMEOUT = 45
START_TIMEOUT = 300


class HubAPIError(RuntimeError):
    def __init__(self, path: str, resp: dict):
        self.path = path
        self.resp = resp
        super().__init__(f"{path} -> code={resp.get('code')} msg={resp.get('msg') or resp.get('_raw')}")


class HubStudio:
    """Hub Studio Local API 客户端。安全校验关闭时不需要 Authorization 头。"""

    def __init__(self, base: str = LOCAL_API, api_key: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base = base.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def call(self, path: str, body: dict | None = None, *, timeout: int | None = None,
             raw: bool = False) -> dict:
        headers = {"Content-Type": "application/json", "Accept-Language": "zh-CN"}
        if self.api_key:
            # 客户端「安全校验」开启时才需要,值取自本地 localstorage 的 localApiKey
            headers["Authorization"] = self.api_key
        req = urllib.request.Request(
            self.base + path, data=json.dumps(body or {}).encode(),
            headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                text = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            raise HubAPIError(path, {"code": e.code, "_raw": e.read().decode("utf-8", "replace")[:400]}) from e
        except urllib.error.URLError as e:
            raise HubAPIError(path, {"code": "NETWORK", "_raw": str(e.reason)}) from e
        try:
            resp = json.loads(text)
        except json.JSONDecodeError:
            resp = {"_raw": text[:800]}
        if raw:
            return resp
        if str(resp.get("code")) not in ("0", "None"):
            raise HubAPIError(path, resp)
        return resp

    # ---------- 环境管理 ----------

    def env_list(self, container_codes: list[str] | None = None) -> list[dict]:
        """不带 containerCodes 只返回当前登录分组;带上可跨分组查。"""
        body = {"containerCodes": container_codes} if container_codes else {}
        d = self.call("/api/v1/env/list", body).get("data")
        if isinstance(d, dict):
            return d.get("list") or []
        return d or []

    def env_create(self, name: str, **kw) -> str:
        body = {"containerName": name, "asDynamicType": 0, "proxyTypeName": "不使用代理", **kw}
        return str(self.call("/api/v1/env/create", body, timeout=120)["data"]["containerCode"])

    def env_del(self, *codes: str) -> dict:
        return self.call("/api/v1/env/del", {"containerCodes": list(codes)}, timeout=90)

    def resolve(self, key: str) -> tuple[str, str]:
        """接受 containerCode 或环境名(或名字片段),返回 (containerCode, containerName)。"""
        key = str(key)
        try:
            rows = self.env_list([key])
            if rows:
                return str(rows[0]["containerCode"]), rows[0].get("containerName") or ""
        except HubAPIError:
            pass
        # 名称查找:先当前分组,失败再退化为直接用 key 当 code
        try:
            for r in self.env_list():
                if key in (r.get("containerName") or ""):
                    return str(r["containerCode"]), r.get("containerName") or ""
        except HubAPIError:
            pass
        return key, key

    # ---------- 浏览器 ----------

    def running(self) -> list[dict]:
        d = self.call("/api/v1/browser/all-browser-status", {}).get("data") or {}
        return d.get("containers") or []

    def find_running(self, code: str) -> dict | None:
        code = str(code)
        for c in self.running():
            if str(c.get("containerCode")) == code:
                return c
        return None

    def start(self, code: str, *, headless: bool = True, window: str | None = "1920,1080",
              tabs: list[str] | None = None, args: list[str] | None = None,
              cdp_hide: bool = False, read_only: bool = False,
              skip_resource_check: bool = True, page_zoom: float | None = None,
              force: bool = False) -> dict:
        """启动环境,返回 start 响应 data(含 debuggingPort)。

        已在运行时默认直接返回该实例的 CDP 端口,不重启 —— 重启会杀掉你正在用的窗口。
        """
        code, name = self.resolve(code)
        existing = self.find_running(code)
        if existing and not force:
            # 已在跑:探测它的 CDP 端口,复用
            port = _probe_cdp_for_pid(existing.get("pid"))
            if port:
                return {"containerCode": code, "containerName": name, "debuggingPort": str(port),
                        "pid": existing.get("pid"), "reused": True}
            raise HubAPIError("/api/v1/browser/start",
                              {"code": "RUNNING_NO_CDP",
                               "_raw": f"环境已在运行(pid={existing.get('pid')})但未暴露 CDP 端口;"
                                       f"加 force=True 强制重启"})

        body: dict[str, Any] = {
            "containerCode": code,
            "isHeadless": bool(headless),
            "skipSystemResourceCheck": bool(skip_resource_check),
        }
        if tabs:
            body["containerTabs"] = tabs
        merged_args = list(args or [])
        if window:
            merged_args.append(f"--window-size={window}")
        if headless and merged_args:
            # 内核 Headless 走 JSON 配置,这里的 --headless=new 只是双保险
            if not any(a.startswith("--headless") for a in merged_args):
                merged_args.append("--headless=new")
        if merged_args:
            body["args"] = merged_args
        if cdp_hide:
            body["cdpHide"] = True
        if read_only:
            body["isWebDriverReadOnlyMode"] = True
        if page_zoom is not None:
            body["pageZoom"] = page_zoom

        resp = self.call("/api/v1/browser/start", body, timeout=START_TIMEOUT)
        data = dict(resp.get("data") or {})
        data.setdefault("containerCode", code)
        data["containerName"] = name
        data["reused"] = False
        return data

    def stop(self, code: str) -> dict:
        code, _ = self.resolve(code)
        return self.call("/api/v1/browser/stop", {"containerCode": code}, timeout=120)

    def stop_all(self, clear_queue: bool = True) -> dict:
        return self.call("/api/v1/browser/stop-all", {"clearQueue": clear_queue}, timeout=180)

    def foreground(self, code: str) -> dict:
        code, _ = self.resolve(code)
        return self.call("/api/v1/browser/foreground", {"containerCode": code})

    def arrange(self, **kw) -> dict:
        return self.call("/api/v1/browser/arrange", kw)

    def is_headless(self, code: str) -> bool | None:
        """真无头判据:CDP 回报的 User-Agent 里是否含 HeadlessChrome。"""
        code, _ = self.resolve(code)
        c = self.find_running(code)
        if not c:
            return None
        port = _probe_cdp_for_pid(c.get("pid"))
        if not port:
            return None
        ok, ver = cdp_get(port, "/json/version")
        if not ok:
            return None
        return "HeadlessChrome" in (ver.get("User-Agent") or "")


# ---------- CDP 底层 ----------

def _listening_ports(pid: int) -> set[int]:
    import subprocess
    out = subprocess.run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-a", "-p", str(pid), "-Fn"],
                         capture_output=True, text=True).stdout
    return {int(line[1:].rsplit(":", 1)[1]) for line in out.splitlines()
            if line.startswith("n") and ":" in line and line[1:].rsplit(":", 1)[1].isdigit()}


def _probe_cdp_for_pid(pid: int | str | None) -> int | None:
    """在进程的监听端口里找哪个是 Chrome DevTools。"""
    if not pid:
        return None
    for p in sorted(_listening_ports(int(pid))):
        ok, ver = cdp_get(p, "/json/version")
        if ok and "Browser" in (ver or {}):
            return p
    return None


def cdp_get(port: int | str, path: str, timeout: float = 4.0) -> tuple[bool, Any]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
            return True, json.loads(r.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        return False, str(e)


class CDPPage:
    """极简 CDP 会话。仅依赖 websocket-client。"""

    def __init__(self, ws_url: str, timeout: float = 180.0):
        try:
            import websocket  # websocket-client
        except ImportError as e:
            raise RuntimeError("需要 websocket-client: python3 -m pip install websocket-client") from e
        self._ws_mod = websocket
        self.ws_url = ws_url
        # suppress_origin 必须为 True:CDP 会拒绝带 Origin 的握手(403)
        self.ws = websocket.create_connection(ws_url, timeout=timeout,
                                             suppress_origin=True, max_size=None)
        self._id = 0
        self._events: list[dict] = []
        self.timeout = timeout
        self._reconnects = 0

    def _reconnect(self) -> None:
        """浏览器会周期性踢掉空闲 CDP 连接（回放/长任务里必现）。
        重连后 CDP 会话状态（已 enable 的域、注入脚本）会重置，
        所以调用方若依赖这些状态需要自己重新 setup。

        注意：create_connection 必须显式传 timeout —— 否则底层 socket
        在某些网络状态下会无限阻塞，表现就是整个脚本静默挂死。
        """
        try:
            self.ws.close()
        except Exception:
            pass
        last = None
        for attempt in range(3):
            try:
                self.ws = self._ws_mod.create_connection(
                    self.ws_url, timeout=min(self.timeout, 30.0),
                    suppress_origin=True, max_size=None)
                self._reconnects += 1
                return
            except Exception as e:
                last = e
                time.sleep(0.6 * (attempt + 1))
        raise RuntimeError(f"CDP 重连失败: {last}")

    def send(self, method: str, params: dict | None = None, timeout: float | None = None,
             *, _retry: bool = True, _watchdog: int = 0) -> dict:
        """带硬超时看门狗。

        websocket 的 settimeout 在 TLS 层读阻塞时**不生效**，一旦浏览器侧
        的 Runtime.evaluate 永不返回（页面 fetch 卡住时会出现），
        recv() 会无限阻塞，整个脚本静默挂死。
        用 SIGALRM 兜一层：超时就抛异常让上层重连/放弃，
        比永远挂着好（后台任务里挂死最难排查）。
        """
        import signal
        if _watchdog == 0:
            _watchdog = int(timeout or self.timeout) + 20

        def _alarm(signum, frame):
            raise TimeoutError(f"CDP {method} 硬超时 {_watchdog}s（socket 层未响应）")

        old = None
        armed = False
        try:
            old = signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(_watchdog)
            armed = True
        except (ValueError, OSError):
            # 非主线程无法装信号处理器，退化为纯 socket 超时
            pass

        try:
            return self._send_once(method, params, timeout, _retry)
        finally:
            if armed:
                try:
                    signal.alarm(0)
                    if old is not None:
                        signal.signal(signal.SIGALRM, old)
                except (ValueError, OSError):
                    pass

    def _send_once(self, method: str, params: dict | None, timeout: float | None,
                   _retry: bool) -> dict:
        self._id += 1
        mid = self._id
        try:
            self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            self.ws.settimeout(timeout or self.timeout)
            while True:
                msg = json.loads(self.ws.recv())
                if msg.get("id") == mid:
                    if "error" in msg:
                        raise RuntimeError(f"{method}: {msg['error']}")
                    return msg.get("result", {})
                if "method" in msg:
                    self._events.append(msg)
        except (self._ws_mod.WebSocketTimeoutException,
                self._ws_mod.WebSocketConnectionClosedException,
                ConnectionResetError, BrokenPipeError, OSError) as e:
            if not _retry:
                raise
            self._reconnect()
            return self._send_once(method, params, timeout, False)

    def add_init_script(self, source: str) -> str:
        """在任何页面 JS 之前注入。跨导航存活,SPA 路由切换也覆盖。

        这是抓 XHR 的正确做法 —— 直接 Runtime.evaluate 注入会被下一次导航冲掉。
        """
        r = self.send("Page.addScriptToEvaluateOnNewDocument", {"source": source})
        return r.get("identifier", "")

    def remove_init_script(self, identifier: str) -> None:
        if identifier:
            self.send("Page.removeScriptToEvaluateOnNewDocument", {"identifier": identifier})

    def enable(self, *domains: str) -> None:
        for d in domains:
            self.send(f"{d}.enable")

    def js(self, expression: str, *, await_promise: bool = False, timeout: float | None = None) -> Any:
        r = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
        }, timeout=timeout)
        res = r.get("result", {})
        if r.get("exceptionDetails"):
            raise RuntimeError(f"JS 异常: {r['exceptionDetails'].get('text')} "
                               f"{(r['exceptionDetails'].get('exception') or {}).get('description', '')[:300]}")
        return res.get("value")

    def navigate(self, url: str, wait: float | None = 3.0) -> dict:
        r = self.send("Page.navigate", {"url": url})
        if wait:
            time.sleep(wait)
        return r

    def url(self) -> str:
        return self.js("location.href")

    def title(self) -> str:
        return self.js("document.title")

    def text(self, selector: str) -> str | None:
        return self.js(f"document.querySelector({json.dumps(selector)})?.innerText ?? null")

    def html(self, selector: str = "html") -> str | None:
        return self.js(f"document.querySelector({json.dumps(selector)})?.outerHTML ?? null")

    def cookies(self, domain_filter: str | None = None) -> list[dict]:
        r = self.send("Network.getAllCookies")
        items = r.get("cookies", [])
        if domain_filter:
            items = [c for c in items if domain_filter in (c.get("domain") or "")]
        return items

    def screenshot(self, path: str, *, full_page: bool = False, fmt: str = "png") -> str:
        import base64
        params: dict[str, Any] = {"format": fmt, "captureBeyondViewport": full_page}
        if full_page:
            m = self.send("Page.getLayoutMetrics")
            cs = m.get("cssContentSize") or m.get("contentSize") or {}
            if cs.get("width") and cs.get("height"):
                params["clip"] = {"x": 0, "y": 0, "width": cs["width"],
                                  "height": min(cs["height"], 20000), "scale": 1}
        data = self.send("Page.captureScreenshot", params).get("data") or ""
        with open(path, "wb") as f:
            f.write(base64.b64decode(data))
        return path

    def user_agent(self) -> str:
        return self.js("navigator.userAgent")

    def is_headless_js(self) -> bool:
        return bool(self.js("/Headless/i.test(navigator.userAgent)"))

    def goto_cdp_url(self) -> None:
        raise NotImplementedError("版本查询走 HTTP GET /json/version,不走 CDP")

    def close(self) -> None:
        try:
            self.ws.close()
        except Exception:
            pass

    def __enter__(self) -> "CDPPage":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def pages(port: int | str, *, poke_when_empty: bool = True) -> list[dict]:
    """列出 page 类型 target。无头刚起来可能只有 about:blank,仍算 page。"""
    ok, tabs = cdp_get(port, "/json/list")
    if not ok:
        raise RuntimeError(f"CDP {port} 不可达: {tabs}")
    out = [t for t in tabs if t.get("type") == "page"]
    if not out and poke_when_empty:
        # 用 /json/new 造一个(老版本用 PUT)
        for method in ("PUT", "GET"):
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method=method)
                with urllib.request.urlopen(req, timeout=5) as r:
                    out.append(json.loads(r.read().decode()))
                break
            except Exception:
                continue
    return out


@contextmanager
def attach(port: int | str, index: int = 0, enable: tuple[str, ...] = ("Page", "Runtime", "Network")) -> Iterator[CDPPage]:
    """连上某个环境的页面 target。"""
    tg = pages(port)
    if not tg:
        raise RuntimeError(f"CDP {port} 没有 page target")
    page = CDPPage(tg[index]["webSocketDebuggerUrl"])
    try:
        if enable:
            page.enable(*enable)
        yield page
    finally:
        page.close()


@contextmanager
def attach_or_start(target: str, *, headless: bool = True, hub: HubStudio | None = None,
                    window: str | None = "1920,1080", **start_kw) -> Iterator[CDPPage]:
    """target 可以是 containerCode 或环境名片段;已在跑就复用,没跑就无头起一个。"""
    hub = hub or HubStudio()
    data = hub.start(target, headless=headless, window=window, **start_kw)
    port = data.get("debuggingPort")
    if not port:
        raise RuntimeError(f"未取到 debuggingPort: {data}")
    with attach(port) as page:
        page.hub_info = data  # type: ignore[attr-defined]
        yield page


# ---------- CLI ----------

def _cmd_list(hub: HubStudio, a) -> int:
    running = {str(c["containerCode"]): c for c in hub.running()}
    rows = hub.env_list()
    if not rows:
        print("(当前分组无环境)")
    print(f"{'containerCode':>13} {'serial':>6}  {'状态':<8} {'CDP':>6}  name")
    for r in sorted(rows, key=lambda x: x.get("serialNumber") or 0):
        code = str(r["containerCode"])
        run = running.get(code)
        pid = run.get("pid") if run else None
        port = _probe_cdp_for_pid(pid) if pid else None
        state = "运行中" if run else "-"
        print(f"{code:>13} {str(r.get('serialNumber') or ''):>6}  {state:<8} "
              f"{str(port or ''):>6}  {r.get('containerName')}")
    extra = [c for code, c in running.items() if code not in {str(r['containerCode']) for r in rows}]
    if extra:
        print("\n其他分组运行中:")
        for c in extra:
            port = _probe_cdp_for_pid(c.get("pid"))
            print(f"{c['containerCode']:>13} {'':>6}  {'运行中':<8} {str(port or ''):>6}")
    return 0


def _cmd_start(hub: HubStudio, a) -> int:
    d = hub.start(a.code, headless=not a.headful, window=a.window, read_only=a.read_only,
                  skip_resource_check=not a.strict, force=a.force,
                  tabs=[a.url] if a.url else None)
    port = d.get("debuggingPort")
    name = d.get("containerName") or ""
    tag = "复用" if d.get("reused") else ("无头" if not a.headful else "有头")
    print(f"[{tag}] {d.get('containerCode')} {name}  CDP={port}  pid={d.get('pid')}")
    if a.verify and port:
        ok, ver = cdp_get(port, "/json/version")
        hl = "HeadlessChrome" in ((ver or {}).get("User-Agent") or "") if ok else None
        print(f"  CDP OK={ok}  无头={hl}  Browser={(ver or {}).get('Browser')}")
        if ok:
            print(f"  UA={ver.get('User-Agent')}")
    return 0


def _cmd_eval(hub: HubStudio, a) -> int:
    with attach(a.port) as p:
        print(json.dumps(p.js(a.js), ensure_ascii=False, indent=2))
    return 0


def _cmd_grab(hub: HubStudio, a) -> int:
    with attach(a.port) as p:
        if a.url:
            p.navigate(a.url, wait=a.wait)
        print("url:  ", p.url())
        print("title:", p.title())
        print("ua:   ", p.user_agent(), f"(JS 层无头={p.is_headless_js()})")
        ck = p.cookies(a.cookie_domain)
        print(f"cookies({a.cookie_domain or 'all'}): {len(ck)}")
        if a.js:
            print("js:   ", json.dumps(p.js(a.js), ensure_ascii=False))
        if a.shot:
            print("shot: ", p.screenshot(a.shot, full_page=a.full_page))
    return 0


def _cmd_stop(hub: HubStudio, a) -> int:
    print(json.dumps(hub.stop(a.code), ensure_ascii=False))
    return 0


def client_version(timeout: float = 5.0) -> dict | None:
    """客户端版本走本地 IPC socket(macOS/Linux: /tmp/Hubstudio-cli),不是 HTTP。

    IPC 上每行一个 JSON 请求/响应。
    """
    import os
    import socket as _s
    path = os.environ.get("HUBSTUDIO_CLI_SOCKET", "/tmp/Hubstudio-cli")
    if not os.path.exists(path):
        return None
    try:
        s = _s.socket(_s.AF_UNIX, _s.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect(path)
        s.sendall(b'{"action":"clientVersion"}\n')
        buf = b""
        while b"\n" not in buf and len(buf) < 65536:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
        s.close()
        line = buf.decode("utf-8", "replace").splitlines()
        for ln in line:
            try:
                return json.loads(ln)
            except json.JSONDecodeError:
                continue
    except OSError:
        return None
    return None


def _cmd_doctor(hub: HubStudio, a) -> int:
    print(f"Local API {hub.base}")
    cv = client_version()
    print("  客户端版本(IPC):", json.dumps(cv, ensure_ascii=False) if cv else "IPC 不可达/格式未知")
    try:
        rows = hub.env_list()
        print(f"  环境(当前分组): {len(rows)}")
    except HubAPIError as e:
        print("  env/list 失败:", e)
    run = hub.running()
    print(f"  运行中: {len(run)}")
    for c in run:
        port = _probe_cdp_for_pid(c.get("pid"))
        hl = None
        if port:
            ok, ver = cdp_get(port, "/json/version")
            hl = "HeadlessChrome" in ((ver or {}).get("User-Agent") or "") if ok else None
        print(f"    {c['containerCode']} pid={c.get('pid')} CDP={port} 无头={hl}")
    try:
        import websocket  # noqa: F401
        print("  websocket-client: OK")
    except ImportError:
        print("  websocket-client: 缺失 → python3 -m pip install websocket-client")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Hub Studio 无头客户端")
    ap.add_argument("--base", default=LOCAL_API)
    ap.add_argument("--api-key", default=None, help="客户端开启安全校验时才需要")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列环境 + 运行状态 + CDP 端口").set_defaults(func=_cmd_list)

    s = sub.add_parser("start", help="启动环境")
    s.add_argument("--code", required=True, help="containerCode 或环境名片段")
    s.add_argument("--headful", action="store_true", help="有头模式(默认无头)")
    s.add_argument("--window", default="1920,1080", help="--window-size,传空字符串禁用")
    s.add_argument("--url", default=None, help="启动时打开的 URL")
    s.add_argument("--read-only", action="store_true", help="不写 cookie 等数据")
    s.add_argument("--strict", action="store_true", help="不跳过系统资源检测")
    s.add_argument("--force", action="store_true", help="已在运行时强制重启")
    s.add_argument("--verify", action="store_true", help="启动后核验 CDP 与无头状态")
    s.set_defaults(func=_cmd_start)

    e = sub.add_parser("eval", help="在页面里跑 JS")
    e.add_argument("--port", required=True, type=int)
    e.add_argument("--js", required=True)
    e.set_defaults(func=_cmd_eval)

    g = sub.add_parser("grab", help="抓页面信息(cookie/title/DOM/截图)")
    g.add_argument("--port", required=True, type=int)
    g.add_argument("--url", default=None)
    g.add_argument("--wait", type=float, default=4.0)
    g.add_argument("--js", default=None, help="额外执行的 JS")
    g.add_argument("--cookie-domain", default=None, help="只看某个域的 cookie,例 tiktok.com")
    g.add_argument("--shot", default=None, help="截图保存路径")
    g.add_argument("--full-page", action="store_true")
    g.set_defaults(func=_cmd_grab)

    st = sub.add_parser("stop", help="关闭环境")
    st.add_argument("--code", required=True)
    st.set_defaults(func=_cmd_stop)

    sub.add_parser("doctor", help="环境自检").set_defaults(func=_cmd_doctor)

    a = ap.parse_args(argv)
    hub = HubStudio(a.base, a.api_key)
    try:
        return a.func(hub, a)
    except HubAPIError as e:
        print(f"API 错误: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
