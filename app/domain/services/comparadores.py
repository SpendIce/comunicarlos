from typing import Protocol
from app.domain.entities.requerimiento import Requerimiento


class ComparadorRequerimiento(Protocol):
    """Interfaz para comparadores de requerimientos"""

    def compare(self, req1: Requerimiento, req2: Requerimiento) -> int:
        """
        Compara dos requerimientos.
        Retorna:
        - Negativo si req1 < req2
        - 0 si req1 == req2
        - Positivo si req1 > req2
        """
        ...


class ComparadorPorPrioridad:
    """Comparador que ordena por prioridad (mayor prioridad primero)"""

    def compare(self, req1: Requerimiento, req2: Requerimiento) -> int:
        """Mayor prioridad primero (orden descendente)"""
        prioridad1 = req1.calcular_prioridad()
        prioridad2 = req2.calcular_prioridad()
        return prioridad2 - prioridad1  # Descendente


class ComparadorPorAntiguedad:
    """Comparador que ordena por fecha de creación (más antiguo primero)"""

    def compare(self, req1: Requerimiento, req2: Requerimiento) -> int:
        """Más antiguo primero (orden ascendente)"""
        if req1.fecha_creacion < req2.fecha_creacion:
            return -1
        elif req1.fecha_creacion > req2.fecha_creacion:
            return 1
        return 0
