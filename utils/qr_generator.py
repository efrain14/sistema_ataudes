import qrcode
import os
from config import QR_DIR, WEB_URL_BASE

def generar_qr(ataud_dict, filename=None):
    """
    Genera un PNG con el QR del ataúd.
    El QR contiene SOLO la URL para abrir el formulario web.
    """
    # El QR debe contener ÚNICAMENTE la URL, nada más
    url = f"{WEB_URL_BASE}/movimiento/{ataud_dict['codigo_qr']}"
    
    # Crear QR simple y limpio
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H  # Alta corrección
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Crear imagen con colores de alto contraste
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Nombre del archivo
    fname = filename or f"QR_{ataud_dict['codigo_qr'].replace('/', '_')}.png"
    ruta = os.path.join(QR_DIR, fname)
    
    # Guardar
    img.save(ruta)
    
    print(f"✅ QR generado: {ruta}")
    print(f"🔗 URL codificada: {url}")
    
    return ruta