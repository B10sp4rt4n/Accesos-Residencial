"""
Test standalone de AUP-EXO sin dependencias
"""

import sys
sys.path.insert(0, '/workspaces/Accesos-Residencial')

# Import directo sin pasar por __init__
from core.exo_hierarchy import (
    ContextoUsuario,
    RolExo,
    ControlAccesoExo,
    PermisoExo,
    tiene_permiso
)


def test_super_admin():
    print("\n" + "="*60)
    print("TEST: Super Admin")
    print("="*60)
    
    super_admin = ContextoUsuario(
        usuario_id="SA-001",
        nombre="Salvador Rodriguez",
        email="salvador@axs.com",
        rol=RolExo.SUPER_ADMIN
    )
    
    print(f"✓ Usuario: {super_admin.nombre}")
    print(f"✓ Rol: {super_admin.rol.nombre_rol}")
    print(f"✓ Nivel: {super_admin.nivel_acceso.name} ({super_admin.nivel_acceso.value})")
    print(f"✓ Es Super Admin: {super_admin.es_super_admin}")
    print(f"✓ MSP ID: {super_admin.msp_id}")
    print(f"✓ Condominio ID: {super_admin.condominio_id}")
    
    # Permisos
    assert tiene_permiso(super_admin, PermisoExo.CREAR_MSP), "Debería poder crear MSP"
    assert tiene_permiso(super_admin, PermisoExo.VER_LEDGER), "Debería poder ver ledger"
    print("✓ Permisos verificados")
    
    # Accesos
    assert ControlAccesoExo.puede_acceder_msp(super_admin, "MSP-001"), "Debería acceder a cualquier MSP"
    assert ControlAccesoExo.puede_acceder_condominio(super_admin, "MSP-001", "COND-001"), "Debería acceder a cualquier condominio"
    print("✓ Control de acceso verificado")
    
    # Filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(super_admin)
    assert filtro == "1=1", "Filtro debería ser sin restricciones"
    print(f"✓ Filtro SQL: {filtro}")


def test_msp_admin():
    print("\n" + "="*60)
    print("TEST: MSP Admin")
    print("="*60)
    
    msp_admin = ContextoUsuario(
        usuario_id="MSPA-001",
        nombre="Juan Pérez",
        email="juan@msp.com",
        rol=RolExo.MSP_ADMIN,
        msp_id="MSP-001"
    )
    
    print(f"✓ Usuario: {msp_admin.nombre}")
    print(f"✓ Rol: {msp_admin.rol.nombre_rol}")
    print(f"✓ Nivel: {msp_admin.nivel_acceso.name} ({msp_admin.nivel_acceso.value})")
    print(f"✓ Es MSP Admin: {msp_admin.es_msp_admin}")
    print(f"✓ MSP ID: {msp_admin.msp_id}")
    print(f"✓ Condominio ID: {msp_admin.condominio_id}")
    
    # Permisos
    assert not tiene_permiso(msp_admin, PermisoExo.CREAR_MSP), "NO debería poder crear MSP"
    assert tiene_permiso(msp_admin, PermisoExo.CREAR_CONDOMINIO), "Debería poder crear condominios"
    assert tiene_permiso(msp_admin, PermisoExo.VER_REPORTES), "Debería poder ver reportes"
    print("✓ Permisos verificados")
    
    # Accesos
    assert ControlAccesoExo.puede_acceder_msp(msp_admin, "MSP-001"), "Debería acceder a su MSP"
    assert not ControlAccesoExo.puede_acceder_msp(msp_admin, "MSP-999"), "NO debería acceder a otro MSP"
    assert ControlAccesoExo.puede_acceder_condominio(msp_admin, "MSP-001", "COND-001"), "Debería acceder a condominios de su MSP"
    print("✓ Control de acceso verificado")
    
    # Filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(msp_admin)
    assert "msp_id = 'MSP-001'" in filtro, "Filtro debería incluir msp_id"
    print(f"✓ Filtro SQL: {filtro}")


