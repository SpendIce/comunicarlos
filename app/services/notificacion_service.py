from typing import List
from app.domain.entities.notificacion import Notificacion


class NotificacionService:
    """
    Gestiona la comunicación asíncrona hacia los supervisores.
    Implementa la lógica del requisito: "Supervisor monitorea a Operador/Técnico".
    """

    def __init__(self, notificacion_repo, usuario_repo):
        self.notificacion_repo = notificacion_repo
        self.usuario_repo = usuario_repo

    def notificar_accion(self, evento, empleado_involucrado):
        """
        Busca a los supervisores del empleado que realizó la acción
        y les genera una alerta.
        """
        # Obtenemos todos los supervisores (o filtramos en DB idealmente)
        todos_supervisores = self.usuario_repo.obtener_supervisores()

        for supervisor in todos_supervisores:
            # Preguntamos al Supervisor si le interesa este empleado (Dominio)
            if supervisor.supervisa_empleado(empleado_involucrado):
                nueva_notif = Notificacion(
                    id=None,
                    usuario_destino=supervisor,
                    mensaje=evento.get_descripcion_detallada(),
                    evento_origen=evento
                )

                self.notificacion_repo.guardar(nueva_notif)

    def marcar_como_leida(self, id_notificacion: int):
        notif = self.notificacion_repo.obtener_por_id(id_notificacion)
        if notif:
            notif.marcar_como_leida()
            self.notificacion_repo.actualizar(notif)