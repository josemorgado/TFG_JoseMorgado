# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAnonymousUser(BasePermission):
    """
    Permite acceso únicamente a usuarios NO autenticados.
    """
    def has_permission(self, request, view):
        # Necesita que la autenticación esté activa para distinguir correctamente
        return not (request.user and request.user.is_authenticated)


class IsModerator(BasePermission):
    """
    Permite acceso únicamente a usuarios autenticados con Perfil.moderator=True.
    """
    message = "Se requieren permisos de moderador."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        perfil = getattr(user, 'perfil', None)
        return bool(perfil and getattr(perfil, 'moderator', False))


class IsAuthorOrModerator(BasePermission):
    message = "Solo el autor o un moderador puede realizar esta acción."

    def has_permission(self, request, view):
        # Lecturas permitidas; escrituras exigen autenticación
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Autor si:
        # - obj.autor == user o obj.autor_id == user.id
        # - o el propio objeto es el User (id coincide)
        es_autor = (
            getattr(obj, 'autor_id', None) == user.id
            or getattr(obj, 'autor', None) == user
            or getattr(obj, 'id', None) == user.id  # si obj es User
        )
        es_moderador = getattr(getattr(user, 'perfil', None), 'moderator', False)
        return es_autor or es_moderador
