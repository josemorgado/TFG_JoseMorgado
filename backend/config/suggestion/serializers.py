from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from django.contrib.contenttypes.models import ContentType

from suggestion.models import Suggestion
from megusta.models import MeGusta


class SuggestionSerializer(serializers.ModelSerializer):

    autor_nombre = SerializerMethodField(
        read_only=True, help_text="Nombre completo o username del autor."
    )
    content_type = SerializerMethodField(
        read_only=True, help_text="Id del content type de Suggestion."
    )
    is_liked = SerializerMethodField(
        read_only=True, help_text="Si el usuario autenticado ha dado MeGusta."
    )
    fecha_creacion_iso = serializers.DateTimeField(
        source="fecha_creacion", format="%Y-%m-%dT%H:%M:%S%z", read_only=True
    )

    autor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        help_text="ID del usuario autor de la sugerencia."
    )

    class Meta:
        model = Suggestion
        fields = [
            "id",
            "titulo",
            "descripcion",
            "autor",
            "autor_nombre",
            "fecha_creacion",
            "fecha_actualizacion",
            "fecha_creacion_iso",
            "num_votos",
            "content_type",
            "is_liked",
        ]
        read_only_fields = [
            "id",
            "fecha_creacion",
            "fecha_actualizacion",
            "num_votos",
            "content_type",
            "is_liked",
            "fecha_creacion_iso",
        ]
        extra_kwargs = {
            "titulo": {"help_text": "Título breve de la sugerencia (5–200 caracteres)."},
            "descripcion": {
                "help_text": "Descripción completa de la sugerencia (10–5000 caracteres)."
            },
        }

    # -----------------------------
    # CAMPOS DERIVADOS
    # -----------------------------

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return None
        nombre = f"{obj.autor.first_name} {obj.autor.last_name}".strip()
        return nombre if nombre else obj.autor.username

    def get_content_type(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        return ct.id

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return MeGusta.objects.is_liked_by(obj, user)

    # -----------------------------
    # CREACIÓN
    # -----------------------------

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        autor_enviado = validated_data.get("autor", None)

        if not user.perfil.moderator:
            validated_data["autor"] = user
        else:
            validated_data["autor"] = autor_enviado or user

        return super().create(validated_data)

    # -----------------------------
    # UPDATE
    # -----------------------------

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user

        if not user.is_staff:
            validated_data.pop("autor", None)
        else:
            if validated_data.get("autor") is None:
                validated_data["autor"] = user

        return super().update(instance, validated_data)

    # -----------------------------
    # VALIDACIONES
    # -----------------------------

    def validate_titulo(self, value):
        value = value.strip()
        if len(value) < 5 or len(value) > 200:
            raise serializers.ValidationError(
                "El título debe tener al menos 5 caracteres y no más de 200."
            )
        return value

    def validate_descripcion(self, value):
        if len(value) < 10 or len(value) > 5000:
            raise serializers.ValidationError(
                "La descripción debe tener entre 10 y 5000 caracteres."
            )
        return value