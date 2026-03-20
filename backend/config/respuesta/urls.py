# respuesta/urls.py
from django.urls import path
from .views import (
    respuestas_listar,
    respuesta_crear,
    respuesta_detalle_publico,
    respuesta_admin,
)

urlpatterns = [
    # Listado público de respuestas por queja
    path('quejas/<int:queja_id>/respuestas/', respuestas_listar, name='respuestas-por-queja'),

    # Crear respuesta (SOLO moderadores)
    path('quejas/<int:queja_id>/respuestas/crear/', respuesta_crear, name='respuesta-crear'),

    # Detalle público de una respuesta
    path('respuestas/<int:respuesta_id>/', respuesta_detalle_publico, name='respuesta-detalle-publico'),

    # Editar/Eliminar (SOLO moderadores)
    path('respuestas/<int:respuesta_id>/admin/', respuesta_admin, name='respuesta-admin'),
]
