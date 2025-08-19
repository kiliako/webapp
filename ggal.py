import math
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from state import STATE
from utils import to_float, fmt_thousand, save_panel_cfg
from config import UNDERLYING_GGAL, UNDERLYING_MEP_A, UNDERLYING_MEP_B
from connection import subscribe_list

try:
    from scipy.stats import norm
    def ndist(x: float) -> float: return float(norm.cdf(x))
except Exception:
    def ndist(x: float) -> float: return 0.5*(1.0+math.erf(x/math.sqrt(2)))

def is_call_code(code: str) -> bool:
    part = code.split("-")[2].strip() if " - " in code else code
    return "C" in part.upper() and "V" not in part.upper()

def is_put_code(code: str) -> bool:
    part = code.split("-")[2].strip() if " - " in code else code
    return "V" in part.upper()

def parse_strike_from_code(code: str) -> Optional[float]:
    try:
        middle = code.split("-")[2].strip()
        digits = "".join([ch for ch in middle if ch.isdigit()])
        if not digits: return None
        return int(digits) / 10.0
    except Exception:
        return None

def bs_price(S, K, T, r, sigma, is_call=True, q=0.0):
    if S<=0 or K<=0 or T<=0 or sigma<=0: return None
    try:
        d1 = (math.log(S/K) + (r - q + 0.5*sigma*sigma)*T) / (sigma*math.sqrt(T))
        d2 = d1 - sigma*math.sqrt(T)
        if is_call:
            return S*math.exp(-q*T)*ndist(d1) - K*math.exp(-r*T)*ndist(d2)
        else:
            return K*math.exp(-r*T)*ndist(-d2) - S*math.exp(-q*T)*ndist(-d1)
    except Exception:
        return None

def implied_vol(price, S, K, T, r, is_call=True, q=0.0, lo=1e-4, hi=5.0, tol=1e-4, maxit=60):
    if price is None or S is None or K is None or T is None or T<=0 or S<=0 or K<=0:
        return None
    f_lo = bs_price(S,K,T,r,lo,is_call,q)
    f_hi = bs_price(S,K,T,r,hi,is_call,q)
    if f_lo is None or f_hi is None: return None
    if (f_lo - price)*(f_hi - price) > 0:
        hi_try = hi
        for _ in range(5):
            hi_try *= 2
            f_hi = bs_price(S,K,T,r,hi_try,is_call,q)
            if f_hi is None: break
            if (f_lo - price)*(f_hi - price) <= 0: hi = hi_try; break
        else:
            return None
    a, b = lo, hi
    fa = bs_price(S,K,T,r,a,is_call,q) - price
    fb = bs_price(S,K,T,r,b,is_call,q) - price
    for _ in range(maxit):
        m = 0.5*(a+b)
        fm = bs_price(S,K,T,r,m,is_call,q) - price
        if fm == 0 or (b-a)/2 < tol: return max(m, 0.0)
        if (fa*fm) < 0: b = m; fb = fm
        else: a = m; fa = fm
    return max(0.5*(a+b), 0.0)

def get_underlying_last_and_var(symbol=UNDERLYING_GGAL) -> Tuple[Optional[float], Optional[float]]:
    rec = STATE.md.get(symbol, {})
    last = to_float(rec.get("LAST"))
    close = to_float(rec.get("CLOSE"))
    var_pct = None
    if last is not None and close not in (None, 0):
        var_pct = (last - close) / close * 100.0
    return last, var_pct

def get_mep_last_and_var() -> Tuple[Optional[float], Optional[float]]:
    a = STATE.md.get(UNDERLYING_MEP_A, {})
    b = STATE.md.get(UNDERLYING_MEP_B, {})
    la, lb = to_float(a.get("LAST")),  to_float(b.get("LAST"))
    ca, cb = to_float(a.get("CLOSE")), to_float(b.get("CLOSE"))
    mep_last  = (la / lb) if (la and lb) else None
    mep_close = (ca / cb) if (ca and cb) else None
    var_pct = ((mep_last - mep_close) / mep_close * 100.0) if (mep_last and mep_close) else None
    return mep_last, var_pct

def ensure_mep_sub():
    need = []
    for s in (UNDERLYING_MEP_A, UNDERLYING_MEP_B):
        if s not in STATE.subscribed_set:
            need.append(s)
    if need:
        subscribe_list(need)

