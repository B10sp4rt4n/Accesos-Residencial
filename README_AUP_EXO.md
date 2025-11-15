# 🏠 AUP-EXO - Sistema de Control de Accesos Residencial

**Arquitectura Universal Plataforma - Experiencia Optimizada**

Sistema de control de accesos residencial de nivel empresarial con trazabilidad inmutable, motor de reglas configurable y gestión integral de evidencias.

## 🎯 Características Principales

### ✅ Core Infrastructure
- **Base de Datos SQLite**: Schema optimizado con 7 tablas relacionales
- **Sistema de Hash SHA-256**: Trazabilidad inmutable estilo blockchain
- **Motor de Reglas**: Evaluación de políticas con 4 tipos de condiciones
- **Gestión de Roles**: Sistema granular con 21 permisos diferentes
- **Orquestador Central**: Coordinación de flujos de acceso
- **Gestión de Evidencias**: Almacenamiento con verificación de integridad

### 🔐 Seguridad y Trazabilidad
- Encadenamiento de eventos con hash SHA-256
- Verificación de integridad de cadena completa
- Auditoría completa de todas las operaciones
- Sistema de roles y permisos granular
- Captura de contexto de dispositivo y red

### 📊 Módulos de Aplicación
- **Personas**: Gestión de residentes, visitantes, empleados
- **Vehículos**: Control vehicular con lista negra
- **Eventos**: Visualización en tiempo real con análisis
- **Vigilancia**: Interfaz touch-friendly para tablets
- **Políticas**: CRUD de reglas de negocio configurables

### 🇲🇽 Estándares Mexicanos
- Validación de placas vehiculares (formatos CDMX, EDO, etc.)
- Validación de CURP
- Validación de teléfonos (10 dígitos)
- Generación de códigos QR

## 🚀 Inicio Rápido

### Requisitos
- Python 3.12+
- pip

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/B10sp4rt4n/Accesos-Residencial.git
cd Accesos-Residencial

# Checkout branch AUP-EXO
git checkout feature/aup-exo-roadmap

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos con datos de ejemplo
python init_data.py

# Iniciar aplicación
streamlit run app_aup_exo.py
```

La aplicación estará disponible en `http://localhost:8501`

### Datos de Ejemplo
El script `init_data.py` crea:
- 5 residentes con datos completos
- 5 vehículos vinculados
- 3 políticas de acceso pre-configuradas
- 20 eventos de acceso simulados

## 📁 Estructura del Proyecto

```
Accesos-Residencial/
├── core/                      # Núcleo AUP-EXO
│   ├── db.py                  # Gestión de base de datos
│   ├── hashing.py             # Sistema de hash y encadenamiento
│   ├── motor_reglas.py        # Evaluador de políticas
│   ├── orquestador.py         # Coordinador central
│   ├── roles.py               # Sistema de permisos
│   ├── utils.py               # Validaciones y utilidades
│   ├── evidencia.py           # Gestión de evidencias
│   └── contexto.py            # Captura de contexto
├── modulos/                   # Módulos de aplicación
│   ├── entidades.py           # Gestión de personas
│   ├── accesos.py             # Gestión de vehículos
│   ├── eventos.py             # Visualización de eventos
│   ├── vigilancia.py          # Interfaz de vigilante
│   └── politicas.py           # Gestión de políticas
├── data/                      # Datos persistentes
│   ├── accesos.sqlite         # Base de datos principal
│   └── evidencia/             # Evidencias fotográficas
├── app_aup_exo.py             # Aplicación principal
├── init_data.py               # Inicializador de datos
└── PROGRESO.md                # Roadmap de 8 fases

```

## 🗄️ Schema de Base de Datos

### Tablas Principales

**entidades**
- Almacena personas y vehículos con hash de integridad
- Campos: entidad_id, tipo, atributos, hash, estado

**eventos**
- Registra todos los accesos con encadenamiento hash
- Campos: evento_id, entidad_id, tipo_evento, hash, hash_previo

**politicas**
- Define reglas de negocio configurables
- Campos: politica_id, nombre, condiciones, prioridad, aplicable_a

**usuarios**
- Gestión de usuarios del sistema
- Campos: usuario_id, nombre, email, rol

**roles**
- Definición de roles y permisos
- Campos: rol_id, nombre, permisos, nivel_acceso

**bitacora**
- Auditoría de operaciones críticas
- Campos: operacion, usuario, timestamp, detalles

**log_reglas**
- Historial de evaluaciones de políticas
- Campos: evento_id, politica_id, resultado, motivo

## 🔧 Configuración

### Motor de Reglas
Las políticas soportan 4 tipos de condiciones:

1. **Horario**: Restricción por horario
   ```json
   {"tipo": "horario", "hora_inicio": "06:00", "hora_fin": "22:00"}
   ```

2. **Días de Semana**: Restricción por días
   ```json
   {"tipo": "dias_semana", "dias_permitidos": ["lunes", "martes", "miercoles"]}
   ```

3. **Lista Negra**: Bloqueo automático
   ```json
   {"tipo": "lista_negra", "accion": "denegar"}
   ```

4. **Autorización Previa**: Requiere aprobación
   ```json
   {"tipo": "autorizacion_previa", "metodo": "residente"}
   ```

### Sistema de Roles

**Roles predefinidos:**
- `administrador`: Acceso total al sistema
- `coordinador`: Gestión de políticas y reportes
- `vigilante`: Registro de accesos y consultas
- `residente`: Consulta limitada de información propia

## 📱 Interfaz de Vigilante

Optimizada para tablets (Samsung Galaxy Tab A8 recomendada):
- Botones touch-friendly (80px)
- Captura de fotos con cámara integrada
- Búsqueda rápida de placas
- Alertas visuales de lista negra
- Registro de vehículos no registrados
- Auto-refresh de eventos en vivo

## 🔄 Roadmap

### ✅ Completado (Fases 1-3)
- Core infrastructure (9 módulos)
- Módulos de aplicación (5 módulos)
- Aplicación principal con navegación

### ⏳ Pendiente (Fases 4-8)
- Testing e integración
- Documentación completa
- Migración a Supabase/PostgreSQL
- Deployment en Streamlit Cloud
- Integración con HotVault/Recordia

Ver [PROGRESO.md](./PROGRESO.md) para detalles completos.

## 🧪 Testing

```bash
# Unit tests (en desarrollo)
pytest tests/ -v

# Verificar integridad de cadena de eventos
python -c "from core.hashing import verificar_cadena_integridad; print(verificar_cadena_integridad())"
```

## 📊 Análisis y Reportes

La aplicación incluye:
- Dashboard en tiempo real
- Análisis de tendencias temporales
- Top 10 entidades/vehículos
- Distribución por tipo de evento
- Tasa de autorización/denegación
- Exportación a CSV

## 🔐 Seguridad

- Todas las contraseñas hasheadas con bcrypt
- Tokens de sesión con expiración
- Row Level Security (próximamente con Supabase)
- Encriptación en tránsito (HTTPS)
- Auditoría completa de operaciones

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👥 Autores

- **Desarrollador Principal** - B10sp4rt4n

## 🙏 Agradecimientos

- Comunidad de Streamlit
- Supabase Team
- Contribuidores del proyecto

## 📞 Soporte

Para reportar bugs o solicitar features, por favor abre un [issue](https://github.com/B10sp4rt4n/Accesos-Residencial/issues).

---

**Versión:** 2.0.0-aup-exo  
**Última actualización:** 15 de noviembre de 2025  
**Estado:** En desarrollo activo (Branch: feature/aup-exo-roadmap)
