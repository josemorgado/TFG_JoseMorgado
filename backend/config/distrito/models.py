from django.db import models

# Create your models here.

class Distrito(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nombre