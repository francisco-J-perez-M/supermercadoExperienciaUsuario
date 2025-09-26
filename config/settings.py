import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

# --- Parámetros de conexión MongoDB ---
MONGO_URI_LOCAL = "mongodb://localhost:27017/"
MONGO_URI_SERVIDOR = os.getenv("MONGO_URI_SERVIDOR", MONGO_URI_LOCAL)
MONGO_DB_NAME = "supermercado_db"

# --- Flags de entorno ---
DESPLIEGUE_LOCAL = os.getenv("DESPLIEGUE_LOCAL", "True") == "True"
DESPLIEGUE_SERVIDOR = os.getenv("DESPLIEGUE_SERVIDOR", "False") == "True"

# --- Parámetros de población inicial ---
REGISTROS_CLIENTES_LOCAL = int(os.getenv("REGISTROS_CLIENTES_LOCAL", "500000"))
REGISTROS_CLIENTES_SERVIDOR = int(os.getenv("REGISTROS_CLIENTES_SERVIDOR", "10"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10000"))

# --- Tema visual para ttkbootstrap ---
GUI_TEMA = os.getenv("GUI_TEMA", "flatly")

# --- Seguridad y control ---
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
