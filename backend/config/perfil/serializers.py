from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Perfil

User = get_user_model()


# Serializador del Perfil del usuario
class PerfilSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(read_only=True)  # edad calculada desde el modelo

    class Meta:
        model = Perfil
        fields = [
            'genero',
            'biografia',
            'moderator',
            'telefono',
            'direccion',
            'fecha_nacimiento',
            'fecha_actualizacion',
            'foto_perfil',
            'edad',
        ]
        read_only_fields = ['fecha_actualizacion', 'edad']

    # Validación de fecha_nacimiento
    def validate_fecha_nacimiento(self, value):
        # La fecha no puede ser futura
        if value and value > date.today():
            raise serializers.ValidationError('La fecha de nacimiento no puede estar en el futuro.')

        # Validación de edad mínima
        if value:
            min_age = 14
            edad = (date.today() - value).days // 365
            if edad < min_age:
                raise serializers.ValidationError(f'La edad mínima es {min_age} años.')

        return value

    # Validación opcional (no cambia lógica): telefono no solo espacios
    def validate_telefono(self, value):
        if value and value.strip() == "":
            raise serializers.ValidationError("El teléfono no puede estar vacío.")
        return value

    # Validación opcional: biografía sin solo espacios
    def validate_biografia(self, value):
        if value and value.strip() == "":
            raise serializers.ValidationError("La biografía no puede estar vacía.")
        return value


# Serializador básico para listar o mostrar usuarios
class UserLiteSerializer(serializers.ModelSerializer):
    # Serializador ligero para uso en respuestas pequeñas
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


# Serializador completo con perfil embebido
class UserPerfilSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(required=True)  # perfil es obligatorio
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_active',
            'perfil',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    # Validación opcional de email bien formado (refuerzo)
    def validate_email(self, value):
        if value and value.strip() == "":
            raise serializers.ValidationError("El email no puede estar vacío.")
        return value

    # Validación opcional de username
    def validate_username(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")
        return value.strip()

    # Creación atómica de usuario + perfil
    @transaction.atomic
    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil')
        password = validated_data.pop('password', None)

        # Crea usuario
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])

        # Crea o actualiza perfil asociado
        perfil_instance, _ = Perfil.objects.get_or_create(user=user)
        perfil_serializer = PerfilSerializer(
            instance=perfil_instance,
            data=perfil_data,
            partial=False,
            context=self.context
        )
        perfil_serializer.is_valid(raise_exception=True)
        perfil_serializer.save()

        return user

    # Actualización atómica de usuario + perfil
    @transaction.atomic
    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', None)
        password = validated_data.pop('password', None)

        # Actualiza User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()

        # Actualiza Perfil si viene incluido
        if perfil_data is not None:
            perfil_instance, _ = Perfil.objects.get_or_create(user=instance)
            perfil_serializer = PerfilSerializer(
                instance=perfil_instance,
                data=perfil_data,
                partial=getattr(self, 'partial', False),
                context=self.context
            )
            perfil_serializer.is_valid(raise_exception=True)
            perfil_serializer.save()

        return instance