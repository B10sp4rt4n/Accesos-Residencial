"""
core/contexto.py
Captura de contexto y metadatos de dispositivo
"""

import platform
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json


def obtener_contexto_dispositivo() -> Dict[str, Any]:
    """
    Obtiene contexto del dispositivo actual
    
    Returns:
        Dict con información del sistema, red, etc.
    """
    try:
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
    except:
        hostname = "desconocido"
        ip_local = "0.0.0.0"
    
    return {
        "sistema_operativo": platform.system(),
        "version_so": platform.release(),
        "arquitectura": platform.machine(),
        "hostname": hostname,
        "ip_local": ip_local,
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat()
    }


def obtener_contexto_navegador(user_agent: str = None) -> Dict[str, Any]:
    """
    Extrae información del navegador desde User-Agent
    
    Args:
        user_agent: String del user agent del navegador
    """
    if not user_agent:
        return {"navegador": "desconocido", "version": None, "plataforma": None}
    
    # Parseo básico de user agent
    contexto = {
        "user_agent_completo": user_agent,
        "navegador": "desconocido",
        "version": None,
        "plataforma": None,
        "es_movil": False
    }
    
    # Detectar navegador
    if "Chrome" in user_agent:
        contexto["navegador"] = "Chrome"
    elif "Firefox" in user_agent:
        contexto["navegador"] = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        contexto["navegador"] = "Safari"
    elif "Edge" in user_agent:
        contexto["navegador"] = "Edge"
    
    # Detectar si es móvil
    if any(x in user_agent for x in ["Mobile", "Android", "iPhone", "iPad"]):
        contexto["es_movil"] = True
    
    # Detectar plataforma
    if "Windows" in user_agent:
        contexto["plataforma"] = "Windows"
    elif "Mac" in user_agent:
        contexto["plataforma"] = "macOS"
    elif "Linux" in user_agent:
        contexto["plataforma"] = "Linux"
    elif "Android" in user_agent:
        contexto["plataforma"] = "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        contexto["plataforma"] = "iOS"
    
    return contexto


def obtener_contexto_geolocalizacion(lat: float = None, lon: float = None) -> Dict[str, Any]:
    """
    Obtiene contexto de geolocalización
    (Útil para verificar que el acceso se registra desde la caseta correcta)
    """
    if lat is None or lon is None:
        return {
            "tiene_geolocalizacion": False,
            "latitud": None,
            "longitud": None
        }
    
    return {
        "tiene_geolocalizacion": True,
        "latitud": lat,
        "longitud": lon,
        "timestamp": datetime.now().isoformat()
    }


def obtener_contexto_red(ip_publica: str = None) -> Dict[str, Any]:
    """
    Obtiene contexto de red
    
    Args:
        ip_publica: IP pública del dispositivo (si está disponible)
    """
    return {
        "ip_publica": ip_publica,
        "timestamp": datetime.now().isoformat()
    }


def validar_contexto_confiable(contexto: dict, config: dict) -> Dict[str, Any]:
    """
    Valida que el contexto sea confiable según configuración
    
    Args:
        contexto: Contexto capturado
        config: Configuración de validación:
            - dispositivos_permitidos: lista de hostnames
            - ips_permitidas: lista de IPs
            - requiere_geolocalizacion: bool
            - radio_permitido_metros: int
    
    Returns:
        dict con 'es_confiable', 'motivo'
    """
    # Validar dispositivo
    if "dispositivos_permitidos" in config:
        hostname = contexto.get("dispositivo", {}).get("hostname")
        if hostname not in config["dispositivos_permitidos"]:
            return {
                "es_confiable": False,
                "motivo": f"Dispositivo no autorizado: {hostname}"
            }
    
    # Validar IP
    if "ips_permitidas" in config:
        ip = contexto.get("red", {}).get("ip_publica")
        if ip not in config["ips_permitidas"]:
            return {
                "es_confiable": False,
                "motivo": f"IP no autorizada: {ip}"
            }
    
    # Validar geolocalización
    if config.get("requiere_geolocalizacion"):
        geo = contexto.get("geolocalizacion", {})
        if not geo.get("tiene_geolocalizacion"):
            return {
                "es_confiable": False,
                "motivo": "Geolocalización requerida pero no disponible"
            }
        
        # Validar radio permitido
        if "ubicacion_caseta" in config and "radio_permitido_metros" in config:
            distancia = calcular_distancia(
                geo["latitud"],
                geo["longitud"],
                config["ubicacion_caseta"]["lat"],
                config["ubicacion_caseta"]["lon"]
            )
            
            if distancia > config["radio_permitido_metros"]:
                return {
                    "es_confiable": False,
                    "motivo": f"Fuera del radio permitido ({distancia:.0f}m)"
                }
    
    return {
        "es_confiable": True,
        "motivo": "Contexto validado correctamente"
    }


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distancia entre dos puntos geográficos (fórmula de Haversine)
    
    Returns:
        Distancia en metros
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Radio de la Tierra en metros
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


