"""
core/db.py
Gestión de base de datos estructural AUP-EXO
"""

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime

DB_PATH = "data/accesos.sqlite"

@contextmanager
def get_db():
    """Context manager para conexiones de base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Inicializa la base de datos con el esquema AUP-EXO"""
    
    # Asegurar que existe el directorio
    Path("data").mkdir(exist_ok=True)
    
    with get_db() as db:
        # Tabla de entidades (universal)
        db.execute("""
            CREATE TABLE IF NOT EXISTS entidades (
                entidad_id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                atributos TEXT NOT NULL,
                hash_prev TEXT,
                hash_actual TEXT NOT NULL,
                estado TEXT DEFAULT 'activo',
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL,
                created_by TEXT,
                updated_by TEXT
            )
        """)
        
        # Tabla de eventos (trazabilidad completa)
        db.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                evento_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entidad_id TEXT,
                tipo_evento TEXT NOT NULL,
                metadata TEXT,
                evidencia_id TEXT,
                hash_actual TEXT NOT NULL,
                timestamp_servidor TEXT NOT NULL,
                timestamp_cliente TEXT,
                actor TEXT NOT NULL,
                dispositivo TEXT,
                origen TEXT,
                contexto TEXT,
                recibo_recordia TEXT,
                FOREIGN KEY (entidad_id) REFERENCES entidades(entidad_id)
            )
        """)
        
        # Tabla de políticas (motor de reglas)
        db.execute("""
            CREATE TABLE IF NOT EXISTS politicas (
                politica_id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                tipo TEXT NOT NULL,
                condiciones TEXT NOT NULL,
                prioridad INTEGER DEFAULT 5,
                estado TEXT DEFAULT 'activa',
                aplicable_a TEXT,
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL,
                created_by TEXT
            )
        """)
        
        # Tabla de usuarios (roles y permisos)
        db.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario_id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                rol TEXT NOT NULL,
                permisos TEXT,
                estado TEXT DEFAULT 'activo',
                ultimo_acceso TEXT,
                fecha_creacion TEXT NOT NULL
            )
        """)
        
        # Tabla de roles
        db.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                rol_id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                permisos TEXT NOT NULL,
                nivel_acceso INTEGER DEFAULT 1,
                fecha_creacion TEXT NOT NULL
            )
        """)
        
        # Tabla de bitácora (auditoría completa)
        db.execute("""
            CREATE TABLE IF NOT EXISTS bitacora (
                bitacora_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabla TEXT NOT NULL,
                operacion TEXT NOT NULL,
                registro_id TEXT NOT NULL,
                datos_anteriores TEXT,
                datos_nuevos TEXT,
                usuario_id TEXT,
                timestamp TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
        """)
        
        # Tabla de log de reglas (debugging y análisis)
        db.execute("""
            CREATE TABLE IF NOT EXISTS log_reglas (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_id INTEGER,
                politica_id TEXT,
                resultado TEXT NOT NULL,
                motivo TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (evento_id) REFERENCES eventos(evento_id),
                FOREIGN KEY (politica_id) REFERENCES politicas(politica_id)
            )
        """)
        
        # Índices para performance
        db.execute("CREATE INDEX IF NOT EXISTS idx_entidades_tipo ON entidades(tipo)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_eventos_timestamp ON eventos(timestamp_servidor)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_eventos_entidad ON eventos(entidad_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON eventos(tipo_evento)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_politicas_estado ON politicas(estado)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol)")
        
        print("✅ Base de datos AUP-EXO inicializada correctamente")


def insertar_datos_ejemplo():
    """Inserta datos de ejemplo para pruebas"""
    with get_db() as db:
        # Roles por defecto
        roles_default = [
            ("admin", "Administrador", "Acceso total al sistema", json.dumps([
                "crear_entidades", "editar_entidades", "eliminar_entidades",
                "crear_politicas", "editar_politicas", "ver_reportes",
                "gestionar_usuarios", "ver_bitacora"
            ]), 10),
            ("coordinador", "Coordinador", "Gestión de accesos y reportes", json.dumps([
                "crear_entidades", "editar_entidades", "crear_politicas",
                "ver_reportes", "ver_bitacora"
            ]), 7),
            ("vigilante", "Vigilante", "Registro de accesos", json.dumps([
                "registrar_acceso", "consultar_entidades", "ver_eventos"
            ]), 3),
            ("residente", "Residente", "Consulta básica", json.dumps([
                "ver_mis_accesos", "autorizar_visitas"
            ]), 1)
        ]
        
        for rol_id, nombre, desc, permisos, nivel in roles_default:
            db.execute("""
                INSERT OR IGNORE INTO roles 
                (rol_id, nombre, descripcion, permisos, nivel_acceso, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rol_id, nombre, desc, permisos, nivel, datetime.now().isoformat()))
        
        print("✅ Datos de ejemplo insertados")


if __name__ == "__main__":
    init_db()
    insertar_datos_ejemplo()
