"""
core/motor_reglas.py
Motor de evaluación de políticas y reglas de negocio
"""

import json
from datetime import datetime, time as dt_time
from typing import Dict, Any, List
from core.db import get_db


class ResultadoEvaluacion:
    """Resultado de evaluación de reglas"""
    def __init__(self, permitido: bool, motivo: str = None, acciones: List[str] = None):
        self.permitido = permitido
        self.motivo = motivo
        self.acciones = acciones or []
        self.politicas_aplicadas = []
    
    def to_dict(self):
        return {
            "permitido": self.permitido,
            "motivo": self.motivo,
            "acciones": self.acciones,
            "politicas_aplicadas": self.politicas_aplicadas
        }


def evaluar_reglas(entidad_id: str, metadata: dict) -> Dict[str, Any]:
    """
    Evalúa todas las reglas aplicables a una entidad
    
    Args:
        entidad_id: ID de la entidad (persona, vehículo, etc.)
        metadata: Datos del contexto (hora, gate, tipo_acceso, etc.)
    
    Returns:
        Dict con resultado de evaluación
    """
    resultado = ResultadoEvaluacion(permitido=True)
    
    # Obtener información de la entidad
    with get_db() as db:
        entidad = db.execute("""
            SELECT * FROM entidades WHERE entidad_id = ?
        """, (entidad_id,)).fetchone()
        
        if not entidad:
            # Entidad no encontrada - denegar por defecto
            resultado.permitido = False
            resultado.motivo = "Entidad no encontrada en el sistema"
            return resultado.to_dict()
        
        # Convertir sqlite3.Row a dict
        entidad_dict = dict(entidad)
        entidad_attrs = json.loads(entidad_dict['atributos'])
        
        # Verificar estado de entidad
        if entidad['estado'] != 'activo':
            resultado.permitido = False
            resultado.motivo = f"Entidad en estado: {entidad['estado']}"
            return resultado.to_dict()
        
        # Obtener políticas activas aplicables
        politicas = db.execute("""
            SELECT * FROM politicas
            WHERE estado = 'activa'
            ORDER BY prioridad DESC
        """).fetchall()
    
    # Evaluar cada política
    for politica in politicas:
        condiciones = json.loads(politica['condiciones'])
        
        # Verificar si aplica a esta entidad
        if politica['aplicable_a']:
            aplicable_a = politica['aplicable_a']  # Es un string simple, no JSON
            # Si no es "global", verificar tipo de entidad
            if aplicable_a != "global" and entidad_dict.get('tipo') != aplicable_a:
                continue
        
        # Evaluar condiciones
        # condiciones es una lista de condiciones individuales
        for condicion in condiciones:
            resultado_condicion = evaluar_condicion_individual(condicion, entidad_attrs, metadata)
            
            if not resultado_condicion['cumple']:
                resultado.permitido = False
                resultado.motivo = resultado_condicion['motivo']
                resultado.politicas_aplicadas.append(politica['politica_id'])
                
                # Registrar en log de reglas
                registrar_log_regla(None, politica['politica_id'], resultado_condicion)
                
                # Si la política es crítica, detener evaluación
                if politica['prioridad'] >= 9:
                    break
                
                # Salir del loop de condiciones de esta política
                break
    
    return resultado.to_dict()


def evaluar_condicion_individual(condicion: dict, entidad_attrs: dict, metadata: dict) -> dict:
    """
    Evalúa una condición individual
    
    Tipos de condiciones:
    - tipo: "horario" con hora_inicio, hora_fin
    - tipo: "dias_semana" con dias_permitidos
    - tipo: "lista_negra"
    - tipo: "autorizacion_previa"
    """
    tipo = condicion.get('tipo')
    
    # Condición de horario
    if tipo == "horario":
        hora_actual = metadata.get('hora', datetime.now().strftime("%H:%M"))
        hora_inicio = condicion['hora_inicio']
        hora_fin = condicion['hora_fin']
        
        if not esta_en_horario(hora_actual, hora_inicio, hora_fin):
            return {
                "cumple": False,
                "motivo": f"Fuera de horario permitido ({hora_inicio}-{hora_fin})"
            }
    
    # Condición de días de semana
    elif tipo == "dias_semana":
        dia_actual = metadata.get('dia', datetime.now().strftime("%A").lower())
        dias_map = {
            "monday": "lunes", "tuesday": "martes", "wednesday": "miercoles",
            "thursday": "jueves", "friday": "viernes", "saturday": "sabado", "sunday": "domingo"
        }
        dia_es = dias_map.get(dia_actual, dia_actual)
        
        if dia_es not in condicion['dias_permitidos']:
            return {
                "cumple": False,
                "motivo": f"Día no permitido: {dia_es}"
            }
    
    # Condición de lista negra
    elif tipo == "lista_negra":
        if entidad_attrs.get('lista_negra') or metadata.get('lista_negra'):
            return {
                "cumple": False,
                "motivo": "Entidad en lista negra"
            }
    
    # Condición de autorización previa
    elif tipo == "autorizacion_previa":
        if not metadata.get('tiene_autorizacion'):
            return {
                "cumple": False,
                "motivo": f"Requiere autorización previa: {condicion.get('metodo', 'general')}"
            }
    
    # Condición cumplida
    return {
        "cumple": True,
        "motivo": None
    }


