from django.urls import path
from .views import (
    imagen_list,
    imagen_detail,
    imagenes_por_comentario,
    imagenes_por_queja,
    imagen_create,#necesita testing
    imagen_delete,

)

urlpatterns = [
    path('', imagen_list),                                                  # GET    /imagenes/
    path('<int:pk>/', imagen_detail),                                       # GET    /imagenes/<pk>/
    path('queja/<int:queja_id>/', imagenes_por_queja),                      # GET /imagenes/queja/<id>/
    path('comentario/<int:comentario_id>/', imagenes_por_comentario),       # GET /imagenes/comentario/<id>/
    path('create/', imagen_create),                                         # POST   /imagenes/create/
    path('<int:pk>/delete/', imagen_delete),                                # DELETE /imagenes/<pk>/delete/
]