import panel as pn
import pandas as pd
from letras import LETRAS_CHART

letras_cols_config = [
    {"title":"Instrumento","field":"Instrumento","hozAlign":"center"},
    {"title":"Vol.C","field":"Vol.C","hozAlign":"center","cssClass":"tab-num"},
    {"title":"Compra","field":"Compra","hozAlign":"center","cssClass":"tab-price"},
    {"title":"Venta","field":"Venta","hozAlign":"center","cssClass":"tab-price"},
    {"title":"Vol.V","field":"Vol.V","hozAlign":"center","cssClass":"tab-num"},
    {"title":"Últ","field":"Últ","hozAlign":"center","cssClass":"tab-price"},
    {"title":"Var","field":"Var","formatter":"html","hozAlign":"center"},
    {"title":"Var %","field":"Var %","formatter":"html","hozAlign":"center"},
    {"title":"Falta (%)","field":"Por Ganar","hozAlign":"center"},
    {"title":"TNA (%)","field":"TNA","hozAlign":"center"},
    {"title":"TEA (%)","field":"TEA","hozAlign":"center"},
    {"title":"VTO","field":"VTO","hozAlign":"center"},
    {"title":"DIAS","field":"DIAS","hozAlign":"center"},
    {"title":"FINISH","field":"FINISH","hozAlign":"center"},
    {"title":"MEP","field":"MEP","hozAlign":"center"},
    {"title":"Banda","field":"Banda Sup","hozAlign":"center"},
    {"title":"% s/ banda","field":"% sobre banda","hozAlign":"center"},
    {"title":"Último","field":"Último cambio","hozAlign":"center"},
]

letras_tabulator = pn.widgets.Tabulator(
    pd.DataFrame(columns=[c["field"] for c in letras_cols_config]),
    pagination=None, selectable=False, layout="fit_data_table", height=300,
    configuration={
        "columnDefaults": {
            "hozAlign": "center",
            "vertAlign": "middle",
            "headerHozAlign": "center",
            "headerSort": False
        },
        "columns": letras_cols_config,
        "rowHeight": 22,
    },
    show_index=False,
)
letras_md = pn.pane.Markdown(
    "**MEP (AL30/AL30D)** — <span class='label'>Últ:</span> <span class='value'>—</span>  |  "
    "<span class='label'>Var:</span> <span class='value'>—</span>",
    css_classes=["metric"],
    styles={"margin":"0","width":"100%","text-align":"center","font-size":"18px","line-height":"1.15","white-space":"nowrap"}
)
letras_bar = pn.Row(letras_md, sizing_mode="stretch_width", height=28, margin=(0, 0, 12, 0))
letras_wrap = pn.Column(letras_tabulator, css_classes=["tbl-letras"], sizing_mode="stretch_width")

letras_tab = pn.Column(
    letras_bar,
    pn.pane.Markdown("### Letras"),
    letras_wrap,
    pn.Spacer(height=8),
    pn.pane.Markdown("#### Curva TEA vs Días a Vto"),
    LETRAS_CHART.pane
)
