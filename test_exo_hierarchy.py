"""
AX-S - AUP-EXO Example Usage
Ejemplos de uso del sistema multi-tenant jerárquico
"""

from core.exo_hierarchy import (
    ContextoUsuario,
    RolExo,
    ControlAccesoExo,
    PermisoExo,
    tiene_permiso
)
from core.db_exo import db_exo


def ejemplo_super_admin():
    """Ejemplo de operaciones como Super Admin (DS)"""
    print("\n" + "="*60)
    print("EJEMPLO: Super Admin (Dominio Superior - DS)")
    print("="*60)
    
    # Crear contexto de Super Admin
    super_admin = ContextoUsuario(
        usuario_id="SA-20251118-001",
        nombre="Salvador Rodriguez",
        email="salvador@axs.com",
        rol=RolExo.SUPER_ADMIN
    )
    
    print(f"\nUsuario: {super_admin.nombre}")
    print(f"Rol: {super_admin.rol.nombre_rol}")
    print(f"Nivel: {super_admin.nivel_acceso.name} ({super_admin.nivel_acceso.value})")
    print(f"MSP ID: {super_admin.msp_id}")
    print(f"Condominio ID: {super_admin.condominio_id}")
    
    # Verificar permisos
    print("\n--- Permisos ---")
    print(f"¿Puede crear MSP? {tiene_permiso(super_admin, PermisoExo.CREAR_MSP)}")
    print(f"¿Puede ver playbooks? {tiene_permiso(super_admin, PermisoExo.VER_PLAYBOOKS)}")
    print(f"¿Puede ver ledger? {tiene_permiso(super_admin, PermisoExo.VER_LEDGER)}")
    
    # Verificar accesos
    print("\n--- Control de Acceso ---")
    print(f"¿Puede acceder a MSP-001? {ControlAccesoExo.puede_acceder_msp(super_admin, 'MSP-001')}")
    print(f"¿Puede acceder a cualquier condominio? {ControlAccesoExo.puede_acceder_condominio(super_admin, 'MSP-001', 'COND-001')}")
    print(f"¿Puede crear MSP Admin? {ControlAccesoExo.puede_crear_usuario(super_admin, RolExo.MSP_ADMIN)}")
    
    # Obtener filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(super_admin)
    print(f"\nFiltro SQL: {filtro}")


def ejemplo_msp_admin():
    """Ejemplo de operaciones como MSP Admin (DD)"""
    print("\n" + "="*60)
    print("EJEMPLO: MSP Admin (Dominio Delegado - DD)")
    print("="*60)
    
    # Crear contexto de MSP Admin
    msp_admin = ContextoUsuario(
        usuario_id="MSPA-20251118-002",
        nombre="Juan Pérez",
        email="juan@msp-seguridad.com",
        rol=RolExo.MSP_ADMIN,
        msp_id="MSP-20251118-001"
    )
    
    print(f"\nUsuario: {msp_admin.nombre}")
    print(f"Rol: {msp_admin.rol.nombre_rol}")
    print(f"Nivel: {msp_admin.nivel_acceso.name} ({msp_admin.nivel_acceso.value})")
    print(f"MSP ID: {msp_admin.msp_id}")
    print(f"Condominio ID: {msp_admin.condominio_id}")
    
    # Verificar permisos
    print("\n--- Permisos ---")
    print(f"¿Puede crear MSP? {tiene_permiso(msp_admin, PermisoExo.CREAR_MSP)}")
    print(f"¿Puede crear condominio? {tiene_permiso(msp_admin, PermisoExo.CREAR_CONDOMINIO)}")
    print(f"¿Puede ver reportes? {tiene_permiso(msp_admin, PermisoExo.VER_REPORTES)}")
    
    # Verificar accesos
    print("\n--- Control de Acceso ---")
    print(f"¿Puede acceder a su MSP (MSP-20251118-001)? {ControlAccesoExo.puede_acceder_msp(msp_admin, 'MSP-20251118-001')}")
    print(f"¿Puede acceder a otro MSP (MSP-999)? {ControlAccesoExo.puede_acceder_msp(msp_admin, 'MSP-999')}")
    print(f"¿Puede acceder a condominio de su MSP? {ControlAccesoExo.puede_acceder_condominio(msp_admin, 'MSP-20251118-001', 'COND-001')}")
    print(f"¿Puede crear Condominio Admin? {ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.CONDOMINIO_ADMIN)}")
    print(f"¿Puede crear Super Admin? {ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.SUPER_ADMIN)}")
    
    # Obtener filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(msp_admin)
    print(f"\nFiltro SQL: {filtro}")


