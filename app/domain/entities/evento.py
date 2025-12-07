from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.domain.enums import TipoEvento


class Evento(ABC):
    """Clase base abstracta para eventos del sistema"""

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            responsable,  # Usuario
            requerimiento,  # Requerimiento
            fecha_hora: Optional[datetime] = None
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.responsable = responsable
        self.requerimiento = requerimiento
        self.fecha_hora = fecha_hora or datetime.now()

    @abstractmethod
    def get_tipo_evento(self) -> TipoEvento:
        """Retorna el tipo de evento"""
        pass

    @abstractmethod
    def get_descripcion_detallada(self) -> str:
        """Retorna una descripción detallada del evento"""
        pass

    def __str__(self) -> str:
        return f"{self.get_tipo_evento().value}: {self.titulo}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, fecha='{self.fecha_hora}')>"


class EventoCreacion(Evento):
    """Evento de creación de requerimiento"""

    def __init__(
            self,
            id: Optional[int],
            responsable,
            requerimiento,
            fecha_hora: Optional[datetime] = None
    ):
        super().__init__(
            id=id,
            titulo="Requerimiento creado",
            descripcion=f"Requerimiento creado por {responsable.nombre}",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.CREACION

    def get_descripcion_detallada(self) -> str:
        return f"{self.responsable.nombre} creó el requerimiento #{self.requerimiento.id}"


class EventoAsignacion(Evento):
    """Evento de asignación de técnico"""

    def __init__(
            self,
            id: Optional[int],
            responsable,  # Operador que asignó
            requerimiento,
            tecnico_asignado,  # Técnico asignado
            fecha_hora: Optional[datetime] = None
    ):
        self.tecnico_asignado = tecnico_asignado
        super().__init__(
            id=id,
            titulo="Requerimiento asignado",
            descripcion=f"Asignado a {tecnico_asignado.nombre} por {responsable.nombre}",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.ASIGNACION

    def get_descripcion_detallada(self) -> str:
        return (f"{self.responsable.nombre} asignó el requerimiento #{self.requerimiento.id} "
                f"a {self.tecnico_asignado.nombre}")


class EventoDerivacion(Evento):
    """Evento de derivación a otro técnico"""

    def __init__(
            self,
            id: Optional[int],
            responsable,  # Técnico origen
            requerimiento,
            tecnico_origen,
            tecnico_destino,
            motivo: str,
            fecha_hora: Optional[datetime] = None
    ):
        self.tecnico_origen = tecnico_origen
        self.tecnico_destino = tecnico_destino
        self.motivo = motivo
        super().__init__(
            id=id,
            titulo="Requerimiento derivado",
            descripcion=f"Derivado de {tecnico_origen.nombre} a {tecnico_destino.nombre}",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.DERIVACION

    def get_descripcion_detallada(self) -> str:
        return (f"{self.tecnico_origen.nombre} derivó el requerimiento #{self.requerimiento.id} "
                f"a {self.tecnico_destino.nombre}. Motivo: {self.motivo}")


class EventoResolucion(Evento):
    """Evento de resolución de requerimiento"""

    def __init__(
            self,
            id: Optional[int],
            responsable,  # Técnico que resolvió
            requerimiento,
            fecha_hora: Optional[datetime] = None
    ):
        super().__init__(
            id=id,
            titulo="Requerimiento resuelto",
            descripcion=f"Resuelto por {responsable.nombre}",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.RESOLUCION

    def get_descripcion_detallada(self) -> str:
        return f"{self.responsable.nombre} resolvió el requerimiento #{self.requerimiento.id}"


class EventoReapertura(Evento):
    """Evento de reapertura de requerimiento"""

    def __init__(
            self,
            id: Optional[int],
            responsable,
            requerimiento,
            motivo: str,
            fecha_hora: Optional[datetime] = None
    ):
        self.motivo = motivo
        super().__init__(
            id=id,
            titulo="Requerimiento reabierto",
            descripcion=f"Reabierto por {responsable.nombre}",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.REAPERTURA

    def get_descripcion_detallada(self) -> str:
        return (f"{self.responsable.nombre} reabrió el requerimiento #{self.requerimiento.id}. "
                f"Motivo: {self.motivo}")


class EventoComentario(Evento):
    """Evento de agregado de comentario"""

    def __init__(
            self,
            id: Optional[int],
            responsable,
            requerimiento,
            comentario,  # Comentario
            fecha_hora: Optional[datetime] = None
    ):
        self.comentario = comentario
        super().__init__(
            id=id,
            titulo="Comentario agregado",
            descripcion=f"{responsable.nombre} agregó un comentario",
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.COMENTARIO

    def get_descripcion_detallada(self) -> str:
        return (f"{self.responsable.nombre} agregó un comentario al requerimiento "
                f"#{self.requerimiento.id}")
