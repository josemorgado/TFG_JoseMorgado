'''Se llama a lexical_filter y a ai_classifier y se clasifica el texto segun la moderation_policy'''
from .ai_classifier import es_contenido_toxico
from .lexical_filter import contiene_lenguaje_ofensivo
from rest_framework import serializers
import settings

def moderate_text(text:str):
    if not settings.ENABLE_AI_MODERATION:
        '''Clasifica el texto segun la politica de moderacion'''
        if contiene_lenguaje_ofensivo(text):
            raise serializers.ValidationError("La queja contiene lenguaje ofensivo o inapropiado.")

        if es_contenido_toxico(text):
            raise serializers.ValidationError("El contenido puede consiferarse ofensivo o inapropiado.")
        pass