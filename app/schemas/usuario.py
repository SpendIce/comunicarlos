from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import TipoUsuario


class UsuarioBase(BaseModel):
    """
    Clase base con los campos comunes.
    Concepto: DRY (Don't Repeat Yourself).
    """
    nombre: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Debe ser un email válido")


class UsuarioCreate(UsuarioBase):
    """
    Schema para el REGISTRO (Input).
    Incluye el password que será hasheado por el servicio.
    """
    password: str = Field(..., min_length=8, description="Contraseña en texto plano")
    # Campo discriminador para saber qué crear desde el front
    tipo: TipoUsuario

    # Campos opcionales específicos para técnicos
    especialidades: Optional[List[str]] = []


class UsuarioRead(UsuarioBase):
    """
    Schema para la RESPUESTA (Output).
    Excluye password, incluye ID y fechas.
    """
    id: int
    tipo_usuario: TipoUsuario = Field(alias="get_tipo_usuario")  # Mapea el método del dominio
    ultimo_acceso: Optional[datetime] = None

    class Config:
        # Permite leer directamente desde la Entidad de Dominio
        from_attributes = True
        # Permite usar métodos de la entidad como campos (ej: get_tipo_usuario)
        populate_by_name = True


class UsuarioLogin(BaseModel):
    """Schema exclusivo para el endpoint de login."""
    email: EmailStr
    password: str