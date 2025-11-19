# modulos/eventos.py
"""
HISTORIAL DE EVENTOS (AUP-EXO)
Visualización de la bitácora estructural del sistema desde ledger_exo.
Versión PRO con jerarquía AUP-EXO y filtros avanzados.
"""

import streamlit as st
from core.db_exo import db_exo
from datetime import datetime


# ================================
#  CONSULTA PRINCIPAL DE EVENTOS
# ================================

def obtener_eventos(
    usuario,
    entidad=None,
    tipo_evento=None,
    usuario_id=None,
    fecha_inicio=None,
    fecha_fin=None,
    limite=300
):
    """
    Obtiene eventos del ledger con filtros jerárquicos AUP-EXO.

    Args:
        usuario: ContextoUsuario (con msp_id, condominio_id)
        entidad: tabla o entidad afectada (msps_exo, condominios_exo, visitantes_exo, etc.)
        tipo_evento: CREATE, UPDATE, DELETE, ACCESS
        usuario_id: filtrar por usuario generador
        fecha_inicio: fecha mínima
        fecha_fin: fecha máxima
        limite: número máximo de registros

    Returns:
        Lista de eventos (list[dict])
    """

    condiciones = []
    params = []

    # -----------------------------------------
    # Jerarquía AUP-EXO: filtro automático
    # -----------------------------------------
    if usuario.msp_id:
        condiciones.append("l.msp_id = %s")
        params.append(usuario.msp_id)

    if usuario.condominio_id:
        condiciones.append("l.condominio_id = %s")
        params.append(usuario.condominio_id)

    # -----------------------------------------
    # Filtros opcionales de la UI
    # -----------------------------------------
    if entidad:
        condiciones.append("l.entidad = %s")
        params.append(entidad)

    if tipo_evento:
        condiciones.append("l.accion = %s")
        params.append(tipo_evento)

    if usuario_id:
        condiciones.append("l.usuario_id = %s")
        params.append(usuario_id)

    if fecha_inicio:
        condiciones.append("l.timestamp >= %s")
        params.append(fecha_inicio)

    if fecha_fin:
        condiciones.append("l.timestamp <= %s")
        params.append(fecha_fin)

    # WHERE dinámico
    where = " AND ".join(condiciones)
    if where:
        where = "WHERE " + where

    query = f"""
        SELECT 
            l.ledger_id AS evento_id,
            l.entidad_id,
            l.entidad,
            l.accion AS tipo_evento,
            l.detalle AS metadata,
            l.timestamp,
            l.usuario_id,
            l.msp_id,
            l.condominio_id,
            l.ip_origen,
            l.user_agent
        FROM ledger_exo l
        {where}
        ORDER BY l.timestamp DESC
        LIMIT {limite}
    """

    return db_exo.execute_query(query, tuple(params), fetch="all")


# ================================
#  INTERFAZ DE USUARIO STREAMLIT
# ================================

def ui_eventos(usuario):
    """
    Interfaz principal de eventos con filtros avanzados.
    
    Args:
        usuario: ContextoUsuario con msp_id y condominio_id
    """
    st.title("📡 Eventos del Sistema (Ledger AUP-EXO)")

    st.info(
        "Vista unificada del ledger del sistema. Filtra por entidad, evento, usuario o fecha.", 
        icon="🗂️"
    )

    # -----------------------------------------
    # Filtros de la barra lateral
    # -----------------------------------------
    st.sidebar.subheader("🔍 Filtros")

    entidad = st.sidebar.selectbox(
        "Entidad",
        options=["", "msps_exo", "condominios_exo", "usuarios_exo", "visitantes_exo", 
                 "residentes_exo", "residencias_exo", "reglas_exo", "accesos_exo"],
        index=0
    )

    tipo_evento = st.sidebar.selectbox(
        "Tipo de evento",
        options=["", "CREATE", "UPDATE", "DELETE", "ACCESS", "LOGIN", "LOGOUT"],
        index=0
    )

    usuario_id = st.sidebar.text_input("Usuario ID")

    fecha_inicio = st.sidebar.date_input("Desde", value=None)
    fecha_fin = st.sidebar.date_input("Hasta", value=None)

    # Convertir fechas
    fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time()) if fecha_inicio else None
    fecha_fin = datetime.combine(fecha_fin, datetime.max.time()) if fecha_fin else None

    # -----------------------------------------
    # Ejecutar búsqueda
    # -----------------------------------------
    eventos = obtener_eventos(
        usuario=usuario,
        entidad=entidad if entidad else None,
        tipo_evento=tipo_evento if tipo_evento else None,
        usuario_id=usuario_id if usuario_id else None,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limite=400
    )

    # -----------------------------------------
    # Mostrar tabla
    # -----------------------------------------
    st.subheader("📋 Eventos encontrados")

    if not eventos:
        st.warning("No hay eventos con los filtros seleccionados.")
        return

    # Mostrar contador
    st.metric("Total de eventos", len(eventos))

    # Tabla visual
    st.dataframe(
        eventos,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------
    # Evento seleccionado (detalle abajo)
    # -----------------------------------------
    st.subheader("📄 Detalle del evento seleccionado")
    
    selected = st.selectbox(
        "Selecciona un evento para ver detalle",
        options=[e["evento_id"] for e in eventos]
    )

    if selected:
        ev = next((x for x in eventos if x["evento_id"] == selected), None)
        if ev:
            st.json(ev)
