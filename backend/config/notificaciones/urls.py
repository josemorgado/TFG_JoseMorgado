# notificaciones/urls.py
from django.urls import path
from .views import  (
    notification_create,
    notification_delete,
    notification_list,
    notification_mark_all_read,
    notification_mark_read,
    notification_mark_unread,
    notification_unread_count
)

urlpatterns = [
    # Listado paginado + filtros (?is_read=true|false, page, page_size)
    path("notificaciones/", notification_list, name="notification_list"),
    # Contador de no leídas
    path(
        "notificaciones/unread-count/",
        notification_unread_count,
        name="notification_unread_count",
    ),
    # Marcar todas como leídas
    path(
        "notificaciones/read-all/",
        notification_mark_all_read,
        name="notification_mark_all_read",
    ),
    # Marcar una como leída
    path(
        "notificaciones/<int:notification_id>/read/",
        notification_mark_read,
        name="notification_mark_read",
    ),
    # Marcar una como NO leída
    path(
        "notificaciones/<int:notification_id>/unread/",
        notification_mark_unread,
        name="notification_mark_unread",
    ),
    # Eliminar una
    path(
        "notificaciones/<int:notification_id>/",
        notification_delete,
        name="notification_delete",
    ),
    # Crear (admin)
    path(
        "notificaciones/create/", notification_create, name="notification_create"
    ),
]
