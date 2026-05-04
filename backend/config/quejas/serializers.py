from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.fields import SerializerMethodField

from quejas.models import Queja
from megusta.models import MeGusta
from respuesta.models import Respuesta

from config.services.moderation.moderation_service import moderate_text


class QuejaSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Queja.

    Responsabilidades:
    - Validar campos individuales y cruzados.
    - Aplicar moderación de contenido textual.
    - Controlar la asignación del autor según permisos.
    - Exponer campos derivados necesarios para el frontend.
    """

    # ───────────────
    # Campos derivados
    # ───────────────
    categoria_nombre = SerializerMethodField()
    distrito_nombre = SerializerMethodField()
    autor_nombre = SerializerMethodField()
    content_type = SerializerMethodField()
    is_liked = SerializerMethodField()
    num_respuestas = SerializerMethodField()

    # Fecha formateada para consumo en frontend
    fecha_creacion_iso = serializers.DateTimeField(
        source="fecha_creacion", format="%Y-%m-%dT%H:%M:%S%z", read_only=True
    )

    # ───────────────
    # Relaciones
    # ───────────────
    autor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        help_text="Autor de la queja. Ignorado para usuarios no moderadores.",
    )

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field("categoria").remote_field.model.objects.all(),
        help_text="Categoría asociada a la queja.",
    )

    distrito = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field("distrito").remote_field.model.objects.all(),
        help_text="Distrito asociado a la queja.",
    )

    # Contadores precalculados (solo lectura)
    imagenes_count = serializers.IntegerField(read_only=True)
    videos_count = serializers.IntegerField(read_only=True)

    # ───────────────
    # Meta
    # ───────────────
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
            "fecha_creacion_iso",
            "num_votos",
            "num_comentarios",
            "num_comentarios_top_level",
            "imagenes_count",
            "videos_count",
            "num_respuestas",
            "content_type",
            "is_liked",
        ]
        read_only_fields = [
            "id",
            "estado",
            "fecha_creacion",
            "fecha_actualizacion",
            "num_votos",
            "num_comentarios",
            "num_comentarios_top_level",
            "imagenes_count",
            "videos_count",
            "num_respuestas",
            "content_type",
            "is_liked",
            "fecha_creacion_iso",
        ]
        extra_kwargs = {
            "titulo": {"help_text": "Título breve y descriptivo (5–200 caracteres)."},
            "descripcion": {
                "help_text": "Descripción detallada de la queja (10–5000 caracteres)."
            },
            "ubicacion": {
                "help_text": "Ubicación relacionada con la incidencia (opcional)."
            },
        }

    # ───────────────
    # Validaciones de campo
    # ───────────────
    def validate_titulo(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "El título no puede estar vacío o contener solo espacios."
            )
        if len(value) < 5 or len(value) > 200:
            raise serializers.ValidationError(
                "El título debe tener entre 5 y 200 caracteres."
            )
        return value

    def validate_descripcion(self, value):
        if len(value) < 10 or len(value) > 5000:
            raise serializers.ValidationError(
                "La descripción debe tener entre 10 y 5000 caracteres."
            )
        return value

    # ───────────────
    # Validaciones cruzadas
    # ───────────────
    def validate(self, data):
        """
        Validaciones que dependen de múltiples campos:
        - Moderación del contenido textual.
        - Evitar duplicados por título y distrito.
        """
        titulo = data.get("titulo", getattr(self.instance, "titulo", ""))
        descripcion = data.get("descripcion", getattr(self.instance, "descripcion", ""))

        # 1. Sistema de moderación de contenido
        texto = f"{titulo} {descripcion}"
        moderate_text(texto)

        # 2. Prevenir duplicados por título y distrito
        distrito = data.get("distrito", getattr(self.instance, "distrito", None))

        qs = Queja.objects.filter(titulo__iexact=titulo, distrito=distrito)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una queja con el mismo título en este distrito."
            )

        return data

    # ───────────────
    # Creación y actualización
    # ───────────────
    def create(self, validated_data):
        """
        Asigna automáticamente el autor y establece el estado inicial.
        """
        request = self.context.get("request")
        user = request.user

        autor_enviado = validated_data.get("autor")

        if not user.perfil.moderator:
            validated_data["autor"] = user
        else:
            validated_data["autor"] = autor_enviado or user

        validated_data.setdefault("estado", "PEN")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Controla la modificación del autor según permisos.
        """
        request = self.context.get("request")
        user = request.user

        if not user.is_staff:
            validated_data.pop("autor", None)
        else:
            validated_data["autor"] = validated_data.get("autor", user)

        return super().update(instance, validated_data)

    # ───────────────
    # Métodos de campos derivados
    # ───────────────
    def get_categoria_nombre(self, obj):
        return getattr(obj.categoria, "nombre", None)

    def get_distrito_nombre(self, obj):
        return getattr(obj.distrito, "nombre", None)

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return None
        nombre = f"{obj.autor.first_name} {obj.autor.last_name}".strip()
        return nombre if nombre else obj.autor.username

    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj).id

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return MeGusta.objects.is_liked_by(obj, user)

    def get_num_respuestas(self, obj):
        return getattr(obj, "num_respuestas", 0)

    def get_num_votos(self, obj):
        return getattr(obj, "num_votos_db", obj.num_votos)

