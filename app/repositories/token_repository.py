from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

class TokenRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["tokens_revocados"]

    async def crear_indice_ttl(self):
        """
        Crea un índice TTL para que los tokens se borren automáticamente
        de la base de datos cuando llegue su fecha de expiración.
        """
        # expireAfterSeconds=0 significa que expira exactamente en la fecha del campo 'expiracion'
        await self.collection.create_index("expiracion", expireAfterSeconds=0)

    async def revocar(self, token: str, expiracion: datetime):
        """Guarda el token en la lista negra"""
        await self.collection.insert_one({
            "token": token,
            "expiracion": expiracion
        })

    async def esta_revocado(self, token: str) -> bool:
        """Verifica si el token está en la lista negra"""
        doc = await self.collection.find_one({"token": token})
        return doc is not None