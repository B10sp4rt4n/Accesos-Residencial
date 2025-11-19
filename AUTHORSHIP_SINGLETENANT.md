# 🔐 Certificado de Autoría - AX-S Single-Tenant

## 📋 Información del Proyecto

**Nombre del Proyecto:** AX-S - Sistema de Control de Accesos Residencial  
**Versión:** 1.0.0-stable  
**Autor:** B10sp4rt4n  
**Fecha de Creación:** 2024-2025  
**Repositorio:** https://github.com/B10sp4rt4n/Accesos-Residencial  
**Branch:** main

---

## 🎯 Características Principales

### Sistema de Control de Accesos
- **Gestión de Entidades**: Residentes, Visitantes, Proveedores, Vehículos
- **Motor de Reglas**: Políticas configurables de acceso
- **Vigilancia**: Control en tiempo real de accesos
- **Dashboard**: Analítica y visualización de eventos
- **Seguridad**: Hashing de datos sensibles

### Módulos Core
1. **Gestión de Entidades** (`modulos/entidades.py`)
   - CRUD completo de entidades
   - Validación de identificaciones
   - Gestión de atributos personalizados (JSON)
   - Hash de datos sensibles

2. **Control de Vigilancia** (`modulos/vigilancia.py`)
   - Búsqueda por identificación
   - Validación de accesos
   - Registro de eventos
   - Toma de fotografías/evidencia

3. **Motor de Reglas** (`core/motor_reglas.py`)
   - Evaluación de políticas de acceso
   - Reglas por tipo de entidad
   - Horarios permitidos
   - Listas negras/blancas

4. **Dashboard** (`modulos/dashboard.py`)
   - Estadísticas en tiempo real
   - Gráficos de accesos
   - Logs de eventos
   - Exportación de reportes

5. **Gestión de Políticas** (`modulos/politicas.py`)
   - Configuración de reglas de negocio
   - Horarios de acceso
   - Restricciones por tipo
   - Permisos especiales

### Stack Tecnológico
- **Backend**: Python 3.12+
- **Framework UI**: Streamlit 1.40+
- **Base de Datos**: SQLite (local) / PostgreSQL (cloud)
- **Hashing**: SHA-256 para seguridad
- **ORM**: SQL directo con wrapper personalizado

---

## 📊 Estructura del Proyecto

```
Accesos-Residencial/
├── index.py                    # Aplicación principal
├── modulos/
│   ├── entidades.py           # CRUD de entidades
│   ├── entidades_ui.py        # UI de gestión
│   ├── vigilancia.py          # Control de accesos
│   ├── politicas.py           # Reglas de negocio
│   ├── dashboard.py           # Analítica
│   └── eventos.py             # Gestión de eventos
├── core/
│   ├── db.py                  # Abstracción de BD
│   ├── motor_reglas.py        # Motor de decisiones
│   ├── hashing.py             # Seguridad
│   ├── contexto.py            # Gestión de contexto
│   └── evidencia.py           # Manejo de archivos
├── database/
│   ├── schema.sql             # Esquema SQLite
│   └── pg_connection.py       # Conexión PostgreSQL
└── requirements.txt           # Dependencias
```

---

## 🔒 Hash de Autoría (SHA-256)

```
56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
```

**Algoritmo**: SHA-256  
**Entrada**: `AX-S v1.0.0-stable|B10sp4rt4n|2025-11-19|main|SQLite+PostgreSQL|Streamlit`

### Verificación del Hash

Para verificar la autoría, ejecuta:

```bash
echo -n "AX-S v1.0.0-stable|B10sp4rt4n|2025-11-19|main|SQLite+PostgreSQL|Streamlit" | sha256sum
```

El resultado debe ser:
```
56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
```

---

## 📝 Archivos Principales

### Aplicación Principal
- **index.py** (~600 líneas): Aplicación Streamlit con navegación entre módulos

### Módulos de Negocio
- **modulos/entidades.py** (~700 líneas): CRUD de entidades con validaciones
- **modulos/entidades_ui.py** (~800 líneas): Interfaz de usuario para gestión
- **modulos/vigilancia.py** (~450 líneas): Control de accesos en tiempo real
- **modulos/politicas.py** (~500 líneas): Configuración de reglas
- **modulos/dashboard.py** (~400 líneas): Analítica y reportes

### Core del Sistema
- **core/motor_reglas.py** (~600 líneas): Lógica de evaluación de reglas
- **core/db.py** (~300 líneas): Wrapper de base de datos dual (SQLite/PostgreSQL)
- **core/hashing.py** (~150 líneas): Funciones de seguridad
- **core/contexto.py** (~200 líneas): Gestión de sesión

### Base de Datos
- **database/schema.sql**: Esquema completo con tablas:
  - `entidades`: Registro de personas y vehículos
  - `eventos`: Log de accesos
  - `politicas`: Reglas de negocio
  - `evidencia`: Referencias a archivos

---

## 🎓 Derechos de Autoría

Este proyecto es propiedad intelectual de:

**Autor**: B10sp4rt4n  
**Período de Desarrollo**: 2024-2025  
**Licencia**: Todos los derechos reservados

