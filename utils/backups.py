import shutil, os
from config import DB_PATH, BACKUPS_DIR
from datetime import datetime

def crear_backup():
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    nombre = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = os.path.join(BACKUPS_DIR, nombre)
    shutil.copy2(DB_PATH, destino)
    return destino