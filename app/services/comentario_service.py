from app.domain.factories.evento_factory import EventoFactory
from app.domain.enums import TipoEvento
from app.domain.entities.comentario import Comentario
from app.domain.exceptions import PermisosDenegadosException


class ComentarioService:
    def __init__(self, req_repo, usuario_repo, notificacion_service):
        self.req_repo = req_repo
        self.usuario_repo = usuario_repo
        self.notificacion_service = notificacion_service

    def agregar_comentario(self, id_req: int, id_autor: int, contenido: str):
        # 1. Cargar datos
        req = self.req_repo.obtener_por_id(id_req)
        autor = self.usuario_repo.obtener_por_id(id_autor)

        # 2. Validar permiso (Polimorfismo)
        if not autor.puede_comentar_requerimiento(req):
            raise PermisosDenegadosException("No tiene permisos para comentar en este requerimiento.")

        # 3. Crear Objeto de Valor/Entidad Comentario
        comentario = Comentario(id=None, contenido=contenido, autor=autor)

        # 4. Modificar el Agregado (Requerimiento)
        req.agregar_comentario(comentario)

        # 5. Registrar Evento
        evento = EventoFactory.crear_evento(
            TipoEvento.COMENTARIO,
            req,
            autor,
            comentario=comentario
        )
        req.agregar_evento(evento)

        # 6. Guardar y Notificar
        self.req_repo.actualizar(req)
        self.notificacion_service.notificar_accion(evento, autor)