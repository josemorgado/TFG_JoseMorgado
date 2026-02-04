from django.contrib import admin

# Register your models here.

from .models import Distrito

@admin.register(Distrito)
class DistritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo')
    search_fields = ('nombre',)
    list_filter = ('nombre',)