def test_condominio_admin():
    print("\n" + "="*60)
    print("TEST: Condominio Admin")
    print("="*60)
    
    condo_admin = ContextoUsuario(
        usuario_id="CA-001",
        nombre="María González",
        email="maria@condo.com",
        rol=RolExo.CONDOMINIO_ADMIN,
        msp_id="MSP-001",
        condominio_id="COND-001"
    )
    
    print(f"✓ Usuario: {condo_admin.nombre}")
    print(f"✓ Rol: {condo_admin.rol.nombre_rol}")
    print(f"✓ Nivel: {condo_admin.nivel_acceso.name} ({condo_admin.nivel_acceso.value})")
    print(f"✓ Es Condominio Admin: {condo_admin.es_condominio_admin}")
    print(f"✓ MSP ID: {condo_admin.msp_id}")
    print(f"✓ Condominio ID: {condo_admin.condominio_id}")
    
    # Permisos
    assert not tiene_permiso(condo_admin, PermisoExo.CREAR_CONDOMINIO), "NO debería poder crear condominios"
    assert tiene_permiso(condo_admin, PermisoExo.CREAR_RESIDENCIA), "Debería poder crear residencias"
    assert tiene_permiso(condo_admin, PermisoExo.CREAR_VISITANTE), "Debería poder crear visitantes"
    print("✓ Permisos verificados")
    
    # Accesos
    assert ControlAccesoExo.puede_acceder_condominio(condo_admin, "MSP-001", "COND-001"), "Debería acceder a su condominio"
    assert not ControlAccesoExo.puede_acceder_condominio(condo_admin, "MSP-001", "COND-999"), "NO debería acceder a otro condominio"
    print("✓ Control de acceso verificado")
    
    # Filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(condo_admin)
    assert "msp_id = 'MSP-001'" in filtro and "condominio_id = 'COND-001'" in filtro, "Filtro debería incluir msp_id y condominio_id"
    print(f"✓ Filtro SQL: {filtro}")


def test_admin_local():
    print("\n" + "="*60)
    print("TEST: Admin Local")
    print("="*60)
    
    admin_local = ContextoUsuario(
        usuario_id="AL-001",
        nombre="Pedro Guardia",
        email="pedro@condo.com",
        rol=RolExo.ADMIN_LOCAL,
        msp_id="MSP-001",
        condominio_id="COND-001"
    )
    
    print(f"✓ Usuario: {admin_local.nombre}")
    print(f"✓ Rol: {admin_local.rol.nombre_rol}")
    print(f"✓ Nivel: {admin_local.nivel_acceso.name} ({admin_local.nivel_acceso.value})")
    print(f"✓ Es Admin Local: {admin_local.es_admin_local}")
    print(f"✓ MSP ID: {admin_local.msp_id}")
    print(f"✓ Condominio ID: {admin_local.condominio_id}")
    
    # Permisos
    assert not tiene_permiso(admin_local, PermisoExo.CREAR_RESIDENCIA), "NO debería poder crear residencias"
    assert tiene_permiso(admin_local, PermisoExo.REGISTRAR_ACCESO), "Debería poder registrar accesos"
    assert tiene_permiso(admin_local, PermisoExo.CREAR_VISITANTE), "Debería poder crear visitantes"
    assert not tiene_permiso(admin_local, PermisoExo.VER_LEDGER), "NO debería ver ledger"
    print("✓ Permisos verificados")
    
    # Accesos
    assert not ControlAccesoExo.puede_crear_usuario(admin_local, RolExo.ADMIN_LOCAL), "NO debería poder crear usuarios"
    print("✓ Control de acceso verificado")
    
    # Filtro SQL
    filtro = ControlAccesoExo.obtener_where_clause(admin_local)
    print(f"✓ Filtro SQL: {filtro}")


