from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared_models.models import environmental_entities as schemas
from . import crud
from .db import get_db

router = APIRouter()

@router.post("/obligations/", response_model=schemas.ComplianceObligation, tags=["Obligaciones de Cumplimiento"])
def create_compliance_obligation(obligation: schemas.ComplianceObligationCreate, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    return crud.create_obligation(db=db, obligation=obligation)

@router.get("/obligations/", response_model=List[schemas.ComplianceObligation], tags=["Obligaciones de Cumplimiento"])
def read_compliance_obligations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    obligations = crud.get_obligations(db, skip=skip, limit=limit)
    return obligations

@router.post("/aspects/{aspect_id}/obligations/{obligation_id}", response_model=schemas.ComplianceObligation, tags=["Obligaciones de Cumplimiento"])
def link_obligation_to_aspect(aspect_id: int, obligation_id: int, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    linked_obligation = crud.link_obligation_to_aspect(db=db, aspect_id=aspect_id, obligation_id=obligation_id)
    if linked_obligation is None:
        raise HTTPException(status_code=404, detail="Aspecto u Obligación no encontrados")
    return linked_obligation