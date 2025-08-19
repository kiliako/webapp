import panel as pn
from state import STATE
from connection import connect_pyrofex, disconnect_pyrofex, unsubscribe_all

btn_connect    = pn.widgets.Button(name="Conectar",    button_type="success",  width=110, height=32)
btn_disconnect = pn.widgets.Button(name="Desconectar", button_type="warning",  width=120, height=32)
btn_unsub      = pn.widgets.Button(name="Desuscribir todo", button_type="danger", width=150, height=32)
status_label   = pn.pane.Markdown(
    "**Conectado:** ❌  &nbsp;&nbsp;|&nbsp;&nbsp; **Suscriptos:** 0  &nbsp;&nbsp;|&nbsp;&nbsp; **MD:** 0",
    styles={"white-space":"nowrap"}
)

def _refresh_status():
    status_label.object = (f"**Conectado:** {'✅' if STATE.connected else '❌'}"
                           f"  &nbsp;&nbsp;|&nbsp;&nbsp; **Suscriptos:** {len(STATE.subscribed_set)}"
                           f"  &nbsp;&nbsp;|&nbsp;&nbsp; **MD:** {STATE.md_count}")

btn_connect.on_click(lambda e: (connect_pyrofex(), _refresh_status()))
btn_disconnect.on_click(lambda e: (disconnect_pyrofex(), _refresh_status()))
btn_unsub.on_click(lambda e: (unsubscribe_all(), _refresh_status()))

toolbar = pn.Row(btn_connect, btn_disconnect, btn_unsub, pn.layout.HSpacer(), status_label,
                 sizing_mode="stretch_width", css_classes=["toolbar"])
