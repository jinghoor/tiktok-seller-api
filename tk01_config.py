#!/usr/bin/env python3
"""店铺上下文 —— 多店铺 / 多区域配置。

之前 `shop_id` / `region` / 各种 host 都是写死在各个模块顶部的常量，
换一个店或换一个国家就得改代码。这个模块把它们收进 `shops.json`：

```json
{
  "active": "tk01",
  "shops": {
    "tk01": {
      "label": "TK01_CrossBorder_Shop",
      "region": "VN",
      "seller_id": "7494XXXXXXXXXX00",
      "aid": "6556",
      "cdp_port": CDP_PORT,
      "api_host": "https://api16-normal-sg.tiktokshopglobalselling.com",
      "seller_origin": "https://seller.tiktokshopglobalselling.com",
      "affiliate_host": "https://affiliate.tiktokshopglobalselling.com",
      "api_app_name": "i18n_ecom_shop",
      "affiliate_app_name": "i18n_ecom_alliance",
      "timezone_name": "Asia/Bangkok"
    }
  }
}
```

用法:

```python
from tk01_config import load_shop, list_shops, set_active

shop = load_shop()            # 当前 active
shop = load_shop("tk02")      # 指定
C.SELLER, C.REGION            # 兼容旧的模块级常量

# 命令行切换
python3 tk01_config.py list
python3 tk01_config.py use tk02
python3 tk01_config.py add tk02 --region TH --seller-id 123… --port 50990
```

## 换区域的注意点（实测踩过的）

| 项 | 说明 |
|---|---|
| `api_host` | VN 走 `api16-normal-sg`；别的区域可能是 `api16-normal-{us,eu,my}` 或 `api16-normal-vn`，**必须实测** |
| `affiliate_host` | 联盟域一直是 `affiliate.tiktokshopglobalselling.com`，区域靠 `shop_region` 区分 |
| `cdp_port` | Hub Studio 里每个容器一个端口，**一个店铺一个端口** |
| `timezone_name` | 只影响请求外观，实测 VN 店返回的是 `Asia/Bangkok`（不是胡志明市） |
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "shops.json"

# 默认店铺 —— 与历史行为一致（原来这些值散在各模块里写死）
DEFAULT_SHOP = {
    "label": "TK01_CrossBorder_Shop",
    "region": "VN",
    "seller_id": "7494XXXXXXXXXX00",
    "aid": "6556",
    "cdp_port": CDP_PORT,
    "api_host": "https://api16-normal-sg.tiktokshopglobalselling.com",
    "seller_origin": "https://seller.tiktokshopglobalselling.com",
    "affiliate_host": "https://affiliate.tiktokshopglobalselling.com",
    "api_app_name": "i18n_ecom_shop",
    "affiliate_app_name": "i18n_ecom_alliance",
    "timezone_name": "Asia/Bangkok",
}


def _ensure_file() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    data = {"active": "tk01", "shops": {"tk01": dict(DEFAULT_SHOP)}}
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data


def load_all() -> dict:
    return _ensure_file()


def list_shops() -> dict:
    return load_all().get("shops") or {}


def active_name() -> str:
    return load_all().get("active") or "tk01"


def set_active(name: str) -> dict:
    d = load_all()
    if name not in (d.get("shops") or {}):
        raise KeyError(f"没有名为 {name} 的店铺；现有: {sorted((d.get('shops') or {}))}")
    d["active"] = name
    CONFIG_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    return d["shops"][name]


def load_shop(name: str | None = None, *, port: int | None = None) -> dict:
    """取店铺配置。`name=None` 用 active。`port` 可覆盖 CDP 端口。"""
    d = load_all()
    shops = d.get("shops") or {}
    key = name or d.get("active") or "tk01"
    shop = dict(shops.get(key) or DEFAULT_SHOP)
    shop["_key"] = key
    if port:
        shop["cdp_port"] = port
    return shop


def add_shop(name: str, **overrides) -> dict:
    d = load_all()
    base = dict(DEFAULT_SHOP)
    base.update({k: v for k, v in overrides.items() if v is not None})
    d.setdefault("shops", {})[name] = base
    CONFIG_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    return base


# ── 兼容层：模块级常量（老代码 `from tk01_config import SELLER` 也能用）──
_ACTIVE = load_shop()
SHOP_KEY = _ACTIVE["_key"]
LABEL = _ACTIVE.get("label")
REGION = _ACTIVE["region"]
SELLER = _ACTIVE["seller_id"]
SHOP_ID = _ACTIVE["seller_id"]
AID = _ACTIVE["aid"]
DEFAULT_PORT = _ACTIVE["cdp_port"]
API_HOST = _ACTIVE["api_host"]
SELLER_ORIGIN = _ACTIVE["seller_origin"]
AFFILIATE_HOST = _ACTIVE["affiliate_host"]
API_APP_NAME = _ACTIVE["api_app_name"]
AFFILIATE_APP_NAME = _ACTIVE["affiliate_app_name"]
TIMEZONE_NAME = _ACTIVE.get("timezone_name") or "Asia/Bangkok"


def main() -> None:
    ap = argparse.ArgumentParser(description="店铺上下文管理（多店铺 / 多区域）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("use"); p.add_argument("name")
    p = sub.add_parser("add"); p.add_argument("name")
    p.add_argument("--label"); p.add_argument("--region"); p.add_argument("--seller-id")
    p.add_argument("--aid"); p.add_argument("--port", type=int)
    p.add_argument("--api-host"); p.add_argument("--seller-origin")
    p.add_argument("--affiliate-host"); p.add_argument("--api-app-name")
    p.add_argument("--affiliate-app-name"); p.add_argument("--timezone")
    sub.add_parser("show")
    a = ap.parse_args()

    if a.cmd == "list":
        cur = active_name()
        for k, v in sorted(list_shops().items()):
            mark = "★" if k == cur else " "
            print(f"  {mark} {k:10} {v.get('region'):4} {v.get('seller_id'):20} "
                  f"port={v.get('cdp_port')}  {v.get('label')}")
    elif a.cmd == "use":
        s = set_active(a.name)
        print(f"已切到 {a.name}: {json.dumps(s, ensure_ascii=False)}")
    elif a.cmd == "add":
        s = add_shop(a.name, label=a.label, region=a.region, seller_id=a.seller_id,
                     aid=a.aid, cdp_port=a.port, api_host=a.api_host,
                     seller_origin=a.seller_origin, affiliate_host=a.affiliate_host,
                     api_app_name=a.api_app_name,
                     affiliate_app_name=a.affiliate_app_name,
                     timezone_name=a.timezone)
        print(f"已添加 {a.name}: {json.dumps(s, ensure_ascii=False, indent=1)}")
    elif a.cmd == "show":
        print(json.dumps(load_shop(), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
