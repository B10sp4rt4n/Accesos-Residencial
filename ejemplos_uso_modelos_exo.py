"""
Ejemplos de Uso - Modelos SQLAlchemy AUP-EXO
Casos de uso reales con los modelos definidos
"""

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.db_exo import (
    Base,
    MSPExo,
    CondominioExo,
    UsuarioExo,
    ResidenciaExo,
    ResidenteExo,
    VisitanteExo,
    AccesoExo,
    LedgerExo
)


# ========================================
# CONFIGURACIÓN DE CONEXIÓN
# ========================================

def get_engine():
    """Crea engine SQLAlchemy para PostgreSQL"""
    # Opción 1: PostgreSQL local/Supabase
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/axs_exo"
    )
    
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True para debug
    return engine


def init_database():
    """Crea todas las tablas en PostgreSQL"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✅ Tablas creadas en PostgreSQL")
    return engine


# ========================================
# EJEMPLO 1: CREAR MSP Y CONDOMINIOS
# ========================================

def ejemplo_crear_msp_y_condominios():
    """Caso de uso: Telcel crea MSP y le asigna condominios"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Crear MSP (Telcel Partner)
        msp = MSPExo(
            msp_id="msp_telcel_cdmx_001",
            nombre="Telcel Partner CDMX",
            razon_social="Telcel Servicios Integrales S.A. de C.V.",
            rfc="TSI950101ABC",
            email_contacto="partners@telcel.com",
            telefono_contacto="+52 55 5000 5000",
            plan="enterprise",
            max_condominios=500,
            configuracion_json='{"white_label": true, "api_access": true}'
        )
        session.add(msp)
        session.flush()  # Obtener ID sin hacer commit
        
        print(f"✅ MSP creado: {msp.msp_id}")
        
        # 2. Crear Condominios bajo el MSP
        condominios = [
            CondominioExo(
                condominio_id="condo_lomas_001",
                msp_id=msp.msp_id,  # FK exógeno
                nombre="Lomas de Chapultepec Residencial",
                direccion="Paseo de la Reforma 123",
                ciudad="Ciudad de México",
                estado_mx="CDMX",
                codigo_postal="11000",
                total_unidades=50,
                configuracion_json='{"horario_acceso": "24/7"}'
            ),
            CondominioExo(
                condominio_id="condo_polanco_001",
                msp_id=msp.msp_id,
                nombre="Polanco Towers",
                direccion="Av. Presidente Masaryk 456",
                ciudad="Ciudad de México",
                estado_mx="CDMX",
                codigo_postal="11560",
                total_unidades=120
            ),
            CondominioExo(
                condominio_id="condo_santafe_001",
                msp_id=msp.msp_id,
                nombre="Santa Fe Corporate Residences",
                direccion="Av. Santa Fe 789",
                ciudad="Ciudad de México",
                estado_mx="CDMX",
                codigo_postal="01210",
                total_unidades=80
            )
        ]
        
        session.add_all(condominios)
        session.commit()
        
        print(f"✅ {len(condominios)} condominios creados bajo MSP {msp.msp_id}")
        
        # 3. Registrar en Ledger
        ledger = LedgerExo(
            ledger_id=f"ldg_{datetime.now().strftime('%Y%m%d%H%M%S')}_001",
            usuario_id="system",
            msp_id=msp.msp_id,
            accion="CREATE",
            entidad="msps_exo",
            entidad_id=msp.msp_id,
            detalle=f"MSP creado con {len(condominios)} condominios"
        )
        session.add(ledger)
        session.commit()
        
        return msp, condominios
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


# ========================================
# EJEMPLO 2: CREAR USUARIO ADMIN CONDOMINIO
# ========================================

