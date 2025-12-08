from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import TipoUsuario, TipoServicio

class ServicioInfo(BaseModel):
    id: int
    tipo: TipoServicio
    numeroServicio: str
    activo: bool
    fechaAlta: datetime

    class Config:
        from_attributes = True

class UsuarioPerfilResponse(BaseModel):
    id: int
    nombre: str
    email: str
    tipoUsuario: TipoUsuario
    fechaCreacion: datetime
    ultimoAcceso: Optional[datetime]
    serviciosSuscritos: Optional[List[ServicioInfo]] = None

    class Config:
        from_attributes = True

        @model_validator(mode='before')
        def map_domain_data(cls, v):
            if hasattr(v, 'email') and not isinstance(v, dict):
                return {
                    "id": v.id,
                    "nombre": v.nombre,
                    "email": str(v.email),
                    "tipoUsuario": v.get_tipo_usuario(),
                    "fechaCreacion": v.fecha_creacion,
                    "ultimoAcceso": v.ultimo_acceso,
                    "serviciosSuscritos": getattr(v, "servicios_suscritos", None)
                }
            return v

class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    passwordActual: Optional[str] = Field(None, description="Contraseña actual (requerida si se cambia password)")
    passwordNuevo: Optional[str] = Field(None, min_length=8, description="Nueva contraseña")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Carlos Pérez",
                "passwordActual": "OldPass123!",
                "passwordNuevo": "NewSecurePass456!"
            }
        }

class TecnicoResponse(BaseModel):
    id: int
    nombre: str
    email: str
    especialidades: List[str] = []
    requerimientosAsignados: int = 0
    requerimientosResueltos: int = 0

    class Config:
        from_attributes = True

        @model_validator(mode='before')
        def map_domain_data(cls, v):
            if hasattr(v, 'email') and not isinstance(v, dict):
                return {
                    "id": v.id,
                    "nombre": v.nombre,
                    "email": str(v.email),
                    "especialidades": v.especialidades,
                    "requerimientosAsignados": getattr(v, "requerimientos_asignados", 0),
                    "requerimientosResueltos": 0
                }
            return v

class OperadorInfo(BaseModel):
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

class ConfigurarSupervisionRequest(BaseModel):
    operadorId: Optional[int] = Field(None, description="ID del operador a supervisar")
    tecnicoId: Optional[int] = Field(None, description="ID del técnico a supervisar")

class SupervisionResponse(BaseModel):
    operadoresSupervisados: List[OperadorInfo]
    tecnicosSupervisados: List[TecnicoInfo]
