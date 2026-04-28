"""
Servicio de moderación de texto.

Aplica:
- Filtro léxico (siempre)
- IA de toxicidad SOLO si está habilitada por entorno
"""

from django.conf import settings
from rest_framework import serializers
from .lexical_filter import contiene_lenguaje_ofensivo


def moderate_text(text: str):
    if contiene_lenguaje_ofensivo(text):
        raise serializers.ValidationError(
            "La queja contiene lenguaje ofensivo o inapropiado."
        )

    if settings.ENABLE_AI_MODERATION:
        from .ai_classifier import es_contenido_toxico

        if es_contenido_toxico(text):
            raise serializers.ValidationError(
                "El contenido puede considerarse ofensivo o inapropiado."
            )