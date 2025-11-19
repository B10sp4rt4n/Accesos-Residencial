# 🚀 AX-S Multi-Tenant - Deploy Rápido en Streamlit Cloud

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## ⚠️ IMPORTANTE: Nueva Base de Datos

Esta es la **versión Multi-Tenant**. Si ya tienes la versión single-tenant:
- ✅ **Crear NUEVO proyecto Neon** para multi-tenant
- ✅ Ver [`DEPLOYMENT_STRATEGY.md`](./DEPLOYMENT_STRATEGY.md)
- ❌ **NO usar misma BD** que single-tenant

---

## 📦 Deploy en 5 Minutos

### 1️⃣ Crear Base de Datos PostgreSQL (GRATIS)

**Opción Neon (Recomendado)**:
1. Ve a https://neon.tech
2. Sign up (gratis, sin tarjeta)
3. Crea proyecto **"AX-S-MultiTenant"** (nuevo proyecto separado)
4. Copia el **Connection String**

### 2️⃣ Deploy en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Login con GitHub
3. Click **"New app"**
4. Configura:
   ```
   Repository: B10sp4rt4n/Accesos-Residencial
   Branch: feature/multi-tenant-fixes
   Main file: index.py
   ```

### 3️⃣ Configurar Secrets

En Streamlit Cloud → **App Settings** → **Secrets**, pega:

```toml
DB_MODE = "postgres"
PG_HOST = "tu-host-neon.aws.neon.tech"
PG_DATABASE = "neondb"
PG_USER = "neondb_owner"
PG_PASSWORD = "tu_password_aqui"
PG_PORT = "5432"
PG_SSLMODE = "require"
```

### 4️⃣ Configurar Advanced Settings

En **Advanced Settings**:
- **Python version**: `3.11`
- **Requirements file**: `requirements-streamlit.txt`

### 5️⃣ Deploy!

Click **"Deploy"** y espera 2-3 minutos.

---

## 🎯 Primera Configuración

Una vez desplegada:

1. **Inicializar BD** (solo primera vez):
   ```bash
   # Localmente con tus credenciales de Neon
   python3 init_streamlit_cloud.py
   ```

2. **O** usa la app directamente:
   - Selecciona rol: **Super Admin**
   - Ve a **Gestión MSPs** → Crea tu MSP
   - Ve a **Gestión Condominios** → Crea tu condominio

---

## 📚 Documentación Completa

Ver [`STREAMLIT_DEPLOYMENT.md`](./STREAMLIT_DEPLOYMENT.md) para:
- Troubleshooting detallado
- Optimizaciones de producción
- Configuración de dominio personalizado
- Monitoreo y logs
- Seguridad

---

## ✅ Checklist Rápido

- [ ] Base de datos PostgreSQL creada
- [ ] Secrets configurados en Streamlit Cloud
- [ ] App desplegada sin errores
- [ ] BD inicializada (tablas creadas)
- [ ] MSP creado
- [ ] Condominio creado
- [ ] Primera entidad registrada

---

## 🆘 Problemas Comunes

**Error: "Connection refused"**
→ Verifica `PG_SSLMODE = "require"` en secrets

**Error: "Table does not exist"**
→ Ejecuta `init_streamlit_cloud.py` localmente

**App lenta**
→ Neon gratis tiene límites, considera upgrade

---

## 📞 Soporte

- **GitHub**: [@B10sp4rt4n](https://github.com/B10sp4rt4n)
- **Issues**: [Reportar problema](https://github.com/B10sp4rt4n/Accesos-Residencial/issues)

---

**Versión**: 2.0.0-multitenant  
**Última actualización**: 19/11/2025
