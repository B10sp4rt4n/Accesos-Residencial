# modulos/politicas.py
"""
POLÍTICAS (Reglas Estructurales) – AUP-EXO
Módulo para gestionar reglas que se aplican a ENTIDADES y EVENTOS.
"""

import json
import streamlit as st
from datetime import datetime
from core.db import get_db


# ---------------------------------------------------------
# Crear una política
# ---------------------------------------------------------
def crear_politica(nombre, descripcion, tipo, condiciones, prioridad=1, estado="activa", aplicable_a="global", created_by="sistema"):
    """
    Crea una nueva política en la base de datos.
    
    Args:
        nombre: Nombre descriptivo de la política
        descripcion: Explicación detallada
        tipo: Tipo de política (acceso, restriccion, horario, etc.)
        condiciones: Lista o dict con condiciones JSON
        prioridad: Nivel de prioridad (0=máxima, 10=mínima)
        estado: activa o inactiva
        aplicable_a: global, residente, visitante, proveedor, vehiculo
        created_by: Usuario que crea la política
    """
    # Generar ID único
    with get_db() as db:
        cursor = db.execute("SELECT COUNT(*) FROM politicas")
        count = cursor.fetchone()[0]
        politica_id = f"POL_{str(count + 1).zfill(3)}"
        
        timestamp = datetime.now().isoformat()
        
        db.execute("""
            INSERT INTO politicas 
            (politica_id, nombre, descripcion, tipo, condiciones, prioridad, estado, 
             aplicable_a, fecha_creacion, fecha_actualizacion, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            politica_id,
            nombre,
            descripcion,
            tipo,
            json.dumps(condiciones),
            prioridad,
            estado,
            aplicable_a,
            timestamp,
            timestamp,
            created_by
        ))
    
    return politica_id


# ---------------------------------------------------------
# Obtener políticas
# ---------------------------------------------------------
def obtener_politicas(estado=None, tipo=None):
    """
    Obtiene políticas de la base de datos con filtros opcionales.
    
    Args:
        estado: Filtrar por 'activa' o 'inactiva' (opcional)
        tipo: Filtrar por tipo de política (opcional)
    """
    with get_db() as db:
        query = "SELECT * FROM politicas WHERE 1=1"
        params = []
        
        if estado:
            query += " AND estado = ?"
            params.append(estado)
        
        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)
        
        query += " ORDER BY prioridad ASC, fecha_creacion DESC"
        
        rows = db.execute(query, params).fetchall()
    
    # Convertir a dicts y parsear condiciones JSON
    politicas = []
    for r in rows:
        politica = dict(r)
        
        # Parsear condiciones JSON
        if politica.get('condiciones'):
            try:
                politica['condiciones_obj'] = json.loads(politica['condiciones'])
            except json.JSONDecodeError:
                politica['condiciones_obj'] = {}
        
        politicas.append(politica)
    
    return politicas


# ---------------------------------------------------------
# Actualizar política
# ---------------------------------------------------------
def actualizar_politica(politica_id, nombre=None, descripcion=None, tipo=None, 
                       condiciones=None, prioridad=None, estado=None, aplicable_a=None):
    """
    Actualiza una política existente.
    Solo actualiza los campos que se proporcionen (no None).
    """
    with get_db() as db:
        # Obtener política actual
        cursor = db.execute("SELECT * FROM politicas WHERE politica_id = ?", (politica_id,))
        actual = cursor.fetchone()
        
        if not actual:
            return False
        
        actual_dict = dict(actual)
        
        # Preparar valores actualizados
        nuevo_nombre = nombre if nombre is not None else actual_dict['nombre']
        nueva_desc = descripcion if descripcion is not None else actual_dict['descripcion']
        nuevo_tipo = tipo if tipo is not None else actual_dict['tipo']
        nuevas_cond = json.dumps(condiciones) if condiciones is not None else actual_dict['condiciones']
        nueva_prio = prioridad if prioridad is not None else actual_dict['prioridad']
        nuevo_estado = estado if estado is not None else actual_dict['estado']
        nuevo_aplicable = aplicable_a if aplicable_a is not None else actual_dict['aplicable_a']
        
        timestamp = datetime.now().isoformat()
        
        db.execute("""
            UPDATE politicas
            SET nombre = ?, descripcion = ?, tipo = ?, condiciones = ?, 
                prioridad = ?, estado = ?, aplicable_a = ?, fecha_actualizacion = ?
            WHERE politica_id = ?
        """, (
            nuevo_nombre,
            nueva_desc,
            nuevo_tipo,
            nuevas_cond,
            nueva_prio,
            nuevo_estado,
            nuevo_aplicable,
            timestamp,
            politica_id
        ))
    
    return True


# ---------------------------------------------------------
# Activar/Desactivar política
# ---------------------------------------------------------
def cambiar_estado_politica(politica_id, nuevo_estado):
    """
    Activa o desactiva una política rápidamente.
    """
    return actualizar_politica(politica_id, estado=nuevo_estado)


# ---------------------------------------------------------
# UI – Gestión de políticas
# ---------------------------------------------------------
def ui_politicas():

    st.header("📋 Gestión de Políticas (Reglas de Acceso) – AUP-EXO")

    st.markdown("""
    **Políticas** son reglas parametrizables que determinan:
    - Quién puede acceder y cuándo
    - Restricciones por horario
    - Límites de visitas
    - Listas negras/blancas
    - Condiciones especiales
    
    Todas las políticas se evalúan automáticamente en el **Orquestador**.
    """)

    st.divider()

    # -------------------------
    # Tabs: Crear | Listar | Editar
    # -------------------------
    tab1, tab2, tab3 = st.tabs(["➕ Crear Política", "📋 Listar Políticas", "✏️ Editar/Gestionar"])

    # ==========================================
    # TAB 1: CREAR POLÍTICA
    # ==========================================
    with tab1:
        st.subheader("Crear nueva política")

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre de la política*", placeholder="Ej: Acceso Proveedores 6-18h")
            tipo = st.selectbox("Tipo de política*", [
                "acceso",
                "restriccion",
                "horario",
                "limite",
                "aprobacion"
            ])

        with col2:
            aplicable_a = st.selectbox("Aplicable a*", [
                "global",
                "residente",
                "visitante",
                "proveedor",
                "vehiculo",
                "persona"
            ])
            prioridad = st.number_input("Prioridad (0=máxima)", min_value=0, max_value=10, value=5)

        descripcion = st.text_area("Descripción", placeholder="Explique qué hace esta política...")

        st.divider()
        st.subheader("⚙️ Configuración de Condiciones")
        
        # Modo de entrada: Simple o Avanzado
        modo = st.radio("Modo de configuración:", ["🎯 Simple (Formulario)", "⚙️ Avanzado (JSON)"], horizontal=True)
        
        condiciones = {}
        condiciones_validas = False
        
        if modo == "🎯 Simple (Formulario)":
            # FORMULARIOS SEGÚN TIPO DE POLÍTICA
            
            if tipo == "horario":
                st.write("**Configurar Horario de Acceso**")
                col1, col2 = st.columns(2)
                with col1:
                    hora_inicio = st.time_input("Hora de inicio", value=None)
                with col2:
                    hora_fin = st.time_input("Hora de fin", value=None)
                
                dias_semana = st.multiselect(
                    "Días permitidos",
                    ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"],
                    default=["lunes", "martes", "miercoles", "jueves", "viernes"]
                )
                
                if hora_inicio and hora_fin and dias_semana:
                    condiciones = {
                        "tipo": "horario",
                        "hora_inicio": hora_inicio.strftime("%H:%M"),
                        "hora_fin": hora_fin.strftime("%H:%M"),
                        "dias": dias_semana
                    }
                    condiciones_validas = True
                    st.success("✅ Horario configurado correctamente")
                else:
                    st.warning("⚠️ Complete todos los campos de horario")
            
            elif tipo == "limite":
                st.write("**Configurar Límites de Visita**")
                col1, col2 = st.columns(2)
                with col1:
                    max_dia = st.number_input("Máximo de visitas por día", min_value=1, max_value=50, value=3)
                with col2:
                    max_mes = st.number_input("Máximo de visitas por mes", min_value=1, max_value=500, value=20)
                
                accion = st.selectbox("Acción al exceder límite:", ["denegar", "requiere_autorizacion", "alerta"])
                
                condiciones = {
                    "tipo": "limite",
                    "max_visitas_dia": max_dia,
                    "max_visitas_mes": max_mes,
                    "accion_exceso": accion
                }
                condiciones_validas = True
                st.success("✅ Límites configurados correctamente")
            
            elif tipo == "aprobacion":
                st.write("**Configurar Aprobación Requerida**")
                col1, col2 = st.columns(2)
                with col1:
                    requiere = st.checkbox("Requiere autorización previa", value=True)
                    nivel = st.selectbox("Nivel de autorización:", ["supervisor", "administrador", "gerencia"])
                with col2:
                    timeout = st.number_input("Timeout en minutos", min_value=5, max_value=240, value=30)
                    notificar = st.checkbox("Enviar notificación", value=True)
                
                condiciones = {
                    "tipo": "aprobacion",
                    "requiere_autorizacion": requiere,
                    "nivel_requerido": nivel,
                    "timeout_minutos": timeout,
                    "notificar": notificar
                }
                condiciones_validas = True
                st.success("✅ Aprobación configurada correctamente")
            
            elif tipo == "restriccion":
                st.write("**Configurar Restricción**")
                tipo_restriccion = st.selectbox("Tipo de restricción:", ["lista_negra", "zona_restringida", "horario_prohibido"])
                
                if tipo_restriccion == "lista_negra":
                    motivo = st.text_area("Motivo de restricción", placeholder="Ej: Incidente de seguridad previo")
                    generar_alerta = st.checkbox("Generar alerta al detectar", value=True)
                    
                    condiciones = {
                        "tipo": "lista_negra",
                        "accion": "denegar",
                        "motivo": motivo,
                        "alerta": generar_alerta
                    }
                elif tipo_restriccion == "zona_restringida":
                    zonas = st.multiselect("Zonas restringidas:", ["Area A", "Area B", "Area C", "Estacionamiento", "Torre 1", "Torre 2"])
                    condiciones = {
                        "tipo": "zona_restringida",
                        "zonas_prohibidas": zonas,
                        "accion": "denegar"
                    }
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        hora_inicio_prohibido = st.time_input("Desde", value=None)
                    with col2:
                        hora_fin_prohibido = st.time_input("Hasta", value=None)
                    
                    if hora_inicio_prohibido and hora_fin_prohibido:
                        condiciones = {
                            "tipo": "horario_prohibido",
                            "hora_inicio": hora_inicio_prohibido.strftime("%H:%M"),
                            "hora_fin": hora_fin_prohibido.strftime("%H:%M")
                        }
                
                if condiciones:
                    condiciones_validas = True
                    st.success("✅ Restricción configurada correctamente")
            
            elif tipo == "acceso":
                st.write("**Configurar Regla de Acceso**")
                acceso_24_7 = st.checkbox("Acceso 24/7 (sin restricciones)", value=False)
                
                if acceso_24_7:
                    condiciones = {
                        "tipo": "acceso_permanente",
                        "horario": "24/7"
                    }
                else:
                    requiere_validacion = st.checkbox("Requiere validación adicional", value=False)
                    tipos_permitidos = st.multiselect(
                        "Tipos de entidad permitidos:",
                        ["residente", "visitante", "proveedor", "servicio"],
                        default=["residente"]
                    )
                    
                    condiciones = {
                        "tipo": "acceso_controlado",
                        "requiere_validacion": requiere_validacion,
                        "tipos_permitidos": tipos_permitidos
                    }
                
                condiciones_validas = True
                st.success("✅ Acceso configurado correctamente")
            
            # Mostrar vista previa del JSON generado
            if condiciones_validas:
                with st.expander("📄 Ver JSON generado"):
                    st.json(condiciones)
        
        else:  # Modo Avanzado (JSON)
            st.write("**Editor JSON Avanzado**")
            
            # Plantillas de ejemplo
            plantilla = st.selectbox("Plantilla de ejemplo:", [
                "Personalizado",
                "Horario específico",
                "Límite de visitas",
                "Requiere autorización",
                "Lista negra"
            ])

            if plantilla == "Horario específico":
                ejemplo_condiciones = """{
  "tipo": "horario",
  "hora_inicio": "06:00",
  "hora_fin": "18:00",
  "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
}"""
            elif plantilla == "Límite de visitas":
                ejemplo_condiciones = """{
  "tipo": "limite",
  "max_visitas_dia": 3,
  "max_visitas_mes": 20,
  "accion_exceso": "denegar"
}"""
            elif plantilla == "Requiere autorización":
                ejemplo_condiciones = """{
  "tipo": "aprobacion",
  "requiere_autorizacion": true,
  "nivel_requerido": "supervisor",
  "timeout_minutos": 30
}"""
            elif plantilla == "Lista negra":
                ejemplo_condiciones = """{
  "tipo": "lista_negra",
  "accion": "denegar",
  "motivo": "Incidente previo registrado",
  "alerta": true
}"""
            else:
                ejemplo_condiciones = """{
  "tipo": "custom",
  "campo": "valor"
}"""

            condiciones_raw = st.text_area(
                "JSON de condiciones*",
                value=ejemplo_condiciones,
                height=250
            )

            # Validar JSON
            try:
                condiciones = json.loads(condiciones_raw)
                condiciones_validas = True
                st.success("✅ JSON válido")
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON inválido: {e}")
                condiciones = {}

        col1, col2 = st.columns(2)

        with col1:
            estado = st.selectbox("Estado inicial", ["activa", "inactiva"])

        with col2:
            created_by = st.text_input("Creado por", value="admin")

        st.divider()

        if st.button("✅ Crear Política", type="primary", disabled=not condiciones_validas):
            if not nombre:
                st.error("El nombre es obligatorio")
            else:
                try:
                    politica_id = crear_politica(
                        nombre=nombre,
                        descripcion=descripcion,
                        tipo=tipo,
                        condiciones=condiciones,
                        prioridad=prioridad,
                        estado=estado,
                        aplicable_a=aplicable_a,
                        created_by=created_by
                    )
                    # Guardar mensaje en session_state para mostrarlo después del rerun
                    st.session_state['msg_politica'] = f"✅ Política creada: {politica_id}"
                    st.session_state['show_balloons'] = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al crear política: {e}")
    
    # Mostrar mensaje guardado después de rerun
    if 'msg_politica' in st.session_state:
        st.success(st.session_state['msg_politica'])
        del st.session_state['msg_politica']
        if st.session_state.get('show_balloons', False):
            st.balloons()
            del st.session_state['show_balloons']

    # ==========================================
    # TAB 2: LISTAR POLÍTICAS
    # ==========================================
    with tab2:
        st.subheader("Políticas registradas")

        # Filtros
        col1, col2 = st.columns(2)

        with col1:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todas", "activa", "inactiva"])

        with col2:
            filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "acceso", "restriccion", "horario", "limite", "aprobacion"])

        estado_filtro = None if filtro_estado == "Todas" else filtro_estado
        tipo_filtro = None if filtro_tipo == "Todos" else filtro_tipo

        politicas = obtener_politicas(estado=estado_filtro, tipo=filtro_tipo)

        if not politicas:
            st.info("No hay políticas registradas con los filtros seleccionados.")
        else:
            st.write(f"**Total: {len(politicas)} políticas**")

            # Tabla resumen
            tabla = []
            for p in politicas:
                icono_estado = "🟢" if p['estado'] == 'activa' else "🔴"
                tabla.append({
                    "ID": p['politica_id'],
                    "Estado": f"{icono_estado} {p['estado']}",
                    "Nombre": p['nombre'],
                    "Tipo": p['tipo'],
                    "Prioridad": p['prioridad'],
                    "Aplicable a": p['aplicable_a'],
                    "Creado": p['fecha_creacion'][:10]
                })

            st.dataframe(tabla, use_container_width=True, hide_index=True)

            # Detalle expandible
            st.divider()
            st.subheader("Detalle de política")

            ids = [p["politica_id"] for p in politicas]
            selected_id = st.selectbox("Seleccionar política:", ids)

            politica_sel = next(p for p in politicas if p["politica_id"] == selected_id)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Información General**")
                st.write(f"**ID:** {politica_sel['politica_id']}")
                st.write(f"**Nombre:** {politica_sel['nombre']}")
                st.write(f"**Descripción:** {politica_sel['descripcion']}")
                st.write(f"**Tipo:** {politica_sel['tipo']}")
                st.write(f"**Aplicable a:** {politica_sel['aplicable_a']}")

            with col2:
                st.write("**Configuración**")
                st.write(f"**Prioridad:** {politica_sel['prioridad']}")
                st.write(f"**Estado:** {politica_sel['estado']}")
                st.write(f"**Creado:** {politica_sel['fecha_creacion'][:19]}")
                st.write(f"**Actualizado:** {politica_sel['fecha_actualizacion'][:19]}")
                st.write(f"**Por:** {politica_sel['created_by']}")

            st.write("**Condiciones (JSON)**")
            st.json(politica_sel['condiciones_obj'])

    # ==========================================
    # TAB 3: EDITAR/GESTIONAR
    # ==========================================
    with tab3:
        st.subheader("Editar política existente")

        politicas = obtener_politicas()

        if not politicas:
            st.info("No hay políticas para editar.")
        else:
            ids = [p["politica_id"] for p in politicas]
            seleccion = st.selectbox("Selecciona política por ID:", ids)

            politica = next(p for p in politicas if p["politica_id"] == seleccion)

            st.write(f"**Editando:** {politica['nombre']}")

            col1, col2 = st.columns(2)

            with col1:
                nuevo_nombre = st.text_input("Nombre", value=politica["nombre"])
                nuevo_tipo = st.selectbox(
                    "Tipo",
                    ["acceso", "restriccion", "horario", "limite", "aprobacion"],
                    index=["acceso", "restriccion", "horario", "limite", "aprobacion"].index(politica["tipo"])
                )

            with col2:
                nuevo_aplicable = st.selectbox(
                    "Aplicable a",
                    ["global", "residente", "visitante", "proveedor", "vehiculo", "persona"],
                    index=["global", "residente", "visitante", "proveedor", "vehiculo", "persona"].index(politica["aplicable_a"])
                )
                nueva_prioridad = st.number_input(
                    "Prioridad",
                    min_value=0,
                    max_value=10,
                    value=politica["prioridad"]
                )

            nueva_desc = st.text_area("Descripción", value=politica["descripcion"])

            nuevas_condiciones_raw = st.text_area(
                "Condiciones (JSON)",
                value=politica["condiciones"],
                height=250
            )

            # Validar JSON
            condiciones_validas = False
            try:
                nuevas_condiciones = json.loads(nuevas_condiciones_raw)
                condiciones_validas = True
                st.success("✅ JSON válido")
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON inválido: {e}")
                nuevas_condiciones = {}

            nuevo_estado = st.selectbox(
                "Estado",
                ["activa", "inactiva"],
                index=0 if politica["estado"] == "activa" else 1
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Actualizar Política", type="primary", disabled=not condiciones_validas):
                    actualizar_politica(
                        seleccion,
                        nombre=nuevo_nombre,
                        descripcion=nueva_desc,
                        tipo=nuevo_tipo,
                        condiciones=nuevas_condiciones,
                        prioridad=nueva_prioridad,
                        estado=nuevo_estado,
                        aplicable_a=nuevo_aplicable
                    )
                    st.success("✅ Política actualizada correctamente.")
                    st.rerun()

            with col2:
                if politica["estado"] == "activa":
                    if st.button("🔴 Desactivar Política", type="secondary"):
                        cambiar_estado_politica(seleccion, "inactiva")
                        st.success("Política desactivada.")
                        st.rerun()
                else:
                    if st.button("🟢 Activar Política", type="secondary"):
                        cambiar_estado_politica(seleccion, "activa")
                        st.success("Política activada.")
                        st.rerun()
