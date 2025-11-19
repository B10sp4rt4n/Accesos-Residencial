# 🚀 AX-S - Deployment a Streamlit Cloud + PostgreSQL

## 📋 Configuración Streamlit Cloud

### 1. **Secrets (PostgreSQL - Neon)**

En **Streamlit Cloud → App Settings → Secrets**, agregar:

```toml
# PostgreSQL (Neon)
DB_MODE = "postgres"
DATABASE_URL = "postgresql://neondb_owner:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# O variables separadas:
PG_HOST = "ep-xxxxx.us-east-2.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"
```

### 2. **Configuración Neon**

1. Ir a [neon.tech](https://neon.tech)
2. Crear nuevo proyecto
3. **Dashboard → Connection Details**
4. Copiar **Connection String**:
   ```
   postgresql://neondb_owner:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### 3. **Inicializar Schema en Neon**

**Opción A: SQL Editor en Neon**

1. Ir a **SQL Editor** en Neon Dashboard
2. Copiar contenido de `database/schema_exo.sql`
3. Ejecutar

**Opción B: Desde local con psql**

```bash
# Usando DATABASE_URL
psql "postgresql://neondb_owner:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require" < database/schema_exo.sql

# O con Python
python init_db_postgresql.py
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
