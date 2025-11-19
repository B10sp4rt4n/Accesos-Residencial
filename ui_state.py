"""
ui_state.py
Gestión de estado jerárquico para dropdowns en cascada
Soluciona resets automáticos y sincronización MSP → Condominio → Torre → Unidad → Residente
"""

import streamlit as st


def reset_lower(level):
    """
    Resetea niveles inferiores según el nivel que cambió
    
    Args:
        level: Nivel que cambió ('msp', 'condominio', 'torre', 'unidad')
    """
    if level == "msp":
        st.session_state.pop("condominio", None)
        st.session_state.pop("torre", None)
        st.session_state.pop("unidad", None)
        st.session_state.pop("residente", None)

    elif level == "condominio":
        st.session_state.pop("torre", None)
        st.session_state.pop("unidad", None)
        st.session_state.pop("residente", None)

    elif level == "torre":
        st.session_state.pop("unidad", None)
        st.session_state.pop("residente", None)

    elif level == "unidad":
        st.session_state.pop("residente", None)
