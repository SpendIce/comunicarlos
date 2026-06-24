from datetime import datetime
from typing import Optional


class Notificacion:
    """
    Alerta generada para Supervisores.

    Contexto: Cuando un Operador o Técnico realiza una acción, sus supervisores
    reciben esta notificación.
    """

    def __init__(
            self,
            id: Optional[int],
            usuario_destino=None,  # Supervisor
            mensaje: Optional[str] = None,
            evento_origen=None,  # Evento que disparó la notificación
            leida: bool = False,
            fecha_creacion: Optional[datetime] = None,
            fecha_hora_generada: Optional[datetime] = None,
            fecha_lectura: Optional[datetime] = None,
            evento=None,
            supervisor=None
    ):
        if evento is not None:
            evento_origen = evento
        if supervisor is not None:
            usuario_destino = supervisor
        if mensaje is None and evento_origen is not None:
            mensaje = evento_origen.get_descripcion_detallada()

        self.id = id
        self.usuario_destino = usuario_destino
        self.supervisor = usuario_destino
        self.mensaje = mensaje
        self.evento_origen = evento_origen
        self.evento = evento_origen
        self.leida = leida
        self.fecha_creacion = fecha_creacion or fecha_hora_generada or datetime.now()
        self.fecha_hora_generada = self.fecha_creacion
        self.fecha_lectura = fecha_lectura

    def marcar_como_leida(self) -> None:
        """
        Cambia el estado de la notificación.
        Idealmente, una notificación leída no debería volver a no-leída.
        """
        if self.leida:
            return
        self.leida = True
        self.fecha_lectura = datetime.now()

    def es_leida(self) -> bool:
        return self.leida

    def __str__(self) -> str:
        estado = "[LEÍDA]" if self.leida else "[NUEVA]"
        return f"{estado} Para {self.usuario_destino.nombre}: {self.mensaje}"
