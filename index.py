# index.py
"""
Sistema de Control de Accesos Residencial
Arquitectura AUP-EXO
"""

import streamlit as st
from modulos.vigilancia import ui_vigilancia
from modulos.entidades_ui import ui_entidades
from modulos.eventos import ui_eventos
from modulos.politicas import ui_politicas

# Configuración de página
st.set_page_config(
    page_title="Accesos Residencial - AUP-EXO",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar - Menú principal
st.sidebar.title("🏠 Accesos Residencial")
st.sidebar.markdown("**Sistema AUP-EXO**")
st.sidebar.divider()

opcion = st.sidebar.radio(
    "Seleccione módulo:",
    [
        "🚧 Control de Accesos",
        "🏢 Registro de Entidades",
        "📊 Historial de Eventos",
        "📋 Políticas y Reglas",
        "ℹ️ Acerca del Sistema"
    ]
)

st.sidebar.divider()

# Información del sistema en sidebar
with st.sidebar.expander("📌 Información"):
    st.caption("**Versión:** 2.0.0-aup-exo")
    st.caption("**Arquitectura:** AUP-EXO")
    st.caption("**Fases completadas:** A, A.1, A.2, A.3, A.4, A.5")

# Renderizado según selección
if opcion == "🚧 Control de Accesos":
    ui_vigilancia()

elif opcion == "🏢 Registro de Entidades":
    ui_entidades()

elif opcion == "📊 Historial de Eventos":
    ui_eventos()

elif opcion == "📋 Políticas y Reglas":
    ui_politicas()

elif opcion == "ℹ️ Acerca del Sistema":
    st.header("ℹ️ Acerca del Sistema")
    
    st.markdown("""
    ## Sistema de Control de Accesos Residencial
    
    **Arquitectura:** AUP-EXO (Arquitectura Universal Plataforma - Experiencia Optimizada)
    
    ### 🎯 Características Principales
    
    ✅ **Modelo Universal de Entidades**
    - Personas, vehículos, visitas y proveedores en una sola tabla
    - Atributos parametrizables en JSON
    - Sin cambios de schema para nuevos tipos
    
    ✅ **Trazabilidad Completa**
    - Hash SHA-256 en cada operación
    - Encadenamiento estilo blockchain
    - Recibo Recordia (certificación externa)
    
    ✅ **Orquestador Centralizado**
    - Todas las operaciones pasan por validación
    - Evaluación de políticas automática
    - Registro estructural de eventos
    
    ✅ **Buscador Universal**
    - Búsqueda por nombre, placa, folio, QR, teléfono
    - Sin navegar entre pantallas
    - Resultados instantáneos
    
    ### 📦 Módulos Implementados
    
    | Módulo | Estado | Descripción |
    |--------|--------|-------------|
    | **Entidades** | ✅ Completado | Registro universal de entidades |
    | **Vigilancia** | ✅ Completado | Control de accesos con orquestador |
    | **Eventos** | ✅ Completado | Historial y auditoría |
    | **Políticas** | ✅ Completado | Gestión de reglas parametrizadas |
    
    ### 🚀 Ventajas del Diseño AUP-EXO
    
    1. **Escalabilidad sin refactoring**
       - Agregar drones, sensores, IoT sin tocar schema
    
    2. **Trazabilidad inmutable**
       - Cadena de hash imposible de alterar
       - Certificación jurídica externa
    
    3. **Políticas parametrizadas**
       - Cambios sin deployment
       - Configuración en tiempo real
    
    4. **Modelo mental simple**
       - Todo es una ENTIDAD
       - Todo genera un EVENTO
       - Todo pasa por ORQUESTADOR
    
    ### 📊 Estado del Sistema
    
    **Fases Completadas:**
    - ✅ FASE A: Infraestructura Core
    - ✅ FASE A.1: Vigilancia AUP-EXO
    - ✅ FASE A.2: UI Universal de Entidades
    - ✅ FASE A.3: Migración y Limpieza
    - ✅ FASE A.4: Historial de Eventos
    - ✅ FASE A.5: Políticas Parametrizadas
    
    **Próximas Fases:**
    - ⏳ FASE B: Módulos complementarios
    - ⏳ FASE C: Testing & Integración
    - ⏳ FASE D: Supabase Migration
    - ⏳ FASE E: Recordia-Bridge producción
    
    ### 🔗 Enlaces
    
    - [Documentación AUP-EXO](./DISENO_AUP_EXO.md)
    - [Estado del Sistema](./ESTADO_SISTEMA.md)
    - [Roadmap](./PROGRESO.md)
    
    ---
    
    **Desarrollado con:** Python 3.12+ | Streamlit | SQLite | SHA-256  
    **Última actualización:** 15 de noviembre de 2025
    """)
