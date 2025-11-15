"""
app/core/qr_engine.py
Motor de generación y validación de códigos QR
AX-S - Sistema de Control de Accesos
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib
import json


def generar_qr_visitante(
    nombre: str,
    residente_autorizador: str,
    vigencia_horas: int = 24,
    metadata: Optional[Dict] = None
) -> str:
    """
    Genera un código QR único para visitante
    
    Args:
        nombre: Nombre del visitante
        residente_autorizador: Residente que autoriza
        vigencia_horas: Horas de validez del QR
        metadata: Información adicional (casa, motivo, etc.)
    
    Returns:
        Código QR único (formato: QR-{hash})
    """
    timestamp = datetime.now()
    expiracion = timestamp + timedelta(hours=vigencia_horas)
    
    datos_qr = {
        "nombre": nombre,
        "autorizador": residente_autorizador,
        "timestamp": timestamp.isoformat(),
        "expira": expiracion.isoformat(),
        "metadata": metadata or {}
    }
    
    contenido = json.dumps(datos_qr, sort_keys=True)
    hash_qr = hashlib.sha256(contenido.encode('utf-8')).hexdigest()[:16]
    
    return f"QR-{hash_qr.upper()}"


def validar_qr(
    codigo_qr: str,
    datos_qr_db: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Valida un código QR contra los datos almacenados
    
    Args:
        codigo_qr: Código QR escaneado
        datos_qr_db: Datos del QR almacenados en DB
    
    Returns:
        Dict con "valido" (bool), "motivo" (str si inválido)
    """
    # Verificar existencia
    if not datos_qr_db:
        return {
            "valido": False,
            "motivo": "Código QR no encontrado en el sistema"
        }
    
    # Verificar vigencia
    if "expira" in datos_qr_db:
        expiracion = datetime.fromisoformat(datos_qr_db["expira"])
        if datetime.now() > expiracion:
            return {
                "valido": False,
                "motivo": f"Código QR expirado (venció: {expiracion.strftime('%Y-%m-%d %H:%M')})"
            }
    
    # Verificar si ya fue usado (si es de un solo uso)
    if datos_qr_db.get("uso_unico") and datos_qr_db.get("usado"):
        return {
            "valido": False,
            "motivo": "Código QR ya fue utilizado"
        }
    
    return {
        "valido": True,
        "motivo": None,
        "datos": datos_qr_db
    }


def generar_qr_proveedor_recurrente(
    empresa: str,
    rfc: str,
    dias_validos: list,
    horario_desde: str,
    horario_hasta: str
) -> str:
    """
    Genera QR para proveedor recurrente con restricciones
    
    Args:
        empresa: Nombre de la empresa
        rfc: RFC del proveedor
        dias_validos: Lista de días ["lunes", "martes", ...]
        horario_desde: Hora inicio (HH:MM)
        horario_hasta: Hora fin (HH:MM)
    
    Returns:
        Código QR permanente (formato: QRPROV-{hash})
    """
    datos_qr = {
        "tipo": "proveedor_recurrente",
        "empresa": empresa,
        "rfc": rfc,
        "restricciones": {
            "dias_validos": dias_validos,
            "horario_desde": horario_desde,
            "horario_hasta": horario_hasta
        },
        "timestamp_creacion": datetime.now().isoformat()
    }
    
    contenido = json.dumps(datos_qr, sort_keys=True)
    hash_qr = hashlib.sha256(contenido.encode('utf-8')).hexdigest()[:16]
    
    return f"QRPROV-{hash_qr.upper()}"
