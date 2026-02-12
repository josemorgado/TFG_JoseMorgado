from rest_framework import serializers
from categoria.models import Categoria

long_minima_nombre = 3
long_minima_descripcion = 10

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo']

    def validate_nombre(self, value):
        # Valida longitud mínima del nombre para evitar registros demasiado genéricos.
        if len(value) < long_minima_nombre:
            raise serializers.ValidationError(
                f"El nombre debe tener al menos {long_minima_nombre} caracteres."
            )
        return value

    def validate_descripcion(self, value):
        # Valida longitud mínima de la descripción para asegurar un nivel básico de detalle.
        if len(value) < long_minima_descripcion:
            raise serializers.ValidationError(
                f"La descripción debe tener al menos {long_minima_descripcion} caracteres."
            )
        return value