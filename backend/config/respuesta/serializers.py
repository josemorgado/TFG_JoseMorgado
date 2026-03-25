# respuesta/serializers.py
from rest_framework import serializers
from .models import Respuesta

class RespuestaSerializer(serializers.ModelSerializer):
    moderador_username = serializers.CharField(
        source='moderador.username',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Respuesta
        fields = '__all__'
        read_only_fields = ('id', 'moderador', 'queja', 'fecha_respuesta', 'fecha_actualizacion')


class RespuestasOverviewSerializer(serializers.Serializer):
    tiempo_medio_primera = serializers.FloatField()  # segundos
    media_respuestas_por_queja = serializers.FloatField()
    total_quejas_respondidas = serializers.IntegerField()

class RespuestasRankingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    total = serializers.IntegerField()