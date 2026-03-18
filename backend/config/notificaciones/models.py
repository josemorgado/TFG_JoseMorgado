from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"