#!/usr/bin/env python3
"""TikTok Shop 站内 IM 客户端 —— 达人/买家私信（protobuf + JSON 双协议）。

## 域与鉴权

IM 不在 `affiliate.` 也不在 `api16-normal-sg.`，先取动态配置：

```
GET {affiliate}/api/v1/im/shop_creator/shop/user/token/get
GET {affiliate}/api/v1/oec/affiliate/seller/im/get/token      ← 备选
→ { token, api_url:"https://oec-im-tt-sg.tiktokglobalshopv.com/",
    ws_url, app_id:380360, biz_service_id:10000,
    user:{role:2, user_id:5038XXXXXXXXXX14},
    region_code:"VN", shop_region:"VN", user_cursor:1787XXXXXXXXXX03 }
```

`api_url` 动态、末尾带 `/`；token 会过期。`user_cursor` 是"已同步到哪"的服务端游标 —— 见下。

## ★ 拉会话：cmd=200，不是 cmd=203

| cmd | 路径 | 作用 | 实测 |
|---|---|---|---|
| 203 `messages_per_user_init_v2` | `v2/message/get_by_user_init` | 初始化同步 | **返回 0 会话**，只回 `per_user_cursor`（== token 里的 `user_cursor`，含义是"你已是最新"）|
| 200 `messages_per_user` | `v2/message/get_by_user_init` | **翻页拉消息流** | ✅ cursor=0 → 50 条 / 9 会话 / has_more=1；再翻 → 31 条 / 8 会话 / 结束 |

服务端认为本账号已 init 完毕，所以 203 不发历史。**会话索引从 200 的消息流里聚合**：
每条 `MessageBody.ext` 带 `shop_oec_id` / `creator_oec_id` / `uname` / `sender_im_role`。

## 报文格式（对齐线上客户端，非推测）

```
Request { cmd, sequence_id, sdk_version, token, refer:3, inbox_type:0,
          device_platform:"web", auth_type:2, device_id, build_number, body }
```

- 读: `sdk_version="0.0.8-feat-add-cmd-in-error"`，`Content-Type: application/x-protobuf`
- 写: `sdk_version="0.0.1-gec"`，同一 Content-Type
- `MessageBody.message_type`: **1000 = 文本**，**50001 = 系统/命令事件**
- `SendMessageRequestBody.message_type` 同样用 **1000**（不是 7）
- `sender_im_role`: 店铺 = `"2"`，达人 = `"4"`
- `conversation/create` 与 `search_conversation_by_users` 是 **JSON** + 头 `x-im-paas-token`

## 端点表

| 用途 | 方法 | URL | 编码 |
|---|---|---|---|
| 消息流/会话索引 | POST | `{api_url}v2/message/get_by_user_init` cmd=200/203 | protobuf |
| 会话内消息 | POST | `{api_url}v1/message/get_by_conversation` cmd=301 | protobuf |
| 发消息 | POST | `{api_url}v1/message/send` cmd=100 | protobuf |
| 标记已读 | POST | `{api_url}v3/conversation/mark_read` cmd=604 | protobuf |
| 读位置 | POST | `{api_url}v3/conversation/get_read_index` cmd=2000 | protobuf |
| 建会话 | POST | `{api_url}api/v1/im/conversation/create?...&oec_region=VN` | JSON |
| 按 handle 搜会话 | GET | `{affiliate}/api/v1/im/shop_creator/shop/conversation/search?...&uname=` | JSON |
| 按用户名搜会话 | POST | `{api_url}api/v1/im/search/search_conversation_by_users` | JSON |
| 通知关系更新 | POST | `{affiliate}/api/v1/affiliate/notification/im/relation/update` | JSON |

## 用法

```bash
python3 tk01_im.py token                        # IM token / api_url
python3 tk01_im.py index [--pages 5]            # 聚合会话索引（含 creator_oec_id / handle）
python3 tk01_im.py conv <conversation_id>       # 读会话消息
python3 tk01_im.py read <conversation_id>       # 标记已读（写）
python3 tk01_im.py send <conv_id> "文本" [--yes]            # 发文本
python3 tk01_im.py batch --conv <id1,id2> --text "话术" [--yes] --gap 6
python3 tk01_im.py batch --creators <oec1,oec2> --text "话术" [--yes]
python3 tk01_im.py create <creator_oec_id>      # 对未聊过的达人建会话
python3 tk01_im.py find <handle>                # 按抖音号搜会话
```
"""
from __future__ import annotations

import argparse
import base64
import json
import random
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_affiliate import AffiliateClient  # noqa: E402
import tk01_config as CFG  # noqa: E402

# ── cmd 号 ──
CMD_SEND = 100
CMD_MESSAGES_PER_USER = 200
CMD_CONV_INIT_V2 = 203
CMD_MESSAGES = 301
CMD_MARK_READ = 604
CMD_CREATE_CONV = 609
CMD_READ_INDEX = 2000
CMD_MIN_INDEX = 2001

# ── message_type ──
MSG_TEXT = 1000
MSG_COMMAND = 50001

