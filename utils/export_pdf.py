from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database.daos import AtaudDAO, HistorialDAO

def exportar_inventario_pdf(ruta):
    doc = SimpleDocTemplate(ruta, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Inventario de Ataúdes", styles["Title"]), Spacer(1, 12)]
    datos = [["Código QR", "Tipo", "Color", "Estado", "Usos", "Precio"]]
    for a in AtaudDAO.listar():
        datos.append([a["codigo_qr"], a["tipo"], a["color"], a["estado"], a["contador_usos"], f"${a['precio']}"])
    t = Table(datos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elementos.append(t)
    doc.build(elementos)
    return True, ruta

def exportar_historial_pdf(ruta):
    doc = SimpleDocTemplate(ruta, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Historial de Movimientos", styles["Title"]), Spacer(1, 12)]
    datos = [["Código", "Movimiento", "Salida", "Retorno", "Detalles"]]
    for h in HistorialDAO.todos():
        datos.append([h["codigo_qr"], h["tipo_movimiento"], h["fecha_salida"],
                      h["fecha_retorno"] or "-", (h["detalles_restauracion"] or "-")[:30]])
    t = Table(datos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elementos.append(t)
    doc.build(elementos)
    return True, ruta