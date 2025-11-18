-- ========================================
-- AX-S PostgreSQL Schema (AUP-EXO)
-- Modelo Universal de Jerarquías, Dominios y Contención
-- ========================================
-- Diseño: Super Admin > MSP > Condominio > Admin Local
-- Arquitectura: Multitenancy MSP-Ready
-- Filosofía: Exógeno, escalable, auditable
-- ========================================

-- ========================================
-- SECCIÓN 1: ROLES Y JERARQUÍAS
-- ========================================

-- 1. Tabla: roles_exo (Roles del sistema)
CREATE TABLE IF NOT EXISTS roles_exo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    nivel INTEGER NOT NULL, -- 1: DS (Super Admin), 2: DD (MSP), 3: SE (Condominio), 4: NO (Local)
    permisos_json TEXT, -- Permisos serializados en JSON
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_roles_exo_nivel ON roles_exo(nivel);

COMMENT ON TABLE roles_exo IS 'Roles jerárquicos del sistema AUP-EXO';
COMMENT ON COLUMN roles_exo.nivel IS '1=DS(Super), 2=DD(MSP), 3=SE(Condominio), 4=NO(Local)';

-- Datos iniciales de roles
INSERT INTO roles_exo (nombre, descripcion, nivel) VALUES
    ('super_admin', 'Super Administrador - Dominio Superior (DS)', 1),
    ('msp_admin', 'Administrador MSP - Dominio Delegado (DD)', 2),
    ('condominio_admin', 'Administrador Condominio - Subdominio Específico (SE)', 3),
    ('admin_local', 'Administrador Local - Nodo Operativo (NO)', 4)
ON CONFLICT (nombre) DO NOTHING;

-- ========================================
-- SECCIÓN 2: DOMINIOS (MSP Y CONDOMINIOS)
-- ========================================

-- 2. Tabla: msps_exo (Managed Service Providers - Dominio Delegado DD)
CREATE TABLE IF NOT EXISTS msps_exo (
    id SERIAL PRIMARY KEY,
    msp_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    nombre VARCHAR(200) NOT NULL,
    razon_social VARCHAR(200),
    rfc VARCHAR(20),
    email_contacto VARCHAR(200),
    telefono_contacto VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'activo', -- activo, suspendido, inactivo
    plan VARCHAR(50) DEFAULT 'basic', -- basic, professional, enterprise
    max_condominios INTEGER DEFAULT 10,
    configuracion_json TEXT, -- Configuración específica del MSP
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_msps_exo_estado ON msps_exo(estado);
CREATE INDEX idx_msps_exo_msp_id ON msps_exo(msp_id);

COMMENT ON TABLE msps_exo IS 'MSPs - Dominio Delegado (DD) - Resellers/Partners';

-- 3. Tabla: condominios_exo (Subdominio Específico SE)
CREATE TABLE IF NOT EXISTS condominios_exo (
    id SERIAL PRIMARY KEY,
    condominio_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    msp_id VARCHAR(100) NOT NULL, -- Referencia al MSP padre
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT,
    ciudad VARCHAR(100),
    estado_mx VARCHAR(100),
    codigo_postal VARCHAR(10),
    telefono VARCHAR(20),
    email VARCHAR(200),
    total_unidades INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'activo', -- activo, suspendido, inactivo
    timezone VARCHAR(50) DEFAULT 'America/Mexico_City',
    configuracion_json TEXT, -- Configuración específica del condominio
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id) ON DELETE RESTRICT
);

CREATE INDEX idx_condominios_exo_msp ON condominios_exo(msp_id);
CREATE INDEX idx_condominios_exo_estado ON condominios_exo(estado);
CREATE INDEX idx_condominios_exo_condominio_id ON condominios_exo(condominio_id);

COMMENT ON TABLE condominios_exo IS 'Condominios - Subdominio Específico (SE) - Clientes finales';

-- ========================================
-- SECCIÓN 3: USUARIOS MULTINIVEL
-- ========================================

