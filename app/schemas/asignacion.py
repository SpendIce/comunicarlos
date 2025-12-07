from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AsignarTecnicoRequest(BaseModel):
    tecnicoId: int = Field(..., description="ID del técnico a asignar")
    comentario: Optional[str] = Field(None, max_length=500, description="Comentario sobre la asignación")

    class Config:
        json_schema_extra = {
            "example": {
                "tecnicoId": 5,
                "comentario": "Asignado a Carlos por su experiencia en telefonía"
            }
        }

class TecnicoAsignadoInfo(BaseModel):
    id: int
    nombre: str
    email: str

class AsignacionResponse(BaseModel):
    id: int
    estado: str
    tecnicoAsignado: TecnicoAsignadoInfo
    fechaAsignacion: datetime

class ReasignarTecnicoRequest(BaseModel):
    tecnicoId: int = Field(..., description="ID del nuevo técnico")
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo de reasignación")

    class Config:
        json_schema_extra = {
            "example": {
                "tecnicoId": 7,
                "motivo": "Carlos no está disponible, reasignando a Pedro"
            }
        }

class DerivarTecnicoRequest(BaseModel):
    tecnicoDestinoId: int = Field(..., description="ID del técnico destino")
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
    tecnicoOrigen: TecnicoAsignadoInfo
    tecnicoDestino: TecnicoAsignadoInfo
    fechaDerivacion: datetime
    motivo: str

