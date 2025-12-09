from fastapi import APIRouter, Path, Depends, status, HTTPException
from app.schemas.servicio import (
    MisServiciosResponse, SolicitarAltaRequest, SolicitarBajaRequest, SolicitudServicioResponse
)
from app.dependencies.auth import verificar_rol_solicitante, get_current_user
from app.services.servicio_service import ServicioService
from app.dependencies.services import get_servicio_service
from app.services.exceptions import NotFoundException

router = APIRouter()

@router.get("/mis-servicios", response_model=MisServiciosResponse)
async def listar_mis_servicios(
    current_user = Depends(verificar_rol_solicitante),
    service: ServicioService = Depends(get_servicio_service)
):
    # current_user ya es un Solicitante con servicios_suscritos cargados por el repo
    return {"servicios": current_user.servicios_suscritos}

@router.post("/solicitar-alta", response_model=SolicitudServicioResponse, status_code=status.HTTP_201_CREATED)
async def solicitar_alta_servicio(
    request: SolicitarAltaRequest,
    current_user = Depends(verificar_rol_solicitante),
    service: ServicioService = Depends(get_servicio_service)
):
    solicitud = await service.solicitar_alta_servicio(
        solicitante_id=current_user.id,
        tipo_servicio=request.tipo_servicio,
        plan_deseado=request.plan_deseado,
        direccion_instalacion=request.direccion_instalacion,
        comentarios=request.comentarios
    )
    return {
        "requerimiento": {
            "id": solicitud.id, "tipo": solicitud.get_tipo(), "titulo": solicitud.titulo,
            "categoria": solicitud.get_categoria(), "estado": solicitud.estado
        },
        "mensaje": "Solicitud de alta creada correctamente"
    }

@router.post("/{servicio_id}/solicitar-baja", response_model=SolicitudServicioResponse, status_code=status.HTTP_201_CREATED)
async def solicitar_baja_servicio(
    servicio_id: int = Path(...),
    request: SolicitarBajaRequest = None,
    current_user = Depends(verificar_rol_solicitante),
    service: ServicioService = Depends(get_servicio_service)
):
    solicitud = await service.solicitar_baja_servicio(
        servicio_id=servicio_id,
        solicitante_id=current_user.id,
        motivo=request.motivo,
        fecha_deseada_baja=str(request.fecha_deseada_baja),
        comentarios=request.comentarios
    )
    return {
        "requerimiento": {
            "id": solicitud.id, "tipo": solicitud.get_tipo(), "titulo": solicitud.titulo,
            "categoria": solicitud.get_categoria(), "estado": solicitud.estado
        },
        "mensaje": "Solicitud de baja creada correctamente"
    }