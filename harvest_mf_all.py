#!/usr/bin/env python3
"""把卖家中心**全部微前端**的 bundle 下下来并抽接口。

页面范围 = atlas 注册表里的 11 个 `mf_*`（`notes/fin_mf_registry.json` 是本地店
deposit 页 HTML 里抓到的注册表）。每个 mf_* 对应一块业务域，所以它们的 bundle
里就装着"所有页面"的接口。

CDN 直连可取（不需要代理、不需要 cookie）。webpack module federation 结构：
  entry: <mf>.js
  chunk: <同目录>/static/js/<id>.<hash>.js
递归展开 `import("./x.js")` 与 `mf_xxx/static/js/...` 两种引用。

输出：
  notes/mf_all/<mf>/*.js          bundle
  notes/api_inventory/mf_<mf>.json 该微前端抽到的接口
  notes/api_inventory/mf_all.json   汇总
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REG = HERE / "notes" / "fin_mf_registry.json"
OUT_JS = HERE / "notes" / "mf_all"
OUT_API = HERE / "notes" / "api_inventory"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/144.0.7559.230 Safari/537.36")

# 路径三种写法（财务那轮踩出来的，全都要覆盖）
TPL = re.compile(r"/(widget/)?api/v\$\{[^}]{0,60}?\|\|\s*(\d)\}/([A-Za-z0-9_/\-]{3,140})")
TPL_NODEF = re.compile(r"/(widget/)?api/v\$\{[^}]{0,80}\}/([A-Za-z0-9_/\-]{3,140})")
LIT = re.compile(r"/(widget/)?api/v(\d)/([A-Za-z0-9_/\-]{3,140})")
OEC = re.compile(r"/api/oec/([A-Za-z0-9_/\-]{3,140})")
METH2 = re.compile(r'method:\s*(?:"([A-Z]{3,6})"|([A-Za-z_$][\w$.]{0,12}))')
ALIAS = {"a.UD": "GET", "i.UD": "GET", "n.UD": "GET", "G": "GET", "O": "GET",
         "we": "GET", "method$1": "GET", "a": "GET"}
JUNK = re.compile(r"(\.js|\.css|\.map|\?.*|\$\{.*|[\"'`].*)$")
REL = re.compile(r'["\'](\.\.?/)?([A-Za-z0-9_~.\-]+\.js)["\']')
CHUNK = re.compile(r'[A-Za-z0-9_/.\-]*?(?:static/js|/js)/[A-Za-z0-9_.~\-]+\.js')


def get(url: str) -> bytes:
    r = subprocess.run(["curl", "-sk", "--max-time", "60", "--compressed",
                        "-H", f"user-agent: {UA}", url], capture_output=True)
    d = r.stdout
    return b"" if d.startswith(b'{"Success":-1') else d


def clean(p: str) -> str:
    p = JUNK.sub("", p) or p
    return re.sub(r"/+$", "", p)


# ★ 有的微前端（mf_data / mf_governance）接口**不带 /api 前缀**：
#     method:"POST" … "/insights/seller/shop/product/category/list"
#     method:"POST" … "/qualification/center/fs/product_qualification_task/list"
#   只认 /api/ 会整族漏掉。判据：该路径字符串**紧邻** `method:"…"`。
#   前端路由不会挨着 method，所以这个邻接条件是干净的区分。
METHOD_CTX = re.compile(r'method:\s*"([A-Z]{3,6})"')
QUOTED_PATH = re.compile(r'["\'`](/[A-Za-z][A-Za-z0-9_/\-{}$\.]{6,150})["\'`]')
SKIP_PREFIX = ("/api", "/widget", "/obj", "/static", "/assets", "/node_modules")
SKIP_EXT = (".js", ".css", ".json", ".png", ".svg", ".webp", ".map", ".jpg", ".gif", ".woff")


def extract_ctx(s: str) -> dict:
    rec: dict[str, dict] = {}
    for m in METHOD_CTX.finditer(s):
        lo, hi = max(0, m.start() - 520), m.start() + 520
        win = s[lo:hi]
        best, bd = None, 10 ** 9
        for c in QUOTED_PATH.finditer(win):
            p = c.group(1)
            if p.startswith(SKIP_PREFIX) or p.endswith(SKIP_EXT):
                continue
            if len([x for x in p.split("/") if x]) < 3:
                continue
            d = abs(c.start() - (m.start() - lo))
            if d < bd:
                best, bd = p, d
        if best and bd <= 460:
            e = rec.setdefault(best, {"m": {}, "names": {}})
            e["m"][m.group(1)] = e["m"].get(m.group(1), 0) + 1
    return rec


def extract(s: str) -> dict:
    rec: dict[str, dict] = {}

    def add(full, win, back):
        if len([x for x in full.split("/") if x]) < 3:
            return
        e = rec.setdefault(full, {"m": {}, "n": 0})
        lits, alias = [], []
        for m in METH2.finditer(win):
            (lits if m.group(1) else alias).append(m.group(1) or m.group(2))
        if lits:
            e["m"][lits[0]] = e["m"].get(lits[0], 0) + 1
        elif alias:
            a = ALIAS.get(alias[0], "POST" if "body:" in win[:200] else "?")
            e["m"][a] = e["m"].get(a, 0) + 1
        nm = None
        for x in re.finditer(r"([A-Z][A-Za-z0-9_]{2,48})\s*\((?:[a-z]+,\s*)*[a-z]+\)\s*\{", back):
            nm = x.group(1)
        if nm:
            e.setdefault("names", {})
            e["names"][nm] = e["names"].get(nm, 0) + 1
        e["n"] += 1

    for m in TPL.finditer(s):
        w, ver, path = m.group(1), m.group(2), m.group(3)
        add(clean(f"/{w or ''}api/v{ver}/{path}"), s[m.end():m.end() + 240],
            s[max(0, m.start() - 300):m.start()])
    for m in TPL_NODEF.finditer(s):
        w, path = m.group(1), m.group(2)
        add(clean(f"/{w or ''}api/v1/{path}"), s[m.end():m.end() + 240],
            s[max(0, m.start() - 300):m.start()])
    for m in LIT.finditer(s):
        w, ver, path = m.group(1), m.group(2), m.group(3)
        add(clean(f"/{w or ''}api/v{ver}/{path}"), s[m.end():m.end() + 240],
            s[max(0, m.start() - 300):m.start()])
    for m in OEC.finditer(s):
        add(clean(f"/api/oec/{m.group(1)}"), s[m.end():m.end() + 240],
            s[max(0, m.start() - 300):m.start()])
    return rec


def main():
    only = sys.argv[1:] or None
    reg = json.loads(REG.read_text(encoding="utf-8"))
    OUT_JS.mkdir(parents=True, exist_ok=True)
    OUT_API.mkdir(parents=True, exist_ok=True)
    master: dict[str, dict] = {}
    for mf, src in sorted(reg.items()):
        if only and mf not in only:
            continue
        url = src if src.startswith("http") else "https:" + src
        if not url.endswith(".js"):
            url = url.rstrip("/") + f"/{mf}.js"
        base = url.rsplit("/", 1)[0]
        # ★ chunk 基址来自 webpack 的 publicPath（写死在 runtime 里）：
        #     __webpack_require__.p = "https://lf16-scmcdn.oecstatic.com/obj/oec-magellan-sg/i18n/ecom/TTS/unihan/"
        #   拼法 = publicPath + "mf_xxx/static/js/<id>.<hash>.js"
        #   entry 自己在 goofy-cdn 上，chunk 却在 oecstatic 上 —— 两个不同 CDN，别猜。
        chunk_base = None
        d = OUT_JS / mf
        d.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*104}\n### {mf}\n    {url}\n{'='*104}")
        queue, seen, files = [], set(), []

        def refs(txt):
            """从一段 JS 里取出所有 chunk 相对引用。"""
            out = []
            for m in REL.finditer(txt):
                out.append(f"{base}/{m.group(2)}")
            for m in CHUNK.finditer(txt):
                raw = m.group(0)
                # raw 形如 mf_xxx/static/js/a.b.js —— 取 mf 名之后的部分（含 static/）
                tail = raw.split(f"{mf}/", 1)[1] if f"{mf}/" in raw else "/".join(raw.split("/")[-3:])
                # ★ tail 只剩 static/js/x.js，必须补回 mf 名那一段
                cands = []
                if chunk_base:
                    cands += [f"{chunk_base}/{mf}/{tail}", f"{chunk_base}/{tail}"]
                cands += [f"{base}/{mf}/{tail}", f"{base}/{tail}"]
                out += cands
            return out

        # 先下 entry：既拿接口，也从它读 publicPath 和 chunk 表
        # ★ 有些 mf 是 garfish loader（6-8KB），没有 CHUNK 式引用，
        #   chunk 表藏在 webpack runtime 的 `t.u=function(e){return"mf_x/static/js/"+e+"."+{id:"hash",…}[e]+".js"}`
        UMAP = re.compile(
            r'\.u\s*=\s*function\s*\(\s*\w+\s*\)\s*\{\s*return\s*"([^"]+)"\s*\+\s*\w+\s*\+\s*"\."\s*\+\s*\{([^}]+)\}\s*\[\s*\w+\s*\]\s*\+\s*"([^"]+)"')

        def umap_refs(txt, cbase):
            """从 webpack .u 函数里还原 chunk URL。"""
            m = UMAP.search(txt)
            if not m:
                return []
            prefix, table, suffix = m.group(1), m.group(2), m.group(3)
            out = []
            for e in re.finditer(r'(\d+|"[^"]+")\s*:\s*"([^"]+)"', table):
                cid = e.group(1).strip('"')
                out.append(f"{cbase}/{prefix}{cid}.{e.group(2)}{suffix}")
            return out

        head = get(url)
        if head:
            d0 = d / re.sub(r"[^A-Za-z0-9._-]", "_", url.split("//", 1)[-1])[-150:]
            d0.write_bytes(head)
            files.append(d0)
            hs = head.decode("utf-8", "replace")
            # .p 可能是绝对（https://…）也可能是相对（/obj/oec-magellan-sg/…）
            # 取**第一个**形似路径的赋值；后面还有 `.p=window.__publicUrl_new__||t.p` 这种噪声
            raw_p = ""
            for mm in re.finditer(r'\.p\s*=\s*"([^"]{4,200})"', hs):
                v = mm.group(1)
                if v.startswith(("http://", "https://", "/")):
                    raw_p = v.rstrip("/")
                    break
            if raw_p.startswith("/"):
                # 相对路径（garfish loader 常见）→ 补 CDN 前缀
                chunk_base = "https://lf16-scmcdn.oecstatic.com" + raw_p
            else:
                chunk_base = raw_p or f"{base}/{mf}"
            print(f"    publicPath = {chunk_base}")
            q = refs(hs)
            if not q:
                q = umap_refs(hs, chunk_base)
                if q:
                    print(f"    用 .u 映射表还原出 {len(q)} 个 chunk")
            queue = [x for x in dict.fromkeys(q) if x not in seen]
        while queue:
            u = queue.pop(0)
            if u in seen:
                continue
            seen.add(u)
            dst = d / re.sub(r"[^A-Za-z0-9._-]", "_", u.split("//", 1)[-1])[-150:]
            if dst.exists() and dst.stat().st_size > 100:
                data = dst.read_bytes()
            else:
                data = get(u)
                if data and len(data) > 100:
                    dst.write_bytes(data)
            if not data or len(data) < 100:
                continue
            files.append(dst)
            s = data.decode("utf-8", "replace")
            queue += [x for x in refs(s) if x not in seen]
            queue = [x for x in dict.fromkeys(queue) if x not in seen]
        size = sum(f.stat().st_size for f in files)
        print(f"    下载 {len(files)} 个文件 / {size/1e6:.1f} MB")

        agg: dict[str, dict] = {}
        for f in files:
            try:
                s = f.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for fn in (extract, extract_ctx):
                for p, e in fn(s).items():
                    t = agg.setdefault(p, {"m": {}, "names": {}})
                    for k, v in e["m"].items():
                        t["m"][k] = t["m"].get(k, 0) + v
                    for k, v in (e.get("names") or {}).items():
                        t["names"][k] = t["names"].get(k, 0) + v
        rows = []
        for p, e in sorted(agg.items()):
            rows.append({"path": p,
                         "method": max(e["m"], key=e["m"].get) if e["m"] else "?",
                         "names": sorted(e["names"], key=e["names"].get, reverse=True)[:3]})
        (OUT_API / f"{mf}.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"    抽到接口 {len(rows)} 个")
        for r in rows[:6]:
            print(f"      {r['method']:5} {r['path']}")
        master[mf] = {"url": url, "files": len(files), "bytes": size, "endpoints": rows}
        time.sleep(0.5)

    # ★ 合并写：分次跑（比如只补 mf_data）不会把别的 mf 结果冲掉
    agg_file = OUT_API / "mf_all.json"
    merged = {}
    if agg_file.exists():
        try:
            merged = json.loads(agg_file.read_text(encoding="utf-8"))
        except Exception:
            merged = {}
    for k, v in master.items():
        if v.get("endpoints"):          # 只覆盖有结果的，空结果不覆盖旧数据
            merged[k] = v
        else:
            merged.setdefault(k, v)
    master = merged
    agg_file.write_text(json.dumps(master, ensure_ascii=False, indent=1), encoding="utf-8")
    union = set()
    for v in master.values():
        union |= {r["path"] for r in v["endpoints"]}
    print(f"\n{'='*104}")
    print(f"微前端 {len(master)} 个 / 接口并集 {len(union)} 个 → notes/api_inventory/mf_all.json")
    for mf, v in sorted(master.items(), key=lambda kv: -len(kv[1]["endpoints"])):
        print(f"  {len(v['endpoints']):>5}  {mf:22} {v['files']:>3} 文件 {v['bytes']/1e6:>6.1f} MB")


if __name__ == "__main__":
    main()
