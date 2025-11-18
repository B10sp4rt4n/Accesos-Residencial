"""
Schemas Pydantic para MSP
Validación de entrada/salida de API
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from datetime import datetime


class MSPCreate(BaseModel):
    """Schema para crear un MSP"""
    msp_id: str = Field(..., min_length=3, max_length=100, description="Identificador único del MSP")
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del MSP")
    razon_social: Optional[str] = Field(None, max_length=200)
    rfc: Optional[str] = Field(None, max_length=20, pattern="^[A-Z0-9]{12,13}$")
    email_contacto: Optional[EmailStr] = None
    telefono_contacto: Optional[str] = Field(None, max_length=20)
    plan: Optional[str] = Field("basic", description="Plan: basic, professional, enterprise")
    max_condominios: Optional[int] = Field(10, ge=1, le=10000)
    configuracion_json: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "msp_id": "msp_telcel_001",
                "nombre": "Telcel Partner CDMX",
                "razon_social": "Telcel Servicios S.A. de C.V.",
                "rfc": "TSE123456ABC",
                "email_contacto": "partners@telcel.com",
                "telefono_contacto": "+52 55 5000 5000",
                "plan": "enterprise",
                "max_condominios": 500
            }
        }


class MSPUpdate(BaseModel):
    """Schema para actualizar un MSP"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    razon_social: Optional[str] = Field(None, max_length=200)
    rfc: Optional[str] = Field(None, max_length=20)
    email_contacto: Optional[EmailStr] = None
    telefono_contacto: Optional[str] = None
    plan: Optional[str] = None
    max_condominios: Optional[int] = Field(None, ge=1, le=10000)
    estado: Optional[str] = Field(None, pattern="^(activo|suspendido|inactivo)$")
    configuracion_json: Optional[Any] = None


class MSPResponse(BaseModel):
    """Schema de respuesta para MSP"""
    msp_id: str
    nombre: str
    razon_social: Optional[str]
    rfc: Optional[str]
    email_contacto: Optional[str]
    telefono_contacto: Optional[str]
    estado: str
    plan: str
    max_condominios: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Reemplaza orm_mode en Pydantic v2


class MSPListResponse(BaseModel):
    """Schema para listado de MSPs"""
    total: int
    msps: list[MSPResponse]
