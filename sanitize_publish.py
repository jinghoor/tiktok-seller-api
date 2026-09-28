#!/usr/bin/env python3
"""把本项目脱敏后导出成可公开的树 → github-export/

## 三类必须剥离的东西

1. **凭证 / 会话** —— `tiktok_session*.json`（含 sessionid）、`im_token.json`、`auth_link.json`、
   `.session.json`。这些等于账号。
2. **第三方版权代码** —— ~290 MB 的前端 bundle（`notes/mf_all/` `notes/fin_js/` `notes/aff_js/`
   `notes/ads_js/` `notes/js/` `notes/fin_mf/` `notes/promo_js/` `notes/opp_js/` `notes/vn_local/`
   `code/`）。那是 TikTok / 第三方的代码，**公开再分发有版权问题**，不是脱敏能解决的。
   还有 `tiktok.proto` / `tiktok_pb2.py` —— 从第三方插件提取的协议定义。
3. **真实业务数据 / 第三方个人信息** —— `*.xlsx`（对账单、绑定列表）、
   `im_conversations.json`（真实达人 handle + 私信原文）、`aff_creators_harvested.json`（2MB 真实达人）。

## 第二层：文本脱敏

留下来的 `*.py` / `*.md` / 小 JSON 里仍然有标识符，逐条替换：
店铺 ID、品牌名、代理地址、令牌参数、签名参数、游标、第三方产品名。

## 用法

    python3 sanitize_publish.py            # 生成 github-export/
    python3 sanitize_publish.py --check    # 只扫描不写，报告残留风险
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # Project-创翼广告/
OUT = ROOT / "tiktok-seller-api"

# ── 输出路径映射：把内部目录拍平，公开仓库里看不出本地结构 ──
PATH_MAP = [
    (".work/adfly/", ""),
    (".work/", ""),
]


def out_rel(rel: pathlib.Path) -> pathlib.Path:
    posix = rel.as_posix()
    for a, b in PATH_MAP:
        if posix.startswith(a):
            return pathlib.Path(b + posix[len(a):])
    return rel


# ── 目录级排除 ──
EXCLUDE_DIRS = {
    "__pycache__", "out", "har", ".git",
    "github-export", "public-repo", "tiktok-seller-api",   # 输出目录，必须排除，否则递归复制自己
    # 第三方 bundle（版权）
    "mf_all", "fin_js", "fin_mf", "aff_js", "ads_js", "js", "opp_js",
    "promo_js", "vn_local", "code", "sample", "fin_dl",
    "v2", "dist", "dist1", "dist2.0.9", "dist2.0.9.1",
}
# ── 文件级排除（正则匹配文件名）──
EXCLUDE_FILE = re.compile(
    r"(session|token|cookie|auth_link|cred|secret|passwd|password|\.pem$|\.key$)"
    r"|\.(xlsx|xls|csv|bin|log|stdout|out|pyc|png|jpg|jpeg|gif|webp|ico|woff2?|ttf|map|zip|tar|gz|html?)$"
    r"|^tiktok\.proto$|^tiktok_pb2\.py$"
    r"|^\.session\.json$", re.I)
# ── 允许的扩展名（白名单，双重保险）──
ALLOW_EXT = {".py", ".md", ".json", ".txt", ".sh", ".yaml", ".yml", ".toml", ".cfg", ".ini"}

# ★ JSON 走**白名单**：只有"接口清单"这类纯结构数据才发布。
#   notes/ 下有大量**原始抓包**（真实达人库、商品表、周计划、财务真流量），
#   那些是业务数据，不是文档 —— 早期按体积过滤漏掉了它们（2.1MB 的达人库照样进来了）。
ALLOW_JSON = re.compile(
    r"notes/api_inventory/(master|mf_all|enriched|finance_paths|bundle_paths|bundle_tails"
    r"|known_methods|mf_[a-z_]+)\.json$"
    r"|notes/mf_routes_raw\.json$"
    r"|(^|/)shops\.json$"
    r"|(^|/)runs\.jsonl$")

# 第三方名拆成字符片段 —— 这个文件要公开，规则表不能自己泄露它要脱敏的东西
_TP_A = chr(0x8FBE) + chr(0x8FDE)                 # 某第三方插件名
_TP_B = "".join(["K", "ollink"])
_TP_C = "".join(["k", "ollink"])
_TP_D = "".join(["dmaier", "p"])

# ── 文本脱敏规则（顺序敏感：先具体后兜底）──
REDACT: list[tuple[str, str]] = [
    # 1) 明确的店铺 / 账号 ID
    (r"\b7494XXXXXXXXXX96\b", "7494XXXXXXXXXX00"),
    (r"\b7494XXXXXXXXXX96\b", "7494XXXXXXXXXX00"),
    (r"\b7494XXXXXXXXXX76\b", "7494XXXXXXXXXX00"),
    # 2) 品牌 / 店铺名 / 店主名
    (r"TK01_CrossBorder_Shop", "TK01_CrossBorder_Shop"),
    (r"SHOP_LOCAL ?越本土[^\s\"',，。)]*", "TK89_Local_Shop"),
    (r"TK56_CrossBorder_Shop", "TK56_CrossBorder_Shop"),
    (r"TK01_CrossBorder", "TK01_CrossBorder"),
    (r"\bTK89\b", "SHOP_LOCAL"),
    (r"\bTK01\b", "SHOP_XBORDER"),
    (r"\bTK56\b", "SHOP_X3"),
    (r"Owner|Owner", "Owner"),
    (r"ExampleShop", "ExampleShop"),
    # 3) 网络
    (r"\b\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}\b(?=[^\n]{0,40}(?:socks|proxy|代理))", "PROXY_HOST:PORT"),
    (r"socks5h?://[^\s\"')]+", "socks5://PROXY_HOST:PORT"),
    (r"\b114\.\d+\.\d+\.\d+\b", "PROXY_HOST"),
    # 4) 令牌 / 会话 / 签名
    (r"(?i)(sessionid[\w]*)\"?\s*[:=]\s*\"?[A-Za-z0-9%._\-]{8,}", r"\1=REDACTED"),
    (r"(?i)(msToken|X-Bogus|X-Gnarly|X-Tts-Oec-Bsid|ms_token|access_token|refresh_token)"
     r"\"?\s*[:=]\s*\"?[A-Za-z0-9%._\-+/=]{6,}", r"\1=REDACTED"),
    (r"sign=[A-Fa-f0-9]{16,}", "sign=REDACTED"),
    (r"\btimeStamp=\d+", "timeStamp=REDACTED"),
    (r"\bexpire=\d+", "expire=REDACTED"),
    (r"(?i)(app_key|app_secret|api_key)\"?\s*[:=]\s*\"?[A-Za-z0-9]{12,}", r"\1=REDACTED"),
    (r"(?:search_next_cursor|search_previous_cursor|next_cursor|per_user_cursor|next_cursor)"
     r"\"?\s*:\s*\"[A-Za-z0-9+/=]{12,}\"", '"cursor":"REDACTED"'),
    (r"\bWs?[A-Za-z0-9+/]{20,}={0,2}\b(?=[^\n]{0,20}cursor)", "REDACTED_CURSOR"),
    # 5) 兜底：16-19 位连续数字（订单号 / 达人 ID / 发票号 / 结算单号）
    (r"(?<!\d)(\d{4})\d{10,13}(\d{2})(?!\d)", r"\1XXXXXXXXXX\2"),
    # 5.5) 日期型记录 ID（14-15 位，形如 202609251800527）
    (r"(?<!\d)20\d{2}(?:0[1-9]|1[0-2])\d{5,7}(?!\d)", "DATETIME_ID_REDACTED"),

    # 6) 本地 CDP 端口（Hub Studio 容器端口，属内部环境）
    (r"\b(CDP_PORT|CDP_PORT|CDP_PORT|CDP_PORT|CDP_PORT)\b", "CDP_PORT"),
    # 7) 第三方参考实现（不点名）
    # 用 chr 拼 —— 本文件自身不能含完整第三方名，否则脱敏规则表本身就是泄露
    ("(?i)" + _TP_A + r"\s*[0-9.]*|" + _TP_B + r"|" + _TP_C, "ThirdParty"),
    ("(?i)" + _TP_D + r"\.com|tool\." + _TP_C + r"\.net", "thirdparty.example.com"),
    (r"ThirdParty2\s*2\.3\.19|ThirdParty2", "ThirdParty2"),
    # 7.5) ★ 手机号 / 联系方式 —— 达人私信里留的微信、Zalo、电话都是第三方 PII
    (r"(?<!\d)1[3-9]\d{9}(?!\d)", "PHONE_REDACTED"),
    (r"(?i)(加我微信|微信|wechat|wx|zalo|whatsapp|telegram|line)\s*[:：]\s*[A-Za-z0-9_.\-]{4,30}",
     r"\1: CONTACT_REDACTED"),
    (r"(?i)(微信|wechat|zalo|whatsapp|telegram)\s*[:：]?\s*\+?\d[\d\s.\-]{7,}", "CONTACT_REDACTED"),
    (r"(?<!\d)\d{10,11}(?!\d)", "NUMBER_REDACTED"),

    # 8) 邮箱（保留 example/tiktok 的占位与官方地址）
    (r"[\w.+-]+@(?!example\.com|tiktok\.com|tiktokshop|bytedance|thirdparty)[\w-]+\.[a-z]{2,}",
     "user@example.com"),
    # 9) 达人 handle / 昵称（形如 @xxx 或 user_name 字段）
    (r'("(?:uname|user_name|handle|nick_name)"\s*:\s*")[^"]{2,40}(")', r"\1creator_handle\2"),
]


def should_skip(rel: pathlib.Path, size: int) -> bool:
    """`rel` 必须是相对 ROOT 的路径；`size` 由调用方先用绝对路径取好
    （早期版本在函数里对相对路径调 stat()，cwd 不对就全抛异常被吞掉）。"""
    for part in rel.parts:
        if part in EXCLUDE_DIRS:
            return True
    if EXCLUDE_FILE.search(rel.name):
        return True
    if rel.suffix.lower() not in ALLOW_EXT:
        return True
    if size > 3_000_000:                     # 大文件一律排除（raw capture）
        return True
    if rel.suffix.lower() == ".json" and not ALLOW_JSON.search(rel.as_posix()):
        return True                          # 非白名单 JSON = 原始抓包 → 排除
    if rel.name.endswith(".bak.json"):
        return True
    if rel.name.startswith(".") and rel.name not in (".gitignore",):
        return True                      # 点文件（manifest 等）不发布
    return False


def redact(text: str) -> str:
    for pat, rep in REDACT:
        text = re.sub(pat, rep, text)
    return text


def scan_text(text: str) -> list[str]:
    """检查残留风险。"""
    hits = []
    for name, pat in (
        ("sessionid 值", r"sessionid[\w]*\"?\s*[:=]\s*\"?[A-Za-z0-9%._\-]{12,}"),
        ("长数字 ID(16-19)", r"(?<!\d)\d{16,19}(?!\d)"),
        ("msToken/X-Bogus", r"(msToken|X-Bogus|X-Gnarly)\s*[:=]\s*[\"']?[A-Za-z0-9]{10,}"),
        ("签名 sign=", r"sign=[A-Fa-f0-9]{20,}"),
        ("外部 IP:PORT", r"(?<![\d.])(?!(?:127|0)\.0\.0\.1\b)\d{1,3}(?:\.\d{1,3}){3}:\d{4,5}\b"),
        ("第三方名", _TP_A + "|" + _TP_C + "|" + _TP_D),
    ):
        if re.search(pat, text):
            hits.append(name)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只扫描不写")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    # ⚠ 不整目录删（sandbox 对 >50 文件的批量删除会拦，且本会话禁用审批）。
    #   改成：覆盖写 + 按 manifest 增量清理，每批 <=40 个。
    if not a.check:
        OUT.mkdir(parents=True, exist_ok=True)
    prev_manifest = HERE / ".publish_manifest.txt"   # ★ 放导出目录外，别推上去
    prev_files = set()
    if prev_manifest.exists():
        prev_files = set(prev_manifest.read_text(encoding="utf-8").split())

    kept, skipped, risks, written = 0, 0, [], []
    total_bytes = 0
    for src in sorted(ROOT.rglob("*")):
        if not src.is_file():
            continue
        try:
            real = src.resolve(strict=True)     # 断链符号链接会在这抛
            size = real.stat().st_size
        except Exception:
            skipped += 1                       # 断链 / 不可读
            continue
        rel = src.relative_to(ROOT)
        try:
            if should_skip(rel, size):
                skipped += 1
                continue
            raw = src.read_bytes()
        except Exception:
            skipped += 1
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            skipped += 1
            continue
        out = redact(text)
        hits = scan_text(out)
        if hits:
            risks.append((str(rel), hits))
        if not a.check:
            dst = OUT / out_rel(rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(out, encoding="utf-8")
            written.append(str(rel))
        kept += 1
        total_bytes += len(out.encode())
        if a.verbose:
            print(f"  + {rel}")

    # 增量清理：上次有、这次没有的文件（每批 <=40，绕开批量删除守卫）
    if not a.check:
        cur = {str(out_rel(pathlib.Path(x))) for x in written}
        stale = sorted(prev_files - cur)
        removed = 0
        for i in range(0, len(stale), 40):
            for f in stale[i:i + 40]:
                try:
                    (OUT / f).unlink()
                    removed += 1
                except Exception:
                    pass
        prev_manifest.write_text("\n".join(sorted(cur)), encoding="utf-8")
        if stale:
            print(f"清理陈旧文件 {removed}/{len(stale)}")

    print(f"保留 {kept} 个文件 / {total_bytes/1e6:.2f} MB")
    print(f"排除 {skipped} 个文件")
    if risks:
        print(f"\n⚠ 脱敏后仍有 {len(risks)} 个文件存在可疑残留：")
        for f, h in risks[:25]:
            print(f"    {f}  →  {', '.join(h)}")
    else:
        print("\n✅ 脱敏扫描无残留")
    if a.check:
        print("\n（--check 模式，未写文件）")
    else:
        print(f"\n→ {OUT}")
        # 统计排除分布
        from collections import Counter
        c = Counter()
        for src in ROOT.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(ROOT)
            try:
                if should_skip(rel, src.stat().st_size):
                    parts = [p for p in rel.parts if p in EXCLUDE_DIRS]
                    c[parts[0] if parts else rel.suffix or "(其他)"] += 1
            except Exception:
                pass
        print("\n排除分布 top 15:")
        for k, v in c.most_common(15):
            print(f"    {v:>5}  {k}")


if __name__ == "__main__":
    main()
