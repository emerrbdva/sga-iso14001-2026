from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared_models.models import environmental_entities as schemas
from . import crud
from .db import get_db

router = APIRouter()

# --- NUEVO ENDPOINT ---
@router.get("/risks/", response_model=List[schemas.Risk], tags=["Riesgos y Oportunidades"])
def read_risks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lee una lista de todos los riesgos en el sistema."""
    risks = crud.get_risks(db, skip=skip, limit=limit)
    return risks

@router.post("/aspects/{aspect_id}/risks/", response_model=schemas.Risk, tags=["Riesgos y Oportunidades"])
def create_risk_for_aspect(aspect_id: int, risk: schemas.RiskCreate, db: Session = Depends(get_db)):
    # Aquí podríamos verificar primero si el aspect_id existe, pero lo omitimos por simplicidad
    return crud.create_risk_for_aspect(db=db, risk=risk, aspect_id=aspect_id)

@router.get("/aspects/{aspect_id}/risks/", response_model=List[schemas.Risk], tags=["Riesgos y Oportunidades"])
def read_risks_for_aspect(aspect_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    risks = crud.get_risks_by_aspect(db, aspect_id=aspect_id, skip=skip, limit=limit)
    return risks