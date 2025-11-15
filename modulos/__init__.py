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

# UI universal de entidades
from .entidades_ui import (
    ui_entidades
)

# Módulo de vigilancia
from .vigilancia import (
    buscar_entidad,
    obtener_eventos_recientes,
    ui_vigilancia,
    ui_resumen_vigilancia,
    render_vigilancia
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
    from .politicas import *
except ImportError:
    pass

__all__ = [
    # Funciones del módulo de entidades (backend)
    'crear_entidad',
    'obtener_entidades',
    'obtener_entidad_por_id',
    'buscar_entidad_por_identificador',
    'actualizar_entidad',
    'desactivar_entidad',
    'reactivar_entidad',
    'ui_gestion_entidades',
    # UI universal de entidades
    'ui_entidades',
    # Funciones del módulo de vigilancia
    'buscar_entidad',
    'obtener_eventos_recientes',
    'ui_vigilancia',
    'ui_resumen_vigilancia',
    # Aliases de compatibilidad
    'render_personas',
    'render_vehiculos',
    'render_vigilancia',
    # Legacy
    'render_eventos',
    'render_politicas'
]
