from typing import List, Optional
from app.domain import Supervisor, Notificacion
from app.services.exceptions import NotFoundException, UnauthorizedException


class NotificacionService:
    """
    Servicio de gestión de notificaciones.
    Maneja la consulta y marcado de notificaciones para supervisores.
    """

    def __init__(
            self,
            notificacion_repository,
            usuario_repository
    ):
        """
        Args:
            notificacion_repository: Repositorio de notificaciones
            usuario_repository: Repositorio de usuarios
        """
        self.notif_repo = notificacion_repository
        self.usuario_repo = usuario_repository

    async def listar_notificaciones(
            self,
            supervisor_id: int,
            leida: Optional[bool] = None,
            page: int = 0,
            size: int = 20
    ) -> tuple[List[Notificacion], int]:
        """
        Lista notificaciones de un supervisor.

        Args:
            supervisor_id: ID del supervisor
            leida: Filtro por estado de lectura (opcional)
            page: Número de página
            size: Tamaño de página

        Returns:
            tuple: (lista_notificaciones, total)

        Raises:
            NotFoundException: Si el supervisor no existe
        """
        # Verificar que es supervisor
        supervisor = await self.usuario_repo.buscar_por_id(supervisor_id)
        if not supervisor or not isinstance(supervisor, Supervisor):
            raise NotFoundException(f"Supervisor {supervisor_id} no encontrado")

        # Buscar notificaciones
        notificaciones = await self.notif_repo.buscar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=leida,
            page=page,
            size=size
        )

        total = await self.notif_repo.contar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=leida
        )

        return notificaciones, total

    async def marcar_como_leida(
            self,
            notificacion_id: int,
            supervisor_id: int
    ) -> Notificacion:
        """
        Marca una notificación como leída.

        Args:
            notificacion_id: ID de la notificación
            supervisor_id: ID del supervisor

        Returns:
            Notificacion: Notificación actualizada

        Raises:
            NotFoundException: Si no existe
            UnauthorizedException: Si no es su notificación
        """
        # Obtener notificación
        notificacion = await self.notif_repo.buscar_por_id(notificacion_id)
        if not notificacion:
            raise NotFoundException(
                f"Notificación {notificacion_id} no encontrada"
            )

        # Verificar que es del supervisor
        if notificacion.supervisor.id != supervisor_id:
            raise UnauthorizedException(
                "No tiene permisos para marcar esta notificación"
            )

        # Marcar como leída
        notificacion.marcar_como_leida()

        # Guardar
        notificacion_actualizada = await self.notif_repo.guardar(notificacion)

        return notificacion_actualizada

    async def marcar_todas_leidas(
            self,
            supervisor_id: int
    ) -> int:
        """
        Marca todas las notificaciones de un supervisor como leídas.

        Args:
            supervisor_id: ID del supervisor

        Returns:
            int: Cantidad de notificaciones marcadas
        """
        # Verificar que es supervisor
        supervisor = await self.usuario_repo.buscar_por_id(supervisor_id)
        if not supervisor or not isinstance(supervisor, Supervisor):
            raise NotFoundException(f"Supervisor {supervisor_id} no encontrado")

        # Obtener notificaciones no leídas
        notificaciones_no_leidas = await self.notif_repo.buscar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=False,
            page=0,
            size=1000  # Todas las no leídas
        )

        # Marcar cada una
        contador = 0
        for notificacion in notificaciones_no_leidas:
            notificacion.marcar_como_leida()
            self.notif_repo.guardar(notificacion)
            contador += 1

        return contador

    async def obtener_resumen(
            self,
            supervisor_id: int
    ) -> dict:
        """
        Obtiene un resumen de notificaciones del supervisor.

        Args:
            supervisor_id: ID del supervisor

        Returns:
            dict: Resumen con totales por tipo
        """
        total_no_leidas = await self.notif_repo.contar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=False
        )

        total_leidas = await self.notif_repo.contar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=True
        )

        # Obtener últimas notificaciones
        ultimas = await self.notif_repo.buscar_por_supervisor(
            supervisor_id=supervisor_id,
            leida=False,
            page=0,
            size=5
        )

        return {
            "totalNoLeidas": total_no_leidas,
            "totalLeidas": total_leidas,
            "ultimasNotificaciones": ultimas
        }
