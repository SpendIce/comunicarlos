from pydantic import BaseModel, Field, model_validator
from typing import List
from datetime import datetime
from app.schemas.enums import TipoUsuario

class CrearComentarioRequest(BaseModel):
    texto: str = Field(..., min_length=5, max_length=1000, description="Texto del comentario")

    class Config:
        json_schema_extra = {
            "example": {
                "texto": "He verificado el estado de la línea y está activa. Voy a reiniciar el servicio."
            }
        }

class AutorInfo(BaseModel):
    id: int
    nombre: str
    tipoUsuario: TipoUsuario

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'get_tipo_usuario') and not isinstance(v, dict):
            return {
                "id": v.id,
                "nombre": v.nombre,
                "tipoUsuario": v.get_tipo_usuario()
            }
        return v


class ComentarioResponse(BaseModel):
    id: int
    texto: str
    autor: AutorInfo
    fechaHora: datetime

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'texto') and not isinstance(v, dict):
            return {
                "id": v.id,
                "texto": v.texto,
                "autor": v.autor,
                "fechaHora": v.fecha_hora
            }
        return v

class ListaComentariosResponse(BaseModel):
    requerimientoId: int
    comentarios: List[ComentarioResponse]
    totalComentarios: int