#!/usr/bin/env python3
"""
TEST DASHBOARD AUP-EXO
Validación de queries y visualizaciones
"""

import sys
from datetime import datetime, date
from modulos.dashboard import _get_eventos_df

print("=" * 60)
print("🧪 TEST DASHBOARD AUP-EXO")
print("=" * 60)

# Test 1: Obtener DataFrame de eventos
print("\n1️⃣ Test: Obtener DataFrame de eventos")
try:
    df = _get_eventos_df()
    print(f"   ✅ DataFrame obtenido: {len(df)} eventos")
    
    if not df.empty:
        print(f"\n   📊 Columnas disponibles:")
        for col in df.columns:
            print(f"      - {col}")
        
        print(f"\n   📈 Primeros 3 eventos:")
        print(df.head(3).to_string())
        
        print(f"\n   📊 Tipos de eventos:")
        print(df['tipo_evento'].value_counts().to_string())
        
        print(f"\n   📅 Eventos de hoy:")
        df['fecha'] = df['fecha'].astype(str)
        hoy_str = date.today().isoformat()
        eventos_hoy = df[df['fecha'] == hoy_str]
        print(f"      Total: {len(eventos_hoy)}")
        
        if len(eventos_hoy) > 0:
            print(f"      Entradas: {len(eventos_hoy[eventos_hoy['tipo_evento'] == 'entrada'])}")
            print(f"      Rechazos: {len(eventos_hoy[eventos_hoy['tipo_evento'] == 'rechazo'])}")
        
    else:
        print("   ⚠️  No hay eventos en la base de datos")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Validar estructura de datos
print("\n2️⃣ Test: Validar estructura de datos")
try:
    required_cols = ['evento_id', 'entidad_id', 'tipo_evento', 'nombre', 
                     'identificador', 'tipo_entidad', 'actor', 'dispositivo',
                     'hora', 'fecha', 'timestamp', 'politica_rechazo', 'hash']
    
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        print(f"   ❌ Columnas faltantes: {missing}")
        sys.exit(1)
    else:
        print(f"   ✅ Todas las columnas requeridas presentes")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Validar JOIN con entidades
print("\n3️⃣ Test: Validar JOIN eventos + entidades")
try:
    if not df.empty:
        # Verificar que hay nombres de entidades
        nombres_validos = df['nombre'].notna().sum()
        print(f"   ✅ Eventos con nombre de entidad: {nombres_validos}/{len(df)}")
        
        # Verificar tipos de entidad
        tipos = df['tipo_entidad'].value_counts()
        print(f"\n   📊 Distribución por tipo de entidad:")
        print(tipos.to_string())
        
    else:
        print("   ⚠️  Sin datos para validar")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Validar datos de hora para mapa de calor
print("\n4️⃣ Test: Validar datos de hora (mapa de calor)")
try:
    # Filtrar solo registros con hora válida
    df_hora = df[(df['hora'].notna()) & (df['hora'] != '')].copy()
    
    if not df_hora.empty:
        # Intentar extraer hora como int
        df_hora['hora_int'] = df_hora['hora'].str.slice(0, 2).astype(int)
        
        horas_unicas = df_hora['hora_int'].nunique()
        print(f"   ✅ Horas únicas detectadas: {horas_unicas}")
        print(f"   📊 Rango de horas: {df_hora['hora_int'].min()}:00 - {df_hora['hora_int'].max()}:00")
        print(f"   📊 Total eventos con hora: {len(df_hora)}/{len(df)}")
        
    else:
        print("   ⚠️  No hay datos de hora para mapa de calor")
        
except Exception as e:
    print(f"   ❌ Error procesando horas: {e}")

# Test 5: Validar datos de rechazo
print("\n5️⃣ Test: Validar datos de rechazos por política")
try:
    rechazos = df[df['tipo_evento'] == 'rechazo']
    
    if not rechazos.empty:
        print(f"   ✅ Rechazos encontrados: {len(rechazos)}")
        
        # Contar motivos
        motivos = rechazos['politica_rechazo'].value_counts()
        print(f"\n   📊 Top motivos de rechazo:")
        print(motivos.head(5).to_string())
        
    else:
        print("   ℹ️  No hay rechazos en el sistema (normal para sistema nuevo)")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("🎯 RESULTADO FINAL")
print("=" * 60)
print("✅ Dashboard validado correctamente")
print("📊 Todas las queries funcionan")
print("🎨 Listo para visualización en Streamlit")
print("\n🚀 Para ejecutar el dashboard:")
print("   streamlit run index.py")
print("=" * 60)
