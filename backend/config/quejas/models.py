from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from megusta.models import MeGusta


# Estados posibles de una queja
class EstadoQueja(models.TextChoices):
    PENDIENTE    = 'PEN', 'Pendiente'
    EN_PROGRESO  = 'ENP', 'En Progreso'
    RESUELTA     = 'RES', 'Resuelta'
    RECHAZADA    = 'REC', 'Rechazada'


class Queja(models.Model):
    # Identificador principal
    id = models.AutoField(primary_key=True)

    # Datos principales
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    # Relaciones
    categoria = models.ForeignKey(
        'categoria.Categoria',
        on_delete=models.CASCADE,
        related_name='quejas',
        null=False,
        blank=False,
    )
    distrito = models.ForeignKey(
        'distrito.Distrito',
        on_delete=models.CASCADE,
        related_name='quejas',
        null=False,
        blank=False,
    )

    # Estado con choices (longitud 3 para los códigos PEN/ENP/RES/REC)
    estado = models.CharField(
        max_length=3,
        choices=EstadoQueja.choices,
        default=EstadoQueja.PENDIENTE,
    )

    # Ubicación opcional
    ubicacion = models.CharField(max_length=255, blank=True, null=True)

    # Autor de la queja
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

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