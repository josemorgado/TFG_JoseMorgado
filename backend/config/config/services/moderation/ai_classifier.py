TOXICITY_THRESHOLD = 0.5

# Cache global del clasificador (singleton)
_toxicity_classifier = None


def _get_toxicity_classifier():
    """
    Devuelve el clasificador de toxicidad.
    Se carga solo la PRIMERA vez que se necesita.
    """
    global _toxicity_classifier

    if _toxicity_classifier is None:
        # IMPORTS PESADOS SOLO AQUÍ
        print("⚠️ CARGANDO MODELO DE TOXICIDAD...")
        from transformers import pipeline

        _toxicity_classifier = pipeline(
            task="text-classification",
            model="unitary/multilingual-toxic-xlm-roberta",
            truncation=True
        )

    return _toxicity_classifier


def es_contenido_toxico(text: str) -> bool:
    """
    Analiza el texto y devuelve True si se considera tóxico.
    """
    if not text or not text.strip():
        return False

    classifier = _get_toxicity_classifier()

    resultado = classifier(text)
    if not resultado:
        return False

    prediccion = resultado[0]
    etiqueta = prediccion.get("label", "").lower()
    score = prediccion.get("score", 0.0)

    return etiqueta == "toxic" and score >= TOXICITY_THRESHOLD