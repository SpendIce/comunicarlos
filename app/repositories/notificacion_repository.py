from abc import abstractmethod
from typing import List, Optional
from app.domain import Notificacion
from app.repositories.base_repository import BaseRepository


class NotificacionRepository(BaseRepository[Notificacion]):
    """Interfaz del repositorio de notificaciones"""

    @abstractmethod
    def buscar_por_supervisor(
            self,
            supervisor_id: int,
            leida: Optional[bool] = None,
            page: int = 0,
            size: int = 20
    ) -> List[Notificacion]:
        """Busca notificaciones de un supervisor"""
        pass

    @abstractmethod
    def contar_por_supervisor(
            self,
            supervisor_id: int,
            leida: Optional[bool] = None
    ) -> int:
        """Cuenta notificaciones de un supervisor"""
        pass
