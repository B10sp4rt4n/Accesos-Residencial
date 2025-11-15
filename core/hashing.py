"""
core/hashing.py
Sistema de hashing estructural para trazabilidad AUP-EXO
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any


def hash_evento(data: dict) -> str:
    """
    Genera hash SHA-256 de un evento
    Garantiza trazabilidad e inmutabilidad
    """
    # Ordenar keys para consistencia
    cadena = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest()


def hash_entidad(entidad_data: dict) -> str:
    """
    Genera hash SHA-256 de una entidad
    Permite detección de cambios
    """
    # Excluir campos que no afectan la identidad
    data_limpia = {
        k: v for k, v in entidad_data.items()
        if k not in ['fecha_actualizacion', 'updated_by', 'hash_prev', 'hash_actual']
    }
    
    cadena = json.dumps(data_limpia, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest()


def verificar_hash(data: dict, hash_esperado: str) -> bool:
    """
    Verifica que el hash de los datos coincida con el esperado
    Útil para validar integridad
    """
    hash_actual = hash_evento(data)
    return hash_actual == hash_esperado


def generar_hash_cadena(
    hash_prev: str | None,
    data: dict,
    timestamp: str | None = None
) -> tuple[str, dict]:
    """
    Genera hash encadenado (blockchain-style)
    
    Returns:
        (hash_actual, data_con_hash)
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    data_completa = {
        **data,
        "hash_prev": hash_prev,
        "timestamp": timestamp
    }
    
    hash_actual = hash_evento(data_completa)
    
    return hash_actual, data_completa


def hash_evidencia(archivo_bytes: bytes, metadata: dict = None) -> str:
    """
    Genera hash de archivo de evidencia (foto, documento)
    Opcionalmente incluye metadata
    """
    hash_archivo = hashlib.sha256(archivo_bytes).hexdigest()
    
    if metadata:
        data_combinada = {
            "hash_archivo": hash_archivo,
            **metadata
        }
        return hash_evento(data_combinada)
    
    return hash_archivo


def generar_id_unico(prefijo: str, data: dict) -> str:
    """
    Genera ID único basado en contenido
    Útil para entidades
    
    Ejemplo: ENT_a3f5b2c...
    """
    hash_data = hash_evento(data)[:12]
    return f"{prefijo}_{hash_data}"


# Funciones de utilidad para validación

def validar_cadena_hash(eventos: list[dict]) -> tuple[bool, str]:
    """
    Valida que una cadena de eventos mantenga integridad
    
    Returns:
        (es_valida, mensaje)
    """
    if not eventos:
        return True, "Sin eventos que validar"
    
    for i in range(1, len(eventos)):
        evento_actual = eventos[i]
        evento_prev = eventos[i-1]
        
        if evento_actual.get('hash_prev') != evento_prev.get('hash_actual'):
            return False, f"Ruptura en cadena en evento {i}: hash_prev no coincide"
        
        # Verificar integridad del evento actual
        data_sin_hash = {k: v for k, v in evento_actual.items() if k != 'hash_actual'}
        hash_calculado = hash_evento(data_sin_hash)
        
        if hash_calculado != evento_actual.get('hash_actual'):
            return False, f"Hash corrupto en evento {i}"
    
    return True, "Cadena válida"


def verificar_cadena_integridad() -> dict:
    """
    Verifica la integridad de toda la cadena de eventos en la base de datos
    
    Returns:
        dict con 'integra', 'total_eventos', 'primer_corrupto', 'detalles'
    """
    from core.db import get_db
    
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM eventos ORDER BY id ASC")
        columns = [desc[0] for desc in cursor.description]
        eventos = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    if not eventos:
        return {
            'integra': True,
            'total_eventos': 0,
            'detalles': 'No hay eventos que verificar'
        }
    
    for i in range(1, len(eventos)):
        evento_actual = eventos[i]
        evento_prev = eventos[i-1]
        
        # Verificar encadenamiento
        if evento_actual.get('hash_previo') != evento_prev.get('hash'):
            return {
                'integra': False,
                'total_eventos': len(eventos),
                'primer_corrupto': evento_actual['id'],
                'detalles': f"Ruptura en cadena: evento {evento_actual['id']} no está encadenado correctamente"
            }
    
    return {
        'integra': True,
        'total_eventos': len(eventos),
        'detalles': f'Cadena verificada correctamente ({len(eventos)} eventos)'
    }


if __name__ == "__main__":
    # Pruebas
    print("=== Pruebas de Hashing ===\n")
    
    # Test 1: Hash básico
    evento1 = {"tipo": "entrada", "placa": "ABC-123", "timestamp": "2025-11-15T10:00:00"}
    hash1 = hash_evento(evento1)
    print(f"Hash evento 1: {hash1}")
    
    # Test 2: Hash encadenado
    hash2, data2 = generar_hash_cadena(hash1, {"tipo": "salida", "placa": "ABC-123"})
    print(f"Hash encadenado: {hash2}")
    
    # Test 3: Validación
    es_valido = verificar_hash(evento1, hash1)
    print(f"Validación: {es_valido}")
    
    # Test 4: ID único
    id_entidad = generar_id_unico("ENT", {"nombre": "Juan Pérez", "tipo": "residente"})
    print(f"ID único generado: {id_entidad}")
