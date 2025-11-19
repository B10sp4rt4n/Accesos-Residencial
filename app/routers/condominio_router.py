"""
Router de Condominio - Endpoints FastAPI
Manejo de requests HTTP para Condominios
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.schemas.condominio import (
    CondominioCreate,
    CondominioUpdate,
    CondominioResponse,
    CondominioListResponse
)
from app.services import condominio_service

router = APIRouter(prefix="/condominio", tags=["Condominios"])


@router.post(
    "/crear",
    response_model=CondominioResponse,
    status_code=201,
    summary="Crear un nuevo Condominio",
    description="Registra un nuevo condominio bajo un MSP"
)
def create_condominio(
    data: CondominioCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo Condominio
    
    - **condominio_id**: Identificador único (ej: condo_lomas_001)
    - **msp_id**: MSP al que pertenece
    - **nombre**: Nombre del condominio
    - **total_unidades**: Número de casas/unidades
    """
    return condominio_service.crear_condominio(db, data)


@router.get(
    "/listar",
    response_model=CondominioListResponse,
    summary="Listar Condominios",
    description="Obtiene listado de condominios con paginación y filtros"
)
def list_condominios(
    msp_id: Optional[str] = Query(None, description="Filtrar por MSP (scope multi-tenant)"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Listar Condominios con filtros
    
    - **msp_id**: Filtrar por MSP (multi-tenant scope)
    - **estado**: Filtrar por estado
    - **skip**: Paginación
    - **limit**: Máximo de registros
    """
    condominios = condominio_service.listar_condominios(
        db,
        msp_id=msp_id,
        estado=estado,
        skip=skip,
        limit=limit
    )
    total = condominio_service.contar_condominios(db, msp_id=msp_id, estado=estado)
    
    return CondominioListResponse(total=total, condominios=condominios)


@router.get(
    "/{condominio_id}",
    response_model=CondominioResponse,
    summary="Obtener Condominio por ID",
    description="Consulta los detalles de un condominio específico"
)
def get_condominio(
    condominio_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener un Condominio por su identificador
    
    - **condominio_id**: Identificador del condominio
    """
    return condominio_service.obtener_condominio(db, condominio_id)


@router.put(
    "/{condominio_id}",
    response_model=CondominioResponse,
    summary="Actualizar Condominio",
    description="Modifica los datos de un condominio existente"
)
def update_condominio(
    condominio_id: str,
    data: CondominioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un Condominio
    
    - Solo se actualizan los campos proporcionados
    """
    return condominio_service.actualizar_condominio(db, condominio_id, data)


@router.delete(
    "/{condominio_id}",
    summary="Eliminar Condominio",
    description="Marca un condominio como inactivo (soft delete)"
)
def delete_condominio(
    condominio_id: str,
    db: Session = Depends(get_db)
):
    """
    Eliminar un Condominio (soft delete)
    
    - No se permite si tiene residencias activas
    """
    return condominio_service.eliminar_condominio(db, condominio_id)


@router.get(
    "/{condominio_id}/estadisticas",
    summary="Estadísticas del Condominio",
    description="Obtiene métricas y estadísticas de un condominio"
)
def get_condominio_stats(
    condominio_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de un Condominio
    
    - Total de residencias
    - Total de residentes
    - Visitantes activos
    - Accesos del día
    """
    return condominio_service.obtener_estadisticas_condominio(db, condominio_id)
