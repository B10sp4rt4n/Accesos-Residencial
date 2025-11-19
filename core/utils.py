"""
core/utils.py
Utilidades generales del sistema
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


def validar_placa_mexico(placa: str, estado: str = None) -> Dict[str, Any]:
    """
    Valida formato de placa mexicana según estado
    
    Returns:
        dict con 'valido', 'placa_normalizada', 'mensaje'
    """
    placa = placa.upper().strip().replace(" ", "")
    
    # Patrones por estado
    patrones = {
        'CDMX': r'^[A-Z]{3}-?\d{3,4}$',
        'EDO': r'^[A-Z]{3}-?\d{2}-?\d{2}$',
        'JAL': r'^[A-Z]{2}-?\d{4,5}$',
        'NL': r'^[A-Z]{3}-?\d{3,4}$',
        'QRO': r'^[A-Z]{3}-?\d{3,4}$',
        'GTO': r'^[A-Z]{3}-?\d{3,4}$',
    }
    
    # Patrón general si no se especifica estado
    patron = patrones.get(estado, r'^[A-Z0-9-]{5,10}$')
    
    if re.match(patron, placa):
        # Normalizar formato
        placa_normalizada = placa.replace("-", "")
        if len(placa_normalizada) >= 6:
            # Formato ABC-1234
            placa_normalizada = f"{placa_normalizada[:3]}-{placa_normalizada[3:]}"
        
        return {
            'valido': True,
            'placa_normalizada': placa_normalizada,
            'mensaje': 'Placa válida'
        }
    else:
        return {
            'valido': False,
            'placa_normalizada': placa,
            'mensaje': f'Formato inválido para {estado or "placa mexicana"}'
        }


def validar_curp(curp: str) -> bool:
    """
    Valida formato de CURP mexicano
    Formato: AAAA######HAAAAA##
    """
    if not curp or len(curp) != 18:
        return False
    
    curp = curp.upper()
    patron = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
    
    return bool(re.match(patron, curp))


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


def validar_telefono_mexico(telefono: str) -> bool:
    """Valida formato de teléfono mexicano (10 dígitos)"""
    telefono = re.sub(r'\D', '', telefono)  # Solo dígitos
    return len(telefono) == 10


def normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre (capitaliza correctamente)"""
    return ' '.join(word.capitalize() for word in nombre.split())


def calcular_edad(fecha_nacimiento: str) -> Optional[int]:
    """Calcula edad a partir de fecha de nacimiento"""
    try:
        nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year
        
        # Ajustar si no ha cumplido años este año
        if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
            edad -= 1
        
        return edad
    except:
        return None


def formato_fecha_es(fecha_iso: str) -> str:
    """Convierte fecha ISO a formato español legible"""
    try:
        dt = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        meses = {
            1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
            7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
        }
        return f"{dt.day} {meses[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
    except:
        return fecha_iso


def tiempo_transcurrido(fecha_iso: str) -> str:
    """Calcula tiempo transcurrido en formato legible"""
    try:
        fecha = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        ahora = datetime.now()
        diferencia = ahora - fecha
        
        segundos = int(diferencia.total_seconds())
        
        if segundos < 60:
            return "hace un momento"
        elif segundos < 3600:
            minutos = segundos // 60
            return f"hace {minutos} min"
        elif segundos < 86400:
            horas = segundos // 3600
            return f"hace {horas} h"
        elif segundos < 604800:
            dias = segundos // 86400
            return f"hace {dias} día{'s' if dias > 1 else ''}"
        else:
            semanas = segundos // 604800
            return f"hace {semanas} semana{'s' if semanas > 1 else ''}"
    except:
        return "desconocido"


def sanitizar_input(texto: str, max_length: int = 255) -> str:
    """Sanitiza input de usuario (previene inyecciones)"""
    if not texto:
        return ""
    
    # Remover caracteres peligrosos
    texto = re.sub(r'[<>{};\\\']', '', texto)
    
    # Limitar longitud
    return texto[:max_length].strip()


