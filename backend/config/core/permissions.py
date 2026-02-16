# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsModerator(BasePermission):
    """
    Permite acceso únicamente a usuarios autenticados con Perfil.moderator=True.
    """
    message = "Se requieren permisos de moderador."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        try:
            # user.perfil proviene de tu OneToOne con related_name='perfil'
            return bool(getattr(user, 'perfil', None) and user.perfil.moderator)
        except Exception:
            # Si no existe Perfil por alguna razón, denegamos.
            return False


class IsAuthorOrModerator(BasePermission):
    """
    Permite acceso si el usuario es el autor del objeto o si es moderador.
    Útil para vistas a nivel de objeto (APIView/GenericView/ViewSet).
    En FBV (function-based views), puedes replicar la misma lógica inline.
    """
    message = "Solo el autor o un moderador puede realizar esta acción."

    def has_object_permission(self, request, view, obj):
        # Permite lecturas sin restricción (si quieres que este permiso maneje también lectura)
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        try:
            es_autor = (getattr(obj, 'autor_id', None) == user.id) or (getattr(obj, 'autor', None) == user)
            es_moderador = getattr(getattr(user, 'perfil', None), 'moderator', False)
            return es_autor or es_moderador
        except Exception:
            return False