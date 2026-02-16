from django.db import models

long_minima_codigo = 2
long_minima_nombre = 3
long_max_codigo = 10
long_max_nombre = 100


class Distrito(models.Model):
    """
    Representa un distrito dentro de la aplicación.
    Cada distrito posee un nombre y un código únicos,
    utilizados para clasificar y localizar incidencias.
    """

    id = models.AutoField(
        primary_key=True,
        help_text="Identificador único del distrito."
    )

    nombre = models.CharField(
        max_length=long_max_nombre,
        unique=True,
        help_text=f"Nombre del distrito. Mínimo {long_minima_nombre} caracteres."
    )

    codigo = models.CharField(
        max_length=long_max_codigo,
        unique=True,
        help_text=f"Código identificativo del distrito. Mínimo {long_minima_codigo} caracteres. Se almacena en mayúsculas."
    )

    def __str__(self):
        return self.nombre

    def clean(self):
        """Normaliza y valida los datos antes de guardar."""
        # Normaliza nombre
        if self.nombre:
            self.nombre = self.nombre.strip()

        # Código siempre en mayúsculas
        if self.codigo:
            self.codigo = self.codigo.strip().upper()

        # Validaciones mínimas
        if self.codigo and len(self.codigo) < long_minima_codigo:
            raise ValueError(f"El código debe tener al menos {long_minima_codigo} caracteres.")

        if self.nombre and len(self.nombre) < long_minima_nombre:
            raise ValueError(f"El nombre debe tener al menos {long_minima_nombre} caracteres.")

        # Validaciones máximas
        if self.codigo and len(self.codigo) > long_max_codigo:
            raise ValueError(f"El código no puede tener más de {long_max_codigo} caracteres.")

        if self.nombre and len(self.nombre) > long_max_nombre:
            raise ValueError(f"El nombre no puede tener más de {long_max_nombre} caracteres.")

    class Meta:
        verbose_name = "Distrito"
        verbose_name_plural = "Distritos"
        ordering = ["id"]