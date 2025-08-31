"""
Configuración centralizada para el Sistema de Gestión Ambiental ISO 14001:2026
"""
from pydantic_settings import BaseSettings
from typing import Optional


class BaseServiceSettings(BaseSettings):
    """Configuración base compartida por todos los servicios"""
    
    # Configuración de Base de Datos
    database_url: str = "postgresql://user:password@db:5432/sga_db"
    
    # Configuración de Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Configuración de APIs
    api_timeout: int = 30
    api_retries: int = 3
    
    # Configuración de Seguridad
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CoreSGASettings(BaseServiceSettings):
    """Configuración específica para el servicio Core SGA"""
    
    # URLs de otros servicios
    ai_service_url: str = "http://ai-engine-api:8001/api/v1"
    
    # Configuración específica
    max_aspects_per_page: int = 100
    enable_ai_classification: bool = True
    

class ReportingEngineSettings(BaseServiceSettings):
    """Configuración específica para el motor de reportes"""
    
    # URLs de servicios
    core_sga_url: str = "http://core-sga-api:8000/api/v1"
    risk_engine_url: str = "http://risk-engine-api:8002/api/v1"
    objectives_engine_url: str = "http://objectives-engine-api:8004/api/v1"
    ghg_engine_url: str = "http://ghg-engine-api:8005/api/v1"
    
    # Configuración de plantillas
    templates_dir: str = "app/templates"
    

class AIEngineSettings(BaseServiceSettings):
    """Configuración específica para el motor de IA"""
    
    # Modelo de IA
    model_name: str = "facebook/bart-large-mnli"
    model_cache_dir: Optional[str] = None
    max_sequence_length: int = 512
    

class GHGEngineSettings(BaseServiceSettings):
    """Configuración específica para el motor de GEI"""
    
    # Factores de emisión por defecto (en kg CO2e por unidad)
    default_electricity_factor: float = 0.82  # Factor promedio de red eléctrica
    default_gasoline_factor: float = 2.31     # kg CO2e por litro
    default_diesel_factor: float = 2.68       # kg CO2e por litro
    

# Función de utilidad para obtener la configuración del servicio
def get_settings(service_name: str) -> BaseServiceSettings:
    """
    Retorna la configuración apropiada según el nombre del servicio
    """
    settings_map = {
        "core_sga": CoreSGASettings,
        "reporting_engine": ReportingEngineSettings,
        "ai_engine": AIEngineSettings,
        "ghg_engine": GHGEngineSettings,
    }
    
    settings_class = settings_map.get(service_name, BaseServiceSettings)
    return settings_class()