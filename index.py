# index.py
"""
Sistema de Control de Accesos Residencial
Arquitectura AUP-EXO Multi-Tenant
"""

import streamlit as st
from modulos.vigilancia import ui_vigilancia
from modulos.entidades_ui import ui_entidades
from modulos.eventos import ui_eventos
from modulos.politicas import ui_politicas
from modulos.dashboard import ui_dashboard

# Auto-inicialización de base de datos
try:
    from core.db import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        # Probar si existe la tabla eventos
        cursor.execute("SELECT COUNT(*) FROM eventos LIMIT 1")
        cursor.fetchone()
    print("✅ Base de datos operativa")
except Exception as e:
    print(f"⚠️  Inicializando base de datos: {e}")
    try:
        # Si falla, intentar con PostgreSQL nativo
        import os
        if os.getenv('DB_MODE') == 'postgres' or (hasattr(st, 'secrets') and st.secrets.get('DB_MODE') == 'postgres'):
            from database.pg_connection import init_pg_schema
            init_pg_schema()
            print("✅ Schema PostgreSQL inicializado")
        else:
            from core.db import init_db
            init_db()
            print("✅ Schema SQLite inicializado")
    except Exception as init_error:
        print(f"❌ Error inicializando: {init_error}")
        st.error(f"Error inicializando base de datos: {init_error}")

# Configuración de página
st.set_page_config(
    page_title="AX-S Multi-Tenant - AUP-EXO",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar session state para contexto multi-tenant
if 'msp_id' not in st.session_state:
    st.session_state.msp_id = None
if 'condominio_id' not in st.session_state:
    st.session_state.condominio_id = None
if 'rol_usuario' not in st.session_state:
    st.session_state.rol_usuario = 'super_admin'  # Por defecto Super Admin

# Sidebar - Contexto Multi-Tenant
st.sidebar.title("🏢 AX-S Multi-Tenant")
st.sidebar.markdown("**Arquitectura AUP-EXO**")
st.sidebar.divider()

# Selector de contexto según rol
with st.sidebar.expander("🔐 Contexto de Trabajo", expanded=True):
    rol = st.selectbox(
        "Rol:",
        ["Super Admin (DS)", "MSP Admin (DD)", "Condominio Admin (SE)", "Admin Local (NO)"],
        help="Selecciona tu nivel de acceso"
    )
    
    if "Super Admin" in rol:
        st.session_state.rol_usuario = 'super_admin'
        st.info("🌟 Acceso total al sistema")
        
    elif "MSP Admin" in rol:
        st.session_state.rol_usuario = 'msp_admin'
        # Aquí iría un selector de MSP desde la base de datos
        msp_seleccionado = st.text_input("MSP ID:", value="MSP-DEMO-001")
        st.session_state.msp_id = msp_seleccionado if msp_seleccionado else None
        
    elif "Condominio Admin" in rol:
        st.session_state.rol_usuario = 'condominio_admin'
        msp_seleccionado = st.text_input("MSP ID:", value="MSP-DEMO-001")
        cond_seleccionado = st.text_input("Condominio ID:", value="COND-DEMO-001")
        st.session_state.msp_id = msp_seleccionado if msp_seleccionado else None
        st.session_state.condominio_id = cond_seleccionado if cond_seleccionado else None
        
    else:  # Admin Local
        st.session_state.rol_usuario = 'admin_local'
        msp_seleccionado = st.text_input("MSP ID:", value="MSP-DEMO-001")
        cond_seleccionado = st.text_input("Condominio ID:", value="COND-DEMO-001")
        st.session_state.msp_id = msp_seleccionado if msp_seleccionado else None
        st.session_state.condominio_id = cond_seleccionado if cond_seleccionado else None

st.sidebar.divider()

opcion = st.sidebar.radio(
    "Seleccione módulo:",
    [
        "🏢 Gestión MSPs",
        "🏘️ Gestión Condominios",
        "🚧 Control de Accesos",
        "🏢 Registro de Entidades",
        "📊 Historial de Eventos",
        "📋 Políticas y Reglas",
        "📈 Dashboard AUP-EXO",
        "ℹ️ Acerca del Sistema"
    ]
)

st.sidebar.divider()

# Información del sistema en sidebar
with st.sidebar.expander("📌 Información"):
    st.caption("**Versión:** 2.0.0-aup-exo-multitenant")
    st.caption("**Arquitectura:** AUP-EXO Multi-Tenant")
    st.caption("**Base de datos:** PostgreSQL (Neon)")
    if st.session_state.msp_id:
        st.caption(f"**MSP Activo:** {st.session_state.msp_id}")
    if st.session_state.condominio_id:
        st.caption(f"**Condominio:** {st.session_state.condominio_id}")

# Renderizado según selección
if opcion == "🏢 Gestión MSPs":
    st.title("🏢 Gestión de MSPs")
    st.info("Módulo de gestión de Managed Service Providers (en desarrollo)")
    
    # Mostrar MSPs existentes
    try:
        from core.db import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM msps_exo ORDER BY created_at DESC")
            msps = cursor.fetchall()
            
            if msps:
                st.success(f"Total de MSPs: {len(msps)}")
                for msp in msps:
                    with st.expander(f"MSP: {msp[2]} ({msp[1]})"):
                        st.write(f"**Razón Social:** {msp[3]}")
                        st.write(f"**Plan:** {msp[8]}")
                        st.write(f"**Estado:** {msp[7]}")
                        st.write(f"**Max Condominios:** {msp[9]}")
            else:
                st.warning("No hay MSPs registrados")
    except Exception as e:
        st.error(f"Error cargando MSPs: {e}")

elif opcion == "🏘️ Gestión Condominios":
    st.title("🏘️ Gestión de Condominios")
    st.info("Módulo de gestión de Condominios (en desarrollo)")
    
    # Filtrar por MSP si está seleccionado
    try:
        from core.db import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            if st.session_state.msp_id:
                cursor.execute("SELECT * FROM condominios_exo WHERE msp_id = ? ORDER BY created_at DESC", 
                             (st.session_state.msp_id,))
            else:
                cursor.execute("SELECT * FROM condominios_exo ORDER BY created_at DESC")
            
            condominios = cursor.fetchall()
            
            if condominios:
                st.success(f"Total de Condominios: {len(condominios)}")
                for cond in condominios:
                    with st.expander(f"Condominio: {cond[3]} ({cond[1]})"):
                        st.write(f"**MSP:** {cond[2]}")
                        st.write(f"**Ciudad:** {cond[5]}")
                        st.write(f"**Estado:** {cond[11]}")
                        st.write(f"**Unidades:** {cond[10]}")
            else:
                st.warning("No hay condominios registrados")
    except Exception as e:
        st.error(f"Error cargando condominios: {e}")

elif opcion == "🚧 Control de Accesos":
    ui_vigilancia()

elif opcion == "🏢 Registro de Entidades":
    ui_entidades()

elif opcion == "📊 Historial de Eventos":
    ui_eventos()

elif opcion == "📋 Políticas y Reglas":
    ui_politicas()

elif opcion == "📈 Dashboard AUP-EXO":
    ui_dashboard()

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
