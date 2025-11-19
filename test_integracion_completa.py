"""
test_integracion_completa.py
Testing end-to-end: POLÍTICAS → MOTOR_REGLAS → ORQUESTADOR → EVENTOS
"""

import sys
sys.path.insert(0, '/workspaces/Accesos-Residencial')

import json
from datetime import datetime
from core.db import get_db
from core.orquestador import OrquestadorAccesos
from modulos.entidades import crear_entidad
from modulos.politicas import crear_politica


def test_flujo_completo_permitido():
    """Test end-to-end de acceso permitido"""
    print("\n🧪 TEST 1: Flujo completo - Acceso PERMITIDO")
    print("=" * 60)
    
    # 1. Crear entidad
    print("\n1️⃣ Creando entidad...")
    entidad_id, _ = crear_entidad(
        tipo="persona",
        nombre="Juan Pérez Residente",
        identificador="RES-001",
        atributos={
            "casa": "15",
            "telefono": "555-0001"
        }
    )
    print(f"   ✅ Entidad creada: {entidad_id}")
    
    # 2. Crear política permisiva
    print("\n2️⃣ Creando política permisiva...")
    politica_id = crear_politica(
        nombre="Test Acceso 24/7",
        descripcion="Acceso sin restricciones",
        tipo="acceso",
        condiciones={
            "tipo": "horario",
            "hora_inicio": "00:00",
            "hora_fin": "23:59"
        },
        prioridad=5,
        estado="activa",
        aplicable_a="global",
        created_by="test_e2e"
    )
    print(f"   ✅ Política creada: {politica_id}")
    
    # 3. Procesar acceso con orquestador
    print("\n3️⃣ Procesando acceso con orquestador...")
    orq = OrquestadorAccesos(usuario_id="test_e2e")
    
    resultado = orq.procesar_acceso(
        entidad_id=entidad_id,
        metadata={
            "hora": "10:00",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "tipo_acceso": "entrada",
            "notas": "Test integración E2E"
        },
        actor="vigilante_test",
        dispositivo="tablet_test"
    )
    
    print(f"   📊 Resultado: {type(resultado).__name__}")
    
    # 4. Verificar resultado
    if isinstance(resultado, str):
        # Es un hash de evento (acceso permitido)
        print(f"   ✅ Acceso PERMITIDO")
        print(f"   📝 Hash del evento: {resultado[:16]}...")
        
        # 5. Verificar que se creó el evento en la DB
        print("\n4️⃣ Verificando evento en base de datos...")
        with get_db() as db:
            evento = db.execute("""
                SELECT * FROM eventos 
                WHERE hash_actual = ?
            """, (resultado,)).fetchone()
            
            if evento:
                print(f"   ✅ Evento encontrado en DB")
                print(f"   Tipo: {evento['tipo_evento']}")
                print(f"   Entidad: {evento['entidad_id']}")
                print(f"   Actor: {evento['actor']}")
                
                metadata_evento = json.loads(evento['metadata'])
                print(f"   Metadata: {list(metadata_evento.keys())}")
                
                # Verificar evaluación en metadata
                if 'evaluacion' in metadata_evento:
                    print(f"   ✅ Evaluación de políticas guardada")
                    print(f"      Permitido: {metadata_evento['evaluacion']['permitido']}")
                
                # Limpiar
                db.execute("DELETE FROM eventos WHERE hash_actual = ?", (resultado,))
        
        # Limpiar política
        with get_db() as db:
            db.execute("DELETE FROM politicas WHERE politica_id = ?", (politica_id,))
        
        print(f"\n✅ TEST 1 EXITOSO - Flujo de acceso permitido funciona correctamente")
        return True
    
    else:
        print(f"   ❌ Resultado inesperado: {resultado}")
        return False


def test_flujo_completo_rechazado():
    """Test end-to-end de acceso rechazado por política"""
    print("\n🧪 TEST 2: Flujo completo - Acceso RECHAZADO por política")
    print("=" * 60)
    
    # 1. Crear entidad
    print("\n1️⃣ Creando entidad...")
    entidad_id, _ = crear_entidad(
        tipo="proveedor",
        nombre="Proveedor Test S.A.",
        identificador="PROV-TEST-001",
        atributos={
            "empresa": "Test Company",
            "rfc": "TEST123456"
        }
    )
    print(f"   ✅ Entidad creada: {entidad_id}")
    
    # 2. Crear política restrictiva
    print("\n2️⃣ Creando política restrictiva...")
    politica_id = crear_politica(
        nombre="Test Horario Proveedores",
        descripcion="Proveedores solo 08:00-17:00",
        tipo="horario",
        condiciones={
            "tipo": "horario",
            "hora_inicio": "08:00",
            "hora_fin": "17:00"
        },
        prioridad=1,
        estado="activa",
        aplicable_a="proveedor",
        created_by="test_e2e"
    )
    print(f"   ✅ Política creada: {politica_id}")
    
    # 3. Intentar acceso fuera de horario
    print("\n3️⃣ Intentando acceso a las 20:00 (fuera de horario)...")
    orq = OrquestadorAccesos(usuario_id="test_e2e")
    
    resultado = orq.procesar_acceso(
        entidad_id=entidad_id,
        metadata={
            "hora": "20:00",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "tipo_acceso": "entrada",
            "notas": "Test rechazo E2E"
        },
        actor="vigilante_test",
        dispositivo="tablet_test"
    )
    
    print(f"   📊 Resultado: {type(resultado).__name__}")
    
    # 4. Verificar rechazo
    if isinstance(resultado, dict) and resultado.get('status') == 'rechazado':
        print(f"   ✅ Acceso RECHAZADO como esperado")
        print(f"   📝 Motivo: {resultado['motivo']}")
        print(f"   📋 Política aplicada: {resultado['politica']}")
        
        # 5. Verificar que se creó evento de rechazo
        print("\n4️⃣ Verificando evento de rechazo en base de datos...")
        with get_db() as db:
            eventos_rechazo = db.execute("""
                SELECT * FROM eventos 
                WHERE entidad_id = ? AND tipo_evento = 'rechazo'
                ORDER BY timestamp_servidor DESC
                LIMIT 1
            """, (entidad_id,)).fetchone()
            
            if eventos_rechazo:
                print(f"   ✅ Evento de rechazo registrado")
                print(f"   Tipo: {eventos_rechazo['tipo_evento']}")
                print(f"   Hash: {eventos_rechazo['hash_actual'][:16]}...")
                
                metadata_evento = json.loads(eventos_rechazo['metadata'])
                if 'motivo_rechazo' in metadata_evento:
                    print(f"   ✅ Motivo guardado: {metadata_evento['motivo_rechazo'][:50]}...")
                
                # Limpiar
                db.execute("DELETE FROM eventos WHERE entidad_id = ?", (entidad_id,))
        
        # Limpiar política
        with get_db() as db:
            db.execute("DELETE FROM politicas WHERE politica_id = ?", (politica_id,))
        
        print(f"\n✅ TEST 2 EXITOSO - Flujo de rechazo funciona correctamente")
        return True
    
    else:
        print(f"   ❌ Resultado inesperado: {resultado}")
        return False


