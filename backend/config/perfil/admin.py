# perfil/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import Perfil

User = get_user_model()

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = (
        "id_col",
        "user_username",
        "user_email",
        "user_first_name",
        "user_last_name",
        "user_is_staff",
        "genero",
        "moderator",
        "telefono",
        "fecha_nacimiento",
        "fecha_actualizacion",
        "foto_thumb",
        "ver_usuario",
    )
    # Enlaza con la columna virtual que sí está en list_display
    list_display_links = ("id_col", "user_username")
    list_select_related = ("user",)
    # Usa pk en lugar de id
    ordering = ("-fecha_actualizacion", "-pk")

    list_filter = (
        "genero",
        "moderator",
        ("user__is_staff", admin.BooleanFieldListFilter),
        ("user__is_active", admin.BooleanFieldListFilter),
        ("user__is_superuser", admin.BooleanFieldListFilter),
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "telefono",
        "direccion",
        "biografia",
    )
    autocomplete_fields = ("user",)
    readonly_fields = ("fecha_actualizacion", "foto_preview")

    fieldsets = (
        ("Usuario", {"fields": ("user",)}),
        ("Perfil", {"fields": ("genero", "moderator", "biografia")}),
        ("Contacto", {"fields": ("telefono", "direccion")}),
        ("Datos personales", {"fields": ("fecha_nacimiento",)}),
        ("Imagen", {"fields": ("foto_perfil", "foto_preview")}),
        ("Metadatos", {"fields": ("fecha_actualizacion",)}),
    )

    # --- Columna virtual "ID" basada en la PK compartida ---
    def id_col(self, obj):
        return obj.pk  # = obj.user_id
    id_col.short_description = "ID"
    id_col.admin_order_field = "pk"  # permite ordenar al pulsar en el encabezado

    # ---- Exponer campos del User (callables) ----
    def user_username(self, obj):
        return obj.user.username if obj.user_id else "—"
    user_username.short_description = "Usuario"
    user_username.admin_order_field = "user__username"

    def user_email(self, obj):
        return obj.user.email if obj.user_id else "—"
    user_email.short_description = "Email"
    user_email.admin_order_field = "user__email"

    def user_first_name(self, obj):
        return obj.user.first_name if obj.user_id else "—"
    user_first_name.short_description = "Nombre"
    user_first_name.admin_order_field = "user__first_name"

    def user_last_name(self, obj):
        return obj.user.last_name if obj.user_id else "—"
    user_last_name.short_description = "Apellidos"
    user_last_name.admin_order_field = "user__last_name"

    def user_is_staff(self, obj):
        return bool(obj.user.is_staff) if obj.user_id else False
    user_is_staff.boolean = True
    user_is_staff.short_description = "Staff"
    user_is_staff.admin_order_field = "user__is_staff"

    # ---- Miniatura y preview de la foto ----
    def foto_thumb(self, obj):
        if obj.foto_perfil:
            return format_html(
                '<img src="{}" style="height:28px;width:28px;object-fit:cover;border-radius:50%;">',
                obj.foto_perfil.url
            )
        return "—"
    foto_thumb.short_description = "Foto"

    def foto_preview(self, obj):
        if obj.pk and obj.foto_perfil:
            return format_html(
                '<img src="{}" style="max-height:180px;max-width:180px;border-radius:6px;">',
                obj.foto_perfil.url
            )
        return "Sin imagen"
    foto_preview.short_description = "Vista previa"

    # ---- Link rápido al User desde Perfil ----
    def ver_usuario(self, obj):
        if not obj.user_id:
            return "—"
        return format_html(
            '<a href="/admin/{}/{}/{}/change/" title="Abrir usuario">Ver usuario</a>',
            User._meta.app_label,
            User._meta.model_name,
            obj.user_id
        )
    ver_usuario.short_description = "Usuario (link)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")