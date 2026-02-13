from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_IMAGENES = 5

# Función para definir la ruta de almacenamiento de la imagen
def media_upload_to(instance, filename):
    tipo = instance.content_type.model
    return f"media/{tipo}/{instance.object_id}/imagenes/{filename}"


class Imagen(models.Model):
    id = models.BigAutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    imagen = models.ImageField(upload_to=media_upload_to)
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["orden", "fecha_creacion"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        constraints = [
            # Garantiza que cada objeto tenga un único orden por imagen
            models.UniqueConstraint(
                fields=["content_type", "object_id", "orden"],
                name="unique_image_order_per_object"
            )
        ]

    def clean(self):
        # Valida el número máximo de imágenes por objeto
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
        # Asigna orden automáticamente si la imagen es nueva
        if self.pk is None:
            if self.orden is None:
                qs = Imagen.objects.filter(
                    content_type=self.content_type,
                    object_id=self.object_id
                )
                ultimo = qs.order_by("-orden").first()
                self.orden = (ultimo.orden + 1) if ultimo else 0
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagen {self.id} para {self.content_object} (Orden: {self.orden})"