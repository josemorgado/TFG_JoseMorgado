from django.contrib import admin

# Register your models here.
from .models import Comentario

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'queja', 'contenido', 'fecha_creacion', 'num_votos', 'parent')
    search_fields = ('contenido',)
    list_filter = ('fecha_creacion','queja','parent')