-- 4. Tabla: usuarios_exo (Usuarios del sistema multinivel)
CREATE TABLE IF NOT EXISTS usuarios_exo (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    rol_id INTEGER NOT NULL, -- Referencia a roles_exo
    msp_id VARCHAR(100), -- NULL para Super Admin
    condominio_id VARCHAR(100), -- NULL para Super Admin y MSP Admin
    
    estado VARCHAR(20) DEFAULT 'activo', -- activo, suspendido, inactivo
    ultimo_acceso TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (rol_id) REFERENCES roles_exo(id),
    FOREIGN KEY (msp_id) REFERENCES msps_exo(msp_id) ON DELETE RESTRICT,
    FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_usuarios_exo_rol ON usuarios_exo(rol_id);
CREATE INDEX idx_usuarios_exo_msp ON usuarios_exo(msp_id);
CREATE INDEX idx_usuarios_exo_condominio ON usuarios_exo(condominio_id);
CREATE INDEX idx_usuarios_exo_email ON usuarios_exo(email);
CREATE INDEX idx_usuarios_exo_estado ON usuarios_exo(estado);

COMMENT ON TABLE usuarios_exo IS 'Usuarios multinivel con scope jerárquico';
COMMENT ON COLUMN usuarios_exo.msp_id IS 'NULL = Super Admin | Valor = MSP/Condominio/Local Admin';
COMMENT ON COLUMN usuarios_exo.condominio_id IS 'NULL = Super Admin/MSP Admin | Valor = Condominio/Local Admin';

-- ========================================
-- SECCIÓN 4: RESIDENCIAS Y RESIDENTES
-- ========================================

-- 5. Tabla: residencias_exo (Casas/Unidades dentro de condominios)
CREATE TABLE IF NOT EXISTS residencias_exo (
    id SERIAL PRIMARY KEY,
    residencia_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    condominio_id VARCHAR(100) NOT NULL,
    numero VARCHAR(50) NOT NULL, -- Número de casa/unidad
    propietario VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(200),
    estado VARCHAR(20) DEFAULT 'activo', -- activo, inactivo, mantenimiento
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_residencias_exo_condominio ON residencias_exo(condominio_id);
CREATE INDEX idx_residencias_exo_numero ON residencias_exo(numero);
CREATE INDEX idx_residencias_exo_estado ON residencias_exo(estado);

COMMENT ON TABLE residencias_exo IS 'Unidades habitacionales dentro de condominios';

-- 6. Tabla: residentes_exo (Personas que viven en las residencias)
CREATE TABLE IF NOT EXISTS residentes_exo (
    id SERIAL PRIMARY KEY,
    residente_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    residencia_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(200),
    tipo VARCHAR(50) DEFAULT 'residente', -- residente, inquilino, familiar
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (residencia_id) REFERENCES residencias_exo(residencia_id) ON DELETE RESTRICT
);

CREATE INDEX idx_residentes_exo_residencia ON residentes_exo(residencia_id);
CREATE INDEX idx_residentes_exo_nombre ON residentes_exo(nombre);
CREATE INDEX idx_residentes_exo_estado ON residentes_exo(estado);

COMMENT ON TABLE residentes_exo IS 'Personas que habitan las residencias';

-- ========================================
-- SECCIÓN 5: VISITANTES Y ACCESOS
-- ========================================

-- 7. Tabla: visitantes_exo (Visitas programadas o autorizadas)
CREATE TABLE IF NOT EXISTS visitantes_exo (
    id SERIAL PRIMARY KEY,
    visitante_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    condominio_id VARCHAR(100) NOT NULL,
    residencia_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    telefono VARCHAR(20),
    tipo_visita VARCHAR(50), -- proveedor, invitado, familiar, delivery, etc.
    fecha_autorizacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_expiracion TIMESTAMPTZ,
    qr_code VARCHAR(200), -- Código QR para acceso
    qr_usado BOOLEAN DEFAULT FALSE,
    estado VARCHAR(20) DEFAULT 'pendiente', -- pendiente, activo, expirado, usado
    observaciones TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT,
    FOREIGN KEY (residencia_id) REFERENCES residencias_exo(residencia_id) ON DELETE RESTRICT
);

CREATE INDEX idx_visitantes_exo_condominio ON visitantes_exo(condominio_id);
CREATE INDEX idx_visitantes_exo_residencia ON visitantes_exo(residencia_id);
CREATE INDEX idx_visitantes_exo_qr ON visitantes_exo(qr_code);
CREATE INDEX idx_visitantes_exo_estado ON visitantes_exo(estado);
CREATE INDEX idx_visitantes_exo_fecha_exp ON visitantes_exo(fecha_expiracion);

COMMENT ON TABLE visitantes_exo IS 'Visitas programadas con QR y control de acceso';

-- 8. Tabla: accesos_exo (Log de entradas y salidas - Bitácora operativa)
CREATE TABLE IF NOT EXISTS accesos_exo (
    id SERIAL PRIMARY KEY,
    acceso_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    visitante_id VARCHAR(100), -- NULL si es residente
    residente_id VARCHAR(100), -- NULL si es visitante
    usuario_operador_id VARCHAR(100), -- Admin local que registró
    condominio_id VARCHAR(100) NOT NULL,
    tipo_acceso VARCHAR(20) NOT NULL, -- entrada, salida
    metodo VARCHAR(50) NOT NULL, -- qr, manual, placa, reconocimiento_facial, etc.
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    resultado VARCHAR(20) NOT NULL, -- permitido, denegado
    comentario TEXT,
    metadata_json TEXT, -- Datos adicionales (placas, fotos, etc.)
    FOREIGN KEY (visitante_id) REFERENCES visitantes_exo(visitante_id),
    FOREIGN KEY (residente_id) REFERENCES residentes_exo(residente_id),
    FOREIGN KEY (usuario_operador_id) REFERENCES usuarios_exo(usuario_id),
    FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE RESTRICT
);

CREATE INDEX idx_accesos_exo_condominio ON accesos_exo(condominio_id);
CREATE INDEX idx_accesos_exo_visitante ON accesos_exo(visitante_id);
CREATE INDEX idx_accesos_exo_residente ON accesos_exo(residente_id);
CREATE INDEX idx_accesos_exo_timestamp ON accesos_exo(timestamp);
CREATE INDEX idx_accesos_exo_resultado ON accesos_exo(resultado);
CREATE INDEX idx_accesos_exo_tipo ON accesos_exo(tipo_acceso);

COMMENT ON TABLE accesos_exo IS 'Bitácora universal de entradas y salidas (NO - Nodo Operativo)';

-- ========================================
-- SECCIÓN 6: REGLAS Y PLAYBOOKS
-- ========================================

-- 9. Tabla: reglas_exo (Reglas de operación por condominio)
CREATE TABLE IF NOT EXISTS reglas_exo (
    id SERIAL PRIMARY KEY,
    regla_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    condominio_id VARCHAR(100) NOT NULL,
    regla_nombre VARCHAR(100) NOT NULL,
    regla_tipo VARCHAR(50) NOT NULL, -- horario, autorizacion, alertas, etc.
    regla_valor TEXT NOT NULL, -- Valor serializado (JSON o texto)
    estado VARCHAR(20) DEFAULT 'activa',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (condominio_id) REFERENCES condominios_exo(condominio_id) ON DELETE CASCADE
);

CREATE INDEX idx_reglas_exo_condominio ON reglas_exo(condominio_id);
CREATE INDEX idx_reglas_exo_tipo ON reglas_exo(regla_tipo);
CREATE INDEX idx_reglas_exo_estado ON reglas_exo(estado);

COMMENT ON TABLE reglas_exo IS 'Reglas específicas por condominio (SE)';

-- 10. Tabla: playbooks_exo (Plantillas por vertical/tipo de negocio)
CREATE TABLE IF NOT EXISTS playbooks_exo (
    id SERIAL PRIMARY KEY,
    playbook_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    tipo VARCHAR(50) NOT NULL, -- residencial, corporativo, industrial, educativo, etc.
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    contenido_json TEXT NOT NULL, -- Configuración completa del playbook
    version VARCHAR(20) DEFAULT '1.0',
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_playbooks_exo_tipo ON playbooks_exo(tipo);
CREATE INDEX idx_playbooks_exo_estado ON playbooks_exo(estado);

COMMENT ON TABLE playbooks_exo IS 'Plantillas heredables para diferentes verticales de negocio';

-- ========================================
-- SECCIÓN 7: AUDITORÍA Y LEDGER
-- ========================================

-- 11. Tabla: ledger_exo (Auditoría universal AUP-EXO)
CREATE TABLE IF NOT EXISTS ledger_exo (
    id SERIAL PRIMARY KEY,
    ledger_id VARCHAR(100) UNIQUE NOT NULL, -- Identificador exógeno
    usuario_id VARCHAR(100),
    msp_id VARCHAR(100),
    condominio_id VARCHAR(100),
    accion VARCHAR(100) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, etc.
    entidad VARCHAR(100) NOT NULL, -- Nombre de la tabla/entidad afectada
    entidad_id VARCHAR(100), -- ID del registro afectado
    detalle TEXT, -- Descripción del cambio
    ip_origen VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (usuario_id) REFERENCES usuarios_exo(usuario_id)
);

CREATE INDEX idx_ledger_exo_usuario ON ledger_exo(usuario_id);
CREATE INDEX idx_ledger_exo_msp ON ledger_exo(msp_id);
CREATE INDEX idx_ledger_exo_condominio ON ledger_exo(condominio_id);
CREATE INDEX idx_ledger_exo_accion ON ledger_exo(accion);
CREATE INDEX idx_ledger_exo_entidad ON ledger_exo(entidad);
CREATE INDEX idx_ledger_exo_timestamp ON ledger_exo(timestamp);

COMMENT ON TABLE ledger_exo IS 'Ledger universal de auditoría - trazabilidad completa tipo Recordia';

-- ========================================
-- SECCIÓN 8: VISTAS Y REPORTES
-- ========================================

-- Vista: accesos_recientes (Últimas 24 horas por condominio)
CREATE OR REPLACE VIEW accesos_recientes_exo AS
SELECT 
    a.acceso_id,
    a.condominio_id,
    c.nombre as condominio_nombre,
    COALESCE(v.nombre, r.nombre) as persona_nombre,
    a.tipo_acceso,
    a.metodo,
    a.resultado,
    a.timestamp,
    u.nombre as operador_nombre
FROM accesos_exo a
LEFT JOIN condominios_exo c ON a.condominio_id = c.condominio_id
LEFT JOIN visitantes_exo v ON a.visitante_id = v.visitante_id
LEFT JOIN residentes_exo r ON a.residente_id = r.residente_id
LEFT JOIN usuarios_exo u ON a.usuario_operador_id = u.usuario_id
WHERE a.timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY a.timestamp DESC;

-- Vista: dashboard_msp (Resumen agregado para MSP Admin)
CREATE OR REPLACE VIEW dashboard_msp_exo AS
SELECT 
    m.msp_id,
    m.nombre as msp_nombre,
    COUNT(DISTINCT c.condominio_id) as total_condominios,
    COUNT(DISTINCT c.condominio_id) FILTER (WHERE c.estado = 'activo') as condominios_activos,
    COUNT(DISTINCT r.residencia_id) as total_residencias,
    COUNT(DISTINCT a.acceso_id) FILTER (WHERE a.timestamp >= NOW() - INTERVAL '24 hours') as accesos_24h
FROM msps_exo m
LEFT JOIN condominios_exo c ON m.msp_id = c.msp_id
LEFT JOIN residencias_exo r ON c.condominio_id = r.condominio_id
LEFT JOIN accesos_exo a ON c.condominio_id = a.condominio_id
GROUP BY m.msp_id, m.nombre;

-- Vista: dashboard_condominio (Resumen para Condominio Admin)
CREATE OR REPLACE VIEW dashboard_condominio_exo AS
SELECT 
    c.condominio_id,
    c.nombre as condominio_nombre,
    c.msp_id,
    COUNT(DISTINCT r.residencia_id) as total_residencias,
    COUNT(DISTINCT res.residente_id) as total_residentes,
    COUNT(DISTINCT v.visitante_id) FILTER (WHERE v.estado = 'activo') as visitantes_activos,
    COUNT(DISTINCT a.acceso_id) FILTER (WHERE a.timestamp >= NOW() - INTERVAL '24 hours') as accesos_24h,
    COUNT(DISTINCT a.acceso_id) FILTER (WHERE a.timestamp >= NOW() - INTERVAL '24 hours' AND a.resultado = 'denegado') as accesos_denegados_24h
FROM condominios_exo c
LEFT JOIN residencias_exo r ON c.condominio_id = r.condominio_id
LEFT JOIN residentes_exo res ON r.residencia_id = res.residencia_id
LEFT JOIN visitantes_exo v ON c.condominio_id = v.condominio_id
LEFT JOIN accesos_exo a ON c.condominio_id = a.condominio_id
GROUP BY c.condominio_id, c.nombre, c.msp_id;

-- ========================================
-- COMENTARIOS FINALES
-- ========================================

COMMENT ON DATABASE current_database() IS 'AX-S PostgreSQL Database - AUP-EXO Multitenancy MSP-Ready';

-- Fin del schema AX-S (AUP-EXO)
-- Versión: 1.0
-- Autor: Salvador (AUP-EXO Design)
-- Compatible con: PostgreSQL 12+
-- ========================================