class ContextoManager:
    """Manager para captura y validación de contexto"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def capturar_contexto_completo(
        self,
        user_agent: str = None,
        ip_publica: str = None,
        lat: float = None,
        lon: float = None
    ) -> Dict[str, Any]:
        """
        Captura contexto completo del acceso
        
        Returns:
            Dict con todo el contexto disponible
        """
        return {
            "dispositivo": obtener_contexto_dispositivo(),
            "navegador": obtener_contexto_navegador(user_agent),
            "red": obtener_contexto_red(ip_publica),
            "geolocalizacion": obtener_contexto_geolocalizacion(lat, lon),
            "timestamp_captura": datetime.now().isoformat()
        }
    
    def validar_contexto(self, contexto: dict) -> Dict[str, Any]:
        """Valida contexto según configuración"""
        return validar_contexto_confiable(contexto, self.config)
    
    def obtener_fingerprint(self, contexto: dict) -> str:
        """
        Genera fingerprint único del dispositivo/sesión
        (Útil para detectar dispositivos duplicados o sospechosos)
        """
        from core.hashing import hash_evento
        
        datos_fingerprint = {
            "hostname": contexto.get("dispositivo", {}).get("hostname"),
            "user_agent": contexto.get("navegador", {}).get("user_agent_completo"),
            "ip_publica": contexto.get("red", {}).get("ip_publica"),
            "plataforma": contexto.get("navegador", {}).get("plataforma")
        }
        
        return hash_evento(datos_fingerprint)[:16]


# Configuración de ejemplo para validación de contexto
CONFIGURACION_EJEMPLO = {
    "dispositivos_permitidos": [
        "tablet-caseta-norte",
        "tablet-caseta-sur",
        "pc-administracion"
    ],
    "ips_permitidas": [
        "192.168.1.100",  # Tablet caseta norte
        "192.168.1.101",  # Tablet caseta sur
        "192.168.1.10"    # PC admin
    ],
    "requiere_geolocalizacion": True,
    "ubicacion_caseta": {
        "lat": 19.432608,
        "lon": -99.133209
    },
    "radio_permitido_metros": 50  # 50 metros alrededor de la caseta
}


if __name__ == "__main__":
    print("=== Pruebas de Contexto ===\n")
    
    # Obtener contexto del dispositivo actual
    contexto_disp = obtener_contexto_dispositivo()
    print(f"Dispositivo: {json.dumps(contexto_disp, indent=2)}\n")
    
    # Simular user agent
    ua = "Mozilla/5.0 (Linux; Android 11) Chrome/96.0 Mobile Safari/537.36"
    contexto_nav = obtener_contexto_navegador(ua)
    print(f"Navegador: {json.dumps(contexto_nav, indent=2)}\n")
    
    # Manager completo
    cm = ContextoManager(CONFIGURACION_EJEMPLO)
    contexto_completo = cm.capturar_contexto_completo(
        user_agent=ua,
        ip_publica="192.168.1.100",
        lat=19.432608,
        lon=-99.133209
    )
    
    print(f"Contexto completo capturado\n")
    
    # Validar
    validacion = cm.validar_contexto(contexto_completo)
    print(f"Validación: {validacion}\n")
    
    # Fingerprint
    fingerprint = cm.obtener_fingerprint(contexto_completo)
    print(f"Fingerprint: {fingerprint}")
