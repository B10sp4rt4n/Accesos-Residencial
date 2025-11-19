"""
Script de inicialización de base de datos para Streamlit Cloud
Crea las tablas msps_exo y condominios_exo si no existen
"""

def init_tables():
    """Inicializar tablas multi-tenant si no existen"""
    from core.db import get_db
    import os
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Detectar si es PostgreSQL o SQLite
        try:
            import streamlit as st
            db_mode = st.secrets.get('DB_MODE', 'sqlite')
        except:
            db_mode = os.getenv('DB_MODE', 'sqlite')
        
        is_postgres = db_mode in ['postgres', 'postgresql']
        
        # Sintaxis compatible
        pk_syntax = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
        
        # Crear tabla msps_exo con nombres de columnas correctos
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS msps_exo (
                id {pk_syntax},
                msp_id TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                razon_social TEXT,
                rfc TEXT,
                email_contacto TEXT,
                telefono_contacto TEXT,
                estado TEXT DEFAULT 'activo',
                plan TEXT DEFAULT 'basico',
                max_condominios INTEGER DEFAULT 10,
                configuracion_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear tabla condominios_exo con nombres de columnas correctos
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS condominios_exo (
                id {pk_syntax},
                condominio_id TEXT UNIQUE NOT NULL,
                msp_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                direccion TEXT,
                ciudad TEXT,
                estado_mx TEXT,
                codigo_postal TEXT,
                telefono TEXT,
                email TEXT,
                total_unidades INTEGER,
                estado TEXT DEFAULT 'activo',
                timezone TEXT DEFAULT 'America/Mexico_City',
                configuracion_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id)
            )
        """)
        
        # Seed idempotente de MSPs esperados (incluso si ya hay algunos)
        msps_seed = [
            ('MSP-001', 'Telmex'),
            ('MSP-TEST-001', 'MSP de Prueba'),
            ('MSP-DEMO-001', 'MSP Demostración'),
            ('MSP-001_Multicable', 'Multicable'),
        ]
        placeholder = '%s' if is_postgres else '?'
        for msp_id, nombre in msps_seed:
            try:
                if is_postgres:
                    cursor.execute(f"""
                        INSERT INTO msps_exo (msp_id, nombre, estado)
                        VALUES ({placeholder}, {placeholder}, 'activo')
                        ON CONFLICT (msp_id) DO UPDATE SET 
                            nombre = EXCLUDED.nombre,
                            estado = 'activo'
                    """, (msp_id, nombre))
                else:
                    cursor.execute(f"""
                        INSERT OR REPLACE INTO msps_exo (msp_id, nombre, estado)
                        VALUES ({placeholder}, {placeholder}, 'activo')
                    """, (msp_id, nombre))
            except Exception as se:
                print(f"⚠️  Seed MSP fallo {msp_id}: {se}")
        
        # Forzar estado activo para seeds si hubiera sido modificado
        try:
            cursor.execute("UPDATE msps_exo SET estado='activo' WHERE msp_id IN ('MSP-001','MSP-TEST-001','MSP-DEMO-001','MSP-001_Multicable') AND estado <> 'activo'")
        except Exception as fe:
            print(f"⚠️  No se pudo forzar estado activo en seeds: {fe}")
        
        # Normalizar estados nulos o vacíos
        try:
            cursor.execute("UPDATE msps_exo SET estado='activo' WHERE estado IS NULL OR estado=''")
        except Exception as ne:
            print(f"⚠️  No se pudo normalizar estados MSP: {ne}")
        
        conn.commit()
        print("✅ Tablas multi-tenant inicializadas correctamente")

if __name__ == '__main__':
    init_tables()
