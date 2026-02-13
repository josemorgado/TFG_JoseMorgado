from django.db import models

long_minima_codigo = 2
long_minima_nombre = 3
long_max_codigo = 10
long_max_nombre = 100

class Distrito(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=long_max_nombre, unique=True)
    codigo = models.CharField(max_length=long_max_codigo, unique=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        # NOTA: se normaliza el nombre para mantener consistencia en la base de datos.
        if self.nombre:
            self.nombre = self.nombre.strip()

        # NOTA: se asegura que el código se guarde siempre en MAYÚSCULAS para evitar duplicados lógicos.
        if self.codigo:
            self.codigo = self.codigo.strip().upper()

        # NOTA: se valida longitud mínima para evitar códigos demasiado cortos.
        if self.codigo and len(self.codigo) < long_minima_codigo:
            raise ValueError(f"El código debe tener al menos {long_minima_codigo} caracteres.")
        
        # NOTA: se valida longitud mínima del nombre para evitar nombres demasiado genéricos.
        if self.nombre and len(self.nombre) < long_minima_nombre:
            raise ValueError(f"El nombre debe tener al menos {long_minima_nombre} caracteres.")
        
        # NOTA: se valida longitud máxima para evitar códigos demasiado largos.
        if self.codigo and len(self.codigo) > long_max_codigo:
            raise ValueError(f"El código no puede tener más de {long_max_codigo} caracteres.")
        
        # NOTA: se valida longitud máxima del nombre para evitar nombres excesivamente largos.
        if self.nombre and len(self.nombre) > long_max_nombre:
            raise ValueError(f"El nombre no puede tener más de {long_max_nombre} caracteres.")