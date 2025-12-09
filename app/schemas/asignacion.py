from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class AsignarTecnicoRequest(BaseModel):
    tecnico_id: int = Field(..., description="ID del técnico a asignar")
    comentario: Optional[str] = Field(None, max_length=500, description="Comentario sobre la asignación")

class TecnicoAsignadoInfo(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_to_str(cls, v):
        return str(v)


class AsignacionResponse(BaseModel):
    id: int
    estado: str
    tecnico_asignado: TecnicoAsignadoInfo
    fecha_asignacion: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def map_domain(cls, v):
        # Mapea Entidad Requerimiento a la respuesta de Asignación
        if hasattr(v, 'tecnico_asignado') and not isinstance(v, dict):
            return {
                "id": v.id,
                "estado": v.estado.value,
                "tecnico_asignado": v.tecnico_asignado,
                "fecha_asignacion": datetime.now()  # Simplificación válida para response
            }
        return v

class ReasignarTecnicoRequest(BaseModel):
    tecnico_id: int = Field(..., description="ID del nuevo técnico")
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de reasignación")

    class Config:
        json_schema_extra = {
            "example": {
                "tecnicoId": 7,
                "motivo": "Carlos no está disponible, reasignando a Pedro"
            }
        }

class DerivarTecnicoRequest(BaseModel):
    tecnico_destino_id: int = Field(..., description="ID del técnico destino")
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de derivación")

    class Config:
        json_schema_extra = {
            "example": {
                "tecnicoDestinoId": 8,
                "motivo": "Requiero apoyo de un especialista en redes para diagnóstico"
            }
        }


class DerivacionResponse(BaseModel):
    id: int
    estado: str
    tecnico_origen: TecnicoAsignadoInfo
    tecnico_destino: TecnicoAsignadoInfo
    fecha_derivacion: datetime
    motivo: str

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def map_domain(cls, v):
        if hasattr(v, 'eventos') and not isinstance(v, dict):
            ultimo_evento = v.eventos[-1]  # Asumimos que es el que acabamos de crear

            return {
                "id": v.id,
                "estado": v.estado.value,
                "tecnico_origen": getattr(ultimo_evento, 'tecnico_origen', None),
                "tecnico_destino": getattr(ultimo_evento, 'tecnico_destino', None),
                "fecha_derivacion": getattr(ultimo_evento, 'fecha_hora', datetime.now()),
                "motivo": getattr(ultimo_evento, 'motivo', "")
            }
        return v

