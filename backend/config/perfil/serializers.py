from datetime import date
import json

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import Perfil

User = get_user_model()


class PerfilSerializer(serializers.ModelSerializer):
    """
    Serializer del perfil de usuario.
    Gestiona la información extendida del usuario y aplica
    validaciones de edad y coherencia de datos.
    """

    edad = serializers.IntegerField(read_only=True)

    class Meta:
        model = Perfil
        fields = [
            "genero",
            "biografia",
            "moderator",
            "telefono",
            "direccion",
            "fecha_nacimiento",
            "fecha_actualizacion",
            "foto_perfil",
            "edad",
        ]
        read_only_fields = ["fecha_actualizacion", "edad"]

    def validate_fecha_nacimiento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede estar en el futuro."
            )

        if value:
            edad = (date.today() - value).days // 365
            if edad < 14:
                raise serializers.ValidationError(
                    "La edad mínima para registrarse es de 14 años."
                )

        return value


class UserMeSerializer(serializers.ModelSerializer):
    """
    Serializer del endpoint /me.
    Devuelve la información del usuario autenticado junto a su perfil,
    ofreciendo además campos aplanados para facilitar el consumo
    desde el frontend.
    """

    perfil = PerfilSerializer(read_only=True)
    is_moderator = serializers.BooleanField(source="perfil.moderator", read_only=True)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_moderator",
            "groups",
            "perfil",
        ]
        read_only_fields = fields


class UserPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer encargado de la creación y actualización conjunta
    del usuario y su perfil asociado.

    Admite tanto peticiones JSON como multipart/form-data,
    permitiendo la gestión de imágenes y campos anidados.
    """

    password = serializers.CharField(write_only=True, required=False)
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "perfil",
        ]

    def validate_email(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El correo electrónico no puede estar vacío."
            )

        qs = User.objects.filter(email__iexact=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Este correo electrónico ya está en uso.")

        return value

    def validate_username(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("El nombre de usuario es obligatorio.")

        qs = User.objects.filter(username__iexact=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con ese nombre de usuario."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")

        telefono = request.data.get("telefono")
        direccion = request.data.get("direccion")
        fecha_nacimiento = request.data.get("fecha_nacimiento")
        genero = request.data.get("genero", "O")
        biografia = request.data.get("biografia", "")
        foto = request.FILES.get("foto_perfil")

        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        Perfil.objects.create(
            user=user,
            telefono=telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            biografia=biografia,
            foto_perfil=foto,
        )

        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")

        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        perfil_instance = instance.perfil

        perfil_raw = request.data.get("perfil")
        perfil_data = {}

        if isinstance(perfil_raw, dict):
            perfil_data = perfil_raw

        elif isinstance(perfil_raw, str):
            try:
                perfil_data = json.loads(perfil_raw)
            except json.JSONDecodeError:
                perfil_data = {}

        if "moderator" in perfil_data:
            usuario_actual = request.user

            if not (
                usuario_actual.is_superuser
                or getattr(usuario_actual.perfil, "moderator", False)
            ):
                raise PermissionDenied(
                    "No tienes permiso para modificar el rol de moderador."
                )

        eliminar_foto = perfil_data.pop("eliminar_foto", False)

        if eliminar_foto is True:
            if perfil_instance.foto_perfil:
                perfil_instance.foto_perfil.delete(save=False)
            perfil_instance.foto_perfil = None

        foto = request.FILES.get("perfil.foto_perfil")

        if foto:
            perfil_data["foto_perfil"] = foto

        perfil_serializer = PerfilSerializer(
            perfil_instance,
            data=perfil_data,
            partial=True,
        )

        perfil_serializer.is_valid(raise_exception=True)
        perfil_serializer.save()

        return instance


class UserLiteSerializer(serializers.ModelSerializer):
    """
    Serializer reducido de usuario.
    Se utiliza en listados y vistas donde no es necesario
    cargar la información completa del perfil.
    """

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
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserWithPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura del usuario junto a su perfil,
    pensado para vistas públicas o de consulta.
    """

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


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitar el restablecimiento de contraseña
    a partir del correo electrónico del usuario.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No existe ningún usuario con este correo electrónico."
            )

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer encargado de confirmar el cambio de contraseña
    mediante token y nueva clave.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()
