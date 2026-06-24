from app.dependencies.auth import get_current_user
from app.dependencies.services import get_auth_service, get_req_service

get_requerimiento_service = get_req_service

__all__ = [
    "get_auth_service",
    "get_current_user",
    "get_req_service",
    "get_requerimiento_service",
]
