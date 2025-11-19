"""
ANALÍTICA AUP-EXO
Módulo de interpretación estructural:
- Comparación T-1 vs T0
- Detección de anomalías
- Patrones inusuales por entidad
- Actividad nocturna
- Etiquetado estructural de riesgo
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from core.db import get_db


# ===========================================================
# 1. Cargar eventos como DataFrame
# ===========================================================
def _get_eventos_df():
    """Obtiene eventos desde la vista eventos (sin JOIN problemático)"""
    with get_db() as db:
        rows = db.execute("""
            SELECT 
                e.evento_id, 
                e.entidad_id, 
                e.tipo_evento, 
                e.metadata,
                e.actor, 
                e.dispositivo, 
                e.timestamp_servidor,
                e.hash_actual,
                '' AS tipo_entidad,
                '{}' AS atributos
            FROM eventos e
            ORDER BY e.timestamp_servidor DESC
        """).fetchall()

    if not rows:
        return pd.DataFrame()

    data = []
    for r in rows:
        metadata = json.loads(r["metadata"]) if r["metadata"] else {}
        atributos = json.loads(r["atributos"]) if r["atributos"] else {}
        
        # Extraer nombre e identificador del JSON de atributos
        nombre = atributos.get("nombre", "N/A")
        identificador = (atributos.get("identificador") or 
                        atributos.get("placa") or 
                        atributos.get("folio") or "N/A")

        data.append({
            "evento_id": r["evento_id"],
            "entidad_id": r["entidad_id"],
            "tipo_evento": r["tipo_evento"],
            "nombre": nombre,
            "identificador": identificador,
            "tipo_entidad": r["tipo_entidad"],
            "actor": r["actor"],
            "dispositivo": r["dispositivo"],
            "hora": metadata.get("hora", ""),
            "fecha": metadata.get("fecha", ""),
            "timestamp": r["timestamp_servidor"],
            "motivo_rechazo": metadata.get("motivo_rechazo", ""),
            "hash": r["hash_actual"]
        })

    df = pd.DataFrame(data)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["hora_int"] = pd.to_numeric(df["hora"].str.slice(0, 2), errors="coerce")

    return df


# ===========================================================
# 2. Comparación T-1 vs T0
# ===========================================================
def comparar_t1_t0(df):
    if df.empty:
        return {}

    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)

    df_hoy = df[df["fecha"].dt.date == hoy]
    df_ayer = df[df["fecha"].dt.date == ayer]

    return {
        "entradas_hoy": df_hoy[df_hoy["tipo_evento"] == "entrada"].shape[0],
        "entradas_ayer": df_ayer[df_ayer["tipo_evento"] == "entrada"].shape[0],
        "rechazos_hoy": df_hoy[df_hoy["tipo_evento"] == "rechazo"].shape[0],
        "rechazos_ayer": df_ayer[df_ayer["tipo_evento"] == "rechazo"].shape[0],
        "variacion_entradas": _variacion(df_hoy, df_ayer, "entrada"),
        "variacion_rechazos": _variacion(df_hoy, df_ayer, "rechazo")
    }


def _variacion(df_hoy, df_ayer, tipo):
    h = df_hoy[df_hoy["tipo_evento"] == tipo].shape[0]
    a = df_ayer[df_ayer["tipo_evento"] == tipo].shape[0]
    if a == 0:
        return 100 if h > 0 else 0
    return round(((h - a) / a) * 100, 2)


# ===========================================================
# 3. Detección de anomalías básicas
# ===========================================================
def detectar_anomalias(df):
    if df.empty:
        return []

    anomalías = []

    # 3.1 Actividad nocturna
    nocturnos = df[df["hora_int"].between(0, 5)]
    if not nocturnos.empty:
        anomalías.append({
            "tipo": "actividad_nocturna",
            "descripcion": f"{len(nocturnos)} eventos entre 00:00 y 05:59",
            "nivel": "medio"
        })

    # 3.2 Rechazos repetidos por la misma entidad
    rechazos = df[df["tipo_evento"] == "rechazo"]
    multip_rech = rechazos["entidad_id"].value_counts()
    for entidad_id, count in multip_rech.items():
        if count >= 3:
            entidad = rechazos[rechazos["entidad_id"] == entidad_id].iloc[0]
            anomalías.append({
                "tipo": "rechazos_repetidos",
                "descripcion": f"La entidad {entidad['nombre']} tiene {count} rechazos.",
                "nivel": "alto"
            })

    # 3.3 Entradas demasiado frecuentes (patrón sospechoso)
    entradas = df[df["tipo_evento"] == "entrada"]
    counts = entradas["entidad_id"].value_counts()
    for entidad_id, count in counts.items():
        if count >= 10:  # Umbral simple; ajustable
            entidad = entradas[entradas["entidad_id"] == entidad_id].iloc[0]
            anomalías.append({
                "tipo": "actividad_extrema",
                "descripcion": f"Actividad inusual de la entidad {entidad['nombre']}: {count} entradas.",
                "nivel": "alto"
            })

    # 3.4 Patrones nuevos o atípicos (día atípico)
    hoy = datetime.now().date()
    entradas_hoy = df[(df["tipo_evento"] == "entrada") & (df["fecha"].dt.date == hoy)]
    entradas_rest = df[(df["tipo_evento"] == "entrada") & (df["fecha"].dt.date != hoy)]

    if not entradas_rest.empty:
        prom_historico = entradas_rest.shape[0] / max(1, entradas_rest["fecha"].dt.date.nunique())
        if entradas_hoy.shape[0] > prom_historico * 2:
            anomalías.append({
                "tipo": "pico_operativo",
                "descripcion": f"Hoy hay un pico inusual de accesos: {entradas_hoy.shape[0]} vs promedio histórico {round(prom_historico,2)}",
                "nivel": "medio"
            })

    return anomalías


# ===========================================================
# 4. Etiquetado estructural de riesgo
# ===========================================================
def etiquetar_eventos(df):
    if df.empty:
        return df

    df = df.copy()  # Evitar SettingWithCopyWarning
    df["etiqueta_riesgo"] = "normal"

    # Actividad nocturna
    df.loc[df["hora_int"].between(0, 5), "etiqueta_riesgo"] = "riesgo_medio"

    # Rechazos → riesgo alto
    df.loc[df["tipo_evento"] == "rechazo", "etiqueta_riesgo"] = "riesgo_alto"

    # Más de 5 eventos en un día → riesgo alto
    conteo_por_entidad = df["entidad_id"].value_counts()
    entidades_altas = conteo_por_entidad[conteo_por_entidad > 5].index
    df.loc[df["entidad_id"].isin(entidades_altas), "etiqueta_riesgo"] = "riesgo_alto"

    return df


# ===========================================================
# 5. Resumen estructural de analítica
# ===========================================================
def resumen_analitico():
    df = _get_eventos_df()

    if df.empty:
        return {
            "t1_t0": {},
            "anomalias": [],
            "df_etiquetado": pd.DataFrame()
        }

    t1_t0 = comparar_t1_t0(df)
    anomalías = detectar_anomalias(df)
    df_etq = etiquetar_eventos(df)

    return {
        "t1_t0": t1_t0,
        "anomalias": anomalías,
        "df_etiquetado": df_etq
    }
