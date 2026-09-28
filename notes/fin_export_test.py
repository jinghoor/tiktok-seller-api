"""真跑一次：建导出任务 → 读导出历史 → 按 file_id 下载。目标本土 SHOP_LOCAL。"""
import json, sys, time
sys.path.insert(0, ".")
from tk01_finance import FinanceClient, FILE_STATUS

C = FinanceClient("tk89", verbose=True)
try:
    print("=== 1. 导出历史（导出前，基线）===")
    h0 = C.export_history()
    print(json.dumps(h0, ensure_ascii=False)[:600])

    print("\n=== 2. 建导出任务：近 14 天结算明细 ===")
    import datetime
    end = datetime.date.today()
    beg = end - datetime.timedelta(days=14)
    r, body = C.export_statement_file(beg.isoformat(), end.isoformat(),
                                      file_type="settlement_detail", time_type=1)
    print(f"  body = {json.dumps(body, ensure_ascii=False)}")
    print(f"  响应 = {json.dumps(r, ensure_ascii=False)[:500]}")

    print("\n=== 3. 轮询导出历史，等它出现 ===")
    for i in range(10):
        time.sleep(3)
        h = C.export_history()
        files = h.get("_decoded") or []
        print(f"  [{i+1}] code={h.get('code')} 文件 {len(files)} 条")
        for f in files:
            print(f"       file_id={f.get('file_id')} status={f.get('status')}"
                  f"({f.get('status_text')}) name={str(f.get('file_name') or f.get('name'))[:40]}"
                  f" keys={sorted(f.keys())}")
        if files:
            print(f"\n  ★ 历史记录真实结构（首条完整）:")
            print("  " + json.dumps(files[0], ensure_ascii=False, indent=2)[:1200])
            fid = files[0].get("file_id")
            st = files[0].get("status")
            if fid and st in (2, 3):
                print(f"\n=== 4. 按 file_id={fid} 下载 ===")
                d = C.download_history_file(fid)
                print("  " + json.dumps(d, ensure_ascii=False)[:800])
            break
finally:
    C.close()
