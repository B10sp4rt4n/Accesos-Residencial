# core/motor_reglas.py
"""
Motor de reglas (POLÍTICAS) – AUP-EXO
Evalúa si una entidad puede acceder según las políticas configuradas.
"""

import json
from datetime import datetime, time
from core.db import get_db


def _hora_en_rango(hora_str, desde_str, hasta_str):
    """
    Verifica si una hora está dentro de un rango [desde, hasta].
    Formato esperado: 'HH:MM'
    """
    try:
        h = datetime.strptime(hora_str, "%H:%M").time()
        desde = datetime.strptime(desde_str, "%H:%M").time()
        hasta = datetime.strptime(hasta_str, "%H:%M").time()
    except Exception:
        # Si hay error de formato, no bloqueamos por horario
        return True

    # Caso simple sin pasar por medianoche
    if desde <= hasta:
        return desde <= h <= hasta
    # Caso donde el rango cruza medianoche
    return h >= desde or h <= hasta


def _contar_visitas_hoy(entidad_id, fecha_str):
    """
    Cuenta cuántas veces ha tenido eventos de 'entrada' la entidad
    en la fecha indicada (YYYY-MM-DD).
    """
    with get_db() as db:
        rows = db.execute("""
            SELECT COUNT(*) as total
            FROM eventos
            WHERE entidad_id = ?
              AND tipo_evento = 'entrada'
              AND DATE(timestamp_servidor) = DATE(?)
        """, (entidad_id, fecha_str)).fetchone()

    return rows["total"] if rows else 0


def _obtener_entidad(entidad_id):
    with get_db() as db:
        row = db.execute("""
            SELECT * FROM entidades WHERE entidad_id = ?
        """, (entidad_id,)).fetchone()
    return dict(row) if row else None


def _obtener_politicas_activas():
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM politicas
            WHERE estado = 'activa'
            ORDER BY prioridad ASC
        """).fetchall()
    return [dict(r) for r in rows]


def evaluar_reglas(entidad_id, metadata):
    """
    Evalúa las políticas activas para la entidad y contexto dados.

    Devuelve:
        {
            "permitido": True/False,
            "motivo": str o None,
            "politica_aplicada": str o None
        }
    """
    entidad = _obtener_entidad(entidad_id)
    if not entidad:
        return {
            "permitido": False,
            "motivo": "Entidad no encontrada.",
            "politica_aplicada": None
        }

    # Parsear atributos JSON de la entidad
    try:
        atributos = json.loads(entidad.get("atributos", "{}"))
    except json.JSONDecodeError:
        atributos = {}

    tipo_entidad = entidad.get("tipo")
    fecha = metadata.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    hora = metadata.get("hora", datetime.now().strftime("%H:%M"))

    politicas = _obtener_politicas_activas()

    # Si no hay políticas, permitimos por defecto
    if not politicas:
        return {
            "permitido": True,
            "motivo": None,
            "politica_aplicada": None
        }

    for pol in politicas:
        try:
            condiciones_raw = pol.get("condiciones", "{}")
            condiciones = json.loads(condiciones_raw) if condiciones_raw else {}
        except json.JSONDecodeError:
            # Si la política tiene JSON roto, la ignoramos
            continue

        # Si condiciones es una lista, convertir a dict para compatibilidad
        if isinstance(condiciones, list):
            # Lista de condiciones - tomar la primera si existe
            if condiciones and len(condiciones) > 0:
                condiciones = condiciones[0]
            else:
                continue
        
        # 1) Filtro por aplicable_a
        aplicable_a = pol.get("aplicable_a", "global")
        if aplicable_a != "global":
            # Si la política es específica de un tipo, verificar
            if aplicable_a != tipo_entidad:
                continue  # Esta política no aplica a este tipo

        # 2) Filtro por tipo_entidad en condiciones (soporte legacy)
        tipo_objetivo = condiciones.get("tipo_entidad")
        if tipo_objetivo and tipo_objetivo != tipo_entidad:
            continue  # Esta política no aplica a este tipo

        # 3) Restricción de horario
        restriccion_horario = condiciones.get("restriccion_horario")
        if restriccion_horario:
            desde = restriccion_horario.get("desde", "00:00")
            hasta = restriccion_horario.get("hasta", "23:59")
            if not _hora_en_rango(hora, desde, hasta):
                return {
                    "permitido": False,
                    "motivo": f"Horario restringido por política '{pol['nombre']}'.",
                    "politica_aplicada": pol["nombre"]
                }

        # 4) Horario alternativo (tipo: horario con hora_inicio/hora_fin)
        if condiciones.get("tipo") == "horario":
            hora_inicio = condiciones.get("hora_inicio", "00:00")
            hora_fin = condiciones.get("hora_fin", "23:59")
            if not _hora_en_rango(hora, hora_inicio, hora_fin):
                return {
                    "permitido": False,
                    "motivo": f"Horario restringido por política '{pol['nombre']}' ({hora_inicio}-{hora_fin}).",
                    "politica_aplicada": pol["nombre"]
                }

        # 5) Límite de visitas por día
        max_visitas_dia = condiciones.get("max_visitas_dia")
        if max_visitas_dia is not None:
            visitas_hoy = _contar_visitas_hoy(entidad_id, fecha)
            if visitas_hoy >= max_visitas_dia:
                return {
                    "permitido": False,
                    "motivo": f"Límite de visitas diarias alcanzado ({visitas_hoy}/{max_visitas_dia}) por política '{pol['nombre']}'.",
                    "politica_aplicada": pol["nombre"]
                }

        # 6) Requiere autorización
        requiere_aut = condiciones.get("requiere_autorizacion")
        if requiere_aut:
            # Verificar si viene autorizado en metadata
            if not metadata.get("autorizado"):
                return {
                    "permitido": False,
                    "motivo": f"Requiere autorización previa según política '{pol['nombre']}'.",
                    "politica_aplicada": pol["nombre"]
                }

        # 7) Lista negra
        if condiciones.get("tipo") == "lista_negra":
            # Verificar si la entidad está marcada en lista negra
            if atributos.get("lista_negra") or metadata.get("lista_negra"):
                return {
                    "permitido": False,
                    "motivo": f"Entidad en lista negra según política '{pol['nombre']}'.",
                    "politica_aplicada": pol["nombre"]
                }

    # Si ninguna política bloquea, se permite
    return {
        "permitido": True,
        "motivo": None,
        "politica_aplicada": None
    }
