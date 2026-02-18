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


class IsModeratorOrRelatedQuejaAuthor(BasePermission):
    """
    Permite la acción si el usuario es moderador o es el autor de la queja relacionada
    con el objeto (directamente si es una Queja, o indirectamente si el objeto es un
    Comentario que cuelga de una Queja).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Define aquí tu criterio de moderador
        is_moderator = getattr(user, 'is_moderator', False) or user.is_staff or user.is_superuser
        if is_moderator:
            return True

        # Obtenemos el objeto genérico asociado a la imagen
        related = getattr(obj, 'content_object', None)
        if related is None:
            return False

        # Caso 1: la imagen cuelga de una Queja -> related.autor
        # (No dependemos del nombre exacto de la clase; duck typing por atributos)
        if hasattr(related, 'autor'):
            # Si es una queja, debería bastar con autor
            try:
                return related.autor_id == user.id
            except Exception:
                pass  # por si related.autor no es FK convencional

        # Caso 2: la imagen cuelga de un Comentario -> related.queja.autor
        if hasattr(related, 'queja') and hasattr(related.queja, 'autor_id'):
            try:
                return related.queja.autor_id == user.id
            except Exception:
                pass

        return False
