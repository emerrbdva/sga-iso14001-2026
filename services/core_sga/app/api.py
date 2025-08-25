from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from shared_models.models import environmental_entities as schemas
from . import crud, models
from .db import get_db

router = APIRouter()

@router.get("/policy", response_model=Optional[schemas.EnvironmentalPolicy], tags=["Política Ambiental"])
def read_environmental_policy(db: Session = Depends(get_db)):
    # ... (código sin cambios)
    policy = crud.get_policy(db=db)
    if not policy:
        raise HTTPException(status_code=404, detail="Política ambiental no ha sido definida todavía.")
    return policy

@router.post("/policy", response_model=schemas.EnvironmentalPolicy, status_code=status.HTTP_201_CREATED, tags=["Política Ambiental"])
def create_or_update_environmental_policy(policy: schemas.EnvironmentalPolicyCreate, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    return crud.update_policy(db=db, policy_data=policy)

@router.post("/aspects", response_model=schemas.EnvironmentalAspect, status_code=status.HTTP_201_CREATED, tags=["Aspectos Ambientales"])
def create_environmental_aspect(aspect: schemas.EnvironmentalAspectCreate, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    return crud.create_aspect(db=db, aspect=aspect)

@router.get("/aspects", response_model=List[schemas.EnvironmentalAspect], tags=["Aspectos Ambientales"])
def read_environmental_aspects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    aspects = crud.get_aspects(db, skip=skip, limit=limit)
    return aspects

@router.get("/aspects/{aspect_id}", response_model=schemas.EnvironmentalAspect, tags=["Aspectos Ambientales"])
def read_environmental_aspect(aspect_id: int, db: Session = Depends(get_db)):
    # ... (código sin cambios)
    db_aspect = crud.get_aspect(db, aspect_id=aspect_id)
    if db_aspect is None:
        raise HTTPException(status_code=404, detail="Aspecto ambiental no encontrado")
    return db_aspect