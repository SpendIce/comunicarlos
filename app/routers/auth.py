from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioLogin
from app.services.authentication_service import AuthenticationService
from app.dependencies import get_auth_service
from app.domain.exceptions import CredencialesInvalidasException, EmailInvalidoException

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthenticationService = Depends(get_auth_service)
):
    """
    Endpoint estándar OAuth2 para obtener token.
    Recibe username (email) y password.
    """
    try:
        # El servicio devuelve el usuario hidratado si es válido
        usuario = service.autenticar(form_data.username, form_data.password)

        # Generar token (Lógica delegada al servicio o infraestructura)
        token = service.generar_token_acceso(usuario)

        return {"access_token": token, "token_type": "bearer"}

    except CredencialesInvalidasException as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/register", response_model=UsuarioRead, status_code=201)
def registrar_usuario(
        usuario_in: UsuarioCreate,
        service: AuthenticationService = Depends(get_auth_service)
):
    """
    Registra un nuevo usuario en el sistema.
    Maneja excepciones de dominio como 'Email inválido'.
    """
    try:
        nuevo_usuario = service.registrar_usuario(
            nombre=usuario_in.nombre,
            email=usuario_in.email,
            password=usuario_in.password,
            tipo=usuario_in.tipo,
            # Argumentos variables para técnicos/supervisores
            especialidades=getattr(usuario_in, 'especialidades', [])
        )
        return nuevo_usuario

    except EmailInvalidoException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))