# modulos/qr_module.py
"""
Módulo de Gestión de Códigos QR
Sistema de Control de Accesos Residencial
"""

import streamlit as st
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import json
from core.db import get_db
from app.core.qr_engine import (
    generar_qr_visitante,
    generar_qr_proveedor_recurrente,
    validar_qr
)


def ui_qr_module():
    """Interfaz principal del módulo QR"""
    st.header("🔲 Gestión de Códigos QR")
    
    st.markdown("""
    **Códigos QR** permiten acceso rápido y seguro mediante escaneo.
    
    - 📱 QR para visitantes (temporales)
    - 🏢 QR para proveedores recurrentes
    - ✅ Validación de códigos
    - 📊 Historial de QRs generados
    """)
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Generar QR Visitante",
        "🏢 QR Proveedor",
        "✅ Validar QR",
        "📋 Historial QRs"
    ])
    
    with tab1:
        _render_generar_qr_visitante()
    
    with tab2:
        _render_generar_qr_proveedor()
    
    with tab3:
        _render_validar_qr()
    
    with tab4:
        _render_historial_qrs()


def _render_generar_qr_visitante():
    """Formulario para generar QR de visitante"""
    st.subheader("📱 Generar QR para Visitante")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_visitante = st.text_input(
            "Nombre del visitante*",
            placeholder="Ej: Juan Pérez"
        )
        residente_autoriza = st.text_input(
            "Residente que autoriza*",
            placeholder="Ej: María López - Casa 123"
        )
    
    with col2:
        vigencia_horas = st.number_input(
            "Vigencia (horas)",
            min_value=1,
            max_value=168,  # 7 días
            value=24
        )
        casa_destino = st.text_input(
            "Casa/Departamento destino",
            placeholder="Ej: Casa 123"
        )
    
    motivo = st.text_area(
        "Motivo de visita (opcional)",
        placeholder="Ej: Reunión familiar, entrega de paquete, etc."
    )
    
    uso_unico = st.checkbox("QR de un solo uso", value=True)
    
    st.divider()
    
    if st.button("🔲 Generar Código QR", type="primary"):
        if not nombre_visitante or not residente_autoriza:
            st.error("❌ Nombre del visitante y residente autorizador son obligatorios")
        else:
            # Generar código QR
            metadata = {
                "casa": casa_destino,
                "motivo": motivo,
                "uso_unico": uso_unico
            }
            
            codigo_qr = generar_qr_visitante(
                nombre=nombre_visitante,
                residente_autorizador=residente_autoriza,
                vigencia_horas=vigencia_horas,
                metadata=metadata
            )
            
            # Guardar en BD
            with get_db() as db:
                timestamp = datetime.now().isoformat()
                expiracion = (datetime.now() + timedelta(hours=vigencia_horas)).isoformat()
                
                datos_json = json.dumps({
                    "nombre": nombre_visitante,
                    "residente": residente_autoriza,
                    "casa": casa_destino,
                    "motivo": motivo,
                    "uso_unico": uso_unico,
                    "expira": expiracion
                })
                
                db.execute("""
                    INSERT INTO codigos_qr 
                    (codigo, tipo, datos_json, fecha_creacion, fecha_expiracion, estado, usado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo_qr,
                    "visitante",
                    datos_json,
                    timestamp,
                    expiracion,
                    "activo",
                    False
                ))
            
            st.success(f"✅ Código QR generado: **{codigo_qr}**")
            
            # Generar imagen QR
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(codigo_qr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a bytes
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(buf, caption=f"QR: {codigo_qr}", width=300)
            
            with col2:
                st.info(f"""
                **Información del QR:**
                - **Visitante:** {nombre_visitante}
                - **Autorizado por:** {residente_autoriza}
                - **Destino:** {casa_destino or 'No especificado'}
                - **Vigencia:** {vigencia_horas} horas
                - **Expira:** {(datetime.now() + timedelta(hours=vigencia_horas)).strftime('%Y-%m-%d %H:%M')}
                - **Uso único:** {'Sí' if uso_unico else 'No'}
                """)
                
                # Botón de descarga
                buf.seek(0)
                st.download_button(
                    label="📥 Descargar QR",
                    data=buf,
                    file_name=f"QR_{codigo_qr}.png",
                    mime="image/png"
                )
            
            st.balloons()


def _render_generar_qr_proveedor():
    """Formulario para QR de proveedor recurrente"""
    st.subheader("🏢 Generar QR para Proveedor Recurrente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        empresa = st.text_input("Nombre de la empresa*", placeholder="Ej: Gas Natural SA")
        rfc = st.text_input("RFC*", placeholder="Ej: GNA850101ABC")
    
    with col2:
        hora_desde = st.time_input("Horario desde", value=None)
        hora_hasta = st.time_input("Horario hasta", value=None)
    
    dias_validos = st.multiselect(
        "Días permitidos",
        ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"],
        default=["lunes", "martes", "miercoles", "jueves", "viernes"]
    )
    
    contacto = st.text_input("Contacto/Teléfono (opcional)", placeholder="5512345678")
    
    st.divider()
    
    if st.button("🔲 Generar QR Proveedor", type="primary"):
        if not empresa or not rfc or not hora_desde or not hora_hasta or not dias_validos:
            st.error("❌ Complete todos los campos obligatorios")
        else:
            codigo_qr = generar_qr_proveedor_recurrente(
                empresa=empresa,
                rfc=rfc,
                dias_validos=dias_validos,
                horario_desde=hora_desde.strftime("%H:%M"),
                horario_hasta=hora_hasta.strftime("%H:%M")
            )
            
            # Guardar en BD
            with get_db() as db:
                datos_json = json.dumps({
                    "empresa": empresa,
                    "rfc": rfc,
                    "dias_validos": dias_validos,
                    "horario_desde": hora_desde.strftime("%H:%M"),
                    "horario_hasta": hora_hasta.strftime("%H:%M"),
                    "contacto": contacto
                })
                
                db.execute("""
                    INSERT INTO codigos_qr 
                    (codigo, tipo, datos_json, fecha_creacion, fecha_expiracion, estado, usado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo_qr,
                    "proveedor_recurrente",
                    datos_json,
                    datetime.now().isoformat(),
                    None,  # Sin expiración
                    "activo",
                    False
                ))
            
            st.success(f"✅ QR Proveedor generado: **{codigo_qr}**")
            
            # Generar imagen QR
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(codigo_qr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(buf, caption=f"QR: {codigo_qr}", width=300)
            
            with col2:
                st.info(f"""
                **QR Proveedor Recurrente:**
                - **Empresa:** {empresa}
                - **RFC:** {rfc}
                - **Horario:** {hora_desde.strftime('%H:%M')} - {hora_hasta.strftime('%H:%M')}
                - **Días:** {', '.join(dias_validos)}
                - **Tipo:** Permanente (sin expiración)
                """)
                
                buf.seek(0)
                st.download_button(
                    label="📥 Descargar QR",
                    data=buf,
                    file_name=f"QR_PROV_{empresa.replace(' ', '_')}.png",
                    mime="image/png"
                )


def _render_validar_qr():
    """Validación de códigos QR"""
    st.subheader("✅ Validar Código QR")
    
    codigo_input = st.text_input(
        "Escanee o ingrese el código QR",
        placeholder="Ej: QR-A1B2C3D4E5F6G7H8"
    )
    
    if st.button("🔍 Validar", type="primary") and codigo_input:
        with get_db() as db:
            cursor = db.execute(
                "SELECT * FROM codigos_qr WHERE codigo = ? AND estado = 'activo'",
                (codigo_input,)
            )
            row = cursor.fetchone()
        
        if not row:
            st.error("❌ Código QR no encontrado o inactivo")
        else:
            datos_qr = dict(row)
            datos_json = json.loads(datos_qr['datos_json'])
            
            # Validar con el motor
            resultado = validar_qr(codigo_input, {
                **datos_json,
                "usado": datos_qr['usado']
            })
            
            if resultado['valido']:
                st.success("✅ **Código QR VÁLIDO**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Información:**")
                    if datos_qr['tipo'] == 'visitante':
                        st.write(f"- **Tipo:** Visitante")
                        st.write(f"- **Nombre:** {datos_json.get('nombre')}")
                        st.write(f"- **Autorizado por:** {datos_json.get('residente')}")
                        st.write(f"- **Casa:** {datos_json.get('casa', 'N/A')}")
                    else:
                        st.write(f"- **Tipo:** Proveedor Recurrente")
                        st.write(f"- **Empresa:** {datos_json.get('empresa')}")
                        st.write(f"- **RFC:** {datos_json.get('rfc')}")
                
                with col2:
                    st.write("**Estado:**")
                    st.write(f"- **Creado:** {datos_qr['fecha_creacion'][:19]}")
                    if datos_qr['fecha_expiracion']:
                        st.write(f"- **Expira:** {datos_qr['fecha_expiracion'][:19]}")
                    else:
                        st.write(f"- **Expira:** Permanente")
                    st.write(f"- **Usado:** {'Sí' if datos_qr['usado'] else 'No'}")
                
                # Marcar como usado si es de un solo uso
                if datos_json.get('uso_unico') and not datos_qr['usado']:
                    if st.button("✅ Marcar como usado"):
                        with get_db() as db:
                            db.execute(
                                "UPDATE codigos_qr SET usado = ? WHERE codigo = ?",
                                (True, codigo_input)
                            )
                        st.success("✅ QR marcado como usado")
                        st.rerun()
            else:
                st.error(f"❌ **Código QR INVÁLIDO**")
                st.warning(f"**Motivo:** {resultado['motivo']}")


def _render_historial_qrs():
    """Historial de QRs generados"""
    st.subheader("📋 Historial de Códigos QR")
    
    filtro_tipo = st.selectbox("Filtrar por tipo:", ["Todos", "visitante", "proveedor_recurrente"])
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "activo", "inactivo", "expirado"])
    
    with get_db() as db:
        query = "SELECT * FROM codigos_qr WHERE 1=1"
        params = []
        
        if filtro_tipo != "Todos":
            query += " AND tipo = ?"
            params.append(filtro_tipo)
        
        if filtro_estado != "Todos":
            if filtro_estado == "expirado":
                query += " AND fecha_expiracion < ?"
                params.append(datetime.now().isoformat())
            else:
                query += " AND estado = ?"
                params.append(filtro_estado)
        
        query += " ORDER BY fecha_creacion DESC LIMIT 100"
        
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
    
    if not rows:
        st.info("No hay códigos QR registrados con los filtros seleccionados")
    else:
        st.write(f"**Total: {len(rows)} códigos QR**")
        
        tabla = []
        for r in rows:
            datos = json.loads(r['datos_json'])
            
            # Determinar estado
            estado_visual = r['estado']
            if r['fecha_expiracion'] and datetime.now() > datetime.fromisoformat(r['fecha_expiracion']):
                estado_visual = "🔴 expirado"
            elif r['usado'] and datos.get('uso_unico'):
                estado_visual = "⚫ usado"
            elif r['estado'] == 'activo':
                estado_visual = "🟢 activo"
            else:
                estado_visual = "🔴 inactivo"
            
            tabla.append({
                "Código": r['codigo'],
                "Tipo": r['tipo'],
                "Estado": estado_visual,
                "Nombre/Empresa": datos.get('nombre') or datos.get('empresa', 'N/A'),
                "Creado": r['fecha_creacion'][:10],
                "Expira": r['fecha_expiracion'][:10] if r['fecha_expiracion'] else "N/A"
            })
        
        st.dataframe(tabla, use_container_width=True, hide_index=True)


# Crear tabla de QRs si no existe
def _init_qr_table():
    """Inicializa tabla de códigos QR"""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS codigos_qr (
                codigo TEXT PRIMARY KEY,
                tipo TEXT NOT NULL,
                datos_json TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_expiracion TEXT,
                estado TEXT DEFAULT 'activo',
                usado INTEGER DEFAULT 0
            )
        """)

# Auto-inicializar tabla al importar
try:
    _init_qr_table()
except:
    pass
