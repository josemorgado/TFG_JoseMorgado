from django.conf import settings
from rest_framework import serializers
from .lexical_filter import contiene_lenguaje_ofensivo

MIN_AI_LENGTH = 10


def moderate_text(text: str):
    if not text or not text.strip():
        return

    if contiene_lenguaje_ofensivo(text):
        raise serializers.ValidationError({
            "moderation": "La queja contiene lenguaje ofensivo o inapropiado."
        })

    if settings.ENABLE_AI_MODERATION and len(text) >= MIN_AI_LENGTH:
        from .ai_classifier import es_contenido_toxico

        if es_contenido_toxico(text):
            raise serializers.ValidationError({
                "toxicity": "El contenido ha sido clasificado como tóxico."
            })