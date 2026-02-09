from django.urls import path
from categoria.views import (
    categoria_list,
    categoria_detail,
    categoria_create,
    categoria_update,
    categoria_delete,
)

urlpatterns = [
    path('', categoria_list),                                   # GET /categoria/
    path('<int:pk>/', categoria_detail),                         # GET /categoria/<pk>/
    path('create/', categoria_create),                           # POST /categoria/create/
    path('<int:pk>/update/', categoria_update),                  # PUT /categoria/<pk>/update/
    path('<int:pk>/delete/', categoria_delete),                  # DELETE /categoria/<pk>/delete/
]
