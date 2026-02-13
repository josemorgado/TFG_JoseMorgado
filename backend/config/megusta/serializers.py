from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import MeGusta


# Serializador para exponer y validar 'me gusta'
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

    # Devuelve un texto legible del objeto genérico asociado
    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None

    # Valida la combinación content_type + object_id
    def validate(self, attrs):
        # NOTA: validación conjunta igual que en el ejemplo de Distrito
        ct = attrs.get('content_type')
        object_id = attrs.get('object_id')

        # Validar ContentType
        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        # Validar object_id (existencia en ese modelo)
        if object_id is None:
            raise serializers.ValidationError({'object_id': 'Debe indicar un objeto válido.'})

        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError(
                {'object_id': 'El objeto asociado no existe para ese ContentType.'}
            )

        return attrs