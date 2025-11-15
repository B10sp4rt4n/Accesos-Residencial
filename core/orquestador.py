"""
core/orquestador.py
Motor central AUP-EXO - Coordina todo el flujo de accesos
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from core.db import get_db
from core.hashing import hash_evento, hash_entidad, generar_hash_cadena
from core.motor_reglas import evaluar_reglas
from core.evidencia import enviar_a_recordia


class OrquestadorAccesos:
    """
    Orquestador central del sistema
    Coordina: reglas, nodos, eventos, auditoría, evidencias
    """
    
    def __init__(self, usuario_id: str = "system"):
        self.usuario_id = usuario_id
    
    def registrar_acceso(
        self,
        entidad_id: str,
        tipo_evento: str,
        metadata: dict,
        actor: str,
        dispositivo: str = "unknown",
        evidencia_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra un evento de acceso completo
        
        Args:
            entidad_id: ID de la entidad que accede
            tipo_evento: "entrada", "salida", "rechazo", "alerta"
            metadata: Información contextual (placa, gate, etc.)
            actor: Usuario que registra el evento
            dispositivo: Dispositivo desde donde se registra
            evidencia_id: ID de evidencia (foto, etc.)
        
        Returns:
            Dict con resultado del registro
        """
        timestamp_servidor = datetime.now().isoformat()
        
        # Obtener último evento para encadenar hash
        with get_db() as db:
            ultimo_evento = db.execute("""
                SELECT hash_actual FROM eventos
                ORDER BY evento_id DESC LIMIT 1
            """).fetchone()
            
            hash_prev = ultimo_evento['hash_actual'] if ultimo_evento else None
        
        # Preparar datos del evento
        evento_data = {
            "entidad_id": entidad_id,
            "tipo_evento": tipo_evento,
            "metadata": metadata,
            "timestamp_servidor": timestamp_servidor,
            "actor": actor,
            "dispositivo": dispositivo
        }
        
        # Generar hash encadenado
        evento_hash, evento_completo = generar_hash_cadena(
            hash_prev,
            evento_data,
            timestamp_servidor
        )
        
        # FASE 3 - Integración EXO-Recordia
        # Enviar a Recordia para trazabilidad jurídica externa
        recibo_recordia = enviar_a_recordia(evento_hash, metadata)
        
        # Insertar en base de datos
        with get_db() as db:
            cursor = db.execute("""
                INSERT INTO eventos (
                    entidad_id, tipo_evento, metadata, evidencia_id,
                    hash_actual, timestamp_servidor, timestamp_cliente,
                    actor, dispositivo, origen, contexto, recibo_recordia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entidad_id,
                tipo_evento,
                json.dumps(metadata),
                evidencia_id,
                evento_hash,
                timestamp_servidor,
                metadata.get('timestamp_cliente'),
                actor,
                dispositivo,
                metadata.get('origen', 'local'),
                json.dumps(metadata.get('contexto', {})),
                recibo_recordia
            ))
            
            evento_id = cursor.lastrowid
        
        # Registrar en bitácora
        self._registrar_bitacora(
            "eventos",
            "INSERT",
            str(evento_id),
            None,
            evento_completo,
            actor
        )
        
        return {
            "success": True,
            "evento_id": evento_id,
            "hash": evento_hash,
            "recibo_recordia": recibo_recordia,
            "timestamp": timestamp_servidor
        }
    
    def procesar_acceso(
        self,
        entidad_id: str,
        metadata: dict,
        actor: str,
        dispositivo: str = "tablet",
        evidencia_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa un intento de acceso (evalúa reglas + registra)
        
        Este es el método principal que debe llamarse desde la interfaz.
        
        Returns:
            Si permitido: evento_hash (str)
            Si rechazado: {"status": "rechazado", "motivo": str, "politica": str}
        """
        # Evaluar reglas de negocio
        evaluacion = evaluar_reglas(entidad_id, metadata)
        
        if not evaluacion['permitido']:
            # Acceso denegado - registrar rechazo
            metadata_rechazo = dict(metadata)
            metadata_rechazo["motivo_rechazo"] = evaluacion["motivo"]
            metadata_rechazo["evaluacion"] = evaluacion
            
            self.registrar_acceso(
                entidad_id=entidad_id,
                tipo_evento="rechazo",
                metadata=metadata_rechazo,
                actor=actor,
                dispositivo=dispositivo,
                evidencia_id=evidencia_id
            )
            
            return {
                "status": "rechazado",
                "motivo": evaluacion["motivo"],
                "politica": evaluacion["politica_aplicada"]
            }
        
        # Acceso permitido - registrar entrada
        metadata_entrada = dict(metadata)
        metadata_entrada["evaluacion"] = evaluacion
        
        resultado_registro = self.registrar_acceso(
            entidad_id=entidad_id,
            tipo_evento="entrada",
            metadata=metadata_entrada,
            actor=actor,
            dispositivo=dispositivo,
            evidencia_id=evidencia_id
        )
        
        # Retornar solo el hash del evento (para compatibilidad con vigilancia)
        return resultado_registro["hash"]
    
    def registrar_salida(
        self,
        entidad_id: str,
        metadata: dict,
        actor: str,
        dispositivo: str = "tablet"
    ) -> Dict[str, Any]:
        """Registra una salida"""
        return self.registrar_acceso(
            entidad_id=entidad_id,
            tipo_evento="salida",
            metadata=metadata,
            actor=actor,
            dispositivo=dispositivo
        )
    
    def crear_entidad(
        self,
        tipo: str,
        atributos: dict,
        created_by: str = None
    ) -> Dict[str, Any]:
        """
        Crea una nueva entidad en el sistema
        
        Args:
            tipo: "persona", "vehiculo", "proveedor", "visita"
            atributos: Datos específicos de la entidad
            created_by: Usuario que crea la entidad
        """
        timestamp = datetime.now().isoformat()
        
        # Generar hash de la entidad
        entidad_data = {
            "tipo": tipo,
            "atributos": atributos,
            "fecha_creacion": timestamp
        }
        
        hash_actual = hash_entidad(entidad_data)
        
        # Generar ID único
        from core.hashing import generar_id_unico
        entidad_id = generar_id_unico("ENT", entidad_data)
        
        # Insertar en base de datos
        with get_db() as db:
            db.execute("""
                INSERT INTO entidades (
                    entidad_id, tipo, atributos, hash_actual,
                    estado, fecha_creacion, fecha_actualizacion, created_by
                ) VALUES (?, ?, ?, ?, 'activo', ?, ?, ?)
            """, (
                entidad_id,
                tipo,
                json.dumps(atributos),
                hash_actual,
                timestamp,
                timestamp,
                created_by or self.usuario_id
            ))
        
        # Registrar en bitácora
        self._registrar_bitacora(
            "entidades",
            "INSERT",
            entidad_id,
            None,
            entidad_data,
            created_by or self.usuario_id
        )
        
        return {
            "success": True,
            "entidad_id": entidad_id,
            "tipo": tipo,
            "hash": hash_actual
        }
    
    def actualizar_entidad(
        self,
        entidad_id: str,
        nuevos_atributos: dict,
        updated_by: str = None
    ) -> Dict[str, Any]:
        """Actualiza una entidad existente"""
        with get_db() as db:
            # Obtener entidad actual
            entidad_actual = db.execute(
                "SELECT * FROM entidades WHERE entidad_id = ?",
                (entidad_id,)
            ).fetchone()
            
            if not entidad_actual:
                return {"success": False, "error": "Entidad no encontrada"}
            
            atributos_actuales = json.loads(entidad_actual['atributos'])
            hash_prev = entidad_actual['hash_actual']
            
            # Combinar atributos
            atributos_nuevos = {**atributos_actuales, **nuevos_atributos}
            
            # Generar nuevo hash
            entidad_data = {
                "tipo": entidad_actual['tipo'],
                "atributos": atributos_nuevos,
                "fecha_actualizacion": datetime.now().isoformat()
            }
            hash_nuevo = hash_entidad(entidad_data)
            
            # Actualizar
            db.execute("""
                UPDATE entidades
                SET atributos = ?, hash_prev = ?, hash_actual = ?,
                    fecha_actualizacion = ?, updated_by = ?
                WHERE entidad_id = ?
            """, (
                json.dumps(atributos_nuevos),
                hash_prev,
                hash_nuevo,
                datetime.now().isoformat(),
                updated_by or self.usuario_id,
                entidad_id
            ))
            
            # Bitácora
            self._registrar_bitacora(
                "entidades",
                "UPDATE",
                entidad_id,
                dict(entidad_actual),
                entidad_data,
                updated_by or self.usuario_id
            )
        
        return {
            "success": True,
            "entidad_id": entidad_id,
            "hash_anterior": hash_prev,
            "hash_nuevo": hash_nuevo
        }
    
    def obtener_entidad(self, entidad_id: str) -> Optional[Dict]:
        """Obtiene una entidad por su ID"""
        with get_db() as db:
            entidad = db.execute(
                "SELECT * FROM entidades WHERE entidad_id = ?",
                (entidad_id,)
            ).fetchone()
            
            if not entidad:
                return None
            
            return {
                "entidad_id": entidad['entidad_id'],
                "tipo": entidad['tipo'],
                "atributos": json.loads(entidad['atributos']),
                "estado": entidad['estado'],
                "hash_actual": entidad['hash_actual'],
                "fecha_creacion": entidad['fecha_creacion'],
                "fecha_actualizacion": entidad['fecha_actualizacion']
            }
    
    def _registrar_bitacora(
        self,
        tabla: str,
        operacion: str,
        registro_id: str,
        datos_anteriores: Any,
        datos_nuevos: Any,
        usuario_id: str
    ):
        """Registra operación en bitácora de auditoría"""
        with get_db() as db:
            db.execute("""
                INSERT INTO bitacora (
                    tabla, operacion, registro_id,
                    datos_anteriores, datos_nuevos,
                    usuario_id, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                tabla,
                operacion,
                registro_id,
                json.dumps(datos_anteriores) if datos_anteriores else None,
                json.dumps(datos_nuevos),
                usuario_id,
                datetime.now().isoformat()
            ))


if __name__ == "__main__":
    from core.db import init_db
    init_db()
    
    # Prueba del orquestador
    print("=== Prueba del Orquestador ===\n")
    
    orq = OrquestadorAccesos(usuario_id="admin")
    
    # Crear entidad
    resultado = orq.crear_entidad(
        tipo="persona",
        atributos={
            "nombre": "Juan Pérez",
            "tipo": "residente",
            "casa": "15"
        },
        created_by="admin"
    )
    print(f"Entidad creada: {resultado}\n")
    
    # Procesar acceso
    acceso = orq.procesar_acceso(
        entidad_id=resultado['entidad_id'],
        metadata={"hora": "10:00", "gate": "GATE_001"},
        actor="vigilante1",
        dispositivo="tablet"
    )
    print(f"Resultado acceso: {acceso}")
