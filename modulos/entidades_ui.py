# modulos/entidades_ui.py
"""
UI UNIVERSAL DE ENTIDADES (AUP-EXO)
Registra cualquier tipo de entidad en un solo flujo estructural.
Sustituye a personas.py, vehiculos.py, visitas.py, proveedores.py
"""

import json
import streamlit as st
from datetime import datetime
from modulos.entidades import (
    crear_entidad,
    obtener_entidades,
    obtener_entidad_por_id,
    actualizar_entidad,
    desactivar_entidad,
    reactivar_entidad
)


# ----------------------------------------------------------------------
#   PLANTILLAS DE ATRIBUTOS POR TIPO
# ----------------------------------------------------------------------
PLANTILLAS = {
    "persona": {
        "tipo_persona": "residente",  # residente, visitante, empleado
        "telefono": "",
        "email": "",
        "direccion": "",
        "casa": "",
        "manzana": "",
        "curp": "",
        "notas": ""
    },
    "vehiculo": {
        "marca": "",
        "modelo": "",
        "color": "",
        "año": "",
        "tipo_vehiculo": "auto",  # auto, moto, camioneta, camion
        "propietario": "",
        "notas": ""
    },
    "visita": {
        "telefono": "",
        "motivo": "",
        "destino": "",
        "casa_destino": "",
        "residente_autoriza": "",
        "vigencia": "",
        "empresa": "",
        "notas": ""
    },
    "proveedor": {
        "empresa": "",
        "telefono": "",
        "rfc": "",
        "giro": "",
        "contacto": "",
        "servicios": "",
        "notas": ""
    }
}


# ----------------------------------------------------------------------
#   UI PRINCIPAL DE ENTIDADES
# ----------------------------------------------------------------------
def ui_entidades():
    """
    Interfaz universal para registrar y gestionar entidades
    Reemplaza múltiples módulos anteriores con un solo flujo AUP-EXO
    """
    st.header("🏢 Registro Universal de Entidades")
    st.markdown("**AUP-EXO:** Un solo flujo para personas, vehículos, visitas y proveedores")

    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["➕ Registrar Nueva", "📋 Consultar", "✏️ Editar/Gestionar"])

    # ------------------------------------------------------------------
    # TAB 1: REGISTRAR NUEVA ENTIDAD
    # ------------------------------------------------------------------
    with tab1:
        _ui_registrar_entidad()

    # ------------------------------------------------------------------
    # TAB 2: CONSULTAR ENTIDADES
    # ------------------------------------------------------------------
    with tab2:
        _ui_consultar_entidades()

    # ------------------------------------------------------------------
    # TAB 3: EDITAR/GESTIONAR
    # ------------------------------------------------------------------
    with tab3:
        _ui_editar_entidades()


# ----------------------------------------------------------------------
#   TAB 1: REGISTRAR NUEVA ENTIDAD
# ----------------------------------------------------------------------
def _ui_registrar_entidad():
    """Formulario universal de registro"""
    st.subheader("Registrar Nueva Entidad")

    # Selección de tipo
    tipo = st.selectbox(
        "Tipo de entidad",
        ["persona", "vehiculo", "visita", "proveedor"],
        help="Selecciona el tipo de entidad a registrar"
    )

    st.divider()

    # Campos básicos
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input(
            "Nombre completo / Descripción",
            placeholder="Ej: Juan Pérez, Toyota Corolla Blanco, etc.",
            help="Nombre descriptivo de la entidad"
        )

    with col2:
        identificador = st.text_input(
            "Identificador único",
            placeholder="Ej: Placa, CURP, Folio, Teléfono, QR",
            help="Identificador principal (puede ser placa, CURP, folio, etc.)"
        )

    st.divider()

    # Atributos específicos según tipo
    st.subheader(f"Atributos de {tipo}")

    # Obtener plantilla base
    plantilla = PLANTILLAS.get(tipo, {})

    # Mostrar campos según tipo
    if tipo == "persona":
        atributos = _formulario_persona(plantilla)
    elif tipo == "vehiculo":
        atributos = _formulario_vehiculo(plantilla)
    elif tipo == "visita":
        atributos = _formulario_visita(plantilla)
    elif tipo == "proveedor":
        atributos = _formulario_proveedor(plantilla)
    else:
        atributos = {}

    # Opción avanzada: JSON manual
    with st.expander("⚙️ Edición avanzada (JSON)"):
        atributos_json = st.text_area(
            "Atributos en formato JSON",
            value=json.dumps(atributos, indent=2, ensure_ascii=False),
            height=200,
            help="Puedes editar directamente el JSON para atributos personalizados"
        )
        try:
            atributos = json.loads(atributos_json)
            st.success("✅ JSON válido")
        except:
            st.error("⚠️ JSON inválido - se usarán los valores del formulario")

    # Botón de registro
    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        if st.button("✅ Registrar Entidad", type="primary", use_container_width=True):
            if not nombre:
                st.error("❌ El nombre es obligatorio")
            else:
                try:
                    # Obtener contexto multi-tenant
                    msp_id = st.session_state.get('msp_id')
                    condominio_id = st.session_state.get('condominio_id')
                    
                    entidad_id, hash_entidad = crear_entidad(
                        tipo=tipo,
                        nombre=nombre,
                        identificador=identificador,
                        atributos=atributos,
                        msp_id=msp_id,
                        condominio_id=condominio_id
                    )
                    st.success(f"✅ Entidad registrada exitosamente")
                    st.info(f"**ID:** `{entidad_id}`")
                    st.info(f"**Hash:** `{hash_entidad[:20]}...`")
                    if msp_id:
                        st.info(f"**MSP:** `{msp_id}`")
                    if condominio_id:
                        st.info(f"**Condominio:** `{condominio_id}`")

                    # Botón para registrar otra
                    if st.button("➕ Registrar otra entidad"):
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al registrar: {str(e)}")

    with col_btn2:
        if st.button("🔄 Limpiar formulario", use_container_width=True):
            st.rerun()