# ── sender_im_role ──
ROLE_SHOP = "2"
ROLE_CREATOR = "4"

SDK_READ = "0.0.8-feat-add-cmd-in-error"
SDK_WRITE = "0.0.1-gec"
BUILD_NUMBER = "ad9801f:Detached: ad9801f296fa566d43c75b86cecc603dce10145f"

# 各端点路径（{api_url} 末尾已带 /）
#
# ★ 路径与 cmd 一一对应，不能串：
#   cmd=203 → v2/message/get_by_user_init   服务端读 messages_per_user_init_v2_body
#   cmd=200 → v2/message/get_by_user        服务端读 messages_per_user_body
# 串了会得到 `request.MessagesPerUserInitV2Body is empty`。
P_BY_USER_INIT = "v2/message/get_by_user_init"
P_BY_USER = "v2/message/get_by_user"
# 实测可用的前缀变体（网关对 /api/v1/message/get_by_user_init + cmd=200 也认）
P_BY_USER_FALLBACK = "api/v1/message/get_by_user_init"
P_CONV_MSGS = "v1/message/get_by_conversation"
P_SEND = "v1/message/send"
P_MARK_READ = "v3/conversation/mark_read"
P_READ_INDEX = "v3/conversation/get_read_index"
P_MIN_INDEX = "v3/conversation/get_min_index"
P_CONV_CREATE = "api/v1/im/conversation/create"
P_SEARCH_USERS = "api/v1/im/search/search_conversation_by_users"
P_TOKEN_ALT = "/api/v1/im/shop_creator/shop/user/token/get"
P_TOKEN = "/api/v1/oec/affiliate/seller/im/get/token"
P_SEARCH_UNAME = "/api/v1/im/shop_creator/shop/conversation/search"
P_RELATION = "/api/v1/affiliate/notification/im/relation/update"

try:
    import tiktok_pb2 as PB
    HAS_PB = True
except Exception:  # pragma: no cover
    PB = None
    HAS_PB = False


class IMError(RuntimeError):
    def __init__(self, msg, *, status=None, cmd=None, log_id=None):
        super().__init__(msg)
        self.status = status
        self.cmd = cmd
        self.log_id = log_id


def activate_shop(shop_key: str | None) -> None:
    """切店铺必须在 `tk01_affiliate` 取值之前生效 —— 它的 host/seller_id/端口是模块级常量。"""
    if not shop_key or shop_key == CFG.active_name():
        return
    CFG.set_active(shop_key)
    import importlib
    import tk01_affiliate
    importlib.reload(tk01_affiliate)
    globals()["AffiliateClient"] = tk01_affiliate.AffiliateClient


