from django.urls import path
from distrito.views import (
    distrito_list,
    distrito_detail,
    distrito_create,
    distrito_update,
    distrito_delete,
)

urlpatterns = [
    path('', distrito_list),                                  # GET    /distrito/
    path('<int:pk>/', distrito_detail),                       # GET    /distrito/<pk>/
    path('create/', distrito_create),                         # POST   /distrito/create/
    path('<int:pk>/update/', distrito_update),                # PUT    /distrito/<pk>/update/
    path('<int:pk>/delete/', distrito_delete),                # DELETE /distrito/<pk>/delete/
]