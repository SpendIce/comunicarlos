from fastapi import APIRouter, Depends, HTTPException, Body
from app.services.requerimiento_service import RequerimientoService
from app.dependencies import get_requerimiento_service, get_current_user
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import (
    PermisosDenegadosException,
    EstadoInvalidoException,
    RecursoNoEncontradoException
)
from app.schemas.requerimiento import AsignarTecnico, DerivarTecnico, ResolverRequerimiento

router = APIRouter(prefix="/requerimientos", tags=["Operaciones"])

@router.put("/{id_req}/asignar")
def asignar_tecnico(
    id_req: int,
    datos: AsignarTecnico,
    service: RequerimientoService = Depends(get_requerimiento_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Un Operador asigna un técnico.
    """
    try:
        service.asignar_tecnico(
            id_req=id_req,
            id_operador=current_user.id,
            id_tecnico=datos.tecnico_id
        )
        return {"mensaje": "Técnico asignado correctamente"}
    except PermisosDenegadosException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except EstadoInvalidoException as e:
        raise HTTPException(status_code=409, detail=str(e)) # 409 Conflict

@router.put("/{id_req}/derivar")
def derivar_requerimiento(
    id_req: int,
    datos: DerivarTecnico,
    service: RequerimientoService = Depends(get_requerimiento_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Un Técnico deriva a otro (Interconsulta).
    """
    try:
        service.derivar_requerimiento(
            id_req=id_req,
            id_tecnico_origen=current_user.id,
            id_tecnico_destino=datos.tecnico_destino_id,
            motivo=datos.motivo
        )
        return {"mensaje": "Requerimiento derivado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id_req}/resolver")
def resolver_requerimiento(
    id_req: int,
    service: RequerimientoService = Depends(get_requerimiento_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    El Técnico marca como resuelto.
    """
    try:
        service.resolver_requerimiento(id_req, current_user.id)
        return {"mensaje": "Requerimiento resuelto exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))