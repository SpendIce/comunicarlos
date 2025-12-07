from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

class SequenceGenerator:
    """Genera IDs secuenciales para simular AUTO_INCREMENT"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.counters = database["counters"]

    async def get_next(self, sequence_name: str) -> int:
        """Obtiene el siguiente ID para una secuencia"""
        result = await self.counters.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return result["value"]