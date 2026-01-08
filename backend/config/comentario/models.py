from django.db import models

# Create your models here.

class Comentario(models.Model):
    id = models.AutoField(primary_key=True)
    queja = models.ForeignKey('quejas.Queja', on_delete=models.CASCADE, related_name='comentarios')
    #autor = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    num_votos = models.IntegerField(default=0)