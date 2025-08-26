import requests
from sqlalchemy.orm import Session
from . import models
from shared_models.models import environmental_entities as schemas
from shared_models.models.environmental_entities import AspectType

# --- CRUD para Política Ambiental ---
def get_policy(db: Session) -> models.EnvironmentalPolicy | None:
    return db.query(models.EnvironmentalPolicy).first()

def update_policy(db: Session, policy_data: schemas.EnvironmentalPolicyCreate) -> models.EnvironmentalPolicy:
    db_policy = get_policy(db)
    if not db_policy:
        db_policy = models.EnvironmentalPolicy(**policy_data.dict())
        db.add(db_policy)
    else:
        for key, value in policy_data.dict().items():
            setattr(db_policy, key, value)
    db.commit()
    db.refresh(db_policy)
    return db_policy

# --- CRUD para Aspectos Ambientales (CON INTEGRACIÓN DE IA) ---
from sqlalchemy.orm import Session, joinedload
# ... (otras importaciones)

def get_aspect(db: Session, aspect_id: int):
    # CAMBIO: Añadimos joinedload para cargar riesgos y obligaciones
    return db.query(models.EnvironmentalAspect).options(
        joinedload(models.EnvironmentalAspect.risks),
        joinedload(models.EnvironmentalAspect.obligations)
    ).filter(models.EnvironmentalAspect.id == aspect_id).first()

def get_aspects(db: Session, skip: int = 0, limit: int = 100):
    # CAMBIO: Añadimos joinedload aquí también
    return db.query(models.EnvironmentalAspect).options(
        joinedload(models.EnvironmentalAspect.risks),
        joinedload(models.EnvironmentalAspect.obligations)
    ).offset(skip).limit(limit).all()

def create_aspect(db: Session, aspect: schemas.EnvironmentalAspectCreate) -> models.EnvironmentalAspect:
    AI_SERVICE_URL = "http://ai-engine-api:8001/api/v1/analyze/aspect_type"
    try:
        response = requests.post(AI_SERVICE_URL, json={"text": aspect.description}, timeout=5)
        if response.status_code == 200:
            ai_data = response.json()
            suggested_type_str = ai_data.get("suggested_category")
            if suggested_type_str in [item.value for item in schemas.AspectType]:
                aspect.aspect_type = schemas.AspectType(suggested_type_str)
    except requests.exceptions.RequestException as e:
        print(f"Advertencia: No se pudo conectar con el servicio de IA. Se usará el valor original. Error: {e}")

    db_aspect = models.EnvironmentalAspect(**aspect.dict())
    db.add(db_aspect)
    db.commit()
    db.refresh(db_aspect)
    return db_aspect