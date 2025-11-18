"""
AX-S - AUP-EXO Database Connection Manager
Gestión de conexiones y queries con contexto jerárquico
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Tuple
import os
from contextlib import contextmanager
import uuid
from datetime import datetime

from core.exo_hierarchy import ContextoUsuario, ControlAccesoExo


class DatabaseExo:
    """Manager de base de datos con soporte multi-tenant AUP-EXO"""
    
    def __init__(self, db_type: str = "sqlite"):
        """
        Inicializa el manager de base de datos
        
        Args:
            db_type: "sqlite" o "postgresql"
        """
        self.db_type = db_type
        self.db_path = "data/axs_exo.db" if db_type == "sqlite" else None
        
        # PostgreSQL config
        self.pg_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "axs_exo"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener conexión a la base de datos"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
        else:
            conn = psycopg2.connect(**self.pg_config, cursor_factory=RealDictCursor)
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch: str = "all"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Ejecuta una query SQL
        
        Args:
            query: Query SQL a ejecutar
            params: Parámetros para la query
            fetch: "all", "one", o "none"
        
        Returns:
            Resultados de la query o None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch == "all":
                return [dict(row) for row in cursor.fetchall()]
            elif fetch == "one":
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                return None
    
    def generar_id(self, prefijo: str = "") -> str:
        """Genera un ID único exógeno"""
        uid = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{prefijo}{timestamp}-{uid}" if prefijo else f"{timestamp}-{uid}"
    
    # ========================================
    # QUERIES CON CONTEXTO JERÁRQUICO
    # ========================================
    
    def query_con_contexto(
        self,
        usuario: ContextoUsuario,
        tabla: str,
        columnas: str = "*",
        condiciones_extra: str = "",
        params: Optional[Tuple] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query SELECT aplicando filtros jerárquicos automáticamente
        
        Args:
            usuario: Contexto del usuario
            tabla: Nombre de la tabla
            columnas: Columnas a seleccionar
            condiciones_extra: Condiciones WHERE adicionales
            params: Parámetros para las condiciones extra
            limit: Límite de resultados
        
        Returns:
            Lista de registros como diccionarios
        """
        # Obtener filtro jerárquico
        where_jerarquico = ControlAccesoExo.obtener_where_clause(usuario)
        
        # Combinar condiciones
        if condiciones_extra:
            where_clause = f"{where_jerarquico} AND {condiciones_extra}"
        else:
            where_clause = where_jerarquico
        
        # Construir query
        query = f"SELECT {columnas} FROM {tabla} WHERE {where_clause}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params, fetch="all")
    
    def insertar_con_contexto(
        self,
        usuario: ContextoUsuario,
        tabla: str,
        datos: Dict[str, Any],
        incluir_msp_condominio: bool = True
    ) -> str:
        """
        Inserta un registro aplicando el contexto jerárquico
        
        Args:
            usuario: Contexto del usuario
            tabla: Nombre de la tabla
            datos: Diccionario con los datos a insertar
            incluir_msp_condominio: Si debe agregar msp_id y condominio_id automáticamente
        
        Returns:
            ID del registro insertado
        """
        # Agregar contexto jerárquico si aplica
        if incluir_msp_condominio:
            if usuario.msp_id and "msp_id" not in datos:
                datos["msp_id"] = usuario.msp_id
            if usuario.condominio_id and "condominio_id" not in datos:
                datos["condominio_id"] = usuario.condominio_id
        
        # Agregar timestamps
        datos["created_at"] = datetime.now().isoformat()
        datos["updated_at"] = datetime.now().isoformat()
        
        # Construir query
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join(["%s"] * len(datos)) if self.db_type == "postgresql" else ", ".join(["?"] * len(datos))
        
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
        
        # Ejecutar
        self.execute_query(query, tuple(datos.values()), fetch="none")
        
        # Retornar ID si existe
        return datos.get("id") or datos.get(f"{tabla[:-4]}_id", "")
    
    def actualizar_con_contexto(
        self,
        usuario: ContextoUsuario,
        tabla: str,
        entidad_id: str,
        nombre_campo_id: str,
        datos: Dict[str, Any]
    ) -> bool:
        """
        Actualiza un registro verificando permisos jerárquicos
        
        Args:
            usuario: Contexto del usuario
            tabla: Nombre de la tabla
            entidad_id: ID de la entidad a actualizar
            nombre_campo_id: Nombre del campo ID (ej: "usuario_id", "condominio_id")
            datos: Datos a actualizar
        
        Returns:
            True si se actualizó, False si no
        """
        # Primero obtener el registro para validar permisos
        query_validacion = f"SELECT msp_id, condominio_id FROM {tabla} WHERE {nombre_campo_id} = %s"
        registro = self.execute_query(
            query_validacion,
            (entidad_id,),
            fetch="one"
        )
        
        if not registro:
            return False
        
        # Validar permisos
        if not ControlAccesoExo.puede_modificar_entidad(
            usuario,
            registro.get("msp_id"),
            registro.get("condominio_id")
        ):
            raise PermissionError(f"Usuario {usuario.usuario_id} no tiene permiso para modificar esta entidad")
        
        # Actualizar timestamp
        datos["updated_at"] = datetime.now().isoformat()
        
        # Construir query
        set_clause = ", ".join([f"{k} = %s" for k in datos.keys()])
        query = f"UPDATE {tabla} SET {set_clause} WHERE {nombre_campo_id} = %s"
        
        # Ejecutar
        params = tuple(list(datos.values()) + [entidad_id])
        self.execute_query(query, params, fetch="none")
        
        return True
    
    # ========================================
    # LEDGER Y AUDITORÍA
    # ========================================
    
    def registrar_auditoria(
        self,
        usuario: ContextoUsuario,
        accion: str,
        entidad: str,
        entidad_id: str,
        detalle: str = "",
        ip_origen: str = "",
        user_agent: str = ""
    ):
        """
        Registra una acción en el ledger de auditoría
        
        Args:
            usuario: Contexto del usuario
            accion: Tipo de acción (CREATE, UPDATE, DELETE, etc.)
            entidad: Nombre de la tabla/entidad
            entidad_id: ID del registro afectado
            detalle: Descripción adicional
            ip_origen: IP del cliente
            user_agent: User agent del cliente
        """
        ledger_id = self.generar_id("LED-")
        
        query = """
        INSERT INTO ledger_exo (
            ledger_id, usuario_id, msp_id, condominio_id,
            accion, entidad, entidad_id, detalle,
            ip_origen, user_agent, timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            ledger_id,
            usuario.usuario_id,
            usuario.msp_id,
            usuario.condominio_id,
            accion,
            entidad,
            entidad_id,
            detalle,
            ip_origen,
            user_agent,
            datetime.now().isoformat()
        )
        
        self.execute_query(query, params, fetch="none")


# Instancia global
db_exo = DatabaseExo(db_type=os.getenv("DB_TYPE", "postgresql"))
