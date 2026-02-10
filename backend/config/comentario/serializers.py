from rest_framework import serializers
from .models import Comentario

class ComentarioSerializer(serializers.ModelSerializer):
    num_votos = serializers.ReadOnlyField()

    class Meta:
        model = Comentario
        fields = [
            'id',
            'queja',
            'autor',
            'contenido',
            'fecha_creacion',
            'num_votos',
            'parent',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'num_votos']