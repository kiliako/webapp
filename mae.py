import time
import requests
from typing import Optional, Tuple
from config import MAE_FOR_URL

_MAE_CACHE = {"ts": 0.0, "price": None, "var": None}

def get_usd_may_from_mae(cache_seconds: int = 30) -> Tuple[Optional[float], Optional[float]]:
    now = time.time()
    if (now - _MAE_CACHE["ts"]) < cache_seconds:
        return _MAE_CACHE["price"], _MAE_CACHE["var"]
    try:
        r = requests.get(MAE_FOR_URL, timeout=4)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            row = data[0]
            def _to_float(x):
                try: return float(x)
                except Exception: return None
            price = _to_float(row.get("ultimo"))
            var   = _to_float(row.get("variacion"))
            _MAE_CACHE.update(ts=now, price=price, var=var)
            return price, var
    except Exception:
        return _MAE_CACHE["price"], _MAE_CACHE["var"]
    return None, None
