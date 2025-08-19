import time
import numpy as np
import pandas as pd
from datetime import date, datetime
from typing import Any, Dict, Optional
from bokeh.models import ColumnDataSource, HoverTool, LabelSet, Range1d
from bokeh.plotting import figure
import panel as pn

from state import STATE
from utils import to_float, fmt_thousand, clean_symbol
from config import VTO_MAP, FINISH_MAP
from ggal import get_mep_last_and_var

def build_letras_df() -> pd.DataFrame:
    today = date.today()
    mep_last, _ = get_mep_last_and_var()
    rows = []
    for sym in STATE.subscribed_order:
        inst_clean = clean_symbol(sym)
        if " - " not in inst_clean:
            continue
        left = inst_clean.split(" - ")[0].strip()
        if left.upper() in ("GGAL","YPFD","PAMP","ALUA","CEPU","AL30","AL30D"):
            continue
        if ("GFGC" in left.upper()) or ("GFGV" in left.upper()):
            continue

        rec: Dict[str, Any] = STATE.md.get(sym, {})
        last  = to_float(rec.get("LAST"))
        bid   = to_float(rec.get("BID")); bid_sz = rec.get("BID_SIZE")
        ask   = to_float(rec.get("ASK")); ask_sz = rec.get("ASK_SIZE")
        close = to_float(rec.get("CLOSE"))
        ts    = rec.get("TS")

        var_abs = (last - close) if (last is not None and close not in (None, 0)) else None
        var_pct = (var_abs / close * 100.0) if (var_abs is not None and close) else None

        finish = FINISH_MAP.get(left)
        vto_str = VTO_MAP.get(left)
        vto = None
        if vto_str:
            try:
                vto = datetime.strptime(vto_str, "%Y-%m-%d").date()
            except Exception:
                vto = None

        dias = (vto - today).days - 1 if vto else None
        if dias is not None and dias < 0:
            dias = 0

        por_ganar = tna = tea = None
        if finish and last and dias and dias > 0 and last > 0:
            try:
                ratio = finish / last
                por_ganar = (ratio - 1.0) * 100.0
                tna = ((ratio - 1.0) * 365.0 / dias) * 100.0
                tea = ((ratio ** (365.0 / dias)) - 1.0) * 100.0
            except Exception:
                pass

        mep_mul = None
        if (mep_last is not None) and (tna is not None) and (dias is not None):
            try:
                mep_mul = mep_last * (1.0 + (tna/100.0/365.0) * dias)
            except Exception:
                mep_mul = None

        banda_sup = None
        pct_sobre = None
        try:
            if vto is not None:
                n_meses = (vto.year - 2025) * 12 + (vto.month - 4)
                if n_meses < 0: n_meses = 0
                banda_sup_val = 1400.0 * (1.0 + 0.01 * n_meses)
                banda_sup = banda_sup_val
                if (mep_mul is not None) and (banda_sup_val != 0):
                    pct_sobre = ((mep_mul - banda_sup_val) / banda_sup_val) * 100.0
        except Exception:
            banda_sup = None
            pct_sobre = None

        def var_html(v: Optional[float]):
            if v is None:
                return ""
            s = f"{v:+.2f}".replace(".", ",")
            if v > 0:
                bg = "rgba(46,204,113,.22)"
            elif v < 0:
                bg = "rgba(231,76,60,.22)"
            else:
                bg = "transparent"
            return f"<span class='iv-cell' style='background:{bg}'>{s}</span>"

        rows.append({
            "Instrumento": inst_clean,
            "Vol.C": "" if bid_sz is None else f"{int(bid_sz):,}".replace(",", "."),
            "Compra": "" if bid   is None else fmt_thousand(bid, 3),
            "Venta":  "" if ask   is None else fmt_thousand(ask, 3),
            "Vol.V": "" if ask_sz is None else f"{int(ask_sz):,}".replace(",", "."),
            "Últ":    "" if last  is None else fmt_thousand(last, 3),
            "Var":    var_html(var_abs),
            "Var %":  var_html(var_pct),
            "Por Ganar": "" if por_ganar is None else f"{por_ganar:.2f}".replace(".", ","),
            "TNA":       "" if tna       is None else f"{tna:.2f}".replace(".", ","),
            "TEA":       "" if tea       is None else f"{tea:.2f}".replace(".", ","),
            "VTO": "" if not vto else vto.strftime("%d/%m/%Y"),
            "DIAS": "" if dias is None else int(dias),
            "FINISH": "" if finish is None else fmt_thousand(finish, 2),
            "MEP": "" if mep_mul is None else fmt_thousand(mep_mul, 2),
            "Banda Sup": "" if banda_sup is None else fmt_thousand(banda_sup, 2),
            "% sobre banda": "" if pct_sobre is None else f"{pct_sobre:+.2f}".replace(".", ","),
            "Último cambio": "" if not ts else time.strftime("%H:%M:%S", time.localtime(ts)),
        })

    cols = ["Instrumento","Vol.C","Compra","Venta","Vol.V","Últ","Var","Var %",
            "Por Ganar","TNA","TEA","VTO","DIAS","FINISH","MEP","Banda Sup","% sobre banda","Último cambio"]
    return pd.DataFrame(rows, columns=cols)

