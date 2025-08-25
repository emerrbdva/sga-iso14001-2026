from transformers import pipeline
from shared_models.models.environmental_entities import AspectType

class AspectClassifier:
    """
    Esta clase carga un modelo de NLP y lo utiliza para clasificar
    descripciones de aspectos ambientales.
    """
    def __init__(self):
        # Cargamos el pipeline de "zero-shot-classification".
        # Esto descarga un modelo pre-entrenado la primera vez que se ejecuta.
        # El modelo solo se carga una vez al iniciar el servicio, lo que es muy eficiente.
        print("Cargando el modelo de IA. Esto puede tardar un momento...")
        self.classifier = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )
        print("Modelo de IA cargado exitosamente.")

    def classify(self, text_to_analyze: str) -> dict:
        """
        Clasifica un texto dado en las categorías de AspectType.
        
        Zero-shot significa que podemos darle las etiquetas de clasificación
        en el momento, sin necesidad de re-entrenar el modelo.
        """
        # Obtenemos las posibles etiquetas de nuestro modelo compartido
        candidate_labels = [e.value for e in AspectType]
        
        # El modelo devuelve las etiquetas ordenadas por probabilidad
        result = self.classifier(text_to_analyze, candidate_labels)
        
        return {
            "suggested_category": result['labels'][0],
            "confidence_score": result['scores'][0]
        }

# Creamos una única instancia global del clasificador para toda la aplicación
classifier = AspectClassifier()