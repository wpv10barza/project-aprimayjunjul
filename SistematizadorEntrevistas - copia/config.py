import os
from pathlib import Path

# --- RUTAS DINÃMICAS DEL PROYECTO ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = BASE_DIR / "inputs"
OUTPUTS_DIR = BASE_DIR / "outputs"
DRIVERS_DIR = BASE_DIR / "drivers"

for d in [DATA_DIR, INPUTS_DIR, OUTPUTS_DIR, DRIVERS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- CONFIGURACIÃ“N CHATGPT ---
CHATGPT_URL = "https://chatgpt.com/"
CHATGPT_TEXTAREA_ID = "prompt-textarea"
CHATGPT_SEND_BUTTON_SELECTOR = "[data-testid='send-button']"

# --- CONFIGURACIÃ“N EDGE ---
_local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local")
EDGE_USER_DATA_DIR = os.path.join(_local_app_data, "Microsoft", "Edge", "User Data")
EDGE_PROFILE_DIR = "Default" 

DEFAULT_WAIT_TIME = 800
DEFAULT_DRIVER_PATH = DRIVERS_DIR / "msedgedriver.exe" 
DEFAULT_SHEETS_URL = None 

# --- RUTAS SISTEMA ---
DEFAULT_DB_CONFIG_PATH = BASE_DIR / "db_config.json"
RESULT_RAW_TXT = DATA_DIR / "resultado_raw.txt"
RESULT_TSV = DATA_DIR / "resultado.tsv"
RESULT_CSV = DATA_DIR / "resultado.csv"
RESULT_XLSX = DATA_DIR / "resultado.xlsx"
MERGED_TSV = DATA_DIR / "merged.tsv"
MERGED_CSV = DATA_DIR / "merged.csv"
MERGED_XLSX = DATA_DIR / "merged.xlsx"

DEFAULT_TARGET_TABLE = "dbo.Respuesta"
DEFAULT_USUARIO_REGISTRO_ID = 1
DEFAULT_SHEET_NAME = "Resultados"

# ==========================================
# CONFIGURACIÃ“N HARDCODED (Rutas Fijas)
# ==========================================

# 1. RUTA DEL PROMPT (FIJA)
PATH_PROMPT_TXT = r"D:\118102025\Downloads\Nueva carpeta\SistematizadorEntrevistas\SistematizadorEntrevistas - copia\REGLA DE CARGA COMPLETA.txt"

# 2. RUTA EXCEL DE GUÃA DE PREGUNTAS (FIJA)
PATH_GUIA_PREGUNTAS_FALLBACK = r"D:\118102025\Downloads\Nueva carpeta\SistematizadorEntrevistas\SistematizadorEntrevistas - copia\respaldo taxonomia_evaluacion_17.xlsx"
# --- EDGE DEBUGGER MODE ---
EDGE_ATTACH_TO_EXISTING = True
EDGE_DEBUG_PORT = 9222
EDGE_PROFILE_DIR = "Default"
EDGE_USER_DATA_DIR = r"C:\Users\ASUS\AppData\Local\Microsoft\Edge\User Data"
EDGE_BINARY_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# --- END EDGE DEBUGGER MODE ---


