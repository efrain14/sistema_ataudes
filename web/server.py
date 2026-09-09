from flask import Flask, render_template, request, redirect, url_for, flash
from database.daos import AtaudDAO, HistorialDAO
from config import WEB_HOST, WEB_PORT, WEB_SECRET, UMBRAL_USOS_CRITICO
import threading

app = Flask(__name__, template_folder="templates")
app.secret_key = WEB_SECRET


@app.route("/movimiento/<codigo_qr>")
def movimiento(codigo_qr):
    ataud = AtaudDAO.buscar_por_codigo(codigo_qr)
    if not ataud:
        return "❌ Ataúd no encontrado", 404
    return render_template("movimiento.html", ataud=ataud, umbral=UMBRAL_USOS_CRITICO)


@app.route("/registrar", methods=["POST"])
def registrar():
    codigo = request.form.get("codigo_qr")
    accion = request.form.get("accion")
    destino = request.form.get("destino", "")
    detalles = request.form.get("detalles", "")
    responsable = request.form.get("responsable", "Operador Móvil")

    ataud = AtaudDAO.buscar_por_codigo(codigo)
    if not ataud:
        return "Ataúd no encontrado", 404

    if accion == "salida_servicio":
        # Validar una salida por día
        from database.daos import AtaudDAO
        if AtaudDAO.ya_salio_hoy(ataud["id"]):
            return "⚠️ Este ataúd ya registró una salida el día de hoy.", 400
            
        ok, msg = AtaudDAO.puede_asignarse(ataud["id"])
        if not ok:
            return f"⚠️ No se puede asignar: {msg}", 400
        HistorialDAO.registrar_salida_servicio(ataud["id"], destino, responsable)
        return "✅ Salida registrada. Ataúd EN USO."

    # ... (código de retorno) ...

    elif accion == "entierro_definitivo":
        # Validar una salida por día
        from database.daos import AtaudDAO
        if AtaudDAO.ya_salio_hoy(ataud["id"]):
            return "⚠️ Este ataúd ya registró una salida el día de hoy.", 400
            
        HistorialDAO.registrar_salida_entierro_definitivo(ataud["id"], destino, detalles)
        return "✅ Registrado. Ataúd DADO DE BAJA (entierro definitivo)."

    return "Acción no válida", 400


def iniciar_servidor_web():
    """Ejecuta el servidor Flask en un hilo separado."""
    import threading
    from config import WEB_HOST, WEB_PORT, WEB_URL_BASE
    
    def run_server():
        from web.server import app
        app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)
    
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    
    # Mensaje informativo con la URL real que debe usarse desde el celular
    print("\n" + "="*70)
    print("🌐  SERVIDOR WEB PARA ESCANEO QR - ACTIVO")
    print("="*70)
    print(f" URL base para móviles: {WEB_URL_BASE}")
    print(f"🔍 Escanea el QR desde tu celular (misma red WiFi)")
    print(f"ℹ️  Si no funciona, verifica que PC y celular estén en la misma red")
    print("="*70 + "\n")