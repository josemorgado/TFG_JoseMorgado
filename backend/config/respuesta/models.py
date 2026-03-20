# respuesta/models.py
from django.db import models
from django.conf import settings
from quejas.models import Queja, EstadoQueja

class Respuesta(models.Model):
    queja = models.ForeignKey(
        Queja,
        on_delete=models.CASCADE,
        related_name="respuestas",
        help_text="Queja a la que responde el moderador."
    )
    moderador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="respuestas_moderadas",
        help_text="Moderador que emitió la respuesta."
    )
    contenido = models.TextField(help_text="Texto completo de la respuesta oficial.")
    nuevo_estado = models.CharField(
        max_length=3,
        choices=EstadoQueja.choices,
        null=True,
        blank=True,
        help_text="Estado al que pasa la queja tras esta respuesta (opcional)."
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_respuesta']
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        indexes = [
            models.Index(fields=['queja']),
            models.Index(fields=['-fecha_respuesta']),
            models.Index(fields=['nuevo_estado']),
        ]

    def __str__(self):
        return f"Respuesta #{self.id} a queja #{self.queja_id}"