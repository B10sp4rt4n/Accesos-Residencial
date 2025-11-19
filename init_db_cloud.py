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
        
        # Insertar MSPs de ejemplo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM msps_exo")
        count = cursor.fetchone()[0]
        
        if count == 0:
            msps = [
                ('MSP-001', 'Telmex'),
                ('MSP-TEST-001', 'MSP de Prueba'),
                ('MSP-DEMO-001', 'MSP Demostración'),
            ]
            
            placeholder = '%s' if is_postgres else '?'
            for msp_id, nombre in msps:
                cursor.execute(f"""
                    INSERT INTO msps_exo (msp_id, nombre, estado)
                    VALUES ({placeholder}, {placeholder}, 'activo')
                """, (msp_id, nombre))
        
        conn.commit()
        print("✅ Tablas multi-tenant inicializadas correctamente")

if __name__ == '__main__':
    init_tables()
