"""
Script de Prueba Rápida - API FastAPI
Valida que todos los endpoints funcionen correctamente
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Imprimir sección visual"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_root():
    """Test 1: Endpoint raíz"""
    print_section("TEST 1: Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Root endpoint OK")


def test_health():
    """Test 2: Health check"""
    print_section("TEST 2: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Health check OK")


def test_crear_msp():
    """Test 3: Crear MSP"""
    print_section("TEST 3: Crear MSP")
    
    data = {
        "msp_id": f"msp_test_{int(datetime.now().timestamp())}",
        "nombre": "MSP Test Automatizado",
        "razon_social": "Test SA de CV",
        "rfc": "TST123456ABC",
        "email_contacto": "test@msp.com",
        "telefono_contacto": "+52 55 1234 5678",
        "plan": "professional",
        "max_condominios": 50
    }
    
    print(f"Datos enviados:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/msp/crear", json=data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ MSP creado exitosamente")
        return response.json()["msp_id"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_listar_msps():
    """Test 4: Listar MSPs"""
    print_section("TEST 4: Listar MSPs")
    
    response = requests.get(f"{BASE_URL}/msp/listar?skip=0&limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total MSPs: {data['total']}")
        print(f"MSPs retornados: {len(data['msps'])}")
        
        for msp in data['msps'][:3]:  # Mostrar primeros 3
            print(f"  - {msp['msp_id']}: {msp['nombre']} ({msp['plan']})")
        
        print("✅ Listado de MSPs OK")
        return data['msps']
    else:
        print(f"❌ Error: {response.text}")
        return []


def test_obtener_msp(msp_id):
    """Test 5: Obtener MSP por ID"""
    print_section(f"TEST 5: Obtener MSP {msp_id}")
    
    response = requests.get(f"{BASE_URL}/msp/{msp_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ MSP obtenido OK")
    else:
        print(f"❌ Error: {response.text}")


def test_estadisticas_msp(msp_id):
    """Test 6: Estadísticas MSP"""
    print_section(f"TEST 6: Estadísticas MSP {msp_id}")
    
    response = requests.get(f"{BASE_URL}/msp/{msp_id}/estadisticas")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Estadísticas OK")
    else:
        print(f"❌ Error: {response.text}")


def test_crear_condominio(msp_id):
    """Test 7: Crear Condominio"""
    print_section(f"TEST 7: Crear Condominio bajo MSP {msp_id}")
    
    data = {
        "condominio_id": f"condo_test_{int(datetime.now().timestamp())}",
        "msp_id": msp_id,
        "nombre": "Condominio Test Automatizado",
        "direccion": "Calle Test 123",
        "ciudad": "Ciudad de México",
        "estado_mx": "CDMX",
        "codigo_postal": "01000",
        "telefono": "+52 55 9999 8888",
        "email": "admin@condotest.com",
        "total_unidades": 25
    }
    
    print(f"Datos enviados:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/condominio/crear", json=data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ Condominio creado exitosamente")
        return response.json()["condominio_id"]
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_listar_condominios(msp_id):
    """Test 8: Listar Condominios del MSP"""
    print_section(f"TEST 8: Listar Condominios del MSP {msp_id}")
    
    response = requests.get(f"{BASE_URL}/condominio/listar?msp_id={msp_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total Condominios del MSP: {data['total']}")
        
        for condo in data['condominios']:
            print(f"  - {condo['condominio_id']}: {condo['nombre']}")
            print(f"    Unidades: {condo['total_unidades']}, Estado: {condo['estado']}")
        
        print("✅ Listado de Condominios OK")
    else:
        print(f"❌ Error: {response.text}")


def test_actualizar_msp(msp_id):
    """Test 9: Actualizar MSP"""
    print_section(f"TEST 9: Actualizar MSP {msp_id}")
    
    data = {
        "plan": "enterprise",
        "max_condominios": 100
    }
    
    print(f"Actualizando: {json.dumps(data, indent=2)}")
    
    response = requests.put(f"{BASE_URL}/msp/{msp_id}", json=data)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print("✅ MSP actualizado OK")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪"*30)
    print("SUITE DE TESTS - API FASTAPI AX-S")
    print("🧪"*30)
    print(f"\nBase URL: {BASE_URL}")
    print("⚠️  Asegúrate de que el servidor esté corriendo:")
    print("   uvicorn app.main:app --reload\n")
    
    try:
        # Tests básicos
        test_root()
        test_health()
        
        # Crear MSP
        msp_id = test_crear_msp()
        if not msp_id:
            print("\n❌ No se pudo crear MSP, abortando tests")
            return
        
        # Tests de MSP
        test_listar_msps()
        test_obtener_msp(msp_id)
        test_estadisticas_msp(msp_id)
        test_actualizar_msp(msp_id)
        
        # Crear y listar Condominios
        condominio_id = test_crear_condominio(msp_id)
        if condominio_id:
            test_listar_condominios(msp_id)
        
        # Resumen final
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS COMPLETADOS")
        print("="*60)
        print(f"\n📋 Entidades creadas:")
        print(f"   - MSP: {msp_id}")
        if condominio_id:
            print(f"   - Condominio: {condominio_id}")
        
        print(f"\n🌐 Ver en Swagger UI: {BASE_URL}/docs")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor")
        print("💡 Asegúrate de ejecutar: uvicorn app.main:app --reload")
        print(f"💡 Servidor esperado en: {BASE_URL}\n")
    
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
