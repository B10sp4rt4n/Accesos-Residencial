import streamlit as st
from app_accesos_residencial import (
    get_mock_data,
    render_dashboard,
    render_eventos_live,
    render_personas,
    render_vehiculos,
    render_politicas,
)

st.set_page_config(page_title="Index · Caseta", layout="wide")

st.title("Caseta · Consola — Index")
st.write("Usa este índice para navegar localmente entre los módulos o para acceder a las URLs desplegadas (si las has configurado en Streamlit Cloud `Secrets`).")

mode = st.sidebar.radio("Modo", ["Local (render)", "Enlaces desplegadas"])

eventos_mock, personas_mock, vehiculos_mock, policies_mock = get_mock_data()

if mode == "Local (render)":
    app = st.sidebar.selectbox("Abrir módulo local:", ["Dashboard", "Eventos (en vivo)", "Personas", "Vehículos", "Políticas"])
    if app == "Dashboard":
        render_dashboard(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif app == "Eventos (en vivo)":
        render_eventos_live(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif app == "Personas":
        render_personas(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif app == "Vehículos":
        render_vehiculos(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif app == "Políticas":
        render_politicas(eventos_mock, personas_mock, vehiculos_mock, policies_mock)

else:
    st.header("Enlaces a apps desplegadas")
    st.write("Si ya desplegaste las apps en Streamlit Cloud, añade las URLs en Settings → Secrets como `DASHBOARD_URL`, `EVENTOS_URL`, `PERSONAS_URL`, `VEHICULOS_URL`, `POLITICAS_URL`.")

    urls = {
        "Dashboard": st.secrets.get("DASHBOARD_URL", ""),
        "Eventos (en vivo)": st.secrets.get("EVENTOS_URL", ""),
        "Personas": st.secrets.get("PERSONAS_URL", ""),
        "Vehículos": st.secrets.get("VEHICULOS_URL", ""),
        "Políticas": st.secrets.get("POLITICAS_URL", ""),
    }

    for name, url in urls.items():
        if url:
            st.markdown(f"- **{name}**: [{url}]({url})")
        else:
            st.markdown(f"- **{name}**: _No definida. Añade `{name.upper().split()[0]}_URL` en Secrets_")

    st.markdown("---")
    st.write("También puedes usar el enlace al repositorio para crear apps manualmente en Streamlit Cloud:")
    repo_url = st.secrets.get("REPO_URL", "https://github.com/B10sp4rt4n/Accesos-Residencial")
    st.markdown(f"- Repositorio: [{repo_url}]({repo_url})")
