from typing import Optional
from app.domain import Operador, Tecnico, Requerimiento, EventoFactory, Notificador
from app.domain.enums import TipoEvento
from app.services.exceptions import NotFoundException, UnauthorizedException


class AsignacionService:
    """
    Servicio de asignación y derivación de requerimientos.
    Coordina la asignación de técnicos a requerimientos.
    """

    def __init__(
            self,
            requerimiento_repository,
            usuario_repository
    ):
        """
        Args:
            requerimiento_repository: Repositorio de requerimientos
            usuario_repository: Repositorio de usuarios
        """
        self.req_repo = requerimiento_repository
        self.usuario_repo = usuario_repository
        self.notificador = Notificador()

    async def asignar_tecnico(
            self,
            requerimiento_id: int,
            tecnico_id: int,
            operador_id: int,
            comentario: Optional[str] = None
    ) -> Requerimiento:
        """
        Asigna un técnico a un requerimiento.

        Args:
            requerimiento_id: ID del requerimiento
            tecnico_id: ID del técnico a asignar
            operador_id: ID del operador que asigna
            comentario: Comentario opcional sobre la asignación

        Returns:
            Requerimiento: Requerimiento actualizado

        Raises:
            NotFoundException: Si no existen los recursos
            UnauthorizedException: Si el usuario no es operador
            EstadoInvalidoException: Si el estado no permite asignación
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(
                f"Requerimiento {requerimiento_id} no encontrado"
            )

        # Obtener técnico
        tecnico = await self.usuario_repo.buscar_por_id(tecnico_id)
        if not tecnico or not isinstance(tecnico, Tecnico):
            raise NotFoundException(f"Técnico {tecnico_id} no encontrado")

        # Obtener operador
        operador = await self.usuario_repo.buscar_por_id(operador_id)
        if not operador or not isinstance(operador, Operador):
            raise UnauthorizedException("Solo operadores pueden asignar técnicos")

        # Agregar comentario si se proporciona
        if comentario:
            from app.domain import Comentario
            comentario_obj = Comentario(
                id=None,
                texto=comentario,
                autor=operador,
                requerimiento=requerimiento
            )
            requerimiento.agregar_comentario(comentario_obj)

        # Asignar técnico (validaciones en el dominio)
        requerimiento.asignar_tecnico(tecnico, operador)

        # Crear evento de asignación
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.ASIGNACION,
            requerimiento=requerimiento,
            responsable=operador,
            tecnico_asignado=tecnico
        )
        requerimiento.agregar_evento(evento)

        # Guardar
        requerimiento_actualizado = await self.req_repo.guardar(requerimiento)

        # Notificar
        self.notificador.notificar_evento(evento)

        return requerimiento_actualizado

    async def reasignar_tecnico(
            self,
            requerimiento_id: int,
            nuevo_tecnico_id: int,
            operador_id: int,
            motivo: str
    ) -> Requerimiento:
        """
        Reasigna un requerimiento a otro técnico.

        Args:
            requerimiento_id: ID del requerimiento
            nuevo_tecnico_id: ID del nuevo técnico
            operador_id: ID del operador que reasigna
            motivo: Motivo de la reasignación

        Returns:
            Requerimiento: Requerimiento actualizado
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(
                f"Requerimiento {requerimiento_id} no encontrado"
            )

        # Obtener nuevo técnico
        nuevo_tecnico = await self.usuario_repo.buscar_por_id(nuevo_tecnico_id)
        if not nuevo_tecnico or not isinstance(nuevo_tecnico, Tecnico):
            raise NotFoundException(f"Técnico {nuevo_tecnico_id} no encontrado")

        # Obtener operador
        operador = await self.usuario_repo.buscar_por_id(operador_id)
        if not operador or not isinstance(operador, Operador):
            raise UnauthorizedException("Solo operadores pueden reasignar técnicos")

        # Reasignar (validaciones en el dominio)
        requerimiento.reasignar_tecnico(nuevo_tecnico, operador)

        # Crear evento de reasignación (usando ASIGNACION)
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.ASIGNACION,
            requerimiento=requerimiento,
            responsable=operador,
            tecnico_asignado=nuevo_tecnico
        )
        requerimiento.agregar_evento(evento)

        # Guardar
        requerimiento_actualizado = await self.req_repo.guardar(requerimiento)

        # Notificar
        self.notificador.notificar_evento(evento)

        return requerimiento_actualizado

    async def derivar_tecnico(
            self,
            requerimiento_id: int,
            tecnico_origen_id: int,
            tecnico_destino_id: int,
            motivo: str
    ) -> Requerimiento:
        """
        Deriva un requerimiento a otro técnico para interconsulta.

        Args:
            requerimiento_id: ID del requerimiento
            tecnico_origen_id: ID del técnico que deriva
            tecnico_destino_id: ID del técnico destino
            motivo: Motivo de la derivación

        Returns:
            Requerimiento: Requerimiento actualizado

        Raises:
            NotFoundException: Si no existen los recursos
            UnauthorizedException: Si no es el técnico asignado
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(
                f"Requerimiento {requerimiento_id} no encontrado"
            )

        # Obtener técnicos
        tecnico_origen = await self.usuario_repo.buscar_por_id(tecnico_origen_id)
        if not tecnico_origen or not isinstance(tecnico_origen, Tecnico):
            raise NotFoundException(f"Técnico origen {tecnico_origen_id} no encontrado")

        tecnico_destino = await self.usuario_repo.buscar_por_id(tecnico_destino_id)
        if not tecnico_destino or not isinstance(tecnico_destino, Tecnico):
            raise NotFoundException(f"Técnico destino {tecnico_destino_id} no encontrado")

        # Derivar (validaciones en el dominio)
        requerimiento.derivar_a_tecnico(tecnico_destino, tecnico_origen, motivo)

        # Crear evento de derivación
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.DERIVACION,
            requerimiento=requerimiento,
            responsable=tecnico_origen,
            tecnico_origen=tecnico_origen,
            tecnico_destino=tecnico_destino,
            motivo=motivo
        )
        requerimiento.agregar_evento(evento)

        # Guardar
        requerimiento_actualizado = await self.req_repo.guardar(requerimiento)

        # Notificar
        self.notificador.notificar_evento(evento)

        return requerimiento_actualizado
