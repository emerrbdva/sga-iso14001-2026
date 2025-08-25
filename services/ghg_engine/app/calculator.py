from typing import List
from . import models

def calculate_emissions(activity_data_list: List[models.ActivityData]) -> dict:
    """
    Calcula las emisiones totales de GEI a partir de una lista de datos de actividad.
    """
    inventory = {
        "total_co2e": 0.0,
        "emissions_by_scope": {
            "Alcance 1": 0.0,
            "Alcance 2": 0.0,
            "Alcance 3": 0.0,
        }
    }
    
    for activity in activity_data_list:
        if activity.source and activity.source.factor:
            # Fórmula: Emisiones = Dato de Actividad * Factor de Emisión
            co2e = activity.value * activity.source.factor.value
            
            # Sumar al total
            inventory["total_co2e"] += co2e
            
            # Sumar al alcance correspondiente
            scope = activity.source.scope.value
            if scope in inventory["emissions_by_scope"]:
                inventory["emissions_by_scope"][scope] += co2e
                
    return inventory