# modulos/vigilancia.py
"""
VIGILANCIA - Accesos Residencial (AUP-EXO)
Flujo completo basado en ENTIDAD → ORQUESTADOR → EVENTO
"""

import json
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional

from core.db import get_db
from core.orquestador import OrquestadorAccesos
from modulos.entidades import obtener_entidades, obtener_entidad_por_id

orq = OrquestadorAccesos()


# ---------------------------------------------------------------------
#  BUSCADOR UNIVERSAL DE ENTIDADES
#  (nombre, placa, QR, folio, teléfono, etc.)
# ---------------------------------------------------------------------
def buscar_entidad(query: str, msp_id=None, condominio_id=None) -> List[Dict]:
    """
    Busca entidades por cualquier criterio con filtrado multi-tenant
    
    Args:
        query: Texto a buscar (nombre, placa, folio, teléfono, etc.)
        msp_id: Filtrar por MSP (opcional)
        condominio_id: Filtrar por Condominio (opcional)
    
    Returns:
        Lista de entidades encontradas
    """
    if not query or len(query) < 2:
        return []

    query_like = f"%{query}%"
    
    # Construir query con filtrado multi-tenant
    sql = """
        SELECT *
        FROM entidades
        WHERE estado = 'activo'
    """
    params = []
    
    # Filtrado multi-tenant
    if msp_id:
        sql += " AND msp_id = ?"
        params.append(msp_id)
    
    if condominio_id:
        sql += " AND condominio_id = ?"
        params.append(condominio_id)
    
    sql += """
        AND (
            entidad_id LIKE ?
            OR tipo LIKE ?
            OR atributos LIKE ?
        )
        ORDER BY fecha_creacion DESC
        LIMIT 20
    """
    params.extend([query_like, query_like, query_like])

    with get_db() as db:
        rows = db.execute(sql, tuple(params)).fetchall()

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


