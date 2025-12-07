from pydantic import BaseModel, EmailStr, Field, validator, model_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import TipoUsuario, TipoServicio

class ServicioSuscritoCreate(BaseModel):
    tipo: TipoServicio = Field(..., description="Tipo de servicio")
    numeroServicio: str = Field(..., min_length=5, max_length=50, description="Número de servicio")

class RegistroRequest(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    tipoUsuario: TipoUsuario = Field(..., description="Tipo de usuario")
    serviciosSuscritos: Optional[List[ServicioSuscritoCreate]] = Field(None, description="Servicios suscritos (requerido para SOLICITANTE)")

    @validator('email')
    def validar_email_corporativo(cls, v, values):
        if 'tipoUsuario' in values and values['tipoUsuario'] in [TipoUsuario.OPERADOR, TipoUsuario.TECNICO]:
            if not v.endswith('@comunicarlos.com.ar'):
                raise ValueError('Operadores y técnicos deben usar email corporativo @comunicarlos.com.ar')
        return v

    @validator('serviciosSuscritos')
    def validar_servicios_solicitante(cls, v, values):
        if 'tipoUsuario' in values and values['tipoUsuario'] == TipoUsuario.SOLICITANTE:
            if not v or len(v) == 0:
                raise ValueError('Solicitantes deben tener al menos un servicio suscrito')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan.perez@ejemplo.com",
                "password": "SecurePass123!",
                "tipoUsuario": "SOLICITANTE",
                "serviciosSuscritos": [
                    {
                        "tipo": "TELEFONIA_CELULAR",
                        "numeroServicio": "299-4567890"
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
    tipoUsuario: TipoUsuario
    fechaCreacion: datetime
    ultimoAcceso: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    def map_domain_entity(cls, v):
        """
        Mapea la Entidad de Dominio a la estructura del Schema JSON.
        Se ejecuta antes de la validación de Pydantic.
        """
        # Si 'v' es un objeto (Entidad de Dominio), lo convertimos manualmente
        if hasattr(v, 'email') and not isinstance(v, dict):
            return {
                "id": v.id,
                "nombre": v.nombre,
                "email": str(v.email),  # Extrae string del Value Object Email
                "tipoUsuario": v.get_tipo_usuario(),  # Llama al método del dominio
                "fechaCreacion": v.fecha_creacion,  # Mapea snake_case a camelCase
                "ultimoAcceso": v.ultimo_acceso
            }
        return v

class LoginResponse(BaseModel):
    token: str = Field(..., description="Token JWT")
    tipo: str = Field(default="Bearer", description="Tipo de token")
    expiresIn: int = Field(default=86400, description="Tiempo de expiración en segundos")
    usuario: UsuarioResponse

    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "tipo": "Bearer",
                "expiresIn": 86400,
                "usuario": {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan.perez@ejemplo.com",
                    "tipoUsuario": "SOLICITANTE",
                    "fechaCreacion": "2025-11-24T10:30:00Z"
                }
            }
        }

class RefreshTokenResponse(BaseModel):
    token: str
    tipo: str = "Bearer"
    expiresIn: int = 86400
