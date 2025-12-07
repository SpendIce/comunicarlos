from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from app.domain.enums import EstadoRequerimiento, TipoRequerimiento
from app.domain.exceptions import (
    EstadoInvalidoException,
    PermisosDenegadosException,
    ValidacionException
)


class Requerimiento(ABC):
    """Clase base abstracta para requerimientos"""

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            solicitante,  # Solicitante
            estado: EstadoRequerimiento = EstadoRequerimiento.NUEVO,
            tecnico_asignado=None,  # Tecnico opcional
            fecha_creacion: Optional[datetime] = None,
            fecha_resolucion: Optional[datetime] = None
    ):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.solicitante = solicitante
        self.estado = estado
        self.tecnico_asignado = tecnico_asignado
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.fecha_resolucion = fecha_resolucion

        # Colecciones
        self.comentarios: List = []
        self.eventos: List = []

        # Validaciones
        self._validar_datos()

    def _validar_datos(self):
        """Validaciones comunes a todos los requerimientos"""
        if len(self.titulo) < 5:
            raise ValidacionException("El título debe tener al menos 5 caracteres")
        if len(self.descripcion) < 10:
            raise ValidacionException("La descripción debe tener al menos 10 caracteres")

    @abstractmethod
    def get_tipo(self) -> TipoRequerimiento:
        """Retorna el tipo de requerimiento"""
        pass

    @abstractmethod
    def get_categoria(self) -> str:
        """Retorna la categoría del requerimiento"""
        pass

    @abstractmethod
    def calcular_prioridad(self) -> int:
        """Calcula la prioridad del requerimiento"""
        pass

    def get_dias_desde_creacion(self) -> int:
        """Calcula los días transcurridos desde la creación"""
        delta = datetime.now() - self.fecha_creacion
        return delta.days

    def agregar_comentario(self, comentario) -> None:
        """Agrega un comentario al requerimiento"""
        if self.estado == EstadoRequerimiento.RESUELTO:
            raise EstadoInvalidoException(
                "No se pueden agregar comentarios a requerimientos resueltos"
            )
        self.comentarios.append(comentario)

    def agregar_evento(self, evento) -> None:
        """Registra un evento en el historial"""
        self.eventos.append(evento)

    def asignar_tecnico(self, tecnico, operador) -> None:
        """Asigna un técnico al requerimiento"""
        if self.estado not in [EstadoRequerimiento.NUEVO, EstadoRequerimiento.ASIGNADO]:
            raise EstadoInvalidoException(
                f"No se puede asignar técnico en estado {self.estado.value}"
            )

        self.tecnico_asignado = tecnico
        self.estado = EstadoRequerimiento.ASIGNADO

    def reasignar_tecnico(self, nuevo_tecnico, operador) -> None:
        """Reasigna el requerimiento a otro técnico"""
        if not self.tecnico_asignado:
            raise EstadoInvalidoException("No hay técnico asignado para reasignar")

        if nuevo_tecnico.id == self.tecnico_asignado.id:
            raise ValidacionException("El nuevo técnico debe ser diferente al actual")

        self.tecnico_asignado = nuevo_tecnico

    def derivar_a_tecnico(self, tecnico_destino, tecnico_origen, motivo: str) -> None:
        """Deriva temporalmente a otro técnico"""
        if not self.tecnico_asignado or self.tecnico_asignado.id != tecnico_origen.id:
            raise PermisosDenegadosException(
                "Solo el técnico asignado puede derivar el requerimiento"
            )

        if tecnico_destino.id == tecnico_origen.id:
            raise ValidacionException("No se puede derivar al mismo técnico")

        self.estado = EstadoRequerimiento.EN_PROCESO

    def resolver(self, tecnico) -> None:
        """Marca el requerimiento como resuelto"""
        if not self.tecnico_asignado or self.tecnico_asignado.id != tecnico.id:
            raise PermisosDenegadosException(
                "Solo el técnico asignado puede resolver el requerimiento"
            )

        if self.estado == EstadoRequerimiento.RESUELTO:
            raise EstadoInvalidoException("El requerimiento ya está resuelto")

        self.estado = EstadoRequerimiento.RESUELTO
        self.fecha_resolucion = datetime.now()

    def reabrir(self, usuario, motivo: str) -> None:
        """Reabre un requerimiento resuelto"""
        if self.estado != EstadoRequerimiento.RESUELTO:
            raise EstadoInvalidoException(
                "Solo se pueden reabrir requerimientos resueltos"
            )

        if len(motivo) < 10:
            raise ValidacionException("El motivo debe tener al menos 10 caracteres")

        self.estado = EstadoRequerimiento.REABIERTO
        self.fecha_resolucion = None

    def get_tiempo_resolucion(self) -> Optional[str]:
        """Calcula el tiempo de resolución si está resuelto"""
        if not self.fecha_resolucion:
            return None

        delta = self.fecha_resolucion - self.fecha_creacion
        horas = delta.total_seconds() / 3600

        if horas < 24:
            return f"{int(horas)} horas"
        else:
            dias = int(horas / 24)
            horas_restantes = int(horas % 24)
            return f"{dias} días {horas_restantes} horas"

    def obtener_historial(self) -> List:
        """Retorna el historial completo de eventos"""
        return sorted(self.eventos, key=lambda e: e.fecha_hora)

    def __str__(self) -> str:
        return f"{self.get_tipo().value} #{self.id}: {self.titulo}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, estado='{self.estado.value}')>"


