-- ========================================
-- AX-S PostgreSQL Schema
-- Tipos nativos PostgreSQL optimizados
-- Multi-Tenant Hierarchy: Super Admin > MSP > Condominio > Admin Local
-- ========================================

-- Tabla: super_admins (nivel superior del sistema)
CREATE TABLE IF NOT EXISTS super_admins (
    super_admin_id VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'activo',
    permisos_especiales TEXT,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    ultimo_acceso TIMESTAMPTZ,
    created_by VARCHAR(100)
);

CREATE INDEX idx_super_admins_estado ON super_admins(estado);
CREATE INDEX idx_super_admins_email ON super_admins(email);

COMMENT ON TABLE super_admins IS 'Super administradores con acceso total al sistema multi-tenant';

-- Tabla: msps (Managed Service Providers)
CREATE TABLE IF NOT EXISTS msps (
    msp_id VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    razon_social VARCHAR(200),
    rfc VARCHAR(20),
    email_contacto VARCHAR(200) NOT NULL,
    telefono_contacto VARCHAR(20),
    direccion TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    plan VARCHAR(50) DEFAULT 'basic',
    max_condominios INTEGER DEFAULT 10,
    configuracion TEXT,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX idx_msps_estado ON msps(estado);
CREATE INDEX idx_msps_nombre ON msps(nombre);

COMMENT ON TABLE msps IS 'Proveedores de servicios que gestionan múltiples condominios';

-- Tabla: condominios (residenciales gestionados por MSPs)
CREATE TABLE IF NOT EXISTS condominios (
    condominio_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(10),
    telefono VARCHAR(20),
    email VARCHAR(200),
    total_unidades INTEGER DEFAULT 0,
    estado_operativo VARCHAR(20) DEFAULT 'activo',
    configuracion TEXT,
    timezone VARCHAR(50) DEFAULT 'America/Mexico_City',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT
);

CREATE INDEX idx_condominios_msp ON condominios(msp_id);
CREATE INDEX idx_condominios_estado ON condominios(estado_operativo);
CREATE INDEX idx_condominios_nombre ON condominios(nombre);

COMMENT ON TABLE condominios IS 'Residenciales individuales asociados a un MSP';

-- Tabla: msp_admins (administradores de MSP)
CREATE TABLE IF NOT EXISTS msp_admins (
    msp_admin_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    permisos TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    ultimo_acceso TIMESTAMPTZ,
    created_by VARCHAR(100),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE CASCADE
);

CREATE INDEX idx_msp_admins_msp ON msp_admins(msp_id);
CREATE INDEX idx_msp_admins_estado ON msp_admins(estado);
CREATE INDEX idx_msp_admins_email ON msp_admins(email);

COMMENT ON TABLE msp_admins IS 'Administradores de MSP con acceso a todos sus condominios';

-- Tabla: condominio_admins (administradores locales por condominio)
CREATE TABLE IF NOT EXISTS condominio_admins (
    condominio_admin_id VARCHAR(100) PRIMARY KEY,
    condominio_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    permisos TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    ultimo_acceso TIMESTAMPTZ,
    created_by VARCHAR(100),
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE CASCADE
);

CREATE INDEX idx_condominio_admins_condominio ON condominio_admins(condominio_id);
CREATE INDEX idx_condominio_admins_estado ON condominio_admins(estado);
CREATE INDEX idx_condominio_admins_email ON condominio_admins(email);

COMMENT ON TABLE condominio_admins IS 'Administradores locales con acceso solo a su condominio específico';

-- Tabla: eventos (bitácora universal)
CREATE TABLE IF NOT EXISTS eventos (
    evento_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100),
    entidad_id VARCHAR(100),
    tipo_evento VARCHAR(50) NOT NULL,
    metadata TEXT,
    evidencia_id VARCHAR(100),
    hash_actual VARCHAR(100) NOT NULL,
    timestamp_servidor TIMESTAMPTZ DEFAULT NOW(),
    timestamp_cliente TIMESTAMPTZ,
    actor VARCHAR(100),
    dispositivo VARCHAR(100),
    origen VARCHAR(100),
    contexto TEXT,
    recibo_recordia VARCHAR(200),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT,
    FOREIGN KEY(entidad_id) REFERENCES entidades(entidad_id)
);

CREATE INDEX idx_eventos_msp ON eventos(msp_id);
CREATE INDEX idx_eventos_condominio ON eventos(condominio_id);
CREATE INDEX idx_eventos_tipo ON eventos(tipo_evento);
CREATE INDEX idx_eventos_timestamp ON eventos(timestamp_servidor);
CREATE INDEX idx_eventos_entidad ON eventos(entidad_id);

