from pydantic import BaseModel, EmailStr, Field, validator, model_validator, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.enums import TipoUsuario, TipoServicio

class ServicioSuscritoCreate(BaseModel):
    tipo: TipoServicio = Field(..., description="Tipo de servicio")
    numero_servicio: str = Field(..., min_length=5, max_length=50, description="Número de servicio")

class RegistroRequest(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    tipo_usuario: TipoUsuario = Field(..., description="Tipo de usuario")
    servicios_suscritos: Optional[List[ServicioSuscritoCreate]] = Field(None, description="Servicios suscritos (requerido para SOLICITANTE)")

    @validator('email')
    def validar_email_corporativo(cls, v, values):
        if 'tipo_usuario' in values and values['tipo_usuario'] in [TipoUsuario.OPERADOR, TipoUsuario.TECNICO]:
            if not v.endswith('@comunicarlos.com.ar'):
                raise ValueError('Operadores y técnicos deben usar email corporativo @comunicarlos.com.ar')
        return v

    @validator('servicios_suscritos')
    def validar_servicios_solicitante(cls, v, values):
        if 'tipo_usuario' in values and values['tipo_usuario'] == TipoUsuario.SOLICITANTE:
            if not v or len(v) == 0:
                raise ValueError('Solicitantes deben tener al menos un servicio suscrito')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@ejemplo.com",
                "password": "SecurePass123!",
                "tipo_usuario": "SOLICITANTE",
                "servicios_suscritos": [
                    {
                        "tipo": "TELEFONIA_CELULAR",
                        "numero_servicio": "299-4567890"
                    }
                ]
            }
        }

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "juan.perez@ejemplo.com",
                "password": "SecurePass123!"
            }
        }

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    tipo_usuario: TipoUsuario
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def map_domain(cls, v: Any) -> Any:
        if hasattr(v, 'email') and not isinstance(v, dict):
            return {
                "id": v.id,
                "nombre": v.nombre,
                "email": str(v.email),
                "tipo_usuario": v.get_tipo_usuario(),
                "fecha_creacion": v.fecha_creacion,
                "ultimo_acceso": v.ultimo_acceso
            }
        return v

class LoginResponse(BaseModel):
    token: str = Field(..., description="Token JWT")
    tipo: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(default=86400, description="Tiempo de expiración en segundos")
    usuario: UsuarioResponse

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "tipo": "Bearer",
                "expires_in": 86400,
                "usuario": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan.perez@ejemplo.com",
                    "tipo_usuario": "SOLICITANTE",
                    "fecha_creacion": "2025-11-24T10:30:00Z"
                }
            }
        }

class RefreshTokenResponse(BaseModel):
    token: str
    tipo: str = "Bearer"
    expires_in: int = 86400
