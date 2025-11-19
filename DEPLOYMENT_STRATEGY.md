# 🔄 Estrategia de Deployment: Single-Tenant vs Multi-Tenant

## 📋 Recomendación: Proyectos Separados en Neon

### ✅ Opción Recomendada: Dos Proyectos Independientes

**Ventajas**:
- ✅ No afecta la versión single-tenant en producción
- ✅ Schemas completamente diferentes sin conflictos
- ✅ Permite probar multi-tenant sin riesgo
- ✅ Rollback fácil si hay problemas
- ✅ Ambas versiones pueden coexistir
- ✅ Plan gratuito de Neon permite múltiples proyectos

---

## 🎯 Plan de Deployment Dual

### Proyecto 1: Single-Tenant (EXISTENTE)
**Base de datos**: Neon Project "AX-S-Production-SingleTenant"  
**Branch Git**: `main`  
**Streamlit App**: `https://ax-s-singletenant.streamlit.app`  
**Schema**: Tablas originales sin `msp_id`/`condominio_id`

```toml
# Secrets para Single-Tenant (YA CONFIGURADO)
DB_MODE = "postgres"
PG_HOST = "ep-dry-star-ada71i00-pooler.c-2.us-east-1.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_actual"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

**Estado**: ✅ Operativo, NO TOCAR

---

### Proyecto 2: Multi-Tenant (NUEVO)
**Base de datos**: Neon Project "AX-S-Production-MultiTenant" (CREAR NUEVO)  
**Branch Git**: `feature/multi-tenant-fixes`  
**Streamlit App**: `https://ax-s-multitenant.streamlit.app`  
**Schema**: Tablas nuevas con `msp_id`/`condominio_id`

```toml
# Secrets para Multi-Tenant (NUEVO PROYECTO NEON)
DB_MODE = "postgres"
PG_HOST = "ep-NUEVO-HOST.us-east-1.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "nuevo_password"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

**Estado**: 🔨 Por crear

---

## 🚀 Pasos para Configuración Dual

### Paso 1: Crear Nuevo Proyecto Neon para Multi-Tenant

1. Ve a https://console.neon.tech
2. Click en **"New Project"**
3. Configuración:
   ```
   Project name: AX-S-Production-MultiTenant
   Region: us-east-1 (mismo que single-tenant para baja latencia)
   PostgreSQL version: 16 (última estable)
   ```
4. Click **"Create Project"**
5. Copia el **Connection String** nuevo

**Connection String esperado**:
```
postgresql://neondb_owner:NEW_PASSWORD@ep-NEW-HOST.us-east-1.aws.neon.tech/neondb?sslmode=require
```

---

### Paso 2: Inicializar BD Multi-Tenant

**Localmente** (para probar antes de deploy):

```bash
# 1. Crear archivo de secrets para multi-tenant
cp .streamlit/secrets.toml .streamlit/secrets-multitenant.toml

# 2. Editar con credenciales del NUEVO proyecto Neon
nano .streamlit/secrets-multitenant.toml
```

**Contenido de `secrets-multitenant.toml`**:
```toml
DB_MODE = "postgres"
PG_HOST = "ep-NEW-HOST.us-east-1.aws.neon.tech"  # NUEVO
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "NEW_PASSWORD"  # NUEVO
PG_PORT = "5432"
PG_SSLMODE = "require"
```

```bash
# 3. Renombrar temporalmente para usar nuevas credenciales
mv .streamlit/secrets.toml .streamlit/secrets-singletenant-backup.toml
mv .streamlit/secrets-multitenant.toml .streamlit/secrets.toml

# 4. Inicializar base de datos multi-tenant
python3 init_streamlit_cloud.py

# 5. Restaurar secrets originales
mv .streamlit/secrets.toml .streamlit/secrets-multitenant.toml
mv .streamlit/secrets-singletenant-backup.toml .streamlit/secrets.toml
```

**Salida esperada**:
```
✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE
📋 Datos creados:
   - MSP: MSP-DEMO-001 (Demo Security Services)
   - Condominio: COND-DEMO-001 (Residencial Demo)
```

---

### Paso 3: Deploy Multi-Tenant en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Click **"New app"** (segunda app)
3. Configuración:
   ```
   Repository: B10sp4rt4n/Accesos-Residencial
   Branch: feature/multi-tenant-fixes  ← IMPORTANTE
   Main file: index.py
   ```

4. **App settings** → **Advanced**:
   ```
   Python version: 3.11
   Requirements file: requirements-streamlit.txt
   ```

5. **App settings** → **Secrets** (USA LAS NUEVAS CREDENCIALES):
   ```toml
   DB_MODE = "postgres"
   PG_HOST = "ep-NEW-HOST.us-east-1.aws.neon.tech"
   PG_DATABASE = "neondb"
   PG_USER = "neondb_owner"
   PG_PASSWORD = "NEW_PASSWORD"
   PG_PORT = "5432"
   PG_SSLMODE = "require"
   ```

6. **Custom subdomain** (opcional):
   ```
   ax-s-multitenant
   ```
   URL final: `https://ax-s-multitenant.streamlit.app`

