from transformers import pipeline

TOXICITY_THRESHOLD = 0.5

_toxicity_classifier = pipeline(
    task="text-classification",
    model="unitary/multilingual-toxic-xlm-roberta",
    truncation=True
)

def es_contenido_toxico(text: str) -> bool:
    """Analiza el texto y devuelve True si se considera tóxico"""
    if not text or not text.strip():
        return False

    resultado = _toxicity_classifier(text)
    if not resultado:
        return False

    prediccion = resultado[0]
    etiqueta = prediccion.get("label", "").lower()
    score = prediccion.get("score", 0.0)

    return etiqueta == "toxic" and score >= TOXICITY_THRESHOLD
