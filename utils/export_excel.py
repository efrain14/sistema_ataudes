import pandas as pd
from database.daos import AtaudDAO, HistorialDAO
import os
from datetime import datetime

def exportar_inventario_excel(ruta_destino):
    df = pd.DataFrame(AtaudDAO.listar())
    if df.empty:
        return False, "No hay datos"
    df.to_excel(ruta_destino, index=False, sheet_name="Inventario")
    return True, ruta_destino

def exportar_historial_excel(ruta_destino):
    df = pd.DataFrame(HistorialDAO.todos())
    if df.empty:
        return False, "No hay historial"
    df.to_excel(ruta_destino, index=False, sheet_name="Historial")
    return True, ruta_destino