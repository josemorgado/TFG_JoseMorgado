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
from datetime import date
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from drf_spectacular.utils import F


class Genero(models.TextChoices):
    """Opciones de género para el perfil de usuario."""
    MASCULINO = 'M', 'Masculino'
    FEMENINO  = 'F', 'Femenino'
    OTRO      = 'O', 'Otro'


def avatar_path(instance, filename):
    """
    Ruta de almacenamiento del avatar del usuario.
    Cada usuario guarda su avatar en su propia carpeta.
    """
    return f'users/{instance.user_id}/avatar/{filename}'


telefono_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='El teléfono debe contener entre 7 y 15 dígitos, opcionalmente empezando por +.'
)


class Perfil(models.Model):
    """
    Extensión del modelo de usuario (OneToOne) con información adicional:
    género, biografía, teléfono, dirección, fecha de nacimiento, avatar y
    bandera de moderador. Incluye validaciones de edad mínima.
    """

    # Relación uno a uno con User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        primary_key=True,
        help_text="Usuario propietario de este perfil."
    )

    # Campos adicionales del perfil
    genero = models.CharField(
        max_length=1,
        choices=Genero.choices,
        default=Genero.OTRO,
        help_text="Género del usuario."
    )
    biografia = models.TextField(
        blank=True,
        help_text="Descripción o biografía breve del usuario."
    )
    moderator = models.BooleanField(
        default=False,
        help_text="Indica si el usuario tiene rol de moderador."
    )
    telefono = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        validators=[telefono_validator],
        help_text="Teléfono de contacto en formato internacional (+NN...)."
    )
    direccion = models.CharField(
        max_length=255,
        blank=False,
        help_text="Dirección postal o de contacto."
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento del usuario."
    )

    # Trazabilidad
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última actualización del perfil."
    )

    # Imagen de perfil
    foto_perfil = models.ImageField(
        upload_to=avatar_path,
        null=True,
        blank=True,
        help_text="Avatar o foto de perfil del usuario."
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        indexes = [
            models.Index(fields=['moderator']),
            models.Index(fields=['genero']),
        ]

    def __str__(self):
        """Representación legible del perfil."""
        return f'Perfil de {self.user.username}'

    def clean(self):
        """
        Validaciones adicionales:
        - La fecha de nacimiento no puede ser futura.
        - Edad mínima de 14 años.
        """
        super().clean()

        if self.fecha_nacimiento:
            if self.fecha_nacimiento > date.today():
                raise ValidationError({
                    'fecha_nacimiento': 'La fecha de nacimiento no puede estar en el futuro.'
                })

            min_age = 14
            edad = (date.today() - self.fecha_nacimiento).days // 365
            if edad < min_age:
                raise ValidationError({
                    'fecha_nacimiento': f'La edad mínima es {min_age} años.'
                })

    @property
    def edad(self):
        """Edad calculada en años completos a partir de la fecha de nacimiento."""
        if not self.fecha_nacimiento:
            return None
        today = date.today()
        return (
            today.year - self.fecha_nacimiento.year
            - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un nuevo usuario."""
    if created:
        Perfil.objects.get_or_create(user=instance)