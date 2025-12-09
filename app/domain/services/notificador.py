from app.domain.entities.evento import Evento
from app.domain.entities.notificacion import Notificacion
from app.repositories.notificacion_repository import NotificacionRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.mongodb.sequence import SequenceGenerator


class Notificador:
    def __init__(
            self,
            usuario_repo: UsuarioRepository,
            notificacion_repo: NotificacionRepository,
            sequence_generator: SequenceGenerator = None
    ):
        self.user_repo = usuario_repo
        self.notif_repo = notificacion_repo
        self.sequence = sequence_generator if sequence_generator else getattr(notificacion_repo, 'sequence', None)

    async def notificar_evento(self, evento: Evento):
        """
        Genera notificaciones para los supervisores del responsable del evento.
        """
        actor = evento.responsable

        supervisores = await self.user_repo.buscar_supervisores_de_empleado(actor.id)

        if not supervisores:
            return

        for supervisor in supervisores:
            if self.sequence:
                notif_id = await self.sequence.get_next("notificacion_id")
            else:
                import time
                notif_id = int(time.time() * 1000)

            notificacion = Notificacion(
                id=notif_id,
                evento=evento,
                supervisor=supervisor
            )

            # 3. Persistir
            await self.notif_repo.guardar(notificacion)