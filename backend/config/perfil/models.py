from datetime import date
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


# ------------------------------------------------------------------------------------
# Modelo de perfil asociado a User mediante relación OneToOne.
# Este modelo amplía la información del usuario con datos adicionales que no
# pertenecen al modelo estándar de Django.
# ------------------------------------------------------------------------------------

class Genero(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO = 'F', 'Femenino'
    OTRO = 'O', 'Otro'


def avatar_path(instance, filename):
    # Cada usuario almacena su avatar en una carpeta propia.
    return f'users/{instance.user_id}/avatar/{filename}'


telefono_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='El teléfono debe contener entre 7 y 15 dígitos, opcionalmente empezando por +.'
)


class Perfil(models.Model):

    # Relación uno a uno con User. El perfil funciona como extensión del modelo de usuario.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        primary_key=True,
    )

    # Campos adicionales propios del perfil
    genero = models.CharField(max_length=1, choices=Genero.choices, default=Genero.MASCULINO)
    biografia = models.TextField(blank=True)
    moderator = models.BooleanField(default=False)  # Indica si el usuario actúa como moderador
    telefono = models.CharField(max_length=15, blank=True, validators=[telefono_validator])
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # Este campo se actualiza automáticamente cada vez que se modifica el perfil.
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Imagen de perfil subida por el usuario
    foto_perfil = models.ImageField(upload_to=avatar_path, null=True, blank=True)

    class Meta:
        # Se añaden índices para optimizar búsquedas por género y rol de moderador.
        indexes = [
            models.Index(fields=['moderator']),
            models.Index(fields=['genero']),
        ]

    def __str__(self):
        return f'Perfil de {self.user.username}'

    # Validaciones adicionales del modelo
    def clean(self):
        super().clean()

        if self.fecha_nacimiento:
            # La fecha de nacimiento no puede ser futura
            if self.fecha_nacimiento > date.today():
                raise ValidationError({
                    'fecha_nacimiento': 'La fecha de nacimiento no puede estar en el futuro.'
                })

            # Se establece una edad mínima para el uso del sistema
            min_age = 14
            edad = (date.today() - self.fecha_nacimiento).days // 365

            if edad < min_age:
                raise ValidationError({
                    'fecha_nacimiento': f'La edad mínima es {min_age} años.'
                })

    @property
    def edad(self):
        # Cálculo dinámico de la edad en función de la fecha de nacimiento
        if not self.fecha_nacimiento:
            return None

        today = date.today()
        return (
            today.year - self.fecha_nacimiento.year
            - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )


# Creación automática de un perfil asociado a cada nuevo usuario
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)