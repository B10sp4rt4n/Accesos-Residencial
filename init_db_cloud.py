"""
Script de inicialización de base de datos para Streamlit Cloud
Crea las tablas msps_exo y condominios_exo si no existen
"""

def init_tables():
    """Inicializar tablas multi-tenant si no existen"""
    from core.db import get_db
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Crear tabla msps_exo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS msps_exo (
                msp_id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                configuracion TEXT,
                estado TEXT DEFAULT 'activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                hash_actual TEXT,
                hash_previo TEXT
            )
        """)
        
        # Crear tabla condominios_exo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS condominios_exo (
                condominio_id TEXT PRIMARY KEY,
                msp_id TEXT NOT NULL,
                nombre TEXT NOT NULL,
                direccion TEXT,
                configuracion TEXT,
                estado TEXT DEFAULT 'activo',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                hash_actual TEXT,
                hash_previo TEXT,
                FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id)
            )
        """)
        
        # Insertar MSPs de ejemplo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM msps_exo")
        count = cursor.fetchone()[0]
        
        if count == 0:
            msps = [
                ('MSP-001', 'Telmex', 'MSP Principal', 'activo'),
                ('MSP-TEST-001', 'MSP de Prueba', 'MSP para testing', 'activo'),
                ('MSP-DEMO-001', 'MSP Demostración', 'MSP de demostración', 'activo'),
            ]
            
            for msp_id, nombre, descripcion, estado in msps:
                cursor.execute("""
                    INSERT INTO msps_exo (msp_id, nombre, descripcion, estado)
                    VALUES (?, ?, ?, ?)
                """, (msp_id, nombre, descripcion, estado))
        
        conn.commit()
        print("✅ Tablas multi-tenant inicializadas correctamente")

if __name__ == '__main__':
    init_tables()
