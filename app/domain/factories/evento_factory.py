from datetime import datetime
from typing import Optional
from app.domain.enums import TipoEvento
from app.domain.entities.evento import (
    Evento,
    EventoCreacion,
    EventoAsignacion,
    EventoDerivacion,
    EventoResolucion,
    EventoReapertura,
    EventoComentario
)


class EventoFactory:
    """
    [Patrón Factory Method]
    Centraliza la lógica de instanciación de la jerarquía de eventos.

    Beneficio POO: Desacoplamiento. Los servicios no necesitan conocer las
    clases concretas (EventoAsignacion, EventoDerivacion, etc.) ni sus
    constructores específicos. Si mañana cambia cómo se construye un evento,
    solo modificamos esta clase.
    """

    @staticmethod
    def crear_evento(
            tipo: TipoEvento,
            requerimiento,
            responsable,
            **kwargs
    ) -> Evento:
        """
        Crea una instancia concreta de Evento basada en el 'tipo'.
        Valida que los argumentos necesarios para ese tipo específico estén presentes.
        """

        # Diccionario de estrategias (Dispatch Table) para evitar múltiples if/else
        constructores = {
            TipoEvento.CREACION: EventoFactory._crear_creacion,
            TipoEvento.ASIGNACION: EventoFactory._crear_asignacion,
            TipoEvento.DERIVACION: EventoFactory._crear_derivacion,
            TipoEvento.RESOLUCION: EventoFactory._crear_resolucion,
            TipoEvento.REAPERTURA: EventoFactory._crear_reapertura,
            TipoEvento.COMENTARIO: EventoFactory._crear_comentario,
        }

        constructor = constructores.get(tipo)
        if not constructor:
            raise ValueError(f"Tipo de evento no soportado por la fábrica: {tipo}")

        # Delegamos la creación al método específico
        return constructor(requerimiento, responsable, **kwargs)

    # ==========================================================================
    # Métodos Privados de Construcción (Helpers)
    # Encapsulan la validación específica de cada tipo de evento.
    # ==========================================================================

    @staticmethod
    def _crear_creacion(req, resp, **kwargs) -> EventoCreacion:
        return EventoCreacion(id=None, responsable=resp, requerimiento=req)

    @staticmethod
    def _crear_asignacion(req, resp, tecnico_asignado=None, **kwargs) -> EventoAsignacion:
        if not tecnico_asignado:
            raise ValueError("Error de Factory: Se requiere 'tecnico_asignado' para eventos de Asignación.")

        return EventoAsignacion(
            id=None,
            responsable=resp,
            requerimiento=req,
            tecnico_asignado=tecnico_asignado
        )

    @staticmethod
    def _crear_derivacion(req, resp, tecnico_origen=None, tecnico_destino=None, motivo=None,
                          **kwargs) -> EventoDerivacion:
        # Validación de integridad de datos obligatoria para derivaciones
        if not all([tecnico_origen, tecnico_destino, motivo]):
            raise ValueError("Error de Factory: Derivación requiere técnico origen, destino y motivo.")

        return EventoDerivacion(
            id=None,
            responsable=resp,
            requerimiento=req,
            tecnico_origen=tecnico_origen,
            tecnico_destino=tecnico_destino,
            motivo=motivo
        )

    @staticmethod
    def _crear_resolucion(req, resp, **kwargs) -> EventoResolucion:
        return EventoResolucion(id=None, responsable=resp, requerimiento=req)

    @staticmethod
    def _crear_reapertura(req, resp, motivo=None, **kwargs) -> EventoReapertura:
        if not motivo:
            raise ValueError("Error de Factory: Se debe especificar un motivo para reabrir un caso.")

        return EventoReapertura(
            id=None,
            responsable=resp,
            requerimiento=req,
            motivo=motivo
        )

    @staticmethod
    def _crear_comentario(req, resp, comentario=None, **kwargs) -> EventoComentario:
        if not comentario:
            raise ValueError("Error de Factory: El contenido del comentario es obligatorio.")

        return EventoComentario(
            id=None,
            responsable=resp,
            requerimiento=req,
            comentario=comentario
        )