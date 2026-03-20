# respuesta/admin.py
from django.contrib import admin
from .models import Respuesta

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ("id", "queja", "moderador", "nuevo_estado", "fecha_respuesta")
    list_filter = ("nuevo_estado", "fecha_respuesta")
    search_fields = ("queja__titulo", "moderador__username", "contenido")