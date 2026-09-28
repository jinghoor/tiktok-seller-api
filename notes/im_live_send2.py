"""真发两条 —— 验证 cmd=100 写路径。发完立刻用 cmd=301 回读确认落库。"""
import json, sys, time
sys.path.insert(0, ".")
from tk01_im import IMClient, MSG_TEXT

TEXT = "Chào bạn, mình là shop ExampleShop. Rất vui được kết nối, mong có cơ hội hợp tác cùng bạn ạ."

TARGETS = [
    {"conversation_id": "7690XXXXXXXXXX92", "handle": "creator_handle"},
    {"conversation_id": "7690XXXXXXXXXX39", "handle": "creator_handle"},
]

M = IMClient(gap=0.9)
out = []
try:
    M.refresh_config()
    print(f"self={M.self_user_id}  region={M.region}  shop={M.seller_id}", flush=True)
    for t in TARGETS:
        cid = t["conversation_id"]
        print(f"\n=== 发 → {t['handle']}  conv={cid}", flush=True)
        r = M.send_text(cid, TEXT, short_id=int(cid), apply=True)
        print(f"    statusCode={r['statusCode']} err={r.get('errorDesc')!r}", flush=True)
        print(f"    client_message_id={r['client_message_id']}", flush=True)
        if r["statusCode"] == 0:
            print(f"    ★ server_message_id={r.get('server_message_id')} "
                  f"status={r.get('status')} check={r.get('check_code')} "
                  f"filtered={r.get('filtered_content')!r} async={r.get('is_async_send')}", flush=True)
        print(f"    logId={r.get('logId')}", flush=True)
        out.append({**t, "result": r})
        time.sleep(5.0)

    print("\n\n===== 回读确认（cmd=301）=====", flush=True)
    for t in TARGETS:
        time.sleep(1.0)
        msgs, meta = M.conversation_messages(t["conversation_id"],
                                             short_id=int(t["conversation_id"]), limit=20)
        print(f"\n  conv={t['conversation_id']} 消息 {len(msgs)} 条 has_more={meta['has_more']}", flush=True)
        for m in msgs:
            who = "我" if str(m.sender) == str(M.self_user_id) else f"达人({m.sender})"
            role = dict(m.ext).get("sender_im_role", "?")
            print(f"    [{m.create_time}] {who} role={role} mt={m.message_type} "
                  f"idx={m.index_in_conversation} {m.content[:110]!r}", flush=True)
    open("notes/im_live_send2.json", "w", encoding="utf-8").write(
        json.dumps({"text": TEXT, "sends": out}, ensure_ascii=False, indent=2, default=str))
finally:
    M.close()
