# ui_state.py
import streamlit as st

def reset_lower(level):
    """
    Marca un reset pendiente para el SIGUIENTE ciclo de render.
    No elimina keys durante el render actual (evita que widgets desaparezcan).
    """
    st.session_state["reset_pending"] = level


def apply_pending_reset():
    """
    Aplica el reset pendiente al inicio del siguiente render.
    Debe llamarse al inicio de cada módulo/página.
    """
    level = st.session_state.get("reset_pending")
    if not level:
        return

    if level == "msp":
        for k in ["condominio", "torre", "unidad", "residente"]:
            st.session_state.pop(k, None)

    elif level == "condominio":
        for k in ["torre", "unidad", "residente"]:
            st.session_state.pop(k, None)

    elif level == "torre":
        for k in ["unidad", "residente"]:
            st.session_state.pop(k, None)

    elif level == "unidad":
        st.session_state.pop("residente", None)

    st.session_state["reset_pending"] = None


def safe_list(value):
    """
    Convierte None en lista vacía para evitar errores en selectbox
    """
    return value if value else []
