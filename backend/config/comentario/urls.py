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
    # GET               /comentarios/
    path('', comentario_list),

    # GET               /comentarios/<int:pk>/
    path('<int:pk>/', comentario_detail),

    # GET               /comentarios/queja/<int:queja_id>/
    path('queja/<int:queja_id>/', comentarios_por_queja),

    # GET               /comentarios/user/<int:user_id>/
    path('user/<int:user_id>/', comentarios_por_usuario),

    # POST              /comentarios/create/
    path('create/', comentario_create),

    # PUT               /comentarios/<int:pk>/update/
    path('<int:pk>/update/', comentario_update),

    # DELETE            /comentarios/<int:pk>/delete/
    path('<int:pk>/delete/', comentario_delete),
]