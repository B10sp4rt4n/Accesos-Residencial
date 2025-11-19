"""
AX-S - Inicialización de Base de Datos EXO
Script para crear el schema SQLite con arquitectura multi-tenant
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "data/axs_exo.db"

def init_db_exo():
    """Inicializa la base de datos EXO con schema completo"""
    
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Eliminar DB existente para empezar limpio
    if os.path.exists(DB_PATH):
        print(f"⚠️  Eliminando base de datos existente: {DB_PATH}")
        os.remove(DB_PATH)
    
    print(f"🔨 Creando nueva base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ========================================
    # 1. ROLES Y JERARQUÍAS
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT,
        nivel INTEGER NOT NULL,
        permisos_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_roles_exo_nivel ON roles_exo(nivel)")
    
    # Insertar roles iniciales
    roles = [
        ('super_admin', 'Super Administrador - Dominio Superior (DS)', 1),
        ('msp_admin', 'Administrador MSP - Dominio Delegado (DD)', 2),
        ('condominio_admin', 'Administrador Condominio - Subdominio Específico (SE)', 3),
        ('admin_local', 'Administrador Local - Nodo Operativo (NO)', 4)
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO roles_exo (nombre, descripcion, nivel) VALUES (?, ?, ?)",
        roles
    )
    
    print("✅ Tabla roles_exo creada")
    
    # ========================================
    # 2. MSPs (Managed Service Providers)
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS msps_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msp_id TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        razon_social TEXT,
        rfc TEXT,
        email_contacto TEXT,
        telefono_contacto TEXT,
        estado TEXT DEFAULT 'activo',
        plan TEXT DEFAULT 'basic',
        max_condominios INTEGER DEFAULT 10,
        configuracion_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_msps_exo_estado ON msps_exo(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_msps_exo_msp_id ON msps_exo(msp_id)")
    
    print("✅ Tabla msps_exo creada")
    
    # ========================================
    # 3. CONDOMINIOS
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condominios_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        condominio_id TEXT UNIQUE NOT NULL,
        msp_id TEXT NOT NULL,
        nombre TEXT NOT NULL,
        direccion TEXT,
        ciudad TEXT,
        estado_mx TEXT,
        codigo_postal TEXT,
        telefono TEXT,
        email TEXT,
        total_unidades INTEGER DEFAULT 0,
        estado TEXT DEFAULT 'activo',
        timezone TEXT DEFAULT 'America/Mexico_City',
        configuracion_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id) ON DELETE RESTRICT
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_condominios_exo_msp ON condominios_exo(msp_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_condominios_exo_estado ON condominios_exo(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_condominios_exo_condominio_id ON condominios_exo(condominio_id)")
    
    print("✅ Tabla condominios_exo creada")
    
    # ========================================
    # 4. USUARIOS MULTINIVEL
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL,
        scope_type TEXT,
        scope_id TEXT,
        msp_id TEXT,
        condominio_id TEXT,
        estado TEXT DEFAULT 'activo',
        ultimo_acceso TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rol) REFERENCES roles_exo(nombre),
        FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id),
        FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id)
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_exo_email ON usuarios_exo(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_exo_rol ON usuarios_exo(rol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_exo_msp ON usuarios_exo(msp_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_exo_condominio ON usuarios_exo(condominio_id)")
    
    print("✅ Tabla usuarios_exo creada")
    
    # ========================================
    # 5. RESIDENCIAS
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS residencias_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        residencia_id TEXT UNIQUE NOT NULL,
        condominio_id TEXT NOT NULL,
        numero_casa TEXT NOT NULL,
        calle TEXT,
        lote TEXT,
        manzana TEXT,
        tipo TEXT DEFAULT 'casa',
        estado TEXT DEFAULT 'ocupada',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_residencias_exo_condominio ON residencias_exo(condominio_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_residencias_exo_numero ON residencias_exo(numero_casa, condominio_id)")
    
    print("✅ Tabla residencias_exo creada")
    
    # ========================================
    # 6. RESIDENTES
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS residentes_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        residente_id TEXT UNIQUE NOT NULL,
        residencia_id TEXT NOT NULL,
        nombre_completo TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        tipo TEXT DEFAULT 'propietario',
        estado TEXT DEFAULT 'activo',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (residencia_id) REFERENCES residencias_exo(residencia_id) ON DELETE RESTRICT
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_residentes_exo_residencia ON residentes_exo(residencia_id)")
    
    print("✅ Tabla residentes_exo creada")
    
    # ========================================
    # 7. VISITANTES
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitantes_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visitante_id TEXT UNIQUE NOT NULL,
        residencia_id TEXT NOT NULL,
        nombre TEXT NOT NULL,
        telefono TEXT,
        tipo TEXT DEFAULT 'visitante',
        qr_code TEXT UNIQUE,
        fecha_entrada_esperada TEXT,
        fecha_salida_esperada TEXT,
        estado TEXT DEFAULT 'pendiente',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (residencia_id) REFERENCES residencias_exo(residencia_id) ON DELETE RESTRICT
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visitantes_exo_residencia ON visitantes_exo(residencia_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_visitantes_exo_qr ON visitantes_exo(qr_code)")
    
    print("✅ Tabla visitantes_exo creada")
    
    # ========================================
    # 8. ACCESOS (Log de entradas/salidas)
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accesos_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acceso_id TEXT UNIQUE NOT NULL,
        condominio_id TEXT NOT NULL,
        tipo_entidad TEXT NOT NULL,
        entidad_id TEXT NOT NULL,
        tipo_acceso TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        vigilante_nombre TEXT,
        notas TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_accesos_exo_condominio ON accesos_exo(condominio_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_accesos_exo_timestamp ON accesos_exo(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_accesos_exo_tipo_entidad ON accesos_exo(tipo_entidad, entidad_id)")
    
    print("✅ Tabla accesos_exo creada")
    
    # ========================================
    # 9. REGLAS (Políticas por condominio)
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reglas_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regla_id TEXT UNIQUE NOT NULL,
        condominio_id TEXT NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        tipo TEXT NOT NULL,
        configuracion_json TEXT,
        activa INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reglas_exo_condominio ON reglas_exo(condominio_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reglas_exo_tipo ON reglas_exo(tipo)")
    
    print("✅ Tabla reglas_exo creada")
    
    # ========================================
    # 10. LEDGER (Auditoría universal)
    # ========================================
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ledger_exo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ledger_id TEXT UNIQUE NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        usuario_id TEXT,
        accion TEXT NOT NULL,
        entidad_tipo TEXT,
        entidad_id TEXT,
        scope_type TEXT,
        scope_id TEXT,
        datos_anteriores TEXT,
        datos_nuevos TEXT,
        ip_address TEXT,
        user_agent TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios_exo(usuario_id)
    )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_exo_timestamp ON ledger_exo(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_exo_usuario ON ledger_exo(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_exo_scope ON ledger_exo(scope_type, scope_id)")
    
    print("✅ Tabla ledger_exo creada")
    
    # ========================================
    # Crear datos de ejemplo
    # ========================================
    
    # MSP de ejemplo
    cursor.execute("""
    INSERT OR IGNORE INTO msps_exo (msp_id, nombre, razon_social, email_contacto, plan, max_condominios)
    VALUES ('MSP-DEMO-001', 'Demo MSP', 'Demo MSP S.A. de C.V.', 'demo@msp.com', 'enterprise', 100)
    """)
    
    # Condominio de ejemplo
    cursor.execute("""
    INSERT OR IGNORE INTO condominios_exo (condominio_id, msp_id, nombre, ciudad, total_unidades)
    VALUES ('COND-DEMO-001', 'MSP-DEMO-001', 'Residencial Demo', 'Ciudad de México', 50)
    """)
    
    print("✅ Datos de ejemplo insertados")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ Base de datos EXO inicializada exitosamente")
    print(f"📁 Ubicación: {DB_PATH}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    init_db_exo()
