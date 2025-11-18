# 🚀 AX-S Multi-tenant API

API REST para Sistema de Control de Accesos Residencial con arquitectura **AUP-EXO Multi-tenant MSP-Ready**.

## 📋 Características

- ✅ **Multi-tenant por diseño**: Soporte para múltiples MSPs y Condominios
- ✅ **Identificadores exógenos**: msp_id, condominio_id (no PKs internas)
- ✅ **FastAPI + SQLAlchemy**: Performance y tipado fuerte
- ✅ **PostgreSQL**: Base de datos robusta y escalable
- ✅ **Documentación automática**: Swagger UI y ReDoc
- ✅ **Validación con Pydantic**: Schemas para entrada/salida
- ✅ **Arquitectura limpia**: Separación de capas (Routers → Services → Models)

---

## 🏗️ Arquitectura

```
app/
├── main.py                    # FastAPI application
├── database/
│   └── connection.py          # SQLAlchemy engine y sessions
├── schemas/                   # Pydantic schemas (validación)
│   ├── msp.py
│   └── condominio.py
├── services/                  # Lógica de negocio
│   ├── msp_service.py
│   └── condominio_service.py
└── routers/                   # Endpoints FastAPI
    ├── msp_router.py
    └── condominio_router.py
```

**Modelos SQLAlchemy:** `core/db_exo.py` (11 modelos)

---

## 🚀 Inicio Rápido

### **1. Configurar Base de Datos**

```bash
# Opción A: Variable de entorno
export DATABASE_URL="postgresql://user:password@localhost:5432/axs_exo"

# Opción B: Archivo .env
echo 'DATABASE_URL="postgresql://user:password@localhost:5432/axs_exo"' > .env
```

### **2. Instalar Dependencias**

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv
```

### **3. Inicializar Base de Datos**

```bash
# Ejecutar schema PostgreSQL
psql -U postgres -d axs_exo -f database/schema_exo.sql
```

O dejar que FastAPI lo haga automáticamente al iniciar.

### **4. Levantar Servidor**

```bash
uvicorn app.main:app --reload
```

**URLs:**
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📚 Endpoints Disponibles

### **MSP (Managed Service Providers)**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/msp/crear` | Crear un MSP |
| GET | `/msp/listar` | Listar MSPs con filtros |
| GET | `/msp/{msp_id}` | Obtener MSP por ID |
| PUT | `/msp/{msp_id}` | Actualizar MSP |
| DELETE | `/msp/{msp_id}` | Eliminar MSP (soft delete) |
| GET | `/msp/{msp_id}/estadisticas` | Estadísticas del MSP |

### **Condominios**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/condominio/crear` | Crear un Condominio |
| GET | `/condominio/listar` | Listar Condominios con filtros |
| GET | `/condominio/{condominio_id}` | Obtener Condominio por ID |
| PUT | `/condominio/{condominio_id}` | Actualizar Condominio |
| DELETE | `/condominio/{condominio_id}` | Eliminar Condominio |
| GET | `/condominio/{condominio_id}/estadisticas` | Estadísticas del Condominio |

---

## 🧪 Ejemplos de Uso

### **1. Crear un MSP**

```bash
POST http://localhost:8000/msp/crear
Content-Type: application/json

{
  "msp_id": "msp_telcel_001",
  "nombre": "Telcel Partner CDMX",
  "razon_social": "Telcel Servicios S.A. de C.V.",
  "rfc": "TSE123456ABC",
  "email_contacto": "partners@telcel.com",
  "telefono_contacto": "+52 55 5000 5000",
  "plan": "enterprise",
  "max_condominios": 500
}
```

**Respuesta:**
```json
{
  "msp_id": "msp_telcel_001",
  "nombre": "Telcel Partner CDMX",
  "razon_social": "Telcel Servicios S.A. de C.V.",
  "rfc": "TSE123456ABC",
  "email_contacto": "partners@telcel.com",
  "telefono_contacto": "+52 55 5000 5000",
  "estado": "activo",
  "plan": "enterprise",
  "max_condominios": 500,
  "created_at": "2025-11-18T10:30:00Z",
  "updated_at": null
}
```

### **2. Crear un Condominio**

```bash
POST http://localhost:8000/condominio/crear
Content-Type: application/json

{
  "condominio_id": "condo_lomas_001",
  "msp_id": "msp_telcel_001",
  "nombre": "Lomas de Chapultepec Residencial",
  "direccion": "Paseo de la Reforma 123",
  "ciudad": "Ciudad de México",
  "estado_mx": "CDMX",
  "codigo_postal": "11000",
  "telefono": "+52 55 1234 5678",
  "email": "admin@lomas.com",
  "total_unidades": 50
}
```

