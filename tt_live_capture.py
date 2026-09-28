#!/usr/bin/env python3
"""实时抓包服务 —— 挂在后台记录所有写请求，随时查询。

用法：
    python3 tt_live_capture.py                  # 前台跑（Ctrl-C 结束）
    python3 tt_live_capture.py --bg             # 后台跑，落盘 notes/tt_live_hits.jsonl
    python3 tt_live_capture.py --show           # 打印已抓到的
    python3 tt_live_capture.py --clear          # 清空

抓到的每条写入 notes/tt_live_hits.jsonl（一行一个 JSON），并实时打印。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hub_headless import CDPPage, cdp_get  # noqa: E402

PORT = int(os.environ.get("TT_CDP_PORT", "CDP_PORT"))
OUT = os.path.join(HERE, "notes", "tt_live_hits.jsonl")

# 只记这些（去掉读接口噪音）
SKIP = ("/list", "/count", "/check", "/progress", "/query_", "/get", "bs/rt", "prediction",
        "feature_control", "island/task", "grayscale", "feelgood", "newest_reply",
        "auth_token", "workbench", "/tab/", "/preload", "/regions", "/warehouses",
        "config_center", "monitor", "ticket")


def is_interesting(path: str, method: str, body: str) -> bool:
    if "/api/v1/" not in path:
        return False
    if method == "GET":
        return False
    if not body:
        return False
    return not any(s in path for s in SKIP)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.clear:
        open(OUT, "w").close()
        print("已清空", OUT)
        return 0
    if a.show:
        if not os.path.exists(OUT):
            print("(无记录)")
            return 0
        for line in open(OUT):
            try:
                h = json.loads(line)
            except json.JSONDecodeError:
                continue
            print(f"{h['t']}  {h['method']} {h['path']}")
            print(f"    {h['body'][:600]}")
        return 0

    ok, tabs = cdp_get(a.port, "/json/list")
    if not ok:
        print(f"CDP {a.port} 不可达", file=sys.stderr)
        return 2
    pages = [t for t in tabs if t.get("type") == "page"]
    if not pages:
        print("没有 page target", file=sys.stderr)
        return 2
    target = pages[0]

    pg = CDPPage(target["webSocketDebuggerUrl"], timeout=600)
    print(f"[live] 挂在 {target.get('url','')[:80]}")
    print(f"[live] 落盘 {OUT}")
    print("[live] 现在去界面上改库存/价格，这里会实时打印真实请求。Ctrl-C 结束。")
    print()

    pg.enable("Page")

    def on_paused(params):
        rid = params.get("requestId")
        try:
            rq = params.get("request", {})
            url = rq.get("url", "")
            path = url.split("?")[0].replace("https://seller-vn.tiktok.com", "")
            body = rq.get("postData", "") or ""
            m = rq.get("method", "")
            if is_interesting(path, m, body):
                rec = {"t": time.strftime("%H:%M:%S"), "method": m, "path": path,
                       "url": url, "body": body}
                with open(OUT, "a") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if not a.quiet:
                    print(f"[★ {rec['t']}] {m} {path}  ({len(body)}B)")
                    print(f"    {body[:700]}")
                    print()
        except Exception as e:  # noqa: BLE001
            print("[live] cb err", type(e).__name__, str(e)[:80])
        try:
            pg.send("Fetch.continueRequest", {"requestId": rid})
        except Exception:
            pass

    # CDP 事件需要同步读取 —— CDPPage.send 会把事件塞进 _events，这里改成阻塞监听
    pg.ws.settimeout(600)
    pg.send("Fetch.enable", {"patterns": [
        {"urlPattern": "*seller-vn.tiktok.com/api/*", "requestStage": "Request"}]})
    try:
        while True:
            try:
                msg = json.loads(pg.ws.recv())
            except Exception as e:  # noqa: BLE001
                print("[live] 连接断开:", type(e).__name__, str(e)[:80])
                break
            if msg.get("method") == "Fetch.requestPaused":
                on_paused(msg["params"])
    except KeyboardInterrupt:
        print("\n[live] 结束")
    finally:
        try:
            pg.send("Fetch.disable")
        except Exception:
            pass
        pg.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
