from sqlalchemy import Column, Integer, String, Date, Float, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from shared_models.models.environmental_entities import GHGScode, EmissionSourceType

Base = declarative_base()

# CORRECTED MODELS
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
