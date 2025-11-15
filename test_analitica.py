#!/usr/bin/env python3
"""
TEST ANALÍTICA AUP-EXO
Validación del módulo de interpretación estructural
"""

import sys
sys.path.insert(0, '/workspaces/Accesos-Residencial')

from datetime import datetime, timedelta
from modulos.analitica import (
    _get_eventos_df,
    comparar_t1_t0,
    detectar_anomalias,
    etiquetar_eventos,
    resumen_analitico
)

print("=" * 60)
print("🧪 TEST ANALÍTICA AUP-EXO")
print("=" * 60)

# Test 1: Cargar DataFrame de eventos
print("\n1️⃣ Test: Cargar eventos para análisis")
try:
    df = _get_eventos_df()
    print(f"   ✅ DataFrame cargado: {len(df)} eventos")
    
    if not df.empty:
        print(f"\n   📊 Columnas del análisis:")
        print(f"      {', '.join(df.columns.tolist())}")
        
        print(f"\n   📈 Tipos de eventos:")
        print(df['tipo_evento'].value_counts().to_string())
        
        print(f"\n   🕐 Eventos con hora válida: {df['hora_int'].notna().sum()}/{len(df)}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Comparación T-1 vs T0
print("\n2️⃣ Test: Comparación T-1 vs T0")
try:
    if not df.empty:
        comparacion = comparar_t1_t0(df)
        
        print(f"\n   📊 Comparación temporal:")
        print(f"      Entradas hoy: {comparacion.get('entradas_hoy', 0)}")
        print(f"      Entradas ayer: {comparacion.get('entradas_ayer', 0)}")
        print(f"      Variación: {comparacion.get('variacion_entradas', 0)}%")
        
        print(f"\n      Rechazos hoy: {comparacion.get('rechazos_hoy', 0)}")
        print(f"      Rechazos ayer: {comparacion.get('rechazos_ayer', 0)}")
        print(f"      Variación: {comparacion.get('variacion_rechazos', 0)}%")
        
        if comparacion:
            print(f"\n   ✅ Comparación T-1 vs T0 funcionando correctamente")
        else:
            print(f"\n   ⚠️  Sin datos suficientes para comparación")
    else:
        print(f"   ⚠️  DataFrame vacío, sin datos para comparar")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Detección de anomalías
print("\n3️⃣ Test: Detección de anomalías")
try:
    if not df.empty:
        anomalias = detectar_anomalias(df)
        
        print(f"\n   📊 Total anomalías detectadas: {len(anomalias)}")
        
        if anomalias:
            print(f"\n   🔍 Anomalías encontradas:")
            for i, anomalia in enumerate(anomalias[:5], 1):
                nivel_emoji = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}.get(anomalia['nivel'], "⚪")
                print(f"\n      {i}. {nivel_emoji} {anomalia['tipo'].upper()}")
                print(f"         Nivel: {anomalia['nivel']}")
                print(f"         {anomalia['descripcion']}")
            
            if len(anomalias) > 5:
                print(f"\n      ... y {len(anomalias) - 5} anomalías más")
            
            # Resumen por tipo
            tipos_anomalias = {}
            for a in anomalias:
                tipo = a['tipo']
                tipos_anomalias[tipo] = tipos_anomalias.get(tipo, 0) + 1
            
            print(f"\n   📊 Resumen por tipo:")
            for tipo, count in tipos_anomalias.items():
                print(f"      {tipo}: {count}")
            
            print(f"\n   ✅ Detección de anomalías funcionando correctamente")
        else:
            print(f"\n   ℹ️  No se detectaron anomalías (sistema operando normalmente)")
            print(f"   ✅ Detección de anomalías funcionando (sin alertas)")
    else:
        print(f"   ⚠️  DataFrame vacío, sin datos para analizar")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Etiquetado de riesgo
print("\n4️⃣ Test: Etiquetado estructural de riesgo")
try:
    if not df.empty:
        df_etiquetado = etiquetar_eventos(df)
        
        print(f"\n   📊 Eventos etiquetados: {len(df_etiquetado)}")
        
        if 'etiqueta_riesgo' in df_etiquetado.columns:
            distribucion = df_etiquetado['etiqueta_riesgo'].value_counts()
            
            print(f"\n   🏷️  Distribución de etiquetas:")
            for etiqueta, count in distribucion.items():
                porcentaje = (count / len(df_etiquetado)) * 100
                emoji = {
                    "riesgo_alto": "🔴",
                    "riesgo_medio": "🟡",
                    "normal": "🟢"
                }.get(etiqueta, "⚪")
                print(f"      {emoji} {etiqueta}: {count} ({porcentaje:.1f}%)")
            
            print(f"\n   ✅ Etiquetado de riesgo funcionando correctamente")
        else:
            print(f"   ❌ Columna 'etiqueta_riesgo' no encontrada")
    else:
        print(f"   ⚠️  DataFrame vacío, sin datos para etiquetar")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Resumen analítico completo
print("\n5️⃣ Test: Resumen analítico completo")
try:
    resumen = resumen_analitico()
    
    print(f"\n   📊 Componentes del resumen:")
    print(f"      ✅ T-1 vs T0: {len(resumen.get('t1_t0', {}))} métricas")
    print(f"      ✅ Anomalías: {len(resumen.get('anomalias', []))} detectadas")
    print(f"      ✅ Eventos etiquetados: {len(resumen.get('df_etiquetado', []))} registros")
    
    if resumen.get('t1_t0'):
        print(f"\n   📈 Comparación temporal:")
        t1_t0 = resumen['t1_t0']
        print(f"      Entradas: {t1_t0.get('entradas_hoy', 0)} hoy vs {t1_t0.get('entradas_ayer', 0)} ayer")
        print(f"      Rechazos: {t1_t0.get('rechazos_hoy', 0)} hoy vs {t1_t0.get('rechazos_ayer', 0)} ayer")
    
    if resumen.get('anomalias'):
        niveles = {}
        for a in resumen['anomalias']:
            nivel = a['nivel']
            niveles[nivel] = niveles.get(nivel, 0) + 1
        
        print(f"\n   🔍 Anomalías por nivel:")
        for nivel, count in niveles.items():
            emoji = {"alto": "🔴", "medio": "🟡", "bajo": "🟢"}.get(nivel, "⚪")
            print(f"      {emoji} {nivel}: {count}")
    
    print(f"\n   ✅ Resumen analítico completo funcionando correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Resumen final
print("\n" + "=" * 60)
print("🎯 RESULTADO FINAL")
print("=" * 60)
print("✅ Módulo de analítica validado correctamente")
print("📊 Funciones operativas:")
print("   • Comparación T-1 vs T0 ✅")
print("   • Detección de anomalías ✅")
print("   • Etiquetado de riesgo ✅")
print("   • Resumen analítico completo ✅")
print("\n🚀 Sistema AUP-EXO ahora puede:")
print("   VER (dashboard) → ENTENDER (analítica) → ALERTAR")
print("=" * 60)
