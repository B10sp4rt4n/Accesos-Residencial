#!/usr/bin/env python3
"""
Script de Verificación de Conexión PostgreSQL
Autor: B10sp4rt4n
Fecha: 2025-11-19

Este script verifica a qué base de datos estás conectado y
muestra el schema para confirmar si es single-tenant o multi-tenant.
"""

import sys

def check_database_version():
    """Verifica la versión de la base de datos conectada"""
    
    print("\n" + "="*70)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("="*70)
    
    try:
        from core.db import get_db
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Obtener información de conexión
            print("\n1️⃣ Información de Conexión:")
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            pg_version = version[0] if isinstance(version, tuple) else version.get('version', 'Unknown')
            print(f"   PostgreSQL: {pg_version.split(',')[0]}")
            
            cursor.execute("SELECT current_database();")
            db_result = cursor.fetchone()
            current_db = db_result[0] if isinstance(db_result, tuple) else db_result.get('current_database', 'Unknown')
            print(f"   Database: {current_db}")
            
            cursor.execute("SELECT current_user;")
            user_result = cursor.fetchone()
            current_user = user_result[0] if isinstance(user_result, tuple) else user_result.get('current_user', 'Unknown')
            print(f"   User: {current_user}")
            
            # Verificar tablas existentes
            print("\n2️⃣ Tablas Existentes:")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            table_names = []
            for table in tables:
                table_name = table[0] if isinstance(table, tuple) else table.get('table_name')
                table_names.append(table_name)
                print(f"   - {table_name}")
            
            # Determinar versión
            print("\n3️⃣ Tipo de Schema Detectado:")
            
            has_msps = 'msps_exo' in table_names
            has_condominios = 'condominios_exo' in table_names
            has_entidades = 'entidades' in table_names
            
            if has_msps and has_condominios:
                print("   🎯 MULTI-TENANT")
                print("   Tablas multi-tenant detectadas:")
                print("   ✅ msps_exo")
                print("   ✅ condominios_exo")
                
                # Verificar columnas en entidades
                if has_entidades:
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'entidades'
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    column_names = [col[0] if isinstance(col, tuple) else col.get('column_name') for col in columns]
                    
                    if 'msp_id' in column_names and 'condominio_id' in column_names:
                        print("   ✅ entidades tiene columnas multi-tenant (msp_id, condominio_id)")
                    else:
                        print("   ⚠️  entidades existe pero NO tiene columnas multi-tenant")
                        print("   ❌ Schema inconsistente detectado!")
                
                # Mostrar conteo de datos
                print("\n4️⃣ Datos en la Base:")
                if has_msps:
                    cursor.execute("SELECT COUNT(*) FROM msps_exo")
                    result = cursor.fetchone()
                    msp_count = result[0] if isinstance(result, tuple) else result.get('count', 0)
                    print(f"   MSPs: {msp_count}")
                
                if has_condominios:
                    cursor.execute("SELECT COUNT(*) FROM condominios_exo")
                    result = cursor.fetchone()
                    condo_count = result[0] if isinstance(result, tuple) else result.get('count', 0)
                    print(f"   Condominios: {condo_count}")
                
                if has_entidades:
                    cursor.execute("SELECT COUNT(*) FROM entidades")
                    result = cursor.fetchone()
                    ent_count = result[0] if isinstance(result, tuple) else result.get('count', 0)
                    print(f"   Entidades: {ent_count}")
                
            elif has_entidades and not has_msps:
                print("   📦 SINGLE-TENANT")
                print("   Tablas single-tenant detectadas:")
                print("   ✅ entidades (sin msp_id/condominio_id)")
                
                # Verificar que NO tenga columnas multi-tenant
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'entidades'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                column_names = [col[0] if isinstance(col, tuple) else col.get('column_name') for col in columns]
                
                if 'msp_id' in column_names or 'condominio_id' in column_names:
                    print("   ⚠️  ADVERTENCIA: Tiene columnas multi-tenant pero no tiene tablas msps_exo/condominios_exo")
                    print("   ❌ Schema inconsistente!")
                else:
                    print("   ✅ Schema single-tenant consistente")
                
                # Mostrar conteo
                print("\n4️⃣ Datos en la Base:")
                cursor.execute("SELECT COUNT(*) FROM entidades")
                result = cursor.fetchone()
                ent_count = result[0] if isinstance(result, tuple) else result.get('count', 0)
                print(f"   Entidades: {ent_count}")
            
            else:
                print("   ❓ INDETERMINADO")
                print("   ⚠️  No se pudieron determinar las tablas del schema")
            
            print("\n" + "="*70)
            print("✅ VERIFICACIÓN COMPLETADA")
            print("="*70 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_database_version()
    sys.exit(0 if success else 1)