class IMClient:
    """站内 IM。token / api_url 动态取；传输走页面 Worker（同源，无 webmssdk 干扰）。"""

    def __init__(self, *, port: int | None = None, gap: float = 0.8,
                 shop: str | None = None, affiliate=None):
        activate_shop(shop)
        self.shop = CFG.load_shop(shop)
        self.region = self.shop["region"]
        self.seller_id = self.shop["seller_id"]
        # 复用调用方已有的联盟连接 —— 同一 CDP 端点起两个 Playwright sync 实例会报
        # "Playwright Sync API inside the asyncio loop"
        self.A = affiliate or AffiliateClient(port=port or self.shop["cdp_port"], gap=gap)
        self._owns_A = affiliate is None
        self.cfg: dict = {}
        self.token_at = 0.0
        self._seq = int(time.time() * 1000) % 10_000_000
        self._p_by_user: str | None = None
        # device_id 线上是浏览器侧生成；这里按店铺派生一个稳定值，避免每次请求都变
        self.device_id = "7" + str(abs(hash(self.seller_id)) % 10**18).zfill(18)

    # ────────────────────────── 配置 ──────────────────────────

    def refresh_config(self) -> dict:
        """取（或刷新）IM token 与 api_url。"""
        for path in (P_TOKEN_ALT, P_TOKEN):
            try:
                r = self.A.ch.call(path, None, method="GET")
            except Exception:
                continue
            d = (r or {}).get("data") or {}
            if d.get("token") and d.get("api_url"):
                self.cfg = d
                self.token_at = time.time()
                return self.cfg
        # 两个端点都失败时给最后一次的真实错误，不吞
        r = self.A.ch.call(P_TOKEN, None, method="GET")
        raise IMError(f"拿不到 IM token: {json.dumps(r, ensure_ascii=False)[:400]}")

    def _need(self) -> dict:
        if not self.cfg or (time.time() - self.token_at) > 600:
            self.refresh_config()
        return self.cfg

    @property
    def api_url(self) -> str:
        return (self._need().get("api_url") or "").rstrip("/") + "/"

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    @property
    def user_cursor(self) -> int:
        try:
            return int(self._need().get("user_cursor") or 0)
        except Exception:
            return 0

    @property
    def self_user_id(self) -> int:
        """我们自己的 IM user_id。

        两个 token 端点返回的字段名不同：
          /api/v1/im/shop_creator/shop/user/token/get → user.id
          /api/v1/oec/affiliate/seller/im/get/token   → user.user_id
        """
        u = self._need().get("user") or {}
        for k in ("user_id", "id", "uid"):
            if u.get(k) not in (None, ""):
                try:
                    return int(u[k])
                except Exception:
                    pass
        return 0

    # ────────────────────────── 信封 ──────────────────────────

    def build_request(self, cmd: int, body_field: str | None, payload,
                      *, sdk_version: str | None = None) -> bytes:
        if not HAS_PB:
            raise IMError("tiktok_pb2 不可用：先跑 `protoc --python_out=. tiktok.proto`")
        cfg = self._need()
        req = PB.Request()
        req.cmd = cmd
        req.sequence_id = self._next_seq()
        req.sdk_version = sdk_version or SDK_READ
        req.build_number = BUILD_NUMBER
        req.token = cfg.get("token") or ""
        req.device_id = self.device_id
        req.refer = 3
        req.inbox_type = 0
        req.device_platform = "web"
        req.auth_type = 2
        if body_field:
            getattr(req.body, body_field).CopyFrom(payload)
        return req.SerializeToString()

    @staticmethod
    def parse_response(raw: bytes):
        resp = PB.Response()
        resp.ParseFromString(raw)
        return resp

    def _check(self, resp, *, ok=(0,)):
        if resp.statusCode not in ok:
            raise IMError(f"cmd={resp.cmd} statusCode={resp.statusCode} "
                          f"{resp.errorDesc[:200]}", status=resp.statusCode,
                          cmd=resp.cmd, log_id=resp.logId)
        return resp

    # ────────────────────────── 传输 ──────────────────────────

    def _http(self, path: str, data: bytes, *, content_type: str,
              extra_headers: dict | None = None, base: str | None = None,
              timeout_ms: int = 25000, raw_text: bool = False):
        """在页面 Worker 里发请求。

        ⚠️ 不能用页面 fetch：联盟域上 webmssdk 会挂住 promise（见主文档 §27）。
        ⚠️ 不能用 about:blank iframe：Origin: null 会被判插件。
        Worker：同源 Origin、无 SDK、不需要页面在前台。
        """
        if not (data or b""):
            data = b"\x00"  # Worker 的 fetch body 不能为 undefined；JSON GET 另走 A.ch.call
        url = (base if base is not None else self.api_url) + path
        hdrs = {"content-type": content_type}
        if extra_headers:
            hdrs.update(extra_headers)
        b64 = base64.b64encode(data).decode()
        js = """(async () => {
          const b64 = %s, hdrs = %s, url = %s;
          const raw = atob(b64);
          const buf = new Uint8Array(raw.length);
          for (let i = 0; i < raw.length; i++) buf[i] = raw.charCodeAt(i);
          const code = `
            self.onmessage = async (ev) => {
              const { url, buf, hdrs } = ev.data;
              try {
                const r = await fetch(url, { method: 'POST', credentials: 'include',
                  headers: hdrs, body: buf });
                const ab = await r.arrayBuffer();
                const u8 = new Uint8Array(ab);
                let s = ''; for (let i = 0; i < u8.length; i += 8192)
                  s += String.fromCharCode.apply(null, u8.subarray(i, i + 8192));
                self.postMessage({ ok: true, status: r.status, b64: btoa(s) });
              } catch (e) { self.postMessage({ ok: false, err: String(e).slice(0,200) }); }
            };`;
          const w = new Worker(URL.createObjectURL(new Blob([code], {type:'application/javascript'})));
          const pr = new Promise(res => { w.onmessage = ev => res(ev.data); });
          w.postMessage({ url: url, buf: buf, hdrs: hdrs });
          const to = new Promise(res => setTimeout(() => res({ok:false, err:'TIMEOUT'}), %d));
          const res = await Promise.race([pr, to]);
          try { w.terminate(); } catch (e) {}
          return JSON.stringify(res);
        })()""" % (json.dumps(b64), json.dumps(hdrs), json.dumps(url), timeout_ms)
        self.A.ch._ensure()
        out = json.loads(self.A.ch._page.evaluate(js))
        if not out.get("ok"):
            raise IMError(f"IM 传输失败 {path}: {out.get('err')} "
                          f"(http={out.get('status')})")
        body = base64.b64decode(out["b64"])
        if raw_text:
            return out.get("status"), body.decode("utf-8", "replace")
        return out.get("status"), body

    def _json_post(self, path: str, obj: dict, **kw):
        status, txt = self._http(
            path, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
            content_type="application/json; charset=utf-8",
            extra_headers={"x-im-paas-token": self._need().get("token") or ""},
            raw_text=True, **kw)
        try:
            return json.loads(txt)
        except Exception:
            return {"_http_status": status, "_raw": txt[:800]}

    def _proto(self, path: str, cmd: int, body_field: str | None, payload, *,
               sdk_version: str | None = None, ok=(0,)):
        data = self.build_request(cmd, body_field, payload, sdk_version=sdk_version)
        _, raw = self._http(path, data, content_type="application/x-protobuf")
        resp = self.parse_response(raw)
        return self._check(resp, ok=ok)

    # ────────────────────── 会话索引（cmd=200 聚合） ──────────────────────

    @staticmethod
    def _parse_ext_json(v: str) -> dict:
        try:
            return json.loads(v) if v else {}
        except Exception:
            return {}

    def _fetch_page_cmd200(self, b):
        """cmd=200 的首选路径 + 自动回退（选中的路径缓存在实例上）。"""
        cands = ([self._p_by_user] if self._p_by_user else [P_BY_USER, P_BY_USER_FALLBACK])
        last = None
        for p in cands:
            try:
                resp = self._proto(p, CMD_MESSAGES_PER_USER, "messages_per_user_body", b)
                self._p_by_user = p
                return resp
            except IMError as e:
                last = e
                if "is empty" in str(e) or "not found" in str(e).lower() or e.status == 404:
                    continue
                raise
        raise last

    def fetch_messages(self, *, cursor: int = 0, limit: int = 50, new_user: int = 1,
                       max_pages: int = 10, on_page=None) -> list:
        """按 cmd=200 翻页拉全部消息（含系统命令事件）。"""
        if not HAS_PB:
            raise IMError("需要 tiktok_pb2")
        out, cur = [], int(cursor)
        for page in range(max_pages):
            b = PB.MessagesPerUserRequestBody()
            b.cursor = cur
            b.limit = limit
            b.new_user = new_user if page == 0 else 0
            b.interval = 0
            resp = self._fetch_page_cmd200(b)
            body = resp.body.messages_per_user_body
            msgs = list(body.messages)
            out += msgs
            if on_page:
                on_page(page, len(msgs), body.has_more, body.next_cursor)
            if not body.has_more or not body.next_cursor or body.next_cursor == cur:
                break
            cur = int(body.next_cursor)
            time.sleep(0.8)
        return out

    def init_cursor(self, *, cursor: int = 0) -> dict:
        """cmd=203：只用来读服务端 `per_user_cursor`（不发历史会话，见模块 docstring）。"""
        if not HAS_PB:
            raise IMError("需要 tiktok_pb2")
        b = PB.MessagesPerUserInitV2RequestBody()
        b.cursor = int(cursor)
        b.new_user = 0
        b.init_sub_type = 0
        resp = self._proto(P_BY_USER_INIT, CMD_CONV_INIT_V2,
                           "messages_per_user_init_v2_body", b)
        x = resp.body.messages_per_user_init_v2_body
        return {"per_user_cursor": int(x.per_user_cursor), "has_more": x.has_more,
                "conversations": len(x.conversations), "messages": len(x.messages)}

    @staticmethod
    def _meta_from_message(m, acc: dict, self_id: int = 0):
        """把一条 MessageBody 的信息并进会话聚合体。"""
        cid = m.conversation_id
        c = acc.setdefault(cid, {
            "conversation_id": cid,
            "short_id": int(m.conversation_short_id or 0) or (int(cid) if cid.isdigit() else 0),
            "type": m.conversation_type,
            "creator_oec_id": None,
            "shop_oec_id": None,
            "handle": None,
            "participants": set(),
            "msg_count": 0,
            "first_time": None,
            "last_time": None,
            "last_text": None,
            "last_sender": None,
            "creator_im_id": None,
            "creator_replied": False,
            "creator_text_count": 0,
            "first_creator_reply_time": None,
            "messages": [],
        })
        c["msg_count"] += 1
        ct = int(m.create_time or 0)
        if ct:
            c["first_time"] = ct if not c["first_time"] else min(c["first_time"], ct)
            c["last_time"] = ct if not c["last_time"] else max(c["last_time"], ct)
        if m.sender:
            c["participants"].add(int(m.sender))
        ext = dict(m.ext)

        # 建会话事件(command_type:8) 的 ext 直接带 shop_oec_id / creator_oec_id
        if ext.get("creator_oec_id"):
            c["creator_oec_id"] = ext["creator_oec_id"]
        if ext.get("shop_oec_id"):
            c["shop_oec_id"] = ext["shop_oec_id"]
        if ext.get("uname"):
            c["handle"] = ext["uname"]
        # 兜底：从 participants 里挑非自己、非 0 的
        if not c["creator_oec_id"]:
            for p in c["participants"]:
                if p not in (0, int(self_id or 0)):
                    c.setdefault("_cand", set()).add(p)

        # 真实文本消息
        if int(m.message_type or 0) == MSG_TEXT:
            role = ext.get("sender_im_role")
            body = (m.content or "").strip()
            c["last_text"] = m.content
            c["last_sender"] = int(m.sender or 0)
            c["last_text_time"] = ct
            c["messages"].append({
                "sender": int(m.sender or 0),
                "role": role,                       # "2"=店铺 "4"=达人
                "time": ct,
                "text": m.content,
                "idx": int(m.index_in_conversation or 0),
                "im_id": ext.get("sender_im_id"),
            })
            if role == ROLE_CREATOR and ext.get("uname"):
                c["handle"] = c["handle"] or ext["uname"]
            if role == ROLE_CREATOR:
                c["creator_im_id"] = ext.get("sender_im_id") or str(m.sender or "")
                # ★ 新建会话会带一条 **空内容 + sender_im_role=4** 的系统通知。
                #   它不算"达人回话"，但 sender 就是达人的 im_id（很有用）。
                if body:
                    c["creator_replied"] = True
                    c["creator_text_count"] = c.get("creator_text_count", 0) + 1
                    c["first_creator_reply_time"] = min(
                        c.get("first_creator_reply_time") or ct, ct)
                else:
                    c["creator_notice_only"] = True
        return c

    def build_index(self, *, max_pages: int = 10, quiet: bool = True) -> dict:
        """聚合出会话索引：conversation_id → 达人映射 + 最后一条消息。"""
        self_id = self.self_user_id
        msgs = self.fetch_messages(max_pages=max_pages)
        acc: dict = {}
        for m in msgs:
            IMClient._meta_from_message(m, acc, self_id)
        for c in acc.values():
            c["participants"] = sorted(c["participants"])
            cand = c.pop("_cand", None)
            if not c["creator_oec_id"] and cand:
                # 只有当建会话事件里没带 creator_oec_id 时才会走到这。
                # participant 里那个非自己的 im_id ≠ creator_oec_id，别混用 ——
                # 单独存成候选人，避免后面拿它当 oec_id 去匹配邀约组。
                other = [p for p in cand if p != self_id]
                c["unmatched_participants"] = other
                if other and not c.get("creator_im_id"):
                    c["creator_im_id"] = str(other[0])
            c["messages"].sort(key=lambda x: (x["time"], x["idx"]))
            c["text_count"] = len(c["messages"])
            c["self_user_id"] = self_id
            c["digit"] = c["last_time"] or 0
        idx = {"self_user_id": self_id, "api_url": self.api_url,
               "token_user_cursor": self.user_cursor,
               "fetched_at": int(time.time() * 1000),
               "message_count": len(msgs),
               "conversations": sorted(acc.values(), key=lambda x: -x["digit"])}
        return idx

    def save_index(self, idx: dict | None = None, name: str = "im_conversations.json") -> Path:
        idx = idx or self.build_index()
        p = HERE / "notes" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(idx, ensure_ascii=False, indent=2, default=str),
                     encoding="utf-8")
        return p

    @staticmethod
    def load_index(name: str = "im_conversations.json") -> dict:
        p = HERE / "notes" / name
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    def find_conversation(self, *, creator_oec_id: str | None = None,
                          handle: str | None = None, index: dict | None = None) -> dict | None:
        """在索引里按 creator_oec_id 或 handle 找会话。"""
        idx = index or IMClient.load_index()
        if not idx:
            idx = self.build_index()
        for c in idx.get("conversations", []):
            if creator_oec_id and str(c.get("creator_oec_id")) == str(creator_oec_id):
                return c
            if handle and (c.get("handle") or "").lower() == str(handle).lower():
                return c
        return None

    # ────────────────────── 会话消息 / 发送 / 已读 ──────────────────────

    def conversation_messages(self, conversation_id: str, *, short_id: int | None = None,
                              limit: int = 20, direction: int = 1,
                              anchor_index: int = 0, conversation_type: int = 2) -> list:
        """cmd=301 读会话内消息。`conversation_short_id` 必填否则报 `conShortId is 0`。"""
        b = PB.MessagesInConversationRequestBody()
        b.conversation_id = str(conversation_id)
        b.conversation_short_id = int(short_id if short_id is not None
                                      else (conversation_id if str(conversation_id).isdigit() else 0))
        b.conversation_type = conversation_type
        b.direction = direction
        b.anchor_index = anchor_index
        b.limit = limit
        resp = self._proto(P_CONV_MSGS, CMD_MESSAGES, "messages_in_conversation_body", b)
        body = resp.body.messages_in_conversation_body
        return list(body.messages), {"has_more": body.has_more,
                                     "next_cursor": int(body.next_cursor),
                                     "log_id": resp.logId}

    def _text_ext(self, text: str, client_msg_id: str) -> dict:
        """店铺→达人的文本消息 ext。字段对齐线上客户端（见模块 docstring）。"""
        now = int(time.time() * 1000)
        reg = self.region
        return {
            "PIGEON_BIZ_TYPE": "1",
            "monitor_send_message_platform": "pc",
            "monitor_send_message_start_time": str(now),
            "type": "text",
            "original_content": text,
            "detect_lang": "",
            "a:translate_status": "0",
            "sender_role": ROLE_SHOP,
            "a:user_language": "zh",
            "shop_region": reg,
            "target_lang": reg.lower(),
            "source_lang": "zh",
            "is_cross_board": "1",
            "cross_board_region": reg,
            "shop_id": self.seller_id,
            "s:mentioned_users": "",
            "s:client_message_id": client_msg_id,
        }

    def send_text(self, conversation_id: str, text: str, *, short_id: int | None = None,
                  conversation_type: int = 2, apply: bool = False) -> dict:
        """cmd=100 发文本。**写操作**；apply=False 只回放报文不发。"""
        cid = str(conversation_id)
        sid = int(short_id if short_id is not None else (cid if cid.isdigit() else 0))
        client_msg_id = str(uuid.uuid4())
        b = PB.SendMessageRequestBody()
        b.conversation_id = cid
        b.conversation_short_id = sid
        b.conversation_type = conversation_type
        b.content = text
        b.mentioned_users.extend([])
        b.client_message_id = client_msg_id
        b.ticket = "deprecated"
        b.message_type = MSG_TEXT
        for k, v in self._text_ext(text, client_msg_id).items():
            b.ext[k] = v
        payload = self.build_request(CMD_SEND, "send_message_body", b,
                                     sdk_version=SDK_WRITE)
        if not apply:
            return {"dry_run": True, "conversation_id": cid, "short_id": sid,
                    "text": text, "bytes": len(payload),
                    "client_message_id": client_msg_id,
                    "hex_head": payload[:64].hex()}

        _, raw = self._http(P_SEND, payload, content_type="application/x-protobuf")
        resp = self.parse_response(raw)
        out = {"conversation_id": cid, "statusCode": resp.statusCode,
               "errorDesc": resp.errorDesc, "logId": resp.logId,
               "client_message_id": client_msg_id}
        if resp.statusCode == 0:
            sb = resp.body.send_message_body
            out.update({"server_message_id": int(sb.server_message_id),
                        "status": sb.status, "check_code": sb.check_code,
                        "check_message": sb.check_message,
                        "filtered_content": sb.filtered_content,
                        "is_async_send": sb.is_async_send,
                        "filter_reason": sb.filter_reason})
        try:
            from tk01_log import log_run
            log_run("im_send", target=cid, ok=(resp.statusCode == 0),
                    params={"text_len": len(text), "short_id": sid},
                    result={"statusCode": resp.statusCode, "err": resp.errorDesc[:200],
                            "server_message_id": out.get("server_message_id")},
                    note="tk01_im.send_text")
        except Exception:
            pass
        return out

    def send_batch(self, targets: list, text: str, *, gap: float | None = None,
                   apply: bool = False, max_send: int = 50,
                   stop_on_error_streak: int = 3, progress=None) -> dict:
        """批量发文本。

        `targets`: [{conversation_id, short_id, creator_oec_id?, handle?}]
        节流：默认 4~9s 随机间隔 —— 站内 IM 有频控，固定间隔短打容易吃验证码。
        """
        results, sent, failed, streak = [], 0, 0, 0
        for i, t in enumerate(targets[:max_send]):
            cid = str(t.get("conversation_id") or "")
            if not cid:
                results.append({"conversation_id": None, "ok": False,
                                "error": "缺少 conversation_id", "target": t})
                continue
            try:
                r = self.send_text(cid, text, short_id=t.get("short_id"), apply=apply)
                ok = bool(r.get("dry_run")) or r.get("statusCode") == 0
                rec = {"conversation_id": cid, "ok": ok,
                       "creator_oec_id": t.get("creator_oec_id"),
                       "handle": t.get("handle"), "result": r}
                if ok:
                    sent += 1
                    streak = 0
                else:
                    failed += 1
                    streak += 1
                results.append(rec)
                if progress:
                    progress(i + 1, len(targets), rec)
            except Exception as e:
                failed += 1
                streak += 1
                results.append({"conversation_id": cid, "ok": False,
                                "creator_oec_id": t.get("creator_oec_id"),
                                "error": str(e)[:300]})
                if progress:
                    progress(i + 1, len(targets), results[-1])
            if streak >= stop_on_error_streak:
                results.append({"aborted": True,
                                "reason": f"连续 {streak} 次失败，疑似触发频控"})
                break
            if i + 1 < min(len(targets), max_send):
                time.sleep(random.uniform(*(gap and (gap, gap * 1.6) or (4.0, 9.0))))
        try:
            from tk01_log import log_run
            log_run("im_batch", target=f"{len(targets)}个目标", ok=(failed == 0),
                    params={"text": text[:120], "apply": apply, "gap": gap},
                    result={"sent": sent, "failed": failed, "total": len(results)},
                    note="tk01_im.send_batch")
        except Exception:
            pass
        return {"applied": apply, "text": text, "sent": sent, "failed": failed,
                "results": results}

    def mark_read(self, conversation_id: str, *, short_id: int | None = None,
                  read_index: int | None = None, apply: bool = False) -> dict:
        """cmd=604 标记已读。"""
        cid = str(conversation_id)
        b = PB.MarkConversationReadRequestBody()
        b.conversation_id = cid
        b.conversation_short_id = int(short_id if short_id is not None
                                      else (cid if cid.isdigit() else 0))
        b.conversation_type = 2
        if read_index:
            b.read_message_index = int(read_index)
            b.read_message_index_v2 = int(read_index)
        b.conv_unread_count = 0
        b.ticket = ""
        payload = self.build_request(CMD_MARK_READ, "mark_conversation_read_body", b)
        if not apply:
            return {"dry_run": True, "conversation_id": cid, "bytes": len(payload)}
        _, raw = self._http(P_MARK_READ, payload, content_type="application/x-protobuf")
        resp = self.parse_response(raw)
        return {"conversation_id": cid, "statusCode": resp.statusCode,
                "errorDesc": resp.errorDesc, "logId": resp.logId}

    def get_read_index(self, conversation_id: str, short_id: int | None = None) -> dict:
        cid = str(conversation_id)
        b = PB.GetConversationParticipantsReadIndexV3RequestBody()
        b.conversation_id = cid
        b.conversation_short_id = int(short_id if short_id is not None
                                      else (cid if cid.isdigit() else 0))
        b.conversation_type = 2
        resp = self._proto(P_READ_INDEX, CMD_READ_INDEX,
                           "participants_read_index_body", b)
        body = resp.body.participants_read_index_body
        return {"conversation_id": cid,
                "rows": [{"uid": r.user_id, "sec_uid": r.sec_uid, "index": r.index,
                          "index_v2": r.index_v2, "index_min": r.index_min}
                         for r in body.indexes],
                "log_id": resp.logId}

    # ────────────────────── 建会话 / 搜会话（JSON） ──────────────────────

    def create_conversation(self, creator_oec_id: str, *, shop_user_id: str | None = None,
                            apply: bool = False) -> dict:
        """对**没聊过**的达人建会话（JSON 端点 + x-im-paas-token）。

        `participants`: role 0 = 达人(uid=creator_oec_id, sender_im_role=4)
                       role 1 = 店铺(uid=**seller_id**, sender_im_role=2)

        ★ role 1 的 uid 是**店铺 id**(`shopInfo.shop_id`)，不是 IM 的 `user.user_id`。
          传 IM user_id 会得到 `98001004 invalid params`（实测）。
        返回 `data.conversation_id`（等于 conversation_short_id），可直接用来发消息。
        """
        cfg = self._need()
        # 线上客户端传的就是 shop_id；shop_user_id 只作为显式覆盖口子
        me = str(shop_user_id or self.seller_id or "")
        body = {"participants": [
            {"role": 0, "uid": str(creator_oec_id), "extra": {"sender_im_role": ROLE_CREATOR}},
            {"role": 1, "uid": me, "extra": {"sender_im_role": ROLE_SHOP}},
        ]}
        if not apply:
            return {"dry_run": True, "url": self.api_url + P_CONV_CREATE,
                    "body": body, "oec_region": self.region,
                    "token_on_request": bool(cfg.get("token"))}
        q = f"?oec_region={self.region}"
        r = self._json_post(P_CONV_CREATE + q, body)
        d = (r or {}).get("data") or {}
        return {"code": r.get("code"), "message": r.get("message"),
                "conversation_short_id": d.get("conversation_short_id"),
                "conversation_id": d.get("conversation_id") or d.get("conversation_short_id"),
                "raw": r if r.get("code") != 0 else None}

    def search_by_uname(self, uname: str, *, cursor: int = 0) -> dict:
        """按达人 handle 在联盟侧搜会话（JSON GET）。"""
        return self.A.ch.call(P_SEARCH_UNAME, None, method="GET",
                              params={"oec_region": self.region, "biz": "shop_creator",
                                      "role": "shop", "cursor": str(cursor),
                                      "uname": uname})

    def search_by_users(self, user_name: str, *, page_no: int = 0,
                        page_size: int = 20) -> dict:
        """在 IM 侧按用户名搜会话（JSON POST）。"""
        q = f"?aid={self.shop['aid']}&page_no={page_no}&page_size={page_size}"
        return self._json_post(P_SEARCH_USERS + q,
                               {"user_name": user_name, "page_no": page_no,
                                "page_size": page_size})

    def notify_relation(self, creator_oec_id: str, action_type: int = 1,
                        apply: bool = False) -> dict:
        """通知服务端「这个达人在我的 IM 关系里建/删」（action_type 1=加 2=删）。"""
        body = {"source": {"role": 2, "user_id": self.seller_id},
                "target": {"role": 1, "user_id": str(creator_oec_id)},
                "action_type": action_type}
        if not apply:
            return {"dry_run": True, "body": body}
        q = f"?aid={self.shop['aid']}&app_name=i18n_ecom_alliance"
        return self.A.ch.call(P_RELATION + q, body, method="POST")

    def close(self):
        if self._owns_A:
            self.A.close()