def build_gal_options_df(calls: List[str], puts: List[str],
                         r_annual_pct: float, q_div_yield_pct: float, days_to_expiry: int) -> pd.DataFrame:
    S0, _ = get_underlying_last_and_var(UNDERLYING_GGAL)
    T = max(days_to_expiry, 1)/365.0
    r = r_annual_pct/100.0
    q = q_div_yield_pct/100.0

    all_syms = set(calls) | set(puts)
    strikes: Dict[float, Dict[str, Optional[str]]] = {}
    for sym in sorted(all_syms):
        K = parse_strike_from_code(sym)
        if K is None: continue
        d = strikes.setdefault(K, {"call": None, "put": None})
        if is_call_code(sym): d["call"] = sym
        elif is_put_code(sym): d["put"] = sym

    rows = []
    for K in sorted(strikes.keys()):
        row = {
            "CALL Ask": None, "IV Ask (CALL)": None, "Notas": None,
            "IV Bid (CALL)": None, "CALL Bid": None, "Pos CALLs": None,
            "Strike": round(K, 2), "Pos PUTs": None,
            "PUT Ask": None, "IV Ask (PUT)": None, "Notas 2": None,
            "IV Bid (PUT)": None, "PUT Bid": None
        }

        csym = strikes[K]["call"]
        if csym in STATE.md:
            md = STATE.md[csym]
            ask = to_float(md.get("BID")); bid = to_float(md.get("ASK"))
            row["CALL Ask"] = None if ask is None else round(ask, 2)
            row["CALL Bid"] = None if bid is None else round(bid, 2)
            if S0 and ask:
                iv_a = implied_vol(ask, S0, K, T, r, is_call=True, q=q)
                row["IV Ask (CALL)"] = None if iv_a is None else round(iv_a*100.0, 2)
            if S0 and bid:
                iv_b = implied_vol(bid, S0, K, T, r, is_call=True, q=q)
                row["IV Bid (CALL)"] = None if iv_b is None else round(iv_b*100.0, 2)

        psym = strikes[K]["put"]
        if psym in STATE.md:
            md = STATE.md[psym]
            ask = to_float(md.get("BID")); bid = to_float(md.get("ASK"))
            row["PUT Ask"] = None if ask is None else round(ask, 2)
            row["PUT Bid"] = None if bid is None else round(bid, 2)
            if S0 and ask:
                iv_a = implied_vol(ask, S0, K, T, r, is_call=False, q=q)
                row["IV Ask (PUT)"] = None if iv_a is None else round(iv_a*100.0, 2)
            if S0 and bid:
                iv_b = implied_vol(bid, S0, K, T, r, is_call=False, q=q)
                row["IV Bid (PUT)"] = None if iv_b is None else round(iv_b*100.0, 2)

        rows.append(row)

    cols = ["CALL Ask","IV Ask (CALL)","Notas","IV Bid (CALL)","CALL Bid","Pos CALLs",
            "Strike","Pos PUTs","PUT Ask","IV Ask (PUT)","Notas 2","IV Bid (PUT)","PUT Bid"]
    df = pd.DataFrame(rows, columns=cols)

    iv_cols = ["IV Ask (CALL)","IV Bid (CALL)","IV Ask (PUT)","IV Bid (PUT)"]
    vals = []
    for c in iv_cols:
        if c in df: vals.extend([v for v in df[c].tolist() if isinstance(v,(int,float))])
    vmin = min(vals) if vals else 10.0
    vmax = max(vals) if vals else 150.0
    if abs(vmax - vmin) < 1e-9: vmin, vmax = max(0.0, vmin-1.0), vmin+1.0

    def _iv_color(value: float, vmin: float, vmax: float, invert: bool=False) -> str:
        if value is None: return "#00000000"
        t = 0.0 if vmax<=vmin else (value - vmin) / (vmax - vmin)
        t = max(0.0, min(1.0, t))
        if invert: t = 1.0 - t
        r = int(46 + t*(231-46))
        g = int(204 + t*(76-204))
        b = int(113 + t*(60-113))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _iv_html(v: Optional[float], vmin: float, vmax: float, invert: bool=False) -> str:
        if v is None: return ""
        c = _iv_color(v, vmin, vmax, invert=invert)
        txt = f"{v:.2f}".replace(".", ",")
        return f"<span class='iv-cell' style='background:{c}'>{txt}</span>"

    for c in iv_cols:
        if c in df: df[c] = df[c].apply(lambda v: _iv_html(v, vmin, vmax, invert=False))
    return df

def refresh_gal_option_lists():
    from utils import load_saved_tickers
    universe = set(STATE.md.keys()) | set(STATE.subscribed_order) | set(load_saved_tickers())
    def _is_ggal_option(sym: str) -> bool:
        if " - " not in sym: return False
        middle = sym.split(" - ")[2].strip().upper()
        return middle.startswith("GFGC") or middle.startswith("GFGV")
    syms = sorted([s for s in universe if _is_ggal_option(s)])
    from ui.ggal_tab import calls_ms, puts_ms
    all_calls = [s for s in syms if is_call_code(s)]
    all_puts  = [s for s in syms if is_put_code(s)]
    calls_ms.options = all_calls
    puts_ms.options  = all_puts
    calls_ms.value = [v for v in STATE.saved_calls if v in all_calls]
    puts_ms.value  = [v for v in STATE.saved_puts  if v in all_puts]

def ensure_underlying_sub():
    if UNDERLYING_GGAL not in STATE.subscribed_set:
        subscribe_list([UNDERLYING_GGAL])
