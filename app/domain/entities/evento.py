from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from app.domain.enums import TipoEvento


class Evento(ABC):
    """
    Clase Abstracta Base para el historial de acciones del sistema.

    Concepto POO: Herencia y Polimorfismo.
    Define el contrato base que todos los eventos deben cumplir.
    Es inmutable en la práctica: representa un hecho histórico que ya ocurrió.
    """

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            responsable,  # Usuario (Polimórfico)
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
        """Retorna el tipo enumerado correspondiente."""
        pass

    @abstractmethod
    def get_descripcion_detallada(self) -> str:
        """
        Método Polimórfico.
        Cada evento sabe cómo describirse a sí mismo en detalle para los reportes.
        """
        pass

    def __str__(self) -> str:
        return f"[{self.fecha_hora.strftime('%Y-%m-%d %H:%M')}] {self.titulo} por {self.responsable.nombre}"


# --- Implementaciones Concretas ---

class EventoCreacion(Evento):
    def __init__(self, id, responsable, requerimiento, fecha_hora=None):
        super().__init__(
            id, "Requerimiento Creado", "Inicio del ciclo de vida",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.CREACION

    def get_descripcion_detallada(self) -> str:
        return f"El requerimiento fue dado de alta en el sistema por {self.responsable.nombre}."


class EventoAsignacion(Evento):
    def __init__(self, id, responsable, requerimiento, tecnico_asignado, fecha_hora=None):
        self.tecnico_asignado = tecnico_asignado
        super().__init__(
            id, "Técnico Asignado", f"Asignado a {tecnico_asignado.nombre}",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.ASIGNACION

    def get_descripcion_detallada(self) -> str:
        return f"El operador {self.responsable.nombre} asignó el caso al técnico {self.tecnico_asignado.nombre}."


class EventoDerivacion(Evento):
    def __init__(self, id, responsable, requerimiento, tecnico_origen, tecnico_destino, motivo, fecha_hora=None):
        self.tecnico_origen = tecnico_origen
        self.tecnico_destino = tecnico_destino
        self.motivo = motivo
        super().__init__(
            id, "Derivación Técnica", "Cambio de responsable técnico",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.DERIVACION

    def get_descripcion_detallada(self) -> str:
        return (f"Derivado de {self.tecnico_origen.nombre} hacia {self.tecnico_destino.nombre}. "
                f"Motivo declarado: {self.motivo}")


class EventoResolucion(Evento):
    def __init__(self, id, responsable, requerimiento, fecha_hora=None):
        super().__init__(
            id, "Caso Resuelto", "Fin del ciclo de atención",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.RESOLUCION

    def get_descripcion_detallada(self) -> str:
        return f"El técnico {self.responsable.nombre} marcó el requerimiento como resuelto exitosamente."


class EventoReapertura(Evento):
    def __init__(self, id, responsable, requerimiento, motivo, fecha_hora=None):
        self.motivo = motivo
        super().__init__(
            id, "Caso Reabierto", "Reinicio del ciclo por inconformidad",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.REAPERTURA

    def get_descripcion_detallada(self) -> str:
        return f"El caso fue reabierto por {self.responsable.nombre}. Razón: {self.motivo}"


class EventoComentario(Evento):
    def __init__(self, id, responsable, requerimiento, comentario, fecha_hora=None):
        self.comentario = comentario  # Objeto Comentario
        super().__init__(
            id, "Nuevo Comentario", "Interacción en el hilo",
            responsable, requerimiento, fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return TipoEvento.COMENTARIO

    def get_descripcion_detallada(self) -> str:
        return f"{self.responsable.nombre} comentó: '{self.comentario.contenido[:50]}...'"