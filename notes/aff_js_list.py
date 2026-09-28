"""只读：从操作员已打开的联盟标签页取资源清单（不导航、不新建页、不抢焦点）。"""
import json, sys
sys.path.insert(0,".")
from tk01_affiliate import AffiliateClient

A = AffiliateClient(gap=0.8)
try:
    A.ch._ensure()
    pg = A.ch._page
    print(f"附着到: {pg.url[:110]}")
    js = """(() => {
      const rs = performance.getEntriesByType('resource');
      const out = rs.filter(r => /\.(js|mjs)(\\?|$)/.test(r.name))
        .map(r => ({u: r.name, s: r.transferSize || r.encodedBodySize || 0}));
      return JSON.stringify({n: rs.length, js: out});
    })()"""
    d = json.loads(pg.evaluate(js))
    print(f"资源总数 {d['n']}，其中 JS {len(d['js'])} 个")
    d["js"].sort(key=lambda x: -x["s"])
    json.dump(d["js"], open("notes/aff_js_urls.json","w"), ensure_ascii=False, indent=1)
    print("\n按体积 top 30:")
    for x in d["js"][:30]:
        print(f"  {x['s']:>9,}  {x['u'][:135]}")
    print(f"\n已存 notes/aff_js_urls.json")
finally:
    A.close()
