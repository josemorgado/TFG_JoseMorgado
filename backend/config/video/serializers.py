# video/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Video, MAX_VIDEOS

class VideoSerializer(serializers.ModelSerializer):
    content_object_text = serializers.SerializerMethodField(read_only=True)

    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all()
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'content_type',
            'object_id',
            'video',
            'orden',
            'fecha_creacion',
            'content_object_text',
        ]
        # 'orden' se autogestiona en la capa de vistas
        read_only_fields = ['id', 'fecha_creacion', 'orden']

    def get_content_object_text(self, obj):
        return str(obj.content_object) if obj.content_object else None

    def validate(self, attrs):
        """
        - Valida que el ContentType sea válido.
        - Valida que el objeto asociado exista.
        - (Opcional) Pre-chequea el máximo de vídeos por objeto
          para dar un error más amigable (el modelo lo refuerza en .clean()).
        """
        ct: ContentType = attrs.get('content_type') or getattr(self.instance, 'content_type', None)
        object_id = attrs.get('object_id') or getattr(self.instance, 'object_id', None)

        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        if object_id is None or not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({'object_id': 'El objeto asociado no existe para ese content_type.'})

        # Pre-chequeo de límite (solo si se crea o si cambian las referencias)
        creating = self.instance is None
        changing_ref = (not creating) and (ct != self.instance.content_type or object_id != self.instance.object_id)
        if creating or changing_ref:
            total = Video.objects.filter(content_type=ct, object_id=object_id).count()
            if total >= MAX_VIDEOS:
                raise serializers.ValidationError({
                    'non_field_errors': [f'Solo se permiten un máximo de {MAX_VIDEOS} videos por objeto.']
                })

        return attrs