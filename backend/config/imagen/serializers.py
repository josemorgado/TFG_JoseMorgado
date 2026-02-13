# imagen/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Imagen

# Serializador para exponer y validar imágenes asociadas genéricamente.
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
        read_only_fields = ['id', 'fecha_creacion', 'orden']

    # Devuelve el texto legible del objeto genérico asociado
    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None

    # Valida que el content_type sea válido y el object_id exista para ese modelo
    def validate(self, attrs):
        # Nota: se valida en conjunto para garantizar la correspondencia CT + object_id
        ct = attrs.get('content_type')
        object_id = attrs.get('object_id')

        # Si es update, completar con valores de instancia cuando falten en attrs
        if self.instance is not None:
            ct = ct or getattr(self.instance, 'content_type', None)
            object_id = object_id if object_id is not None else getattr(self.instance, 'object_id', None)

        # Validación de content_type
        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        # Validación de object_id (entero positivo y existencia)
        if object_id in (None, ''):
            raise serializers.ValidationError({'object_id': 'Debe indicar el identificador del objeto.'})
        if not isinstance(object_id, int) or object_id <= 0:
            raise serializers.ValidationError({'object_id': 'El identificador del objeto debe ser un entero positivo.'})
        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe para ese content_type.'})

        return attrs

    # Valida que se suministre un archivo de imagen válido
    def validate_imagen(self, value):
        # Nota: DRF y el campo ImageField ya validan el archivo; se añade mensaje claro
        if value is None:
            raise serializers.ValidationError('Debe proporcionar un archivo de imagen.')
        return value