def ejemplo_crear_usuario_admin(condominio_id: str, msp_id: str):
    """Caso de uso: Asignar admin a un condominio"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        usuario = UsuarioExo(
            usuario_id=f"user_{condominio_id}_admin_001",
            nombre="Juan Pérez García",
            email=f"admin@{condominio_id}.com",
            password_hash="$2b$12$dummy_hash_for_example",  # Usar bcrypt real
            rol_id=3,  # 3 = Condominio Admin (SE)
            msp_id=msp_id,
            condominio_id=condominio_id,
            estado="activo"
        )
        
        session.add(usuario)
        session.commit()
        
        print(f"✅ Usuario admin creado: {usuario.email}")
        print(f"   Scope: MSP={usuario.msp_id}, Condominio={usuario.condominio_id}")
        
        return usuario
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


# ========================================
# EJEMPLO 3: REGISTRAR RESIDENCIAS Y RESIDENTES
# ========================================

def ejemplo_crear_residencias(condominio_id: str):
    """Caso de uso: Registrar 5 casas en un condominio"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        residencias = []
        
        for i in range(1, 6):
            residencia = ResidenciaExo(
                residencia_id=f"{condominio_id}_casa_{i:03d}",
                condominio_id=condominio_id,
                numero=f"Casa {i}",
                propietario=f"Propietario Casa {i}",
                telefono=f"+52 55 {1000 + i:04d} {2000 + i:04d}",
                email=f"casa{i}@{condominio_id}.com"
            )
            residencias.append(residencia)
            
            # Agregar 2 residentes por casa
            residente1 = ResidenteExo(
                residente_id=f"{residencia.residencia_id}_res_001",
                residencia_id=residencia.residencia_id,
                nombre=f"Residente Principal Casa {i}",
                telefono=residencia.telefono,
                tipo="residente"
            )
            
            residente2 = ResidenteExo(
                residente_id=f"{residencia.residencia_id}_res_002",
                residencia_id=residencia.residencia_id,
                nombre=f"Familiar Casa {i}",
                tipo="familiar"
            )
            
            session.add(residencia)
            session.add(residente1)
            session.add(residente2)
        
        session.commit()
        
        print(f"✅ {len(residencias)} residencias creadas")
        print(f"✅ {len(residencias) * 2} residentes registrados")
        
        return residencias
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


# ========================================
# EJEMPLO 4: AUTORIZAR VISITANTE CON QR
# ========================================

def ejemplo_autorizar_visitante(residencia_id: str, condominio_id: str):
    """Caso de uso: Residente autoriza visitante y genera QR"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Generar visitante con QR válido por 24 horas
        visitante = VisitanteExo(
            visitante_id=f"vis_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            condominio_id=condominio_id,
            residencia_id=residencia_id,
            nombre="Carlos Martínez - Plomero",
            telefono="+52 55 9999 8888",
            tipo_visita="proveedor",
            fecha_autorizacion=datetime.now(),
            fecha_expiracion=datetime.now() + timedelta(hours=24),
            qr_code=f"QR_{datetime.now().strftime('%Y%m%d%H%M%S')}_ABCD1234",
            estado="activo",
            observaciones="Reparación de tubería - Casa 5"
        )
        
        session.add(visitante)
        session.commit()
        
        print(f"✅ Visitante autorizado: {visitante.nombre}")
        print(f"   QR Code: {visitante.qr_code}")
        print(f"   Válido hasta: {visitante.fecha_expiracion}")
        
        return visitante
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


# ========================================
# EJEMPLO 5: REGISTRAR ACCESO CON QR
# ========================================

def ejemplo_registrar_acceso_qr(visitante_id: str, condominio_id: str, usuario_operador_id: str):
    """Caso de uso: Vigilante registra entrada con QR"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Buscar visitante
        visitante = session.query(VisitanteExo).filter_by(visitante_id=visitante_id).first()
        
        if not visitante:
            raise ValueError(f"Visitante {visitante_id} no encontrado")
        
        if visitante.estado != "activo":
            raise ValueError(f"Visitante en estado: {visitante.estado}")
        
        if visitante.fecha_expiracion < datetime.now():
            raise ValueError("QR expirado")
        
        # 2. Registrar acceso
        acceso = AccesoExo(
            acceso_id=f"acc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            visitante_id=visitante_id,
            condominio_id=condominio_id,
            usuario_operador_id=usuario_operador_id,
            tipo_acceso="entrada",
            metodo="qr",
            resultado="permitido",
            comentario=f"Acceso QR exitoso - {visitante.nombre}",
            metadata_json=f'{{"qr_code": "{visitante.qr_code}", "timestamp": "{datetime.now().isoformat()}"}}'
        )
        
        # 3. Marcar QR como usado
        visitante.qr_usado = True
        visitante.estado = "usado"
        
        session.add(acceso)
        session.commit()
        
        print(f"✅ Acceso registrado: {acceso.acceso_id}")
        print(f"   Visitante: {visitante.nombre}")
        print(f"   Método: QR - {visitante.qr_code}")
        
        return acceso
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error al registrar acceso: {e}")
        raise
    finally:
        session.close()


