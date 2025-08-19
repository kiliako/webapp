# config.py
import os
from dotenv import load_dotenv, find_dotenv
import pyRofex
from pathlib import Path

# Carga .env (en la raíz del repo)
load_dotenv(find_dotenv())

# --- Mapear el nombre a enum (robusto) ---
ENV = pyRofex.Environment.LIVE

# --- Credenciales ---
USUARIO  = os.getenv("PYROFEX_USER") or ""
PASSWORD = os.getenv("PYROFEX_PASS") or ""
CUENTA   = os.getenv("PYROFEX_ACCOUNT") or ""

# --- Endpoints ---
REST_URL = os.getenv("REST_URL", "https://api.veta.xoms.com.ar/")
WS_URL   = os.getenv("WS_URL",   "wss://api.veta.xoms.com.ar/")

# --- Archivos locales ---
SAVE_TICKERS   = Path(__file__).with_name("tickers_saved.txt")
SAVE_PANEL_CFG = Path(__file__).with_name("panel_settings.json")

# Underlyings
UNDERLYING_GGAL  = "MERV - XMEV - GGAL - 24hs"
UNDERLYING_MEP_A = "MERV - XMEV - AL30 - 24hs"
UNDERLYING_MEP_B = "MERV - XMEV - AL30D - 24hs"

# MAE
MAE_FOR_URL = "https://api.marketdata.mae.com.ar/api/mercado/resumen/FOR"

# Mapas de VTO y FINISH (como los tenías)
VTO_MAP = {
    'S15G5': '2025-8-19','S29G5': '2025-8-29','S12S5': '2025-9-12','S30S5': '2025-9-30',
    'T17O5': '2025-10-17','S31O5': '2025-10-31','S10N5': '2025-11-10','S28N5': '2025-11-28',
    'T15D5': '2025-12-15','T30E6': '2026-1-30','T13F6': '2026-2-13','S29Y6': '2026-5-29',
    'T30J6': '2026-6-30','TO26': '2026-10-17','T15E7': '2027-1-15','TY30P': '2030-5-30',
}
FINISH_MAP = {
    'S15G5': 146.794496767123,'S29G5': 157.700710502466,'S12S5': 158.976578936986,
    'S30S5': 159.735473315069,'T17O5': 158.870918136986,'S31O5': 132.819735616438,
    'S10N5': 122.252745205479,'S28N5': 123.55976460274,'T15D5': 170.838755342466,
    'T30E6': 142.220193575342,'T13F6': 144.962705479452,'S29Y6': 132.045967123288,
    'T30J6': 144.89499,'TO26': 123,'T15E7': 161.107234493151,'TY30P': 253.533251506849,
}

def missing_env_vars() -> list[str]:
    """Devuelve variables faltantes críticas para conectarse."""
    missing = []
    if not USUARIO:  missing.append("PYROFEX_USER")
    if not PASSWORD: missing.append("PYROFEX_PASS")
    if not CUENTA:   missing.append("PYROFEX_ACCOUNT")
    return missing
