# 🔧 Cambios Requeridos en la Base de Datos PostgreSQL Externa

## 📌 PROBLEMA IDENTIFICADO

El código en `modulos/` consulta la tabla `eventos` que **NO existe** en el esquema PostgreSQL (`schema_exo.sql`).

En PostgreSQL solo existe la tabla `ledger_exo` con columnas diferentes.

**Error producido:**
```
UndefinedColumn: column "evento_id" does not exist
UndefinedColumn: column "tipo_evento" does not exist
```

---

## ✅ SOLUCIÓN IMPLEMENTADA

Se creó una **vista SQL** llamada `eventos` que mapea automáticamente `ledger_exo` a la estructura esperada por el código legacy.

---

## 🚀 PASOS PARA APLICAR EN LA BASE DE DATOS EXTERNA

### **Opción 1: Ejecutar archivo SQL completo** (Recomendado)

```bash
psql -h TU_HOST -U TU_USUARIO -d TU_DATABASE -f database/fix_eventos_view.sql
```

Reemplaza:
- `TU_HOST`: hostname de tu PostgreSQL (ej: `db.neon.tech`)
- `TU_USUARIO`: usuario PostgreSQL (ej: `postgres`)
- `TU_DATABASE`: nombre de la base de datos (ej: `accesos_residencial`)

---

### **Opción 2: Copiar y pegar en consola SQL**

1. Conéctate a tu PostgreSQL (Neon, Supabase, etc.)
2. Abre el **SQL Editor** o consola SQL
3. Copia y pega este comando:

```sql
CREATE OR REPLACE VIEW eventos AS
SELECT 
    l.ledger_id AS evento_id,
    l.msp_id,
    l.condominio_id,
    l.entidad_id,
    l.accion AS tipo_evento,
    l.detalle AS metadata,
    NULL::VARCHAR(100) AS evidencia_id,
    ''::VARCHAR(100) AS hash_actual,
    l.timestamp AS timestamp_servidor,
    l.timestamp AS timestamp_cliente,
    l.usuario_id AS actor,
    l.ip_origen AS dispositivo,
    l.ip_origen AS origen,
    l.user_agent AS contexto,
    NULL::VARCHAR(200) AS recibo_recordia
FROM ledger_exo l;
```

4. Click en **Run** o **Execute**

---

## ✅ VERIFICAR QUE FUNCIONÓ

Ejecuta esta query:

```sql
SELECT COUNT(*) AS total_eventos FROM eventos;
```

Deberías ver:
- ✅ Sin errores
- ✅ Un número (puede ser 0 si aún no hay datos)

---

## 📊 MAPEO DE COLUMNAS

| **Columna esperada (eventos)** | **Columna real (ledger_exo)** | **Tipo** |
|-------------------------------|-------------------------------|----------|
| `evento_id` | `ledger_id` | VARCHAR |
| `tipo_evento` | `accion` | VARCHAR |
| `metadata` | `detalle` | TEXT |
| `actor` | `usuario_id` | VARCHAR |
| `dispositivo` | `ip_origen` | VARCHAR |
| `timestamp_servidor` | `timestamp` | TIMESTAMPTZ |
| `hash_actual` | `''` (vacío) | VARCHAR |
| `evidencia_id` | `NULL` | VARCHAR |

---

## 🔄 MÓDULOS AFECTADOS (YA CORREGIDOS)

Los siguientes módulos consultaban `eventos` y ahora funcionarán con la vista:

- ✅ `modulos/eventos.py` - **Actualizado a versión PRO con ledger_exo**
- ✅ `modulos/dashboard.py` - Funcionará con vista eventos
- ✅ `modulos/analitica.py` - Funcionará con vista eventos
- ✅ `modulos/vigilancia.py` - Funcionará con vista eventos
- ✅ `modulos/accesos.py` - Funcionará con vista eventos

---

## 📝 ARCHIVOS MODIFICADOS EN ESTE REPOSITORIO

### 1. `database/schema_exo.sql`
- ✅ Se agregó la vista `eventos` en SECCIÓN 8

### 2. `modulos/eventos.py`
- ✅ Se reemplazó con versión PRO que usa `ledger_exo` directamente
- ✅ Incluye jerarquía AUP-EXO (filtrado por MSP/Condominio)
- ✅ Filtros avanzados: entidad, tipo_evento, usuario, fechas
- ✅ UI moderna con sidebar y detalle JSON

### 3. `database/fix_eventos_view.sql` (NUEVO)
- ✅ Script SQL para ejecutar en PostgreSQL externo
- ✅ Crea la vista `eventos` de compatibilidad

---

## 🎯 SIGUIENTE PASO

**Ejecuta el script SQL en tu base de datos PostgreSQL externa:**

```bash
psql -h TU_HOST -U TU_USUARIO -d TU_DATABASE -f database/fix_eventos_view.sql
```

O copia/pega el contenido en tu consola SQL.

---

## ❓ PREGUNTAS FRECUENTES

### ¿Por qué usar una vista y no crear la tabla eventos?

- **Evita duplicación**: `ledger_exo` ya tiene todos los eventos
- **Mantiene auditoría**: Un solo lugar de verdad
- **Compatibilidad**: El código legacy sigue funcionando
- **Actualización automática**: La vista refleja cambios en `ledger_exo` al instante

### ¿Qué pasa con el hash_actual?

Por ahora se devuelve vacío (`''`). Si necesitas hashes:
1. Agregar columna `hash` a `ledger_exo`
2. Actualizar la vista para mapear `l.hash AS hash_actual`

### ¿Debo modificar schema_exo.sql completo?

No necesariamente. Puedes:
- **Solo ejecutar** `fix_eventos_view.sql` (más rápido)
- **O reemplazar** `schema_exo.sql` completo (si estás migrando)

---

## 📞 SOPORTE

Si encuentras errores:
1. Verifica que la tabla `ledger_exo` exista
2. Revisa que tengas permisos para crear vistas
3. Confirma la conexión a PostgreSQL en `core/db_exo.py`
