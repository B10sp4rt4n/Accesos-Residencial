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


# ========================================
# MODELOS SQLALCHEMY - AUP-EXO
# ========================================
# Modelos 100% fieles al schema PostgreSQL existente
# Filosofía: Identificadores exógenos (msp_id, condominio_id)
# NO se usan PKs internas para FKs, solo para indexing
# ========================================

try:
    from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
    from sqlalchemy.sql import func
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.dialects.postgresql import JSON
    
    Base = declarative_base()
    
    
    class RolExo(Base):
        """Roles jerárquicos del sistema AUP-EXO"""
        __tablename__ = "roles_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        nombre = Column(String(50), unique=True, nullable=False)
        descripcion = Column(Text, nullable=True)
        nivel = Column(Integer, nullable=False)  # 1:DS, 2:DD, 3:SE, 4:NO
        permisos_json = Column(Text, nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<RolExo(nombre={self.nombre}, nivel={self.nivel})>"
    
    
    class MSPExo(Base):
        """MSPs - Dominio Delegado (DD) - Resellers/Partners"""
        __tablename__ = "msps_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        msp_id = Column(String(100), unique=True, index=True, nullable=False)  # Identificador exógeno
        
        nombre = Column(String(200), nullable=False)
        razon_social = Column(String(200), nullable=True)
        rfc = Column(String(20), nullable=True)
        
        email_contacto = Column(String(200), nullable=True)
        telefono_contacto = Column(String(20), nullable=True)
        
        estado = Column(String(20), default="activo")  # activo, suspendido, inactivo
        plan = Column(String(50), default="basic")  # basic, professional, enterprise
        max_condominios = Column(Integer, default=10)
        
        configuracion_json = Column(Text, nullable=True)  # TEXT en PostgreSQL, se parsea como JSON
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<MSPExo(msp_id={self.msp_id}, nombre={self.nombre}, plan={self.plan})>"
    
    
    class CondominioExo(Base):
        """Condominios - Subdominio Específico (SE) - Clientes finales"""
        __tablename__ = "condominios_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        condominio_id = Column(String(100), unique=True, index=True, nullable=False)  # Identificador exógeno
        
        # FK: Usa msp_id exógeno, NO el PK interno (filosofía AUP-EXO)
        msp_id = Column(
            String(100),
            ForeignKey("msps_exo.msp_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        
        nombre = Column(String(200), nullable=False)
        direccion = Column(Text, nullable=True)
        ciudad = Column(String(100), nullable=True)
        estado_mx = Column(String(100), nullable=True)
        codigo_postal = Column(String(10), nullable=True)
        telefono = Column(String(20), nullable=True)
        email = Column(String(200), nullable=True)
        total_unidades = Column(Integer, default=0)
        
        estado = Column(String(20), default="activo")  # activo, suspendido, inactivo
        timezone = Column(String(50), default="America/Mexico_City")
        
        configuracion_json = Column(Text, nullable=True)
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<CondominioExo(condominio_id={self.condominio_id}, nombre={self.nombre}, msp={self.msp_id})>"
    
    
    class UsuarioExo(Base):
        """Usuarios multinivel con scope jerárquico"""
        __tablename__ = "usuarios_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        usuario_id = Column(String(100), unique=True, index=True, nullable=False)
        
        nombre = Column(String(200), nullable=False)
        email = Column(String(200), unique=True, index=True, nullable=False)
        password_hash = Column(String(255), nullable=False)
        
        rol_id = Column(Integer, ForeignKey("roles_exo.id"), nullable=False, index=True)
        
        # FKs exógenos: NULL para Super Admin
        msp_id = Column(
            String(100),
            ForeignKey("msps_exo.msp_id", ondelete="RESTRICT"),
            nullable=True,
            index=True
        )
        condominio_id = Column(
            String(100),
            ForeignKey("condominios_exo.condominio_id", ondelete="RESTRICT"),
            nullable=True,
            index=True
        )
        
        estado = Column(String(20), default="activo", index=True)
        ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<UsuarioExo(usuario_id={self.usuario_id}, email={self.email}, rol_id={self.rol_id})>"
    
    
    class ResidenciaExo(Base):
        """Unidades habitacionales dentro de condominios"""
        __tablename__ = "residencias_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        residencia_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FK exógeno
        condominio_id = Column(
            String(100),
            ForeignKey("condominios_exo.condominio_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        
        numero = Column(String(50), nullable=False, index=True)
        propietario = Column(String(200), nullable=True)
        telefono = Column(String(20), nullable=True)
        email = Column(String(200), nullable=True)
        
        estado = Column(String(20), default="activo", index=True)
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<ResidenciaExo(residencia_id={self.residencia_id}, numero={self.numero}, condominio={self.condominio_id})>"
    
    
    class ResidenteExo(Base):
        """Personas que habitan las residencias"""
        __tablename__ = "residentes_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        residente_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FK exógeno
        residencia_id = Column(
            String(100),
            ForeignKey("residencias_exo.residencia_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        
        nombre = Column(String(200), nullable=False, index=True)
        telefono = Column(String(20), nullable=True)
        email = Column(String(200), nullable=True)
        tipo = Column(String(50), default="residente")  # residente, inquilino, familiar
        
        estado = Column(String(20), default="activo", index=True)
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<ResidenteExo(residente_id={self.residente_id}, nombre={self.nombre})>"
    
    
    class VisitanteExo(Base):
        """Visitas programadas con QR y control de acceso"""
        __tablename__ = "visitantes_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        visitante_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FKs exógenos
        condominio_id = Column(
            String(100),
            ForeignKey("condominios_exo.condominio_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        residencia_id = Column(
            String(100),
            ForeignKey("residencias_exo.residencia_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        
        nombre = Column(String(200), nullable=False)
        telefono = Column(String(20), nullable=True)
        tipo_visita = Column(String(50), nullable=True)  # proveedor, invitado, familiar, delivery
        
        fecha_autorizacion = Column(DateTime(timezone=True), server_default=func.now())
        fecha_expiracion = Column(DateTime(timezone=True), nullable=True, index=True)
        
        qr_code = Column(String(200), nullable=True, index=True)
        qr_usado = Column(Boolean, default=False)
        
        estado = Column(String(20), default="pendiente", index=True)  # pendiente, activo, expirado, usado
        observaciones = Column(Text, nullable=True)
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<VisitanteExo(visitante_id={self.visitante_id}, nombre={self.nombre}, estado={self.estado})>"
    
    
    class AccesoExo(Base):
        """Bitácora universal de entradas y salidas (NO - Nodo Operativo)"""
        __tablename__ = "accesos_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        acceso_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FKs exógenos (nullable para visitante o residente)
        visitante_id = Column(
            String(100),
            ForeignKey("visitantes_exo.visitante_id"),
            nullable=True,
            index=True
        )
        residente_id = Column(
            String(100),
            ForeignKey("residentes_exo.residente_id"),
            nullable=True,
            index=True
        )
        usuario_operador_id = Column(
            String(100),
            ForeignKey("usuarios_exo.usuario_id"),
            nullable=True
        )
        condominio_id = Column(
            String(100),
            ForeignKey("condominios_exo.condominio_id", ondelete="RESTRICT"),
            nullable=False,
            index=True
        )
        
        tipo_acceso = Column(String(20), nullable=False, index=True)  # entrada, salida
        metodo = Column(String(50), nullable=False)  # qr, manual, placa, reconocimiento_facial
        timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
        resultado = Column(String(20), nullable=False, index=True)  # permitido, denegado
        
        comentario = Column(Text, nullable=True)
        metadata_json = Column(Text, nullable=True)  # Datos adicionales (placas, fotos, etc.)
        
        def __repr__(self):
            return f"<AccesoExo(acceso_id={self.acceso_id}, tipo={self.tipo_acceso}, resultado={self.resultado})>"
    
    
    class ReglaExo(Base):
        """Reglas de operación por condominio"""
        __tablename__ = "reglas_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        regla_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FK exógeno
        condominio_id = Column(
            String(100),
            ForeignKey("condominios_exo.condominio_id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )
        
        regla_nombre = Column(String(100), nullable=False)
        regla_tipo = Column(String(50), nullable=False)  # horario, autorizacion, alertas
        regla_valor = Column(Text, nullable=False)  # JSON serializado
        
        estado = Column(String(20), default="activa")
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<ReglaExo(regla_id={self.regla_id}, nombre={self.regla_nombre}, tipo={self.regla_tipo})>"
    
    
    class PlaybookExo(Base):
        """Plantillas predefinidas por vertical/industria"""
        __tablename__ = "playbooks_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        playbook_id = Column(String(100), unique=True, index=True, nullable=False)
        
        nombre = Column(String(100), nullable=False)
        vertical = Column(String(50), nullable=False, index=True)  # residencial, corporativo, industrial
        descripcion = Column(Text, nullable=True)
        configuracion_json = Column(Text, nullable=False)  # Configuración completa del playbook
        
        estado = Column(String(20), default="activo")
        
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        
        def __repr__(self):
            return f"<PlaybookExo(playbook_id={self.playbook_id}, nombre={self.nombre}, vertical={self.vertical})>"
    
    
    class LedgerExo(Base):
        """Ledger universal de auditoría (inmutable, append-only)"""
        __tablename__ = "ledger_exo"
        
        id = Column(Integer, primary_key=True, index=True)
        ledger_id = Column(String(100), unique=True, index=True, nullable=False)
        
        # FKs exógenos
        usuario_id = Column(String(100), nullable=True, index=True)
        msp_id = Column(String(100), nullable=True, index=True)
        condominio_id = Column(String(100), nullable=True, index=True)
        
        accion = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE, ACCESS
        entidad = Column(String(100), nullable=False, index=True)  # msps_exo, condominios_exo, etc.
        entidad_id = Column(String(100), nullable=True)
        
        detalle = Column(Text, nullable=True)  # JSON con before/after
        ip_origen = Column(String(50), nullable=True)
        user_agent = Column(Text, nullable=True)
        
        timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
        
        def __repr__(self):
            return f"<LedgerExo(ledger_id={self.ledger_id}, accion={self.accion}, entidad={self.entidad})>"
    
    
    # Exportar modelos
    __all__ = [
        'Base',
        'RolExo',
        'MSPExo',
        'CondominioExo',
        'UsuarioExo',
        'ResidenciaExo',
        'ResidenteExo',
        'VisitanteExo',
        'AccesoExo',
        'ReglaExo',
        'PlaybookExo',
        'LedgerExo',
    ]

except ImportError:
    # SQLAlchemy no instalado, los modelos no estarán disponibles
    # El resto del módulo (DatabaseExo) funciona con psycopg2 nativo
    Base = None
    print("⚠️  SQLAlchemy no disponible. Modelos ORM deshabilitados. Usando psycopg2 nativo.")
