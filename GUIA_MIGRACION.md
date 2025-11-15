# 📋 Guía de Migración AUP-EXO

## 🎯 Resumen de la Migración

El sistema ha sido completamente migrado de una arquitectura CRUD tradicional a **AUP-EXO** (Arquitectura Universal Plataforma - Experiencia Optimizada).

---

## 📊 Comparativa: Antes vs Después

### ❌ ANTES (Legacy)

```
Estructura fragmentada:
├── personas.py          (CRUD personas)
├── vehiculos.py         (CRUD vehículos)
├── visitas.py           (CRUD visitas)
├── proveedores.py       (CRUD proveedores)
├── vigilante.py         (Control accesos)
├── dashboard.py         (Vista datos)
├── eventos.py           (Lista eventos)
└── politicas.py         (Reglas)

Problemas:
- Código duplicado (~1,030 líneas)
- Escrituras directas a DB
- Sin trazabilidad
- Sin validación centralizada
- Difícil de escalar
```

### ✅ AHORA (AUP-EXO)

```
Estructura unificada:
├── index.py             (Menú principal)
├── modulos/
│   ├── entidades.py     (Backend universal)
│   ├── entidades_ui.py  (UI universal)
│   └── vigilancia.py    (Control con orquestador)
├── core/
│   ├── db.py
│   ├── orquestador.py
│   ├── hashing.py
│   └── ...
└── legacy/              (Archivos obsoletos)

Ventajas:
- Código reducido 50%
- Todo pasa por ORQUESTADOR
- Trazabilidad completa (hash chain)
- Validación centralizada
- Escalabilidad infinita
```

---

## 🔄 Mapeo de Funcionalidades

| Funcionalidad Antigua | Nueva Ubicación | Estado |
|----------------------|-----------------|--------|
| Registrar persona | `modulos/entidades_ui.py` → Tab "Registrar" → Tipo "persona" | ✅ |
| Registrar vehículo | `modulos/entidades_ui.py` → Tab "Registrar" → Tipo "vehiculo" | ✅ |
| Registrar visita | `modulos/entidades_ui.py` → Tab "Registrar" → Tipo "visita" | ✅ |
| Registrar proveedor | `modulos/entidades_ui.py` → Tab "Registrar" → Tipo "proveedor" | ✅ |
| Buscar persona | `modulos/vigilancia.py` → Buscador universal | ✅ |
| Buscar vehículo | `modulos/vigilancia.py` → Buscador universal | ✅ |
| Registrar acceso | `modulos/vigilancia.py` → Seleccionar entidad → "Registrar ENTRADA/SALIDA" | ✅ |
| Ver eventos | `modulos/vigilancia.py` → Panel lateral "Eventos Recientes" | ✅ |
| Dashboard | En desarrollo (FASE B) | 🟡 |
| Políticas | En desarrollo (FASE B) | 🟡 |

---

## 🚀 Nuevas Capacidades

### 1. Buscador Universal
**Antes:** Navegar entre múltiples pantallas  
**Ahora:** Un solo campo busca TODO

```python
# Buscar por:
- Nombre: "Juan Pérez"
- Placa: "ABC-1234"
- Folio: "FOLIO-001"
- Teléfono: "5512345678"
- QR: Escanear código
```

### 2. Trazabilidad Completa
**Antes:** Sin historial de cambios  
**Ahora:** Cadena de hash inmutable

```
Estado inicial:
  hash_actual = abc123...
  hash_previo = NULL

Actualización:
  hash_actual = def456...
  hash_previo = abc123... ← Enlace al anterior

Siguiente actualización:
  hash_actual = ghi789...
  hash_previo = def456... ← Cadena completa
```

### 3. Orquestador Centralizado
**Antes:** Escrituras directas a DB  
**Ahora:** Todo pasa por validación

```python
# Flujo anterior:
db.execute("INSERT INTO personas ...")  # Sin validación

# Flujo AUP-EXO:
orquestador.procesar_acceso(...)
  ↓ Evalúa políticas
  ↓ Valida reglas
  ↓ Genera hash
  ↓ Recibo Recordia
  ↓ Registra evento
```

### 4. Soft Delete
**Antes:** DELETE físico (pérdida de datos)  
**Ahora:** Desactivación con preservación

```python
# Desactivar (no elimina):
desactivar_entidad(id)  # estado = 'inactivo'

# Historial completo se mantiene
# Puede reactivarse si es necesario
```

---

## 📖 Guía de Uso para Usuarios

### Registrar una Persona

