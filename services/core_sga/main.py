from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import models
from app.db import engine, get_db
from app.api import router as api_router
from shared_models.config import get_settings
from shared_models.logging_utils import setup_logger
from sqlalchemy.orm import Session
from sqlalchemy import text

# Configuración y logging
settings = get_settings("core_sga")
logger = setup_logger("core_sga", settings.log_level)

# ESTA LÍNEA ES LA CLAVE: Le dice a SQLAlchemy que cree todas las tablas
# definidas en 'models.py' en la base de datos al arrancar.
logger.info("Creating database tables")
models.Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI(
    title="Servicio Core del SGA - ISO 14001:2026",
    description="Gestiona las entidades centrales del Sistema de Gestión Ambiental.",
    version="1.0.0"
)

logger.info("FastAPI application initialized")

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- FIN DE LA CONFIGURACIÓN DE CORS ---

# Incluye las rutas de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint de salud para verificar que el servicio está activo."""
    logger.info("Health check requested")
    return {"status": "ok", "service": "core-sga", "version": "1.0.0"}

@app.get("/health", tags=["Health Check"])
def health_check():
    """Health check detallado que incluye conectividad de base de datos."""
    logger.info("Detailed health check requested")
    
    health_status = {
        "status": "healthy",
        "service": "core-sga",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Verificar conectividad de base de datos
    try:
        db: Session = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
        logger.info("Database connectivity check passed")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        logger.error("Database connectivity check failed", error=str(e))
    finally:
        if 'db' in locals():
            db.close()
    
    # Verificar conectividad con servicio de IA
    try:
        from shared_models.http_client import create_http_client
        ai_client = create_http_client("ai_engine", settings.ai_service_url)
        # Esto no hará la petición real debido al circuit breaker, pero verifica la configuración
        health_status["checks"]["ai_service"] = "configured"
    except Exception as e:
        health_status["checks"]["ai_service"] = f"configuration_error: {str(e)}"
        logger.warning("AI service configuration check failed", error=str(e))
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=health_status, status_code=status_code)