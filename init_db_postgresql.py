"""
AX-S - Inicialización de Base de Datos PostgreSQL EXO
Script para crear el schema PostgreSQL con arquitectura multi-tenant
"""

import os
import psycopg2
from dotenv import load_dotenv
import toml

# Cargar variables de entorno
load_dotenv()

def get_db_config():
    """Obtener configuración de la base de datos desde variables de entorno o secrets.toml"""
    
    # Intentar cargar desde .streamlit/secrets.toml primero
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            database_url = secrets.get("DATABASE_URL")
            if database_url:
                print("📖 Usando configuración de .streamlit/secrets.toml")
                return {"dsn": database_url}
            
            # Si no hay DATABASE_URL, usar variables separadas
            if all(key in secrets for key in ["PG_HOST", "PG_DATABASE", "PG_USER", "PG_PASSWORD"]):
                print("📖 Usando configuración de .streamlit/secrets.toml")
                return {
                    "host": secrets["PG_HOST"],
                    "port": secrets.get("PG_PORT", "5432"),
                    "database": secrets["PG_DATABASE"],
                    "user": secrets["PG_USER"],
                    "password": secrets["PG_PASSWORD"],
                    "sslmode": secrets.get("PG_SSLMODE", "require"),
                }
        except Exception as e:
            print(f"⚠️  No se pudo leer secrets.toml: {e}")
    
    # Opción 1: DATABASE_URL desde .env
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print("📖 Usando DATABASE_URL de .env")
        return {"dsn": database_url}
    
    # Opción 2: Variables separadas desde .env
    print("📖 Usando variables de entorno")
    return {
        "host": os.getenv("PG_HOST", "localhost"),
        "port": os.getenv("PG_PORT", "5432"),
        "database": os.getenv("PG_DATABASE", "axs_exo"),
        "user": os.getenv("PG_USER", "postgres"),
        "password": os.getenv("PG_PASSWORD", "postgres"),
    }


def init_db_postgresql():
    """Inicializa la base de datos PostgreSQL con schema completo"""
    
    print("🔨 Inicializando base de datos PostgreSQL EXO")
    print("="*60)
    
    # Obtener configuración
    config = get_db_config()
    
    try:
        # Conectar a PostgreSQL
        if "dsn" in config:
            conn = psycopg2.connect(config["dsn"])
            print(f"✅ Conectado vía DATABASE_URL")
        else:
            conn = psycopg2.connect(**config)
            print(f"✅ Conectado a {config['host']}:{config['port']}/{config['database']}")
        
        cursor = conn.cursor()
        
        # Verificar si las tablas ya existen
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%_exo'
        """)
        existing_tables = cursor.fetchall()
        
        if existing_tables:
            print(f"\n⚠️  La base de datos ya tiene {len(existing_tables)} tablas EXO:")
            for table in existing_tables[:5]:
                print(f"   - {table[0]}")
            if len(existing_tables) > 5:
                print(f"   ... y {len(existing_tables) - 5} más")
            
            response = input("\n¿Desea recrear el schema? Esto BORRARÁ todos los datos (s/N): ")
            if response.lower() != 's':
                print("❌ Operación cancelada")
                conn.close()
                return
            
            print("\n🗑️  Eliminando tablas existentes...")
            # Drop todas las tablas _exo
            for table in existing_tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE")
            conn.commit()
            print("✅ Tablas eliminadas")
        
        cursor = conn.cursor()
        
        # Leer el archivo schema_exo.sql
        schema_file = "database/schema_exo.sql"
        
        if not os.path.exists(schema_file):
            print(f"⚠️  Archivo {schema_file} no encontrado")
            print("Creando schema básico...")
            create_basic_schema(cursor)
        else:
            print(f"📄 Ejecutando {schema_file}...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Ejecutar el schema
            cursor.execute(schema_sql)
            print("✅ Schema ejecutado correctamente")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("="*60)
        print("✅ Base de datos PostgreSQL EXO inicializada exitosamente")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        raise


def create_basic_schema(cursor):
    """Crea un schema básico si no existe el archivo SQL"""
    
    # Roles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles_exo (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(50) UNIQUE NOT NULL,
        descripcion TEXT,
        nivel INTEGER NOT NULL,
        permisos_json TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    )
    """)
    
    # MSPs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS msps_exo (
        id SERIAL PRIMARY KEY,
        msp_id VARCHAR(100) UNIQUE NOT NULL,
        nombre VARCHAR(200) NOT NULL,
        razon_social VARCHAR(200),
        rfc VARCHAR(20),
        email_contacto VARCHAR(200),
        telefono_contacto VARCHAR(20),
        estado VARCHAR(20) DEFAULT 'activo',
        plan VARCHAR(50) DEFAULT 'basic',
        max_condominios INTEGER DEFAULT 10,
        configuracion_json TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    )
    """)
    
    # Condominios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condominios_exo (
        id SERIAL PRIMARY KEY,
        condominio_id VARCHAR(100) UNIQUE NOT NULL,
        msp_id VARCHAR(100) NOT NULL,
        nombre VARCHAR(200) NOT NULL,
        direccion TEXT,
        ciudad VARCHAR(100),
        estado_mx VARCHAR(100),
        codigo_postal VARCHAR(10),
        telefono VARCHAR(20),
        email VARCHAR(200),
        total_unidades INTEGER DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'activo',
        timezone VARCHAR(50) DEFAULT 'America/Mexico_City',
        configuracion_json TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id) ON DELETE RESTRICT
    )
    """)
    
    # Datos de ejemplo
    cursor.execute("""
    INSERT INTO roles_exo (nombre, descripcion, nivel) VALUES
        ('super_admin', 'Super Administrador - Dominio Superior (DS)', 1),
        ('msp_admin', 'Administrador MSP - Dominio Delegado (DD)', 2),
        ('condominio_admin', 'Administrador Condominio - Subdominio Específico (SE)', 3),
        ('admin_local', 'Administrador Local - Nodo Operativo (NO)', 4)
    ON CONFLICT (nombre) DO NOTHING
    """)
    
    cursor.execute("""
    INSERT INTO msps_exo (msp_id, nombre, razon_social, email_contacto, plan, max_condominios)
    VALUES ('MSP-DEMO-001', 'Demo MSP', 'Demo MSP S.A. de C.V.', 'demo@msp.com', 'enterprise', 100)
    ON CONFLICT (msp_id) DO NOTHING
    """)
    
    cursor.execute("""
    INSERT INTO condominios_exo (condominio_id, msp_id, nombre, ciudad, total_unidades)
    VALUES ('COND-DEMO-001', 'MSP-DEMO-001', 'Residencial Demo', 'Ciudad de México', 50)
    ON CONFLICT (condominio_id) DO NOTHING
    """)
    
    print("✅ Schema básico creado")


if __name__ == "__main__":
    init_db_postgresql()
