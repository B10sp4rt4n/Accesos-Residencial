"""
modulos/eventos.py  
Visualización y gestión de eventos del sistema AUP-EXO
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core import get_db
from core.hashing import verificar_cadena_integridad


def render_eventos():
    """Renderiza interfaz de eventos"""
    st.header("📋 Registro de Eventos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["En Vivo", "Historial", "Análisis", "Integridad"])
    
    with tab1:
        _render_eventos_live()
    
    with tab2:
        _render_historial_eventos()
    
    with tab3:
        _render_analisis_eventos()
    
    with tab4:
        _render_verificacion_integridad()


def _render_eventos_live():
    """Vista en tiempo real de eventos"""
    st.subheader("🔴 Eventos en Vivo")
    
    # Auto-refresh
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Esta vista se actualiza automáticamente")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
    
    # Últimos eventos
    eventos_recientes = _obtener_eventos_recientes(limite=20)
    
    if not eventos_recientes:
        st.info("No hay eventos recientes")
        return
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    eventos_hoy = _contar_eventos_por_fecha(datetime.now().date())
    accesos_autorizados = len([e for e in eventos_recientes if e['resultado'] == 'autorizado'])
    accesos_denegados = len([e for e in eventos_recientes if e['resultado'] == 'denegado'])
    
    col1.metric("Eventos Hoy", eventos_hoy)
    col2.metric("Autorizados", accesos_autorizados, delta=f"{(accesos_autorizados/len(eventos_recientes)*100):.0f}%")
    col3.metric("Denegados", accesos_denegados, delta=f"-{(accesos_denegados/len(eventos_recientes)*100):.0f}%")
    col4.metric("Total", len(eventos_recientes))
    
    # Lista de eventos
    st.subheader("Últimos 20 Eventos")
    
    for evento in eventos_recientes:
        _render_evento_card(evento)


def _render_evento_card(evento: Dict):
    """Renderiza tarjeta de evento individual"""
    # Iconos según tipo y resultado
    tipo_icon = {
        "entrada": "🟢",
        "salida": "🔴",
        "acceso_vehicular": "🚗",
        "acceso_peatonal": "🚶"
    }.get(evento['tipo_evento'], "📋")
    
    resultado_icon = {
        "autorizado": "✅",
        "denegado": "❌",
        "pendiente": "⏳"
    }.get(evento['resultado'], "❓")
    
    # Container
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            st.write(f"### {tipo_icon}")
            timestamp = pd.to_datetime(evento['timestamp'])
            st.write(f"{timestamp.strftime('%H:%M:%S')}")
        
        with col2:
            st.write(f"**{evento['tipo_evento'].upper()}**")
            if evento.get('entidad_id'):
                st.write(f"Entidad: {evento['entidad_id']}")
            if evento.get('vehiculo_id'):
                st.write(f"Vehículo: {evento['vehiculo_id']}")
        
        with col3:
            st.write(f"{resultado_icon} **{evento['resultado']}**")
            if evento.get('motivo_denegacion'):
                st.write(f"Motivo: {evento['motivo_denegacion']}")
            if evento.get('usuario_registro'):
                st.write(f"Guardia: {evento['usuario_registro']}")
        
        with col4:
            if st.button("Ver", key=f"ver_{evento['id']}"):
                _mostrar_detalle_evento(evento['id'])
        
        st.divider()


def _render_historial_eventos():
    """Historial completo de eventos con filtros"""
    st.subheader("📚 Historial de Eventos")
    
    # Filtros avanzados
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fecha_inicio = st.date_input(
            "Fecha Inicio",
            value=datetime.now().date() - timedelta(days=7)
        )
    
    with col2:
        fecha_fin = st.date_input(
            "Fecha Fin",
            value=datetime.now().date()
        )
    
    with col3:
        tipo_evento = st.selectbox(
            "Tipo Evento",
            ["Todos", "entrada", "salida", "acceso_vehicular", "acceso_peatonal"]
        )
    
    with col4:
        resultado = st.selectbox(
            "Resultado",
            ["Todos", "autorizado", "denegado", "pendiente"]
        )
    
    # Búsqueda adicional
    col5, col6 = st.columns(2)
    with col5:
        buscar_entidad = st.text_input("Buscar por ID Entidad")
    with col6:
        buscar_vehiculo = st.text_input("Buscar por ID Vehículo")
    
    # Botón buscar
    if st.button("🔍 Buscar Eventos"):
        eventos = _buscar_eventos_filtrados(
            fecha_inicio,
            fecha_fin,
            tipo_evento if tipo_evento != "Todos" else None,
            resultado if resultado != "Todos" else None,
            buscar_entidad if buscar_entidad else None,
            buscar_vehiculo if buscar_vehiculo else None
        )
        
        if not eventos:
            st.warning("No se encontraron eventos con los filtros especificados")
            return
        
        st.success(f"Se encontraron {len(eventos)} eventos")
        
        # DataFrame
        df = pd.DataFrame(eventos)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "ID",
                "timestamp": "Fecha/Hora",
                "tipo_evento": "Tipo",
                "resultado": "Resultado",
                "entidad_id": "Entidad",
                "vehiculo_id": "Vehículo",
                "hash": "Hash"
            }
        )
        
        # Exportar
        if st.button("📥 Exportar CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Descargar CSV",
                csv,
                f"eventos_{fecha_inicio}_{fecha_fin}.csv",
                "text/csv"
            )


def _render_analisis_eventos():
    """Análisis y estadísticas de eventos"""
    st.subheader("📊 Análisis de Eventos")
    
    # Selector de periodo
    periodo = st.selectbox(
        "Periodo de Análisis",
        ["Últimas 24 horas", "Últimos 7 días", "Últimos 30 días", "Personalizado"]
    )
    
    if periodo == "Últimas 24 horas":
        fecha_inicio = datetime.now() - timedelta(hours=24)
        fecha_fin = datetime.now()
    elif periodo == "Últimos 7 días":
        fecha_inicio = datetime.now() - timedelta(days=7)
        fecha_fin = datetime.now()
    elif periodo == "Últimos 30 días":
        fecha_inicio = datetime.now() - timedelta(days=30)
        fecha_fin = datetime.now()
    else:
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde")
        with col2:
            fecha_fin = st.date_input("Hasta")
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
    
    # Obtener datos
    eventos = _obtener_eventos_periodo(fecha_inicio, fecha_fin)
    
    if not eventos:
        st.info("No hay eventos en el periodo seleccionado")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    total_eventos = len(eventos)
    autorizados = len([e for e in eventos if e['resultado'] == 'autorizado'])
    denegados = len([e for e in eventos if e['resultado'] == 'denegado'])
    tasa_autorizacion = (autorizados / total_eventos * 100) if total_eventos > 0 else 0
    
    col1.metric("Total Eventos", total_eventos)
    col2.metric("Autorizados", autorizados, delta=f"{tasa_autorizacion:.1f}%")
    col3.metric("Denegados", denegados)
    col4.metric("Tasa Éxito", f"{tasa_autorizacion:.1f}%")
    
    # Gráficas
    st.subheader("Distribución de Eventos")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfica por tipo
        df = pd.DataFrame(eventos)
        if not df.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            tipo_counts = df['tipo_evento'].value_counts()
            ax.pie(tipo_counts.values, labels=tipo_counts.index, autopct='%1.1f%%')
            ax.set_title('Eventos por Tipo')
            st.pyplot(fig)
    
    with col_g2:
        # Gráfica por resultado
        if not df.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            resultado_counts = df['resultado'].value_counts()
            colors = ['green' if r == 'autorizado' else 'red' for r in resultado_counts.index]
            ax.bar(resultado_counts.index, resultado_counts.values, color=colors)
            ax.set_title('Eventos por Resultado')
            ax.set_ylabel('Cantidad')
            st.pyplot(fig)
    
    # Tendencia temporal
    st.subheader("Tendencia Temporal")
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['fecha'] = df['timestamp'].dt.date
        
        eventos_por_dia = df.groupby('fecha').size().reset_index(name='cantidad')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(eventos_por_dia['fecha'], eventos_por_dia['cantidad'], marker='o')
        ax.set_title('Eventos por Día')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Eventos')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    # Top entidades/vehículos
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Top 10 Entidades")
        if not df.empty and 'entidad_id' in df.columns:
            top_entidades = df['entidad_id'].value_counts().head(10)
            st.bar_chart(top_entidades)
    
    with col_t2:
        st.subheader("Top 10 Vehículos")
        if not df.empty and 'vehiculo_id' in df.columns:
            top_vehiculos = df['vehiculo_id'].value_counts().head(10)
            st.bar_chart(top_vehiculos)


def _render_verificacion_integridad():
    """Verificación de integridad de la cadena de eventos"""
    st.subheader("🔐 Verificación de Integridad")
    
    st.write("""
    Esta herramienta verifica la integridad de la cadena de eventos utilizando 
    el sistema de hashing AUP-EXO. Cada evento está encadenado al anterior mediante 
    su hash, similar a blockchain.
    """)
    
    # Verificación completa
    if st.button("🔍 Verificar Integridad Completa"):
        with st.spinner("Verificando cadena de eventos..."):
            resultado = verificar_cadena_integridad()
            
            if resultado['integra']:
                st.success(f"✅ Cadena de eventos íntegra ({resultado['total_eventos']} eventos verificados)")
                st.metric("Eventos Verificados", resultado['total_eventos'])
            else:
                st.error(f"❌ Se detectaron inconsistencias en la cadena")
                st.write(f"**Primer evento corrupto:** {resultado.get('primer_corrupto')}")
                st.write(f"**Detalles:** {resultado.get('detalles')}")
    
    # Verificación de evento específico
    st.divider()
    st.subheader("Verificar Evento Específico")
    
    evento_id = st.number_input("ID del Evento", min_value=1, step=1)
    
    if st.button("Verificar Evento"):
        evento = _obtener_evento_por_id(evento_id)
        
        if not evento:
            st.error("Evento no encontrado")
            return
        
        # Mostrar detalles
        st.write("**Detalles del Evento:**")
        st.json(evento)
        
        # Verificar hash
        hash_actual = evento.get('hash')
        hash_previo = evento.get('hash_previo')
        
        st.write(f"**Hash actual:** `{hash_actual}`")
        st.write(f"**Hash previo:** `{hash_previo}`")
        
        # TODO: Implementar verificación individual
        st.info("Verificación individual en desarrollo")


# Funciones auxiliares

def _obtener_eventos_recientes(limite: int = 20) -> List[Dict]:
    """Obtiene eventos más recientes"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM eventos ORDER BY timestamp DESC LIMIT ?",
            (limite,)
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _contar_eventos_por_fecha(fecha: datetime.date) -> int:
    """Cuenta eventos de una fecha específica"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM eventos WHERE DATE(timestamp) = ?",
            (fecha.isoformat(),)
        )
        return cursor.fetchone()[0]


def _buscar_eventos_filtrados(
    fecha_inicio: datetime.date,
    fecha_fin: datetime.date,
    tipo_evento: Optional[str] = None,
    resultado: Optional[str] = None,
    entidad_id: Optional[str] = None,
    vehiculo_id: Optional[str] = None
) -> List[Dict]:
    """Busca eventos con filtros múltiples"""
    with get_db() as conn:
        query = "SELECT * FROM eventos WHERE DATE(timestamp) BETWEEN ? AND ?"
        params = [fecha_inicio.isoformat(), fecha_fin.isoformat()]
        
        if tipo_evento:
            query += " AND tipo_evento = ?"
            params.append(tipo_evento)
        
        if resultado:
            query += " AND resultado = ?"
            params.append(resultado)
        
        if entidad_id:
            query += " AND entidad_id = ?"
            params.append(int(entidad_id))
        
        if vehiculo_id:
            query += " AND vehiculo_id = ?"
            params.append(int(vehiculo_id))
        
        query += " ORDER BY timestamp DESC LIMIT 500"
        
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _obtener_eventos_periodo(fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict]:
    """Obtiene eventos de un periodo"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM eventos WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC",
            (fecha_inicio.isoformat(), fecha_fin.isoformat())
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _obtener_evento_por_id(evento_id: int) -> Optional[Dict]:
    """Obtiene un evento por ID"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM eventos WHERE id = ?", (evento_id,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None


def _mostrar_detalle_evento(evento_id: int):
    """Muestra detalle completo de un evento"""
    evento = _obtener_evento_por_id(evento_id)
    
    if not evento:
        st.error("Evento no encontrado")
        return
    
    st.subheader(f"Evento #{evento_id}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Información General**")
        st.write(f"Tipo: {evento['tipo_evento']}")
        st.write(f"Timestamp: {pd.to_datetime(evento['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}")
        st.write(f"Resultado: {evento['resultado']}")
        
        if evento.get('motivo_denegacion'):
            st.write(f"Motivo: {evento['motivo_denegacion']}")
    
    with col2:
        st.write("**Trazabilidad**")
        st.write(f"Hash: `{evento.get('hash', 'N/A')[:16]}...`")
        st.write(f"Hash Previo: `{evento.get('hash_previo', 'N/A')[:16]}...`")
        st.write(f"Usuario: {evento.get('usuario_registro', 'N/A')}")
    
    # Datos completos
    with st.expander("Ver JSON Completo"):
        st.json(evento)


if __name__ == "__main__":
    st.set_page_config(page_title="Eventos", layout="wide")
    render_eventos()
