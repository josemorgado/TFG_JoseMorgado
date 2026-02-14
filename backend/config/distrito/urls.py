from django.urls import path
from distrito.views import (
    distrito_list,
    distrito_detail,
    distrito_create,
    distrito_update,
    distrito_delete,
)

urlpatterns = [
    # GET               /distritos/
    path('', distrito_list, name='distrito-list'),

    # GET               /distritos/<int:pk>/
    path('<int:pk>/', distrito_detail, name='distrito-detail'),

    # POST              /distritos/create/
    path('create/', distrito_create, name='distrito-create'),

    # PUT               /distritos/<int:pk>/update/
    path('<int:pk>/update/', distrito_update, name='distrito-update'),

    # DELETE            /distritos/<int:pk>/delete/
    path('<int:pk>/delete/', distrito_delete, name='distrito-delete'),
]