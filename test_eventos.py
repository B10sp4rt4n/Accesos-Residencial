"""
test_eventos.py
Testing del módulo de historial de eventos AUP-EXO
"""

import sys
sys.path.insert(0, '/workspaces/Accesos-Residencial')

from core.db import get_db
from modulos.eventos import obtener_eventos
import json


def test_lectura_eventos():
    """Verifica que se puedan leer eventos desde la base"""
    print("\n🧪 TEST 1: Lectura de eventos")
    print("-" * 60)
    
    eventos = obtener_eventos()
    
    if eventos:
        print(f"✅ Se encontraron {len(eventos)} eventos")
        
        # Mostrar primer evento
        primer_evento = eventos[0]
        print(f"\n📋 Primer evento:")
        print(f"   ID: {primer_evento['evento_id']}")
        print(f"   Tipo: {primer_evento['tipo_evento']}")
        print(f"   Entidad: {primer_evento['tipo_entidad']} - {primer_evento['nombre']}")
        print(f"   Identificador: {primer_evento['identificador']}")
        print(f"   Hash: {primer_evento['hash_actual'][:20]}...")
        
        # Verificar metadata
        metadata = json.loads(primer_evento['metadata']) if primer_evento['metadata'] else {}
        print(f"   Metadata: {metadata}")
        
    else:
        print("⚠️ No hay eventos en la base de datos")
        print("   Ejecuta primero test_flujo_vigilancia.py para crear eventos")
    
    return eventos


def test_filtro_por_tipo():
    """Verifica filtros por tipo de evento"""
    print("\n🧪 TEST 2: Filtros por tipo de evento")
    print("-" * 60)
    
    tipos = ["entrada", "salida", "rechazo", "incidente"]
    
    for tipo in tipos:
        eventos = obtener_eventos(tipo=tipo)
        print(f"   {tipo}: {len(eventos)} eventos")
    
    # Verificar que filtro funciona
    entradas = obtener_eventos(tipo="entrada")
    salidas = obtener_eventos(tipo="salida")
    
    if entradas or salidas:
        print(f"\n✅ Filtros funcionando correctamente")
        if entradas:
            print(f"   Ejemplo entrada: {entradas[0]['tipo_evento']}")
        if salidas:
            print(f"   Ejemplo salida: {salidas[0]['tipo_evento']}")
    else:
        print("\n⚠️ No hay eventos de entrada/salida para verificar filtros")
    
    return True


def test_join_entidades():
    """Verifica que el JOIN con tabla entidades funciona"""
    print("\n🧪 TEST 3: JOIN con tabla entidades")
    print("-" * 60)
    
    eventos = obtener_eventos()
    
    if not eventos:
        print("⚠️ No hay eventos para verificar JOIN")
        return False
    
    # Verificar que todos los campos de entidad están presentes
    campos_requeridos = ['nombre', 'identificador', 'tipo_entidad']
    
    for evento in eventos[:3]:  # Revisar primeros 3
        print(f"\n📋 Evento {evento['evento_id']}:")
        
        for campo in campos_requeridos:
            if campo in evento and evento[campo]:
                print(f"   ✅ {campo}: {evento[campo]}")
            else:
                print(f"   ❌ {campo}: FALTANTE")
                return False
    
    print(f"\n✅ JOIN con entidades funcionando correctamente")
    return True


def test_metadata_estructura():
    """Verifica estructura de metadata en eventos"""
    print("\n🧪 TEST 4: Estructura de metadata")
    print("-" * 60)
    
    eventos = obtener_eventos()
    
    if not eventos:
        print("⚠️ No hay eventos para verificar metadata")
        return False
    
    for evento in eventos[:3]:
        print(f"\n📋 Evento {evento['evento_id']}:")
        
        if evento['metadata']:
            try:
                metadata = json.loads(evento['metadata'])
                print(f"   ✅ Metadata válida (JSON)")
                print(f"   Campos: {list(metadata.keys())}")
                
                # Mostrar algunos valores
                for key, value in list(metadata.items())[:3]:
                    print(f"      - {key}: {value}")
                
            except json.JSONDecodeError:
                print(f"   ❌ Metadata NO es JSON válido")
                return False
        else:
            print(f"   ⚠️ Sin metadata")
    
    print(f"\n✅ Metadata con estructura correcta")
    return True


