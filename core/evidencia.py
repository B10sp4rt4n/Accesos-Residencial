"""
core/evidencia.py
Gestión de evidencias (fotos, documentos)
Puente EXO para HotVault futuro
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from core.hashing import hash_evidencia


class GestorEvidencias:
    """Gestor de evidencias fotográficas y documentales"""
    
    def __init__(self, base_path: str = "data/evidencia"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def guardar_evidencia(
        self,
        archivo_bytes: bytes,
        tipo: str,
        metadata: dict,
        entidad_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Guarda una evidencia y retorna su ID y hash
        
        Args:
            archivo_bytes: Contenido del archivo
            tipo: "foto_placa", "foto_persona", "documento", etc.
            metadata: Información adicional (timestamp, gate_id, etc.)
            entidad_id: ID de entidad relacionada
        
        Returns:
            Dict con evidencia_id, hash, ruta
        """
        timestamp = datetime.now()
        
        # Generar hash de la evidencia
        hash_archivo = hash_evidencia(archivo_bytes, metadata)
        
        # Generar ID único
        evidencia_id = f"EV_{tipo}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{hash_archivo[:8]}"
        
        # Determinar ruta de almacenamiento
        fecha_dir = self.base_path / timestamp.strftime('%Y/%m/%d')
        fecha_dir.mkdir(parents=True, exist_ok=True)
        
        # Extensión basada en tipo
        ext = self._obtener_extension(tipo)
        nombre_archivo = f"{evidencia_id}{ext}"
        ruta_completa = fecha_dir / nombre_archivo
        
        # Guardar archivo
        with open(ruta_completa, 'wb') as f:
            f.write(archivo_bytes)
        
        # Guardar metadata
        metadata_completa = {
            "evidencia_id": evidencia_id,
            "tipo": tipo,
            "hash": hash_archivo,
            "tamanio_bytes": len(archivo_bytes),
            "timestamp": timestamp.isoformat(),
            "entidad_id": entidad_id,
            "ruta_relativa": str(ruta_completa.relative_to(self.base_path)),
            **metadata
        }
        
        metadata_path = ruta_completa.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_completa, f, indent=2, ensure_ascii=False)
        
        return {
            "evidencia_id": evidencia_id,
            "hash": hash_archivo,
            "ruta": str(ruta_completa),
            "tamanio": len(archivo_bytes),
            "timestamp": timestamp.isoformat()
        }
    
    def obtener_evidencia(self, evidencia_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una evidencia por su ID
        
        Returns:
            Dict con datos y metadata de la evidencia
        """
        # Buscar archivo de metadata
        for metadata_file in self.base_path.rglob(f"{evidencia_id}.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Leer archivo de evidencia
            archivo_path = metadata_file.with_suffix(
                self._obtener_extension(metadata['tipo'])
            )
            
            if archivo_path.exists():
                with open(archivo_path, 'rb') as f:
                    contenido = f.read()
                
                return {
                    **metadata,
                    "contenido": contenido,
                    "existe": True
                }
        
        return None
    
    def verificar_integridad(self, evidencia_id: str) -> Dict[str, Any]:
        """
        Verifica la integridad de una evidencia
        
        Returns:
            Dict con 'integra', 'hash_esperado', 'hash_actual'
        """
        evidencia = self.obtener_evidencia(evidencia_id)
        
        if not evidencia:
            return {
                "integra": False,
                "motivo": "Evidencia no encontrada"
            }
        
        hash_esperado = evidencia['hash']
        metadata_original = {k: v for k, v in evidencia.items() 
                           if k not in ['contenido', 'existe']}
        hash_actual = hash_evidencia(evidencia['contenido'], metadata_original)
        
        return {
            "integra": hash_esperado == hash_actual,
            "hash_esperado": hash_esperado,
            "hash_actual": hash_actual,
            "motivo": "Íntegra" if hash_esperado == hash_actual else "Hash no coincide"
        }
    
    def listar_evidencias_entidad(self, entidad_id: str) -> list:
        """Lista todas las evidencias de una entidad"""
        evidencias = []
        
        for metadata_file in self.base_path.rglob("*.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if metadata.get('entidad_id') == entidad_id:
                evidencias.append({
                    "evidencia_id": metadata['evidencia_id'],
                    "tipo": metadata['tipo'],
                    "timestamp": metadata['timestamp'],
                    "tamanio_bytes": metadata['tamanio_bytes'],
                    "hash": metadata['hash']
                })
        
        return sorted(evidencias, key=lambda x: x['timestamp'], reverse=True)
    
    def eliminar_evidencia(self, evidencia_id: str) -> bool:
        """
        Elimina una evidencia (soft delete - marca como eliminada)
        
        Nota: En producción con HotVault, esto sería inmutable
        """
        evidencia = self.obtener_evidencia(evidencia_id)
        
        if not evidencia:
            return False
        
        # Marcar como eliminada en metadata
        for metadata_file in self.base_path.rglob(f"{evidencia_id}.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            metadata['eliminada'] = True
            metadata['timestamp_eliminacion'] = datetime.now().isoformat()
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
        
        return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del almacenamiento de evidencias"""
        total_archivos = 0
        total_bytes = 0
        por_tipo = {}
        
        for metadata_file in self.base_path.rglob("*.json"):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if not metadata.get('eliminada'):
                total_archivos += 1
                total_bytes += metadata.get('tamanio_bytes', 0)
                
                tipo = metadata.get('tipo', 'desconocido')
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        return {
            "total_evidencias": total_archivos,
            "espacio_usado_bytes": total_bytes,
            "espacio_usado_mb": round(total_bytes / (1024 * 1024), 2),
            "por_tipo": por_tipo
        }
    
    def _obtener_extension(self, tipo: str) -> str:
        """Obtiene extensión de archivo según tipo de evidencia"""
        extensiones = {
            "foto_placa": ".jpg",
            "foto_persona": ".jpg",
            "foto_vehiculo": ".jpg",
            "foto_general": ".jpg",
            "documento": ".pdf",
            "identificacion": ".jpg",
            "otro": ".bin"
        }
        return extensiones.get(tipo, ".bin")
    
    def generar_url_temporal(self, evidencia_id: str, valido_minutos: int = 60) -> str:
        """
        Genera URL temporal para acceso a evidencia
        (Placeholder para integración futura con HotVault)
        """
        from core.hashing import hash_evento
        
        data = {
            "evidencia_id": evidencia_id,
            "expira": (datetime.now() + timedelta(minutes=valido_minutos)).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        token = hash_evento(data)[:16]
        
        # En producción: URL real con firma
        return f"/evidencias/{evidencia_id}?token={token}"


# Integración futura con HotVault
class HotVaultBridge:
    """
    Puente para integración futura con HotVault
    (Sistema de almacenamiento inmutable distribuido)
    """
    
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint
        self.habilitado = False  # Activar cuando HotVault esté disponible
    
    def subir_evidencia(self, evidencia_id: str, contenido: bytes, metadata: dict):
        """Sube evidencia a HotVault"""
        if not self.habilitado:
            return {"success": False, "motivo": "HotVault no habilitado"}
        
        # TODO: Implementar cuando HotVault esté disponible
        # POST a HotVault con evidencia encriptada
        pass
    
    def obtener_evidencia(self, evidencia_id: str):
        """Obtiene evidencia desde HotVault"""
        if not self.habilitado:
            return None
        
        # TODO: Implementar
        pass
    
    def verificar_existencia(self, hash_evidencia: str) -> bool:
        """Verifica si una evidencia existe en HotVault"""
        if not self.habilitado:
            return False
        
        # TODO: Implementar
        pass


if __name__ == "__main__":
    print("=== Pruebas de Gestor de Evidencias ===\n")
    
    gestor = GestorEvidencias()
    
    # Guardar evidencia de prueba
    contenido_prueba = b"Esto es una foto de prueba"
    metadata_prueba = {
        "gate_id": "GATE_001",
        "placa": "ABC-1234",
        "confianza": 0.95
    }
    
    resultado = gestor.guardar_evidencia(
        contenido_prueba,
        "foto_placa",
        metadata_prueba,
        "ENT_test123"
    )
    
    print(f"Evidencia guardada: {resultado}\n")
    
    # Verificar integridad
    integridad = gestor.verificar_integridad(resultado['evidencia_id'])
    print(f"Integridad: {integridad}\n")
    
    # Estadísticas
    stats = gestor.obtener_estadisticas()
    print(f"Estadísticas: {stats}")
