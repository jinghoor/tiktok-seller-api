import json, sys, time
sys.path.insert(0,".")
from tk01_affiliate import AffiliateClient
A=AffiliateClient(gap=0.9)
GID="7690XXXXXXXXXX47"
try:
    r=A.call("group_detail", {"invitation_group_id": GID})
    open("notes/aff_group_detail.json","w",encoding="utf-8").write(
        json.dumps(r,ensure_ascii=False,indent=2))
    inv=(r.get("data") or {}).get("invitation") or {}
    print(f"code={r.get('code')} invitation keys={sorted(inv.keys())}")
    for k,v in inv.items():
        if isinstance(v,list):
            print(f"\n★ {k}: {len(v)} 条")
            for x in v[:12]:
                print("   ", json.dumps(x,ensure_ascii=False)[:520])
        elif isinstance(v,dict):
            print(f"\n· {k}: {json.dumps(v,ensure_ascii=False)[:400]}")
        else:
            print(f"· {k} = {str(v)[:150]}")
    # 再扫 search/creator 的分页键名
    print("\n===== search/creator 分页键名扫描 =====")
    for label, body in [
        ("page_number", {"invitation_group_id":GID,"page_number":1,"page_size":20}),
        ("page/limit",   {"invitation_group_id":GID,"page":1,"limit":20}),
        ("offset/limit", {"invitation_group_id":GID,"offset":0,"limit":20}),
        ("invitation_id",{"invitation_id":GID,"page_number":1,"page_size":20}),
    ]:
        try:
            rr=A.call("group_search_creator", body)
            m=str(rr.get("message"))[:180]
            print(f"  [{label}] code={rr.get('code')} {m}")
            if rr.get("code")==0:
                open("notes/aff_group_creators.json","w",encoding="utf-8").write(
                    json.dumps(rr,ensure_ascii=False,indent=2))
                print("    ★ 成功，已存")
                break
        except Exception as e:
            print(f"  [{label}] ✗ {str(e)[:180]}")
        time.sleep(1.1)
finally:
    A.close()
