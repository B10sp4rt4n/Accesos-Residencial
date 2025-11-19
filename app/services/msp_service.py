"""
Servicio de MSP - Lógica de negocio pura
Manejo de operaciones CRUD para MSPs
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional

from core.db_exo import MSPExo
from app.schemas.msp import MSPCreate, MSPUpdate


def crear_msp(db: Session, data: MSPCreate) -> MSPExo:
    """
    Crear un nuevo MSP
    
    Args:
        db: Sesión de base de datos
        data: Datos del MSP a crear
        
    Returns:
        MSPExo: MSP creado
        
    Raises:
        HTTPException: Si el MSP ya existe
    """
    # Validar si ya existe
    existing = db.query(MSPExo).filter_by(msp_id=data.msp_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"El MSP con msp_id '{data.msp_id}' ya existe"
        )
    
    try:
        # Convertir configuracion_json a string si es dict
        config_json = data.configuracion_json
        if isinstance(config_json, dict):
            import json
            config_json = json.dumps(config_json)
        
        new_msp = MSPExo(
            msp_id=data.msp_id,
            nombre=data.nombre,
            razon_social=data.razon_social,
            rfc=data.rfc,
            email_contacto=data.email_contacto,
            telefono_contacto=data.telefono_contacto,
            plan=data.plan,
            max_condominios=data.max_condominios,
            configuracion_json=config_json
        )
        
        db.add(new_msp)
        db.commit()
        db.refresh(new_msp)
        
        return new_msp
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")


def listar_msps(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None
) -> List[MSPExo]:
    """
    Listar MSPs con paginación y filtros
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        estado: Filtrar por estado (activo, suspendido, inactivo)
        
    Returns:
        List[MSPExo]: Lista de MSPs
    """
    query = db.query(MSPExo)
    
    if estado:
        query = query.filter(MSPExo.estado == estado)
    
    return query.offset(skip).limit(limit).all()


def contar_msps(db: Session, estado: Optional[str] = None) -> int:
    """Contar total de MSPs"""
    query = db.query(MSPExo)
    if estado:
        query = query.filter(MSPExo.estado == estado)
    return query.count()


def obtener_msp(db: Session, msp_id: str) -> MSPExo:
    """
    Obtener un MSP por su ID
    
    Args:
        db: Sesión de base de datos
        msp_id: Identificador del MSP
        
    Returns:
        MSPExo: MSP encontrado
        
    Raises:
        HTTPException: Si no se encuentra el MSP
    """
    msp = db.query(MSPExo).filter_by(msp_id=msp_id).first()
    
    if not msp:
        raise HTTPException(
            status_code=404,
            detail=f"MSP con msp_id '{msp_id}' no encontrado"
        )
    
    return msp


def actualizar_msp(db: Session, msp_id: str, data: MSPUpdate) -> MSPExo:
    """
    Actualizar un MSP existente
    
    Args:
        db: Sesión de base de datos
        msp_id: Identificador del MSP
        data: Datos a actualizar
        
    Returns:
        MSPExo: MSP actualizado
        
    Raises:
        HTTPException: Si no se encuentra el MSP
    """
    msp = obtener_msp(db, msp_id)
    
    # Actualizar solo los campos proporcionados
    update_data = data.model_dump(exclude_unset=True)
    
    # Convertir configuracion_json si es necesario
    if 'configuracion_json' in update_data and isinstance(update_data['configuracion_json'], dict):
        import json
        update_data['configuracion_json'] = json.dumps(update_data['configuracion_json'])
    
    for field, value in update_data.items():
        setattr(msp, field, value)
    
    try:
        db.commit()
        db.refresh(msp)
        return msp
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")


def eliminar_msp(db: Session, msp_id: str) -> dict:
    """
    Eliminar un MSP (soft delete cambiando estado a 'inactivo')
    
    Args:
        db: Sesión de base de datos
        msp_id: Identificador del MSP
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si no se encuentra el MSP o tiene condominios activos
    """
    msp = obtener_msp(db, msp_id)
    
    # Verificar si tiene condominios activos
    from core.db_exo import CondominioExo
    condominios_activos = db.query(CondominioExo).filter_by(
        msp_id=msp_id,
        estado="activo"
    ).count()
    
    if condominios_activos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el MSP. Tiene {condominios_activos} condominios activos"
        )
    
    # Soft delete
    msp.estado = "inactivo"
    db.commit()
    
    return {"message": f"MSP '{msp_id}' marcado como inactivo"}


def obtener_estadisticas_msp(db: Session, msp_id: str) -> dict:
    """
    Obtener estadísticas de un MSP
    
    Args:
        db: Sesión de base de datos
        msp_id: Identificador del MSP
        
    Returns:
        dict: Estadísticas del MSP
    """
    msp = obtener_msp(db, msp_id)
    
    from core.db_exo import CondominioExo, UsuarioExo
    
    # Contar condominios
    total_condominios = db.query(CondominioExo).filter_by(msp_id=msp_id).count()
    condominios_activos = db.query(CondominioExo).filter_by(
        msp_id=msp_id,
        estado="activo"
    ).count()
    
    # Contar usuarios
    total_usuarios = db.query(UsuarioExo).filter_by(msp_id=msp_id).count()
    
    return {
        "msp_id": msp_id,
        "nombre": msp.nombre,
        "plan": msp.plan,
        "max_condominios": msp.max_condominios,
        "total_condominios": total_condominios,
        "condominios_activos": condominios_activos,
        "condominios_disponibles": msp.max_condominios - total_condominios,
        "total_usuarios": total_usuarios,
        "estado": msp.estado
    }
