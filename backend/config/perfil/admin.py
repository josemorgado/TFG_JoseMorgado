from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Perfil

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Información Detallada del Perfil'
    fk_name = 'user'
    
    fieldsets = (
        ('Datos Personales', {
            'fields': ('nombre_completo', ('apellido_1', 'apellido_2'), 'fecha_nacimiento', 'foto_perfil', 'genero', 'moderator')
        }),
        ('Contacto y Ubicación', {
            'fields': (('telefono', 'direccion', 'email'),)
        }),
        ('Contenido', {
            'fields': ('biografia',)
        }),
    )

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    
    list_display = ('thumbnail_foto', 'username', 'email', 'full_name_custom', 'get_telefono', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'perfil__telefono', 'perfil__nombre_completo')
    ordering = ('-date_joined',)

    def full_name_custom(self, obj):
        # Añadimos try/except por seguridad si un usuario antiguo no tiene perfil
        try:
            return f"{obj.perfil.nombre_completo} {obj.perfil.apellido_1}"
        except Perfil.DoesNotExist:
            return ""
    full_name_custom.short_description = 'Nombre Real'

    def get_telefono(self, obj):
        try:
            return obj.perfil.telefono
        except Perfil.DoesNotExist:
            return ""
    get_telefono.short_description = 'Teléfono'

    def thumbnail_foto(self, obj):
        try:
            if obj.perfil.foto_perfil:
                return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.perfil.foto_perfil.url)
        except Perfil.DoesNotExist:
            pass
        return format_html('<img src="https://ui-avatars.com/api/?name={}&background=random" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.username)
    thumbnail_foto.short_description = 'Foto'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)