"""
core/roles.py
Sistema de roles y permisos AUP-EXO
"""

import json
from enum import Enum
from typing import List, Dict, Optional
from core.db import get_db


class Permisos(Enum):
    """Permisos disponibles en el sistema"""
    # Entidades
    CREAR_ENTIDADES = "crear_entidades"
    EDITAR_ENTIDADES = "editar_entidades"
    ELIMINAR_ENTIDADES = "eliminar_entidades"
    VER_ENTIDADES = "ver_entidades"
    
    # Accesos
    REGISTRAR_ACCESO = "registrar_acceso"
    VER_ACCESOS = "ver_accesos"
    AUTORIZAR_ACCESO = "autorizar_acceso"
    
    # Políticas
    CREAR_POLITICAS = "crear_politicas"
    EDITAR_POLITICAS = "editar_politicas"
    ELIMINAR_POLITICAS = "eliminar_politicas"
    VER_POLITICAS = "ver_politicas"
    
    # Reportes
    VER_REPORTES = "ver_reportes"
    EXPORTAR_REPORTES = "exportar_reportes"
    
    # Usuarios
    CREAR_USUARIOS = "crear_usuarios"
    EDITAR_USUARIOS = "editar_usuarios"
    ELIMINAR_USUARIOS = "eliminar_usuarios"
    GESTIONAR_USUARIOS = "gestionar_usuarios"
    
    # Sistema
    VER_BITACORA = "ver_bitacora"
    CONFIGURAR_SISTEMA = "configurar_sistema"
    VER_EVENTOS = "ver_eventos"
    
    # Específicos
    VER_MIS_ACCESOS = "ver_mis_accesos"
    AUTORIZAR_VISITAS = "autorizar_visitas"
    CONSULTAR_ENTIDADES = "consultar_entidades"


