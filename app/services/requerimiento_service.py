from typing import List, Optional
from app.domain import (
    Requerimiento, Incidente, Solicitud,
    Solicitante, Operador, Tecnico,
    EventoFactory, Notificador, Usuario
)
from app.domain.enums import (
    TipoRequerimiento, EstadoRequerimiento,
    NivelUrgencia, CategoriaIncidente, CategoriaSolicitud, TipoEvento
)
from app.domain.exceptions import (
    EstadoInvalidoException,
    PermisosDenegadosException
)
from app.services.exceptions import NotFoundException, UnauthorizedException


class RequerimientoService:
    """
    Servicio de gestión de requerimientos.
    Coordina operaciones de creación, consulta, resolución y reapertura.
    """

    def __init__(self, requerimiento_repository, usuario_repository, notificador):
        """
        Args:
            requerimiento_repository: Repositorio de requerimientos
            usuario_repository: Repositorio de usuarios
        """
        self.req_repo = requerimiento_repository
        self.usuario_repo = usuario_repository
        self.notificador = notificador

    # ========================================================================
    # Creación de Requerimientos
    # ========================================================================

    async def crear_requerimiento(
            self,
            solicitante_id: int,
            tipo: TipoRequerimiento,
            titulo: str,
            descripcion: str,
            categoria: str,
            nivel_urgencia: Optional[NivelUrgencia] = None
    ) -> Requerimiento:
        """
        Crea un nuevo requerimiento (incidente o solicitud).

        Args:
            solicitante_id: ID del solicitante
            tipo: INCIDENTE o SOLICITUD
            titulo: Título del requerimiento
            descripcion: Descripción detallada
            categoria: Categoría específica
            nivel_urgencia: Urgencia (solo para incidentes)

        Returns:
            Requerimiento: Requerimiento creado

        Raises:
            NotFoundException: Si el solicitante no existe
            ValueError: Si los datos son inválidos
        """
        # Obtener solicitante
        solicitante = await self.usuario_repo.buscar_por_id(solicitante_id)
        if not solicitante or not isinstance(solicitante, Solicitante):
            raise NotFoundException(f"Solicitante {solicitante_id} no encontrado")

        # Crear requerimiento según tipo
        if tipo == TipoRequerimiento.INCIDENTE:
            if nivel_urgencia is None:
                raise ValueError("nivel_urgencia es requerido para incidentes")

            requerimiento = Incidente(
                id=None,
                titulo=titulo,
                descripcion=descripcion,
                solicitante=solicitante,
                nivel_urgencia=nivel_urgencia,
                categoria=CategoriaIncidente[categoria],
                estado=EstadoRequerimiento.NUEVO
            )

        elif tipo == TipoRequerimiento.SOLICITUD:
            requerimiento = Solicitud(
                id=None,
                titulo=titulo,
                descripcion=descripcion,
                solicitante=solicitante,
                categoria=CategoriaSolicitud[categoria],
                estado=EstadoRequerimiento.NUEVO
            )

        else:
            raise ValueError(f"Tipo de requerimiento inválido: {tipo}")

        # Crear evento de creación
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.CREACION,
            requerimiento=requerimiento,
            responsable=solicitante
        )
        requerimiento.agregar_evento(evento)

        # Guardar en repositorio
        requerimiento_guardado = await self.req_repo.guardar(requerimiento)

        # Notificar (si hay supervisores)
        await self.notificador.notificar_evento(evento)

        return requerimiento_guardado

    # ========================================================================
    # Consultas
    # ========================================================================

    async def obtener_requerimiento(
            self,
            requerimiento_id: int,
            usuario_actual: Usuario
    ) -> Requerimiento:
        """
        Obtiene un requerimiento por ID con control de permisos.

        Args:
            requerimiento_id: ID del requerimiento
            usuario_actual: Usuario que realiza la consulta

        Returns:
            Requerimiento: Requerimiento encontrado

        Raises:
            NotFoundException: Si no existe
            UnauthorizedException: Si no tiene permisos
        """
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(f"Requerimiento {requerimiento_id} no encontrado")

        # Verificar permisos
        if not usuario_actual.puede_ver_requerimiento(requerimiento):
            raise UnauthorizedException(
                "No tiene permisos para ver este requerimiento"
            )

        return requerimiento

    async def listar_requerimientos(
            self,
            usuario_actual: Usuario,
            estado: Optional[EstadoRequerimiento] = None,
            tipo: Optional[TipoRequerimiento] = None,
            page: int = 0,
            size: int = 20
    ) -> tuple[List[Requerimiento], int]:
        """
        Lista requerimientos según permisos del usuario.

        Args:
            usuario_actual: Usuario que realiza la consulta
            estado: Filtro por estado (opcional)
            tipo: Filtro por tipo (opcional)
            page: Número de página
            size: Tamaño de página

        Returns:
            tuple: (lista_requerimientos, total_elementos)
        """
        # Aplicar filtros según tipo de usuario
        if isinstance(usuario_actual, Solicitante):
            # Solicitantes solo ven sus propios requerimientos
            requerimientos = await self.req_repo.buscar_por_solicitante(
                solicitante_id=usuario_actual.id,
                estado=estado,
                tipo=tipo,
                page=page,
                size=size
            )

        elif isinstance(usuario_actual, Tecnico):
            # Técnicos solo ven requerimientos asignados a ellos
            requerimientos = await self.req_repo.buscar_por_tecnico(
                tecnico_id=usuario_actual.id,
                estado=estado,
                tipo=tipo,
                page=page,
                size=size
            )

        else:
            # Operadores y Supervisores ven todos
            requerimientos = await self.req_repo.buscar_todos(
                estado=estado,
                tipo=tipo,
                page=page,
                size=size
            )

        total = self.req_repo.contar(
            usuario=usuario_actual,
            estado=estado,
            tipo=tipo
        )

        return requerimientos, total

    async def obtener_requerimientos_priorizados(
            self,
            estado: EstadoRequerimiento = EstadoRequerimiento.NUEVO,
            limite: int = 10
    ) -> List[Requerimiento]:
        """
        Obtiene requerimientos ordenados por prioridad.

        Args:
            estado: Estado de los requerimientos
            limite: Cantidad máxima a retornar

        Returns:
            List[Requerimiento]: Lista ordenada por prioridad
        """
        requerimientos = await self.req_repo.buscar_por_estado(estado)

        # Ordenar por prioridad (mayor primero)
        requerimientos_ordenados = sorted(
            requerimientos,
            key=lambda r: r.calcular_prioridad(),
            reverse=True
        )

        return requerimientos_ordenados[:limite]

    # ========================================================================
    # Resolución y Reapertura
    # ========================================================================

    async def resolver_requerimiento(
            self,
            requerimiento_id: int,
            tecnico_id: int,
            comentario_resolucion: Optional[str] = None
    ) -> Requerimiento:
        """
        Marca un requerimiento como resuelto.

        Args:
            requerimiento_id: ID del requerimiento
            tecnico_id: ID del técnico que resuelve
            comentario_resolucion: Comentario opcional

        Returns:
            Requerimiento: Requerimiento actualizado

        Raises:
            NotFoundException: Si no existe
            UnauthorizedException: Si no tiene permisos
            EstadoInvalidoException: Si el estado no permite resolución
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(f"Requerimiento {requerimiento_id} no encontrado")

        # Obtener técnico
        tecnico = await self.usuario_repo.buscar_por_id(tecnico_id)
        if not tecnico or not isinstance(tecnico, Tecnico):
            raise NotFoundException(f"Técnico {tecnico_id} no encontrado")

        # Agregar comentario si se proporciona
        if comentario_resolucion:
            from app.domain import Comentario
            comentario_id = await self.req_repo.siguiente_id_comentario()
            comentario = Comentario(
                id=comentario_id,
                texto=comentario_resolucion,
                autor=tecnico,
                requerimiento=requerimiento
            )
            requerimiento.agregar_comentario(comentario)

            # Evento de comentario
            evento_comentario = EventoFactory.crear_evento(
                tipo=TipoEvento.COMENTARIO,
                requerimiento=requerimiento,
                responsable=tecnico,
                comentario=comentario
            )
            requerimiento.agregar_evento(evento_comentario)
            await self.notificador.notificar_evento(evento_comentario)

        # Resolver requerimiento (validaciones en el dominio)
        requerimiento.resolver(tecnico)

        # Crear evento de resolución
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.RESOLUCION,
            requerimiento=requerimiento,
            responsable=tecnico
        )
        requerimiento.agregar_evento(evento)

        # Guardar
        requerimiento_actualizado = await self.req_repo.guardar(requerimiento)

        # Notificar
        await self.notificador.notificar_evento(evento)

        return requerimiento_actualizado

    async def reabrir_requerimiento(
            self,
            requerimiento_id: int,
            usuario_id: int,
            motivo: str
    ) -> Requerimiento:
        """
        Reabre un requerimiento resuelto.

        Args:
            requerimiento_id: ID del requerimiento
            usuario_id: ID del usuario que reabre
            motivo: Motivo de reapertura

        Returns:
            Requerimiento: Requerimiento actualizado

        Raises:
            NotFoundException: Si no existe
            EstadoInvalidoException: Si no está resuelto
        """
        # Obtener requerimiento
        requerimiento = await self.req_repo.buscar_por_id(requerimiento_id)
        if not requerimiento:
            raise NotFoundException(f"Requerimiento {requerimiento_id} no encontrado")

        # Obtener usuario
        usuario = await self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise NotFoundException(f"Usuario {usuario_id} no encontrado")

        # Reabrir (validaciones en el dominio)
        requerimiento.reabrir(usuario, motivo)

        # Crear evento
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.REAPERTURA,
            requerimiento=requerimiento,
            responsable=usuario,
            motivo=motivo
        )
        requerimiento.agregar_evento(evento)

        # Guardar
        requerimiento_actualizado = await self.req_repo.guardar(requerimiento)

        # Notificar
        await self.notificador.notificar_evento(evento)

        return requerimiento_actualizado