# ----------------------------------------------------------------------
#   FORMULARIOS ESPECÍFICOS POR TIPO
# ----------------------------------------------------------------------
def _formulario_persona(plantilla):
    """Formulario para personas"""
    col1, col2 = st.columns(2)

    with col1:
        tipo_persona = st.selectbox(
            "Tipo de persona",
            ["residente", "visitante", "empleado", "contratista"],
            index=0
        )
        telefono = st.text_input("Teléfono", value=plantilla.get("telefono", ""))
        email = st.text_input("Email", value=plantilla.get("email", ""))
        curp = st.text_input("CURP", value=plantilla.get("curp", ""))

    with col2:
        direccion = st.text_input("Dirección/Lote", value=plantilla.get("direccion", ""))
        casa = st.text_input("Número de casa", value=plantilla.get("casa", ""))
        manzana = st.text_input("Manzana", value=plantilla.get("manzana", ""))
        notas = st.text_area("Notas", value=plantilla.get("notas", ""), height=100)

    return {
        "tipo_persona": tipo_persona,
        "telefono": telefono,
        "email": email,
        "direccion": direccion,
        "casa": casa,
        "manzana": manzana,
        "curp": curp,
        "notas": notas
    }


def _formulario_vehiculo(plantilla):
    """Formulario para vehículos"""
    col1, col2 = st.columns(2)

    with col1:
        marca = st.text_input("Marca", value=plantilla.get("marca", ""))
        modelo = st.text_input("Modelo", value=plantilla.get("modelo", ""))
        color = st.text_input("Color", value=plantilla.get("color", ""))

    with col2:
        año = st.text_input("Año", value=plantilla.get("año", ""))
        tipo_vehiculo = st.selectbox(
            "Tipo de vehículo",
            ["auto", "moto", "camioneta", "camion", "otro"]
        )
        propietario = st.text_input("Propietario", value=plantilla.get("propietario", ""))

    notas = st.text_area("Notas", value=plantilla.get("notas", ""), height=100)

    return {
        "marca": marca,
        "modelo": modelo,
        "color": color,
        "año": año,
        "tipo_vehiculo": tipo_vehiculo,
        "propietario": propietario,
        "notas": notas
    }


def _formulario_visita(plantilla):
    """Formulario para visitas"""
    col1, col2 = st.columns(2)

    with col1:
        telefono = st.text_input("Teléfono", value=plantilla.get("telefono", ""))
        motivo = st.text_input("Motivo de la visita", value=plantilla.get("motivo", ""))
        destino = st.text_input("Destino (casa/lote)", value=plantilla.get("destino", ""))

    with col2:
        residente_autoriza = st.text_input(
            "Residente que autoriza",
            value=plantilla.get("residente_autoriza", "")
        )
        vigencia = st.text_input(
            "Vigencia (días/fecha)",
            value=plantilla.get("vigencia", ""),
            help="Ej: 1 día, 1 semana, 2025-12-31"
        )
        empresa = st.text_input("Empresa (opcional)", value=plantilla.get("empresa", ""))

    notas = st.text_area("Notas", value=plantilla.get("notas", ""), height=100)

    return {
        "telefono": telefono,
        "motivo": motivo,
        "destino": destino,
        "casa_destino": destino,
        "residente_autoriza": residente_autoriza,
        "vigencia": vigencia,
        "empresa": empresa,
        "notas": notas
    }


