from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.entities.servicio import Servicio
from app.domain.entities.usuario import Solicitante
from app.domain.value_objects.email import Email
from app.domain.enums import TipoServicio
from app.infrastructure.mongodb.sequence import SequenceGenerator

class ServicioRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["servicios"]
        self.sequence = SequenceGenerator(database)

    async def guardar(self, servicio: Servicio) -> Servicio:
        """Guarda o actualiza un servicio en la colección independiente"""
        if servicio.id is None:
            servicio.id = await self.sequence.get_next("servicio_id")

        # Mapeo a documento
        doc = {
            "_id": servicio.id,
            "tipo": servicio.tipo.value,
            "numero_servicio": servicio.numero_servicio,
            "solicitante_id": servicio.solicitante.id if servicio.solicitante else None,
            "activo": servicio.activo,
            "fecha_alta": servicio.fecha_alta
        }

        await self.collection.replace_one({"_id": servicio.id}, doc, upsert=True)
        return servicio

    async def buscar_por_id(self, id: int) -> Optional[Servicio]:
        doc = await self.collection.find_one({"_id": id})
        if not doc:
            return None
        return self._to_entity(doc)

    async def buscar_por_solicitante(self, solicitante_id: int) -> List[Servicio]:
        cursor = self.collection.find({"solicitante_id": solicitante_id})
        docs = await cursor.to_list(length=100)
        return [self._to_entity(doc) for doc in docs]

    async def buscar_activos_por_solicitante(self, solicitante_id: int) -> List[Servicio]:
        cursor = self.collection.find({"solicitante_id": solicitante_id, "activo": True})
        docs = await cursor.to_list(length=100)
        return [self._to_entity(doc) for doc in docs]

    def _to_entity(self, doc: dict) -> Servicio:
        solicitante_proxy = None
        if doc.get("solicitante_id"):
            solicitante_proxy = Solicitante(
                id=doc["solicitante_id"],
                nombre="Ref", # Placeholder
                email=Email("ref@internal.com"),
                password_hash=""
            )

        return Servicio(
            id=doc["_id"],
            tipo=TipoServicio(doc["tipo"]),
            numero_servicio=doc["numero_servicio"],
            solicitante=solicitante_proxy,
            activo=doc["activo"],
            fecha_alta=doc.get("fecha_alta")
        )