def ejemplo_condominio_admin():
    """Ejemplo de operaciones como Condominio Admin (SE)"""
    print("\n" + "="*60)
    print("EJEMPLO: Condominio Admin (Subdominio Específico - SE)")
    print("="*60)
    
    # Crear contexto de Condominio Admin
    condo_admin = ContextoUsuario(
        usuario_id="CA-20251118-003",
        nombre="María González",
        email="maria@residencial-lagos.com",
        rol=RolExo.CONDOMINIO_ADMIN,
        msp_id="MSP-20251118-001",
        condominio_id="COND-20251118-001"
    )
    
    print(f"\nUsuario: {condo_admin.nombre}")
    print(f"Rol: {condo_admin.rol.nombre_rol}")
    print(f"Nivel: {condo_admin.nivel_acceso.name} ({condo_admin.nivel_acceso.value})")
    print(f"MSP ID: {condo_admin.msp_id}")
    print(f"Condominio ID: {condo_admin.condominio_id}")
    
    # Verificar permisos
    print("\n--- Permisos ---")
    print(f"¿Puede crear condominio? {tiene_permiso(condo_admin, PermisoExo.CREAR_CONDOMINIO)}")
    print(f"¿Puede crear residencia? {tiene_permiso(condo_admin, PermisoExo.CREAR_RESIDENCIA)}")
    print(f"¿Puede crear visitante? {tiene_permiso(condo_admin, PermisoExo.CREAR_VISITANTE)}")
    print(f"¿Puede ver ledger? {tiene_permiso(condo_admin, PermisoExo.VER_LEDGER)}")
    
    # Verificar accesos
    print("\n--- Control de Acceso ---")
    print(f"¿Puede acceder a su condominio? {ControlAccesoExo.puede_acceder_condominio(condo_admin, 'MSP-20251118-001', 'COND-20251118-001')}")
    print(f"¿Puede acceder a otro condominio? {ControlAccesoExo.puede_acceder_condominio(condo_admin, 'MSP-20251118-001', 'COND-999')}")
    print(f"¿Puede crear Admin Local? {ControlAccesoExo.puede_crear_usuario(condo_admin, RolExo.ADMIN_LOCAL)}")
    print(f"¿Puede crear MSP Admin? {ControlAccesoExo.puede_crear_usuario(condo_admin, RolExo.MSP_ADMIN)}")
    
    # Obtener filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(condo_admin)
    print(f"\nFiltro SQL: {filtro}")


