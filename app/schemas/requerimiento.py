from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import (
    EstadoRequerimiento,
    NivelUrgencia,
    CategoriaIncidente,
    CategoriaSolicitud,
    TipoRequerimiento
)
from app.schemas.usuario import UsuarioRead
from app.schemas.comentario import ComentarioRead, EventoRead


# --- INPUTS (Polimorfismo en creación) ---

class RequerimientoCreateBase(BaseModel):
    titulo: str = Field(..., min_length=5)
    descripcion: str = Field(..., min_length=10)
    solicitante_id: int


class IncidenteCreate(RequerimientoCreateBase):
    """Input específico para Incidentes."""
    nivel_urgencia: NivelUrgencia
    categoria: CategoriaIncidente


class SolicitudCreate(RequerimientoCreateBase):
    """Input específico para Solicitudes."""
    categoria: CategoriaSolicitud


# --- ACTIONS (Inputs para acciones específicas) ---

class AsignarTecnico(BaseModel):
    tecnico_id: int


class DerivarTecnico(BaseModel):
    tecnico_destino_id: int
    motivo: str


class ResolverRequerimiento(BaseModel):
    comentario_final: Optional[str] = None


class ReabrirRequerimiento(BaseModel):
    motivo: str


# --- OUTPUT (Lectura unificada) ---

class RequerimientoRead(BaseModel):
    """
    Schema unificado de respuesta.
    Al leer una lista, pueden venir Incidentes o Solicitudes.
    Pydantic mapeará los campos que existan en la entidad y dejará null los que no.
    """
    id: int
    titulo: str
    descripcion: str
    estado: EstadoRequerimiento
    tipo: TipoRequerimiento = Field(alias="get_tipo")  # Polimorfismo del Dominio

    # Campos calculados del dominio
    prioridad: int = Field(alias="calcular_prioridad")

    # Relaciones
    solicitante: UsuarioRead
    tecnico_asignado: Optional[UsuarioRead] = None

    # Campos específicos (Opcionales porque dependen del tipo)
    nivel_urgencia: Optional[NivelUrgencia] = None
    categoria_incidente: Optional[CategoriaIncidente] = Field(None, alias="categoria")
    categoria_solicitud: Optional[CategoriaSolicitud] = Field(None, alias="categoria")

    # Historial
    fecha_creacion: datetime
    fecha_resolucion: Optional[datetime] = None
    comentarios: List[ComentarioRead] = []
    eventos: List[EventoRead] = []

    class Config:
        from_attributes = True
        populate_by_name = True