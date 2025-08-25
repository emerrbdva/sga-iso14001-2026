from fastapi import APIRouter
from .schemas import AnalysisRequest, AnalysisResponse
from .processor import classifier

router = APIRouter()

@router.post("/analyze/aspect_type", response_model=AnalysisResponse, tags=["Análisis de Aspectos"])
def analyze_aspect_type(request: AnalysisRequest):
    """
    Recibe una descripción textual de un aspecto ambiental y devuelve
    una sugerencia de su tipo (Emisión, Consumo, etc.) y un puntaje de confianza.
    """
    result = classifier.classify(request.text)
    return AnalysisResponse(**result)