def test_limite_visitas():
    """Test de límite de visitas funcionando en flujo completo"""
    print("\n🧪 TEST 3: Límite de visitas con orquestador")
    print("=" * 60)
    
    # 1. Crear entidad
    print("\n1️⃣ Creando entidad visitante...")
    entidad_id, _ = crear_entidad(
        tipo="persona",
        nombre="Visitante Frecuente",
        identificador="VIS-LIMIT-001",
        atributos={
            "tipo": "visitante"
        }
    )
    print(f"   ✅ Entidad creada: {entidad_id}")
    
    # 2. Crear política de límite
    print("\n2️⃣ Creando política con límite de 2 visitas/día...")
    politica_id = crear_politica(
        nombre="Test Límite Visitas",
        descripcion="Máximo 2 visitas por día",
        tipo="limite",
        condiciones={
            "max_visitas_dia": 2
        },
        prioridad=1,
        estado="activa",
        aplicable_a="global",
        created_by="test_e2e"
    )
    print(f"   ✅ Política creada: {politica_id}")
    
    # 3. Procesar 3 accesos
    print("\n3️⃣ Procesando 3 intentos de acceso...")
    orq = OrquestadorAccesos(usuario_id="test_e2e")
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    resultados = []
    
    for i in range(1, 4):
        print(f"\n   Intento {i}:")
        resultado = orq.procesar_acceso(
            entidad_id=entidad_id,
            metadata={
                "hora": f"10:{i:02d}",
                "fecha": fecha_hoy,
                "tipo_acceso": "entrada",
                "notas": f"Intento #{i}"
            },
            actor="vigilante_test",
            dispositivo="tablet_test"
        )
        
        if isinstance(resultado, str):
            print(f"      ✅ PERMITIDO (hash: {resultado[:12]}...)")
            resultados.append("permitido")
        elif isinstance(resultado, dict) and resultado.get('status') == 'rechazado':
            print(f"      ❌ RECHAZADO: {resultado['motivo'][:60]}...")
            resultados.append("rechazado")
        else:
            print(f"      ⚠️ Resultado inesperado: {resultado}")
            resultados.append("error")
    
    # 4. Verificar resultados
    print(f"\n4️⃣ Verificando resultados...")
    print(f"   Resultados: {resultados}")
    
    if resultados == ["permitido", "permitido", "rechazado"]:
        print(f"   ✅ Límite de visitas funcionando correctamente")
        print(f"      - Primera visita: permitida")
        print(f"      - Segunda visita: permitida")
        print(f"      - Tercera visita: rechazada por límite")
        
        # Limpiar
        with get_db() as db:
            db.execute("DELETE FROM eventos WHERE entidad_id = ?", (entidad_id,))
            db.execute("DELETE FROM politicas WHERE politica_id = ?", (politica_id,))
        
        print(f"\n✅ TEST 3 EXITOSO - Límite de visitas funciona en flujo completo")
        return True
    else:
        print(f"   ❌ Resultados inesperados")
        return False


# ---------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING DE INTEGRACIÓN COMPLETA (E2E)")
    print("   POLÍTICAS → MOTOR_REGLAS → ORQUESTADOR → EVENTOS")
    print("=" * 60)
    
    # Ejecutar tests
    resultados = []
    
    resultados.append(("Flujo completo - Acceso permitido", test_flujo_completo_permitido()))
    resultados.append(("Flujo completo - Acceso rechazado", test_flujo_completo_rechazado()))
    resultados.append(("Límite de visitas E2E", test_limite_visitas()))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTING E2E")
    print("=" * 60)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        icono = "✅" if resultado else "❌"
        print(f"{icono} {nombre}")
    
    print(f"\n🎯 RESULTADO FINAL: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 ¡Integración completa funcionando perfectamente!")
        print("\n📊 FLUJO OPERATIVO VERIFICADO:")
        print("   ENTIDAD → POLÍTICAS → MOTOR_REGLAS → ORQUESTADOR → EVENTO")
        print("\n🚀 Sistema AUP-EXO con cerebro de reglas OPERATIVO")
    else:
        print(f"\n⚠️ {total - exitosos} tests fallaron")
        print("   Revisar integración entre módulos")
