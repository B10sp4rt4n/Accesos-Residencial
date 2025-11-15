# Arquitectura del Sistema - Accesos Residencial

## 📐 Visión General

Sistema de control de accesos vehicular para residenciales, diseñado para ser económico, escalable y fácil de usar.

## 🏗️ Arquitectura Actual (MVP)

```
┌─────────────────────────────────────────────────┐
│                  TABLET                         │
│           (Samsung Galaxy Tab A8)               │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │      Navegador Web (Chrome/Safari)      │   │
│  │                                         │   │
│  │  ┌───────────────────────────────────┐  │   │
│  │  │   vigilante.py (Streamlit App)   │  │   │
│  │  │   - Captura de fotos             │  │   │
│  │  │   - Búsqueda de placas           │  │   │
│  │  │   - Registro de eventos          │  │   │
│  │  └───────────────────────────────────┘  │   │
│  └─────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │ WiFi/4G
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────┐
│           Streamlit Cloud (Hosting)             │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │   Aplicación Web (Python/Streamlit)    │   │
│  │   - vigilante.py                       │   │
│  │   - app.py (admin)                     │   │
│  └─────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │ API REST
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────┐
│          Supabase (Backend as a Service)        │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  PostgreSQL  │  │   Storage    │            │
│  │   Database   │  │   (Fotos)    │            │
│  │              │  │              │            │
│  │ - eventos    │  │ - placas/    │            │
│  │ - personas   │  │ - docs/      │            │
│  │ - vehiculos  │  │              │            │
│  │ - politicas  │  │              │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │          Authentication                  │  │
│  │  - Login de guardias                     │  │
│  │  - Row Level Security (RLS)              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📊 Modelo de Datos

### Entidades Principales

```python
# personas
{
    "id": "uuid",
    "nombre": "string",
    "tipo": "residente | visitante | empleado",
    "curp": "string",
    "doc_tipo": "INE | Pasaporte | Licencia",
    "casa": "string",
    "telefono": "string",
    "status": "activo | inactivo",
    "foto_url": "string",
    "created_at": "timestamp"
}

# vehiculos
{
    "id": "uuid",
    "persona_id": "uuid (FK)",
    "placa": "string",
    "estado_mex": "string",
    "marca": "string",
    "modelo": "string",
    "color": "string",
    "foto_url": "string",
    "en_lista_negra": "boolean",
    "created_at": "timestamp"
}

# eventos
{
    "id": "uuid",
    "timestamp": "timestamp",
    "tipo": "entrada | salida",
    "persona_id": "uuid (FK)",
    "vehiculo_id": "uuid (FK)",
    "placa": "string",
    "gate_id": "string",
    "guardia_id": "uuid (FK)",
    "foto_evento_url": "string",
    "placa_confianza": "decimal",
    "verificacion_manual": "boolean",
    "notas": "text"
}

# politicas
{
    "id": "uuid",
    "nombre": "string",
    "descripcion": "text",
    "tipo": "string",
    "prioridad": "Crítica | Alta | Media | Baja",
    "aplicable_a": "string",
    "activa": "boolean",
    "config": "jsonb"
}
```

## 🔄 Flujos de Trabajo

### 1. Registro de Acceso (Residente Conocido)

```
1. Vehículo se acerca
2. Vigilante captura foto de placa (opcional)
3. Vigilante ingresa placa manualmente
4. Sistema busca en BD
5. Muestra información del residente
6. Vigilante presiona "PERMITIR"
7. Evento guardado en BD
8. Confirmación visual

⏱️ Tiempo: 10-15 segundos
```

### 2. Registro de Visitante Nuevo

```
1. Vehículo desconocido
2. Sistema indica "NO REGISTRADO"
3. Vigilante completa formulario:
   - Nombre
   - Casa destino
   - Tipo (visitante/empleado/delivery)
4. Vigilante presiona "REGISTRAR Y PERMITIR"
5. Persona y vehículo guardados en BD
6. Evento de entrada registrado

⏱️ Tiempo: 30-45 segundos
```

### 3. Alerta de Lista Negra

```
1. Vigilante ingresa placa
2. Sistema detecta vehículo en lista negra
3. Alerta roja automática
4. ACCESO DENEGADO (sin opción de anular)
5. Botón "NOTIFICAR SEGURIDAD"
6. Administración es contactada

⏱️ Tiempo: 5 segundos
```

## 🚀 Roadmap de Evolución

### Fase 1: MVP (Actual)
- ✅ Interfaz de vigilante
- ✅ Base de datos mock
- ✅ Captura manual de placas
- ✅ Registro básico de eventos

### Fase 2: Integración BD (1-2 semanas)
- [ ] Conectar Supabase
- [ ] Migrar datos mock
- [ ] Autenticación de guardias
- [ ] Almacenamiento de fotos

### Fase 3: OCR Básico (2-4 semanas)
- [ ] Integrar Tesseract OCR
- [ ] Procesamiento de fotos
- [ ] Validación de placas mexicanas
- [ ] Mejora de confianza

### Fase 4: Automatización (2-3 meses)
- [ ] Cámara LPR dedicada
- [ ] Lectura automática de placas
- [ ] Barrera automática
- [ ] Notificaciones push

### Fase 5: Analítica Avanzada (3-6 meses)
- [ ] Reportes personalizados
- [ ] Predicción de horarios pico
- [ ] Detección de anomalías
- [ ] Dashboard ejecutivo

## 💻 Stack Tecnológico

### Frontend
- **Streamlit** - Framework web en Python
- **HTML/CSS personalizado** - Estilos touch-friendly

### Backend
- **Supabase** - Backend as a Service
  - PostgreSQL (base de datos)
  - Authentication (login)
  - Storage (fotos)
  - Realtime (WebSocket)

### Hosting
- **Streamlit Cloud** - Hosting gratuito
- **GitHub** - Control de versiones

### Futuro
- **OpenALPR / Tesseract** - OCR de placas
- **Twilio** - SMS para notificaciones
- **SendGrid** - Email para reportes

## 🔐 Seguridad

### Actual
- ✅ HTTPS por defecto (Streamlit Cloud)
- ✅ Datos en la nube (Supabase)
- ✅ Session state para usuarios

### Planeado
- [ ] Autenticación de guardias
- [ ] Row Level Security (RLS)
- [ ] Auditoría completa
- [ ] Encriptación de datos sensibles
- [ ] Backups automáticos

## 📈 Escalabilidad

### Capacidad Actual (Tier Gratis)
- **Eventos**: ~50,000
- **Personas**: ~2,000
- **Vehículos**: ~1,000
- **Fotos**: ~5,000
- **Duración**: 6-12 meses

### Escalamiento
- **Tier Pro** ($25/mes): 10x capacidad
- **Múltiples tablets**: Sin costo adicional
- **Múltiples casetas**: Configuración `gate_id`

## 🎯 Métricas de Éxito

### Operacionales
- Tiempo de registro: < 20 segundos
- Errores de captura: < 5%
- Disponibilidad: > 99%

### Negocio
- Reducción de papel: 100%
- Evidencia fotográfica: 100%
- Satisfacción vigilantes: > 4/5
- ROI: 6 meses

## 📞 Soporte y Mantenimiento

### Actualizaciones
- **Código**: Push a GitHub → Deploy automático
- **Datos**: Migraciones SQL en Supabase
- **Configuración**: Secrets en Streamlit Cloud

### Monitoreo
- Logs en Streamlit Cloud
- Métricas de Supabase
- Alertas por email (futuro)

---

**Versión**: 1.0  
**Última actualización**: Noviembre 2025  
**Autor**: Sistema Accesos Residencial
