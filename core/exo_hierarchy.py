"""
AX-S - AUP-EXO Hierarchy Management
Control de acceso jerárquico multinivel

Niveles:
1. DS (Dominio Superior) - Super Admin
2. DD (Dominio Delegado) - MSP Admin
3. SE (Subdominio Específico) - Condominio Admin
4. NO (Nodo Operativo) - Admin Local
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class NivelAcceso(Enum):
    """Niveles de acceso en la jerarquía AUP-EXO"""
    DS = 1  # Dominio Superior - Super Admin
    DD = 2  # Dominio Delegado - MSP Admin
    SE = 3  # Subdominio Específico - Condominio Admin
    NO = 4  # Nodo Operativo - Admin Local


class RolExo(Enum):
    """Roles del sistema AUP-EXO"""
    SUPER_ADMIN = ("super_admin", NivelAcceso.DS)
    MSP_ADMIN = ("msp_admin", NivelAcceso.DD)
    CONDOMINIO_ADMIN = ("condominio_admin", NivelAcceso.SE)
    ADMIN_LOCAL = ("admin_local", NivelAcceso.NO)
    
    def __init__(self, nombre: str, nivel: NivelAcceso):
        self.nombre_rol = nombre
        self.nivel = nivel


@dataclass
class ContextoUsuario:
    """Contexto de usuario con scope jerárquico"""
    usuario_id: str
    nombre: str
    email: str
    rol: RolExo
    msp_id: Optional[str] = None
    condominio_id: Optional[str] = None
    
    def __post_init__(self):
        """Validar coherencia del contexto según el rol"""
        if self.rol == RolExo.SUPER_ADMIN:
            # Super Admin no debe tener msp_id ni condominio_id
            if self.msp_id or self.condominio_id:
                raise ValueError("Super Admin no debe tener msp_id ni condominio_id asignados")
        
        elif self.rol == RolExo.MSP_ADMIN:
            # MSP Admin debe tener msp_id pero no condominio_id
            if not self.msp_id:
                raise ValueError("MSP Admin debe tener msp_id asignado")
            if self.condominio_id:
                raise ValueError("MSP Admin no debe tener condominio_id asignado")
        
        elif self.rol in [RolExo.CONDOMINIO_ADMIN, RolExo.ADMIN_LOCAL]:
            # Condominio/Admin Local deben tener ambos
            if not self.msp_id or not self.condominio_id:
                raise ValueError(f"{self.rol.nombre_rol} debe tener msp_id y condominio_id asignados")
    
    @property
    def nivel_acceso(self) -> NivelAcceso:
        """Retorna el nivel de acceso del usuario"""
        return self.rol.nivel
    
    @property
    def es_super_admin(self) -> bool:
        """Verifica si el usuario es Super Admin"""
        return self.rol == RolExo.SUPER_ADMIN
    
    @property
    def es_msp_admin(self) -> bool:
        """Verifica si el usuario es MSP Admin"""
        return self.rol == RolExo.MSP_ADMIN
    
    @property
    def es_condominio_admin(self) -> bool:
        """Verifica si el usuario es Condominio Admin"""
        return self.rol == RolExo.CONDOMINIO_ADMIN
    
    @property
    def es_admin_local(self) -> bool:
        """Verifica si el usuario es Admin Local"""
        return self.rol == RolExo.ADMIN_LOCAL


class ControlAccesoExo:
    """Control de acceso jerárquico AUP-EXO"""
    
    @staticmethod
    def puede_acceder_msp(usuario: ContextoUsuario, msp_id: str) -> bool:
        """
        Verifica si el usuario puede acceder a un MSP específico
        
        Reglas:
        - Super Admin: Acceso a todos los MSPs
        - MSP Admin: Solo a su MSP
        - Condominio/Local Admin: Solo a su MSP (lectura limitada)
        """
        if usuario.es_super_admin:
            return True
        
        return usuario.msp_id == msp_id
    
    @staticmethod
    def puede_acceder_condominio(usuario: ContextoUsuario, msp_id: str, condominio_id: str) -> bool:
        """
        Verifica si el usuario puede acceder a un condominio específico
        
        Reglas:
        - Super Admin: Acceso a todos los condominios
        - MSP Admin: Solo a condominios de su MSP
        - Condominio/Local Admin: Solo a su condominio
        """
        if usuario.es_super_admin:
            return True
        
        if usuario.es_msp_admin:
            return usuario.msp_id == msp_id
        
        # Condominio Admin y Admin Local
        return usuario.msp_id == msp_id and usuario.condominio_id == condominio_id
    
    @staticmethod
    def puede_crear_usuario(usuario: ContextoUsuario, rol_objetivo: RolExo) -> bool:
        """
        Verifica si el usuario puede crear otro usuario con el rol objetivo
        
        Reglas:
        - Super Admin: Puede crear cualquier rol
        - MSP Admin: Puede crear Condominio Admin y Admin Local
        - Condominio Admin: Puede crear Admin Local
        - Admin Local: No puede crear usuarios
        """
        if usuario.es_super_admin:
            return True
        
        if usuario.es_msp_admin:
            return rol_objetivo in [RolExo.CONDOMINIO_ADMIN, RolExo.ADMIN_LOCAL]
        
        if usuario.es_condominio_admin:
            return rol_objetivo == RolExo.ADMIN_LOCAL
        
        return False
    
    @staticmethod
    def puede_modificar_entidad(
        usuario: ContextoUsuario,
        entidad_msp_id: Optional[str],
        entidad_condominio_id: Optional[str]
    ) -> bool:
        """
        Verifica si el usuario puede modificar una entidad específica
        
        Args:
            usuario: Contexto del usuario
            entidad_msp_id: MSP ID de la entidad (puede ser None)
            entidad_condominio_id: Condominio ID de la entidad (puede ser None)
        """
        if usuario.es_super_admin:
            return True
        
        if usuario.es_msp_admin:
            return usuario.msp_id == entidad_msp_id
        
        # Condominio Admin y Admin Local
        return (
            usuario.msp_id == entidad_msp_id and
            usuario.condominio_id == entidad_condominio_id
        )
    
    @staticmethod
    def obtener_filtro_sql(usuario: ContextoUsuario, alias_tabla: str = "") -> Dict[str, Any]:
        """
        Genera filtros SQL para queries según el contexto del usuario
        
        Retorna un diccionario con los filtros a aplicar:
        - Super Admin: {} (sin filtros)
        - MSP Admin: {"msp_id": "xxx"}
        - Condominio/Local Admin: {"msp_id": "xxx", "condominio_id": "yyy"}
        """
        if usuario.es_super_admin:
            return {}
        
        filtros = {}
        
        if usuario.msp_id:
            filtros["msp_id"] = usuario.msp_id
        
        if usuario.condominio_id:
            filtros["condominio_id"] = usuario.condominio_id
        
        return filtros
    
    @staticmethod
    def obtener_where_clause(usuario: ContextoUsuario, alias_tabla: str = "") -> str:
        """
        Genera cláusula WHERE SQL según el contexto del usuario
        
        Args:
            usuario: Contexto del usuario
            alias_tabla: Alias de la tabla (ej: "a" para "a.msp_id")
        
        Returns:
            Cláusula WHERE sin el "WHERE" inicial
        """
        if usuario.es_super_admin:
            return "1=1"  # Sin restricciones
        
        prefix = f"{alias_tabla}." if alias_tabla else ""
        conditions = []
        
        if usuario.msp_id:
            conditions.append(f"{prefix}msp_id = '{usuario.msp_id}'")
        
        if usuario.condominio_id:
            conditions.append(f"{prefix}condominio_id = '{usuario.condominio_id}'")
        
        return " AND ".join(conditions) if conditions else "1=1"


class PermisoExo(Enum):
    """Permisos granulares del sistema"""
    # Gestión de MSPs
    VER_MSPS = "ver_msps"
    CREAR_MSP = "crear_msp"
    EDITAR_MSP = "editar_msp"
    ELIMINAR_MSP = "eliminar_msp"
    
    # Gestión de Condominios
    VER_CONDOMINIOS = "ver_condominios"
    CREAR_CONDOMINIO = "crear_condominio"
    EDITAR_CONDOMINIO = "editar_condominio"
    ELIMINAR_CONDOMINIO = "eliminar_condominio"
    
    # Gestión de Usuarios
    VER_USUARIOS = "ver_usuarios"
    CREAR_USUARIO = "crear_usuario"
    EDITAR_USUARIO = "editar_usuario"
    ELIMINAR_USUARIO = "eliminar_usuario"
    
    # Gestión de Residencias
    VER_RESIDENCIAS = "ver_residencias"
    CREAR_RESIDENCIA = "crear_residencia"
    EDITAR_RESIDENCIA = "editar_residencia"
    ELIMINAR_RESIDENCIA = "eliminar_residencia"
    
    # Gestión de Accesos
    VER_ACCESOS = "ver_accesos"
    REGISTRAR_ACCESO = "registrar_acceso"
    
    # Gestión de Visitantes
    VER_VISITANTES = "ver_visitantes"
    CREAR_VISITANTE = "crear_visitante"
    EDITAR_VISITANTE = "editar_visitante"
    ELIMINAR_VISITANTE = "eliminar_visitante"
    
    # Playbooks
    VER_PLAYBOOKS = "ver_playbooks"
    CREAR_PLAYBOOK = "crear_playbook"
    EDITAR_PLAYBOOK = "editar_playbook"
    
    # Auditoría
    VER_LEDGER = "ver_ledger"
    VER_REPORTES = "ver_reportes"


# Matriz de permisos por rol
PERMISOS_POR_ROL: Dict[RolExo, set[PermisoExo]] = {
    RolExo.SUPER_ADMIN: set(PermisoExo),  # Todos los permisos
    
    RolExo.MSP_ADMIN: {
        PermisoExo.VER_MSPS,
        PermisoExo.VER_CONDOMINIOS,
        PermisoExo.CREAR_CONDOMINIO,
        PermisoExo.EDITAR_CONDOMINIO,
        PermisoExo.VER_USUARIOS,
        PermisoExo.CREAR_USUARIO,
        PermisoExo.EDITAR_USUARIO,
        PermisoExo.VER_RESIDENCIAS,
        PermisoExo.VER_ACCESOS,
        PermisoExo.VER_VISITANTES,
        PermisoExo.VER_PLAYBOOKS,
        PermisoExo.VER_REPORTES,
        PermisoExo.VER_LEDGER,
    },
    
    RolExo.CONDOMINIO_ADMIN: {
        PermisoExo.VER_CONDOMINIOS,
        PermisoExo.EDITAR_CONDOMINIO,
        PermisoExo.VER_USUARIOS,
        PermisoExo.CREAR_USUARIO,
        PermisoExo.VER_RESIDENCIAS,
        PermisoExo.CREAR_RESIDENCIA,
        PermisoExo.EDITAR_RESIDENCIA,
        PermisoExo.VER_ACCESOS,
        PermisoExo.VER_VISITANTES,
        PermisoExo.CREAR_VISITANTE,
        PermisoExo.EDITAR_VISITANTE,
        PermisoExo.ELIMINAR_VISITANTE,
        PermisoExo.VER_REPORTES,
    },
    
    RolExo.ADMIN_LOCAL: {
        PermisoExo.VER_RESIDENCIAS,
        PermisoExo.VER_ACCESOS,
        PermisoExo.REGISTRAR_ACCESO,
        PermisoExo.VER_VISITANTES,
        PermisoExo.CREAR_VISITANTE,
    },
}


def tiene_permiso(usuario: ContextoUsuario, permiso: PermisoExo) -> bool:
    """Verifica si un usuario tiene un permiso específico"""
    permisos_rol = PERMISOS_POR_ROL.get(usuario.rol, set())
    return permiso in permisos_rol
