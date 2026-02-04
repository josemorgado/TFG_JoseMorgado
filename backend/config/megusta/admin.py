from django.contrib import admin

# Register your models here.
from .models import MeGusta

@admin.register(MeGusta)
class MeGustaAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'autor', 'fecha_creacion')
    search_fields = ('autor__username', 'content_type__model')
    list_filter = ('fecha_creacion','content_type','object_id')