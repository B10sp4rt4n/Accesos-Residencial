"""
modulos/politicas.py
Gestión de políticas de acceso con motor de reglas AUP-EXO
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
from typing import Dict, List, Optional
from core import get_db, evaluar_reglas
from core.motor_reglas import TIPOS_CONDICION


def render_politicas():
    """Renderiza interfaz de gestión de políticas"""
    st.header("📋 Políticas de Acceso")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Ver Todas",
        "Crear Nueva",
        "Pruebas",
        "Log de Evaluaciones"
    ])
    
    with tab1:
        _render_lista_politicas()
    
    with tab2:
        _render_formulario_politica()
    
    with tab3:
        _render_prueba_politicas()
    
    with tab4:
        _render_log_evaluaciones()


def _render_lista_politicas():
    """Lista todas las políticas registradas"""
    st.subheader("Políticas Configuradas")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_estado = st.selectbox(
            "Estado",
            ["Todas", "activas", "inactivas"]
        )
    
    with col2:
        filtro_prioridad = st.selectbox(
            "Prioridad",
            ["Todas", "critica", "alta", "media", "baja"]
        )
    
    with col3:
        filtro_tipo = st.selectbox(
            "Tipo",
            ["Todos", "residente", "visitante", "empleado", "proveedor", "global"]
        )
    
    # Obtener políticas
    politicas = _obtener_politicas_filtradas(filtro_estado, filtro_prioridad, filtro_tipo)
    
    if not politicas:
        st.info("No hay políticas registradas")
        return
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(politicas)
    activas = len([p for p in politicas if p['activa']])
    criticas = len([p for p in politicas if p['prioridad'] == 'critica'])
    
    col1.metric("Total Políticas", total)
    col2.metric("Activas", activas, delta=f"{(activas/total*100):.0f}%")
    col3.metric("Inactivas", total - activas)
    col4.metric("Críticas", criticas)
    
    # Lista de políticas
    st.markdown("---")
    
    for politica in politicas:
        _render_politica_card(politica)


def _render_politica_card(politica: Dict):
    """Renderiza tarjeta de política individual"""
    
    # Iconos según prioridad
    prioridad_icons = {
        "critica": "🔴",
        "alta": "🟠",
        "media": "🟡",
        "baja": "🟢"
    }
    
    estado_icon = "✅" if politica['activa'] else "❌"
    prioridad_icon = prioridad_icons.get(politica['prioridad'], "⚪")
    
    with st.expander(
        f"{prioridad_icon} {politica['nombre']} {estado_icon}",
        expanded=False
    ):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Descripción:** {politica['descripcion']}")
            st.write(f"**Tipo:** {politica['tipo_entidad']}")
            st.write(f"**Prioridad:** {politica['prioridad']}")
            
            # Mostrar condiciones
            if politica['condiciones']:
                st.write("**Condiciones:**")
                condiciones = json.loads(politica['condiciones'])
                
                for i, cond in enumerate(condiciones, 1):
                    st.write(f"{i}. {_formatear_condicion(cond)}")
        
        with col2:
            st.write(f"**Estado:** {'Activa' if politica['activa'] else 'Inactiva'}")
            st.write(f"**Orden:** {politica['orden']}")
            st.write(f"**Creada:** {pd.to_datetime(politica['created_at']).strftime('%d/%m/%Y')}")
            
            # Acciones
            if politica['activa']:
                if st.button("Desactivar", key=f"deact_{politica['id']}"):
                    _cambiar_estado_politica(politica['id'], False)
            else:
                if st.button("Activar", key=f"act_{politica['id']}"):
                    _cambiar_estado_politica(politica['id'], True)
            
            if st.button("Editar", key=f"edit_{politica['id']}"):
                st.session_state.editando_politica = politica['id']
            
            if st.button("Eliminar", key=f"del_{politica['id']}"):
                if st.confirm(f"¿Eliminar política '{politica['nombre']}'?"):
                    _eliminar_politica(politica['id'])


def _render_formulario_politica():
    """Formulario para crear/editar política"""
    st.subheader("Crear Nueva Política")
    
    with st.form("form_politica"):
        # Información básica
        st.markdown("### Información General")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre de la Política *")
            tipo_entidad = st.selectbox(
                "Aplicable a *",
                ["global", "residente", "visitante", "empleado", "proveedor"]
            )
            prioridad = st.selectbox(
                "Prioridad *",
                ["critica", "alta", "media", "baja"]
            )
        
        with col2:
            descripcion = st.text_area("Descripción *", height=100)
            orden = st.number_input(
                "Orden de Evaluación",
                min_value=1,
                max_value=100,
                value=10,
                help="Las políticas se evalúan en orden ascendente"
            )
            activa = st.checkbox("Activar inmediatamente", value=True)
        
        # Condiciones
        st.markdown("### Condiciones")
        st.write("Define las condiciones que deben cumplirse para que esta política se aplique")
        
        condiciones = []
        
        # Condición de horario
        st.markdown("#### 1. Restricción de Horario")
        usar_horario = st.checkbox("Aplicar restricción de horario")
        
        if usar_horario:
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                hora_inicio = st.time_input("Hora inicio permitida", value=time(6, 0))
            with col_h2:
                hora_fin = st.time_input("Hora fin permitida", value=time(22, 0))
            
            condiciones.append({
                "tipo": "horario",
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "hora_fin": hora_fin.strftime("%H:%M")
            })
        
        # Condición de días
        st.markdown("#### 2. Restricción de Días")
        usar_dias = st.checkbox("Aplicar restricción de días")
        
        if usar_dias:
            dias_permitidos = st.multiselect(
                "Días permitidos",
                ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"],
                default=["lunes", "martes", "miercoles", "jueves", "viernes"]
            )
            
            condiciones.append({
                "tipo": "dias_semana",
                "dias_permitidos": dias_permitidos
            })
        
        # Condición de lista negra
        st.markdown("#### 3. Verificación de Lista Negra")
        verificar_lista_negra = st.checkbox("Bloquear acceso a entidades en lista negra", value=True)
        
        if verificar_lista_negra:
            condiciones.append({
                "tipo": "lista_negra",
                "accion": "denegar"
            })
        
        # Condición de autorización previa
        st.markdown("#### 4. Autorización Previa")
        requiere_autorizacion = st.checkbox("Requiere autorización previa")
        
        if requiere_autorizacion:
            metodo = st.selectbox(
                "Método de autorización",
                ["residente", "administracion", "sistema"]
            )
            
            condiciones.append({
                "tipo": "autorizacion_previa",
                "metodo": metodo
            })
        
        # Condición personalizada (JSON)
        st.markdown("#### 5. Condición Personalizada (Avanzado)")
        usar_custom = st.checkbox("Agregar condición personalizada")
        
        if usar_custom:
            json_custom = st.text_area(
                "JSON de condición",
                placeholder='{"tipo": "custom", "campo": "valor"}',
                height=100
            )
            
            try:
                if json_custom:
                    cond_custom = json.loads(json_custom)
                    condiciones.append(cond_custom)
            except json.JSONDecodeError:
                st.error("JSON inválido")
        
        # Acción de la política
        st.markdown("### Acción")
        
        accion = st.radio(
            "¿Qué hacer cuando las condiciones se cumplen?",
            ["permitir", "denegar", "requiere_aprobacion"]
        )
        
        # Submit
        submitted = st.form_submit_button("Crear Política", type="primary")
        
        if submitted:
            if not nombre or not descripcion:
                st.error("Nombre y descripción son obligatorios")
                return
            
            # Crear política
            try:
                _crear_politica(
                    nombre=nombre,
                    descripcion=descripcion,
                    tipo_entidad=tipo_entidad,
                    prioridad=prioridad,
                    condiciones=condiciones,
                    accion=accion,
                    orden=orden,
                    activa=activa
                )
                
                st.success(f"✅ Política '{nombre}' creada correctamente")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error al crear política: {str(e)}")


def _render_prueba_politicas():
    """Herramienta de prueba de políticas"""
    st.subheader("🧪 Probar Evaluación de Políticas")
    
    st.write("""
    Simula un evento de acceso para ver qué políticas se aplicarían 
    y cuál sería el resultado final.
    """)
    
    with st.form("test_politicas"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_entidad_test = st.selectbox(
                "Tipo de entidad",
                ["residente", "visitante", "empleado", "proveedor"]
            )
            
            entidad_id_test = st.number_input(
                "ID de entidad (opcional)",
                min_value=0,
                value=0
            )
            
            lista_negra_test = st.checkbox("Entidad en lista negra")
        
        with col2:
            fecha_test = st.date_input("Fecha del acceso")
            hora_test = st.time_input("Hora del acceso")
            
            tiene_autorizacion = st.checkbox("Tiene autorización previa")
        
        submitted_test = st.form_submit_button("🧪 Evaluar Políticas")
        
        if submitted_test:
            # Construir contexto de prueba
            contexto_prueba = {
                "tipo_entidad": tipo_entidad_test,
                "entidad_id": entidad_id_test if entidad_id_test > 0 else None,
                "lista_negra": lista_negra_test,
                "timestamp": datetime.combine(fecha_test, hora_test),
                "tiene_autorizacion": tiene_autorizacion
            }
            
            # Evaluar
            with st.spinner("Evaluando políticas..."):
                resultado = evaluar_reglas(
                    tipo_entidad=tipo_entidad_test,
                    entidad_id=entidad_id_test if entidad_id_test > 0 else None,
                    contexto=contexto_prueba
                )
            
            # Mostrar resultado
            st.markdown("---")
            st.subheader("Resultado de la Evaluación")
            
            if resultado['autorizado']:
                st.success("✅ ACCESO AUTORIZADO")
            else:
                st.error("❌ ACCESO DENEGADO")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            
            col_r1.metric("Políticas Evaluadas", resultado['total_evaluadas'])
            col_r2.metric("Políticas Aplicadas", resultado['total_aplicadas'])
            col_r3.metric("Resultado", "Autorizado" if resultado['autorizado'] else "Denegado")
            
            # Detalles
            with st.expander("Ver detalles de evaluación"):
                st.json(resultado)


def _render_log_evaluaciones():
    """Log de evaluaciones de políticas"""
    st.subheader("📜 Historial de Evaluaciones")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=datetime.now().date() - pd.Timedelta(days=7)
        )
    
    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=datetime.now().date()
        )
    
    if st.button("🔍 Buscar Evaluaciones"):
        evaluaciones = _obtener_log_evaluaciones(fecha_desde, fecha_hasta)
        
        if not evaluaciones:
            st.info("No se encontraron evaluaciones en el periodo")
            return
        
        st.success(f"Se encontraron {len(evaluaciones)} evaluaciones")
        
        # DataFrame
        df = pd.DataFrame(evaluaciones)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "id": "ID",
                "timestamp": "Fecha/Hora",
                "politica_id": "Política",
                "evento_id": "Evento",
                "resultado": "Resultado",
                "motivo": "Motivo"
            }
        )


# Funciones auxiliares

def _obtener_politicas_filtradas(
    estado: str,
    prioridad: str,
    tipo: str
) -> List[Dict]:
    """Obtiene políticas con filtros"""
    with get_db() as conn:
        query = "SELECT * FROM politicas WHERE 1=1"
        params = []
        
        if estado == "activas":
            query += " AND activa = 1"
        elif estado == "inactivas":
            query += " AND activa = 0"
        
        if prioridad != "Todas":
            query += " AND prioridad = ?"
            params.append(prioridad)
        
        if tipo != "Todos":
            query += " AND tipo_entidad = ?"
            params.append(tipo)
        
        query += " ORDER BY orden ASC, prioridad DESC"
        
        cursor = conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _crear_politica(
    nombre: str,
    descripcion: str,
    tipo_entidad: str,
    prioridad: str,
    condiciones: List[Dict],
    accion: str,
    orden: int,
    activa: bool
):
    """Crea nueva política"""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO politicas (
                nombre, descripcion, tipo_entidad, condiciones,
                accion, prioridad, orden, activa, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            descripcion,
            tipo_entidad,
            json.dumps(condiciones),
            accion,
            prioridad,
            orden,
            1 if activa else 0,
            datetime.now().isoformat()
        ))
        conn.commit()


def _cambiar_estado_politica(politica_id: int, activa: bool):
    """Cambia el estado de una política"""
    with get_db() as conn:
        conn.execute(
            "UPDATE politicas SET activa = ?, updated_at = ? WHERE id = ?",
            (1 if activa else 0, datetime.now().isoformat(), politica_id)
        )
        conn.commit()
    
    st.success(f"Política {'activada' if activa else 'desactivada'}")
    st.rerun()


def _eliminar_politica(politica_id: int):
    """Elimina una política"""
    with get_db() as conn:
        conn.execute("DELETE FROM politicas WHERE id = ?", (politica_id,))
        conn.commit()
    
    st.success("Política eliminada")
    st.rerun()


def _formatear_condicion(condicion: Dict) -> str:
    """Formatea una condición para mostrarla"""
    tipo = condicion.get('tipo', 'desconocido')
    
    if tipo == "horario":
        return f"Horario: {condicion['hora_inicio']} - {condicion['hora_fin']}"
    elif tipo == "dias_semana":
        dias = ", ".join(condicion['dias_permitidos'])
        return f"Días: {dias}"
    elif tipo == "lista_negra":
        return "Verificar lista negra"
    elif tipo == "autorizacion_previa":
        return f"Requiere autorización: {condicion['metodo']}"
    else:
        return f"{tipo}: {json.dumps(condicion)}"


def _obtener_log_evaluaciones(
    fecha_desde: datetime.date,
    fecha_hasta: datetime.date
) -> List[Dict]:
    """Obtiene log de evaluaciones de políticas"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM log_reglas 
            WHERE DATE(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT 500
        """, (fecha_desde.isoformat(), fecha_hasta.isoformat()))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


if __name__ == "__main__":
    st.set_page_config(page_title="Políticas", layout="wide")
    render_politicas()
