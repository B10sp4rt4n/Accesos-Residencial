"""
modulos/accesos.py
Gestión de vehículos y control de accesos con AUP-EXO
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core import get_db, OrquestadorAccesos, evaluar_reglas
from core.utils import validar_placa_mexico, generar_codigo_qr_data


def render_vehiculos():
    """Renderiza interfaz de gestión de vehículos"""
    st.header("🚗 Gestión de Vehículos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Ver Todos", "Registrar Nuevo", "Buscar", "Lista Negra"])
    
    with tab1:
        _render_lista_vehiculos()
    
    with tab2:
        _render_formulario_vehiculo()
    
    with tab3:
        _render_busqueda_vehiculos()
    
    with tab4:
        _render_lista_negra()


def _render_lista_vehiculos():
    """Lista todos los vehículos registrados"""
    st.subheader("Vehículos Registrados")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filtro_tipo = st.selectbox(
            "Tipo",
            ["Todos", "auto", "moto", "camioneta", "pickup", "otro"]
        )
    with col2:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todos", "activo", "inactivo", "bloqueado"]
        )
    with col3:
        filtro_lista_negra = st.checkbox("Solo Lista Negra")
    with col4:
        limite = st.number_input("Mostrar", min_value=10, max_value=500, value=50)
    
    # Consultar DB
    vehiculos = _obtener_vehiculos_filtrados(filtro_tipo, filtro_estado, filtro_lista_negra, limite)
    
    if not vehiculos:
        st.info("No hay vehículos registrados")
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vehículos", len(vehiculos))
    col2.metric("Activos", len([v for v in vehiculos if v['estado'] == 'activo']))
    col3.metric("Lista Negra", len([v for v in vehiculos if v.get('lista_negra')]))
    col4.metric("Accesos Hoy", _contar_accesos_vehiculos_hoy())
    
    # DataFrame
    df = pd.DataFrame(vehiculos)
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "placa": "Placa",
            "estado_mx": "Estado",
            "tipo": "Tipo",
            "propietario_id": "ID Propietario",
            "estado": "Estado",
            "lista_negra": st.column_config.CheckboxColumn("Lista Negra")
        }
    )
    
    # Exportar
    if st.button("📥 Exportar CSV"):
        csv = df.to_csv(index=False)
        st.download_button("Descargar", csv, "vehiculos.csv", "text/csv")


def _render_formulario_vehiculo():
    """Formulario para registrar vehículo"""
    st.subheader("Registrar Nuevo Vehículo")
    
    with st.form("form_vehiculo"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Datos del Vehículo**")
            placa = st.text_input(
                "Placa *",
                max_chars=10,
                help="Formato: ABC-123-D o ABC-1234"
            ).upper()
            
            estado_mx = st.selectbox(
                "Estado (México) *",
                ["CDMX", "EDO", "JAL", "NL", "QRO", "GTO", "PUE", "VER", "YUC", "Otro"]
            )
            
            tipo_vehiculo = st.selectbox(
                "Tipo *",
                ["auto", "moto", "camioneta", "pickup", "camion", "otro"]
            )
            
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            color = st.text_input("Color")
        
        with col2:
            st.write("**Propietario**")
            
            # Buscar propietario
            propietario_nombre = st.text_input("Buscar Propietario (nombre)")
            propietario_id = None
            
            if propietario_nombre:
                personas = _buscar_personas_por_nombre(propietario_nombre)
                if personas:
                    propietario_seleccionado = st.selectbox(
                        "Seleccionar Propietario",
                        personas,
                        format_func=lambda p: f"{p['nombre_completo']} - {p['tipo']}"
                    )
                    propietario_id = propietario_seleccionado['id']
                else:
                    st.warning("No se encontraron personas")
            
            st.write("**Observaciones**")
            notas = st.text_area("Notas")
            
            lista_negra = st.checkbox("Agregar a Lista Negra")
            if lista_negra:
                motivo_lista_negra = st.text_area("Motivo Lista Negra *")
        
        submitted = st.form_submit_button("Registrar Vehículo")
        
        if submitted:
            # Validaciones
            if not placa or not estado_mx or not tipo_vehiculo:
                st.error("Placa, estado y tipo son obligatorios")
                return
            
            resultado = validar_placa_mexico(placa)
            if not resultado["valida"]:
                st.error(f"Placa inválida: {resultado['mensaje']}")
                return
            
            if lista_negra and not motivo_lista_negra:
                st.error("Debe especificar motivo para lista negra")
                return
            
            # Verificar si placa ya existe
            if _verificar_placa_existe(placa):
                st.error("Esta placa ya está registrada")
                return
            
            # Registrar
            try:
                orquestador = OrquestadorAccesos()
                
                datos_adicionales = {
                    "marca": marca,
                    "modelo": modelo,
                    "color": color,
                    "notas": notas,
                    "lista_negra": lista_negra
                }
                
                if lista_negra:
                    datos_adicionales["motivo_lista_negra"] = motivo_lista_negra
                    datos_adicionales["fecha_lista_negra"] = datetime.now().isoformat()
                
                vehiculo_id = orquestador.crear_entidad(
                    tipo="vehiculo",
                    identificador=placa,
                    propietario_id=propietario_id,
                    datos_adicionales=datos_adicionales
                )
                
                st.success(f"✅ Vehículo registrado con ID: {vehiculo_id}")
                st.balloons()
                
                # Generar código QR
                if st.checkbox("Generar código QR"):
                    qr_data = generar_codigo_qr_data({
                        "tipo": "vehiculo",
                        "placa": placa,
                        "id": vehiculo_id
                    })
                    st.code(qr_data)
                
            except Exception as e:
                st.error(f"Error al registrar: {str(e)}")


def _render_busqueda_vehiculos():
    """Búsqueda de vehículos"""
    st.subheader("🔍 Buscar Vehículo")
    
    criterio = st.selectbox("Buscar por", ["Placa", "Propietario", "Marca/Modelo"])
    valor = st.text_input(f"Ingrese {criterio}")
    
    if st.button("Buscar") and valor:
        vehiculos = _buscar_vehiculo(criterio.lower(), valor)
        
        if not vehiculos:
            st.warning("No se encontraron resultados")
            return
        
        st.success(f"Se encontraron {len(vehiculos)} resultado(s)")
        
        for v in vehiculos:
            lista_negra_badge = "🚫 LISTA NEGRA" if v.get('lista_negra') else ""
            
            with st.expander(f"🚗 {v['placa']} ({v['estado_mx']}) {lista_negra_badge}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {v['id']}")
                    st.write(f"**Placa:** {v['placa']}")
                    st.write(f"**Estado:** {v['estado_mx']}")
                    st.write(f"**Tipo:** {v['tipo']}")
                    st.write(f"**Propietario ID:** {v.get('propietario_id', 'N/A')}")
                
                with col2:
                    st.write(f"**Estado:** {v['estado']}")
                    st.write(f"**Hash:** {v.get('hash', 'N/A')[:16]}")
                    st.write(f"**Registrado:** {pd.to_datetime(v['created_at']).strftime('%d/%m/%Y')}")
                    
                    if v.get('lista_negra'):
                        st.error(f"**Motivo:** {v.get('motivo_lista_negra', 'N/A')}")
                
                # Acciones
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    if st.button("Ver Historial", key=f"hist_{v['id']}"):
                        _mostrar_historial_vehiculo(v['id'])
                with col_a2:
                    if not v.get('lista_negra'):
                        if st.button("Agregar a Lista Negra", key=f"block_{v['id']}"):
                            _agregar_lista_negra(v['id'])
                    else:
                        if st.button("Quitar de Lista Negra", key=f"unblock_{v['id']}"):
                            _quitar_lista_negra(v['id'])


def _render_lista_negra():
    """Gestión de lista negra de vehículos"""
    st.subheader("🚫 Lista Negra de Vehículos")
    
    vehiculos_ln = _obtener_vehiculos_lista_negra()
    
    if not vehiculos_ln:
        st.info("No hay vehículos en lista negra")
        return
    
    st.metric("Vehículos en Lista Negra", len(vehiculos_ln))
    
    for v in vehiculos_ln:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.write(f"### 🚗 {v['placa']}")
                st.write(f"Estado: {v['estado_mx']}")
                st.write(f"Tipo: {v['tipo']}")
            
            with col2:
                st.write(f"**Motivo:** {v.get('motivo_lista_negra', 'N/A')}")
                st.write(f"**Fecha:** {pd.to_datetime(v.get('fecha_lista_negra', v['created_at'])).strftime('%d/%m/%Y')}")
            
            with col3:
                if st.button("Quitar", key=f"remove_ln_{v['id']}"):
                    _quitar_lista_negra(v['id'])
                    st.rerun()
            
            st.divider()


def _obtener_vehiculos_filtrados(tipo: str, estado: str, lista_negra: bool, limite: int) -> List[Dict]:
    """Obtiene vehículos con filtros"""
    with get_db() as conn:
        query = "SELECT * FROM entidades WHERE tipo_entidad = 'vehiculo'"
        params = []
        
        if tipo != "Todos":
            query += " AND tipo = ?"
            params.append(tipo)
        
        if estado != "Todos":
            query += " AND estado = ?"
            params.append(estado)
        
        if lista_negra:
            query += " AND lista_negra = 1"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limite)
        
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _buscar_vehiculo(criterio: str, valor: str) -> List[Dict]:
    """Busca vehículo por criterio"""
    with get_db() as conn:
        query = "SELECT * FROM entidades WHERE tipo_entidad = 'vehiculo'"
        
        if criterio == "placa":
            query += " AND placa LIKE ?"
            valor = f"%{valor}%"
        elif criterio == "propietario":
            # Buscar ID del propietario primero
            query += " AND propietario_id IN (SELECT id FROM entidades WHERE nombre_completo LIKE ?)"
            valor = f"%{valor}%"
        elif criterio == "marca/modelo":
            query += " AND (marca LIKE ? OR modelo LIKE ?)"
            valor = f"%{valor}%"
            cursor = conn.execute(query, [valor, valor])
        else:
            cursor = conn.execute(query, [valor])
        
        if criterio != "marca/modelo":
            cursor = conn.execute(query, [valor])
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _buscar_personas_por_nombre(nombre: str) -> List[Dict]:
    """Busca personas por nombre"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM entidades WHERE tipo_entidad = 'persona' AND nombre_completo LIKE ? LIMIT 10",
            (f"%{nombre}%",)
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _verificar_placa_existe(placa: str) -> bool:
    """Verifica si una placa ya existe"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM entidades WHERE tipo_entidad = 'vehiculo' AND placa = ?",
            (placa,)
        )
        return cursor.fetchone()[0] > 0


def _obtener_vehiculos_lista_negra() -> List[Dict]:
    """Obtiene vehículos en lista negra"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM entidades WHERE tipo_entidad = 'vehiculo' AND lista_negra = 1"
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _agregar_lista_negra(vehiculo_id: int):
    """Agrega vehículo a lista negra"""
    motivo = st.text_input("Motivo para agregar a lista negra")
    
    if st.button("Confirmar"):
        with get_db() as conn:
            conn.execute("""
                UPDATE entidades 
                SET lista_negra = 1, 
                    motivo_lista_negra = ?,
                    fecha_lista_negra = ?,
                    updated_at = ?
                WHERE id = ?
            """, (motivo, datetime.now().isoformat(), datetime.now().isoformat(), vehiculo_id))
            conn.commit()
        
        st.success("Vehículo agregado a lista negra")
        st.rerun()


