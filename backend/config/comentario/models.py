from django.db import models
from django.contrib.contenttypes.models import ContentType
from video.models import Video
from megusta.models import MeGusta
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from imagen.models import Imagen
from megusta.models import MeGusta


class Comentario(models.Model):
    """
    Representa un comentario asociado a una queja dentro de la aplicación.
    Permite hilos de respuestas mediante el campo 'parent' y soporta conteo
    dinámico de votos (MeGusta) gracias a ContentType.
    """

    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único del comentario."
    )

    queja = models.ForeignKey(
        'quejas.Queja',
        on_delete=models.CASCADE,
        related_name='comentarios',
        help_text="Queja a la que pertenece el comentario."
    )

    autor = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        help_text="Usuario autor del comentario."
    )

    contenido = models.TextField(
        help_text="Contenido textual del comentario."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del comentario."
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='respuestas',
        null=True,
        blank=True,
        verbose_name="Comentario padre",
        help_text="Comentario al que este responde. Permite crear hilos."
    )

    @property
    def num_votos(self):
        """Número total de votos (MeGusta) recibidos por este comentario."""
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["fecha_creacion"]

    def __str__(self):
        return f"Comentario #{self.id} de {self.autor}"

@receiver(pre_delete, sender=Comentario)
def borrar_imagenes_comentario(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    Imagen.objects.filter(content_type=ct, object_id=instance.id).delete()


@receiver(pre_delete, sender=Comentario)
def borrar_videos_comentario(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    Video.objects.filter(content_type=ct, object_id=instance.id).delete()

@receiver(pre_delete, sender=Comentario)
def borrar_megusta_comentario(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    MeGusta.objects.filter(content_type=ct, object_id=instance.id).delete()
