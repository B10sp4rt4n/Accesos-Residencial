"""
modulos/vigilancia.py
Interfaz optimizada para vigilantes integrada con AUP-EXO
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Dict, Optional
from core import OrquestadorAccesos, get_db
from core.contexto import ContextoManager
from core.utils import validar_placa_mexico


def render_vigilancia():
    """Renderiza interfaz principal de vigilante"""
    
    # CSS personalizado
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stButton > button {
            height: 80px;
            font-size: 24px;
            font-weight: bold;
            border-radius: 12px;
        }
        .evento-card {
            padding: 16px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 4px solid;
        }
        .evento-entrada {
            background-color: #d1fae5;
            border-left-color: #10b981;
        }
        .evento-salida {
            background-color: #dbeafe;
            border-left-color: #3b82f6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    _mostrar_header()
    
    # Layout principal
    col_principal, col_lateral = st.columns([2, 1])
    
    with col_principal:
        _vista_registro_acceso()
    
    with col_lateral:
        _vista_eventos_recientes()
    
    # Footer con acciones rápidas
    _mostrar_footer()


def _mostrar_header():
    """Header con información del vigilante"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🏠 Caseta - Sistema AUP-EXO")
    
    with col2:
        turno = "Matutino" if datetime.now().hour < 14 else "Vespertino"
        st.markdown(f"**Turno:** {turno}")
    
    with col3:
        usuario = st.session_state.get("usuario_id", "Vigilante")
        st.markdown(f"**👤 {usuario}**")
    
    st.divider()


def _vista_registro_acceso():
    """Vista principal de registro de accesos"""
    st.markdown("## 📸 Registro de Acceso")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📷 Captura de Placa")
        
        # Camera input
        foto_placa = st.camera_input(
            "Captura la placa del vehículo",
            label_visibility="collapsed"
        )
        
        if foto_placa is not None:
            st.image(foto_placa, caption="Foto capturada", width=200)
            
            if st.button("🔍 PROCESAR FOTO", use_container_width=True, type="primary"):
                # TODO: OCR en producción
                st.session_state.foto_capturada = foto_placa.getvalue()
                st.info("💡 Ingresa la placa manualmente a la derecha")
    
    with col2:
        st.markdown("### ⌨️ Búsqueda de Placa")
        
        placa = st.text_input(
            "Ingresa placa",
            placeholder="ABC-1234",
            max_chars=10,
            label_visibility="collapsed"
        ).upper()
        
        if st.button("🔍 BUSCAR VEHÍCULO", use_container_width=True):
            if placa:
                # Validar formato
                resultado_validacion = validar_placa_mexico(placa)
                
                if not resultado_validacion["valida"]:
                    st.error(f"❌ {resultado_validacion['mensaje']}")
                    return
                
                st.session_state.placa_actual = placa
                st.rerun()
    
    # Si hay placa seleccionada, mostrar verificación
    if "placa_actual" in st.session_state:
        st.markdown("---")
        _vista_verificacion_vehiculo(st.session_state.placa_actual)


def _vista_verificacion_vehiculo(placa: str):
    """Verifica y muestra información del vehículo"""
    
    # Buscar vehículo en DB
    vehiculo = _buscar_vehiculo_por_placa(placa)
    
    if not vehiculo:
        _vista_vehiculo_no_registrado(placa)
        return
    
    # Verificar lista negra
    if vehiculo.get('lista_negra'):
        _vista_alerta_lista_negra(vehiculo)
        return
    
    # Vehículo válido
    _vista_vehiculo_autorizado(vehiculo)


def _vista_alerta_lista_negra(vehiculo: Dict):
    """Alerta de vehículo en lista negra"""
    st.error("🚨 ALERTA DE SEGURIDAD - VEHÍCULO BLOQUEADO")
    
    col1, col2 = st.columns([1, 2])
    
    with col2:
        st.markdown(f"### ❌ ACCESO DENEGADO")
        st.markdown(f"**Placa:** {vehiculo['placa']}")
        st.markdown(f"**Tipo:** {vehiculo['tipo']}")
        st.markdown(f"**Motivo:** {vehiculo.get('motivo_lista_negra', 'No especificado')}")
    
    st.error("⛔ ACCESO AUTOMÁTICAMENTE DENEGADO")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🚨 NOTIFICAR SEGURIDAD", use_container_width=True):
            # Registrar evento de intento de acceso bloqueado
            orquestador = OrquestadorAccesos()
            orquestador.registrar_acceso(
                tipo_evento="intento_acceso_bloqueado",
                vehiculo_id=vehiculo['id'],
                resultado="denegado",
                motivo_denegacion="Vehículo en lista negra",
                usuario_registro=st.session_state.get("usuario_id")
            )
            
            st.success("✅ Notificación enviada")
            time.sleep(1)
            _limpiar_sesion()
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 NUEVA BÚSQUEDA", use_container_width=True):
            _limpiar_sesion()
            st.rerun()


