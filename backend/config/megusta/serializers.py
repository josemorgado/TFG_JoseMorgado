from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import MeGusta


class MeGustaSerializer(serializers.ModelSerializer):
    """
    Serializador del modelo MeGusta.
    Valida la correspondencia entre `content_type` y `object_id`,
    y expone una representación legible del objeto asociado.
    """

    content_object_text = serializers.SerializerMethodField(
        read_only=True,
        help_text="Representación textual del objeto al que se dio 'me gusta'."
    )

    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        help_text="ContentType del objeto asociado (p. ej.: quejas.queja o comentario.comentario)."
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
        read_only_fields = ['id', 'fecha_creacion','autor']
        extra_kwargs = {
            "object_id": {
                "help_text": "ID del objeto (queja/comentario) dentro del modelo especificado."
            },
            "autor": {
                "help_text": "Usuario que realiza el 'me gusta'."
            }
        }

    def get_content_object_text(self, obj):
        """Devuelve un texto representando el objeto asociado."""
        return str(obj.content_object) if obj.content_object else None

    def validate(self, attrs):
        """
        Valida que:
        - content_type sea válido y apunte a un modelo real
        - object_id exista dentro del modelo indicado
        """

        ct = attrs.get('content_type')
        object_id = attrs.get('object_id')

        # Validación ContentType
        model_cls = ct.model_class() if ct else None
        if not model_cls:
            raise serializers.ValidationError({'content_type': 'ContentType inválido.'})

        # Validación object_id
        if object_id is None:
            raise serializers.ValidationError({'object_id': 'Debe indicar un objeto válido.'})

        if not model_cls.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError(
                {'object_id': 'El objeto asociado no existe para ese ContentType.'}
            )

        return attrs