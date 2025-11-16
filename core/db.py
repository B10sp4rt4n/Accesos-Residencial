"""
core/db.py
Gestión de base de datos estructural AUP-EXO
Soporta SQLite (desarrollo) y PostgreSQL (producción)
"""

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime

DB_PATH = "data/accesos.sqlite"

@contextmanager
def get_db():
    """
    Context manager para conexiones de base de datos.
    Usa PostgreSQL si DATABASE_URL está en secrets (Streamlit Cloud),
    sino usa SQLite local.
    """
    use_postgres = False
    conn = None
    
    try:
        # Intentar PostgreSQL primero (producción)
        import streamlit as st
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(st.secrets['DATABASE_URL'])
            use_postgres = True
    except:
        pass
    
    if not conn:
        # Fallback a SQLite (desarrollo)
        conn = sqlite3.connect(DB_PATH if Path(DB_PATH).exists() else "axs_v2.db")
        conn.row_factory = sqlite3.Row
    
    try:
        # Wrapper para compatibilidad de queries
        if use_postgres:
            # Crear cursor con dict factory
            original_cursor = conn.cursor
            def cursor_with_dict():
                return original_cursor(cursor_factory=RealDictCursor)
            conn.cursor = cursor_with_dict
            
            # Wrapper para execute que convierte ? a %s
            cur = conn.cursor()
            original_execute = cur.execute
            def execute_compat(query, params=None):
                query = query.replace('?', '%s')
                if params:
                    return original_execute(query, params)
                return original_execute(query)
            cur.execute = execute_compat
            yield conn
        else:
            yield conn
            conn.commit()
    except Exception as e:
        if hasattr(conn, 'rollback'):
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def init_db():
    """Inicializa la base de datos con el esquema AUP-EXO"""
    
    # Asegurar que existe el directorio
    Path("data").mkdir(exist_ok=True)
    
    with get_db() as db:
        # Tabla de entidades (universal: personas, vehículos, etc.)
        # DISEÑO AUP-EXO: Nodo universal parametrizable
        # - No usamos tablas separadas con estructura distinta
        # - Todo es "una entidad parametrizable" con atributos JSON
        # - hash_actual y evolución permiten reconstruir historial completo
        # - Permite agregar nuevos tipos sin cambiar schema
        db.execute("""
            CREATE TABLE IF NOT EXISTS entidades (
                entidad_id TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                atributos JSON NOT NULL,
                hash_actual TEXT NOT NULL,
                hash_previo TEXT,
                estado TEXT DEFAULT 'activo',
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL,
                created_by TEXT
            )
        """)
        
        # Tabla de eventos (con encadenamiento hash)
        # DISEÑO AUP-EXO: Bitácora reconstruible con hash encadenado
        # - Permite recuperar cada acceso incluso si la base se corrompe
        # - hash_actual enlaza con hash_previo del siguiente evento (blockchain-style)
        # - recibo_recordia: enlace a sistema externo de trazabilidad jurídica
        db.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                evento_id TEXT PRIMARY KEY,
                entidad_id TEXT,
                tipo_evento TEXT NOT NULL,
                metadata TEXT,
                evidencia_id TEXT,
                hash_actual TEXT NOT NULL,
                timestamp_servidor TEXT NOT NULL,
                timestamp_cliente TEXT,
                actor TEXT,
                dispositivo TEXT,
                origen TEXT,
                contexto TEXT,
                recibo_recordia TEXT,
                FOREIGN KEY(entidad_id) REFERENCES entidades(entidad_id)
            )
        """)
        
        # Tabla de políticas (motor de reglas)
        # DISEÑO AUP-EXO: Políticas parametrizadas
        # - Pueden crecer sin cambiar código
        # - Condiciones en JSON permiten infinitas combinaciones
        # - Evaluación dinámica sin recompilación
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
