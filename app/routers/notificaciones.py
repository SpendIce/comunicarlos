from fastapi import APIRouter, Path, Query, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.notificacion import (
    NotificacionResponse, PaginatedNotificacionesResponse, MarcarLeidasResponse
)
from app.dependencies.auth import verificar_rol_supervisor
from app.services.notificacion_service import NotificacionService
from app.dependencies.services import get_notificacion_service

router = APIRouter()


@router.get("", response_model=PaginatedNotificacionesResponse)
async def listar_notificaciones(
        leida: Optional[bool] = Query(None),
        page: int = Query(0, ge=0),
        size: int = Query(20, ge=1, le=100),
        current_user=Depends(verificar_rol_supervisor),
        service: NotificacionService = Depends(get_notificacion_service)
):
    notificaciones, total = await service.listar_notificaciones(
        supervisor_id=current_user.id,
        leida=leida,
        page=page,
        size=size
    )

    # Calcular total de no leídas para el contador del frontend
    total_no_leidas = await service.notif_repo.contar_por_supervisor(
        supervisor_id=current_user.id,
        leida=False
    )

    return {
        "content": notificaciones,
        "totalNoLeidas": total_no_leidas,
        "totalElements": total,
        "page": page,
        "size": size
    }


@router.patch("/{id}/leer", response_model=NotificacionResponse)
async def marcar_notificacion_leida(
        id: int = Path(...),
        current_user=Depends(verificar_rol_supervisor),
        service: NotificacionService = Depends(get_notificacion_service)
):
    return await service.marcar_como_leida(id, current_user.id)


@router.patch("/leer-todas", response_model=MarcarLeidasResponse)
async def marcar_todas_leidas(
        current_user=Depends(verificar_rol_supervisor),
        service: NotificacionService = Depends(get_notificacion_service)
):
    cantidad = await service.marcar_todas_leidas(current_user.id)
    return {
        "notificacionesMarcadas": cantidad,
        "mensaje": f"Se marcaron {cantidad} notificaciones como leídas"
    }