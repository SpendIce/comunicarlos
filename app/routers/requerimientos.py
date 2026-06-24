from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union
from app.schemas.requerimiento import (
    RequerimientoRead, IncidenteCreate, SolicitudCreate
)
from app.services.requerimiento_service import RequerimientoService
from app.dependencies import get_requerimiento_service, get_current_user
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import PermisosDenegadosException, RecursoNoEncontradoException

router = APIRouter(prefix="/requerimientos", tags=["Requerimientos"])


@router.post("/incidentes", response_model=RequerimientoRead, status_code=201)
def crear_incidente(
        incidente_in: IncidenteCreate,
        service: RequerimientoService = Depends(get_requerimiento_service),
        current_user: Usuario = Depends(get_current_user)
):
    """Crea un Incidente (Falla de servicio)."""
    try:
        return service.crear_incidente(
            solicitante_id=current_user.id,  # Usamos el ID del token, seguridad
            titulo=incidente_in.titulo,
            descripcion=incidente_in.descripcion,
            urgencia=incidente_in.nivel_urgencia,
            categoria=incidente_in.categoria
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solicitudes", response_model=RequerimientoRead, status_code=201)
def crear_solicitud(
        solicitud_in: SolicitudCreate,
        service: RequerimientoService = Depends(get_requerimiento_service),
        current_user: Usuario = Depends(get_current_user)
):
    """Crea una Solicitud (Alta/Baja servicio)."""
    return service.crear_solicitud(
        solicitante_id=current_user.id,
        titulo=solicitud_in.titulo,
        descripcion=solicitud_in.descripcion,
        categoria=solicitud_in.categoria
    )


@router.get("/", response_model=List[RequerimientoRead])
def listar_requerimientos(
        service: RequerimientoService = Depends(get_requerimiento_service),
        current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna la lista de requerimientos.
    Polimorfismo: El servicio filtra automáticamente qué puede ver el usuario.
    """
    return service.obtener_requerimientos_usuario(current_user.id)


@router.get("/{id_req}", response_model=RequerimientoRead)
def obtener_requerimiento(
        id_req: int,
        service: RequerimientoService = Depends(get_requerimiento_service),
        current_user: Usuario = Depends(get_current_user)
):
    try:
        req = service._get_requerimiento(id_req)  # Método interno o público get_by_id

        # Validación de visibilidad explícita (Doble check)
        if not current_user.puede_ver_requerimiento(req):
            raise PermisosDenegadosException("No tiene acceso a este requerimiento")

        return req

    except RecursoNoEncontradoException:
        raise HTTPException(status_code=404, detail="Requerimiento no encontrado")
    except PermisosDenegadosException:
        raise HTTPException(status_code=403, detail="Acceso denegado")