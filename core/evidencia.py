# core/evidencia.py
"""
Gestión de evidencias y puente a Recordia (AUP-EXO)
"""


def enviar_a_recordia(evento_hash, metadata):
    """
    Envía evento a Recordia para trazabilidad jurídica externa.
    
    FASE EXO - Integración con Recordia-Bridge (stub preliminar)
    
    Args:
        evento_hash: Hash SHA-256 del evento
        metadata: Metadatos del evento
    
    Returns:
        Recibo de Recordia (formato: REC-{hash_prefix})
    
    TODO: En producción, conectar con Recordia-Bridge real
    """
    # Por ahora: stub que retorna recibo simulado
    recibo = f"REC-{evento_hash[:10]}"
    
    return recibo
