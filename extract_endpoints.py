#!/usr/bin/env python3
"""从 bundle.pretty.js 提取完整接口映射(backend / method / path / 前端函数名)。

bundle 结构:每个后端一个模块段,段首声明域名:
    getServersDomain$N = () => ({ prod: "https://<host>", ... })[env] + `/${prefix}`
段内统一用 axios 实例 `request`(默认 baseURL=前端域名),前缀变量在该段内赋值
(BASE_URL$N / domain$N)。

输出: adfly_api/spec/endpoints.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from backend_map import normalize_endpoints

HERE = Path(__file__).resolve().parent
BUNDLE = HERE / "code" / "v2" / "bundle.pretty.js"
OUT = HERE / "adfly_api" / "spec" / "endpoints.json"

# 段首行号 → (backend key, host)
SECTIONS = [
    (10028, "front", "front-v1.aiadfly.com"),
    (12512, "finance_bff", "finance-bff-v1.aiadfly.com"),
    (21118, "advertise", "advertise-bff-v1.aiadfly.com"),
    (41560, "automation", "automation-v1.aiadfly.com"),
    (42650, "ai_agent", "ai-agent-v1.aiadfly.com"),
    (48738, "mcp_open", "mcp-open.aiadfly.com"),
    (49806, "finance", "finance-v1.aiadfly.com"),
]

CALL_RE = re.compile(
    r"([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(?[^)\n]{0,70}\)?\s*=>\s*\n?\s*"
    r"request\s*\.\s*(get|post|put|delete|patch)\s*\(\s*([^\n]{0,320})"
)


def first_arg(arg: str) -> str:
    depth, quote, cut = 0, None, len(arg)
    for i, ch in enumerate(arg):
        if quote:
            if ch == quote and arg[i - 1] != "\\":
                quote = None
            continue
        if ch in "\"'`":
            quote = ch
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                cut = i
                break
            depth -= 1
        elif ch == "," and depth == 0:
            cut = i
            break
    return arg[:cut].strip()


def backend_of(line_no: int) -> str:
    key = SECTIONS[0][1]
    for start, k, _h in SECTIONS:
        if line_no >= start:
            key = k
        else:
            break
    return key


def main() -> None:
    text = BUNDLE.read_text(encoding="utf-8")
    rows, seen = [], set()
    for m in CALL_RE.finditer(text):
        fn, method, raw = m.group(1), m.group(2).upper(), m.group(3)
        line_no = text.count("\n", 0, m.start()) + 1
        arg = first_arg(raw)
        arg = re.sub(r"^(BASE_URL\$?[0-9A-Za-z_]*|domain\$?\d*|baseURL)\s*\+\s*", "", arg)
        arg = re.sub(r"\$\{[A-Za-z_$][\w$]*\}", "", arg)
        path = (re.search(r"[\"'`]([^\"'`]*)[\"'`]", arg) or [None, arg])[1] or ""
        path = path.replace("`", "").strip()
        if "+" in path:
            path = path.split("+")[0].strip()
        if not path.startswith("/"):
            path = "/" + path
        backend = backend_of(line_no)
        if "baseURL: r" in raw and "getServersDomain$3" in raw:
            backend = "advertise"
        key = (fn, method, path, backend)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"fn": fn, "method": method, "path": path, "backend": backend, "line": line_no})

    changed = normalize_endpoints(rows)
    print(f"\n归属纠正 {len(changed)} 条(段 → 真实组):")
    for fn, section, old, new in changed[:12]:
        print(f"  {fn:38} section={section:11} -> {new}")
    if len(changed) > 12:
        print(f"  … 另有 {len(changed)-12} 条")

    # 归属纠正后可能撞车(同一真实路径被两个段各定义一次),这里再去重。
    uniq: dict = {}
    aliases: dict = {}
    for r in rows:
        key = (r["backend"], r["method"], r["path"])
        if key in uniq:
            aliases.setdefault(key, []).append(r["fn"])
            continue
        uniq[key] = r
    dup = len(rows) - len(uniq)
    if dup:
        print(f"\n去重 {dup} 条(纠正归属后同路径重复):")
        for key, al in list(aliases.items())[:8]:
            print(f"  {key[1]} {key[2]:46} 别名 {al}")
    rows = list(uniq.values())
    for key, al in aliases.items():
        uniq[key]["aliases"] = al

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"接口总数: {len(rows)}")
    by: dict[str, int] = {}
    for r in rows:
        by[r["backend"]] = by.get(r["backend"], 0) + 1
    for k, v in sorted(by.items(), key=lambda x: -x[1]):
        print(f"  {k:12} {v:4}")
    print(f"\n写入 {OUT}")


if __name__ == "__main__":
    main()
