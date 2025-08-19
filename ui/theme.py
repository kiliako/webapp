import panel as pn

pn.extension("tabulator", sizing_mode="stretch_width", notifications=True)

pn.config.raw_css.append("""
.tabulator .tabulator-cell {
    font-size: 10px ;
    line-height: 1.2;
    min-height: 28px !important;
}
.tabulator .tabulator-header { font-size: 14px; }
.tbl-letras .tabulator-header,
.tbl-letras .tabulator-header .tabulator-col,
.tbl-ggal   .tabulator-header,
.tbl-ggal   .tabulator-header .tabulator-col {
    background-color: #6D6D70 !important;
    color: #0b1320 !important;
    font-weight: 700;
}
.tbl-letras .tabulator-header .tabulator-col,
.tbl-ggal   .tabulator-header .tabulator-col {
    border-right: 1px solid rgba(0,0,0,0.15) !important;
}
.tbl-letras .tabulator-header .tabulator-col:last-child,
.tbl-ggal   .tabulator-header .tabulator-col:last-child { border-right: none !important; }
.tabulator .tabulator-header { box-shadow: none !important; }
.tbl-letras .tabulator-row .tabulator-cell { padding: 2px 4px !important; line-height: 1.2 !important; }
.tbl-ggal   .tabulator-row .tabulator-cell { padding: 3px 6px !important; line-height: 1.25 !important; }
.tbl-ggal   .tabulator-row { min-height: 24px !important; }

.metric { font-size: 10px; line-height: 1.2; white-space: nowrap; text-align: center; width: 100%; }
.metric .label { color:#a9b1bd; margin-right:6px; }
.metric .value { color:#e6e6e6; font-weight:700; }
.tab-price { background: rgba(255,255,255,0.06); }
.tab-num   { text-align: center; }
.var-green { color: #2ecc71 !important; font-weight: 700; }
.var-red   { color: #e74c3c !important; font-weight: 700; }
.var-zero  { color:#000 !important; font-weight:700; }
.iv-cell   { border-radius: 4px; padding: 0 6px; display: inline-block; width: 100%; }
.ggal-bar  { display:flex; justify-content:center; align-items:center; padding:2px 0; }
.ggal-bar p{ margin:0; }
""")

template = pn.template.FastListTemplate(
    title="pyRofex Live • Letras & Opciones",
    theme="dark",
    header_background="#0f1115",
    header_color="#e6e6e6",
)

template.header.append(
    pn.pane.HTML("""
<style>
.toolbar { position: sticky; top: 0; z-index: 100; background: #0f1115;
  border-bottom: 1px solid #2a2f3a; padding: 6px 10px; margin: 0 0 0 0; }
.statusbar { display:flex; align-items:center; gap:10px; }
</style>
    """, sizing_mode="stretch_width")
)
