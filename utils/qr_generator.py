import qrcode
import json
import os
from config import QR_DIR

def generar_qr(ataud_dict, filename=None):
    """Genera un PNG con el QR del ataúd. Retorna la ruta del archivo."""
    payload = {
        "codigo": ataud_dict["codigo_qr"],
        "tipo": ataud_dict["tipo"],
        "color": ataud_dict["color"],
        "usos": ataud_dict.get("contador_usos", 0),
        "estado": ataud_dict.get("estado", "Disponible"),
        "proveedor": ataud_dict.get("proveedor_nombre", ""),
        # URL para escaneo móvil (Opción A)
        "url": f"http://localhost:5000/movimiento/{ataud_dict['codigo_qr']}"
    }
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(payload, ensure_ascii=False))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    fname = filename or f"QR_{ataud_dict['codigo_qr'].replace('/', '_')}.png"
    ruta = os.path.join(QR_DIR, fname)
    img.save(ruta)
    return ruta