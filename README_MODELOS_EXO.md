# 🧱 Modelos SQLAlchemy AUP-EXO

## 📋 Resumen

Modelos SQLAlchemy 100% fieles al schema PostgreSQL `database/schema_exo.sql`.

**Filosofía AUP-EXO:**
- ✅ Identificadores exógenos (`msp_id`, `condominio_id`, NO PKs internas)
- ✅ FKs apuntan a identificadores de negocio
- ✅ Multi-tenant por diseño (scope MSP)
- ✅ Jerarquía: Super Admin > MSP > Condominio > Local

---

## 🗃️ Modelos Disponibles

### **1. RolExo** - Roles Jerárquicos
```python
from core.db_exo import RolExo

# 4 niveles:
# 1: DS (Dominio Superior - Super Admin)
# 2: DD (Dominio Delegado - MSP Admin)
# 3: SE (Subdominio Específico - Condominio Admin)
# 4: NO (Nodo Operativo - Admin Local)
```

### **2. MSPExo** - Managed Service Providers
```python
from core.db_exo import MSPExo

msp = MSPExo(
    msp_id="msp_telcel_001",  # Identificador exógeno
    nombre="Telcel Partner CDMX",
    plan="enterprise",        # basic, professional, enterprise
    max_condominios=500
)
```

### **3. CondominioExo** - Condominios
```python
from core.db_exo import CondominioExo

condo = CondominioExo(
    condominio_id="condo_lomas_001",
    msp_id="msp_telcel_001",  # FK exógeno (NO PK interna)
    nombre="Lomas Residencial",
    total_unidades=50
)
```

### **4. UsuarioExo** - Usuarios Multi-nivel
```python
from core.db_exo import UsuarioExo

# Super Admin: msp_id=NULL, condominio_id=NULL
super_admin = UsuarioExo(
    usuario_id="user_superadmin_001",
    rol_id=1,
    msp_id=None,
    condominio_id=None
)

# MSP Admin: msp_id=valor, condominio_id=NULL
msp_admin = UsuarioExo(
    usuario_id="user_msp_001",
    rol_id=2,
    msp_id="msp_telcel_001",
    condominio_id=None
)

# Condominio Admin: ambos con valor
condo_admin = UsuarioExo(
    usuario_id="user_condo_001",
    rol_id=3,
    msp_id="msp_telcel_001",
    condominio_id="condo_lomas_001"
)
```

### **5. ResidenciaExo** - Unidades Habitacionales
```python
from core.db_exo import ResidenciaExo

residencia = ResidenciaExo(
    residencia_id="res_lomas_010",
    condominio_id="condo_lomas_001",
    numero="Casa 10",
    propietario="María González"
)
```

### **6. ResidenteExo** - Personas que Habitan
```python
from core.db_exo import ResidenteExo

residente = ResidenteExo(
    residente_id="res_lomas_010_001",
    residencia_id="res_lomas_010",
    nombre="Carlos Martínez",
    tipo="residente"  # residente, inquilino, familiar
)
```

### **7. VisitanteExo** - Visitas con QR
```python
from core.db_exo import VisitanteExo
from datetime import datetime, timedelta

visitante = VisitanteExo(
    visitante_id="vis_20251118_001",
    condominio_id="condo_lomas_001",
    residencia_id="res_lomas_010",
    nombre="Juan Pérez - Plomero",
    tipo_visita="proveedor",
    qr_code="QR_20251118_ABCD1234",
    fecha_expiracion=datetime.now() + timedelta(hours=24),
    estado="activo"
)
```

### **8. AccesoExo** - Bitácora de Entradas/Salidas
```python
from core.db_exo import AccesoExo

acceso = AccesoExo(
    acceso_id="acc_20251118_001",
    visitante_id="vis_20251118_001",
    condominio_id="condo_lomas_001",
    tipo_acceso="entrada",     # entrada, salida
    metodo="qr",               # qr, manual, placa, facial
    resultado="permitido"      # permitido, denegado
)
```

### **9. ReglaExo** - Reglas por Condominio
```python
from core.db_exo import ReglaExo

regla = ReglaExo(
    regla_id="regla_horario_001",
    condominio_id="condo_lomas_001",
    regla_nombre="Horario Nocturno",
    regla_tipo="horario",
    regla_valor='{"inicio": "22:00", "fin": "06:00"}'
)
```

### **10. PlaybookExo** - Plantillas por Vertical
```python
from core.db_exo import PlaybookExo

playbook = PlaybookExo(
    playbook_id="pb_residencial_001",
    nombre="Residencial Estándar",
    vertical="residencial",  # residencial, corporativo, industrial
    configuracion_json='{"max_visitantes_dia": 10}'
)
```

### **11. LedgerExo** - Auditoría Inmutable
```python
from core.db_exo import LedgerExo

ledger = LedgerExo(
    ledger_id="ldg_20251118_001",
    usuario_id="user_admin_001",
    msp_id="msp_telcel_001",
    accion="CREATE",           # CREATE, UPDATE, DELETE, ACCESS
    entidad="condominios_exo",
    entidad_id="condo_lomas_001"
)
```

---

## 🚀 Uso Rápido

### **1. Configurar Engine**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db_exo import Base

# PostgreSQL
DATABASE_URL = "postgresql://user:password@host:port/database"
engine = create_engine(DATABASE_URL, echo=True)

# Crear todas las tablas
Base.metadata.create_all(engine)

# Crear session
Session = sessionmaker(bind=engine)
session = Session()
```

### **2. Crear Registros**

```python
from core.db_exo import MSPExo, CondominioExo

