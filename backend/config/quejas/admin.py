
from django.contrib import admin
from .models import Queja

@admin.register(Queja)
class QuejaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "categoria", "fecha_creacion", "num_votos", "num_comentarios", "ubicacion")
    list_filter = ("estado", "categoria")
    search_fields = ("titulo", "descripcion")
    readonly_fields = ("fecha_creacion", "fecha_actualizacion")
