import json, sys
sys.path.insert(0,".")
from tk01_im import IMClient
M=IMClient(gap=0.8)
try:
    M.refresh_config()
    r=M.search_by_users("tauhhxjl")
    open("notes/im_search_by_users.json","w",encoding="utf-8").write(
        json.dumps(r,ensure_ascii=False,indent=2))
    print(json.dumps(r,ensure_ascii=False,indent=2)[:4000])
finally:
    M.close()
