"""
Repositorio de Usuarios con MongoDB.
Implementa persistencia y reconstrucción de entidades (Usuario y sus subclases).
"""
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

# Imports explícitos de entidades para evitar ciclos con app.domain
from app.domain.entities.usuario import (
    Usuario, Solicitante, Operador, Tecnico, Supervisor
)
from app.domain.entities.servicio import Servicio
from app.domain.value_objects.email import Email
from app.domain.enums import TipoUsuario, TipoServicio
from app.infrastructure.mongodb.sequence import SequenceGenerator


class UsuarioRepository:
    """
    Repositorio concreto de usuarios.
    Utiliza Aggregation Framework para lecturas complejas (joins) y métodos estándar para escrituras.
    """

    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["usuarios"]
        # No guardamos referencia a 'servicios' aquí para escritura,
        # pero la usaremos implícitamente en los $lookup de lectura.
        self.sequence = SequenceGenerator(database)

    # ========================================================================
    # Operaciones de Escritura (Create / Update / Delete)
    # ========================================================================

    async def guardar(self, usuario: Usuario) -> Usuario:
        """
        Guarda o actualiza un usuario en la base de datos.
        Nota: No guarda automáticamente los servicios anidados; eso lo coordina el Servicio de Dominio.
        """
        # Generar ID si es un usuario nuevo
        if usuario.id is None:
            usuario.id = await self.sequence.get_next("usuario_id")

        # Convertir entidad a documento BSON
        doc = self._to_document(usuario)

        # Upsert (Insertar o Actualizar)
        await self.collection.replace_one(
            {"_id": usuario.id},
            doc,
            upsert=True
        )

        return usuario

    async def eliminar(self, id: int) -> bool:
        """Elimina un usuario por su ID"""
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    # ========================================================================
    # Operaciones de Lectura (Read)
    # ========================================================================

    async def buscar_por_id(self, id: int) -> Optional[Usuario]:
        """
        Busca un usuario por ID.
        Si es un Solicitante, trae sus servicios usando $lookup.
        """
        return await self._buscar_uno_con_relaciones({"_id": id})

    async def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca un usuario por Email.
        Si es un Solicitante, trae sus servicios usando $lookup.
        """
        return await self._buscar_uno_con_relaciones({"email": email})

    async def existe_email(self, email: str) -> bool:
        """Verifica eficientemente si un email ya está registrado"""
        count = await self.collection.count_documents({"email": email})
        return count > 0

    # ========================================================================
    # Búsquedas Específicas por Rol
    # ========================================================================

    async def buscar_tecnicos(
            self,
            especialidad: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Tecnico]:
        """Recupera lista de técnicos, con filtro opcional de especialidad"""
        query = {"tipo_usuario": TipoUsuario.TECNICO.value}
        if especialidad:
            query["especialidades"] = especialidad

        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        # Mapeamos los documentos a entidades Tecnico
        return [await self._to_entity(doc) for doc in docs]

    async def buscar_operadores(self, skip: int = 0, limit: int = 100) -> List[Operador]:
        """Recupera lista de operadores"""
        query = {"tipo_usuario": TipoUsuario.OPERADOR.value}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [await self._to_entity(doc) for doc in docs]

    async def buscar_supervisores(self, skip: int = 0, limit: int = 100) -> List[Supervisor]:
        """Recupera lista de supervisores"""
        query = {"tipo_usuario": TipoUsuario.SUPERVISOR.value}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [await self._to_entity(doc) for doc in docs]

    async def buscar_supervisores_de_empleado(self, empleado_id: int) -> List[Supervisor]:
        """
        Encuentra supervisores asignados a un empleado específico (Técnico u Operador).
        """
        query = {
            "tipo_usuario": TipoUsuario.SUPERVISOR.value,
            "$or": [
                {"operadores_ids": empleado_id},
                {"tecnicos_ids": empleado_id}
            ]
        }
        cursor = self.collection.find(query)
        docs = await cursor.to_list(length=100)
        return [await self._to_entity(doc) for doc in docs]

    # ========================================================================
    # Métodos Privados de Mapeo y Agregación
    # ========================================================================

    async def _buscar_uno_con_relaciones(self, filtro: dict) -> Optional[Usuario]:
        """
        Ejecuta una agregación para obtener el usuario y sus servicios (JOIN) en una sola consulta.
        """
        pipeline = [
            {"$match": filtro},
            # Hacemos LEFT JOIN con la colección de servicios
            {
                "$lookup": {
                    "from": "servicios",
                    "localField": "_id",
                    "foreignField": "solicitante_id",
                    "as": "servicios_data" # Los servicios quedarán en este array temporal
                }
            }
        ]

        cursor = self.collection.aggregate(pipeline)
        resultados = await cursor.to_list(length=1)

        if not resultados:
            return None

        # Convertimos el documento enriquecido a Entidad
        return await self._to_entity(resultados[0])

    def _to_document(self, usuario: Usuario) -> dict:
        """Serializa la Entidad a estructura de MongoDB"""
        doc = {
            "_id": usuario.id,
            "nombre": usuario.nombre,
            "email": str(usuario.email),
            "password_hash": usuario.password_hash,
            "tipo_usuario": usuario.get_tipo_usuario().value,
            "fecha_creacion": usuario.fecha_creacion,
            "ultimo_acceso": usuario.ultimo_acceso
        }

        # Persistir campos específicos según subclase
        if isinstance(usuario, Tecnico):
            doc["especialidades"] = getattr(usuario, "especialidades", [])

        elif isinstance(usuario, Supervisor):
            # Guardamos solo los IDs de las referencias para mantener consistencia
            doc["operadores_ids"] = [op.id for op in usuario.operadores_supervisados if op.id]
            doc["tecnicos_ids"] = [tec.id for tec in usuario.tecnicos_supervisados if tec.id]

        return doc

    async def _to_entity(self, doc: dict) -> Usuario:
        """
        Deserializa el documento MongoDB a la Entidad correcta.
        Maneja la reconstrucción de objetos ValueObject (Email) y listas anidadas.
        """
        # Value Objects
        email = Email(doc["email"])

        # Determinación de tipo para instanciar la clase correcta
        tipo_str = doc.get("tipo_usuario")
        try:
            tipo = TipoUsuario(tipo_str)
        except ValueError:
            # Fallback por si el dato en BD no coincide exactamente
            tipo = TipoUsuario.SOLICITANTE

        base_args = {
            "id": doc["_id"],
            "nombre": doc["nombre"],
            "email": email,
            "password_hash": doc["password_hash"],
            "fecha_creacion": doc.get("fecha_creacion"),
            "ultimo_acceso": doc.get("ultimo_acceso")
        }

        if tipo == TipoUsuario.SOLICITANTE:
            servicios = []
            if "servicios_data" in doc:
                for s_data in doc["servicios_data"]:
                    servicios.append(Servicio(
                        id=s_data["_id"],
                        tipo=TipoServicio(s_data["tipo"]),
                        numero_servicio=s_data["numero_servicio"],
                        solicitante=None,
                        activo=s_data["activo"],
                        fecha_alta=s_data.get("fecha_alta")
                    ))

            return Solicitante(
                **base_args,
                servicios_suscritos=servicios
            )

        elif tipo == TipoUsuario.OPERADOR:
            return Operador(**base_args)

        elif tipo == TipoUsuario.TECNICO:
            return Tecnico(
                **base_args,
                especialidades=doc.get("especialidades", [])
            )

        elif tipo == TipoUsuario.SUPERVISOR:
            # Nota: Los supervisados se cargan "lazy" o mediante otra consulta si se requieren completos.
            # Aquí devolvemos el Supervisor base.
            return Supervisor(**base_args)

        else:
            # Fallback seguro
            return Usuario(**base_args)