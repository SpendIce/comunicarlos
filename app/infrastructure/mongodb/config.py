from pydantic_settings import BaseSettings


class MongoDBSettings(BaseSettings):
    """Configuración de MongoDB"""
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "mesa_ayuda_db"

    class Config:
        env_file = ".env"


mongodb_settings = MongoDBSettings()