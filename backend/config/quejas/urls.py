# quejas/urls.py
from django.urls import path
from quejas.views import (
    quejas_list,
    queja_detail,
    queja_create,
    queja_update,
    queja_delete,
    quejas_por_categoria,
    quejas_por_distrito,
    quejas_por_autor,
    queja_cambiar_estado,
)

urlpatterns = [
    # GET               /quejas/
    path('', quejas_list, name='queja-list'),

    # GET               /quejas/<int:pk>/
    path('<int:pk>/', queja_detail, name='queja-detail'),

    # POST              /quejas/create/
    path('create/', queja_create, name='queja-create'),

    # PUT               /quejas/<int:pk>/update/
    path('<int:pk>/update/', queja_update, name='queja-update'),

    # DELETE            /quejas/<int:pk>/delete/
    path('<int:pk>/delete/', queja_delete, name='queja-delete'),

    # GET               /quejas/categoria/<int:categoria_id>/
    path('categoria/<int:categoria_id>/', quejas_por_categoria, name='quejas-por-categoria'),

    # GET               /quejas/distrito/<int:distrito_id>/
    path('distrito/<int:distrito_id>/', quejas_por_distrito, name='quejas-por-distrito'),

    # GET               /quejas/autor/<int:autor_id>/
    path('autor/<int:autor_id>/', quejas_por_autor, name='quejas-por-autor'),

    # PATCH             /quejas/<int:pk>/estado/
    path('<int:pk>/estado/', queja_cambiar_estado, name='queja-cambiar-estado'),
]