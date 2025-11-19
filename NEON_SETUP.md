# 🗄️ Configuración de PostgreSQL en Neon para Multi-Tenant

## 🎯 Objetivo

Configurar una nueva base de datos PostgreSQL en Neon Cloud específicamente para la versión **Multi-Tenant** de AX-S, sin afectar ninguna base de datos single-tenant existente.

---

## 📋 Paso 1: Crear Nuevo Proyecto en Neon

### 1.1 Acceder a Neon Console

1. Ve a: https://console.neon.tech
2. Login con tu cuenta
3. Click en **"New Project"**

### 1.2 Configuración del Proyecto

```
Project name: AX-S-MultiTenant-Production
Region: us-east-1 (o el más cercano a ti)
PostgreSQL version: 16 (recomendado)
Compute size: 0.25 vCPU (free tier)
```

4. Click **"Create Project"**

### 1.3 Copiar Credenciales

Una vez creado, verás la **Connection String**. Cópiala completa:

```
postgresql://neondb_owner:XXXXXXXX@ep-XXXXXX-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Guarda estos datos** (los necesitarás):
- **Host**: `ep-XXXXXX-pooler.us-east-1.aws.neon.tech`
- **Database**: `neondb`
- **User**: `neondb_owner`
- **Password**: `XXXXXXXX`
- **Port**: `5432`

---

## 📋 Paso 2: Crear Schema Multi-Tenant

### 2.1 Abrir SQL Editor en Neon

1. En Neon Console, ve a **"SQL Editor"** (menú izquierdo)
2. Asegúrate de estar en el proyecto **AX-S-MultiTenant-Production**

### 2.2 Ejecutar Script de Creación de Tablas

Copia y pega el siguiente SQL en el editor y ejecuta (**Run**):

```sql
-- ============================================
-- AX-S Multi-Tenant Schema
-- Creación de Tablas para PostgreSQL en Neon
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
    estado TEXT DEFAULT 'activo',
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
    total_unidades INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Entidades (Residentes, Visitantes, Proveedores, Vehículos)
