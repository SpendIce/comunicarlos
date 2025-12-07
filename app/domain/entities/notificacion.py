from datetime import datetime
from typing import Optional


class Notificacion:
    """Notificación enviada a un supervisor"""

    def __init__(
            self,
            id: Optional[int],
            evento,  # Evento
            supervisor,  # Supervisor
            fecha_hora_generada: Optional[datetime] = None,
            leida: bool = False,
            fecha_lectura: Optional[datetime] = None
    ):
        self.id = id
        self.evento = evento
        self.supervisor = supervisor
        self.fecha_hora_generada = fecha_hora_generada or datetime.now()
        self.leida = leida
        self.fecha_lectura = fecha_lectura

    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída"""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = datetime.now()

    def get_descripcion(self) -> str:
        """Retorna la descripción del evento notificado"""
        return self.evento.get_descripcion_detallada()

    def es_leida(self) -> bool:
        """Verifica si la notificación fue leída"""
        return self.leida

    def __str__(self) -> str:
        estado = "Leída" if self.leida else "No leída"
        return f"[{estado}] {self.get_descripcion()}"

    def __repr__(self) -> str:
        return f"<Notificacion(id={self.id}, leida={self.leida}, fecha='{self.fecha_hora_generada}')>"
