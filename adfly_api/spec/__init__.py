"""接口清单加载器。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.json"
ENDPOINTS_PATH = HERE / "endpoints.json"


@lru_cache(maxsize=1)
def config() -> Dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_endpoints() -> List[Dict[str, Any]]:
    if not ENDPOINTS_PATH.exists():
        return []
    return json.loads(ENDPOINTS_PATH.read_text(encoding="utf-8"))
