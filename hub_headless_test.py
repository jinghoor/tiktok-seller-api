#!/usr/bin/env python3
"""Hub Studio 无头模式实测。

验证三件事:
  1. POST /api/v1/browser/start 接受 isHeadless 并真正生效(看内核进程命令行出现 --headless)
  2. 无头实例仍暴露 CDP /json/version,调试端口不变
  3. 无头实例的页面仍可读(导航 + DOM 抓取)

结束后删除测试环境,不留痕。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

LOCAL = "http://127.0.0.1:6873"
TEST_NAME = "ZZ-headless-probe"
TIMEOUT_START = 300


def api(path: str, body: dict | None = None, timeout: int = 60) -> dict:
    req = urllib.request.Request(
        LOCAL + path,
        data=json.dumps(body or {}).encode(),
        headers={"Content-Type": "application/json", "Accept-Language": "zh-CN"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def cdp_get(port: int, path: str, timeout: float = 4.0):
    """返回 (ok, 内容)。CDP 在 127.0.0.1 上无需鉴权。"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
            return True, json.loads(r.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        return False, str(e)


def pids_for_port(port: int) -> list[int]:
    """找监听该端口的进程 pid。"""
    out = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True, text=True,
    )
    return [int(x) for x in out.stdout.split() if x.strip().isdigit()]


def cmdline(pid: int) -> list[str]:
    out = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True)
    return out.stdout.split()


def has_gui_window(pid: int) -> bool:
    """用 Quartz 查该 pid 是否有窗口服务器窗口 —— 无头最硬的判据。"""
    script = f'''
import Quartz, sys
info = Quartz.CGWindowListCopyWindowInfo(
    Quartz.kCGWindowListOptionAll | Quartz.kCGWindowListExcludeDesktopElements,
    Quartz.kCGNullWindowID)
n = sum(1 for w in info if w.get('kCGWindowOwnerPID') == {pid})
print(n)
'''
    r = subprocess.run(["/usr/bin/python3", "-c", script], capture_output=True, text=True)
    if r.returncode != 0:
        return None  # pyobjc 不可用
    return int(r.stdout.strip() or 0)


def new_ports(before: set[int]) -> set[int]:
    out2 = subprocess.run(
        ["bash", "-c", "lsof -nP -iTCP -sTCP:LISTEN | awk '{print $9}' | sed 's/.*://' | sort -un"],
        capture_output=True, text=True,
    )
    ports = {int(x) for x in out2.stdout.split() if x.isdigit()}
    return ports - before


