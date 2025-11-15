"""
app/core/trace.py
Generación de eventos estructurales con trazabilidad
AX-S - Sistema de Control de Accesos
"""

from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json


def generar_hash_evento(evento_data: Dict[str, Any], hash_previo: Optional[str] = None) -> str:
    """
    Genera hash SHA-256 para un evento con encadenamiento opcional
    
    Args:
        evento_data: Datos del evento
        hash_previo: Hash del evento anterior (para encadenamiento blockchain-style)
    
    Returns:
        Hash SHA-256 del evento
    """
    datos_completos = {
        "evento": evento_data,
        "hash_previo": hash_previo or "GENESIS",
        "timestamp": datetime.now().isoformat()
    }
    
    contenido = json.dumps(datos_completos, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(contenido.encode('utf-8')).hexdigest()


def crear_evento_trace(
    tipo_evento: str,
    entidad_id: str,
    metadata: Dict[str, Any],
    actor: str,
    dispositivo: str = "sistema"
) -> Dict[str, Any]:
    """
    Crea un evento estructural con trazabilidad completa
    
    Args:
        tipo_evento: "entrada", "salida", "rechazo", "alerta", etc.
        entidad_id: ID de la entidad involucrada
        metadata: Información contextual del evento
        actor: Usuario/sistema que genera el evento
        dispositivo: Dispositivo origen
    
    Returns:
        Evento estructurado con hash y timestamp
    """
    timestamp_servidor = datetime.now().isoformat()
    
    evento = {
        "tipo_evento": tipo_evento,
        "entidad_id": entidad_id,
        "metadata": metadata,
        "actor": actor,
        "dispositivo": dispositivo,
        "timestamp_servidor": timestamp_servidor
    }
    
    # Generar hash del evento
    evento_hash = generar_hash_evento(evento)
    evento["hash"] = evento_hash
    
    return evento


def validar_integridad_evento(evento: Dict[str, Any]) -> bool:
    """
    Valida la integridad de un evento verificando su hash
    
    Args:
        evento: Evento a validar
    
    Returns:
        True si el hash coincide, False si fue alterado
    """
    if "hash" not in evento:
        return False
    
    hash_original = evento.pop("hash")
    hash_calculado = generar_hash_evento(evento)
    evento["hash"] = hash_original
    
    return hash_original == hash_calculado
