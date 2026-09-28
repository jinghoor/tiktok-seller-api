import json, sys, time
sys.path.insert(0,".")
from tk01_im import IMClient, P_SEARCH_UNAME
M=IMClient(gap=0.8)
try:
    M.refresh_config()
    print(f"self_user_id={M.self_user_id} region={M.region}")
    for uname in ("huyenlee.review","tauhhxjl","njsjsbax5nw"):
        for extra in ({}, {"im_id":"4452XXXXXXXXXX35"}):
            try:
                r=M.A.ch.call(P_SEARCH_UNAME, None, method="GET",
                    params={"oec_region":M.region,"biz":"shop_creator","role":"shop",
                            "cursor":"0","uname":uname, **extra})
                print(f"\n  uname={uname!r} extra={extra} → code={r.get('code')} "
                      f"data={json.dumps(r.get('data'),ensure_ascii=False)[:300]}")
            except Exception as e:
                print(f"\n  uname={uname!r} extra={extra} → ✗ {str(e)[:160]}")
            time.sleep(0.8)
    print("\n===== search_by_users (JSON POST, IM 域) =====")
    for name in ("huyenlee.review","tauhhxjl"):
        try:
            r=M.search_by_users(name)
            print(f"  {name!r} → {json.dumps(r,ensure_ascii=False)[:400]}")
        except Exception as e:
            print(f"  {name!r} → ✗ {str(e)[:200]}")
        time.sleep(1.0)
    print("\n===== init_cursor (cmd=203) =====")
    try: print("  ", json.dumps(M.init_cursor(), ensure_ascii=False))
    except Exception as e: print("  ✗", str(e)[:200])
    print("\n===== get_read_index (cmd=2000) =====")
    try: print("  ", json.dumps(M.get_read_index("7580XXXXXXXXXX98"), ensure_ascii=False))
    except Exception as e: print("  ✗", str(e)[:200])
finally:
    M.close()
