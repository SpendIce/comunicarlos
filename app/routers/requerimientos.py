from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from typing import Optional
from app.schemas.requerimiento import (
    CrearRequerimientoRequest,
    RequerimientoResponse,
    RequerimientoListaResponse,
    ResolverRequerimientoRequest,
    ReabrirRequerimientoRequest,
    PaginatedResponse
)
from app.schemas.enums import EstadoRequerimiento, TipoRequerimiento
from app.dependencies.auth import (
    get_current_user,
    verificar_rol_solicitante,
    verificar_rol_tecnico
)
from app.services.requerimiento_service import RequerimientoService
from app.dependencies.services import get_req_service


router = APIRouter()

@router.post("", response_model=RequerimientoResponse, status_code=status.HTTP_201_CREATED)
async def crear_requerimiento(
        request: CrearRequerimientoRequest,
        current_user=Depends(verificar_rol_solicitante),
        service: RequerimientoService = Depends(get_req_service)
):

    return await service.crear_requerimiento(
        solicitante_id=current_user.id,
        tipo=request.tipo,
        titulo=request.titulo,
        descripcion=request.descripcion,
        categoria=request.categoria,
        nivel_urgencia=request.nivel_urgencia
    )

@router.get("", response_model=PaginatedResponse[RequerimientoListaResponse])
async def listar_requerimientos(
        estado: Optional[EstadoRequerimiento] = Query(None),
        tipo: Optional[TipoRequerimiento] = Query(None),
        page: int = Query(0, ge=0),
        size: int = Query(20, ge=1, le=100),
        current_user=Depends(get_current_user),
        service: RequerimientoService = Depends(get_req_service)
):
    requerimientos, total = await service.listar_requerimientos(
        usuario_actual=current_user,
        estado=estado,
        tipo=tipo,
        page=page,
        size=size
    )

    total_pages = (total + size - 1) // size
    return {
        "content": requerimientos,
        "page": page,
        "size": size,
        "total_elements": total,
        "total_pages": total_pages,
        "is_first": page == 0,
        "is_last": page >= total_pages - 1
    }


@router.get("/{id}", response_model=RequerimientoResponse)
async def obtener_requerimiento(
        id: int = Path(...),
        current_user=Depends(get_current_user),
        service: RequerimientoService = Depends(get_req_service)
):
    return await service.obtener_requerimiento(id, current_user)


@router.patch("/{id}/resolver", response_model=RequerimientoResponse)
async def resolver_requerimiento(
        id: int = Path(...),
        request: ResolverRequerimientoRequest = None,
        current_user=Depends(verificar_rol_tecnico),
        service: RequerimientoService = Depends(get_req_service)
):
    comentario = request.comentarioResolucion if request else None
    return await service.resolver_requerimiento(
        requerimiento_id=id,
        tecnico_id=current_user.id,
        comentario_resolucion=comentario
    )


@router.patch(
    "/{id}/reabrir",
    response_model=RequerimientoResponse,
    summary="Reabrir requerimiento",
    description="Reabrir un requerimiento resuelto (operadores y técnicos)"
)
async def reabrir_requerimiento(
    id: int = Path(..., description="ID del requerimiento"),
    request: ReabrirRequerimientoRequest = None,
    current_user = Depends(get_current_user),
    service: RequerimientoService = Depends(get_req_service)
):
    # Validar que venga el motivo
    if not request or not request.motivo:
         raise HTTPException(status_code=400, detail="El motivo es requerido para reabrir")

    return await service.reabrir_requerimiento(
        requerimiento_id=id,
        usuario_id=current_user.id,
        motivo=request.motivo
    )
