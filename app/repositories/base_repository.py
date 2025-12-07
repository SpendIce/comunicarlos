from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Interfaz base para todos los repositorios.
    Define el contrato que deben cumplir todas las implementaciones.

    Aplica Repository Pattern - La interfaz está en el dominio,
    las implementaciones concretas están en infraestructura.
    """

    @abstractmethod
    def guardar(self, entidad: T) -> T:
        """
        Guarda o actualiza una entidad.

        Args:
            entidad: Entidad del dominio a persistir

        Returns:
            T: Entidad guardada con ID asignado
        """
        pass

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[T]:
        """
        Busca una entidad por su ID.

        Args:
            id: Identificador único

        Returns:
            Optional[T]: Entidad encontrada o None
        """
        pass

    @abstractmethod
    def eliminar(self, id: int) -> bool:
        """
        Elimina una entidad por su ID.

        Args:
            id: Identificador único

        Returns:
            bool: True si se eliminó correctamente
        """
        pass

    @abstractmethod
    def buscar_todos(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Busca todas las entidades con paginación.

        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros

        Returns:
            List[T]: Lista de entidades
        """
        pass

