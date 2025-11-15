"""
core/__init__.py
Exportaciones del core AUP-EXO
"""

from .db import get_db, init_db
from .orquestador import OrquestadorAccesos
from .motor_reglas import evaluar_reglas
from .hashing import hash_evento, hash_entidad, verificar_cadena_integridad
from .roles import RoleManager, Permisos
from .contexto import ContextoManager

__all__ = [
    "get_db",
    "init_db",
    "OrquestadorAccesos",
    "evaluar_reglas",
    "hash_evento",
    "hash_entidad",
    "verificar_cadena_integridad",
    "RoleManager",
    "Permisos",
    "ContextoManager"
]

__version__ = "2.0.0-aup-exo"
__author__ = "Accesos Residencial Team"

from core.db import get_db, init_db
from core.orquestador import OrquestadorAccesos
from core.motor_reglas import evaluar_reglas
from core.hashing import hash_evento, hash_entidad
from core.roles import RoleManager, Permisos

__all__ = [
    'get_db',
    'init_db',
    'OrquestadorAccesos',
    'evaluar_reglas',
    'hash_evento',
    'hash_entidad',
    'RoleManager',
    'Permisos'
]
