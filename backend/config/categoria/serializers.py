from rest_framework import serializers
from categoria.models import Categoria

long_minima_nombre = 3
long_minima_descripcion = 10


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Categoría.
    Proporciona validaciones adicionales para evitar nombres y descripciones demasiado cortas.
    """

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo']
        extra_kwargs = {
            "nombre": {
                "help_text": "Nombre visible de la categoría. Mínimo 3 caracteres."
            },
            "descripcion": {
                "help_text": "Descripción detallada de la categoría. Mínimo 10 caracteres."
            },
            "activo": {
                "help_text": "Indica si la categoría está activa."
            }
        }

    def validate_nombre(self, value):
        """Valida que el nombre tenga una longitud mínima adecuada."""
        if len(value) < long_minima_nombre:
            raise serializers.ValidationError(
                f"El nombre debe tener al menos {long_minima_nombre} caracteres."
            )
        return value

    def validate_descripcion(self, value):
        """Valida que la descripción tenga suficiente detalle."""
        if len(value) < long_minima_descripcion:
            raise serializers.ValidationError(
                f"La descripción debe tener al menos {long_minima_descripcion} caracteres."
            )
        return value