def generar_codigo_qr_data(entidad_id: str, valido_hasta: str = None) -> str:
    """
    Genera datos para código QR de acceso temporal
    
    Returns:
        JSON string con datos del QR
    """
    if not valido_hasta:
        # Válido por 24 horas por defecto
        valido_hasta = (datetime.now() + timedelta(days=1)).isoformat()
    
    data = {
        "entidad_id": entidad_id,
        "tipo": "acceso_temporal",
        "valido_hasta": valido_hasta,
        "generado": datetime.now().isoformat()
    }
    
    return json.dumps(data)


def verificar_codigo_qr(qr_data: str) -> Dict[str, Any]:
    """
    Verifica validez de código QR
    
    Returns:
        dict con 'valido', 'entidad_id', 'motivo'
    """
    try:
        data = json.loads(qr_data)
        
        # Verificar expiración
        valido_hasta = datetime.fromisoformat(data['valido_hasta'])
        ahora = datetime.now()
        
        if ahora > valido_hasta:
            return {
                'valido': False,
                'entidad_id': data.get('entidad_id'),
                'motivo': 'Código QR expirado'
            }
        
        return {
            'valido': True,
            'entidad_id': data.get('entidad_id'),
            'motivo': 'Código válido'
        }
    except Exception as e:
        return {
            'valido': False,
            'entidad_id': None,
            'motivo': f'Código inválido: {str(e)}'
        }


def formatear_bytes(bytes_cantidad: int) -> str:
    """Formatea cantidad de bytes en formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes_cantidad < 1024.0:
            return f"{bytes_cantidad:.1f} {unidad}"
        bytes_cantidad /= 1024.0
    return f"{bytes_cantidad:.1f} TB"


def generar_reporte_resumen(eventos: list) -> Dict[str, Any]:
    """Genera resumen estadístico de eventos"""
    if not eventos:
        return {
            'total': 0,
            'entradas': 0,
            'salidas': 0,
            'rechazos': 0,
            'mas_activo': None
        }
    
    total = len(eventos)
    entradas = sum(1 for e in eventos if e.get('tipo_evento') == 'entrada')
    salidas = sum(1 for e in eventos if e.get('tipo_evento') == 'salida')
    rechazos = sum(1 for e in eventos if e.get('tipo_evento') == 'rechazo')
    
    # Entidad más activa
    entidades_count = {}
    for e in eventos:
        ent_id = e.get('entidad_id')
        if ent_id:
            entidades_count[ent_id] = entidades_count.get(ent_id, 0) + 1
    
    mas_activo = max(entidades_count, key=entidades_count.get) if entidades_count else None
    
    return {
        'total': total,
        'entradas': entradas,
        'salidas': salidas,
        'rechazos': rechazos,
        'mas_activo': mas_activo,
        'tasa_rechazo': round((rechazos / total * 100), 2) if total > 0 else 0
    }


# Constantes útiles
DIAS_SEMANA_ES = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


if __name__ == "__main__":
    # Pruebas
    print("=== Pruebas de Utilidades ===\n")
    
    # Validar placa
    placa = validar_placa_mexico("ABC1234", "CDMX")
    print(f"Placa: {placa}\n")
    
    # Validar CURP
    curp_valido = validar_curp("CURP810312HDFLRS09")
    print(f"CURP válido: {curp_valido}\n")
    
    # Tiempo transcurrido
    hace_2h = (datetime.now() - timedelta(hours=2)).isoformat()
    print(f"Tiempo: {tiempo_transcurrido(hace_2h)}\n")
    
    # QR
    qr_data = generar_codigo_qr_data("ENT_test123")
    print(f"QR generado: {qr_data}\n")
    
    verificacion = verificar_codigo_qr(qr_data)
    print(f"Verificación QR: {verificacion}")
