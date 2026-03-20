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