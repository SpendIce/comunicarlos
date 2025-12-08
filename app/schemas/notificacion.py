from pydantic import BaseModel, model_validator
from typing import List, Optional
from datetime import datetime
from app.schemas.enums import TipoEvento

class RequerimientoNotifInfo(BaseModel):
    id: int
    titulo: str
    urgencia: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'titulo') and not isinstance(v, dict):
            urgencia = None
            if hasattr(v, 'nivel_urgencia'):
                urgencia = v.nivel_urgencia.value
            return {
                "id": v.id,
                "titulo": v.titulo,
                "urgencia": urgencia
            }
        return v


class ResponsableInfo(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class EventoNotifInfo(BaseModel):
    tipo: TipoEvento
    descripcion: str
    requerimiento: RequerimientoNotifInfo
    responsable: ResponsableInfo

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'get_tipo_evento') and not isinstance(v, dict):
            return {
                "tipo": v.get_tipo_evento(),
                "descripcion": v.descripcion,
                "requerimiento": v.requerimiento,
                "responsable": v.responsable
            }
        return v

class NotificacionResponse(BaseModel):
    id: int
    leida: bool
    fechaHoraGenerada: datetime
    fechaLectura: Optional[datetime]
    evento: EventoNotifInfo

    class Config:
        from_attributes = True

class PaginatedNotificacionesResponse(BaseModel):
    content: List[NotificacionResponse]
    totalNoLeidas: int
    totalElements: int
    page: int
    size: int

class MarcarLeidasResponse(BaseModel):
    notificacionesMarcadas: int
    mensaje: str

