-- ========================================
-- AX-S PostgreSQL Schema
-- Tipos nativos PostgreSQL optimizados
-- ========================================

-- Tabla: eventos (bitácora universal)
CREATE TABLE IF NOT EXISTS eventos (
    evento_id VARCHAR(100) PRIMARY KEY,
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
    FOREIGN KEY(entidad_id) REFERENCES entidades(entidad_id)
);

CREATE INDEX idx_eventos_tipo ON eventos(tipo_evento);
CREATE INDEX idx_eventos_timestamp ON eventos(timestamp_servidor);
CREATE INDEX idx_eventos_entidad ON eventos(entidad_id);

-- Tabla: visitas
CREATE TABLE IF NOT EXISTS visitas (
    id SERIAL PRIMARY KEY,
    visitante VARCHAR(200) NOT NULL,
    residente VARCHAR(200) NOT NULL,
    fecha_entrada TIMESTAMPTZ DEFAULT NOW(),
    fecha_salida TIMESTAMPTZ,
    motivo TEXT,
    observaciones TEXT,
    foto_url VARCHAR(500),
    qr_code VARCHAR(100),
    qr_usado BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

CREATE INDEX idx_visitas_visitante ON visitas(visitante);
CREATE INDEX idx_visitas_residente ON visitas(residente);
CREATE INDEX idx_visitas_fecha ON visitas(fecha_entrada);

-- Tabla: proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    empresa VARCHAR(200),
    tipo_servicio VARCHAR(100),
    fecha_entrada TIMESTAMPTZ DEFAULT NOW(),
    fecha_salida TIMESTAMPTZ,
    autorizado_por VARCHAR(200),
    observaciones TEXT,
    foto_url VARCHAR(500),
    metadata JSONB
);

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
    nombre VARCHAR(200) NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_residentes_unidad ON residentes(unidad);
CREATE INDEX idx_residentes_activo ON residentes(activo);

-- Tabla: entidades (AUP-EXO - sistema universal)
CREATE TABLE IF NOT EXISTS entidades (
    entidad_id VARCHAR(100) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    atributos TEXT NOT NULL,
    hash_actual VARCHAR(100) NOT NULL,
    hash_previo VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX idx_entidades_tipo ON entidades(tipo);
CREATE INDEX idx_entidades_estado ON entidades(estado);

-- Tabla: politicas (reglas AUP-EXO)
CREATE TABLE IF NOT EXISTS politicas (
    politica_id VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    condiciones TEXT NOT NULL,
    prioridad INTEGER DEFAULT 5,
    estado VARCHAR(20) DEFAULT 'activa',
    aplicable_a VARCHAR(50),
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_actualizacion TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX idx_politicas_tipo ON politicas(tipo);
CREATE INDEX idx_politicas_estado ON politicas(estado);

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
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL,
    permisos TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    ultimo_acceso TIMESTAMPTZ,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_usuarios_rol ON usuarios(rol);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);

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
