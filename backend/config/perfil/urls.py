# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Usuarios (User + Perfil anidado)
    path('', views.usuario_list, name='usuario-list'),
    path('<int:pk>/', views.usuario_detail, name='usuario-detail'),
    path('create/', views.usuario_create, name='usuario-create'),
    path('<int:pk>/update/', views.usuario_update, name='usuario-update'),
    path('<int:pk>/partial-update/', views.usuario_partial_update, name='usuario-partial-update'),
    path('<int:pk>/delete/', views.usuario_delete, name='usuario-delete'),
]