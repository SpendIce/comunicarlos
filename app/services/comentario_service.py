from typing import List
from app.domain import Comentario, Usuario, EventoFactory
from app.domain.enums import TipoEvento
from app.services.exceptions import NotFoundException, UnauthorizedException


class ComentarioService:
    """
    Servicio de gestión de comentarios.
    Coordina la creación y consulta de comentarios en requerimientos.
    """

    def __init__(
            self,
            requerimiento_repository,
            usuario_repository,
            notificador
    ):
        """
        Args:
            requerimiento_repository: Repositorio de requerimientos
            usuario_repository: Repositorio de usuarios
        """
        self.req_repo = requerimiento_repository
        self.usuario_repo = usuario_repository
        self.notificador = notificador

    async def agregar_comentario(
            self,
            requerimiento_id: int,
            usuario_id: int,
            texto: str
    ) -> Comentario:
        """
        Agrega un comentario a un requerimiento.

        Args:
            requerimiento_id: ID del requerimiento
            usuario_id: ID del usuario que comenta
            texto: Texto del comentario

        Returns:
            Comentario: Comentario creado

        Raises:
            NotFoundException: Si no existen los recursos
            UnauthorizedException: Si no tiene permisos
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(
                f"Requerimiento {requerimiento_id} no encontrado"
            )

        # Obtener usuario
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise NotFoundException(f"Usuario {usuario_id} no encontrado")

        # Verificar permisos
        if not usuario.puede_comentar_requerimiento(requerimiento):
            raise UnauthorizedException(
                "No tiene permisos para comentar en este requerimiento"
            )

        # Crear comentario
        nuevo_id = await self.req_repo.siguiente_id_comentario()
        comentario = Comentario(
            id=nuevo_id,
            texto=texto,
            autor=usuario,
            requerimiento=requerimiento
        )

        # Agregar al requerimiento
        requerimiento.agregar_comentario(comentario)

        # Crear evento de comentario
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.COMENTARIO,
            requerimiento=requerimiento,
            responsable=usuario,
            comentario=comentario
        )
        requerimiento.agregar_evento(evento)

        # Guardar requerimiento con el nuevo comentario
        await self.req_repo.guardar(requerimiento)

        # Notificar
        await self.notificador.notificar_evento(evento)

        return comentario

    async def listar_comentarios(
            self,
            requerimiento_id: int,
            usuario_actual: Usuario
    ) -> List[Comentario]:
        """
        Lista comentarios de un requerimiento.

        Args:
            requerimiento_id: ID del requerimiento
            usuario_actual: Usuario que realiza la consulta

        Returns:
            List[Comentario]: Lista de comentarios ordenada cronológicamente

        Raises:
            NotFoundException: Si no existe el requerimiento
            UnauthorizedException: Si no tiene permisos
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(
                f"Requerimiento {requerimiento_id} no encontrado"
            )

        # Verificar permisos
        if not usuario_actual.puede_ver_requerimiento(requerimiento):
            raise UnauthorizedException(
                "No tiene permisos para ver este requerimiento"
            )

        # Retornar comentarios ordenados por fecha
        return sorted(
            requerimiento.comentarios,
            key=lambda c: c.fecha_hora
        )
