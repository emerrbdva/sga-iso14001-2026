import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Leemos la URL de conexión desde las variables de entorno que definimos en docker-compose.yml
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Creamos el "motor" de SQLAlchemy que se conectará a PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Creamos una fábrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creamos una clase Base de la cual heredarán nuestros modelos de tabla (ORM models)
Base = declarative_base()

# --- Dependencia para la API ---
def get_db():
    """
    Esta función es una dependencia de FastAPI. Se encarga de:
    1. Crear una nueva sesión de BD para cada petición a la API.
    2. Entregar la sesión al endpoint.
    3. Asegurarse de que la sesión se cierre siempre al finalizar, incluso si hay un error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()