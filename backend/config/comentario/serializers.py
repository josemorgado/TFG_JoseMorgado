from rest_framework import serializers
from .models import Comentario

long_minima_contenido = 3


class ComentarioSerializer(serializers.ModelSerializer):
    """
    Serializador del modelo Comentario.
    Incluye validación de contenido mínimo y coherencia del hilo (parent).
    Expone también el campo calculado 'num_votos' en modo de solo lectura.
    """

    num_votos = serializers.ReadOnlyField(
        help_text="Número total de votos recibidos por este comentario."
    )

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
        read_only_fields = ['id', 'fecha_creacion', 'num_votos', 'autor']
        extra_kwargs = {
            "queja": {
                "help_text": "ID de la queja a la que pertenece este comentario."
            },
            "autor": {
                "help_text": "Usuario autor del comentario."
            },
            "contenido": {
                "help_text": f"Texto del comentario. Mínimo {long_minima_contenido} caracteres."
            },
            "parent": {
                "help_text": "Comentario padre si este es una respuesta. Debe pertenecer a la misma queja."
            }
        }

    def validate_contenido(self, value: str) -> str:
        """Valida que el contenido tenga una longitud mínima válida."""
        if value is None or not isinstance(value, str) or len(value.strip()) < long_minima_contenido:
            raise serializers.ValidationError(
                f"El contenido debe tener al menos {long_minima_contenido} caracteres."
            )
        return value.strip()

    def validate(self, attrs):
        """
        Valida coherencia entre comentario padre y la misma queja.
        - Un comentario no puede ser su propio parent.
        - El parent debe pertenecer a la misma queja.
        """
        parent = attrs.get('parent')
        queja = attrs.get('queja') or getattr(self.instance, 'queja', None)

        if parent:
            if self.instance and parent.pk == getattr(self.instance, 'pk', None):
                raise serializers.ValidationError({
                    "parent": "Un comentario no puede ser su propio padre."
                })

            if queja is not None and parent.queja_id != queja.id:
                raise serializers.ValidationError({
                    "parent": "El comentario padre debe pertenecer a la misma queja."
                })

        return attrs

    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)