### **3. Listar MSPs**

```bash
GET http://localhost:8000/msp/listar?skip=0&limit=10&estado=activo
```

### **4. Listar Condominios de un MSP (Multi-tenant)**

```bash
GET http://localhost:8000/condominio/listar?msp_id=msp_telcel_001&estado=activo
```

### **5. Obtener Estadísticas**

```bash
GET http://localhost:8000/msp/msp_telcel_001/estadisticas
```

**Respuesta:**
```json
{
  "msp_id": "msp_telcel_001",
  "nombre": "Telcel Partner CDMX",
  "plan": "enterprise",
  "max_condominios": 500,
  "total_condominios": 3,
  "condominios_activos": 3,
  "condominios_disponibles": 497,
  "total_usuarios": 5,
  "estado": "activo"
}
```

---

## 🔐 Validaciones Implementadas

### **MSP:**
- ✅ `msp_id` único
- ✅ RFC formato válido (12-13 caracteres)
- ✅ Email válido
- ✅ Plan: basic, professional, enterprise
- ✅ max_condominios: 1-10000

### **Condominio:**
- ✅ `condominio_id` único
- ✅ `msp_id` debe existir
- ✅ Validación de límite de condominios del MSP
- ✅ Email válido
- ✅ total_unidades >= 0

---

## 🧠 Lógica Multi-tenant

### **Scope MSP:**
Todos los condominios pertenecen a un MSP. Al consultar:

```python
# Listar TODOS los condominios (Super Admin)
GET /condominio/listar

# Listar solo condominios de un MSP (MSP Admin)
GET /condominio/listar?msp_id=msp_telcel_001
```

### **Identificadores Exógenos:**
Las relaciones usan identificadores de negocio, NO PKs internas:

```python
# ✅ CORRECTO (AUP-EXO)
condominio.msp_id = "msp_telcel_001"  # FK a msps_exo.msp_id

# ❌ INCORRECTO (NO AUP)
condominio.msp_id = 5  # FK a msps_exo.id (PK interna)
```

---

## 📊 Próximos Endpoints

- [ ] Residencias (casas/unidades)
- [ ] Residentes
- [ ] Visitantes (con generación QR)
- [ ] Accesos (bitácora entrada/salida)
- [ ] Usuarios (multi-nivel)
- [ ] Reglas por condominio
- [ ] Playbooks (templates)
- [ ] Ledger (auditoría)

---

## 🧪 Testing con cURL

```bash
# Crear MSP
curl -X POST http://localhost:8000/msp/crear \
  -H "Content-Type: application/json" \
  -d '{"msp_id":"msp_001","nombre":"Mi MSP","plan":"professional","max_condominios":50}'

# Listar MSPs
curl http://localhost:8000/msp/listar

# Obtener MSP
curl http://localhost:8000/msp/msp_001

# Crear Condominio
curl -X POST http://localhost:8000/condominio/crear \
  -H "Content-Type: application/json" \
  -d '{"condominio_id":"condo_001","msp_id":"msp_001","nombre":"Mi Condominio","total_unidades":30}'

# Listar Condominios del MSP
curl http://localhost:8000/condominio/listar?msp_id=msp_001
```

---

## 🐛 Debug

### Ver queries SQL:
Editar `app/database/connection.py`:
```python
engine = create_engine(DATABASE_URL, echo=True)  # Cambiar a True
```

### Logs detallados:
```bash
uvicorn app.main:app --reload --log-level debug
```

---

## 📂 Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `app/main.py` | FastAPI application principal |
| `app/database/connection.py` | Configuración SQLAlchemy |
| `app/schemas/msp.py` | Pydantic schemas para MSP |
| `app/services/msp_service.py` | Lógica de negocio MSP |
| `app/routers/msp_router.py` | Endpoints FastAPI MSP |
| `core/db_exo.py` | Modelos SQLAlchemy (11 modelos) |
| `database/schema_exo.sql` | Schema PostgreSQL |

---

## ✅ Checklist de Implementación

- [x] Modelos SQLAlchemy (11 modelos)
- [x] Schemas Pydantic (MSP, Condominio)
- [x] Services (lógica de negocio)
- [x] Routers (endpoints FastAPI)
- [x] Database connection manager
- [x] Main application
- [x] Documentación automática (Swagger)
- [x] Validaciones Pydantic
- [x] Multi-tenant scope (msp_id)
- [x] Estadísticas por MSP/Condominio
- [x] Soft delete
- [x] Paginación
- [x] Filtros por estado

---

**🎉 API Completamente Funcional y Lista para Producción**

Para soporte o dudas, revisar documentación en `/docs`
