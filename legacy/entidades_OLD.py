"""
modulos/entidades.py
Gestión de personas (residentes, visitantes, empleados) con AUP-EXO
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from core import get_db, OrquestadorAccesos, hash_entidad
from core.utils import validar_curp, validar_email, validar_telefono_mexico


def render_personas():
    """Renderiza interfaz de gestión de personas"""
    st.header("👥 Gestión de Personas")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["Ver Todas", "Registrar Nueva", "Buscar"])
    
    with tab1:
        _render_lista_personas()
    
    with tab2:
        _render_formulario_registro()
    
    with tab3:
        _render_busqueda_personas()


def _render_lista_personas():
    """Lista todas las personas registradas"""
    st.subheader("Personas Registradas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_tipo = st.selectbox(
            "Tipo",
            ["Todos", "residente", "visitante", "empleado", "proveedor"]
        )
    with col2:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todos", "activo", "inactivo", "bloqueado"]
        )
    with col3:
        limite = st.number_input("Mostrar registros", min_value=10, max_value=500, value=50)
    
    # Consultar DB
    personas = _obtener_personas_filtradas(filtro_tipo, filtro_estado, limite)
    
    if not personas:
        st.info("No hay personas registradas")
        return
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Personas", len(personas))
    col2.metric("Residentes", len([p for p in personas if p['tipo'] == 'residente']))
    col3.metric("Visitantes", len([p for p in personas if p['tipo'] == 'visitante']))
    col4.metric("Activos", len([p for p in personas if p['estado'] == 'activo']))
    
    # DataFrame
    df = pd.DataFrame(personas)
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y %H:%M')
    if 'updated_at' in df.columns:
        df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%d/%m/%Y %H:%M')
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "tipo": "Tipo",
            "nombre_completo": "Nombre Completo",
            "curp": "CURP",
            "telefono": "Teléfono",
            "email": "Email",
            "estado": "Estado",
            "created_at": "Registro"
        }
    )
    
    # Exportar datos
    if st.button("📥 Exportar a CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Descargar CSV",
            csv,
            "personas.csv",
            "text/csv"
        )


def _render_formulario_registro():
    """Formulario para registrar nueva persona"""
    st.subheader("Registrar Nueva Persona")
    
    with st.form("form_persona"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox(
                "Tipo de Persona *",
                ["residente", "visitante", "empleado", "proveedor"]
            )
            nombre = st.text_input("Nombre Completo *")
            curp = st.text_input("CURP", max_chars=18)
            telefono = st.text_input("Teléfono", placeholder="5512345678")
        
        with col2:
            email = st.text_input("Email", placeholder="ejemplo@correo.com")
            direccion = st.text_area("Dirección", height=100)
            
            if tipo == "residente":
                lote = st.text_input("Lote/Casa")
                manzana = st.text_input("Manzana")
            elif tipo == "visitante":
                residente_autoriza = st.text_input("Residente que Autoriza")
            
        notas = st.text_area("Notas/Observaciones")
        
        submitted = st.form_submit_button("Registrar Persona")
        
        if submitted:
            # Validaciones
            if not nombre or not tipo:
                st.error("Nombre y tipo son obligatorios")
                return
            
            if curp and not validar_curp(curp):
                st.error("CURP inválida")
                return
            
            if email and not validar_email(email):
                st.error("Email inválido")
                return
            
            if telefono and not validar_telefono_mexico(telefono):
                st.error("Teléfono inválido (debe ser 10 dígitos)")
                return
            
            # Registrar en DB
            try:
                orquestador = OrquestadorAccesos()
                
                datos_adicionales = {"notas": notas}
                if tipo == "residente":
                    datos_adicionales["lote"] = lote
                    datos_adicionales["manzana"] = manzana
                elif tipo == "visitante":
                    datos_adicionales["residente_autoriza"] = residente_autoriza
                
                entidad_id = orquestador.crear_entidad(
                    tipo=tipo,
                    nombre=nombre,
                    curp=curp,
                    telefono=telefono,
                    email=email,
                    direccion=direccion,
                    datos_adicionales=datos_adicionales
                )
                
                st.success(f"✅ Persona registrada con ID: {entidad_id}")
                st.balloons()
                
                # Mostrar hash de trazabilidad
                with st.expander("Ver detalles de trazabilidad"):
                    st.code(f"ID: {entidad_id}")
                    st.code(f"Hash: {hash_entidad({'nombre': nombre, 'curp': curp})[:16]}")
                
            except Exception as e:
                st.error(f"Error al registrar: {str(e)}")


def _render_busqueda_personas():
    """Búsqueda de personas"""
    st.subheader("🔍 Buscar Persona")
    
    criterio = st.selectbox(
        "Buscar por",
        ["Nombre", "CURP", "Teléfono", "Email"]
    )
    
    valor = st.text_input(f"Ingrese {criterio}")
    
    if st.button("Buscar") and valor:
        personas = _buscar_persona(criterio.lower(), valor)
        
        if not personas:
            st.warning("No se encontraron resultados")
            return
        
        st.success(f"Se encontraron {len(personas)} resultado(s)")
        
        for p in personas:
            with st.expander(f"{p['nombre_completo']} - {p['tipo']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {p['id']}")
                    st.write(f"**Tipo:** {p['tipo']}")
                    st.write(f"**CURP:** {p.get('curp', 'N/A')}")
                    st.write(f"**Teléfono:** {p.get('telefono', 'N/A')}")
                    st.write(f"**Email:** {p.get('email', 'N/A')}")
                
                with col2:
                    st.write(f"**Estado:** {p['estado']}")
                    st.write(f"**Hash:** {p.get('hash', 'N/A')[:16]}")
                    st.write(f"**Registrado:** {pd.to_datetime(p['created_at']).strftime('%d/%m/%Y')}")
                
                # Acciones
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    if st.button("Ver Historial", key=f"hist_{p['id']}"):
                        _mostrar_historial_accesos(p['id'])
                with col_a2:
                    if st.button("Editar", key=f"edit_{p['id']}"):
                        st.info("Función en desarrollo")
                with col_a3:
                    if p['estado'] == 'activo':
                        if st.button("Bloquear", key=f"block_{p['id']}"):
                            _cambiar_estado_persona(p['id'], 'bloqueado')
                    else:
                        if st.button("Activar", key=f"active_{p['id']}"):
                            _cambiar_estado_persona(p['id'], 'activo')


def _obtener_personas_filtradas(tipo: str, estado: str, limite: int) -> List[Dict]:
    """Obtiene personas de la base de datos con filtros"""
    with get_db() as conn:
        query = "SELECT * FROM entidades WHERE tipo_entidad = 'persona'"
        params = []
        
        if tipo != "Todos":
            query += " AND tipo = ?"
            params.append(tipo)
        
        if estado != "Todos":
            query += " AND estado = ?"
            params.append(estado)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limite)
        
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _buscar_persona(criterio: str, valor: str) -> List[Dict]:
    """Busca persona por criterio"""
    with get_db() as conn:
        query = "SELECT * FROM entidades WHERE tipo_entidad = 'persona'"
        
        if criterio == "nombre":
            query += " AND nombre_completo LIKE ?"
            valor = f"%{valor}%"
        elif criterio == "curp":
            query += " AND curp = ?"
        elif criterio == "telefono":
            query += " AND telefono = ?"
        elif criterio == "email":
            query += " AND email LIKE ?"
            valor = f"%{valor}%"
        
        cursor = conn.execute(query, [valor])
        columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _cambiar_estado_persona(persona_id: int, nuevo_estado: str):
    """Cambia el estado de una persona"""
    with get_db() as conn:
        conn.execute(
            "UPDATE entidades SET estado = ?, updated_at = ? WHERE id = ?",
            (nuevo_estado, datetime.now().isoformat(), persona_id)
        )
        conn.commit()
    
    st.success(f"Estado actualizado a: {nuevo_estado}")
    st.rerun()


def _mostrar_historial_accesos(persona_id: int):
    """Muestra historial de accesos de una persona"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM eventos 
            WHERE entidad_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (persona_id,))
        
        eventos = cursor.fetchall()
        
        if not eventos:
            st.info("No hay accesos registrados")
            return
        
        st.subheader(f"Últimos {len(eventos)} Accesos")
        
        for evento in eventos:
            tipo_icon = "🟢" if evento[3] == "entrada" else "🔴"
            resultado_icon = "✅" if evento[5] == "autorizado" else "❌"
            
            st.write(f"{tipo_icon} {pd.to_datetime(evento[1]).strftime('%d/%m/%Y %H:%M')} - {resultado_icon} {evento[5]}")


if __name__ == "__main__":
    st.set_page_config(page_title="Personas", layout="wide")
    render_personas()