def ejemplo_admin_local():
    """Ejemplo de operaciones como Admin Local (NO)"""
    print("\n" + "="*60)
    print("EJEMPLO: Admin Local (Nodo Operativo - NO)")
    print("="*60)
    
    # Crear contexto de Admin Local
    admin_local = ContextoUsuario(
        usuario_id="AL-20251118-004",
        nombre="Pedro Ramírez",
        email="pedro.guardia@residencial-lagos.com",
        rol=RolExo.ADMIN_LOCAL,
        msp_id="MSP-20251118-001",
        condominio_id="COND-20251118-001"
    )
    
    print(f"\nUsuario: {admin_local.nombre}")
    print(f"Rol: {admin_local.rol.nombre_rol}")
    print(f"Nivel: {admin_local.nivel_acceso.name} ({admin_local.nivel_acceso.value})")
    print(f"MSP ID: {admin_local.msp_id}")
    print(f"Condominio ID: {admin_local.condominio_id}")
    
    # Verificar permisos
    print("\n--- Permisos ---")
    print(f"¿Puede crear residencia? {tiene_permiso(admin_local, PermisoExo.CREAR_RESIDENCIA)}")
    print(f"¿Puede registrar acceso? {tiene_permiso(admin_local, PermisoExo.REGISTRAR_ACCESO)}")
    print(f"¿Puede ver visitantes? {tiene_permiso(admin_local, PermisoExo.VER_VISITANTES)}")
    print(f"¿Puede crear visitante? {tiene_permiso(admin_local, PermisoExo.CREAR_VISITANTE)}")
    print(f"¿Puede ver ledger? {tiene_permiso(admin_local, PermisoExo.VER_LEDGER)}")
    
    # Verificar accesos
    print("\n--- Control de Acceso ---")
    print(f"¿Puede acceder a su condominio? {ControlAccesoExo.puede_acceder_condominio(admin_local, 'MSP-20251118-001', 'COND-20251118-001')}")
    print(f"¿Puede crear usuarios? {ControlAccesoExo.puede_crear_usuario(admin_local, RolExo.ADMIN_LOCAL)}")
    
    # Obtener filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(admin_local)
    print(f"\nFiltro SQL: {filtro}")


def ejemplo_comparacion_roles():
    """Comparación de capacidades entre roles"""
    print("\n" + "="*60)
    print("COMPARACIÓN DE ROLES")
    print("="*60)
    
    # Crear contextos
    super_admin = ContextoUsuario(
        usuario_id="SA-001", nombre="Super", email="super@axs.com",
        rol=RolExo.SUPER_ADMIN
    )
    
    msp_admin = ContextoUsuario(
        usuario_id="MSPA-001", nombre="MSP Admin", email="msp@test.com",
        rol=RolExo.MSP_ADMIN, msp_id="MSP-001"
    )
    
    condo_admin = ContextoUsuario(
        usuario_id="CA-001", nombre="Condo Admin", email="condo@test.com",
        rol=RolExo.CONDOMINIO_ADMIN, msp_id="MSP-001", condominio_id="COND-001"
    )
    
    admin_local = ContextoUsuario(
        usuario_id="AL-001", nombre="Local Admin", email="local@test.com",
        rol=RolExo.ADMIN_LOCAL, msp_id="MSP-001", condominio_id="COND-001"
    )
    
    # Tabla de comparación
    roles = [
        ("Super Admin", super_admin),
        ("MSP Admin", msp_admin),
        ("Condominio Admin", condo_admin),
        ("Admin Local", admin_local)
    ]
    
    permisos_clave = [
        PermisoExo.CREAR_MSP,
        PermisoExo.CREAR_CONDOMINIO,
        PermisoExo.CREAR_USUARIO,
        PermisoExo.CREAR_RESIDENCIA,
        PermisoExo.REGISTRAR_ACCESO,
        PermisoExo.VER_LEDGER,
    ]
    
    print(f"\n{'Permiso':<25} | {'Super':<6} | {'MSP':<6} | {'Condo':<6} | {'Local':<6}")
    print("-" * 70)
    
    for permiso in permisos_clave:
        nombre_permiso = permiso.value.replace("_", " ").title()
        resultados = [
            "✓" if tiene_permiso(ctx, permiso) else "✗"
            for _, ctx in roles
        ]
        print(f"{nombre_permiso:<25} | {resultados[0]:^6} | {resultados[1]:^6} | {resultados[2]:^6} | {resultados[3]:^6}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AX-S AUP-EXO - EJEMPLOS DE USO" + " "*17 + "║")
    print("║" + " "*6 + "Sistema Multi-Tenant Jerárquico" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        ejemplo_super_admin()
        ejemplo_msp_admin()
        ejemplo_condominio_admin()
        ejemplo_admin_local()
        ejemplo_comparacion_roles()
        
        print("\n" + "="*60)
        print("✓ Todos los ejemplos ejecutados correctamente")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
