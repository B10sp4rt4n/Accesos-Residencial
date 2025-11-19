#!/usr/bin/env python3
"""
Script de Verificación de Autoría - AX-S
Autor: B10sp4rt4n
Fecha: 2025-11-19

Este script verifica la autenticidad de las versiones Multi-Tenant y Single-Tenant
del sistema AX-S mediante hashes SHA-256.
"""

import hashlib
import sys

def verify_hash(content, expected_hash, version):
    """
    Verifica el hash SHA-256 de una versión
    
    Args:
        content (str): Contenido a hashear
        expected_hash (str): Hash esperado
        version (str): Nombre de la versión
    
    Returns:
        bool: True si el hash coincide, False en caso contrario
    """
    calculated_hash = hashlib.sha256(content.encode()).hexdigest()
    
    print(f"\n{'='*70}")
    print(f"Verificando: {version}")
    print(f"{'='*70}")
    print(f"Hash Esperado:  {expected_hash}")
    print(f"Hash Calculado: {calculated_hash}")
    
    if calculated_hash == expected_hash:
        print("✅ VERIFICACIÓN EXITOSA - Hash coincide")
        return True
    else:
        print("❌ VERIFICACIÓN FALLIDA - Hash NO coincide")
        print("\n⚠️  ADVERTENCIA: El código puede haber sido modificado")
        print("    Contacte al autor original: @B10sp4rt4n")
        return False

def main():
    """Función principal de verificación"""
    
    print("\n" + "="*70)
    print("VERIFICACIÓN DE AUTORÍA - SISTEMA AX-S")
    print("="*70)
    print("Autor: B10sp4rt4n")
    print("Repositorio: github.com/B10sp4rt4n/Accesos-Residencial")
    print("Fecha: 2025-11-19")
    
    # Definir contenidos y hashes esperados
    versions = {
        "Multi-Tenant v2.0.0": {
            "content": "AX-S v2.0.0-multitenant|B10sp4rt4n|2025-11-19|feature/multi-tenant-fixes|commits:dbb74e2,e3fc415,8c36395,e72f5a0,fa4336c",
            "hash": "82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06"
        },
        "Single-Tenant v1.0.0": {
            "content": "AX-S v1.0.0-stable|B10sp4rt4n|2025-11-19|main|SQLite+PostgreSQL|Streamlit",
            "hash": "56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0"
        }
    }
    
    # Verificar todas las versiones
    results = {}
    for version_name, version_data in versions.items():
        results[version_name] = verify_hash(
            version_data["content"],
            version_data["hash"],
            version_name
        )
    
    # Resultado final
    print(f"\n{'='*70}")
    print("RESULTADO FINAL DE VERIFICACIÓN")
    print(f"{'='*70}")
    
    all_valid = True
    for version_name, is_valid in results.items():
        status = "✅ VÁLIDO" if is_valid else "❌ INVÁLIDO"
        print(f"{version_name}: {status}")
        if not is_valid:
            all_valid = False
    
    print(f"{'='*70}\n")
    
    if all_valid:
        print("🎉 Todas las verificaciones fueron exitosas")
        print("   El código es auténtico y no ha sido alterado\n")
        return 0
    else:
        print("⚠️  ADVERTENCIA: Algunas verificaciones fallaron")
        print("   El código puede haber sido modificado sin autorización")
        print("   Contacte al autor: @B10sp4rt4n en GitHub\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
