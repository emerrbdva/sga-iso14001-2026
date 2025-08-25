# CAMBIO: Se han añadido TODOS los tipos de datos y Enums que usamos en el archivo.
from sqlalchemy import (Boolean, Column, Integer, String, DateTime, Date, Float, 
                        Enum as SQLAlchemyEnum, ForeignKey, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base
from shared_models.models.environmental_entities import (
    LifecycleStage, AspectType, RiskCategory, ObligationType, 
    GHGScode, EmissionSourceType, FindingType
)

# --- Tabla de Asociación ---
aspect_obligation_link = Table('aspect_obligation_link', Base.metadata,
    Column('aspect_id', Integer, ForeignKey('environmental_aspects.id'), primary_key=True),
    Column('obligation_id', Integer, ForeignKey('compliance_obligations.id'), primary_key=True)
)

# --- Clases de Tablas ---
class EnvironmentalPolicy(Base):
    __tablename__ = "environmental_policies"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, index=True)
    content = Column(String)
    approval_date = Column(DateTime)
    approved_by = Column(String)
    includes_climate_commitment = Column(Boolean, default=False)
    includes_circular_economy_commitment = Column(Boolean, default=False)
    includes_biodiversity_commitment = Column(Boolean, default=False)

class EnvironmentalAspect(Base):
    __tablename__ = "environmental_aspects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    lifecycle_stage = Column(SQLAlchemyEnum(LifecycleStage))
    aspect_type = Column(SQLAlchemyEnum(AspectType))
    is_significant = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones existentes y nuevas
    obligations = relationship("ComplianceObligation", secondary=aspect_obligation_link, back_populates="aspects")
    risks = relationship("Risk")

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    category = Column(SQLAlchemyEnum(RiskCategory), nullable=False)
    probability = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    aspect_id = Column(Integer, ForeignKey("environmental_aspects.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    @property
    def risk_level(self) -> int:
        return self.probability * self.impact

class ComplianceObligation(Base):
    __tablename__ = "compliance_obligations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    source = Column(String)
    obligation_type = Column(SQLAlchemyEnum(ObligationType))
    aspects = relationship("EnvironmentalAspect", secondary=aspect_obligation_link, back_populates="obligations")

class Objective(Base):
    __tablename__ = "objectives"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    target_value = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    indicators = relationship("Indicator", back_populates="objective")

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    current_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    objective_id = Column(Integer, ForeignKey("objectives.id"))
    objective = relationship("Objective", back_populates="indicators")

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source = Column(String)

class EmissionSource(Base):
    __tablename__ = "emission_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(SQLAlchemyEnum(EmissionSourceType), nullable=False)
    scope = Column(SQLAlchemyEnum(GHGScode), nullable=False)
    factor_id = Column(Integer, ForeignKey("emission_factors.id"))
    factor = relationship("EmissionFactor")
    activity_data = relationship("ActivityData", back_populates="source")

class ActivityData(Base):
    __tablename__ = "activity_data"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    activity_date = Column(Date, nullable=False)
    source_id = Column(Integer, ForeignKey("emission_sources.id"))
    source = relationship("EmissionSource", back_populates="activity_data")

# --- NUEVAS TABLAS PARA AUDITORÍAS ---

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Relación: Una auditoría tiene muchos hallazgos
    findings = relationship("AuditFinding", back_populates="audit")

class AuditFinding(Base):
    __tablename__ = "audit_findings"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    evidence = Column(String, nullable=False)
    clause = Column(String, nullable=False)
    finding_type = Column(SQLAlchemyEnum(FindingType), nullable=False)
    
    # Clave foránea que vincula este hallazgo a una auditoría
    audit_id = Column(Integer, ForeignKey("audits.id"))
    
    # Relación inversa: Un hallazgo pertenece a una auditoría
    audit = relationship("Audit", back_populates="findings")
