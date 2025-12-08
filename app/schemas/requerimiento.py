from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from app.schemas.enums import (
    TipoRequerimiento, EstadoRequerimiento, NivelUrgencia
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

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'email') and not isinstance(v, dict):
            return {
                "id": v.id,
                "nombre": v.nombre,
                "email": str(v.email)
            }
        return v

class TecnicoInfo(BaseModel):
    id: int
    nombre: str
    email: str

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'email') and not isinstance(v, dict):
            return {
                "id": v.id,
                "nombre": v.nombre,
                "email": str(v.email)
            }
        return v

class ComentarioInfo(BaseModel):
    id: int
    texto: str
    autor: dict
    fechaHora: datetime

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'texto') and not isinstance(v, dict):
            return {
                "id": v.id,
                "texto": v.texto,
                "autor": {
                    "id": v.autor.id,
                    "nombre": v.autor.nombre,
                    "email": str(v.autor.email)
                },
                "fechaHora": v.fecha_hora
            }
        return v

class EventoInfo(BaseModel):
    id: Optional[int] = None
    tipo: str
    descripcion: str
    responsable: dict
    fechaHora: datetime
    detalles: Optional[dict] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'get_tipo_evento') and not isinstance(v, dict):
            return {
                "id": v.id,
                "tipo": v.get_tipo_evento().value,
                "descripcion": v.descripcion,
                "responsable": {
                    "id": v.responsable.id,
                    "nombre": v.responsable.nombre
                },
                "fechaHora": v.fecha_hora,
                "detalles": None
            }
        return v

class RequerimientoResponse(BaseModel):
    id: int
    tipo: TipoRequerimiento
    titulo: str
    descripcion: str
    categoria: str
    nivelUrgencia: Optional[NivelUrgencia] = None
    estado: EstadoRequerimiento
    prioridad: int
    solicitante: SolicitanteInfo
    tecnicoAsignado: Optional[TecnicoInfo] = None
    fechaCreacion: datetime
    fechaResolucion: Optional[datetime] = None
    diasDesdeCreacion: int
    comentarios: List[ComentarioInfo] = []
    eventos: List[EventoInfo] = []

    class Config:
        from_attributes = True

        @model_validator(mode='before')
        def map_domain_entity(cls, v):
            """Mapea Entidad Requerimiento -> Schema"""
            if hasattr(v, 'titulo') and not isinstance(v, dict):
                # Determinar si es Incidente para extraer urgencia
                nivel_urgencia = None
                if v.get_tipo() == TipoRequerimiento.INCIDENTE:
                    nivel_urgencia = v.nivel_urgencia

                return {
                    "id": v.id,
                    "tipo": v.get_tipo(),
                    "titulo": v.titulo,
                    "descripcion": v.descripcion,
                    "categoria": v.get_categoria(),
                    "nivelUrgencia": nivel_urgencia,
                    "estado": v.estado,
                    "prioridad": v.calcular_prioridad(),
                    "solicitante": v.solicitante,  # Pydantic usará SolicitanteInfo para validar esto
                    "tecnicoAsignado": v.tecnico_asignado,  # Puede ser None
                    "fechaCreacion": v.fecha_creacion,
                    "fechaResolucion": v.fecha_resolucion,
                    "diasDesdeCreacion": v.get_dias_desde_creacion(),
                    "comentarios": v.comentarios,
                    "eventos": v.eventos
                }
            return v

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
