from typing import List
from app.domain.entities.usuario import Supervisor
from app.domain.entities.notificacion import Notificacion
from app.domain.entities.evento import Evento

class Notificador:
    """
    Servicio de dominio que implementa el patrón Observer.
    Notifica a supervisores cuando ocurren eventos.

    Singleton - Solo debe existir una instancia en el sistema.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Notificador, cls).__new__(cls)
            cls._instance._supervisores = []
        return cls._instance

    def __init__(self):
        pass

    def registrar_supervisor(self, supervisor: Supervisor) -> None:
        """Registra un supervisor para recibir notificaciones"""
        if supervisor not in self._supervisores:
            self._supervisores.append(supervisor)

    def desregistrar_supervisor(self, supervisor: Supervisor) -> None:
        """Desregistra un supervisor"""
        if supervisor in self._supervisores:
            self._supervisores.remove(supervisor)

    def notificar_evento(self, evento: Evento) -> List[Notificacion]:
        """
        Notifica a los supervisores interesados sobre un evento.

        Un supervisor está interesado si supervisa al responsable del evento.
        """
        supervisores_interesados = self._obtener_supervisores_interesados(evento)
        notificaciones_generadas = []

        for supervisor in supervisores_interesados:
            notificacion = Notificacion(
                id=None,
                evento=evento,
                supervisor=supervisor
            )
            supervisor.recibir_notificacion(notificacion)
            notificaciones_generadas.append(notificacion)

        return notificaciones_generadas

    def _obtener_supervisores_interesados(self, evento: Evento) -> List[Supervisor]:
        """
        Determina qué supervisores deben ser notificados.

        Un supervisor es notificado si supervisa al responsable del evento.
        """
        supervisores_interesados = []
        responsable = evento.responsable

        for supervisor in self._supervisores:
            if supervisor.supervisa_empleado(responsable):
                supervisores_interesados.append(supervisor)

        return supervisores_interesados

    def get_supervisores_registrados(self) -> List[Supervisor]:
        """Retorna la lista de supervisores registrados"""
        return self._supervisores.copy()

    def limpiar(self) -> None:
        """Limpia todos los supervisores registrados (útil para testing)"""
        self._supervisores.clear()
