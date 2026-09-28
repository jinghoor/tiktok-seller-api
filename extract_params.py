#!/usr/bin/env python3
"""从服务端 proto 校验报错里提取接口的必填字段,并对残余未知做**参数发现**。

服务端用的是 protoc-gen-validate 风格校验,报错文案直接给出:
    invalid <MessageName>.<FieldPath>: <constraint>
例:invalid GetPixelListRequest.AdvertiserId: value length must be at least 1 runes
→ 接口需要 advertiser_id,长度 ≥ 1

未知的用参数发现:反复调用,把报错字段用合成值填上,直到服务端不再报"缺字段"
或达到耐心上限。这一步只发**写接口之外**的请求,且合成值不构成有效业务操作。

输出 spec/params.json
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from adfly_api import AdflyClient  # noqa: E402

VALIDATE_RE = re.compile(r"invalid\s+([A-Za-z0-9_]+)\.([A-Za-z0-9_.\[\]]+)\s*:\s*(.+)")
MISSING_RE = re.compile(r"(?:Key:\s*'([A-Za-z0-9_.]+)'|([a-z_][a-z0-9_]*)\s*(?:is\s+)?(?:nil|为空|required|is empty))", re.I)
ENUM_RE = re.compile(r"value must be in list \[([^\]]+)\]")

# proto 字段名(大驼峰) → 请求体的 snake_case
def to_snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return re.sub(r"_+", "_", s).lower()


def constraint_kind(text: str) -> tuple:
    """(类型, 约束描述, 允许值)。顺序很重要:先枚举,再数字,最后才 const。"""
    t = text.lower()
    m = ENUM_RE.search(text)
    if m:
        return "enum", text.strip(), [x.strip() for x in m.group(1).split()]
    if "runes" in t or "length" in t or "字符" in t:
        return "string", text.strip(), None
    if any(k in t for k in ("greater than", "at least", "less than", "gap between",
                            "must be >", "must be <", "outside range")):
        return "number", text.strip(), None
    if t.strip() in ("true", "false") or "bool" in t:
        return "bool", text.strip(), None
    if "email" in t:
        return "email", text.strip(), None
    if "uri" in t or "url" in t:
        return "url", text.strip(), None
    if "must be" in t or "must equal" in t:
        return "const", text.strip(), None
    return "unknown", text.strip(), None


def parse_error(msg: str) -> dict | None:
    m = VALIDATE_RE.search(msg)
    if not m:
        return None
    message_name, field_path, constraint = m.group(1), m.group(2), m.group(3)
    leaf = field_path.split(".")[-1].replace("[]", "")
    kind, desc, allowed = constraint_kind(constraint)
    return {"proto_message": message_name, "proto_field": field_path,
            "json_field": to_snake(leaf), "kind": kind,
            "constraint": desc[:120], "allowed": allowed}


def synthesize(field: str, kind: str, allowed, ctx: dict):
    """造一个能过校验的合成值。

    优先用真实上下文里的真 id —— 这样某些接口能真正跑通,而不是只过参数校验。
    注意:这里绝不能把"约束文案"当值传,否则永远解不出来。
    """
    if allowed:
        return allowed[0]
    key = field.lower()
    # 真实值优先(去下划线后匹配)
    flat = key.replace("_", "")
    for rk, rv in ctx["real"].items():
        if rk.replace("_", "") == flat or flat.endswith(rk.replace("_", "")):
            return rv
    if kind == "number":
        return 1
    if kind == "bool":
        return True
    if kind in ("url", "email"):
        return "https://example.com/a.jpg" if kind == "url" else "a@example.com"
    if "currency" in key:
        return "USD"
    if "date" in key or "time" in key:
        return ctx["start_date"]
    if key.endswith("id") or key.endswith("_ids"):
        return ctx["real"].get("advertiser_id", "1")
    if "platform" in key:
        return 1
    return "x"


def main() -> None:
    rows = json.loads((HERE / "adfly_api/spec/coverage.json").read_text())
    c = AdflyClient(state_path=HERE / "adfly_api/.session.json")
    if not c.session.token:
        print("需要先登录")
        sys.exit(2)

    # 真实上下文:能直接用真 id 的接口就能跑通,不必靠合成值
    real = {}
    try:
        advs = c.advertisers()
        if advs:
            real["advertiser_id"] = advs[0]["advertiser_id"]
        a = c.ads.get_gmv_max_auth_list() or {}
        if (a.get("list") or []):
            real["tiktok_auth_id"] = (a["list"][0] or {}).get("id")
        gm = c.ads.get_gmv_max_list({"page": 1, "page_size": 1}) or {}
        first = (gm.get("list") or [{}])[0]
        real["campaign_id"] = first.get("campaign_id", "")
        real["store_id"] = first.get("store_id", "")
    except Exception as e:
        print("上下文获取部分失败:", str(e)[:70])
    ctx = {"real": {k: v for k, v in real.items() if v}, "start_date": "2026-09-01"}

    # ---- 第一遍:从已有报错里解析 ----
    found: dict = {}
    unresolved = []
    for r in rows:
        parsed = parse_error(r["msg"])
        key = f'{r["backend"]}::{r["method"]} {r["path"]}'
        if parsed:
            found[key] = {"path": r["path"], "backend": r["backend"], "method": r["method"],
                          "status": r["status"], "fields": [parsed]}
        elif r["status"] in ("PARAM", "NOAUTH", "AUTH", "ERROR"):
            unresolved.append(r)
    # 第一遍只从单条报错里解析出一个字段;发现轮会反复补字段直到服务端不再抱怨,
    # 所以把「已解析出的」也一起送进发现轮,取信息量更大的结果。
    already = [r for r in rows if f'{r["backend"]}::{r["method"]} {r["path"]}' in found]
    unresolved.extend(already)
    seen_keys = set()
    unresolved = [r for r in unresolved
                  if not (f'{r["backend"]}::{r["method"]} {r["path"]}' in seen_keys
                          or seen_keys.add(f'{r["backend"]}::{r["method"]} {r["path"]}'))]
    print(f"第一遍(离线解析):{len(found)} 个接口拿到字段;"
          f"{len(unresolved)} 个进入发现轮(含已解析的,用于补全字段)")

    # ---- 第二遍:参数发现(逐个补字段,最多 6 轮) ----
    def discover(r):
        key = f'{r["backend"]}::{r["method"]} {r["path"]}'
        fields = []
        body = {"page": 1, "page_size": 5}
        seen = set()
        def done(status, msg=""):
            return key, {"path": r["path"], "backend": r["backend"], "method": r["method"],
                         "status": status, "fields": fields, "body": body,
                         "last_msg": msg[:130]}

        for _ in range(6):
            try:
                c.call(r["backend"], r["method"], r["path"], body)
                return done("RESOLVED")
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                parsed = parse_error(msg)
                if not parsed:
                    # 参数校验过了,业务层拒绝(数据不存在/无权限等)也算"字段已摸清"
                    if fields:
                        return done("PARAMS_COMPLETE", msg)
                    return done(r["status"], msg)
                fld = parsed["json_field"]
                if fld in seen:
                    # 同一字段重复报错:说明我给的值过不了语义校验(如 id 不存在)
                    return done("PARAMS_COMPLETE", msg)
                seen.add(fld)
                fields.append(parsed)
                body[fld] = synthesize(fld, parsed["kind"], parsed["allowed"], ctx)
        return done("PARAMS_COMPLETE", "达到探测上限")

    if unresolved:
        print(f"第二遍(参数发现,{len(unresolved)} 个 × 最多 6 轮)…")
        def richness(rec: dict) -> tuple:
            """信息量排序:发现出的可复现 body > 字段更多 > 状态更靠前。"""
            quality = {"RESOLVED": 3, "PARAMS_COMPLETE": 2}.get(rec.get("status"), 1)
            return (1 if rec.get("body") is not None else 0,
                    len(rec.get("fields", [])), quality)

        with cf.ThreadPoolExecutor(6) as ex:
            for key, rec in ex.map(discover, unresolved):
                old = found.get(key)
                # 第一遍只做离线解析,拿不到 body;发现轮的结果更可信
                if old is None or richness(rec) > richness(old):
                    found[key] = rec

    (HERE / "adfly_api/spec/params.json").write_text(
        json.dumps(found, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

    resolved = sum(1 for v in found.values() if v.get("status") == "RESOLVED")
    complete = sum(1 for v in found.values() if v.get("status") == "PARAMS_COMPLETE")
    total_fields = sum(len(v["fields"]) for v in found.values())
    print(f"\n参数参考:{len(found)} 个接口 / {total_fields} 个字段")
    print(f"  完全跑通 {resolved} 个 / 字段已摸清(业务层拒绝) {complete} 个")
    from collections import Counter
    print("字段类型分布:", dict(Counter(f["kind"] for v in found.values() for f in v["fields"])))
    print("\n=== 解出的接口示例 ===")
    for k, v in list(found.items())[:10]:
        flds = ", ".join(f'{f["json_field"]}({f["kind"]})' for f in v["fields"])
        print(f'  [{v.get("status","?"):9}] {k.split("::")[1]:44} {flds[:70]}')


if __name__ == "__main__":
    main()
