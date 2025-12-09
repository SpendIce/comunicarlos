from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Optional, Any
from datetime import datetime, date
from app.schemas.enums import TipoServicio

class ServicioResponse(BaseModel):
    id: int
    tipo: TipoServicio
    numero_servicio: str
    activo: bool
    fecha_alta: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def map_domain(cls, v: Any) -> Any:
        # Mapeo manual Entidad Servicio -> Schema
        if hasattr(v, 'numero_servicio') and not isinstance(v, dict):
            return {
                "id": v.id,
                "tipo": v.tipo,
                "numero_servicio": v.numero_servicio,
                "activo": v.activo,
                "fecha_alta": getattr(v, 'fecha_alta', None)
            }
        return v

class MisServiciosResponse(BaseModel):
    servicios: List[ServicioResponse]

class SolicitarAltaRequest(BaseModel):
    tipo_servicio: TipoServicio = Field(..., description="Tipo de servicio a dar de alta")
    plan_deseado: str = Field(..., min_length=5, max_length=100, description="Plan o paquete deseado")
    direccion_instalacion: str = Field(..., min_length=10, max_length=200, description="Dirección de instalación")
    comentarios: Optional[str] = Field(None, max_length=500, description="Comentarios adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "tipo_servicio": "TELEVISION",
                "plan_deseado": "Plan HD Premium",
                "direccion_instalacion": "Av. San Martín 1234, Neuquén Capital",
                "comentarios": "Preferencia de instalación por la mañana"
            }
        }

class SolicitarBajaRequest(BaseModel):
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de la baja")
    fecha_deseada_baja: date = Field(..., description="Fecha deseada para la baja")
    comentarios: Optional[str] = Field(None, max_length=500, description="Comentarios adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "motivo": "Me mudo a otra provincia",
                "fecha_deseada_baja": "2025-12-31",
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
