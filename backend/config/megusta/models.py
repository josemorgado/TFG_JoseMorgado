from django.db import models, transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


    
class MeGustaQuerySet(models.QuerySet):
    def for_instance(self, obj):
        ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=obj.pk)
    
    def for_model_and_id(self, model, object_id):
        ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
        return self.filter(content_type=ct, object_id=object_id)
    
    def count_for(self, obj):
        return self.for_instance(obj).count()
    
    def is_liked_by(self, obj, user):
        if not user or not user.is_authenticated:
            return False
        return self.for_instance(obj).filter(autor=user).exists()
    
    def toggle_like(self, obj, user):
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
            # Por si hay condición de carrera con el UniqueConstraint
            return False, None
        
        
class MeGustaManager(models.Manager):
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
    
    
class MeGusta(models.Model):
    id = models.AutoField(primary_key=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    autor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='megustas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    objects = MeGustaManager()
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['content_type', 'object_id', 'autor'], name='unique_megusta_per_user_per_object')
        ]
        
    def __str__(self):
        return f'MeGusta by {self.autor} on {self.content_object}'
