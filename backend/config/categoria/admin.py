from django.contrib import admin
from .models import Categoria

# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)