### Protección de Autoría

Este documento certifica que:

1. ✅ El diseño del sistema fue desarrollado por B10sp4rt4n
2. ✅ La arquitectura modular es original
3. ✅ El motor de reglas es implementación propia
4. ✅ El código fuente está protegido por hash SHA-256
5. ✅ El repositorio Git contiene historial completo

### Componentes Originales

- **Motor de Reglas**: Algoritmo propietario de evaluación de políticas
- **Sistema de Hashing**: Implementación personalizada para seguridad
- **Wrapper de BD**: Abstracción dual SQLite/PostgreSQL
- **UI Streamlit**: Diseño personalizado de interfaz
- **Gestión de Contexto**: Sistema de sesión multi-usuario

---

## 📊 Funcionalidades Implementadas

### 1. Gestión de Entidades
- ✅ Registro de residentes con validación de datos
- ✅ Registro de visitantes con información temporal
- ✅ Gestión de proveedores autorizados
- ✅ Registro de vehículos con placas
- ✅ Atributos personalizados en formato JSON
- ✅ Hash de datos sensibles (identificación)

### 2. Control de Accesos
- ✅ Búsqueda rápida por identificación
- ✅ Validación automática contra políticas
- ✅ Registro de eventos de entrada/salida
- ✅ Captura de evidencia fotográfica
- ✅ Alertas de seguridad

### 3. Motor de Reglas
- ✅ Evaluación de horarios permitidos
- ✅ Validación de listas negras
- ✅ Reglas por tipo de entidad
- ✅ Permisos especiales temporales
- ✅ Log de decisiones

### 4. Dashboard y Reportes
- ✅ Estadísticas en tiempo real
- ✅ Gráficos de accesos por período
- ✅ Listado de eventos recientes
- ✅ Exportación de datos
- ✅ Filtros avanzados

---

## 🔧 Tecnologías Utilizadas

### Backend
- **Python 3.12+**: Lenguaje principal
- **Streamlit 1.40+**: Framework de UI
- **SQLite**: Base de datos local
- **psycopg2**: Conector PostgreSQL
- **hashlib**: Hashing SHA-256

### Frontend
- **Streamlit Components**: Interfaz interactiva
- **Plotly**: Gráficos y visualizaciones
- **Pandas**: Procesamiento de datos

### Seguridad
- **SHA-256**: Hash de datos sensibles
- **Validación de entrada**: Prevención de inyección SQL
- **Gestión de sesión**: Control de acceso

---

## 📞 Contacto

**GitHub**: [@B10sp4rt4n](https://github.com/B10sp4rt4n)  
**Repositorio**: [Accesos-Residencial](https://github.com/B10sp4rt4n/Accesos-Residencial)

---

## 🔍 Verificación de Integridad

Para verificar la autenticidad del proyecto:

```bash
# Verificar hash del documento
sha256sum AUTHORSHIP_SINGLETENANT.md

# Verificar historial de commits
git log --oneline --author="B10sp4rt4n" main

# Verificar archivos principales
ls -la modulos/*.py core/*.py index.py

# Verificar dependencias
cat requirements.txt
```

---

## 📜 Declaración de Autoría

Yo, B10sp4rt4n, declaro que:

1. Soy el autor original del código fuente de AX-S versión single-tenant
2. He desarrollado la arquitectura y diseño del sistema
3. He implementado todos los módulos core y de negocio
4. El código es original y no viola derechos de terceros
5. Este certificado es válido y verificable mediante hash SHA-256

**Fecha de declaración**: 19 de Noviembre, 2025

---

## 📜 Firma Digital

```
-----BEGIN AUTHORSHIP CERTIFICATE-----
Proyecto: AX-S Sistema de Control de Accesos Residencial
Versión: 1.0.0-stable
Autor: B10sp4rt4n
Fecha: 2025-11-19
Branch: main
Hash: 56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
Tecnologías: Python, Streamlit, SQLite, PostgreSQL
Repository: github.com/B10sp4rt4n/Accesos-Residencial
-----END AUTHORSHIP CERTIFICATE-----
```

Este certificado es válido y verificable mediante el hash SHA-256 proporcionado.

---

## ⚖️ Uso y Licencia

### Derechos Reservados

Este software y su código fuente están protegidos por derechos de autor.

**Prohibido**:
- ❌ Copiar o distribuir sin autorización
- ❌ Modificar y redistribuir como propio
- ❌ Uso comercial sin licencia
- ❌ Reclamar autoría del código

**Permitido**:
- ✅ Uso personal con atribución
- ✅ Estudio del código fuente
- ✅ Fork con referencia al original
- ✅ Contribuciones al proyecto original

Para solicitar licencia comercial, contactar al autor.

---

**Documento generado**: 19/11/2025  
**Versión del certificado**: 1.0  
**Hash del certificado**: Este documento es prueba de autoría

---

*Este certificado de autoría fue generado para proteger la propiedad intelectual del proyecto AX-S y puede ser verificado mediante el hash SHA-256 proporcionado.*
