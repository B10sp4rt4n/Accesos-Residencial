"""
core/db.py
Gestión de base de datos estructural AUP-EXO
Soporta SQLite (desarrollo) y PostgreSQL (producción)
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_PATH = "data/accesos.sqlite"
DB_MODE = os.getenv('DB_MODE', 'sqlite')  # 'sqlite' o 'postgres'

@contextmanager
def get_db():
    """
    Context manager para conexiones de base de datos.
    
    Estrategia:
    1. Si DB_MODE=postgres → usa database/pg_connection.py
    2. Si DB_MODE=sqlite → usa SQLite local
    3. Si está en Streamlit Cloud → detecta DATABASE_URL en secrets
    """
    use_postgres = False
    conn = None
    
    # Opción 1: Streamlit Cloud con secrets individuales (PG_HOST, PG_DATABASE, etc.)
    try:
        import streamlit as st
        print(f"🔍 DEBUG: Streamlit detectado, hasattr secrets: {hasattr(st, 'secrets')}")
        if hasattr(st, 'secrets'):
            print(f"🔍 DEBUG: Secrets disponibles: {list(st.secrets.keys())}")
            db_mode = st.secrets.get('DB_MODE', '')
            if db_mode in ['postgres', 'postgresql']:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                import socket
                
                print(f"🔍 DEBUG: Intentando conectar a PostgreSQL...")
                print(f"   Host: {st.secrets.get('PG_HOST', 'N/A')}")
                print(f"   Database: {st.secrets.get('PG_DATABASE', 'N/A')}")
                
                # Forzar IPv4 (fix para Streamlit Cloud)
                original_getaddrinfo = socket.getaddrinfo
                def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
                    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
                socket.getaddrinfo = getaddrinfo_ipv4_only
                
                try:
                    conn = psycopg2.connect(
                        host=st.secrets['PG_HOST'],
                        database=st.secrets['PG_DATABASE'],
                        user=st.secrets['PG_USER'],
                        password=st.secrets['PG_PASSWORD'],
                        port=int(st.secrets.get('PG_PORT', 5432))
                    )
                    use_postgres = True
                    print("✅ Conectado a PostgreSQL via Streamlit secrets")
                finally:
                    socket.getaddrinfo = original_getaddrinfo
    except Exception as e:
        print(f"⚠️  Error en Opción 1: {e}")
        pass
    
    # Opción 2: Streamlit Cloud con DATABASE_URL
    if not conn:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                import socket
                
                print(f"🔍 DEBUG: Conectando via DATABASE_URL")
                
                # Forzar IPv4
                original_getaddrinfo = socket.getaddrinfo
                def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
                    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
                socket.getaddrinfo = getaddrinfo_ipv4_only
                
                try:
                    conn = psycopg2.connect(st.secrets['DATABASE_URL'])
                    use_postgres = True
                    print("✅ Conectado a PostgreSQL via DATABASE_URL")
                finally:
                    socket.getaddrinfo = original_getaddrinfo
        except Exception as e:
            print(f"⚠️  Error en Opción 2: {e}")
            pass
    
    # Opción 3: Variable de entorno DB_MODE (desarrollo local)
    if not conn and DB_MODE == 'postgres':
        try:
            from database.pg_connection import get_pg
            conn = get_pg()
            use_postgres = True
            print("✅ Conectado a PostgreSQL via .env local")
        except Exception as e:
            print(f"⚠️  Error conectando PostgreSQL: {e}")
            print("📌 Fallback a SQLite...")
    
    # Opción 4: Fallback a SQLite (desarrollo)
    if not conn:
        conn = sqlite3.connect(DB_PATH if Path(DB_PATH).exists() else "axs_v2.db")
        conn.row_factory = sqlite3.Row
        print("📌 Usando SQLite (desarrollo local)")
    
    try:
        # Wrapper para compatibilidad de queries
        if use_postgres:
            # Crear cursor con dict factory
            from psycopg2.extras import RealDictCursor
            
            # Wrapper del método cursor() para que siempre use RealDictCursor
            original_cursor_method = conn.cursor
            def cursor_with_dict():
                cur = original_cursor_method(cursor_factory=RealDictCursor)
                # Agregar wrapper al execute del cursor para convertir ? a %s
                original_cur_execute = cur.execute
                def execute_compat(query, params=None):
                    query = query.replace('?', '%s')
                    if params:
                        return original_cur_execute(query, params)
                    return original_cur_execute(query)
                cur.execute = execute_compat
                return cur
            
            # Crear wrapper de conexión para compatibilidad
            class PostgresConnectionWrapper:
                def __init__(self, pg_conn):
                    self._conn = pg_conn
                
                def cursor(self):
                    return cursor_with_dict()
                
                def execute(self, query, params=None):
                    cur = self.cursor()
                    query = query.replace('?', '%s')
                    if params:
                        cur.execute(query, params)
                    else:
                        cur.execute(query)
                    return cur
                
                def commit(self):
                    return self._conn.commit()
                
                def rollback(self):
                    return self._conn.rollback()
                
                def close(self):
                    return self._conn.close()
            
            conn = PostgresConnectionWrapper(conn)
        
        yield conn
        
        # IMPORTANTE: Commit para ambos tipos de BD
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
