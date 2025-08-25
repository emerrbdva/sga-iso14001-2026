from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from shared_models.models.environmental_entities import ObligationType

Base = declarative_base()

class Objective(Base):
    __tablename__ = "objectives"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    target_value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    indicators = relationship("Indicator", back_populates="objective")

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    current_value = Column(Float)
    unit = Column(String)
    objective_id = Column(Integer, ForeignKey("objectives.id"))
    objective = relationship("Objective", back_populates="indicators")