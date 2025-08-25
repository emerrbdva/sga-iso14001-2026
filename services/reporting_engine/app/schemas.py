from pydantic import BaseModel
from typing import List, Dict, Optional
# Importamos los modelos que vamos a recibir de los otros servicios
from shared_models.models.environmental_entities import (
    EnvironmentalPolicy, EnvironmentalAspect, Risk, 
    ComplianceObligation, Objective
)

class GHGInventory(BaseModel):
    total_co2e: float
    emissions_by_scope: Dict[str, float]

class SustainabilityReport(BaseModel):
    company_name: str
    reporting_period: str
    policy: Optional[EnvironmentalPolicy] = None
    significant_aspects: List[EnvironmentalAspect] = []
    top_risks: List[Risk] = []
    objectives_summary: List[Objective] = []
    ghg_inventory: Optional[GHGInventory] = None