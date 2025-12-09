from pydantic import BaseModel, model_validator, Field
from typing import List, Optional, Any
from datetime import datetime
from app.schemas.enums import TipoEvento

class RequerimientoNotifInfo(BaseModel):
    id: int
    titulo: str
    urgencia: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def map_domain(cls, v: Any) -> Any:
        if hasattr(v, 'titulo') and not isinstance(v, dict):
            urgencia = None
            if hasattr(v, 'nivel_urgencia') and v.nivel_urgencia is not None:
                try:
                    urgencia = v.nivel_urgencia.value
                except AttributeError:
                    urgencia = str(v.nivel_urgencia)
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
    @classmethod
    def map_domain(cls, v: Any) -> Any:
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

    @model_validator(mode='before')
    @classmethod
    def map_domain(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            fecha = getattr(v, 'fecha_hora_generada', None)
            if not fecha:
                fecha = getattr(v, 'fecha_creacion', datetime.now())
            return {
                "id": v.id,
                "leida": v.leida,
                "fechaHoraGenerada": fecha,
                "fechaLectura": getattr(v, 'fecha_lectura', None),
                "evento": v.evento
            }
        return v

class PaginatedNotificacionesResponse(BaseModel):
    content: List[NotificacionResponse]
    totalNoLeidas: int
    totalElements: int
    page: int
    size: int

class MarcarLeidasResponse(BaseModel):
    notificacionesMarcadas: int
    mensaje: str

