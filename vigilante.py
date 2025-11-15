"""
Interfaz optimizada para vigilantes de caseta.
Diseño minimalista, touch-friendly y rápido.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time

st.set_page_config(
    page_title="🏠 Caseta - Vigilante",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para interfaz de vigilante
st.markdown("""
<style>
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Botones grandes y touch-friendly */
    .stButton > button {
        height: 80px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 12px;
        width: 100%;
    }
    
    /* Botón permitir verde */
    .btn-permitir > button {
        background-color: #10b981;
        color: white;
        border: 3px solid #059669;
    }
    
    /* Botón denegar rojo */
    .btn-denegar > button {
        background-color: #ef4444;
        color: white;
        border: 3px solid #dc2626;
    }
    
    /* Cards de eventos */
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
    
    .evento-alerta {
        background-color: #fee2e2;
        border-left-color: #ef4444;
    }
    
    /* Texto grande y legible */
    h1 {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Inputs más grandes */
    .stTextInput > div > div > input {
        font-size: 20px;
        height: 50px;
    }
    
    /* Métricas destacadas */
    [data-testid="stMetricValue"] {
        font-size: 32px;
    }
</style>
""", unsafe_allow_html=True)


# ============= DATOS MOCK =============
@st.cache_data
def get_mock_data():
    """Datos de prueba (en producción vendría de Supabase)"""
    vehiculos_db = {
        "ABC-1234": {
            "persona": "Juan Pérez",
            "tipo": "residente",
            "casa": "15",
            "vehiculo": "Toyota Corolla Gris",
            "ultima_visita": datetime.now() - timedelta(hours=2),
            "foto_url": "https://via.placeholder.com/150",
            "en_lista_negra": False
        },
        "XYZ-7890": {
            "persona": "María López",
            "tipo": "residente",
            "casa": "22",
            "vehiculo": "Honda Civic Blanco",
            "ultima_visita": datetime.now() - timedelta(days=1),
            "foto_url": "https://via.placeholder.com/150",
            "en_lista_negra": False
        },
        "DEF-4567": {
            "persona": "VEHÍCULO REPORTADO",
            "tipo": "bloqueado",
            "casa": "-",
            "vehiculo": "Nissan Versa Negro",
            "ultima_visita": None,
            "foto_url": "https://via.placeholder.com/150",
            "en_lista_negra": True,
            "motivo_bloqueo": "Reporte de conducta inapropiada"
        }
    }
    
    eventos_recientes = [
        {"hora": "14:23", "placa": "ABC-1234", "tipo": "entrada", "persona": "Juan Pérez", "casa": "15", "status": "ok"},
        {"hora": "14:18", "placa": "XYZ-7890", "tipo": "salida", "persona": "María López", "casa": "22", "status": "ok"},
        {"hora": "14:05", "placa": "GHI-9999", "tipo": "entrada", "persona": "Visitante", "casa": "8", "status": "manual"},
        {"hora": "13:47", "placa": "JKL-3456", "tipo": "salida", "persona": "Carlos Ruiz", "casa": "31", "status": "ok"},
    ]
    
    return vehiculos_db, eventos_recientes


def registrar_evento(placa, tipo, persona, casa, verificacion_manual=False):
    """Registra un evento de acceso"""
    evento = {
        "timestamp": datetime.now(),
        "placa": placa,
        "tipo": tipo,
        "persona": persona,
        "casa": casa,
        "guardia": st.session_state.get("guardia_nombre", "Juan Pérez"),
        "gate": "GATE_001",
        "verificacion_manual": verificacion_manual
    }
    
    # En producción: guardar en Supabase
    if "eventos" not in st.session_state:
        st.session_state.eventos = []
    st.session_state.eventos.insert(0, evento)
    
    return evento


def mostrar_header():
    """Header con info del vigilante y turno"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 🏠 Caseta Norte")
    
    with col2:
        turno = "Matutino" if datetime.now().hour < 14 else "Vespertino"
        st.markdown(f"**Turno:** {turno}")
    
    with col3:
        guardia = st.session_state.get("guardia_nombre", "Juan Pérez")
        st.markdown(f"**👤 {guardia}**")
    
    st.divider()


