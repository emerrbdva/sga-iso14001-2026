from fastapi import FastAPI
from app import models
from app.db import engine
from app.api import router as api_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Servicio Core del SGA - ISO 14001:2026",
    description="Gestiona las entidades centrales del Sistema de Gestión Ambiental.",
    version="1.0.0"
)

# CAMBIO: Se eliminó ", tags=["SGA Core"]" de esta línea
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint de salud para verificar que el servicio está activo."""
    return {"status": "ok", "service": "Core SGA"}