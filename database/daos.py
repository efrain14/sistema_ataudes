from database.connection import get_connection
from config import UMBRAL_USOS_CRITICO
from datetime import datetime
import hashlib


# ============ USUARIOS ============
class UsuarioDAO:
    @staticmethod
    def autenticar(username, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM usuarios WHERE username=? AND password_hash=? AND activo=1",
            (username, pw_hash)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def listar():
        conn = get_connection()
        rows = conn.execute("SELECT id, username, nombre_completo, rol, activo FROM usuarios").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def crear(username, password, nombre_completo, rol="operador"):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES (?,?,?,?)",
                (username, pw_hash, nombre_completo, rol)
            )
            conn.commit()
            return True, "Usuario creado"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()


# ============ ATAUDES ============
class AtaudDAO:
    @staticmethod
    def crear(data: dict):
        conn = get_connection()
        try:
            conn.execute("""
                INSERT INTO ataudes (codigo_qr, codigo_viejo, tipo, color, precio,
                    fecha_compra, factura_compra, proveedor_nombre, proveedor_contacto, estado, contador_usos)
                VALUES (?,?,?,?,?,?,?,?,?,?,0)
            """, (
                data["codigo_qr"], data.get("codigo_viejo"), data["tipo"], data["color"],
                float(data["precio"]), data["fecha_compra"], data["factura_compra"],
                data["proveedor_nombre"], data.get("proveedor_contacto"), "Disponible"
            ))
            conn.commit()
            return True, "Ataúd registrado correctamente"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def listar(filtros=None):
        conn = get_connection()
        query = "SELECT * FROM ataudes WHERE 1=1"
        params = []
        if filtros:
            if filtros.get("codigo_qr"):
                query += " AND codigo_qr LIKE ?"; params.append(f"%{filtros['codigo_qr']}%")
            if filtros.get("codigo_viejo"):
                query += " AND codigo_viejo LIKE ?"; params.append(f"%{filtros['codigo_viejo']}%")
            if filtros.get("tipo"):
                query += " AND tipo LIKE ?"; params.append(f"%{filtros['tipo']}%")
            if filtros.get("color"):
                query += " AND color LIKE ?"; params.append(f"%{filtros['color']}%")
            if filtros.get("estado"):
                query += " AND estado = ?"; params.append(filtros["estado"])
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def buscar_por_codigo(codigo_qr):
        conn = get_connection()
        row = conn.execute("SELECT * FROM ataudes WHERE codigo_qr=?", (codigo_qr,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def actualizar(id_ataud, data: dict):
        conn = get_connection()
        try:
            conn.execute("""
                UPDATE ataudes SET codigo_viejo=?, tipo=?, color=?, precio=?,
                    fecha_compra=?, factura_compra=?, proveedor_nombre=?, proveedor_contacto=?
                WHERE id=?
            """, (
                data.get("codigo_viejo"), data["tipo"], data["color"], float(data["precio"]),
                data["fecha_compra"], data["factura_compra"], data["proveedor_nombre"],
                data.get("proveedor_contacto"), id_ataud
            ))
            conn.commit()
            return True, "Actualizado"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def cambiar_estado(id_ataud, nuevo_estado):
        conn = get_connection()
        conn.execute("UPDATE ataudes SET estado=? WHERE id=?", (nuevo_estado, id_ataud))
        conn.commit()
        conn.close()

    @staticmethod
    def incrementar_usos(id_ataud):
        conn = get_connection()
        conn.execute("UPDATE ataudes SET contador_usos = contador_usos + 1 WHERE id=?", (id_ataud,))
        conn.commit()
        conn.close()

    @staticmethod
    def dar_baja(id_ataud):
        conn = get_connection()
        conn.execute("UPDATE ataudes SET estado='Dado de Baja' WHERE id=?", (id_ataud,))
        conn.commit()
        conn.close()

    @staticmethod
    def puede_asignarse(id_ataud):
        """Verifica si el ataúd puede asignarse a un servicio."""
        ataud = AtaudDAO.buscar_por_id(id_ataud)
        if not ataud:
            return False, "Ataúd no encontrado"
        if ataud["estado"] != "Disponible":
            return False, f"Estado actual: {ataud['estado']}"
        if ataud["contador_usos"] >= UMBRAL_USOS_CRITICO:
            return False, f"Supera umbral crítico ({UMBRAL_USOS_CRITICO} usos). Requiere revisión estructural."
        return True, "OK"

    @staticmethod
    def buscar_por_id(id_ataud):
        conn = get_connection()
        row = conn.execute("SELECT * FROM ataudes WHERE id=?", (id_ataud,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def generar_siguiente_codigo():
        """Genera el siguiente código QR automático: AT-YYYY-NNN"""
        from datetime import datetime
        año = datetime.now().year
        conn = get_connection()
        # Buscar el último código del año actual
        row = conn.execute(
            "SELECT codigo_qr FROM ataudes WHERE codigo_qr LIKE ? ORDER BY id DESC LIMIT 1",
            (f"AT-{año}-%",)
        ).fetchone()
        conn.close()
        
        if row:
            # Extraer el número y incrementar
            ultimo_num = int(row["codigo_qr"].split("-")[-1])
            nuevo_num = ultimo_num + 1
        else:
            nuevo_num = 1
        
        return f"AT-{año}-{nuevo_num:03d}"

    @staticmethod
    def obtener_tipos_unicos():
        """Retorna lista de tipos de ataúd únicos registrados."""
        conn = get_connection()
        rows = conn.execute("SELECT DISTINCT tipo FROM ataudes WHERE tipo IS NOT NULL ORDER BY tipo").fetchall()
        conn.close()
        return [r["tipo"] for r in rows]

    @staticmethod
    def obtener_colores_unicos():
        """Retorna lista de colores únicos registrados."""
        conn = get_connection()
        rows = conn.execute("SELECT DISTINCT color FROM ataudes WHERE color IS NOT NULL ORDER BY color").fetchall()
        conn.close()
        return [r["color"] for r in rows]

    @staticmethod
    def metricas():
        conn = get_connection()
        total = conn.execute("SELECT COUNT(*) FROM ataudes").fetchone()[0]
        disp = conn.execute("SELECT COUNT(*) FROM ataudes WHERE estado='Disponible'").fetchone()[0]
        uso = conn.execute("SELECT COUNT(*) FROM ataudes WHERE estado='En Uso'").fetchone()[0]
        rest = conn.execute("SELECT COUNT(*) FROM ataudes WHERE estado='En Restauración'").fetchone()[0]
        baja = conn.execute("SELECT COUNT(*) FROM ataudes WHERE estado='Dado de Baja'").fetchone()[0]
        criticos = conn.execute(
            f"SELECT COUNT(*) FROM ataudes WHERE contador_usos >= {UMBRAL_USOS_CRITICO} AND estado != 'Dado de Baja'"
        ).fetchone()[0]
        conn.close()
        return {"total": total, "disponibles": disp, "en_uso": uso, "restauracion": rest, "baja": baja, "criticos": criticos}

    @staticmethod
    def ya_salio_hoy(ataud_id):
        """Verifica si el ataúd ya tiene una salida registrada en la fecha actual."""
        from datetime import datetime
        conn = get_connection()
        hoy = datetime.now().strftime("%Y-%m-%d")
        
        # Usamos DATE(fecha_salida, 'localtime') para coincidir con la fecha local del usuario
        row = conn.execute(
            "SELECT COUNT(*) as count FROM historial_usos WHERE ataud_id = ? AND DATE(fecha_salida, 'localtime') = ?",
            (ataud_id, hoy)
        ).fetchone()
        conn.close()
        return row["count"] > 0
    
# ============ HISTORIAL ============
class HistorialDAO:
    @staticmethod
    def registrar_salida_servicio(ataud_id, destino, responsable, observaciones=""):
        conn = get_connection()
        conn.execute("""
            INSERT INTO historial_usos (ataud_id, tipo_movimiento, fecha_salida, destino, observaciones)
            VALUES (?,?,CURRENT_TIMESTAMP,?,?)
        """, (ataud_id, "Salida Servicio", destino, observaciones))
        conn.execute("UPDATE ataudes SET estado='En Uso' WHERE id=?", (ataud_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_retorno_restauracion(ataud_id, detalles, responsable):
        conn = get_connection()
        # Cerrar el registro de salida abierto
        conn.execute("""
            UPDATE historial_usos
            SET fecha_retorno=CURRENT_TIMESTAMP, detalles_restauracion=?, responsable_restauracion=?
            WHERE ataud_id=? AND fecha_retorno IS NULL
            ORDER BY fecha_salida DESC LIMIT 1
        """, (detalles, responsable, ataud_id))
        # Fallback si el UPDATE anterior no funciona por sintaxis SQLite
        ultimo = conn.execute("""
            SELECT id FROM historial_usos WHERE ataud_id=? AND fecha_retorno IS NULL
            ORDER BY fecha_salida DESC LIMIT 1
        """, (ataud_id,)).fetchone()
        if ultimo:
            conn.execute("""
                UPDATE historial_usos SET fecha_retorno=CURRENT_TIMESTAMP,
                detalles_restauracion=?, responsable_restauracion=? WHERE id=?
            """, (detalles, responsable, ultimo["id"]))
        conn.execute("UPDATE ataudes SET estado='En Restauración' WHERE id=?", (ataud_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def confirmar_restauracion(ataud_id):
        conn = get_connection()
        conn.execute("""
            INSERT INTO historial_usos (ataud_id, tipo_movimiento, fecha_salida, fecha_retorno)
            VALUES (?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)
        """, (ataud_id, "Restauracion Completada"))
        conn.execute("UPDATE ataudes SET estado='Disponible', contador_usos = contador_usos + 1 WHERE id=?", (ataud_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_salida_entierro_definitivo(ataud_id, destino, observaciones=""):
        conn = get_connection()
        conn.execute("""
            INSERT INTO historial_usos (ataud_id, tipo_movimiento, fecha_salida, destino, observaciones)
            VALUES (?,?,CURRENT_TIMESTAMP,?,?)
        """, (ataud_id, "Salida Entierro Definitivo", destino, observaciones))
        conn.execute("UPDATE ataudes SET estado='Dado de Baja' WHERE id=?", (ataud_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def historial_de(ataud_id):
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM historial_usos WHERE ataud_id=? ORDER BY fecha_salida DESC",
            (ataud_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def todos():
        conn = get_connection()
        rows = conn.execute("""
            SELECT h.*, a.codigo_qr, a.tipo, a.color
            FROM historial_usos h JOIN ataudes a ON h.ataud_id = a.id
            ORDER BY h.fecha_salida DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]