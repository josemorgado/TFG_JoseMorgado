from django.db import models, transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# ============================================================
# QuerySet personalizado con operaciones de 'Me Gusta'
# ============================================================
class MeGustaQuerySet(models.QuerySet):
    """
    QuerySet personalizado para operaciones sobre likes:
    - Obtención por instancia
    - Conteo
    - Comprobación de si un usuario ha dado like
    - Alternancia (toggle) de like
    """

    def for_instance(self, obj):
        """Devuelve los 'me gusta' asociados a una instancia concreta."""
        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=obj.pk)

    def for_model_and_id(self, model, object_id):
        """Devuelve likes para un modelo específico y un ID concreto."""
        ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=object_id)

    def count_for(self, obj):
        """Cuenta cuántos likes tiene una instancia."""
        return self.for_instance(obj).count()

    def is_liked_by(self, obj, user):
        """Determina si un usuario ha dado like a una instancia."""
        if not user or not user.is_authenticated:
            return False
        return self.for_instance(obj).filter(autor=user).exists()

    def toggle_like(self, obj, user):
        """
        Alterna entre agregar o eliminar un like.
        Devuelve:
            (True, instance)  -> se creó
            (False, None)     -> se eliminó
        """
        if not user or not user.is_authenticated:
            return None

        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)

        try:
            with transaction.atomic():
                instance, created = self.get_or_create(
                    autor=user,
                    content_type=ct,
                    object_id=obj.pk
                )

                if not created:
                    instance.delete()

                return created, (instance if created else None)

        except IntegrityError:
            # Protege contra condiciones de carrera y violaciones de unicidad
            return False, None


# ============================================================
# Manager principal basado en el QuerySet personalizado
# ============================================================
class MeGustaManager(models.Manager):
    """Manager principal que expone métodos utilitarios basados en MeGustaQuerySet."""

    def get_queryset(self):
        return MeGustaQuerySet(self.model, using=self._db)

    def for_instance(self, obj):
        return self.get_queryset().for_instance(obj)

    def for_model_and_id(self, model, object_id):
        return self.get_queryset().for_model_and_id(model, object_id)

    def count_for(self, obj):
        return self.get_queryset().count_for(obj)

    def is_liked_by(self, obj, user):
        return self.get_queryset().is_liked_by(obj, user)

    def toggle_like(self, obj, user):
        return self.get_queryset().toggle_like(obj, user)


# ============================================================
# Modelo principal MeGusta
# ============================================================
class MeGusta(models.Model):
    """
    Representa un 'me gusta' asociado dinámicamente a una queja o comentario,
    mediante ContentType. Garantiza que cada usuario solo pueda dar un like
    por objeto.
    """

    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único del MeGusta."
    )

    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        help_text="Modelo al que está asociado el Like (queja/comentario)."
    )

    object_id = models.PositiveIntegerField(
        help_text="ID del objeto dentro del modelo asociado."
    )

    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    autor = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='megustas',
        help_text="Usuario que dio el 'me gusta'."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en la que se realizó el 'me gusta'."
    )

    objects = MeGustaManager()

    class Meta:
        verbose_name = "Me Gusta"
        verbose_name_plural = "Me Gustas"
        # Unicidad: un usuario solo puede dar un like por objeto
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'autor'],
                name='unique_megusta_per_user_per_object'
            )
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"MeGusta by {self.autor} on {self.content_object}"