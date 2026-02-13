from rest_framework import serializers
from distrito.models import Distrito, long_minima_codigo, long_minima_nombre, long_max_codigo, long_max_nombre

# Serializador para exponer y validar distritos.
class DistritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distrito
        fields = ['id', 'nombre', 'codigo']
        read_only_fields = ['id']

    # Valida y normaliza el nombre (longitud mínima, no vacío visual).
    def validate_nombre(self, value: str) -> str:
        # NOTA: se evita basura y se respeta el límite del modelo.
        if value is None or not isinstance(value, str):
            raise serializers.ValidationError("El nombre es obligatorio.")
        limpio = value.strip()
        if len(limpio) < long_minima_nombre:
            raise serializers.ValidationError(f"El nombre debe tener al menos {long_minima_nombre} caracteres.")
        if len(limpio) > long_max_nombre:
            raise serializers.ValidationError(f"El nombre no puede tener más de {long_max_nombre} caracteres.")
        return limpio

    # Valida y normaliza el código (upper-case y sin espacios).
    def validate_codigo(self, value: str) -> str:
        # NOTA: se estandariza a mayúsculas para evitar duplicados por casing.
        if value is None or not isinstance(value, str):
            raise serializers.ValidationError("El código es obligatorio.")
        limpio = value.strip()
        if len(limpio) < long_minima_codigo:
            raise serializers.ValidationError(f"El código debe tener al menos {long_minima_codigo} caracteres.")

        if len(limpio) > long_max_codigo:
            raise serializers.ValidationError(f"El código no puede tener más de {long_max_codigo} caracteres.")
        if " " in limpio:
            raise serializers.ValidationError("El código no puede contener espacios.")
        import re
        if not re.match(r"^[A-Za-z0-9_-]+$", limpio):
            raise serializers.ValidationError(
                "El código solo puede contener letras, números, guión y guión bajo."
            )
        return limpio.upper()
