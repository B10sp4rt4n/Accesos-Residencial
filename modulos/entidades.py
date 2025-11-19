# modulos/entidades.py
"""
Módulo universal de ENTIDADES para Accesos-Residencial
AUP-EXO: modelo estructural unificado para personas, vehículos y visitas.
"""

import json
import streamlit as st
from datetime import datetime
from core.db import get_db
from core.hashing import hash_evento

# ------------------------------------------------------------------
# Crear una nueva entidad
# ------------------------------------------------------------------

def crear_entidad(tipo, nombre=None, identificador=None, atributos=None, msp_id=None, condominio_id=None):
    """
    Crea una nueva entidad en el sistema AUP-EXO con contexto multi-tenant
    
    Args:
        tipo: Tipo de entidad (persona, vehiculo, visita, proveedor, etc.)
        nombre: Nombre descriptivo de la entidad
        identificador: Identificador único (placa, folio, teléfono, etc.)
        atributos: Diccionario con atributos adicionales
        msp_id: ID del MSP (contexto multi-tenant)
        condominio_id: ID del Condominio (contexto multi-tenant)
    
    Returns:
        Tupla (entidad_id, hash)
    """
    atributos = atributos or {}

    entidad_data = {
        "tipo": tipo,
        "nombre": nombre,
        "identificador": identificador,
        "atributos": atributos,
        "timestamp": datetime.utcnow().isoformat()
    }

    entidad_hash = hash_evento(entidad_data)
    
    # Generar ID único para la entidad
    timestamp_str = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    entidad_id = f"ENT_{tipo[:3].upper()}_{timestamp_str}_{entidad_hash[:8]}"

    timestamp = datetime.utcnow().isoformat()
    
    with get_db() as db:
        db.execute("""
            INSERT INTO entidades (
                entidad_id, tipo, atributos, hash_actual, 
                fecha_creacion, fecha_actualizacion, estado,
                msp_id, condominio_id
            )
            VALUES (?, ?, ?, ?, ?, ?, 'activo', ?, ?)
        """, (
            entidad_id,
            tipo,
            json.dumps({
                "nombre": nombre,
                "identificador": identificador,
                **atributos
            }),
            entidad_hash,
            timestamp,
            timestamp,
            msp_id,
            condominio_id
        ))

    return entidad_id, entidad_hash


# ------------------------------------------------------------------
# Obtener todas las entidades
# ------------------------------------------------------------------

def obtener_entidades(tipo=None, estado='activo', msp_id=None, condominio_id=None):
    """
    Obtiene entidades del sistema con filtrado multi-tenant
    
    Args:
        tipo: Filtrar por tipo de entidad (opcional)
        estado: Filtrar por estado (activo/inactivo/todos)
        msp_id: Filtrar por MSP (opcional, None = todos)
        condominio_id: Filtrar por Condominio (opcional, None = todos)
    
    Returns:
        Lista de entidades como diccionarios
    """
    query = "SELECT * FROM entidades WHERE 1=1"
    params = []

    # Filtrado multi-tenant
    if msp_id:
        query += " AND msp_id = ?"
        params.append(msp_id)
    
    if condominio_id:
        query += " AND condominio_id = ?"
        params.append(condominio_id)

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    if estado and estado != 'todos':
        query += " AND estado = ?"
        params.append(estado)
    
    query += " ORDER BY fecha_creacion DESC"

    with get_db() as db:
        rows = db.execute(query, params).fetchall()

    entidades = []
    for row in rows:
        entidad = dict(row)
        # Parsear atributos JSON
        if entidad.get('atributos'):
            try:
                entidad['atributos'] = json.loads(entidad['atributos'])
            except:
                entidad['atributos'] = {}
        entidades.append(entidad)
    
    return entidades


# ------------------------------------------------------------------
# Buscar entidad por ID
# ------------------------------------------------------------------

