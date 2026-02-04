from django.urls import path
from quejas.views import quejas_list, queja_create, queja_detail

urlpatterns = [
    path('', quejas_list, name='quejas-list'),
    path('<int:pk>/', queja_detail, name='queja-detail'),
    path('create/', queja_create, name='queja-create'),
]