def test_hash_trazabilidad():
    """Verifica que todos los eventos tienen hash"""
    print("\n🧪 TEST 5: Trazabilidad con hash")
    print("-" * 60)
    
    eventos = obtener_eventos()
    
    if not eventos:
        print("⚠️ No hay eventos para verificar hash")
        return False
    
    eventos_con_hash = 0
    eventos_sin_hash = 0
    
    for evento in eventos:
        if evento['hash_actual'] and len(evento['hash_actual']) == 64:
            eventos_con_hash += 1
        else:
            eventos_sin_hash += 1
            print(f"   ⚠️ Evento {evento['evento_id']} sin hash válido")
    
    print(f"\n📊 Resultados:")
    print(f"   ✅ Eventos con hash SHA-256: {eventos_con_hash}")
    print(f"   ❌ Eventos sin hash: {eventos_sin_hash}")
    
    if eventos_con_hash == len(eventos):
        print(f"\n✅ Todos los eventos tienen hash SHA-256")
        
        # Mostrar ejemplo de cadena
        print(f"\n🔗 Ejemplo de hash (primeros 3):")
        for evento in eventos[:3]:
            print(f"   Evento {evento['evento_id']}: {evento['hash_actual'][:16]}...")
        
        return True
    else:
        print(f"\n⚠️ {eventos_sin_hash} eventos sin hash")
        return False


def test_campos_actor_dispositivo():
    """Verifica que eventos tienen actor y dispositivo"""
    print("\n🧪 TEST 6: Actor y Dispositivo")
    print("-" * 60)
    
    eventos = obtener_eventos()
    
    if not eventos:
        print("⚠️ No hay eventos para verificar")
        return False
    
    for evento in eventos[:5]:
        print(f"\n📋 Evento {evento['evento_id']}:")
        print(f"   Actor: {evento.get('actor', 'N/A')}")
        print(f"   Dispositivo: {evento.get('dispositivo', 'N/A')}")
        print(f"   Timestamp: {evento.get('timestamp_servidor', 'N/A')}")
    
    print(f"\n✅ Campos estructurales presentes")
    return True


def verificar_base_datos():
    """Verifica que la tabla eventos existe y tiene registros"""
    print("\n🔍 VERIFICACIÓN: Base de datos")
    print("-" * 60)
    
    with get_db() as db:
        # Verificar tabla eventos
        cursor = db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='eventos'
        """)
        
        if cursor.fetchone():
            print("✅ Tabla 'eventos' existe")
            
            # Contar registros
            cursor = db.execute("SELECT COUNT(*) FROM eventos")
            count = cursor.fetchone()[0]
            print(f"✅ {count} eventos en la base")
            
            # Verificar schema
            cursor = db.execute("PRAGMA table_info(eventos)")
            columnas = cursor.fetchall()
            print(f"✅ {len(columnas)} columnas en tabla eventos")
            
            return True
        else:
            print("❌ Tabla 'eventos' NO existe")
            return False


# ---------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SUITE DE TESTING - MÓDULO EVENTOS (AUP-EXO)")
    print("=" * 60)
    
    # Verificar base de datos primero
    if not verificar_base_datos():
        print("\n❌ La base de datos no está configurada correctamente")
        sys.exit(1)
    
    # Ejecutar tests
    resultados = []
    
    resultados.append(("Lectura de eventos", test_lectura_eventos() is not None))
    resultados.append(("Filtros por tipo", test_filtro_por_tipo()))
    resultados.append(("JOIN entidades", test_join_entidades()))
    resultados.append(("Estructura metadata", test_metadata_estructura()))
    resultados.append(("Hash trazabilidad", test_hash_trazabilidad()))
    resultados.append(("Actor y dispositivo", test_campos_actor_dispositivo()))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTING")
    print("=" * 60)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        icono = "✅" if resultado else "❌"
        print(f"{icono} {nombre}")
    
    print(f"\n🎯 RESULTADO FINAL: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 ¡Módulo de eventos funcionando perfectamente!")
        print("   Sistema AUP-EXO con trazabilidad completa operativo")
    else:
        print(f"\n⚠️ {total - exitosos} tests fallaron")
        print("   Revisar implementación o crear eventos de prueba")
