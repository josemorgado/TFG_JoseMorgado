# respuesta/serializers.py
from rest_framework import serializers
from .models import Respuesta

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = '__all__'
        read_only_fields = ('id', 'moderador', 'queja', 'fecha_respuesta', 'fecha_actualizacion')