from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Imagen

# ---------- Utilidades ----------

def _thumbnail(obj, size=80):
    """
    Devuelve un <img> pequeño para visualizar la imagen si existe.
    """
    try:
        if obj.imagen and hasattr(obj.imagen, 'url'):
            return format_html(
                '<img src="{}" style="height:{}px;width:auto;border-radius:8px;" />',
                obj.imagen.url, size
            )
    except Exception:
        pass
    return "—"


# ---------- Admin principal para Imagen ----------

@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'content_type',       # tipo del objeto: queja, comentario, etc.
        'object_id',          # id del objeto objetivo
        'preview',            # miniatura
        'orden',
        'fecha_creacion',
    )
    list_filter = (
        ('content_type', admin.RelatedOnlyFieldListFilter),
        'fecha_creacion',
    )
    search_fields = (
        'object_id',
    )
    readonly_fields = ('preview', 'fecha_creacion')
    ordering = ('content_type', 'object_id', 'orden', 'id')
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id', 'imagen', 'orden', 'preview')
        }),
        ('Metadatos', {
            'classes': ('collapse',),
            'fields': ('fecha_creacion',)
        }),
    )

    def preview(self, obj):
        return _thumbnail(obj)