def obtener_entidad_por_id(entidad_id):
    """
    Obtiene una entidad específica por su ID
    
    Args:
        entidad_id: ID de la entidad
    
    Returns:
        Diccionario con datos de la entidad o None
    """
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM entidades WHERE entidad_id = ?",
            (entidad_id,)
        ).fetchone()
    
    if row:
        entidad = dict(row)
        if entidad.get('atributos'):
            try:
                entidad['atributos'] = json.loads(entidad['atributos'])
            except:
                entidad['atributos'] = {}
        return entidad
    return None


# ------------------------------------------------------------------
# Buscar entidad por identificador
# ------------------------------------------------------------------

def buscar_entidad_por_identificador(identificador, tipo=None):
    """
    Busca entidad por identificador (placa, folio, etc.)
    
    Args:
        identificador: Identificador a buscar
        tipo: Tipo de entidad (opcional)
    
    Returns:
        Entidad encontrada o None
    """
    query = """
        SELECT * FROM entidades 
        WHERE json_extract(atributos, '$.identificador') = ? 
        AND estado = 'activo'
    """
    params = [identificador]
    
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    with get_db() as db:
        row = db.execute(query, params).fetchone()
    
    if row:
        entidad = dict(row)
        if entidad.get('atributos'):
            try:
                entidad['atributos'] = json.loads(entidad['atributos'])
            except:
                entidad['atributos'] = {}
        return entidad
    return None


# ------------------------------------------------------------------
# Actualizar entidad
# ------------------------------------------------------------------

def actualizar_entidad(entidad_id, nombre=None, identificador=None, atributos=None):
    """
    Actualiza una entidad existente preservando trazabilidad
    
    Args:
        entidad_id: ID de la entidad a actualizar
        nombre: Nuevo nombre (opcional)
        identificador: Nuevo identificador (opcional)
        atributos: Nuevos atributos (opcional)
    
    Returns:
        Nuevo hash de la entidad
    """
    # Obtener entidad actual
    entidad_actual = obtener_entidad_por_id(entidad_id)
    if not entidad_actual:
        raise ValueError(f"Entidad {entidad_id} no encontrada")
    
    # Parse atributos actuales safely (puede ser None, string JSON, o dict)
    atributos_raw = entidad_actual.get('atributos')
    if atributos_raw:
        try:
            if isinstance(atributos_raw, str):
                atributos_actuales = json.loads(atributos_raw)
            else:
                atributos_actuales = atributos_raw if isinstance(atributos_raw, dict) else {}
        except (json.JSONDecodeError, TypeError):
            atributos_actuales = {}
    else:
        atributos_actuales = {}
    
    atributos_nuevos = atributos or {}
    
    if nombre:
        atributos_nuevos['nombre'] = nombre
    if identificador:
        atributos_nuevos['identificador'] = identificador
    
    atributos_finales = {**atributos_actuales, **atributos_nuevos}
    
    # Generar nuevo hash
    entidad_data = {
        "entidad_id": entidad_id,
        "tipo": entidad_actual['tipo'],
        "atributos": atributos_finales,
        "timestamp": datetime.utcnow().isoformat(),
        "hash_previo": entidad_actual['hash_actual']
    }
    
    nuevo_hash = hash_evento(entidad_data)
    timestamp = datetime.utcnow().isoformat()

    with get_db() as db:
        db.execute("""
            UPDATE entidades
            SET atributos = ?, 
                fecha_actualizacion = ?,
                hash_previo = hash_actual, 
                hash_actual = ?
            WHERE entidad_id = ?
        """, (
            json.dumps(atributos_finales),
            timestamp,
            nuevo_hash,
            entidad_id
        ))

    return nuevo_hash


# ------------------------------------------------------------------
# Eliminar entidad (desactivar, no borrar físicamente)
# ------------------------------------------------------------------

def desactivar_entidad(entidad_id):
    """
    Desactiva una entidad sin borrarla físicamente
    Mantiene trazabilidad completa
    
    Args:
        entidad_id: ID de la entidad a desactivar
    
    Returns:
        True si se desactivó correctamente
    """
    timestamp = datetime.utcnow().isoformat()
    
    with get_db() as db:
        db.execute("""
            UPDATE entidades
            SET estado = 'inactivo',
                fecha_actualizacion = ?
            WHERE entidad_id = ?
        """, (timestamp, entidad_id,))

    return True


