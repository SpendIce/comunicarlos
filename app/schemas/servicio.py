from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from app.schemas.enums import TipoServicio

class ServicioResponse(BaseModel):
    id: int
    tipo: TipoServicio
    numeroServicio: str
    activo: bool
    fechaAlta: datetime
    incidentesActivos: int = 0
    ultimoIncidente: Optional[datetime] = None

    class Config:
        from_attributes = True

class MisServiciosResponse(BaseModel):
    servicios: List[ServicioResponse]

class SolicitarAltaRequest(BaseModel):
    tipoServicio: TipoServicio = Field(..., description="Tipo de servicio a dar de alta")
    planDeseado: str = Field(..., min_length=5, max_length=100, description="Plan o paquete deseado")
    direccionInstalacion: str = Field(..., min_length=10, max_length=200, description="Dirección de instalación")
    comentarios: Optional[str] = Field(None, max_length=500, description="Comentarios adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "tipoServicio": "TELEVISION",
                "planDeseado": "Plan HD Premium",
                "direccionInstalacion": "Av. San Martín 1234, Neuquén Capital",
                "comentarios": "Preferencia de instalación por la mañana"
            }
        }

class SolicitarBajaRequest(BaseModel):
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de la baja")
    fechaDeseadaBaja: date = Field(..., description="Fecha deseada para la baja")
    comentarios: Optional[str] = Field(None, max_length=500, description="Comentarios adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "motivo": "Me mudo a otra provincia",
                "fechaDeseadaBaja": "2025-12-31",
                "comentarios": "Solicito portabilidad de número"
            }
        }

class RequerimientoBasicInfo(BaseModel):
    id: int
    tipo: str
    titulo: str
    categoria: str
    estado: str

class SolicitudServicioResponse(BaseModel):
    requerimiento: RequerimientoBasicInfo
    servicio: Optional[dict] = None
    mensaje: str
