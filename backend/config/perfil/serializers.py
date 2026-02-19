from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Perfil

User = get_user_model()


# Serializador del Perfil del usuario
class PerfilSerializer(serializers.ModelSerializer):
    """
    Serializador del perfil de usuario.
    Expone campos del perfil y valida la fecha de nacimiento (no futura y edad mínima).
    """
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
        extra_kwargs = {
            "genero": {"help_text": "Género del usuario (M, F u O)."},
            "biografia": {"help_text": "Descripción o biografía breve del usuario."},
            "moderator": {"help_text": "Indica si el usuario tiene rol de moderador."},
            "telefono": {"help_text": "Teléfono en formato internacional (+NN...)."},
            "direccion": {"help_text": "Dirección postal o de contacto."},
            "fecha_nacimiento": {"help_text": "Fecha de nacimiento del usuario (YYYY-MM-DD)."},
            "foto_perfil": {"help_text": "Archivo de imagen para el avatar (multipart/form-data)."},
            "edad": {"help_text": "Edad calculada en años (solo lectura)."},
            "fecha_actualizacion": {"help_text": "Última fecha/hora de actualización (solo lectura)."},
        }

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

    # Validación: biografía no vacía
    def validate_biografia(self, value):
        if value is not None and value.strip() == "":
            raise serializers.ValidationError("La biografía no puede estar vacía.")
        return value

    # Validación: teléfono no vacío
    def validate_telefono(self, value):
        if value is not None and value.strip() == "":
            raise serializers.ValidationError("El teléfono no puede estar vacío.")
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
        extra_kwargs = {
            "username": {"help_text": "Nombre único de usuario."},
            "email": {"help_text": "Correo electrónico del usuario."},
            "first_name": {"help_text": "Nombre."},
            "last_name": {"help_text": "Apellidos."},
            "is_active": {"help_text": "Indica si la cuenta está activa."},
            "date_joined": {"help_text": "Fecha de alta (solo lectura)."},
            "last_login": {"help_text": "Último acceso (solo lectura)."},
        }


# Serializador completo con perfil embebido
class UserPerfilSerializer(serializers.ModelSerializer):
    """
    Serializador compuesto para crear/actualizar el usuario y su perfil embebido
    en una sola operación. Acepta multipart/form-data para foto de perfil.
    """
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
        extra_kwargs = {
            "username": {"help_text": "Nombre único de usuario."},
            "email": {"help_text": "Correo electrónico único del usuario."},
            "first_name": {"help_text": "Nombre."},
            "last_name": {"help_text": "Apellidos."},
            "password": {"help_text": "Contraseña del usuario (solo escritura)."},
            "is_active": {"help_text": "Indica si la cuenta está activa."},
            "perfil": {"help_text": "Datos del perfil asociado al usuario."},
            "date_joined": {"help_text": "Fecha de alta (solo lectura)."},
            "last_login": {"help_text": "Último acceso (solo lectura)."},
        }

    # Validación opcional de email bien formado (refuerzo)

    def validate_email(self, value):
        if value is None or value.strip() == "":
            raise serializers.ValidationError("El email no puede ser nulo.")
        qs = User.objects.filter(email__iexact=value)
        # Excluir al propio usuario en caso de update
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def validate_username(self, value):
        if value is None:
            return value
        qs = User.objects.filter(username__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre de usuario.")
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