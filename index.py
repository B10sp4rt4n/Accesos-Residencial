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

# Configuración de página (debe estar primero)
st.set_page_config(
    page_title="AX-S Multi-Tenant - AUP-EXO",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones de caché para datos dinámicos
@st.cache_data(ttl=60)
def get_msps_list():
    """Obtener listado de MSPs desde la base de datos"""
    try:
        from core.db import get_db
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT msp_id, nombre FROM msps_exo WHERE estado = 'activo' ORDER BY nombre")
            rows = cursor.fetchall()
            if rows:
                # Manejar tanto dict (PostgreSQL) como tuple (SQLite)
                if isinstance(rows[0], dict):
                    return {row['msp_id']: row['nombre'] for row in rows}
                else:
                    return {row[0]: row[1] for row in rows}
            return {}
    except Exception as e:
        st.error(f"Error cargando MSPs: {e}")
        return {}

@st.cache_data(ttl=60)
def get_condominios_by_msp(msp_id):
    """Obtener condominios de un MSP específico"""
    try:
        from core.db import get_db
        import os
        
        # Detectar tipo de base de datos
        is_postgres = os.getenv('DB_MODE') == 'postgres' or (hasattr(st, 'secrets') and st.secrets.get('DB_MODE') == 'postgres')
        placeholder = '%s' if is_postgres else '?'
        
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"SELECT condominio_id, nombre FROM condominios_exo WHERE msp_id = {placeholder} AND estado = 'activo' ORDER BY nombre"
            cursor.execute(query, (msp_id,))
            rows = cursor.fetchall()
            if rows:
                # Manejar tanto dict (PostgreSQL) como tuple (SQLite)
                if isinstance(rows[0], dict):
                    return {row['condominio_id']: row['nombre'] for row in rows}
                else:
                    return {row[0]: row[1] for row in rows}
            return {}
    except Exception as e:
        st.error(f"Error cargando condominios: {e}")
        return {}

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
        
        # Dropdown dinámico de MSPs
        msps = get_msps_list()
        if msps:
            msp_options = [""] + list(msps.keys())
            msp_display = ["-- Seleccionar MSP --"] + [f"{k} - {v}" for k, v in msps.items()]
            msp_idx = st.selectbox(
                "MSP:",
                range(len(msp_options)),
                format_func=lambda x: msp_display[x],
                help="Selecciona el MSP para filtrar"
            )
            st.session_state.msp_id = msp_options[msp_idx] if msp_idx > 0 else None
        else:
            st.warning("⚠️ No hay MSPs disponibles")
            st.session_state.msp_id = None
        
    elif "Condominio Admin" in rol:
        st.session_state.rol_usuario = 'condominio_admin'
        
        # Dropdown de MSPs
        msps = get_msps_list()
        if msps:
            msp_options = [""] + list(msps.keys())
            msp_display = ["-- Seleccionar MSP --"] + [f"{k} - {v}" for k, v in msps.items()]
            msp_idx = st.selectbox(
                "MSP:",
                range(len(msp_options)),
                format_func=lambda x: msp_display[x]
            )
            selected_msp = msp_options[msp_idx] if msp_idx > 0 else None
            st.session_state.msp_id = selected_msp
            
            # Dropdown de Condominios (filtrado por MSP)
            if selected_msp:
                condominios = get_condominios_by_msp(selected_msp)
                if condominios:
                    cond_options = [""] + list(condominios.keys())
                    cond_display = ["-- Seleccionar Condominio --"] + [f"{k} - {v}" for k, v in condominios.items()]
                    cond_idx = st.selectbox(
                        "Condominio:",
                        range(len(cond_options)),
                        format_func=lambda x: cond_display[x]
                    )
                    st.session_state.condominio_id = cond_options[cond_idx] if cond_idx > 0 else None
                else:
                    st.warning(f"⚠️ No hay condominios para {selected_msp}")
                    st.session_state.condominio_id = None
            else:
                st.session_state.condominio_id = None
        else:
            st.warning("⚠️ No hay MSPs disponibles")
            st.session_state.msp_id = None
            st.session_state.condominio_id = None
        
    else:  # Admin Local
        st.session_state.rol_usuario = 'admin_local'
        
        # Mismo selector que Condominio Admin
        msps = get_msps_list()
        if msps:
            msp_options = [""] + list(msps.keys())
            msp_display = ["-- Seleccionar MSP --"] + [f"{k} - {v}" for k, v in msps.items()]
            msp_idx = st.selectbox(
                "MSP:",
                range(len(msp_options)),
                format_func=lambda x: msp_display[x]
            )
            selected_msp = msp_options[msp_idx] if msp_idx > 0 else None
            st.session_state.msp_id = selected_msp
            
            if selected_msp:
                condominios = get_condominios_by_msp(selected_msp)
                if condominios:
                    cond_options = [""] + list(condominios.keys())
                    cond_display = ["-- Seleccionar Condominio --"] + [f"{k} - {v}" for k, v in condominios.items()]
                    cond_idx = st.selectbox(
                        "Condominio:",
                        range(len(cond_options)),
                        format_func=lambda x: cond_display[x]
                    )
                    st.session_state.condominio_id = cond_options[cond_idx] if cond_idx > 0 else None
                else:
                    st.warning(f"⚠️ No hay condominios para {selected_msp}")
                    st.session_state.condominio_id = None
            else:
                st.session_state.condominio_id = None
        else:
            st.warning("⚠️ No hay MSPs disponibles")
            st.session_state.msp_id = None
            st.session_state.condominio_id = None

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
    
    # Tabs para organizar funcionalidad
    tab_list, tab_create = st.tabs(["📋 Listado", "➕ Nuevo MSP"])
    
    with tab_create:
        st.subheader("➕ Crear Nuevo MSP")
        
        with st.form("form_crear_msp"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_msp_id = st.text_input("ID del MSP*", 
                    placeholder="MSP-XXX-001",
                    help="Identificador único del MSP")
                nuevo_nombre = st.text_input("Nombre Comercial*", 
                    placeholder="Mi Empresa MSP")
                nueva_razon = st.text_input("Razón Social", 
                    placeholder="Mi Empresa MSP S.A. de C.V.")
                nuevo_rfc = st.text_input("RFC", 
                    placeholder="ABC123456XYZ")
            
            with col2:
                nuevo_email = st.text_input("Email de Contacto*", 
                    placeholder="contacto@msp.com")
                nuevo_tel = st.text_input("Teléfono", 
                    placeholder="+52 55 1234 5678")
                nuevo_plan = st.selectbox("Plan", 
                    ["basic", "professional", "enterprise"])
                nuevo_max_cond = st.number_input("Máximo de Condominios", 
                    min_value=1, value=10, step=1)
            
            submit = st.form_submit_button("✅ Crear MSP", use_container_width=True)
            
            if submit:
                if not nuevo_msp_id or not nuevo_nombre or not nuevo_email:
                    st.error("⚠️ Los campos marcados con * son obligatorios")
                else:
                    try:
                        from core.db import get_db
                        from datetime import datetime
                        
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute("""
                                INSERT INTO msps_exo 
                                (msp_id, nombre, razon_social, rfc, email_contacto, 
                                 telefono_contacto, estado, plan, max_condominios, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, 'activo', ?, ?, ?)
                            """, (nuevo_msp_id, nuevo_nombre, nueva_razon, nuevo_rfc,
                                  nuevo_email, nuevo_tel, nuevo_plan, nuevo_max_cond,
                                  datetime.now().isoformat()))
                            conn.commit()
                        
                        st.success(f"✅ MSP '{nuevo_nombre}' creado exitosamente!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al crear MSP: {e}")
    
    with tab_list:
        st.subheader("📋 MSPs Registrados")
        
        # Botón de refresh
        if st.button("🔄 Actualizar", use_container_width=False):
            st.rerun()
        
        # Mostrar MSPs existentes
        try:
            from core.db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM msps_exo ORDER BY created_at DESC")
                msps = cursor.fetchall()
                
                if msps:
                    st.success(f"📊 Total de MSPs: {len(msps)}")
                    
                    for msp in msps:
                        with st.expander(f"🏢 {msp[2]} ({msp[1]})", expanded=False):
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**ID:** {msp[1]}")
                                st.write(f"**Razón Social:** {msp[3] or 'N/A'}")
                                st.write(f"**RFC:** {msp[4] or 'N/A'}")
                                st.write(f"**Email:** {msp[5]}")
                            
                            with col_info2:
                                st.write(f"**Teléfono:** {msp[6] or 'N/A'}")
                                st.write(f"**Plan:** {msp[8]}")
                                st.write(f"**Estado:** {msp[7]}")
                                st.write(f"**Max Condominios:** {msp[9]}")
                else:
                    st.warning("📭 No hay MSPs registrados")
                    st.info("💡 Crea tu primer MSP en la pestaña 'Nuevo MSP'")
        except Exception as e:
            st.error(f"❌ Error cargando MSPs: {e}")

elif opcion == "🏘️ Gestión Condominios":
    st.title("🏘️ Gestión de Condominios")
    
    # Tabs para organizar funcionalidad
    tab_list, tab_create = st.tabs(["📋 Listado", "➕ Nuevo Condominio"])
    
    with tab_create:
        st.subheader("➕ Crear Nuevo Condominio")
        
        # Obtener lista de MSPs disponibles
        try:
            from core.db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT msp_id, nombre FROM msps_exo WHERE estado = 'activo' ORDER BY nombre")
                msps_disponibles = cursor.fetchall()
        except Exception as e:
            st.error(f"Error cargando MSPs: {e}")
            msps_disponibles = []
        
        if not msps_disponibles:
            st.warning("⚠️ No hay MSPs disponibles. Primero crea un MSP en el módulo 'Gestión MSPs'.")
        else:
            with st.form("form_crear_condominio"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nuevo_cond_id = st.text_input("ID del Condominio*", 
                        placeholder="COND-XXX-001",
                        help="Identificador único del condominio")
                    nuevo_nombre = st.text_input("Nombre*", 
                        placeholder="Residencial Las Palmas")
                    
                    # Selector de MSP
                    msp_options = {f"{msp[1]} ({msp[0]})": msp[0] for msp in msps_disponibles}
                    msp_seleccionado = st.selectbox("MSP*", 
                        options=list(msp_options.keys()),
                        help="Selecciona el MSP al que pertenecerá este condominio")
                    nuevo_msp = msp_options[msp_seleccionado]
                    
                    nueva_ciudad = st.text_input("Ciudad", 
                        placeholder="Ciudad de México")
                    nuevo_estado = st.text_input("Estado", 
                        placeholder="CDMX")
                
                with col2:
                    nueva_direccion = st.text_area("Dirección", 
                        placeholder="Calle, Colonia, CP")
                    nuevo_telefono = st.text_input("Teléfono", 
                        placeholder="+52 55 1234 5678")
                    nuevo_email = st.text_input("Email", 
                        placeholder="contacto@residencial.com")
                    nuevas_unidades = st.number_input("Total de Unidades", 
                        min_value=1, value=50, step=1)
                
                submit = st.form_submit_button("✅ Crear Condominio", use_container_width=True)
                
                if submit:
                    if not nuevo_cond_id or not nuevo_nombre or not nuevo_msp:
                        st.error("⚠️ Los campos marcados con * son obligatorios")
                    else:
                        try:
                            from core.db import get_db
                            from datetime import datetime
                            
                            with get_db() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO condominios_exo 
                                    (condominio_id, msp_id, nombre, direccion, ciudad, estado_mx, 
                                     telefono, email, total_unidades, estado, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', ?)
                                """, (nuevo_cond_id, nuevo_msp, nuevo_nombre, nueva_direccion,
                                      nueva_ciudad, nuevo_estado, nuevo_telefono, nuevo_email,
                                      nuevas_unidades, datetime.now().isoformat()))
                                conn.commit()
                            
                            st.success(f"✅ Condominio '{nuevo_nombre}' creado exitosamente!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al crear condominio: {e}")
    
    with tab_list:
        st.subheader("📋 Condominios Registrados")
        
        # Filtro por MSP
        col_filter1, col_filter2 = st.columns([3, 1])
        with col_filter1:
            filtro_msp = st.text_input("Filtrar por MSP ID:", 
                value=st.session_state.msp_id or "",
                placeholder="Dejar vacío para ver todos")
        with col_filter2:
            btn_refresh = st.button("🔄 Actualizar", use_container_width=True)
        
        # Listar condominios
        try:
            from core.db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                if filtro_msp:
                    cursor.execute("SELECT * FROM condominios_exo WHERE msp_id = ? ORDER BY created_at DESC", 
                                 (filtro_msp,))
                else:
                    cursor.execute("SELECT * FROM condominios_exo ORDER BY created_at DESC")
                
                condominios = cursor.fetchall()
                
                if condominios:
                    st.success(f"📊 Total de Condominios: {len(condominios)}")
                    
                    for cond in condominios:
                        with st.expander(f"🏘️ {cond[3]} ({cond[1]})", expanded=False):
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**ID:** {cond[1]}")
                                st.write(f"**MSP:** {cond[2]}")
                                st.write(f"**Ciudad:** {cond[5] or 'N/A'}")
                                st.write(f"**Estado:** {cond[6] or 'N/A'}")
                            
                            with col_info2:
                                st.write(f"**Teléfono:** {cond[8] or 'N/A'}")
                                st.write(f"**Email:** {cond[9] or 'N/A'}")
                                st.write(f"**Total Unidades:** {cond[10]}")
                                st.write(f"**Estado:** {cond[11]}")
                            
                            if cond[4]:  # Dirección
                                st.write(f"**Dirección:** {cond[4]}")
                else:
                    st.warning("📭 No hay condominios registrados")
                    st.info("💡 Crea tu primer condominio en la pestaña 'Nuevo Condominio'")
        except Exception as e:
            st.error(f"❌ Error cargando condominios: {e}")

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
