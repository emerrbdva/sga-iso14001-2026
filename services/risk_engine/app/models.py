from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func # <--- AÑADIR ESTA IMPORTACIÓN
from shared_models.models.environmental_entities import RiskCategory

Base = declarative_base()

class Risk(Base):
    __tablename__ = "risks"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    category = Column(SQLAlchemyEnum(RiskCategory))
    probability = Column(Integer)
    impact = Column(Integer)
    aspect_id = Column(Integer, ForeignKey("environmental_aspects.id"))
    
    # --- CAMBIO: AÑADIMOS LA LÓGICA DE AUTO-GENERACIÓN DE FECHAS ---
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Y también la propiedad calculada para el risk_level
    @property
    def risk_level(self) -> int:
        return self.probability * self.impact

class EnvironmentalAspect(Base):
    __tablename__ = "environmental_aspects"
    id = Column(Integer, primary_key=True)
    name = Column(String)