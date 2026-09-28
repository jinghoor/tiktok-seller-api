#!/usr/bin/env python3
"""达人邀约后跟踪 —— 把「定向计划」和「站内 IM」对起来。

## 为什么要这个

邀约(定向计划)和聊天(IM)是两套系统、两套 ID：

| 侧 | ID | 来源 |
|---|---|---|
| 定向计划 | `creator_oec_id` + `user_name` + `invitation_id` + `group_creator_status` | `invitation_group/detail` |
| 站内 IM | `conversation_id` + 达人 im_id + `creator_oec_id`(在会话 ext 里) | `v2/message/get_by_user` |

**唯一能对上的是 `creator_oec_id`**（会话创建事件的 ext 里带，
`search_conversation_by_users` 的 `biz_ext` 里也带）。所以跟踪表按 oec_id 做 join。

## 数据来源（全部实测）

1. `invitation_group/search` → `data.invitation_list[]`（**不是** `invitation_groups`）
   `{id, name, group_status:2进行中/4已终止, creator_cnt, creator_added_cnt, creator_posted_cnt, start_time, end_time}`
2. `invitation_group/detail` `{invitation_group_id}` → `data.invitation.creator_id_list[]`
   每条：`{base_info:{creator_id, nick_name, user_name, creator_oec_id},
           invitation_id, group_creator_status, product_add_cnt, effective_status}`
3. IM 会话索引（`tk01_im.py index`）→ `creator_oec_id → conversation_id + 消息流`

## 状态语义

- `group_creator_status`: **0 = 待接受**（实测 10/10 都是 0）。其余取值未实测，
  一律按原值输出（`status_raw`），不猜。
- `creator_replied`: 会话里存在 `sender_im_role="4"` 的文本消息 —— 达人回过话。
- `unread`: 该会话 `paas:read_index == 0` 或我们有未读（用 cmd=2000 读实时读位置时才准）。

## 用法

```bash
python3 tk01_im_track.py groups                      # 列定向计划
python3 tk01_im_track.py creators 7690XXXXXXXXXX47 --full
python3 tk01_im_track.py track --refresh --save      # 全计划跟踪表（标出未回话的）
python3 tk01_im_track.py track 7690XXXXXXXXXX47
python3 tk01_im_track.py ensure --yes               # 给没会话的受邀达人建会话（写）
python3 tk01_im_track.py followup --text "话术" --yes # 给未回话的群发跟进（写）
```
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_affiliate import AffiliateClient  # noqa: E402
from tk01_im import IMClient, IMError, activate_shop  # noqa: E402
import tk01_config as CFG  # noqa: E402

GROUP_STATUS = {1: "待开始", 2: "进行中", 3: "已结束", 4: "已终止"}
CREATOR_STATUS = {0: "待接受"}


def _ms(v) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def _fmt(ms) -> str:
    if not ms:
        return "-"
    import datetime
    return datetime.datetime.fromtimestamp(ms / 1000).strftime("%m-%d %H:%M")


class InviteTracker:
    """定向计划 × 站内 IM 的联表跟踪。"""

    def __init__(self, *, shop: str | None = None, port: int | None = None,
                 gap: float = 0.9):
        activate_shop(shop)
        self.shop = CFG.load_shop(shop)
        self.A = AffiliateClient(port=port or self.shop["cdp_port"], gap=gap)
        self.M: IMClient | None = None

    # ── 计划侧 ──
    def groups(self, *, page_size: int = 50) -> list:
        r = self.A.call("group_search", {"cur_page": 1, "page_size": page_size})
        if r.get("code") != 0:
            raise RuntimeError(f"group_search code={r.get('code')} {r.get('message')}")
        d = r.get("data") or {}
        return d.get("invitation_list") or []

    def group_creators(self, group_id: str) -> dict:
        r = self.A.call("group_detail", {"invitation_group_id": str(group_id)})
        if r.get("code") != 0:
            raise RuntimeError(f"group_detail code={r.get('code')} {r.get('message')}")
        inv = (r.get("data") or {}).get("invitation") or {}
        rows = []
        for x in inv.get("creator_id_list") or []:
            bi = x.get("base_info") or {}
            rows.append({
                "creator_oec_id": str(bi.get("creator_oec_id") or bi.get("creator_id") or ""),
                "creator_id": str(bi.get("creator_id") or ""),
                "nick_name": bi.get("nick_name") or "",
                "handle": bi.get("user_name") or "",
                "invitation_id": str(x.get("invitation_id") or ""),
                "creator_status": x.get("group_creator_status"),
                "creator_status_text": CREATOR_STATUS.get(x.get("group_creator_status"),
                                                          f"status={x.get('group_creator_status')}"),
                "product_add_cnt": x.get("product_add_cnt"),
                "effective_status": x.get("effective_status"),
            })
        return {
            "group_id": str(inv.get("id") or group_id),
            "name": inv.get("name") or "",
            "group_status": inv.get("group_status"),
            "group_status_text": GROUP_STATUS.get(inv.get("group_status"),
                                                  f"status={inv.get('group_status')}"),
            "region": inv.get("region"),
            "start_time": _ms(inv.get("start_time")),
            "end_time": _ms(inv.get("end_time")),
            "creator_cnt": inv.get("creator_cnt"),
            "creator_added_cnt": inv.get("creator_added_cnt"),
            "creator_posted_cnt": inv.get("creator_posted_cnt"),
            "product_cnt": inv.get("product_cnt"),
            "creators": rows,
        }

    # ── IM 侧 ──
    def im(self) -> IMClient:
        if self.M is None:
            # 复用 tracker 的联盟连接：两个 Playwright sync 实例会互相干扰
            self.M = IMClient(shop=self.shop["_key"], affiliate=self.A)
        return self.M

    def im_index(self, *, refresh: bool = False, max_pages: int = 6) -> dict:
        if not refresh:
            cached = IMClient.load_index()
            if cached:
                return cached
        return self.im().build_index(max_pages=max_pages)

    # ── 联表 ──
    def track(self, group_id: str | None = None, *, refresh_index: bool = False,
              live_read: bool = False, save: bool = False) -> dict:
        idx = self.im_index(refresh=refresh_index)
        by_creator = {}
        for c in idx.get("conversations", []):
            oid = c.get("creator_oec_id")
            if oid:
                by_creator[str(oid)] = c

        gs = self.groups()
        if group_id:
            gs = [g for g in gs if str(g.get("id")) == str(group_id)]
            if not gs:
                raise RuntimeError(f"没找到计划 {group_id}；现有: "
                                   f"{[g.get('id') for g in self.groups()]}")

        out_groups = []
        for g in gs:
            det = self.group_creators(g["id"])
            rows, matched, replied, no_conv = [], 0, 0, 0
            for c in det["creators"]:
                oid = c["creator_oec_id"]
                conv = by_creator.get(oid)
                row = dict(c)
                row["has_conversation"] = bool(conv)
                row["conversation_id"] = conv["conversation_id"] if conv else None
                row["short_id"] = conv["short_id"] if conv else None
                row["creator_replied"] = bool(conv and conv.get("creator_replied"))
                row["first_creator_reply_time"] = conv.get("first_creator_reply_time") if conv else None
                row["last_time"] = conv.get("last_time") if conv else None
                row["last_text"] = (conv.get("last_text") or "")[:160] if conv else ""
                row["text_count"] = conv.get("text_count", 0) if conv else 0
                if conv:
                    matched += 1
                    if row["creator_replied"]:
                        replied += 1
                else:
                    no_conv += 1
                if live_read and conv:
                    try:
                        ri = self.im().get_read_index(conv["conversation_id"],
                                                      conv.get("short_id"))
                        mine = [x for x in ri["rows"]
                                if str(x["uid"]) == str(idx.get("self_user_id"))]
                        row["our_read_index"] = mine[0]["index"] if mine else None
                    except IMError as e:
                        row["our_read_index_error"] = str(e)[:120]
                rows.append(row)

            out_groups.append({
                **{k: det[k] for k in ("group_id", "name", "group_status",
                                       "group_status_text", "region", "start_time",
                                       "end_time", "creator_cnt", "creator_added_cnt",
                                       "creator_posted_cnt", "product_cnt")},
                "im_matched": matched, "im_replied": replied, "im_no_conversation": no_conv,
                "creators": rows,
            })

        res = {"shop": self.shop["_key"], "region": self.shop["region"],
               "seller_id": self.shop["seller_id"],
               "im_self_user_id": idx.get("self_user_id"),
               "im_index_fetched_at": idx.get("fetched_at"),
               "im_conversation_count": len(idx.get("conversations", [])),
               "tracked_at": int(time.time() * 1000),
               "groups": out_groups}
        if save:
            p = HERE / "notes" / "aff_invite_tracking.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str),
                         encoding="utf-8")
            res["_saved"] = str(p)
        try:
            from tk01_log import log_run
            log_run("invite_track", target=f"{len(out_groups)}个计划", ok=True,
                    result={"groups": [(g["group_id"], g["im_matched"], g["im_replied"])
                                       for g in out_groups]},
                    note="tk01_im_track.track")
        except Exception:
            pass
        return res

    # ── 给没会话的达人建会话（写） ──
    def ensure_conversations(self, group_id: str, *, apply: bool = False,
                             limit: int = 50) -> dict:
        idx = self.im_index(refresh=True)
        have = {str(c.get("creator_oec_id")) for c in idx.get("conversations", [])
                if c.get("creator_oec_id")}
        det = self.group_creators(group_id)
        todo = [c for c in det["creators"] if c["creator_oec_id"] not in have][:limit]
        results = []
        for c in todo:
            try:
                r = self.im().create_conversation(c["creator_oec_id"], apply=apply)
                results.append({"creator_oec_id": c["creator_oec_id"],
                                "handle": c["handle"],
                                "conversation_id": r.get("conversation_id"),
                                "code": r.get("code"), "dry_run": r.get("dry_run", False)})
            except Exception as e:
                results.append({"creator_oec_id": c["creator_oec_id"],
                                "handle": c["handle"], "error": str(e)[:200]})
            if apply:
                time.sleep(1.5)
        return {"group_id": group_id, "applied": apply,
                "need": len(todo), "existing": len(det["creators"]) - len(todo),
                "results": results}

    # ── 跟进群发（写） ──
    def followup(self, text: str, group_id: str | None = None, *, apply: bool = False,
                 only_no_reply: bool = True, only_active_groups: bool = True,
                 gap: float | None = None, max_send: int = 50) -> dict:
        # 群发是写操作，必须用最新会话状态（可能有刚建出来的会话）
        tr = self.track(group_id, refresh_index=True)
        targets = []
        for g in tr["groups"]:
            if only_active_groups and g["group_status"] != 2:
                continue
            for c in g["creators"]:
                if not c["has_conversation"]:
                    continue
                if only_no_reply and c["creator_replied"]:
                    continue
                targets.append({"conversation_id": c["conversation_id"],
                                "short_id": c["short_id"],
                                "creator_oec_id": c["creator_oec_id"],
                                "handle": c["handle"],
                                "group_id": g["group_id"]})
        res = self.im().send_batch(targets, text, gap=gap, apply=apply, max_send=max_send,
                                   progress=lambda i, n, r: print(
                                       f"    [{i}/{n}] {r.get('handle')} "
                                       f"{'ok' if r.get('ok') else 'FAIL'}", flush=True))
        res["targets"] = len(targets)
        res["only_no_reply"] = only_no_reply
        return res

    def close(self):
        if self.M:
            self.M.close()      # 复用连接时不会关 self.A
        self.A.close()


# ─────────────────────────── CLI ───────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="达人邀约后跟踪（定向计划 × 站内 IM）")
    ap.add_argument("--shop", default=None)
    ap.add_argument("--port", type=int, default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("groups")
    p = sub.add_parser("creators"); p.add_argument("group_id")
    p.add_argument("--full", action="store_true")
    p = sub.add_parser("track"); p.add_argument("group_id", nargs="?")
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--live-read", action="store_true")
    p.add_argument("--save", action="store_true"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("ensure"); p.add_argument("group_id")
    p.add_argument("--yes", action="store_true"); p.add_argument("--limit", type=int, default=50)
    p = sub.add_parser("followup"); p.add_argument("--text", required=True)
    p.add_argument("--group", default=None); p.add_argument("--all", action="store_true")
    p.add_argument("--yes", action="store_true"); p.add_argument("--gap", type=float, default=None)
    p.add_argument("--max", type=int, default=50)
    a = ap.parse_args()

    T = InviteTracker(shop=a.shop, port=a.port)
    try:
        if a.cmd == "groups":
            gs = T.groups()
            print(f"  定向计划 {len(gs)} 个（店铺 {T.shop['_key']} / {T.shop['region']}）")
            for g in gs:
                st = g.get("group_status")
                print(f"    {g.get('id')}  {str(g.get('name'))[:26]:28} "
                      f"{GROUP_STATUS.get(st, f'status={st}'):6} 达人={g.get('creator_cnt'):<4} "
                      f"已接受={g.get('creator_added_cnt'):<4} 已发布={g.get('creator_posted_cnt'):<4} "
                      f"{_fmt(_ms(g.get('start_time')))}~{_fmt(_ms(g.get('end_time')))}")
        elif a.cmd == "creators":
            det = T.group_creators(a.group_id)
            print(f"  {det['name']}  [{det['group_status_text']}]  "
                  f"达人 {det['creator_cnt']} / 已接受 {det['creator_added_cnt']} / "
                  f"已发布 {det['creator_posted_cnt']}")
            for c in det["creators"]:
                print(f"    {c['creator_oec_id']:22} @{c['handle']:26} {c['nick_name'][:22]:24} "
                      f"{c['creator_status_text']:8} inv={c['invitation_id']}")
            if a.full:
                print(json.dumps(det, ensure_ascii=False, indent=2)[:4000])
        elif a.cmd == "track":
            res = T.track(a.group_id, refresh_index=a.refresh, live_read=a.live_read,
                          save=a.save)
            if a.json:
                print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
                return
            print(f"  店铺 {res['shop']} / {res['region']}   self_im={res['im_self_user_id']}")
            print(f"  IM 会话索引 {res['im_conversation_count']} 个"
                  f"（fetched_at={_fmt(res['im_index_fetched_at'])}）")
            for g in res["groups"]:
                print(f"\n  ● {g['name']}  [{g['group_status_text']}]  id={g['group_id']}")
                print(f"    达人 {g['creator_cnt']} | IM 命中 {g['im_matched']} | "
                      f"达人回话 {g['im_replied']} | 无会话 {g['im_no_conversation']}")
                for c in g["creators"]:
                    flag = "✔已回" if c["creator_replied"] else ("·无会话" if not c["has_conversation"] else "✗未回")
                    print(f"      {flag:6} {c['creator_oec_id']:22} @{c['handle']:26} "
                          f"{c['creator_status_text']:8} conv={str(c['conversation_id'])[:20]:22} "
                          f"最后={_fmt(c['last_time'])} {str(c['last_text'])[:36]!r}")
            if res.get("_saved"):
                print(f"\n  已存 {res['_saved']}")
        elif a.cmd == "ensure":
            r = T.ensure_conversations(a.group_id, apply=a.yes, limit=a.limit)
            print(f"  需要建会话 {r['need']} 个，已有 {r['existing']} 个  applied={r['applied']}")
            for x in r["results"]:
                print(f"    {x.get('creator_oec_id')} @{x.get('handle'):26} "
                      f"→ {x.get('conversation_id') or x.get('error')}")
        elif a.cmd == "followup":
            gid = None if a.all else a.group
            r = T.followup(a.text, gid, apply=a.yes, only_no_reply=not a.all,
                           gap=a.gap, max_send=a.max)
            print(f"  目标 {r['targets']} 个  applied={r['applied']} "
                  f"sent={r['sent']} failed={r['failed']}")
    except Exception as e:
        print(f"  ✗ {type(e).__name__}: {str(e)[:400]}")
        sys.exit(2)
    finally:
        T.close()


if __name__ == "__main__":
    main()