# ---------------------------------------------------------------------
#  OBTENER EVENTOS RECIENTES
# ---------------------------------------------------------------------
def obtener_eventos_recientes(limite: int = 10) -> List[Dict]:
    """
    Obtiene los últimos eventos del sistema
    
    Args:
        limite: Número máximo de eventos a retornar
    
    Returns:
        Lista de eventos recientes
    """
    # La columna en 'entidades' es 'entidad_id'; confirmar existencia y fallback a 'id'
    with get_db() as db:
        # Detectar nombre de PK usable para el JOIN
        cols_ent = [c[0] if not isinstance(c, dict) else c['column_name'] for c in db.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name='entidades'").fetchall()]
        pk_join_col = 'entidad_id' if 'entidad_id' in cols_ent else 'id'
        # Construir query dinámica segura (placeholder al final)
        query = f"""
            SELECT 
                e.*,
                ent.tipo as entidad_tipo,
                ent.atributos as entidad_atributos
            FROM eventos e
            LEFT JOIN entidades ent ON e.entidad_id = ent.{pk_join_col}
            ORDER BY e.timestamp_servidor DESC
            LIMIT ?
        """
        rows = db.execute(query, (limite,)).fetchall()
    
    eventos = []
    for row in rows:
        evento = dict(row)
        # Parsear metadata
        if evento.get('metadata'):
            try:
                evento['metadata'] = json.loads(evento['metadata'])
            except:
                evento['metadata'] = {}
        # Parsear atributos de entidad
        if evento.get('entidad_atributos'):
            try:
                evento['entidad_atributos'] = json.loads(evento['entidad_atributos'])
            except:
                evento['entidad_atributos'] = {}
        eventos.append(evento)
    
    return eventos


# ---------------------------------------------------------------------
#  UI PRINCIPAL DEL MÓDULO DE VIGILANCIA
# ---------------------------------------------------------------------
def ui_vigilancia():
    """
    Interfaz principal de vigilancia con flujo AUP-EXO
    ENTIDAD → ORQUESTADOR → EVENTO
    """
    st.markdown("""
    <style>
        .stButton > button {
            height: 60px;
            font-size: 18px;
            font-weight: bold;
        }
        .evento-card {
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 4px solid;
        }
        .evento-entrada {
            background-color: #d1fae5;
            border-left-color: #10b981;
        }
        .evento-salida {
            background-color: #fee2e2;
            border-left-color: #ef4444;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("🚧 Control de Accesos - Vigilancia")
    st.markdown("**Sistema AUP-EXO:** ENTIDAD → ORQUESTADOR → EVENTO")
    
    # Información del vigilante
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        turno = "Matutino" if datetime.now().hour < 14 else "Vespertino"
        st.metric("Turno", turno)
    with col_info2:
        hora_actual = datetime.now().strftime("%H:%M:%S")
        st.metric("Hora", hora_actual)
    with col_info3:
        vigilante = st.session_state.get("usuario_id", "Vigilante 1")
        st.metric("Operador", vigilante)
    
    st.divider()
    
    # Layout principal
    col_principal, col_lateral = st.columns([2, 1])
    
    with col_principal:
        _vista_registro_acceso()
    
    with col_lateral:
        _vista_eventos_recientes()


# ---------------------------------------------------------------------
#  VISTA: REGISTRO DE ACCESO
# ---------------------------------------------------------------------
def _vista_registro_acceso():
    """Vista principal para registrar accesos"""
    st.subheader("🔍 Buscador Universal de Entidades")
    
    # Mostrar contexto activo
    msp_id = st.session_state.get('msp_id')
    condominio_id = st.session_state.get('condominio_id')
    rol_usuario = st.session_state.get('rol_usuario', 'super_admin')
    
    if msp_id or condominio_id or rol_usuario == 'super_admin':
        with st.expander("🎯 Contexto Activo", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                if rol_usuario == 'super_admin':
                    st.info("👑 **Super Admin**\nAcceso total")
                else:
                    st.info(f"👤 **Rol:** {rol_usuario}")
            with col2:
                if msp_id:
                    st.success(f"🏢 **MSP:** `{msp_id}`")
                else:
                    st.warning("🏢 **MSP:** Sin seleccionar")
            with col3:
                if condominio_id:
                    st.success(f"🏘️ **Condominio:** `{condominio_id}`")
                else:
                    st.warning("🏘️ **Condominio:** Sin seleccionar")
    
    # Buscador
    busqueda = st.text_input(
        "Buscar por nombre, placa, folio, QR, teléfono...",
        placeholder="Ejemplo: ABC-1234, Juan Pérez, FOLIO-001",
        key="busqueda_entidad"
    )
    
    if busqueda:
        # Obtener contexto multi-tenant
        msp_id = st.session_state.get('msp_id')
        condominio_id = st.session_state.get('condominio_id')
        
        resultados = buscar_entidad(busqueda, msp_id=msp_id, condominio_id=condominio_id)
        
        if resultados:
            st.success(f"✅ {len(resultados)} entidad(es) encontrada(s)")
            
            # Crear opciones para selectbox
            opciones = {}
            for r in resultados:
                # Parse atributos safely (puede ser None, string JSON, o dict)
                atributos_raw = r.get('atributos')
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
                
                nombre = attrs.get('nombre', 'Sin nombre')
                identificador = attrs.get('identificador', 'Sin ID')
                tipo = r['tipo'].upper()
                
                label = f"{tipo} | {nombre} | {identificador}"
                opciones[label] = r
            
            # Selección de entidad
            seleccion = st.selectbox(
                "Seleccionar entidad:",
                list(opciones.keys()),
                key="select_entidad"
            )
            
            if seleccion:
                entidad = opciones[seleccion]
                
                # Mostrar información de la entidad
                with st.expander("📋 Información de la entidad", expanded=True):
                    col_ent1, col_ent2, col_ent3 = st.columns(3)
                    
                    with col_ent1:
                        st.write(f"**ID:** `{entidad['entidad_id']}`")
                        st.write(f"**Tipo:** {entidad['tipo']}")
                        st.write(f"**Estado:** {entidad['estado']}")
                    
                    with col_ent2:
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
                        
                        st.write(f"**Nombre:** {attrs.get('nombre', 'N/A')}")
                        st.write(f"**Identificador:** {attrs.get('identificador', 'N/A')}")
                        hash_val = entidad.get('hash_actual', '')
                        if hash_val:
                            st.write(f"**Hash:** `{hash_val[:16]}...`")
                        else:
                            st.write(f"**Hash:** `Sin hash`")
                    
                    with col_ent3:
                        msp_val = entidad.get('msp_id')
                        condo_val = entidad.get('condominio_id')
                        if msp_val:
                            st.write(f"**🏢 MSP:** `{msp_val}`")
                        else:
                            st.write(f"**🏢 MSP:** Sin asignar")
                        
                        if condo_val:
                            st.write(f"**🏘️ Condominio:** `{condo_val}`")
                        else:
                            st.write(f"**🏘️ Condominio:** Sin asignar")
                    
                    # Atributos completos
                    st.json(attrs)
                
                st.divider()
                
                # Formulario de acceso
                st.subheader("🚪 Registrar Acceso")
                
                col_form1, col_form2 = st.columns(2)
                
                with col_form1:
                    tipo_evento = st.selectbox(
                        "Tipo de acceso",
                        ["entrada", "salida"],
                        key="tipo_evento"
                    )
                
                with col_form2:
                    actor = st.text_input(
                        "Vigilante",
                        value=st.session_state.get("usuario_id", "Vigilante 1"),
                        key="actor"
                    )
                
                # Notas adicionales
                notas = st.text_area(
                    "Notas u observaciones (opcional)",
                    placeholder="Ej: Visitante autorizado por residente Casa 15",
                    key="notas_acceso"
                )
                
                # Metadata del acceso
                metadata = {
                    "tipo_acceso": tipo_evento,
                    "hora": datetime.now().strftime("%H:%M:%S"),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "notas": notas,
                    "contexto": {
                        "ip": st.session_state.get("ip", "127.0.0.1"),
                        "terminal": "vigilancia_web",
                        "modulo": "vigilancia_aup_exo"
                    }
                }
                
                # Botón de registro
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button(
                        f"✅ Registrar {tipo_evento.upper()}",
                        type="primary",
                        use_container_width=True,
                        key="btn_registrar"
                    ):
                        with st.spinner("Procesando acceso..."):
                            try:
                                # Procesar acceso vía ORQUESTADOR
                                if tipo_evento == "entrada":
                                    # Para entradas: evaluar políticas
                                    resultado = orq.procesar_acceso(
                                        entidad_id=entidad["entidad_id"],
                                        metadata=metadata,
                                        actor=actor,
                                        dispositivo="vigilancia_module"
                                    )
                                else:
                                    # Para salidas: registro directo
                                    resultado = orq.registrar_acceso(
                                        entidad_id=entidad["entidad_id"],
                                        tipo_evento="salida",
                                        metadata=metadata,
                                        actor=actor,
                                        dispositivo="vigilancia_module"
                                    )
                                
                                # Verificar resultado
                                if isinstance(resultado, dict):
                                    if resultado.get("decision") == "rechazado":
                                        st.error(f"❌ Acceso RECHAZADO")
                                        st.warning(f"**Motivo:** {resultado.get('motivo', 'No especificado')}")
                                        
                                        # Mostrar políticas violadas
                                        if resultado.get('politicas_violadas'):
                                            st.write("**Políticas violadas:**")
                                            for pol in resultado['politicas_violadas']:
                                                st.write(f"- {pol}")
                                    else:
                                        # Acceso permitido
                                        st.success("✅ Acceso PERMITIDO y registrado correctamente")
                                        
                                        # Información del evento
                                        st.info(f"**Evento ID:** `{resultado.get('evento_id', 'N/A')}`")
                                        st.info(f"**Hash:** `{resultado.get('hash', 'N/A')[:20]}...`")
                                        
                                        # Recibo Recordia
                                        if resultado.get('recibo_recordia'):
                                            st.success(f"📜 **Recibo Recordia:** `{resultado['recibo_recordia']}`")
                                        
                                        # Limpiar búsqueda
                                        if st.button("🔄 Registrar otro acceso"):
                                            st.rerun()
                                else:
                                    # Formato legacy (solo hash)
                                    st.success("✅ Acceso PERMITIDO y registrado")
                                    st.info(f"**Hash del evento:** `{str(resultado)[:20]}...`")
                                
                            except Exception as e:
                                st.error(f"❌ Error al procesar acceso: {str(e)}")
                                st.exception(e)
                
                with col_btn2:
                    if st.button("🔙 Cancelar", use_container_width=True):
                        st.rerun()
        
        else:
            st.warning("⚠️ No se encontraron entidades con ese criterio")
            st.info("💡 Intenta con: nombre, placa, folio, teléfono, etc.")
    
    else:
        st.info("👆 Ingresa un criterio de búsqueda para comenzar")


# ---------------------------------------------------------------------
#  VISTA: EVENTOS RECIENTES
# ---------------------------------------------------------------------
def _vista_eventos_recientes():
    """Vista lateral con eventos recientes"""
    st.subheader("📊 Eventos Recientes")
    
    # Selector de cantidad
    limite = st.selectbox("Mostrar últimos", [5, 10, 20, 50], index=1, key="limite_eventos")
    
    # Obtener eventos
    eventos = obtener_eventos_recientes(limite=limite)
    
    if eventos:
        for evento in eventos:
            tipo_evento = evento.get('tipo_evento', 'N/A')
            timestamp = evento.get('timestamp_servidor', '')
            
            # Extraer nombre de entidad
            attrs_ent = evento.get('entidad_atributos', {})
            nombre_entidad = attrs_ent.get('nombre', 'Sin nombre')
            id_entidad = attrs_ent.get('identificador', 'Sin ID')
            tipo_entidad = evento.get('entidad_tipo', 'N/A')
            
            # Estilo según tipo de evento
            clase_css = "evento-entrada" if tipo_evento == "entrada" else "evento-salida"
            icono = "🟢" if tipo_evento == "entrada" else "🔴"
            
            # Card del evento
            st.markdown(f"""
            <div class="evento-card {clase_css}">
                <strong>{icono} {tipo_evento.upper()}</strong><br>
                <small>{tipo_entidad.upper()}: {nombre_entidad}</small><br>
                <small>ID: {id_entidad}</small><br>
                <small>⏰ {timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No hay eventos registrados")
    
    # Botón para refrescar
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()


# ---------------------------------------------------------------------
# PANTALLA RESUMIDA PARA INDEX
# ---------------------------------------------------------------------
def ui_resumen_vigilancia():
    """Resumen de vigilancia para página principal"""
    st.write("### 🚧 Vigilancia (Accesos)")
    st.write("Registra accesos mediante el buscador universal de entidades.")
    
    # Estadísticas rápidas
    eventos = obtener_eventos_recientes(limite=100)
    
    if eventos:
        col1, col2 = st.columns(2)
        
        with col1:
            entradas = sum(1 for e in eventos if e.get('tipo_evento') == 'entrada')
            st.metric("Entradas hoy", entradas)
        
        with col2:
            salidas = sum(1 for e in eventos if e.get('tipo_evento') == 'salida')
            st.metric("Salidas hoy", salidas)


# ---------------------------------------------------------------------
# ALIAS DE COMPATIBILIDAD
# ---------------------------------------------------------------------
def render_vigilancia():
    """Alias de compatibilidad con código anterior"""
    ui_vigilancia()