# ------------------------------------------------------------------
# Reactivar entidad
# ------------------------------------------------------------------

def reactivar_entidad(entidad_id):
    """
    Reactiva una entidad previamente desactivada
    
    Args:
        entidad_id: ID de la entidad a reactivar
    
    Returns:
        True si se reactivó correctamente
    """
    timestamp = datetime.utcnow().isoformat()
    
    with get_db() as db:
        db.execute("""
            UPDATE entidades
            SET estado = 'activo',
                fecha_actualizacion = ?
            WHERE entidad_id = ?
        """, (timestamp, entidad_id,))

    return True


# ------------------------------------------------------------------
# Interfaz Streamlit para administración básica
# ------------------------------------------------------------------

def ui_gestion_entidades():
    """
    Interfaz de usuario para gestión de entidades
    Compatible con arquitectura AUP-EXO
    """
    st.header("🏢 Gestión de Entidades")
    st.markdown("**Modelo Universal AUP-EXO:** Personas, Vehículos, Visitas, Proveedores")

    # Tabs para diferentes acciones
    tab1, tab2, tab3 = st.tabs(["➕ Crear", "📋 Consultar", "✏️ Actualizar"])
    
    # TAB 1: CREAR ENTIDAD
    with tab1:
        st.subheader("Crear Nueva Entidad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox(
                "Tipo de entidad",
                ["persona", "vehiculo", "visita", "proveedor", "trabajador", "otro"]
            )
            nombre = st.text_input("Nombre / Descripción")
        
        with col2:
            identificador = st.text_input("Identificador (placa, folio, teléfono, etc.)")
            
        st.markdown("**Atributos Adicionales (JSON)**")
        atributos_raw = st.text_area(
            "Atributos opcionales",
            value='{}',
            height=100,
            help="Ejemplo: {\"telefono\": \"5512345678\", \"direccion\": \"Casa 15\"}"
        )

        try:
            atributos = json.loads(atributos_raw)
            atributos_validos = True
        except:
            st.error("⚠️ Atributos mal formateados. Debe ser JSON válido.")
            atributos_validos = False

        if st.button("✅ Crear Entidad", type="primary"):
            if not nombre:
                st.error("El nombre es obligatorio")
            elif not atributos_validos:
                st.error("Corrige el formato JSON de atributos")
            else:
                try:
                    entidad_id, hash_entidad = crear_entidad(
                        tipo=tipo,
                        nombre=nombre,
                        identificador=identificador,
                        atributos=atributos
                    )
                    st.success(f"✅ Entidad creada exitosamente")
                    st.info(f"**ID:** `{entidad_id}`")
                    st.info(f"**Hash:** `{hash_entidad[:16]}...`")
                except Exception as e:
                    st.error(f"Error al crear entidad: {str(e)}")
    
    # TAB 2: CONSULTAR ENTIDADES
    with tab2:
        st.subheader("Entidades Registradas")
        
        col1, col2 = st.columns(2)
        with col1:
            filtro_tipo = st.selectbox(
                "Filtrar por tipo",
                ["todos", "persona", "vehiculo", "visita", "proveedor", "trabajador"],
                key="filtro_tipo"
            )
        with col2:
            filtro_estado = st.selectbox(
                "Estado",
                ["activo", "inactivo", "todos"],
                key="filtro_estado"
            )
        
        # Aplicar filtros
        tipo_query = None if filtro_tipo == "todos" else filtro_tipo
        estado_query = filtro_estado
        
        entidades = obtener_entidades(tipo=tipo_query, estado=estado_query)
        
        if entidades:
            st.metric("Total de entidades", len(entidades))
            
            # Mostrar en tabla
            for entidad in entidades:
                # Parse atributos safely (puede ser None, string JSON, o dict)
                atributos_raw = entidad.get('atributos')
                if atributos_raw:
                    try:
                        if isinstance(atributos_raw, str):
                            attrs = json.loads(atributos_raw)
                        else:
                            attrs = atributos_raw if isinstance(atributos_raw, dict) else {}
                    except (json.JSONDecodeError, TypeError):
                        attrs = {}
                else:
                    attrs = {}
                
                nombre_display = attrs.get('nombre', 'Sin nombre')
                id_display = attrs.get('identificador', 'Sin ID')
                
                with st.expander(
                    f"{entidad['tipo'].upper()} - {nombre_display} ({id_display})"
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**ID:** `{entidad['entidad_id']}`")
                        st.write(f"**Tipo:** {entidad['tipo']}")
                        st.write(f"**Estado:** {entidad['estado']}")
                    with col_b:
                        st.write(f"**Creado:** {entidad['fecha_creacion']}")
                        st.write(f"**Actualizado:** {entidad['fecha_actualizacion']}")
                        hash_val = entidad.get('hash_actual', '')
                        if hash_val:
                            st.write(f"**Hash:** `{hash_val[:16]}...`")
                        else:
                            st.write(f"**Hash:** `Sin hash`")
                    
                    st.json(attrs)
        else:
            st.info("📭 No hay entidades registradas con estos filtros.")
    
    # TAB 3: ACTUALIZAR/DESACTIVAR
    with tab3:
        st.subheader("Actualizar o Desactivar Entidad")
        
        entidad_id_actualizar = st.text_input("ID de la entidad")
        
        if entidad_id_actualizar:
            entidad = obtener_entidad_por_id(entidad_id_actualizar)
            
            if entidad:
                st.success(f"✅ Entidad encontrada: **{entidad['tipo']}**")
                
                # Parse atributos safely (puede ser None, string JSON, o dict)
                atributos_raw = entidad.get('atributos')
                if atributos_raw:
                    try:
                        if isinstance(atributos_raw, str):
                            attrs = json.loads(atributos_raw)
                        else:
                            attrs = atributos_raw if isinstance(atributos_raw, dict) else {}
                    except (json.JSONDecodeError, TypeError):
                        attrs = {}
                else:
                    attrs = {}
                
                st.json(attrs)
                
                st.markdown("---")
                nuevo_nombre = st.text_input(
                    "Nuevo nombre (dejar vacío para no cambiar)",
                    value=attrs.get('nombre', '')
                )
                nuevo_identificador = st.text_input(
                    "Nuevo identificador (dejar vacío para no cambiar)",
                    value=attrs.get('identificador', '')
                )
                
                nuevos_atributos_raw = st.text_area(
                    "Nuevos atributos (JSON)",
                    value=json.dumps(attrs, indent=2),
                    height=150
                )
                
                col_update, col_deactivate = st.columns(2)
                
                with col_update:
                    if st.button("💾 Actualizar", type="primary"):
                        try:
                            nuevos_atributos = json.loads(nuevos_atributos_raw)
                            nuevo_hash = actualizar_entidad(
                                entidad_id_actualizar,
                                nombre=nuevo_nombre if nuevo_nombre else None,
                                identificador=nuevo_identificador if nuevo_identificador else None,
                                atributos=nuevos_atributos
                            )
                            st.success(f"✅ Entidad actualizada. Nuevo hash: `{nuevo_hash[:16]}...`")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                with col_deactivate:
                    if entidad['estado'] == 'activo':
                        if st.button("🚫 Desactivar", type="secondary"):
                            desactivar_entidad(entidad_id_actualizar)
                            st.success("✅ Entidad desactivada")
                            st.rerun()
                    else:
                        if st.button("✅ Reactivar", type="secondary"):
                            reactivar_entidad(entidad_id_actualizar)
                            st.success("✅ Entidad reactivada")
                            st.rerun()
            else:
                st.error("❌ Entidad no encontrada")


# ------------------------------------------------------------------
# ALIAS para compatibilidad con código anterior
# ------------------------------------------------------------------

def render_personas():
    """Alias de compatibilidad - redirige a ui_gestion_entidades"""
    ui_gestion_entidades()

def render_vehiculos():
    """Alias de compatibilidad - redirige a ui_gestion_entidades"""
    ui_gestion_entidades()
