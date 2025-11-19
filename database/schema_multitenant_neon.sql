-- ============================================
-- AX-S Multi-Tenant Schema for PostgreSQL
-- Versión: 2.0.0-multitenant
-- Fecha: 2025-11-19
-- Autor: B10sp4rt4n
-- ============================================

-- Este script crea el schema completo para la versión
-- multi-tenant de AX-S en PostgreSQL (Neon Cloud)

-- ============================================
-- LIMPIEZA (Opcional - solo si necesitas reiniciar)
-- ============================================

-- Descomentar estas líneas solo si quieres borrar todo y empezar de cero
-- DROP TABLE IF EXISTS entidades CASCADE;
-- DROP TABLE IF EXISTS condominios_exo CASCADE;
-- DROP TABLE IF EXISTS msps_exo CASCADE;

-- ============================================
-- TABLAS PRINCIPALES
-- ============================================

-- Tabla: MSPs (Multi-Service Providers)
CREATE TABLE IF NOT EXISTS msps_exo (
    id SERIAL PRIMARY KEY,
    msp_id TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    direccion TEXT,
    ciudad TEXT,
    estado_mx TEXT,
    cp TEXT,
    telefono TEXT,
    email TEXT,
    estado TEXT DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Condominios
CREATE TABLE IF NOT EXISTS condominios_exo (
    id SERIAL PRIMARY KEY,
    condominio_id TEXT UNIQUE NOT NULL,
    msp_id TEXT NOT NULL REFERENCES msps_exo(msp_id) ON DELETE CASCADE,
    nombre TEXT NOT NULL,
    direccion TEXT,
    ciudad TEXT,
    estado_mx TEXT,
    cp TEXT,
    telefono TEXT,
    email TEXT,
    total_unidades INTEGER DEFAULT 0 CHECK (total_unidades >= 0),
    estado TEXT DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Entidades (Residentes, Visitantes, Proveedores, Vehículos)
CREATE TABLE IF NOT EXISTS entidades (
    id SERIAL PRIMARY KEY,
    tipo TEXT CHECK (tipo IN ('residente', 'visitante', 'proveedor', 'vehiculo', 'emergencia')),
    nombre_completo TEXT,
    identificacion TEXT,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    atributos TEXT, -- JSON almacenado como texto para compatibilidad
    hash_actual TEXT,
    hash_previo TEXT,
    msp_id TEXT REFERENCES msps_exo(msp_id) ON DELETE SET NULL,
    condominio_id TEXT REFERENCES condominios_exo(condominio_id) ON DELETE SET NULL,
    estado TEXT DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    -- Columnas legacy (nullable para compatibilidad)
    nombre TEXT,
    creado_en TIMESTAMP
);

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

-- Índices en msps_exo
CREATE INDEX IF NOT EXISTS idx_msps_msp_id ON msps_exo(msp_id);
CREATE INDEX IF NOT EXISTS idx_msps_estado ON msps_exo(estado);
CREATE INDEX IF NOT EXISTS idx_msps_created_at ON msps_exo(created_at DESC);

-- Índices en condominios_exo
CREATE INDEX IF NOT EXISTS idx_condominios_condominio_id ON condominios_exo(condominio_id);
CREATE INDEX IF NOT EXISTS idx_condominios_msp_id ON condominios_exo(msp_id);
CREATE INDEX IF NOT EXISTS idx_condominios_estado ON condominios_exo(estado);
CREATE INDEX IF NOT EXISTS idx_condominios_created_at ON condominios_exo(created_at DESC);

-- Índices en entidades
CREATE INDEX IF NOT EXISTS idx_entidades_tipo ON entidades(tipo);
CREATE INDEX IF NOT EXISTS idx_entidades_identificacion ON entidades(identificacion);
CREATE INDEX IF NOT EXISTS idx_entidades_msp_id ON entidades(msp_id);
CREATE INDEX IF NOT EXISTS idx_entidades_condominio_id ON entidades(condominio_id);
CREATE INDEX IF NOT EXISTS idx_entidades_estado ON entidades(estado);
CREATE INDEX IF NOT EXISTS idx_entidades_fecha_creacion ON entidades(fecha_creacion DESC);

-- Índice compuesto para búsquedas multi-tenant
CREATE INDEX IF NOT EXISTS idx_entidades_msp_condo ON entidades(msp_id, condominio_id);

-- ============================================
-- TRIGGERS PARA AUTO-ACTUALIZACIÓN
-- ============================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para msps_exo
DROP TRIGGER IF EXISTS update_msps_updated_at ON msps_exo;
CREATE TRIGGER update_msps_updated_at
    BEFORE UPDATE ON msps_exo
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para condominios_exo
DROP TRIGGER IF EXISTS update_condominios_updated_at ON condominios_exo;
CREATE TRIGGER update_condominios_updated_at
    BEFORE UPDATE ON condominios_exo
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para entidades (fecha_actualizacion)
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_entidades_fecha ON entidades;
CREATE TRIGGER update_entidades_fecha
    BEFORE UPDATE ON entidades
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- ============================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- ============================================

COMMENT ON TABLE msps_exo IS 'Multi-Service Providers - Empresas de seguridad que gestionan múltiples condominios';
COMMENT ON TABLE condominios_exo IS 'Condominios administrados por MSPs - cada condominio pertenece a un MSP';
COMMENT ON TABLE entidades IS 'Entidades del sistema: residentes, visitantes, proveedores, vehículos';

COMMENT ON COLUMN msps_exo.msp_id IS 'Identificador único del MSP (ej: MSP-001)';
COMMENT ON COLUMN msps_exo.estado IS 'Estado del MSP: activo, inactivo, suspendido';

COMMENT ON COLUMN condominios_exo.condominio_id IS 'Identificador único del condominio (ej: COND-001)';
COMMENT ON COLUMN condominios_exo.msp_id IS 'MSP al que pertenece el condominio';
COMMENT ON COLUMN condominios_exo.total_unidades IS 'Número total de unidades/departamentos';

COMMENT ON COLUMN entidades.tipo IS 'Tipo de entidad: residente, visitante, proveedor, vehiculo, emergencia';
COMMENT ON COLUMN entidades.atributos IS 'JSON con atributos específicos del tipo de entidad';
COMMENT ON COLUMN entidades.hash_actual IS 'Hash SHA-256 de los datos actuales (para detección de cambios)';
COMMENT ON COLUMN entidades.hash_previo IS 'Hash SHA-256 previo (auditoría de cambios)';
COMMENT ON COLUMN entidades.msp_id IS 'MSP al que pertenece la entidad (filtrado multi-tenant)';
COMMENT ON COLUMN entidades.condominio_id IS 'Condominio al que pertenece la entidad (filtrado multi-tenant)';

-- ============================================
-- DATOS DE EJEMPLO (Opcional)
-- ============================================

-- Insertar MSP de ejemplo solo si no existe
INSERT INTO msps_exo (msp_id, nombre, email, telefono, ciudad, estado)
VALUES (
    'MSP-DEMO-001',
    'Demo Security Services',
    'demo@ejemplo.com',
    '+52 55 1234 5678',
    'Ciudad de México',
    'activo'
)
ON CONFLICT (msp_id) DO NOTHING;

-- Insertar Condominio de ejemplo solo si no existe
INSERT INTO condominios_exo (
    condominio_id, 
    msp_id, 
    nombre, 
    direccion,
    ciudad, 
    cp,
    total_unidades, 
    estado
)
VALUES (
    'COND-DEMO-001',
    'MSP-DEMO-001',
    'Residencial Las Palmas Demo',
    'Av. Principal 123, Col. Centro',
    'Ciudad de México',
    '01000',
    50,
    'activo'
)
ON CONFLICT (condominio_id) DO NOTHING;

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Ver tablas creadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Ver índices creados
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Ver datos de ejemplo
SELECT 'MSPs:', COUNT(*) FROM msps_exo
UNION ALL
SELECT 'Condominios:', COUNT(*) FROM condominios_exo
UNION ALL
SELECT 'Entidades:', COUNT(*) FROM entidades;

-- Verificar foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

-- Confirmación
SELECT 'Schema multi-tenant creado exitosamente!' AS status;
