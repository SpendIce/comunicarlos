from fastapi import APIRouter, Path, Depends
from app.schemas.asignacion import (
    AsignarTecnicoRequest,
    AsignacionResponse,
    ReasignarTecnicoRequest,
    DerivarTecnicoRequest,
    DerivacionResponse
)
from app.dependencies.auth import verificar_rol_operador, verificar_rol_tecnico
from app.services.asignacion_service import AsignacionService
from app.dependencies.services import get_asignacion_service

router = APIRouter()

@router.post("/{id}/asignar", response_model=AsignacionResponse)
async def asignar_tecnico(
    id: int = Path(...),
    request: AsignarTecnicoRequest = None,
    current_user = Depends(verificar_rol_operador),
    service: AsignacionService = Depends(get_asignacion_service)
):
    return await service.asignar_tecnico(
        requerimiento_id=id,
        tecnico_id=request.tecnico_id,
        operador_id=current_user.id,
        comentario=request.comentario
    )

@router.put("/{id}/asignar", response_model=AsignacionResponse)
async def reasignar_tecnico(
    id: int = Path(...),
    request: ReasignarTecnicoRequest = None,
    current_user = Depends(verificar_rol_operador),
    service: AsignacionService = Depends(get_asignacion_service)
):
    return await service.reasignar_tecnico(
        requerimiento_id=id,
        nuevo_tecnico_id=request.tecnico_id,
        operador_id=current_user.id,
        motivo=request.motivo
    )

@router.post("/{id}/derivar", response_model=DerivacionResponse)
async def derivar_tecnico(
    id: int = Path(...),
    request: DerivarTecnicoRequest = None,
    current_user = Depends(verificar_rol_tecnico),
    service: AsignacionService = Depends(get_asignacion_service)
):
    return await service.derivar_tecnico(
        requerimiento_id=id,
        tecnico_origen_id=current_user.id,
        tecnico_destino_id=request.tecnico_destino_id,
        motivo=request.motivo
    )