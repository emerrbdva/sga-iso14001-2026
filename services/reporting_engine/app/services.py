import requests
from datetime import date
from typing import List, Optional, Dict

# URLs base de nuestros microservicios. Usamos los nombres de servicio de Docker.
URL_CORE_SGA = "http://core-sga-api:8000/api/v1"
URL_RISK_ENGINE = "http://risk-engine-api:8002/api/v1"
URL_OBJECTIVES_ENGINE = "http://objectives-engine-api:8004/api/v1"
URL_GHG_ENGINE = "http://ghg-engine-api:8005/api/v1"

def get_policy() -> Optional[dict]:
    """Obtiene la política ambiental del Servicio Core."""
    try:
        response = requests.get(f"{URL_CORE_SGA}/policy", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar el Servicio Core para la política: {e}")
        return None

def get_significant_aspects() -> List[dict]:
    """Obtiene todos los aspectos y los filtra por significancia."""
    try:
        response = requests.get(f"{URL_CORE_SGA}/aspects", params={"limit": 500}, timeout=5)
        response.raise_for_status()
        all_aspects = response.json()
        # Filtramos en Python los que son significativos
        return [aspect for aspect in all_aspects if aspect.get("is_significant")]
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar el Servicio Core para los aspectos: {e}")
        return []

def get_ghg_inventory(start_date: date, end_date: date) -> Optional[dict]:
    """Obtiene el inventario de GEI del Motor de Huella de Carbono."""
    try:
        response = requests.get(
            f"{URL_GHG_ENGINE}/inventory/",
            params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            timeout=10 # Damos más tiempo a este cálculo
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar el Motor de GEI: {e}")
        return None

# Podríamos añadir funciones similares para get_top_risks, get_objectives, etc.
# Por simplicidad, nos centraremos en estos para el reporte inicial.