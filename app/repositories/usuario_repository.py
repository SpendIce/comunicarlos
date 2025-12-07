"""
Repositorio de Usuarios con MongoDB.
Incluye TODA la implementación - sin interfaces separadas.
Los métodos de mapeo están integrados en la clase.
"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain import (
    Usuario, Solicitante, Operador, Tecnico, Supervisor,
    Email, Servicio
)
from app.domain.enums import TipoUsuario, TipoServicio
from app.infrastructure.mongodb.sequence import SequenceGenerator
from datetime import datetime


class UsuarioRepository:
    """
    Repositorio concreto de usuarios para MongoDB.
    Maneja persistencia Y mapeo en una sola clase.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database["usuarios"]
        self.servicios_collection = database["servicios"]
        self.sequence = SequenceGenerator(database)

    # ========================================================================
    # CRUD Básico
    # ========================================================================

    async def guardar(self, usuario: Usuario) -> Usuario:
        """Guarda o actualiza un usuario"""
        # Asignar ID si es nuevo
        if usuario.id is None:
            usuario.id = await self.sequence.get_next("usuario_id")

        # Convertir a documento MongoDB
        doc = self._to_document(usuario)

        # Upsert
        await self.collection.replace_one(
            {"_id": usuario.id},
            doc,
            upsert=True
        )

        # Guardar servicios si es solicitante
        if isinstance(usuario, Solicitante):
            await self._guardar_servicios(usuario)

        return usuario

    async def buscar_por_id(self, id: int) -> Optional[Usuario]:
        """Busca un usuario por ID"""
        doc = await self.collection.find_one({"_id": id})
        if not doc:
            return None
        return await self._to_entity(doc)

    async def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca un usuario por email"""
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
        return await self._to_entity(doc)

    async def existe_email(self, email: str) -> bool:
        """Verifica si existe un email"""
        count = await self.collection.count_documents({"email": email})
        return count > 0

    async def eliminar(self, id: int) -> bool:
        """Elimina un usuario"""
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    # ========================================================================
    # Consultas Específicas
    # ========================================================================

    async def buscar_tecnicos(
            self,
            especialidad: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Tecnico]:
        """Busca técnicos opcionalmente filtrados por especialidad"""
        query = {"tipo_usuario": "TECNICO"}
        if especialidad:
            query["especialidades"] = especialidad

        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [await self._to_entity(doc) for doc in docs]

    async def buscar_operadores(self, skip: int = 0, limit: int = 100) -> List[Operador]:
        """Busca todos los operadores"""
        cursor = self.collection.find({"tipo_usuario": "OPERADOR"}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [await self._to_entity(doc) for doc in docs]

    async def buscar_supervisores(self, skip: int = 0, limit: int = 100) -> List[Supervisor]:
        """Busca todos los supervisores"""
        cursor = self.collection.find({"tipo_usuario": "SUPERVISOR"}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [await self._to_entity(doc) for doc in docs]

    # ========================================================================
    # MAPEO: Entidad ↔ Documento
    # Métodos privados integrados en la clase
    # ========================================================================

    def _to_document(self, usuario: Usuario) -> dict:
        """Convierte entidad de dominio a documento MongoDB"""
        doc = {
            "_id": usuario.id,
            "nombre": usuario.nombre,
            "email": str(usuario.email),
            "password_hash": usuario.password_hash,
            "tipo_usuario": usuario.get_tipo_usuario().value,
            "fecha_creacion": usuario.fecha_creacion,
            "ultimo_acceso": usuario.ultimo_acceso
        }

        # Campos específicos por tipo
        if isinstance(usuario, Tecnico):
            doc["especialidades"] = usuario.especialidades
        elif isinstance(usuario, Supervisor):
            doc["operadores_ids"] = [op.id for op in usuario.operadores_supervisados if op.id]
            doc["tecnicos_ids"] = [tec.id for tec in usuario.tecnicos_supervisados if tec.id]

        return doc

    async def _to_entity(self, doc: dict) -> Usuario:
        """Convierte documento MongoDB a entidad de dominio"""
        email = Email(doc["email"])
        tipo = TipoUsuario(doc["tipo_usuario"])

        if tipo == TipoUsuario.SOLICITANTE:
            # Cargar servicios
            servicios = await self._cargar_servicios(doc["_id"])
            return Solicitante(
                id=doc["_id"],
                nombre=doc["nombre"],
                email=email,
                password_hash=doc["password_hash"],
                servicios_suscritos=servicios,
                fecha_creacion=doc["fecha_creacion"],
                ultimo_acceso=doc.get("ultimo_acceso")
            )

        elif tipo == TipoUsuario.OPERADOR:
            return Operador(
                id=doc["_id"],
                nombre=doc["nombre"],
                email=email,
                password_hash=doc["password_hash"],
                fecha_creacion=doc["fecha_creacion"],
                ultimo_acceso=doc.get("ultimo_acceso")
            )

        elif tipo == TipoUsuario.TECNICO:
            return Tecnico(
                id=doc["_id"],
                nombre=doc["nombre"],
                email=email,
                password_hash=doc["password_hash"],
                especialidades=doc.get("especialidades", []),
                fecha_creacion=doc["fecha_creacion"],
                ultimo_acceso=doc.get("ultimo_acceso")
            )

        else:  # SUPERVISOR
            # Cargar operadores y técnicos supervisados (lazy loading simple)
            return Supervisor(
                id=doc["_id"],
                nombre=doc["nombre"],
                email=email,
                password_hash=doc["password_hash"],
                fecha_creacion=doc["fecha_creacion"],
                ultimo_acceso=doc.get("ultimo_acceso")
            )

    # ========================================================================
    # Helpers para relaciones
    # ========================================================================

    async def _guardar_servicios(self, solicitante: Solicitante) -> None:
        """Guarda los servicios de un solicitante"""
        for servicio in solicitante.servicios_suscritos:
            if servicio.id is None:
                servicio.id = await self.sequence.get_next("servicio_id")

            doc = {
                "_id": servicio.id,
                "tipo": servicio.tipo.value,
                "numero_servicio": servicio.numero_servicio,
                "solicitante_id": solicitante.id,
                "activo": servicio.activo,
                "fecha_alta": servicio.fecha_alta
            }

            await self.servicios_collection.replace_one(
                {"_id": servicio.id},
                doc,
                upsert=True
            )

    async def _cargar_servicios(self, solicitante_id: int) -> List[Servicio]:
        """Carga los servicios de un solicitante"""
        cursor = self.servicios_collection.find({"solicitante_id": solicitante_id})
        docs = await cursor.to_list(length=100)

        servicios = []
        for doc in docs:
            # Necesitamos una referencia al solicitante (circular)
            # Para evitar recursión infinita, creamos un stub
            servicio = Servicio(
                id=doc["_id"],
                tipo=TipoServicio(doc["tipo"]),
                numero_servicio=doc["numero_servicio"],
                solicitante=None,  # Se asigna después
                activo=doc["activo"],
                fecha_alta=doc["fecha_alta"]
            )
            servicios.append(servicio)

        return servicios