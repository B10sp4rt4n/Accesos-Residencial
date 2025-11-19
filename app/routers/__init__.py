"""
Routers __init__ - Exportar todos los routers
"""

from app.routers import msp_router
from app.routers import condominio_router

__all__ = [
    'msp_router',
    'condominio_router',
]
