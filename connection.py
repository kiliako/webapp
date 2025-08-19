import queue
import time
import pyRofex
from typing import Any, Dict, List
from state import STATE
from config import REST_URL, WS_URL, USUARIO, PASSWORD, CUENTA, missing_env_vars
from utils import save_tickers_list, load_saved_tickers
import panel as pn

def _put(payload: Dict[str, Any]):
    if STATE.msg_queue:
        try:
            STATE.msg_queue.put_nowait(payload)
        except Exception:
            pass

def market_data_handler(message): _put({"type":"marketData","data":message})
def order_report_handler(message): _put({"type":"orderReport","data":message})
def error_handler(message):        _put({"type":"error","data":message})
def exception_handler(e):          _put({"type":"exception","data":str(getattr(e,"message",repr(e)))})

def connect_pyrofex():
    if STATE.connected:
        auto_subscribe_after_connect(); return

    # Validación previa: si faltan credenciales, no intentes conectar
    missing = missing_env_vars()
    if missing:
        # Mostrá un aviso claro en consola (y podés agregar un pn.state.notifications si querés)
        print(f"[CONFIG] Faltan variables en .env: {', '.join(missing)}")
        return

    # Setear endpoints y abrir WS
    pyRofex._set_environment_parameter("url", REST_URL, pyRofex.Environment.LIVE)
    pyRofex._set_environment_parameter("ws",  WS_URL,   pyRofex.Environment.LIVE)

    STATE.msg_queue = queue.Queue()
    pyRofex.initialize(USUARIO, PASSWORD, CUENTA, pyRofex.Environment.LIVE)
    pyRofex.init_websocket_connection(
        market_data_handler=market_data_handler,
        order_report_handler=order_report_handler,
        error_handler=error_handler,
        exception_handler=exception_handler
    )
    STATE.connected = True
    auto_subscribe_after_connect()
    if missing:
        pn.state.notifications.error(f"Faltan variables en .env: {', '.join(missing)}")
        return

def disconnect_pyrofex():
    try: pyRofex.close_websocket_connection()
    except Exception: pass
    STATE.connected = False
    STATE.msg_queue = None

def subscribe_list(tickers: List[str]):
    if not STATE.connected: return
    tickers = [t.strip() for t in tickers if t and t.strip()]
    new = [t for t in tickers if t not in STATE.subscribed_set]
    if not new: return
    entries = [
        pyRofex.MarketDataEntry.LAST,
        pyRofex.MarketDataEntry.BIDS,
        pyRofex.MarketDataEntry.OFFERS,
        pyRofex.MarketDataEntry.CLOSING_PRICE
    ]
    pyRofex.market_data_subscription(tickers=new, entries=entries)
    STATE.subscribed_set.update(new)
    for t in new:
        if t not in STATE.subscribed_order:
            STATE.subscribed_order.append(t)
    save_tickers_list(STATE.subscribed_order)

def unsubscribe_all():
    if STATE.connected and STATE.subscribed_set:
        try: pyRofex.market_data_unsubscription(tickers=list(STATE.subscribed_set))
        except Exception: pass
    STATE.subscribed_set.clear()
    STATE.subscribed_order.clear()
    save_tickers_list([])

def auto_subscribe_after_connect():
    saved = load_saved_tickers()
    if saved: subscribe_list(saved)

def update_md_from_payload(payload: Dict[str, Any]):
    data = payload.get("data", {})
    sym = data.get("instrumentId", {}).get("symbol")
    if not sym: return
    md = data.get("marketData", {})
    la = md.get("LA"); bi = md.get("BI"); ofr = md.get("OF"); cl = md.get("CL")
    rec = STATE.md.get(sym, {
        "LAST": None, "BID": None, "ASK": None, "CLOSE": None,
        "BID_SIZE": None, "ASK_SIZE": None, "TS": None
    })
    if la:  rec["LAST"] = la.get("price")
    if bi and isinstance(bi, list) and len(bi) > 0:
        rec["BID"] = bi[0].get("price"); rec["BID_SIZE"] = bi[0].get("size")
    if ofr and isinstance(ofr, list) and len(ofr) > 0:
        rec["ASK"] = ofr[0].get("price"); rec["ASK_SIZE"] = ofr[0].get("size")
    if cl:  rec["CLOSE"] = cl.get("price")
    rec["TS"] = time.time()
    STATE.md[sym] = rec

def drain_queue(limit=4000):
    if not STATE.msg_queue: return 0
    pulled = 0
    while pulled < limit:
        try: payload = STATE.msg_queue.get_nowait()
        except queue.Empty: break
        pulled += 1
        if payload.get("type") == "marketData":
            update_md_from_payload(payload)
            STATE.md_count += 1
    return pulled
