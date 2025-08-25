from sqlalchemy.orm import Session, joinedload
from . import models
from shared_models.models import environmental_entities as schemas

def get_audit(db: Session, audit_id: int):
    # Usamos joinedload para cargar siempre los hallazgos junto con la auditoría
    return db.query(models.Audit).options(joinedload(models.Audit.findings)).filter(models.Audit.id == audit_id).first()

def get_audits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Audit).options(joinedload(models.Audit.findings)).offset(skip).limit(limit).all()

def create_audit(db: Session, audit: schemas.AuditCreate):
    db_audit = models.Audit(**audit.dict())
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

def create_finding_for_audit(db: Session, finding: schemas.AuditFindingCreate, audit_id: int):
    db_finding = models.AuditFinding(**finding.dict(), audit_id=audit_id)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding