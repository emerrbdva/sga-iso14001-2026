from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from shared_models.models.environmental_entities import ObligationType

Base = declarative_base()

# CAMBIO: Se añaden las ForeignKey a la tabla de asociación, igual que en core-sga
aspect_obligation_link = Table('aspect_obligation_link', Base.metadata,
    Column('aspect_id', Integer, ForeignKey('environmental_aspects.id'), primary_key=True),
    Column('obligation_id', Integer, ForeignKey('compliance_obligations.id'), primary_key=True)
)

class EnvironmentalAspect(Base):
    __tablename__ = "environmental_aspects"
    id = Column(Integer, primary_key=True)
    # Se añade 'back_populates' para una relación bidireccional correcta
    obligations = relationship("ComplianceObligation", secondary=aspect_obligation_link, back_populates="aspects")

class ComplianceObligation(Base):
    __tablename__ = "compliance_obligations"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    source = Column(String)
    obligation_type = Column(SQLAlchemyEnum(ObligationType))
    # Se añade 'back_populates' para una relación bidireccional correcta
    aspects = relationship("EnvironmentalAspect", secondary=aspect_obligation_link, back_populates="obligations")