def _quitar_lista_negra(vehiculo_id: int):
    """Quita vehículo de lista negra"""
    with get_db() as conn:
        conn.execute("""
            UPDATE entidades 
            SET lista_negra = 0, 
                motivo_lista_negra = NULL,
                fecha_lista_negra = NULL,
                updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), vehiculo_id))
        conn.commit()
    
    st.success("Vehículo removido de lista negra")
    st.rerun()


def _mostrar_historial_vehiculo(vehiculo_id: int):
    """Muestra historial de accesos del vehículo"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM eventos 
            WHERE vehiculo_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 30
        """, (vehiculo_id,))
        
        eventos = cursor.fetchall()
        
        if not eventos:
            st.info("No hay accesos registrados")
            return
        
        st.subheader(f"Últimos {len(eventos)} Accesos")
        
        df_eventos = pd.DataFrame(eventos)
        st.dataframe(df_eventos, use_container_width=True)


def _contar_accesos_vehiculos_hoy() -> int:
    """Cuenta accesos de vehículos hoy"""
    hoy = datetime.now().date().isoformat()
    
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT COUNT(*) FROM eventos 
            WHERE DATE(timestamp) = ? AND tipo_evento = 'acceso_vehicular'
        """, (hoy,))
        
        return cursor.fetchone()[0]


if __name__ == "__main__":
    st.set_page_config(page_title="Vehículos", layout="wide")
    render_vehiculos()