def vista_escaneo():
    """Vista principal de escaneo de placas"""
    st.markdown("## 📸 Registro de Acceso")
    
    # Opción 1: Captura con cámara de la tablet
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📷 Tomar Foto de Placa")
        
        # Camera input nativo de Streamlit
        foto_placa = st.camera_input(
            "Captura la placa del vehículo",
            label_visibility="collapsed"
        )
        
        if foto_placa is not None:
            st.image(foto_placa, caption="Foto capturada", width=200)
            
            # Botón para procesar la foto
            if st.button("🔍 ANALIZAR PLACA", use_container_width=True, type="primary"):
                with st.spinner("Procesando imagen..."):
                    # TODO: En producción usar OCR (Tesseract, Google Vision, etc.)
                    # Por ahora: pedir ingreso manual después de la foto
                    st.session_state.foto_guardada = foto_placa
                    st.session_state.modo_ingreso = "con_foto"
                    time.sleep(0.5)
                    st.info("💡 Ingresa la placa manualmente abajo")
    
    with col2:
        st.markdown("### ⌨️ Búsqueda Manual")
        
        # Mostrar hint si hay foto capturada
        if "foto_guardada" in st.session_state:
            st.caption("Ingresa la placa que viste en la foto ↑")
        
        placa_manual = st.text_input(
            "Ingresa placa",
            placeholder="ABC-1234",
            max_chars=10,
            label_visibility="collapsed",
            key="input_placa"
        ).upper()
        
        if st.button("🔍 BUSCAR", use_container_width=True):
            if placa_manual:
                st.session_state.placa_escaneada = placa_manual
                st.session_state.confianza = 1.0  # Manual = 100% confianza
                st.rerun()
            else:
                st.warning("⚠️ Ingresa una placa válida")


