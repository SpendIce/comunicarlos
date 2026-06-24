from typing import List, Optional
from datetime import datetime

# Dominio
from app.domain.entities.requerimiento import Requerimiento
from app.domain.enums import TipoEvento, EstadoRequerimiento
from app.domain.factories.evento_factory import EventoFactory
from app.domain.exceptions import PermisosDenegadosException, RecursoNoEncontradoException


class RequerimientoService:
    """
    Servicio Principal del Core de Negocio.
    Patrón: Fachada (Facade) para la gestión del ciclo de vida de los requerimientos.

    Este servicio orquesta la interacción entre:
    1. Las Entidades (Reglas de negocio)
    2. Los Repositorios (Persistencia)
    3. El Factory de Eventos (Historial)
    4. El Servicio de Notificaciones (Observabilidad)
    """

    def __init__(
            self,
            requerimiento_repo,
            usuario_repo,
            notificacion_service
    ):
        self.requerimiento_repo = requerimiento_repo
        self.usuario_repo = usuario_repo
        self.notificacion_service = notificacion_service

    # =================================================================
    # CASOS DE USO: CREACIÓN
    # =================================================================

    def crear_incidente(self, solicitante_id: int, titulo: str, descripcion: str,
                        urgencia, categoria) -> Requerimiento:
        """Coordina el alta de un nuevo Incidente."""

        # 1. Recuperar al actor
        solicitante = self._get_usuario(solicitante_id)

        # 2. Instanciar Entidad (La validación ocurre dentro del __init__ de la entidad)
        # Aquí se nota la inversión de control: el dominio controla la creación.
        from app.domain.entities.requerimiento import Incidente
        incidente = Incidente(
            id=None,
            titulo=titulo,
            descripcion=descripcion,
            solicitante=solicitante,
            nivel_urgencia=urgencia,
            categoria=categoria
        )

        # 3. Registrar Evento de Creación (Auditabilidad)
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.CREACION,
            requerimiento=incidente,
            responsable=solicitante
        )
        incidente.agregar_evento(evento)

        # 4. Persistir
        nuevo_incidente = self.requerimiento_repo.guardar(incidente)
        return nuevo_incidente

    def crear_solicitud(self, solicitante_id: int, titulo: str, descripcion: str,
                        categoria) -> Requerimiento:
        """Coordina el alta de una nueva Solicitud de Servicio."""
        solicitante = self._get_usuario(solicitante_id)

        from app.domain.entities.requerimiento import Solicitud
        solicitud = Solicitud(
            id=None,
            titulo=titulo,
            descripcion=descripcion,
            solicitante=solicitante,
            categoria=categoria
        )

        evento = EventoFactory.crear_evento(TipoEvento.CREACION, solicitud, solicitante)
        solicitud.agregar_evento(evento)

        return self.requerimiento_repo.guardar(solicitud)

    # =================================================================
    # CASOS DE USO: GESTIÓN (ASIGNAR, RESOLVER, DERIVAR)
    # =================================================================

    def asignar_tecnico(self, id_req: int, id_operador: int, id_tecnico: int):
        """
        Un Operador asigna un técnico a un requerimiento.
        """
        # 1. Obtener Agregados
        req = self._get_requerimiento(id_req)
        operador = self._get_usuario(id_operador)
        tecnico = self._get_usuario(id_tecnico)

        # 2. Validar Permisos (Polimorfismo)
        # El método 'puede_asignar_requerimiento' debe existir en Operador
        if not hasattr(operador, 'puede_asignar_requerimiento') or not operador.puede_asignar_requerimiento():
            raise PermisosDenegadosException("Solo los operadores pueden asignar requerimientos.")

        # 3. Ejecutar Lógica de Dominio (Cambio de estado)
        req.asignar_tecnico(tecnico, operador)

        # 4. Generar Evento Histórico
        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.ASIGNACION,
            requerimiento=req,
            responsable=operador,
            tecnico_asignado=tecnico
        )
        req.agregar_evento(evento)

        # 5. Persistir y Notificar (Efectos colaterales)
        self.requerimiento_repo.actualizar(req)
        self.notificacion_service.notificar_accion(evento, tecnico)  # Avisar al supervisado

    def derivar_requerimiento(self, id_req: int, id_tecnico_origen: int,
                              id_tecnico_destino: int, motivo: str):
        """
        Un Técnico deriva el trabajo a otro colega (Interconsulta).
        """
        req = self._get_requerimiento(id_req)
        origen = self._get_usuario(id_tecnico_origen)
        destino = self._get_usuario(id_tecnico_destino)

        # Validación de dominio delegada a la entidad
        req.derivar_a_tecnico(destino, origen, motivo)

        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.DERIVACION,
            requerimiento=req,
            responsable=origen,
            tecnico_origen=origen,
            tecnico_destino=destino,
            motivo=motivo
        )
        req.agregar_evento(evento)

        self.requerimiento_repo.actualizar(req)
        self.notificacion_service.notificar_accion(evento, origen)

    def resolver_requerimiento(self, id_req: int, id_tecnico: int):
        """
        El técnico marca el fin del trabajo.
        """
        req = self._get_requerimiento(id_req)
        tecnico = self._get_usuario(id_tecnico)

        # La entidad valida si el técnico es el asignado
        req.resolver(tecnico)

        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.RESOLUCION,
            requerimiento=req,
            responsable=tecnico
        )
        req.agregar_evento(evento)

        self.requerimiento_repo.actualizar(req)
        self.notificacion_service.notificar_accion(evento, tecnico)

    def reabrir_requerimiento(self, id_req: int, id_usuario: int, motivo: str):
        """
        Permite reabrir un caso si el usuario no está conforme.
        """
        req = self._get_requerimiento(id_req)
        usuario = self._get_usuario(id_usuario)

        req.reabrir(usuario, motivo)

        evento = EventoFactory.crear_evento(
            tipo=TipoEvento.REAPERTURA,
            requerimiento=req,
            responsable=usuario,
            motivo=motivo
        )
        req.agregar_evento(evento)

        self.requerimiento_repo.actualizar(req)

        # Si quien reabre no es el técnico, notificamos al técnico anterior o sus supervisores
        if req.tecnico_asignado:
            self.notificacion_service.notificar_accion(evento, req.tecnico_asignado)

    # =================================================================
    # CONSULTAS (READ)
    # =================================================================

    def obtener_requerimientos_usuario(self, id_usuario: int) -> List[Requerimiento]:
        """
        Filtra requerimientos según lo que el usuario 'puede ver'.
        """
        usuario = self._get_usuario(id_usuario)
        todos = self.requerimiento_repo.obtener_todos()

        # Filtrado en memoria usando la regla de negocio polimórfica.
        # (Nota: En producción real esto se haría en base de datos por performance,
        # pero para fines académicos demuestra el uso de POO 'puede_ver_requerimiento')
        return [r for r in todos if usuario.puede_ver_requerimiento(r)]

    # =================================================================
    # MÉTODOS PRIVADOS (HELPERS)
    # =================================================================

    def _get_usuario(self, uid):
        u = self.usuario_repo.obtener_por_id(uid)
        if not u: raise RecursoNoEncontradoException(f"Usuario {uid} no encontrado")
        return u

    def _get_requerimiento(self, rid):
        r = self.requerimiento_repo.obtener_por_id(rid)
        if not r: raise RecursoNoEncontradoException(f"Requerimiento {rid} no encontrado")
        return r