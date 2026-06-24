from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.usuario import UsuarioRead
from app.schemas.enums import TipoEvento

class ComentarioCreate(BaseModel):
    contenido: str = Field(..., min_length=1)

class ComentarioRead(BaseModel):
    id: int
    contenido: str
    autor: UsuarioRead # Anidación de objetos
    fecha_hora: datetime

    class Config:
        from_attributes = True

class EventoRead(BaseModel):
    """
    Historial de acciones.
    Usamos 'descripcion_detallada' que viene del polimorfismo del dominio.
    """
    titulo: str
    descripcion: str = Field(alias="get_descripcion_detallada")
    tipo: TipoEvento = Field(alias="get_tipo_evento")
    responsable: UsuarioRead
    fecha_hora: datetime

    class Config:
        from_attributes = True
        populate_by_name = True