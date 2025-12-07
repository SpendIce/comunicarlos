from fastapi import APIRouter, Depends, Query, Path, status
from typing import Optional
from app.schemas.requerimiento import (
    CrearRequerimientoRequest,
    RequerimientoResponse,
    RequerimientoListaResponse,
    ResolverRequerimientoRequest,
    ReabrirRequerimientoRequest,
    PaginatedResponse
)
from app.schemas.enums import EstadoRequerimiento, TipoRequerimiento, NivelUrgencia
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
        nivel_urgencia=request.nivelUrgencia
    )


@router.get("", response_model=PaginatedResponse[RequerimientoListaResponse])
async def listar_requerimientos(
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
        "totalElements": total,
        "totalPages": total_pages,
        "isFirst": page == 0,
        "isLast": page >= total_pages - 1
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
    current_user = Depends(get_current_user)
):
    """
    Reabrir un requerimiento previamente resuelto.

    **Para OPERADORES y TECNICOS**

    Útil cuando:
    - El problema persiste
    - El cliente reporta que la solución no funcionó
    - Se detectó que se cerró prematuramente

    ## Validaciones:
    - El requerimiento debe estar RESUELTO
    - Se requiere un motivo de reapertura

    ## Efectos:
    - Cambia estado a REABIERTO
    - Se puede reasignar a otro técnico si es necesario
    - Genera evento de reapertura
    """
    # TODO: Implementar
    pass


async def verificar_rol_solicitante():
    # TODO: Implementar
    pass


async def verificar_rol_tecnico():
    # TODO: Implementar
    pass