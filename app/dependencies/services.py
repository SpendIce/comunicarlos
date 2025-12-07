from fastapi import Depends
from app.infrastructure.mongodb.database import mongodb
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.requerimiento_repository import RequerimientoRepository
from app.repositories.servicio_repository import ServicioRepository
from app.repositories.notificacion_repository import NotificacionRepository
from app.services.authentication_service import AutenticacionService
from app.services.requerimiento_service import RequerimientoService
from app.services.asignacion_service import AsignacionService
from app.services.comentario_service import ComentarioService
from app.services.notificacion_service import NotificacionService
from app.services.servicio_service import ServicioService
from app.services.reporte_service import ReporteService


# --- Repositories ---
def get_db():
    return mongodb.get_database()


def get_usuario_repo(db=Depends(get_db)):
    return UsuarioRepository(db)


def get_requerimiento_repo(db=Depends(get_db), user_repo=Depends(get_usuario_repo)):
    return RequerimientoRepository(db, user_repo)


class ServicioRepositoryImpl(ServicioRepository):
    def __init__(self, db):
        self.collection = db["servicios"]

    def guardar(self, entidad): pass

    def buscar_por_id(self, id): pass

    def eliminar(self, id): pass

    def buscar_todos(self): pass

    async def buscar_por_solicitante(self, id):
        cursor = self.collection.find({"solicitante_id": id})
        return await cursor.to_list(length=100)

    async def buscar_activos_por_solicitante(self, id): return []


def get_servicio_repo(db=Depends(get_db)):
    # Aquí deberías usar una clase concreta completa, usamos un mock funcional por ahora
    # o extender UsuarioRepository que ya maneja servicios internamente.
    # Dado que UsuarioRepository ya maneja servicios, podemos reusar lógica allí o instanciar uno nuevo.
    return ServicioRepositoryImpl(db)


class NotificacionRepositoryImpl(NotificacionRepository):
    def __init__(self, db, user_repo):
        self.collection = db["notificaciones"]
        self.user_repo = user_repo

    async def guardar(self, notif):
        # Lógica de guardado simplificada
        doc = {"_id": notif.id, "leida": notif.leida, "supervisor_id": notif.supervisor.id}
        await self.collection.replace_one({"_id": notif.id}, doc, upsert=True)
        return notif

    async def buscar_por_id(self, id):
        return None

    def eliminar(self, id):
        return True

    def buscar_todos(self):
        return []

    async def buscar_por_supervisor(self, supervisor_id, leida=None, page=0, size=20):
        query = {"supervisor_id": supervisor_id}
        if leida is not None: query["leida"] = leida
        cursor = self.collection.find(query).skip(page * size).limit(size)
        return await cursor.to_list(length=size)  # Falta mapeo entidad

    async def contar_por_supervisor(self, supervisor_id, leida=None):
        query = {"supervisor_id": supervisor_id}
        if leida is not None: query["leida"] = leida
        return await self.collection.count_documents(query)


def get_notificacion_repo(
    db=Depends(get_db),
    user_repo=Depends(get_usuario_repo)
):
    return NotificacionRepositoryImpl(db, user_repo)


# --- Services ---
def get_auth_service(
    user_repo=Depends(get_usuario_repo),
    serv_repo=Depends(get_servicio_repo)
):
    return AutenticacionService(user_repo, serv_repo)


def get_req_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo)
):
    return RequerimientoService(req_repo, user_repo)


def get_asignacion_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo)
):
    return AsignacionService(req_repo, user_repo)


def get_comentario_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo)
):
    return ComentarioService(req_repo, user_repo)


def get_notificacion_service(
    notif_repo=Depends(get_notificacion_repo),
    user_repo=Depends(get_usuario_repo)
):
    return NotificacionService(notif_repo, user_repo)


def get_servicio_service(
    serv_repo=Depends(get_servicio_repo),
    user_repo=Depends(get_usuario_repo),
    req_repo=Depends(get_requerimiento_repo)
):
    return ServicioService(serv_repo, user_repo, req_repo)

def get_reporte_service(
    req_repo=Depends(get_requerimiento_repo),
    user_repo=Depends(get_usuario_repo)
):
    return ReporteService(req_repo, user_repo)