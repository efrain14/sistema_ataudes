from database.connection import get_connection
import hashlib

def inicializar_bd():
    """Crea todas las tablas y el usuario admin por defecto."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'operador')),
        activo INTEGER DEFAULT 1,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ataudes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_qr TEXT UNIQUE NOT NULL,
        codigo_viejo TEXT,
        tipo TEXT NOT NULL,
        color TEXT NOT NULL,
        precio REAL NOT NULL CHECK(precio > 0),
        fecha_compra DATE NOT NULL,
        factura_compra TEXT NOT NULL,
        proveedor_nombre TEXT NOT NULL,
        proveedor_contacto TEXT,
        estado TEXT NOT NULL CHECK(estado IN ('Disponible','En Uso','En Restauración','Dado de Baja')) DEFAULT 'Disponible',
        contador_usos INTEGER DEFAULT 0,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS historial_usos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ataud_id INTEGER NOT NULL,
        tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('Salida Servicio','Retorno Restauracion','Salida Entierro Definitivo','Restauracion Completada')),
        fecha_salida TIMESTAMP NOT NULL,
        fecha_retorno TIMESTAMP,
        detalles_restauracion TEXT,
        responsable_restauracion TEXT,
        destino TEXT,
        observaciones TEXT,
        FOREIGN KEY (ataud_id) REFERENCES ataudes(id) ON DELETE CASCADE
    )
    """)

    # Usuario admin por defecto (admin / admin123)
    c.execute("SELECT COUNT(*) FROM usuarios WHERE username='admin'")
    if c.fetchone()[0] == 0:
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        """, ("admin", pw_hash, "Administrador", "admin"))

    conn.commit()
    conn.close()