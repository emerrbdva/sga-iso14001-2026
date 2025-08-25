from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="Motor de Huella de Carbono (GEI) del SGA",
    description="Gestiona y calcula el inventario de emisiones de GEI según ISO 14064-1.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "service": "GHG Engine"}