def evaluar_condiciones(condiciones: dict, entidad_attrs: dict, metadata: dict) -> dict:
    """
    Evalúa un conjunto de condiciones
    
    Condiciones soportadas:
    - horario_permitido: {"inicio": "08:00", "fin": "20:00"}
    - dias_permitidos: ["lunes", "martes", ...]
    - tipo_restringido: ["visitante", "proveedor"]
    - lista_negra: true/false
    - requiere_autorizacion: true/false
    - tiempo_max_estancia: 120 (minutos)
    """
    
    # Horario
    if 'horario_permitido' in condiciones:
        horario = condiciones['horario_permitido']
        hora_actual = metadata.get('hora', datetime.now().strftime("%H:%M"))
        
        if not esta_en_horario(hora_actual, horario['inicio'], horario['fin']):
            return {
                "cumple": False,
                "motivo": f"Fuera de horario permitido ({horario['inicio']}-{horario['fin']})"
            }
    
    # Días permitidos
    if 'dias_permitidos' in condiciones:
        dia_actual = metadata.get('dia', datetime.now().strftime("%A").lower())
        dias_map = {
            "monday": "lunes", "tuesday": "martes", "wednesday": "miercoles",
            "thursday": "jueves", "friday": "viernes", "saturday": "sabado", "sunday": "domingo"
        }
        dia_es = dias_map.get(dia_actual, dia_actual)
        
        if dia_es not in condiciones['dias_permitidos']:
            return {
                "cumple": False,
                "motivo": f"Día no permitido: {dia_es}"
            }
    
    # Lista negra
    if condiciones.get('verificar_lista_negra'):
        if entidad_attrs.get('en_lista_negra'):
            return {
                "cumple": False,
                "motivo": "Entidad en lista negra"
            }
    
    # Requiere autorización
    if condiciones.get('requiere_autorizacion'):
        if not metadata.get('autorizado'):
            return {
                "cumple": False,
                "motivo": "Requiere autorización previa"
            }
    
    # Tipo restringido
    if 'tipos_restringidos' in condiciones:
        if entidad_attrs.get('tipo') in condiciones['tipos_restringidos']:
            return {
                "cumple": False,
                "motivo": f"Tipo restringido: {entidad_attrs.get('tipo')}"
            }
    
    # Límite de visitas
    if 'max_visitas_dia' in condiciones:
        visitas_hoy = metadata.get('visitas_hoy', 0)
        if visitas_hoy >= condiciones['max_visitas_dia']:
            return {
                "cumple": False,
                "motivo": f"Límite de visitas alcanzado ({condiciones['max_visitas_dia']})"
            }
    
    # Todas las condiciones cumplidas
    return {"cumple": True, "motivo": None}


def esta_en_horario(hora_actual: str, hora_inicio: str, hora_fin: str) -> bool:
    """Verifica si una hora está dentro de un rango"""
    try:
        h_actual = datetime.strptime(hora_actual, "%H:%M").time()
        h_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        h_fin = datetime.strptime(hora_fin, "%H:%M").time()
        
        if h_inicio <= h_fin:
            return h_inicio <= h_actual <= h_fin
        else:  # Cruza medianoche
            return h_actual >= h_inicio or h_actual <= h_fin
    except:
        return True  # En caso de error, permitir


def registrar_log_regla(evento_id: int, politica_id: str, resultado: dict):
    """Registra el resultado de evaluación de una regla"""
    with get_db() as db:
        db.execute("""
            INSERT INTO log_reglas (evento_id, politica_id, resultado, motivo, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            evento_id,
            politica_id,
            json.dumps(resultado),
            resultado.get('motivo'),
            datetime.now().isoformat()
        ))


def crear_politica_ejemplo():
    """Crea políticas de ejemplo"""
    with get_db() as db:
        politicas_ejemplo = [
            {
                "politica_id": "POL_HORARIO_VISITANTES",
                "nombre": "Horario de Visitantes",
                "descripcion": "Visitantes solo pueden ingresar de 8:00 a 20:00",
                "tipo": "restriccion_horario",
                "condiciones": json.dumps({
                    "horario_permitido": {"inicio": "08:00", "fin": "20:00"}
                }),
                "prioridad": 7,
                "aplicable_a": json.dumps(["visitante"]),
            },
            {
                "politica_id": "POL_LISTA_NEGRA",
                "nombre": "Verificación Lista Negra",
                "descripcion": "Bloquear acceso a entidades en lista negra",
                "tipo": "seguridad",
                "condiciones": json.dumps({
                    "verificar_lista_negra": True
                }),
                "prioridad": 10,
                "aplicable_a": json.dumps(["persona", "vehiculo"]),
            },
            {
                "politica_id": "POL_AUTORIZACION_PROVEEDORES",
                "nombre": "Autorización de Proveedores",
                "descripcion": "Proveedores requieren autorización del residente",
                "tipo": "autorizacion",
                "condiciones": json.dumps({
                    "requiere_autorizacion": True
                }),
                "prioridad": 8,
                "aplicable_a": json.dumps(["proveedor", "delivery"]),
            }
        ]
        
        for pol in politicas_ejemplo:
            db.execute("""
                INSERT OR IGNORE INTO politicas
                (politica_id, nombre, descripcion, tipo, condiciones, prioridad, 
                 estado, aplicable_a, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, 'activa', ?, datetime('now'), datetime('now'))
            """, (
                pol['politica_id'], pol['nombre'], pol['descripcion'],
                pol['tipo'], pol['condiciones'], pol['prioridad'],
                pol['aplicable_a']
            ))
        
        print("✅ Políticas de ejemplo creadas")


if __name__ == "__main__":
    from core.db import init_db
    init_db()
    crear_politica_ejemplo()
    
    # Prueba de evaluación
    print("\n=== Prueba de Motor de Reglas ===")
    resultado = evaluar_reglas("ENT_test", {
        "hora": "21:00",
        "tipo": "visitante"
    })
    print(f"Resultado: {resultado}")
