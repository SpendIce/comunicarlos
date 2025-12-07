from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from jose import JWTError, jwt
from app.config import settings
from app.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.mongodb.database import mongodb
from app.domain.enums import TipoUsuario

security = HTTPBearer()


async def get_usuario_repo():
    return UsuarioRepository(mongodb.get_database())


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        usuario_repo: UsuarioRepository = Depends(get_usuario_repo)
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Convertir user_id a int si tu dominio usa int, o dejar str si migraste a UUID/ObjectId
    try:
        usuario = await usuario_repo.buscar_por_id(int(user_id))
    except ValueError:
        raise credentials_exception

    if usuario is None:
        raise credentials_exception

    return usuario


async def require_role(required_roles: list[TipoUsuario]):
    """
    Factory para crear dependencies que verifican roles específicos.
    """

    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.tipoUsuario not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos. Se requiere rol: {', '.join([r.value for r in required_roles])}"
            )
        return current_user

    return role_checker


# Funciones helper para roles específicos
async def verificar_rol_solicitante(current_user=Depends(get_current_user)):
    if current_user.tipoUsuario != TipoUsuario.SOLICITANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo solicitantes pueden acceder a este recurso"
        )
    return current_user


async def verificar_rol_operador(current_user=Depends(get_current_user)):
    if current_user.tipoUsuario != TipoUsuario.OPERADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo operadores pueden acceder a este recurso"
        )
    return current_user


async def verificar_rol_tecnico(current_user=Depends(get_current_user)):
    if current_user.tipoUsuario != TipoUsuario.TECNICO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo técnicos pueden acceder a este recurso"
        )
    return current_user


async def verificar_rol_supervisor(current_user=Depends(get_current_user)):
    if current_user.tipoUsuario != TipoUsuario.SUPERVISOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo supervisores pueden acceder a este recurso"
        )
    return current_user


async def verificar_rol_staff(current_user=Depends(get_current_user)):
    """Verifica que sea operador, técnico o supervisor (personal interno)"""
    roles_permitidos = [TipoUsuario.OPERADOR, TipoUsuario.TECNICO, TipoUsuario.SUPERVISOR]
    if current_user.tipoUsuario not in roles_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal interno puede acceder a este recurso"
        )
    return current_user
