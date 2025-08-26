from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.db import engine
from app.api import router as api_router

# ESTA LÍNEA ES LA CLAVE: Le dice a SQLAlchemy que cree todas las tablas
# definidas en 'models.py' en la base de datos al arrancar.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio Core del SGA - ISO 14001:2026",
    description="Gestiona las entidades centrales del Sistema de Gestión Ambiental.",
    version="1.0.0"
)

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
    return {"status": "ok", "service": "core-sga"}