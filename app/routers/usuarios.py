from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List
from app.schemas.usuario import (
    UsuarioPerfilResponse, ActualizarPerfilRequest,
    TecnicoResponse, SupervisionResponse, ConfigurarSupervisionRequest
)
from app.services.authentication_service import AutenticacionService
from app.dependencies.auth import get_current_user, verificar_rol_operador, verificar_rol_supervisor
from app.dependencies.services import get_auth_service, get_usuario_repo

router = APIRouter()


@router.get("/me", response_model=UsuarioPerfilResponse)
async def obtener_perfil_actual(current_user=Depends(get_current_user)):
    # Pydantic (from_attributes=True) mapeará automáticamente la entidad Usuario a UsuarioPerfilResponse
    # Para solicitantes, mapeará automáticamente servicios_suscritos
    return current_user


@router.put("/me", response_model=UsuarioPerfilResponse)
async def actualizar_perfil(
        request: ActualizarPerfilRequest,
        current_user=Depends(get_current_user),
        user_repo=Depends(get_usuario_repo),
        auth_service: AutenticacionService = Depends(get_auth_service)
):
    # Validar password actual si se quiere cambiar
    if request.passwordNuevo:
        if not request.passwordActual:
            raise HTTPException(status_code=400, detail="Password actual requerido")
        if not auth_service.verificar_password(request.passwordActual, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Password actual incorrecto")
        current_user.password_hash = auth_service.hash_password(request.passwordNuevo)

    if request.nombre:
        current_user.actualizar_nombre(request.nombre)

    await user_repo.guardar(current_user)
    return current_user


@router.get("/tecnicos", response_model=List[TecnicoResponse])
async def listar_tecnicos(
        especialidad: str = None,
        current_user=Depends(verificar_rol_operador),
        user_repo=Depends(get_usuario_repo)
):
    tecnicos = await user_repo.buscar_tecnicos(especialidad=especialidad)
    return tecnicos


@router.post("/supervisores/me/supervisados", response_model=SupervisionResponse)
async def configurar_supervision(
        request: ConfigurarSupervisionRequest,
        current_user=Depends(verificar_rol_supervisor),
        user_repo=Depends(get_usuario_repo)
):
    if request.operador_id:
        op = await user_repo.buscar_por_id(request.operador_id)
        if op: current_user.agregar_operador_supervisado(op)

    if request.tecnico_id:
        tec = await user_repo.buscar_por_id(request.tecnico_id)
        if tec: current_user.agregar_tecnico_supervisado(tec)

    await user_repo.guardar(current_user)

    return {
        "operadores_supervisados": current_user.operadores_supervisados,
        "tecnicos_supervisados": current_user.tecnicos_supervisados
    }