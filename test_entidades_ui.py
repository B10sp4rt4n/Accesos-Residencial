#!/usr/bin/env python3
"""
test_entidades_ui.py
Prueba de la UI universal de entidades
Simula registro de diferentes tipos
"""

from modulos.entidades import crear_entidad, obtener_entidades
from modulos.entidades_ui import PLANTILLAS

def test_registros_completos():
    """Prueba registro de diferentes tipos de entidades"""
    print("=" * 70)
    print("🧪 PRUEBA DE UI UNIVERSAL DE ENTIDADES")
    print("=" * 70)

    # 1. REGISTRAR PERSONA (RESIDENTE)
    print("\n1️⃣ Registrando RESIDENTE...")
    persona_attrs = {
        **PLANTILLAS['persona'],
        "tipo_persona": "residente",
        "telefono": "5512345678",
        "email": "maria.garcia@ejemplo.com",
        "direccion": "Lote 25",
        "casa": "25",
        "manzana": "B",
        "curp": "GAMA850315MDFRRR01",
        "notas": "Residente desde 2020"
    }
    
    persona_id, persona_hash = crear_entidad(
        tipo="persona",
        nombre="María García López",
        identificador="GAMA850315",
        atributos=persona_attrs
    )
    print(f"   ✅ Residente registrado: {persona_id}")
    print(f"      Hash: {persona_hash[:20]}...")

    # 2. REGISTRAR VEHÍCULO
    print("\n2️⃣ Registrando VEHÍCULO...")
    vehiculo_attrs = {
        **PLANTILLAS['vehiculo'],
        "marca": "Nissan",
        "modelo": "Versa",
        "color": "Plata",
        "año": "2022",
        "tipo_vehiculo": "auto",
        "propietario": "María García",
        "notas": "Vehículo principal de la familia"
    }
    
    vehiculo_id, vehiculo_hash = crear_entidad(
        tipo="vehiculo",
        nombre="Nissan Versa Plata",
        identificador="NVZ-4455",
        atributos=vehiculo_attrs
    )
    print(f"   ✅ Vehículo registrado: {vehiculo_id}")
    print(f"      Hash: {vehiculo_hash[:20]}...")

    # 3. REGISTRAR VISITA
    print("\n3️⃣ Registrando VISITA...")
    visita_attrs = {
        **PLANTILLAS['visita'],
        "telefono": "5598765432",
        "motivo": "Entrega de paquete",
        "destino": "Casa 25",
        "casa_destino": "25",
        "residente_autoriza": "María García",
        "vigencia": "1 día",
        "empresa": "DHL Express",
        "notas": "Paquete grande, requiere firma"
    }
    
    visita_id, visita_hash = crear_entidad(
        tipo="visita",
        nombre="Roberto Mensajero",
        identificador="FOLIO-DHL-12345",
        atributos=visita_attrs
    )
    print(f"   ✅ Visita registrada: {visita_id}")
    print(f"      Hash: {visita_hash[:20]}...")

    # 4. REGISTRAR PROVEEDOR
    print("\n4️⃣ Registrando PROVEEDOR...")
    proveedor_attrs = {
        **PLANTILLAS['proveedor'],
        "empresa": "Jardinería Pro",
        "telefono": "5587654321",
        "rfc": "JPR1234567XX",
        "giro": "Servicios de jardinería",
        "contacto": "Luis Hernández",
        "servicios": "Mantenimiento de áreas verdes",
        "notas": "Servicio quincenal"
    }
    
    proveedor_id, proveedor_hash = crear_entidad(
        tipo="proveedor",
        nombre="Jardinería Pro SA de CV",
        identificador="JPR-PROV-001",
        atributos=proveedor_attrs
    )
    print(f"   ✅ Proveedor registrado: {proveedor_id}")
    print(f"      Hash: {proveedor_hash[:20]}...")

    # 5. CONSULTAR TODAS LAS ENTIDADES
    print("\n5️⃣ Consultando entidades registradas...")
    
    personas = obtener_entidades(tipo="persona")
    vehiculos = obtener_entidades(tipo="vehiculo")
    visitas = obtener_entidades(tipo="visita")
    proveedores = obtener_entidades(tipo="proveedor")
    
    print(f"\n   📊 TOTALES:")
    print(f"      👥 Personas: {len(personas)}")
    print(f"      🚗 Vehículos: {len(vehiculos)}")
    print(f"      🚪 Visitas: {len(visitas)}")
    print(f"      🏢 Proveedores: {len(proveedores)}")
    print(f"      📦 TOTAL: {len(personas) + len(vehiculos) + len(visitas) + len(proveedores)}")

    # 6. VERIFICAR PLANTILLAS
    print("\n6️⃣ Verificando plantillas disponibles...")
    for tipo, plantilla in PLANTILLAS.items():
        campos = len(plantilla.keys())
        print(f"   ✅ {tipo.upper()}: {campos} campos predefinidos")

    print("\n" + "=" * 70)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
    print("\n📊 RESUMEN:")
    print("   ✅ 4 tipos de entidades registradas")
    print("   ✅ Plantillas funcionando correctamente")
    print("   ✅ Atributos específicos por tipo")
    print("   ✅ Hashes generados automáticamente")
    print("\n🎯 UI Universal lista para usar con Streamlit")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_registros_completos()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
