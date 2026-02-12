from django.urls import path
from categoria.views import (
    categoria_list,
    categoria_detail,
    categoria_create,
    categoria_update,
    categoria_delete,
    categoria_toggle_estado,
)

urlpatterns = [
    path('', categoria_list),                                   # GET /categorias/
    path('<int:pk>/', categoria_detail),                         # GET /categorias/<pk>/
    path('create/', categoria_create),                           # POST /categorias/create/
    path('<int:pk>/update/', categoria_update),                  # PUT /categorias/<pk>/update/
    path('<int:pk>/delete/', categoria_delete),                  # DELETE /categorias/<pk>/delete/
    path('<int:pk>/toggle-estado/', categoria_toggle_estado),    # POST/PATCH /categorias/<pk>/toggle-estado/
]