CREATE TABLE IF NOT EXISTS entidades (
    id SERIAL PRIMARY KEY,
    tipo TEXT,
    nombre_completo TEXT,
    identificacion TEXT,
    telefono TEXT,
    email TEXT,
    direccion TEXT,
    atributos TEXT,
    hash_actual TEXT,
    hash_previo TEXT,
    msp_id TEXT REFERENCES msps_exo(msp_id) ON DELETE SET NULL,
    condominio_id TEXT REFERENCES condominios_exo(condominio_id) ON DELETE SET NULL,
    estado TEXT DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    nombre TEXT,
    creado_en TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_msps_msp_id ON msps_exo(msp_id);
CREATE INDEX IF NOT EXISTS idx_msps_estado ON msps_exo(estado);

CREATE INDEX IF NOT EXISTS idx_condominios_condominio_id ON condominios_exo(condominio_id);
CREATE INDEX IF NOT EXISTS idx_condominios_msp_id ON condominios_exo(msp_id);
CREATE INDEX IF NOT EXISTS idx_condominios_estado ON condominios_exo(estado);

CREATE INDEX IF NOT EXISTS idx_entidades_tipo ON entidades(tipo);
CREATE INDEX IF NOT EXISTS idx_entidades_identificacion ON entidades(identificacion);
CREATE INDEX IF NOT EXISTS idx_entidades_msp_id ON entidades(msp_id);
CREATE INDEX IF NOT EXISTS idx_entidades_condominio_id ON entidades(condominio_id);
CREATE INDEX IF NOT EXISTS idx_entidades_estado ON entidades(estado);

-- Comentarios para documentación
COMMENT ON TABLE msps_exo IS 'Multi-Service Providers - Empresas de seguridad';
COMMENT ON TABLE condominios_exo IS 'Condominios administrados por MSPs';
COMMENT ON TABLE entidades IS 'Entidades del sistema (residentes, visitantes, proveedores, vehículos)';

COMMENT ON COLUMN entidades.tipo IS 'Tipo: residente, visitante, proveedor, vehiculo';
COMMENT ON COLUMN entidades.atributos IS 'JSON con atributos específicos por tipo';
COMMENT ON COLUMN entidades.hash_actual IS 'Hash SHA-256 de datos actuales';
COMMENT ON COLUMN entidades.hash_previo IS 'Hash SHA-256 de datos previos (para auditoría)';
```

### 2.3 Verificar Creación

Ejecuta este query para verificar que las tablas se crearon:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

**Resultado esperado**:
```
table_name
-----------------
condominios_exo
entidades
msps_exo
```

---

## 📋 Paso 3: Insertar Datos de Ejemplo

### 3.1 Crear MSP de Prueba

```sql
INSERT INTO msps_exo (msp_id, nombre, email, telefono, ciudad, estado)
VALUES (
    'MSP-DEMO-001',
    'Demo Security Services',
    'demo@ejemplo.com',
    '+52 55 1234 5678',
    'Ciudad de México',
    'activo'
);
```

### 3.2 Crear Condominio de Prueba

```sql
INSERT INTO condominios_exo (
    condominio_id, 
    msp_id, 
    nombre, 
    ciudad, 
    total_unidades, 
    estado
)
VALUES (
    'COND-DEMO-001',
    'MSP-DEMO-001',
    'Residencial Demo',
    'Ciudad de México',
    50,
    'activo'
);
```

### 3.3 Verificar Datos

```sql
-- Ver MSPs
SELECT msp_id, nombre, ciudad, estado FROM msps_exo;

-- Ver Condominios
SELECT condominio_id, msp_id, nombre, total_unidades FROM condominios_exo;

-- Contar entidades
SELECT COUNT(*) as total_entidades FROM entidades;
```

---

## 📋 Paso 4: Configurar Connection Pooling

### 4.1 Habilitar Pooler (Recomendado)

En Neon, el pooler ya está habilitado por defecto. Asegúrate de usar la URL con `-pooler`:

✅ **Correcto**:
```
ep-XXXXXX-pooler.us-east-1.aws.neon.tech
```

❌ **Incorrecto** (sin pooler):
```
ep-XXXXXX.us-east-1.aws.neon.tech
```

### 4.2 Configuración de Parámetros

En Neon Console → **Settings** → **Connection pooling**:

```
Mode: Transaction
Pool size: 100 (default)
```

---

## 📋 Paso 5: Configurar Backups (Automáticos)

Neon hace backups automáticos, pero puedes configurar:

1. En Neon Console → **Settings** → **Compute**
2. **Auto-suspend**: 5 minutos de inactividad (ahorra recursos)
3. **Autoscaling**: Habilitado (free tier: 0.25 vCPU fijo)

---

## 📋 Paso 6: Seguridad y Acceso

### 6.1 Rotar Password (Opcional pero Recomendado)

1. Neon Console → **Settings** → **Reset password**
2. Copia el nuevo password
3. Actualiza `.streamlit/secrets.toml`

### 6.2 Restringir Acceso por IP (Pro Plan)

En tier gratuito no está disponible, pero en producción considera:
- Neon Pro: Permite IP allowlist
- Útil para mayor seguridad

---

## 📋 Paso 7: Monitoreo

### 7.1 Ver Métricas en Neon Console

- **Dashboard** → Ver uso de CPU, memoria, storage
- **Monitoring** → Queries lentas, conexiones activas
- **Logs** → Ver errores de conexión

### 7.2 Alertas (Pro Plan)

En tier gratuito, revisa manualmente:
- Storage usado: `SELECT pg_database_size('neondb') / 1024 / 1024 AS size_mb;`
- Conexiones activas: `SELECT count(*) FROM pg_stat_activity;`

---

## 📋 Paso 8: Optimizaciones para Producción

### 8.1 Vacuum y Analyze Automáticos

Neon lo hace automáticamente, pero puedes forzar:

```sql
VACUUM ANALYZE msps_exo;
VACUUM ANALYZE condominios_exo;
VACUUM ANALYZE entidades;
```

### 8.2 Ver Estadísticas de Tablas

```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as "rows",
    n_dead_tup as "dead_rows",
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;
```

---

## 🔧 Troubleshooting

### Problema: "Connection refused"

**Solución**:
```sql
-- Verificar que Neon Compute esté activo
-- En Neon Console, ve a Dashboard y verifica estado
```

### Problema: "Too many connections"

**Solución**:
```sql
-- Ver conexiones actuales
SELECT count(*) FROM pg_stat_activity;

-- Cerrar conexiones idle
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < now() - interval '5 minutes';
```

### Problema: "Relation does not exist"

**Solución**:
```sql
-- Listar todas las tablas
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Re-ejecutar script de creación de tablas
```

---

## 📊 Checklist de Configuración Neon

- [ ] Proyecto creado: `AX-S-MultiTenant-Production`
- [ ] Connection string copiada y guardada
- [ ] SQL Editor abierto
- [ ] Tablas creadas: `msps_exo`, `condominios_exo`, `entidades`
- [ ] Índices creados correctamente
- [ ] Datos de ejemplo insertados (MSP + Condominio)
- [ ] Verificación: `SELECT * FROM msps_exo;` retorna 1 fila
- [ ] Pooler habilitado (URL con `-pooler`)
- [ ] Auto-suspend configurado (5 min)
- [ ] Password guardado en lugar seguro

---

## 🎯 Siguiente Paso: Conectar desde Streamlit

Una vez completados estos pasos, copia las credenciales a:

**Localmente** (`.streamlit/secrets.toml`):
```toml
DB_MODE = "postgres"
PG_HOST = "ep-XXXXXX-pooler.us-east-1.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

**Streamlit Cloud** (App Settings → Secrets):
```toml
DB_MODE = "postgres"
PG_HOST = "ep-XXXXXX-pooler.us-east-1.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

---

## ✅ Verificación Final

Ejecuta desde tu terminal:

```bash
python3 check_db_version.py
```

**Salida esperada**:
```
🎯 MULTI-TENANT
✅ msps_exo
✅ condominios_exo
✅ entidades tiene columnas multi-tenant (msp_id, condominio_id)
MSPs: 1
Condominios: 1
Entidades: 0
```

---

**Documento creado**: 19/11/2025  
**Autor**: B10sp4rt4n  
**Versión**: 1.0
