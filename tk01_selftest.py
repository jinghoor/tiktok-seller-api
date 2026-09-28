#!/usr/bin/env python3
"""IM 全链路自检 —— 只读，不发消息、不建会话。

跑法：nohup python3 tk01_selftest.py > notes/im_selftest.out 2>&1 &
输出同时写 notes/im_selftest.json。
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_im import IMClient, IMError  # noqa: E402
from tk01_im_track import InviteTracker  # noqa: E402

R = []


def check(name, fn):
    t0 = time.time()
    try:
        val = fn()
        ok = True
        detail = val
    except Exception as e:
        ok = False
        detail = f"{type(e).__name__}: {str(e)[:220]}"
    R.append({"name": name, "ok": ok, "ms": int((time.time() - t0) * 1000),
              "detail": detail if isinstance(detail, (str, int, float, bool, type(None)))
              else (f"{type(detail).__name__}", json.dumps(detail, ensure_ascii=False, default=str)[:300])})
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag}] {name:44} {R[-1]['ms']:>6}ms  {R[-1]['detail']}", flush=True)
    return ok


def main():
    # ★ 同一个 CDP 端点只能有一个 Playwright sync 实例：
    #   InviteTracker 先建，把它已有的联盟连接借给 IMClient 用。
    T = InviteTracker()
    M = IMClient(affiliate=T.A)
    T.M = M
    try:
        cfg = {}
        check("01 IM token（首选端点）", lambda: cfg.update(M.refresh_config()) or
              {"api_url": cfg["api_url"], "user_id": M.self_user_id,
               "region": cfg.get("region_code")})
        check("02 self_user_id 非 0（两字段名兼容）",
              lambda: M.self_user_id if M.self_user_id else (_ for _ in ()).throw(
                  AssertionError("self_user_id=0")))
        check("03 cmd=203 初始化游标（只回 per_user_cursor）",
              lambda: M.init_cursor())
        cur = {}
        check("03b cmd=203 用上次 per_user_cursor 拉增量",
              lambda: (cur.update(M.init_cursor()), cur)[1])
        msgs = []
        check("04 cmd=200 翻页拉消息流",
              lambda: (msgs.extend(M.fetch_messages(max_pages=4)),
                       {"messages": len(msgs),
                        "conversations": len({m.conversation_id for m in msgs})})[1])
        idx = M.build_index(max_pages=4)
        check("05 会话索引聚合（creator_oec_id 映射）",
              lambda: {"conversations": len(idx["conversations"]),
                       "with_creator": sum(1 for c in idx["conversations"]
                                           if c.get("creator_oec_id")),
                       "with_handle": sum(1 for c in idx["conversations"]
                                          if c.get("handle"))})
        target = next((c for c in idx["conversations"] if c.get("creator_replied")), None) \
            or idx["conversations"][0]
        check(f"06 cmd=301 读会话消息 ({target['conversation_id']})",
              lambda: {"messages": len(M.conversation_messages(
                  target["conversation_id"], short_id=target["short_id"], limit=20)[0])})
        check(f"07 cmd=2000 读位置 ({target['conversation_id']})",
              lambda: {"rows": len(M.get_read_index(target["conversation_id"],
                                                    target["short_id"])["rows"])})
        handle = next((c["handle"] for c in idx["conversations"] if c.get("handle")), None)
        check(f"08 search_conversation_by_users ({handle!r})",
              lambda: {"matched": len(M.search_by_users(handle)["data"]["matched_conversations"])}
              if handle else "跳过（索引里没有 handle）")
        # 建会话 dry-run：不动数据
        check("09 conversation/create 报文构造（dry-run）",
              lambda: {"uid_role1": M.create_conversation("7493XXXXXXXXXX92")["body"]
                       ["participants"][1]["uid"],
                       "== seller_id": M.create_conversation("7493XXXXXXXXXX92")["body"]
                       ["participants"][1]["uid"] == M.seller_id})
        check("10 发文本报文构造（dry-run，不发）",
              lambda: {"bytes": M.send_text(target["conversation_id"], "SELFTEST",
                                            short_id=target["short_id"])["bytes"]})

        gs = []
        check("11 invitation_group/search", lambda: (gs.extend(T.groups()),
                                                     {"groups": len(gs)})[1])
        gid = next((g["id"] for g in gs if g.get("group_status") == 2), None) or gs[0]["id"]
        det = {}
        check(f"12 invitation_group/detail ({gid})",
              lambda: (det.update(T.group_creators(gid)),
                       {"creators": len(det["creators"]),
                        "status": det["group_status_text"]})[1])
        check("13 邀约 × IM 联表", lambda: (
            lambda r: {"groups": len(r["groups"]),
                       "im_matched": sum(g["im_matched"] for g in r["groups"]),
                       "im_replied": sum(g["im_replied"] for g in r["groups"])}
        )(T.track(gid)))
    finally:
        T.close()
        ok = sum(1 for x in R if x["ok"])
        print(f"\n===== {ok}/{len(R)} PASS =====", flush=True)
        out = HERE / "notes" / "im_selftest.json"
        out.write_text(json.dumps({"passed": ok, "total": len(R), "checks": R},
                                  ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"结果: {out}", flush=True)


if __name__ == "__main__":
    main()
