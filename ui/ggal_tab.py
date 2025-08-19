import panel as pn
import pandas as pd
from state import STATE
from utils import save_panel_cfg
from ggal import is_call_code, is_put_code, refresh_gal_option_lists, ensure_underlying_sub

def underlying_short(symbol: str) -> str:
    return symbol.split(" - ")[2].strip() if " - " in symbol else symbol

under_md = pn.pane.Markdown(
    "**GGAL** — <span class='label'>Últ:</span> <span class='value'>—</span>  |  "
    "<span class='label'>Var:</span> <span class='value'>—</span>",
    css_classes=["metric"],
    styles={"margin":"0","width":"100%","text-align":"center","font-size":"18px","line-height":"1.15","white-space":"nowrap"}
)
under_bar = pn.Row(pn.layout.HSpacer(), under_md, pn.layout.HSpacer(),
                   sizing_mode="stretch_width", height=28, margin=(0, 0, 20, 0))

ggal_cols_config = [
    {"title":"CALL Ask","field":"CALL Ask","hozAlign":"center","cssClass":"tab-price"},
    {"title":"IV Ask (CALL) %","field":"IV Ask (CALL)","formatter":"html","hozAlign":"center"},
    {"title":"Notas","field":"Notas","hozAlign":"center"},
    {"title":"IV Bid (CALL) %","field":"IV Bid (CALL)","formatter":"html","hozAlign":"center"},
    {"title":"CALL Bid","field":"CALL Bid","hozAlign":"center","cssClass":"tab-price"},
    {"title":"Pos CALLs","field":"Pos CALLs","hozAlign":"center"},
    {"title":"Strike","field":"Strike","hozAlign":"center"},
    {"title":"Pos PUTs","field":"Pos PUTs","hozAlign":"center"},
    {"title":"PUT Ask","field":"PUT Ask","hozAlign":"center","cssClass":"tab-price"},
    {"title":"IV Ask (PUT) %","field":"IV Ask (PUT)","formatter":"html","hozAlign":"center"},
    {"title":"Notas 2","field":"Notas 2","hozAlign":"center"},
    {"title":"IV Bid (PUT) %","field":"IV Bid (PUT)","formatter":"html","hozAlign":"center"},
    {"title":"PUT Bid","field":"PUT Bid","hozAlign":"center","cssClass":"tab-price"},
]

ggal_tabulator = pn.widgets.Tabulator(
    pd.DataFrame(columns=[c["field"] for c in ggal_cols_config]),
    pagination=None, selectable=False, layout="fit_data_table", height=240,
    configuration={
        "columnDefaults": {
            "hozAlign": "center",
            "vertAlign": "middle",
            "headerHozAlign": "center",
            "headerSort": False
        },
        "columns": ggal_cols_config,
        "rowHeight": 24,
    },
    show_index=False,
)

ggal_wrap = pn.Column(ggal_tabulator, css_classes=["tbl-ggal"], sizing_mode="stretch_width")

days_input = pn.widgets.IntInput(name="Días a Vto", value=30, step=1, width=120)
r_input    = pn.widgets.FloatInput(name="Tasa libre (anual %)", value=60.0, step=0.25, width=160)
q_input    = pn.widgets.FloatInput(name="Div. yield (anual %)", value=0.0, step=0.1, width=160)

calls_ms = pn.widgets.MultiSelect(name="CALLs GGAL", options=[], value=[], size=10, width=520)
puts_ms  = pn.widgets.MultiSelect(name="PUTs GGAL",  options=[], value=[], size=10, width=520)

btn_sel_calls = pn.widgets.Button(name="Seleccionar TODOS los CALLs", button_type="primary", width=260)
btn_sel_puts  = pn.widgets.Button(name="Seleccionar TODOS los PUTs",  button_type="primary", width=260)
btn_sel_all   = pn.widgets.Button(name="Seleccionar TODO (CALLs + PUTs)", button_type="primary", width=300)

def select_all_calls(event):
    calls_ms.value = list(calls_ms.options)
    STATE.saved_calls = list(calls_ms.value); save_panel_cfg(STATE)
    ensure_underlying_sub()

def select_all_puts(event):
    puts_ms.value = list(puts_ms.options)
    STATE.saved_puts = list(puts_ms.value); save_panel_cfg(STATE)
    ensure_underlying_sub()

def select_all_both(event):
    select_all_calls(event); select_all_puts(event)

btn_sel_calls.on_click(select_all_calls)
btn_sel_puts.on_click(select_all_puts)
btn_sel_all.on_click(select_all_both)

def on_calls_change(event):
    STATE.saved_calls = list(event.new); save_panel_cfg(STATE)
    from connection import subscribe_list
    need = [s for s in event.new if s not in STATE.subscribed_set]
    if need: subscribe_list(need)
    ensure_underlying_sub()

def on_puts_change(event):
    STATE.saved_puts = list(event.new); save_panel_cfg(STATE)
    from connection import subscribe_list
    need = [s for s in event.new if s not in STATE.subscribed_set]
    if need: subscribe_list(need)
    ensure_underlying_sub()

calls_ms.param.watch(on_calls_change, "value")
puts_ms.param.watch(on_puts_change, "value")

ggal_tab = pn.Column(
    under_bar,
    pn.layout.Divider(margin=(0,0,4,0)),
    ggal_wrap,
    pn.Spacer(height=6),
    pn.Row(btn_sel_calls, btn_sel_puts, btn_sel_all, margin=(0,0,0,0)),
    pn.Row(calls_ms, puts_ms, margin=(0,0,0,0)),
    pn.Spacer(height=6),
    pn.Row(days_input, r_input, q_input, margin=(0,0,0,0)),
    margin=(0,0,0,0)
)