def vista_verificacion(placa, confianza):
    """Muestra la información del vehículo y permite autorizar/denegar"""
    vehiculos_db, _ = get_mock_data()
    
    st.markdown("---")
    
    # Mostrar foto si existe
    if "foto_guardada" in st.session_state:
        with st.expander("📸 Ver foto capturada"):
            st.image(st.session_state.foto_guardada, width=300)
    
    # Verificar si existe en BD
    if placa in vehiculos_db:
        datos = vehiculos_db[placa]
        
        # LISTA NEGRA - Alerta crítica
        if datos.get("en_lista_negra", False):
            st.error("🚨 ALERTA DE SEGURIDAD")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(datos["foto_url"], width=150)
            
            with col2:
                st.markdown(f"### ❌ VEHÍCULO BLOQUEADO")
                st.markdown(f"**Placa:** {placa}")
                st.markdown(f"**Vehículo:** {datos['vehiculo']}")
                st.markdown(f"**Motivo:** {datos.get('motivo_bloqueo', 'No especificado')}")
            
            st.error("⛔ ACCESO DENEGADO AUTOMÁTICAMENTE")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🚨 NOTIFICAR SEGURIDAD", use_container_width=True, type="primary"):
                    st.success("✅ Notificación enviada a seguridad")
                    time.sleep(1)
                    limpiar_escaneo()
                    st.rerun()
            
            with col_btn2:
                if st.button("📞 CONTACTAR ADMIN", use_container_width=True):
                    st.info("Llamando a administración...")
            
            return
        
        # VEHÍCULO AUTORIZADO
        st.success(f"✅ VEHÍCULO REGISTRADO (Confianza: {confianza*100:.0f}%)")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(datos["foto_url"], caption=f"Placa: {placa}")
        
        with col2:
            st.markdown(f"### {datos['persona']}")
            st.markdown(f"**Tipo:** {datos['tipo'].title()}")
            st.markdown(f"**Casa/Depto:** {datos['casa']}")
            st.markdown(f"**Vehículo:** {datos['vehiculo']}")
            
            if datos["ultima_visita"]:
                tiempo_desde = datetime.now() - datos["ultima_visita"]
                if tiempo_desde.days > 0:
                    st.markdown(f"**Última visita:** Hace {tiempo_desde.days} días")
                elif tiempo_desde.seconds > 3600:
                    st.markdown(f"**Última visita:** Hace {tiempo_desde.seconds//3600} horas")
                else:
                    st.markdown(f"**Última visita:** Hace {tiempo_desde.seconds//60} minutos")
        
        # Selección de tipo de acceso
        col_tipo1, col_tipo2 = st.columns(2)
        with col_tipo1:
            tipo_acceso = st.radio(
                "Tipo de movimiento",
                ["🚗 ENTRADA", "🚙 SALIDA"],
                horizontal=True,
                label_visibility="collapsed"
            )
        
        # Notas opcionales
        notas = st.text_input("📝 Notas (opcional)", placeholder="Ej: Trae visita, paquete grande, etc.")
        
        # Botones de acción
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ PERMITIR ACCESO", use_container_width=True, type="primary"):
                tipo = "entrada" if "ENTRADA" in tipo_acceso else "salida"
                registrar_evento(placa, tipo, datos["persona"], datos["casa"])
                st.success(f"✅ Acceso {tipo} registrado correctamente")
                st.balloons()
                time.sleep(1)
                limpiar_escaneo()
                st.rerun()
        
        with col_btn2:
            if st.button("❌ DENEGAR ACCESO", use_container_width=True):
                motivo = st.text_input("Motivo de denegación:")
                if motivo:
                    st.warning(f"⛔ Acceso denegado: {motivo}")
                    time.sleep(1)
                    limpiar_escaneo()
                    st.rerun()
    
    else:
        # VEHÍCULO NO REGISTRADO
        st.warning(f"⚠️ VEHÍCULO NO REGISTRADO")
        st.markdown(f"### Placa: {placa}")
        st.markdown(f"Confianza de lectura: {confianza*100:.0f}%")
        
        with st.form("registro_nuevo"):
            st.markdown("#### Registrar nuevo acceso")
            
            col1, col2 = st.columns(2)
            with col1:
                tipo_persona = st.selectbox(
                    "Tipo de persona",
                    ["Visitante", "Residente Nuevo", "Empleado Doméstico", "Delivery/Proveedor"]
                )
                nombre = st.text_input("Nombre completo *", placeholder="Juan Pérez")
            
            with col2:
                casa = st.text_input("Casa/Depto *", placeholder="15")
                telefono = st.text_input("Teléfono", placeholder="5512345678")
            
            tipo_acceso = st.radio("Tipo de movimiento", ["ENTRADA", "SALIDA"], horizontal=True)
            notas = st.text_area("Observaciones", placeholder="Ej: Autorizado por residente vía telefónica")
            
            col_submit1, col_submit2 = st.columns(2)
            with col_submit1:
                submitted = st.form_submit_button("✅ REGISTRAR Y PERMITIR", use_container_width=True, type="primary")
            with col_submit2:
                denegado = st.form_submit_button("❌ DENEGAR", use_container_width=True)
            
            if submitted:
                if nombre and casa:
                    tipo = "entrada" if tipo_acceso == "ENTRADA" else "salida"
                    registrar_evento(placa, tipo, nombre, casa, verificacion_manual=True)
                    st.success(f"✅ Nuevo {tipo_persona.lower()} registrado - Acceso permitido")
                    st.balloons()
                    time.sleep(2)
                    limpiar_escaneo()
                    st.rerun()
                else:
                    st.error("⚠️ Nombre y casa son obligatorios")
            
            if denegado:
                st.warning("⛔ Acceso denegado")
                time.sleep(1)
                limpiar_escaneo()
                st.rerun()


