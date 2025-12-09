from app.infrastructure.mongodb.database import mongodb
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.requerimiento_repository import RequerimientoRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.servicio_repository import ServicioRepository
from app.repositories.notificacion_repository import NotificacionRepository

def get_usuario_repo() -> UsuarioRepository:
    db = mongodb.get_database()
    return UsuarioRepository(db)

def get_requerimiento_repo() -> RequerimientoRepository:
    db = mongodb.get_database()
    usuario_repo = get_usuario_repo()
    return RequerimientoRepository(db, usuario_repo)

async def get_token_repo() -> TokenRepository:
    db = mongodb.get_database()
    repo = TokenRepository(db)
    await repo.crear_indice_ttl()
    return repo

def get_servicio_repo() -> ServicioRepository:
    db = mongodb.get_database()
    return ServicioRepository(db)

def get_notificacion_repo() -> NotificacionRepository:
    db = mongodb.get_database()
    user_repo = get_usuario_repo()
    return NotificacionRepository(db, user_repo)