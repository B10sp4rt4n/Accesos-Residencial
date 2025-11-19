# ui_state.py
import streamlit as st

def reset_lower(level):
    """
    Limpia niveles jerárquicos inferiores cada vez que un dropdown superior cambia.
    Esto previene valores fantasmas, listas vacías, reinicios incorrectos y
    desincronización entre MSP -> Condominio -> Torre -> Unidad -> Residente.
    """

    if level == "msp":
        for key in ("condominio", "torre", "unidad", "residente"):
            st.session_state.pop(key, None)

    elif level == "condominio":
        for key in ("torre", "unidad", "residente"):
            st.session_state.pop(key, None)

    elif level == "torre":
        for key in ("unidad", "residente"):
            st.session_state.pop(key, None)

    elif level == "unidad":
        st.session_state.pop("residente", None)


def safe_list(value):
    """
    Convierte None en lista vacía para evitar errores en selectbox
    """
    return value if value else []
