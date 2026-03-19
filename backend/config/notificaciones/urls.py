# notificaciones/urls.py
from django.urls import path
from .views import (
    notification_create,
    notification_delete,
    notification_list,
    notification_mark_all_read,
    notification_mark_read,
    notification_mark_unread,
    notification_unread_count,
)

urlpatterns = [
    # Listado paginado + filtros (?is_read=true|false, page, page_size)
    path("", notification_list, name="notification_list"),
    # Contador de no leídas
    path(
        "unread-count/",
        notification_unread_count,
        name="notification_unread_count",
    ),
    # Marcar todas como leídas
    path(
        "read-all/",
        notification_mark_all_read,
        name="notification_mark_all_read",
    ),
    # Marcar una como leída
    path(
        "<int:notification_id>/read/",
        notification_mark_read,
        name="notification_mark_read",
    ),
    # Marcar una como NO leída
    path(
        "<int:notification_id>/unread/",
        notification_mark_unread,
        name="notification_mark_unread",
    ),
    # Eliminar una
    path(
        "<int:notification_id>/",
        notification_delete,
        name="notification_delete",
    ),
    # Crear (admin)
    path("create/", notification_create, name="notification_create"),
]