# Crear MSP
msp = MSPExo(
    msp_id="msp_001",
    nombre="Mi MSP",
    plan="professional"
)
session.add(msp)

# Crear Condominio
condo = CondominioExo(
    condominio_id="condo_001",
    msp_id="msp_001",  # FK exógeno
    nombre="Mi Condominio"
)
session.add(condo)

session.commit()
```

### **3. Query Multi-tenant**

```python
# Query todos los condominios de un MSP
condominios = session.query(CondominioExo).filter_by(
    msp_id="msp_001",
    estado="activo"
).all()

# Query con JOIN
from core.db_exo import UsuarioExo

usuarios = session.query(UsuarioExo).filter_by(
    condominio_id="condo_001"
).all()
```

### **4. Actualizar Registros**

```python
# Buscar MSP
msp = session.query(MSPExo).filter_by(msp_id="msp_001").first()

# Actualizar
msp.plan = "enterprise"
msp.max_condominios = 1000

session.commit()
```

### **5. Eliminar con Cascade**

```python
# Eliminar regla (CASCADE en condominios_exo)
regla = session.query(ReglaExo).filter_by(regla_id="regla_001").first()
session.delete(regla)
session.commit()

# Eliminar MSP (RESTRICT - falla si tiene condominios)
msp = session.query(MSPExo).filter_by(msp_id="msp_001").first()
session.delete(msp)  # ❌ Error si tiene condominios activos
```

---

## 🧪 Tests

```bash
# Ejecutar tests de modelos
python test_models_exo.py

# Salida esperada:
# ✅ 11 modelos SQLAlchemy definidos
# ✅ Identificadores exógenos implementados
# ✅ Foreign Keys correctos (msp_id, condominio_id)
# ✅ 100% fiel al schema PostgreSQL
# ✅ Filosofía AUP-EXO respetada
```

---

## 📚 Ejemplos Completos

Ver `ejemplos_uso_modelos_exo.py` para 6 casos de uso reales:

1. ✅ Crear MSP y Condominios
2. ✅ Crear Usuario Admin
3. ✅ Registrar Residencias y Residentes
4. ✅ Autorizar Visitante con QR
5. ✅ Registrar Acceso con QR
6. ✅ Query Multi-tenant por MSP

```bash
# Editar DATABASE_URL en el archivo y ejecutar:
python ejemplos_uso_modelos_exo.py
```

---

## 📂 Estructura de Archivos

```
/workspaces/Accesos-Residencial/
├── core/
│   └── db_exo.py                    # Modelos SQLAlchemy (línea 290+)
├── database/
│   └── schema_exo.sql               # Schema PostgreSQL original
├── test_models_exo.py               # Tests de validación
├── ejemplos_uso_modelos_exo.py      # Ejemplos de uso
└── README_MODELOS_EXO.md            # Este archivo
```

---

## 🔑 Conceptos Clave

### **Identificadores Exógenos vs. PKs Internas**

```python
# ❌ INCORRECTO (NO AUP-EXO)
class CondominioMalo(Base):
    id = Column(Integer, primary_key=True)
    msp_id = Column(Integer, ForeignKey("msps.id"))  # ❌ FK a PK interna

# ✅ CORRECTO (AUP-EXO)
class CondominioExo(Base):
    id = Column(Integer, primary_key=True)              # Solo para indexing
    condominio_id = Column(String, unique=True)         # Identificador exógeno
    msp_id = Column(String, ForeignKey("msps_exo.msp_id"))  # ✅ FK a ID exógeno
```

### **Scope Multi-tenant**

```python
# Super Admin ve TODO
condominios = session.query(CondominioExo).all()

# MSP Admin ve solo SU scope
condominios = session.query(CondominioExo).filter_by(
    msp_id="msp_telcel_001"
).all()

# Condominio Admin ve solo SU condominio
usuarios = session.query(UsuarioExo).filter_by(
    condominio_id="condo_lomas_001"
).all()
```

### **Nullable FKs para Jerarquía**

```python
# Super Admin: NO tiene MSP ni Condominio
usuario = UsuarioExo(
    usuario_id="superadmin_001",
    rol_id=1,
    msp_id=None,           # ✅ Nullable
    condominio_id=None     # ✅ Nullable
)

# MSP Admin: tiene MSP pero NO condominio
usuario = UsuarioExo(
    usuario_id="msp_admin_001",
    rol_id=2,
    msp_id="msp_001",      # ✅ Tiene valor
    condominio_id=None     # ✅ Nullable
)
```

---

## ⚠️ Requisitos

```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

Ver `requirements.txt` para versiones específicas.

---

## 🎯 Siguiente Paso

1. **Configurar PostgreSQL:**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:port/axs_exo"
   ```

2. **Crear tablas:**
   ```python
   from sqlalchemy import create_engine
   from core.db_exo import Base
   
   engine = create_engine(DATABASE_URL)
   Base.metadata.create_all(engine)
   ```

3. **Usar modelos:**
   ```python
   from core.db_exo import MSPExo, CondominioExo
   from sqlalchemy.orm import sessionmaker
   
   Session = sessionmaker(bind=engine)
   session = Session()
   
   # ... tu código aquí ...
   ```

---

## 📞 Soporte

- **Schema SQL:** `database/schema_exo.sql`
- **Tests:** `test_models_exo.py`
- **Ejemplos:** `ejemplos_uso_modelos_exo.py`
- **Documentación AUP-EXO:** `RESUMEN_EXO.md`, `DISENO_AUP_EXO.md`

---

**Última actualización:** 18 de Noviembre, 2025  
**Versión:** 1.0  
**Branch:** `feature/multi-tenant-hierarchy`
