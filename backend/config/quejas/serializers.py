import dis
import re
from webbrowser import get
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from django.contrib.contenttypes.models import ContentType
from quejas.models import Queja
from megusta.models import MeGusta


class QuejaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Queja.
    Mantiene todas las validaciones y lógica original, añadiendo
    descripciones para mejorar la documentación en Swagger.
    """

    # Campos de solo lectura derivados
    categoria_nombre = SerializerMethodField(
        read_only=True, help_text="Nombre legible de la categoría."
    )
    distrito_nombre = SerializerMethodField(
        read_only=True, help_text="Nombre legible del distrito."
    )
    autor_nombre = SerializerMethodField(
        read_only=True, help_text="Nombre completo o username del autor."
    )
    content_type = SerializerMethodField(
        read_only=True, help_text="Id del content type de queja"
    )
    is_liked = SerializerMethodField(
        read_only=True, help_text="Si el usuario autenticado ha dado megusta"
    )
    fecha_creacion_iso = serializers.DateTimeField(
        source="fecha_creacion", format="%Y-%m-%dT%H:%M:%S%z", read_only=True
    )
    # Campos relacionados (en producción el autor vendrá del request)
    autor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        help_text="ID del usuario autor de la queja.",
    )

    # Querysets dinámicos para evitar import circular
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field("categoria").remote_field.model.objects.all(),
        help_text="ID de la categoría asociada.",
    )
    distrito = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field("distrito").remote_field.model.objects.all(),
        help_text="ID del distrito asociado.",
    )

    imagenes_count = serializers.IntegerField(read_only=True)
    videos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Queja
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "categoria_nombre",
            "distrito",
            "distrito_nombre",
            "estado",
            "ubicacion",
            "autor",
            "autor_nombre",
            "fecha_creacion",
            "fecha_actualizacion",
            "num_votos",
            "num_comentarios",
            "num_comentarios_top_level",
            "content_type",
            "is_liked",
            "fecha_creacion_iso",
            "imagenes_count",
            "videos_count",
        ]
        read_only_fields = [
            "id",
            "estado",
            "fecha_creacion",
            "fecha_actualizacion",
            "num_votos",
            "num_comentarios",
            "num_comentarios_top_level",
            "content_type",
            "is_liked",
            "fecha_creacion_iso",
            "imagenes_count",
            "videos_count",
        ]
        extra_kwargs = {
            "titulo": {"help_text": "Título breve y descriptivo (5–200 caracteres)."},
            "descripcion": {
                "help_text": "Descripción detallada de la queja (10–5000 caracteres)."
            },
            "ubicacion": {
                "help_text": "Ubicación relacionada con la incidencia (opcional)."
            },
            "estado": {"help_text": "Estado de la queja (solo lectura)."},
            "fecha_creacion": {"help_text": "Fecha y hora de creación (solo lectura)."},
            "fecha_actualizacion": {
                "help_text": "Fecha y hora de última modificación (solo lectura)."
            },
        }

    # Obtener el content_type de queja para la creacion de comentarios, imagenes y videos
    def get_content_type(selft, obj):
        ct = ContentType.objects.get_for_model(obj)
        return ct.id

    # CREACIÓN DE QUEJA
    def create(self, validated_data):
        # El autor se asigna automáticamente desde el request
        request = self.context.get("request")
        user = request.user

        autor_enviado = validated_data.get("autor", None)

        if not user.perfil.moderator:
            validated_data["autor"] = user

        else:
            if autor_enviado is None:
                validated_data["autor"] = user
            else:
                validated_data["autor"] = autor_enviado

        validated_data.setdefault("estado", "PEN")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        user = request.user

        autor_enviado = validated_data.get("autor", None)

        # Usuarios normales NO pueden cambiar el autor
        if not user.is_staff:
            validated_data.pop("autor", None)
        else:
            # Si es moderador: si no envía autor → él mismo
            if autor_enviado is None:
                validated_data["autor"] = user

        return super().update(instance, validated_data)

    # VALIDACIÓN DEL TÍTULO
    def validate_titulo(self, value):
        value = value.strip()
        if len(value) < 5 or len(value) > 200:
            raise serializers.ValidationError(
                "El título debe tener al menos 5 caracteres y no más de 200."
            )
        if not value:
            raise serializers.ValidationError(
                "El título no puede estar vacío o contener solo espacios."
            )
        return value

    # VALIDACIÓN DE DESCRIPCIÓN
    def validate_descripcion(self, value):
        if len(value) < 10 or len(value) > 5000:
            raise serializers.ValidationError(
                "La descripción debe tener entre 10 y 5000 caracteres."
            )
        return value

    # VALIDACIONES CRUZADAS
    def validate(self, data):
        # Evita duplicar quejas con el mismo título en un distrito
        request = self.context.get("request")
        user = getattr(request, "user", None)

        titulo = data.get("titulo", getattr(self.instance, "titulo", None))
        distrito = data.get("distrito", getattr(self.instance, "distrito", None))

        qs = Queja.objects.filter(titulo__iexact=titulo, distrito=distrito)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya has presentado una queja con el mismo título en este distrito."
            )
        return data

    # CAMPOS DERIVADOS
    def get_categoria_nombre(self, obj):
        return getattr(obj.categoria, "nombre", None)

    def get_distrito_nombre(self, obj):
        return getattr(obj.distrito, "nombre", None)

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return None
        nombre = f"{obj.autor.first_name} {obj.autor.last_name}".strip()
        return nombre if nombre else obj.autor.username

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return MeGusta.objects.is_liked_by(obj, user)
