"""
database/migrate_sqlite_to_pg.py
================================
Migra datos desde SQLite (axs.db / axs_v2.db) a PostgreSQL.
Ejecutar solo cuando se tenga PostgreSQL configurado.
"""

import sqlite3
import os
from database.pg_connection import get_pg_cursor, init_pg_schema
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    """
    Migra datos de SQLite a PostgreSQL.
    
    Estrategia:
    1. Inicializa schema PostgreSQL
    2. Lee todas las tablas de SQLite
    3. Inserta en PostgreSQL con ON CONFLICT DO NOTHING
    """
    
    # Rutas SQLite posibles
    sqlite_paths = ['axs_v2.db', 'data/accesos.sqlite', 'axs.db']
    sqlite_conn = None
    
    for path in sqlite_paths:
        if os.path.exists(path):
            print(f"📂 Encontrado: {path}")
            sqlite_conn = sqlite3.connect(path)
            sqlite_conn.row_factory = sqlite3.Row
            break
    
    if not sqlite_conn:
        print("❌ No se encontró ninguna base SQLite para migrar")
        return False
    
    print("🔄 Iniciando migración SQLite → PostgreSQL...")
    
    # 1. Inicializar schema PostgreSQL
    try:
        init_pg_schema()
    except Exception as e:
        print(f"⚠️  Schema ya existe o error: {e}")
    
    # 2. Migrar tablas
    tables_to_migrate = [
        'entidades',
        'eventos',
        'politicas',
        'usuarios',
        'roles',
        'bitacora'
    ]
    
    total_rows = 0
    
    for table in tables_to_migrate:
        try:
            # Leer de SQLite
            cursor_sqlite = sqlite_conn.cursor()
            cursor_sqlite.execute(f"SELECT * FROM {table}")
            rows = cursor_sqlite.fetchall()
            
            if not rows:
                print(f"  ⏭️  {table}: Sin datos")
                continue
            
            # Obtener nombres de columnas
            columns = [description[0] for description in cursor_sqlite.description]
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            # Insertar en PostgreSQL
            with get_pg_cursor(dict_cursor=False) as cur_pg:
                insert_query = f"""
                    INSERT INTO {table} ({columns_str})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """
                
                for row in rows:
                    try:
                        cur_pg.execute(insert_query, tuple(row))
                    except Exception as e:
                        print(f"    ⚠️  Error en fila: {e}")
                
                total_rows += len(rows)
                print(f"  ✅ {table}: {len(rows)} registros migrados")
        
        except Exception as e:
            print(f"  ❌ Error en {table}: {e}")
    
    sqlite_conn.close()
    print(f"\n🎉 Migración completada: {total_rows} registros totales")
    return True

if __name__ == '__main__':
    # Verificar que DB_MODE sea postgres
    if os.getenv('DB_MODE') != 'postgres':
        print("❌ DB_MODE debe ser 'postgres' para migrar")
        print("   Configura en .env: DB_MODE=postgres")
        exit(1)
    
    # Verificar credenciales PostgreSQL
    if not os.getenv('PG_HOST'):
        print("❌ Falta configuración PostgreSQL en .env")
        print("   Configura: PG_HOST, PG_DATABASE, PG_USER, PG_PASSWORD")
        exit(1)
    
    migrate_data()
