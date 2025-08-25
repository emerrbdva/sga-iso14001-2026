from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Motor de Objetivos e Indicadores del SGA",
    description="Gestiona los objetivos ambientales y sus indicadores de desempeño (KPIs).",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "Objectives Engine"}