-- Tabla: visitas
CREATE TABLE IF NOT EXISTS visitas (
    id SERIAL PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100) NOT NULL,
    visitante VARCHAR(200) NOT NULL,
    residente VARCHAR(200) NOT NULL,
    fecha_entrada TIMESTAMPTZ DEFAULT NOW(),
    fecha_salida TIMESTAMPTZ,
    motivo TEXT,
    observaciones TEXT,
    foto_url VARCHAR(500),
    qr_code VARCHAR(100),
    qr_usado BOOLEAN DEFAULT FALSE,
    metadata JSONB,
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_visitas_msp ON visitas(msp_id);
CREATE INDEX idx_visitas_condominio ON visitas(condominio_id);
CREATE INDEX idx_visitas_visitante ON visitas(visitante);
CREATE INDEX idx_visitas_residente ON visitas(residente);
CREATE INDEX idx_visitas_fecha ON visitas(fecha_entrada);

-- Tabla: proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    empresa VARCHAR(200),
    tipo_servicio VARCHAR(100),
    fecha_entrada TIMESTAMPTZ DEFAULT NOW(),
    fecha_salida TIMESTAMPTZ,
    autorizado_por VARCHAR(200),
    observaciones TEXT,
    foto_url VARCHAR(500),
    metadata JSONB,
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_proveedores_msp ON proveedores(msp_id);
CREATE INDEX idx_proveedores_condominio ON proveedores(condominio_id);
CREATE INDEX idx_proveedores_nombre ON proveedores(nombre);
CREATE INDEX idx_proveedores_empresa ON proveedores(empresa);

-- Tabla: bitacora_exo (eventos AUP-EXO)
CREATE TABLE IF NOT EXISTS bitacora_exo (
    id SERIAL PRIMARY KEY,
    tipo_evento VARCHAR(50) NOT NULL,
    entidad_id INTEGER,
    entidad_tipo VARCHAR(50),
    descripcion TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    score INTEGER DEFAULT 0,
    nivel_riesgo VARCHAR(20) DEFAULT 'NORMAL'
);

CREATE INDEX idx_bitacora_tipo ON bitacora_exo(tipo_evento);
CREATE INDEX idx_bitacora_entidad ON bitacora_exo(entidad_id);
CREATE INDEX idx_bitacora_timestamp ON bitacora_exo(timestamp);
CREATE INDEX idx_bitacora_riesgo ON bitacora_exo(nivel_riesgo);

