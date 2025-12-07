from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.infrastructure.mongodb.config import mongodb_settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Gestión de conexión a MongoDB (Singleton Pattern).
    Mantiene una única conexión a la base de datos.
    """
    _instance: Optional['MongoDB'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    async def conectar(self) -> None:
        """Establece conexión con MongoDB"""
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(
                    mongodb_settings.MONGODB_URL,
                    maxPoolSize=10,
                    minPoolSize=2
                )
                self._database = self._client[mongodb_settings.MONGODB_DB_NAME]
                await self._client.admin.command('ping')
                logger.info(f"✅ Conectado a MongoDB: {mongodb_settings.MONGODB_DB_NAME}")
                await self._crear_indices()
            except Exception as e:
                logger.error(f"❌ Error al conectar a MongoDB: {e}")
                raise

    async def desconectar(self) -> None:
        """Cierra la conexión"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("🔌 Desconectado de MongoDB")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Retorna la instancia de la base de datos"""
        if self._database is None:
            raise RuntimeError("Base de datos no inicializada")
        return self._database

    async def _crear_indices(self) -> None:
        """Crea índices para optimizar consultas"""
        db = self.get_database()
        try:
            # Usuarios
            await db.usuarios.create_index("email", unique=True)
            await db.usuarios.create_index("tipo_usuario")

            # Requerimientos
            await db.requerimientos.create_index("solicitante_id")
            await db.requerimientos.create_index("tecnico_asignado_id")
            await db.requerimientos.create_index("estado")
            await db.requerimientos.create_index([("estado", 1), ("fecha_creacion", -1)])

            # Servicios
            await db.servicios.create_index("solicitante_id")

            # Notificaciones
            await db.notificaciones.create_index([("supervisor_id", 1), ("leida", 1)])

            logger.info("✅ Índices creados")
        except Exception as e:
            logger.warning(f"⚠️ Índices: {e}")


mongodb = MongoDB()


