from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Motor de Auditorías del SGA (ISO 19011)",
    description="Gestiona la planificación, ejecución y seguimiento de auditorías.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "Audit Engine"}