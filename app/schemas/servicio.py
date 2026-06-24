from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.enums import TipoServicio

class ServicioCreate(BaseModel):
    """Datos necesarios para contratar un servicio."""
    tipo: TipoServicio
    numero_servicio: str = Field(..., min_length=5, description="Identificador técnico del servicio")

class ServicioRead(BaseModel):
    """Representación pública de un servicio contratado."""
    id: int
    tipo: TipoServicio
    numero_servicio: str
    activo: bool
    fecha_alta: datetime

    class Config:
        from_attributes = True