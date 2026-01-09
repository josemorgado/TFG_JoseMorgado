from django.db import models

# Create your models here.


from django.db import models
from django.contrib.contenttypes.models import ContentType
from megusta.models import MeGusta


class EstadoQueja(models.TextChoices):
        PENDIENTE = 'PEN', 'Pendiente'
        EN_PROGRESO = 'ENP', 'En Progreso'
        RESUELTA = 'RES', 'Resuelta'
        RECHAZADA = 'REC', 'Rechazada'

class Queja(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey('categoria.Categoria', on_delete=models.CASCADE, related_name='quejas', null=False, blank=False)
    distrito = models.ForeignKey('distrito.Distrito', on_delete=models.CASCADE, related_name='quejas', null=False, blank=False)
    estado = models.CharField(max_length=3,choices= EstadoQueja.choices, default=EstadoQueja.PENDIENTE)
    ubicacion = models.CharField(max_length=255,blank=True, null=True)
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    #Este campo se actualizará mediante señales cuando se añadan o eliminen MeGusta o Comentarios
    #No se guarda en la base de datos, se calcula al vuelo
    @property
    def num_votos(self):
        ct = ContentType.objects.get_for_model(self, for_concrete_model=False)
        return MeGusta.objects.filter(content_type=ct, object_id=self.pk).count()
    num_comentarios = models.IntegerField(default=0)
    