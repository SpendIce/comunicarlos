from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from app.schemas.auth import LoginRequest, LoginResponse, RegistroRequest, UsuarioResponse, RefreshTokenResponse
from app.services.authentication_service import AutenticacionService
from app.dependencies.services import get_auth_service

router = APIRouter()
security = HTTPBearer()


@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registro(
        request: RegistroRequest,
        service: AutenticacionService = Depends(get_auth_service)
):
    try:
        servicios = [s.model_dump() for s in request.serviciosSuscritos] if request.serviciosSuscritos else None

        nuevo_usuario = await service.registrar_usuario(
            # Nota: Asegurate que el servicio sea async o usa run_in_threadpool
            nombre=request.nombre,
            email=request.email,
            password=request.password,
            tipo_usuario=request.tipoUsuario,
            servicios_suscritos=servicios
        )
        return nuevo_usuario
    except Exception as e:
        print(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar usuario: {str(e)}"
        )


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


# ... logout y refresh (opcionales por ahora) ...


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
    description="Invalida el token JWT actual"
)
async def logout(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """
    Cerrar sesión del usuario actual.

    Invalida el token JWT para que no pueda ser usado nuevamente.
    """
    # TODO: Implementar lógica de logout
    pass


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Renovar token",
    description="Obtener un nuevo token JWT sin necesidad de login"
)
async def refresh_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    """
    Renovar token JWT.

    Útil para mantener la sesión activa sin requerir que el usuario
    ingrese sus credenciales nuevamente.
    """
    # TODO: Implementar lógica de refresh token
    pass
