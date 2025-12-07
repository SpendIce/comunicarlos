from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.enums import TipoEvento

class RequerimientoNotifInfo(BaseModel):
    id: int
    titulo: str
    urgencia: Optional[str]

class ResponsableInfo(BaseModel):
    id: int
    nombre: str

class EventoNotifInfo(BaseModel):
    tipo: TipoEvento
    descripcion: str
    requerimiento: RequerimientoNotifInfo
    responsable: ResponsableInfo

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