def _formulario_proveedor(plantilla):
    """Formulario para proveedores"""
    col1, col2 = st.columns(2)

    with col1:
        empresa = st.text_input("Empresa", value=plantilla.get("empresa", ""))
        telefono = st.text_input("Teléfono", value=plantilla.get("telefono", ""))
        rfc = st.text_input("RFC", value=plantilla.get("rfc", ""))

    with col2:
        giro = st.text_input("Giro comercial", value=plantilla.get("giro", ""))
        contacto = st.text_input("Persona de contacto", value=plantilla.get("contacto", ""))
        servicios = st.text_input("Servicios", value=plantilla.get("servicios", ""))

    notas = st.text_area("Notas", value=plantilla.get("notas", ""), height=100)

    return {
        "empresa": empresa,
        "telefono": telefono,
        "rfc": rfc,
        "giro": giro,
        "contacto": contacto,
        "servicios": servicios,
        "notas": notas
    }


# ----------------------------------------------------------------------
#   TAB 2: CONSULTAR ENTIDADES
# ----------------------------------------------------------------------
def _ui_consultar_entidades():
    """Vista de consulta de entidades"""
    st.subheader("Entidades Registradas")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        filtro_tipo = st.selectbox(
            "Filtrar por tipo",
            ["todos", "persona", "vehiculo", "visita", "proveedor"]
        )

    with col2:
        filtro_estado = st.selectbox(
            "Estado",
            ["activo", "inactivo", "todos"]
        )

    with col3:
        if st.button("🔄 Actualizar lista"):
            st.rerun()

    # Obtener contexto multi-tenant
    msp_id = st.session_state.get('msp_id')
    condominio_id = st.session_state.get('condominio_id')
    
    # Mostrar contexto activo
    if msp_id or condominio_id:
        with st.expander("🔍 Filtrado por contexto", expanded=False):
            if msp_id:
                st.info(f"**MSP:** {msp_id}")
            if condominio_id:
                st.info(f"**Condominio:** {condominio_id}")

    # Obtener entidades con filtrado multi-tenant
    tipo_query = None if filtro_tipo == "todos" else filtro_tipo
    estado_query = filtro_estado

    entidades = obtener_entidades(
        tipo=tipo_query, 
        estado=estado_query,
        msp_id=msp_id,
        condominio_id=condominio_id
    )

    if entidades:
        st.metric("Total de entidades", len(entidades))

        # Agrupar por tipo
        personas = [e for e in entidades if e['tipo'] == 'persona']
        vehiculos = [e for e in entidades if e['tipo'] == 'vehiculo']
        visitas = [e for e in entidades if e['tipo'] == 'visita']
        proveedores = [e for e in entidades if e['tipo'] == 'proveedor']

        # Mostrar métricas
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("👥 Personas", len(personas))
        col_m2.metric("🚗 Vehículos", len(vehiculos))
        col_m3.metric("🚪 Visitas", len(visitas))
        col_m4.metric("🏢 Proveedores", len(proveedores))

        st.divider()

        # Mostrar tabla expandible
        for entidad in entidades:
            # Parsear atributos JSON, manejar casos de NULL o cadena vacía
            atributos_raw = entidad.get('atributos')
            if atributos_raw:
                try:
                    if isinstance(atributos_raw, str):
                        attrs = json.loads(atributos_raw)
                    else:
                        attrs = atributos_raw if isinstance(atributos_raw, dict) else {}
                except (json.JSONDecodeError, TypeError):
                    attrs = {}
            else:
                attrs = {}
            
            nombre = attrs.get('nombre', 'Sin nombre') if attrs else 'Sin nombre'
            identificador = attrs.get('identificador', 'Sin ID') if attrs else 'Sin ID'
            tipo = entidad['tipo']

            # Icono por tipo
            iconos = {
                'persona': '👤',
                'vehiculo': '🚗',
                'visita': '🚪',
                'proveedor': '🏢'
            }
            icono = iconos.get(tipo, '📦')

            with st.expander(f"{icono} {tipo.upper()} - {nombre} ({identificador})"):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.write(f"**ID:** `{entidad['entidad_id']}`")
                    st.write(f"**Tipo:** {tipo}")
                    st.write(f"**Estado:** {entidad['estado']}")

                with col_b:
                    st.write(f"**Creado:** {entidad['fecha_creacion']}")
                    st.write(f"**Actualizado:** {entidad['fecha_actualizacion']}")
                    hash_val = entidad.get('hash_actual', '')
                    if hash_val:
                        st.write(f"**Hash:** `{hash_val[:16]}...`")
                    else:
                        st.write(f"**Hash:** `Sin hash`")

                st.json(attrs)

    else:
        st.info("📭 No hay entidades registradas con estos filtros")


