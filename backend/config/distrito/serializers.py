from rest_framework import serializers
from distrito.models import Distrito

class DistritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distrito
        fields = ['id', 'nombre', 'codigo']
        read_only_fields = ['id']

    # Validaciones de ejemplo
    def validate_nombre(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if len(value) > 100:
            raise serializers.ValidationError("El nombre no puede tener más de 100 caracteres.")
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_codigo(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("El código debe tener al menos 2 caracteres.")
        if len(value) > 10:
            raise serializers.ValidationError("El código no puede tener más de 10 caracteres.")
        return value