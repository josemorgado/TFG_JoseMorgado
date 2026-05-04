# video/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Video, MAX_VIDEOS


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializador del modelo Video.
    Incluye validación de ContentType + object_id, límite de videos por objeto,
    y expone una representación legible del objeto asociado.
    """

    content_object_text = serializers.SerializerMethodField(
        read_only=True,
        help_text="Representación textual del objeto al que pertenece este video."
    )

    video_url = serializers.SerializerMethodField(
        read_only=True,
        help_text="URL absoluta pública del video."
    )

    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        help_text="ContentType del objeto asociado."
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'content_type',
            'object_id',
            'video',        # campo original (ruta relativa)
            'video_url',    # ✅ URL ABSOLUTA
            'orden',
            'fecha_creacion',
            'content_object_text',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'orden']
        extra_kwargs = {
            "object_id": {"help_text": "ID del objeto dentro del modelo especificado."},
            "video": {"help_text": "Archivo de video enviado vía multipart/form-data."},
            "orden": {"help_text": "Orden del video dentro del conjunto."},
        }

    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None

    def get_video_url(self, obj):
        """
        Devuelve la URL absoluta del video
        (http://localhost:8000/media/...)
        """
        request = self.context.get("request")
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        return None

    def validate(self, attrs):
        ct = attrs.get('content_type') or getattr(self.instance, 'content_type', None)
        object_id = attrs.get('object_id') or getattr(self.instance, 'object_id', None)

        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        if object_id is None or not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe.'})

        creating = self.instance is None
        changing_ref = (
            not creating
            and (ct != self.instance.content_type or object_id != self.instance.object_id)
        )

        if creating or changing_ref:
            total = Video.objects.filter(content_type=ct, object_id=object_id).count()
            if total >= MAX_VIDEOS:
                raise serializers.ValidationError(
                    f'Solo se permite un máximo de {MAX_VIDEOS} video por objeto.'
                )

        return attrs

    def validate_video(self, value):
        if value is None:
            raise serializers.ValidationError("Debe proporcionar un archivo de video.")
        return value