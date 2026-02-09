from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.

class Perfil(models.Model):
    id=models.AutoField(primary_key=True)
    user= models.OneToOneField('auth.User', on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100, blank=True)
    genero = models.BooleanField(null=False,default=True)  # True para masculino, False para femenino
    apellido_1 = models.CharField(max_length=50, blank=True)
    apellido_2 = models.CharField(max_length=50, blank=True)
    biografia = models.TextField(blank=True)
    moderator = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    foto_perfil = models.ImageField(upload_to='media/fotos_perfil/', null=True, blank=True)
    
    def __str__(self):
        return f'Perfil de {self.user.username}'
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Verificamos si el perfil ya existe ANTES de intentar nada
        # Esto sucede porque el Admin a veces es más rápido que el signal
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(user=instance)     
        
