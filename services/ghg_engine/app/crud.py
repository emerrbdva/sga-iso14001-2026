from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import date
from . import models
from shared_models.models import environmental_entities as schemas

# --- CRUD para Factores de Emisión ---
def create_emission_factor(db: Session, factor: schemas.EmissionFactorCreate):
    db_factor = models.EmissionFactor(**factor.dict())
    try:
        db.add(db_factor)
        db.commit()
        db.refresh(db_factor)
        return db_factor
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Emission factor with name '{factor.name}' already exists.")

# --- CRUD para Fuentes de Emisión ---
def create_emission_source(db: Session, source: schemas.EmissionSourceCreate):
    db_source = models.EmissionSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

# --- CRUD para Datos de Actividad ---
def create_activity_data(db: Session, activity: schemas.ActivityDataCreate):
    db_activity = models.ActivityData(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity
    
def get_activity_data_for_period(db: Session, start_date: date, end_date: date):
    # Usamos joinedload para cargar eficientemente los datos relacionados
    return db.query(models.ActivityData).options(
        joinedload(models.ActivityData.source).joinedload(models.EmissionSource.factor)
    ).filter(models.ActivityData.activity_date.between(start_date, end_date)).all()