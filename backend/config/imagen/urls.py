# imagen/urls.py
from django.urls import path
from .views import (
    imagen_list,
    imagen_detail,
    imagenes_por_comentario,
    imagenes_por_queja,
    imagen_create,  # necesita testing
    imagen_delete,
)

urlpatterns = [
    # GET               /imagenes/
    path('', imagen_list, name='imagen-list'),

    # GET               /imagenes/<int:pk>/
    path('<int:pk>/', imagen_detail, name='imagen-detail'),

    # GET               /imagenes/queja/<int:queja_id>/
    path('queja/<int:queja_id>/', imagenes_por_queja, name='imagenes-por-queja'),

    # GET               /imagenes/comentario/<int:comentario_id>/
    path('comentario/<int:comentario_id>/', imagenes_por_comentario, name='imagenes-por-comentario'),

    # POST              /imagenes/create/
    path('create/', imagen_create, name='imagen-create'),

    # DELETE            /imagenes/<int:pk>/delete/
    path('<int:pk>/delete/', imagen_delete, name='imagen-delete'),
]