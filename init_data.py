"""
init_data.py
Script para inicializar la base de datos con datos de ejemplo
"""

from core import init_db, OrquestadorAccesos, get_db
from datetime import datetime, timedelta
import random


def crear_datos_ejemplo():
    """Crea datos de ejemplo para demostración"""
    
    print("🚀 Inicializando base de datos AUP-EXO...")
    
    # Inicializar DB
    init_db()
    print("✅ Base de datos creada")
    
    orquestador = OrquestadorAccesos()
    
    # Crear residentes
    print("\n👥 Creando residentes...")
    residentes = []
    
    nombres_residentes = [
        ("Juan Pérez", "Casa 15", "Manzana A"),
        ("María López", "Casa 22", "Manzana B"),
        ("Carlos Ruiz", "Casa 31", "Manzana C"),
        ("Ana Martínez", "Casa 8", "Manzana A"),
        ("Luis Rodríguez", "Casa 45", "Manzana D")
    ]
    
    for nombre, lote, manzana in nombres_residentes:
        residente_id = orquestador.crear_entidad(
            tipo="persona",
            atributos={
                "tipo": "residente",
                "nombre_completo": nombre,
                "curp": f"CURP{random.randint(1000, 9999)}",
                "telefono": f"55{random.randint(10000000, 99999999)}",
                "email": f"{nombre.lower().replace(' ', '.')}@ejemplo.com",
                "direccion": f"{lote}, {manzana}",
                "lote": lote,
                "manzana": manzana
            }
        )
        residentes.append(residente_id['entidad_id'])
        print(f"  ✓ {nombre} - ID: {residente_id['entidad_id']}")
    
    # Crear vehículos
    print("\n🚗 Creando vehículos...")
    vehiculos = []
    
    placas = [
        ("ABC-1234", "CDMX", "Toyota Corolla", "Gris", residentes[0]),
        ("XYZ-7890", "CDMX", "Honda Civic", "Blanco", residentes[1]),
        ("DEF-4567", "EDO", "Nissan Versa", "Negro", residentes[2]),
        ("GHI-9012", "JAL", "Mazda 3", "Rojo", residentes[3]),
        ("JKL-3456", "NL", "Ford Focus", "Azul", residentes[4])
    ]
    
    for placa, estado, marca, color, propietario_id in placas:
        vehiculo_id = orquestador.crear_entidad(
            tipo="vehiculo",
            atributos={
                "placa": placa,
                "tipo": "auto",
                "estado_mx": estado,
                "marca": marca.split()[0],
                "modelo": " ".join(marca.split()[1:]),
                "color": color,
                "propietario_id": propietario_id
            }
        )
        vehiculos.append(vehiculo_id['entidad_id'])
        print(f"  ✓ {placa} ({marca} {color}) - ID: {vehiculo_id['entidad_id']}")
    
    # Crear políticas básicas
    print("\n📜 Creando políticas...")
    
    with get_db() as conn:
        # Política 1: Horario residentes
        conn.execute("""
            INSERT OR REPLACE INTO politicas (
                politica_id, nombre, descripcion, tipo, condiciones,
                prioridad, estado, aplicable_a, fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "POL_001",
            "Acceso 24/7 Residentes",
            "Los residentes tienen acceso las 24 horas con identificación válida",
            "acceso",
            '[{"tipo": "horario", "hora_inicio": "00:00", "hora_fin": "23:59"}]',
            1,
            "activa",
            "residente",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Política 2: Horario visitantes
        conn.execute("""
            INSERT OR REPLACE INTO politicas (
                politica_id, nombre, descripcion, tipo, condiciones,
                prioridad, estado, aplicable_a, fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "POL_002",
            "Horario Visitantes",
            "Los visitantes solo pueden ingresar de 6:00 AM a 10:00 PM",
            "acceso",
            '[{"tipo": "horario", "hora_inicio": "06:00", "hora_fin": "22:00"}]',
            2,
            "activa",
            "visitante",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Política 3: Lista negra
        conn.execute("""
            INSERT OR REPLACE INTO politicas (
                politica_id, nombre, descripcion, tipo, condiciones,
                prioridad, estado, aplicable_a, fecha_creacion, fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "POL_003",
            "Bloqueo Lista Negra",
            "Vehículos y personas en lista negra son rechazados automáticamente",
            "restriccion",
            '[{"tipo": "lista_negra", "accion": "denegar"}]',
            0,
            "activa",
            "global",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
    
    print("  ✓ 3 políticas creadas")
    
    # Crear eventos de ejemplo
    print("\n📋 Creando eventos de ejemplo...")
    
    tipos_evento = ["entrada", "salida"]
    
    for i in range(20):
        timestamp = datetime.now() - timedelta(hours=random.randint(0, 48))
        
        resultado = orquestador.procesar_acceso(
            entidad_id=random.choice(residentes),
            metadata={
                "vehiculo_id": random.choice(vehiculos),
                "tipo_acceso": random.choice(tipos_evento),
                "gate": "GATE_001",
                "timestamp_cliente": timestamp.isoformat()
            },
            actor="vigilante_demo",
            dispositivo="tablet-caseta-norte"
        )
        
        if i % 5 == 0:
            print(f"  ✓ {i+1} eventos creados...")
    
    print(f"  ✓ 20 eventos de acceso registrados")
    
    # Resumen
    print("\n" + "="*50)
    print("✅ INICIALIZACIÓN COMPLETADA")
    print("="*50)
    print(f"📊 Resumen:")
    print(f"  • {len(residentes)} residentes")
    print(f"  • {len(vehiculos)} vehículos")
    print(f"  • 3 políticas de acceso")
    print(f"  • 20 eventos registrados")
    print("\n🚀 El sistema está listo para usar")
    print("\n💡 Para iniciar la aplicación:")
    print("   streamlit run app_aup_exo.py")
    print()


if __name__ == "__main__":
    crear_datos_ejemplo()
