"""
Script de migración de SQLite a PostgreSQL (Neon)
Migra toda la estructura y datos de axs_v2.db a PostgreSQL
"""
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse

def get_postgres_conn():
    """Obtiene conexión a PostgreSQL desde secrets."""
    # Leer desde archivo secrets
    import tomli
    with open('.streamlit/secrets.toml', 'rb') as f:
        secrets = tomli.load(f)
    
    db_url = secrets['DATABASE_URL']
    
    # Parsear URL
    result = urlparse(db_url)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

def migrate_sqlite_to_postgres():
    """Migra toda la BD de SQLite a PostgreSQL."""
    print("🔄 Iniciando migración SQLite → PostgreSQL...")
    
    # Conectar a ambas BDs
    sqlite_conn = sqlite3.connect('axs_v2.db')
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = get_postgres_conn()
    pg_cur = pg_conn.cursor()
    
    # Obtener todas las tablas
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in sqlite_cur.fetchall()]
    
    print(f"📊 Tablas encontradas: {len(tables)}")
    
    for table in tables:
        print(f"\n📦 Migrando tabla: {table}")
        
        # Obtener estructura de tabla
        sqlite_cur.execute(f"PRAGMA table_info({table})")
        columns = sqlite_cur.fetchall()
        
        # Crear tabla en PostgreSQL (adaptando tipos)
        col_defs = []
        for col in columns:
            name = col[1]
            sqlite_type = col[2].upper()
            
            # Mapear tipos SQLite → PostgreSQL
            pg_type = {
                'INTEGER': 'INTEGER',
                'TEXT': 'TEXT',
                'REAL': 'REAL',
                'BLOB': 'BYTEA',
                'NUMERIC': 'NUMERIC',
                'BOOLEAN': 'BOOLEAN',
                'DATETIME': 'TIMESTAMP',
                'DATE': 'DATE',
                'TIME': 'TIME'
            }.get(sqlite_type, 'TEXT')
            
            nullable = "NOT NULL" if col[3] else ""
            primary_key = "PRIMARY KEY" if col[5] else ""
            
            col_defs.append(f'"{name}" {pg_type} {nullable} {primary_key}')
        
        # Crear tabla
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)})'
        try:
            pg_cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            pg_cur.execute(create_sql)
            print(f"  ✅ Tabla creada")
        except Exception as e:
            print(f"  ⚠️ Error creando tabla: {e}")
            continue
        
        # Migrar datos
        sqlite_cur.execute(f'SELECT * FROM {table}')
        rows = sqlite_cur.fetchall()
        
        if rows:
            col_names = [col[1] for col in columns]
            placeholders = ','.join(['%s'] * len(col_names))
            col_names_quoted = ','.join([f'"{c}"' for c in col_names])
            insert_sql = f'INSERT INTO "{table}" ({col_names_quoted}) VALUES ({placeholders})'
            
            for row in rows:
                try:
                    pg_cur.execute(insert_sql, tuple(row))
                except Exception as e:
                    print(f"  ⚠️ Error insertando fila: {e}")
            
            print(f"  ✅ {len(rows)} registros migrados")
        else:
            print(f"  ℹ️ Tabla vacía")
    
    # Commit y cerrar
    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n✅ Migración completada exitosamente!")

if __name__ == "__main__":
    # Instalar tomli si no existe
    try:
        import tomli
    except ImportError:
        print("📦 Instalando tomli...")
        os.system("pip install tomli")
        import tomli
    
    migrate_sqlite_to_postgres()
