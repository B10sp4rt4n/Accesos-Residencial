# 🐘 PostgreSQL Migration Guide - AX-S

## 📋 Índice

1. [Arquitectura](#arquitectura)
2. [Configuración](#configuración)
3. [Uso del Módulo](#uso-del-módulo)
4. [Migración de Datos](#migración-de-datos)
5. [Deployment](#deployment)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura

### **Enfoque Adoptado**

Hemos implementado una migración PostgreSQL **nativa y directa** usando:

- ✅ **psycopg2**: Driver nativo sin ORM
- ✅ **RealDictCursor**: Resultados como diccionarios
- ✅ **SQL directo**: Sin abstracción pesada
- ✅ **Dual mode**: SQLite (dev) + PostgreSQL (prod)

### **Estructura de Archivos**

```
database/
├── __init__.py
├── pg_connection.py      # Módulo de conexión PostgreSQL
├── schema.sql            # Schema nativo PostgreSQL
└── migrate_sqlite_to_pg.py  # Script de migración

core/
└── db.py                 # Capa de compatibilidad (detecta DB_MODE)
```

---

## ⚙️ Configuración

### **1. Variables de Entorno (.env)**

```bash
# Modo de base de datos
DB_MODE=postgres          # 'sqlite' o 'postgres'

# PostgreSQL / Supabase
PG_HOST=db.xxxxxx.supabase.co
PG_DATABASE=postgres
PG_USER=postgres
PG_PASSWORD=tu_password_seguro
PG_PORT=5432
```

### **2. Supabase Setup (Recomendado)**

1. Crear cuenta en [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Ir a **Settings → Database**
4. Copiar credenciales:
   - Host: `db.xxxxxx.supabase.co`
   - Database: `postgres`
   - User: `postgres`
   - Password: (generado)
   - Port: `5432`

5. Pegar en `.env`

### **3. Inicializar Schema**

```bash
cd /workspaces/Accesos-Residencial
python -c "from database.pg_connection import init_pg_schema; init_pg_schema()"
```

Esto ejecuta `database/schema.sql` y crea:
- ✅ 10 tablas optimizadas para PostgreSQL
- ✅ Índices (GIN, BTREE)
- ✅ Vistas (eventos_recientes, top_entidades_riesgo)
- ✅ Comentarios de documentación

---

## 🔌 Uso del Módulo

### **Opción 1: Context Manager (Recomendado)**

```python
from database.pg_connection import get_pg_cursor

# Query con resultados dict
with get_pg_cursor() as cur:
    cur.execute("SELECT * FROM eventos WHERE tipo = %s LIMIT 10", ('ingreso',))
    eventos = cur.fetchall()
    
    for evento in eventos:
        print(evento['tipo'], evento['detalle'])  # dict access
```

### **Opción 2: Funciones Helper**

```python
from database.pg_connection import execute_query, execute_insert, execute_update

# SELECT
eventos = execute_query(
    "SELECT * FROM eventos WHERE entidad_id = %s ORDER BY timestamp DESC",
    (100,)
)

# INSERT con RETURNING id
evento_id = execute_insert(
    "INSERT INTO eventos (tipo, rol, detalle) VALUES (%s, %s, %s) RETURNING id",
    ('ingreso', 'vigilante', 'Acceso concedido')
)

# UPDATE
rows_affected = execute_update(
    "UPDATE entidades SET score = score + %s WHERE id = %s",
    (10, 100)
)
```

### **Opción 3: Usar `core/db.py` (Compatibilidad)**

```python
from core.db import get_db

# Detecta automáticamente DB_MODE
with get_db() as conn:
    cur = conn.cursor()
    # ✅ Sigue usando ? (se convierte a %s automáticamente si es PostgreSQL)
    cur.execute("SELECT * FROM eventos WHERE id = ?", (123,))
    evento = cur.fetchone()
```

---

## 🔄 Migración de Datos

### **SQLite → PostgreSQL**

Si ya tienes datos en `axs_v2.db` o `axs.db`:

```bash
# 1. Configurar PostgreSQL en .env
echo "DB_MODE=postgres" >> .env

# 2. Ejecutar migración
python database/migrate_sqlite_to_pg.py
```

**Proceso:**
1. ✅ Lee todas las tablas de SQLite
2. ✅ Inicializa schema PostgreSQL
3. ✅ Inserta datos con `ON CONFLICT DO NOTHING` (sin duplicados)
4. ✅ Reporta estadísticas

**Salida esperada:**
```
📂 Encontrado: axs_v2.db
✅ Schema PostgreSQL inicializado correctamente
  ✅ entidades: 150 registros migrados
  ✅ eventos: 1203 registros migrados
  ✅ politicas: 12 registros migrados
  ✅ usuarios: 5 registros migrados
  ✅ roles: 4 registros migrados
🎉 Migración completada: 1374 registros totales
```

---

## 🚀 Deployment

### **Streamlit Cloud**

1. Ir a **App settings → Secrets**
2. Agregar:

```toml
DB_MODE = "postgres"
PG_HOST = "db.xxxxxx.supabase.co"
PG_DATABASE = "postgres"
PG_USER = "postgres"
PG_PASSWORD = "tu_password"
PG_PORT = "5432"
```

3. Actualizar `requirements.txt`:

```
psycopg2-binary>=2.9.11
python-dotenv>=1.2.1
```

4. Deploy automático detecta `DB_MODE=postgres` y usa PostgreSQL

### **Docker**

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Instalar dependencias PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Variables de entorno desde .env
ENV DB_MODE=postgres

CMD ["streamlit", "run", "index.py"]
```

---

## 🛠️ Troubleshooting

### **Error: "connection refused"**

**Causa**: PostgreSQL no está corriendo o credenciales incorrectas

**Solución**:
```bash
# Probar conexión
python -c "from database.pg_connection import test_connection; print(test_connection())"

# Si falla, verificar:
# 1. PG_HOST correcto
# 2. Puerto 5432 abierto
# 3. Password correcto
# 4. Database existe
```

### **Error: "relation does not exist"**

**Causa**: Schema no inicializado

**Solución**:
```bash
python -c "from database.pg_connection import init_pg_schema; init_pg_schema()"
```

### **Error: "syntax error near '?'"**

**Causa**: Query SQLite sin convertir a PostgreSQL

**Solución**: Cambiar `?` → `%s`

```python
# ❌ Incorrecto
cur.execute("SELECT * FROM eventos WHERE id = ?", (123,))

# ✅ Correcto
cur.execute("SELECT * FROM eventos WHERE id = %s", (123,))
```

### **Performance lento**

**Causa**: Falta índices o query no optimizada

**Solución**:
```sql
-- Ver queries lentas
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;

-- Crear índice custom
CREATE INDEX idx_custom ON eventos(tipo, timestamp);
```

---

## 📊 Diferencias SQLite vs PostgreSQL

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Placeholder | `?` | `%s` |
| Autoincrement | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| JSON | `TEXT` | `JSONB` |
| Timestamp | `TEXT` | `TIMESTAMPTZ` |
| Insert Ignore | `INSERT OR IGNORE` | `INSERT ... ON CONFLICT DO NOTHING` |
| Concurrent writes | ❌ Lock | ✅ MVCC |

---

## 📝 Ejemplos Completos

### **Registrar Evento con Sentinel**

```python
from database.pg_connection import execute_insert, execute_update

# 1. Crear evento
evento_id = execute_insert("""
    INSERT INTO eventos (tipo, rol, detalle, entidad_id, score, metadata)
    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
    RETURNING id
""", (
    'ingreso',
    'vigilante',
    'Acceso concedido - QR válido',
    100,
    0,
    '{"dispositivo": "caseta-1", "qr_code": "QR123"}'
))

# 2. Actualizar score entidad
execute_update("""
    UPDATE entidades 
    SET score = score + %s,
        ultima_actividad = NOW()
    WHERE id = %s
""", (10, 100))

# 3. Crear insight Sentinel
execute_insert("""
    INSERT INTO sentinel_insights (entidad_id, tipo_insight, descripcion, severidad, metadata)
    VALUES (%s, %s, %s, %s, %s::jsonb)
    RETURNING id
""", (
    100,
    'patron_inusual',
    'Acceso fuera de horario habitual',
    'WARNING',
    '{"horario": "23:45", "promedio": "08:30"}'
))
```

### **Dashboard con Vistas**

```python
from database.pg_connection import execute_query

# Vista: eventos recientes (últimos 7 días)
eventos = execute_query("""
    SELECT * FROM eventos_recientes
    WHERE nivel_riesgo IN ('ALTO', 'CRITICO')
    ORDER BY timestamp DESC
""")

# Vista: top entidades de riesgo
entidades_riesgo = execute_query("""
    SELECT * FROM top_entidades_riesgo
    LIMIT 20
""")

# Streamlit
import streamlit as st

st.dataframe(eventos)
st.dataframe(entidades_riesgo)
```

---

## ✅ Checklist de Migración

- [ ] Instalar `psycopg2-binary` y `python-dotenv`
- [ ] Crear proyecto Supabase (o PostgreSQL local)
- [ ] Configurar `.env` con credenciales
- [ ] Ejecutar `init_pg_schema()`
- [ ] Migrar datos con `migrate_sqlite_to_pg.py` (si aplica)
- [ ] Cambiar `DB_MODE=postgres` en producción
- [ ] Probar todos los módulos
- [ ] Verificar Sentinel™ funciona
- [ ] Configurar backups automáticos (Supabase lo hace)
- [ ] Monitorear performance con `pg_stat_statements`

---

**🎉 Migración Completa - PostgreSQL nativo sin ORM**
