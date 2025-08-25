from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import traceback
import sys
from . import models
from shared_models.models import environmental_entities as schemas

def get_obligation(db: Session, obligation_id: int):
    """
    Obtiene una obligación de cumplimiento por su ID.
    """
    return db.query(models.ComplianceObligation).filter(models.ComplianceObligation.id == obligation_id).first()

def get_obligations(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de obligaciones de cumplimiento.
    """
    return db.query(models.ComplianceObligation).offset(skip).limit(limit).all()

def create_obligation(db: Session, obligation: schemas.ComplianceObligationCreate):
    """
    Crea una nueva obligación de cumplimiento en la base de datos.
    """
    db_obligation = models.ComplianceObligation(**obligation.dict())
    db.add(db_obligation)
    db.commit()
    db.refresh(db_obligation)
    return db_obligation

def link_obligation_to_aspect(db: Session, aspect_id: int, obligation_id: int):
    """
    Vincula un aspecto ambiental existente a una obligación de cumplimiento existente.
    """
    try:
        # Busca la obligación para asegurarse de que existe
        obligation = db.query(models.ComplianceObligation).filter(models.ComplianceObligation.id == obligation_id).first()
        if not obligation:
            print("Obligation not found, returning None", file=sys.stderr)
            return None

        # Directly attempt to insert the link
        insert_stmt = text(
            "INSERT INTO aspect_obligation_link (aspect_id, obligation_id) VALUES (:aspect_id, :obligation_id)"
        )
        db.execute(insert_stmt, {"aspect_id": aspect_id, "obligation_id": obligation_id})
        db.commit()

        # Refresca la obligación para cargar la nueva relación
        db.refresh(obligation)
        print("Link created successfully", file=sys.stderr)
        return obligation
    except Exception as e:
        db.rollback() # Rollback for any exception
        print(f"CRITICAL ERROR in link_obligation_to_aspect: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise # Re-raise the exception