def test_validaciones():
    print("\n" + "="*60)
    print("TEST: Validaciones de Coherencia")
    print("="*60)
    
    # Test 1: Super Admin con msp_id (debería fallar)
    try:
        bad_super = ContextoUsuario(
            usuario_id="SA-BAD",
            nombre="Bad Super",
            email="bad@test.com",
            rol=RolExo.SUPER_ADMIN,
            msp_id="MSP-001"  # Esto está mal
        )
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        print(f"✓ Validación 1 OK: {str(e)}")
    
    # Test 2: MSP Admin sin msp_id (debería fallar)
    try:
        bad_msp = ContextoUsuario(
            usuario_id="MSPA-BAD",
            nombre="Bad MSP",
            email="bad@test.com",
            rol=RolExo.MSP_ADMIN
            # Falta msp_id
        )
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        print(f"✓ Validación 2 OK: {str(e)}")
    
    # Test 3: Condominio Admin sin condominio_id (debería fallar)
    try:
        bad_condo = ContextoUsuario(
            usuario_id="CA-BAD",
            nombre="Bad Condo",
            email="bad@test.com",
            rol=RolExo.CONDOMINIO_ADMIN,
            msp_id="MSP-001"
            # Falta condominio_id
        )
        assert False, "Debería haber lanzado ValueError"
    except ValueError as e:
        print(f"✓ Validación 3 OK: {str(e)}")


def test_jerarquia_creacion_usuarios():
    print("\n" + "="*60)
    print("TEST: Jerarquía de Creación de Usuarios")
    print("="*60)
    
    super_admin = ContextoUsuario("SA-001", "Super", "s@a.com", RolExo.SUPER_ADMIN)
    msp_admin = ContextoUsuario("MSPA-001", "MSP", "m@a.com", RolExo.MSP_ADMIN, msp_id="MSP-001")
    condo_admin = ContextoUsuario("CA-001", "Condo", "c@a.com", RolExo.CONDOMINIO_ADMIN, msp_id="MSP-001", condominio_id="COND-001")
    admin_local = ContextoUsuario("AL-001", "Local", "l@a.com", RolExo.ADMIN_LOCAL, msp_id="MSP-001", condominio_id="COND-001")
    
    # Super Admin puede crear todos
    for rol in [RolExo.SUPER_ADMIN, RolExo.MSP_ADMIN, RolExo.CONDOMINIO_ADMIN, RolExo.ADMIN_LOCAL]:
        assert ControlAccesoExo.puede_crear_usuario(super_admin, rol), f"Super Admin debería poder crear {rol.nombre_rol}"
    print("✓ Super Admin puede crear todos los roles")
    
    # MSP Admin puede crear Condominio Admin y Admin Local
    assert not ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.SUPER_ADMIN)
    assert not ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.MSP_ADMIN)
    assert ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.CONDOMINIO_ADMIN)
    assert ControlAccesoExo.puede_crear_usuario(msp_admin, RolExo.ADMIN_LOCAL)
    print("✓ MSP Admin puede crear Condominio Admin y Admin Local")
    
    # Condominio Admin solo puede crear Admin Local
    assert ControlAccesoExo.puede_crear_usuario(condo_admin, RolExo.ADMIN_LOCAL)
    assert not ControlAccesoExo.puede_crear_usuario(condo_admin, RolExo.CONDOMINIO_ADMIN)
    print("✓ Condominio Admin solo puede crear Admin Local")
    
    # Admin Local no puede crear nadie
    for rol in [RolExo.SUPER_ADMIN, RolExo.MSP_ADMIN, RolExo.CONDOMINIO_ADMIN, RolExo.ADMIN_LOCAL]:
        assert not ControlAccesoExo.puede_crear_usuario(admin_local, rol), f"Admin Local NO debería poder crear {rol.nombre_rol}"
    print("✓ Admin Local no puede crear usuarios")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*8 + "AX-S AUP-EXO - TESTS DE JERARQUÍA" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_super_admin()
        test_msp_admin()
        test_condominio_admin()
        test_admin_local()
        test_validaciones()
        test_jerarquia_creacion_usuarios()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}\n")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
