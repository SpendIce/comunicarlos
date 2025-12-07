from typing import Optional, Dict, Any
from datetime import datetime
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
    Factory para crear diferentes tipos de eventos - Factory Pattern (Clásico)

    Implementa el patrón Factory con un único método 'crear_evento' que
    determina qué tipo de evento instanciar según el tipo recibido.
    """

    @staticmethod
    def crear_evento(
            tipo: TipoEvento,
            requerimiento,
            responsable,
            **kwargs
    ) -> Evento:
        """
        Método principal del Factory Pattern.
        Crea un evento según el tipo especificado.

        Args:
            tipo: TipoEvento que determina qué evento crear
            requerimiento: Requerimiento asociado al evento
            responsable: Usuario responsable del evento
            **kwargs: Parámetros adicionales específicos de cada tipo de evento

        Returns:
            Evento: Instancia del tipo de evento correspondiente

        Raises:
            ValueError: Si el tipo de evento no es válido

        Ejemplos:
            # Crear evento de creación
            evento = EventoFactory.crear_evento(
                TipoEvento.CREACION,
                requerimiento=req,
                responsable=solicitante
            )

            # Crear evento de asignación
            evento = EventoFactory.crear_evento(
                TipoEvento.ASIGNACION,
                requerimiento=req,
                responsable=operador,
                tecnico_asignado=tecnico
            )
        """
        # Mapeo de tipos a métodos privados de creación
        factory_methods = {
            TipoEvento.CREACION: EventoFactory._crear_evento_creacion,
            TipoEvento.ASIGNACION: EventoFactory._crear_evento_asignacion,
            TipoEvento.DERIVACION: EventoFactory._crear_evento_derivacion,
            TipoEvento.RESOLUCION: EventoFactory._crear_evento_resolucion,
            TipoEvento.REAPERTURA: EventoFactory._crear_evento_reapertura,
            TipoEvento.COMENTARIO: EventoFactory._crear_evento_comentario,
        }

        # Obtener el método correspondiente al tipo
        factory_method = factory_methods.get(tipo)

        if factory_method is None:
            raise ValueError(f"Tipo de evento no válido: {tipo}")

        # Llamar al método específico con los parámetros
        return factory_method(
            requerimiento=requerimiento,
            responsable=responsable,
            **kwargs
        )
        
    # ========================================================================
    # Métodos privados para crear cada tipo específico de evento
    # ========================================================================

    @staticmethod
    def _crear_evento_creacion(
        requerimiento,
        responsable,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoCreacion:
        """Método privado para crear EventoCreacion"""
        return EventoCreacion(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    @staticmethod
    def _crear_evento_asignacion(
        requerimiento,
        responsable,
        tecnico_asignado=None,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoAsignacion:
        """Método privado para crear EventoAsignacion"""
        if tecnico_asignado is None:
            raise ValueError("tecnico_asignado es requerido para EventoAsignacion")

        return EventoAsignacion(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            tecnico_asignado=tecnico_asignado,
            fecha_hora=fecha_hora
        )

    @staticmethod
    def _crear_evento_derivacion(
        requerimiento,
        responsable,
        tecnico_origen=None,
        tecnico_destino=None,
        motivo: Optional[str] = None,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoDerivacion:
        """Método privado para crear EventoDerivacion"""
        if tecnico_origen is None:
            raise ValueError("tecnico_origen es requerido para EventoDerivacion")
        if tecnico_destino is None:
            raise ValueError("tecnico_destino es requerido para EventoDerivacion")
        if motivo is None:
            raise ValueError("motivo es requerido para EventoDerivacion")

        return EventoDerivacion(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            tecnico_origen=tecnico_origen,
            tecnico_destino=tecnico_destino,
            motivo=motivo,
            fecha_hora=fecha_hora
        )

    @staticmethod
    def _crear_evento_resolucion(
        requerimiento,
        responsable,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoResolucion:
        """Método privado para crear EventoResolucion"""
        return EventoResolucion(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    @staticmethod
    def _crear_evento_reapertura(
        requerimiento,
        responsable,
        motivo: Optional[str] = None,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoReapertura:
        """Método privado para crear EventoReapertura"""
        if motivo is None:
            raise ValueError("motivo es requerido para EventoReapertura")

        return EventoReapertura(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            motivo=motivo,
            fecha_hora=fecha_hora
        )

    @staticmethod
    def _crear_evento_comentario(
        requerimiento,
        responsable,
        comentario=None,
        fecha_hora: Optional[datetime] = None,
        **kwargs
    ) -> EventoComentario:
        """Método privado para crear EventoComentario"""
        if comentario is None:
            raise ValueError("comentario es requerido para EventoComentario")

        return EventoComentario(
            id=None,
            responsable=responsable,
            requerimiento=requerimiento,
            comentario=comentario,
            fecha_hora=fecha_hora
        )