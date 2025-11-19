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
from ui_state import reset_lower, safe_list, apply_pending_reset

# Configuración de página (debe estar primero)
st.set_page_config(
    page_title="AX-S Multi-Tenant - AUP-EXO",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar tablas multi-tenant solo una vez por sesión
try:
    from init_db_cloud import init_tables
    if 'MULTI_INIT_DONE' not in st.session_state:
        init_tables()
        st.session_state['MULTI_INIT_DONE'] = True
except Exception as e:
    st.warning(f"⚠️ No se pudieron inicializar tablas multi-tenant: {e}")

# Aplicar resets pendientes del ciclo anterior
apply_pending_reset()

# Funciones de caché para datos dinámicos
@st.cache_data(ttl=60)
def get_msps_list():
    """Obtener listado de MSPs desde la base de datos (seguro frente a 'no results to fetch')."""
    from core.db import get_db
    import os
    try:
        db_mode = os.getenv('DB_MODE') or (hasattr(st, 'secrets') and st.secrets.get('DB_MODE'))
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT msp_id, nombre FROM msps_exo WHERE estado = 'activo' ORDER BY nombre"
            cursor.execute(query)
            # Algunos entornos han mostrado ProgrammingError: no results to fetch; validar antes
            try:
                rows = cursor.fetchall() if getattr(cursor, 'description', None) else []
            except Exception as fe:
                # Si ocurre el error específico, tratamos como lista vacía y logueamos
                if 'no results to fetch' in str(fe):
                    st.warning("⚠️ Cursor sin result set tras SELECT; reintentar...")
                    # Reintentar una vez con nuevo cursor
                    cursor = conn.cursor()
                    cursor.execute(query)
                    rows = cursor.fetchall() if getattr(cursor, 'description', None) else []
                else:
                    raise fe
            if rows:
                first = rows[0]
                if isinstance(first, dict):
                    return [(r['msp_id'], r['nombre']) for r in rows]
                else:
                    return [(r[0], r[1]) for r in rows]
            return []
    except Exception as e:
        st.error(f"Error cargando MSPs: {e}")
        return []

@st.cache_data(ttl=60)
def get_condominios_by_msp(msp_id):
    """Obtener condominios de un MSP específico"""
    try:
        from core.db import get_db
        import os
        
        # Detectar tipo de base de datos
        db_mode = os.getenv('DB_MODE') or (hasattr(st, 'secrets') and st.secrets.get('DB_MODE'))
        is_postgres = db_mode in ['postgres', 'postgresql']
        placeholder = '%s' if is_postgres else '?'
        
        # Debug temporal
        st.info(f"🔍 DB_MODE={db_mode}, placeholder={placeholder}")
        
        with get_db() as conn:
            cursor = conn.cursor()
            query = f"SELECT condominio_id, nombre FROM condominios_exo WHERE msp_id = {placeholder} AND estado = 'activo' ORDER BY nombre"
            cursor.execute(query, (msp_id,))
            rows = cursor.fetchall()
            if rows:
                # Manejar tanto dict (PostgreSQL) como tuple (SQLite)
                if isinstance(rows[0], dict):
                    return [(row['condominio_id'], row['nombre']) for row in rows]
                else:
                    return [(row[0], row[1]) for row in rows]
            return []
    except Exception as e:
        st.error(f"Error cargando condominios: {e}")
        return []

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
if "msp_id" not in st.session_state:
    st.session_state["msp_id"] = None
if "condominio_id" not in st.session_state:
    st.session_state["condominio_id"] = None
if "rol_usuario" not in st.session_state:
    st.session_state["rol_usuario"] = "super_admin"

# Sidebar - Contexto Multi-Tenant
st.sidebar.title("🏢 AX-S Multi-Tenant")
st.sidebar.markdown("**Arquitectura AUP-EXO**")
st.sidebar.divider()

# Selector de contexto según rol
with st.sidebar.expander("🔐 Contexto de Trabajo", expanded=True):
    rol = st.selectbox(
        "Rol:",
        [
            "Super Admin (DS)",
            "MSP Admin (DD)",
            "Condominio Admin (SE)",
            "Admin Local (NO)",
        ],
        key="rol_selector",
        help="Selecciona tu nivel de acceso",
    )

    # SUPER ADMIN: sin contexto, ve todo
    if rol.startswith("Super Admin"):
        st.session_state["rol_usuario"] = "super_admin"
        st.session_state["msp_id"] = None
        st.session_state["condominio_id"] = None
        st.info("🌟 Acceso total sin fijar MSP/Condominio.")

    # MSP ADMIN: selecciona MSP y Condominio
    elif rol.startswith("MSP Admin"):
        st.session_state["rol_usuario"] = "msp_admin"

        # MSP
        msps = safe_list(get_msps_list())
        if not msps:
            st.warning("No hay MSPs activos configurados en la base.")
            st.session_state["msp_id"] = None
            st.session_state["condominio_id"] = None
        else:
            msp_labels = ["-- Seleccionar MSP --"] + [
                f"{msp_id} - {nombre}" for msp_id, nombre in msps
            ]

            msp_label = st.selectbox(
                "MSP",
                msp_labels,
                key="ctx_msp_admin_msp",
                on_change=lambda: reset_lower("msp"),
            )

            if msp_label != "-- Seleccionar MSP --":
                st.session_state["msp_id"] = msp_label.split(" - ", 1)[0]
            else:
                st.session_state["msp_id"] = None

            # CONDOMINIO
            if st.session_state["msp_id"]:
                condos = safe_list(get_condominios_by_msp(st.session_state["msp_id"]))
            else:
                condos = []

            condo_labels = ["-- Seleccionar Condominio --"] + [
                f"{cid} - {nombre}" for cid, nombre in condos
            ]

            condo_label = st.selectbox(
                "Condominio",
                condo_labels,
                key="ctx_msp_admin_condo",
                on_change=lambda: reset_lower("condominio"),
            )

            if condo_label != "-- Seleccionar Condominio --":
                st.session_state["condominio_id"] = condo_label.split(" - ", 1)[0]
            else:
                st.session_state["condominio_id"] = None

    # CONDOMINIO ADMIN: ya conoces el MSP, solo fija condominio
    elif rol.startswith("Condominio Admin"):
        st.session_state["rol_usuario"] = "condominio_admin"

        msps = safe_list(get_msps_list())
        msp_labels = ["-- Seleccionar MSP --"] + [
            f"{msp_id} - {nombre}" for msp_id, nombre in msps
        ]

        msp_label = st.selectbox(
            "MSP",
            msp_labels,
            key="ctx_condo_admin_msp",
            on_change=lambda: reset_lower("msp"),
        )

        if msp_label != "-- Seleccionar MSP --":
            st.session_state["msp_id"] = msp_label.split(" - ", 1)[0]
        else:
            st.session_state["msp_id"] = None

        if st.session_state["msp_id"]:
            condos = safe_list(get_condominios_by_msp(st.session_state["msp_id"]))
        else:
            condos = []

        condo_labels = ["-- Seleccionar Condominio --"] + [
            f"{cid} - {nombre}" for cid, nombre in condos
        ]

        condo_label = st.selectbox(
            "Condominio",
            condo_labels,
            key="ctx_condo_admin_condo",
            on_change=lambda: reset_lower("condominio"),
        )

        if condo_label != "-- Seleccionar Condominio --":
            st.session_state["condominio_id"] = condo_label.split(" - ", 1)[0]
        else:
            st.session_state["condominio_id"] = None

    # ADMIN LOCAL: se asume condominio ya fijado por otro flujo
    else:
        st.session_state["rol_usuario"] = "admin_local"
        st.info(
            "Modo Admin Local: se asume contexto de condominio fijado por otro flujo."
        )

# ----------------------------------------------------------------------
# RESUMEN DEL CONTEXTO SELECCIONADO (debajo del selector)
# ----------------------------------------------------------------------
st.sidebar.divider()

# Mostrar confirmación visual del contexto activo
msp_actual = st.session_state.get("msp_id")
condo_actual = st.session_state.get("condominio_id")
rol_actual = st.session_state.get("rol_usuario", "super_admin")

if rol_actual == "super_admin":
    st.sidebar.success("✅ **Contexto:** Super Admin (Todo)")
elif msp_actual and condo_actual:
    st.sidebar.success(f"✅ **MSP:** `{msp_actual}`\n\n✅ **Condominio:** `{condo_actual}`")
elif msp_actual:
    st.sidebar.warning(f"✅ **MSP:** `{msp_actual}`\n\n⚠️ **Condominio:** Sin seleccionar")
else:
    st.sidebar.warning("⚠️ **Contexto incompleto**\n\nSelecciona MSP/Condominio arriba")

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
    
    # Obtener contexto
    msp_id_actual = st.session_state.get('msp_id')
    rol_actual = st.session_state.get('rol_usuario', 'super_admin')
    
    # Mostrar banner de contexto
    if rol_actual != 'super_admin' and msp_id_actual:
        st.info(f"🏢 **Viendo solo tu MSP:** `{msp_id_actual}`")
    elif rol_actual == 'super_admin':
        st.success("👑 **Super Admin:** Viendo todos los MSPs")
    else:
        st.warning("⚠️ Selecciona un MSP en el contexto del sidebar")
    
    st.divider()
    
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
                            
                            # Verificar si ya existe
                            cursor.execute("SELECT COUNT(*) FROM msps_exo WHERE msp_id = ?", (nuevo_msp_id,))
                            if cursor.fetchone()[0] > 0:
                                st.error(f"⚠️ Ya existe un MSP con ID '{nuevo_msp_id}'")
                            else:
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
                
                # Filtrar por contexto
                if rol_actual == 'super_admin':
                    # Super Admin ve todos
                    cursor.execute("SELECT * FROM msps_exo ORDER BY created_at DESC")
                elif msp_id_actual:
                    # MSP Admin solo ve su propio MSP
                    cursor.execute("SELECT * FROM msps_exo WHERE msp_id = ? ORDER BY created_at DESC", (msp_id_actual,))
                else:
                    # Sin contexto, no mostrar nada
                    rows = []
                    
                rows = cursor.fetchall()
                
                # Normalizar datos independientemente del formato
                msps = []
                if rows:
                    for row in rows:
                        if isinstance(row, dict):
                            msps.append(row)
                        else:
                            # Convertir tupla a dict para acceso consistente
                            # Orden: id, msp_id, nombre, razon_social, rfc, email_contacto, 
                            #        telefono_contacto, estado, plan, max_condominios, created_at, updated_at
                            msps.append({
                                'id': row[0] if len(row) > 0 else None,
                                'msp_id': row[1] if len(row) > 1 else None,
                                'nombre': row[2] if len(row) > 2 else None,
                                'razon_social': row[3] if len(row) > 3 else None,
                                'rfc': row[4] if len(row) > 4 else None,
                                'email_contacto': row[5] if len(row) > 5 else None,
                                'telefono_contacto': row[6] if len(row) > 6 else None,
                                'estado': row[7] if len(row) > 7 else None,
                                'plan': row[8] if len(row) > 8 else None,
                                'max_condominios': row[9] if len(row) > 9 else None,
                            })
                
                if msps:
                    st.success(f"📊 Total de MSPs: {len(msps)}")
                    
                    for msp in msps:
                        with st.expander(f"🏢 {msp['nombre']} ({msp['msp_id']})", expanded=False):
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**ID:** {msp['msp_id']}")
                                st.write(f"**Razón Social:** {msp['razon_social'] or 'N/A'}")
                                st.write(f"**RFC:** {msp['rfc'] or 'N/A'}")
                                st.write(f"**Email:** {msp['email_contacto']}")
                            
                            with col_info2:
                                st.write(f"**Teléfono:** {msp['telefono_contacto'] or 'N/A'}")
                                st.write(f"**Plan:** {msp['plan']}")
                                st.write(f"**Estado:** {msp['estado']}")
                                st.write(f"**Max Condominios:** {msp['max_condominios']}")
                else:
                    st.warning("📭 No hay MSPs registrados")
                    st.info("💡 Crea tu primer MSP en la pestaña 'Nuevo MSP'")
        except Exception as e:
            st.error(f"❌ Error cargando MSPs: {e}")

elif opcion == "🏘️ Gestión Condominios":
    st.title("🏘️ Gestión de Condominios")
    
    # Obtener contexto
    msp_id_actual = st.session_state.get('msp_id')
    condo_id_actual = st.session_state.get('condominio_id')
    rol_actual = st.session_state.get('rol_usuario', 'super_admin')
    
    # Mostrar banner de contexto
    if rol_actual == 'super_admin':
        st.success("👑 **Super Admin:** Viendo todos los Condominios")
    elif msp_id_actual and condo_id_actual:
        st.info(f"🏘️ **Viendo solo:** MSP `{msp_id_actual}` → Condominio `{condo_id_actual}`")
    elif msp_id_actual:
        st.info(f"🏢 **Viendo condominios del MSP:** `{msp_id_actual}`")
    else:
        st.warning("⚠️ Selecciona un MSP en el contexto del sidebar")
    
    st.divider()
    
    # Tabs para organizar funcionalidad
    tab_list, tab_create = st.tabs(["📋 Listado", "➕ Nuevo Condominio"])
    
    with tab_create:
        st.subheader("➕ Crear Nuevo Condominio")
        
        # Obtener lista de MSPs disponibles (respetando contexto del usuario)
        try:
            from core.db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Filtrar MSPs según el contexto del usuario
                if rol_actual == "super_admin":
                    # Super Admin ve todos los MSPs
                    cursor.execute("SELECT msp_id, nombre FROM msps_exo WHERE estado = 'activo' ORDER BY nombre")
                elif msp_id_actual:
                    # MSP Admin solo puede crear condominios para su propio MSP
                    cursor.execute("SELECT msp_id, nombre FROM msps_exo WHERE msp_id = ? AND estado = 'activo' ORDER BY nombre",
                                 (msp_id_actual,))
                else:
                    # Sin contexto, no mostrar MSPs
                    cursor.execute("SELECT msp_id, nombre FROM msps_exo WHERE 1=0")
                
                rows = cursor.fetchall()
                
                # Convertir a lista de tuplas independientemente del formato
                msps_disponibles = []
                if rows:
                    for row in rows:
                        if isinstance(row, dict):
                            msps_disponibles.append((row['msp_id'], row['nombre']))
                        else:
                            msps_disponibles.append((row[0], row[1]))
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
                    msp_options = {f"{nombre} ({msp_id})": msp_id for msp_id, nombre in msps_disponibles}
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
                                
                                # Verificar si ya existe
                                cursor.execute("SELECT COUNT(*) FROM condominios_exo WHERE condominio_id = ?", (nuevo_cond_id,))
                                if cursor.fetchone()[0] > 0:
                                    st.error(f"⚠️ Ya existe un condominio con ID '{nuevo_cond_id}'")
                                else:
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
        
        # Listar condominios (respetando contexto del usuario)
        try:
            from core.db import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Filtrar según el contexto del usuario
                if rol_actual == "super_admin":
                    # Super Admin ve todos los condominios
                    if filtro_msp:
                        cursor.execute("SELECT * FROM condominios_exo WHERE msp_id = ? ORDER BY created_at DESC", 
                                     (filtro_msp,))
                    else:
                        cursor.execute("SELECT * FROM condominios_exo ORDER BY created_at DESC")
                elif condo_id_actual:
                    # Condominio Admin solo ve su condominio
                    cursor.execute("SELECT * FROM condominios_exo WHERE condominio_id = ? ORDER BY created_at DESC",
                                 (condo_id_actual,))
                elif msp_id_actual:
                    # MSP Admin solo ve condominios de su MSP
                    cursor.execute("SELECT * FROM condominios_exo WHERE msp_id = ? ORDER BY created_at DESC",
                                 (msp_id_actual,))
                else:
                    # Sin contexto, no mostrar nada
                    cursor.execute("SELECT * FROM condominios_exo WHERE 1=0")
                
                rows = cursor.fetchall()
                
                # Normalizar datos independientemente del formato
                condominios = []
                if rows:
                    for row in rows:
                        if isinstance(row, dict):
                            condominios.append(row)
                        else:
                            # Convertir tupla a dict para acceso consistente
                            # Orden: id, condominio_id, msp_id, nombre, direccion, ciudad, estado_mx, 
                            #        cp, telefono, email, total_unidades, estado, created_at, updated_at
                            condominios.append({
                                'id': row[0] if len(row) > 0 else None,
                                'condominio_id': row[1] if len(row) > 1 else None,
                                'msp_id': row[2] if len(row) > 2 else None,
                                'nombre': row[3] if len(row) > 3 else None,
                                'direccion': row[4] if len(row) > 4 else None,
                                'ciudad': row[5] if len(row) > 5 else None,
                                'estado_mx': row[6] if len(row) > 6 else None,
                                'cp': row[7] if len(row) > 7 else None,
                                'telefono': row[8] if len(row) > 8 else None,
                                'email': row[9] if len(row) > 9 else None,
                                'total_unidades': row[10] if len(row) > 10 else None,
                                'estado': row[11] if len(row) > 11 else None,
                            })
                
                if condominios:
                    st.success(f"📊 Total de Condominios: {len(condominios)}")
                    
                    for cond in condominios:
                        with st.expander(f"🏘️ {cond['nombre']} ({cond['condominio_id']})", expanded=False):
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.write(f"**ID:** {cond['condominio_id']}")
                                st.write(f"**MSP:** {cond['msp_id']}")
                                st.write(f"**Ciudad:** {cond['ciudad'] or 'N/A'}")
                                st.write(f"**Estado:** {cond['estado_mx'] or 'N/A'}")
                            
                            with col_info2:
                                st.write(f"**Teléfono:** {cond['telefono'] or 'N/A'}")
                                st.write(f"**Email:** {cond['email'] or 'N/A'}")
                                st.write(f"**Total Unidades:** {cond['total_unidades']}")
                                st.write(f"**Estado:** {cond['estado']}")
                            
                            if cond['direccion']:
                                st.write(f"**Dirección:** {cond['direccion']}")
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
