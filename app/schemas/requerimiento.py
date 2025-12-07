from pydantic import BaseModel, Field, validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from app.schemas.enums import (
    TipoRequerimiento, EstadoRequerimiento, NivelUrgencia,
    CategoriaIncidente, CategoriaSolicitud
)

class CrearRequerimientoRequest(BaseModel):
    tipo: TipoRequerimiento = Field(..., description="INCIDENTE o SOLICITUD")
    titulo: str = Field(..., min_length=5, max_length=200, description="Título del requerimiento")
    descripcion: str = Field(..., min_length=10, max_length=2000, description="Descripción detallada")
    categoria: str = Field(..., description="Categoría del requerimiento")
    nivelUrgencia: Optional[NivelUrgencia] = Field(None, description="Urgencia (solo para INCIDENTE)")

    @validator('nivelUrgencia')
    def validar_urgencia_incidente(cls, v, values):
        if 'tipo' in values:
            if values['tipo'] == TipoRequerimiento.INCIDENTE and v is None:
                raise ValueError('nivelUrgencia es requerido para INCIDENTE')
            if values['tipo'] == TipoRequerimiento.SOLICITUD and v is not None:
                raise ValueError('nivelUrgencia no debe especificarse para SOLICITUD')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "INCIDENTE",
                "titulo": "No puedo realizar llamadas",
                "descripcion": "Desde esta mañana mi celular no puede realizar llamadas salientes",
                "categoria": "SERVICIO_INACCESIBLE",
                "nivelUrgencia": "CRITICO"
            }
        }

class SolicitanteInfo(BaseModel):
    id: int
    nombre: str
    email: str

class TecnicoInfo(BaseModel):
    id: int
    nombre: str
    email: str

class ComentarioInfo(BaseModel):
    id: int
    texto: str
    autor: dict
    fechaHora: datetime

class EventoInfo(BaseModel):
    id: int
    tipo: str
    descripcion: str
    responsable: dict
    fechaHora: datetime
    detalles: Optional[dict] = None

class RequerimientoResponse(BaseModel):
    id: int
    tipo: TipoRequerimiento
    titulo: str
    descripcion: str
    categoria: str
    nivelUrgencia: Optional[NivelUrgencia]
    estado: EstadoRequerimiento
    prioridad: int
    solicitante: SolicitanteInfo
    tecnicoAsignado: Optional[TecnicoInfo]
    fechaCreacion: datetime
    fechaResolucion: Optional[datetime]
    diasDesdeCreacion: int
    comentarios: List[ComentarioInfo] = []
    eventos: List[EventoInfo] = []

    class Config:
        from_attributes = True

class RequerimientoListaResponse(BaseModel):
    id: int
    tipo: TipoRequerimiento
    titulo: str
    categoria: str
    nivelUrgencia: Optional[NivelUrgencia]
    estado: EstadoRequerimiento
    prioridad: int
    solicitante: SolicitanteInfo
    tecnicoAsignado: Optional[TecnicoInfo]
    fechaCreacion: datetime
    diasDesdeCreacion: int

    class Config:
        from_attributes = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    content: List[T]
    page: int
    size: int
    totalElements: int
    totalPages: int
    isFirst: bool
    isLast: bool

class ResolverRequerimientoRequest(BaseModel):
    comentarioResolucion: Optional[str] = Field(None, min_length=10, max_length=1000, description="Comentario de resolución")

    class Config:
        json_schema_extra = {
            "example": {
                "comentarioResolucion": "Se reinició el servicio. La línea está operativa nuevamente."
            }
        }

class ReabrirRequerimientoRequest(BaseModel):
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de reapertura")

    class Config:
        json_schema_extra = {
            "example": {
                "motivo": "El problema persiste. El cliente reporta que sigue sin servicio."
            }
        }