1. **Menú Principal** → `🏢 Registro de Entidades`
2. **Tab** → `➕ Registrar Nueva`
3. **Tipo** → Seleccionar `persona`
4. **Datos básicos:**
   - Nombre completo
   - Identificador (CURP, teléfono, etc.)
5. **Completar formulario:**
   - Tipo: residente/visitante/empleado/contratista
   - Teléfono, email, dirección
   - Casa, manzana
   - Notas
6. **Click** → `✅ Registrar Entidad`

### Registrar un Acceso

1. **Menú Principal** → `🚧 Control de Accesos`
2. **Buscador** → Escribir placa, nombre o folio
3. **Seleccionar** entidad de resultados
4. **Tipo de acceso** → entrada o salida
5. **Notas** (opcional)
6. **Click** → `✅ Registrar ENTRADA/SALIDA`

### Consultar Entidades

1. **Menú Principal** → `🏢 Registro de Entidades`
2. **Tab** → `📋 Consultar`
3. **Filtrar** por tipo y estado
4. **Expandir** entidad para ver detalles completos

### Editar una Entidad

1. **Menú Principal** → `🏢 Registro de Entidades`
2. **Tab** → `✏️ Editar/Gestionar`
3. **Ingresar ID** de la entidad
4. **Editar** datos (formulario o JSON)
5. **Click** → `💾 Actualizar`
   - Se genera nuevo hash
   - hash_previo se preserva automáticamente

---

## 🔧 Guía Técnica para Desarrolladores

### Estructura del Sistema

```python
# Backend
from modulos.entidades import (
    crear_entidad,           # Crear nueva entidad
    obtener_entidades,       # Listar con filtros
    actualizar_entidad,      # Actualizar con trazabilidad
    desactivar_entidad       # Soft delete
)

# Frontend
from modulos.entidades_ui import ui_entidades

# Vigilancia
from modulos.vigilancia import (
    ui_vigilancia,           # UI principal
    buscar_entidad,          # Buscador universal
    obtener_eventos_recientes  # Eventos del día
)

# Core
from core.orquestador import OrquestadorAccesos
from core.hashing import hash_evento
```

### Agregar Nuevo Tipo de Entidad

```python
# 1. Agregar plantilla en modulos/entidades_ui.py
PLANTILLAS["drone"] = {
    "modelo": "",
    "autonomia": "",
    "zona_asignada": "",
    "altitud_max": ""
}

# 2. (Opcional) Crear formulario específico
def _formulario_drone(plantilla):
    modelo = st.text_input("Modelo")
    autonomia = st.text_input("Autonomía (minutos)")
    # ...
    return {...}

# 3. Agregar al selectbox
tipo = st.selectbox(
    "Tipo de entidad",
    ["persona", "vehiculo", "visita", "proveedor", "drone"]
)

# ¡Listo! Sin cambios de schema
```

### Crear Evento Programáticamente

```python
from core.orquestador import OrquestadorAccesos

orq = OrquestadorAccesos()

# Para entrada (evalúa políticas):
resultado = orq.procesar_acceso(
    entidad_id="ENT_PER_...",
    metadata={"hora": "14:30", "fecha": "2025-11-15"},
    actor="Sistema Automático",
    dispositivo="api_module"
)

# Para salida (registro directo):
resultado = orq.registrar_acceso(
    entidad_id="ENT_VEH_...",
    tipo_evento="salida",
    metadata={...},
    actor="Sistema",
    dispositivo="api"
)
```

---

## 🧪 Testing

### Ejecutar Pruebas

```bash
# Prueba de entidades
python test_entidades.py

# Prueba de UI
python test_entidades_ui.py

# Prueba de flujo completo
python test_flujo_vigilancia.py
```

### Verificar Integridad

```python
from core.hashing import verificar_cadena_integridad

# Verificar hash chain de una entidad
es_valido = verificar_cadena_integridad(entidad_id)
```

---

## 📚 Documentación Adicional

- **Diseño AUP-EXO:** `DISENO_AUP_EXO.md`
- **Estado del Sistema:** `ESTADO_SISTEMA.md`
- **Roadmap:** `PROGRESO.md`
- **Resumen Ejecutivo:** `RESUMEN_EJECUTIVO.md`

---

## 🆘 Soporte

Si encuentras algún problema durante la migración:

1. Verifica que usas los módulos correctos (no legacy)
2. Consulta esta guía de mapeo
3. Revisa los archivos de documentación
4. Ejecuta las pruebas para validar

---

**Última actualización:** 15 de noviembre de 2025  
**Versión:** 2.0.0-aup-exo  
**Branch:** feature/aup-exo-roadmap
