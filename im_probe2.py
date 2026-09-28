#!/usr/bin/env python3
"""第二轮 IM 探针：会话列表(690) / 消息流翻页(200) / 对话内消息(301)。

结果写 notes/im_probe2.log，原始响应落盘 notes/im_probe2/。
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tiktok_pb2 as PB
from tk01_im import IMClient

OUT = os.path.join(HERE, "notes", "im_probe2")
os.makedirs(OUT, exist_ok=True)
LOG = []


def L(*a):
    LOG.append(" ".join(str(x) for x in a))


def _mk_req(M, cfg, cmd, field, obj):
    req = PB.Request()
    req.cmd = cmd
    req.sequence_id = M._next_seq()
    req.sdk_version = "1.2.2"
    req.token = cfg["token"]
    req.refer = 3
    req.inbox_type = 0
    req.device_platform = "web"
    req.auth_type = 2
    if field:
        getattr(req.body, field).CopyFrom(obj)
    return req


def send(M, cfg, label, cmd, field, obj, path, save=None):
    req = _mk_req(M, cfg, cmd, field, obj) if field is not None else _mk_req(M, cfg, cmd, None, None)
    payload = req.SerializeToString()
    L(f"\n=== {label}\n    POST {path}  cmd={cmd} req={len(payload)}B")
    try:
        raw = M._post_proto(path, payload)
    except Exception as e:
        L(f"    ✗ {str(e)[:200]}")
        return None
    fn = os.path.join(OUT, (save or label.split()[0]) + ".bin")
    with open(fn, "wb") as fh:
        fh.write(raw)
    L(f"    resp={len(raw)}B")
    r = PB.Response()
    try:
        r.ParseFromString(raw)
    except Exception as e:
        L(f"    ✗ 解析失败 {e}  head={raw[:80].hex()}")
        return None
    L(f"    回显cmd={r.cmd} statusCode={r.statusCode} err={r.errorDesc!r} logId={r.logId}")
    for fld, val in r.body.ListFields():
        L(f"    body字段={fld.name} fields={[f.name for f, _ in val.ListFields()] if hasattr(val, 'ListFields') else '-'}")
    return r


def dump_690(r):
    if not r.body.HasField("conversation_group_list_body"):
        return []
    g = r.body.conversation_group_list_body.conversation_group_list
    L(f"    ★ group=({g.group.group_id},{g.group.group_name!r}) next_cursor={g.next_cursor} "
      f"has_more={g.has_more} total_count={g.total_count} entries={len(g.entries)}")
    rows = []
    for e in g.entries[:60]:
        c = e.conversation
        ci = {f.name: v for f, v in c.ListFields() if not hasattr(v, "ListFields") and not isinstance(v, (bytes,))}
        prof = {}
        if c.creator_profile:
            try:
                prof = json.loads(c.creator_profile)
            except Exception:
                prof = {"_raw": c.creator_profile[:200]}
        ui = {}
        if c.HasField("user_info"):
            ui = {f.name: v for f, v in c.user_info.ListFields() if not hasattr(v, "ListFields")}
        rows.append({
            "conversation_id": c.conversation_id,
            "type": c.conversation_type,
            "short_id": c.conversation_short_id,
            "inbox_type": c.inbox_type,
            "badge": c.badge_count, "badge_v2": c.badge_count_v2,
            "participants": c.participants_count,
            "is_participant": c.is_participant,
            "user_info": ui,
            "creator_profile": prof,
            "msgs_in_entry": len(e.messages),
            "read_index": c.conversation_setting_info.read_index if c.HasField("conversation_setting_info") else None,
            "min_index": c.conversation_setting_info.min_index if c.HasField("conversation_setting_info") else None,
            "raw_fields": list(ci.keys()),
        })
        L(f"      · conv={c.conversation_id} t={c.conversation_type} badge={c.badge_count} "
          f"unread_v2={c.badge_count_v2} part={c.participants_count} msgs={len(e.messages)} "
          f"prof={json.dumps(prof, ensure_ascii=False)[:200]}")
    return rows


def main():
    M = IMClient(gap=1.0)
    rows690 = []
    try:
        cfg = M.refresh_config()
        L(f"api_url={cfg['api_url']} uid={cfg['user']['user_id']} role={cfg['user']['role']}")

        # ---- 690: 会话分组列表（试不同 group_id） ----
        for gid in (0, 1, 2, 3):
            b = PB.GetConversationGroupListRequestBody()
            b.conversation_group_list.group.group_id = gid
            b.conversation_group_list.cursor = 0
            b.conversation_group_list.direction = 0
            b.conversation_group_list.limit = 20
            r = send(M, cfg, f"690-group{gid}", 690, "conversation_group_list_body", b,
                     "/api/v1/conversation/get_group_list", save=f"690_g{gid}")
            if r:
                got = dump_690(r)
                if got:
                    rows690 = got
                    break
            time.sleep(1.3)

        # ---- 200: 消息流翻页验证 ----
        seen_cursors = []
        cur = 0
        for page in range(3):
            b = PB.MessagesPerUserRequestBody()
            b.cursor = cur
            b.limit = 50
            b.new_user = 1 if page == 0 else 0
            b.interval = 0
            r = send(M, cfg, f"200-page{page}", 200, "messages_per_user_body", b,
                     "/api/v1/message/get_by_user_init", save=f"200_p{page}")
            if not r or not r.body.HasField("messages_per_user_body"):
                break
            mb = r.body.messages_per_user_body
            convs = sorted({m.conversation_id for m in mb.messages})
            L(f"    ★ page{page}: msgs={len(mb.messages)} has_more={mb.has_more} "
              f"next_cursor={mb.next_cursor} 涉及会话={len(convs)}")
            seen_cursors.append((page, len(mb.messages), mb.next_cursor, mb.has_more, len(convs)))
            if not mb.has_more or mb.next_cursor == cur:
                break
            cur = mb.next_cursor
            time.sleep(1.3)
        L(f"    翻页汇总: {seen_cursors}")

        # ---- 301: 对话内消息 ----
        target = None
        if rows690:
            target = rows690[0]["conversation_id"]
        else:
            target = "7580XXXXXXXXXX98"
        for direction, anchor in ((1, 0), (0, 0)):
            b = PB.MessagesInConversationRequestBody()
            b.conversation_id = target
            b.conversation_type = 2
            b.direction = direction
            b.anchor_index = anchor
            b.limit = 20
            r = send(M, cfg, f"301-dir{direction}-{target[:8]}", 301, "messages_in_conversation_body", b,
                     "/api/v1/message/get_in_conversation", save=f"301_d{direction}")
            if r and r.body.HasField("messages_in_conversation_body"):
                mb = r.body.messages_in_conversation_body
                L(f"    ★ msgs={len(mb.messages)} has_more={mb.has_more} next_cursor={mb.next_cursor}")
                for m in mb.messages[:5]:
                    L(f"      · idx={m.index_in_conversation} sender={m.sender} ctime={m.create_time} "
                      f"type={m.message_type} content={m.content[:150]!r}")
            time.sleep(1.3)

        with open(os.path.join(OUT, "conversations_690.json"), "w", encoding="utf-8") as fh:
            json.dump(rows690, fh, ensure_ascii=False, indent=2)
    finally:
        M.close()
        with open(os.path.join(OUT, "probe2.log"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(LOG))


if __name__ == "__main__":
    main()
