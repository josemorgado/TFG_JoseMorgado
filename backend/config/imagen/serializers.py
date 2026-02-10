# imagen/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Imagen

class ImagenSerializer(serializers.ModelSerializer):
    
    content_object_text = serializers.SerializerMethodField(read_only=True)

    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )
    class Meta:
        model = Imagen
        fields = [
            'id',
            'content_type',
            'object_id',
            'imagen',
            'orden',
            'fecha_creacion',
            'content_object_text',
        ]
        read_only_fields = ['id', 'fecha_creacion','orden']

    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None
    