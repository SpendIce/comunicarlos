"""
Inyección de dependencias para repositorios.
Crea instancias conectadas a MongoDB.
"""
from app.infrastructure.mongodb.database import mongodb
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.requerimiento_repository import RequerimientoRepository

def get_usuario_repository() -> UsuarioRepository:
    """Dependency para repositorio de usuarios"""
    db = mongodb.get_database()
    return UsuarioRepository(db)

def get_requerimiento_repository() -> RequerimientoRepository:
    """Dependency para repositorio de requerimientos"""
    db = mongodb.get_database()
    usuario_repo = get_usuario_repository()
    return RequerimientoRepository(db, usuario_repo)
