# usuarios/serializers.py
from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Perfil

User = get_user_model()


class PerfilSerializer(serializers.ModelSerializer):
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
            'edad'
        ]
        read_only_fields = ['fecha_actualizacion', 'edad']

    def validate_fecha_nacimiento(self, value):
        if value:
            if value > date.today():
                raise serializers.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
            min_age = 14
            edad = (date.today() - value).days // 365
            if edad < min_age:
                raise serializers.ValidationError(f'La edad mínima es {min_age} años.')
        return value


class UserLiteSerializer(serializers.ModelSerializer):
    """Serializer básico de User para listar/mostrar."""
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
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']



class UserPerfilSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(required=True)  # explícitamente requerido
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'is_active', 'perfil', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    @transaction.atomic
    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil')
        password = validated_data.pop('password', None)

        # 1) Crea el usuario
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])

        # 2) Crea/actualiza el Perfil usando su propio serializer (no setattr)
        #    Usamos instance explícita para evitar sorpresas con la señal post_save
        perfil_instance, _ = Perfil.objects.get_or_create(user=user)

        perfil_serializer = PerfilSerializer(
            instance=perfil_instance,
            data=perfil_data,
            partial=False,                   # en create esperamos todos los campos de perfil
            context=self.context
        )
        perfil_serializer.is_valid(raise_exception=True)
        perfil_serializer.save()            # ← aquí sí se persisten los campos

        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', None)
        password = validated_data.pop('password', None)

        # 1) Actualiza User
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()

        # 2) Actualiza Perfil (si viene en el payload)
        if perfil_data is not None:
            perfil_instance, _ = Perfil.objects.get_or_create(user=instance)
            perfil_serializer = PerfilSerializer(
                instance=perfil_instance,
                data=perfil_data,
                partial=getattr(self, 'partial', False),  # respeta PUT/PATCH
                context=self.context
            )
            perfil_serializer.is_valid(raise_exception=True)
            perfil_serializer.save()

        return instance
