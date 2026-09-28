import json, sys, time
sys.path.insert(0,".")
from tk01_affiliate import AffiliateClient
A=AffiliateClient(gap=0.9)
def L(*a): print(*a, flush=True)
try:
    L("===== group_search 列出现有计划 =====")
    r=A.call("group_search", {"cur_page":1,"page_size":20})
    L(f"  code={r.get('code')} msg={str(r.get('message'))[:120]}")
    d=r.get("data") or {}
    L(f"  data keys={sorted(d.keys())}")
    groups = d.get("invitation_groups") or d.get("list") or d.get("groups") or []
    L(f"  计划 {len(groups)} 个")
    for g in groups:
        L(f"    id={g.get('id')} name={g.get('name')!r} status={g.get('status')} "
          f"creator_cnt={g.get('creator_cnt')} added={g.get('creator_added_cnt')} "
          f"keys={sorted(g.keys())[:22]}")
    open("notes/aff_group_search.json","w",encoding="utf-8").write(
        json.dumps(r,ensure_ascii=False,indent=2))
    gid = str(groups[0].get("id")) if groups else None
    L(f"\n  用 gid={gid} 继续探 search/creator")
    L("\n===== group_search_creator 绑定探针 =====")
    variants=[
      ("空body", {}),
      ("invitation_group_id", {"invitation_group_id": gid}),
      ("group_id", {"group_id": gid}),
      ("id", {"id": gid}),
      ("+分页", {"invitation_group_id": gid, "cur_page":1, "page_size":20}),
    ]
    for label,body in variants:
        try:
            r=A.call("group_search_creator", body)
            L(f"\n  [{label}] code={r.get('code')} msg={str(r.get('message'))[:220]}")
            dd=r.get("data") or {}
            if r.get("code")==0:
                L(f"    keys={sorted(dd.keys())}")
                for k,v in dd.items():
                    if isinstance(v,list):
                        L(f"    ★ {k}: {len(v)} 条")
                        if v: L(f"       首条={json.dumps(v[0],ensure_ascii=False)[:700]}")
                    else:
                        L(f"    {k}={str(v)[:150]}")
                open("notes/aff_group_creators.json","w",encoding="utf-8").write(
                    json.dumps(r,ensure_ascii=False,indent=2))
                break
        except Exception as e:
            L(f"\n  [{label}] ✗ {str(e)[:220]}")
        time.sleep(1.0)
finally:
    A.close()
