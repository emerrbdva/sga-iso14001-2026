from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared_models.models import environmental_entities as schemas
from . import crud
from .db import get_db

router = APIRouter()

@router.post("/audits/", response_model=schemas.Audit, tags=["Auditorías"])
def create_audit(audit: schemas.AuditCreate, db: Session = Depends(get_db)):
    return crud.create_audit(db=db, audit=audit)

@router.get("/audits/", response_model=List[schemas.Audit], tags=["Auditorías"])
def read_audits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    audits = crud.get_audits(db, skip=skip, limit=limit)
    return audits

@router.post("/audits/{audit_id}/findings/", response_model=schemas.AuditFinding, tags=["Auditorías"])
def create_finding_for_audit(audit_id: int, finding: schemas.AuditFindingCreate, db: Session = Depends(get_db)):
    db_audit = crud.get_audit(db, audit_id=audit_id)
    if db_audit is None:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    return crud.create_finding_for_audit(db=db, finding=finding, audit_id=audit_id)