def _vista_vehiculo_autorizado(vehiculo: Dict):
    """Muestra información de vehículo autorizado"""
    st.success("✅ VEHÍCULO REGISTRADO")
    
    # Buscar propietario
    propietario = _buscar_propietario(vehiculo.get('propietario_id'))
    
    col1, col2 = st.columns([1, 2])
    
    with col2:
        if propietario:
            st.markdown(f"### {propietario['nombre_completo']}")
            st.markdown(f"**Tipo:** {propietario['tipo'].title()}")
            st.markdown(f"**Dirección:** {propietario.get('direccion', 'N/A')}")
        
        st.markdown(f"**Vehículo:** {vehiculo['placa']} - {vehiculo['tipo']}")
        st.markdown(f"**Marca/Modelo:** {vehiculo.get('marca', '')} {vehiculo.get('modelo', '')}")
    
    # Tipo de acceso
    st.markdown("---")
    
    col_tipo1, col_tipo2 = st.columns(2)
    
    with col_tipo1:
        tipo_acceso = st.radio(
            "Tipo de movimiento",
            ["🚗 ENTRADA", "🚙 SALIDA"],
            horizontal=True
        )
    
    with col_tipo2:
        notas = st.text_input("📝 Notas (opcional)")
    
    # Botones de acción
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("✅ PERMITIR ACCESO", use_container_width=True, type="primary"):
            _registrar_acceso_vehiculo(
                vehiculo,
                "entrada" if "ENTRADA" in tipo_acceso else "salida",
                propietario,
                notas
            )
    
    with col_btn2:
        if st.button("❌ DENEGAR ACCESO", use_container_width=True):
            motivo = st.text_input("Motivo de denegación:")
            if motivo:
                _registrar_denegacion(vehiculo, motivo)


def _vista_vehiculo_no_registrado(placa: str):
    """Formulario para vehículo no registrado"""
    st.warning("⚠️ VEHÍCULO NO REGISTRADO")
    st.markdown(f"### Placa: {placa}")
    
    with st.form("registro_visitante"):
        st.markdown("#### Registrar Nuevo Acceso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_persona = st.selectbox(
                "Tipo de persona",
                ["visitante", "residente", "empleado", "proveedor"]
            )
            nombre = st.text_input("Nombre completo *")
            telefono = st.text_input("Teléfono")
        
        with col2:
            tipo_vehiculo = st.selectbox(
                "Tipo de vehículo",
                ["auto", "moto", "camioneta", "pickup", "camion"]
            )
            casa_destino = st.text_input("Casa/Depto destino *")
            
        notas = st.text_area("Observaciones")
        
        col_submit1, col_submit2 = st.columns(2)
        
        with col_submit1:
            submitted = st.form_submit_button(
                "✅ REGISTRAR Y PERMITIR",
                use_container_width=True,
                type="primary"
            )
        
        with col_submit2:
            denegado = st.form_submit_button(
                "❌ DENEGAR",
                use_container_width=True
            )
        
        if submitted:
            if not nombre or not casa_destino:
                st.error("Nombre y casa destino son obligatorios")
                return
            
            _registrar_nuevo_acceso(
                placa,
                nombre,
                tipo_persona,
                tipo_vehiculo,
                casa_destino,
                telefono,
                notas
            )
        
        if denegado:
            st.warning("⛔ Acceso denegado")
            time.sleep(1)
            _limpiar_sesion()
            st.rerun()


def _vista_eventos_recientes():
    """Muestra eventos recientes del día"""
    st.markdown("### 📋 Accesos Recientes")
    
    eventos = _obtener_eventos_hoy()
    
    # Métricas
    total_hoy = len(eventos)
    entradas = len([e for e in eventos if e['tipo_evento'] == 'entrada'])
    salidas = len([e for e in eventos if e['tipo_evento'] == 'salida'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total_hoy)
    col2.metric("Entradas", entradas)
    col3.metric("Salidas", salidas)
    
    st.markdown("---")
    
    # Lista de eventos
    for evento in eventos[:10]:
        hora = pd.to_datetime(evento['timestamp']).strftime("%H:%M")
        tipo_icon = "🚗" if evento['tipo_evento'] == 'entrada' else "🚙"
        resultado_icon = "✅" if evento['resultado'] == 'autorizado' else "❌"
        
        tipo_class = f"evento-{evento['tipo_evento']}"
        
        st.markdown(f"""
        <div class="evento-card {tipo_class}">
            <strong>{hora}</strong> • {tipo_icon} {evento['tipo_evento'].upper()} {resultado_icon}<br>
            ID: {evento.get('vehiculo_id', 'N/A')}
        </div>
        """, unsafe_allow_html=True)


def _mostrar_footer():
    """Footer con acciones rápidas"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚨 EMERGENCIA", use_container_width=True):
            st.error("🚨 Protocolo de emergencia activado")
    
    with col2:
        if st.button("📊 REPORTE TURNO", use_container_width=True):
            _generar_reporte_turno()
    
    with col3:
        if st.button("🔄 LIMPIAR", use_container_width=True):
            _limpiar_sesion()
            st.rerun()


# Funciones auxiliares

def _buscar_vehiculo_por_placa(placa: str) -> Optional[Dict]:
    """Busca vehículo por placa"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM entidades WHERE tipo_entidad = 'vehiculo' AND placa = ?",
            (placa,)
        )
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None


