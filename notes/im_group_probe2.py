import json, sys, time
sys.path.insert(0,".")
from tk01_affiliate import AffiliateClient
A=AffiliateClient(gap=0.9)
def L(*a): print(*a, flush=True)
GID="7690XXXXXXXXXX47"
try:
    L("===== group_detail =====")
    try:
        r=A.call("group_detail", {"invitation_group_id": GID})
        L(f"  code={r.get('code')} msg={str(r.get('message'))[:200]}")
        d=r.get("data") or {}
        L(f"  keys={sorted(d.keys())}")
        open("notes/aff_group_detail.json","w",encoding="utf-8").write(
            json.dumps(r,ensure_ascii=False,indent=2))
        ig = d.get("invitation_group") or {}
        L(f"  invitation_group keys={sorted(ig.keys())}")
        for k,v in ig.items():
            if isinstance(v,list) and v:
                L(f"  ★ {k}: {len(v)} 条  首条={json.dumps(v[0],ensure_ascii=False)[:800]}")
            elif not isinstance(v,(dict,list)):
                L(f"  {k}={str(v)[:120]}")
    except Exception as e:
        L(f"  ✗ {str(e)[:250]}")

    L("\n===== group_search_creator 变体 =====")
    variants=[
      ("gid+分页", {"invitation_group_id":GID,"cur_page":1,"page_size":20}),
      ("+search/order_params", {"invitation_group_id":GID,"cur_page":1,"page_size":20,
                                "search_params":{},"order_params":{}}),
      ("嵌套 invitation_group_id", {"search_params":{"invitation_group_id":GID},
                                    "cur_page":1,"page_size":20}),
      ("group_id+分页", {"group_id":GID,"cur_page":1,"page_size":20}),
      ("id str", {"id":GID,"cur_page":1,"page_size":20}),
    ]
    for label,body in variants:
        try:
            r=A.call("group_search_creator", body)
            L(f"\n  [{label}] code={r.get('code')} msg={str(r.get('message'))[:230]}")
            if r.get("code")==0:
                open("notes/aff_group_creators.json","w",encoding="utf-8").write(
                    json.dumps(r,ensure_ascii=False,indent=2))
                dd=r.get("data") or {}
                L(f"    keys={sorted(dd.keys())}")
                for k,v in dd.items():
                    if isinstance(v,list) and v:
                        L(f"    ★ {k}: {len(v)} 条")
                        L(f"       首条={json.dumps(v[0],ensure_ascii=False)[:900]}")
                break
        except Exception as e:
            L(f"\n  [{label}] ✗ {str(e)[:230]}")
        time.sleep(1.1)
finally:
    A.close()
