from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_IMAGENES = 5

def media_upload_to(instance, filename):
    """
    Genera la ruta de almacenamiento del archivo de imagen en función del tipo
    de objeto relacionado y su identificador. La estructura resultante será:

        media/<modelo_relacionado>/<id_relacionado>/imagenes/<filename>

    Ejemplo:
        media/queja/42/imagenes/foto.png
    """
    tipo = instance.content_type.model
    return f"{tipo}/{instance.object_id}/imagenes/{filename}"


class Imagen(models.Model):
    """
    Modelo que representa una imagen asociada a cualquier entidad del sistema
    (Queja, Comentario, etc.) mediante una relación genérica. Permite limitar
    el número máximo de imágenes por objeto y mantener un orden explícito.
    """

    id = models.BigAutoField(
        primary_key=True,
        help_text="Identificador único de la imagen."
    )

    # Relación genérica: (content_type + object_id) -> content_object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=(
            "Tipo de contenido del objeto relacionado (p. ej., 'queja' o 'comentario'). "
            "Internamente apunta al modelo de la app correspondiente."
        )
    )
    object_id = models.PositiveIntegerField(
        help_text="Identificador del objeto relacionado al que pertenece esta imagen."
    )
    content_object = GenericForeignKey(
        "content_type", "object_id"
    )

    imagen = models.ImageField(
        upload_to=media_upload_to,
        help_text=(
            "Archivo de imagen. Se almacenará bajo la ruta generada dinámicamente "
            "por 'media_upload_to'."
        )
    )

    orden = models.PositiveIntegerField(
        default=None,
        help_text=(
            "Posición de orden dentro del conjunto de imágenes del objeto relacionado. "
            "Si no se indica, se asigna automáticamente al guardar."
        )
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó el registro."
    )

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        # Orden por defecto: primero por 'orden' y, como desempate, por fecha de creación.
        ordering = ["orden", "fecha_creacion"]
        # Índice para acelerar consultas por relación genérica (muy usado en listados)
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        # Garantiza que no haya dos imágenes con el mismo 'orden' para el mismo objeto
        constraints = [
            models.UniqueConstraint(
                fields=["content_type", "object_id", "orden"],
                name="unique_image_order_per_object",
            )
        ]

    def clean(self):
        """
        Validaciones de dominio:
        - Limita el número de imágenes por objeto (MAX_IMAGENES).
        """
        if self.pk is None:
            total = Imagen.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id
            ).count()

            if total >= MAX_IMAGENES:
                raise ValidationError(
                    _(f"Solo se permiten un máximo de {MAX_IMAGENES} imágenes por objeto.")
                )

    def save(self, *args, **kwargs):
        """
        Asigna automáticamente el 'orden' cuando el registro es nuevo y no se proporcionó.
        Valida el modelo completo antes de guardar (full_clean).
        """
        if self.pk is None:
            if self.orden is None:
                qs = Imagen.objects.filter(
                    content_type=self.content_type,
                    object_id=self.object_id
                )
                ultimo = qs.order_by("-orden").first()
                self.orden = (ultimo.orden + 1) if ultimo and ultimo.orden is not None else 0

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación legible: útil en admin y logs.
        """
        return f"Imagen {self.id} para {self.content_object} (Orden: {self.orden})"