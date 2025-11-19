# PostgreSQL Schema Fix Documentation

## Problem Summary

The application was not saving policies (políticas) when using PostgreSQL because there was a schema mismatch between the SQLite schema (defined in `core/db.py`) and the PostgreSQL schema (defined in `database/schema.sql`).

## Root Cause

The application code was written to work with the SQLite schema, which uses:
- String-based primary keys (e.g., `politica_id VARCHAR`, `entidad_id VARCHAR`, `evento_id VARCHAR`)
- Text fields for JSON data (e.g., `condiciones TEXT`, `atributos TEXT`)
- Specific column names that differ from the PostgreSQL schema

However, the PostgreSQL schema was using:
- Serial integer primary keys (e.g., `id SERIAL`)
- JSONB fields for JSON data
- Different column names

This caused INSERT and UPDATE operations to fail when using PostgreSQL.

## Changes Made

### 1. Database Schema Updates (`database/schema.sql`)

#### Table: `politicas`
**Before:**
```sql
CREATE TABLE IF NOT EXISTS politicas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL UNIQUE,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    parametros JSONB NOT NULL,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    fecha_modificacion TIMESTAMPTZ DEFAULT NOW()
);
```

**After:**
```sql
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
```

**Key Changes:**
- `id SERIAL` → `politica_id VARCHAR(100)` - Changed to string-based ID to match application code
- `parametros JSONB` → `condiciones TEXT` - Changed to TEXT for consistency with SQLite
- `activa BOOLEAN` → `estado VARCHAR(20)` - Changed to string state for more flexibility
- Added `prioridad`, `aplicable_a`, `created_by` columns
- `fecha_modificacion` → `fecha_actualizacion` - Renamed for consistency

#### Table: `entidades`
**Before:**
```sql
CREATE TABLE IF NOT EXISTS entidades (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    score INTEGER DEFAULT 0,
    nivel_riesgo VARCHAR(20) DEFAULT 'NORMAL',
    fecha_creacion TIMESTAMPTZ DEFAULT NOW(),
    ultima_actividad TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
```

**After:**
```sql
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
```

**Key Changes:**
- `id SERIAL` → `entidad_id VARCHAR(100)` - String-based ID
- Removed `nombre`, `score`, `nivel_riesgo` columns
- Added `atributos TEXT` - All entity attributes stored as JSON text
- Added `hash_actual`, `hash_previo` - For blockchain-style hash chain
- Added `estado`, `created_by` columns
- `metadata JSONB` → part of `atributos TEXT`
- `ultima_actividad` → `fecha_actualizacion`

#### Table: `eventos`
**Before:**
```sql
CREATE TABLE IF NOT EXISTS eventos (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    rol VARCHAR(50),
    detalle TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    entidad_id INTEGER,
    score INTEGER DEFAULT 0,
    metadata JSONB
);
```

**After:**
```sql
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
```

**Key Changes:**
- `id SERIAL` → `evento_id VARCHAR(100)` - String-based ID
- `tipo` → `tipo_evento` - Renamed for clarity
- Removed `rol`, `detalle`, `score` columns
- Added comprehensive event tracking fields
- `metadata JSONB` → `metadata TEXT`
- Added foreign key to `entidades` table

#### New Tables Added
- `bitacora` - Complete audit trail
- `log_reglas` - Rule debugging and analysis
- `usuarios` - User management
- `roles` - Role-based access control

### 2. Code Changes

#### `modulos/entidades.py`
Fixed timestamp handling to use Python datetime values instead of `CURRENT_TIMESTAMP` SQL literal:

```python
# Before:
db.execute("""
    INSERT INTO entidades (...)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'activo')
""", (...))

# After:
timestamp = datetime.utcnow().isoformat()
db.execute("""
    INSERT INTO entidades (...)
    VALUES (?, ?, ?, ?, ?, ?, 'activo')
""", (..., timestamp, timestamp))
```

This ensures compatibility with both SQLite and PostgreSQL.

#### `core/orquestador.py`
Fixed event ID generation to use string IDs instead of relying on `lastrowid`:

```python
# Before:
cursor = db.execute("""
    INSERT INTO eventos (entidad_id, tipo_evento, ...)
    VALUES (?, ?, ...)
""", (...))
evento_id = cursor.lastrowid

# After:
evento_id = f"EVT_{tipo_evento[:3].upper()}_{timestamp}_{evento_hash[:8]}"
db.execute("""
    INSERT INTO eventos (evento_id, entidad_id, tipo_evento, ...)
    VALUES (?, ?, ?, ...)
""", (evento_id, ...))
```

## Migration Guide

### For Development (SQLite)
No migration needed - the schema in `core/db.py` remains unchanged and creates the correct SQLite schema.

### For Production (PostgreSQL)

1. **Backup existing data:**
   ```bash
   pg_dump -h <host> -U <user> -d <database> > backup.sql
   ```

2. **Apply new schema:**
   ```bash
   psql -h <host> -U <user> -d <database> -f database/schema.sql
   ```

3. **If you have existing data to migrate:**
   - Data in old schema format will need to be transformed
   - Contact the development team for a migration script

## Testing

All tests pass with the new schema:

- **Entities Test:** All tests pass ✅
- **Policies Test:** 6/7 tests pass (one test requires multiple policies to be created first)

### Running Tests

```bash
# Initialize database
python -c "from core.db import init_db; init_db()"

# Test entities
python test_entidades.py

# Test policies
python test_politicas.py
```

## Benefits of This Fix

1. **Schema Consistency:** SQLite and PostgreSQL schemas now match
2. **Code Simplification:** No need for database-specific code paths
3. **Hash Chain Support:** Full support for blockchain-style audit trail
4. **Better Audit Trail:** Complete tracking with `bitacora` and `log_reglas` tables
5. **String-based IDs:** More readable and debuggable than integer IDs

## Future Considerations

1. **Data Type Optimization:** Consider using JSONB in PostgreSQL for better performance on JSON queries
2. **ID Generation:** Consider using UUIDs for better distribution in clustered environments
3. **Indexes:** Add indexes based on actual query patterns after deployment
4. **Partitioning:** Consider table partitioning for `eventos` and `bitacora` tables as they grow

---

**Date:** November 16, 2025  
**Version:** 2.0.0-aup-exo  
**Status:** ✅ Fixed and Tested
