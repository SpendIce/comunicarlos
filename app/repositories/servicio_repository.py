from abc import abstractmethod
from typing import List
from app.domain import Servicio
from app.repositories.base_repository import BaseRepository


class ServicioRepository(BaseRepository[Servicio]):
    """Interfaz del repositorio de servicios"""

    @abstractmethod
    def buscar_por_solicitante(self, solicitante_id: int) -> List[Servicio]:
        """Busca todos los servicios de un solicitante"""
        pass

    @abstractmethod
    def buscar_activos_por_solicitante(self, solicitante_id: int) -> List[Servicio]:
        """Busca servicios activos de un solicitante"""
        pass
