"""
app/core/visitor_engine.py
Motor de gestión de visitantes y folios
AX-S - Sistema de Control de Accesos
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
import random
import string


def generar_folio_visita() -> str:
    """
    Genera un folio único para visita
    
    Formato: VIS-YYYYMMDD-XXXX
    Ejemplo: VIS-20251115-A3F9
    
    Returns:
        Folio único de visita
    """
    fecha_str = datetime.now().strftime("%Y%m%d")
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    return f"VIS-{fecha_str}-{codigo}"


def registrar_visitante(
    nombre: str,
    identificador: str,
    residente_autoriza: str,
    casa_destino: str,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Registra un visitante con folio automático
    
    Args:
        nombre: Nombre completo del visitante
        identificador: INE, licencia, pasaporte, etc.
        residente_autoriza: Nombre del residente que autoriza
        casa_destino: Casa a la que visita
        metadata: Info adicional (motivo, vehículo, etc.)
    
    Returns:
        Dict con folio, entidad_id y datos del visitante
    """
    folio = generar_folio_visita()
    timestamp = datetime.now().isoformat()
    
    visitante = {
        "folio": folio,
        "tipo": "visitante",
        "nombre": nombre,
        "identificador": identificador,
        "residente_autoriza": residente_autoriza,
        "casa_destino": casa_destino,
        "timestamp_registro": timestamp,
        "metadata": metadata or {}
    }
    
    return visitante


def validar_autorizacion_residente(
    residente_id: str,
    visitante_nombre: str,
    casa_destino: str
) -> Dict[str, bool]:
    """
    Valida que un residente pueda autorizar una visita
    
    Args:
        residente_id: ID del residente
        visitante_nombre: Nombre del visitante
        casa_destino: Casa de destino
    
    Returns:
        Dict con "autorizado" (bool) y "motivo" (str si no autorizado)
    """
    # TODO: Implementar lógica de validación
    # - Verificar que residente existe
    # - Verificar que casa corresponde al residente
    # - Verificar límites de visitas por día
    # - Verificar lista negra
    
    return {
        "autorizado": True,
        "motivo": None
    }


def listar_visitas_del_dia(fecha: Optional[date] = None) -> list:
    """
    Lista todas las visitas del día actual o fecha específica
    
    Args:
        fecha: Fecha a consultar (default: hoy)
    
    Returns:
        Lista de visitas del día
    """
    # TODO: Implementar query a BD
    # SELECT * FROM visitas WHERE DATE(timestamp_registro) = fecha
    
    return []


def marcar_salida_visitante(folio: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
    """
    Registra la salida de un visitante
    
    Args:
        folio: Folio de la visita
        timestamp: Timestamp de salida (default: ahora)
    
    Returns:
        Dict con confirmación de salida
    """
    timestamp_salida = timestamp or datetime.now().isoformat()
    
    return {
        "folio": folio,
        "timestamp_salida": timestamp_salida,
        "estado": "finalizada"
    }
