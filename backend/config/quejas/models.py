from django.db import models

# Create your models here.

class EstadoQueja(models.TextChoices):
        PENDIENTE = 'PEN', 'Pendiente'
        EN_PROGRESO = 'ENP', 'En Progreso'
        RESUELTA = 'RES', 'Resuelta'
        RECHAZADA = 'REC', 'Rechazada'

class Queja(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    #categoria_id = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    #distrito_id = models.ForeignKey('Distrito', on_delete=models.CASCADE)
    estado = models.CharField(max_length=3,choices= EstadoQueja.choices, default=EstadoQueja.PENDIENTE)
    ubicacion = models.CharField(max_length=255,blank=True, null=True)
    #autor_id = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    num_votos = models.IntegerField(default=0)
    num_comentarios = models.IntegerField(default=0)
    