from fastapi import FastAPI
# CAMBIO: Se quita el punto de la importación
from app.api import router as api_router

app = FastAPI(
    title="Motor de Cumplimiento del SGA - ISO 14001:2026",
    description="Gestiona las Obligaciones de Cumplimiento y su vínculo con los Aspectos.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "Compliance Engine"}