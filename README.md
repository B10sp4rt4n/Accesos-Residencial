# Accesos-Residencial 🏠

Sistema de control de accesos para residenciales con interfaz web optimizada para tablets.

## 📱 Módulos Disponibles

### 1. **Interfaz de Vigilante** (`vigilante.py`) ⭐ NUEVO
Interfaz optimizada para tablets en caseta:
- ✅ Diseño touch-friendly (botones 80px)
- ✅ Captura de fotos con cámara de tablet
- ✅ Búsqueda rápida de placas
- ✅ Alertas visuales (verde/rojo)
- ✅ Sistema de lista negra
- ✅ Registro de visitantes
- ✅ Funciona con presupuesto mínimo ($240-350)

```bash
streamlit run vigilante.py
```

### 2. **Dashboard Administrativo** (`app.py`)
Panel de control con métricas y análisis:
- Dashboard general
- Eventos en tiempo real
- Gestión de personas
- Gestión de vehículos
- Políticas de seguridad

```bash
streamlit run app.py
```

## 🚀 Cómo desplegar en Streamlit Cloud

1. Ir a https://streamlit.io/cloud e iniciar sesión con GitHub.
2. Crear una nueva app y conectar este repositorio.
3. Como `Main file` usar:
   - **Para vigilantes:** `vigilante.py`
   - **Para administración:** `app.py`
4. Streamlit Cloud instalará las dependencias desde `requirements.txt` automáticamente.
5. Opcional: en la sección "Secrets" de tu app en Streamlit Cloud añade variables sensibles (ej.: `SUPABASE_URL`, `SUPABASE_KEY`) si vas a conectar a Supabase.

## 💰 Presupuesto Inicial (Solo Tablet)

### Hardware Necesario
```
Samsung Galaxy Tab A8 (10.5"): $200
Funda protectora con soporte: $25
Cable USB-C de repuesto: $15
───────────────────────────────
TOTAL: $240
```

### Software (GRATIS)
- ✅ Streamlit Cloud: $0 (hosting)
- ✅ Supabase: $0 (hasta 500MB)
- ✅ GitHub: $0 (repositorio)

### Costo Mensual
- Internet WiFi/Datos: $0-15
- **Total mensual: $0-15**

## 🎯 Características del Sistema

### Para Vigilantes
- 📸 Captura de placas con cámara de tablet
- 🔍 Búsqueda manual rápida
- ✅ Verificación automática en base de datos
- 🚨 Alertas de seguridad (lista negra)
- 📝 Registro de visitantes nuevos
- 📊 Historial de eventos del turno
- ⚡ Tiempo de registro: ~15 segundos

### Para Administradores
- 📊 Dashboard con métricas en tiempo real
- 👥 Gestión de residentes y visitantes
- 🚗 Control de vehículos registrados
- 📋 Políticas de seguridad configurables
- 📈 Análisis y reportes
- 🔄 Eventos en vivo

## 🔧 Instalación Local

Nota sobre reproducibilidad

Se han fijado versiones básicas en `requirements.txt` para evitar sorpresas en Cloud. Si quieres actualizar a versiones más recientes, edita `requirements.txt` y crea un nuevo commit.

Index local

Se añadió `index.py` como índice para probar y navegar localmente entre los módulos (Dashboard, Eventos, Personas, Vehículos, Políticas). Ejecuta:

```bash
streamlit run index.py
```

También puedes usar `index.py` para enlazar a las apps desplegadas si defines las URLs en Streamlit Cloud Secrets (`DASHBOARD_URL`, `EVENTOS_URL`, `PERSONAS_URL`, `VEHICULOS_URL`, `POLITICAS_URL`, `REPO_URL`).

Ejecución local

1. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ejecutar la app localmente:

```bash
streamlit run app.py
```

Notas

- Si planeas usar Supabase, añade las variables de entorno en la sección "Secrets" de Streamlit Cloud (`SUPABASE_URL`, `SUPABASE_KEY`).
- El archivo `app_accesos_residencial` contiene la app principal; se exporta vía `app.py` para facilitar el despliegue.
Software Acceso a Resdencial