class RoleManager:
    """Gestor de roles y permisos"""
    
    def __init__(self):
        self.cache_roles = {}
    
    def obtener_rol(self, rol_id: str) -> Optional[Dict]:
        """Obtiene información de un rol"""
        if rol_id in self.cache_roles:
            return self.cache_roles[rol_id]
        
        with get_db() as db:
            rol = db.execute(
                "SELECT * FROM roles WHERE rol_id = ?",
                (rol_id,)
            ).fetchone()
            
            if rol:
                rol_dict = {
                    "rol_id": rol['rol_id'],
                    "nombre": rol['nombre'],
                    "descripcion": rol['descripcion'],
                    "permisos": json.loads(rol['permisos']),
                    "nivel_acceso": rol['nivel_acceso']
                }
                self.cache_roles[rol_id] = rol_dict
                return rol_dict
        
        return None
    
    def tiene_permiso(self, usuario_id: str, permiso: str) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        with get_db() as db:
            usuario = db.execute(
                "SELECT rol FROM usuarios WHERE usuario_id = ? AND estado = 'activo'",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return False
            
            rol = self.obtener_rol(usuario['rol'])
            if not rol:
                return False
            
            return permiso in rol['permisos']
    
    def obtener_permisos_usuario(self, usuario_id: str) -> List[str]:
        """Obtiene todos los permisos de un usuario"""
        with get_db() as db:
            usuario = db.execute(
                "SELECT rol FROM usuarios WHERE usuario_id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return []
            
            rol = self.obtener_rol(usuario['rol'])
            return rol['permisos'] if rol else []
    
    def crear_rol(
        self,
        rol_id: str,
        nombre: str,
        descripcion: str,
        permisos: List[str],
        nivel_acceso: int = 1
    ) -> bool:
        """Crea un nuevo rol"""
        try:
            with get_db() as db:
                db.execute("""
                    INSERT INTO roles (
                        rol_id, nombre, descripcion, permisos,
                        nivel_acceso, fecha_creacion
                    ) VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    rol_id,
                    nombre,
                    descripcion,
                    json.dumps(permisos),
                    nivel_acceso
                ))
            
            # Limpiar caché
            self.cache_roles.pop(rol_id, None)
            return True
        except Exception as e:
            print(f"Error creando rol: {e}")
            return False
    
    def asignar_rol_usuario(self, usuario_id: str, rol_id: str) -> bool:
        """Asigna un rol a un usuario"""
        try:
            with get_db() as db:
                db.execute(
                    "UPDATE usuarios SET rol = ? WHERE usuario_id = ?",
                    (rol_id, usuario_id)
                )
            return True
        except Exception as e:
            print(f"Error asignando rol: {e}")
            return False
    
    def validar_nivel_acceso(
        self,
        usuario_id: str,
        nivel_requerido: int
    ) -> bool:
        """Verifica si el usuario tiene el nivel de acceso requerido"""
        with get_db() as db:
            usuario = db.execute(
                "SELECT rol FROM usuarios WHERE usuario_id = ?",
                (usuario_id,)
            ).fetchone()
            
            if not usuario:
                return False
            
            rol = self.obtener_rol(usuario['rol'])
            if not rol:
                return False
            
            return rol['nivel_acceso'] >= nivel_requerido


# Decorador para requerir permisos
def requiere_permiso(permiso: str):
    """Decorador para verificar permisos antes de ejecutar una función"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            usuario_id = getattr(self, 'usuario_id', None)
            if not usuario_id:
                raise PermissionError("Usuario no autenticado")
            
            role_manager = RoleManager()
            if not role_manager.tiene_permiso(usuario_id, permiso):
                raise PermissionError(f"Permiso requerido: {permiso}")
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def inicializar_roles_default():
    """Crea los roles por defecto del sistema"""
    role_manager = RoleManager()
    
    # Administrador
    role_manager.crear_rol(
        rol_id="admin",
        nombre="Administrador",
        descripcion="Acceso total al sistema",
        permisos=[p.value for p in Permisos],
        nivel_acceso=10
    )
    
    # Coordinador
    role_manager.crear_rol(
        rol_id="coordinador",
        nombre="Coordinador",
        descripcion="Gestión de accesos y reportes",
        permisos=[
            Permisos.CREAR_ENTIDADES.value,
            Permisos.EDITAR_ENTIDADES.value,
            Permisos.VER_ENTIDADES.value,
            Permisos.REGISTRAR_ACCESO.value,
            Permisos.VER_ACCESOS.value,
            Permisos.AUTORIZAR_ACCESO.value,
            Permisos.CREAR_POLITICAS.value,
            Permisos.EDITAR_POLITICAS.value,
            Permisos.VER_POLITICAS.value,
            Permisos.VER_REPORTES.value,
            Permisos.EXPORTAR_REPORTES.value,
            Permisos.VER_BITACORA.value,
            Permisos.VER_EVENTOS.value
        ],
        nivel_acceso=7
    )
    
    # Vigilante
    role_manager.crear_rol(
        rol_id="vigilante",
        nombre="Vigilante",
        descripcion="Registro de accesos",
        permisos=[
            Permisos.REGISTRAR_ACCESO.value,
            Permisos.VER_ACCESOS.value,
            Permisos.CONSULTAR_ENTIDADES.value,
            Permisos.VER_EVENTOS.value,
            Permisos.VER_ENTIDADES.value
        ],
        nivel_acceso=3
    )
    
    # Residente
    role_manager.crear_rol(
        rol_id="residente",
        nombre="Residente",
        descripcion="Consulta básica y autorización de visitas",
        permisos=[
            Permisos.VER_MIS_ACCESOS.value,
            Permisos.AUTORIZAR_VISITAS.value
        ],
        nivel_acceso=1
    )
    
    print("✅ Roles por defecto inicializados")


if __name__ == "__main__":
    from core.db import init_db
    init_db()
    inicializar_roles_default()
    
    # Pruebas
    print("\n=== Pruebas de Roles ===")
    rm = RoleManager()
    
    # Obtener rol
    rol_admin = rm.obtener_rol("admin")
    print(f"Rol admin: {rol_admin['nombre']}")
    print(f"Permisos: {len(rol_admin['permisos'])}")
    
    rol_vigilante = rm.obtener_rol("vigilante")
    print(f"\nRol vigilante: {rol_vigilante['nombre']}")
    print(f"Permisos: {rol_vigilante['permisos']}")
