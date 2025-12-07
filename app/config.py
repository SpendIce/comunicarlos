from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "Sistema Mesa de Ayuda - Comunicarlos"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/mesa_ayuda"

    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # Paginación
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Email corporativo
    CORPORATE_EMAIL_DOMAIN: str = "@comunicarlos.com.ar"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