# ----------------------------------------------------------------------
#   TAB 3: EDITAR/GESTIONAR ENTIDADES
# ----------------------------------------------------------------------
def _ui_editar_entidades():
    """Gestión y edición de entidades existentes"""
    st.subheader("Editar o Gestionar Entidad")

    # Buscar entidad por ID
    entidad_id = st.text_input(
        "ID de la entidad",
        placeholder="Ej: ENT_PER_20251115...",
        help="Ingresa el ID completo de la entidad"
    )

    if entidad_id:
        entidad = obtener_entidad_por_id(entidad_id)

        if entidad:
            st.success(f"✅ Entidad encontrada: **{entidad['tipo'].upper()}**")

            # Parsear atributos JSON, manejar casos de NULL o cadena vacía
            atributos_raw = entidad.get('atributos')
            if atributos_raw:
                try:
                    if isinstance(atributos_raw, str):
                        attrs = json.loads(atributos_raw)
                    else:
                        attrs = atributos_raw if isinstance(atributos_raw, dict) else {}
                except (json.JSONDecodeError, TypeError):
                    attrs = {}
            else:
                attrs = {}

            # Mostrar información actual
            with st.expander("📋 Información actual", expanded=True):
                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.write(f"**Tipo:** {entidad['tipo']}")
                    st.write(f"**Estado:** {entidad['estado']}")
                    st.write(f"**Creado:** {entidad['fecha_creacion']}")

                with col_info2:
                    st.write(f"**ID:** `{entidad['entidad_id']}`")
                    hash_actual = entidad.get('hash_actual', '')
                    if hash_actual:
                        st.write(f"**Hash actual:** `{hash_actual[:20]}...`")
                    else:
                        st.write(f"**Hash actual:** `Sin hash`")
                    hash_previo = entidad.get('hash_previo')
                    if hash_previo:
                        st.write(f"**Hash previo:** `{hash_previo[:20]}...`")

                st.json(attrs)

            st.divider()

            # Formulario de edición
            st.subheader("Actualizar Datos")

            nuevo_nombre = st.text_input(
                "Nombre",
                value=attrs.get('nombre', ''),
                key="edit_nombre"
            )

            nuevo_identificador = st.text_input(
                "Identificador",
                value=attrs.get('identificador', ''),
                key="edit_identificador"
            )

            # Atributos en JSON
            nuevos_atributos_raw = st.text_area(
                "Atributos (JSON)",
                value=json.dumps(attrs, indent=2, ensure_ascii=False),
                height=250,
                key="edit_attrs"
            )

            try:
                nuevos_atributos = json.loads(nuevos_atributos_raw)
                json_valido = True
            except:
                st.error("⚠️ JSON inválido")
                json_valido = False

            st.divider()

            # Botones de acción
            col_act1, col_act2, col_act3 = st.columns(3)

            with col_act1:
                if st.button("💾 Actualizar", type="primary", use_container_width=True):
                    if json_valido:
                        try:
                            nuevo_hash = actualizar_entidad(
                                entidad_id,
                                nombre=nuevo_nombre,
                                identificador=nuevo_identificador,
                                atributos=nuevos_atributos
                            )
                            st.success("✅ Entidad actualizada correctamente")
                            st.info(f"**Nuevo hash:** `{nuevo_hash[:20]}...`")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

            with col_act2:
                if entidad['estado'] == 'activo':
                    if st.button("🚫 Desactivar", use_container_width=True):
                        desactivar_entidad(entidad_id)
                        st.success("✅ Entidad desactivada")
                        st.rerun()
                else:
                    if st.button("✅ Reactivar", use_container_width=True):
                        reactivar_entidad(entidad_id)
                        st.success("✅ Entidad reactivada")
                        st.rerun()

            with col_act3:
                if st.button("🔙 Cancelar", use_container_width=True):
                    st.rerun()

        else:
            st.error("❌ Entidad no encontrada")
            st.info("💡 Verifica que el ID sea correcto")


# ----------------------------------------------------------------------
# ALIAS DE COMPATIBILIDAD
# ----------------------------------------------------------------------
def render_personas():
    """Alias para compatibilidad - redirige a ui_entidades"""
    ui_entidades()


def render_vehiculos():
    """Alias para compatibilidad - redirige a ui_entidades"""
    ui_entidades()
