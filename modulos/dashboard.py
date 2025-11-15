"""
DASHBOARD AUP-EXO
Visualización estructural del sistema de accesos.
"""

import json
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, date
from core.db import get_db
from modulos.analitica import resumen_analitico


# ----------------------------------------------------
# Helpers
# ----------------------------------------------------
def _get_eventos_df():
    with get_db() as db:
        rows = db.execute("""
            SELECT e.evento_id, e.entidad_id, e.tipo_evento, e.metadata,
                   e.actor, e.dispositivo, e.timestamp_servidor,
                   e.hash_actual, en.tipo AS tipo_entidad, en.atributos
            FROM eventos e
            JOIN entidades en ON en.entidad_id = e.entidad_id
            ORDER BY evento_id DESC
        """).fetchall()

    if not rows:
        return pd.DataFrame()

    data = []
    for r in rows:
        metadata = json.loads(r["metadata"]) if r["metadata"] else {}
        atributos = json.loads(r["atributos"]) if r["atributos"] else {}
        
        # Extraer nombre e identificador del JSON de atributos
        nombre = atributos.get("nombre", "N/A")
        identificador = (atributos.get("identificador") or 
                        atributos.get("placa") or 
                        atributos.get("folio") or "N/A")
        
        data.append({
            "evento_id": r["evento_id"],
            "entidad_id": r["entidad_id"],
            "tipo_evento": r["tipo_evento"],
            "nombre": nombre,
            "identificador": identificador,
            "tipo_entidad": r["tipo_entidad"],
            "actor": r["actor"],
            "dispositivo": r["dispositivo"],
            "hora": metadata.get("hora", ""),
            "fecha": metadata.get("fecha", ""),
            "timestamp": r["timestamp_servidor"],
            "politica_rechazo": metadata.get("motivo_rechazo", ""),
            "hash": r["hash_actual"]
        })
    return pd.DataFrame(data)


