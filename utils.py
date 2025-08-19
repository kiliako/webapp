import json
import numpy as np
import pandas as pd
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional
from config import SAVE_TICKERS, SAVE_PANEL_CFG

def to_float(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    try:
        return float(x)
    except Exception:
        return None

def fmt_thousand(x: Optional[float], dec: int) -> str:
    if x is None or (isinstance(x, float) and (np.isnan(x))):
        return ""
    try:
        s = f"{float(x):,.{dec}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return ""

def parse_input_tickers(text: str) -> List[str]:
    raw = []
    for line in (text or "").splitlines():
        raw.extend([p.strip() for p in line.split(",")])
    return [t for t in raw if t]

def clean_symbol(symbol: str) -> str:
    if not symbol:
        return symbol
    parts = [p.strip() for p in symbol.split("-")]
    if len(parts) >= 4 and parts[0] == "MERV" and parts[1] == "XMEV":
        return f"{parts[2]} - {parts[3]}"
    return symbol

def load_saved_tickers() -> List[str]:
    try:
        if SAVE_TICKERS.exists():
            return [ln.strip() for ln in SAVE_TICKERS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except Exception:
        pass
    return []

def save_tickers_list(tickers: List[str]) -> None:
    try:
        norm = [t for t in [t.strip() for t in tickers] if t]
        SAVE_TICKERS.write_text("\n".join(norm), encoding="utf-8")
    except Exception:
        pass

def load_panel_cfg(state_obj) -> None:
    if SAVE_PANEL_CFG.exists():
        try:
            d = json.loads(SAVE_PANEL_CFG.read_text(encoding="utf-8"))
            state_obj.saved_calls = d.get("ggal_calls", [])
            state_obj.saved_puts  = d.get("ggal_puts", [])
        except Exception:
            pass

def save_panel_cfg(state_obj) -> None:
    try:
        SAVE_PANEL_CFG.write_text(json.dumps({
            "ggal_calls": state_obj.saved_calls,
            "ggal_puts":  state_obj.saved_puts
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def bcra_bands_for_date(d: date) -> tuple[float, float]:
    n_meses = (d.year - 2025) * 12 + (d.month - 4)
    if n_meses < 0:
        n_meses = 0
    piso  = 1000.0 * (1.0 - 0.01 * n_meses)
    techo = 1400.0 * (1.0 + 0.01 * n_meses)
    return piso, techo
