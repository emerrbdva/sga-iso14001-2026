from pydantic import BaseModel
from typing import List

class AnalysisRequest(BaseModel):
    """El texto que queremos analizar."""
    text: str

class AnalysisResponse(BaseModel):
    """La respuesta del modelo de IA."""
    suggested_category: str
    confidence_score: float