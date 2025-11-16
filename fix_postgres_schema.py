"""
Script para recrear TODAS las tablas de PostgreSQL con el esquema correcto
que coincida con el código actual de AX-S
"""
import psycopg2
import tomli

with open('.streamlit/secrets.toml', 'rb') as f:
    secrets = tomli.load(f)

conn = psycopg2.connect(secrets['DATABASE_URL'])
cur = conn.cursor()

print('🔧 RECREANDO ESQUEMA COMPLETO EN POSTGRESQL...\n')

# Drop todas las tablas viejas
tables_to_drop = ['politicas', 'roles', 'log_reglas', 'bitacora']
for table in tables_to_drop:
    try:
        cur.execute(f'DROP TABLE IF EXISTS {table} CASCADE')
        print(f'✅ Tabla {table} eliminada')
    except Exception as e:
        print(f'⚠️  Error eliminando {table}: {e}')

# Crear tablas con esquema correcto (igual que SQLite en core/db.py)

# TABLA POLITICAS
cur.execute("""
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
print('✅ Tabla politicas creada')

# TABLA ROLES
cur.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        rol_id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        permisos TEXT NOT NULL,
        nivel_acceso INTEGER DEFAULT 1,
        fecha_creacion TEXT NOT NULL
    )
""")
print('✅ Tabla roles creada')

# TABLA LOG_REGLAS
cur.execute("""
    CREATE TABLE IF NOT EXISTS log_reglas (
        log_id SERIAL PRIMARY KEY,
        evento_id INTEGER,
        politica_id TEXT,
        resultado TEXT NOT NULL,
        motivo TEXT,
        timestamp TEXT NOT NULL
    )
""")
print('✅ Tabla log_reglas creada')

# TABLA BITACORA (si no existe)
cur.execute("""
    CREATE TABLE IF NOT EXISTS bitacora (
        bitacora_id SERIAL PRIMARY KEY,
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
print('✅ Tabla bitacora creada')

# Crear índices para performance
cur.execute("CREATE INDEX IF NOT EXISTS idx_politicas_estado ON politicas(estado)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_politicas_tipo ON politicas(tipo)")
print('✅ Índices creados')

conn.commit()
conn.close()

print('\n✅ ESQUEMA POSTGRESQL COMPLETADO')
print('   Ahora todas las tablas coinciden con el código SQLite')
