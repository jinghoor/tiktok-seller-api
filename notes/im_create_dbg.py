import json, sys
sys.path.insert(0,".")
from tk01_im import IMClient, P_CONV_CREATE
M=IMClient(gap=0.9)
try:
    M.refresh_config()
    me=M.self_user_id
    print(f"me={me} region={M.region} api={M.api_url}")
    body={"participants":[
        {"role":0,"uid":"7493XXXXXXXXXX92","extra":{"sender_im_role":"4"}},
        {"role":1,"uid":str(me),"extra":{"sender_im_role":"2"}}]}
    for q in [
      f"?aid=6556&app_name=i18n_ecom_alliance&oec_region={M.region}",
      f"?oec_region={M.region}",
      f"?aid=6556&oec_region={M.region}",
      "",
    ]:
        try:
            r=M._json_post(P_CONV_CREATE+q, body)
            print(f"\n### q={q!r}\n  {json.dumps(r,ensure_ascii=False)[:700]}")
        except Exception as e:
            print(f"\n### q={q!r}\n  ✗ {str(e)[:250]}")
    print("\n===== search_by_users('ngoctrinh89') 看会话是否已建 =====")
    try:
        r=M.search_by_users("ngoctrinh89")
        print("  ", json.dumps(r,ensure_ascii=False)[:800])
    except Exception as e:
        print("  ✗", str(e)[:200])
finally:
    M.close()
