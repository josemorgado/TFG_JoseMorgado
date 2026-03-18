from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notificacion
        fields = ['id', 'user', 'title', 'message', 'created_at', 'is_read', 'url']
        read_only_fields = ['id', 'created_at', 'user']


class NotificacionCreateSerializer(serializers.ModelSerializer):
    """
    Útil para endpoints internos o de admin que creen notificaciones para otro usuario.
    Mantén control con permisos.
    """
    class Meta:
        model = Notificacion
        fields = ['id', 'user', 'title', 'message', 'url']
        read_only_fields = ['id']