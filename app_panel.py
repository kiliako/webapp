


## Raíz

### `app_panel.py`

import panel as pn
from ui.theme import template
from ui.toolbar import toolbar, _refresh_status, status_label
from ui.subscriptions import subs_card
from ui.letras_tab import letras_tab, letras_tabulator, letras_md
from ui.ggal_tab import (
    ggal_tab, ggal_tabulator, days_input, r_input, q_input,
    calls_ms, puts_ms, refresh_gal_option_lists, ensure_underlying_sub
)
from letras import build_letras_df, LETRAS_CHART
from ggal import get_underlying_last_and_var, get_mep_last_and_var, ensure_mep_sub
from mae import get_usd_may_from_mae
from utils import fmt_thousand, bcra_bands_for_date, to_float
from connection import connect_pyrofex, drain_queue
from config import UNDERLYING_GGAL
from datetime import date

pn.extension("tabulator", sizing_mode="stretch_width", notifications=True)

# Layout principal
template.main.insert(0, toolbar)
template.main.append(letras_tab)
template.main.append(ggal_tab)
template.main.append(pn.Spacer(height=8))
template.main.append(subs_card)

def update_all():
    drain_queue(4000)
    _refresh_status()
    refresh_gal_option_lists()
    ensure_mep_sub()
    ensure_underlying_sub()

    # --- Letras: tabla + gráfico ---
    df_letras = build_letras_df()
    letras_tabulator.value = df_letras
    letras_tabulator.height = 44 + max(len(df_letras), 1) * 30
    LETRAS_CHART.update(df_letras)

    # --- GGAL Opciones ---
    days = max(int(days_input.value or 30), 1)
    r    = float(r_input.value or 60.0)
    q    = float(q_input.value or 0.0)
    from ggal import build_gal_options_df  # lazy import para evitar ciclos
    df_opt = build_gal_options_df(list(calls_ms.value), list(puts_ms.value), r, q, days)
    ggal_tabulator.value = df_opt
    ggal_tabulator.height = 44 + max(len(df_opt), 1) * 30

    # --- Barra GGAL ---
    S0, Svar = get_underlying_last_and_var(UNDERLYING_GGAL)
    s_last = "—" if S0 is None else fmt_thousand(S0, 2)
    if Svar is None:
        var_html = "<span class='value'>—</span>"
    else:
        v = 0.0 if abs(Svar) < 1e-4 else Svar
        s_var_txt = "0,00%" if v == 0 else f"{v:+.2f}%".replace(".", ",")
        color = "#2ecc71" if v > 0 else ("#e74c3c" if v < 0 else "#000000")
        var_html = f"<span class='value' style='color:{color};font-weight:700'>{s_var_txt}</span>"
    from ui.ggal_tab import under_md
    under_md.object = (
        f"**GGAL**  <span class='label'>:</span> "
        f"<span class='value'>{s_last}</span>  |  "
        f"<span class='label'>Var:</span> {var_html}"
    )

    # --- Barra LETRAS: MEP + USD Mayorista + Bandas ---
    mep_last, mep_var = get_mep_last_and_var()
    mep_last_txt = "—" if mep_last is None else fmt_thousand(mep_last, 2)
    if mep_var is None:
        mep_var_html = "<span class='value'>—</span>"
    else:
        vv = 0.0 if abs(mep_var) < 1e-4 else mep_var
        txt = "0,00%" if vv == 0 else f"{vv:+.2f}%".replace(".", ",")
        col = "#2ecc71" if vv > 0 else ("#e74c3c" if vv < 0 else "#000000")
        mep_var_html = f"<span class='value' style='color:{col};font-weight:700'>{txt}</span>"

    usd_last, usd_var = get_usd_may_from_mae(cache_seconds=30)
    usd_last_txt = "—" if usd_last is None else fmt_thousand(usd_last, 2)
    if usd_var is None:
        usd_var_html = "<span class='value'>—</span>"
    else:
        uv  = 0.0 if abs(usd_var) < 1e-4 else usd_var
        utxt = "0,00%" if uv == 0 else f"{uv:+.2f}%".replace(".", ",")
        ucol = "#2ecc71" if uv > 0 else ("#e74c3c" if uv < 0 else "#000000")
        usd_var_html = f"<span class='value' style='color:{ucol};font-weight:700'>{utxt}</span>"

    piso_hoy, techo_hoy = bcra_bands_for_date(date.today())
    letras_md.object = (
        f"**MEP (AL30/AL30D)**  <span class='label'>:</span> "
        f"<span class='value'>{mep_last_txt}</span>  |  "
        f"<span class='label'>Var:</span> {mep_var_html}"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        f"**USD/ARS:** <span class='value'>{usd_last_txt}</span>  |  "
        f"<span class='label'>Var:</span> {usd_var_html}"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        f"<span class='label'>Bandas hoy:</span> "
        f"<span class='value'>{fmt_thousand(piso_hoy,2)}</span> – "
        f"<span class='value'>{fmt_thousand(techo_hoy,2)}</span>"
    )

pn.state.add_periodic_callback(update_all, period=500, start=True)

def _boot():
    connect_pyrofex()
    refresh_gal_option_lists()
    _refresh_status()
    ensure_mep_sub()
    ensure_underlying_sub()
_boot()

# panel serve app_panel.py --autoreload --show
template.servable()
