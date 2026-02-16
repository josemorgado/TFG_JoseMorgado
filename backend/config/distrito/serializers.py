from rest_framework import serializers
from distrito.models import Distrito, long_minima_codigo, long_minima_nombre, long_max_codigo, long_max_nombre


class DistritoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Distrito.
    Incluye validaciones de longitud y formato en los campos 'nombre' y 'codigo'.
    """

    class Meta:
        model = Distrito
        fields = ['id', 'nombre', 'codigo']
        read_only_fields = ['id']
        extra_kwargs = {
            "nombre": {
                "help_text": f"Nombre del distrito. Entre {long_minima_nombre} y {long_max_nombre} caracteres."
            },
            "codigo": {
                "help_text": (
                    f"Código identificativo. Entre {long_minima_codigo} y {long_max_codigo} caracteres, "
                    "sin espacios y solo letras, números, guiones y guiones bajos."
                )
            }
        }

    def validate_nombre(self, value: str) -> str:
        """Valida y normaliza el nombre del distrito."""
        if value is None or not isinstance(value, str):
            raise serializers.ValidationError("El nombre es obligatorio.")

        limpio = value.strip()

        if len(limpio) < long_minima_nombre:
            raise serializers.ValidationError(
                f"El nombre debe tener al menos {long_minima_nombre} caracteres."
            )

        if len(limpio) > long_max_nombre:
            raise serializers.ValidationError(
                f"El nombre no puede tener más de {long_max_nombre} caracteres."
            )

        return limpio

    def validate_codigo(self, value: str) -> str:
        """Valida y normaliza el código del distrito."""
        if value is None or not isinstance(value, str):
            raise serializers.ValidationError("El código es obligatorio.")

        limpio = value.strip()

        if len(limpio) < long_minima_codigo:
            raise serializers.ValidationError(
                f"El código debe tener al menos {long_minima_codigo} caracteres."
            )

        if len(limpio) > long_max_codigo:
            raise serializers.ValidationError(
                f"El código no puede tener más de {long_max_codigo} caracteres."
            )

        if " " in limpio:
            raise serializers.ValidationError("El código no puede contener espacios.")

        import re
        if not re.match(r"^[A-Za-z0-9_-]+$", limpio):
            raise serializers.ValidationError(
                "El código solo puede contener letras, números, guión y guión bajo."
            )

        return limpio.upper()