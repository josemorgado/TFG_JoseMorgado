from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.contenttypes.models import ContentType
from imagen.models import Imagen
from video.models import Video
from megusta.models import MeGusta
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericRelation



# Estados posibles de una queja
class EstadoQueja(models.TextChoices):
    PENDIENTE    = 'PEN', 'Pendiente'
    EN_PROGRESO  = 'ENP', 'En Progreso'
    RESUELTA     = 'RES', 'Resuelta'
    RECHAZADA    = 'REC', 'Rechazada'


class Queja(models.Model):
    # Identificador principal
    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único de la queja."
    )

    # Datos principales
    titulo = models.CharField(
        max_length=200,
        help_text="Título breve y descriptivo de la queja (máx. 200 caracteres)."
    )
    descripcion = models.TextField(
        help_text="Descripción detallada de la incidencia."
    )

    # Relaciones
    categoria = models.ForeignKey(
        'categoria.Categoria',
        on_delete=models.CASCADE,
        related_name='quejas',
        null=False,
        blank=False,
        help_text="Categoría a la que pertenece la queja."
    )
    distrito = models.ForeignKey(
        'distrito.Distrito',
        on_delete=models.CASCADE,
        related_name='quejas',
        null=False,
        blank=False,
        help_text="Distrito asociado a la queja."
    )

    # Estado con choices (longitud 3 para los códigos PEN/ENP/RES/REC)
    estado = models.CharField(
        max_length=3,
        choices=EstadoQueja.choices,
        default=EstadoQueja.PENDIENTE,
        help_text="Estado actual de la queja (PEN/ENP/RES/REC)."
    )

    # Ubicación opcional
    ubicacion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Ubicación opcional relacionada con la queja."
    )

    # Autor de la queja
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario autor que creó la queja."
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación de la queja."
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última actualización."
    )

    imagenes = GenericRelation(
        Imagen,
        related_query_name="queja"
    )
    videos = GenericRelation(
        Video,
        related_query_name="queja"
    )

    class Meta:
        # Orden por creación descendente
        ordering = ['-fecha_creacion']
        # Índices útiles para filtros frecuentes
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['autor']),
            models.Index(fields=['categoria']),
            models.Index(fields=['distrito']),
            models.Index(fields=['-fecha_creacion']),
        ]
        verbose_name = "Queja"
        verbose_name_plural = "Quejas"

    def __str__(self):
        # Representación corta y legible
        return f'Queja #{self.id} — {self.titulo[:40]}'

    # Validaciones no disruptivas
    def clean(self):
        # Normaliza espacios en título y descripción
        if self.titulo:
            self.titulo = self.titulo.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()

    # Conteos dinámicos (no se almacenan en DB)

    @property
    def num_votos(self):
        # Número total de 'me gusta' asociados a esta queja
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()

    @property
    def num_comentarios(self):
        # Número total de comentarios (incluye respuestas)
        from comentario.models import Comentario
        return Comentario.objects.filter(queja=self.pk).count()

    @property
    def num_comentarios_top_level(self):
        # Número de comentarios de primer nivel
        from comentario.models import Comentario
        return Comentario.objects.filter(queja=self.pk, parent__isnull=True).count()


@receiver(pre_delete, sender=Queja)
def borrar_imagenes_queja(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    Imagen.objects.filter(content_type=ct, object_id=instance.id).delete()

@receiver(pre_delete, sender=Queja)
def borrar_videos_queja(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    Video.objects.filter(content_type=ct, object_id=instance.id).delete()

@receiver(pre_delete, sender=Queja)
def borrar_megusta_comentario(sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(instance)
    MeGusta.objects.filter(content_type=ct, object_id=instance.id).delete()