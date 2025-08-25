from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Servicio de IA para SGA - ISO 14001:2026",
    description="Provee funcionalidades de NLP para enriquecer datos del SGA.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint de salud para verificar que el servicio de IA está activo."""
    return {"status": "ok", "service": "AI Engine"}