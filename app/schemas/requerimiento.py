from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Generic, TypeVar, Any
from datetime import datetime
from app.schemas.enums import (
    TipoRequerimiento, EstadoRequerimiento, NivelUrgencia
)

class CrearRequerimientoRequest(BaseModel):
    tipo: TipoRequerimiento = Field(..., description="INCIDENTE o SOLICITUD")
    titulo: str = Field(..., min_length=5, max_length=200, description="Título del requerimiento")
    descripcion: str = Field(..., min_length=10, max_length=2000, description="Descripción detallada")
    categoria: str = Field(..., description="Categoría del requerimiento")
    nivel_urgencia: Optional[NivelUrgencia] = Field(None, description="Urgencia (solo para INCIDENTE)")

    @field_validator('nivel_urgencia')
    @classmethod
    def validar_urgencia_incidente(cls, v, info):
        values = info.data
        if 'tipo' in values:
            if values['tipo'] == TipoRequerimiento.INCIDENTE and v is None:
                raise ValueError('nivel_urgencia es requerido para INCIDENTE')
            if values['tipo'] == TipoRequerimiento.SOLICITUD and v is not None:
                raise ValueError('nivel_urgencia no debe especificarse para SOLICITUD')
        return v

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "tipo": "INCIDENTE",
                "titulo": "No puedo realizar llamadas",
                "descripcion": "Desde esta mañana mi celular no puede realizar llamadas salientes",
                "categoria": "SERVICIO_INACCESIBLE",
                "nivelUrgencia": "CRITICO"
            }
        })

class SolicitanteInfo(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes = True)

    @field_validator('email', mode='before')
    @classmethod
    def email_to_str(cls, v):
        return str(v)

class TecnicoInfo(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_to_str(cls, v):
        return str(v)

class ComentarioInfo(BaseModel):
    id: int
    texto: str
    autor: dict
    fecha_hora: datetime

    model_config = ConfigDict(from_attributes=True)

class EventoInfo(BaseModel):
    id: Optional[int] = None
    tipo: str
    descripcion: str
    responsable: dict
    fecha_hora: datetime
    detalles: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def map_enums(cls, v: Any) -> Any:
        if hasattr(v, 'get_tipo_evento'):
            return {
                "id": v.id,
                "tipo": v.get_tipo_evento().value,
                "descripcion": v.descripcion,
                "responsable": {"id": v.responsable.id, "nombre": v.responsable.nombre},
                "fecha_hora": v.fecha_hora
            }
        return v

class RequerimientoResponse(BaseModel):
    id: int
    tipo: TipoRequerimiento
    titulo: str
    descripcion: str
    categoria: str
    nivel_urgencia: Optional[NivelUrgencia] = None
    estado: EstadoRequerimiento
    prioridad: int
    solicitante: SolicitanteInfo
    tecnico_asignado: Optional[TecnicoInfo] = None
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime] = None
    dias_desde_creacion: int
    comentarios: List[ComentarioInfo] = []
    eventos: List[EventoInfo] = []

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def calcular_campos_dinamicos(cls, v: Any) -> Any:
        if hasattr(v, 'get_tipo') and not isinstance(v, dict):
            return {
                "id": v.id,
                "tipo": v.get_tipo(),
                "titulo": v.titulo,
                "descripcion": v.descripcion,
                "categoria": v.get_categoria(),
                "nivel_urgencia": getattr(v, 'nivel_urgencia', None),
                "estado": v.estado,
                "prioridad": v.calcular_prioridad(),
                "solicitante": v.solicitante,
                "tecnico_asignado": v.tecnico_asignado,
                "fecha_creacion": v.fecha_creacion,
                "fecha_resolucion": v.fecha_resolucion,
                "dias_desde_creacion": v.get_dias_desde_creacion(),
                "comentarios": v.comentarios,
                "eventos": v.obtener_historial()
            }
        return v

class RequerimientoListaResponse(BaseModel):
    id: int
    tipo: TipoRequerimiento
    titulo: str
    categoria: str
    nivelUrgencia: Optional[NivelUrgencia] = None
    estado: EstadoRequerimiento
    prioridad: int
    solicitante: SolicitanteInfo
    tecnico_asignado: Optional[TecnicoInfo] = None
    fecha_creacion: datetime
    dias_desde_creacion: int

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def calcular_campos(cls, v: Any) -> Any:
        if hasattr(v, 'get_tipo') and not isinstance(v, dict):
            return {
                "id": v.id,
                "tipo": v.get_tipo(),
                "titulo": v.titulo,
                "categoria": v.get_categoria(),
                "nivel_urgencia": getattr(v, 'nivel_urgencia', None),
                "estado": v.estado,
                "prioridad": v.calcular_prioridad(),
                "solicitante": v.solicitante,
                "tecnico_asignado": v.tecnico_asignado,
                "fecha_creacion": v.fecha_creacion,
                "dias_desde_creacion": v.get_dias_desde_creacion()
            }
        return v

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    content: List[T]
    page: int
    size: int
    total_elements: int
    total_pages: int
    is_first: bool
    is_last: bool

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
