"""
Schemas Pydantic para Condominio
Validación de entrada/salida de API
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from datetime import datetime


class CondominioCreate(BaseModel):
    """Schema para crear un Condominio"""
    condominio_id: str = Field(..., min_length=3, max_length=100)
    msp_id: str = Field(..., description="MSP al que pertenece")
    nombre: str = Field(..., min_length=3, max_length=200)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    estado_mx: Optional[str] = Field(None, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=10)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    total_unidades: Optional[int] = Field(0, ge=0)
    timezone: Optional[str] = Field("America/Mexico_City", max_length=50)
    configuracion_json: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "condominio_id": "condo_lomas_001",
                "msp_id": "msp_telcel_001",
                "nombre": "Lomas de Chapultepec Residencial",
                "direccion": "Paseo de la Reforma 123",
                "ciudad": "Ciudad de México",
                "estado_mx": "CDMX",
                "codigo_postal": "11000",
                "telefono": "+52 55 1234 5678",
                "email": "admin@lomas.com",
                "total_unidades": 50
            }
        }


class CondominioUpdate(BaseModel):
    """Schema para actualizar un Condominio"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    estado_mx: Optional[str] = None
    codigo_postal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    total_unidades: Optional[int] = Field(None, ge=0)
    estado: Optional[str] = Field(None, pattern="^(activo|suspendido|inactivo)$")
    timezone: Optional[str] = None
    configuracion_json: Optional[Any] = None


class CondominioResponse(BaseModel):
    """Schema de respuesta para Condominio"""
    condominio_id: str
    msp_id: str
    nombre: str
    direccion: Optional[str]
    ciudad: Optional[str]
    estado_mx: Optional[str]
    codigo_postal: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    total_unidades: int
    estado: str
    timezone: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CondominioListResponse(BaseModel):
    """Schema para listado de Condominios"""
    total: int
    condominios: list[CondominioResponse]
