from django.db import models

class Categoria(models.Model):
    """
    Modelo que representa una categoría utilizada para clasificar incidencias
    dentro de la aplicación 'Alcalde Escúchame'.
    """

    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único de la categoría."
    )
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre visible de la categoría. Ejemplo: 'Transporte', 'Limpieza', etc."
    )
    descripcion = models.TextField(
        help_text="Descripción breve que explica el propósito de la categoría."
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si la categoría está activa y disponible para su uso."
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["id"]  # ayuda a Swagger a mostrar respuestas ordenadas

    def __str__(self):
        return self.nombre