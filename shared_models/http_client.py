"""
Cliente HTTP robusto para comunicación entre microservicios
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from contextlib import asynccontextmanager
import time
from shared_models.logging_utils import setup_logger


class ServiceError(Exception):
    """Excepción base para errores de comunicación entre servicios"""
    pass


class ServiceUnavailableError(ServiceError):
    """El servicio no está disponible"""
    pass


class ServiceTimeoutError(ServiceError):
    """Timeout en la comunicación con el servicio"""
    pass


class ServiceBadRequestError(ServiceError):
    """Error en la petición (4xx)"""
    pass


class ServiceInternalError(ServiceError):
    """Error interno del servicio (5xx)"""
    pass


class RobustHTTPClient:
    """
    Cliente HTTP robusto con retry automático, circuit breaker básico y logging
    """
    
    def __init__(
        self,
        service_name: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_wait_min: int = 1,
        retry_wait_max: int = 10
    ):
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_wait_min = retry_wait_min
        self.retry_wait_max = retry_wait_max
        self.logger = setup_logger(f"http_client_{service_name}")
        
        # Circuit breaker básico
        self.failure_count = 0
        self.last_failure_time = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60  # segundos
    
    def _is_circuit_open(self) -> bool:
        """Verifica si el circuit breaker está abierto"""
        if self.failure_count >= self.circuit_breaker_threshold:
            if time.time() - self.last_failure_time < self.circuit_breaker_timeout:
                return True
            else:
                # Reset del circuit breaker después del timeout
                self.failure_count = 0
        return False
    
    def _on_success(self):
        """Callback para cuando una petición es exitosa"""
        if self.failure_count > 0:
            self.logger.info(f"Service {self.service_name} recovered", 
                           failure_count=self.failure_count)
        self.failure_count = 0
    
    def _on_failure(self):
        """Callback para cuando una petición falla"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.circuit_breaker_threshold:
            self.logger.error(f"Circuit breaker opened for {self.service_name}",
                            failure_count=self.failure_count)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Realiza la petición HTTP con retry automático"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            start_time = time.time()
            
            try:
                response = await client.request(method, url, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log de la petición
                from shared_models.logging_utils import log_api_call
                log_api_call(
                    self.logger,
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    service=self.service_name
                )
                
                # Manejo de errores HTTP
                if response.status_code >= 500:
                    self._on_failure()
                    raise ServiceInternalError(
                        f"Internal error from {self.service_name}: {response.status_code}"
                    )
                elif response.status_code >= 400:
                    raise ServiceBadRequestError(
                        f"Bad request to {self.service_name}: {response.status_code} - {response.text}"
                    )
                
                self._on_success()
                return response
                
            except httpx.TimeoutException:
                self._on_failure()
                raise ServiceTimeoutError(f"Timeout connecting to {self.service_name}")
            except httpx.ConnectError:
                self._on_failure()
                raise ServiceUnavailableError(f"Cannot connect to {self.service_name}")
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Realiza una petición GET"""
        if self._is_circuit_open():
            raise ServiceUnavailableError(f"Circuit breaker open for {self.service_name}")
        
        response = await self._make_request("GET", endpoint, params=params, **kwargs)
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Realiza una petición POST"""
        if self._is_circuit_open():
            raise ServiceUnavailableError(f"Circuit breaker open for {self.service_name}")
        
        request_kwargs = kwargs
        if json_data is not None:
            request_kwargs["json"] = json_data
        if data is not None:
            request_kwargs["data"] = data
            
        response = await self._make_request("POST", endpoint, **request_kwargs)
        return response.json()
    
    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Realiza una petición PUT"""
        if self._is_circuit_open():
            raise ServiceUnavailableError(f"Circuit breaker open for {self.service_name}")
        
        response = await self._make_request("PUT", endpoint, json=json_data, **kwargs)
        return response.json()
    
    async def delete(
        self,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Realiza una petición DELETE"""
        if self._is_circuit_open():
            raise ServiceUnavailableError(f"Circuit breaker open for {self.service_name}")
        
        response = await self._make_request("DELETE", endpoint, **kwargs)
        return response.json() if response.content else {}


# Versión síncrona para compatibilidad con código existente
class SyncRobustHTTPClient:
    """Versión síncrona del cliente HTTP robusto"""
    
    def __init__(self, service_name: str, base_url: str, **kwargs):
        self.async_client = RobustHTTPClient(service_name, base_url, **kwargs)
    
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición GET síncrona"""
        return asyncio.run(self.async_client.get(endpoint, **kwargs))
    
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición POST síncrona"""
        return asyncio.run(self.async_client.post(endpoint, **kwargs))
    
    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición PUT síncrona"""
        return asyncio.run(self.async_client.put(endpoint, **kwargs))
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición DELETE síncrona"""
        return asyncio.run(self.async_client.delete(endpoint, **kwargs))


# Factory function para crear clientes HTTP
def create_http_client(
    service_name: str,
    base_url: str,
    async_client: bool = False,
    **kwargs
) -> Union[RobustHTTPClient, SyncRobustHTTPClient]:
    """
    Crea un cliente HTTP robusto
    
    Args:
        service_name: Nombre del servicio destino
        base_url: URL base del servicio
        async_client: Si True, retorna cliente asíncrono
        **kwargs: Argumentos adicionales para el cliente
    
    Returns:
        Cliente HTTP configurado
    """
    if async_client:
        return RobustHTTPClient(service_name, base_url, **kwargs)
    else:
        return SyncRobustHTTPClient(service_name, base_url, **kwargs)