from rest_framework import serializers
from .models import Comentario

long_minima_contenido = 3

class ComentarioSerializer(serializers.ModelSerializer):
    num_votos = serializers.ReadOnlyField()

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
        read_only_fields = ['id', 'fecha_creacion', 'num_votos']

    def validate_contenido(self, value: str) -> str:
        if value is None or not isinstance(value, str) or len(value.strip()) < long_minima_contenido:
            raise serializers.ValidationError(f"El contenido debe tener al menos {long_minima_contenido} caracteres.")
        return value.strip()

    # Valida coherencia del parent con la misma queja y evita autorreferencia
    def validate(self, attrs):
        # NOTA: se garantiza que el parent pertenezca a la misma queja para mantener la coherencia del hilo
        parent = attrs.get('parent')
        queja = attrs.get('queja') or getattr(self.instance, 'queja', None)

        if parent:
            if self.instance and parent.pk == getattr(self.instance, 'pk', None):
                raise serializers.ValidationError({"parent": "Un comentario no puede ser su propio padre."})

            if queja is not None and parent.queja_id != queja.id:
                raise serializers.ValidationError({"parent": "El comentario padre debe pertenecer a la misma queja."})

        return attrs