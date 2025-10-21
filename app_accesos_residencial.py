import time, pandas as pd, streamlit as st
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
# from supabase import create_client, Client

st.set_page_config(page_title="Caseta · Consola", layout="wide")
import time, pandas as pd, streamlit as st
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Caseta · Consola", layout="wide")


@st.cache_data
def get_mock_data():
    """Genera datos mock para la demo.

    Retorna: (eventos, personas, vehiculos, policies)
    """
    eventos_data = []
    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
        evento = {
            "id": i + 1,
            "timestamp": timestamp.isoformat(),
            "tipo": random.choice(["entrada", "salida"]),
            "gate_id": random.choice(["GATE_001", "GATE_002", "GATE_003"]),
            "guardia_id": random.choice(["GUARD_001", "GUARD_002", "GUARD_003"]),
            "doc_verificada": random.choice([True, False]),
            "placa_verificada": random.choice([True, False]),
            "notas": random.choice(["", "Visitante", "Residente", "Autorizado"])
        }
        eventos_data.append(evento)

    nombres = ["Juan Pérez", "María García", "Carlos López", "Ana Martínez", "Luis Rodríguez", "Carmen Fernández"]
    personas_data = []
    for i in range(50):
        persona = {
            "id": i + 1,
            "nombre": random.choice(nombres),
            "tipo": random.choice(["residente", "visitante", "empleado"]),
            "curp": f"CURP{str(i+1).zfill(3)}",
            "doc_tipo": random.choice(["INE", "Pasaporte", "Licencia"]),
            "ultima_verificacion_ts": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "status": random.choice(["activo", "inactivo", "pendiente"])
        }
        personas_data.append(persona)

    vehiculos_data = []
    estados = ["CDMX", "EDO", "JAL", "NL", "QRO"]
    for i in range(30):
        vehiculo = {
            "id": i + 1,
            "persona_id": random.randint(1, 50),
            "placa": f"{random.choice(['ABC', 'XYZ', 'DEF'])}-{random.randint(100, 999)}",
            "estado_mex": random.choice(estados),
            "placa_confianza": round(random.uniform(0.7, 1.0), 2),
            "ultimo_ingreso_ts": (datetime.now() - timedelta(days=random.randint(0, 15))).isoformat()
        }
        vehiculos_data.append(vehiculo)

    policies_data = [
        {
            "id": 1,
            "nombre": "Horario de Acceso Residentes",
            "descripcion": "Los residentes tienen acceso 24/7 al fraccionamiento con identificación válida",
            "tipo": "Acceso",
            "activa": True,
            "prioridad": "Alta",
            "aplicable_a": "Residentes",
            "created_at": (datetime.now() - timedelta(days=30)).isoformat()
        },
        {
            "id": 2,
            "nombre": "Horario de Visitantes",
            "descripcion": "Los visitantes solo pueden ingresar de 6:00 AM a 10:00 PM, requieren autorización del residente",
            "tipo": "Acceso",
            "activa": True,
            "prioridad": "Alta",
            "aplicable_a": "Visitantes",
            "created_at": (datetime.now() - timedelta(days=25)).isoformat()
        },
        {
            "id": 3,
            "nombre": "Verificación Doble Factor",
            "descripcion": "Todo acceso requiere verificación de documento de identidad y placa vehicular",
            "tipo": "Verificación",
            "activa": True,
            "prioridad": "Crítica",
            "aplicable_a": "Todos",
            "created_at": (datetime.now() - timedelta(days=20)).isoformat()
        },
        {
            "id": 4,
            "nombre": "Lista Negra Vehicular",
            "descripcion": "Vehículos en lista negra son rechazados automáticamente",
            "tipo": "Restricción",
            "activa": True,
            "prioridad": "Crítica",
            "aplicable_a": "Vehículos",
            "created_at": (datetime.now() - timedelta(days=15)).isoformat()
        },
        {
            "id": 5,
            "nombre": "Registro de Empleados Domésticos",
            "descripcion": "Personal doméstico debe estar pre-registrado y autorizado por el residente",
            "tipo": "Registro",
            "activa": True,
            "prioridad": "Media",
            "aplicable_a": "Empleados",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat()
        },
        {
            "id": 6,
            "nombre": "Protocolo de Emergencia",
            "descripcion": "En caso de emergencia, permitir acceso inmediato a servicios de emergencia sin verificación",
            "tipo": "Emergencia",
            "activa": True,
            "prioridad": "Crítica",
            "aplicable_a": "Servicios Emergencia",
            "created_at": (datetime.now() - timedelta(days=8)).isoformat()
        },
        {
            "id": 7,
            "nombre": "Límite de Vehículos por Residente",
            "descripcion": "Cada residente puede registrar máximo 4 vehículos en el sistema",
            "tipo": "Límite",
            "activa": True,
            "prioridad": "Media",
            "aplicable_a": "Residentes",
            "created_at": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "id": 8,
            "nombre": "Delivery y Paquetería",
            "descripcion": "Servicios de delivery tienen acceso de 7:00 AM a 9:00 PM, registro temporal automático",
            "tipo": "Acceso",
            "activa": False,
            "prioridad": "Baja",
            "aplicable_a": "Delivery",
            "created_at": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "id": 9,
            "nombre": "Confianza Mínima de Placas",
            "descripcion": "Sistema requiere confianza mínima del 85% en lectura de placas para acceso automático",
            "tipo": "Verificación",
            "activa": True,
            "prioridad": "Alta",
            "aplicable_a": "Sistema",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "id": 10,
            "nombre": "Backup Manual",
            "descripcion": "En caso de falla del sistema, el guardia puede autorizar acceso manualmente",
            "tipo": "Contingencia",
            "activa": True,
            "prioridad": "Media",
            "aplicable_a": "Sistema",
            "created_at": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]

    return eventos_data, personas_data, vehiculos_data, policies_data


def render_dashboard(eventos_mock, personas_mock, vehiculos_mock, policies_mock):
    st.header("Dashboard")
    today = pd.Timestamp.now(tz='UTC').date().isoformat()

    entradas_hoy = [e for e in eventos_mock if e["tipo"] == "entrada" and e["timestamp"].startswith(today)]
    salidas_hoy = [e for e in eventos_mock if e["tipo"] == "salida" and e["timestamp"].startswith(today)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas hoy", len(entradas_hoy))
    c2.metric("Salidas hoy", len(salidas_hoy))
    c3.metric("Total Personas", len(personas_mock))
    c4.metric("Vehículos Registrados", len(vehiculos_mock))

    st.subheader("Análisis Visual")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Entradas vs Salidas (Últimos 7 días)**")
        dias = []
        entradas_por_dia = []
        salidas_por_dia = []
        for i in range(7):
            fecha = (datetime.now() - timedelta(days=i)).date().isoformat()
            dias.append(fecha)
            entradas_dia = len([e for e in eventos_mock if e["tipo"] == "entrada" and e["timestamp"].startswith(fecha)])
            salidas_dia = len([e for e in eventos_mock if e["tipo"] == "salida" and e["timestamp"].startswith(fecha)])
            entradas_por_dia.append(entradas_dia)
            salidas_por_dia.append(salidas_dia)
        df_dias = pd.DataFrame({'Fecha': dias, 'Entradas': entradas_por_dia, 'Salidas': salidas_por_dia})
        st.line_chart(df_dias.set_index('Fecha'))

    with col2:
        st.write("**Distribución por Tipo de Persona**")
        tipos_personas = {}
        for persona in personas_mock:
            tipo = persona['tipo']
            tipos_personas[tipo] = tipos_personas.get(tipo, 0) + 1
        df_tipos = pd.DataFrame(list(tipos_personas.items()), columns=['Tipo', 'Cantidad'])
        st.bar_chart(df_tipos.set_index('Tipo'))

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Actividad por Gate**")
        gates = {}
        for evento in eventos_mock:
            gate = evento['gate_id']
            gates[gate] = gates.get(gate, 0) + 1
        df_gates = pd.DataFrame(list(gates.items()), columns=['Gate', 'Eventos'])
        st.bar_chart(df_gates.set_index('Gate'))

    with col4:
        st.write("**Estados de Vehículos**")
        estados = {}
        for vehiculo in vehiculos_mock:
            estado = vehiculo['estado_mex']
            estados[estado] = estados.get(estado, 0) + 1
        df_estados = pd.DataFrame(list(estados.items()), columns=['Estado', 'Vehículos'])
        st.bar_chart(df_estados.set_index('Estado'))

    st.subheader("Métricas de Verificación")
    col5, col6, col7, col8 = st.columns(4)
    docs_verificadas = len([e for e in eventos_mock if e.get('doc_verificada')])
    placas_verificadas = len([e for e in eventos_mock if e.get('placa_verificada')])
    personas_activas = len([p for p in personas_mock if p['status'] == 'activo'])
    confianza_promedio = np.mean([v['placa_confianza'] for v in vehiculos_mock])
    col5.metric("Docs Verificadas", f"{docs_verificadas}/{len(eventos_mock)}")
    col6.metric("Placas Verificadas", f"{placas_verificadas}/{len(eventos_mock)}")
    col7.metric("Personas Activas", personas_activas)
    col8.metric("Confianza Promedio", f"{confianza_promedio:.2f}")

    st.subheader("Eventos Recientes")
    eventos_recientes = pd.DataFrame(eventos_mock[:10])
    if not eventos_recientes.empty:
        eventos_recientes['timestamp'] = pd.to_datetime(eventos_recientes['timestamp']).dt.strftime('%H:%M:%S')
        st.dataframe(eventos_recientes[['timestamp', 'tipo', 'gate_id', 'doc_verificada', 'placa_verificada']], width='stretch', hide_index=True)


def render_eventos_live(eventos_mock, personas_mock, vehiculos_mock, policies_mock):
    st.header("Eventos (en vivo)")
    interval = st.sidebar.slider("Refrescar cada (seg)", 3, 30, 6)
    placeholder = st.empty()

    # Usar st.experimental_memo para actualizar automáticamente sin bucle bloqueante
    for _ in range(1):
        eventos_live = eventos_mock.copy()
        for i in range(random.randint(0, 3)):
            nuevo_evento = {
                "timestamp": datetime.now().isoformat(),
                "tipo": random.choice(["entrada", "salida"]),
                "gate_id": random.choice(["GATE_001", "GATE_002", "GATE_003"]),
                "guardia_id": random.choice(["GUARD_001", "GUARD_002", "GUARD_003"]),
                "doc_verificada": random.choice([True, False]),
                "placa_verificada": random.choice([True, False]),
                "notas": random.choice(["", "Visitante", "Residente", "Autorizado"])
            }
            eventos_live.insert(0, nuevo_evento)

        df = pd.DataFrame(eventos_live[:100])
        placeholder.dataframe(df, width='stretch', hide_index=True)

    # Instrucción para refrescar la página automáticamente
    st.experimental_rerun()


def render_personas(eventos_mock, personas_mock, vehiculos_mock, policies_mock):
    st.header("Personas")
    df = pd.DataFrame(personas_mock)
    st.dataframe(df, width='stretch', hide_index=True)


def render_vehiculos(eventos_mock, personas_mock, vehiculos_mock, policies_mock):
    st.header("Vehículos")
    df = pd.DataFrame(vehiculos_mock)
    st.dataframe(df, width='stretch', hide_index=True)


def render_politicas(eventos_mock, personas_mock, vehiculos_mock, policies_mock):
    st.header("Políticas de Seguridad")
    df = pd.DataFrame(policies_mock)
    col1, col2, col3, col4 = st.columns(4)
    políticas_activas = len([p for p in policies_mock if p['activa']])
    políticas_críticas = len([p for p in policies_mock if p['prioridad'] == 'Crítica'])
    col1.metric("Total Políticas", len(policies_mock))
    col2.metric("Políticas Activas", políticas_activas)
    col3.metric("Políticas Críticas", políticas_críticas)
    col4.metric("Políticas Inactivas", len(policies_mock) - políticas_activas)

    st.subheader("Filtros")
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + list(set([p['tipo'] for p in policies_mock])))
    with col_filter2:
        filtro_prioridad = st.selectbox("Filtrar por Prioridad", ["Todos", "Crítica", "Alta", "Media", "Baja"])
    with col_filter3:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos", "Activas", "Inactivas"])

    policies_filtradas = policies_mock.copy()
    if filtro_tipo != "Todos":
        policies_filtradas = [p for p in policies_filtradas if p['tipo'] == filtro_tipo]
    if filtro_prioridad != "Todos":
        policies_filtradas = [p for p in policies_filtradas if p['prioridad'] == filtro_prioridad]
    if filtro_estado == "Activas":
        policies_filtradas = [p for p in policies_filtradas if p['activa']]
    elif filtro_estado == "Inactivas":
        policies_filtradas = [p for p in policies_filtradas if not p['activa']]

    st.subheader(f"Políticas ({len(policies_filtradas)} encontradas)")
    for policy in policies_filtradas:
        if policy['prioridad'] == 'Crítica':
            border_color = "🔴"
        elif policy['prioridad'] == 'Alta':
            border_color = "🟠"
        elif policy['prioridad'] == 'Media':
            border_color = "🟡"
        else:
            border_color = "🟢"
        estado_icon = "✅" if policy['activa'] else "❌"
        with st.container():
            col_main, col_status = st.columns([4, 1])
            with col_main:
                st.write(f"**{border_color} {policy['nombre']}**")
                st.write(f"📝 {policy['descripcion']}")
                st.write(f"🏷️ **Tipo:** {policy['tipo']} | **Aplicable a:** {policy['aplicable_a']}")
                st.write(f"📅 **Creado:** {pd.to_datetime(policy['created_at']).strftime('%d/%m/%Y')}")
            with col_status:
                st.write(f"**Estado:** {estado_icon}")
                st.write(f"**Prioridad:** {policy['prioridad']}")
                if policy['activa']:
                    if st.button(f"Desactivar", key=f"deactivate_{policy['id']}"):
                        st.info(f"Política '{policy['nombre']}' desactivada")
                else:
                    if st.button(f"Activar", key=f"activate_{policy['id']}"):
                        st.success(f"Política '{policy['nombre']}' activada")
            st.divider()


def main():
    eventos_mock, personas_mock, vehiculos_mock, policies_mock = get_mock_data()
    st.sidebar.title("Caseta · Consola")
    tab = st.sidebar.radio("Módulos", ["Dashboard", "Eventos (en vivo)", "Personas", "Vehículos", "Políticas"])
    if tab == "Dashboard":
        render_dashboard(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif tab == "Eventos (en vivo)":
        render_eventos_live(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif tab == "Personas":
        render_personas(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif tab == "Vehículos":
        render_vehiculos(eventos_mock, personas_mock, vehiculos_mock, policies_mock)
    elif tab == "Políticas":
        render_politicas(eventos_mock, personas_mock, vehiculos_mock, policies_mock)


if __name__ == "__main__":
    main()
