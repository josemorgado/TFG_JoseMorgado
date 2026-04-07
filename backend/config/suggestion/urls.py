# suggestions/urls.py
from django.urls import path
from suggestion.views import (
    suggestions_list,
    suggestion_detail,
    suggestion_create,
    suggestion_update,
    suggestion_delete,
    suggestions_por_autor,
)

urlpatterns = [
    # GET               /suggestions/
    path('', suggestions_list, name='suggestions-list'),

    # GET               /suggestions/<int:pk>/
    path('<int:pk>/', suggestion_detail, name='suggestion-detail'),

    # POST              /suggestions/create/
    path('create/', suggestion_create, name='suggestion-create'),

    # PUT               /suggestions/<int:pk>/update/
    path('<int:pk>/update/', suggestion_update, name='suggestion-update'),

    # DELETE            /suggestions/<int:pk>/delete/
    path('<int:pk>/delete/', suggestion_delete, name='suggestion-delete'),

    # GET               /suggestions/autor/<int:autor_id>/
    path('autor/<int:autor_id>/', suggestions_por_autor, name='suggestions-por-autor'),
]