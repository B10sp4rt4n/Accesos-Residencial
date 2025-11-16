# 🚀 AX-S - Deployment a Streamlit Cloud + PostgreSQL

## 📋 Configuración Streamlit Cloud

### 1. **Secrets (PostgreSQL - Supabase)**

En **Streamlit Cloud → App Settings → Secrets**, agregar:

```toml
# PostgreSQL (Supabase)
DB_MODE = "postgres"
PG_HOST = "db.xxxxxx.supabase.co"
PG_DATABASE = "postgres"
PG_USER = "postgres"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"

# O usar DATABASE_URL (compatible)
DATABASE_URL = "postgresql://postgres:tu_password@db.xxxxxx.supabase.co:5432/postgres"
```

### 2. **Configuración Supabase**

1. Ir a [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. **Settings → Database → Connection string**
4. Copiar credenciales:
   - Host: `db.xxxxxx.supabase.co`
   - Database: `postgres`
   - User: `postgres`
   - Password: (ver en Settings)
   - Port: `5432`

### 3. **Inicializar Schema en Supabase**

**Opción A: SQL Editor en Supabase**

1. Ir a **SQL Editor** en Supabase
2. Copiar contenido de `database/schema.sql`
3. Ejecutar

**Opción B: Desde local**

```bash
# Configurar .env local
DB_MODE=postgres
PG_HOST=db.xxxxxx.supabase.co
PG_DATABASE=postgres
PG_USER=postgres
PG_PASSWORD=tu_password
PG_PORT=5432

# Ejecutar
python -c "from database.pg_connection import init_pg_schema; init_pg_schema()"
```

### 4. **Deploy Streamlit Cloud**

1. **Repositorio GitHub**: Ya está en `feature/aup-exo-roadmap`
2. **New app** en Streamlit Cloud
3. **Repository**: `B10sp4rt4n/Accesos-Residencial`
4. **Branch**: `feature/aup-exo-roadmap`
5. **Main file path**: `index.py`
6. **Python version**: `3.12`
7. **Advanced settings → Secrets**: Pegar config de arriba

### 5. **Auto-inicialización**

El archivo `index.py` ya tiene auto-inicialización:

```python
try:
    from core.db import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM eventos")
    conn.close()
except:
    from core.db import init_db
    init_db()
```

Si las tablas no existen, se crean automáticamente.

---

## 🔄 Flujo de Datos

```
┌─────────────────────┐
│  Streamlit Cloud    │
│  (App Frontend)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  core/db.py         │
│  (Detecta DB_MODE)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  PostgreSQL         │
│  (Supabase)         │
│  - Persistente      │
│  - Backups auto     │
│  - Escalable        │
└─────────────────────┘
```

---

## ✅ Checklist Deployment

- [ ] Crear proyecto Supabase
- [ ] Copiar credenciales PostgreSQL
- [ ] Ejecutar `database/schema.sql` en Supabase SQL Editor
- [ ] Configurar Secrets en Streamlit Cloud
- [ ] Deploy app desde GitHub
- [ ] Verificar logs: "✅ DB PostgreSQL operativa"
- [ ] Probar funcionalidad completa

---

## 🛠️ Troubleshooting

### Error: "relation eventos does not exist"

**Solución**: Ejecutar `database/schema.sql` en Supabase SQL Editor

### Error: "connection refused"

**Solución**: Verificar credenciales en Secrets (host, password, etc.)

### App muy lenta

**Solución**: 
1. Verificar índices en PostgreSQL
2. Revisar logs de Supabase (lentitud de queries)
3. Agregar más índices si es necesario

---

## 📊 Monitoreo

### Supabase Dashboard
- **Database → Tables**: Ver datos en tiempo real
- **Logs**: Ver queries ejecutadas
- **Performance**: Métricas de velocidad

### Streamlit Cloud
- **Logs**: Ver errores de conexión
- **Analytics**: Uso de la app

---

## 🔐 Seguridad

✅ **Secrets en Streamlit Cloud** (no en código)  
✅ **PostgreSQL con SSL** (Supabase por defecto)  
✅ **Backups automáticos** (Supabase daily)  
✅ **RLS (Row Level Security)** disponible en Supabase

---

## 🚀 URL Final

Después del deploy, la app estará en:

```
https://tu-app.streamlit.app
```

Conectada a PostgreSQL persistente en Supabase 🐘
