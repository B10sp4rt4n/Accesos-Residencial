"""
Router de MSP - Endpoints FastAPI
Manejo de requests HTTP para MSPs
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.schemas.msp import (
    MSPCreate,
    MSPUpdate,
    MSPResponse,
    MSPListResponse
)
from app.services import msp_service

router = APIRouter(prefix="/msp", tags=["MSP - Managed Service Providers"])


@router.post(
    "/crear",
    response_model=MSPResponse,
    status_code=201,
    summary="Crear un nuevo MSP",
    description="Registra un nuevo Managed Service Provider en el sistema"
)
def create_msp(
    data: MSPCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo MSP
    
    - **msp_id**: Identificador único (ej: msp_telcel_001)
    - **nombre**: Nombre del MSP
    - **plan**: basic, professional, enterprise
    - **max_condominios**: Límite de condominios permitidos
    """
    return msp_service.crear_msp(db, data)


@router.get(
    "/listar",
    response_model=MSPListResponse,
    summary="Listar MSPs",
    description="Obtiene listado de MSPs con paginación y filtros"
)
def list_msps(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: activo, suspendido, inactivo"),
    db: Session = Depends(get_db)
):
    """
    Listar MSPs con paginación
    
    - **skip**: Paginación - registros a saltar
    - **limit**: Paginación - máximo de registros
    - **estado**: Filtro opcional por estado
    """
    msps = msp_service.listar_msps(db, skip=skip, limit=limit, estado=estado)
    total = msp_service.contar_msps(db, estado=estado)
    
    return MSPListResponse(total=total, msps=msps)


@router.get(
    "/{msp_id}",
    response_model=MSPResponse,
    summary="Obtener MSP por ID",
    description="Consulta los detalles de un MSP específico"
)
def get_msp(
    msp_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener un MSP por su identificador único
    
    - **msp_id**: Identificador del MSP (ej: msp_telcel_001)
    """
    return msp_service.obtener_msp(db, msp_id)


@router.put(
    "/{msp_id}",
    response_model=MSPResponse,
    summary="Actualizar MSP",
    description="Modifica los datos de un MSP existente"
)
def update_msp(
    msp_id: str,
    data: MSPUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un MSP existente
    
    - Solo se actualizan los campos proporcionados
    - Los demás campos permanecen sin cambios
    """
    return msp_service.actualizar_msp(db, msp_id, data)


@router.delete(
    "/{msp_id}",
    summary="Eliminar MSP",
    description="Marca un MSP como inactivo (soft delete)"
)
def delete_msp(
    msp_id: str,
    db: Session = Depends(get_db)
):
    """
    Eliminar un MSP (soft delete)
    
    - Cambia el estado a 'inactivo'
    - No se permite si tiene condominios activos
    """
    return msp_service.eliminar_msp(db, msp_id)


@router.get(
    "/{msp_id}/estadisticas",
    summary="Estadísticas del MSP",
    description="Obtiene métricas y estadísticas de un MSP"
)
def get_msp_stats(
    msp_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de un MSP
    
    - Total de condominios
    - Condominios activos
    - Condominios disponibles
    - Total de usuarios
    """
    return msp_service.obtener_estadisticas_msp(db, msp_id)
