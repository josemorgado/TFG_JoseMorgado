from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.dispatch import receiver

from imagen.models import Imagen
from video.models import Video
from megusta.models import MeGusta

class Suggestion(models.Model):

    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único de la sugerencia."
    )

    titulo = models.CharField(
        max_length=200,
        help_text="Título breve de la sugerencia."
    )

    descripcion = models.TextField(
        help_text="Descripción completa de la sugerencia."
    )


    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sugerencias',
        help_text="Usuario que creó la sugerencia."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación."
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización."
    )


    class Meta:
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['autor']),
            models.Index(fields=['-fecha_creacion']),
        ]
        verbose_name = "Sugerencia"
        verbose_name_plural = "Sugerencias"

    def __str__(self):
        return f"Sugerencia #{self.id} — {self.titulo[:40]}"

    def clean(self):
        if self.titulo:
            self.titulo = self.titulo.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()

    @property
    def num_votos(self):
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()




@receiver(pre_delete, sender=Suggestion)
def borrar_megusta_sugerencia(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    MeGusta.objects.filter(content_type=ct, object_id=instance.id).delete()