def mostrar_eventos_recientes():
    """Lista de eventos recientes del día"""
    _, eventos_mock = get_mock_data()
    
    # Combinar con eventos nuevos de la sesión
    eventos_sesion = st.session_state.get("eventos", [])
    
    st.markdown("### 📋 Accesos Recientes (Hoy)")
    
    total_hoy = len(eventos_mock) + len(eventos_sesion)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total hoy", total_hoy)
    col2.metric("Entradas", random.randint(20, 30))
    col3.metric("Salidas", random.randint(15, 25))
    
    st.markdown("---")
    
    # Mostrar eventos de la sesión
    for evento in eventos_sesion[:5]:
        hora = evento["timestamp"].strftime("%H:%M")
        tipo_icon = "🚗" if evento["tipo"] == "entrada" else "🚙"
        status_icon = "⚠️" if evento.get("verificacion_manual") else "✅"
        
        st.markdown(f"""
        <div class="evento-card evento-{evento['tipo']}">
            <strong>{hora}</strong> • {tipo_icon} {evento['tipo'].upper()} {status_icon}<br>
            <strong>{evento['placa']}</strong> • {evento['persona']}<br>
            Casa {evento['casa']} • Guardia: {evento['guardia']}
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar eventos mock
    for evento in eventos_mock[:3]:
        tipo_class = f"evento-{evento['tipo']}"
        if evento["status"] == "manual":
            tipo_class = "evento-alerta"
        
        tipo_icon = "🚗" if evento["tipo"] == "entrada" else "🚙"
        status_icon = "⚠️" if evento["status"] == "manual" else "✅"
        
        st.markdown(f"""
        <div class="evento-card {tipo_class}">
            <strong>{evento['hora']}</strong> • {tipo_icon} {evento['tipo'].upper()} {status_icon}<br>
            <strong>{evento['placa']}</strong> • {evento['persona']}<br>
            Casa {evento['casa']}
        </div>
        """, unsafe_allow_html=True)


def limpiar_escaneo():
    """Limpia los datos de escaneo"""
    if "placa_escaneada" in st.session_state:
        del st.session_state.placa_escaneada
    if "confianza" in st.session_state:
        del st.session_state.confianza
    if "foto_guardada" in st.session_state:
        del st.session_state.foto_guardada
    if "modo_ingreso" in st.session_state:
        del st.session_state.modo_ingreso


def main():
    # Inicializar sesión
    if "guardia_nombre" not in st.session_state:
        st.session_state.guardia_nombre = "Juan Pérez"
    
    # Header
    mostrar_header()
    
    # Layout principal
    col_principal, col_lateral = st.columns([2, 1])
    
    with col_principal:
        # Vista de escaneo
        vista_escaneo()
        
        # Si hay placa escaneada, mostrar verificación
        if "placa_escaneada" in st.session_state:
            placa = st.session_state.placa_escaneada
            confianza = st.session_state.get("confianza", 0.95)
            vista_verificacion(placa, confianza)
            
            # Botón para cancelar
            if st.button("🔄 NUEVA BÚSQUEDA", use_container_width=True):
                limpiar_escaneo()
                st.rerun()
    
    with col_lateral:
        # Eventos recientes
        mostrar_eventos_recientes()
    
    # Footer con botones de emergencia/ayuda
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        if st.button("🚨 EMERGENCIA", use_container_width=True):
            st.error("🚨 Protocolo de emergencia activado")
    
    with col_f2:
        if st.button("📊 REPORTES", use_container_width=True):
            st.info("Abriendo módulo de reportes...")
    
    with col_f3:
        if st.button("⚙️ CONFIGURACIÓN", use_container_width=True):
            st.info("Abriendo configuración...")


if __name__ == "__main__":
    main()
