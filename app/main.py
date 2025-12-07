from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import bcrypt
import passlib.handlers.bcrypt

if not hasattr(bcrypt, '__about__'):
    class MockAbout:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = MockAbout()


from app.routers import (
    auth, usuarios, requerimientos, comentarios,
    asignaciones, notificaciones, servicios, reportes
)
from app.infrastructure.mongodb.database import mongodb
import logging


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para gestionar el ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Conectar a MongoDB
    logger.info("🚀 Iniciando aplicación...")
    try:
        await mongodb.conectar()
        logger.info("✅ Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al iniciar: {e}")
        raise

    yield  # La aplicación se ejecuta aquí

    # Shutdown: Desconectar de MongoDB
    logger.info("🛑 Cerrando aplicación...")
    await mongodb.desconectar()
    logger.info("✅ Aplicación cerrada correctamente")


app = FastAPI(
    title="Sistema de Mesa de Ayuda - Comunicarlos",
    description="""
    API REST para gestión de requerimientos técnicos con MongoDB.

    ## Características:
    * Autenticación JWT
    * Gestión de usuarios por roles
    * Requerimientos (incidentes y solicitudes)
    * Sistema de notificaciones
    * Reportes y dashboards

    ## Arquitectura:
    * FastAPI + MongoDB
    * Repository Pattern
    * Domain-Driven Design
    * Docker containerizado
    """,
    version="1.0.0",
    lifespan=lifespan  # ← Gestión del ciclo de vida
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(requerimientos.router, prefix="/api/v1/requerimientos", tags=["Requerimientos"])
app.include_router(comentarios.router, prefix="/api/v1/requerimientos", tags=["Comentarios"])
app.include_router(asignaciones.router, prefix="/api/v1/requerimientos", tags=["Asignaciones"])
app.include_router(notificaciones.router, prefix="/api/v1/notificaciones", tags=["Notificaciones"])
app.include_router(servicios.router, prefix="/api/v1/servicios", tags=["Servicios"])
app.include_router(reportes.router, prefix="/api/v1/reportes", tags=["Reportes"])


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "API Sistema de Mesa de Ayuda - Comunicarlos",
        "version": "1.0.0",
        "database": "MongoDB",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check con estado de MongoDB"""
    try:
        # Verificar conexión a MongoDB
        db = mongodb.get_database()
        await db.command('ping')
        mongodb_status = "connected"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"

    return {
        "status": "healthy" if mongodb_status == "connected" else "unhealthy",
        "mongodb": mongodb_status
    }

