from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Perfil

User = get_user_model()


# --------- Perfil ---------
class PerfilSerializer(serializers.ModelSerializer):
    """
    Serializador del perfil de usuario, alineado con el modelo.
    Incluye validación de fecha de nacimiento y expone campos de solo lectura.
    """
    edad = serializers.IntegerField(read_only=True)

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
            "genero": {
                "help_text": "Género del usuario (M, F u O)."
            },
            "biografia": {
                "help_text": "Descripción o biografía breve del usuario.",
            },
            "moderator": {
                "help_text": "Indica si el usuario tiene rol de moderador."
            },
            "telefono": {
                "help_text": "Teléfono en formato internacional (+NN...).",
                "required": True,
            },
            "direccion": {
                "help_text": "Dirección postal o de contacto.",
                "required": True,
            },
            "fecha_nacimiento": {
                "help_text": "Fecha de nacimiento del usuario (YYYY-MM-DD).",
                "required": True,
            },
            "foto_perfil": {
                "help_text": "Archivo de imagen para el avatar (multipart/form-data)."
            },
        }

    # Validación: fecha_nacimiento no futura y edad mínima
    def validate_fecha_nacimiento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        if value:
            min_age = 14
            edad = (date.today() - value).days // 365
            if edad < min_age:
                raise serializers.ValidationError(f'La edad mínima es {min_age} años.')
        return value


# --------- User Lite (para listar/mostrar) ---------
class UserLiteSerializer(serializers.ModelSerializer):
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


# --------- User + Perfil (crear/actualizar en una operación) ---------
class UserPerfilSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    # Campos del perfil expuestos directamente
    telefono = serializers.CharField(write_only=True)
    direccion = serializers.CharField(write_only=True)
    fecha_nacimiento = serializers.DateField(write_only=True)
    genero = serializers.CharField(write_only=True, required=False)
    biografia = serializers.CharField(write_only=True, required=False)
    foto_perfil = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "telefono",
            "direccion",
            "fecha_nacimiento",
            "genero",
            "biografia",
            "foto_perfil",
        ]
    # Validación de email único
    def validate_email(self, value):
        if value is None or value.strip() == "":
            raise serializers.ValidationError("El email no puede estar vacío.")
        qs = User.objects.filter(email__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value.strip()

    # Validación de username único y no vacío
    def validate_username(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")
        qs = User.objects.filter(username__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre de usuario.")
        return value.strip()

    # -------------------------
    # CREATE
    # -------------------------

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")

        # Extraer datos de perfil
        telefono = validated_data.pop("telefono")
        direccion = validated_data.pop("direccion")
        fecha_nacimiento = validated_data.pop("fecha_nacimiento")
        genero = validated_data.pop("genero", "O")
        biografia = validated_data.pop("biografia", "")
        foto_perfil = validated_data.pop("foto_perfil", None)

        # Crear usuario SOLO con campos válidos
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Crear perfil correctamente
        Perfil.objects.create(
            user=user,
            telefono=telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            biografia=biografia,
            foto_perfil=foto_perfil,
        )

        return user
    # -------------------------
    # UPDATE
    # -------------------------

    @transaction.atomic
    def update(self, instance, validated_data):
        perfil_data = validated_data.pop("perfil", None)
        password = validated_data.pop("password", None)

        # Actualizar User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        # Actualizar Perfil
        if perfil_data is not None:
            perfil_instance = instance.perfil

            request = self.context.get("request")
            if request and request.FILES.get("perfil.foto_perfil"):
                perfil_data["foto_perfil"] = request.FILES.get("perfil.foto_perfil")

            perfil_serializer = PerfilSerializer(
                instance=perfil_instance,
                data=perfil_data,
                partial=self.partial,
                context=self.context,
            )
            perfil_serializer.is_valid(raise_exception=True)
            perfil_serializer.save()

        return instance

class UserWithPerfilSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
            "perfil",
        ]
        read_only_fields = fields