# imagen/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Imagen


class ImagenSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Imagen.
    Valida la correspondencia entre `content_type` y `object_id`,
    y expone una representación legible del objeto relacionado.
    """

    content_object_text = serializers.SerializerMethodField(
        read_only=True,
        help_text="Representación textual del objeto asociado (queja/comentario)."
    )
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        help_text="ContentType del objeto asociado (p.ej., quejas.queja o comentario.comentario)."
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
        extra_kwargs = {
            "object_id": {
                "help_text": "ID del objeto (queja/comentario) dentro del modelo indicado en content_type."
            },
            "imagen": {
                "help_text": "Archivo de imagen (multipart/form-data)."
            },
            "orden": {
                "help_text": "Posición de la imagen dentro del objeto. Se asigna automáticamente."
            }
        }

    def get_content_object_text(self, obj):
        """Devuelve el texto legible del objeto genérico asociado."""
        return str(obj.content_object) if obj.content_object else None

    def validate(self, attrs):
        """
        Valida que:
        - content_type sea válido y resoluble a un modelo.
        - object_id sea entero positivo.
        - exista un objeto con ese id para el modelo indicado.
        También soporta updates completando desde la instancia.
        """
        ct = attrs.get('content_type')
        object_id = attrs.get('object_id')

        # En update, completamos con los valores actuales si no vienen en attrs
        if self.instance is not None:
            ct = ct or getattr(self.instance, 'content_type', None)
            object_id = object_id if object_id is not None else getattr(self.instance, 'object_id', None)

        # Validación de content_type
        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        # Validación de object_id
        if object_id in (None, ''):
            raise serializers.ValidationError({'object_id': 'Debe indicar el identificador del objeto.'})
        if not isinstance(object_id, int) or object_id <= 0:
            raise serializers.ValidationError({'object_id': 'El identificador del objeto debe ser un entero positivo.'})
        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe para ese content_type.'})

        return attrs

    def validate_imagen(self, value):
        """Valida que se suministre un archivo de imagen válido."""
        if value is None:
            raise serializers.ValidationError('Debe proporcionar un archivo de imagen.')
        return value
