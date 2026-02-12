from django.urls import path
from comentario.views import (
    comentario_list,
    comentario_detail,
    comentario_create,
    comentario_update,
    comentario_delete,
    comentarios_por_queja,
    comentarios_por_usuario,
)

urlpatterns = [
    path('', comentario_list),                                   # GET /comentario/
    path('<int:pk>/', comentario_detail),                        # GET /comentario/<pk>/
    path('queja/<int:queja_id>/', comentarios_por_queja),            # GET    /comentario/queja/<queja_id>/
    path('user/<int:user_id>/', comentarios_por_usuario),         # GET    /comentario/user/<user_id>/
    path('create/', comentario_create),                          # POST /comentario/create/
    path('<int:pk>/update/', comentario_update),                 # PUT /comentario/<pk>/update/
    path('<int:pk>/delete/', comentario_delete),                 # DELETE /comentario/<pk>/delete/
]
