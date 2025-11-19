#!/usr/bin/env python3
"""
Script de Inicialización Rápida para Streamlit Cloud
Autor: B10sp4rt4n
Fecha: 2025-11-19

Este script inicializa la base de datos PostgreSQL en producción
con datos mínimos necesarios para comenzar.
"""

import os
import sys
from datetime import datetime

def init_streamlit_cloud_db():
    """Inicializa la base de datos para Streamlit Cloud"""
    
    print("="*70)
    print("INICIALIZACIÓN DE BASE DE DATOS - STREAMLIT CLOUD")
    print("="*70)
    
    # Importar después de prints para ver errores
    try:
        from core.db import get_db
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("   Asegúrate de estar en el directorio correcto")
        return False
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 1. Crear tablas si no existen
            print("\n1️⃣ Creando tablas...")
            
            # Tabla MSPs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS msps_exo (
                    id SERIAL PRIMARY KEY,
                    msp_id TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    ciudad TEXT,
                    estado_mx TEXT,
                    cp TEXT,
                    telefono TEXT,
                    email TEXT,
                    estado TEXT DEFAULT 'activo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("   ✅ Tabla msps_exo verificada")
            
            # Tabla Condominios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS condominios_exo (
                    id SERIAL PRIMARY KEY,
                    condominio_id TEXT UNIQUE NOT NULL,
                    msp_id TEXT NOT NULL REFERENCES msps_exo(msp_id),
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    ciudad TEXT,
                    estado_mx TEXT,
                    cp TEXT,
                    telefono TEXT,
                    email TEXT,
                    total_unidades INTEGER DEFAULT 0,
                    estado TEXT DEFAULT 'activo',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("   ✅ Tabla condominios_exo verificada")
            
            # Tabla Entidades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entidades (
                    id SERIAL PRIMARY KEY,
                    tipo TEXT,
                    nombre_completo TEXT,
                    identificacion TEXT,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    atributos TEXT,
                    hash_actual TEXT,
                    hash_previo TEXT,
                    msp_id TEXT REFERENCES msps_exo(msp_id),
                    condominio_id TEXT REFERENCES condominios_exo(condominio_id),
                    estado TEXT DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    nombre TEXT,
                    creado_en TIMESTAMP
                )
            """)
            print("   ✅ Tabla entidades verificada")
            
            conn.commit()
            
            # 2. Verificar si ya existen datos
            print("\n2️⃣ Verificando datos existentes...")
            cursor.execute("SELECT COUNT(*) FROM msps_exo")
            result = cursor.fetchone()
            msp_count = result[0] if isinstance(result, tuple) else result.get('count', 0)
            
            if msp_count > 0:
                print(f"   ℹ️  Base de datos ya tiene {msp_count} MSP(s)")
                print("   ✅ Inicialización completada (datos existentes)")
                return True
            
            # 3. Crear datos de ejemplo solo si está vacío
            print("\n3️⃣ Creando datos de ejemplo...")
            
            # MSP de ejemplo
            cursor.execute("""
                INSERT INTO msps_exo (msp_id, nombre, email, telefono, ciudad, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (msp_id) DO NOTHING
            """, (
                'MSP-DEMO-001',
                'Demo Security Services',
                'demo@ejemplo.com',
                '+52 55 1234 5678',
                'Ciudad de México',
                'activo'
            ))
            print("   ✅ MSP de ejemplo creado")
            
            # Condominio de ejemplo
            cursor.execute("""
                INSERT INTO condominios_exo 
                (condominio_id, msp_id, nombre, ciudad, total_unidades, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (condominio_id) DO NOTHING
            """, (
                'COND-DEMO-001',
                'MSP-DEMO-001',
                'Residencial Demo',
                'Ciudad de México',
                50,
                'activo'
            ))
            print("   ✅ Condominio de ejemplo creado")
            
            conn.commit()
            
            print("\n" + "="*70)
            print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            print("\n📋 Datos creados:")
            print("   - MSP: MSP-DEMO-001 (Demo Security Services)")
            print("   - Condominio: COND-DEMO-001 (Residencial Demo)")
            print("\n🚀 Siguiente paso:")
            print("   1. Abre la aplicación Streamlit")
            print("   2. Selecciona 'Super Admin' como rol")
            print("   3. Selecciona el MSP y Condominio demo")
            print("   4. Comienza a registrar entidades")
            print("\n" + "="*70 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_streamlit_cloud_db()
    sys.exit(0 if success else 1)
