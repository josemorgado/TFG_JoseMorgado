from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

MAX_VIDEOS = 1
# Funcion para definir la ruta de acceso al video
def media_upload_to(instance, filename):
    tipo = instance.content_type.model
    return f'media/{tipo}/{instance.object_id}/videos/{filename}'

class Video(models.Model):
    id = models.BigAutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    video = models.FileField(upload_to=media_upload_to)
    orden = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['orden', 'fecha_creacion']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['content_type', 'object_id', 'orden'], name='unique_video_order_per_object')
        ]
        
    def clean(self):
        # Validar el numero maximo de videos por objeto
        if self.pk is None:
            total = Video.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id
            ).count()
            if total >= MAX_VIDEOS:
                raise ValidationError(
                    _(f'Solo se permiten un maximo de {MAX_VIDEOS} videos por objeto.')
                )
                
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'Video {self.id} para {self.content_object} (Orden: {self.orden})'
            
    

       
    
