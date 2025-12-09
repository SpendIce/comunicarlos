from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain.entities.requerimiento import Requerimiento, Incidente, Solicitud
from app.domain.enums import TipoRequerimiento, EstadoRequerimiento, NivelUrgencia, CategoriaIncidente, CategoriaSolicitud
from app.infrastructure.mongodb.sequence import SequenceGenerator


class RequerimientoRepository:
    def __init__(self, database: AsyncIOMotorDatabase, usuario_repository):
        self.collection = database["requerimientos"]
        self.sequence = SequenceGenerator(database)
        self.usuario_repo = usuario_repository

    async def guardar(self, requerimiento: Requerimiento) -> Requerimiento:
        if requerimiento.id is None:
            requerimiento.id = await self.sequence.get_next("requerimiento_id")

        doc = self._to_document(requerimiento)
        await self.collection.replace_one({"_id": requerimiento.id}, doc, upsert=True)
        return requerimiento

    async def buscar_por_id(self, id: int) -> Optional[Requerimiento]:
        doc = await self.collection.find_one({"_id": id})
        return await self._to_entity(doc) if doc else None

    async def siguiente_id_comentario(self) -> int:
        """Genera el siguiente ID único para un comentario"""
        return await self.sequence.get_next("comentario_id")

    async def buscar_con_filtros(self, filtros: dict, page: int, size: int) -> tuple[List[Requerimiento], int]:
        """Método genérico para listar con paginación"""
        cursor = self.collection.find(filtros).sort("fecha_creacion", -1).skip(page * size).limit(size)
        total = await self.collection.count_documents(filtros)
        docs = await cursor.to_list(length=size)
        entidades = [await self._to_entity(doc) for doc in docs]
        return entidades, total

    # --- AGREGACIONES PARA REPORTES (Dashboard) ---

    async def obtener_metricas_globales(self) -> Dict[str, Any]:
        """Calcula métricas generales usando Aggregation Framework"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": 1},
                    "incidentes": {"$sum": {"$cond": [{"$eq": ["$tipo", "INCIDENTE"]}, 1, 0]}},
                    "solicitudes": {"$sum": {"$cond": [{"$eq": ["$tipo", "SOLICITUD"]}, 1, 0]}},
                    "resueltos": {"$sum": {"$cond": [{"$eq": ["$estado", "RESUELTO"]}, 1, 0]}},
                    "pendientes": {"$sum": {"$cond": [{"$ne": ["$estado", "RESUELTO"]}, 1, 0]}}
                }
            }
        ]
        resultado = await self.collection.aggregate(pipeline).to_list(1)
        return resultado[0] if resultado else {}

    async def obtener_distribucion_estado(self) -> Dict[str, int]:
        pipeline = [{"$group": {"_id": "$estado", "count": {"$sum": 1}}}]
        cursor = self.collection.aggregate(pipeline)
        return {doc["_id"]: doc["count"] for doc in await cursor.to_list(None)}

    async def obtener_distribucion_urgencia(self) -> Dict[str, int]:
        pipeline = [
            {"$match": {"tipo": "INCIDENTE"}},
            {"$group": {"_id": "$nivel_urgencia", "count": {"$sum": 1}}}
        ]
        cursor = self.collection.aggregate(pipeline)
        return {doc["_id"]: doc["count"] for doc in await cursor.to_list(None)}

    async def obtener_incidentes_criticos_pendientes(self) -> List[dict]:
        """Retorna info resumida de incidentes críticos no resueltos"""
        query = {
            "tipo": "INCIDENTE",
            "nivel_urgencia": "CRITICO",
            "estado": {"$ne": "RESUELTO"}
        }
        cursor = self.collection.find(query, {
            "_id": 1, "titulo": 1, "tecnico_asignado_nombre": 1,
            "fecha_creacion": 1, "fecha_resolucion": 1
        }).sort("fecha_creacion", 1)
        return await cursor.to_list(length=50)

    def _to_document(self, req: Requerimiento) -> dict:
        """Convierte entidad a documento MongoDB"""
        doc = {
            "_id": req.id,
            "tipo": req.get_tipo().value,
            "titulo": req.titulo,
            "descripcion": req.descripcion,
            "estado": req.estado.value,
            "solicitante_id": req.solicitante.id,
            "solicitante_nombre": req.solicitante.nombre,
            "tecnico_asignado_id": req.tecnico_asignado.id if req.tecnico_asignado else None,
            "tecnico_asignado_nombre": req.tecnico_asignado.nombre if req.tecnico_asignado else None,
            "fecha_creacion": req.fecha_creacion,
            "fecha_resolucion": req.fecha_resolucion,
            "comentarios": [
                {
                    "id": c.id,
                    "texto": c.texto,
                    "autor_id": c.autor.id,
                    "autor_nombre": c.autor.nombre,
                    "fecha_hora": c.fecha_hora
                }
                for c in req.comentarios
            ],
            "eventos": [
                {
                    "id": e.id,
                    "tipo": e.get_tipo_evento().value,
                    "titulo": e.titulo,
                    "descripcion": e.descripcion,
                    "responsable_id": e.responsable.id,
                    "responsable_nombre": e.responsable.nombre,
                    "fecha_hora": e.fecha_hora
                }
                for e in req.eventos
            ]
        }

        # Campos específicos por tipo
        if isinstance(req, Incidente):
            doc["nivel_urgencia"] = req.nivel_urgencia.value
            doc["categoria"] = req.categoria.value
        else:  # Solicitud
            doc["categoria"] = req.categoria.value

        return doc

    async def _to_entity(self, doc: dict) -> Requerimiento:
        """Convierte documento MongoDB a entidad"""
        # Cargar relaciones
        solicitante = await self.usuario_repo.buscar_por_id(doc["solicitante_id"])
        tecnico = None
        if doc.get("tecnico_asignado_id"):
            tecnico = await self.usuario_repo.buscar_por_id(doc["tecnico_asignado_id"])

        tipo = TipoRequerimiento(doc["tipo"])
        estado = EstadoRequerimiento(doc["estado"])

        # Crear requerimiento según tipo
        if tipo == TipoRequerimiento.INCIDENTE:
            req = Incidente(
                id=doc["_id"],
                titulo=doc["titulo"],
                descripcion=doc["descripcion"],
                solicitante=solicitante,
                nivel_urgencia=NivelUrgencia(doc["nivel_urgencia"]),
                categoria=CategoriaIncidente(doc["categoria"]),
                estado=estado,
                tecnico_asignado=tecnico,
                fecha_creacion=doc["fecha_creacion"],
                fecha_resolucion=doc.get("fecha_resolucion")
            )
        else:
            req = Solicitud(
                id=doc["_id"],
                titulo=doc["titulo"],
                descripcion=doc["descripcion"],
                solicitante=solicitante,
                categoria=CategoriaSolicitud(doc["categoria"]),
                estado=estado,
                tecnico_asignado=tecnico,
                fecha_creacion=doc["fecha_creacion"],
                fecha_resolucion=doc.get("fecha_resolucion")
            )

        # Comentarios y eventos se cargan bajo demanda o se ignoran
        # (ya están en el documento si se necesitan para display)

        return req