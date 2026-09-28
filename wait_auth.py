#!/usr/bin/env python3
"""等 TikTok 授权完成并打印结果。

    python3 wait_auth.py                 # 用最近一次生成的链接
    python3 wait_auth.py --new           # 先生成一条新链接再等
    python3 wait_auth.py --link-ex-id X  # 指定某次授权
    python3 wait_auth.py --minutes 10    # 等待上限(默认 15 分钟)
    python3 wait_auth.py --once          # 只查一次,不轮询
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api import AdflyClient
from adfly_api import helpers as H

STATE = HERE / "notes" / "auth_link.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", action="store_true", help="重新生成授权链接")
    ap.add_argument("--link-ex-id")
    ap.add_argument("--minutes", type=float, default=15.0)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=float, default=3.0)
    args = ap.parse_args()

    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    c.t.timeout = 20.0
    c.t.retries = 4
    if not c.session.token:
        print("先登录: python3 -m adfly_api login --account <手机号>", file=sys.stderr)
        return 2

    def snapshot(label: str, tries: int = 5) -> tuple:
        """取基线。网络抖动很常见,拿不到就重试,绝不因为取基线失败而中断等待。"""
        for i in range(tries):
            try:
                bcs = {b["bc_detail"]["bc_id"] for b in H.tt_bc_list(c, 1960)}
                advs = {a["advertiser_id"] for a in c.advertisers()}
                return bcs, advs
            except Exception as exc:  # noqa: BLE001
                print(f"  ({label} 第 {i+1}/{tries} 次失败: {type(exc).__name__},重试)")
                time.sleep(2 * (i + 1))
        print(f"  ({label} 取不到,按空基线继续 —— 不影响判断授权结果)", file=sys.stderr)
        return set(), set()

    before, before_adv = snapshot("基线")

    if args.link_ex_id:
        link_ex_id = args.link_ex_id
        link = ""
    else:
        if args.new or not STATE.exists():
            L = H.auth_link(c, platform=1)
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps({**L, "created_at": time.time()},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
            print("新授权链接:")
            print()
            print("   " + L["auth_link"])
            print()
            link, link_ex_id = L["auth_link"], L["link_ex_id"]
        else:
            d = json.loads(STATE.read_text(encoding="utf-8"))
            link, link_ex_id = d["auth_link"], d["link_ex_id"]
            age = int(time.time() - d.get("created_at", time.time()))
            print(f"沿用 {age // 60} 分 {age % 60} 秒前生成的链接:")
            print()
            print("   " + link)
            print()

    print(f"link_ex_id = {link_ex_id}")
    print(f"已有 BC {len(before)} 个 / 广告账户 {len(before_adv)} 个")
    print()

    if args.once:
        r = H.check_auth_result(c, link_ex_id)
        print(f"查询结果: {json.dumps(r, ensure_ascii=False, default=str)[:300]}")
        return 0 if r.get("result") else 1

    deadline = time.time() + args.minutes * 60
    print(f"等待授权完成(上限 {args.minutes:g} 分钟,每 {args.interval:g}s 查一次)…")
    polls = 0
    try:
        while time.time() < deadline: CONTACT_REDACTED += 1
            r = H.check_auth_result(c, link_ex_id)
            if r.get("result"):
                print(f"\n✓ 授权成功(第 {polls} 次查询)")
                print(f"  result = {json.dumps(r['result'], ensure_ascii=False, default=str)[:400]}")
                if r.get("auth"):
                    print(f"  auth   = {json.dumps(r['auth'], ensure_ascii=False, default=str)[:400]}")
                after, after_adv = snapshot("对比", tries=5)
                new_bc = after - before
                new_adv = after_adv - before_adv
                print(f"\n  BC: {len(before)} → {len(after)}" + (f"  新增 {sorted(new_bc)}" if new_bc else "  无新增"))
                print(f"  广告账户: {len(before_adv)} → {len(after_adv)}"
                      + (f"  新增 {sorted(new_adv)}" if new_adv else "  无新增"))
                if new_bc:
                    print("\n  新 BC 详情:")
                    try:
                        cur = H.tt_bc_list(c, 1960)
                    except Exception:
                        cur = []
                    for b in cur:
                        if b["bc_detail"]["bc_id"] in new_bc:
                            det = b["bc_detail"]
                            print(f"    {det['bc_id']}  {det['name']}  {det['company']}  "
                                  f"{det['currency']}  {det['registered_area']}  role={b['user_role']}")
                else:
                    print("\n  提示:授权完成但没看到新 BC。可能你勾选的 BC 已经授权过了,"
                          "或者选的是广告账户而非商务中心。")
                return 0
            if polls % 10 == 0:
                left = int(deadline - time.time())
                print(f"  … 仍在等待({polls} 次查询,剩余 {left // 60}分{left % 60}秒)")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n已被中断")
        return 130
    print(f"\n超时:{args.minutes:g} 分钟内没等到 result。")
    print("  可能原因:授权未真正完成 / 链接已过期 / 你选的是广告账户而非商务中心。")
    print("  排查:重新跑 python3 wait_auth.py --new 生成新链接再试。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
