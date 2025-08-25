from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from shared_models.models import environmental_entities as schemas
from . import crud, calculator
from .db import get_db

router = APIRouter()

# Endpoints de configuración
@router.post("/factors/", response_model=schemas.EmissionFactor, tags=["Configuración GEI"])
def create_factor(factor: schemas.EmissionFactorCreate, db: Session = Depends(get_db)):
    return crud.create_emission_factor(db=db, factor=factor)

@router.post("/sources/", response_model=schemas.EmissionSource, tags=["Configuración GEI"])
def create_source(source: schemas.EmissionSourceCreate, db: Session = Depends(get_db)):
    return crud.create_emission_source(db=db, source=source)

# Endpoint para registrar datos
@router.post("/activity-data/", response_model=schemas.ActivityData, tags=["Datos de Actividad"])
def create_activity(activity: schemas.ActivityDataCreate, db: Session = Depends(get_db)):
    return crud.create_activity_data(db=db, activity=activity)

# Endpoint principal de cálculo
@router.get("/inventory/", tags=["Cálculo de Inventario GEI"])
def get_ghg_inventory(start_date: date, end_date: date, db: Session = Depends(get_db)):
    activity_data = crud.get_activity_data_for_period(db, start_date=start_date, end_date=end_date)
    inventory = calculator.calculate_emissions(activity_data)
    return inventory