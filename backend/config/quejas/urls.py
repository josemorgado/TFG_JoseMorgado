
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
    path('', quejas_list),                              # GET /quejas/
    path('<int:pk>/', queja_detail),                    # GET /quejas/<pk>/
    path('create/', queja_create),                      # POST /quejas/create/
    path('<int:pk>/update/', queja_update),             # PUT /quejas/<pk>/update/
    path('<int:pk>/delete/', queja_delete),             # DELETE /quejas/<pk>/delete/
    path('categoria/<int:categoria_id>/', quejas_por_categoria),  # GET /quejas/categoria/<id>/
    path('distrito/<int:distrito_id>/', quejas_por_distrito),     # GET /quejas/distrito/<id>/
    path('autor/<int:autor_id>/', quejas_por_autor),              # GET /quejas/autor/<id>/
    path('<int:pk>/estado/', queja_cambiar_estado),               # PATCH /quejas/<pk>/estado/
]
