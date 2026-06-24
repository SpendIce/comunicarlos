from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from app.domain.enums import EstadoRequerimiento, TipoRequerimiento, NivelUrgencia, CategoriaSolicitud
from app.domain.exceptions import EstadoInvalidoException, ValidacionException


class Requerimiento(ABC):
    """
    Clase base para Incidentes y Solicitudes.
    Mantiene el historial inmutable y gestiona el ciclo de vida (State pattern simplificado).
    """

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            solicitante,
            estado: EstadoRequerimiento = EstadoRequerimiento.NUEVO,
            tecnico_asignado=None,
            fecha_creacion: Optional[datetime] = None,
            fecha_resolucion: Optional[datetime] = None
    ):
        self._validar_contenido(titulo, descripcion)

        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.solicitante = solicitante
        self.estado = estado
        self.tecnico_asignado = tecnico_asignado
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.fecha_resolucion = fecha_resolucion

        # Historial de eventos y comentarios (Composición)
        self.eventos: List = []
        self.comentarios: List = []

    def _validar_contenido(self, titulo: str, descripcion: str):
        """Validaciones de integridad de datos básicas."""
        if len(titulo) < 5:
            raise ValidacionException("El título es demasiado corto (mínimo 5 caracteres).")
        if len(descripcion) < 10:
            raise ValidacionException("La descripción debe ser detallada (mínimo 10 caracteres).")

    @abstractmethod
    def calcular_prioridad(self) -> int:
        """
        Método Polimórfico Clave:
        Cada tipo de requerimiento decide cómo se prioriza en la cola de atención.
        Retorna un entero (mayor número = mayor prioridad).
        """
        pass

    def asignar_tecnico(self, tecnico, operador=None) -> None:
        """Transición de estado: NUEVO -> ASIGNADO"""
        if self.estado not in [EstadoRequerimiento.NUEVO, EstadoRequerimiento.ASIGNADO]:
            raise EstadoInvalidoException(f"No se puede asignar un requerimiento en estado {self.estado.value}")

        self.tecnico_asignado = tecnico
        self.estado = EstadoRequerimiento.ASIGNADO

    def resolver(self, tecnico=None) -> None:
        """Transición de estado: ASIGNADO/EN_PROCESO -> RESUELTO"""
        if self.estado == EstadoRequerimiento.RESUELTO:
            raise EstadoInvalidoException("El requerimiento ya se encuentra resuelto.")

        self.estado = EstadoRequerimiento.RESUELTO
        self.fecha_resolucion = datetime.now()

    def agregar_evento(self, evento) -> None:
        """El historial es solo de agregado (append-only) para auditoría."""
        self.eventos.append(evento)

    def agregar_comentario(self, comentario) -> None:
        self.comentarios.append(comentario)


class Incidente(Requerimiento):
    """
    Problema con un servicio existente.
    Prioridad basada en Urgencia + Antigüedad.
    """

    def __init__(self, id, titulo, descripcion, solicitante, nivel_urgencia: NivelUrgencia, categoria, **kwargs):
        self.nivel_urgencia = nivel_urgencia
        self.categoria = categoria
        super().__init__(id, titulo, descripcion, solicitante, **kwargs)

    def calcular_prioridad(self) -> int:
        # Lógica de Negocio: Peso de urgencia (100, 50, 10) + días de espera.
        dias_abierto = (datetime.now() - self.fecha_creacion).days
        return self.nivel_urgencia.get_peso() + dias_abierto

    def get_tipo(self) -> TipoRequerimiento:
        return TipoRequerimiento.INCIDENTE


class Solicitud(Requerimiento):
    """
    Pedido de nuevo servicio o baja.
    Prioridad basada estrictamente en FIFO (First In, First Out).
    """

    def __init__(self, id, titulo, descripcion, solicitante, categoria: CategoriaSolicitud, **kwargs):
        self.categoria = categoria
        super().__init__(id, titulo, descripcion, solicitante, **kwargs)

    def calcular_prioridad(self) -> int:
        # Lógica de Negocio: Solo importa cuánto tiempo lleva esperando.
        return (datetime.now() - self.fecha_creacion).days

    def get_tipo(self) -> TipoRequerimiento:
        return TipoRequerimiento.SOLICITUD
