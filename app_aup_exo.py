"""
app.py - Aplicación principal AUP-EXO
Sistema de Control de Accesos Residencial
"""

import streamlit as st
from core import init_db
from modulos.entidades import render_personas
from modulos.accesos import render_vehiculos
from modulos.eventos import render_eventos
from modulos.vigilancia import render_vigilancia
from modulos.politicas import render_politicas


# Configuración de página
st.set_page_config(
    page_title="AUP-EXO - Control de Accesos",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inicializar_sistema():
    """Inicializa el sistema y la base de datos"""
    # Inicializar DB si no existe
    try:
        init_db()
    except Exception as e:
        st.error(f"Error al inicializar base de datos: {str(e)}")
        return False
    
    # Inicializar variables de sesión
    if "usuario_id" not in st.session_state:
        st.session_state.usuario_id = "admin"  # TODO: Sistema de login
    
    if "usuario_rol" not in st.session_state:
        st.session_state.usuario_rol = "administrador"
    
    return True


def render_sidebar():
    """Renderiza la barra lateral de navegación"""
    with st.sidebar:
        st.title("🏠 AUP-EXO")
        st.caption("Sistema de Control de Accesos")
        
        st.divider()
        
        # Información del usuario
        st.write(f"**Usuario:** {st.session_state.usuario_id}")
        st.write(f"**Rol:** {st.session_state.usuario_rol}")
        
        st.divider()
        
        # Navegación principal
        st.subheader("Módulos")
        
        modulo = st.radio(
            "Seleccionar módulo",
            [
                "🚨 Vigilancia",
                "📋 Eventos",
                "👥 Personas",
                "🚗 Vehículos",
                "📜 Políticas"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Acciones rápidas
        st.subheader("Acciones Rápidas")
        
        if st.button("🔄 Recargar Sistema"):
            st.cache_data.clear()
            st.rerun()
        
        if st.button("📊 Generar Reporte"):
            st.info("Generando reporte...")
        
        if st.button("⚙️ Configuración"):
            st.info("Módulo de configuración en desarrollo")
        
        st.divider()
        
        # Información del sistema
        st.caption("**Versión:** 2.0.0-aup-exo")
        st.caption("**Arquitectura:** AUP-EXO")
        st.caption("**Base de Datos:** SQLite")
        
        return modulo


def main():
    """Función principal de la aplicación"""
    
    # Inicializar sistema
    if not inicializar_sistema():
        st.error("❌ Error al inicializar el sistema")
        st.stop()
    
    # Renderizar sidebar y obtener módulo seleccionado
    modulo_seleccionado = render_sidebar()
    
    # Renderizar módulo correspondiente
    if modulo_seleccionado == "🚨 Vigilancia":
        render_vigilancia()
    
    elif modulo_seleccionado == "📋 Eventos":
        render_eventos()
    
    elif modulo_seleccionado == "👥 Personas":
        render_personas()
    
    elif modulo_seleccionado == "🚗 Vehículos":
        render_vehiculos()
    
    elif modulo_seleccionado == "📜 Políticas":
        render_politicas()


if __name__ == "__main__":
    main()
