from sqlalchemy.orm import Session
from . import models
from shared_models.models import environmental_entities as schemas

def get_risk(db: Session, risk_id: int):
    return db.query(models.Risk).filter(models.Risk.id == risk_id).first()

# --- NUEVA FUNCIÓN ---
def get_risks(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de todos los riesgos."""
    return db.query(models.Risk).offset(skip).limit(limit).all()

def get_risks_by_aspect(db: Session, aspect_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Risk).filter(models.Risk.aspect_id == aspect_id).offset(skip).limit(limit).all()

def create_risk_for_aspect(db: Session, risk: schemas.RiskCreate, aspect_id: int):
    db_risk = models.Risk(**risk.dict(), aspect_id=aspect_id)
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk
