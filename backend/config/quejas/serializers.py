import dis
from webbrowser import get
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField

from quejas.models import Queja


class QuejaSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Queja.
    Mantiene todas las validaciones y lógica original, añadiendo
    descripciones para mejorar la documentación en Swagger.
    """

    # Campos de solo lectura derivados
    categoria_nombre = SerializerMethodField(read_only=True, help_text="Nombre legible de la categoría.")
    distrito_nombre  = SerializerMethodField(read_only=True, help_text="Nombre legible del distrito.")
    autor_nombre     = SerializerMethodField(read_only=True, help_text="Nombre completo o username del autor.")

    # Campos relacionados (en producción el autor vendrá del request)
    autor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="ID del usuario autor de la queja (se asigna automáticamente en producción)."
    )  # Quitar esta línea en producción

    # Querysets dinámicos para evitar import circular
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field('categoria').remote_field.model.objects.all(),
        help_text="ID de la categoría asociada."
    )
    distrito = serializers.PrimaryKeyRelatedField(
        queryset=Queja._meta.get_field('distrito').remote_field.model.objects.all(),
        help_text="ID del distrito asociado."
    )

    class Meta:
        model = Queja
        fields = [
            'id',
            'titulo',
            'descripcion',
            'categoria',
            'categoria_nombre',
            'distrito',
            'distrito_nombre',
            'estado',
            'ubicacion',
            'autor',
            'autor_nombre',
            'fecha_creacion',
            'fecha_actualizacion',
            'num_votos',
            'num_comentarios',
            'num_comentarios_top_level',
        ]
        read_only_fields = [
            'id',
            'estado',
            'autor',
            'fecha_creacion',
            'fecha_actualizacion',
            'num_votos',
            'num_comentarios',
            'num_comentarios_top_level',
        ]
        extra_kwargs = {
            "titulo": {
                "help_text": "Título breve y descriptivo (5–200 caracteres)."
            },
            "descripcion": {
                "help_text": "Descripción detallada de la queja (10–5000 caracteres)."
            },
            "ubicacion": {
                "help_text": "Ubicación relacionada con la incidencia (opcional)."
            },
            "estado": {
                "help_text": "Estado de la queja (solo lectura)."
            },
            "fecha_creacion": {
                "help_text": "Fecha y hora de creación (solo lectura)."
            },
            "fecha_actualizacion": {
                "help_text": "Fecha y hora de última modificación (solo lectura)."
            },
        }

    # CREACIÓN DE QUEJA
    def create(self, validated_data):
        # El autor se asigna automáticamente desde el request
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        validated_data.setdefault("autor", user)
        validated_data.setdefault("estado", "PEN")  # Estado inicial

        return super().create(validated_data)

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
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        titulo = data.get('titulo', getattr(self.instance, 'titulo', None))
        distrito = data.get('distrito', getattr(self.instance, 'distrito', None))

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
        return getattr(obj.categoria, 'nombre', None)

    def get_distrito_nombre(self, obj):
        return getattr(obj.distrito, 'nombre', None)

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return None
        nombre = f"{obj.autor.first_name} {obj.autor.last_name}".strip()
        return nombre if nombre else obj.autor.username