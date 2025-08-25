from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

# --- Enums (sin cambios) ---
class LifecycleStage(str, Enum):
    RAW_MATERIAL_ACQUISITION = "Adquisición de Materias Primas"
    DESIGN_AND_DEVELOPMENT = "Diseño y Desarrollo"
    MANUFACTURING = "Fabricación"
    TRANSPORTATION_DISTRIBUTION = "Transporte y Distribución"
    USE_AND_SERVICE = "Uso y Servicio"
    END_OF_LIFE = "Fin de Vida"

class AspectType(str, Enum):
    EMISSION = "Emisión"
    CONSUMPTION = "Consumo"
    WASTE_GENERATION = "Generación de Residuo"
    RESOURCE_USE = "Uso de Recurso Natural"

class RiskCategory(str, Enum):
    OPERATIONAL = "Operacional"
    COMPLIANCE = "Cumplimiento Legal"
    CLIMATE_PHYSICAL = "Climático Físico"
    CLIMATE_TRANSITION = "Climático de Transición"
    BIODIVERSITY = "Biodiversidad"
    REPUTATIONAL = "Reputacional"

class ObligationType(str, Enum):
    LEGAL = "Legal"
    PERMIT = "Permiso/Licencia"
    STANDARD = "Norma Voluntaria"
    OTHER = "Otro"
    
class GHGScode(str, Enum):
    SCOPE_1 = "Alcance 1"
    SCOPE_2 = "Alcance 2"
    SCOPE_3 = "Alcance 3"

class EmissionSourceType(str, Enum):
    STATIONARY_COMBUSTION = "Combustión Estacionaria"
    MOBILE_COMBUSTION = "Combustión Móvil"
    FUGITIVE_EMISSIONS = "Emisiones Fugitivas"
    PROCESS_EMISSIONS = "Emisiones de Proceso"
    PURCHASED_ELECTRICITY = "Electricidad Comprada"
    
class FindingType(str, Enum):
    CONFORMITY = "Conformidad"
    NONCONFORMITY_MINOR = "No Conformidad Menor"
    NONCONFORMITY_MAJOR = "No Conformidad Mayor"
    OPPORTUNITY_FOR_IMPROVEMENT = "Oportunidad de Mejora"

# --- MODELOS BASE Y DE CREACIÓN ---
class EnvironmentalPolicyBase(BaseModel):
    version: str
    content: str
    approval_date: datetime
    approved_by: str
    includes_climate_commitment: bool
    includes_circular_economy_commitment: bool
    includes_biodiversity_commitment: bool

class EnvironmentalPolicyCreate(EnvironmentalPolicyBase):
    pass

class EnvironmentalAspectBase(BaseModel):
    name: str
    description: str
    lifecycle_stage: LifecycleStage
    aspect_type: AspectType
    is_significant: bool = False

class EnvironmentalAspectCreate(EnvironmentalAspectBase):
    pass

class ComplianceObligationBase(BaseModel):
    name: str
    description: str
    source: str
    obligation_type: ObligationType

class ComplianceObligationCreate(ComplianceObligationBase):
    pass

class RiskBase(BaseModel):
    description: str
    category: RiskCategory
    probability: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    aspect_id: Optional[int] = None

class RiskCreate(RiskBase):
    pass

class IndicatorBase(BaseModel):
    name: str
    current_value: float
    unit: str
    
class IndicatorCreate(IndicatorBase):
    pass

class ObjectiveBase(BaseModel):
    description: str
    target_value: float
    start_date: date
    end_date: date

class ObjectiveCreate(ObjectiveBase):
    pass

class EmissionFactorBase(BaseModel):
    name: str
    value: float
    unit: str
    source: str = "IPCC 2006"

class EmissionFactorCreate(EmissionFactorBase):
    pass

class EmissionSourceBase(BaseModel):
    name: str
    source_type: EmissionSourceType
    scope: GHGScode

class EmissionSourceCreate(EmissionSourceBase):
    factor_id: int

class ActivityDataBase(BaseModel):
    value: float
    unit: str
    activity_date: date
    source_id: int

class ActivityDataCreate(ActivityDataBase):
    pass

class AuditFindingBase(BaseModel):
    description: str = Field(..., description="Descripción detallada del hallazgo")
    evidence: str = Field(..., description="Evidencia observada que soporta el hallazgo")
    clause: str = Field(..., description="Cláusula de la norma auditada (ej. ISO 14001: 6.1.2)")
    finding_type: FindingType

class AuditFindingCreate(AuditFindingBase):
    pass

class AuditBase(BaseModel):
    scope: str = Field(..., description="Alcance de la auditoría (qué áreas o procesos se auditan)")
    start_date: date
    end_date: date

class AuditCreate(AuditBase):
    pass

# --- MODELOS DE RESPUESTA (para evitar bucles infinitos) ---

# Modelos "simples" sin relaciones anidadas
class ComplianceObligationSimple(ComplianceObligationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EnvironmentalAspectSimple(EnvironmentalAspectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ObjectiveSimple(ObjectiveBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AuditSimple(AuditBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    
class RiskSimple(RiskBase):
    id: int
    risk_level: int
    model_config = ConfigDict(from_attributes=True)

# Modelos "completos" que usan los modelos simples para las relaciones
class EnvironmentalAspect(EnvironmentalAspectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    obligations: List[ComplianceObligationSimple] = []
    risks: List[RiskSimple] = []
    model_config = ConfigDict(from_attributes=True)
    
class ComplianceObligation(ComplianceObligationBase):
    id: int
    aspects: List[EnvironmentalAspectSimple] = []
    model_config = ConfigDict(from_attributes=True)

class Indicator(IndicatorBase):
    id: int
    objective: ObjectiveSimple
    model_config = ConfigDict(from_attributes=True)

class Objective(ObjectiveBase):
    id: int
    indicators: List[Indicator] = []
    model_config = ConfigDict(from_attributes=True)
    
class AuditFinding(AuditFindingBase):
    id: int
    audit: AuditSimple
    model_config = ConfigDict(from_attributes=True)

class Audit(AuditBase):
    id: int
    findings: List[AuditFinding] = []
    model_config = ConfigDict(from_attributes=True)

# Modelos completos que no tienen relaciones complejas
class EnvironmentalPolicy(EnvironmentalPolicyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Risk(RiskBase):
    id: int
    risk_level: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
    
class EmissionFactor(EmissionFactorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class EmissionSource(EmissionSourceBase):
    id: int
    factor: EmissionFactor
    model_config = ConfigDict(from_attributes=True)

class ActivityData(ActivityDataBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Pydantic necesita que llamemos a esto para resolver las referencias cruzadas
EnvironmentalAspect.model_rebuild()
ComplianceObligation.model_rebuild()
Indicator.model_rebuild()
Objective.model_rebuild()
Audit.model_rebuild()
AuditFinding.model_rebuild()