# ─────────────────────────── CLI ───────────────────────────

def _fmt_time(ms) -> str:
    if not ms:
        return "-"
    import datetime
    try:
        return datetime.datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ms)


def main() -> None:
    ap = argparse.ArgumentParser(description="TikTok Shop 站内 IM")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--shop", default=None, help="店铺 key（shops.json）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("token")
    p = sub.add_parser("init"); p.add_argument("--cursor", type=int, default=0)
    p = sub.add_parser("index"); p.add_argument("--pages", type=int, default=6)
    p.add_argument("--save", action="store_true")

    p = sub.add_parser("conv"); p.add_argument("conversation_id")
    p.add_argument("--short-id", type=int, default=None); p.add_argument("--limit", type=int, default=20)
    p = sub.add_parser("read"); p.add_argument("conversation_id"); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("send"); p.add_argument("conversation_id"); p.add_argument("text")
    p.add_argument("--short-id", type=int, default=None); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("batch"); p.add_argument("--conv", default=""); p.add_argument("--creators", default="")
    p.add_argument("--text", required=True); p.add_argument("--yes", action="store_true")
    p.add_argument("--gap", type=float, default=None); p.add_argument("--max", type=int, default=50)
    p = sub.add_parser("create"); p.add_argument("creator_oec_id"); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("find"); p.add_argument("handle")
    p = sub.add_parser("search"); p.add_argument("user_name")
    a = ap.parse_args()

    M = IMClient(port=a.port, shop=a.shop)
    try:
        if a.cmd == "token":
            c = M.refresh_config()
            for k in ("api_url", "ws_url", "app_id", "fp_id", "app_key",
                      "biz_service_id", "frontier_service_id", "region_code",
                      "shop_region", "user_cursor"):
                print(f"  {k:20} {str(c.get(k))[:70]}")
            print(f"  token                {str(c.get('token'))[:40]}…")
            print(f"  user                 {json.dumps(c.get('user'), ensure_ascii=False)}")
        elif a.cmd == "init":
            print(json.dumps(M.init_cursor(cursor=a.cursor), ensure_ascii=False))
        elif a.cmd == "index":
            idx = M.build_index(max_pages=a.pages)
            cs = idx["conversations"]
            print(f"  消息 {idx['message_count']} 条 → 会话 {len(cs)} 个"
                  f"（self={idx['self_user_id']}, user_cursor={idx['token_user_cursor']}）")
            for c in cs:
                print(f"    {c['conversation_id']:22} short={str(c['short_id']):20} "
                      f"达人={str(c['creator_oec_id']):22} @{str(c['handle'])[:18]:20} "
                      f"消息={c['msg_count']:<4} 最后={_fmt_time(c['last_time'])}  "
                      f"{(c['last_text'] or '')[:40]!r}")
            if a.save:
                print(f"  已存 {M.save_index(idx)}")
        elif a.cmd == "conv":
            msgs, meta = M.conversation_messages(a.conversation_id, short_id=a.short_id,
                                                 limit=a.limit)
            print(f"  消息 {len(msgs)} 条 has_more={meta['has_more']} logId={meta['log_id']}")
            for m in msgs:
                who = "我" if str(m.sender) == str(M.self_user_id) else str(m.sender)
                tag = "文本" if m.message_type == MSG_TEXT else f"cmd{m.message_type}"
                print(f"    [{_fmt_time(m.create_time)}] {who} {tag} {str(m.content)[:100]!r}")
        elif a.cmd == "read":
            print(json.dumps(M.mark_read(a.conversation_id, apply=a.yes),
                             ensure_ascii=False))
        elif a.cmd == "send":
            r = M.send_text(a.conversation_id, a.text, short_id=a.short_id, apply=a.yes)
            print(json.dumps(r, ensure_ascii=False, indent=2))
        elif a.cmd == "batch":
            idx = IMClient.load_index() or M.build_index()
            by_id = {str(c["conversation_id"]): c for c in idx["conversations"]}
            by_creator = {str(c.get("creator_oec_id")): c for c in idx["conversations"]
                          if c.get("creator_oec_id")}
            targets, missing = [], []
            for cid in [x for x in a.conv.split(",") if x]:
                (targets.append(by_id[cid]) if cid in by_id
                 else missing.append(("conv", cid)))
            for oid in [x for x in a.creators.split(",") if x]:
                (targets.append(by_creator[oid]) if oid in by_creator
                 else missing.append(("creator", oid)))
            print(f"  命中会话 {len(targets)} 个，未命中 {len(missing)} 个: {missing}")
            if not targets:
                return
            res = M.send_batch(targets, a.text, gap=a.gap, apply=a.yes, max_send=a.max,
                               progress=lambda i, n, r: print(
                                   f"    [{i}/{n}] {r.get('conversation_id')} "
                                   f"{'ok' if r.get('ok') else 'FAIL ' + str(r.get('error') or r.get('result'))[:80]}"))
            print(f"  applied={res['applied']} sent={res['sent']} failed={res['failed']}")
        elif a.cmd == "create":
            print(json.dumps(M.create_conversation(a.creator_oec_id, apply=a.yes),
                             ensure_ascii=False, indent=2))
        elif a.cmd == "find":
            print(json.dumps(M.search_by_uname(a.handle), ensure_ascii=False)[:1500])
        elif a.cmd == "search":
            print(json.dumps(M.search_by_users(a.user_name), ensure_ascii=False)[:1500])
    except IMError as e:
        print(f"  ✗ {e}")
        sys.exit(2)
    finally:
        M.close()




if __name__ == "__main__":
    main()
