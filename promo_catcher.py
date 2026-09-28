#!/usr/bin/env python3
"""促销 create/update 请求抓取器 —— 原始 websocket + 后台线程。

⚠️ 为什么不能用 Playwright 的 cdp.on() + cdp.send()（v1/v2 都栽在这）:
   Playwright 同步 API 的事件回调跑在它自己的 asyncio 事件循环里，
   在回调内调用 cdp.send("Fetch.continueRequest") 会抛 asyncio.CancelledError，
   请求永远得不到放行 → **整个页面被挂死**。
   operator 连续三次"提交没反应/像网络问题"，根因就是这个。

本版直接用 websocket-client 对每个 tab 建独立连接，在 daemon 线程里
收 Fetch.requestPaused 并立刻 continueRequest；主线程只负责发现新 tab 和收尾。
主线程与线程之间只通过文件/计数通信，不共享 Playwright 对象。

用法:
  python3 promo_catcher.py [--port CDP_PORT] [--seconds 1800] [--out notes/caught.jsonl]
"""
from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.request
from pathlib import Path

import websocket

HERE = Path(__file__).resolve().parent

PATTERNS = [{"urlPattern": pat, "requestStage": "Request"} for pat in (
    "*tiktokshopglobalselling.com/api/*create*",
    "*tiktokshopglobalselling.com/api/*update*",
    "*tiktokshopglobalselling.com/api/*submit*",
    "*tiktokshopglobalselling.com/api/v1/promotion/*",
)]


class TabCatcher(threading.Thread):
    """一条 tab 一条 websocket，事件循环跑在自己的线程里。"""

    def __init__(self, ws_url: str, tag: str, sink, counter, seen):
        super().__init__(daemon=True)
        self.ws_url, self.tag = ws_url, tag
        self.sink, self.counter, self.seen = sink, counter, seen
        self.ws = None
        self._id = 0
        self._lock = threading.Lock()

    def _send(self, method: str, params: dict) -> None:
        with self._lock:
            self._id += 1
            mid = self._id
        try:
            self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        except Exception:
            pass

    def run(self) -> None:
        try:
            self.ws = websocket.create_connection(self.ws_url, timeout=180,
                                                  suppress_origin=True)
        except Exception as e:
            print(f"  ✗ {self.tag}: ws 连接失败 {str(e)[:70]}", flush=True)
            return
        self._send("Fetch.enable", {"patterns": PATTERNS})
        print(f"  ✓ 已挂载 {self.tag}", flush=True)
        while True:
            try:
                raw = self.ws.recv()
            except Exception:
                break
            if not raw:
                break
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get("method") != "Fetch.requestPaused":
                continue
            p = msg.get("params") or {}
            rid = p.get("requestId")
            req = p.get("request") or {}
            try:
                if req.get("method") != "OPTIONS":
                    url = req.get("url", "")
                    rec = {"at": time.strftime("%H:%M:%S"), "tab": self.tag,
                           "method": req.get("method"),
                           "path": url.split("?")[0].split(".com")[-1],
                           "full_url": url, "body": req.get("postData"),
                           "body_entries": req.get("postDataEntries")}
                    self.sink.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    self.counter[0] += 1
                    print(f"\n★ [{rec['at']}] #{self.counter[0]} {rec['method']} {rec['path']}"
                          f"\n  body={len(rec['body'] or '')}B\n  {(rec['body'] or '')[:1500]}\n",
                          flush=True)
            except Exception as e:
                print("  记录异常:", str(e)[:90], flush=True)
            finally:
                # 必须立刻放行 —— 这是 v1/v2 的死因
                self._send("Fetch.continueRequest", {"requestId": rid})


def list_pages(port: int) -> list[dict]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=8) as f:
        return [t for t in json.load(f) if t.get("type") == "page"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=CDP_PORT)
    ap.add_argument("--seconds", type=int, default=1800)
    ap.add_argument("--out", default=str(HERE / "notes" / "caught.jsonl"))
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("")
    sink = out.open("a", buffering=1)
    counter = [0]
    seen: set[str] = set()

    def attach(url: str, tag: str) -> None:
        TabCatcher(url, tag, sink, counter, seen).start()

    # 初始挂载全部 tiktok 页面
    for t in list_pages(args.port):
        u = t.get("url") or ""
        if "tiktokshopglobalselling.com" not in u or not t.get("webSocketDebuggerUrl"):
            continue
        seen.add(t["id"])
        attach(t["webSocketDebuggerUrl"], u.split("/")[-1][:40] or t["id"][:8])

    print(f"\n监听中（{args.seconds}s）—— 每 3 秒扫描新 tab", flush=True)
    print(f"结果 → {out}\n", flush=True)

    deadline = time.time() + args.seconds
    try:
        while time.time() < deadline: CONTACT_REDACTED(3)
            try:
                for t in list_pages(args.port):
                    u = t.get("url") or ""
                    if t["id"] in seen or "tiktokshopglobalselling.com" not in u:
                        continue
                    if not t.get("webSocketDebuggerUrl"):
                        continue
                    seen.add(t["id"])
                    attach(t["webSocketDebuggerUrl"], (u.split("/")[-1][:40] or t["id"][:8]))
            except Exception as e:
                print("  扫描异常:", str(e)[:80], flush=True)
    except KeyboardInterrupt:
        print("\n手动停止", flush=True)
    finally:
        sink.close()
        print(f"结束：共捕获 {counter[0]} 条 → {out}", flush=True)


if __name__ == "__main__":
    main()
