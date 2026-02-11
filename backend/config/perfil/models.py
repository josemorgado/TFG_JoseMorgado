from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# ------------------------------------------------------------------------------------
# Atributos del modelo User (no duplicar en Perfil):
# - username
# - password
# - first_name
# - last_name
# - email
# - is_staff
# - is_active
# - is_superuser
# - last_login
# - date_joined
# - groups
# - user_permissions
# ------------------------------------------------------------------------------------
class Genero(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO = 'F', 'Femenino'
    OTRO = 'O', 'Otro'

class Perfil(models.Model):
    # Usa el AUTH_USER_MODEL y permite acceder como user.perfil
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        primary_key=True,
    )

    # Campos propios del perfil (extras respecto a User)
    genero = models.CharField(max_length=1, choices=Genero.choices, default=Genero.MASCULINO)    
    biografia = models.TextField(blank=True)
    moderator = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'perfil'):
        Perfil.objects.create(user=instance)

        
   