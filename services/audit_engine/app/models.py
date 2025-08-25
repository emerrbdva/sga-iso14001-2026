from sqlalchemy import Column, Integer, String, Date, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from shared_models.models.environmental_entities import FindingType

Base = declarative_base()

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    scope = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    findings = relationship("AuditFinding", back_populates="audit")

class AuditFinding(Base):
    __tablename__ = "audit_findings"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    evidence = Column(String)
    clause = Column(String)
    finding_type = Column(SQLAlchemyEnum(FindingType))
    audit_id = Column(Integer, ForeignKey("audits.id"))
    audit = relationship("Audit", back_populates="findings")