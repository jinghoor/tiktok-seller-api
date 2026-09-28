#!/usr/bin/env python3
"""在 discount/create 页面点「同意并发布」，用 Playwright 的请求监听抓 discount/create 的完整 body。

为什么用 Playwright page.on("request") 而不是注 JS hook:
  Page.addScriptToEvaluateOnNewDocument 注册的脚本绑定在 CDP session 上，
  python 一退出连接就断，脚本随之被移除 —— 上次就是这样丢掉 payload 的。
  Playwright 的 request.post_data 在网络层拿,不受页面上下文/导航影响。

前置条件: 页面上已选好折扣类型 + 商品 + 折扣值(由 pw_s*.py 步骤完成)。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402

PORT = "http://127.0.0.1:CDP_PORT"
OUT = Path(__file__).resolve().parent / "notes" / "promo_create_payload.json"

captured: list[dict] = []


def main() -> None:
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(PORT)
        page = next(x for x in b.contexts[0].pages if "discount/create" in x.url)

        def on_request(req):
            u = req.url
            if "/api/v1/promotion/" not in u and "/promotion/" not in u:
                return
            if req.method in ("OPTIONS",):
                return
            captured.append({"method": req.method, "url": u,
                             "path": u.split("?")[0].split(".com")[-1],
                             "body": req.post_data})

        def on_response(res):
            for c in captured:
                if c.get("url") == res.url and "status" not in c:
                    c["status"] = res.status
                    try:
                        c["resp"] = res.text()[:3000]
                    except Exception:
                        pass

        page.on("request", on_request)
        page.on("response", on_response)

        # 提交前基线
        print("提交前 URL:", page.url[:100])
        btn = page.locator("button", has_text="同意并发布").first
        print("按钮 disabled:", btn.is_disabled())
        btn.click()
        print("已点击「同意并发布」，等待…")

        for i in range(20):
            time.sleep(1)
            if any("create" in (c.get("path") or "") for c in captured):
                time.sleep(2.5)
                break
            try:
                if "management" in page.url:
                    break
            except Exception:
                pass

        print(f"\n=== 捕获 {len(captured)} 条 promotion 请求 ===")
        for c in captured:
            print(f"  [{c.get('status')}] {c['method']:5} {c['path'][:80]}  body={len(c.get('body') or '')}")

        creates = [c for c in captured if (c.get("path") or "").endswith("/discount/create")]
        if creates:
            c = creates[-1]
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(json.dumps(
                {"path": c["path"], "method": c["method"],
                 "body_raw": c.get("body"),
                 "body": json.loads(c["body"]) if (c.get("body") or "").startswith(("{", "[")) else None,
                 "resp": c.get("resp"),
                 "all_requests": captured}, ensure_ascii=False, indent=2))
            print(f"\n=== discount/create payload → {OUT} ===")
            print("REQ :", (c.get("body") or "")[:2500])
            print("RESP:", (c.get("resp") or "")[:900])
        else:
            print("\n没有捕获到 discount/create —— 检查页面是否报校验错误")
            print("页面文本尾部:", page.evaluate("document.body.innerText.slice(-600)"))

        # 结束后顺手把 hook hits 也存一份(若该 tab 恰好有)
        print("\n最终 URL:", page.url[:110])


if __name__ == "__main__":
    main()