# ========================================
# EJEMPLO 6: QUERY MULTI-TENANT
# ========================================

def ejemplo_query_por_msp(msp_id: str):
    """Caso de uso: Super Admin consulta todos los condominios de un MSP"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query con scope MSP
        condominios = session.query(CondominioExo).filter_by(
            msp_id=msp_id,
            estado="activo"
        ).all()
        
        print(f"\n📊 Condominios del MSP {msp_id}:")
        print(f"   Total activos: {len(condominios)}")
        
        for condo in condominios:
            print(f"   - {condo.nombre} ({condo.condominio_id})")
            print(f"     Unidades: {condo.total_unidades}")
            
            # Contar residencias
            residencias = session.query(ResidenciaExo).filter_by(
                condominio_id=condo.condominio_id
            ).count()
            
            # Contar visitantes activos
            visitantes = session.query(VisitanteExo).filter_by(
                condominio_id=condo.condominio_id,
                estado="activo"
            ).count()
            
            print(f"     Residencias: {residencias} | Visitantes activos: {visitantes}")
        
        return condominios
        
    finally:
        session.close()


# ========================================
# FLUJO COMPLETO DE EJEMPLO
# ========================================

def ejemplo_flujo_completo():
    """Flujo completo: MSP → Condominio → Residencia → Visitante → Acceso"""
    print("\n" + "="*60)
    print("FLUJO COMPLETO - AUP-EXO con SQLAlchemy")
    print("="*60 + "\n")
    
    # Paso 1: Crear MSP y Condominios
    print("📦 PASO 1: Crear MSP y Condominios")
    print("-" * 60)
    msp, condominios = ejemplo_crear_msp_y_condominios()
    
    # Paso 2: Crear Usuario Admin
    print("\n👤 PASO 2: Crear Usuario Admin para Condominio")
    print("-" * 60)
    usuario = ejemplo_crear_usuario_admin(
        condominio_id=condominios[0].condominio_id,
        msp_id=msp.msp_id
    )
    
    # Paso 3: Registrar Residencias
    print("\n🏠 PASO 3: Registrar Residencias y Residentes")
    print("-" * 60)
    residencias = ejemplo_crear_residencias(condominios[0].condominio_id)
    
    # Paso 4: Autorizar Visitante
    print("\n🎫 PASO 4: Autorizar Visitante con QR")
    print("-" * 60)
    visitante = ejemplo_autorizar_visitante(
        residencia_id=residencias[0].residencia_id,
        condominio_id=condominios[0].condominio_id
    )
    
    # Paso 5: Registrar Acceso
    print("\n🚪 PASO 5: Registrar Acceso con QR")
    print("-" * 60)
    acceso = ejemplo_registrar_acceso_qr(
        visitante_id=visitante.visitante_id,
        condominio_id=condominios[0].condominio_id,
        usuario_operador_id=usuario.usuario_id
    )
    
    # Paso 6: Query Multi-tenant
    print("\n📊 PASO 6: Query Multi-tenant por MSP")
    print("-" * 60)
    ejemplo_query_por_msp(msp.msp_id)
    
    print("\n" + "="*60)
    print("✅ FLUJO COMPLETO EXITOSO")
    print("="*60 + "\n")


# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║  EJEMPLOS DE USO - MODELOS SQLALCHEMY AUP-EXO             ║
╚════════════════════════════════════════════════════════════╝

⚠️  NOTA: Este script requiere PostgreSQL configurado
    
    Configurar DATABASE_URL antes de ejecutar:
    export DATABASE_URL="postgresql://user:pass@host:port/db"
    
    O editar la función get_engine() en este archivo.

📋 Opciones disponibles:
    1. Ejecutar flujo completo (recomendado)
    2. Ejecutar ejemplos individuales
    3. Inicializar base de datos

""")
    
    # Descomentar para ejecutar:
    # init_database()  # Solo primera vez
    # ejemplo_flujo_completo()
