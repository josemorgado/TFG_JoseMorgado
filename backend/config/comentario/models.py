from django.db import models
from django.contrib.contenttypes.models import ContentType
from megusta.models import MeGusta

# Modelo que representa comentarios asociados a una queja, con soporte para respuestas encadenadas.
class Comentario(models.Model):
    id = models.AutoField(primary_key=True)

    # Relación con la queja a la que pertenece el comentario.
    queja = models.ForeignKey(
        'quejas.Queja',
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    # Usuario autor del comentario.
    autor = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def num_votos(self):
        # Obtiene el número de votos (MeGusta) asociados a este comentario mediante ContentType.
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()

    # Relación opcional con un comentario padre para soportar hilos de respuestas.
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='respuestas',
        null=True,
        blank=True,
        verbose_name="Comentario Padre"
    )