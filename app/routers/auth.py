from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from app.schemas.auth import LoginRequest, LoginResponse, RegistroRequest, UsuarioResponse, RefreshTokenResponse
from app.services.authentication_service import AutenticacionService
from app.dependencies.services import get_auth_service
from app.services.exceptions import UnauthorizedException

router = APIRouter()
security = HTTPBearer()


@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registro(
        request: RegistroRequest,
        service: AutenticacionService = Depends(get_auth_service)
):
    servicios = [s.model_dump() for s in request.servicios_suscritos] if request.servicios_suscritos else None

    nuevo_usuario = await service.registrar_usuario(
        nombre=request.nombre,
        email=request.email,
        password=request.password,
        tipo_usuario=request.tipo_usuario,
        servicios_suscritos=servicios
    )
    return nuevo_usuario



@router.post("/login", response_model=LoginResponse)
async def login(
        request: LoginRequest,
        service: AutenticacionService = Depends(get_auth_service)
):
    usuario, token = await service.autenticar(request.email, request.password)
    return LoginResponse(
        token=token,
        usuario=usuario
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión"
)
async def logout(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        service: AutenticacionService = Depends(get_auth_service)
):
    """
    Cerrar sesión. Invalida el token actual agregándolo a una lista de bloqueo.
    """
    token = credentials.credentials
    await service.revocar_token(token)

    return {"message": "Sesión cerrada exitosamente"}

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar token",
    description="Obtener un nuevo token JWT sin necesidad de login"
)
async def refresh_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                        service: AutenticacionService = Depends(get_auth_service)):
    """
    Genera un nuevo token JWT para un usuario ya autenticado.
    """
    token_actual = credentials.credentials
    # Obtenemos el usuario del token actual (valida que no haya expirado aún)
    usuario = await service.obtener_usuario_desde_token(token_actual)

    # Generamos uno nuevo
    nuevo_token = service.crear_token_acceso(usuario)

    return {
        "token": nuevo_token,
        "tipo": "Bearer",
        "expires_in": 86400  # O el valor configurado en settings
    }
