"""
Schemas __init__ - Exportar todos los schemas
"""

from app.schemas.msp import (
    MSPCreate,
    MSPUpdate,
    MSPResponse,
    MSPListResponse
)

from app.schemas.condominio import (
    CondominioCreate,
    CondominioUpdate,
    CondominioResponse,
    CondominioListResponse
)

__all__ = [
    # MSP
    'MSPCreate',
    'MSPUpdate',
    'MSPResponse',
    'MSPListResponse',
    # Condominio
    'CondominioCreate',
    'CondominioUpdate',
    'CondominioResponse',
    'CondominioListResponse',
]
