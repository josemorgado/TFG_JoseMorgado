from datetime import date
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# Opciones de género como TextChoices
class Genero(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO  = 'F', 'Femenino'
    OTRO      = 'O', 'Otro'


# Ruta de almacenamiento para el avatar del usuario
def avatar_path(instance, filename):
    # Cada usuario almacena su avatar en una carpeta propia
    return f'users/{instance.user_id}/avatar/{filename}'


# Validador para el campo teléfono
telefono_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='El teléfono debe contener entre 7 y 15 dígitos, opcionalmente empezando por +.'
)

# Campos heredados de User:
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

class Perfil(models.Model):

    # Relación uno a uno con User, actuando como extensión del modelo de usuario
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        primary_key=True,
    )

    # Campos adicionales del perfil
    genero = models.CharField(max_length=1, choices=Genero.choices, default=Genero.MASCULINO)
    biografia = models.TextField(blank=True)
    moderator = models.BooleanField(default=False)  # Indica si el usuario es moderador
    telefono = models.CharField(max_length=15, blank=True, validators=[telefono_validator])
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # Fecha de última actualización del perfil
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Imagen de perfil subida por el usuario
    foto_perfil = models.ImageField(upload_to=avatar_path, null=True, blank=True)

    class Meta:
        # Índices para optimizar consultas
        indexes = [
            models.Index(fields=['moderator']),
            models.Index(fields=['genero']),
        ]

    def __str__(self):
        # Representación legible del perfil en panel admin y logs
        return f'Perfil de {self.user.username}'

    # Validaciones adicionales del modelo
    def clean(self):
        super().clean()

        if self.fecha_nacimiento:
            # La fecha de nacimiento no puede estar en el futuro
            if self.fecha_nacimiento > date.today():
                raise ValidationError({
                    'fecha_nacimiento': 'La fecha de nacimiento no puede estar en el futuro.'
                })

            # Validación de edad mínima
            min_age = 14
            edad = (date.today() - self.fecha_nacimiento).days // 365

            if edad < min_age:
                raise ValidationError({
                    'fecha_nacimiento': f'La edad mínima es {min_age} años.'
                })

    @property
    def edad(self):
        # Cálculo dinámico de edad basado en la fecha de nacimiento
        if not self.fecha_nacimiento:
            return None

        today = date.today()
        return (
            today.year - self.fecha_nacimiento.year
            - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )


# Crea automáticamente un perfil para cada usuario nuevo
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)