def _buscar_propietario(propietario_id: Optional[int]) -> Optional[Dict]:
    """Busca información del propietario"""
    if not propietario_id:
        return None
    
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM entidades WHERE id = ?",
            (propietario_id,)
        )
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None


def _registrar_acceso_vehiculo(
    vehiculo: Dict,
    tipo: str,
    propietario: Optional[Dict],
    notas: str
):
    """Registra acceso de vehículo autorizado"""
    orquestador = OrquestadorAccesos()
    
    # Capturar contexto del dispositivo
    cm = ContextoManager()
    contexto = cm.capturar_contexto_completo()
    
    # Procesar acceso
    resultado = orquestador.procesar_acceso(
        tipo_acceso=tipo,
        vehiculo_id=vehiculo['id'],
        entidad_id=propietario['id'] if propietario else None,
        evidencia_foto=st.session_state.get('foto_capturada'),
        contexto_dispositivo=contexto,
        usuario_registro=st.session_state.get('usuario_id', 'vigilante'),
        notas=notas
    )
    
    if resultado['autorizado']:
        st.success(f"✅ Acceso {tipo} registrado correctamente")
        st.balloons()
    else:
        st.error(f"❌ Acceso denegado: {resultado.get('motivo')}")
    
    time.sleep(2)
    _limpiar_sesion()
    st.rerun()


def _registrar_nuevo_acceso(
    placa: str,
    nombre: str,
    tipo_persona: str,
    tipo_vehiculo: str,
    casa_destino: str,
    telefono: str,
    notas: str
):
    """Registra nuevo acceso (persona y vehículo no registrados)"""
    orquestador = OrquestadorAccesos()
    
    # Crear persona
    persona_id = orquestador.crear_entidad(
        tipo=tipo_persona,
        nombre=nombre,
        telefono=telefono,
        datos_adicionales={"casa_destino": casa_destino}
    )
    
    # Crear vehículo
    vehiculo_id = orquestador.crear_entidad(
        tipo="vehiculo",
        identificador=placa,
        propietario_id=persona_id,
        datos_adicionales={
            "tipo": tipo_vehiculo,
            "registro_temporal": True
        }
    )
    
    # Registrar acceso
    cm = ContextoManager()
    contexto = cm.capturar_contexto_completo()
    
    resultado = orquestador.procesar_acceso(
        tipo_acceso="entrada",
        vehiculo_id=vehiculo_id,
        entidad_id=persona_id,
        evidencia_foto=st.session_state.get('foto_capturada'),
        contexto_dispositivo=contexto,
        usuario_registro=st.session_state.get('usuario_id', 'vigilante'),
        notas=f"Nuevo registro. {notas}"
    )
    
    if resultado['autorizado']:
        st.success(f"✅ Nuevo {tipo_persona} registrado - Acceso permitido")
        st.balloons()
    else:
        st.error(f"❌ Error al registrar: {resultado.get('motivo')}")
    
    time.sleep(2)
    _limpiar_sesion()
    st.rerun()


def _registrar_denegacion(vehiculo: Dict, motivo: str):
    """Registra denegación de acceso"""
    orquestador = OrquestadorAccesos()
    
    orquestador.registrar_acceso(
        tipo_evento="acceso_denegado",
        vehiculo_id=vehiculo['id'],
        resultado="denegado",
        motivo_denegacion=motivo,
        usuario_registro=st.session_state.get('usuario_id')
    )
    
    st.warning(f"⛔ Acceso denegado: {motivo}")
    time.sleep(2)
    _limpiar_sesion()
    st.rerun()


def _obtener_eventos_hoy() -> list:
    """Obtiene eventos de hoy"""
    hoy = datetime.now().date().isoformat()
    
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM eventos 
            WHERE DATE(timestamp) = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (hoy,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _generar_reporte_turno():
    """Genera reporte del turno actual"""
    st.info("Generando reporte de turno...")
    
    eventos_hoy = _obtener_eventos_hoy()
    
    st.write(f"**Total eventos:** {len(eventos_hoy)}")
    st.write(f"**Entradas:** {len([e for e in eventos_hoy if e['tipo_evento'] == 'entrada'])}")
    st.write(f"**Salidas:** {len([e for e in eventos_hoy if e['tipo_evento'] == 'salida'])}")
    st.write(f"**Autorizados:** {len([e for e in eventos_hoy if e['resultado'] == 'autorizado'])}")
    st.write(f"**Denegados:** {len([e for e in eventos_hoy if e['resultado'] == 'denegado'])}")


def _limpiar_sesion():
    """Limpia variables de sesión"""
    keys_to_remove = ['placa_actual', 'foto_capturada']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


if __name__ == "__main__":
    st.set_page_config(
        page_title="Vigilancia",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    render_vigilancia()
