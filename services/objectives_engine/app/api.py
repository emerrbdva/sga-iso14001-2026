from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared_models.models import environmental_entities as schemas
from . import crud
from .db import get_db

router = APIRouter()

@router.post("/objectives/", response_model=schemas.Objective, tags=["Objetivos e Indicadores"])
def create_objective(objective: schemas.ObjectiveCreate, db: Session = Depends(get_db)):
    return crud.create_objective(db=db, objective=objective)

@router.get("/objectives/", response_model=List[schemas.Objective], tags=["Objetivos e Indicadores"])
def read_objectives(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    objectives = crud.get_objectives(db, skip=skip, limit=limit)
    return objectives

@router.post("/objectives/{objective_id}/indicators/", response_model=schemas.Indicator, tags=["Objetivos e Indicadores"])
def create_indicator_for_objective(objective_id: int, indicator: schemas.IndicatorCreate, db: Session = Depends(get_db)):
    # Verificamos si el objetivo existe antes de añadirle un indicador
    db_objective = crud.get_objective(db, objective_id=objective_id)
    if db_objective is None:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    return crud.create_indicator_for_objective(db=db, indicator=indicator, objective_id=objective_id)