-- Tabla: residentes
CREATE TABLE IF NOT EXISTS residentes (
    id SERIAL PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_residentes_msp ON residentes(msp_id);
CREATE INDEX idx_residentes_condominio ON residentes(condominio_id);
CREATE INDEX idx_residentes_unidad ON residentes(unidad);
CREATE INDEX idx_residentes_activo ON residentes(activo);

-- Tabla: entidades (AUP-EXO - sistema universal)
CREATE TABLE IF NOT EXISTS entidades (
    entidad_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100),
    tipo VARCHAR(50) NOT NULL,
    atributos TEXT NOT NULL,
    hash_actual VARCHAR(100) NOT NULL,
    hash_previo VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_entidades_msp ON entidades(msp_id);
CREATE INDEX idx_entidades_condominio ON entidades(condominio_id);
CREATE INDEX idx_entidades_tipo ON entidades(tipo);
CREATE INDEX idx_entidades_estado ON entidades(estado);

-- Tabla: politicas (reglas AUP-EXO)
CREATE TABLE IF NOT EXISTS politicas (
    politica_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100),
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    condiciones TEXT NOT NULL,
    prioridad INTEGER DEFAULT 5,
    estado VARCHAR(20) DEFAULT 'activa',
    aplicable_a VARCHAR(50),
    ambito VARCHAR(20) DEFAULT 'condominio',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_politicas_msp ON politicas(msp_id);
CREATE INDEX idx_politicas_condominio ON politicas(condominio_id);
CREATE INDEX idx_politicas_tipo ON politicas(tipo);
CREATE INDEX idx_politicas_estado ON politicas(estado);
CREATE INDEX idx_politicas_ambito ON politicas(ambito);

COMMENT ON COLUMN politicas.ambito IS 'Define si la política aplica a nivel: global, msp, o condominio';

-- Tabla: bitacora (auditoría completa)
CREATE TABLE IF NOT EXISTS bitacora (
    bitacora_id SERIAL PRIMARY KEY,
    tabla VARCHAR(100) NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    registro_id VARCHAR(100) NOT NULL,
    datos_anteriores TEXT,
    datos_nuevos TEXT,
    usuario_id VARCHAR(100),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    ip_address VARCHAR(50),
    user_agent TEXT
);

CREATE INDEX idx_bitacora_tabla ON bitacora(tabla);
CREATE INDEX idx_bitacora_timestamp ON bitacora(timestamp);

-- Tabla: log_reglas (debugging y análisis)
CREATE TABLE IF NOT EXISTS log_reglas (
    log_id SERIAL PRIMARY KEY,
    evento_id VARCHAR(100),
    politica_id VARCHAR(100),
    resultado VARCHAR(50) NOT NULL,
    motivo TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (evento_id) REFERENCES eventos(evento_id),
    FOREIGN KEY (politica_id) REFERENCES politicas(politica_id)
);

CREATE INDEX idx_log_reglas_evento ON log_reglas(evento_id);
CREATE INDEX idx_log_reglas_politica ON log_reglas(politica_id);
CREATE INDEX idx_log_reglas_timestamp ON log_reglas(timestamp);

-- Tabla: usuarios (roles y permisos)
CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id VARCHAR(100) PRIMARY KEY,
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100),
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL,
    permisos TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    nivel_acceso VARCHAR(20) DEFAULT 'local',
    ultimo_acceso TIMESTAMPTZ,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY(msp_id) REFERENCES msps(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY(condominio_id) REFERENCES condominios(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_usuarios_msp ON usuarios(msp_id);
CREATE INDEX idx_usuarios_condominio ON usuarios(condominio_id);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);
CREATE INDEX idx_usuarios_nivel ON usuarios(nivel_acceso);

COMMENT ON COLUMN usuarios.nivel_acceso IS 'Define el nivel de acceso: super_admin, msp, condominio, local';

-- Tabla: roles
CREATE TABLE IF NOT EXISTS roles (
    rol_id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    permisos TEXT NOT NULL,
    nivel_acceso INTEGER DEFAULT 1,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_roles_nivel ON roles(nivel_acceso);

-- Tabla: sentinel_insights (AX-S Sentinel™)
CREATE TABLE IF NOT EXISTS sentinel_insights (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    tipo_insight VARCHAR(100) NOT NULL,
    descripcion TEXT,
    severidad VARCHAR(20) DEFAULT 'INFO',
    score_cambio INTEGER DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_sentinel_entidad ON sentinel_insights(entidad_id);
CREATE INDEX idx_sentinel_tipo ON sentinel_insights(tipo_insight);
CREATE INDEX idx_sentinel_severidad ON sentinel_insights(severidad);
CREATE INDEX idx_sentinel_timestamp ON sentinel_insights(timestamp);

-- Tabla: visionline_sync (integración futura)
CREATE TABLE IF NOT EXISTS visionline_sync (
    id SERIAL PRIMARY KEY,
    tipo_operacion VARCHAR(50) NOT NULL,
    entidad_id INTEGER,
    payload JSONB,
    estado VARCHAR(20) DEFAULT 'PENDIENTE',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    respuesta JSONB
);

CREATE INDEX idx_visionline_estado ON visionline_sync(estado);
CREATE INDEX idx_visionline_timestamp ON visionline_sync(timestamp);

-- Vista: eventos_recientes (últimos 7 días)
CREATE OR REPLACE VIEW eventos_recientes AS
SELECT 
    e.id,
    e.tipo,
    e.rol,
    e.detalle,
    e.timestamp,
    e.entidad_id,
    e.score,
    ent.nombre as entidad_nombre,
    ent.nivel_riesgo
FROM eventos e
LEFT JOIN entidades ent ON e.entidad_id = ent.id
WHERE e.timestamp >= NOW() - INTERVAL '7 days'
ORDER BY e.timestamp DESC;

-- Vista: top_entidades_riesgo
CREATE OR REPLACE VIEW top_entidades_riesgo AS
SELECT 
    id,
    tipo,
    nombre,
    score,
    nivel_riesgo,
    ultima_actividad,
    (metadata->>'eventos_count')::INTEGER as eventos_count
FROM entidades
WHERE score > 0
ORDER BY score DESC, ultima_actividad DESC
LIMIT 50;

-- Comentarios para documentación
COMMENT ON TABLE eventos IS 'Bitácora universal de todos los eventos del sistema';
COMMENT ON TABLE entidades IS 'Sistema AUP-EXO: gestión universal de entidades con scoring';
COMMENT ON TABLE sentinel_insights IS 'AX-S Sentinel™: insights de comportamiento y riesgo';
COMMENT ON TABLE visionline_sync IS 'Cola de sincronización con VisionLine (futuro)';
