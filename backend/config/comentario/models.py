from django.db import models

# Create your models here.
from django.db import models
from django.contrib.contenttypes.models import ContentType
from megusta.models import MeGusta

class Comentario(models.Model):
    id = models.AutoField(primary_key=True)
    queja = models.ForeignKey('quejas.Queja', on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    @property
    def num_votos(self):
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='respuestas', null=True, blank=True, verbose_name="Comentario Padre")