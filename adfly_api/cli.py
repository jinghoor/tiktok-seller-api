#!/usr/bin/env python3
"""adfly_api 命令行入口。

    python -m adfly_api login  --account PHONE_REDACTED [--password ...]
    python -m adfly_api me
    python -m adfly_api token  --company <company_ex_id>
    python -m adfly_api list   [--backend advertise] [--grep gmv]
    python -m adfly_api call   <backend> <METHOD> <path> [json_body]
    python -m adfly_api raw    <backend> <METHOD> <path> [json_body]

密码优先从环境变量 ADFLY_PASSWORD 或交互式隐藏输入读取,避免落进 shell history。
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adfly_api import AdflyClient  # noqa: E402
from adfly_api.spec import load_endpoints  # noqa: E402
from adfly_api.transport import AdflyAuthError, AdflyError  # noqa: E402


def _client(args: argparse.Namespace) -> AdflyClient:
    return AdflyClient(env=args.env, state_path=Path(args.state).expanduser(), verbose=args.verbose)


def cmd_login(args: argparse.Namespace) -> int:
    pwd = args.password or os.environ.get("ADFLY_PASSWORD") or getpass.getpass("password: ")
    c = _client(args)
    sess = c.login(args.account, pwd)
    print(f"登录成功: {sess.user.get('name', '')} ({sess.user.get('phone', '')})")
    print(f"company_ex_id: {sess.company_ex_id or '(空,试试 company/list)'}")
    for co in c.companies()[:10]:
        print(f"  - {co.get('company_ex_id', co.get('ex_id', '?'))}  {co.get('company_name', co.get('name', ''))}")
    return 0


def cmd_me(args: argparse.Namespace) -> int:
    c = _client(args)
    info = c.me()
    print(json.dumps({k: v for k, v in info.items() if k != "token"}, ensure_ascii=False, indent=2))
    if args.show_token:
        print("\ntoken:", info.get("token", ""))
    return 0


def cmd_token(args: argparse.Namespace) -> int:
    """打印当前 token(默认打码),用于注入到别处。"""
    c = _client(args)
    tok = c.session.token
    if not tok:
        print("没有 token,先 login", file=sys.stderr)
        return 1
    if args.full:
        print(tok)
    else:
        print(f"{tok[:18]}...{tok[-8:]}  (len={len(tok)})")
    if args.company:
        c.use_company(args.company)
        print("company_ex_id ->", args.company)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = load_endpoints()
    if args.backend:
        rows = [r for r in rows if r["backend"] == args.backend]
    if args.grep:
        needle = args.grep.lower()
        rows = [r for r in rows if needle in r["path"].lower() or needle in r["fn"].lower()]
    if args.path:
        needle = args.path.lower()
        rows = [r for r in rows if needle in r["path"].lower()]
    for r in sorted(rows, key=lambda x: (x["backend"], x["path"])):
        print(f'{r["backend"]:12} {r["method"]:6} {r["path"]:56} {r["fn"]}')
    print(f"\n共 {len(rows)} 条")
    return 0


def cmd_call(args: argparse.Namespace, raw: bool = False) -> int:
    c = _client(args)
    body = json.loads(args.body) if args.body else None
    try:
        out = c.raw(args.backend, args.method, args.path, body) if raw else c.call(
            args.backend, args.method, args.path, body
        )
    except AdflyAuthError as exc:
        print(f"登录态失效: {exc}", file=sys.stderr)
        return 2
    except AdflyError as exc:
        print(f"业务错误: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="adfly_api", description="ad.aiadfly.com 接口客户端")
    p.add_argument("--env", choices=["prod", "test"], default=None)
    p.add_argument("--state", default="~/.adfly/session.json")
    p.add_argument("--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("login", help="登录并缓存 token")
    s.add_argument("--account", required=True, help="手机号或邮箱")
    s.add_argument("--password", help="不传则读 ADFLY_PASSWORD 或交互输入")
    s.set_defaults(func=cmd_login)

    s = sub.add_parser("me", help="当前用户信息")
    s.add_argument("--show-token", action="store_true")
    s.set_defaults(func=cmd_me)

    s = sub.add_parser("token", help="打印/切换 token 与公司")
    s.add_argument("--full", action="store_true", help="打印完整 token")
    s.add_argument("--company", help="切换 company_ex_id")
    s.set_defaults(func=cmd_token)

    s = sub.add_parser("list", help="列出接口清单")
    s.add_argument("--backend")
    s.add_argument("--grep")
    s.add_argument("--path")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("call", help="调用接口,只打印 data")
    s.add_argument("backend")
    s.add_argument("method")
    s.add_argument("path")
    s.add_argument("body", nargs="?")
    s.set_defaults(func=lambda a: cmd_call(a, raw=False))

    s = sub.add_parser("raw", help="调用接口,打印完整信封")
    s.add_argument("backend")
    s.add_argument("method")
    s.add_argument("path")
    s.add_argument("body", nargs="?")
    s.set_defaults(func=lambda a: cmd_call(a, raw=True))
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
