import panel as pn
from utils import parse_input_tickers, load_saved_tickers, save_tickers_list
from connection import subscribe_list, unsubscribe_all
from ui.toolbar import _refresh_status

subs_text = pn.widgets.TextAreaInput(
    name="Listado de tickers (uno por línea o separados por coma):",
    height=180, value="\n".join(load_saved_tickers()),
    placeholder=("Ej:\n"
                 "MERV - XMEV - S15G5 - 24hs\n"
                 "MERV - XMEV - S29G5 - 24hs\n"
                 "MERV - XMEV - GFGC65025G - 24hs\n"
                 "MERV - XMEV - GFGV65025G - 24hs")
)

btn_subscribe_list = pn.widgets.Button(name="Suscribir listado", button_type="success", width=160)
btn_unsub_all_main = pn.widgets.Button(name="Desuscribir todo", button_type="danger", width=160)
btn_save_list      = pn.widgets.Button(name="Guardar listado", button_type="primary", width=160)
btn_load_and_sub   = pn.widgets.Button(name="Cargar guardado y suscribir", button_type="warning", width=230)

btn_subscribe_list.on_click(lambda e: (subscribe_list(parse_input_tickers(subs_text.value)), _refresh_status()))
btn_unsub_all_main.on_click(lambda e: (unsubscribe_all(), _refresh_status()))
btn_save_list.on_click(lambda e: save_tickers_list(parse_input_tickers(subs_text.value)))

def _load_and_sub(e):
    saved = load_saved_tickers()
    if saved:
        subs_text.value = "\n".join(saved)
        subscribe_list(saved); _refresh_status()
btn_load_and_sub.on_click(_load_and_sub)

subs_card = pn.Card(
    pn.pane.Markdown("### Suscripciones"),
    subs_text,
    pn.Row(btn_subscribe_list, btn_unsub_all_main, btn_save_list, btn_load_and_sub),
    collapsed=False
)
