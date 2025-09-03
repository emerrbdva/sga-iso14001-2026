"""
Sistema de logging centralizado para SGA ISO 14001:2026
"""
import logging
import sys
from typing import Optional
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Formateador personalizado para logs en formato JSON"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": getattr(record, 'service', 'unknown'),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Añadir información adicional si está disponible
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
            
        if hasattr(record, 'aspect_id'):
            log_entry["aspect_id"] = record.aspect_id
            
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(
    service_name: str,
    log_level: str = "INFO",
    log_format: str = "json"
) -> logging.Logger:
    """
    Configura y retorna un logger estandarizado para el servicio
    
    Args:
        service_name: Nombre del servicio (ej: "core_sga", "ai_engine")
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato del log ("json" o "text")
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(service_name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Crear handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Crear un adapter personalizado para incluir el nombre del servicio
    class ServiceAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return msg, kwargs
            
        def debug(self, msg, **kwargs):
            self.logger.debug(msg, extra={"service": service_name, **kwargs})
            
        def info(self, msg, **kwargs):
            self.logger.info(msg, extra={"service": service_name, **kwargs})
            
        def warning(self, msg, **kwargs):
            self.logger.warning(msg, extra={"service": service_name, **kwargs})
            
        def error(self, msg, **kwargs):
            self.logger.error(msg, extra={"service": service_name, **kwargs})
            
        def critical(self, msg, **kwargs):
            self.logger.critical(msg, extra={"service": service_name, **kwargs})
    
    return ServiceAdapter(logger, {})


def log_api_call(
    logger,
    method: str,
    url: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    **extra_fields
):
    """
    Registra una llamada a API de manera estandarizada
    
    Args:
        logger: Logger configurado
        method: Método HTTP (GET, POST, etc.)
        url: URL de la llamada
        status_code: Código de respuesta HTTP
        duration_ms: Duración en milisegundos
        **extra_fields: Campos adicionales para el log
    """
    log_data = {
        "api_method": method,
        "api_url": url,
        **extra_fields
    }
    
    if status_code:
        log_data["status_code"] = status_code
        
    if duration_ms:
        log_data["duration_ms"] = duration_ms
    
    if status_code and status_code >= 400:
        logger.error(f"API call failed: {method} {url}", **log_data)
    else:
        logger.info(f"API call: {method} {url}", **log_data)


def log_database_operation(
    logger,
    operation: str,
    table: str,
    record_id: Optional[str] = None,
    duration_ms: Optional[float] = None,
    **extra_fields
):
    """
    Registra una operación de base de datos de manera estandarizada
    
    Args:
        logger: Logger configurado
        operation: Tipo de operación (CREATE, READ, UPDATE, DELETE)
        table: Nombre de la tabla
        record_id: ID del registro afectado
        duration_ms: Duración en milisegundos
        **extra_fields: Campos adicionales para el log
    """
    log_data = {
        "db_operation": operation,
        "db_table": table,
        **extra_fields
    }
    
    if record_id:
        log_data["record_id"] = record_id
        
    if duration_ms:
        log_data["duration_ms"] = duration_ms
    
    logger.info(f"Database {operation}: {table}", **log_data)


def log_business_event(
    logger,
    event_type: str,
    description: str,
    **extra_fields
):
    """
    Registra un evento de negocio importante
    
    Args:
        logger: Logger configurado
        event_type: Tipo de evento (ej: "aspect_created", "audit_completed")
        description: Descripción del evento
        **extra_fields: Campos adicionales para el log
    """
    log_data = {
        "event_type": event_type,
        **extra_fields
    }
    
    logger.info(f"Business event: {description}", **log_data)