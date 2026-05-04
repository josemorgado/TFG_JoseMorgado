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

    imagen_url = serializers.SerializerMethodField(
        read_only=True,
        help_text="URL absoluta pública de la imagen."
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
            'imagen',        # campo original (ruta relativa)
            'imagen_url',    # ✅ URL ABSOLUTA
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

    def get_imagen_url(self, obj):
        """
        Devuelve la URL absoluta de la imagen
        (http://localhost:8000/media/...)
        """
        request = self.context.get("request")
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None

    def validate(self, attrs):
        """
        Validaciones de content_type y object_id.
        """
        ct = attrs.get('content_type')
        object_id = attrs.get('object_id')

        if self.instance is not None:
            ct = ct or getattr(self.instance, 'content_type', None)
            object_id = object_id if object_id is not None else getattr(self.instance, 'object_id', None)

        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        if object_id in (None, ''):
            raise serializers.ValidationError({'object_id': 'Debe indicar el identificador del objeto.'})
        if not isinstance(object_id, int) or object_id <= 0:
            raise serializers.ValidationError({'object_id': 'El identificador debe ser un entero positivo.'})
        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe.'})

        return attrs

    def validate_imagen(self, value):
        if value is None:
            raise serializers.ValidationError('Debe proporcionar un archivo de imagen.')
        return value