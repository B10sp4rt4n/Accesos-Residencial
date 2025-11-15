"""
app/core/__init__.py
Módulos centrales de AX-S (AUP-EXO)
Sistema de Control de Accesos - Versión SaaS
"""

from .orchestrator import OrquestadorAccesos
from .policy_engine import evaluar_reglas
from .trace import crear_evento_trace, generar_hash_evento, validar_integridad_evento
from .qr_engine import generar_qr_visitante, validar_qr, generar_qr_proveedor_recurrente
from .visitor_engine import generar_folio_visita, registrar_visitante, marcar_salida_visitante
from .provider_engine import registrar_proveedor, configurar_horarios_proveedor, validar_acceso_proveedor
from .emergency_engine import registrar_emergencia, autorizar_emergencia_automatica, marcar_salida_emergencia
from .analytics import resumen_analitico, comparar_t1_t0, detectar_anomalias

__all__ = [
    # Orquestador principal
    "OrquestadorAccesos",
    
    # Motor de políticas
    "evaluar_reglas",
    
    # Trazabilidad
    "crear_evento_trace",
    "generar_hash_evento",
    "validar_integridad_evento",
    
    # QR
    "generar_qr_visitante",
    "validar_qr",
    "generar_qr_proveedor_recurrente",
    
    # Visitantes
    "generar_folio_visita",
    "registrar_visitante",
    "marcar_salida_visitante",
    
    # Proveedores
    "registrar_proveedor",
    "configurar_horarios_proveedor",
    "validar_acceso_proveedor",
    
    # Emergencias
    "registrar_emergencia",
    "autorizar_emergencia_automatica",
    "marcar_salida_emergencia",
    
    # Analítica
    "resumen_analitico",
    "comparar_t1_t0",
    "detectar_anomalias"
]

__version__ = "1.0.0-saas"
__author__ = "AUP-EXO"
