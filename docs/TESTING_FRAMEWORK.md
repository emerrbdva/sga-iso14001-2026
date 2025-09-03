# Testing Framework Setup for SGA ISO 14001:2026

## Configuración de Testing

Para implementar un framework de testing robusto, se recomienda:

### 1. Estructura de Directorios de Tests

```
tests/
├── unit/
│   ├── test_core_sga/
│   ├── test_ai_engine/
│   ├── test_reporting_engine/
│   └── shared/
├── integration/
│   ├── test_api_endpoints/
│   └── test_service_communication/
├── e2e/
│   └── test_workflows/
├── conftest.py
└── requirements.txt
```

### 2. Dependencias Recomendadas

```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
httpx>=0.24.0
testcontainers>=3.7.0
factory-boy>=3.2.0
faker>=18.0.0
```

### 3. Configuración Base (conftest.py)

```python
import pytest
import asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_models.config import BaseServiceSettings

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture
def test_settings(postgres_container):
    class TestSettings(BaseServiceSettings):
        database_url: str = postgres_container.get_connection_url()
        log_level: str = "DEBUG"
    return TestSettings()

@pytest.fixture
def db_session(test_settings):
    engine = create_engine(test_settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
```

### 4. Tests de Ejemplo

#### Test Unitario (test_core_sga/test_crud.py)
```python
def test_create_environmental_aspect(db_session):
    from services.core_sga.app import crud
    from shared_models.models.environmental_entities import EnvironmentalAspectCreate
    
    aspect_data = EnvironmentalAspectCreate(
        name="Test Aspect",
        description="Test description",
        aspect_type="Emisión"
    )
    
    aspect = crud.create_aspect(db_session, aspect_data)
    assert aspect.name == "Test Aspect"
    assert aspect.id is not None
```

#### Test de Integración (test_api_endpoints/test_core_sga.py)
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_aspect_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/aspects", json={
            "name": "Test Aspect",
            "description": "Test description"
        })
    assert response.status_code == 201
```

### 5. Comandos de Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=services --cov=shared_models

# Solo tests unitarios
pytest tests/unit/

# Tests específicos
pytest tests/unit/test_core_sga/

# Tests en paralelo
pytest -n auto
```

### 6. CI/CD Integration

Para GitHub Actions, crear `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r tests/requirements.txt
      - run: pytest --cov --cov-report=xml
```

### 7. Mocking para Tests

```python
# test_ai_integration.py
from unittest.mock import patch, Mock

@patch('shared_models.http_client.SyncRobustHTTPClient.post')
def test_ai_classification_with_mock(mock_post):
    mock_post.return_value = {
        "suggested_category": "Emisión",
        "confidence_score": 0.95
    }
    
    # Test logic here
```

### 8. Factory Pattern para Datos de Test

```python
# factories.py
import factory
from shared_models.models.environmental_entities import EnvironmentalAspectCreate

class EnvironmentalAspectFactory(factory.Factory):
    class Meta:
        model = EnvironmentalAspectCreate
    
    name = factory.Faker('company')
    description = factory.Faker('text')
    aspect_type = factory.Faker('random_element', 
                               elements=['Emisión', 'Consumo', 'Generación de Residuo'])
```

## Próximos Pasos

1. Crear la estructura de directorios de tests
2. Instalar dependencias de testing
3. Implementar tests básicos para funciones críticas
4. Configurar CI/CD pipeline
5. Añadir tests de cobertura mínima (>80%)
6. Implementar tests de carga para APIs críticas