def main() -> int:
    report: dict = {"steps": []}

    def step(name: str, **kw):
        entry = {"step": name, **kw}
        report["steps"].append(entry)
        print(f"\n[STEP] {name}")
        for k, v in kw.items():
            print(f"   {k}: {v}")
        return entry

    # ---------- 0. 基线 ----------
    base = subprocess.run(
        ["bash", "-c", "lsof -nP -iTCP -sTCP:LISTEN | awk '{print $9}' | sed 's/.*://' | sort -un"],
        capture_output=True, text=True,
    )
    base_ports = {int(x) for x in base.stdout.split() if x.isdigit()}
    step("baseline", listening_ports=len(base_ports))

    # ---------- 1. 创建一次性测试环境 ----------
    created = api("/api/v1/env/create", {
        "containerName": TEST_NAME,
        "remark": "headless capability probe - safe to delete",
        "asDynamicType": 0,
        "proxyTypeName": "不使用代理",
        "type": "windows",
    }, timeout=90)
    step("env/create", resp=created)
    code = created.get("data")
    container_code = None
    if isinstance(code, dict):
        container_code = code.get("containerCode") or code.get("id")
    elif isinstance(code, (int, str)):
        container_code = code
    if not container_code:
        # 回退:按名字查列表
        lst = api("/api/v1/env/list", {})
        rows = lst.get("data", {}).get("list", []) if isinstance(lst.get("data"), dict) else []
        hit = [r for r in rows if r.get("containerName") == TEST_NAME]
        container_code = hit[0]["containerCode"] if hit else None
    step("resolve containerCode", container_code=container_code)
    if not container_code:
        print("!! 无法取得 containerCode,终止")
        return 2

    container_code = str(container_code)
    started_pid = None
    debug_port = None
    try:
        # ---------- 2. 无头启动 ----------
        t0 = time.time()
        st = api("/api/v1/browser/start", {
            "containerCode": container_code,
            "isHeadless": True,
            "containerTabs": ["about:blank"],
            "skipSystemResourceCheck": True,
        }, timeout=TIMEOUT_START)
        step("browser/start (isHeadless=true)", elapsed=round(time.time() - t0, 1), resp=st)

        data = st.get("data") or {}
        started_pid = data.get("pid")
        debug_port = data.get("debuggingPort") or data.get("debugPort") or data.get("port")

        # 端口兜底:对比基线找出新监听端口
        if not debug_port:
            time.sleep(2)
            cand = new_ports(base_ports)
            step("new listening ports", ports=sorted(cand))
            # 逐个试 CDP
            for p in sorted(cand):
                ok, ver = cdp_get(p, "/json/version")
                if ok:
                    debug_port = p
                    step("CDP found on new port", port=p, browser=ver.get("Browser"))
                    break

        # ---------- 3. 进程标志验证 ----------
        time.sleep(2)
        if debug_port:
            pids = pids_for_port(debug_port)
        else:
            pids = [started_pid] if started_pid else []
        for pid in pids:
            if not pid:
                continue
            args = cmdline(pid)
            hl = [a for a in args if "headless" in a.lower()]
            step("process args", pid=pid, headless_flags=hl,
                 ua_lang=[a for a in args if "AppleLanguages" in a or a in ("(en)", "(zh-CN)")][:2],
                 gui_windows=has_gui_window(pid))

        # ---------- 4. CDP 可连 + 页面可读 ----------
        if debug_port:
            ok, ver = cdp_get(debug_port, "/json/version")
            step("CDP /json/version", ok=ok, value=ver)
            ok2, tabs = cdp_get(debug_port, "/json/list")
            step("CDP /json/list", ok=ok2,
                 tab_count=len(tabs) if isinstance(tabs, list) else None,
                 tabs=[{k: t.get(k) for k in ("type", "title", "url")} for t in (tabs or [])][:5])

            # WebSocket 驱动:导航 + 读 DOM + 执行 JS
            try:
                import websocket  # websocket-client
            except ImportError:
                step("websocket", available=False,
                     note="pip install websocket-client")
            else:
                ws_url = None
                if isinstance(tabs, list):
                    for t in tabs:
                        if t.get("type") == "page":
                            ws_url = t.get("webSocketDebuggerUrl")
                            break
                if not ws_url:
                    step("websocket", available=True, ws_url=None, note="无 page target")
                else:
                    # CDP 会拒绝带 Origin 的 WS 握手;websocket-client 默认塞 Origin,这里显式抑制
                    ws = websocket.create_connection(
                        ws_url, timeout=20, suppress_origin=True, max_size=None)
                    seq = [0]

                    def send(method, params=None, timeout_s=25):
                        seq[0] += 1
                        ws.send(json.dumps({"id": seq[0], "method": method, "params": params or {}}))
                        ws.settimeout(timeout_s)
                        while True:
                            msg = json.loads(ws.recv())
                            if msg.get("id") == seq[0]:
                                return msg

                    ver_r = send("Runtime.evaluate", {
                        "expression": "JSON.stringify({ua:navigator.userAgent,"
                                      "headless:/Headless/i.test(navigator.userAgent),"
                                      "w:innerWidth,h:innerHeight,"
                                      "webdriver:navigator.webdriver})",
                        "returnByValue": True,
                    })
                    step("Runtime.evaluate (blank page)",
                         result=ver_r.get("result", {}).get("result", {}).get("value"))

                    nav = send("Page.navigate", {"url": "https://example.com/"})
                    step("Page.navigate", result=nav.get("result", {}))
                    time.sleep(3)
                    dom = send("Runtime.evaluate", {
                        "expression": "document.title + ' | ' + (document.querySelector('h1')?.innerText || '')",
                        "returnByValue": True,
                    })
                    step("read DOM after navigate",
                         value=dom.get("result", {}).get("result", {}).get("value"))

                    shot = send("Page.captureScreenshot", {"format": "png"})
                    b64 = shot.get("result", {}).get("data") or ""
                    step("Page.captureScreenshot", bytes=len(b64) * 3 // 4)
                    if b64:
                        import base64
                        with open("/tmp/hub_headless_shot.png", "wb") as f:
                            f.write(base64.b64decode(b64))
                        print("   saved: /tmp/hub_headless_shot.png")
                    ws.close()

            # 落地 CDP 端口映射,便于后续 selenimum / puppeteer 接入
            with open("/tmp/hub_headless_result.json", "w") as f:
                json.dump({"containerCode": container_code, "debuggingPort": debug_port,
                           "pid": started_pid}, f, indent=2)
    finally:
        # ---------- 5. 清理 ----------
        if debug_port or started_pid:
            stop = api("/api/v1/browser/stop", {"containerCode": container_code}, timeout=120)
            step("browser/stop", resp=stop)
        time.sleep(2)
        dele = api("/api/v1/env/del", {"containerCodes": [container_code]}, timeout=90)
        if dele.get("code") not in (0, "0"):
            dele = api("/api/v1/env/del", {"containerCode": container_code}, timeout=90)
        step("env/del", resp=dele)
        report["cdp"] = {"debuggingPort": debug_port, "pid": started_pid}

    print("\n" + "=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2)[:6000])
    with open("/tmp/hub_headless_report.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