# ----------------------------------------------------
# UI Principal
# ----------------------------------------------------
def ui_dashboard():

    st.header("Dashboard AUP-EXO")
    df = _get_eventos_df()

    if df.empty:
        st.info("No hay eventos para mostrar en el dashboard.")
        return

    # Convertir tipos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    hoy = date.today()
    df_hoy = df[df["fecha"].dt.date == hoy]

    # ------------------------------------------------
    # KPIs
    # ------------------------------------------------
    st.subheader("Indicadores del Día")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Accesos Permitidos", df_hoy[df_hoy["tipo_evento"] == "entrada"].shape[0])

    with col2:
        st.metric("Accesos Rechazados", df_hoy[df_hoy["tipo_evento"] == "rechazo"].shape[0])

    with col3:
        st.metric("Total Eventos Hoy", df_hoy.shape[0])

    # ------------------------------------------------
    # ANALÍTICA: COMPARACIÓN T-1 VS T0
    # ------------------------------------------------
    st.divider()
    st.subheader("📊 Analítica Estructural")
    
    # Obtener resumen analítico
    resumen = resumen_analitico()
    
    # Comparación temporal
    if resumen.get('t1_t0'):
        st.markdown("**Comparación T-1 vs T0**")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            t1_t0 = resumen['t1_t0']
            entradas_hoy = t1_t0.get('entradas_hoy', 0)
            entradas_ayer = t1_t0.get('entradas_ayer', 0)
            var_entradas = t1_t0.get('variacion_entradas', 0)
            
            st.metric(
                "Entradas Hoy vs Ayer",
                f"{entradas_hoy}",
                f"{var_entradas:+.1f}% vs ayer ({entradas_ayer})"
            )
        
        with col_t2:
            rechazos_hoy = t1_t0.get('rechazos_hoy', 0)
            rechazos_ayer = t1_t0.get('rechazos_ayer', 0)
            var_rechazos = t1_t0.get('variacion_rechazos', 0)
            
            st.metric(
                "Rechazos Hoy vs Ayer",
                f"{rechazos_hoy}",
                f"{var_rechazos:+.1f}% vs ayer ({rechazos_ayer})"
            )
    
    # Anomalías detectadas
    if resumen.get('anomalias'):
        st.markdown("**🔍 Anomalías Detectadas**")
        
        anomalias = resumen['anomalias']
        
        # Agrupar por nivel
        anomalias_alto = [a for a in anomalias if a['nivel'] == 'alto']
        anomalias_medio = [a for a in anomalias if a['nivel'] == 'medio']
        anomalias_bajo = [a for a in anomalias if a['nivel'] == 'bajo']
        
        if anomalias_alto:
            st.error(f"🔴 **{len(anomalias_alto)} anomalías de nivel ALTO**")
            for a in anomalias_alto[:3]:
                st.markdown(f"- **{a['tipo'].replace('_', ' ').title()}**: {a['descripcion']}")
        
        if anomalias_medio:
            st.warning(f"🟡 **{len(anomalias_medio)} anomalías de nivel MEDIO**")
            for a in anomalias_medio[:3]:
                st.markdown(f"- **{a['tipo'].replace('_', ' ').title()}**: {a['descripcion']}")
        
        if anomalias_bajo:
            st.info(f"🟢 **{len(anomalias_bajo)} anomalías de nivel BAJO**")
            for a in anomalias_bajo[:3]:
                st.markdown(f"- **{a['tipo'].replace('_', ' ').title()}**: {a['descripcion']}")
        
        # Mostrar total
        if len(anomalias) > 6:
            st.caption(f"... y {len(anomalias) - 6} anomalías más")
    else:
        st.success("✅ **No se detectaron anomalías** - Sistema operando normalmente")
    
    st.divider()

    # ------------------------------------------------
    # ACCESOS VS RECHAZOS
    # ------------------------------------------------
    st.subheader("Accesos vs Rechazos por Día")

    df_count = df.groupby(["fecha", "tipo_evento"]).size().reset_index(name="total")

    chart1 = alt.Chart(df_count).mark_line(point=True).encode(
        x="fecha:T",
        y="total:Q",
        color="tipo_evento:N",
        tooltip=["fecha:T", "tipo_evento:N", "total:Q"]
    ).properties(height=250)

    st.altair_chart(chart1, use_container_width=True)

    # ------------------------------------------------
    # TOP ENTIDADES
    # ------------------------------------------------
    st.subheader("Top Entidades Más Activas")

    top = df["nombre"].value_counts().reset_index()
    top.columns = ["nombre", "eventos"]

    st.dataframe(top.head(10))

    # ------------------------------------------------
    # MAPA DE CALOR POR HORA
    # ------------------------------------------------
    st.subheader("Mapa de calor de accesos por hora")

    try:
        # Filtrar solo registros con hora válida
        df_hora = df[df["hora"].notna() & (df["hora"] != "")].copy()
        
        if not df_hora.empty:
            df_hora["hora_int"] = df_hora["hora"].str.slice(0, 2).astype(int)

            heat = df_hora.groupby(["hora_int", "tipo_evento"]).size().reset_index(name="conteo")

            chart2 = alt.Chart(heat).mark_rect().encode(
                x=alt.X("hora_int:O", title="Hora"),
                y=alt.Y("tipo_evento:N", title="Tipo de evento"),
                color=alt.Color("conteo:Q", scale=alt.Scale(scheme="blues")),
                tooltip=["hora_int", "tipo_evento", "conteo"]
            ).properties(height=300)

            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info("No hay datos de hora suficientes para generar el mapa de calor.")

    except Exception as e:
        st.warning(f"No se pudo generar mapa de calor: {e}")

    # ------------------------------------------------
    # DIAS DE LA SEMANA (histórico)
    # ------------------------------------------------
    st.subheader("Comportamiento por día de la semana")

    df["dia_semana"] = df["timestamp"].dt.day_name()

    chart3 = alt.Chart(
        df.groupby("dia_semana").size().reset_index(name="total")
    ).mark_bar().encode(
        x="dia_semana:N",
        y="total:Q",
        tooltip=["total"]
    ).properties(height=250)

    st.altair_chart(chart3, use_container_width=True)

    # ------------------------------------------------
    # POLÍTICAS QUE MÁS RECHAZAN
    # ------------------------------------------------
    st.subheader("Principales motivos de rechazo")

    rechazos = df[df["tipo_evento"] == "rechazo"]

    if not rechazos.empty:
        rc = rechazos["politica_rechazo"].value_counts().reset_index()
        rc.columns = ["motivo", "rechazos"]

        chart4 = alt.Chart(rc).mark_bar().encode(
            x="motivo:N",
            y="rechazos:Q",
            tooltip=["rechazos"],
            color="motivo:N"
        ).properties(height=250)

        st.altair_chart(chart4, use_container_width=True)
    else:
        st.info("No hay rechazos en el sistema.")

    # ------------------------------------------------
    # ÚLTIMOS 20 EVENTOS
    # ------------------------------------------------
    st.subheader("Últimos 20 eventos")

    st.dataframe(df.head(20))

    # ------------------------------------------------
    # ANÁLISIS ESTRUCTURAL AUP-EXO (RAW)
    # ------------------------------------------------
    st.divider()
    st.subheader("Análisis estructural (AUP-EXO)")

    res = resumen_analitico()

    st.write("## T-1 vs T0")
    st.json(res["t1_t0"])

    st.write("## Anomalías detectadas")
    if res["anomalias"]:
        st.json(res["anomalias"])
    else:
        st.success("No se detectaron anomalías.")

    st.write("## Eventos etiquetados (riesgo)")
    st.dataframe(res["df_etiquetado"].head(20))
