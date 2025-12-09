from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.infrastructure.mongodb.sequence import SequenceGenerator
from app.domain.entities.notificacion import Notificacion
from app.domain.entities.evento import Evento
from app.domain.entities.requerimiento import Incidente, Solicitud
from app.domain.entities.usuario import Supervisor, Usuario
from app.domain.enums import TipoEvento, TipoRequerimiento, NivelUrgencia, TipoUsuario
from app.domain.value_objects.email import Email


class UsuarioSnapshot(Usuario):
    """
    Clase concreta utilizada exclusivamente para reconstruir usuarios
    desde snapshots de notificaciones donde no se requiere comportamiento real.
    """

    def get_tipo_usuario(self) -> TipoUsuario:
        return TipoUsuario.SOLICITANTE

    def puede_ver_requerimiento(self, requerimiento) -> bool:
        return False

    def puede_comentar_requerimiento(self, requerimiento) -> bool:
        return False

class EventoSnapshot(Evento):
    """
    Clase concreta para reconstruir eventos desde snapshots.
    """
    def __init__(self, tipo: TipoEvento, responsable, fecha_hora, descripcion: str, requerimiento):
        self._tipo = tipo
        super().__init__(
            id=None,
            titulo=f"Evento: {tipo.value}",
            descripcion=descripcion,
            responsable=responsable,
            requerimiento=requerimiento,
            fecha_hora=fecha_hora
        )

    def get_tipo_evento(self) -> TipoEvento:
        return self._tipo

    def get_descripcion_detallada(self) -> str:
        return self.descripcion

class NotificacionRepository:
    def __init__(self, database: AsyncIOMotorDatabase, usuario_repository):
        self.collection = database["notificaciones"]
        self.user_repo = usuario_repository
        self.sequence = SequenceGenerator(database)

    async def guardar(self, notif: Notificacion) -> Notificacion:
        req = notif.evento.requerimiento

        nivel_urgencia = None
        if hasattr(req, 'nivel_urgencia') and req.nivel_urgencia:
            nivel_urgencia = req.nivel_urgencia.value

        doc = {
            "_id": notif.id,
            "leida": notif.leida,
            "supervisor_id": notif.supervisor.id,
            "fecha_creacion": notif.fecha_hora_generada,
            "fecha_lectura": notif.fecha_lectura,
            "evento": {
                "tipo": notif.evento.get_tipo_evento().value,
                "descripcion": notif.evento.descripcion,
                "fecha_hora": notif.evento.fecha_hora,
                "responsable": {
                    "id": notif.evento.responsable.id,
                    "nombre": notif.evento.responsable.nombre
                },
                "requerimiento": {
                    "id": req.id,
                    "titulo": req.titulo,
                    "tipo": req.get_tipo().value,
                    "nivel_urgencia": nivel_urgencia
                }
            }
        }

        await self.collection.replace_one({"_id": notif.id}, doc, upsert=True)
        return notif

    async def buscar_por_id(self, id: int) -> Optional[Notificacion]:
        doc = await self.collection.find_one({"_id": id})
        if not doc:
            return None
        return await self._to_entity(doc)

    async def eliminar(self, id: int) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    async def buscar_todos(self) -> List[Notificacion]:
        cursor = self.collection.find().limit(100)
        docs = await cursor.to_list(length=100)
        return [await self._to_entity(doc) for doc in docs]

    async def buscar_por_supervisor(
            self,
            supervisor_id: int,
            leida: Optional[bool] = None,
            page: int = 0,
            size: int = 20
    ) -> List[Notificacion]:
        query = {"supervisor_id": supervisor_id}
        if leida is not None:
            query["leida"] = leida

        cursor = self.collection.find(query).sort("fecha_creacion", -1).skip(page * size).limit(size)
        docs = await cursor.to_list(length=size)

        return [await self._to_entity(doc) for doc in docs]

    async def contar_por_supervisor(self, supervisor_id: int, leida: Optional[bool] = None) -> int:
        query = {"supervisor_id": supervisor_id}
        if leida is not None:
            query["leida"] = leida
        return await self.collection.count_documents(query)

    async def _to_entity(self, doc: dict) -> Notificacion:
        supervisor = Supervisor(
            id=doc["supervisor_id"],
            nombre="Supervisor",
            email=Email("proxy@system.local"),
            password_hash=""
        )

        req_data = doc["evento"]["requerimiento"]
        tipo_req = TipoRequerimiento(req_data["tipo"])

        desc_placeholder = "Descripción no disponible en vista de notificación."

        if tipo_req == TipoRequerimiento.INCIDENTE:
            urgencia = NivelUrgencia(req_data["nivel_urgencia"]) if req_data.get("nivel_urgencia") else None
            requerimiento = Incidente(
                id=req_data["id"],
                titulo=req_data["titulo"],
                descripcion=desc_placeholder,
                solicitante=None,
                categoria=None,
                nivel_urgencia=urgencia
            )
        else:
            requerimiento = Solicitud(
                id=req_data["id"],
                titulo=req_data["titulo"],
                descripcion=desc_placeholder,
                solicitante=None,
                categoria=None
            )

        resp_data = doc["evento"]["responsable"]
        responsable = UsuarioSnapshot(
            id=resp_data["id"],
            nombre=resp_data["nombre"],
            email=Email("snapshot@system.local"),
            password_hash=""
        )

        evento = EventoSnapshot(
            tipo=TipoEvento(doc["evento"]["tipo"]),
            descripcion=doc["evento"]["descripcion"],
            requerimiento=requerimiento,
            responsable=responsable,
            fecha_hora=doc["evento"]["fecha_hora"]
        )

        return Notificacion(
            id=doc["_id"],
            evento=evento,
            supervisor=supervisor,
            fecha_hora_generada=doc["fecha_creacion"],
            leida=doc["leida"],
            fecha_lectura=doc.get("fecha_lectura")
        )