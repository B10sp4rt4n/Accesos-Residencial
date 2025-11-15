"""
modulos/__init__.py
Exportaciones de módulos AUP-EXO
"""

# Módulo universal de entidades
from .entidades import (
    crear_entidad,
    obtener_entidades,
    obtener_entidad_por_id,
    buscar_entidad_por_identificador,
    actualizar_entidad,
    desactivar_entidad,
    reactivar_entidad,
    ui_gestion_entidades,
    render_personas,
    render_vehiculos
)

# Módulos legacy (compatibilidad)
try:
    from .accesos import *
except ImportError:
    pass

try:
    from .eventos import *
except ImportError:
    pass

try:
    from .vigilancia import *
except ImportError:
    pass

try:
    from .politicas import *
except ImportError:
    pass

__all__ = [
    # Funciones del módulo de entidades
    'crear_entidad',
    'obtener_entidades',
    'obtener_entidad_por_id',
    'buscar_entidad_por_identificador',
    'actualizar_entidad',
    'desactivar_entidad',
    'reactivar_entidad',
    'ui_gestion_entidades',
    # Aliases de compatibilidad
    'render_personas',
    'render_vehiculos',
    # Legacy
    'render_eventos',
    'render_vigilancia',
    'render_politicas'
]
