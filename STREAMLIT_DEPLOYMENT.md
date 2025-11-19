# 🚀 Deployment a Streamlit Cloud - AX-S Multi-Tenant

## ⚠️ IMPORTANTE: Versión Multi-Tenant

Esta guía es para la **versión Multi-Tenant** del sistema. Si ya tienes la versión **Single-Tenant** desplegada:

- ✅ **Recomendado**: Crear un **nuevo proyecto Neon** separado para multi-tenant
- ✅ Ver [`DEPLOYMENT_STRATEGY.md`](./DEPLOYMENT_STRATEGY.md) para estrategia dual
- ❌ **NO** usar la misma base de datos que single-tenant (schemas diferentes)

---

## 📋 Pre-requisitos

1. **Cuenta en Streamlit Cloud**: https://share.streamlit.io
2. **Base de datos PostgreSQL NUEVA** (recomendado: [Neon](https://neon.tech) - gratis)
3. **Repositorio en GitHub**: Ya configurado en `B10sp4rt4n/Accesos-Residencial`

---

## 🎯 Paso 1: Preparar Base de Datos PostgreSQL

### ⚠️ Si ya tienes Single-Tenant en Producción

**CREAR NUEVO PROYECTO NEON** para multi-tenant:
- No usar la misma BD que single-tenant
- Schemas son diferentes (multi-tenant tiene `msp_id`/`condominio_id`)
- Ver [`DEPLOYMENT_STRATEGY.md`](./DEPLOYMENT_STRATEGY.md) para detalles

### Opción A: Neon (Recomendado - Gratis)

1. Ve a https://neon.tech
2. Crea una cuenta gratuita
3. Crea un nuevo proyecto llamado **"AX-S-MultiTenant"** (nombre diferente si ya tienes single-tenant)
4. Copia la **Connection String** que se ve así:
   ```
   postgresql://user:password@ep-xxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### Opción B: Otros Proveedores

- **Supabase**: https://supabase.com (gratis)
- **ElephantSQL**: https://www.elephantsql.com (gratis hasta 20MB)
- **Railway**: https://railway.app (gratis con límites)

---

## 🎯 Paso 2: Inicializar la Base de Datos

Una vez que tengas tu PostgreSQL, necesitas crear las tablas. Ejecuta esto **localmente** primero:

```bash
# 1. Clonar el repositorio (si no lo tienes)
git clone https://github.com/B10sp4rt4n/Accesos-Residencial.git
cd Accesos-Residencial

# 2. Checkout a la rama multi-tenant
git checkout feature/multi-tenant-fixes

# 3. Configurar variables de entorno
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 4. Editar .streamlit/secrets.toml con tus credenciales de Neon
nano .streamlit/secrets.toml
```

**Contenido de `.streamlit/secrets.toml`**:
```toml
DB_MODE = "postgres"
PG_HOST = "ep-xxxxx.us-east-1.aws.neon.tech"  # Tu host de Neon
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

```bash
# 5. Instalar dependencias
pip install -r requirements-streamlit.txt

# 6. Inicializar base de datos
python3 init_db_exo.py
```

**Salida esperada**:
```
✅ Tablas creadas correctamente
✅ MSP de ejemplo creado
✅ Condominio de ejemplo creado
✅ Base de datos lista para producción
```

---

## 🎯 Paso 3: Deploy en Streamlit Cloud

### 3.1 Conectar Repositorio

1. Ve a https://share.streamlit.io
2. Click en **"New app"**
3. Conecta tu cuenta de GitHub
4. Selecciona:
   - **Repository**: `B10sp4rt4n/Accesos-Residencial`
   - **Branch**: `feature/multi-tenant-fixes`
   - **Main file path**: `index.py`

### 3.2 Configurar Secrets

1. En Streamlit Cloud, ve a **App settings** → **Secrets**
2. Pega el siguiente contenido (reemplaza con tus datos de Neon):

```toml
# PostgreSQL Configuration (Neon)
DB_MODE = "postgres"
PG_HOST = "ep-dry-star-ada71i00-pooler.c-2.us-east-1.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "TU_PASSWORD_NEON_AQUI"
PG_PORT = "5432"
PG_SSLMODE = "require"

# Opcionalmente, puedes usar DATABASE_URL en lugar de los campos separados
# DATABASE_URL = "postgresql://user:password@host/database?sslmode=require"
```

### 3.3 Configuraciones Avanzadas (Opcional)

En **App settings** → **Advanced settings**:

- **Python version**: 3.11
- **Requirements file**: `requirements-streamlit.txt`
- **Packages file**: `packages.txt`

### 3.4 Deploy

1. Click en **"Deploy!"**
2. Espera 2-3 minutos mientras se construye
3. Tu app estará disponible en: `https://tu-app.streamlit.app`

---

## 🎯 Paso 4: Configuración Inicial en Producción

Una vez desplegada la app:

### 4.1 Crear Usuario Super Admin

1. Abre la app en `https://tu-app.streamlit.app`
2. En el sidebar, selecciona:
   - **Rol**: Super Admin
   - Deja MSP y Condominio vacíos
3. Verás el panel de confirmación: ⚠️ ⚠️

### 4.2 Crear tu Primer MSP

1. Ve a **"Gestión MSPs"** en el menú
2. Click en tab **"➕ Nuevo MSP"**
3. Llena el formulario:
   ```
   ID del MSP: MSP-001
   Nombre: Mi Empresa de Seguridad
   Email: contacto@miempresa.com
   Teléfono: +52 55 1234 5678
   ```
4. Click **"✅ Crear MSP"**

### 4.3 Crear tu Primer Condominio

1. Ve a **"Gestión Condominios"**
2. Click en tab **"➕ Nuevo Condominio"**
3. Llena el formulario:
   ```
   ID del Condominio: COND-001
   Nombre: Residencial Las Palmas
   MSP: Selecciona el MSP que creaste
   Ciudad: Ciudad de México
   ```
4. Click **"✅ Crear Condominio"**

### 4.4 Seleccionar Contexto

En el sidebar:
1. Selecciona el MSP creado
2. Selecciona el Condominio creado
3. Verás: ✅ ✅ (contexto confirmado)

### 4.5 Registrar Primera Entidad

1. Ve a **"Registro de Entidades"**
2. Registra un residente, visitante o proveedor
3. Verifica que aparezca en **"Consultar Entidades"**

---

## 🔧 Troubleshooting

### Problema: "Connection refused" o error de BD

**Solución**:
1. Verifica que los secrets estén correctamente configurados
2. Asegúrate de que `PG_SSLMODE = "require"`
3. Verifica que el host de Neon sea correcto (debe incluir `-pooler`)

### Problema: "No module named 'psycopg2'"

**Solución**:
1. Verifica que `requirements-streamlit.txt` esté configurado como requirements file
2. Asegúrate de que incluya `psycopg2-binary==2.9.9`

### Problema: "Table does not exist"

**Solución**:
1. Ejecuta `init_db_exo.py` localmente apuntando a tu BD de producción
2. O ejecuta manualmente los scripts SQL en Neon Console:
   - Abre Neon Console
   - Ve a SQL Editor
   - Copia el contenido de `database/schema_exo.sql`
   - Ejecuta

### Problema: App lenta o timeout

**Solución**:
1. Neon gratis tiene límites de conexiones (pool pequeño)
2. Considera agregar `@st.cache_data` a queries frecuentes
3. Upgrade a Neon Pro si necesitas más conexiones

---

## 📊 Monitoreo y Logs

### Ver Logs en Streamlit Cloud

1. Ve a tu app en Streamlit Cloud
2. Click en **"Manage app"**
3. Click en **"Logs"**
4. Verás los logs en tiempo real

### Logs Importantes

```
✅ Conectado a PostgreSQL via Streamlit secrets
✅ Base de datos operativa
```

Si ves estos mensajes, la conexión está funcionando correctamente.

---

## 🔒 Seguridad en Producción

### 1. Secrets Management

- ✅ **NUNCA** commits secrets.toml al repositorio
- ✅ Usa solo Streamlit Cloud Secrets para producción
- ✅ Rota las contraseñas periódicamente

### 2. Base de Datos

- ✅ Habilita SSL/TLS (`sslmode=require`)
- ✅ Usa passwords fuertes (generadas)
- ✅ Limita acceso por IP (si es posible)

### 3. Backups

Neon hace backups automáticos, pero considera:
```bash
# Backup manual periódico
pg_dump postgresql://user:pass@host/db > backup-$(date +%Y%m%d).sql
```

---

## 🚀 Optimizaciones para Producción

### 1. Caché de Queries

Agrega en `index.py`:

```python
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_msps_cached():
    return get_msps_list()

@st.cache_data(ttl=300)
def get_condominios_cached(msp_id):
    return get_condominios_by_msp(msp_id)
```

### 2. Connection Pooling

Ya está implementado en `core/db.py` con context managers.

### 3. Índices en PostgreSQL

```sql
-- Agregar índices para queries frecuentes
CREATE INDEX idx_entidades_msp ON entidades(msp_id);
CREATE INDEX idx_entidades_condo ON entidades(condominio_id);
CREATE INDEX idx_entidades_identificacion ON entidades(identificacion);
```

---

## 📱 Configuración de Dominio Personalizado

Si quieres usar tu propio dominio (ej: `app.miseguridad.com`):

1. En Streamlit Cloud, ve a **Settings** → **General**
2. En **Custom subdomain**, ingresa: `ax-s-miseguridad`
3. Tu URL será: `https://ax-s-miseguridad.streamlit.app`

Para dominio completo personalizado, necesitas **Streamlit for Teams** (pago).

---

## 🎉 Checklist de Deploy Exitoso

- [ ] Base de datos PostgreSQL creada (Neon/Supabase)
- [ ] Secrets configurados en Streamlit Cloud
- [ ] App desplegada sin errores
- [ ] Logs muestran "✅ Conectado a PostgreSQL"
- [ ] Tablas creadas (`msps_exo`, `condominios_exo`, `entidades`)
- [ ] Primer MSP creado
- [ ] Primer Condominio creado
- [ ] Contexto seleccionado (✅ ✅)
- [ ] Primera entidad registrada
- [ ] Filtrado multi-tenant funcionando

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** en Streamlit Cloud
2. **Verifica secrets** (typos comunes: espacios extra, quotes incorrectas)
3. **Prueba localmente** primero con los mismos secrets
4. **Contacta**: @B10sp4rt4n en GitHub

---

## 🔗 URLs Importantes

- **App en Streamlit Cloud**: https://share.streamlit.io
- **Neon Console**: https://console.neon.tech
- **Repositorio**: https://github.com/B10sp4rt4n/Accesos-Residencial
- **Documentación**: Ver `MULTITENANT_IMPLEMENTATION.md`

---

**Última actualización**: 19 de Noviembre, 2025  
**Versión**: 2.0.0-multitenant  
**Autor**: B10sp4rt4n