from app.domain.enums import NivelUrgencia, CategoriaIncidente, CategoriaSolicitud


class Incidente(Requerimiento):
    """Requerimiento de tipo Incidente - Problema con servicio existente"""

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            solicitante,
            nivel_urgencia: NivelUrgencia,
            categoria: CategoriaIncidente,
            estado: EstadoRequerimiento = EstadoRequerimiento.NUEVO,
            tecnico_asignado=None,
            fecha_creacion: Optional[datetime] = None,
            fecha_resolucion: Optional[datetime] = None
    ):
        self.nivel_urgencia = nivel_urgencia
        self.categoria = categoria
        super().__init__(
            id, titulo, descripcion, solicitante, estado,
            tecnico_asignado, fecha_creacion, fecha_resolucion
        )

    def get_tipo(self) -> TipoRequerimiento:
        return TipoRequerimiento.INCIDENTE

    def get_categoria(self) -> str:
        return self.categoria.value

    def calcular_prioridad(self) -> int:
        """
        Calcula prioridad combinando urgencia y antigüedad.
        Fórmula: peso_urgencia + días_desde_creación

        Ejemplo:
        - CRITICO (100) + 2 días = 102
        - IMPORTANTE (50) + 5 días = 55
        - MENOR (10) + 10 días = 20
        """
        peso_urgencia = self.nivel_urgencia.get_peso()
        dias = self.get_dias_desde_creacion()
        return peso_urgencia + dias

    def es_urgencia_critica(self) -> bool:
        """Verifica si es de urgencia crítica"""
        return self.nivel_urgencia == NivelUrgencia.CRITICO

    def get_peso_urgencia(self) -> int:
        """Retorna el peso numérico de la urgencia"""
        return self.nivel_urgencia.get_peso()


class Solicitud(Requerimiento):
    """Requerimiento de tipo Solicitud - Alta/baja de servicios"""

    def __init__(
            self,
            id: Optional[int],
            titulo: str,
            descripcion: str,
            solicitante,
            categoria: CategoriaSolicitud,
            estado: EstadoRequerimiento = EstadoRequerimiento.NUEVO,
            tecnico_asignado=None,
            fecha_creacion: Optional[datetime] = None,
            fecha_resolucion: Optional[datetime] = None
    ):
        self.categoria = categoria
        super().__init__(
            id, titulo, descripcion, solicitante, estado,
            tecnico_asignado, fecha_creacion, fecha_resolucion
        )

    def get_tipo(self) -> TipoRequerimiento:
        return TipoRequerimiento.SOLICITUD

    def get_categoria(self) -> str:
        return self.categoria.value

    def calcular_prioridad(self) -> int:
        """
        Las solicitudes se priorizan solo por antigüedad (FIFO).
        Fórmula: días_desde_creación
        """
        return self.get_dias_desde_creacion()

    def es_alta_servicio(self) -> bool:
        """Verifica si es solicitud de alta de servicio"""
        return self.categoria == CategoriaSolicitud.ALTA_SERVICIO

    def es_baja_servicio(self) -> bool:
        """Verifica si es solicitud de baja de servicio"""
        return self.categoria == CategoriaSolicitud.BAJA_SERVICIO

