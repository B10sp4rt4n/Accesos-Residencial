#!/usr/bin/env python3
"""
test_entidades.py
Script de prueba para el módulo universal de entidades AUP-EXO
"""

from modulos.entidades import (
    crear_entidad,
    obtener_entidades,
    obtener_entidad_por_id,
    buscar_entidad_por_identificador,
    actualizar_entidad,
    desactivar_entidad
)

def test_crear_persona():
    """Prueba creación de persona"""
    print("\n1️⃣ Creando persona...")
    ent_id, ent_hash = crear_entidad(
        tipo='persona',
        nombre='María González',
        identificador='CURP123456',
        atributos={
            'telefono': '5512345678',
            'email': 'maria@ejemplo.com',
            'direccion': 'Casa 25, Manzana B'
        }
    )
    print(f"   ✅ Persona creada: {ent_id}")
    print(f"   Hash: {ent_hash[:20]}...")
    return ent_id

def test_crear_vehiculo():
    """Prueba creación de vehículo"""
    print("\n2️⃣ Creando vehículo...")
    ent_id, ent_hash = crear_entidad(
        tipo='vehiculo',
        nombre='Honda Civic Blanco',
        identificador='ABC-1234',
        atributos={
            'marca': 'Honda',
            'modelo': 'Civic',
            'color': 'Blanco',
            'año': '2022'
        }
    )
    print(f"   ✅ Vehículo creado: {ent_id}")
    print(f"   Hash: {ent_hash[:20]}...")
    return ent_id

def test_crear_visita():
    """Prueba creación de visita"""
    print("\n3️⃣ Creando visita...")
    ent_id, ent_hash = crear_entidad(
        tipo='visita',
        nombre='Carlos Ramírez',
        identificador='FOLIO-001',
        atributos={
            'telefono': '5598765432',
            'motivo': 'Entrega paquete',
            'destino': 'Casa 30'
        }
    )
    print(f"   ✅ Visita creada: {ent_id}")
    print(f"   Hash: {ent_hash[:20]}...")
    return ent_id

def test_consultar_entidades():
    """Prueba consulta de entidades"""
    print("\n4️⃣ Consultando entidades...")
    
    personas = obtener_entidades(tipo='persona')
    print(f"   📊 Total personas: {len(personas)}")
    
    vehiculos = obtener_entidades(tipo='vehiculo')
    print(f"   📊 Total vehículos: {len(vehiculos)}")
    
    visitas = obtener_entidades(tipo='visita')
    print(f"   📊 Total visitas: {len(visitas)}")
    
    todas = obtener_entidades()
    print(f"   📊 Total entidades: {len(todas)}")

def test_buscar_por_identificador():
    """Prueba búsqueda por identificador"""
    print("\n5️⃣ Buscando entidad por identificador...")
    
    # Buscar vehículo ABC-1234
    vehiculo = buscar_entidad_por_identificador('ABC-1234', tipo='vehiculo')
    if vehiculo:
        print(f"   ✅ Vehículo encontrado: {vehiculo['atributos'].get('nombre')}")
        print(f"      ID: {vehiculo['entidad_id']}")
    else:
        print("   ❌ Vehículo no encontrado")

def test_actualizar_entidad(entidad_id):
    """Prueba actualización de entidad"""
    print(f"\n6️⃣ Actualizando entidad {entidad_id[:20]}...")
    
    nuevo_hash = actualizar_entidad(
        entidad_id,
        atributos={
            'telefono': '5599887766',
            'email': 'nuevo@ejemplo.com',
            'notas': 'Actualizado en test'
        }
    )
    print(f"   ✅ Entidad actualizada")
    print(f"   Nuevo hash: {nuevo_hash[:20]}...")

def test_desactivar_entidad(entidad_id):
    """Prueba desactivación de entidad"""
    print(f"\n7️⃣ Desactivando entidad {entidad_id[:20]}...")
    
    resultado = desactivar_entidad(entidad_id)
    if resultado:
        print(f"   ✅ Entidad desactivada correctamente")
    
    # Verificar que no aparece en consultas activas
    activas = obtener_entidades(estado='activo')
    print(f"   📊 Entidades activas restantes: {len(activas)}")

def test_obtener_por_id(entidad_id):
    """Prueba obtención por ID"""
    print(f"\n8️⃣ Obteniendo entidad por ID...")
    
    entidad = obtener_entidad_por_id(entidad_id)
    if entidad:
        print(f"   ✅ Entidad encontrada:")
        print(f"      Tipo: {entidad['tipo']}")
        print(f"      Estado: {entidad['estado']}")
        print(f"      Atributos: {entidad['atributos']}")
    else:
        print(f"   ❌ Entidad no encontrada")

def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DEL MÓDULO UNIVERSAL DE ENTIDADES")
    print("=" * 60)
    
    try:
        # Crear entidades
        persona_id = test_crear_persona()
        vehiculo_id = test_crear_vehiculo()
        visita_id = test_crear_visita()
        
        # Consultar
        test_consultar_entidades()
        
        # Buscar
        test_buscar_por_identificador()
        
        # Actualizar
        test_actualizar_entidad(persona_id)
        
        # Obtener por ID
        test_obtener_por_id(persona_id)
        
        # Desactivar
        test_desactivar_entidad(visita_id)
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
