from sqlalchemy.orm import Session, joinedload
from . import models
from shared_models.models import environmental_entities as schemas

def get_objective(db: Session, objective_id: int):
    # Usamos joinedload para cargar siempre los indicadores junto con el objetivo
    return db.query(models.Objective).options(joinedload(models.Objective.indicators)).filter(models.Objective.id == objective_id).first()

def get_objectives(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Objective).options(joinedload(models.Objective.indicators)).offset(skip).limit(limit).all()

def create_objective(db: Session, objective: schemas.ObjectiveCreate):
    db_objective = models.Objective(**objective.dict())
    db.add(db_objective)
    db.commit()
    db.refresh(db_objective)
    return db_objective

def create_indicator_for_objective(db: Session, indicator: schemas.IndicatorCreate, objective_id: int):
    db_indicator = models.Indicator(**indicator.dict(), objective_id=objective_id)
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator