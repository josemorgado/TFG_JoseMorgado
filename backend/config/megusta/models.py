from django.db import models, transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# QuerySet personalizado para operar con likes
class MeGustaQuerySet(models.QuerySet):

    def for_instance(self, obj):
        # Devuelve los 'me gusta' asociados a una instancia concreta
        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=obj.pk)

    def for_model_and_id(self, model, object_id):
        # Devuelve los 'me gusta' filtrados por modelo y su ID
        ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=object_id)

    def count_for(self, obj):
        # Cuenta los 'me gusta' de una instancia
        return self.for_instance(obj).count()

    def is_liked_by(self, obj, user):
        # Comprueba si el usuario ha dado 'me gusta' a la instancia
        if not user or not user.is_authenticated:
            return False
        return self.for_instance(obj).filter(autor=user).exists()

    def toggle_like(self, obj, user):
        # Alterna entre agregar o quitar un 'me gusta'
        if not user or not user.is_authenticated:
            return None

        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)

        try:
            # Bloque atómico para evitar condiciones de carrera
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
            # Seguridad ante conflictos con la restricción de unicidad
            return False, None


# Manager principal basado en el QuerySet personalizado
class MeGustaManager(models.Manager):

    def get_queryset(self):
        # Devuelve el QuerySet personalizado
        return MeGustaQuerySet(self.model, using=self._db)

    def for_instance(self, obj):
        # Proxies hacia el queryset
        return self.get_queryset().for_instance(obj)

    def for_model_and_id(self, model, object_id):
        # Proxy
        return self.get_queryset().for_model_and_id(model, object_id)

    def count_for(self, obj):
        # Proxy
        return self.get_queryset().count_for(obj)

    def is_liked_by(self, obj, user):
        # Proxy
        return self.get_queryset().is_liked_by(obj, user)

    def toggle_like(self, obj, user):
        # Proxy
        return self.get_queryset().toggle_like(obj, user)


class MeGusta(models.Model):
    id = models.AutoField(primary_key=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='megustas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = MeGustaManager()

    class Meta:
        # Garantiza que un usuario solo pueda dar un 'me gusta' por objeto
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'autor'],
                name='unique_megusta_per_user_per_object'
            )
        ]
        # Índice para consultas rápidas
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'MeGusta by {self.autor} on {self.content_object}'