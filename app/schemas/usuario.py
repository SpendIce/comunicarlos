from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.enums import TipoUsuario, TipoServicio

class ServicioInfo(BaseModel):
    id: int
    tipo: TipoServicio
    numero_servicio: str
    activo: bool
    fecha_alta: datetime

    model_config = ConfigDict(from_attributes=True)

class UsuarioPerfilResponse(BaseModel):
    id: int
    nombre: str
    email: str
    tipo_usuario: TipoUsuario
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]
    servicios_suscritos: Optional[List[ServicioInfo]] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_str(cls, v):
        return str(v)

class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    password_ctual: Optional[str] = Field(None, description="Contraseña actual (requerida si se cambia password)")
    password_nuevo: Optional[str] = Field(None, min_length=8, description="Nueva contraseña")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Carlos Pérez",
                "password_actual": "OldPass123!",
                "password_nuevo": "NewSecurePass456!"
            }
        }

class TecnicoResponse(BaseModel):
    id: int
    nombre: str
    email: str
    especialidades: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_str(cls, v):
        return str(v)

class OperadorInfo(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_str(cls, v):
        return str(v)

class TecnicoInfo(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('email', mode='before')
    @classmethod
    def email_str(cls, v):
        return str(v)

class ConfigurarSupervisionRequest(BaseModel):
    operador_id: Optional[int] = Field(None, description="ID del operador a supervisar")
    tecnico_id: Optional[int] = Field(None, description="ID del técnico a supervisar")

class SupervisionResponse(BaseModel):
    operadores_supervisados: List[OperadorInfo]
    tecnicos_supervisados: List[TecnicoInfo]
