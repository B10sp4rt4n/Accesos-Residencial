# modulos/eventos.py
"""
HISTORIAL DE EVENTOS (AUP-EXO)
Visualización de la bitácora estructural de ENTIDADES.
"""

import json
import streamlit as st
from core.db import get_db


# ---------------------------------------------------------------------
# Obtener eventos desde la base
# ---------------------------------------------------------------------
def obtener_eventos(tipo=None):
    with get_db() as db:
        if tipo:
            rows = db.execute("""
                SELECT e.evento_id, e.entidad_id, e.tipo_evento, e.metadata,
                       e.actor, e.dispositivo, e.timestamp_servidor,
                       e.hash_actual, 
                       en.tipo AS tipo_entidad,
                       en.atributos
                FROM eventos e
                JOIN entidades en ON en.entidad_id = e.entidad_id
                WHERE e.tipo_evento = ?
                ORDER BY e.evento_id DESC
            """, (tipo,)).fetchall()
        else:
            rows = db.execute("""
                SELECT e.evento_id, e.entidad_id, e.tipo_evento, e.metadata,
                       e.actor, e.dispositivo, e.timestamp_servidor,
                       e.hash_actual,
                       en.tipo AS tipo_entidad,
                       en.atributos
                FROM eventos e
                JOIN entidades en ON en.entidad_id = e.entidad_id
                ORDER BY e.evento_id DESC
            """).fetchall()

    # Convertir a dicts y extraer nombre/identificador del JSON
    eventos = []
    for r in rows:
        evento = dict(r)
        
        # Parsear atributos JSON
        if evento.get('atributos'):
            try:
                atributos = json.loads(evento['atributos'])
                evento['nombre'] = atributos.get('nombre', 'N/A')
                evento['identificador'] = atributos.get('identificador') or atributos.get('placa') or atributos.get('folio') or 'N/A'
            except json.JSONDecodeError:
                evento['nombre'] = 'N/A'
                evento['identificador'] = 'N/A'
        else:
            evento['nombre'] = 'N/A'
            evento['identificador'] = 'N/A'
        
        eventos.append(evento)
    
    return eventos


# ---------------------------------------------------------------------
# UI principal del historial
# ---------------------------------------------------------------------
def ui_eventos():

    st.header("📊 Historial de Eventos (AUP-EXO)")

    # ---------------- FILTRO POR TIPO -----------------
    tipo = st.selectbox(
        "Filtrar por tipo de evento",
        ["Todos", "entrada", "salida", "rechazo", "incidente"]
    )

    filtro = None if tipo == "Todos" else tipo

    eventos = obtener_eventos(filtro)

    if not eventos:
        st.info("No hay eventos registrados todavía.")
        return

    # --------- TABLA PRINCIPAL ------------------------
    st.subheader("🔍 Bitácora estructural de accesos")

    tabla = []
    for e in eventos:
        metadata = json.loads(e["metadata"]) if e["metadata"] else {}
        tabla.append({
            "ID Evento": e["evento_id"],
            "Entidad": f"{e['tipo_entidad'].upper()} - {e['nombre']}",
            "Identificador": e["identificador"],
            "Tipo de Evento": e["tipo_evento"],
            "Actor": e["actor"],
            "Dispositivo": e["dispositivo"],
            "Hora": metadata.get("hora", ""),
            "Fecha": metadata.get("fecha", ""),
            "Hash": e["hash_actual"][:12] + "...",
            "Timestamp Servidor": e["timestamp_servidor"]
        })

    st.dataframe(tabla, height=400)

    # ----------- DETALLE ESTRUCTURAL -------------------
    st.subheader("🔬 Detalle estructural del evento seleccionado")

    ids = [e["evento_id"] for e in eventos]
    selected_id = st.selectbox("Selecciona ID de evento:", ids)

    seleccionado = next(ev for ev in eventos if ev["evento_id"] == selected_id)

    st.write("### Información de la Entidad vinculada")
    st.json({
        "ID Entidad": seleccionado["entidad_id"],
        "Tipo": seleccionado["tipo_entidad"],
        "Nombre": seleccionado["nombre"],
        "Identificador": seleccionado["identificador"]
    })

    st.write("### Metadata del evento")
    st.json(json.loads(seleccionado["metadata"]))

    st.write("### Datos estructurales")
    st.json({
        "Actor": seleccionado["actor"],
        "Dispositivo": seleccionado["dispositivo"],
        "Timestamp servidor": seleccionado["timestamp_servidor"],
        "Hash estructural": seleccionado["hash_actual"]
    })
