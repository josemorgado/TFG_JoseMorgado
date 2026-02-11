# megusta/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import MeGusta

class MeGustaSerializer(serializers.ModelSerializer):

    content_object_text = serializers.SerializerMethodField(read_only=True)

    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )

    class Meta:
        model = MeGusta
        fields = [
            'id',
            'content_type',
            'object_id',
            'autor',
            'fecha_creacion',
            'content_object_text',
        ]
        read_only_fields = ['id', 'fecha_creacion']

    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None

    def validate(self, attrs):
        ct: ContentType = attrs.get('content_type')
        object_id = attrs.get('object_id')

        # Validar ContentType
        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        # Validar existencia de la instancia asociada
        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe para ese content_type.'})

        return attrs