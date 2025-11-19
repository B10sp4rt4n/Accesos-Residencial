"""
Servicio de Condominio - Lógica de negocio pura
Manejo de operaciones CRUD para Condominios
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List, Optional

from core.db_exo import CondominioExo, MSPExo
from app.schemas.condominio import CondominioCreate, CondominioUpdate


def crear_condominio(db: Session, data: CondominioCreate) -> CondominioExo:
    """
    Crear un nuevo Condominio
    
    Args:
        db: Sesión de base de datos
        data: Datos del condominio a crear
        
    Returns:
        CondominioExo: Condominio creado
        
    Raises:
        HTTPException: Si el condominio ya existe o MSP no existe
    """
    # Validar que el MSP exista
    msp = db.query(MSPExo).filter_by(msp_id=data.msp_id).first()
    if not msp:
        raise HTTPException(
            status_code=404,
            detail=f"MSP con msp_id '{data.msp_id}' no encontrado"
        )
    
    # Validar límite de condominios del MSP
    total_condominios = db.query(CondominioExo).filter_by(msp_id=data.msp_id).count()
    if total_condominios >= msp.max_condominios:
        raise HTTPException(
            status_code=400,
            detail=f"MSP '{data.msp_id}' ha alcanzado su límite de {msp.max_condominios} condominios"
        )
    
    # Validar si el condominio ya existe
    existing = db.query(CondominioExo).filter_by(condominio_id=data.condominio_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"El condominio con condominio_id '{data.condominio_id}' ya existe"
        )
    
    try:
        # Convertir configuracion_json a string si es dict
        config_json = data.configuracion_json
        if isinstance(config_json, dict):
            import json
            config_json = json.dumps(config_json)
        
        new_condo = CondominioExo(
            condominio_id=data.condominio_id,
            msp_id=data.msp_id,
            nombre=data.nombre,
            direccion=data.direccion,
            ciudad=data.ciudad,
            estado_mx=data.estado_mx,
            codigo_postal=data.codigo_postal,
            telefono=data.telefono,
            email=data.email,
            total_unidades=data.total_unidades,
            timezone=data.timezone,
            configuracion_json=config_json
        )
        
        db.add(new_condo)
        db.commit()
        db.refresh(new_condo)
        
        return new_condo
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")


def listar_condominios(
    db: Session,
    msp_id: Optional[str] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[CondominioExo]:
    """
    Listar condominios con filtros y paginación
    
    Args:
        db: Sesión de base de datos
        msp_id: Filtrar por MSP (scope multi-tenant)
        estado: Filtrar por estado
        skip: Número de registros a saltar
        limit: Número máximo de registros
        
    Returns:
        List[CondominioExo]: Lista de condominios
    """
    query = db.query(CondominioExo)
    
    if msp_id:
        query = query.filter(CondominioExo.msp_id == msp_id)
    
    if estado:
        query = query.filter(CondominioExo.estado == estado)
    
    return query.offset(skip).limit(limit).all()


def contar_condominios(
    db: Session,
    msp_id: Optional[str] = None,
    estado: Optional[str] = None
) -> int:
    """Contar total de condominios con filtros"""
    query = db.query(CondominioExo)
    
    if msp_id:
        query = query.filter(CondominioExo.msp_id == msp_id)
    
    if estado:
        query = query.filter(CondominioExo.estado == estado)
    
    return query.count()


def obtener_condominio(db: Session, condominio_id: str) -> CondominioExo:
    """
    Obtener un condominio por su ID
    
    Args:
        db: Sesión de base de datos
        condominio_id: Identificador del condominio
        
    Returns:
        CondominioExo: Condominio encontrado
        
    Raises:
        HTTPException: Si no se encuentra
    """
    condo = db.query(CondominioExo).filter_by(condominio_id=condominio_id).first()
    
    if not condo:
        raise HTTPException(
            status_code=404,
            detail=f"Condominio con condominio_id '{condominio_id}' no encontrado"
        )
    
    return condo


def actualizar_condominio(
    db: Session,
    condominio_id: str,
    data: CondominioUpdate
) -> CondominioExo:
    """
    Actualizar un condominio existente
    
    Args:
        db: Sesión de base de datos
        condominio_id: Identificador del condominio
        data: Datos a actualizar
        
    Returns:
        CondominioExo: Condominio actualizado
    """
    condo = obtener_condominio(db, condominio_id)
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Convertir configuracion_json si es necesario
    if 'configuracion_json' in update_data and isinstance(update_data['configuracion_json'], dict):
        import json
        update_data['configuracion_json'] = json.dumps(update_data['configuracion_json'])
    
    for field, value in update_data.items():
        setattr(condo, field, value)
    
    try:
        db.commit()
        db.refresh(condo)
        return condo
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e)}")


def eliminar_condominio(db: Session, condominio_id: str) -> dict:
    """
    Eliminar un condominio (soft delete)
    
    Args:
        db: Sesión de base de datos
        condominio_id: Identificador del condominio
        
    Returns:
        dict: Mensaje de confirmación
    """
    condo = obtener_condominio(db, condominio_id)
    
    # Verificar si tiene residencias activas
    from core.db_exo import ResidenciaExo
    residencias_activas = db.query(ResidenciaExo).filter_by(
        condominio_id=condominio_id,
        estado="activo"
    ).count()
    
    if residencias_activas > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar. Tiene {residencias_activas} residencias activas"
        )
    
    # Soft delete
    condo.estado = "inactivo"
    db.commit()
    
    return {"message": f"Condominio '{condominio_id}' marcado como inactivo"}


def obtener_estadisticas_condominio(db: Session, condominio_id: str) -> dict:
    """
    Obtener estadísticas de un condominio
    
    Args:
        db: Sesión de base de datos
        condominio_id: Identificador del condominio
        
    Returns:
        dict: Estadísticas del condominio
    """
    condo = obtener_condominio(db, condominio_id)
    
    from core.db_exo import ResidenciaExo, ResidenteExo, VisitanteExo, AccesoExo
    from datetime import datetime, timedelta
    
    # Contar residencias
    total_residencias = db.query(ResidenciaExo).filter_by(
        condominio_id=condominio_id
    ).count()
    
    # Contar residentes
    residencias_ids = [r.residencia_id for r in db.query(ResidenciaExo).filter_by(
        condominio_id=condominio_id
    ).all()]
    
    total_residentes = 0
    if residencias_ids:
        total_residentes = db.query(ResidenteExo).filter(
            ResidenteExo.residencia_id.in_(residencias_ids)
        ).count()
    
    # Contar visitantes activos
    visitantes_activos = db.query(VisitanteExo).filter_by(
        condominio_id=condominio_id,
        estado="activo"
    ).count()
    
    # Accesos hoy
    hoy = datetime.now().date()
    accesos_hoy = db.query(AccesoExo).filter(
        AccesoExo.condominio_id == condominio_id,
        AccesoExo.timestamp >= hoy
    ).count()
    
    return {
        "condominio_id": condominio_id,
        "nombre": condo.nombre,
        "msp_id": condo.msp_id,
        "total_unidades": condo.total_unidades,
        "total_residencias": total_residencias,
        "total_residentes": total_residentes,
        "visitantes_activos": visitantes_activos,
        "accesos_hoy": accesos_hoy,
        "estado": condo.estado
    }
