from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Perfil

User = get_user_model()


# -------------------------------
# Inline que aparecerá en admin de User
# -------------------------------
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    fk_name = 'user'
    extra = 0
    verbose_name_plural = 'Perfil'
    readonly_fields = ('fecha_actualizacion', 'foto_preview')

    def foto_preview(self, obj):
        if obj and obj.foto_perfil:
            return format_html(
                '{}',
                obj.foto_perfil.url
            )
        return "(Sin foto)"
    foto_preview.short_description = "Vista previa"


# -------------------------------
# Registramos User con el inline
# -------------------------------
# 1. Desregistramos el User original del admin
admin.site.unregister(User)

# 2. Lo registramos de nuevo con nuestro inline añadido
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)