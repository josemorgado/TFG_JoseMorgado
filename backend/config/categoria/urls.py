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
    # GET           /categorias/
    path('', categoria_list, name='categoria-list'),

    # GET           /categorias/<int:pk>/
    path('<int:pk>/', categoria_detail, name='categoria-detail'),

    # POST          /categorias/create/
    path('create/', categoria_create, name='categoria-create'),

    # PUT           /categorias/<int:pk>/update/
    path('<int:pk>/update/', categoria_update, name='categoria-update'),

    # DELETE        /categorias/<int:pk>/delete/
    path('<int:pk>/delete/', categoria_delete, name='categoria-delete'),

    # POST          /categorias/<int:pk>/toggle-estado/
    path('<int:pk>/toggle-estado/', categoria_toggle_estado, name='categoria-toggle-estado'),
]