7. Click **"Deploy!"**

---

## 📊 Resultado: Dos Apps Independientes

### App 1: Single-Tenant (Producción Actual)
```
URL: https://ax-s-singletenant.streamlit.app
Branch: main
Neon DB: ep-dry-star-ada71i00-pooler...
Schema: entidades (sin msp_id/condominio_id)
Estado: ✅ Operativo, sin cambios
```

### App 2: Multi-Tenant (Nuevo)
```
URL: https://ax-s-multitenant.streamlit.app
Branch: feature/multi-tenant-fixes
Neon DB: ep-NEW-HOST...
Schema: entidades (con msp_id/condominio_id), msps_exo, condominios_exo
Estado: 🆕 Nueva implementación
```

---

## 🔄 Migración Gradual (Opcional)

Si en el futuro quieres migrar de single a multi-tenant:

### Opción A: Mantener Ambas Versiones
- Clientes antiguos: siguen en single-tenant
- Clientes nuevos: usan multi-tenant
- Sin downtime

### Opción B: Migración Completa
1. **Exportar datos** de single-tenant:
   ```bash
   pg_dump postgresql://user:pass@single-tenant-host/db > backup-single.sql
   ```

2. **Crear script de migración**:
   ```python
   # Agregar msp_id y condominio_id a datos existentes
   # Asignar MSP/Condominio por defecto
   ```

3. **Importar a multi-tenant**:
   ```bash
   psql postgresql://user:pass@multi-tenant-host/db < migrated-data.sql
   ```

4. **Cambiar DNS/URL** cuando esté listo

---

## 💰 Costos (Neon Free Tier)

### Límites Gratuitos por Proyecto
- ✅ **10 proyectos gratuitos** en total
- ✅ **3 GB de almacenamiento** por proyecto
- ✅ **100 horas de compute** por mes
- ✅ **Conexiones**: 100 concurrentes

### Con 2 Proyectos
```
Single-Tenant: 1 proyecto
Multi-Tenant:  1 proyecto
Total usado:   2/10 proyectos (20% del límite)
```

**Costo total**: $0 USD/mes 🎉

---

## ⚠️ Consideraciones Importantes

### 1. NO Mezclar Schemas
- ❌ NO agregar columnas multi-tenant a BD single-tenant
- ❌ NO usar mismo proyecto Neon para ambas versiones
- ✅ Proyectos completamente separados

### 2. Gestión de Secrets
```bash
# Mantener separados
.streamlit/
├── secrets.toml              # Para desarrollo local
├── secrets-singletenant.toml # Backup single-tenant
└── secrets-multitenant.toml  # Backup multi-tenant
```

### 3. Testing
- Probar **localmente** antes de cada deploy
- Verificar conexión a BD correcta
- Confirmar schema correcto

---

## 🎯 Checklist de Setup Dual

### Single-Tenant (Ya Existente)
- [x] Proyecto Neon creado
- [x] App en Streamlit Cloud desplegada
- [x] Secrets configurados
- [x] Schema sin msp_id/condominio_id
- [x] En producción funcionando

### Multi-Tenant (Nuevo)
- [ ] Crear nuevo proyecto Neon
- [ ] Copiar connection string
- [ ] Inicializar BD con `init_streamlit_cloud.py`
- [ ] Verificar tablas: msps_exo, condominios_exo, entidades
- [ ] Deploy en Streamlit Cloud (nueva app)
- [ ] Configurar secrets con nuevas credenciales
- [ ] Probar funcionalidad multi-tenant
- [ ] Confirmar aislamiento de datos

---

## 📞 Soporte

Si tienes dudas durante el proceso:

1. **Verificar conexiones** con script de test
2. **Revisar logs** en Streamlit Cloud
3. **Comparar schemas** entre ambas BDs
4. **Contactar**: @B10sp4rt4n

---

## 🎉 Beneficios de Esta Estrategia

1. ✅ **Sin riesgo**: Single-tenant sigue funcionando
2. ✅ **Testing seguro**: Multi-tenant se prueba aislado
3. ✅ **Rollback fácil**: Solo apagar app multi-tenant
4. ✅ **Costo cero**: Ambas en tier gratuito
5. ✅ **Flexibilidad**: Puedes cambiar entre versiones
6. ✅ **Comparación**: Ambas apps lado a lado

---

**Recomendación Final**: 🎯 **Crear proyecto Neon separado para multi-tenant**

Esto te permite:
- Mantener single-tenant estable
- Experimentar con multi-tenant sin riesgo
- Decidir luego si migrar o mantener ambas

---

**Documento creado**: 19/11/2025  
**Autor**: B10sp4rt4n  
**Versión**: 1.0
