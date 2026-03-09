from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
import json
from .models import Perfil

User = get_user_model()


# --------- Perfil ---------


class PerfilSerializer(serializers.ModelSerializer):
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
                raise serializers.ValidationError("La edad mínima es 14 años.")
        return value


class UserPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer que sirve para:
    - Crear usuario + perfil
    - Actualizar usuario + perfil (PUT/PATCH)
    Acepta:
    - JSON con {"perfil": {...}}
    - multipart/form-data con perfil="{}" y perfil.foto_perfil=archivo
    """

    # password no obligatorio en update
    password = serializers.CharField(write_only=True, required=False)

    # Datos del perfil (solo lectura en update)
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
            raise serializers.ValidationError("El email no puede estar vacío.")
        qs = User.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Este email ya está en uso.")
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

    # ============================================================
    # CREATE
    # ============================================================
    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")

        # Extraer campos del perfil desde request.data
        # (No vienen en validated_data por usar PerfilSerializer)
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

    # ============================================================
    # UPDATE
    # ============================================================
    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # -------------------------
        # 1. Procesar datos simples del usuario
        # -------------------------
        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        # -------------------------
        # 2. Procesar datos del perfil
        # -------------------------

        perfil_instance = instance.perfil

        # perfil puede llegar:
        # - como JSON anidado {perfil: {...}}
        # - como string JSON en multipart: perfil="{...}"
        perfil_raw = request.data.get("perfil")

        perfil_data = {}

        if isinstance(perfil_raw, dict):
            perfil_data = perfil_raw

        elif isinstance(perfil_raw, str):
            try:
                perfil_data = json.loads(perfil_raw)
            except json.JSONDecodeError:
                perfil_data = {}

        # Añadir foto subida
        foto = request.FILES.get("perfil.foto_perfil")
        if foto:
            perfil_data["foto_perfil"] = foto

        # Construir serializer del perfil
        perfil_serializer = PerfilSerializer(
            perfil_instance,
            data=perfil_data,
            partial=True,
        )
        perfil_serializer.is_valid(raise_exception=True)
        perfil_serializer.save()

        return instance


# --------- User Lite (para listar/mostrar) ---------
class UserLiteSerializer(serializers.ModelSerializer):
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
        extra_kwargs = {
            "username": {"help_text": "Nombre único de usuario."},
            "email": {"help_text": "Correo electrónico del usuario."},
            "first_name": {"help_text": "Nombre."},
            "last_name": {"help_text": "Apellidos."},
            "is_active": {"help_text": "Indica si la cuenta está activa."},
            "date_joined": {"help_text": "Fecha de alta (solo lectura)."},
            "last_login": {"help_text": "Último acceso (solo lectura)."},
        }


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
