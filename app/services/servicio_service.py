from typing import List, Optional
from app.domain import Servicio, Solicitante, Solicitud, EventoFactory, Notificador
from app.domain.enums import TipoServicio, CategoriaSolicitud, TipoEvento
from app.services.exceptions import NotFoundException, UnauthorizedException


class ServicioService:
    """
    Servicio de gestión de servicios suscritos.
    Maneja altas, bajas y consultas de servicios.
    """

    def __init__(
            self,
            servicio_repository,
            usuario_repository,
            requerimiento_repository
    ):
        """
        Args:
            servicio_repository: Repositorio de servicios
            usuario_repository: Repositorio de usuarios
            requerimiento_repository: Repositorio de requerimientos
        """
        self.servicio_repo = servicio_repository
        self.usuario_repo = usuario_repository
        self.req_repo = requerimiento_repository

    async def listar_servicios_solicitante(
            self,
            solicitante_id: int
    ) -> List[Servicio]:
        """
        Lista todos los servicios de un solicitante.

        Args:
            solicitante_id: ID del solicitante

        Returns:
            List[Servicio]: Lista de servicios

        Raises:
            NotFoundException: Si el solicitante no existe
        """
        # Verificar que es solicitante
        solicitante = await self.usuario_repo.buscar_por_id(solicitante_id)
        if not solicitante or not isinstance(solicitante, Solicitante):
            raise NotFoundException(f"Solicitante {solicitante_id} no encontrado")

        # Obtener servicios
        servicios = await self.servicio_repo.buscar_por_solicitante(solicitante_id)

        return servicios

    async def solicitar_alta_servicio(
            self,
            solicitante_id: int,
            tipo_servicio: TipoServicio,
            plan_deseado: str,
            direccion_instalacion: str,
            comentarios: Optional[str] = None
    ) -> Solicitud:
        """
        Crea una solicitud de alta de nuevo servicio.
        Genera un requerimiento de tipo SOLICITUD.

        Args:
            solicitante_id: ID del solicitante
            tipo_servicio: Tipo de servicio (TELEFONIA, INTERNET, TV)
            plan_deseado: Plan o paquete deseado
            direccion_instalacion: Dirección para instalación
            comentarios: Comentarios adicionales

        Returns:
            Solicitud: Solicitud creada
        """
        # Obtener solicitante
        solicitante = await self.usuario_repo.buscar_por_id(solicitante_id)
        if not solicitante or not isinstance(solicitante, Solicitante):
            raise NotFoundException(f"Solicitante {solicitante_id} no encontrado")

        # Crear título y descripción
        titulo = f"Solicitud de alta de servicio: {tipo_servicio.value}"
        descripcion = (
            f"Plan deseado: {plan_deseado}\n"
            f"Dirección de instalación: {direccion_instalacion}"
        )
        if comentarios:
            descripcion += f"\nComentarios: {comentarios}"

        # Crear solicitud
        solicitud = Solicitud(
            id=None,
            titulo=titulo,
            descripcion=descripcion,
            solicitante=solicitante,
            categoria=CategoriaSolicitud.ALTA_SERVICIO
        )

        # Crear evento de creación
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.CREACION,
            requerimiento=solicitud,
            responsable=solicitante
        )
        solicitud.agregar_evento(evento)

        # Guardar
        solicitud_guardada = await self.req_repo.guardar(solicitud)

        # Notificar
        notificador = Notificador()
        notificador.notificar_evento(evento)

        return solicitud_guardada

    async def solicitar_baja_servicio(
            self,
            servicio_id: int,
            solicitante_id: int,
            motivo: str,
            fecha_deseada_baja: str,
            comentarios: Optional[str] = None
    ) -> Solicitud:
        """
        Crea una solicitud de baja de servicio existente.
        Genera un requerimiento de tipo SOLICITUD.

        Args:
            servicio_id: ID del servicio
            solicitante_id: ID del solicitante
            motivo: Motivo de la baja
            fecha_deseada_baja: Fecha deseada para la baja
            comentarios: Comentarios adicionales

        Returns:
            Solicitud: Solicitud creada
        """
        # Obtener servicio
        servicio = await self.servicio_repo.buscar_por_id(servicio_id)
        if not servicio:
            raise NotFoundException(f"Servicio {servicio_id} no encontrado")

        # Verificar que pertenece al solicitante
        if servicio.solicitante.id != solicitante_id:
            raise UnauthorizedException(
                "No tiene permisos para dar de baja este servicio"
            )

        # Obtener solicitante
        solicitante = await self.usuario_repo.buscar_por_id(solicitante_id)

        # Crear título y descripción
        titulo = f"Solicitud de baja de servicio: {servicio.tipo.value}"
        descripcion = (
            f"Servicio: {servicio.tipo.value} ({servicio.numero_servicio})\n"
            f"Motivo: {motivo}\n"
            f"Fecha deseada de baja: {fecha_deseada_baja}"
        )
        if comentarios:
            descripcion += f"\nComentarios: {comentarios}"

        # Crear solicitud
        solicitud = Solicitud(
            id=None,
            titulo=titulo,
            descripcion=descripcion,
            solicitante=solicitante,
            categoria=CategoriaSolicitud.BAJA_SERVICIO
        )

        # Crear evento de creación
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.CREACION,
            requerimiento=solicitud,
            responsable=solicitante
        )
        solicitud.agregar_evento(evento)

        # Guardar
        solicitud_guardada = await self.req_repo.guardar(solicitud)

        # Notificar
        notificador = Notificador()
        notificador.notificar_evento(evento)

        return solicitud_guardada
