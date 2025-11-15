"""
app/core/emergency_engine.py
Motor de accesos de emergencia (bomberos, ambulancias, policía)
AX-S - Sistema de Control de Accesos
"""

from datetime import datetime
from typing import Dict, Any, Optional


TIPOS_EMERGENCIA = {
    "bomberos": {
        "prioridad": 1,
        "auto_autorizado": True,
        "requiere_bitacora": True
    },
    "ambulancia": {
        "prioridad": 1,
        "auto_autorizado": True,
        "requiere_bitacora": True
    },
    "policia": {
        "prioridad": 2,
        "auto_autorizado": True,
        "requiere_bitacora": True
    },
    "proteccion_civil": {
        "prioridad": 2,
        "auto_autorizado": True,
        "requiere_bitacora": True
    },
    "servicios_publicos": {
        "prioridad": 3,
        "auto_autorizado": False,
        "requiere_bitacora": True
    }
}


def registrar_emergencia(
    tipo_emergencia: str,
    unidad: str,
    placa: Optional[str] = None,
    motivo: str = "",
    casa_destino: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Registra un acceso de emergencia
    
    Args:
        tipo_emergencia: "bomberos", "ambulancia", "policia", etc.
        unidad: Número de unidad (ej: "BOM-15", "AMB-03")
        placa: Placa del vehículo (opcional)
        motivo: Descripción breve del incidente
        casa_destino: Casa de destino (si aplica)
        metadata: Info adicional
    
    Returns:
        Registro de emergencia con folio
    """
    timestamp = datetime.now()
    
    # Generar folio de emergencia
    fecha_str = timestamp.strftime("%Y%m%d%H%M")
    folio = f"EMER-{tipo_emergencia.upper()[:3]}-{fecha_str}"
    
    config_tipo = TIPOS_EMERGENCIA.get(tipo_emergencia, {
        "prioridad": 5,
        "auto_autorizado": False,
        "requiere_bitacora": True
    })
    
    emergencia = {
        "folio": folio,
        "tipo": "emergencia",
        "tipo_emergencia": tipo_emergencia,
        "unidad": unidad,
        "placa": placa,
        "motivo": motivo,
        "casa_destino": casa_destino,
        "timestamp_entrada": timestamp.isoformat(),
        "prioridad": config_tipo["prioridad"],
        "auto_autorizado": config_tipo["auto_autorizado"],
        "metadata": metadata or {}
    }
    
    return emergencia


def autorizar_emergencia_automatica(tipo_emergencia: str) -> bool:
    """
    Verifica si un tipo de emergencia está auto-autorizado
    
    Args:
        tipo_emergencia: Tipo de emergencia
    
    Returns:
        True si está auto-autorizado, False si requiere confirmación
    """
    config = TIPOS_EMERGENCIA.get(tipo_emergencia, {})
    return config.get("auto_autorizado", False)


def marcar_salida_emergencia(folio: str) -> Dict[str, Any]:
    """
    Registra la salida de una unidad de emergencia
    
    Args:
        folio: Folio de la emergencia
    
    Returns:
        Registro de salida
    """
    timestamp_salida = datetime.now().isoformat()
    
    return {
        "folio": folio,
        "timestamp_salida": timestamp_salida,
        "estado": "finalizada"
    }


def generar_bitacora_emergencias(fecha: str) -> Dict[str, Any]:
    """
    Genera bitácora de emergencias del día
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD
    
    Returns:
        Bitácora con todas las emergencias del día
    """
    # TODO: Implementar query a BD
    # SELECT * FROM eventos WHERE tipo = 'emergencia' AND DATE(timestamp) = fecha
    
    return {
        "fecha": fecha,
        "total_emergencias": 0,
        "por_tipo": {},
        "eventos": []
    }


def alertar_administracion_emergencia(emergencia: Dict[str, Any]) -> bool:
    """
    Envía alerta a administración sobre emergencia
    
    Args:
        emergencia: Datos de la emergencia
    
    Returns:
        True si alerta fue enviada exitosamente
    """
    # TODO: Implementar integración con notifications.py
    # - Email urgente
    # - SMS/WhatsApp a grupo de administración
    # - Notificación push
    
    return True
