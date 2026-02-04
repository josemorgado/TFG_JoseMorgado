from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html
from .models import Video

class VideoInline(GenericTabularInline):
    model = Video
    extra = 1
    max_num = 2  
    fields = ('video', 'orden', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_content_object', 'preview_video', 'orden', 'fecha_creacion')
    list_filter = ('content_type', 'fecha_creacion')
    search_fields = ('object_id',)
    readonly_fields = ('fecha_creacion', 'preview_video_full')
    
    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id', 'video', 'orden')
        }),
        ('Vista Previa y Metadatos', {
            'fields': ('preview_video_full', 'fecha_creacion'),
        }),
    )

    @admin.display(description="Objeto Asociado")
    def display_content_object(self, obj):
        """Muestra qué tipo de objeto es y su ID"""
        if obj.content_object:
            return f"{obj.content_type.model.upper()}: {obj.content_object}"
        return f"{obj.content_type.model.upper()} (ID: {obj.object_id})"

    @admin.display(description="Miniatura")
    def preview_video(self, obj):
        """Reproductor pequeño para la lista general"""
        if obj.video:
            return format_html(
                '<video width="120" height="80" style="border-radius:5px; background:#000;">'
                '<source src="{0}">'
                '</video>',
                obj.video.url
            )
        return "No hay archivo"

    @admin.display(description="Reproductor")
    def preview_video_full(self, obj):
        """Reproductor grande para la ficha de edición"""
        if obj.video:
            return format_html(
                '<video width="400" controls style="border: 1px solid #ccc;">'
                '<source src="{0}">'
                'Tu navegador no soporta la reproducción de video.'
                '</video>',
                obj.video.url
            )
        return "Sube un video para activarlo"