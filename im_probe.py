#!/usr/bin/env python3
"""IM 报文探针：只打计数与关键字段，原始响应落盘到 notes/im_probe/。

用途：确认 get_by_user_init 各变体里到底哪个返回会话列表。
输出重定向到文件后 read，避免大 hex 打爆 stdout 管道。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tiktok_pb2 as PB
from tk01_im import IMClient

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes", "im_probe")
os.makedirs(OUT, exist_ok=True)

LOG = []


def L(*a):
    line = " ".join(str(x) for x in a)
    LOG.append(line)


def body_set(msg):
    return [f.name for f, _ in msg.ListFields()]


def probe(M, cfg, label, cmd, field, kwargs, path="/api/v1/message/get_by_user_init"):
    cls = {
        "messages_per_user_init_v2_body": PB.MessagesPerUserInitV2RequestBody,
        "messages_per_user_body": PB.MessagesPerUserRequestBody,
    }[field]
    obj = cls()
    for k, v in kwargs.items():
        setattr(obj, k, v)

    req = PB.Request()
    req.cmd = cmd
    req.sequence_id = M._next_seq()
    req.sdk_version = "1.2.2"
    req.token = cfg["token"]
    req.refer = 3
    req.inbox_type = 0
    req.device_platform = "web"
    req.auth_type = 2
    getattr(req.body, field).CopyFrom(obj)
    payload = req.SerializeToString()

    L(f"\n=== {label} | cmd={cmd} {kwargs} | req={len(payload)}B")
    try:
        raw = M._post_proto(path, payload)
    except Exception as e:
        L(f"    ✗ 请求异常 {str(e)[:160]}")
        return None

    fn = os.path.join(OUT, f"{cmd}_{field}_{abs(hash(label)) % 10000}.bin")
    with open(fn, "wb") as fh:
        fh.write(raw)
    L(f"    resp={len(raw)}B → {os.path.relpath(fn, os.path.dirname(OUT))}")

    r = PB.Response()
    try:
        r.ParseFromString(raw)
    except Exception as e:
        L(f"    ✗ 解析失败 {e}")
        return None

    L(f"    回显cmd={r.cmd} statusCode={r.statusCode} err={r.errorDesc!r}")
    L(f"    logId={r.logId} seq={r.sequenceId} inboxType={r.inboxType} retry={r.retryCount}")
    L(f"    body非空={body_set(r.body)}")

    # 遍历所有可能的 ResponseBody 字段，谁有内容就报谁
    for fld, val in r.body.ListFields():
        n = None
        if hasattr(val, "__len__"):
            try:
                n = len(val)
            except TypeError:
                n = None
        L(f"      · {fld.name} len={n} fields={body_set(val) if hasattr(val, 'ListFields') else '-'}")

    for fname in ("messages_per_user_init_v2_body", "messages_per_user_body"):
        if r.body.HasField(fname):
            b = getattr(r.body, fname)
            convs = getattr(b, "conversations", [])
            msgs = getattr(b, "messages", [])
            L(f"    ★ {fname}: conversations={len(convs)} messages={len(msgs)} "
              f"has_more={getattr(b,'has_more','-')} next_cursor={getattr(b,'next_cursor','-')} "
              f"per_user_cursor={getattr(b,'per_user_cursor','-')} init_type={getattr(b,'init_type','-')}")
            if convs:
                L(f"      首会话: {json.dumps(IMClient.conv_brief(convs[0]), ensure_ascii=False)[:500]}")
            if msgs:
                m0 = msgs[0]
                L(f"      首消息: conv={m0.conversation_id} type={m0.conversation_type} "
                  f"sender={m0.sender} ctime={m0.create_time} "
                  f"content={m0.content[:120]!r}")
    return r


def main():
    M = IMClient(gap=1.0)
    try:
        cfg = M.refresh_config()
        L(f"api_url={cfg['api_url']}")
        L(f"token={cfg['token'][:24]}... uid={cfg['user']['user_id']} role={cfg['user']['role']} "
          f"region={cfg.get('region_code')} shop_region={cfg.get('shop_region')} "
          f"user_cursor={cfg.get('user_cursor')} biz={cfg.get('biz_service_id')}")

        variants = [
            ("A 基线 cursor=0", 203, "messages_per_user_init_v2_body",
             dict(cursor=0, new_user=0, init_sub_type=0)),
            ("B new_user=1", 203, "messages_per_user_init_v2_body",
             dict(cursor=0, new_user=1, init_sub_type=0)),
            ("C sub_type=3", 203, "messages_per_user_init_v2_body",
             dict(cursor=0, new_user=0, init_sub_type=3)),
            ("D sub_type=1", 203, "messages_per_user_init_v2_body",
             dict(cursor=0, new_user=0, init_sub_type=1)),
            ("E cmd200 limit=20", 200, "messages_per_user_body",
             dict(cursor=0, limit=20, new_user=0, interval=0)),
            ("F cmd200 用 user_cursor", 200, "messages_per_user_body",
             dict(cursor=int(cfg.get("user_cursor") or 0), limit=20, new_user=0, interval=0)),
        ]
        for label, cmd, field, kw in variants:
            probe(M, cfg, label, cmd, field, kw)
            time.sleep(1.3)
    finally:
        M.close()
        with open(os.path.join(OUT, "probe.log"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(LOG))


if __name__ == "__main__":
    main()
