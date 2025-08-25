from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Motor de Reportes del SGA",
    description="Agrega datos de todos los servicios para generar reportes de sostenibilidad.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "Reporting Engine"}