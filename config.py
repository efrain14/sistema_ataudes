import os

# Rutas base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventario_ataudes.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
QR_DIR = os.path.join(ASSETS_DIR, "qr")

# Crear carpetas si no existen
for d in [ASSETS_DIR, BACKUPS_DIR, QR_DIR]:
    os.makedirs(d, exist_ok=True)

# Umbral crítico de usos (a partir de aquí se bloquea)
UMBRAL_USOS_CRITICO = 20

# Estados válidos
ESTADOS_VALIDOS = ("Disponible", "En Uso", "En Restauración", "Dado de Baja")

# Servidor web para escaneo móvil (Opción A)
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
WEB_SECRET = "cambia-esta-clave-secreta-en-produccion"