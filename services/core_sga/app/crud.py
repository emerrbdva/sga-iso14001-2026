import requests
from sqlalchemy.orm import Session
from . import models
from shared_models.models import environmental_entities as schemas
from shared_models.models.environmental_entities import AspectType
from shared_models.config import get_settings
from shared_models.logging_utils import setup_logger, log_api_call, log_database_operation, log_business_event
from shared_models.http_client import create_http_client, ServiceError

# Configuración y logging
settings = get_settings("core_sga")
logger = setup_logger("core_sga", settings.log_level)

# Cliente HTTP para comunicación con otros servicios
ai_client = create_http_client("ai_engine", settings.ai_service_url)

# --- CRUD para Política Ambiental ---
def get_policy(db: Session) -> models.EnvironmentalPolicy | None:
    logger.info("Retrieving environmental policy")
    try:
        policy = db.query(models.EnvironmentalPolicy).first()
        log_database_operation(logger, "READ", "environmental_policies", 
                             record_id=str(policy.id) if policy else None)
        return policy
    except Exception as e:
        logger.error("Failed to retrieve environmental policy", error=str(e))
        raise

def update_policy(db: Session, policy_data: schemas.EnvironmentalPolicyCreate) -> models.EnvironmentalPolicy:
    logger.info("Updating environmental policy")
    try:
        db_policy = get_policy(db)
        if not db_policy:
            db_policy = models.EnvironmentalPolicy(**policy_data.dict())
            db.add(db_policy)
            operation = "CREATE"
        else:
            for key, value in policy_data.dict().items():
                setattr(db_policy, key, value)
            operation = "UPDATE"
            
        db.commit()
        db.refresh(db_policy)
        
        log_database_operation(logger, operation, "environmental_policies", 
                             record_id=str(db_policy.id))
        log_business_event(logger, "policy_updated", 
                         f"Environmental policy {operation.lower()}d",
                         policy_id=db_policy.id)
        
        return db_policy
    except Exception as e:
        db.rollback()
        logger.error("Failed to update environmental policy", error=str(e))
        raise

# --- CRUD para Aspectos Ambientales (CON INTEGRACIÓN DE IA) ---
from sqlalchemy.orm import Session, joinedload
# ... (otras importaciones)

def get_aspect(db: Session, aspect_id: int):
    logger.info("Retrieving environmental aspect", aspect_id=aspect_id)
    try:
        # CAMBIO: Añadimos joinedload para cargar riesgos y obligaciones
        aspect = db.query(models.EnvironmentalAspect).options(
            joinedload(models.EnvironmentalAspect.risks),
            joinedload(models.EnvironmentalAspect.obligations)
        ).filter(models.EnvironmentalAspect.id == aspect_id).first()
        
        log_database_operation(logger, "READ", "environmental_aspects", 
                             record_id=str(aspect_id))
        return aspect
    except Exception as e:
        logger.error("Failed to retrieve environmental aspect", 
                    aspect_id=aspect_id, error=str(e))
        raise

def get_aspects(db: Session, skip: int = 0, limit: int = 100):
    logger.info("Retrieving environmental aspects list", skip=skip, limit=limit)
    try:
        # CAMBIO: Añadimos joinedload aquí también
        aspects = db.query(models.EnvironmentalAspect).options(
            joinedload(models.EnvironmentalAspect.risks),
            joinedload(models.EnvironmentalAspect.obligations)
        ).offset(skip).limit(limit).all()
        
        log_database_operation(logger, "READ", "environmental_aspects", 
                             record_count=len(aspects))
        return aspects
    except Exception as e:
        logger.error("Failed to retrieve environmental aspects", 
                    skip=skip, limit=limit, error=str(e))
        raise

def create_aspect(db: Session, aspect: schemas.EnvironmentalAspectCreate) -> models.EnvironmentalAspect:
    logger.info("Creating environmental aspect", aspect_name=aspect.name)
    
    # Intentar clasificación con IA si está habilitada
    if settings.enable_ai_classification:
        try:
            ai_response = ai_client.post(
                "/analyze/aspect_type",
                json_data={"text": aspect.description}
            )
            
            suggested_type_str = ai_response.get("suggested_category")
            confidence = ai_response.get("confidence_score", 0)
            
            logger.info("AI classification completed", 
                       suggested_type=suggested_type_str,
                       confidence=confidence,
                       aspect_name=aspect.name)
            
            # Solo usar la sugerencia si la confianza es alta
            if (suggested_type_str in [item.value for item in schemas.AspectType] 
                and confidence > 0.7):
                aspect.aspect_type = schemas.AspectType(suggested_type_str)
                logger.info("AI classification applied", 
                           original_type=aspect.aspect_type,
                           suggested_type=suggested_type_str)
        
        except ServiceError as e:
            logger.warning("AI service unavailable, using original classification", 
                         error=str(e), aspect_name=aspect.name)
        except Exception as e:
            logger.error("Unexpected error in AI classification", 
                        error=str(e), aspect_name=aspect.name)

    try:
        db_aspect = models.EnvironmentalAspect(**aspect.dict())
        db.add(db_aspect)
        db.commit()
        db.refresh(db_aspect)
        
        log_database_operation(logger, "CREATE", "environmental_aspects", 
                             record_id=str(db_aspect.id))
        log_business_event(logger, "aspect_created", 
                         f"Environmental aspect '{db_aspect.name}' created",
                         aspect_id=db_aspect.id,
                         aspect_type=db_aspect.aspect_type.value if db_aspect.aspect_type else None)
        
        return db_aspect
    
    except Exception as e:
        db.rollback()
        logger.error("Failed to create environmental aspect", 
                    aspect_name=aspect.name, error=str(e))
        raise