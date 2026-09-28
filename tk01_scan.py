#!/usr/bin/env python3
"""GMV Max 广告异常检测 —— 找出会「占满全店商品」的广告系列。

为什么需要这个：
  实测踩过一次严重事故 —— 建 GMV Max 时若 `product_specific_type=1`（所有商品），
  该广告会把**全店商品**纳入投放，导致其它任何广告都无法再选这些商品
  （validate/ create 全部返回 product_roi2_mutex_error）。
  当时全店 196 个商品被一个广告锁死，只能先把它关掉才能继续。

判据（读 all_ad_data/detail，纯只读）：
  · `ad_info.product_specific_type == 1`  → 「所有商品」模式 ★高危
  · `ad_info.product_list` 为空            → 印证全店模式
  · `ad_info.inventory_flow_type == 1`     → 全店库存流

本工具只检测、只报告，**不会自动关广告**。关与不关由你决定；
确认要关时用 `--disable <campaign_id>`，它调用：
  POST /oec_ads/shopping/v1/creation/campaign/update_status
  body: {"campaign_list":[<数字ID数组>], "operation": 2}
  → {"code":0,"data":{"status":"success"}}

用法:
  python3 tk01_scan.py --scan                # 扫描已知广告，列出高危项
  python3 tk01_scan.py --check <campaign_id> # 查单个
  python3 tk01_scan.py --disable <campaign_id>            # 关掉（需你确认）
  python3 tk01_scan.py --disable <campaign_id> --yes      # 跳过交互确认
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from tk01_ads import AADVID, OEC_SELLER_ID, PageSession  # noqa: E402

KNOWN_FILE = HERE / "notes" / "tk01_campaigns.json"
DONE_FILE = HERE / "notes" / "tk01_done.json"


class Scanner(PageSession):
    # 页面必须停在卖家中心且已加载，否则 detail 查询返回 code=3。
    # 实测：批量建广告后页面会自动跳到 /ads-creation/dashboard，
    # 此时直接查 detail 一定失败。
    CREATE_URL = "https://seller.tiktokshopglobalselling.com/ads-creation/creation?mpa=1"

    def ensure_ready(self) -> bool:
        """必须在创建页且已渲染。

        实测：detail 查询依赖页面上下文——停在 dashboard 时返回 code=3，
        导航到 /ads-creation/creation 后同一 ID 立刻返回 code=0。
        所以不能只判断"域名对不对"，必须导航到创建页并等渲染完成。
        """
        import time as _t
        try:
            url = self.pg.js("location.href") or ""
        except Exception:
            url = ""
        need_nav = "/ads-creation/creation" not in url
        # 即使 URL 对，内容也可能没渲染好（body 很短）
        if not need_nav:
            try:
                if (self.pg.js("document.body.innerText.length") or 0) >= 600:
                    return True
            except Exception:
                need_nav = True
        if need_nav:
            self.pg.send("Page.navigate", {"url": self.CREATE_URL})
        for _ in range(15):
            _t.sleep(2)
            try:
                if (self.pg.js("document.body.innerText.length") or 0) > 400:
                    return True
            except Exception:
                pass
        return False

    # 所有 JS 都在这里集中构造，避免多份拼接残留导致漏 return
    def detail(self, campaign_id) -> dict:
        cid = str(campaign_id)
        js = (
            "(async()=>{\n"
            f"  const S='{OEC_SELLER_ID}', A='{AADVID}';\n"
            "  const _ck=(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))||'').slice(10);\n"
            "  const h={'accept':'application/json, text/plain, */*'};\n"
            "  if(_ck) h['x-csrftoken']=decodeURIComponent(_ck);\n"
            "  const q=`aadvid=${A}&oec_seller_id=${S}&locale=zh&language=zh`;\n"
            f"  const r=await fetch('/oec_ads/shopping/v1/creation/all_ad_data/detail?'+q+'&campaign_id={cid}',\n"
            "    {headers:h,credentials:'include'});\n"
            "  const j=await r.json();\n"
            "  const d=j.data||{}; const ai=d.ad_info||{}; const ci=d.campaign_info||{};\n"
            "  return JSON.stringify({\n"
            "    code: j.code,\n"
            "    campaign_id: ci.campaign_id, campaign_name: ci.campaign_name,\n"
            "    ad_id: ai.ad_id, ad_name: ai.name,\n"
            "    product_specific_type: ai.product_specific_type,\n"
            "    inventory_flow_type: ai.inventory_flow_type,\n"
            "    inventory_flow: ai.inventory_flow,\n"
            "    product_list_len: (ai.product_list||[]).length,\n"
            "    roas_bid: ai.roas_bid, budget: ai.budget,\n"
            "    schedule_type: ai.schedule_type, start_time: ai.start_time, end_time: ai.end_time,\n"
            "    opt_status: ci.opt_status, external_type: ai.external_type\n"
            "  });\n"
            "})()"
        )
        raw = self.pg.js(js, await_promise=True, timeout=120)
        try:
            return json.loads(raw or "{}")
        except Exception:
            return {}

    @staticmethod
    def is_high_risk(d: dict) -> bool:
        """全店模式判定。

        ⚠ 必须先确认查询成功（code==0）。查询失败时字段全空，
        空值会被误判成"列表为空=全店模式"，也会被误判成"正常"。
        """
        if not d or d.get("code") not in (0, None):
            return False                    # 未知，不妄下结论
        return (d.get("product_specific_type") == 1
                or (d.get("product_list_len", 0) == 0
                    and d.get("inventory_flow_type") == 1))

    @staticmethod
    def unknown(d: dict) -> bool:
        return not d or d.get("code") not in (0, None)

    def disable(self, campaign_id) -> dict:
        """关广告。campaign_list 必须是**数字数组**（传对象数组会报 ParseInt 失败）。"""
        cid = int(campaign_id)
        js = """(async()=>{
  const S='%s', A='%s';
  const _ck=(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))||'').slice(10);
  const h={'content-type':'application/json; charset=utf-8','accept':'application/json, text/plain, */*'};
  if(_ck) h['x-csrftoken']=decodeURIComponent(_ck);
  const q=`aadvid=${A}&oec_seller_id=${S}&locale=zh&language=zh`;
  const r=await fetch('/oec_ads/shopping/v1/creation/campaign/update_status?'+q,
    {method:'POST',headers:h,credentials:'include',
     body:JSON.stringify({campaign_list:[%d], operation:2})});
  return r.status+'|'+(await r.text()).slice(0,300);
})()""" % (OEC_SELLER_ID, AADVID, cid)
        raw = self.pg.js(js, await_promise=True, timeout=180)
        return {"raw": raw, "ok": bool(raw and '"code":0' in raw)}

    def available_count(self, limit_pages: int = 8) -> int:
        js = """(async()=>{
  const S='%s', A='%s', ORG='%s';
  const _ck=(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))||'').slice(10);
  const h={'content-type':'application/json','accept':'application/json, text/plain, */*'};
  if(_ck) h['x-csrftoken']=decodeURIComponent(_ck);
  let n=0;
  for(let p=1;p<=%d;p++){
    const q=`aadvid=${A}&oec_seller_id=${S}&locale=zh&language=zh&org_id=${ORG}&exclude_mutex=true&new_product_only=false`;
    const r=await fetch('/oec_ads/shopping/v1/creation/search_spu?'+q,
      {method:'POST',headers:h,credentials:'include',
       body:JSON.stringify({page_info:{page_index:p,page_size:50},sort_param:{sort_field:9,sort_order:0},
         spu_scope:1,title:'',spu_ids:[],sku_ids:[],mutex_scene:2})});
    const j=await r.json(); const infos=((j.data||{}).spu_infos)||[];
    if(!infos.length) break; n+=infos.length;
    if(infos.length<50) break;
    await new Promise(r=>setTimeout(r,250));
  }
  return String(n);
})()""" % (OEC_SELLER_ID, AADVID, "7385XXXXXXXXXX92", limit_pages)
        raw = self.pg.js(js, await_promise=True, timeout=240)
        try:
            return int(raw)
        except Exception:
            return -1


def known_campaign_ids() -> list[str]:
    """收集要扫描的 campaign_id：优先 notes/tk01_campaigns.json。"""
    ids: list[str] = []
    if KNOWN_FILE.exists():
        try:
            d = json.loads(KNOWN_FILE.read_text(encoding="utf-8"))
            if isinstance(d, list):
                ids += [str(x) if not isinstance(x, dict) else str(x.get("campaign_id")) for x in d]
        except Exception:
            pass
    for f in HERE.glob("notes/tk01_batch*.log"):
        pass
    # 从批量日志里抓 campaign=号码
    import re
    for lg in (HERE / "notes").glob("tk01_*.log"):
        try:
            for m in re.finditer(r"campaign=(\d{10,})", lg.read_text(encoding="utf-8", errors="replace")):
                ids.append(m.group(1))
        except Exception:
            pass
    for lg in (Path("/tmp")).glob("tk01_*.log"):
        try:
            for m in re.finditer(r"campaign=(\d{10,})", lg.read_text(encoding="utf-8", errors="replace")):
                ids.append(m.group(1))
        except Exception:
            pass
    return list(dict.fromkeys(i for i in ids if i and i != "None"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="扫描全部已知广告")
    ap.add_argument("--check", metavar="CAMPAIGN_ID")
    ap.add_argument("--disable", metavar="CAMPAIGN_ID", help="关闭指定广告")
    ap.add_argument("--yes", action="store_true", help="跳过交互确认")
    ap.add_argument("--avail", action="store_true", help="只看当前可用商品数")
    ap.add_argument("--port", type=int, default=CDP_PORT)
    a = ap.parse_args()

    sc = Scanner(port=a.port)
    try:
        if not sc.ensure_ready():
            print("⚠ 页面未就绪（无法连到卖家中心创建页）")
        if a.avail:
            print(f"当前可用商品数(exclude_mutex=true): {sc.available_count()}")
            return 0

        if a.check:
            d = sc.detail(a.check)
            print(json.dumps(d, ensure_ascii=False, indent=1))
            print(f"\n>>> 高危(全店模式): {'⚠ 是' if Scanner.is_high_risk(d) else '否'}")
            return 0

        if a.disable:
            d = sc.detail(a.disable)
            if Scanner.unknown(d):
                print(f"⚠ 查不到该广告详情（code={d.get('code')}），"
                      f"请确认 campaign_id 是否正确、或它是否已被关闭")
                print(f"   detail: {json.dumps(d, ensure_ascii=False)[:200]}")
                return 1
            print("目标广告:")
            print(f"  名称: {d.get('campaign_name')}")
            print(f"  product_specific_type: {d.get('product_specific_type')} "
                  f"({ '所有商品 ⚠' if d.get('product_specific_type')==1 else '选定商品' })")
            print(f"  product_list 长度: {d.get('product_list_len')}")
            print(f"  opt_status: {d.get('opt_status')}")
            if not a.yes:
                ans = input(f"\n确认关闭 campaign_id={a.disable} ？(yes/no) ").strip().lower()
                if ans not in ("y", "yes"):
                    print("已取消")
                    return 0
            before = sc.available_count()
            r = sc.disable(a.disable)
            print(f"\n关闭请求: {r['raw'][:200]}")
            print(f"关闭成功: {'✅' if r['ok'] else '❌'}")
            import time
            time.sleep(4)
            after = sc.available_count()
            print(f"可用商品数: {before} → {after}   {'🎉 商品已释放' if after > before else ''}")
            return 0 if r["ok"] else 1

        if a.scan:
            ids = known_campaign_ids()
            print(f"扫描 {len(ids)} 个已知广告…\n")
            risky = []
            for i, cid in enumerate(ids, 1):
                d = sc.detail(cid)
                if Scanner.unknown(d):
                    print(f"  [{i}/{len(ids)}] ? 查不到 code={d.get('code')} {cid}")
                    continue
                hr = Scanner.is_high_risk(d)
                flag = "⚠ 高危" if hr else "  正常"
                print(f"  [{i}/{len(ids)}] {flag} {cid}  "
                      f"pst={d.get('product_specific_type')} "
                      f"plist={d.get('product_list_len')} "
                      f"opt={d.get('opt_status')}  {str(d.get('campaign_name'))[:38]}")
                if hr:
                    risky.append(d)
            print(f"\n{'='*60}")
            if risky:
                print(f"⚠ 发现 {len(risky)} 个「全店模式」广告 —— 会锁死所有商品：")
                for d in risky:
                    print(f"   campaign_id={d.get('campaign_id')}  {d.get('campaign_name')}")
                print("\n建议逐个确认后关闭：")
                print(f"   python3 tk01_scan.py --disable <campaign_id>")
            else:
                print("✅ 未发现全店模式广告")
            return 0

        ap.print_help()
        return 0
    finally:
        sc.close()


if __name__ == "__main__":
    raise SystemExit(main())
