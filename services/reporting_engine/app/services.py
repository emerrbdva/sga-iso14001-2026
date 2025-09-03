import requests
from datetime import date
from typing import List, Optional, Dict
from shared_models.config import get_settings
from shared_models.logging_utils import setup_logger, log_api_call
from shared_models.http_client import create_http_client, ServiceError

# Configuración y logging
settings = get_settings("reporting_engine")
logger = setup_logger("reporting_engine", settings.log_level)

# Clientes HTTP para comunicación con otros servicios
core_sga_client = create_http_client("core_sga", settings.core_sga_url)
risk_engine_client = create_http_client("risk_engine", settings.risk_engine_url)
objectives_engine_client = create_http_client("objectives_engine", settings.objectives_engine_url)
ghg_engine_client = create_http_client("ghg_engine", settings.ghg_engine_url)

def get_policy() -> Optional[dict]:
    """Obtiene la política ambiental del Servicio Core."""
    logger.info("Fetching environmental policy from core service")
    try:
        policy_data = core_sga_client.get("/policy")
        logger.info("Environmental policy retrieved successfully")
        return policy_data
    except ServiceError as e:
        logger.error("Failed to fetch environmental policy", error=str(e))
        return None
    except Exception as e:
        logger.error("Unexpected error fetching policy", error=str(e))
        return None

def get_significant_aspects() -> List[dict]:
    """Obtiene todos los aspectos y los filtra por significancia."""
    logger.info("Fetching significant environmental aspects")
    try:
        all_aspects = core_sga_client.get("/aspects", params={"limit": 500})
        # Filtramos en Python los que son significativos
        significant_aspects = [aspect for aspect in all_aspects if aspect.get("is_significant")]
        
        logger.info("Significant aspects retrieved", 
                   total_aspects=len(all_aspects),
                   significant_count=len(significant_aspects))
        return significant_aspects
    except ServiceError as e:
        logger.error("Failed to fetch environmental aspects", error=str(e))
        return []
    except Exception as e:
        logger.error("Unexpected error fetching aspects", error=str(e))
        return []

def get_ghg_inventory(start_date: date, end_date: date) -> Optional[dict]:
    """Obtiene el inventario de GEI del Motor de Huella de Carbono."""
    logger.info("Fetching GHG inventory", start_date=start_date.isoformat(), 
               end_date=end_date.isoformat())
    try:
        inventory_data = ghg_engine_client.get(
            "/inventory/",
            params={
                "start_date": start_date.isoformat(), 
                "end_date": end_date.isoformat()
            }
        )
        logger.info("GHG inventory retrieved successfully",
                   total_co2e=inventory_data.get("total_co2e", 0))
        return inventory_data
    except ServiceError as e:
        logger.error("Failed to fetch GHG inventory", error=str(e))
        return None
    except Exception as e:
        logger.error("Unexpected error fetching GHG inventory", error=str(e))
        return None

# Podríamos añadir funciones similares para get_top_risks, get_objectives, etc.
# Por simplicidad, nos centraremos en estos para el reporte inicial.