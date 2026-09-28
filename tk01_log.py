#!/usr/bin/env python3
"""运行日志 —— 每个写操作追加一条 `notes/runs.jsonl`。

之前跑完只有一堆 `notes/*.json` 快照，**查不到"这次邀约了谁、结果如何"**。
这个模块补上那条时间线：

```python
from tk01_log import log_run, tail

log_run("invite_group", target="7690…", ok=True,
        params={"n_creators": 10, "n_products": 3, "commission": 15},
        result={"plan_id": "7690…", "status": 2})
```

产物 `notes/runs.jsonl`，每行一条：

```json
{"ts": "2026-09-28T00:19:03", "epoch": 1790…, "shop": "tk01", "region": "VN",
 "action": "invite_group", "target": "7690…", "ok": true,
 "params": {…}, "result": {…}, "note": null}
```

查询：

```bash
python3 tk01_log.py tail -n 20
python3 tk01_log.py tail --action invite_group
python3 tk01_log.py stats
```
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG_FILE = HERE / "notes" / "runs.jsonl"

_MAX_FIELD = 1200          # 单字段截断，避免一行几 MB


def _shrink(v):
    """把值压到可落盘的规模（长字符串截断、深结构只留摘要）。"""
    if isinstance(v, str):
        return v if len(v) <= _MAX_FIELD else v[:_MAX_FIELD] + f"…(+{len(v)-_MAX_FIELD})"
    if isinstance(v, (int, float, bool)) or v is None:
        return v
    if isinstance(v, list):
        if len(v) > 30:
            return {"_list_len": len(v), "_head": [_shrink(x) for x in v[:5]]}
        return [_shrink(x) for x in v]
    if isinstance(v, dict):
        out = {}
        for k, x in list(v.items())[:40]:
            if k in ("raw", "creator_profile_list", "products", "record_list",
                     "invitation_list", "images", "avatar"):
                out[k] = f"<{type(x).__name__} len={len(x) if hasattr(x,'__len__') else '?'}>"
                continue
            out[k] = _shrink(x)
        return out
    return str(v)[:200]


def log_run(action: str, *, target=None, ok=None, params=None, result=None,
            note=None, shop: str | None = None, region: str | None = None) -> dict:
    """追加一条运行记录。返回写入的那条（方便断言/打印）。"""
    if shop is None or region is None:
        try:
            from tk01_config import active_name, REGION
            shop = shop or active_name()
            region = region or REGION
        except Exception:
            shop = shop or "?"
            region = region or "?"
    rec = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "epoch": int(time.time()),
        "shop": shop,
        "region": region,
        "action": action,
        "target": _shrink(target),
        "ok": ok,
        "params": _shrink(params) if params is not None else None,
        "result": _shrink(result) if result is not None else None,
        "note": note,
    }
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"    [log] 写入失败: {str(e)[:60]}", flush=True)
    return rec


def read_all() -> list[dict]:
    if not LOG_FILE.exists():
        return []
    out = []
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: CONTACT_REDACTED
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def tail(n: int = 20, action: str | None = None, only_fail: bool = False) -> list[dict]:
    rows = read_all()
    if action:
        rows = [r for r in rows if r.get("action") == action]
    if only_fail:
        rows = [r for r in rows if r.get("ok") is False]
    return rows[-n:]


def main() -> None:
    ap = argparse.ArgumentParser(description="运行日志查询")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("tail"); p.add_argument("-n", type=int, default=20)
    p.add_argument("--action"); p.add_argument("--fail", action="store_true")
    sub.add_parser("stats")
    sub.add_parser("path")
    a = ap.parse_args()

    if a.cmd == "path":
        print(LOG_FILE)
        return
    if a.cmd == "stats":
        rows = read_all()
        if not rows:
            print("  （还没有运行记录）")
            return
        by_action: dict[str, list] = {}
        for r in rows:
            by_action.setdefault(r.get("action") or "?", []).append(r)
        print(f"  共 {len(rows)} 条记录   "
              f"从 {rows[0].get('ts')} 到 {rows[-1].get('ts')}")
        for act, rs in sorted(by_action.items(), key=lambda x: -len(x[1])):
            ok = sum(1 for r in rs if r.get("ok"))
            bad = sum(1 for r in rs if r.get("ok") is False)
            print(f"    {act:24} {len(rs):>4} 次  成功 {ok:>4}  失败 {bad:>4}")
        return

    rows = tail(a.n, action=a.action, only_fail=a.fail)
    if not rows:
        print("  （没有匹配的记录）")
        return
    for r in rows:
        flag = "✓" if r.get("ok") else ("✗" if r.get("ok") is False else "·")
        p_ = r.get("params") or {}
        res = r.get("result") or {}
        brief = ""
        for k in ("plan_id", "id", "success_cnt", "n_creators", "n_chosen", "code"):
            if isinstance(res, dict) and res.get(k) is not None:
                brief += f" {k}={res[k]}"
        for k in ("name", "n_creators", "n_products", "commission", "page"):
            if isinstance(p_, dict) and p_.get(k) is not None:
                brief += f" {k}={p_[k]}"
        print(f"  {r.get('ts')} {flag} {str(r.get('action')):20} "
              f"{str(r.get('target'))[:22]:24}{brief[:110]}")


if __name__ == "__main__":
    main()