class LetrasChart:
    def __init__(self):
        self.src = ColumnDataSource(dict(x=[], y=[], label=[], y_label=[]))
        p = figure(height=500, sizing_mode="stretch_width",
                   background_fill_color="#0f1115", border_fill_color="#0f1115",
                   toolbar_location=None)
        p.y_range = Range1d(start=0, end=1)
        p.circle("x","y", size=7, source=self.src, line_alpha=0, fill_alpha=0.9)
        labels = LabelSet(
            x='x', y='y_label', text='label', source=self.src,
            text_font_size='7pt', text_color="#e6e6e6",
            text_align="center", text_baseline="bottom",
            y_offset=8,
            background_fill_color="#0f1115",
            background_fill_alpha=0.6
        )
        p.add_layout(labels)

        p.xaxis.axis_label = "DIAS"
        p.yaxis.axis_label = "TEA (%)"
        p.xaxis.major_label_text_color = "#c9d1d9"
        p.yaxis.major_label_text_color = "#c9d1d9"
        p.axis.axis_label_text_color = "#a9b1bd"
        p.grid.grid_line_alpha = 0.25
        p.add_tools(HoverTool(tooltips=[("Días","@x{0}"),("TEA","@y{0.00}%"),("Letra","@label")]))
        self.fig = p
        self.pane = pn.pane.Bokeh(self.fig)

    def update(self, df: pd.DataFrame):
        if df is None or df.empty:
            self.src.data = dict(x=[], y=[], y_label=[], label=[])
            return

        data = df.copy()
        data["LETRA"] = data["Instrumento"].str.split(" - ").str[0].str.strip()
        data = data[(data["TEA"].astype(str) != "") & (data["DIAS"].astype(str) != "")]
        data = data[data["LETRA"].str.upper() != "TY30P"]
        if data.empty:
            self.src.data = dict(x=[], y=[], y_label=[], label=[])
            return

        def to_num(v):
            try:
                return float(str(v).replace(",", "."))
            except Exception:
                return np.nan

        x = data["DIAS"].apply(to_num).values.astype(float)
        y = data["TEA"].apply(to_num).values.astype(float)
        label = data["LETRA"].fillna("").astype(str).values

        mask = np.isfinite(x) & np.isfinite(y)
        x, y, label = x[mask], y[mask], label[mask]

        if len(y):
            y_min = float(np.min(y)); y_max = float(np.max(y))
            if not np.isfinite(y_min) or not np.isfinite(y_max):
                y_min, y_max = 0.0, 1.0
            if y_max - y_min < 1e-9:
                y_min -= 1.0; y_max += 1.0
            pad = 10.0
            self.fig.y_range.start = y_min - pad
            self.fig.y_range.end   = y_max + pad

        if len(x):
            order = np.argsort(x)
            span = float(np.ptp(y)) if np.ptp(y) > 0 else 1.0
            off = (np.mod(np.arange(len(order)), 2) * 2 - 1) * (span * 0.02)
            y_label = y.copy()
            y_label[order] = y_label[order] + off
        else:
            y_label = y

        self.fig.renderers = [r for r in self.fig.renderers if getattr(r, "name", "") != "trend"]
        if len(x) > 2:
            coef = np.polyfit(x, y, deg=2)
            poly = np.poly1d(coef)
            x_fit = np.linspace(float(np.min(x)), float(np.max(x)), 200)
            y_fit = poly(x_fit)
            self.fig.line(x_fit, y_fit, line_color="orange", line_width=2, alpha=0.8,
                          legend_label="Tendencia", name="trend")

        self.src.data = dict(x=x, y=y, y_label=y_label, label=label)

LETRAS_CHART = LetrasChart()
