import os
import socket

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

# ============ CONFIGURACIÓN DE RED PARA QR ============
def obtener_ip_local():
    """Obtiene automáticamente la IP local de la PC."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

# IP y puerto del servidor web
WEB_HOST = "0.0.0.0"  # Escucha en todas las interfaces
WEB_PORT = 5000
WEB_SECRET = "cambia-esta-clave-secreta-en-produccion"

# URL base para los QR (se genera automáticamente)
WEB_URL_BASE = f"http://{obtener_ip_local()}:{WEB_PORT}"