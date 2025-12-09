from fastapi import Depends
from app.services.authentication_service import AutenticacionService
from app.services.requerimiento_service import RequerimientoService
from app.services.asignacion_service import AsignacionService
from app.services.comentario_service import ComentarioService
from app.services.notificacion_service import NotificacionService
from app.services.servicio_service import ServicioService
from app.services.reporte_service import ReporteService
from app.repositories.token_repository import TokenRepository
from app.dependencies.repositories import (
    get_usuario_repo,
    get_requerimiento_repo,
    get_servicio_repo,
    get_notificacion_repo,
    get_token_repo
)
from app.domain.services.notificador import Notificador
from app.infrastructure.mongodb.sequence import SequenceGenerator
from app.infrastructure.mongodb.database import mongodb

def _crear_notificador(user_repo, notif_repo) -> Notificador:
    db = mongodb.get_database()
    seq = SequenceGenerator(db)
    return Notificador(user_repo, notif_repo, seq)

async def get_auth_service(
    user_repo=Depends(get_usuario_repo),
    servicio_repo=Depends(get_servicio_repo),
    token_repo: TokenRepository = Depends(get_token_repo)
) -> AutenticacionService:
    return AutenticacionService(user_repo, servicio_repo, token_repo)

def get_req_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo),
    notif_repo=Depends(get_notificacion_repo)
):
    notificador = _crear_notificador(user_repo, notif_repo)
    return RequerimientoService(req_repo, user_repo, notificador)

def get_asignacion_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo),
    notif_repo=Depends(get_notificacion_repo)
):
    notificador = _crear_notificador(user_repo, notif_repo)
    return AsignacionService(req_repo, user_repo, notificador)

def get_comentario_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo),
    notif_repo=Depends(get_notificacion_repo)
):
    notificador = _crear_notificador(user_repo, notif_repo)
    return ComentarioService(req_repo, user_repo, notificador)

def get_notificacion_service(
    notif_repo=Depends(get_notificacion_repo),
    user_repo=Depends(get_usuario_repo)
):
    return NotificacionService(notif_repo, user_repo)

def get_servicio_service(
    serv_repo=Depends(get_servicio_repo),
    user_repo=Depends(get_usuario_repo),
    req_repo=Depends(get_requerimiento_repo),
    notif_repo=Depends(get_notificacion_repo)
):
    notificador = _crear_notificador(user_repo, notif_repo)
    return ServicioService(serv_repo, user_repo, req_repo, notificador)

def get_reporte_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo)
):
    return ReporteService(req_repo, user_repo)