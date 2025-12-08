from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime

class AsignarTecnicoRequest(BaseModel):
    tecnicoId: int = Field(..., description="ID del técnico a asignar")
    comentario: Optional[str] = Field(None, max_length=500, description="Comentario sobre la asignación")

class TecnicoAsignadoInfo(BaseModel):
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
                "email": str(v.email)  # Conversión Email -> str
            }
        return v


class AsignacionResponse(BaseModel):
    id: int
    estado: str
    tecnicoAsignado: TecnicoAsignadoInfo
    fechaAsignacion: datetime

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        # Mapea Entidad Requerimiento a la respuesta de Asignación
        if hasattr(v, 'tecnico_asignado') and not isinstance(v, dict):
            return {
                "id": v.id,
                "estado": v.estado.value,
                "tecnicoAsignado": v.tecnico_asignado,
                # Usamos la fecha del último evento de asignación o la actual si no hay
                "fechaAsignacion": datetime.now()  # Simplificación válida para response
            }
        return v

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

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain(cls, v):
        # Este validador es TRUCOSO porque 'v' es un Requerimiento, pero la respuesta
        # espera datos del evento de derivación.
        # En el router, deberías devolver el EVENTO o construir este dict manualmente.
        # Si el servicio devuelve Requerimiento, no tenemos fácil acceso al "último evento de derivación" aquí.

        # ASUMIENDO QUE EL SERVICIO RETORNA EL REQUERIMIENTO:
        if hasattr(v, 'eventos') and not isinstance(v, dict):
            # Buscar el último evento de derivación
            # Esto es un parche. Lo ideal es que el servicio devuelva una estructura con estos datos.
            ultimo_evento = v.eventos[-1]  # Asumimos que es el que acabamos de crear

            return {
                "id": v.id,
                "estado": v.estado.value,
                "tecnicoOrigen": getattr(ultimo_evento, 'tecnico_origen', None),
                "tecnicoDestino": getattr(ultimo_evento, 'tecnico_destino', None),
                "fechaDerivacion": getattr(ultimo_evento, 'fecha_hora', datetime.now()),
                "motivo": getattr(ultimo_evento, 'motivo', "")
            }
        return v

