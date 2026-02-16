from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_VIDEOS = 1


# Ruta de almacenamiento para los videos
def media_upload_to(instance, filename):
    # Cada objeto guarda sus videos en una carpeta por tipo y su ID
    tipo = instance.content_type.model
    return f'media/{tipo}/{instance.object_id}/videos/{filename}'


class Video(models.Model):
    # Identificador principal
    id = models.BigAutoField(
        primary_key=True,
        help_text="Identificador único del video."
    )

    # Relación genérica hacia cualquier modelo
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Modelo al que está asociado el video (p. ej., queja o comentario)."
    )
    object_id = models.PositiveIntegerField(
        help_text="ID del objeto concreto dentro del modelo asociado."
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Archivo de video subido
    video = models.FileField(
        upload_to=media_upload_to,
        help_text="Archivo de video subido (multipart/form-data)."
    )

    # Orden dentro del conjunto (aunque MAX_VIDEOS=1)
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Posición del video dentro del objeto padre."
    )

    # Fecha de creación del registro
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del registro."
    )

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ['orden', 'fecha_creacion']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        constraints = [
            # Un video por orden dentro del mismo objeto
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'orden'],
                name='unique_video_order_per_object'
            ),
        ]

    def clean(self):
        # Validar número máximo de videos por objeto (solo al crear)
        if self.pk is None:
            total = Video.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id
            ).count()

            if total >= MAX_VIDEOS:
                raise ValidationError(
                    _(f'Solo se permiten un máximo de {MAX_VIDEOS} videos por objeto.')
                )

    def save(self, *args, **kwargs):
        # Validaciones antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        # Representación legible
        return f'Video {self.id} para {self.content_object} (Orden: {self.orden})'